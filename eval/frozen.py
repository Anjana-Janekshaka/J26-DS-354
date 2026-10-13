"""The frozen controller configuration every benchmark and the demo run with.

``eval/synthetic/controller/frozen_rule_config.json`` is written by
``eval.synthetic.controller.tune_rules`` (train + val only). The routing options were then checked
against the other dev sets (LoCoMo dev, in-stream LoCoMo dev, LoCoMo-Plus dev) before freezing;
see CLAUDE.md section 12. Test splits are only ever run with this configuration.
"""

from __future__ import annotations

import json
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


def frozen_controller(**overrides) -> RuleBasedController:
    cfg, default = frozen_rule_config(**overrides)
    return RuleBasedController(cfg, default_strategy=default)
