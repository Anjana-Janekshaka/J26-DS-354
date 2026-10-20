window.CEAI_SESSIONS = window.CEAI_SESSIONS || {};
window.CEAI_SESSIONS["short-utils--control"] = {
 "scenario": "short-utils (control)",
 "slug": "short-utils--control",
 "language": "python",
 "held_out": true,
 "system": "frozen",
 "mode": "full",
 "budget": 700,
 "recorded_at": "2026-10-19T11:24:55+00:00",
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
 "n_traps": 1,
 "score": {
  "adaptive": 0,
  "fixed_6_exchange_window": 0,
  "sliding_window": 0,
  "summarization": 0,
  "rag": 0,
  "hybrid": 0
 },
 "turns": [
  {
   "exchange": 1,
   "turn_id": "t0001",
   "user": "Write a helper that chunks a list into batches of n.",
   "assistant": "```python\ndef batched(items, n):\n    for i in range(0, len(items), n):\n        yield items[i:i + n]\n```",
   "signal": {
    "turn_count": 1,
    "task_type": "code_generation",
    "matched_pattern": "pattern:code_generation",
    "topic_similarity": null,
    "shift": false,
    "recall_request": false,
    "tokens_used": 14,
    "budget": 700
   },
   "features": {
    "turn_count": 1,
    "token_budget_pressure": 0.02,
    "task_type": "code_generation",
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
     "reason": "token pressure 0.02 < 0.90: full recent history fits, window is lossless"
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
     "matched": true,
     "fired": false,
     "rule": "build_request",
     "strategy": "hybrid",
     "hard": true,
     "reason": "task_type=code_generation (build-request pattern) -> hybrid: recent window + RAG to surface existing definitions before writing new code"
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
    "latency_ms": 0.0944,
    "override": [],
    "full": "[history_fits] token pressure 0.02 < 0.90: full recent history fits, window is lossless | features: turn=1, pressure=0.02, task=code_generation, prior=None, since_switch=0",
    "rule": "history_fits",
    "rule_reason": "token pressure 0.02 < 0.90: full recent history fits, window is lossless",
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
     "latency_ms": 1.16,
     "quality": {
      "tier_emitted": "L1",
      "loss_score": 0.0,
      "loss_threshold_exceeded": false,
      "symbol_retention_rate": null
     }
    },
    "rag": {
     "tokens": 0,
     "latency_ms": 0.83,
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
   "user": "Make it accept any iterable, not just lists.",
   "assistant": "```python\ndef batched(iterable, n):\n    it = iter(iterable)\n    while chunk := list(islice(it, n)):\n        yield chunk\n```",
   "signal": {
    "turn_count": 3,
    "task_type": "code_generation",
    "matched_pattern": "carry_over",
    "topic_similarity": null,
    "shift": false,
    "recall_request": false,
    "tokens_used": 60,
    "budget": 700
   },
   "features": {
    "turn_count": 3,
    "token_budget_pressure": 0.0857,
    "task_type": "code_generation",
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
     "matched": true,
     "fired": false,
     "rule": "build_request",
     "strategy": "hybrid",
     "hard": true,
     "reason": "task_type=code_generation (build-request pattern) -> hybrid: recent window + RAG to surface existing definitions before writing new code"
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
    "latency_ms": 0.0716,
    "override": [],
    "full": "[history_fits] token pressure 0.09 < 0.90: full recent history fits, window is lossless | features: turn=3, pressure=0.09, task=code_generation, prior=sliding_window, since_switch=0",
    "rule": "history_fits",
    "rule_reason": "token pressure 0.09 < 0.90: full recent history fits, window is lossless",
    "dwell": [],
    "escalations": []
   },
   "candidates": {
    "sliding_window": {
     "tokens": 48,
     "latency_ms": 0.72,
     "quality": {
      "kept": 2,
      "relevance": 0.399,
      "freshness": 0.959,
      "importance": 0.325,
      "state": 1.0,
      "composite": 0.671
     }
    },
    "summarization": {
     "tokens": 52,
     "latency_ms": 1.11,
     "quality": {
      "tier_emitted": "L1",
      "loss_score": 0.0,
      "loss_threshold_exceeded": false,
      "symbol_retention_rate": 1.0
     }
    },
    "rag": {
     "tokens": 65,
     "latency_ms": 1.3,
     "quality": {
      "granularity_tag": "turn",
      "retrieved": 2,
      "stale_flags": 0
     }
    }
   },
   "prompt": {
    "tokens": 48,
    "context": "user: Write a helper that chunks a list into batches of n.\nassistant: ```python\ndef batched(items, n):\n    for i in range(0, len(items), n):\n        yield items[i:i + n]\n```",
    "truncated": false
   },
   "raised": [],
   "traps": []
  },
  {
   "exchange": 3,
   "turn_id": "t0005",
   "user": "Use it to send user ids to the API 100 at a time.",
   "assistant": "(scripted reply omitted - the check is on the context the model would receive)",
   "signal": {
    "turn_count": 5,
    "task_type": "code_generation",
    "matched_pattern": "carry_over",
    "topic_similarity": null,
    "shift": false,
    "recall_request": false,
    "tokens_used": 113,
    "budget": 700
   },
   "features": {
    "turn_count": 5,
    "token_budget_pressure": 0.1614,
    "task_type": "code_generation",
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
     "reason": "token pressure 0.16 < 0.90: full recent history fits, window is lossless"
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
     "matched": true,
     "fired": false,
     "rule": "build_request",
     "strategy": "hybrid",
     "hard": true,
     "reason": "task_type=code_generation (build-request pattern) -> hybrid: recent window + RAG to surface existing definitions before writing new code"
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
    "latency_ms": 0.0666,
    "override": [],
    "full": "[history_fits] token pressure 0.16 < 0.90: full recent history fits, window is lossless | features: turn=5, pressure=0.16, task=code_generation, prior=sliding_window, since_switch=1",
    "rule": "history_fits",
    "rule_reason": "token pressure 0.16 < 0.90: full recent history fits, window is lossless",
    "dwell": [],
    "escalations": []
   },
   "candidates": {
    "sliding_window": {
     "tokens": 96,
     "latency_ms": 0.66,
     "quality": {
      "kept": 4,
      "relevance": 0.036,
      "freshness": 0.882,
      "importance": 0.312,
      "state": 1.0,
      "composite": 0.558
     }
    },
    "summarization": {
     "tokens": 101,
     "latency_ms": 1.06,
     "quality": {
      "tier_emitted": "L1",
      "loss_score": 0.0,
      "loss_threshold_exceeded": false,
      "symbol_retention_rate": 1.0
     }
    },
    "rag": {
     "tokens": 0,
     "latency_ms": 1.69,
     "quality": {
      "granularity_tag": "turn",
      "retrieved": 0,
      "stale_flags": 0
     }
    }
   },
   "prompt": {
    "tokens": 97,
    "context": "user: Write a helper that chunks a list into batches of n.\nassistant: ```python\ndef batched(items, n):\n    for i in range(0, len(items), n):\n        yield items[i:i + n]\n```\nuser: Make it accept any iterable, not just lists.\nassistant: ```python\ndef batched(iterable, n):\n    it = iter(iterable)\n    while chunk := list(islice(it, n)):\n        yield chunk\n```",
    "truncated": false
   },
   "raised": [],
   "traps": [
    {
     "name": "recent rename (control)",
     "description": "a change one exchange back; any reasonable memory should carry it",
     "planted_at": 2,
     "kind": "rename",
     "adaptive": {
      "caught": false,
      "detail": "unmarked stale `def batched(items, n)` present",
      "strategy": "sliding_window"
     },
     "fixed_6_exchange_window": {
      "caught": false,
      "detail": "unmarked stale `def batched(items, n)` present"
     },
     "sliding_window": {
      "caught": false,
      "detail": "unmarked stale `def batched(items, n)` present"
     },
     "summarization": {
      "caught": false,
      "detail": "unmarked stale `def batched(items, n)` present"
     },
     "rag": {
      "caught": false,
      "detail": "missing `def batched(iterable, n)`"
     },
     "hybrid": {
      "caught": false,
      "detail": "unmarked stale `def batched(items, n)` present"
     }
    }
   ]
  }
 ]
};
