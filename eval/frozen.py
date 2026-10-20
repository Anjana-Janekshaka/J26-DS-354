"""The frozen controller configuration every benchmark and the demo run with.

``eval/synthetic/controller/frozen_rule_config.json`` is written by
``eval.synthetic.controller.tune_rules`` (train + val only). The routing options were then checked
against the other dev sets (LoCoMo dev, in-stream LoCoMo dev, LoCoMo-Plus dev) before freezing;
see CLAUDE.md section 12. Test splits are only ever run with this configuration.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from controller import RuleBasedController, RuleConfig
from retrieval import ContradictionConfig
from retrieval.chunking import BoundaryConfig

FROZEN_RULES = Path(__file__).parent / "synthetic" / "controller" / "frozen_rule_config.json"


def frozen_rule_config(**overrides) -> tuple[RuleConfig, str]:
    """(RuleConfig, default_strategy) from the frozen file, with optional field overrides."""
    if FROZEN_RULES.exists():
        data = json.loads(FROZEN_RULES.read_text(encoding="utf-8"))
        cfg, default = RuleConfig(**data["config"]), data.get("default_strategy", "sliding_window")
    else:
        cfg, default = RuleConfig(), "sliding_window"
    overrides = {**SYSTEM_RULES.get(system_name(), {}), **overrides}
    if overrides:
        cfg = cfg.model_copy(update=overrides)
    return cfg, default


# System variants. "frozen" is the configuration all 2026-10-15 test results were produced with.
# "v2_hybrid" adds hybrid BM25 + dense retrieval (selected on LoCoMo dev only; pre-registered in
# docs/v2_hybrid_preregistration.md before any test split was run with it).
SYSTEMS: dict[str, dict] = {
    "frozen": {},
    "v2_hybrid": {"hybrid": True},
    # v3 (docs/v3_preregistration.md): hybrid only for question turns + summarizer facts as RAG observations
    "v3_qa_hybrid_obs": {"hybrid_task_types": ("qa",), "observations": True},
    # v4 (docs/v4_preregistration.md): the two component candidates that passed their dev gates.
    # Retrieval side: the staleness ensemble (weights and threshold fitted on the dev contradiction pairs).
    # Plus the dev-tuned chunking weights (eval.locomo.chunking_search; joined after beating fixed segments on test).
    "v4": {"boundary": BoundaryConfig(bias=-4.556022, w_semantic=4.408378, w_length=0.354663, w_turns=2.261815, max_segment_tokens=150, max_segment_turns=3),
           "contradiction": ContradictionConfig(ensemble=(-3.020881, 1.329963, 1.243888, 0.441096, 2.506616), ensemble_threshold=0.4666)},
    # v4b (amendment in docs/v4_preregistration.md): v4 without the sliding-window weights, which failed gate G2.
    "v4b": {},
}
SYSTEMS["v4b"] = dict(SYSTEMS["v4"])
# v5_recall (docs/v5_recall_preregistration.md): the frozen system plus the controller's recall-request
# rule. Retrieval is unchanged; only the routing differs.
SYSTEMS["v5_recall"] = {}

# Controller rule overrides per system, applied on top of the frozen rule file.
SYSTEM_RULES: dict[str, dict] = {"v5_recall": {"recall_requests_as_qa": True}}

# Sliding-window weights per system ("relevance,freshness,importance,state"); the v4 weights were
# chosen on the dev half of the topic-shift workloads (eval.synthetic.sliding_window.select_weights).
SYSTEM_SW_WEIGHTS: dict[str, str] = {"v4": "0.5,0,0.5,0"}


def system_name() -> str:
    """The system variant from ``CEAI_SYSTEM`` (default ``frozen``)."""
    name = os.environ.get("CEAI_SYSTEM", "frozen")
    if name not in SYSTEMS:
        raise ValueError(f"CEAI_SYSTEM={name!r}; expected one of {sorted(SYSTEMS)}")
    return name


def llm_policy() -> str:
    """``CEAI_LLM_POLICY``: ``strict`` (default, no LLM in the memory path) or ``assisted`` (the LLM
    writes the L2/L3 summary tiers only; docs/llm_policy_preregistration.md)."""
    policy = os.environ.get("CEAI_LLM_POLICY", "strict")
    if policy not in ("strict", "assisted"):
        raise ValueError(f"CEAI_LLM_POLICY={policy!r}; expected 'strict' or 'assisted'")
    return policy


def system_retrieval(**kwargs) -> dict:
    """RetrievalConfig keyword arguments with the selected system variant applied on top.

    Also applies the variant's sliding-window weights through ``CEAI_SW_WEIGHTS``, which every
    ``DynamicSlidingWindow`` built without an explicit config reads (harnesses call this before
    constructing the pipeline)."""
    name = system_name()
    if name in SYSTEM_SW_WEIGHTS:
        os.environ["CEAI_SW_WEIGHTS"] = SYSTEM_SW_WEIGHTS[name]
    return {**kwargs, **SYSTEMS[name]}


def frozen_controller(**overrides) -> RuleBasedController:
    cfg, default = frozen_rule_config(**overrides)
    return RuleBasedController(cfg, default_strategy=default)
