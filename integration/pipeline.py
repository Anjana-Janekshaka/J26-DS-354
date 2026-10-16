"""End-to-end turn loop wiring every package together.

Per user turn:
  1. pending dashboard overrides are forwarded to the controller;
  2. the Conversation Manager registers the message and broadcasts its ``TurnSignal``;
  3. the three strategy modules build candidate contexts in parallel, while the controller decides
     from the signal alone (it never receives the outputs - section 5);
  4. the LLM Interface assembles the prompt from the selected strategy's output;
  5. the decision record is appended to the log, then Tier 2 signals from this turn's outputs are
     raised as escalation events that the controller will consume on the *next* turn;
  6. the user message is ingested into every module's memory (and the assistant reply, if any).
"""

from __future__ import annotations

import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from contracts import (
    ControllerDecision,
    ControllerFeatureVector,
    ConversationTurn,
    DecisionLogRecord,
    EscalationEvent,
    StrategyModule,
    StrategyModuleOutput,
    TurnSignal,
    utcnow,
)
from contracts.text import CachingEmbedder, Embedder
from controller import RuleBasedController, RuleConfig
from conversation_manager import ClassifierConfig, ConversationManager, SignalBus
from decision_logger import DecisionLogger, OverrideInbox
from retrieval import NLIScorer, RetrievalConfig, RetrievalEngine
from sliding_window import DynamicSlidingWindow, SlidingWindowConfig
from summarization import HierarchicalSummarizer, LLMGenerator, SummarizationConfig

from .llm_interface import AssembledPrompt, assemble_prompt


@dataclass
class TurnResult:
    turn: ConversationTurn
    signal: TurnSignal
    feature_vector: ControllerFeatureVector
    decision: ControllerDecision
    outputs: dict[str, StrategyModuleOutput]
    prompt: AssembledPrompt
    escalations: list[EscalationEvent]
    response: str | None = None


def default_embedder() -> Embedder:
    from retrieval import SentenceTransformerEmbedder

    return CachingEmbedder(SentenceTransformerEmbedder())


