window.CEAI_SESSIONS = window.CEAI_SESSIONS || {};
window.CEAI_SESSIONS["auth-module"] = {
 "scenario": "auth-module",
 "slug": "auth-module",
 "language": "python",
 "held_out": true,
 "system": "frozen",
 "mode": "full",
 "budget": 700,
 "recorded_at": "2026-10-19T11:24:06+00:00",
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
 "n_traps": 3,
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
   "user": "We're replacing our homemade auth with something sane. Where do we start?",
   "assistant": "Password hashing first, then token issuing and verification, then the login and refresh endpoints. Keep the crypto in `auth/security.py` and nothing else touches the hash format directly.",
   "signal": {
    "turn_count": 1,
    "task_type": "chat",
    "matched_pattern": "carry_over",
    "topic_similarity": null,
    "shift": false,
    "recall_request": false,
    "tokens_used": 17,
    "budget": 700
   },
   "features": {
    "turn_count": 1,
    "token_budget_pressure": 0.0243,
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
   "user": "Write the password hashing function.",
   "assistant": "```python\ndef hash_password(password):\n    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()\n```",
   "signal": {
    "turn_count": 3,
    "task_type": "code_generation",
    "matched_pattern": "pattern:code_generation",
    "topic_similarity": null,
    "shift": false,
    "recall_request": false,
    "tokens_used": 62,
    "budget": 700
   },
   "features": {
    "turn_count": 3,
    "token_budget_pressure": 0.0886,
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
    "latency_ms": 0.1071,
    "override": [],
    "full": "[history_fits] token pressure 0.09 < 0.90: full recent history fits, window is lossless | features: turn=3, pressure=0.09, task=code_generation, prior=sliding_window, since_switch=0",
    "rule": "history_fits",
    "rule_reason": "token pressure 0.09 < 0.90: full recent history fits, window is lossless",
    "dwell": [],
    "escalations": []
   },
   "candidates": {
    "sliding_window": {
     "tokens": 54,
     "latency_ms": 0.71,
     "quality": {
      "kept": 2,
      "relevance": 0.393,
      "freshness": 0.959,
      "importance": 0.025,
      "state": 1.0,
      "composite": 0.594
     }
    },
    "summarization": {
     "tokens": 58,
     "latency_ms": 1.12,
     "quality": {
      "tier_emitted": "L1",
      "loss_score": 0.0,
      "loss_threshold_exceeded": false,
      "symbol_retention_rate": null
     }
    },
    "rag": {
     "tokens": 71,
     "latency_ms": 1.24,
     "quality": {
      "granularity_tag": "turn",
      "retrieved": 2,
      "stale_flags": 0
     }
    }
   },
   "prompt": {
    "tokens": 54,
    "context": "user: We're replacing our homemade auth with something sane. Where do we start?\nassistant: Password hashing first, then token issuing and verification, then the login and refresh endpoints. Keep the crypto in `auth/security.py` and nothing else touches the hash format directly.",
    "truncated": false
   },
   "raised": [],
   "traps": []
  },
  {
   "exchange": 3,
   "turn_id": "t0005",
   "user": "Now token verification.",
   "assistant": "```python\nACCESS_TOKEN_TTL = 3600\n\ndef verify_token(token):\n    try:\n        return jwt.decode(token, SECRET_KEY, algorithms=['HS256'])\n    except jwt.PyJWTError:\n        return None\n```",
   "signal": {
    "turn_count": 5,
    "task_type": "code_generation",
    "matched_pattern": "carry_over",
    "topic_similarity": null,
    "shift": false,
    "recall_request": false,
    "tokens_used": 94,
    "budget": 700
   },
   "features": {
    "turn_count": 5,
    "token_budget_pressure": 0.1343,
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
    "latency_ms": 0.0601,
    "override": [],
    "full": "[history_fits] token pressure 0.13 < 0.90: full recent history fits, window is lossless | features: turn=5, pressure=0.13, task=code_generation, prior=sliding_window, since_switch=1",
    "rule": "history_fits",
    "rule_reason": "token pressure 0.13 < 0.90: full recent history fits, window is lossless",
    "dwell": [],
    "escalations": []
   },
   "candidates": {
    "sliding_window": {
     "tokens": 88,
     "latency_ms": 0.64,
     "quality": {
      "kept": 4,
      "relevance": 0.308,
      "freshness": 0.882,
      "importance": 0.163,
      "state": 1.0,
      "composite": 0.588
     }
    },
    "summarization": {
     "tokens": 92,
     "latency_ms": 1.0,
     "quality": {
      "tier_emitted": "L1",
      "loss_score": 0.0,
      "loss_threshold_exceeded": false,
      "symbol_retention_rate": 1.0
     }
    },
    "rag": {
     "tokens": 82,
     "latency_ms": 1.58,
     "quality": {
      "granularity_tag": "segment",
      "retrieved": 2,
      "stale_flags": 0
     }
    }
   },
   "prompt": {
    "tokens": 88,
    "context": "user: We're replacing our homemade auth with something sane. Where do we start?\nassistant: Password hashing first, then token issuing and verification, then the login and refresh endpoints. Keep the crypto in `auth/security.py` and nothing else touches the hash format directly.\nuser: Write the password hashing function.\nassistant: ```python\ndef hash_password(password):\n    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()\n```",
    "truncated": false
   },
   "raised": [],
   "traps": []
  },
  {
   "exchange": 4,
   "turn_id": "t0007",
   "user": "Security review says hashing cost must be configurable and tokens must expire after 15 minutes.",
   "assistant": "```python\nACCESS_TOKEN_TTL = 900\n\ndef hash_password(password, rounds=12):\n    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds)).decode()\n```\nLong sessions are handled by refresh tokens instead.",
   "signal": {
    "turn_count": 7,
    "task_type": "code_generation",
    "matched_pattern": "carry_over",
    "topic_similarity": 0.465,
    "shift": false,
    "recall_request": false,
    "tokens_used": 162,
    "budget": 700
   },
   "features": {
    "turn_count": 7,
    "token_budget_pressure": 0.2314,
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
     "reason": "token pressure 0.23 < 0.90: full recent history fits, window is lossless"
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
    "latency_ms": 0.0702,
    "override": [],
    "full": "[history_fits] token pressure 0.23 < 0.90: full recent history fits, window is lossless | features: turn=7, pressure=0.23, task=code_generation, prior=sliding_window, since_switch=2",
    "rule": "history_fits",
    "rule_reason": "token pressure 0.23 < 0.90: full recent history fits, window is lossless",
    "dwell": [],
    "escalations": []
   },
   "candidates": {
    "sliding_window": {
     "tokens": 143,
     "latency_ms": 0.58,
     "quality": {
      "kept": 6,
      "relevance": 0.313,
      "freshness": 0.814,
      "importance": 0.225,
      "state": 1.0,
      "composite": 0.588
     }
    },
    "summarization": {
     "tokens": 148,
     "latency_ms": 0.95,
     "quality": {
      "tier_emitted": "L1",
      "loss_score": 0.0,
      "loss_threshold_exceeded": false,
      "symbol_retention_rate": 1.0
     }
    },
    "rag": {
     "tokens": 191,
     "latency_ms": 1.89,
     "quality": {
      "granularity_tag": "turn",
      "retrieved": 5,
      "stale_flags": 0
     }
    }
   },
   "prompt": {
    "tokens": 144,
    "context": "user: We're replacing our homemade auth with something sane. Where do we start?\nassistant: Password hashing first, then token issuing and verification, then the login and refresh endpoints. Keep the crypto in `auth/security.py` and nothing else touches the hash format directly.\nuser: Write the password hashing function.\nassistant: ```python\ndef hash_password(password):\n    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()\n```\nuser: Now token verification.\nassistant: ```python\nACCESS_TOKEN_TTL = 3600\n\ndef verify_token(token):\n    try:\n        return jwt.decode(token, SECRET_KEY, algorithms=['HS256'])\n    except jwt.PyJWTError:\n        return None\n```",
    "truncated": false
   },
   "raised": [],
   "traps": []
  },
  {
   "exchange": 5,
   "turn_id": "t0009",
   "user": "Add the refresh endpoint.",
   "assistant": "POST /auth/refresh takes the refresh token from an httpOnly cookie, rotates it (the old one is revoked in Redis), and returns a new access token. Reuse of a revoked token revokes the whole family.",
   "signal": {
    "turn_count": 9,
    "task_type": "code_generation",
    "matched_pattern": "pattern:code_generation",
    "topic_similarity": 0.076,
    "shift": true,
    "recall_request": false,
    "tokens_used": 219,
    "budget": 700
   },
   "features": {
    "turn_count": 9,
    "token_budget_pressure": 0.3129,
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
     "reason": "token pressure 0.31 < 0.90: full recent history fits, window is lossless"
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
    "latency_ms": 0.0617,
    "override": [],
    "full": "[history_fits] token pressure 0.31 < 0.90: full recent history fits, window is lossless | features: turn=9, pressure=0.31, task=code_generation, prior=sliding_window, since_switch=3",
    "rule": "history_fits",
    "rule_reason": "token pressure 0.31 < 0.90: full recent history fits, window is lossless",
    "dwell": [],
    "escalations": []
   },
   "candidates": {
    "sliding_window": {
     "tokens": 212,
     "latency_ms": 0.53,
     "quality": {
      "kept": 8,
      "relevance": 0.075,
      "freshness": 0.753,
      "importance": 0.294,
      "state": 0.5,
      "composite": 0.405
     }
    },
    "summarization": {
     "tokens": 218,
     "latency_ms": 0.98,
     "quality": {
      "tier_emitted": "L1",
      "loss_score": 0.0,
      "loss_threshold_exceeded": false,
      "symbol_retention_rate": 1.0
     }
    },
    "rag": {
     "tokens": 0,
     "latency_ms": 2.05,
     "quality": {
      "granularity_tag": "turn",
      "retrieved": 0,
      "stale_flags": 0
     }
    }
   },
   "prompt": {
    "tokens": 214,
    "context": "user: We're replacing our homemade auth with something sane. Where do we start?\nassistant: Password hashing first, then token issuing and verification, then the login and refresh endpoints. Keep the crypto in `auth/security.py` and nothing else touches the hash format directly.\nuser: Write the password hashing function.\nassistant: ```python\ndef hash_password(password):\n    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()\n```\nuser: Now token verification.\nassistant: ```python\nACCESS_TOKEN_TTL = 3600\n\ndef verify_token(token):\n    try:\n        return jwt.decode(token, SECRET_KEY, algorithms=['HS256'])\n    except jwt.PyJWTError:\n        return None\n```\nuser: Security review says hashing cost must be configurable and tokens must expire after 15 minutes.\nassistant: ```python\nACCESS_TOKEN_TTL = 900\n\ndef hash_password(password, rounds=12):\n    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds)).decode()\n```\nLong sessions are handled by refresh tokens instead.",
    "truncated": false
   },
   "raised": [],
   "traps": []
  },
  {
   "exchange": 6,
   "turn_id": "t0011",
   "user": "Add login rate limiting.",
   "assistant": "Five failed attempts per account per 15 minutes and 20 per IP, tracked in Redis with sliding windows; the response is the same for unknown users and wrong passwords.",
   "signal": {
    "turn_count": 11,
    "task_type": "code_generation",
    "matched_pattern": "carry_over",
    "topic_similarity": 0.167,
    "shift": false,
    "recall_request": false,
    "tokens_used": 273,
    "budget": 700
   },
   "features": {
    "turn_count": 11,
    "token_budget_pressure": 0.39,
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
    "latency_ms": 0.0636,
    "override": [],
    "full": "[history_fits] token pressure 0.39 < 0.90: full recent history fits, window is lossless | features: turn=11, pressure=0.39, task=code_generation, prior=sliding_window, since_switch=4",
    "rule": "history_fits",
    "rule_reason": "token pressure 0.39 < 0.90: full recent history fits, window is lossless",
    "dwell": [],
    "escalations": []
   },
   "candidates": {
    "sliding_window": {
     "tokens": 266,
     "latency_ms": 0.49,
     "quality": {
      "kept": 10,
      "relevance": 0.229,
      "freshness": 0.698,
      "importance": 0.24,
      "state": 0.6,
      "composite": 0.442
     }
    },
    "summarization": {
     "tokens": 297,
     "latency_ms": 1.21,
     "quality": {
      "tier_emitted": "L1",
      "loss_score": 0.0,
      "loss_threshold_exceeded": false,
      "symbol_retention_rate": 1.0
     }
    },
    "rag": {
     "tokens": 291,
     "latency_ms": 2.29,
     "quality": {
      "granularity_tag": "turn",
      "retrieved": 7,
      "stale_flags": 1
     }
    }
   },
   "prompt": {
    "tokens": 268,
    "context": "user: We're replacing our homemade auth with something sane. Where do we start?\nassistant: Password hashing first, then token issuing and verification, then the login and refresh endpoints. Keep the crypto in `auth/security.py` and nothing else touches the hash format directly.\nuser: Write the password hashing function.\nassistant: ```python\ndef hash_password(password):\n    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()\n```\nuser: Now token verification.\nassistant: ```python\nACCESS_TOKEN_TTL = 3600\n\ndef verify_token(token):\n    try:\n        return jwt.decode(token, SECRET_KEY, algorithms=['HS256'])\n    except jwt.PyJWTError:\n        return None\n```\nuser: Security review says hashing cost must be configurable and tokens must expire after 15 minutes.\nassistant: ```python\nACCESS_TOKEN_TTL = 900\n\ndef hash_password(password, rounds=12):\n    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds)).decode()\n```\nLong sessions are handled by refresh tokens instead.\nuser: Add the refresh endpoint.\nassistant: POST /auth/refresh takes the refresh token from an httpOnly cookie, rotates it (the old one is revoked in Redis), and returns a new access token. Reuse of a revoked token revokes the whole family.",
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
   "exchange": 7,
   "turn_id": "t0013",
   "user": "Write an audit log for auth events.",
   "assistant": "Every login, failed login, refresh, logout and password change writes a structured event with user id, IP, user agent and outcome to the `audit_events` table, retained for a year.",
   "signal": {
    "turn_count": 13,
    "task_type": "code_generation",
    "matched_pattern": "carry_over",
    "topic_similarity": 0.213,
    "shift": false,
    "recall_request": false,
    "tokens_used": 319,
    "budget": 700
   },
   "features": {
    "turn_count": 13,
    "token_budget_pressure": 0.4557,
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
    "strategy": "hybrid",
    "latency_ms": 0.0717,
    "override": [],
    "full": "[history_fits] token pressure 0.46 < 0.90: full recent history fits, window is lossless | escalation from t0011: 1 stale chunk(s) flagged -> hybrid so the superseding facts are retrievable next to the recent window | features: turn=13, pressure=0.46, task=code_generation, prior=sliding_window, since_switch=5",
    "rule": "history_fits",
    "rule_reason": "token pressure 0.46 < 0.90: full recent history fits, window is lossless",
    "dwell": [],
    "escalations": [
     "escalation from t0011: 1 stale chunk(s) flagged -> hybrid so the superseding facts are retrievable next to the recent window"
    ]
   },
   "candidates": {
    "sliding_window": {
     "tokens": 309,
     "latency_ms": 0.47,
     "quality": {
      "kept": 12,
      "relevance": 0.259,
      "freshness": 0.649,
      "importance": 0.221,
      "state": 0.667,
      "composite": 0.449
     }
    },
    "summarization": {
     "tokens": 340,
     "latency_ms": 1.35,
     "quality": {
      "tier_emitted": "L1",
      "loss_score": 0.0,
      "loss_threshold_exceeded": false,
      "symbol_retention_rate": 1.0
     }
    },
    "rag": {
     "tokens": 394,
     "latency_ms": 2.42,
     "quality": {
      "granularity_tag": "turn",
      "retrieved": 9,
      "stale_flags": 1
     }
    }
   },
   "prompt": {
    "tokens": 403,
    "context": "[Retrieved memory]\n[turns: t0001]\nuser: We're replacing our homemade auth with something sane. Where do we start?\n\n---\n\n[turns: t0005]\nuser: Now token verification.\n[!] stale: superseded by turn:t0010 (nli, confidence 0.99) - prefer the newer chunk\n\n---\n\n[turns: t0002 t0003]\nassistant: Password hashing first, then token issuing and verification, then the login and refresh endpoints. Keep the crypto in `auth/security.py` and nothing else touches the hash format directly.\nuser: Write the password hashing function.\n\n---\n\n[turns: t0007]\nuser: Security review says hashing cost must be configurable and tokens must expire after 15 minutes.\n\n---\n\n[turns: t0008]\nassistant: ```python\nACCESS_TOKEN_TTL = 900\n\ndef hash_password(password, rounds=12):\n    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds)).decode()\n```\nLong sessions are handled by refresh tokens instead.\n\n---\n\n[turns: t0006]\nassistant: ```python\nACCESS_TOKEN_TTL = 3600\n\ndef verify_token(token):\n    try:\n        return jwt.decode(token, SECRET_KEY, algorithms=['HS256'])\n    except jwt.PyJWTError:\n        return None\n```\n\n[Recent turns]\nassistant: ```python\ndef hash_password(password):\n    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()\n```\nuser: Add the refresh endpoint.\nassistant: POST /auth/refresh takes the refresh token from an httpOnly cookie, rotates it (the old one is revoked in Redis), and returns a new access token. Reuse of a revoked token revokes the whole family.\nuser: Add login rate limiting.\nassistant: Five failed attempts per account per 15 minutes and 20 per IP, tracked in Redis with sliding windows; the response is the same for unknown users and wrong passwords.",
    "truncated": false
   },
   "raised": [],
   "traps": []
  },
  {
   "exchange": 8,
   "turn_id": "t0015",
   "user": "Support TOTP two-factor.",
   "assistant": "pyotp with a 30-second step and one step of drift allowed; secrets encrypted at rest with a KMS key; ten single-use recovery codes stored as bcrypt hashes.",
   "signal": {
    "turn_count": 15,
    "task_type": "code_generation",
    "matched_pattern": "carry_over",
    "topic_similarity": 0.178,
    "shift": false,
    "recall_request": false,
    "tokens_used": 368,
    "budget": 700
   },
   "features": {
    "turn_count": 15,
    "token_budget_pressure": 0.5257,
    "task_type": "code_generation",
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
    "strategy": "hybrid",
    "latency_ms": 0.0595,
    "override": [],
    "full": "[history_fits] token pressure 0.53 < 0.90: full recent history fits, window is lossless | dwell: held hybrid (0 < 3 turns since last switch) | features: turn=15, pressure=0.53, task=code_generation, prior=hybrid, since_switch=0",
    "rule": "history_fits",
    "rule_reason": "token pressure 0.53 < 0.90: full recent history fits, window is lossless",
    "dwell": [
     "dwell: held hybrid (0 < 3 turns since last switch)"
    ],
    "escalations": []
   },
   "candidates": {
    "sliding_window": {
     "tokens": 360,
     "latency_ms": 0.43,
     "quality": {
      "kept": 14,
      "relevance": 0.078,
      "freshness": 0.605,
      "importance": 0.204,
      "state": 0.714,
      "composite": 0.4
     }
    },
    "summarization": {
     "tokens": 391,
     "latency_ms": 1.49,
     "quality": {
      "tier_emitted": "L1",
      "loss_score": 0.0,
      "loss_threshold_exceeded": false,
      "symbol_retention_rate": 1.0
     }
    },
    "rag": {
     "tokens": 160,
     "latency_ms": 2.54,
     "quality": {
      "granularity_tag": "turn",
      "retrieved": 3,
      "stale_flags": 1
     }
    }
   },
   "prompt": {
    "tokens": 423,
    "context": "[Retrieved memory]\n[turns: t0005]\nuser: Now token verification.\n[!] stale: superseded by turn:t0010 (nli, confidence 0.99) - prefer the newer chunk\n\n---\n\n[turns: t0010 | supersedes turn:t0005]\nassistant: POST /auth/refresh takes the refresh token from an httpOnly cookie, rotates it (the old one is revoked in Redis), and returns a new access token. Reuse of a revoked token revokes the whole family.\n\n[Recent turns]\nuser: We're replacing our homemade auth with something sane. Where do we start?\nassistant: Password hashing first, then token issuing and verification, then the login and refresh endpoints. Keep the crypto in `auth/security.py` and nothing else touches the hash format directly.\nuser: Write the password hashing function.\nassistant: ```python\ndef hash_password(password):\n    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()\n```\nassistant: ```python\nACCESS_TOKEN_TTL = 3600\n\ndef verify_token(token):\n    try:\n        return jwt.decode(token, SECRET_KEY, algorithms=['HS256'])\n    except jwt.PyJWTError:\n        return None\n```\nuser: Security review says hashing cost must be configurable and tokens must expire after 15 minutes.\nassistant: ```python\nACCESS_TOKEN_TTL = 900\n\ndef hash_password(password, rounds=12):\n    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds)).decode()\n```\nLong sessions are handled by refresh tokens instead.\nuser: Add the refresh endpoint.\nuser: Add login rate limiting.\nassistant: Five failed attempts per account per 15 minutes and 20 per IP, tracked in Redis with sliding windows; the response is the same for unknown users and wrong passwords.\nuser: Write an audit log for auth events.\nassistant: Every login, failed login, refresh, logout and password change writes a structured event with user id, IP, user agent and outcome to the `audit_events` table, retained for a year.",
    "truncated": false
   },
   "raised": [],
   "traps": []
  },
  {
   "exchange": 9,
   "turn_id": "t0017",
   "user": "Write the OpenAPI security scheme.",
   "assistant": "Declared a bearer JWT scheme and a cookie scheme for refresh, applied the bearer scheme globally and marked login and refresh as public.",
   "signal": {
    "turn_count": 17,
    "task_type": "code_generation",
    "matched_pattern": "carry_over",
    "topic_similarity": 0.444,
    "shift": false,
    "recall_request": false,
    "tokens_used": 414,
    "budget": 700
   },
   "features": {
    "turn_count": 17,
    "token_budget_pressure": 0.5914,
    "task_type": "code_generation",
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
    "strategy": "hybrid",
    "latency_ms": 0.0725,
    "override": [],
    "full": "[history_fits] token pressure 0.59 < 0.90: full recent history fits, window is lossless | dwell: held hybrid (1 < 3 turns since last switch) | features: turn=17, pressure=0.59, task=code_generation, prior=hybrid, since_switch=1",
    "rule": "history_fits",
    "rule_reason": "token pressure 0.59 < 0.90: full recent history fits, window is lossless",
    "dwell": [
     "dwell: held hybrid (1 < 3 turns since last switch)"
    ],
    "escalations": []
   },
   "candidates": {
    "sliding_window": {
     "tokens": 405,
     "latency_ms": 0.42,
     "quality": {
      "kept": 16,
      "relevance": 0.262,
      "freshness": 0.565,
      "importance": 0.184,
      "state": 0.75,
      "composite": 0.44
     }
    },
    "summarization": {
     "tokens": 433,
     "latency_ms": 1.9,
     "quality": {
      "tier_emitted": "L1",
      "loss_score": 0.0,
      "loss_threshold_exceeded": false,
      "symbol_retention_rate": 1.0
     }
    },
    "rag": {
     "tokens": 515,
     "latency_ms": 2.73,
     "quality": {
      "granularity_tag": "turn",
      "retrieved": 11,
      "stale_flags": 1
     }
    }
   },
   "prompt": {
    "tokens": 519,
    "context": "[Retrieved memory]\n[turns: t0002 t0003]\nassistant: Password hashing first, then token issuing and verification, then the login and refresh endpoints. Keep the crypto in `auth/security.py` and nothing else touches the hash format directly.\nuser: Write the password hashing function.\n\n---\n\n[turns: t0011 t0012]\nuser: Add login rate limiting.\nassistant: Five failed attempts per account per 15 minutes and 20 per IP, tracked in Redis with sliding windows; the response is the same for unknown users and wrong passwords.\n\n---\n\n[turns: t0001]\nuser: We're replacing our homemade auth with something sane. Where do we start?\n\n---\n\n[turns: t0005]\nuser: Now token verification.\n[!] stale: superseded by turn:t0010 (nli, confidence 0.99) - prefer the newer chunk\n\n---\n\n[turns: t0010 | supersedes turn:t0005]\nassistant: POST /auth/refresh takes the refresh token from an httpOnly cookie, rotates it (the old one is revoked in Redis), and returns a new access token. Reuse of a revoked token revokes the whole family.\n\n---\n\n[turns: t0007]\nuser: Security review says hashing cost must be configurable and tokens must expire after 15 minutes.\n\n---\n\n[turns: t0006]\nassistant: ```python\nACCESS_TOKEN_TTL = 3600\n\ndef verify_token(token):\n    try:\n        return jwt.decode(token, SECRET_KEY, algorithms=['HS256'])\n    except jwt.PyJWTError:\n        return None\n```\n\n[Recent turns]\nassistant: ```python\ndef hash_password(password):\n    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()\n```\nassistant: ```python\nACCESS_TOKEN_TTL = 900\n\ndef hash_password(password, rounds=12):\n    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds)).decode()\n```\nLong sessions are handled by refresh tokens instead.\nuser: Add the refresh endpoint.\nuser: Write an audit log for auth events.\nassistant: Every login, failed login, refresh, logout and password change writes a structured event with user id, IP, user agent and outcome to the `audit_events` table, retained for a year.\nuser: Support TOTP two-factor.\nassistant: pyotp with a 30-second step and one step of drift allowed; secrets encrypted at rest with a KMS key; ten single-use recovery codes stored as bcrypt hashes.",
    "truncated": false
   },
   "raised": [],
   "traps": []
  },
  {
   "exchange": 10,
   "turn_id": "t0019",
   "user": "Write the admin script that resets a user's password with a stronger cost of 14.",
   "assistant": "(scripted reply omitted - the check is on the context the model would receive)",
   "signal": {
    "turn_count": 19,
    "task_type": "code_generation",
    "matched_pattern": "pattern:code_generation",
    "topic_similarity": 0.378,
    "shift": false,
    "recall_request": false,
    "tokens_used": 462,
    "budget": 700
   },
   "features": {
    "turn_count": 19,
    "token_budget_pressure": 0.66,
    "task_type": "code_generation",
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
    "strategy": "hybrid",
    "latency_ms": 0.0722,
    "override": [],
    "full": "[history_fits] token pressure 0.66 < 0.90: full recent history fits, window is lossless | dwell: held hybrid (2 < 3 turns since last switch) | features: turn=19, pressure=0.66, task=code_generation, prior=hybrid, since_switch=2",
    "rule": "history_fits",
    "rule_reason": "token pressure 0.66 < 0.90: full recent history fits, window is lossless",
    "dwell": [
     "dwell: held hybrid (2 < 3 turns since last switch)"
    ],
    "escalations": []
   },
   "candidates": {
    "sliding_window": {
     "tokens": 442,
     "latency_ms": 0.43,
     "quality": {
      "kept": 18,
      "relevance": 0.252,
      "freshness": 0.529,
      "importance": 0.164,
      "state": 0.778,
      "composite": 0.431
     }
    },
    "summarization": {
     "tokens": 470,
     "latency_ms": 2.17,
     "quality": {
      "tier_emitted": "L1",
      "loss_score": 0.0,
      "loss_threshold_exceeded": false,
      "symbol_retention_rate": 1.0
     }
    },
    "rag": {
     "tokens": 557,
     "latency_ms": 2.83,
     "quality": {
      "granularity_tag": "turn",
      "retrieved": 12,
      "stale_flags": 2
     }
    }
   },
   "prompt": {
    "tokens": 542,
    "context": "[Retrieved memory]\n[turns: t0002 t0003]\nassistant: Password hashing first, then token issuing and verification, then the login and refresh endpoints. Keep the crypto in `auth/security.py` and nothing else touches the hash format directly.\nuser: Write the password hashing function.\n\n---\n\n[turns: t0011 t0012]\nuser: Add login rate limiting.\nassistant: Five failed attempts per account per 15 minutes and 20 per IP, tracked in Redis with sliding windows; the response is the same for unknown users and wrong passwords.\n\n---\n\n[turns: t0008]\nassistant: ```python\nACCESS_TOKEN_TTL = 900\n\ndef hash_password(password, rounds=12):\n    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds)).decode()\n```\nLong sessions are handled by refresh tokens instead.\n\n---\n\n[turns: t0013 t0014]\nuser: Write an audit log for auth events.\nassistant: Every login, failed login, refresh, logout and password change writes a structured event with user id, IP, user agent and outcome to the `audit_events` table, retained for a year.\n\n---\n\n[turns: t0001]\nuser: We're replacing our homemade auth with something sane. Where do we start?\n\n---\n\n[turns: t0004]\nassistant: ```python\ndef hash_password(password):\n    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()\n```\n[!] stale: superseded by turn:t0008 (signature_diff, confidence 1.00) - prefer the newer chunk\n\n[Recent turns]\nuser: Now token verification.\nassistant: ```python\nACCESS_TOKEN_TTL = 3600\n\ndef verify_token(token):\n    try:\n        return jwt.decode(token, SECRET_KEY, algorithms=['HS256'])\n    except jwt.PyJWTError:\n        return None\n```\nuser: Security review says hashing cost must be configurable and tokens must expire after 15 minutes.\nuser: Add the refresh endpoint.\nassistant: POST /auth/refresh takes the refresh token from an httpOnly cookie, rotates it (the old one is revoked in Redis), and returns a new access token. Reuse of a revoked token revokes the whole family.\nuser: Support TOTP two-factor.\nassistant: pyotp with a 30-second step and one step of drift allowed; secrets encrypted at rest with a KMS key; ten single-use recovery codes stored as bcrypt hashes.\nuser: Write the OpenAPI security scheme.\nassistant: Declared a bearer JWT scheme and a cookie scheme for refresh, applied the bearer scheme globally and marked login and refresh as public.",
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
     "name": "added rounds parameter",
     "description": "hash_password gained a rounds parameter at exchange 4",
     "planted_at": 4,
     "kind": "signature",
     "adaptive": {
      "caught": true,
      "detail": "found `def hash_password(password, rounds=12)`",
      "strategy": "hybrid"
     },
     "fixed_6_exchange_window": {
      "caught": true,
      "detail": "found `def hash_password(password, rounds=12)`"
     },
     "sliding_window": {
      "caught": false,
      "detail": "unmarked stale `def hash_password(password):` present"
     },
     "summarization": {
      "caught": true,
      "detail": "found `def hash_password(password, rounds=12)`"
     },
     "rag": {
      "caught": true,
      "detail": "found `def hash_password(password, rounds=12)`"
     },
     "hybrid": {
      "caught": true,
      "detail": "found `def hash_password(password, rounds=12)`"
     }
    }
   ]
  },
  {
   "exchange": 11,
   "turn_id": "t0021",
   "user": "Write a dependency that checks a bearer token and returns the claims for protected routes.",
   "assistant": "(scripted reply omitted - the check is on the context the model would receive)",
   "signal": {
    "turn_count": 21,
    "task_type": "code_generation",
    "matched_pattern": "carry_over",
    "topic_similarity": 0.342,
    "shift": false,
    "recall_request": false,
    "tokens_used": 499,
    "budget": 700
   },
   "features": {
    "turn_count": 21,
    "token_budget_pressure": 0.7129,
    "task_type": "code_generation",
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
     "reason": "token pressure 0.71 < 0.90: full recent history fits, window is lossless"
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
    "strategy": "hybrid",
    "latency_ms": 0.0806,
    "override": [],
    "full": "[history_fits] token pressure 0.71 < 0.90: full recent history fits, window is lossless | escalation from t0019: 1 stale chunk(s) flagged -> hybrid so the superseding facts are retrievable next to the recent window | features: turn=21, pressure=0.71, task=code_generation, prior=hybrid, since_switch=3",
    "rule": "history_fits",
    "rule_reason": "token pressure 0.71 < 0.90: full recent history fits, window is lossless",
    "dwell": [],
    "escalations": [
     "escalation from t0019: 1 stale chunk(s) flagged -> hybrid so the superseding facts are retrievable next to the recent window"
    ]
   },
   "candidates": {
    "sliding_window": {
     "tokens": 481,
     "latency_ms": 0.47,
     "quality": {
      "kept": 20,
      "relevance": 0.198,
      "freshness": 0.496,
      "importance": 0.152,
      "state": 0.8,
      "composite": 0.412
     }
    },
    "summarization": {
     "tokens": 509,
     "latency_ms": 2.41,
     "quality": {
      "tier_emitted": "L1",
      "loss_score": 0.0,
      "loss_threshold_exceeded": false,
      "symbol_retention_rate": 1.0
     }
    },
    "rag": {
     "tokens": 450,
     "latency_ms": 3.06,
     "quality": {
      "granularity_tag": "turn",
      "retrieved": 10,
      "stale_flags": 1
     }
    }
   },
   "prompt": {
    "tokens": 592,
    "context": "[Retrieved memory]\n[turns: t0005]\nuser: Now token verification.\n[!] stale: superseded by turn:t0010 (nli, confidence 0.99) - prefer the newer chunk\n\n---\n\n[turns: t0010 | supersedes turn:t0005]\nassistant: POST /auth/refresh takes the refresh token from an httpOnly cookie, rotates it (the old one is revoked in Redis), and returns a new access token. Reuse of a revoked token revokes the whole family.\n\n---\n\n[turns: t0006]\nassistant: ```python\nACCESS_TOKEN_TTL = 3600\n\ndef verify_token(token):\n    try:\n        return jwt.decode(token, SECRET_KEY, algorithms=['HS256'])\n    except jwt.PyJWTError:\n        return None\n```\n\n---\n\n[turns: t0007]\nuser: Security review says hashing cost must be configurable and tokens must expire after 15 minutes.\n\n---\n\n[turns: t0002 t0003]\nassistant: Password hashing first, then token issuing and verification, then the login and refresh endpoints. Keep the crypto in `auth/security.py` and nothing else touches the hash format directly.\nuser: Write the password hashing function.\n\n---\n\n[turns: t0001]\nuser: We're replacing our homemade auth with something sane. Where do we start?\n\n---\n\n[turns: t0016]\nassistant: pyotp with a 30-second step and one step of drift allowed; secrets encrypted at rest with a KMS key; ten single-use recovery codes stored as bcrypt hashes.\n\n[Recent turns]\nassistant: ```python\ndef hash_password(password):\n    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()\n```\nassistant: ```python\nACCESS_TOKEN_TTL = 900\n\ndef hash_password(password, rounds=12):\n    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds)).decode()\n```\nLong sessions are handled by refresh tokens instead.\nuser: Add the refresh endpoint.\nuser: Add login rate limiting.\nassistant: Five failed attempts per account per 15 minutes and 20 per IP, tracked in Redis with sliding windows; the response is the same for unknown users and wrong passwords.\nuser: Write an audit log for auth events.\nassistant: Every login, failed login, refresh, logout and password change writes a structured event with user id, IP, user agent and outcome to the `audit_events` table, retained for a year.\nuser: Support TOTP two-factor.\nuser: Write the OpenAPI security scheme.\nassistant: Declared a bearer JWT scheme and a cookie scheme for refresh, applied the bearer scheme globally and marked login and refresh as public.\nuser: Write the admin script that resets a user's password with a stronger cost of 14.\nassistant: (scripted reply omitted - the check is on the context the model would receive)",
    "truncated": false
   },
   "raised": [],
   "traps": [
    {
     "name": "duplicate token verifier",
     "description": "verify_token exists since exchange 3",
     "planted_at": 3,
     "kind": "duplicate",
     "adaptive": {
      "caught": true,
      "detail": "found `def verify_token(`",
      "strategy": "hybrid"
     },
     "fixed_6_exchange_window": {
      "caught": false,
      "detail": "missing `def verify_token(`"
     },
     "sliding_window": {
      "caught": true,
      "detail": "found `def verify_token(`"
     },
     "summarization": {
      "caught": true,
      "detail": "found `def verify_token(`"
     },
     "rag": {
      "caught": true,
      "detail": "found `def verify_token(`"
     },
     "hybrid": {
      "caught": true,
      "detail": "found `def verify_token(`"
     }
    }
   ]
  },
  {
   "exchange": 12,
   "turn_id": "t0023",
   "user": "How long are access tokens valid for? I'm writing the client's refresh timer.",
   "assistant": "(scripted reply omitted - the check is on the context the model would receive)",
   "signal": {
    "turn_count": 23,
    "task_type": "qa",
    "matched_pattern": "pattern:qa",
    "topic_similarity": 0.291,
    "shift": false,
    "recall_request": false,
    "tokens_used": 537,
    "budget": 700
   },
   "features": {
    "turn_count": 23,
    "token_budget_pressure": 0.7671,
    "task_type": "qa",
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
     "reason": "token pressure 0.77 < 0.90: full recent history fits, window is lossless"
    },
    {
     "fn": "qa",
     "matched": true,
     "fired": false,
     "rule": "recall_question",
     "strategy": "rag",
     "hard": true,
     "reason": "task_type=qa (recall of earlier facts) with history over budget -> RAG retrieves the specific turns"
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
    "full": "[history_fits] token pressure 0.77 < 0.90: full recent history fits, window is lossless | features: turn=23, pressure=0.77, task=qa, prior=hybrid, since_switch=4",
    "rule": "history_fits",
    "rule_reason": "token pressure 0.77 < 0.90: full recent history fits, window is lossless",
    "dwell": [],
    "escalations": []
   },
   "candidates": {
    "sliding_window": {
     "tokens": 510,
     "latency_ms": 0.47,
     "quality": {
      "kept": 21,
      "relevance": 0.251,
      "freshness": 0.479,
      "importance": 0.145,
      "state": 0.833,
      "composite": 0.427
     }
    },
    "summarization": {
     "tokens": 558,
     "latency_ms": 2.68,
     "quality": {
      "tier_emitted": "L1",
      "loss_score": 0.0,
      "loss_threshold_exceeded": false,
      "symbol_retention_rate": 1.0
     }
    },
    "rag": {
     "tokens": 611,
     "latency_ms": 1154.38,
     "quality": {
      "granularity_tag": "turn",
      "retrieved": 14,
      "stale_flags": 1
     }
    }
   },
   "prompt": {
    "tokens": 512,
    "context": "user: We're replacing our homemade auth with something sane. Where do we start?\nassistant: Password hashing first, then token issuing and verification, then the login and refresh endpoints. Keep the crypto in `auth/security.py` and nothing else touches the hash format directly.\nassistant: ```python\ndef hash_password(password):\n    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()\n```\nuser: Now token verification.\nassistant: ```python\nACCESS_TOKEN_TTL = 3600\n\ndef verify_token(token):\n    try:\n        return jwt.decode(token, SECRET_KEY, algorithms=['HS256'])\n    except jwt.PyJWTError:\n        return None\n```\nuser: Security review says hashing cost must be configurable and tokens must expire after 15 minutes.\nassistant: ```python\nACCESS_TOKEN_TTL = 900\n\ndef hash_password(password, rounds=12):\n    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds)).decode()\n```\nLong sessions are handled by refresh tokens instead.\nuser: Add the refresh endpoint.\nassistant: POST /auth/refresh takes the refresh token from an httpOnly cookie, rotates it (the old one is revoked in Redis), and returns a new access token. Reuse of a revoked token revokes the whole family.\nuser: Add login rate limiting.\nassistant: Five failed attempts per account per 15 minutes and 20 per IP, tracked in Redis with sliding windows; the response is the same for unknown users and wrong passwords.\nuser: Write an audit log for auth events.\nassistant: Every login, failed login, refresh, logout and password change writes a structured event with user id, IP, user agent and outcome to the `audit_events` table, retained for a year.\nuser: Support TOTP two-factor.\nassistant: pyotp with a 30-second step and one step of drift allowed; secrets encrypted at rest with a KMS key; ten single-use recovery codes stored as bcrypt hashes.\nuser: Write the OpenAPI security scheme.\nassistant: Declared a bearer JWT scheme and a cookie scheme for refresh, applied the bearer scheme globally and marked login and refresh as public.\nuser: Write the admin script that resets a user's password with a stronger cost of 14.\nassistant: (scripted reply omitted - the check is on the context the model would receive)\nuser: Write a dependency that checks a bearer token and returns the claims for protected routes.\nassistant: (scripted reply omitted - the check is on the context the model would receive)",
    "truncated": false
   },
   "raised": [],
   "traps": [
    {
     "name": "changed token lifetime",
     "description": "ACCESS_TOKEN_TTL changed 3600 -> 900 at exchange 4",
     "planted_at": 4,
     "kind": "config",
     "adaptive": {
      "caught": false,
      "detail": "unmarked stale `ACCESS_TOKEN_TTL = 3600` present",
      "strategy": "sliding_window"
     },
     "fixed_6_exchange_window": {
      "caught": false,
      "detail": "missing `ACCESS_TOKEN_TTL = 900`"
     },
     "sliding_window": {
      "caught": false,
      "detail": "unmarked stale `ACCESS_TOKEN_TTL = 3600` present"
     },
     "summarization": {
      "caught": false,
      "detail": "missing `ACCESS_TOKEN_TTL = 900`"
     },
     "rag": {
      "caught": false,
      "detail": "unmarked stale `ACCESS_TOKEN_TTL = 3600` present"
     },
     "hybrid": {
      "caught": false,
      "detail": "unmarked stale `ACCESS_TOKEN_TTL = 3600` present"
     }
    }
   ]
  }
 ]
};
