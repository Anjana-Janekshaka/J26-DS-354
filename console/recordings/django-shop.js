window.CEAI_SESSIONS = window.CEAI_SESSIONS || {};
window.CEAI_SESSIONS["django-shop"] = {
 "scenario": "django-shop",
 "slug": "django-shop",
 "language": "python",
 "held_out": true,
 "system": "frozen",
 "mode": "full",
 "budget": 700,
 "recorded_at": "2026-10-19T11:22:55+00:00",
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
  "adaptive": 2,
  "fixed_6_exchange_window": 0,
  "sliding_window": 2,
  "summarization": 2,
  "rag": 2,
  "hybrid": 2
 },
 "turns": [
  {
   "exchange": 1,
   "turn_id": "t0001",
   "user": "We're adding a product catalogue to our Django shop. Quick plan?",
   "assistant": "A `catalog` app with Product and Category models, a list view with filters, a detail view, and an admin with search. Slugs in URLs, prices handled carefully.",
   "signal": {
    "turn_count": 1,
    "task_type": "chat",
    "matched_pattern": "carry_over",
    "topic_similarity": null,
    "shift": false,
    "recall_request": false,
    "tokens_used": 16,
    "budget": 700
   },
   "features": {
    "turn_count": 1,
    "token_budget_pressure": 0.0229,
    "task_type": "chat",
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
    "latency_ms": 0.0677,
    "override": [],
    "full": "[history_fits] token pressure 0.02 < 0.90: full recent history fits, window is lossless | features: turn=1, pressure=0.02, task=chat, prior=None, since_switch=0",
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
     "latency_ms": 1.08,
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
   "user": "Ground rule before any model code: how do we store money?",
   "assistant": "Never floats. Every price field is `models.DecimalField(max_digits=10, decimal_places=2)` and every calculation uses `Decimal`; this applies to carts, discounts and tax as well.",
   "signal": {
    "turn_count": 3,
    "task_type": "exploration",
    "matched_pattern": "pattern:exploration",
    "topic_similarity": null,
    "shift": false,
    "recall_request": false,
    "tokens_used": 69,
    "budget": 700
   },
   "features": {
    "turn_count": 3,
    "token_budget_pressure": 0.0986,
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
     "reason": "token pressure 0.10 < 0.90: full recent history fits, window is lossless"
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
    "latency_ms": 0.1005,
    "override": [],
    "full": "[history_fits] token pressure 0.10 < 0.90: full recent history fits, window is lossless | features: turn=3, pressure=0.10, task=exploration, prior=sliding_window, since_switch=0",
    "rule": "history_fits",
    "rule_reason": "token pressure 0.10 < 0.90: full recent history fits, window is lossless",
    "dwell": [],
    "escalations": []
   },
   "candidates": {
    "sliding_window": {
     "tokens": 54,
     "latency_ms": 0.73,
     "quality": {
      "kept": 2,
      "relevance": 0.139,
      "freshness": 0.959,
      "importance": 0.0,
      "state": 1.0,
      "composite": 0.524
     }
    },
    "summarization": {
     "tokens": 58,
     "latency_ms": 0.97,
     "quality": {
      "tier_emitted": "L1",
      "loss_score": 0.0,
      "loss_threshold_exceeded": false,
      "symbol_retention_rate": null
     }
    },
    "rag": {
     "tokens": 0,
     "latency_ms": 1.56,
     "quality": {
      "granularity_tag": "turn",
      "retrieved": 0,
      "stale_flags": 0
     }
    }
   },
   "prompt": {
    "tokens": 54,
    "context": "user: We're adding a product catalogue to our Django shop. Quick plan?\nassistant: A `catalog` app with Product and Category models, a list view with filters, a detail view, and an admin with search. Slugs in URLs, prices handled carefully.",
    "truncated": false
   },
   "raised": [],
   "traps": []
  },
  {
   "exchange": 3,
   "turn_id": "t0005",
   "user": "Write a helper that turns product titles into URL slugs, handling accents.",
   "assistant": "```python\ndef slugify_title(title):\n    ascii_title = unicodedata.normalize('NFKD', title).encode('ascii', 'ignore').decode()\n    return slugify(ascii_title)[:80]\n```",
   "signal": {
    "turn_count": 5,
    "task_type": "code_generation",
    "matched_pattern": "pattern:code_generation",
    "topic_similarity": null,
    "shift": false,
    "recall_request": false,
    "tokens_used": 126,
    "budget": 700
   },
   "features": {
    "turn_count": 5,
    "token_budget_pressure": 0.18,
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
     "reason": "token pressure 0.18 < 0.90: full recent history fits, window is lossless"
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
    "latency_ms": 0.0927,
    "override": [],
    "full": "[history_fits] token pressure 0.18 < 0.90: full recent history fits, window is lossless | features: turn=5, pressure=0.18, task=code_generation, prior=sliding_window, since_switch=1",
    "rule": "history_fits",
    "rule_reason": "token pressure 0.18 < 0.90: full recent history fits, window is lossless",
    "dwell": [],
    "escalations": []
   },
   "candidates": {
    "sliding_window": {
     "tokens": 109,
     "latency_ms": 0.69,
     "quality": {
      "kept": 4,
      "relevance": 0.109,
      "freshness": 0.882,
      "importance": 0.125,
      "state": 1.0,
      "composite": 0.529
     }
    },
    "summarization": {
     "tokens": 113,
     "latency_ms": 0.86,
     "quality": {
      "tier_emitted": "L1",
      "loss_score": 0.0,
      "loss_threshold_exceeded": false,
      "symbol_retention_rate": null
     }
    },
    "rag": {
     "tokens": 65,
     "latency_ms": 1.91,
     "quality": {
      "granularity_tag": "segment",
      "retrieved": 1,
      "stale_flags": 0
     }
    }
   },
   "prompt": {
    "tokens": 109,
    "context": "user: We're adding a product catalogue to our Django shop. Quick plan?\nassistant: A `catalog` app with Product and Category models, a list view with filters, a detail view, and an admin with search. Slugs in URLs, prices handled carefully.\nuser: Ground rule before any model code: how do we store money?\nassistant: Never floats. Every price field is `models.DecimalField(max_digits=10, decimal_places=2)` and every calculation uses `Decimal`; this applies to carts, discounts and tax as well.",
    "truncated": false
   },
   "raised": [],
   "traps": []
  },
  {
   "exchange": 4,
   "turn_id": "t0007",
   "user": "Product pages are slow on the category listing.",
   "assistant": "Each product fetches its category and first image separately. Use `select_related('category').prefetch_related('images')` in the queryset.",
   "signal": {
    "turn_count": 7,
    "task_type": "code_generation",
    "matched_pattern": "carry_over",
    "topic_similarity": 0.192,
    "shift": false,
    "recall_request": false,
    "tokens_used": 183,
    "budget": 700
   },
   "features": {
    "turn_count": 7,
    "token_budget_pressure": 0.2614,
    "task_type": "code_generation",
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
     "reason": "token pressure 0.26 < 0.90: full recent history fits, window is lossless"
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
    "latency_ms": 0.0839,
    "override": [],
    "full": "[history_fits] token pressure 0.26 < 0.90: full recent history fits, window is lossless | features: turn=7, pressure=0.26, task=code_generation, prior=sliding_window, since_switch=2",
    "rule": "history_fits",
    "rule_reason": "token pressure 0.26 < 0.90: full recent history fits, window is lossless",
    "dwell": [],
    "escalations": []
   },
   "candidates": {
    "sliding_window": {
     "tokens": 172,
     "latency_ms": 0.64,
     "quality": {
      "kept": 6,
      "relevance": 0.14,
      "freshness": 0.814,
      "importance": 0.2,
      "state": 1.0,
      "composite": 0.538
     }
    },
    "summarization": {
     "tokens": 176,
     "latency_ms": 0.85,
     "quality": {
      "tier_emitted": "L1",
      "loss_score": 0.0,
      "loss_threshold_exceeded": false,
      "symbol_retention_rate": 1.0
     }
    },
    "rag": {
     "tokens": 91,
     "latency_ms": 2.38,
     "quality": {
      "granularity_tag": "segment",
      "retrieved": 2,
      "stale_flags": 0
     }
    }
   },
   "prompt": {
    "tokens": 172,
    "context": "user: We're adding a product catalogue to our Django shop. Quick plan?\nassistant: A `catalog` app with Product and Category models, a list view with filters, a detail view, and an admin with search. Slugs in URLs, prices handled carefully.\nuser: Ground rule before any model code: how do we store money?\nassistant: Never floats. Every price field is `models.DecimalField(max_digits=10, decimal_places=2)` and every calculation uses `Decimal`; this applies to carts, discounts and tax as well.\nuser: Write a helper that turns product titles into URL slugs, handling accents.\nassistant: ```python\ndef slugify_title(title):\n    ascii_title = unicodedata.normalize('NFKD', title).encode('ascii', 'ignore').decode()\n    return slugify(ascii_title)[:80]\n```",
    "truncated": false
   },
   "raised": [],
   "traps": []
  },
  {
   "exchange": 5,
   "turn_id": "t0009",
   "user": "Add a search box to the product list.",
   "assistant": "Postgres full-text search: a `SearchVector('title', 'description')` with a GIN index and `SearchRank` ordering; fall back to `icontains` on SQLite for local development.",
   "signal": {
    "turn_count": 9,
    "task_type": "code_generation",
    "matched_pattern": "carry_over",
    "topic_similarity": 0.442,
    "shift": false,
    "recall_request": false,
    "tokens_used": 225,
    "budget": 700
   },
   "features": {
    "turn_count": 9,
    "token_budget_pressure": 0.3214,
    "task_type": "code_generation",
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
     "reason": "token pressure 0.32 < 0.90: full recent history fits, window is lossless"
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
    "latency_ms": 0.0717,
    "override": [],
    "full": "[history_fits] token pressure 0.32 < 0.90: full recent history fits, window is lossless | features: turn=9, pressure=0.32, task=code_generation, prior=sliding_window, since_switch=3",
    "rule": "history_fits",
    "rule_reason": "token pressure 0.32 < 0.90: full recent history fits, window is lossless",
    "dwell": [],
    "escalations": []
   },
   "candidates": {
    "sliding_window": {
     "tokens": 214,
     "latency_ms": 0.6,
     "quality": {
      "kept": 8,
      "relevance": 0.199,
      "freshness": 0.753,
      "importance": 0.163,
      "state": 1.0,
      "composite": 0.529
     }
    },
    "summarization": {
     "tokens": 219,
     "latency_ms": 0.97,
     "quality": {
      "tier_emitted": "L1",
      "loss_score": 0.0,
      "loss_threshold_exceeded": false,
      "symbol_retention_rate": 1.0
     }
    },
    "rag": {
     "tokens": 151,
     "latency_ms": 2.57,
     "quality": {
      "granularity_tag": "turn",
      "retrieved": 4,
      "stale_flags": 0
     }
    }
   },
   "prompt": {
    "tokens": 215,
    "context": "user: We're adding a product catalogue to our Django shop. Quick plan?\nassistant: A `catalog` app with Product and Category models, a list view with filters, a detail view, and an admin with search. Slugs in URLs, prices handled carefully.\nuser: Ground rule before any model code: how do we store money?\nassistant: Never floats. Every price field is `models.DecimalField(max_digits=10, decimal_places=2)` and every calculation uses `Decimal`; this applies to carts, discounts and tax as well.\nuser: Write a helper that turns product titles into URL slugs, handling accents.\nassistant: ```python\ndef slugify_title(title):\n    ascii_title = unicodedata.normalize('NFKD', title).encode('ascii', 'ignore').decode()\n    return slugify(ascii_title)[:80]\n```\nuser: Product pages are slow on the category listing.\nassistant: Each product fetches its category and first image separately. Use `select_related('category').prefetch_related('images')` in the queryset.",
    "truncated": false
   },
   "raised": [],
   "traps": []
  },
  {
   "exchange": 6,
   "turn_id": "t0011",
   "user": "Make product images responsive.",
   "assistant": "Generate 400, 800 and 1600 px renditions on upload with django-imagekit and emit `srcset`/`sizes` in the template, with lazy loading below the fold.",
   "signal": {
    "turn_count": 11,
    "task_type": "code_generation",
    "matched_pattern": "carry_over",
    "topic_similarity": 0.285,
    "shift": false,
    "recall_request": false,
    "tokens_used": 275,
    "budget": 700
   },
   "features": {
    "turn_count": 11,
    "token_budget_pressure": 0.3929,
    "task_type": "code_generation",
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
     "reason": "token pressure 0.39 < 0.90: full recent history fits, window is lossless"
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
    "latency_ms": 0.0769,
    "override": [],
    "full": "[history_fits] token pressure 0.39 < 0.90: full recent history fits, window is lossless | features: turn=11, pressure=0.39, task=code_generation, prior=sliding_window, since_switch=4",
    "rule": "history_fits",
    "rule_reason": "token pressure 0.39 < 0.90: full recent history fits, window is lossless",
    "dwell": [],
    "escalations": []
   },
   "candidates": {
    "sliding_window": {
     "tokens": 268,
     "latency_ms": 0.57,
     "quality": {
      "kept": 10,
      "relevance": 0.138,
      "freshness": 0.698,
      "importance": 0.14,
      "state": 1.0,
      "composite": 0.494
     }
    },
    "summarization": {
     "tokens": 291,
     "latency_ms": 1.26,
     "quality": {
      "tier_emitted": "L1",
      "loss_score": 0.0,
      "loss_threshold_exceeded": false,
      "symbol_retention_rate": 1.0
     }
    },
    "rag": {
     "tokens": 145,
     "latency_ms": 2.79,
     "quality": {
      "granularity_tag": "turn",
      "retrieved": 4,
      "stale_flags": 0
     }
    }
   },
   "prompt": {
    "tokens": 269,
    "context": "user: We're adding a product catalogue to our Django shop. Quick plan?\nassistant: A `catalog` app with Product and Category models, a list view with filters, a detail view, and an admin with search. Slugs in URLs, prices handled carefully.\nuser: Ground rule before any model code: how do we store money?\nassistant: Never floats. Every price field is `models.DecimalField(max_digits=10, decimal_places=2)` and every calculation uses `Decimal`; this applies to carts, discounts and tax as well.\nuser: Write a helper that turns product titles into URL slugs, handling accents.\nassistant: ```python\ndef slugify_title(title):\n    ascii_title = unicodedata.normalize('NFKD', title).encode('ascii', 'ignore').decode()\n    return slugify(ascii_title)[:80]\n```\nuser: Product pages are slow on the category listing.\nassistant: Each product fetches its category and first image separately. Use `select_related('category').prefetch_related('images')` in the queryset.\nuser: Add a search box to the product list.\nassistant: Postgres full-text search: a `SearchVector('title', 'description')` with a GIN index and `SearchRank` ordering; fall back to `icontains` on SQLite for local development.",
    "truncated": false
   },
   "raised": [],
   "traps": []
  },
  {
   "exchange": 7,
   "turn_id": "t0013",
   "user": "Add caching to the category pages.",
   "assistant": "Per-view caching for 10 minutes keyed on the querystring, plus a `post_save` signal on Product that clears the affected category's cache keys.",
   "signal": {
    "turn_count": 13,
    "task_type": "code_generation",
    "matched_pattern": "carry_over",
    "topic_similarity": 0.426,
    "shift": false,
    "recall_request": false,
    "tokens_used": 326,
    "budget": 700
   },
   "features": {
    "turn_count": 13,
    "token_budget_pressure": 0.4657,
    "task_type": "code_generation",
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
     "reason": "token pressure 0.47 < 0.90: full recent history fits, window is lossless"
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
    "latency_ms": 0.0933,
    "override": [],
    "full": "[history_fits] token pressure 0.47 < 0.90: full recent history fits, window is lossless | features: turn=13, pressure=0.47, task=code_generation, prior=sliding_window, since_switch=5",
    "rule": "history_fits",
    "rule_reason": "token pressure 0.47 < 0.90: full recent history fits, window is lossless",
    "dwell": [],
    "escalations": []
   },
   "candidates": {
    "sliding_window": {
     "tokens": 317,
     "latency_ms": 0.55,
     "quality": {
      "kept": 12,
      "relevance": 0.185,
      "freshness": 0.649,
      "importance": 0.125,
      "state": 1.0,
      "composite": 0.49
     }
    },
    "summarization": {
     "tokens": 340,
     "latency_ms": 1.42,
     "quality": {
      "tier_emitted": "L1",
      "loss_score": 0.0,
      "loss_threshold_exceeded": false,
      "symbol_retention_rate": 1.0
     }
    },
    "rag": {
     "tokens": 161,
     "latency_ms": 2.97,
     "quality": {
      "granularity_tag": "turn",
      "retrieved": 5,
      "stale_flags": 0
     }
    }
   },
   "prompt": {
    "tokens": 318,
    "context": "user: We're adding a product catalogue to our Django shop. Quick plan?\nassistant: A `catalog` app with Product and Category models, a list view with filters, a detail view, and an admin with search. Slugs in URLs, prices handled carefully.\nuser: Ground rule before any model code: how do we store money?\nassistant: Never floats. Every price field is `models.DecimalField(max_digits=10, decimal_places=2)` and every calculation uses `Decimal`; this applies to carts, discounts and tax as well.\nuser: Write a helper that turns product titles into URL slugs, handling accents.\nassistant: ```python\ndef slugify_title(title):\n    ascii_title = unicodedata.normalize('NFKD', title).encode('ascii', 'ignore').decode()\n    return slugify(ascii_title)[:80]\n```\nuser: Product pages are slow on the category listing.\nassistant: Each product fetches its category and first image separately. Use `select_related('category').prefetch_related('images')` in the queryset.\nuser: Add a search box to the product list.\nassistant: Postgres full-text search: a `SearchVector('title', 'description')` with a GIN index and `SearchRank` ordering; fall back to `icontains` on SQLite for local development.\nuser: Make product images responsive.\nassistant: Generate 400, 800 and 1600 px renditions on upload with django-imagekit and emit `srcset`/`sizes` in the template, with lazy loading below the fold.",
    "truncated": false
   },
   "raised": [],
   "traps": []
  },
  {
   "exchange": 8,
   "turn_id": "t0015",
   "user": "Translate the shop into Sinhala and Tamil.",
   "assistant": "Enabled `LocaleMiddleware`, marked template strings with `{% translate %}`, and used django-modeltranslation for product titles and descriptions. URLs get a language prefix.",
   "signal": {
    "turn_count": 15,
    "task_type": "chat",
    "matched_pattern": "shift_default",
    "topic_similarity": 0.121,
    "shift": true,
    "recall_request": false,
    "tokens_used": 371,
    "budget": 700
   },
   "features": {
    "turn_count": 15,
    "token_budget_pressure": 0.53,
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
     "reason": "token pressure 0.53 < 0.90: full recent history fits, window is lossless"
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
    "latency_ms": 0.102,
    "override": [],
    "full": "[history_fits] token pressure 0.53 < 0.90: full recent history fits, window is lossless | features: turn=15, pressure=0.53, task=chat, prior=sliding_window, since_switch=6",
    "rule": "history_fits",
    "rule_reason": "token pressure 0.53 < 0.90: full recent history fits, window is lossless",
    "dwell": [],
    "escalations": []
   },
   "candidates": {
    "sliding_window": {
     "tokens": 359,
     "latency_ms": 0.55,
     "quality": {
      "kept": 14,
      "relevance": 0.078,
      "freshness": 0.605,
      "importance": 0.118,
      "state": 0.5,
      "composite": 0.325
     }
    },
    "summarization": {
     "tokens": 382,
     "latency_ms": 1.64,
     "quality": {
      "tier_emitted": "L1",
      "loss_score": 0.0,
      "loss_threshold_exceeded": false,
      "symbol_retention_rate": 1.0
     }
    },
    "rag": {
     "tokens": 111,
     "latency_ms": 1125.46,
     "quality": {
      "granularity_tag": "turn",
      "retrieved": 3,
      "stale_flags": 0
     }
    }
   },
   "prompt": {
    "tokens": 360,
    "context": "user: We're adding a product catalogue to our Django shop. Quick plan?\nassistant: A `catalog` app with Product and Category models, a list view with filters, a detail view, and an admin with search. Slugs in URLs, prices handled carefully.\nuser: Ground rule before any model code: how do we store money?\nassistant: Never floats. Every price field is `models.DecimalField(max_digits=10, decimal_places=2)` and every calculation uses `Decimal`; this applies to carts, discounts and tax as well.\nuser: Write a helper that turns product titles into URL slugs, handling accents.\nassistant: ```python\ndef slugify_title(title):\n    ascii_title = unicodedata.normalize('NFKD', title).encode('ascii', 'ignore').decode()\n    return slugify(ascii_title)[:80]\n```\nuser: Product pages are slow on the category listing.\nassistant: Each product fetches its category and first image separately. Use `select_related('category').prefetch_related('images')` in the queryset.\nuser: Add a search box to the product list.\nassistant: Postgres full-text search: a `SearchVector('title', 'description')` with a GIN index and `SearchRank` ordering; fall back to `icontains` on SQLite for local development.\nuser: Make product images responsive.\nassistant: Generate 400, 800 and 1600 px renditions on upload with django-imagekit and emit `srcset`/`sizes` in the template, with lazy loading below the fold.\nuser: Add caching to the category pages.\nassistant: Per-view caching for 10 minutes keyed on the querystring, plus a `post_save` signal on Product that clears the affected category's cache keys.",
    "truncated": false
   },
   "raised": [],
   "traps": []
  },
  {
   "exchange": 9,
   "turn_id": "t0017",
   "user": "Set up the admin so staff can bulk-edit prices.",
   "assistant": "Added `list_editable = ['price', 'in_stock']` on the Product admin with a CSV import action through django-import-export, validated row by row.",
   "signal": {
    "turn_count": 17,
    "task_type": "chat",
    "matched_pattern": "carry_over",
    "topic_similarity": 0.177,
    "shift": false,
    "recall_request": false,
    "tokens_used": 417,
    "budget": 700
   },
   "features": {
    "turn_count": 17,
    "token_budget_pressure": 0.5957,
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
    "latency_ms": 0.054,
    "override": [],
    "full": "[history_fits] token pressure 0.60 < 0.90: full recent history fits, window is lossless | features: turn=17, pressure=0.60, task=chat, prior=sliding_window, since_switch=7",
    "rule": "history_fits",
    "rule_reason": "token pressure 0.60 < 0.90: full recent history fits, window is lossless",
    "dwell": [],
    "escalations": []
   },
   "candidates": {
    "sliding_window": {
     "tokens": 404,
     "latency_ms": 0.53,
     "quality": {
      "kept": 16,
      "relevance": 0.174,
      "freshness": 0.565,
      "importance": 0.106,
      "state": 0.562,
      "composite": 0.352
     }
    },
    "summarization": {
     "tokens": 457,
     "latency_ms": 1.84,
     "quality": {
      "tier_emitted": "L1",
      "loss_score": 0.0,
      "loss_threshold_exceeded": false,
      "symbol_retention_rate": 1.0
     }
    },
    "rag": {
     "tokens": 284,
     "latency_ms": 926.01,
     "quality": {
      "granularity_tag": "turn",
      "retrieved": 7,
      "stale_flags": 0
     }
    }
   },
   "prompt": {
    "tokens": 405,
    "context": "user: We're adding a product catalogue to our Django shop. Quick plan?\nassistant: A `catalog` app with Product and Category models, a list view with filters, a detail view, and an admin with search. Slugs in URLs, prices handled carefully.\nuser: Ground rule before any model code: how do we store money?\nassistant: Never floats. Every price field is `models.DecimalField(max_digits=10, decimal_places=2)` and every calculation uses `Decimal`; this applies to carts, discounts and tax as well.\nuser: Write a helper that turns product titles into URL slugs, handling accents.\nassistant: ```python\ndef slugify_title(title):\n    ascii_title = unicodedata.normalize('NFKD', title).encode('ascii', 'ignore').decode()\n    return slugify(ascii_title)[:80]\n```\nuser: Product pages are slow on the category listing.\nassistant: Each product fetches its category and first image separately. Use `select_related('category').prefetch_related('images')` in the queryset.\nuser: Add a search box to the product list.\nassistant: Postgres full-text search: a `SearchVector('title', 'description')` with a GIN index and `SearchRank` ordering; fall back to `icontains` on SQLite for local development.\nuser: Make product images responsive.\nassistant: Generate 400, 800 and 1600 px renditions on upload with django-imagekit and emit `srcset`/`sizes` in the template, with lazy loading below the fold.\nuser: Add caching to the category pages.\nassistant: Per-view caching for 10 minutes keyed on the querystring, plus a `post_save` signal on Product that clears the affected category's cache keys.\nuser: Translate the shop into Sinhala and Tamil.\nassistant: Enabled `LocaleMiddleware`, marked template strings with `{% translate %}`, and used django-modeltranslation for product titles and descriptions. URLs get a language prefix.",
    "truncated": false
   },
   "raised": [],
   "traps": []
  },
  {
   "exchange": 10,
   "turn_id": "t0019",
   "user": "New products added through the import need slugs generated from their names, including names with diacritics.",
   "assistant": "(scripted reply omitted - the check is on the context the model would receive)",
   "signal": {
    "turn_count": 19,
    "task_type": "chat",
    "matched_pattern": "carry_over",
    "topic_similarity": 0.2,
    "shift": false,
    "recall_request": false,
    "tokens_used": 476,
    "budget": 700
   },
   "features": {
    "turn_count": 19,
    "token_budget_pressure": 0.68,
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
     "reason": "token pressure 0.68 < 0.90: full recent history fits, window is lossless"
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
    "latency_ms": 0.0682,
    "override": [],
    "full": "[history_fits] token pressure 0.68 < 0.90: full recent history fits, window is lossless | features: turn=19, pressure=0.68, task=chat, prior=sliding_window, since_switch=8",
    "rule": "history_fits",
    "rule_reason": "token pressure 0.68 < 0.90: full recent history fits, window is lossless",
    "dwell": [],
    "escalations": []
   },
   "candidates": {
    "sliding_window": {
     "tokens": 437,
     "latency_ms": 0.52,
     "quality": {
      "kept": 17,
      "relevance": 0.206,
      "freshness": 0.544,
      "importance": 0.106,
      "state": 0.618,
      "composite": 0.368
     }
    },
    "summarization": {
     "tokens": 505,
     "latency_ms": 1.95,
     "quality": {
      "tier_emitted": "L1",
      "loss_score": 0.0,
      "loss_threshold_exceeded": false,
      "symbol_retention_rate": 1.0
     }
    },
    "rag": {
     "tokens": 475,
     "latency_ms": 786.41,
     "quality": {
      "granularity_tag": "turn",
      "retrieved": 11,
      "stale_flags": 1
     }
    }
   },
   "prompt": {
    "tokens": 438,
    "context": "user: We're adding a product catalogue to our Django shop. Quick plan?\nassistant: A `catalog` app with Product and Category models, a list view with filters, a detail view, and an admin with search. Slugs in URLs, prices handled carefully.\nassistant: Never floats. Every price field is `models.DecimalField(max_digits=10, decimal_places=2)` and every calculation uses `Decimal`; this applies to carts, discounts and tax as well.\nuser: Write a helper that turns product titles into URL slugs, handling accents.\nassistant: ```python\ndef slugify_title(title):\n    ascii_title = unicodedata.normalize('NFKD', title).encode('ascii', 'ignore').decode()\n    return slugify(ascii_title)[:80]\n```\nuser: Product pages are slow on the category listing.\nassistant: Each product fetches its category and first image separately. Use `select_related('category').prefetch_related('images')` in the queryset.\nuser: Add a search box to the product list.\nassistant: Postgres full-text search: a `SearchVector('title', 'description')` with a GIN index and `SearchRank` ordering; fall back to `icontains` on SQLite for local development.\nuser: Make product images responsive.\nassistant: Generate 400, 800 and 1600 px renditions on upload with django-imagekit and emit `srcset`/`sizes` in the template, with lazy loading below the fold.\nuser: Add caching to the category pages.\nassistant: Per-view caching for 10 minutes keyed on the querystring, plus a `post_save` signal on Product that clears the affected category's cache keys.\nuser: Translate the shop into Sinhala and Tamil.\nassistant: Enabled `LocaleMiddleware`, marked template strings with `{% translate %}`, and used django-modeltranslation for product titles and descriptions. URLs get a language prefix.\nuser: Set up the admin so staff can bulk-edit prices.\nassistant: Added `list_editable = ['price', 'in_stock']` on the Product admin with a CSV import action through django-import-export, validated row by row.",
    "truncated": false
   },
   "raised": [
    {
     "kind": "contradiction_flagged",
     "source_module": "rag",
     "detail": {
      "n_flags": 1
     }
    }
   ],
   "traps": [
    {
     "name": "duplicate slug helper",
     "description": "slugify_title exists since exchange 3",
     "planted_at": 3,
     "kind": "duplicate",
     "adaptive": {
      "caught": true,
      "detail": "found `def slugify_title(`",
      "strategy": "sliding_window"
     },
     "fixed_6_exchange_window": {
      "caught": false,
      "detail": "missing `def slugify_title(`"
     },
     "sliding_window": {
      "caught": true,
      "detail": "found `def slugify_title(`"
     },
     "summarization": {
      "caught": true,
      "detail": "found `def slugify_title(`"
     },
     "rag": {
      "caught": true,
      "detail": "found `def slugify_title(`"
     },
     "hybrid": {
      "caught": true,
      "detail": "found `def slugify_title(`"
     }
    }
   ]
  },
  {
   "exchange": 11,
   "turn_id": "t0021",
   "user": "Add a discount field to the cart and compute the discounted total.",
   "assistant": "(scripted reply omitted - the check is on the context the model would receive)",
   "signal": {
    "turn_count": 21,
    "task_type": "chat",
    "matched_pattern": "shift_default",
    "topic_similarity": 0.138,
    "shift": true,
    "recall_request": false,
    "tokens_used": 510,
    "budget": 700
   },
   "features": {
    "turn_count": 21,
    "token_budget_pressure": 0.7286,
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
     "reason": "token pressure 0.73 < 0.90: full recent history fits, window is lossless"
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
    "strategy": "hybrid",
    "latency_ms": 0.0829,
    "override": [],
    "full": "[history_fits] token pressure 0.73 < 0.90: full recent history fits, window is lossless | escalation from t0019: 1 stale chunk(s) flagged -> hybrid so the superseding facts are retrievable next to the recent window | features: turn=21, pressure=0.73, task=chat, prior=sliding_window, since_switch=9",
    "rule": "history_fits",
    "rule_reason": "token pressure 0.73 < 0.90: full recent history fits, window is lossless",
    "dwell": [],
    "escalations": [
     "escalation from t0019: 1 stale chunk(s) flagged -> hybrid so the superseding facts are retrievable next to the recent window"
    ]
   },
   "candidates": {
    "sliding_window": {
     "tokens": 306,
     "latency_ms": 0.52,
     "quality": {
      "kept": 11,
      "relevance": 0.099,
      "freshness": 0.643,
      "importance": 0.145,
      "state": 0.386,
      "composite": 0.318
     }
    },
    "summarization": {
     "tokens": 548,
     "latency_ms": 2.07,
     "quality": {
      "tier_emitted": "L1",
      "loss_score": 0.0,
      "loss_threshold_exceeded": false,
      "symbol_retention_rate": 1.0
     }
    },
    "rag": {
     "tokens": 132,
     "latency_ms": 644.84,
     "quality": {
      "granularity_tag": "turn",
      "retrieved": 3,
      "stale_flags": 0
     }
    }
   },
   "prompt": {
    "tokens": 348,
    "context": "[Retrieved memory]\n[turns: t0004]\nassistant: Never floats. Every price field is `models.DecimalField(max_digits=10, decimal_places=2)` and every calculation uses `Decimal`; this applies to carts, discounts and tax as well.\n\n---\n\n[turns: t0003]\nuser: Ground rule before any model code: how do we store money?\n\n[Recent turns]\nassistant: ```python\ndef slugify_title(title):\n    ascii_title = unicodedata.normalize('NFKD', title).encode('ascii', 'ignore').decode()\n    return slugify(ascii_title)[:80]\n```\nassistant: Generate 400, 800 and 1600 px renditions on upload with django-imagekit and emit `srcset`/`sizes` in the template, with lazy loading below the fold.\nuser: Add caching to the category pages.\nassistant: Per-view caching for 10 minutes keyed on the querystring, plus a `post_save` signal on Product that clears the affected category's cache keys.\nuser: Translate the shop into Sinhala and Tamil.\nassistant: Enabled `LocaleMiddleware`, marked template strings with `{% translate %}`, and used django-modeltranslation for product titles and descriptions. URLs get a language prefix.\nuser: Set up the admin so staff can bulk-edit prices.\nassistant: Added `list_editable = ['price', 'in_stock']` on the Product admin with a CSV import action through django-import-export, validated row by row.\nuser: New products added through the import need slugs generated from their names, including names with diacritics.\nassistant: (scripted reply omitted - the check is on the context the model would receive)",
    "truncated": false
   },
   "raised": [],
   "traps": [
    {
     "name": "money decision",
     "description": "money must use Decimal (decided at exchange 2)",
     "planted_at": 2,
     "kind": "decision",
     "adaptive": {
      "caught": true,
      "detail": "found `Decimal`",
      "strategy": "hybrid"
     },
     "fixed_6_exchange_window": {
      "caught": false,
      "detail": "missing `Decimal`"
     },
     "sliding_window": {
      "caught": true,
      "detail": "found `Decimal`"
     },
     "summarization": {
      "caught": true,
      "detail": "found `Decimal`"
     },
     "rag": {
      "caught": true,
      "detail": "found `Decimal`"
     },
     "hybrid": {
      "caught": true,
      "detail": "found `Decimal`"
     }
    }
   ]
  }
 ]
};
