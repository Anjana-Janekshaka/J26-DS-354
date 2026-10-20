window.CEAI_SESSIONS = window.CEAI_SESSIONS || {};
window.CEAI_SESSIONS["async-scraper"] = {
 "scenario": "async-scraper",
 "slug": "async-scraper",
 "language": "python",
 "held_out": true,
 "system": "frozen",
 "mode": "full",
 "budget": 700,
 "recorded_at": "2026-10-19T11:24:28+00:00",
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
  "fixed_6_exchange_window": 1,
  "sliding_window": 1,
  "summarization": 2,
  "rag": 2,
  "hybrid": 2
 },
 "turns": [
  {
   "exchange": 1,
   "turn_id": "t0001",
   "user": "I need a scraper for public price pages. Start simple.",
   "assistant": "A fetch function, a parser per site, and a CSV writer. Respect robots.txt and add a user agent with a contact address.",
   "signal": {
    "turn_count": 1,
    "task_type": "chat",
    "matched_pattern": "carry_over",
    "topic_similarity": null,
    "shift": false,
    "recall_request": false,
    "tokens_used": 14,
    "budget": 700
   },
   "features": {
    "turn_count": 1,
    "token_budget_pressure": 0.02,
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
    "latency_ms": 0.0822,
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
     "latency_ms": 1.13,
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
   "user": "Write fetch.",
   "assistant": "```python\ndef fetch(url):\n    return requests.get(url, headers=HEADERS, timeout=20).text\n```",
   "signal": {
    "turn_count": 3,
    "task_type": "chat",
    "matched_pattern": "carry_over",
    "topic_similarity": null,
    "shift": false,
    "recall_request": false,
    "tokens_used": 48,
    "budget": 700
   },
   "features": {
    "turn_count": 3,
    "token_budget_pressure": 0.0686,
    "task_type": "chat",
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
     "reason": "token pressure 0.07 < 0.90: full recent history fits, window is lossless"
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
    "latency_ms": 0.0837,
    "override": [],
    "full": "[history_fits] token pressure 0.07 < 0.90: full recent history fits, window is lossless | features: turn=3, pressure=0.07, task=chat, prior=sliding_window, since_switch=0",
    "rule": "history_fits",
    "rule_reason": "token pressure 0.07 < 0.90: full recent history fits, window is lossless",
    "dwell": [],
    "escalations": []
   },
   "candidates": {
    "sliding_window": {
     "tokens": 43,
     "latency_ms": 0.7,
     "quality": {
      "kept": 2,
      "relevance": 0.304,
      "freshness": 0.959,
      "importance": 0.025,
      "state": 1.0,
      "composite": 0.572
     }
    },
    "summarization": {
     "tokens": 47,
     "latency_ms": 0.99,
     "quality": {
      "tier_emitted": "L1",
      "loss_score": 0.0,
      "loss_threshold_exceeded": false,
      "symbol_retention_rate": null
     }
    },
    "rag": {
     "tokens": 60,
     "latency_ms": 1083.61,
     "quality": {
      "granularity_tag": "turn",
      "retrieved": 2,
      "stale_flags": 0
     }
    }
   },
   "prompt": {
    "tokens": 43,
    "context": "user: I need a scraper for public price pages. Start simple.\nassistant: A fetch function, a parser per site, and a CSV writer. Respect robots.txt and add a user agent with a contact address.",
    "truncated": false
   },
   "raised": [],
   "traps": []
  },
  {
   "exchange": 3,
   "turn_id": "t0005",
   "user": "Normalise URLs so we don't scrape the same page twice.",
   "assistant": "```python\ndef normalize_url(url):\n    parts = urlsplit(url)\n    query = urlencode(sorted(parse_qsl(parts.query)))\n    return urlunsplit((parts.scheme, parts.netloc.lower(), parts.path.rstrip('/'), query, ''))\n```",
   "signal": {
    "turn_count": 5,
    "task_type": "chat",
    "matched_pattern": "carry_over",
    "topic_similarity": null,
    "shift": false,
    "recall_request": false,
    "tokens_used": 90,
    "budget": 700
   },
   "features": {
    "turn_count": 5,
    "token_budget_pressure": 0.1286,
    "task_type": "chat",
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
     "reason": "token pressure 0.13 < 0.90: full recent history fits, window is lossless"
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
    "latency_ms": 0.0632,
    "override": [],
    "full": "[history_fits] token pressure 0.13 < 0.90: full recent history fits, window is lossless | features: turn=5, pressure=0.13, task=chat, prior=sliding_window, since_switch=1",
    "rule": "history_fits",
    "rule_reason": "token pressure 0.13 < 0.90: full recent history fits, window is lossless",
    "dwell": [],
    "escalations": []
   },
   "candidates": {
    "sliding_window": {
     "tokens": 75,
     "latency_ms": 0.63,
     "quality": {
      "kept": 4,
      "relevance": 0.33,
      "freshness": 0.882,
      "importance": 0.163,
      "state": 1.0,
      "composite": 0.594
     }
    },
    "summarization": {
     "tokens": 79,
     "latency_ms": 0.89,
     "quality": {
      "tier_emitted": "L1",
      "loss_score": 0.0,
      "loss_threshold_exceeded": false,
      "symbol_retention_rate": 1.0
     }
    },
    "rag": {
     "tokens": 104,
     "latency_ms": 877.75,
     "quality": {
      "granularity_tag": "turn",
      "retrieved": 3,
      "stale_flags": 0
     }
    }
   },
   "prompt": {
    "tokens": 75,
    "context": "user: I need a scraper for public price pages. Start simple.\nassistant: A fetch function, a parser per site, and a CSV writer. Respect robots.txt and add a user agent with a contact address.\nuser: Write fetch.\nassistant: ```python\ndef fetch(url):\n    return requests.get(url, headers=HEADERS, timeout=20).text\n```",
    "truncated": false
   },
   "raised": [],
   "traps": []
  },
  {
   "exchange": 4,
   "turn_id": "t0007",
   "user": "It's too slow for 20k pages. Go async.",
   "assistant": "```python\nasync def fetch(url, session):\n    async with session.get(url, headers=HEADERS) as resp:\n        return await resp.text()\n```\nOne `aiohttp.ClientSession` is created in `main` and passed down; concurrency is capped with a semaphore of 20.",
   "signal": {
    "turn_count": 7,
    "task_type": "chat",
    "matched_pattern": "carry_over",
    "topic_similarity": 0.391,
    "shift": false,
    "recall_request": false,
    "tokens_used": 157,
    "budget": 700
   },
   "features": {
    "turn_count": 7,
    "token_budget_pressure": 0.2243,
    "task_type": "chat",
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
     "reason": "token pressure 0.22 < 0.90: full recent history fits, window is lossless"
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
    "latency_ms": 0.0512,
    "override": [],
    "full": "[history_fits] token pressure 0.22 < 0.90: full recent history fits, window is lossless | features: turn=7, pressure=0.22, task=chat, prior=sliding_window, since_switch=2",
    "rule": "history_fits",
    "rule_reason": "token pressure 0.22 < 0.90: full recent history fits, window is lossless",
    "dwell": [],
    "escalations": []
   },
   "candidates": {
    "sliding_window": {
     "tokens": 142,
     "latency_ms": 0.57,
     "quality": {
      "kept": 6,
      "relevance": 0.229,
      "freshness": 0.814,
      "importance": 0.242,
      "state": 1.0,
      "composite": 0.571
     }
    },
    "summarization": {
     "tokens": 147,
     "latency_ms": 0.89,
     "quality": {
      "tier_emitted": "L1",
      "loss_score": 0.0,
      "loss_threshold_exceeded": false,
      "symbol_retention_rate": 1.0
     }
    },
    "rag": {
     "tokens": 129,
     "latency_ms": 715.68,
     "quality": {
      "granularity_tag": "turn",
      "retrieved": 4,
      "stale_flags": 0
     }
    }
   },
   "prompt": {
    "tokens": 143,
    "context": "user: I need a scraper for public price pages. Start simple.\nassistant: A fetch function, a parser per site, and a CSV writer. Respect robots.txt and add a user agent with a contact address.\nuser: Write fetch.\nassistant: ```python\ndef fetch(url):\n    return requests.get(url, headers=HEADERS, timeout=20).text\n```\nuser: Normalise URLs so we don't scrape the same page twice.\nassistant: ```python\ndef normalize_url(url):\n    parts = urlsplit(url)\n    query = urlencode(sorted(parse_qsl(parts.query)))\n    return urlunsplit((parts.scheme, parts.netloc.lower(), parts.path.rstrip('/'), query, ''))\n```",
    "truncated": false
   },
   "raised": [],
   "traps": []
  },
  {
   "exchange": 5,
   "turn_id": "t0009",
   "user": "Some sites block us.",
   "assistant": "Honour Retry-After, add per-domain rate limits (1 request per second by default), rotate nothing deceptive, and back off exponentially on 429.",
   "signal": {
    "turn_count": 9,
    "task_type": "chat",
    "matched_pattern": "carry_over",
    "topic_similarity": 0.365,
    "shift": false,
    "recall_request": false,
    "tokens_used": 227,
    "budget": 700
   },
   "features": {
    "turn_count": 9,
    "token_budget_pressure": 0.3243,
    "task_type": "chat",
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
    "latency_ms": 0.0589,
    "override": [],
    "full": "[history_fits] token pressure 0.32 < 0.90: full recent history fits, window is lossless | features: turn=9, pressure=0.32, task=chat, prior=sliding_window, since_switch=3",
    "rule": "history_fits",
    "rule_reason": "token pressure 0.32 < 0.90: full recent history fits, window is lossless",
    "dwell": [],
    "escalations": []
   },
   "candidates": {
    "sliding_window": {
     "tokens": 220,
     "latency_ms": 0.53,
     "quality": {
      "kept": 8,
      "relevance": 0.186,
      "freshness": 0.753,
      "importance": 0.269,
      "state": 1.0,
      "composite": 0.552
     }
    },
    "summarization": {
     "tokens": 226,
     "latency_ms": 0.95,
     "quality": {
      "tier_emitted": "L1",
      "loss_score": 0.0,
      "loss_threshold_exceeded": false,
      "symbol_retention_rate": 1.0
     }
    },
    "rag": {
     "tokens": 260,
     "latency_ms": 586.39,
     "quality": {
      "granularity_tag": "turn",
      "retrieved": 6,
      "stale_flags": 1
     }
    }
   },
   "prompt": {
    "tokens": 222,
    "context": "user: I need a scraper for public price pages. Start simple.\nassistant: A fetch function, a parser per site, and a CSV writer. Respect robots.txt and add a user agent with a contact address.\nuser: Write fetch.\nassistant: ```python\ndef fetch(url):\n    return requests.get(url, headers=HEADERS, timeout=20).text\n```\nuser: Normalise URLs so we don't scrape the same page twice.\nassistant: ```python\ndef normalize_url(url):\n    parts = urlsplit(url)\n    query = urlencode(sorted(parse_qsl(parts.query)))\n    return urlunsplit((parts.scheme, parts.netloc.lower(), parts.path.rstrip('/'), query, ''))\n```\nuser: It's too slow for 20k pages. Go async.\nassistant: ```python\nasync def fetch(url, session):\n    async with session.get(url, headers=HEADERS) as resp:\n        return await resp.text()\n```\nOne `aiohttp.ClientSession` is created in `main` and passed down; concurrency is capped with a semaphore of 20.",
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
   "traps": []
  },
  {
   "exchange": 6,
   "turn_id": "t0011",
   "user": "Parse prices that look like 'Rs. 1,250.00' or '1.250,00 \u20ac'.",
   "assistant": "Use `price-parser`'s `Price.fromstring`, which handles both separators and currency symbols, and store amount plus currency code.",
   "signal": {
    "turn_count": 11,
    "task_type": "chat",
    "matched_pattern": "carry_over",
    "topic_similarity": 0.194,
    "shift": false,
    "recall_request": false,
    "tokens_used": 285,
    "budget": 700
   },
   "features": {
    "turn_count": 11,
    "token_budget_pressure": 0.4071,
    "task_type": "chat",
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
     "reason": "token pressure 0.41 < 0.90: full recent history fits, window is lossless"
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
    "latency_ms": 0.0707,
    "override": [],
    "full": "[history_fits] token pressure 0.41 < 0.90: full recent history fits, window is lossless | escalation from t0009: 1 stale chunk(s) flagged -> hybrid so the superseding facts are retrievable next to the recent window | features: turn=11, pressure=0.41, task=chat, prior=sliding_window, since_switch=4",
    "rule": "history_fits",
    "rule_reason": "token pressure 0.41 < 0.90: full recent history fits, window is lossless",
    "dwell": [],
    "escalations": [
     "escalation from t0009: 1 stale chunk(s) flagged -> hybrid so the superseding facts are retrievable next to the recent window"
    ]
   },
   "candidates": {
    "sliding_window": {
     "tokens": 259,
     "latency_ms": 0.49,
     "quality": {
      "kept": 10,
      "relevance": 0.156,
      "freshness": 0.698,
      "importance": 0.23,
      "state": 1.0,
      "composite": 0.521
     }
    },
    "summarization": {
     "tokens": 276,
     "latency_ms": 1.22,
     "quality": {
      "tier_emitted": "L1",
      "loss_score": 0.0,
      "loss_threshold_exceeded": false,
      "symbol_retention_rate": 1.0
     }
    },
    "rag": {
     "tokens": 140,
     "latency_ms": 487.46,
     "quality": {
      "granularity_tag": "turn",
      "retrieved": 3,
      "stale_flags": 0
     }
    }
   },
   "prompt": {
    "tokens": 299,
    "context": "[Retrieved memory]\n[turns: t0001 t0002]\nuser: I need a scraper for public price pages. Start simple.\nassistant: A fetch function, a parser per site, and a CSV writer. Respect robots.txt and add a user agent with a contact address.\n\n---\n\n[turns: t0006]\nassistant: ```python\ndef normalize_url(url):\n    parts = urlsplit(url)\n    query = urlencode(sorted(parse_qsl(parts.query)))\n    return urlunsplit((parts.scheme, parts.netloc.lower(), parts.path.rstrip('/'), query, ''))\n```\n\n---\n\n[turns: t0005]\nuser: Normalise URLs so we don't scrape the same page twice.\n\n[Recent turns]\nuser: Write fetch.\nassistant: ```python\ndef fetch(url):\n    return requests.get(url, headers=HEADERS, timeout=20).text\n```\nuser: It's too slow for 20k pages. Go async.\nassistant: ```python\nasync def fetch(url, session):\n    async with session.get(url, headers=HEADERS) as resp:\n        return await resp.text()\n```\nOne `aiohttp.ClientSession` is created in `main` and passed down; concurrency is capped with a semaphore of 20.\nuser: Some sites block us.\nassistant: Honour Retry-After, add per-domain rate limits (1 request per second by default), rotate nothing deceptive, and back off exponentially on 429.",
    "truncated": false
   },
   "raised": [],
   "traps": []
  },
  {
   "exchange": 7,
   "turn_id": "t0013",
   "user": "Store results in SQLite instead of CSV.",
   "assistant": "A `prices` table keyed on (normalized_url, scraped_at) with amount, currency and raw text; writes batched in transactions of 500.",
   "signal": {
    "turn_count": 13,
    "task_type": "chat",
    "matched_pattern": "shift_default",
    "topic_similarity": 0.103,
    "shift": true,
    "recall_request": false,
    "tokens_used": 324,
    "budget": 700
   },
   "features": {
    "turn_count": 13,
    "token_budget_pressure": 0.4629,
    "task_type": "chat",
    "prior_strategy": "hybrid",
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
     "reason": "token pressure 0.46 < 0.90: full recent history fits, window is lossless"
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
    "latency_ms": 0.0813,
    "override": [],
    "full": "[history_fits] token pressure 0.46 < 0.90: full recent history fits, window is lossless | dwell: held hybrid (0 < 3 turns since last switch) | features: turn=13, pressure=0.46, task=chat, prior=hybrid, since_switch=0",
    "rule": "history_fits",
    "rule_reason": "token pressure 0.46 < 0.90: full recent history fits, window is lossless",
    "dwell": [
     "dwell: held hybrid (0 < 3 turns since last switch)"
    ],
    "escalations": []
   },
   "candidates": {
    "sliding_window": {
     "tokens": 314,
     "latency_ms": 0.48,
     "quality": {
      "kept": 12,
      "relevance": 0.109,
      "freshness": 0.649,
      "importance": 0.204,
      "state": 0.5,
      "composite": 0.365
     }
    },
    "summarization": {
     "tokens": 331,
     "latency_ms": 1.43,
     "quality": {
      "tier_emitted": "L1",
      "loss_score": 0.0,
      "loss_threshold_exceeded": false,
      "symbol_retention_rate": 1.0
     }
    },
    "rag": {
     "tokens": 106,
     "latency_ms": 400.33,
     "quality": {
      "granularity_tag": "turn",
      "retrieved": 3,
      "stale_flags": 0
     }
    }
   },
   "prompt": {
    "tokens": 345,
    "context": "[Retrieved memory]\n[turns: t0001 t0002]\nuser: I need a scraper for public price pages. Start simple.\nassistant: A fetch function, a parser per site, and a CSV writer. Respect robots.txt and add a user agent with a contact address.\n\n---\n\n[turns: t0003]\nuser: Write fetch.\n\n[Recent turns]\nassistant: ```python\ndef fetch(url):\n    return requests.get(url, headers=HEADERS, timeout=20).text\n```\nuser: Normalise URLs so we don't scrape the same page twice.\nassistant: ```python\ndef normalize_url(url):\n    parts = urlsplit(url)\n    query = urlencode(sorted(parse_qsl(parts.query)))\n    return urlunsplit((parts.scheme, parts.netloc.lower(), parts.path.rstrip('/'), query, ''))\n```\nuser: It's too slow for 20k pages. Go async.\nassistant: ```python\nasync def fetch(url, session):\n    async with session.get(url, headers=HEADERS) as resp:\n        return await resp.text()\n```\nOne `aiohttp.ClientSession` is created in `main` and passed down; concurrency is capped with a semaphore of 20.\nuser: Some sites block us.\nassistant: Honour Retry-After, add per-domain rate limits (1 request per second by default), rotate nothing deceptive, and back off exponentially on 429.\nuser: Parse prices that look like 'Rs. 1,250.00' or '1.250,00 \u20ac'.\nassistant: Use `price-parser`'s `Price.fromstring`, which handles both separators and currency symbols, and store amount plus currency code.",
    "truncated": false
   },
   "raised": [],
   "traps": []
  },
  {
   "exchange": 8,
   "turn_id": "t0015",
   "user": "Schedule it daily.",
   "assistant": "A systemd timer on the VM at 04:30 with `Persistent=true`, logs to the journal, and a heartbeat ping to the uptime monitor at the end of a successful run.",
   "signal": {
    "turn_count": 15,
    "task_type": "chat",
    "matched_pattern": "shift_default",
    "topic_similarity": 0.043,
    "shift": true,
    "recall_request": false,
    "tokens_used": 363,
    "budget": 700
   },
   "features": {
    "turn_count": 15,
    "token_budget_pressure": 0.5186,
    "task_type": "chat",
    "prior_strategy": "hybrid",
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
     "reason": "token pressure 0.52 < 0.90: full recent history fits, window is lossless"
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
    "latency_ms": 0.0727,
    "override": [],
    "full": "[history_fits] token pressure 0.52 < 0.90: full recent history fits, window is lossless | dwell: held hybrid (1 < 3 turns since last switch) | features: turn=15, pressure=0.52, task=chat, prior=hybrid, since_switch=1",
    "rule": "history_fits",
    "rule_reason": "token pressure 0.52 < 0.90: full recent history fits, window is lossless",
    "dwell": [
     "dwell: held hybrid (1 < 3 turns since last switch)"
    ],
    "escalations": []
   },
   "candidates": {
    "sliding_window": {
     "tokens": 338,
     "latency_ms": 0.46,
     "quality": {
      "kept": 12,
      "relevance": 0.097,
      "freshness": 0.646,
      "importance": 0.221,
      "state": 0.292,
      "composite": 0.314
     }
    },
    "summarization": {
     "tokens": 374,
     "latency_ms": 1.58,
     "quality": {
      "tier_emitted": "L1",
      "loss_score": 0.0,
      "loss_threshold_exceeded": false,
      "symbol_retention_rate": 1.0
     }
    },
    "rag": {
     "tokens": 161,
     "latency_ms": 332.78,
     "quality": {
      "granularity_tag": "turn",
      "retrieved": 4,
      "stale_flags": 0
     }
    }
   },
   "prompt": {
    "tokens": 392,
    "context": "[Retrieved memory]\n[turns: t0007]\nuser: It's too slow for 20k pages. Go async.\n\n---\n\n[turns: t0010]\nassistant: Honour Retry-After, add per-domain rate limits (1 request per second by default), rotate nothing deceptive, and back off exponentially on 429.\n\n---\n\n[turns: t0001 t0002]\nuser: I need a scraper for public price pages. Start simple.\nassistant: A fetch function, a parser per site, and a CSV writer. Respect robots.txt and add a user agent with a contact address.\n\n[Recent turns]\nassistant: ```python\ndef fetch(url):\n    return requests.get(url, headers=HEADERS, timeout=20).text\n```\nuser: Normalise URLs so we don't scrape the same page twice.\nassistant: ```python\ndef normalize_url(url):\n    parts = urlsplit(url)\n    query = urlencode(sorted(parse_qsl(parts.query)))\n    return urlunsplit((parts.scheme, parts.netloc.lower(), parts.path.rstrip('/'), query, ''))\n```\nassistant: ```python\nasync def fetch(url, session):\n    async with session.get(url, headers=HEADERS) as resp:\n        return await resp.text()\n```\nOne `aiohttp.ClientSession` is created in `main` and passed down; concurrency is capped with a semaphore of 20.\nuser: Some sites block us.\nuser: Parse prices that look like 'Rs. 1,250.00' or '1.250,00 \u20ac'.\nassistant: Use `price-parser`'s `Price.fromstring`, which handles both separators and currency symbols, and store amount plus currency code.\nuser: Store results in SQLite instead of CSV.\nassistant: A `prices` table keyed on (normalized_url, scraped_at) with amount, currency and raw text; writes batched in transactions of 500.",
    "truncated": false
   },
   "raised": [],
   "traps": []
  },
  {
   "exchange": 9,
   "turn_id": "t0017",
   "user": "Write a parser for the new electronics site.",
   "assistant": "Selectors live in a per-site config: product name from `h1.title`, price from `[itemprop=price]`, availability from the JSON-LD block when present.",
   "signal": {
    "turn_count": 17,
    "task_type": "chat",
    "matched_pattern": "shift_default",
    "topic_similarity": 0.029,
    "shift": true,
    "recall_request": false,
    "tokens_used": 413,
    "budget": 700
   },
   "features": {
    "turn_count": 17,
    "token_budget_pressure": 0.59,
    "task_type": "chat",
    "prior_strategy": "hybrid",
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
     "reason": "token pressure 0.59 < 0.90: full recent history fits, window is lossless"
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
    "latency_ms": 0.077,
    "override": [],
    "full": "[history_fits] token pressure 0.59 < 0.90: full recent history fits, window is lossless | dwell: held hybrid (2 < 3 turns since last switch) | features: turn=17, pressure=0.59, task=chat, prior=hybrid, since_switch=2",
    "rule": "history_fits",
    "rule_reason": "token pressure 0.59 < 0.90: full recent history fits, window is lossless",
    "dwell": [
     "dwell: held hybrid (2 < 3 turns since last switch)"
    ],
    "escalations": []
   },
   "candidates": {
    "sliding_window": {
     "tokens": 368,
     "latency_ms": 0.46,
     "quality": {
      "kept": 13,
      "relevance": 0.139,
      "freshness": 0.614,
      "importance": 0.211,
      "state": 0.202,
      "composite": 0.292
     }
    },
    "summarization": {
     "tokens": 416,
     "latency_ms": 2.0,
     "quality": {
      "tier_emitted": "L1",
      "loss_score": 0.0526,
      "loss_threshold_exceeded": false,
      "symbol_retention_rate": 1.0
     }
    },
    "rag": {
     "tokens": 255,
     "latency_ms": 289.12,
     "quality": {
      "granularity_tag": "turn",
      "retrieved": 6,
      "stale_flags": 1
     }
    }
   },
   "prompt": {
    "tokens": 475,
    "context": "[Retrieved memory]\n[turns: t0001 t0002]\nuser: I need a scraper for public price pages. Start simple.\nassistant: A fetch function, a parser per site, and a CSV writer. Respect robots.txt and add a user agent with a contact address.\n\n---\n\n[turns: t0011 t0012]\nuser: Parse prices that look like 'Rs. 1,250.00' or '1.250,00 \u20ac'.\nassistant: Use `price-parser`'s `Price.fromstring`, which handles both separators and currency symbols, and store amount plus currency code.\n[!] stale: superseded by turn:t0014 (nli, confidence 0.96) - prefer the newer chunk\n\n---\n\n[turns: t0003]\nuser: Write fetch.\n\n---\n\n[turns: t0009]\nuser: Some sites block us.\n\n---\n\n[turns: t0005]\nuser: Normalise URLs so we don't scrape the same page twice.\n\n[Recent turns]\nassistant: ```python\ndef fetch(url):\n    return requests.get(url, headers=HEADERS, timeout=20).text\n```\nassistant: ```python\ndef normalize_url(url):\n    parts = urlsplit(url)\n    query = urlencode(sorted(parse_qsl(parts.query)))\n    return urlunsplit((parts.scheme, parts.netloc.lower(), parts.path.rstrip('/'), query, ''))\n```\nassistant: ```python\nasync def fetch(url, session):\n    async with session.get(url, headers=HEADERS) as resp:\n        return await resp.text()\n```\nOne `aiohttp.ClientSession` is created in `main` and passed down; concurrency is capped with a semaphore of 20.\nassistant: Honour Retry-After, add per-domain rate limits (1 request per second by default), rotate nothing deceptive, and back off exponentially on 429.\nuser: Store results in SQLite instead of CSV.\nassistant: A `prices` table keyed on (normalized_url, scraped_at) with amount, currency and raw text; writes batched in transactions of 500.\nuser: Schedule it daily.\nassistant: A systemd timer on the VM at 04:30 with `Persistent=true`, logs to the journal, and a heartbeat ping to the uptime monitor at the end of a successful run.",
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
   "traps": []
  },
  {
   "exchange": 10,
   "turn_id": "t0019",
   "user": "Add a crawler step that fetches every product link found on a category page.",
   "assistant": "(scripted reply omitted - the check is on the context the model would receive)",
   "signal": {
    "turn_count": 19,
    "task_type": "chat",
    "matched_pattern": "shift_default",
    "topic_similarity": 0.072,
    "shift": true,
    "recall_request": false,
    "tokens_used": 469,
    "budget": 700
   },
   "features": {
    "turn_count": 19,
    "token_budget_pressure": 0.67,
    "task_type": "chat",
    "prior_strategy": "hybrid",
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
     "reason": "token pressure 0.67 < 0.90: full recent history fits, window is lossless"
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
    "latency_ms": 0.0902,
    "override": [],
    "full": "[history_fits] token pressure 0.67 < 0.90: full recent history fits, window is lossless | escalation from t0017: 1 stale chunk(s) flagged -> hybrid so the superseding facts are retrievable next to the recent window | features: turn=19, pressure=0.67, task=chat, prior=hybrid, since_switch=3",
    "rule": "history_fits",
    "rule_reason": "token pressure 0.67 < 0.90: full recent history fits, window is lossless",
    "dwell": [],
    "escalations": [
     "escalation from t0017: 1 stale chunk(s) flagged -> hybrid so the superseding facts are retrievable next to the recent window"
    ]
   },
   "candidates": {
    "sliding_window": {
     "tokens": 294,
     "latency_ms": 0.48,
     "quality": {
      "kept": 10,
      "relevance": 0.155,
      "freshness": 0.628,
      "importance": 0.245,
      "state": 0.2,
      "composite": 0.307
     }
    },
    "summarization": {
     "tokens": 465,
     "latency_ms": 2.3,
     "quality": {
      "tier_emitted": "L1",
      "loss_score": 0.0526,
      "loss_threshold_exceeded": false,
      "symbol_retention_rate": 1.0
     }
    },
    "rag": {
     "tokens": 396,
     "latency_ms": 269.45,
     "quality": {
      "granularity_tag": "turn",
      "retrieved": 8,
      "stale_flags": 1
     }
    }
   },
   "prompt": {
    "tokens": 454,
    "context": "[Retrieved memory]\n[turns: t0001 t0002]\nuser: I need a scraper for public price pages. Start simple.\nassistant: A fetch function, a parser per site, and a CSV writer. Respect robots.txt and add a user agent with a contact address.\n\n---\n\n[turns: t0004]\nassistant: ```python\ndef fetch(url):\n    return requests.get(url, headers=HEADERS, timeout=20).text\n```\n[!] stale: superseded by turn:t0008 (signature_diff, confidence 1.00) - prefer the newer chunk\n\n---\n\n[turns: t0008 | supersedes turn:t0004]\nassistant: ```python\nasync def fetch(url, session):\n    async with session.get(url, headers=HEADERS) as resp:\n        return await resp.text()\n```\nOne `aiohttp.ClientSession` is created in `main` and passed down; concurrency is capped with a semaphore of 20.\n\n---\n\n[turns: t0005]\nuser: Normalise URLs so we don't scrape the same page twice.\n\n---\n\n[turns: t0007]\nuser: It's too slow for 20k pages. Go async.\n\n---\n\n[turns: t0014]\nassistant: A `prices` table keyed on (normalized_url, scraped_at) with amount, currency and raw text; writes batched in transactions of 500.\n\n[Recent turns]\nassistant: ```python\ndef normalize_url(url):\n    parts = urlsplit(url)\n    query = urlencode(sorted(parse_qsl(parts.query)))\n    return urlunsplit((parts.scheme, parts.netloc.lower(), parts.path.rstrip('/'), query, ''))\n```\nuser: Store results in SQLite instead of CSV.\nuser: Schedule it daily.\nassistant: A systemd timer on the VM at 04:30 with `Persistent=true`, logs to the journal, and a heartbeat ping to the uptime monitor at the end of a successful run.\nuser: Write a parser for the new electronics site.\nassistant: Selectors live in a per-site config: product name from `h1.title`, price from `[itemprop=price]`, availability from the JSON-LD block when present.",
    "truncated": false
   },
   "raised": [],
   "traps": [
    {
     "name": "now async",
     "description": "fetch became async with a session parameter at exchange 4",
     "planted_at": 4,
     "kind": "signature",
     "adaptive": {
      "caught": true,
      "detail": "found `async def fetch(url, session)`",
      "strategy": "hybrid"
     },
     "fixed_6_exchange_window": {
      "caught": true,
      "detail": "found `async def fetch(url, session)`"
     },
     "sliding_window": {
      "caught": false,
      "detail": "unmarked stale `def fetch(url):` present"
     },
     "summarization": {
      "caught": true,
      "detail": "found `async def fetch(url, session)`"
     },
     "rag": {
      "caught": true,
      "detail": "found `async def fetch(url, session)`"
     },
     "hybrid": {
      "caught": true,
      "detail": "found `async def fetch(url, session)`"
     }
    }
   ]
  },
  {
   "exchange": 11,
   "turn_id": "t0021",
   "user": "Before queueing links, canonicalise them so duplicates with different query orders collapse.",
   "assistant": "(scripted reply omitted - the check is on the context the model would receive)",
   "signal": {
    "turn_count": 21,
    "task_type": "chat",
    "matched_pattern": "carry_over",
    "topic_similarity": 0.215,
    "shift": false,
    "recall_request": false,
    "tokens_used": 506,
    "budget": 700
   },
   "features": {
    "turn_count": 21,
    "token_budget_pressure": 0.7229,
    "task_type": "chat",
    "prior_strategy": "hybrid",
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
     "reason": "token pressure 0.72 < 0.90: full recent history fits, window is lossless"
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
    "latency_ms": 0.0773,
    "override": [],
    "full": "[history_fits] token pressure 0.72 < 0.90: full recent history fits, window is lossless | features: turn=21, pressure=0.72, task=chat, prior=hybrid, since_switch=4",
    "rule": "history_fits",
    "rule_reason": "token pressure 0.72 < 0.90: full recent history fits, window is lossless",
    "dwell": [],
    "escalations": []
   },
   "candidates": {
    "sliding_window": {
     "tokens": 353,
     "latency_ms": 0.49,
     "quality": {
      "kept": 12,
      "relevance": 0.174,
      "freshness": 0.589,
      "importance": 0.217,
      "state": 0.328,
      "composite": 0.327
     }
    },
    "summarization": {
     "tokens": 502,
     "latency_ms": 2.67,
     "quality": {
      "tier_emitted": "L1",
      "loss_score": 0.0526,
      "loss_threshold_exceeded": false,
      "symbol_retention_rate": 1.0
     }
    },
    "rag": {
     "tokens": 291,
     "latency_ms": 251.46,
     "quality": {
      "granularity_tag": "turn",
      "retrieved": 7,
      "stale_flags": 0
     }
    }
   },
   "prompt": {
    "tokens": 355,
    "context": "assistant: ```python\ndef fetch(url):\n    return requests.get(url, headers=HEADERS, timeout=20).text\n```\nuser: Normalise URLs so we don't scrape the same page twice.\nassistant: ```python\ndef normalize_url(url):\n    parts = urlsplit(url)\n    query = urlencode(sorted(parse_qsl(parts.query)))\n    return urlunsplit((parts.scheme, parts.netloc.lower(), parts.path.rstrip('/'), query, ''))\n```\nassistant: ```python\nasync def fetch(url, session):\n    async with session.get(url, headers=HEADERS) as resp:\n        return await resp.text()\n```\nOne `aiohttp.ClientSession` is created in `main` and passed down; concurrency is capped with a semaphore of 20.\nassistant: Honour Retry-After, add per-domain rate limits (1 request per second by default), rotate nothing deceptive, and back off exponentially on 429.\nassistant: A `prices` table keyed on (normalized_url, scraped_at) with amount, currency and raw text; writes batched in transactions of 500.\nuser: Schedule it daily.\nassistant: A systemd timer on the VM at 04:30 with `Persistent=true`, logs to the journal, and a heartbeat ping to the uptime monitor at the end of a successful run.\nuser: Write a parser for the new electronics site.\nassistant: Selectors live in a per-site config: product name from `h1.title`, price from `[itemprop=price]`, availability from the JSON-LD block when present.\nuser: Add a crawler step that fetches every product link found on a category page.\nassistant: (scripted reply omitted - the check is on the context the model would receive)",
    "truncated": false
   },
   "raised": [],
   "traps": [
    {
     "name": "duplicate URL normaliser",
     "description": "normalize_url exists since exchange 3",
     "planted_at": 3,
     "kind": "duplicate",
     "adaptive": {
      "caught": true,
      "detail": "found `def normalize_url(`",
      "strategy": "sliding_window"
     },
     "fixed_6_exchange_window": {
      "caught": false,
      "detail": "missing `def normalize_url(`"
     },
     "sliding_window": {
      "caught": true,
      "detail": "found `def normalize_url(`"
     },
     "summarization": {
      "caught": true,
      "detail": "found `def normalize_url(`"
     },
     "rag": {
      "caught": true,
      "detail": "found `def normalize_url(`"
     },
     "hybrid": {
      "caught": true,
      "detail": "found `def normalize_url(`"
     }
    }
   ]
  }
 ]
};
