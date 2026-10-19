window.CEAI_SESSIONS = window.CEAI_SESSIONS || {};
window.CEAI_SESSIONS["go-client"] = {
 "scenario": "go-client",
 "slug": "go-client",
 "language": "go",
 "held_out": true,
 "system": "frozen",
 "mode": "full",
 "budget": 700,
 "recorded_at": "2026-10-19T11:23:18+00:00",
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
   "user": "I'm writing a Go client for our internal metrics API. How should it look?",
   "assistant": "A `metrics` package with a `Client` struct holding an `*http.Client` and base URL, a constructor, and one method per endpoint returning typed structs and an error.",
   "signal": {
    "turn_count": 1,
    "task_type": "chat",
    "matched_pattern": "carry_over",
    "topic_similarity": null,
    "shift": false,
    "recall_request": false,
    "tokens_used": 19,
    "budget": 700
   },
   "features": {
    "turn_count": 1,
    "token_budget_pressure": 0.0271,
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
    "latency_ms": 0.0861,
    "override": [],
    "full": "[history_fits] token pressure 0.03 < 0.90: full recent history fits, window is lossless | features: turn=1, pressure=0.03, task=chat, prior=None, since_switch=0",
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
     "latency_ms": 1.12,
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
   "user": "Write the constructor.",
   "assistant": "```go\nfunc NewClient(addr string) *Client {\n    return &Client{base: addr, http: &http.Client{}}\n}\n```",
   "signal": {
    "turn_count": 3,
    "task_type": "chat",
    "matched_pattern": "carry_over",
    "topic_similarity": null,
    "shift": false,
    "recall_request": false,
    "tokens_used": 64,
    "budget": 700
   },
   "features": {
    "turn_count": 3,
    "token_budget_pressure": 0.0914,
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
    "latency_ms": 0.1064,
    "override": [],
    "full": "[history_fits] token pressure 0.09 < 0.90: full recent history fits, window is lossless | features: turn=3, pressure=0.09, task=chat, prior=sliding_window, since_switch=0",
    "rule": "history_fits",
    "rule_reason": "token pressure 0.09 < 0.90: full recent history fits, window is lossless",
    "dwell": [],
    "escalations": []
   },
   "candidates": {
    "sliding_window": {
     "tokens": 58,
     "latency_ms": 0.73,
     "quality": {
      "kept": 2,
      "relevance": 0.115,
      "freshness": 0.959,
      "importance": 0.1,
      "state": 1.0,
      "composite": 0.543
     }
    },
    "summarization": {
     "tokens": 62,
     "latency_ms": 1.01,
     "quality": {
      "tier_emitted": "L1",
      "loss_score": 0.0,
      "loss_threshold_exceeded": false,
      "symbol_retention_rate": null
     }
    },
    "rag": {
     "tokens": 47,
     "latency_ms": 1076.98,
     "quality": {
      "granularity_tag": "turn",
      "retrieved": 1,
      "stale_flags": 0
     }
    }
   },
   "prompt": {
    "tokens": 58,
    "context": "user: I'm writing a Go client for our internal metrics API. How should it look?\nassistant: A `metrics` package with a `Client` struct holding an `*http.Client` and base URL, a constructor, and one method per endpoint returning typed structs and an error.",
    "truncated": false
   },
   "raised": [],
   "traps": []
  },
  {
   "exchange": 3,
   "turn_id": "t0005",
   "user": "Requests hang forever when the server is down. The constructor must take a timeout.",
   "assistant": "```go\nfunc NewClient(addr string, timeout time.Duration) *Client {\n    return &Client{base: addr, http: &http.Client{Timeout: timeout}}\n}\n```\nCallers now pass e.g. `5*time.Second`.",
   "signal": {
    "turn_count": 5,
    "task_type": "chat",
    "matched_pattern": "carry_over",
    "topic_similarity": null,
    "shift": false,
    "recall_request": false,
    "tokens_used": 114,
    "budget": 700
   },
   "features": {
    "turn_count": 5,
    "token_budget_pressure": 0.1629,
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
    "latency_ms": 0.0945,
    "override": [],
    "full": "[history_fits] token pressure 0.16 < 0.90: full recent history fits, window is lossless | features: turn=5, pressure=0.16, task=chat, prior=sliding_window, since_switch=1",
    "rule": "history_fits",
    "rule_reason": "token pressure 0.16 < 0.90: full recent history fits, window is lossless",
    "dwell": [],
    "escalations": []
   },
   "candidates": {
    "sliding_window": {
     "tokens": 96,
     "latency_ms": 0.7,
     "quality": {
      "kept": 4,
      "relevance": 0.212,
      "freshness": 0.882,
      "importance": 0.125,
      "state": 1.0,
      "composite": 0.555
     }
    },
    "summarization": {
     "tokens": 100,
     "latency_ms": 0.94,
     "quality": {
      "tier_emitted": "L1",
      "loss_score": 0.0,
      "loss_threshold_exceeded": false,
      "symbol_retention_rate": null
     }
    },
    "rag": {
     "tokens": 125,
     "latency_ms": 880.19,
     "quality": {
      "granularity_tag": "turn",
      "retrieved": 3,
      "stale_flags": 0
     }
    }
   },
   "prompt": {
    "tokens": 96,
    "context": "user: I'm writing a Go client for our internal metrics API. How should it look?\nassistant: A `metrics` package with a `Client` struct holding an `*http.Client` and base URL, a constructor, and one method per endpoint returning typed structs and an error.\nuser: Write the constructor.\nassistant: ```go\nfunc NewClient(addr string) *Client {\n    return &Client{base: addr, http: &http.Client{}}\n}\n```",
    "truncated": false
   },
   "raised": [],
   "traps": []
  },
  {
   "exchange": 4,
   "turn_id": "t0007",
   "user": "Add a method to push a batch of samples.",
   "assistant": "`func (c *Client) Push(ctx context.Context, samples []Sample) error` marshals to JSON, POSTs to /v1/push with the context, and returns a typed `*APIError` on non-2xx.",
   "signal": {
    "turn_count": 7,
    "task_type": "code_generation",
    "matched_pattern": "pattern:code_generation",
    "topic_similarity": 0.016,
    "shift": true,
    "recall_request": false,
    "tokens_used": 178,
    "budget": 700
   },
   "features": {
    "turn_count": 7,
    "token_budget_pressure": 0.2543,
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
    "latency_ms": 0.0802,
    "override": [],
    "full": "[history_fits] token pressure 0.25 < 0.90: full recent history fits, window is lossless | features: turn=7, pressure=0.25, task=code_generation, prior=sliding_window, since_switch=2",
    "rule": "history_fits",
    "rule_reason": "token pressure 0.25 < 0.90: full recent history fits, window is lossless",
    "dwell": [],
    "escalations": []
   },
   "candidates": {
    "sliding_window": {
     "tokens": 166,
     "latency_ms": 0.66,
     "quality": {
      "kept": 6,
      "relevance": 0.037,
      "freshness": 0.814,
      "importance": 0.2,
      "state": 0.5,
      "composite": 0.388
     }
    },
    "summarization": {
     "tokens": 171,
     "latency_ms": 0.92,
     "quality": {
      "tier_emitted": "L1",
      "loss_score": 0.0,
      "loss_threshold_exceeded": false,
      "symbol_retention_rate": null
     }
    },
    "rag": {
     "tokens": 0,
     "latency_ms": 704.87,
     "quality": {
      "granularity_tag": "turn",
      "retrieved": 0,
      "stale_flags": 0
     }
    }
   },
   "prompt": {
    "tokens": 167,
    "context": "user: I'm writing a Go client for our internal metrics API. How should it look?\nassistant: A `metrics` package with a `Client` struct holding an `*http.Client` and base URL, a constructor, and one method per endpoint returning typed structs and an error.\nuser: Write the constructor.\nassistant: ```go\nfunc NewClient(addr string) *Client {\n    return &Client{base: addr, http: &http.Client{}}\n}\n```\nuser: Requests hang forever when the server is down. The constructor must take a timeout.\nassistant: ```go\nfunc NewClient(addr string, timeout time.Duration) *Client {\n    return &Client{base: addr, http: &http.Client{Timeout: timeout}}\n}\n```\nCallers now pass e.g. `5*time.Second`.",
    "truncated": false
   },
   "raised": [],
   "traps": []
  },
  {
   "exchange": 5,
   "turn_id": "t0009",
   "user": "Write table-driven tests.",
   "assistant": "Tests use `httptest.NewServer` with cases for success, 500, malformed JSON and context cancellation; each case asserts the error type with `errors.As`.",
   "signal": {
    "turn_count": 9,
    "task_type": "code_generation",
    "matched_pattern": "pattern:code_generation",
    "topic_similarity": 0.208,
    "shift": false,
    "recall_request": false,
    "tokens_used": 237,
    "budget": 700
   },
   "features": {
    "turn_count": 9,
    "token_budget_pressure": 0.3386,
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
     "reason": "token pressure 0.34 < 0.90: full recent history fits, window is lossless"
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
    "latency_ms": 0.0764,
    "override": [],
    "full": "[history_fits] token pressure 0.34 < 0.90: full recent history fits, window is lossless | features: turn=9, pressure=0.34, task=code_generation, prior=sliding_window, since_switch=3",
    "rule": "history_fits",
    "rule_reason": "token pressure 0.34 < 0.90: full recent history fits, window is lossless",
    "dwell": [],
    "escalations": []
   },
   "candidates": {
    "sliding_window": {
     "tokens": 230,
     "latency_ms": 0.62,
     "quality": {
      "kept": 8,
      "relevance": 0.065,
      "freshness": 0.753,
      "importance": 0.188,
      "state": 0.625,
      "composite": 0.408
     }
    },
    "summarization": {
     "tokens": 235,
     "latency_ms": 0.89,
     "quality": {
      "tier_emitted": "L1",
      "loss_score": 0.0,
      "loss_threshold_exceeded": false,
      "symbol_retention_rate": null
     }
    },
    "rag": {
     "tokens": 20,
     "latency_ms": 564.59,
     "quality": {
      "granularity_tag": "turn",
      "retrieved": 1,
      "stale_flags": 0
     }
    }
   },
   "prompt": {
    "tokens": 231,
    "context": "user: I'm writing a Go client for our internal metrics API. How should it look?\nassistant: A `metrics` package with a `Client` struct holding an `*http.Client` and base URL, a constructor, and one method per endpoint returning typed structs and an error.\nuser: Write the constructor.\nassistant: ```go\nfunc NewClient(addr string) *Client {\n    return &Client{base: addr, http: &http.Client{}}\n}\n```\nuser: Requests hang forever when the server is down. The constructor must take a timeout.\nassistant: ```go\nfunc NewClient(addr string, timeout time.Duration) *Client {\n    return &Client{base: addr, http: &http.Client{Timeout: timeout}}\n}\n```\nCallers now pass e.g. `5*time.Second`.\nuser: Add a method to push a batch of samples.\nassistant: `func (c *Client) Push(ctx context.Context, samples []Sample) error` marshals to JSON, POSTs to /v1/push with the context, and returns a typed `*APIError` on non-2xx.",
    "truncated": false
   },
   "raised": [],
   "traps": []
  },
  {
   "exchange": 6,
   "turn_id": "t0011",
   "user": "Add retries.",
   "assistant": "Wrapped the transport in a small retrier: up to 3 attempts on 502/503/504 and network errors, exponential backoff with jitter, never retrying after the context is done.",
   "signal": {
    "turn_count": 11,
    "task_type": "chat",
    "matched_pattern": "shift_default",
    "topic_similarity": 0.06,
    "shift": true,
    "recall_request": false,
    "tokens_used": 277,
    "budget": 700
   },
   "features": {
    "turn_count": 11,
    "token_budget_pressure": 0.3957,
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
    "latency_ms": 0.0799,
    "override": [],
    "full": "[history_fits] token pressure 0.40 < 0.90: full recent history fits, window is lossless | features: turn=11, pressure=0.40, task=chat, prior=sliding_window, since_switch=4",
    "rule": "history_fits",
    "rule_reason": "token pressure 0.40 < 0.90: full recent history fits, window is lossless",
    "dwell": [],
    "escalations": []
   },
   "candidates": {
    "sliding_window": {
     "tokens": 272,
     "latency_ms": 0.59,
     "quality": {
      "kept": 10,
      "relevance": 0.096,
      "freshness": 0.698,
      "importance": 0.185,
      "state": 0.35,
      "composite": 0.332
     }
    },
    "summarization": {
     "tokens": 253,
     "latency_ms": 1.14,
     "quality": {
      "tier_emitted": "L1",
      "loss_score": 0.3333,
      "loss_threshold_exceeded": true,
      "symbol_retention_rate": null
     }
    },
    "rag": {
     "tokens": 40,
     "latency_ms": 457.32,
     "quality": {
      "granularity_tag": "turn",
      "retrieved": 1,
      "stale_flags": 0
     }
    }
   },
   "prompt": {
    "tokens": 273,
    "context": "user: I'm writing a Go client for our internal metrics API. How should it look?\nassistant: A `metrics` package with a `Client` struct holding an `*http.Client` and base URL, a constructor, and one method per endpoint returning typed structs and an error.\nuser: Write the constructor.\nassistant: ```go\nfunc NewClient(addr string) *Client {\n    return &Client{base: addr, http: &http.Client{}}\n}\n```\nuser: Requests hang forever when the server is down. The constructor must take a timeout.\nassistant: ```go\nfunc NewClient(addr string, timeout time.Duration) *Client {\n    return &Client{base: addr, http: &http.Client{Timeout: timeout}}\n}\n```\nCallers now pass e.g. `5*time.Second`.\nuser: Add a method to push a batch of samples.\nassistant: `func (c *Client) Push(ctx context.Context, samples []Sample) error` marshals to JSON, POSTs to /v1/push with the context, and returns a typed `*APIError` on non-2xx.\nuser: Write table-driven tests.\nassistant: Tests use `httptest.NewServer` with cases for success, 500, malformed JSON and context cancellation; each case asserts the error type with `errors.As`.",
    "truncated": false
   },
   "raised": [
    {
     "kind": "loss_threshold_exceeded",
     "source_module": "summarization",
     "detail": {
      "loss_score": 0.3333,
      "tier_emitted": "L1",
      "symbol_retention_rate": null
     }
    }
   ],
   "traps": []
  },
  {
   "exchange": 7,
   "turn_id": "t0013",
   "user": "Expose Prometheus metrics for the client itself.",
   "assistant": "A histogram of request durations labelled by endpoint and status class, and a counter of retries, registered on an optional registerer passed via a functional option.",
   "signal": {
    "turn_count": 13,
    "task_type": "chat",
    "matched_pattern": "shift_default",
    "topic_similarity": 0.139,
    "shift": true,
    "recall_request": false,
    "tokens_used": 330,
    "budget": 700
   },
   "features": {
    "turn_count": 13,
    "token_budget_pressure": 0.4714,
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
    "latency_ms": 0.0969,
    "override": [],
    "full": "[history_fits] token pressure 0.47 < 0.90: full recent history fits, window is lossless | escalation from t0011 (loss_threshold_exceeded) noted; no change for sliding_window | features: turn=13, pressure=0.47, task=chat, prior=sliding_window, since_switch=5",
    "rule": "history_fits",
    "rule_reason": "token pressure 0.47 < 0.90: full recent history fits, window is lossless",
    "dwell": [],
    "escalations": [
     "escalation from t0011 (loss_threshold_exceeded) noted; no change for sliding_window"
    ]
   },
   "candidates": {
    "sliding_window": {
     "tokens": 313,
     "latency_ms": 0.58,
     "quality": {
      "kept": 11,
      "relevance": 0.199,
      "freshness": 0.666,
      "importance": 0.196,
      "state": 0.239,
      "composite": 0.325
     }
    },
    "summarization": {
     "tokens": 300,
     "latency_ms": 1.3,
     "quality": {
      "tier_emitted": "L1",
      "loss_score": 0.3333,
      "loss_threshold_exceeded": true,
      "symbol_retention_rate": null
     }
    },
    "rag": {
     "tokens": 284,
     "latency_ms": 390.44,
     "quality": {
      "granularity_tag": "turn",
      "retrieved": 5,
      "stale_flags": 0
     }
    }
   },
   "prompt": {
    "tokens": 314,
    "context": "user: I'm writing a Go client for our internal metrics API. How should it look?\nassistant: A `metrics` package with a `Client` struct holding an `*http.Client` and base URL, a constructor, and one method per endpoint returning typed structs and an error.\nassistant: ```go\nfunc NewClient(addr string) *Client {\n    return &Client{base: addr, http: &http.Client{}}\n}\n```\nuser: Requests hang forever when the server is down. The constructor must take a timeout.\nassistant: ```go\nfunc NewClient(addr string, timeout time.Duration) *Client {\n    return &Client{base: addr, http: &http.Client{Timeout: timeout}}\n}\n```\nCallers now pass e.g. `5*time.Second`.\nuser: Add a method to push a batch of samples.\nassistant: `func (c *Client) Push(ctx context.Context, samples []Sample) error` marshals to JSON, POSTs to /v1/push with the context, and returns a typed `*APIError` on non-2xx.\nuser: Write table-driven tests.\nassistant: Tests use `httptest.NewServer` with cases for success, 500, malformed JSON and context cancellation; each case asserts the error type with `errors.As`.\nuser: Add retries.\nassistant: Wrapped the transport in a small retrier: up to 3 attempts on 502/503/504 and network errors, exponential backoff with jitter, never retrying after the context is done.",
    "truncated": false
   },
   "raised": [
    {
     "kind": "loss_threshold_exceeded",
     "source_module": "summarization",
     "detail": {
      "loss_score": 0.3333,
      "tier_emitted": "L1",
      "symbol_retention_rate": null
     }
    }
   ],
   "traps": []
  },
  {
   "exchange": 8,
   "turn_id": "t0015",
   "user": "Make it a proper module others can import.",
   "assistant": "`go mod init git.internal/platform/metrics`, tagged v0.1.0, with a README example and `go vet` plus `staticcheck` in CI.",
   "signal": {
    "turn_count": 15,
    "task_type": "code_generation",
    "matched_pattern": "pattern:code_generation",
    "topic_similarity": 0.156,
    "shift": false,
    "recall_request": false,
    "tokens_used": 373,
    "budget": 700
   },
   "features": {
    "turn_count": 15,
    "token_budget_pressure": 0.5329,
    "task_type": "code_generation",
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
    "latency_ms": 0.0727,
    "override": [],
    "full": "[history_fits] token pressure 0.53 < 0.90: full recent history fits, window is lossless | escalation from t0013 (loss_threshold_exceeded) noted; no change for sliding_window | features: turn=15, pressure=0.53, task=code_generation, prior=sliding_window, since_switch=6",
    "rule": "history_fits",
    "rule_reason": "token pressure 0.53 < 0.90: full recent history fits, window is lossless",
    "dwell": [],
    "escalations": [
     "escalation from t0013 (loss_threshold_exceeded) noted; no change for sliding_window"
    ]
   },
   "candidates": {
    "sliding_window": {
     "tokens": 337,
     "latency_ms": 0.54,
     "quality": {
      "kept": 12,
      "relevance": 0.122,
      "freshness": 0.646,
      "importance": 0.179,
      "state": 0.375,
      "composite": 0.331
     }
    },
    "summarization": {
     "tokens": 343,
     "latency_ms": 1.41,
     "quality": {
      "tier_emitted": "L1",
      "loss_score": 0.3333,
      "loss_threshold_exceeded": true,
      "symbol_retention_rate": null
     }
    },
    "rag": {
     "tokens": 221,
     "latency_ms": 313.05,
     "quality": {
      "granularity_tag": "turn",
      "retrieved": 6,
      "stale_flags": 0
     }
    }
   },
   "prompt": {
    "tokens": 338,
    "context": "assistant: A `metrics` package with a `Client` struct holding an `*http.Client` and base URL, a constructor, and one method per endpoint returning typed structs and an error.\nassistant: ```go\nfunc NewClient(addr string) *Client {\n    return &Client{base: addr, http: &http.Client{}}\n}\n```\nuser: Requests hang forever when the server is down. The constructor must take a timeout.\nassistant: ```go\nfunc NewClient(addr string, timeout time.Duration) *Client {\n    return &Client{base: addr, http: &http.Client{Timeout: timeout}}\n}\n```\nCallers now pass e.g. `5*time.Second`.\nuser: Add a method to push a batch of samples.\nassistant: `func (c *Client) Push(ctx context.Context, samples []Sample) error` marshals to JSON, POSTs to /v1/push with the context, and returns a typed `*APIError` on non-2xx.\nuser: Write table-driven tests.\nassistant: Tests use `httptest.NewServer` with cases for success, 500, malformed JSON and context cancellation; each case asserts the error type with `errors.As`.\nuser: Add retries.\nassistant: Wrapped the transport in a small retrier: up to 3 attempts on 502/503/504 and network errors, exponential backoff with jitter, never retrying after the context is done.\nuser: Expose Prometheus metrics for the client itself.\nassistant: A histogram of request durations labelled by endpoint and status class, and a counter of retries, registered on an optional registerer passed via a functional option.",
    "truncated": false
   },
   "raised": [
    {
     "kind": "loss_threshold_exceeded",
     "source_module": "summarization",
     "detail": {
      "loss_score": 0.3333,
      "tier_emitted": "L1",
      "symbol_retention_rate": null
     }
    }
   ],
   "traps": []
  },
  {
   "exchange": 9,
   "turn_id": "t0017",
   "user": "Lint complains about exported identifiers without comments.",
   "assistant": "Added doc comments to every exported type and function, starting with the identifier name as golint expects.",
   "signal": {
    "turn_count": 17,
    "task_type": "chat",
    "matched_pattern": "shift_default",
    "topic_similarity": 0.139,
    "shift": true,
    "recall_request": false,
    "tokens_used": 421,
    "budget": 700
   },
   "features": {
    "turn_count": 17,
    "token_budget_pressure": 0.6014,
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
    "latency_ms": 0.094,
    "override": [],
    "full": "[history_fits] token pressure 0.60 < 0.90: full recent history fits, window is lossless | escalation from t0015 (loss_threshold_exceeded) noted; no change for sliding_window | features: turn=17, pressure=0.60, task=chat, prior=sliding_window, since_switch=7",
    "rule": "history_fits",
    "rule_reason": "token pressure 0.60 < 0.90: full recent history fits, window is lossless",
    "dwell": [],
    "escalations": [
     "escalation from t0015 (loss_threshold_exceeded) noted; no change for sliding_window"
    ]
   },
   "candidates": {
    "sliding_window": {
     "tokens": 277,
     "latency_ms": 0.52,
     "quality": {
      "kept": 9,
      "relevance": 0.077,
      "freshness": 0.711,
      "importance": 0.183,
      "state": 0.312,
      "composite": 0.321
     }
    },
    "summarization": {
     "tokens": 395,
     "latency_ms": 1.67,
     "quality": {
      "tier_emitted": "L1",
      "loss_score": 0.1579,
      "loss_threshold_exceeded": true,
      "symbol_retention_rate": null
     }
    },
    "rag": {
     "tokens": 95,
     "latency_ms": 264.38,
     "quality": {
      "granularity_tag": "turn",
      "retrieved": 3,
      "stale_flags": 0
     }
    }
   },
   "prompt": {
    "tokens": 277,
    "context": "assistant: ```go\nfunc NewClient(addr string, timeout time.Duration) *Client {\n    return &Client{base: addr, http: &http.Client{Timeout: timeout}}\n}\n```\nCallers now pass e.g. `5*time.Second`.\nassistant: `func (c *Client) Push(ctx context.Context, samples []Sample) error` marshals to JSON, POSTs to /v1/push with the context, and returns a typed `*APIError` on non-2xx.\nassistant: Tests use `httptest.NewServer` with cases for success, 500, malformed JSON and context cancellation; each case asserts the error type with `errors.As`.\nuser: Add retries.\nassistant: Wrapped the transport in a small retrier: up to 3 attempts on 502/503/504 and network errors, exponential backoff with jitter, never retrying after the context is done.\nuser: Expose Prometheus metrics for the client itself.\nassistant: A histogram of request durations labelled by endpoint and status class, and a counter of retries, registered on an optional registerer passed via a functional option.\nuser: Make it a proper module others can import.\nassistant: `go mod init git.internal/platform/metrics`, tagged v0.1.0, with a README example and `go vet` plus `staticcheck` in CI.",
    "truncated": false
   },
   "raised": [
    {
     "kind": "loss_threshold_exceeded",
     "source_module": "summarization",
     "detail": {
      "loss_score": 0.1579,
      "tier_emitted": "L1",
      "symbol_retention_rate": null
     }
    }
   ],
   "traps": []
  },
  {
   "exchange": 10,
   "turn_id": "t0019",
   "user": "Write the main function for the exporter binary that creates a metrics client for http://metrics:9000.",
   "assistant": "(scripted reply omitted - the check is on the context the model would receive)",
   "signal": {
    "turn_count": 19,
    "task_type": "code_generation",
    "matched_pattern": "pattern:code_generation",
    "topic_similarity": 0.196,
    "shift": false,
    "recall_request": false,
    "tokens_used": 466,
    "budget": 700
   },
   "features": {
    "turn_count": 19,
    "token_budget_pressure": 0.6657,
    "task_type": "code_generation",
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
    "latency_ms": 0.0594,
    "override": [],
    "full": "[history_fits] token pressure 0.67 < 0.90: full recent history fits, window is lossless | escalation from t0017 (loss_threshold_exceeded) noted; no change for sliding_window | features: turn=19, pressure=0.67, task=code_generation, prior=sliding_window, since_switch=8",
    "rule": "history_fits",
    "rule_reason": "token pressure 0.67 < 0.90: full recent history fits, window is lossless",
    "dwell": [],
    "escalations": [
     "escalation from t0017 (loss_threshold_exceeded) noted; no change for sliding_window"
    ]
   },
   "candidates": {
    "sliding_window": {
     "tokens": 400,
     "latency_ms": 0.49,
     "quality": {
      "kept": 14,
      "relevance": 0.289,
      "freshness": 0.577,
      "importance": 0.154,
      "state": 0.357,
      "composite": 0.344
     }
    },
    "summarization": {
     "tokens": 428,
     "latency_ms": 1.73,
     "quality": {
      "tier_emitted": "L1",
      "loss_score": 0.1579,
      "loss_threshold_exceeded": true,
      "symbol_retention_rate": null
     }
    },
    "rag": {
     "tokens": 527,
     "latency_ms": 212.2,
     "quality": {
      "granularity_tag": "turn",
      "retrieved": 11,
      "stale_flags": 1
     }
    }
   },
   "prompt": {
    "tokens": 401,
    "context": "user: I'm writing a Go client for our internal metrics API. How should it look?\nassistant: A `metrics` package with a `Client` struct holding an `*http.Client` and base URL, a constructor, and one method per endpoint returning typed structs and an error.\nassistant: ```go\nfunc NewClient(addr string) *Client {\n    return &Client{base: addr, http: &http.Client{}}\n}\n```\nassistant: ```go\nfunc NewClient(addr string, timeout time.Duration) *Client {\n    return &Client{base: addr, http: &http.Client{Timeout: timeout}}\n}\n```\nCallers now pass e.g. `5*time.Second`.\nassistant: `func (c *Client) Push(ctx context.Context, samples []Sample) error` marshals to JSON, POSTs to /v1/push with the context, and returns a typed `*APIError` on non-2xx.\nassistant: Tests use `httptest.NewServer` with cases for success, 500, malformed JSON and context cancellation; each case asserts the error type with `errors.As`.\nuser: Add retries.\nassistant: Wrapped the transport in a small retrier: up to 3 attempts on 502/503/504 and network errors, exponential backoff with jitter, never retrying after the context is done.\nuser: Expose Prometheus metrics for the client itself.\nassistant: A histogram of request durations labelled by endpoint and status class, and a counter of retries, registered on an optional registerer passed via a functional option.\nuser: Make it a proper module others can import.\nassistant: `go mod init git.internal/platform/metrics`, tagged v0.1.0, with a README example and `go vet` plus `staticcheck` in CI.\nuser: Lint complains about exported identifiers without comments.\nassistant: Added doc comments to every exported type and function, starting with the identifier name as golint expects.",
    "truncated": false
   },
   "raised": [
    {
     "kind": "loss_threshold_exceeded",
     "source_module": "summarization",
     "detail": {
      "loss_score": 0.1579,
      "tier_emitted": "L1",
      "symbol_retention_rate": null
     }
    },
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
     "name": "added timeout parameter",
     "description": "NewClient gained a timeout parameter at exchange 3",
     "planted_at": 3,
     "kind": "signature",
     "adaptive": {
      "caught": false,
      "detail": "unmarked stale `func NewClient(addr string) *Client` present",
      "strategy": "sliding_window"
     },
     "fixed_6_exchange_window": {
      "caught": false,
      "detail": "missing `func NewClient(addr string, timeout time.Duration)`"
     },
     "sliding_window": {
      "caught": false,
      "detail": "unmarked stale `func NewClient(addr string) *Client` present"
     },
     "summarization": {
      "caught": false,
      "detail": "missing `func NewClient(addr string, timeout time.Duration)`"
     },
     "rag": {
      "caught": false,
      "detail": "unmarked stale `func NewClient(addr string) *Client` present"
     },
     "hybrid": {
      "caught": false,
      "detail": "unmarked stale `func NewClient(addr string) *Client` present"
     }
    }
   ]
  }
 ]
};
