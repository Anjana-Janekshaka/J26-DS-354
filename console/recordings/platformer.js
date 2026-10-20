window.CEAI_SESSIONS = window.CEAI_SESSIONS || {};
window.CEAI_SESSIONS["platformer"] = {
 "scenario": "platformer",
 "slug": "platformer",
 "language": "python",
 "held_out": true,
 "system": "frozen",
 "mode": "full",
 "budget": 700,
 "recorded_at": "2026-10-19T11:24:49+00:00",
 "rule_config": {
  "low_pressure": 0.9,
  "high_pressure": 0.9,
  "min_dwell_turns": 3,
  "long_chat_strategy": "summarization",
  "loss_escalation_target": "rag",
  "qa_strategy": "rag",
  "recall_requests_as_qa": false,
  "default_strategy": "sliding_window"
 },
 "n_traps": 2,
 "score": {
  "adaptive": 0,
  "fixed_6_exchange_window": 1,
  "sliding_window": 0,
  "summarization": 0,
  "rag": 0,
  "hybrid": 0
 },
 "turns": [
  {
   "exchange": 1,
   "turn_id": "t0001",
   "user": "I'm making a small platformer in pygame. How do I organise the update loop?",
   "assistant": "Fixed timestep: accumulate frame time and step physics in 1/120 s increments, render once per frame with interpolation. Entities hold position, velocity and a collider.",
   "signal": {
    "turn_count": 1,
    "task_type": "exploration",
    "matched_pattern": "pattern:exploration",
    "topic_similarity": null,
    "shift": false,
    "recall_request": false,
    "tokens_used": 20,
    "budget": 700
   },
   "features": {
    "turn_count": 1,
    "token_budget_pressure": 0.0286,
    "task_type": "exploration",
    "prior_strategy": null,
    "time_since_last_switch": 0
   },
   "rules": [
    {
     "fn": "fits",
     "matched": true,
     "fired": true,
     "rule": "history_fits",
     "strategy": "sliding_window",
     "hard": false,
     "reason": "token pressure 0.03 < 0.90: full recent history fits, window is lossless"
    },
    {
     "fn": "qa",
     "matched": false,
     "fired": false,
     "rule": null,
     "strategy": null,
     "hard": null,
     "reason": null
    },
    {
     "fn": "build",
     "matched": false,
     "fired": false,
     "rule": null,
     "strategy": null,
     "hard": null,
     "reason": null
    },
    {
     "fn": "refactor",
     "matched": false,
     "fired": false,
     "rule": null,
     "strategy": null,
     "hard": null,
     "reason": null
    },
    {
     "fn": "debug",
     "matched": false,
     "fired": false,
     "rule": null,
     "strategy": null,
     "hard": null,
     "reason": null
    },
    {
     "fn": "recall_request",
     "matched": false,
     "fired": false,
     "rule": null,
     "strategy": null,
     "hard": null,
     "reason": null
    },
    {
     "fn": "long_open",
     "matched": false,
     "fired": false,
     "rule": null,
     "strategy": null,
     "hard": null,
     "reason": null
    }
   ],
   "decision": {
    "strategy": "sliding_window",
    "latency_ms": 0.0652,
    "override": [],
    "full": "[history_fits] token pressure 0.03 < 0.90: full recent history fits, window is lossless | features: turn=1, pressure=0.03, task=exploration, prior=None, since_switch=0",
    "rule": "history_fits",
    "rule_reason": "token pressure 0.03 < 0.90: full recent history fits, window is lossless",
    "dwell": [],
    "escalations": []
   },
   "candidates": {
    "sliding_window": {
     "tokens": 0,
     "latency_ms": 0.81,
     "quality": {
      "kept": 0,
      "relevance": 0.0,
      "freshness": 0.0,
      "importance": 0.0,
      "state": 0.0,
      "composite": 0.0
     }
    },
    "summarization": {
     "tokens": 0,
     "latency_ms": 1.1,
     "quality": {
      "tier_emitted": "L1",
      "loss_score": 0.0,
      "loss_threshold_exceeded": false,
      "symbol_retention_rate": null
     }
    },
    "rag": {
     "tokens": 0,
     "latency_ms": 0.82,
     "quality": {
      "granularity_tag": "turn",
      "retrieved": 0,
      "stale_flags": 0
     }
    }
   },
   "prompt": {
    "tokens": 0,
    "context": "",
    "truncated": false
   },
   "raised": [],
   "traps": []
  },
  {
   "exchange": 2,
   "turn_id": "t0003",
   "user": "Write the physics step.",
   "assistant": "```python\nGRAVITY = 980\n\ndef apply_physics(entity, dt):\n    entity.vy += GRAVITY * dt\n    entity.x += entity.vx * dt\n    entity.y += entity.vy * dt\n```",
   "signal": {
    "turn_count": 3,
    "task_type": "exploration",
    "matched_pattern": "carry_over",
    "topic_similarity": null,
    "shift": false,
    "recall_request": false,
    "tokens_used": 62,
    "budget": 700
   },
   "features": {
    "turn_count": 3,
    "token_budget_pressure": 0.0886,
    "task_type": "exploration",
    "prior_strategy": "sliding_window",
    "time_since_last_switch": 0
   },
   "rules": [
    {
     "fn": "fits",
     "matched": true,
     "fired": true,
     "rule": "history_fits",
     "strategy": "sliding_window",
     "hard": false,
     "reason": "token pressure 0.09 < 0.90: full recent history fits, window is lossless"
    },
    {
     "fn": "qa",
     "matched": false,
     "fired": false,
     "rule": null,
     "strategy": null,
     "hard": null,
     "reason": null
    },
    {
     "fn": "build",
     "matched": false,
     "fired": false,
     "rule": null,
     "strategy": null,
     "hard": null,
     "reason": null
    },
    {
     "fn": "refactor",
     "matched": false,
     "fired": false,
     "rule": null,
     "strategy": null,
     "hard": null,
     "reason": null
    },
    {
     "fn": "debug",
     "matched": false,
     "fired": false,
     "rule": null,
     "strategy": null,
     "hard": null,
     "reason": null
    },
    {
     "fn": "recall_request",
     "matched": false,
     "fired": false,
     "rule": null,
     "strategy": null,
     "hard": null,
     "reason": null
    },
    {
     "fn": "long_open",
     "matched": false,
     "fired": false,
     "rule": null,
     "strategy": null,
     "hard": null,
     "reason": null
    }
   ],
   "decision": {
    "strategy": "sliding_window",
    "latency_ms": 0.0628,
    "override": [],
    "full": "[history_fits] token pressure 0.09 < 0.90: full recent history fits, window is lossless | features: turn=3, pressure=0.09, task=exploration, prior=sliding_window, since_switch=0",
    "rule": "history_fits",
    "rule_reason": "token pressure 0.09 < 0.90: full recent history fits, window is lossless",
    "dwell": [],
    "escalations": []
   },
   "candidates": {
    "sliding_window": {
     "tokens": 55,
     "latency_ms": 0.71,
     "quality": {
      "kept": 2,
      "relevance": 0.16,
      "freshness": 0.959,
      "importance": 0.05,
      "state": 1.0,
      "composite": 0.542
     }
    },
    "summarization": {
     "tokens": 59,
     "latency_ms": 0.97,
     "quality": {
      "tier_emitted": "L1",
      "loss_score": 0.0,
      "loss_threshold_exceeded": false,
      "symbol_retention_rate": null
     }
    },
    "rag": {
     "tokens": 43,
     "latency_ms": 1085.75,
     "quality": {
      "granularity_tag": "turn",
      "retrieved": 1,
      "stale_flags": 0
     }
    }
   },
   "prompt": {
    "tokens": 55,
    "context": "user: I'm making a small platformer in pygame. How do I organise the update loop?\nassistant: Fixed timestep: accumulate frame time and step physics in 1/120 s increments, render once per frame with interpolation. Entities hold position, velocity and a collider.",
    "truncated": false
   },
   "raised": [],
   "traps": []
  },
  {
   "exchange": 3,
   "turn_id": "t0005",
   "user": "Jumping feels floaty.",
   "assistant": "Stronger gravity and a cap on fall speed:\n```python\nGRAVITY = 1800\n```\nand clamp `vy` to 900.",
   "signal": {
    "turn_count": 5,
    "task_type": "exploration",
    "matched_pattern": "carry_over",
    "topic_similarity": null,
    "shift": false,
    "recall_request": false,
    "tokens_used": 121,
    "budget": 700
   },
   "features": {
    "turn_count": 5,
    "token_budget_pressure": 0.1729,
    "task_type": "exploration",
    "prior_strategy": "sliding_window",
    "time_since_last_switch": 1
   },
   "rules": [
    {
     "fn": "fits",
     "matched": true,
     "fired": true,
     "rule": "history_fits",
     "strategy": "sliding_window",
     "hard": false,
     "reason": "token pressure 0.17 < 0.90: full recent history fits, window is lossless"
    },
    {
     "fn": "qa",
     "matched": false,
     "fired": false,
     "rule": null,
     "strategy": null,
     "hard": null,
     "reason": null
    },
    {
     "fn": "build",
     "matched": false,
     "fired": false,
     "rule": null,
     "strategy": null,
     "hard": null,
     "reason": null
    },
    {
     "fn": "refactor",
     "matched": false,
     "fired": false,
     "rule": null,
     "strategy": null,
     "hard": null,
     "reason": null
    },
    {
     "fn": "debug",
     "matched": false,
     "fired": false,
     "rule": null,
     "strategy": null,
     "hard": null,
     "reason": null
    },
    {
     "fn": "recall_request",
     "matched": false,
     "fired": false,
     "rule": null,
     "strategy": null,
     "hard": null,
     "reason": null
    },
    {
     "fn": "long_open",
     "matched": false,
     "fired": false,
     "rule": null,
     "strategy": null,
     "hard": null,
     "reason": null
    }
   ],
   "decision": {
    "strategy": "sliding_window",
    "latency_ms": 0.1036,
    "override": [],
    "full": "[history_fits] token pressure 0.17 < 0.90: full recent history fits, window is lossless | features: turn=5, pressure=0.17, task=exploration, prior=sliding_window, since_switch=1",
    "rule": "history_fits",
    "rule_reason": "token pressure 0.17 < 0.90: full recent history fits, window is lossless",
    "dwell": [],
    "escalations": []
   },
   "candidates": {
    "sliding_window": {
     "tokens": 113,
     "latency_ms": 0.64,
     "quality": {
      "kept": 4,
      "relevance": 0.185,
      "freshness": 0.882,
      "importance": 0.2,
      "state": 1.0,
      "composite": 0.567
     }
    },
    "summarization": {
     "tokens": 117,
     "latency_ms": 0.9,
     "quality": {
      "tier_emitted": "L1",
      "loss_score": 0.0,
      "loss_threshold_exceeded": false,
      "symbol_retention_rate": 1.0
     }
    },
    "rag": {
     "tokens": 119,
     "latency_ms": 879.26,
     "quality": {
      "granularity_tag": "turn",
      "retrieved": 3,
      "stale_flags": 0
     }
    }
   },
   "prompt": {
    "tokens": 113,
    "context": "user: I'm making a small platformer in pygame. How do I organise the update loop?\nassistant: Fixed timestep: accumulate frame time and step physics in 1/120 s increments, render once per frame with interpolation. Entities hold position, velocity and a collider.\nuser: Write the physics step.\nassistant: ```python\nGRAVITY = 980\n\ndef apply_physics(entity, dt):\n    entity.vy += GRAVITY * dt\n    entity.x += entity.vx * dt\n    entity.y += entity.vy * dt\n```",
    "truncated": false
   },
   "raised": [],
   "traps": []
  },
  {
   "exchange": 4,
   "turn_id": "t0007",
   "user": "Rename the physics function, we now have a separate collision pass so it only integrates motion.",
   "assistant": "```python\ndef integrate_motion(entity, dt):\n    entity.vy = min(entity.vy + GRAVITY * dt, 900)\n    entity.x += entity.vx * dt\n    entity.y += entity.vy * dt\n```",
   "signal": {
    "turn_count": 7,
    "task_type": "code_refactor",
    "matched_pattern": "pattern:code_refactor",
    "topic_similarity": 0.358,
    "shift": false,
    "recall_request": false,
    "tokens_used": 175,
    "budget": 700
   },
   "features": {
    "turn_count": 7,
    "token_budget_pressure": 0.25,
    "task_type": "code_refactor",
    "prior_strategy": "sliding_window",
    "time_since_last_switch": 2
   },
   "rules": [
    {
     "fn": "fits",
     "matched": true,
     "fired": true,
     "rule": "history_fits",
     "strategy": "sliding_window",
     "hard": false,
     "reason": "token pressure 0.25 < 0.90: full recent history fits, window is lossless"
    },
    {
     "fn": "qa",
     "matched": false,
     "fired": false,
     "rule": null,
     "strategy": null,
     "hard": null,
     "reason": null
    },
    {
     "fn": "build",
     "matched": false,
     "fired": false,
     "rule": null,
     "strategy": null,
     "hard": null,
     "reason": null
    },
    {
     "fn": "refactor",
     "matched": true,
     "fired": false,
     "rule": "refactor_request",
     "strategy": "summarization",
     "hard": true,
     "reason": "task_type=code_refactor -> summarization: merged L1 symbol table carries current signatures and renames"
    },
    {
     "fn": "debug",
     "matched": false,
     "fired": false,
     "rule": null,
     "strategy": null,
     "hard": null,
     "reason": null
    },
    {
     "fn": "recall_request",
     "matched": false,
     "fired": false,
     "rule": null,
     "strategy": null,
     "hard": null,
     "reason": null
    },
    {
     "fn": "long_open",
     "matched": false,
     "fired": false,
     "rule": null,
     "strategy": null,
     "hard": null,
     "reason": null
    }
   ],
   "decision": {
    "strategy": "sliding_window",
    "latency_ms": 0.069,
    "override": [],
    "full": "[history_fits] token pressure 0.25 < 0.90: full recent history fits, window is lossless | features: turn=7, pressure=0.25, task=code_refactor, prior=sliding_window, since_switch=2",
    "rule": "history_fits",
    "rule_reason": "token pressure 0.25 < 0.90: full recent history fits, window is lossless",
    "dwell": [],
    "escalations": []
   },
   "candidates": {
    "sliding_window": {
     "tokens": 155,
     "latency_ms": 0.58,
     "quality": {
      "kept": 6,
      "relevance": 0.259,
      "freshness": 0.814,
      "importance": 0.183,
      "state": 1.0,
      "composite": 0.564
     }
    },
    "summarization": {
     "tokens": 160,
     "latency_ms": 0.9,
     "quality": {
      "tier_emitted": "L1",
      "loss_score": 0.0,
      "loss_threshold_exceeded": false,
      "symbol_retention_rate": 1.0
     }
    },
    "rag": {
     "tokens": 180,
     "latency_ms": 704.05,
     "quality": {
      "granularity_tag": "turn",
      "retrieved": 5,
      "stale_flags": 0
     }
    }
   },
   "prompt": {
    "tokens": 156,
    "context": "user: I'm making a small platformer in pygame. How do I organise the update loop?\nassistant: Fixed timestep: accumulate frame time and step physics in 1/120 s increments, render once per frame with interpolation. Entities hold position, velocity and a collider.\nuser: Write the physics step.\nassistant: ```python\nGRAVITY = 980\n\ndef apply_physics(entity, dt):\n    entity.vy += GRAVITY * dt\n    entity.x += entity.vx * dt\n    entity.y += entity.vy * dt\n```\nuser: Jumping feels floaty.\nassistant: Stronger gravity and a cap on fall speed:\n```python\nGRAVITY = 1800\n```\nand clamp `vy` to 900.",
    "truncated": false
   },
   "raised": [],
   "traps": []
  },
  {
   "exchange": 5,
   "turn_id": "t0009",
   "user": "Collision with tiles?",
   "assistant": "Resolve axes separately: move on x, push out of overlapping tiles, then the same on y, and set `on_ground` when a downward move is blocked.",
   "signal": {
    "turn_count": 9,
    "task_type": "code_refactor",
    "matched_pattern": "carry_over",
    "topic_similarity": 0.276,
    "shift": false,
    "recall_request": false,
    "tokens_used": 232,
    "budget": 700
   },
   "features": {
    "turn_count": 9,
    "token_budget_pressure": 0.3314,
    "task_type": "code_refactor",
    "prior_strategy": "sliding_window",
    "time_since_last_switch": 3
   },
   "rules": [
    {
     "fn": "fits",
     "matched": true,
     "fired": true,
     "rule": "history_fits",
     "strategy": "sliding_window",
     "hard": false,
     "reason": "token pressure 0.33 < 0.90: full recent history fits, window is lossless"
    },
    {
     "fn": "qa",
     "matched": false,
     "fired": false,
     "rule": null,
     "strategy": null,
     "hard": null,
     "reason": null
    },
    {
     "fn": "build",
     "matched": false,
     "fired": false,
     "rule": null,
     "strategy": null,
     "hard": null,
     "reason": null
    },
    {
     "fn": "refactor",
     "matched": true,
     "fired": false,
     "rule": "refactor_request",
     "strategy": "summarization",
     "hard": true,
     "reason": "task_type=code_refactor -> summarization: merged L1 symbol table carries current signatures and renames"
    },
    {
     "fn": "debug",
     "matched": false,
     "fired": false,
     "rule": null,
     "strategy": null,
     "hard": null,
     "reason": null
    },
    {
     "fn": "recall_request",
     "matched": false,
     "fired": false,
     "rule": null,
     "strategy": null,
     "hard": null,
     "reason": null
    },
    {
     "fn": "long_open",
     "matched": false,
     "fired": false,
     "rule": null,
     "strategy": null,
     "hard": null,
     "reason": null
    }
   ],
   "decision": {
    "strategy": "sliding_window",
    "latency_ms": 0.0719,
    "override": [],
    "full": "[history_fits] token pressure 0.33 < 0.90: full recent history fits, window is lossless | features: turn=9, pressure=0.33, task=code_refactor, prior=sliding_window, since_switch=3",
    "rule": "history_fits",
    "rule_reason": "token pressure 0.33 < 0.90: full recent history fits, window is lossless",
    "dwell": [],
    "escalations": []
   },
   "candidates": {
    "sliding_window": {
     "tokens": 226,
     "latency_ms": 0.54,
     "quality": {
      "kept": 8,
      "relevance": 0.114,
      "freshness": 0.753,
      "importance": 0.225,
      "state": 1.0,
      "composite": 0.523
     }
    },
    "summarization": {
     "tokens": 231,
     "latency_ms": 0.94,
     "quality": {
      "tier_emitted": "L1",
      "loss_score": 0.0,
      "loss_threshold_exceeded": false,
      "symbol_retention_rate": 1.0
     }
    },
    "rag": {
     "tokens": 98,
     "latency_ms": 563.88,
     "quality": {
      "granularity_tag": "turn",
      "retrieved": 3,
      "stale_flags": 0
     }
    }
   },
   "prompt": {
    "tokens": 227,
    "context": "user: I'm making a small platformer in pygame. How do I organise the update loop?\nassistant: Fixed timestep: accumulate frame time and step physics in 1/120 s increments, render once per frame with interpolation. Entities hold position, velocity and a collider.\nuser: Write the physics step.\nassistant: ```python\nGRAVITY = 980\n\ndef apply_physics(entity, dt):\n    entity.vy += GRAVITY * dt\n    entity.x += entity.vx * dt\n    entity.y += entity.vy * dt\n```\nuser: Jumping feels floaty.\nassistant: Stronger gravity and a cap on fall speed:\n```python\nGRAVITY = 1800\n```\nand clamp `vy` to 900.\nuser: Rename the physics function, we now have a separate collision pass so it only integrates motion.\nassistant: ```python\ndef integrate_motion(entity, dt):\n    entity.vy = min(entity.vy + GRAVITY * dt, 900)\n    entity.x += entity.vx * dt\n    entity.y += entity.vy * dt\n```",
    "truncated": false
   },
   "raised": [],
   "traps": []
  },
  {
   "exchange": 6,
   "turn_id": "t0011",
   "user": "Add coyote time and jump buffering.",
   "assistant": "Allow a jump up to 0.1 s after leaving a ledge and remember a jump press for 0.12 s before landing.",
   "signal": {
    "turn_count": 11,
    "task_type": "code_refactor",
    "matched_pattern": "carry_over",
    "topic_similarity": 0.341,
    "shift": false,
    "recall_request": false,
    "tokens_used": 277,
    "budget": 700
   },
   "features": {
    "turn_count": 11,
    "token_budget_pressure": 0.3957,
    "task_type": "code_refactor",
    "prior_strategy": "sliding_window",
    "time_since_last_switch": 4
   },
   "rules": [
    {
     "fn": "fits",
     "matched": true,
     "fired": true,
     "rule": "history_fits",
     "strategy": "sliding_window",
     "hard": false,
     "reason": "token pressure 0.40 < 0.90: full recent history fits, window is lossless"
    },
    {
     "fn": "qa",
     "matched": false,
     "fired": false,
     "rule": null,
     "strategy": null,
     "hard": null,
     "reason": null
    },
    {
     "fn": "build",
     "matched": false,
     "fired": false,
     "rule": null,
     "strategy": null,
     "hard": null,
     "reason": null
    },
    {
     "fn": "refactor",
     "matched": true,
     "fired": false,
     "rule": "refactor_request",
     "strategy": "summarization",
     "hard": true,
     "reason": "task_type=code_refactor -> summarization: merged L1 symbol table carries current signatures and renames"
    },
    {
     "fn": "debug",
     "matched": false,
     "fired": false,
     "rule": null,
     "strategy": null,
     "hard": null,
     "reason": null
    },
    {
     "fn": "recall_request",
     "matched": false,
     "fired": false,
     "rule": null,
     "strategy": null,
     "hard": null,
     "reason": null
    },
    {
     "fn": "long_open",
     "matched": false,
     "fired": false,
     "rule": null,
     "strategy": null,
     "hard": null,
     "reason": null
    }
   ],
   "decision": {
    "strategy": "sliding_window",
    "latency_ms": 0.0747,
    "override": [],
    "full": "[history_fits] token pressure 0.40 < 0.90: full recent history fits, window is lossless | features: turn=11, pressure=0.40, task=code_refactor, prior=sliding_window, since_switch=4",
    "rule": "history_fits",
    "rule_reason": "token pressure 0.40 < 0.90: full recent history fits, window is lossless",
    "dwell": [],
    "escalations": []
   },
   "candidates": {
    "sliding_window": {
     "tokens": 267,
     "latency_ms": 0.52,
     "quality": {
      "kept": 10,
      "relevance": 0.242,
      "freshness": 0.698,
      "importance": 0.185,
      "state": 1.0,
      "composite": 0.531
     }
    },
    "summarization": {
     "tokens": 294,
     "latency_ms": 1.23,
     "quality": {
      "tier_emitted": "L1",
      "loss_score": 0.0,
      "loss_threshold_exceeded": false,
      "symbol_retention_rate": 1.0
     }
    },
    "rag": {
     "tokens": 307,
     "latency_ms": 451.78,
     "quality": {
      "granularity_tag": "turn",
      "retrieved": 7,
      "stale_flags": 0
     }
    }
   },
   "prompt": {
    "tokens": 269,
    "context": "user: I'm making a small platformer in pygame. How do I organise the update loop?\nassistant: Fixed timestep: accumulate frame time and step physics in 1/120 s increments, render once per frame with interpolation. Entities hold position, velocity and a collider.\nuser: Write the physics step.\nassistant: ```python\nGRAVITY = 980\n\ndef apply_physics(entity, dt):\n    entity.vy += GRAVITY * dt\n    entity.x += entity.vx * dt\n    entity.y += entity.vy * dt\n```\nuser: Jumping feels floaty.\nassistant: Stronger gravity and a cap on fall speed:\n```python\nGRAVITY = 1800\n```\nand clamp `vy` to 900.\nuser: Rename the physics function, we now have a separate collision pass so it only integrates motion.\nassistant: ```python\ndef integrate_motion(entity, dt):\n    entity.vy = min(entity.vy + GRAVITY * dt, 900)\n    entity.x += entity.vx * dt\n    entity.y += entity.vy * dt\n```\nuser: Collision with tiles?\nassistant: Resolve axes separately: move on x, push out of overlapping tiles, then the same on y, and set `on_ground` when a downward move is blocked.",
    "truncated": false
   },
   "raised": [],
   "traps": []
  },
  {
   "exchange": 7,
   "turn_id": "t0013",
   "user": "Load levels from Tiled.",
   "assistant": "pytmx loads .tmx maps; tile layers become collision rects, the object layer spawns enemies and pickups by type.",
   "signal": {
    "turn_count": 13,
    "task_type": "chat",
    "matched_pattern": "shift_default",
    "topic_similarity": 0.138,
    "shift": true,
    "recall_request": false,
    "tokens_used": 315,
    "budget": 700
   },
   "features": {
    "turn_count": 13,
    "token_budget_pressure": 0.45,
    "task_type": "chat",
    "prior_strategy": "sliding_window",
    "time_since_last_switch": 5
   },
   "rules": [
    {
     "fn": "fits",
     "matched": true,
     "fired": true,
     "rule": "history_fits",
     "strategy": "sliding_window",
     "hard": false,
     "reason": "token pressure 0.45 < 0.90: full recent history fits, window is lossless"
    },
    {
     "fn": "qa",
     "matched": false,
     "fired": false,
     "rule": null,
     "strategy": null,
     "hard": null,
     "reason": null
    },
    {
     "fn": "build",
     "matched": false,
     "fired": false,
     "rule": null,
     "strategy": null,
     "hard": null,
     "reason": null
    },
    {
     "fn": "refactor",
     "matched": false,
     "fired": false,
     "rule": null,
     "strategy": null,
     "hard": null,
     "reason": null
    },
    {
     "fn": "debug",
     "matched": false,
     "fired": false,
     "rule": null,
     "strategy": null,
     "hard": null,
     "reason": null
    },
    {
     "fn": "recall_request",
     "matched": false,
     "fired": false,
     "rule": null,
     "strategy": null,
     "hard": null,
     "reason": null
    },
    {
     "fn": "long_open",
     "matched": false,
     "fired": false,
     "rule": null,
     "strategy": null,
     "hard": null,
     "reason": null
    }
   ],
   "decision": {
    "strategy": "sliding_window",
    "latency_ms": 0.0562,
    "override": [],
    "full": "[history_fits] token pressure 0.45 < 0.90: full recent history fits, window is lossless | features: turn=13, pressure=0.45, task=chat, prior=sliding_window, since_switch=5",
    "rule": "history_fits",
    "rule_reason": "token pressure 0.45 < 0.90: full recent history fits, window is lossless",
    "dwell": [],
    "escalations": []
   },
   "candidates": {
    "sliding_window": {
     "tokens": 307,
     "latency_ms": 0.47,
     "quality": {
      "kept": 12,
      "relevance": 0.105,
      "freshness": 0.649,
      "importance": 0.163,
      "state": 0.5,
      "composite": 0.354
     }
    },
    "summarization": {
     "tokens": 334,
     "latency_ms": 1.37,
     "quality": {
      "tier_emitted": "L1",
      "loss_score": 0.0,
      "loss_threshold_exceeded": false,
      "symbol_retention_rate": 1.0
     }
    },
    "rag": {
     "tokens": 81,
     "latency_ms": 368.83,
     "quality": {
      "granularity_tag": "segment",
      "retrieved": 2,
      "stale_flags": 0
     }
    }
   },
   "prompt": {
    "tokens": 309,
    "context": "user: I'm making a small platformer in pygame. How do I organise the update loop?\nassistant: Fixed timestep: accumulate frame time and step physics in 1/120 s increments, render once per frame with interpolation. Entities hold position, velocity and a collider.\nuser: Write the physics step.\nassistant: ```python\nGRAVITY = 980\n\ndef apply_physics(entity, dt):\n    entity.vy += GRAVITY * dt\n    entity.x += entity.vx * dt\n    entity.y += entity.vy * dt\n```\nuser: Jumping feels floaty.\nassistant: Stronger gravity and a cap on fall speed:\n```python\nGRAVITY = 1800\n```\nand clamp `vy` to 900.\nuser: Rename the physics function, we now have a separate collision pass so it only integrates motion.\nassistant: ```python\ndef integrate_motion(entity, dt):\n    entity.vy = min(entity.vy + GRAVITY * dt, 900)\n    entity.x += entity.vx * dt\n    entity.y += entity.vy * dt\n```\nuser: Collision with tiles?\nassistant: Resolve axes separately: move on x, push out of overlapping tiles, then the same on y, and set `on_ground` when a downward move is blocked.\nuser: Add coyote time and jump buffering.\nassistant: Allow a jump up to 0.1 s after leaving a ledge and remember a jump press for 0.12 s before landing.",
    "truncated": false
   },
   "raised": [],
   "traps": []
  },
  {
   "exchange": 8,
   "turn_id": "t0015",
   "user": "Add a camera that follows the player.",
   "assistant": "A dead-zone camera with smoothing, clamped to level bounds, and a look-ahead in the facing direction.",
   "signal": {
    "turn_count": 15,
    "task_type": "chat",
    "matched_pattern": "shift_default",
    "topic_similarity": 0.011,
    "shift": true,
    "recall_request": false,
    "tokens_used": 352,
    "budget": 700
   },
   "features": {
    "turn_count": 15,
    "token_budget_pressure": 0.5029,
    "task_type": "chat",
    "prior_strategy": "sliding_window",
    "time_since_last_switch": 6
   },
   "rules": [
    {
     "fn": "fits",
     "matched": true,
     "fired": true,
     "rule": "history_fits",
     "strategy": "sliding_window",
     "hard": false,
     "reason": "token pressure 0.50 < 0.90: full recent history fits, window is lossless"
    },
    {
     "fn": "qa",
     "matched": false,
     "fired": false,
     "rule": null,
     "strategy": null,
     "hard": null,
     "reason": null
    },
    {
     "fn": "build",
     "matched": false,
     "fired": false,
     "rule": null,
     "strategy": null,
     "hard": null,
     "reason": null
    },
    {
     "fn": "refactor",
     "matched": false,
     "fired": false,
     "rule": null,
     "strategy": null,
     "hard": null,
     "reason": null
    },
    {
     "fn": "debug",
     "matched": false,
     "fired": false,
     "rule": null,
     "strategy": null,
     "hard": null,
     "reason": null
    },
    {
     "fn": "recall_request",
     "matched": false,
     "fired": false,
     "rule": null,
     "strategy": null,
     "hard": null,
     "reason": null
    },
    {
     "fn": "long_open",
     "matched": false,
     "fired": false,
     "rule": null,
     "strategy": null,
     "hard": null,
     "reason": null
    }
   ],
   "decision": {
    "strategy": "sliding_window",
    "latency_ms": 0.0662,
    "override": [],
    "full": "[history_fits] token pressure 0.50 < 0.90: full recent history fits, window is lossless | features: turn=15, pressure=0.50, task=chat, prior=sliding_window, since_switch=6",
    "rule": "history_fits",
    "rule_reason": "token pressure 0.50 < 0.90: full recent history fits, window is lossless",
    "dwell": [],
    "escalations": []
   },
   "candidates": {
    "sliding_window": {
     "tokens": 307,
     "latency_ms": 0.46,
     "quality": {
      "kept": 11,
      "relevance": 0.093,
      "freshness": 0.663,
      "importance": 0.177,
      "state": 0.295,
      "composite": 0.307
     }
    },
    "summarization": {
     "tokens": 369,
     "latency_ms": 1.47,
     "quality": {
      "tier_emitted": "L1",
      "loss_score": 0.0,
      "loss_threshold_exceeded": false,
      "symbol_retention_rate": 1.0
     }
    },
    "rag": {
     "tokens": 95,
     "latency_ms": 302.92,
     "quality": {
      "granularity_tag": "segment",
      "retrieved": 2,
      "stale_flags": 0
     }
    }
   },
   "prompt": {
    "tokens": 309,
    "context": "assistant: Fixed timestep: accumulate frame time and step physics in 1/120 s increments, render once per frame with interpolation. Entities hold position, velocity and a collider.\nassistant: ```python\nGRAVITY = 980\n\ndef apply_physics(entity, dt):\n    entity.vy += GRAVITY * dt\n    entity.x += entity.vx * dt\n    entity.y += entity.vy * dt\n```\nassistant: Stronger gravity and a cap on fall speed:\n```python\nGRAVITY = 1800\n```\nand clamp `vy` to 900.\nuser: Rename the physics function, we now have a separate collision pass so it only integrates motion.\nassistant: ```python\ndef integrate_motion(entity, dt):\n    entity.vy = min(entity.vy + GRAVITY * dt, 900)\n    entity.x += entity.vx * dt\n    entity.y += entity.vy * dt\n```\nuser: Collision with tiles?\nassistant: Resolve axes separately: move on x, push out of overlapping tiles, then the same on y, and set `on_ground` when a downward move is blocked.\nuser: Add coyote time and jump buffering.\nassistant: Allow a jump up to 0.1 s after leaving a ledge and remember a jump press for 0.12 s before landing.\nuser: Load levels from Tiled.\nassistant: pytmx loads .tmx maps; tile layers become collision rects, the object layer spawns enemies and pickups by type.",
    "truncated": false
   },
   "raised": [],
   "traps": []
  },
  {
   "exchange": 9,
   "turn_id": "t0017",
   "user": "Sound effects?",
   "assistant": "Preload with `pygame.mixer.Sound`, play jumps and pickups on separate channels, and duck the music during dialogue.",
   "signal": {
    "turn_count": 17,
    "task_type": "chat",
    "matched_pattern": "shift_default",
    "topic_similarity": 0.11,
    "shift": true,
    "recall_request": false,
    "tokens_used": 381,
    "budget": 700
   },
   "features": {
    "turn_count": 17,
    "token_budget_pressure": 0.5443,
    "task_type": "chat",
    "prior_strategy": "sliding_window",
    "time_since_last_switch": 7
   },
   "rules": [
    {
     "fn": "fits",
     "matched": true,
     "fired": true,
     "rule": "history_fits",
     "strategy": "sliding_window",
     "hard": false,
     "reason": "token pressure 0.54 < 0.90: full recent history fits, window is lossless"
    },
    {
     "fn": "qa",
     "matched": false,
     "fired": false,
     "rule": null,
     "strategy": null,
     "hard": null,
     "reason": null
    },
    {
     "fn": "build",
     "matched": false,
     "fired": false,
     "rule": null,
     "strategy": null,
     "hard": null,
     "reason": null
    },
    {
     "fn": "refactor",
     "matched": false,
     "fired": false,
     "rule": null,
     "strategy": null,
     "hard": null,
     "reason": null
    },
    {
     "fn": "debug",
     "matched": false,
     "fired": false,
     "rule": null,
     "strategy": null,
     "hard": null,
     "reason": null
    },
    {
     "fn": "recall_request",
     "matched": false,
     "fired": false,
     "rule": null,
     "strategy": null,
     "hard": null,
     "reason": null
    },
    {
     "fn": "long_open",
     "matched": false,
     "fired": false,
     "rule": null,
     "strategy": null,
     "hard": null,
     "reason": null
    }
   ],
   "decision": {
    "strategy": "sliding_window",
    "latency_ms": 0.0836,
    "override": [],
    "full": "[history_fits] token pressure 0.54 < 0.90: full recent history fits, window is lossless | features: turn=17, pressure=0.54, task=chat, prior=sliding_window, since_switch=7",
    "rule": "history_fits",
    "rule_reason": "token pressure 0.54 < 0.90: full recent history fits, window is lossless",
    "dwell": [],
    "escalations": []
   },
   "candidates": {
    "sliding_window": {
     "tokens": 245,
     "latency_ms": 0.46,
     "quality": {
      "kept": 9,
      "relevance": 0.1,
      "freshness": 0.684,
      "importance": 0.2,
      "state": 0.236,
      "composite": 0.305
     }
    },
    "summarization": {
     "tokens": 361,
     "latency_ms": 1.8,
     "quality": {
      "tier_emitted": "L1",
      "loss_score": 0.0,
      "loss_threshold_exceeded": false,
      "symbol_retention_rate": 1.0
     }
    },
    "rag": {
     "tokens": 130,
     "latency_ms": 253.89,
     "quality": {
      "granularity_tag": "turn",
      "retrieved": 3,
      "stale_flags": 0
     }
    }
   },
   "prompt": {
    "tokens": 247,
    "context": "assistant: ```python\nGRAVITY = 980\n\ndef apply_physics(entity, dt):\n    entity.vy += GRAVITY * dt\n    entity.x += entity.vx * dt\n    entity.y += entity.vy * dt\n```\nassistant: Stronger gravity and a cap on fall speed:\n```python\nGRAVITY = 1800\n```\nand clamp `vy` to 900.\nassistant: ```python\ndef integrate_motion(entity, dt):\n    entity.vy = min(entity.vy + GRAVITY * dt, 900)\n    entity.x += entity.vx * dt\n    entity.y += entity.vy * dt\n```\nuser: Add coyote time and jump buffering.\nassistant: Allow a jump up to 0.1 s after leaving a ledge and remember a jump press for 0.12 s before landing.\nuser: Load levels from Tiled.\nassistant: pytmx loads .tmx maps; tile layers become collision rects, the object layer spawns enemies and pickups by type.\nuser: Add a camera that follows the player.\nassistant: A dead-zone camera with smoothing, clamped to level bounds, and a look-ahead in the facing direction.",
    "truncated": false
   },
   "raised": [],
   "traps": []
  },
  {
   "exchange": 10,
   "turn_id": "t0019",
   "user": "Write the enemy update that runs the motion integration for each enemy every step.",
   "assistant": "(scripted reply omitted - the check is on the context the model would receive)",
   "signal": {
    "turn_count": 19,
    "task_type": "chat",
    "matched_pattern": "shift_default",
    "topic_similarity": 0.097,
    "shift": true,
    "recall_request": false,
    "tokens_used": 423,
    "budget": 700
   },
   "features": {
    "turn_count": 19,
    "token_budget_pressure": 0.6043,
    "task_type": "chat",
    "prior_strategy": "sliding_window",
    "time_since_last_switch": 8
   },
   "rules": [
    {
     "fn": "fits",
     "matched": true,
     "fired": true,
     "rule": "history_fits",
     "strategy": "sliding_window",
     "hard": false,
     "reason": "token pressure 0.60 < 0.90: full recent history fits, window is lossless"
    },
    {
     "fn": "qa",
     "matched": false,
     "fired": false,
     "rule": null,
     "strategy": null,
     "hard": null,
     "reason": null
    },
    {
     "fn": "build",
     "matched": false,
     "fired": false,
     "rule": null,
     "strategy": null,
     "hard": null,
     "reason": null
    },
    {
     "fn": "refactor",
     "matched": false,
     "fired": false,
     "rule": null,
     "strategy": null,
     "hard": null,
     "reason": null
    },
    {
     "fn": "debug",
     "matched": false,
     "fired": false,
     "rule": null,
     "strategy": null,
     "hard": null,
     "reason": null
    },
    {
     "fn": "recall_request",
     "matched": false,
     "fired": false,
     "rule": null,
     "strategy": null,
     "hard": null,
     "reason": null
    },
    {
     "fn": "long_open",
     "matched": false,
     "fired": false,
     "rule": null,
     "strategy": null,
     "hard": null,
     "reason": null
    }
   ],
   "decision": {
    "strategy": "sliding_window",
    "latency_ms": 0.0676,
    "override": [],
    "full": "[history_fits] token pressure 0.60 < 0.90: full recent history fits, window is lossless | features: turn=19, pressure=0.60, task=chat, prior=sliding_window, since_switch=8",
    "rule": "history_fits",
    "rule_reason": "token pressure 0.60 < 0.90: full recent history fits, window is lossless",
    "dwell": [],
    "escalations": []
   },
   "candidates": {
    "sliding_window": {
     "tokens": 331,
     "latency_ms": 0.47,
     "quality": {
      "kept": 13,
      "relevance": 0.274,
      "freshness": 0.606,
      "importance": 0.131,
      "state": 0.168,
      "composite": 0.295
     }
    },
    "summarization": {
     "tokens": 391,
     "latency_ms": 1.9,
     "quality": {
      "tier_emitted": "L1",
      "loss_score": 0.0,
      "loss_threshold_exceeded": false,
      "symbol_retention_rate": 1.0
     }
    },
    "rag": {
     "tokens": 423,
     "latency_ms": 242.88,
     "quality": {
      "granularity_tag": "turn",
      "retrieved": 10,
      "stale_flags": 0
     }
    }
   },
   "prompt": {
    "tokens": 333,
    "context": "assistant: Fixed timestep: accumulate frame time and step physics in 1/120 s increments, render once per frame with interpolation. Entities hold position, velocity and a collider.\nassistant: ```python\nGRAVITY = 980\n\ndef apply_physics(entity, dt):\n    entity.vy += GRAVITY * dt\n    entity.x += entity.vx * dt\n    entity.y += entity.vy * dt\n```\nuser: Rename the physics function, we now have a separate collision pass so it only integrates motion.\nassistant: ```python\ndef integrate_motion(entity, dt):\n    entity.vy = min(entity.vy + GRAVITY * dt, 900)\n    entity.x += entity.vx * dt\n    entity.y += entity.vy * dt\n```\nassistant: Resolve axes separately: move on x, push out of overlapping tiles, then the same on y, and set `on_ground` when a downward move is blocked.\nuser: Add coyote time and jump buffering.\nassistant: Allow a jump up to 0.1 s after leaving a ledge and remember a jump press for 0.12 s before landing.\nuser: Load levels from Tiled.\nassistant: pytmx loads .tmx maps; tile layers become collision rects, the object layer spawns enemies and pickups by type.\nuser: Add a camera that follows the player.\nassistant: A dead-zone camera with smoothing, clamped to level bounds, and a look-ahead in the facing direction.\nuser: Sound effects?\nassistant: Preload with `pygame.mixer.Sound`, play jumps and pickups on separate channels, and duck the music during dialogue.",
    "truncated": false
   },
   "raised": [],
   "traps": [
    {
     "name": "renamed physics function",
     "description": "apply_physics renamed to integrate_motion at exchange 4",
     "planted_at": 4,
     "kind": "rename",
     "adaptive": {
      "caught": false,
      "detail": "unmarked stale `def apply_physics(` present",
      "strategy": "sliding_window"
     },
     "fixed_6_exchange_window": {
      "caught": true,
      "detail": "found `def integrate_motion(`"
     },
     "sliding_window": {
      "caught": false,
      "detail": "unmarked stale `def apply_physics(` present"
     },
     "summarization": {
      "caught": false,
      "detail": "unmarked stale `def apply_physics(` present"
     },
     "rag": {
      "caught": false,
      "detail": "unmarked stale `def apply_physics(` present"
     },
     "hybrid": {
      "caught": false,
      "detail": "unmarked stale `def apply_physics(` present"
     }
    }
   ]
  },
  {
   "exchange": 11,
   "turn_id": "t0021",
   "user": "What gravity value does the game use? The level designer needs it for jump heights.",
   "assistant": "(scripted reply omitted - the check is on the context the model would receive)",
   "signal": {
    "turn_count": 21,
    "task_type": "chat",
    "matched_pattern": "shift_default",
    "topic_similarity": 0.096,
    "shift": true,
    "recall_request": false,
    "tokens_used": 461,
    "budget": 700
   },
   "features": {
    "turn_count": 21,
    "token_budget_pressure": 0.6586,
    "task_type": "chat",
    "prior_strategy": "sliding_window",
    "time_since_last_switch": 9
   },
   "rules": [
    {
     "fn": "fits",
     "matched": true,
     "fired": true,
     "rule": "history_fits",
     "strategy": "sliding_window",
     "hard": false,
     "reason": "token pressure 0.66 < 0.90: full recent history fits, window is lossless"
    },
    {
     "fn": "qa",
     "matched": false,
     "fired": false,
     "rule": null,
     "strategy": null,
     "hard": null,
     "reason": null
    },
    {
     "fn": "build",
     "matched": false,
     "fired": false,
     "rule": null,
     "strategy": null,
     "hard": null,
     "reason": null
    },
    {
     "fn": "refactor",
     "matched": false,
     "fired": false,
     "rule": null,
     "strategy": null,
     "hard": null,
     "reason": null
    },
    {
     "fn": "debug",
     "matched": false,
     "fired": false,
     "rule": null,
     "strategy": null,
     "hard": null,
     "reason": null
    },
    {
     "fn": "recall_request",
     "matched": false,
     "fired": false,
     "rule": null,
     "strategy": null,
     "hard": null,
     "reason": null
    },
    {
     "fn": "long_open",
     "matched": false,
     "fired": false,
     "rule": null,
     "strategy": null,
     "hard": null,
     "reason": null
    }
   ],
   "decision": {
    "strategy": "sliding_window",
    "latency_ms": 0.0557,
    "override": [],
    "full": "[history_fits] token pressure 0.66 < 0.90: full recent history fits, window is lossless | features: turn=21, pressure=0.66, task=chat, prior=sliding_window, since_switch=9",
    "rule": "history_fits",
    "rule_reason": "token pressure 0.66 < 0.90: full recent history fits, window is lossless",
    "dwell": [],
    "escalations": []
   },
   "candidates": {
    "sliding_window": {
     "tokens": 264,
     "latency_ms": 0.47,
     "quality": {
      "kept": 10,
      "relevance": 0.236,
      "freshness": 0.618,
      "importance": 0.185,
      "state": 0.181,
      "composite": 0.305
     }
    },
    "summarization": {
     "tokens": 427,
     "latency_ms": 2.14,
     "quality": {
      "tier_emitted": "L1",
      "loss_score": 0.0,
      "loss_threshold_exceeded": false,
      "symbol_retention_rate": 1.0
     }
    },
    "rag": {
     "tokens": 416,
     "latency_ms": 230.07,
     "quality": {
      "granularity_tag": "turn",
      "retrieved": 9,
      "stale_flags": 0
     }
    }
   },
   "prompt": {
    "tokens": 266,
    "context": "assistant: ```python\nGRAVITY = 980\n\ndef apply_physics(entity, dt):\n    entity.vy += GRAVITY * dt\n    entity.x += entity.vx * dt\n    entity.y += entity.vy * dt\n```\nassistant: Stronger gravity and a cap on fall speed:\n```python\nGRAVITY = 1800\n```\nand clamp `vy` to 900.\nassistant: ```python\ndef integrate_motion(entity, dt):\n    entity.vy = min(entity.vy + GRAVITY * dt, 900)\n    entity.x += entity.vx * dt\n    entity.y += entity.vy * dt\n```\nassistant: Allow a jump up to 0.1 s after leaving a ledge and remember a jump press for 0.12 s before landing.\nuser: Load levels from Tiled.\nassistant: A dead-zone camera with smoothing, clamped to level bounds, and a look-ahead in the facing direction.\nuser: Sound effects?\nassistant: Preload with `pygame.mixer.Sound`, play jumps and pickups on separate channels, and duck the music during dialogue.\nuser: Write the enemy update that runs the motion integration for each enemy every step.\nassistant: (scripted reply omitted - the check is on the context the model would receive)",
    "truncated": false
   },
   "raised": [],
   "traps": [
    {
     "name": "changed gravity",
     "description": "GRAVITY changed 980 -> 1800 at exchange 3",
     "planted_at": 3,
     "kind": "config",
     "adaptive": {
      "caught": false,
      "detail": "unmarked stale `GRAVITY = 980` present",
      "strategy": "sliding_window"
     },
     "fixed_6_exchange_window": {
      "caught": false,
      "detail": "missing `GRAVITY = 1800`"
     },
     "sliding_window": {
      "caught": false,
      "detail": "unmarked stale `GRAVITY = 980` present"
     },
     "summarization": {
      "caught": false,
      "detail": "missing `GRAVITY = 1800`"
     },
     "rag": {
      "caught": false,
      "detail": "unmarked stale `GRAVITY = 980` present"
     },
     "hybrid": {
      "caught": false,
      "detail": "unmarked stale `GRAVITY = 980` present"
     }
    }
   ]
  }
 ]
};
