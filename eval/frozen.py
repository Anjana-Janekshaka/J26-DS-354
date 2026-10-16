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

FROZEN_RULES = Path(__file__).parent / "synthetic" / "controller" / "frozen_rule_config.json"


def frozen_rule_config(**overrides) -> tuple[RuleConfig, str]:
    """(RuleConfig, default_strategy) from the frozen file, with optional field overrides."""
    if FROZEN_RULES.exists():
        data = json.loads(FROZEN_RULES.read_text(encoding="utf-8"))
        cfg, default = RuleConfig(**data["config"]), data.get("default_strategy", "sliding_window")
    else:
        cfg, default = RuleConfig(), "sliding_window"
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
}


def system_name() -> str:
    """The system variant from ``CEAI_SYSTEM`` (default ``frozen``)."""
    name = os.environ.get("CEAI_SYSTEM", "frozen")
    if name not in SYSTEMS:
        raise ValueError(f"CEAI_SYSTEM={name!r}; expected one of {sorted(SYSTEMS)}")
    return name


def system_retrieval(**kwargs) -> dict:
    """RetrievalConfig keyword arguments with the selected system variant applied on top."""
    return {**kwargs, **SYSTEMS[system_name()]}


def frozen_controller(**overrides) -> RuleBasedController:
    cfg, default = frozen_rule_config(**overrides)
    return RuleBasedController(cfg, default_strategy=default)