class MemoryPipeline:
    def __init__(
        self,
        conversation_id: str,
        token_budget: int = 1024,
        *,
        embedder: Embedder | None = None,
        nli: NLIScorer | None = None,
        log_dir: str | Path | None = None,
        modules: dict[str, StrategyModule] | None = None,
        controller: RuleBasedController | None = None,
        llm=None,
        summarize_with_llm: bool = False,
        sw_config: SlidingWindowConfig | None = None,
        summarization_config: SummarizationConfig | None = None,
        retrieval_config: RetrievalConfig | None = None,
        rule_config: RuleConfig | None = None,
        classifier_config: ClassifierConfig | None = None,
    ):
        self.conversation_id = conversation_id
        self.token_budget = token_budget
        self.embedder = embedder or default_embedder()
        self.bus = SignalBus()
        self.manager = ConversationManager(conversation_id, token_budget, self.bus, self.embedder, classifier_config)
        if modules is None:
            generator = LLMGenerator(llm) if (summarize_with_llm and llm is not None) else None
            modules = {
                "sliding_window": DynamicSlidingWindow(self.embedder, sw_config),
                "summarization": HierarchicalSummarizer(generator, summarization_config),
                "rag": RetrievalEngine(self.embedder, nli, retrieval_config),
            }
        self.modules = modules
        for m in self.modules.values():
            self.bus.subscribe(m.observe_signal)
        self.controller = controller or RuleBasedController(rule_config)
        self.llm = llm
        self.logger = DecisionLogger(log_dir) if log_dir else None
        self.overrides = OverrideInbox(Path(log_dir) / "overrides.jsonl") if log_dir else None
        self._pool = ThreadPoolExecutor(max_workers=len(self.modules), thread_name_prefix="strategy")
        self._reported_flags: set[tuple[str, str]] = set()
        self.history: list[TurnResult] = []

    # ------------------------------------------------------------------ memory without a decision
    def add_turn(
        self,
        role: str,
        content: str,
        *,
        speaker: str | None = None,
        timestamp: datetime | None = None,
        metadata: dict | None = None,
    ) -> ConversationTurn:
        obs = self.manager.observe(role, content, decision_point=False, speaker=speaker, timestamp=timestamp, metadata=metadata)
        self._ingest(obs.turn)
        return obs.turn

    def assistant_turn(self, content: str, **kw) -> ConversationTurn:
        return self.add_turn("assistant", content, **kw)

    def _ingest(self, turn: ConversationTurn) -> None:
        for m in self.modules.values():
            m.ingest(turn)
        self._feed_observations(turn)

    _OBSERVATION_KINDS = ("statement", "user_state", "constraint", "decision")

    def _feed_observations(self, turn: ConversationTurn) -> None:
        """v3 option: pass the summarizer's verbatim fact sentences for this turn to RAG as short
        retrievable observations. Integration wires the two packages; neither imports the other."""
        rag = self.modules.get("rag")
        if rag is None or not getattr(getattr(rag, "config", None), "observations", False):
            return
        from summarization.extract import extract_facts

        seq = getattr(self, "_obs_seq", [0])
        self._obs_seq = seq
        facts, _ = extract_facts(turn, seq)
        for f in facts:
            if f.kind in self._OBSERVATION_KINDS and len(f.value.split()) >= 4:
                rag.add_observation(f.value, turn)

    # ------------------------------------------------------------------ escalations (Tier 2, next turn)
    def _escalations(self, signal: TurnSignal, outputs: dict[str, StrategyModuleOutput], commit: bool = True) -> list[EscalationEvent]:
        """``commit=False`` (evaluation probes) builds the events without marking flags as reported."""
        events: list[EscalationEvent] = []
        summ = outputs.get("summarization")
        if summ is not None and summ.quality.loss_threshold_exceeded:  # type: ignore[union-attr]
            q = summ.quality
            events.append(
                EscalationEvent(
                    event_id=uuid.uuid4().hex[:12],
                    conversation_id=self.conversation_id,
                    source_turn_id=signal.turn_id,
                    source_module="summarization",
                    kind="loss_threshold_exceeded",
                    detail={"loss_score": q.loss_score, "tier_emitted": q.tier_emitted, "symbol_retention_rate": q.symbol_retention_rate},  # type: ignore[union-attr]
                    raised_at=utcnow(),
                )
            )
        rag = outputs.get("rag")
        if rag is not None:
            new = [f for f in rag.quality.contradiction_flags if (f.chunk_id, f.superseded_by) not in self._reported_flags]  # type: ignore[union-attr]
            if new:
                if commit:
                    self._reported_flags |= {(f.chunk_id, f.superseded_by) for f in new}
                events.append(
                    EscalationEvent(
                        event_id=uuid.uuid4().hex[:12],
                        conversation_id=self.conversation_id,
                        source_turn_id=signal.turn_id,
                        source_module="rag",
                        kind="contradiction_flagged",
                        detail={"n_flags": len(new), "flags": [f.model_dump() for f in new]},
                        raised_at=utcnow(),
                    )
                )
        return events

    # ------------------------------------------------------------------ decision turn
    def user_turn(self, content: str, *, remember: bool = True, respond: bool = True, **kw) -> TurnResult:
        """Run one decision turn. ``remember=False`` asks without storing the message (eval probes)."""
        if self.overrides is not None:
            for req in self.overrides.poll():
                self.controller.request_override(req)

        if remember:
            obs = self.manager.observe("user", content, decision_point=True, **kw)
        else:
            obs = self.manager.probe(content, **kw)
        signal = obs.signal
        futures = {name: self._pool.submit(m.build_context, signal, content) for name, m in self.modules.items()}
        feature_vector, decision = self.controller.decide(signal, commit=remember)  # signal only: no module outputs
        outputs = {name: f.result() for name, f in futures.items()}

        prompt = assemble_prompt(decision, outputs, content, signal.token_usage.budget)
        if self.logger is not None:
            self.logger.log(
                DecisionLogRecord(
                    turn_id=signal.turn_id,
                    feature_vector=feature_vector,
                    decision=decision,
                    module_outputs=outputs,  # type: ignore[arg-type]
                    logged_at=utcnow(),
                )
            )
        events = self._escalations(signal, outputs, commit=remember)
        for ev in events:
            if remember:
                self.controller.register_escalation(ev)
            if self.logger is not None:
                self.logger.log_escalation(ev)

        if remember:
            self._ingest(obs.turn)

        response = None
        if respond and self.llm is not None:
            response = self.llm(prompt.system, f"[Memory context]\n{prompt.context}\n\n[Current message]\n{content}")
            self.assistant_turn(response)
        result = TurnResult(obs.turn, signal, feature_vector, decision, outputs, prompt, events, response)
        self.history.append(result)
        return result

    def close(self) -> None:
        self._pool.shutdown(wait=True)
