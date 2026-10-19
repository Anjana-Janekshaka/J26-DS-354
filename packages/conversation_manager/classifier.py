"""Rule-based task-type classifier and topic-shift detector (P1).

Task type comes from phrasing patterns; a topic shift is declared when the new user message's
embedding similarity to the recent-topic centroid drops below a threshold, or when the user
explicitly signals a change of subject. Both are cheap and deterministic.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

import numpy as np

from contracts.text import Embedder, has_code

# Ordered: first match wins. Each entry: (task_type, compiled pattern).
_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    (
        "debugging",
        re.compile(
            r"\b(traceback|stack ?trace|exception|error|errors|bug|crash(es|ed)?|fails?|failing|failed|broken|"
            r"doesn'?t work|not working|keyerror|typeerror|valueerror|attributeerror|nameerror|segfault|"
            r"returns? (none|null|empty)|wrong (output|result)|debug)\b",
            re.I,
        ),
    ),
    (
        "code_refactor",
        re.compile(
            r"\b(refactor|rename|renamed|restructure|clean ?up|simplif(y|ied)|extract (a |the )?(function|method|class)|"
            r"change (the )?(signature|param(eter)?s?|argument)|update (all )?(the )?(calls?|callers|call sites|usages?)|"
            r"migrate|deprecate|switch (it|this) to|move .* into|call(ing)? (it|the|our)? ?\w+ (from|in)|use (the|our) existing)\b",
            re.I,
        ),
    ),
    (
        "code_generation",
        re.compile(
            r"\b(write|implement|add|create|build|generate|make|code up|scaffold)\b.{0,40}?"
            r"\b(function|helper|method|class|endpoint|route|test|tests|script|module|handler|util(ity)?|decorator|api|cli|query)\b",
            re.I,
        ),
    ),
    (
        "qa",
        re.compile(
            r"\b(remind me|what did (we|i|you)|what was|what were|did (we|i|you)|when did|where did|who (did|was|is)|"
            r"how (many|long|old)|which .{0,30}(did|was)|earlier you|you (said|mentioned)|we (said|decided|agreed)|"
            r"do you remember|recall)\b",
            re.I,
        ),
    ),
    (
        "exploration",
        re.compile(
            r"\b(how does|how do|explain|walk me through|what is|what are|what's|overview|explore|look (at|into)|"
            r"understand|tell me about|compare|pros and cons|options for|idea)\b",
            re.I,
        ),
    ),
]

_EXPLICIT_SHIFT = re.compile(
    r"\b(switching gears|change of topic|new topic|different (topic|question|subject)|unrelated|"
    r"on another note|moving on|let'?s move on|separate (question|issue)|by the way|btw|anyway,)\b",
    re.I,
)

# Recall request (Tier 0 cue, independent of task type): a request or question that points back at
# earlier conversation content. Explicit memory phrasing counts on its own; a back-reference counts
# only inside a request or question, so statements ("I told my boss ...") are not flagged.
_RECALL_EXPLICIT = re.compile(
    r"\b(remind me|do you (still )?remember|can you recall|go back to what)\b",
    re.I,
)
_RECALL_BACKREF = re.compile(
    r"\b((i|we)( had| have|'ve|'d)? (told|mentioned|said|shared|asked|described|listed|discussed|talked about|went over|"
    r"covered|decided|agreed|planned|brought up|noted|explained|showed|gave|wrote|chose|picked)|"
    r"you (told|said|mentioned|suggested|recommended|gave|showed|explained|wrote)( me| us)?|"
    r"did (i|we|you) (tell|mention|say|share|ask|describe|list|discuss|talk about|go over|cover|decide|agree|plan|"
    r"bring up|note|explain|show|give|write|choose|pick|suggest|recommend)|"
    r"(earlier|previously|before|so far|up to now) (in|during|throughout) (this|our) (conversation|chat|discussion|session)s?|"
    r"in (our|this) (previous|earlier|last|past|first) (conversation|chat|discussion|session)s?|"
    r"(throughout|over|across) (the course of )?(our|this) (conversation|chat|discussion|session)s?|"
    r"(my|our) (earlier|previous|original|initial|first) (message|question|request|plan|idea|choice|preference|answer)s?)\b",
    re.I,
)
_REQUEST = re.compile(
    r"^\s*(please\s+)?(can|could|would|will) you\b|^\s*(please\s+)?(list|tell|show|give|remind|walk|"
    r"go over|repeat|name|describe|outline|explain)\b",
    re.I,
)


def is_recall_request(text: str) -> bool:
    if _RECALL_EXPLICIT.search(text):
        return True
    return bool(_RECALL_BACKREF.search(text)) and (text.rstrip().endswith("?") or bool(_REQUEST.search(text)))


_ENTITY = re.compile(r"(?<!^)(?<![.!?]\s)\b([A-Z][a-z]{2,})\b")
_ENTITY_STOP = {"what", "when", "where", "which", "who", "why", "how", "the", "this", "that", "did", "does", "can", "could",
                "would", "should", "is", "are", "was", "were", "have", "has", "also", "now", "okay", "thanks", "yes", "and"}

_WH_QUESTION = re.compile(r"^\s*(when|where|who|what|which|how|why|did|does|is|was|were|has|have)\b.*\?\s*$", re.I | re.S)


@dataclass
class ClassifierConfig:
    shift_similarity_threshold: float = 0.15
    centroid_window: int = 4
    min_turns_before_shift: int = 3


@dataclass
class Classification:
    task_type: str
    shift_detected: bool
    matched_rule: str
    topic_similarity: float | None
    recall_request: bool = False


@dataclass
class TaskTypeClassifier:
    embedder: Embedder | None = None
    config: ClassifierConfig = field(default_factory=ClassifierConfig)
    _recent: list[np.ndarray] = field(default_factory=list)
    _seen: int = 0
    _last_type: str = "chat"
    _entities: set = field(default_factory=set)

    def classify_phrasing(self, text: str) -> tuple[str | None, str]:
        # A question naming an entity already seen in this conversation is a recall question,
        # whatever its surface form ("What is Caroline's identity?" is recall, not exploration).
        if text.rstrip().endswith("?") and not _PATTERNS[0][1].search(text):
            mentioned = {m.lower() for m in _ENTITY.findall(text)}
            if mentioned & self._entities:
                return "qa", "pattern:question_about_known_entity"
        for task, pat in _PATTERNS:
            if pat.search(text):
                return task, f"pattern:{task}"
        if _WH_QUESTION.match(text):
            return "qa", "pattern:wh_question"
        if has_code(text):
            return "code_generation", "pattern:code_block"
        return None, "none"

    def observe(self, text: str, decision_point: bool) -> Classification:
        """Update topic state with ``text``; classify task type when it is a decision point."""
        sim = None
        shift = False
        vec = None
        if self.embedder is not None:
            vec = self.embedder.encode([text])[0]
            if self._recent and self._seen >= self.config.min_turns_before_shift:
                centroid = np.mean(self._recent, axis=0)
                n = np.linalg.norm(centroid)
                sim = float(vec @ centroid / n) if n > 0 else 0.0
                shift = sim < self.config.shift_similarity_threshold
        if _EXPLICIT_SHIFT.search(text) and self._seen > 0:
            shift = True

        task, rule = (None, "none")
        if decision_point:
            task, rule = self.classify_phrasing(text)
        if task is None:
            # Unmatched phrasing keeps the current task type unless the topic shifted.
            task = "chat" if shift else self._last_type
            rule = "carry_over" if not shift else "shift_default"
        if decision_point:
            self._last_type = task

        self._entities |= {m.lower() for m in _ENTITY.findall(text)} - _ENTITY_STOP
        if vec is not None:
            if shift:
                self._recent = []
            self._recent.append(vec)
            self._recent = self._recent[-self.config.centroid_window :]
        self._seen += 1
        return Classification(task_type=task, shift_detected=shift, matched_rule=rule, topic_similarity=sim,
                              recall_request=decision_point and is_recall_request(text))
