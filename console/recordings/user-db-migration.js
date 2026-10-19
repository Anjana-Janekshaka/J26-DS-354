window.CEAI_SESSIONS = window.CEAI_SESSIONS || {};
window.CEAI_SESSIONS["user-db-migration"] = {
 "scenario": "user-db-migration",
 "slug": "user-db-migration",
 "language": "sql",
 "held_out": true,
 "system": "frozen",
 "mode": "full",
 "budget": 700,
 "recorded_at": "2026-10-19T11:23:41+00:00",
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
  "adaptive": 1,
  "fixed_6_exchange_window": 0,
  "sliding_window": 1,
  "summarization": 0,
  "rag": 0,
  "hybrid": 1
 },
 "turns": [
  {
   "exchange": 1,
   "turn_id": "t0001",
   "user": "We are cleaning up the users table in Postgres. Show me the current shape first.",
   "assistant": "users(id bigserial primary key, email_address text unique not null, full_name text, created_at timestamptz default now(), last_login timestamptz).",
   "signal": {
    "turn_count": 1,
    "task_type": "chat",
    "matched_pattern": "carry_over",
    "topic_similarity": null,
    "shift": false,
    "recall_request": false,
    "tokens_used": 20,
    "budget": 700
   },
   "features": {
    "turn_count": 1,
    "token_budget_pressure": 0.0286,
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
    "latency_ms": 0.0713,
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
     "latency_ms": 1.07,
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
   "user": "Rename email_address to email, the ORM and API already call it email.",
   "assistant": "Migration `0042_rename_email.sql`:\n```sql\nALTER TABLE users RENAME COLUMN email_address TO email;\n```\nThe unique index follows the column automatically.",
   "signal": {
    "turn_count": 3,
    "task_type": "code_refactor",
    "matched_pattern": "pattern:code_refactor",
    "topic_similarity": null,
    "shift": false,
    "recall_request": false,
    "tokens_used": 75,
    "budget": 700
   },
   "features": {
    "turn_count": 3,
    "token_budget_pressure": 0.1071,
    "task_type": "code_refactor",
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
     "reason": "token pressure 0.11 < 0.90: full recent history fits, window is lossless"
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
    "latency_ms": 0.0772,
    "override": [],
    "full": "[history_fits] token pressure 0.11 < 0.90: full recent history fits, window is lossless | features: turn=3, pressure=0.11, task=code_refactor, prior=sliding_window, since_switch=0",
    "rule": "history_fits",
    "rule_reason": "token pressure 0.11 < 0.90: full recent history fits, window is lossless",
    "dwell": [],
    "escalations": []
   },
   "candidates": {
    "sliding_window": {
     "tokens": 58,
     "latency_ms": 0.71,
     "quality": {
      "kept": 2,
      "relevance": 0.173,
      "freshness": 0.959,
      "importance": 0.1,
      "state": 1.0,
      "composite": 0.558
     }
    },
    "summarization": {
     "tokens": 62,
     "latency_ms": 0.95,
     "quality": {
      "tier_emitted": "L1",
      "loss_score": 0.0,
      "loss_threshold_exceeded": false,
      "symbol_retention_rate": null
     }
    },
    "rag": {
     "tokens": 46,
     "latency_ms": 1.22,
     "quality": {
      "granularity_tag": "turn",
      "retrieved": 1,
      "stale_flags": 0
     }
    }
   },
   "prompt": {
    "tokens": 58,
    "context": "user: We are cleaning up the users table in Postgres. Show me the current shape first.\nassistant: users(id bigserial primary key, email_address text unique not null, full_name text, created_at timestamptz default now(), last_login timestamptz).",
    "truncated": false
   },
   "raised": [],
   "traps": []
  },
  {
   "exchange": 3,
   "turn_id": "t0005",
   "user": "Add a partial index for active users.",
   "assistant": "```sql\nCREATE INDEX CONCURRENTLY users_active_idx ON users (last_login) WHERE last_login > now() - interval '90 days';\n```\nNote that `now()` in a partial index predicate is not allowed; use a boolean `is_active` column maintained by a nightly job instead.",
   "signal": {
    "turn_count": 5,
    "task_type": "code_refactor",
    "matched_pattern": "carry_over",
    "topic_similarity": null,
    "shift": false,
    "recall_request": false,
    "tokens_used": 120,
    "budget": 700
   },
   "features": {
    "turn_count": 5,
    "token_budget_pressure": 0.1714,
    "task_type": "code_refactor",
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
    "latency_ms": 0.0638,
    "override": [],
    "full": "[history_fits] token pressure 0.17 < 0.90: full recent history fits, window is lossless | features: turn=5, pressure=0.17, task=code_refactor, prior=sliding_window, since_switch=1",
    "rule": "history_fits",
    "rule_reason": "token pressure 0.17 < 0.90: full recent history fits, window is lossless",
    "dwell": [],
    "escalations": []
   },
   "candidates": {
    "sliding_window": {
     "tokens": 110,
     "latency_ms": 0.65,
     "quality": {
      "kept": 4,
      "relevance": 0.228,
      "freshness": 0.882,
      "importance": 0.125,
      "state": 1.0,
      "composite": 0.559
     }
    },
    "summarization": {
     "tokens": 114,
     "latency_ms": 0.86,
     "quality": {
      "tier_emitted": "L1",
      "loss_score": 0.0,
      "loss_threshold_exceeded": false,
      "symbol_retention_rate": null
     }
    },
    "rag": {
     "tokens": 113,
     "latency_ms": 1.63,
     "quality": {
      "granularity_tag": "segment",
      "retrieved": 2,
      "stale_flags": 0
     }
    }
   },
   "prompt": {
    "tokens": 110,
    "context": "user: We are cleaning up the users table in Postgres. Show me the current shape first.\nassistant: users(id bigserial primary key, email_address text unique not null, full_name text, created_at timestamptz default now(), last_login timestamptz).\nuser: Rename email_address to email, the ORM and API already call it email.\nassistant: Migration `0042_rename_email.sql`:\n```sql\nALTER TABLE users RENAME COLUMN email_address TO email;\n```\nThe unique index follows the column automatically.",
    "truncated": false
   },
   "raised": [],
   "traps": []
  },
  {
   "exchange": 4,
   "turn_id": "t0007",
   "user": "OK, add is_active and the job.",
   "assistant": "Added `is_active boolean not null default true` and a pg_cron job that sets it from last_login every night at 03:00. The partial index is now `WHERE is_active`.",
   "signal": {
    "turn_count": 7,
    "task_type": "code_refactor",
    "matched_pattern": "carry_over",
    "topic_similarity": 0.394,
    "shift": false,
    "recall_request": false,
    "tokens_used": 193,
    "budget": 700
   },
   "features": {
    "turn_count": 7,
    "token_budget_pressure": 0.2757,
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
     "reason": "token pressure 0.28 < 0.90: full recent history fits, window is lossless"
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
    "latency_ms": 0.0802,
    "override": [],
    "full": "[history_fits] token pressure 0.28 < 0.90: full recent history fits, window is lossless | features: turn=7, pressure=0.28, task=code_refactor, prior=sliding_window, since_switch=2",
    "rule": "history_fits",
    "rule_reason": "token pressure 0.28 < 0.90: full recent history fits, window is lossless",
    "dwell": [],
    "escalations": []
   },
   "candidates": {
    "sliding_window": {
     "tokens": 182,
     "latency_ms": 0.6,
     "quality": {
      "kept": 6,
      "relevance": 0.231,
      "freshness": 0.814,
      "importance": 0.167,
      "state": 1.0,
      "composite": 0.553
     }
    },
    "summarization": {
     "tokens": 186,
     "latency_ms": 0.86,
     "quality": {
      "tier_emitted": "L1",
      "loss_score": 0.0,
      "loss_threshold_exceeded": false,
      "symbol_retention_rate": null
     }
    },
    "rag": {
     "tokens": 223,
     "latency_ms": 2.05,
     "quality": {
      "granularity_tag": "segment",
      "retrieved": 4,
      "stale_flags": 0
     }
    }
   },
   "prompt": {
    "tokens": 182,
    "context": "user: We are cleaning up the users table in Postgres. Show me the current shape first.\nassistant: users(id bigserial primary key, email_address text unique not null, full_name text, created_at timestamptz default now(), last_login timestamptz).\nuser: Rename email_address to email, the ORM and API already call it email.\nassistant: Migration `0042_rename_email.sql`:\n```sql\nALTER TABLE users RENAME COLUMN email_address TO email;\n```\nThe unique index follows the column automatically.\nuser: Add a partial index for active users.\nassistant: ```sql\nCREATE INDEX CONCURRENTLY users_active_idx ON users (last_login) WHERE last_login > now() - interval '90 days';\n```\nNote that `now()` in a partial index predicate is not allowed; use a boolean `is_active` column maintained by a nightly job instead.",
    "truncated": false
   },
   "raised": [],
   "traps": []
  },
  {
   "exchange": 5,
   "turn_id": "t0009",
   "user": "Set up row level security for the support tool.",
   "assistant": "Enabled RLS on users, a `support` role that can select id, email and full_name only through a security-barrier view, and a policy restricting rows to the support agent's region.",
   "signal": {
    "turn_count": 9,
    "task_type": "chat",
    "matched_pattern": "shift_default",
    "topic_similarity": 0.146,
    "shift": true,
    "recall_request": false,
    "tokens_used": 247,
    "budget": 700
   },
   "features": {
    "turn_count": 9,
    "token_budget_pressure": 0.3529,
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
     "reason": "token pressure 0.35 < 0.90: full recent history fits, window is lossless"
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
    "latency_ms": 0.0616,
    "override": [],
    "full": "[history_fits] token pressure 0.35 < 0.90: full recent history fits, window is lossless | features: turn=9, pressure=0.35, task=chat, prior=sliding_window, since_switch=3",
    "rule": "history_fits",
    "rule_reason": "token pressure 0.35 < 0.90: full recent history fits, window is lossless",
    "dwell": [],
    "escalations": []
   },
   "candidates": {
    "sliding_window": {
     "tokens": 235,
     "latency_ms": 0.55,
     "quality": {
      "kept": 8,
      "relevance": 0.089,
      "freshness": 0.753,
      "importance": 0.163,
      "state": 0.5,
      "composite": 0.376
     }
    },
    "summarization": {
     "tokens": 239,
     "latency_ms": 0.82,
     "quality": {
      "tier_emitted": "L1",
      "loss_score": 0.0,
      "loss_threshold_exceeded": false,
      "symbol_retention_rate": null
     }
    },
    "rag": {
     "tokens": 83,
     "latency_ms": 1071.53,
     "quality": {
      "granularity_tag": "segment",
      "retrieved": 1,
      "stale_flags": 0
     }
    }
   },
   "prompt": {
    "tokens": 235,
    "context": "user: We are cleaning up the users table in Postgres. Show me the current shape first.\nassistant: users(id bigserial primary key, email_address text unique not null, full_name text, created_at timestamptz default now(), last_login timestamptz).\nuser: Rename email_address to email, the ORM and API already call it email.\nassistant: Migration `0042_rename_email.sql`:\n```sql\nALTER TABLE users RENAME COLUMN email_address TO email;\n```\nThe unique index follows the column automatically.\nuser: Add a partial index for active users.\nassistant: ```sql\nCREATE INDEX CONCURRENTLY users_active_idx ON users (last_login) WHERE last_login > now() - interval '90 days';\n```\nNote that `now()` in a partial index predicate is not allowed; use a boolean `is_active` column maintained by a nightly job instead.\nuser: OK, add is_active and the job.\nassistant: Added `is_active boolean not null default true` and a pg_cron job that sets it from last_login every night at 03:00. The partial index is now `WHERE is_active`.",
    "truncated": false
   },
   "raised": [],
   "traps": []
  },
  {
   "exchange": 6,
   "turn_id": "t0011",
   "user": "Backups: are we covered?",
   "assistant": "Daily base backups with WAL archiving to object storage, 14-day retention, and a monthly restore test into a scratch instance that runs the app's smoke tests.",
   "signal": {
    "turn_count": 11,
    "task_type": "chat",
    "matched_pattern": "shift_default",
    "topic_similarity": 0.057,
    "shift": true,
    "recall_request": true,
    "tokens_used": 298,
    "budget": 700
   },
   "features": {
    "turn_count": 11,
    "token_budget_pressure": 0.4257,
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
     "reason": "token pressure 0.43 < 0.90: full recent history fits, window is lossless"
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
    "latency_ms": 0.0645,
    "override": [],
    "full": "[history_fits] token pressure 0.43 < 0.90: full recent history fits, window is lossless | features: turn=11, pressure=0.43, task=chat, prior=sliding_window, since_switch=4",
    "rule": "history_fits",
    "rule_reason": "token pressure 0.43 < 0.90: full recent history fits, window is lossless",
    "dwell": [],
    "escalations": []
   },
   "candidates": {
    "sliding_window": {
     "tokens": 269,
     "latency_ms": 0.51,
     "quality": {
      "kept": 9,
      "relevance": 0.043,
      "freshness": 0.725,
      "importance": 0.15,
      "state": 0.306,
      "composite": 0.306
     }
    },
    "summarization": {
     "tokens": 308,
     "latency_ms": 1.06,
     "quality": {
      "tier_emitted": "L1",
      "loss_score": 0.1,
      "loss_threshold_exceeded": false,
      "symbol_retention_rate": null
     }
    },
    "rag": {
     "tokens": 50,
     "latency_ms": 863.15,
     "quality": {
      "granularity_tag": "turn",
      "retrieved": 1,
      "stale_flags": 0
     }
    }
   },
   "prompt": {
    "tokens": 269,
    "context": "assistant: users(id bigserial primary key, email_address text unique not null, full_name text, created_at timestamptz default now(), last_login timestamptz).\nuser: Rename email_address to email, the ORM and API already call it email.\nassistant: Migration `0042_rename_email.sql`:\n```sql\nALTER TABLE users RENAME COLUMN email_address TO email;\n```\nThe unique index follows the column automatically.\nuser: Add a partial index for active users.\nassistant: ```sql\nCREATE INDEX CONCURRENTLY users_active_idx ON users (last_login) WHERE last_login > now() - interval '90 days';\n```\nNote that `now()` in a partial index predicate is not allowed; use a boolean `is_active` column maintained by a nightly job instead.\nuser: OK, add is_active and the job.\nassistant: Added `is_active boolean not null default true` and a pg_cron job that sets it from last_login every night at 03:00. The partial index is now `WHERE is_active`.\nuser: Set up row level security for the support tool.\nassistant: Enabled RLS on users, a `support` role that can select id, email and full_name only through a security-barrier view, and a policy restricting rows to the support agent's region.",
    "truncated": false
   },
   "raised": [],
   "traps": []
  },
  {
   "exchange": 7,
   "turn_id": "t0013",
   "user": "Write a migration to add a soft-delete column.",
   "assistant": "Added `deleted_at timestamptz` and changed the unique constraint to a partial unique index on the address column `WHERE deleted_at IS NULL` so a deleted user's address can sign up again.",
   "signal": {
    "turn_count": 13,
    "task_type": "chat",
    "matched_pattern": "shift_default",
    "topic_similarity": 0.075,
    "shift": true,
    "recall_request": false,
    "tokens_used": 345,
    "budget": 700
   },
   "features": {
    "turn_count": 13,
    "token_budget_pressure": 0.4929,
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
     "reason": "token pressure 0.49 < 0.90: full recent history fits, window is lossless"
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
    "latency_ms": 0.0713,
    "override": [],
    "full": "[history_fits] token pressure 0.49 < 0.90: full recent history fits, window is lossless | features: turn=13, pressure=0.49, task=chat, prior=sliding_window, since_switch=5",
    "rule": "history_fits",
    "rule_reason": "token pressure 0.49 < 0.90: full recent history fits, window is lossless",
    "dwell": [],
    "escalations": []
   },
   "candidates": {
    "sliding_window": {
     "tokens": 296,
     "latency_ms": 0.51,
     "quality": {
      "kept": 10,
      "relevance": 0.159,
      "freshness": 0.695,
      "importance": 0.14,
      "state": 0.225,
      "composite": 0.304
     }
    },
    "summarization": {
     "tokens": 352,
     "latency_ms": 1.24,
     "quality": {
      "tier_emitted": "L1",
      "loss_score": 0.1,
      "loss_threshold_exceeded": false,
      "symbol_retention_rate": null
     }
    },
    "rag": {
     "tokens": 283,
     "latency_ms": 715.02,
     "quality": {
      "granularity_tag": "segment",
      "retrieved": 4,
      "stale_flags": 0
     }
    }
   },
   "prompt": {
    "tokens": 296,
    "context": "assistant: users(id bigserial primary key, email_address text unique not null, full_name text, created_at timestamptz default now(), last_login timestamptz).\nassistant: Migration `0042_rename_email.sql`:\n```sql\nALTER TABLE users RENAME COLUMN email_address TO email;\n```\nThe unique index follows the column automatically.\nuser: Add a partial index for active users.\nassistant: ```sql\nCREATE INDEX CONCURRENTLY users_active_idx ON users (last_login) WHERE last_login > now() - interval '90 days';\n```\nNote that `now()` in a partial index predicate is not allowed; use a boolean `is_active` column maintained by a nightly job instead.\nuser: OK, add is_active and the job.\nassistant: Added `is_active boolean not null default true` and a pg_cron job that sets it from last_login every night at 03:00. The partial index is now `WHERE is_active`.\nuser: Set up row level security for the support tool.\nassistant: Enabled RLS on users, a `support` role that can select id, email and full_name only through a security-barrier view, and a policy restricting rows to the support agent's region.\nuser: Backups: are we covered?\nassistant: Daily base backups with WAL archiving to object storage, 14-day retention, and a monthly restore test into a scratch instance that runs the app's smoke tests.",
    "truncated": false
   },
   "raised": [],
   "traps": []
  },
  {
   "exchange": 8,
   "turn_id": "t0015",
   "user": "Add a view for the analytics team with signups per week.",
   "assistant": "`CREATE VIEW signups_weekly AS SELECT date_trunc('week', created_at) AS week, count(*) FROM users WHERE deleted_at IS NULL GROUP BY 1;` granted to the analytics role.",
   "signal": {
    "turn_count": 15,
    "task_type": "chat",
    "matched_pattern": "shift_default",
    "topic_similarity": 0.042,
    "shift": true,
    "recall_request": false,
    "tokens_used": 404,
    "budget": 700
   },
   "features": {
    "turn_count": 15,
    "token_budget_pressure": 0.5771,
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
     "reason": "token pressure 0.58 < 0.90: full recent history fits, window is lossless"
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
    "latency_ms": 0.0693,
    "override": [],
    "full": "[history_fits] token pressure 0.58 < 0.90: full recent history fits, window is lossless | features: turn=15, pressure=0.58, task=chat, prior=sliding_window, since_switch=6",
    "rule": "history_fits",
    "rule_reason": "token pressure 0.58 < 0.90: full recent history fits, window is lossless",
    "dwell": [],
    "escalations": []
   },
   "candidates": {
    "sliding_window": {
     "tokens": 306,
     "latency_ms": 0.47,
     "quality": {
      "kept": 10,
      "relevance": 0.2,
      "freshness": 0.679,
      "importance": 0.115,
      "state": 0.2,
      "composite": 0.298
     }
    },
    "summarization": {
     "tokens": 408,
     "latency_ms": 1.4,
     "quality": {
      "tier_emitted": "L1",
      "loss_score": 0.1,
      "loss_threshold_exceeded": false,
      "symbol_retention_rate": null
     }
    },
    "rag": {
     "tokens": 420,
     "latency_ms": 605.98,
     "quality": {
      "granularity_tag": "segment",
      "retrieved": 6,
      "stale_flags": 1
     }
    }
   },
   "prompt": {
    "tokens": 306,
    "context": "assistant: users(id bigserial primary key, email_address text unique not null, full_name text, created_at timestamptz default now(), last_login timestamptz).\nuser: Add a partial index for active users.\nassistant: ```sql\nCREATE INDEX CONCURRENTLY users_active_idx ON users (last_login) WHERE last_login > now() - interval '90 days';\n```\nNote that `now()` in a partial index predicate is not allowed; use a boolean `is_active` column maintained by a nightly job instead.\nassistant: Added `is_active boolean not null default true` and a pg_cron job that sets it from last_login every night at 03:00. The partial index is now `WHERE is_active`.\nuser: Set up row level security for the support tool.\nassistant: Enabled RLS on users, a `support` role that can select id, email and full_name only through a security-barrier view, and a policy restricting rows to the support agent's region.\nuser: Backups: are we covered?\nassistant: Daily base backups with WAL archiving to object storage, 14-day retention, and a monthly restore test into a scratch instance that runs the app's smoke tests.\nuser: Write a migration to add a soft-delete column.\nassistant: Added `deleted_at timestamptz` and changed the unique constraint to a partial unique index on the address column `WHERE deleted_at IS NULL` so a deleted user's address can sign up again.",
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
   "exchange": 9,
   "turn_id": "t0017",
   "user": "Write a query that finds a user by their address, case-insensitively, for the login page.",
   "assistant": "(scripted reply omitted - the check is on the context the model would receive)",
   "signal": {
    "turn_count": 17,
    "task_type": "code_generation",
    "matched_pattern": "pattern:code_generation",
    "topic_similarity": 0.23,
    "shift": false,
    "recall_request": false,
    "tokens_used": 472,
    "budget": 700
   },
   "features": {
    "turn_count": 17,
    "token_budget_pressure": 0.6743,
    "task_type": "code_generation",
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
    "strategy": "hybrid",
    "latency_ms": 0.0689,
    "override": [],
    "full": "[history_fits] token pressure 0.67 < 0.90: full recent history fits, window is lossless | escalation from t0015: 1 stale chunk(s) flagged -> hybrid so the superseding facts are retrievable next to the recent window | features: turn=17, pressure=0.67, task=code_generation, prior=sliding_window, since_switch=7",
    "rule": "history_fits",
    "rule_reason": "token pressure 0.67 < 0.90: full recent history fits, window is lossless",
    "dwell": [],
    "escalations": [
     "escalation from t0015: 1 stale chunk(s) flagged -> hybrid so the superseding facts are retrievable next to the recent window"
    ]
   },
   "candidates": {
    "sliding_window": {
     "tokens": 388,
     "latency_ms": 0.45,
     "quality": {
      "kept": 12,
      "relevance": 0.199,
      "freshness": 0.62,
      "importance": 0.142,
      "state": 0.328,
      "composite": 0.322
     }
    },
    "summarization": {
     "tokens": 497,
     "latency_ms": 1.83,
     "quality": {
      "tier_emitted": "L1",
      "loss_score": 0.0625,
      "loss_threshold_exceeded": false,
      "symbol_retention_rate": null
     }
    },
    "rag": {
     "tokens": 452,
     "latency_ms": 485.77,
     "quality": {
      "granularity_tag": "segment",
      "retrieved": 7,
      "stale_flags": 1
     }
    }
   },
   "prompt": {
    "tokens": 514,
    "context": "[Retrieved memory]\n[turns: t0005 t0006]\nuser: Add a partial index for active users.\nassistant: ```sql\nCREATE INDEX CONCURRENTLY users_active_idx ON users (last_login) WHERE last_login > now() - interval '90 days';\n```\nNote that `now()` in a partial index predicate is not allowed; use a boolean `is_active` column maintained by a nightly job instead.\n\n---\n\n[turns: t0001 t0002]\nuser: We are cleaning up the users table in Postgres. Show me the current shape first.\nassistant: users(id bigserial primary key, email_address text unique not null, full_name text, created_at timestamptz default now(), last_login timestamptz).\n[!] stale: superseded by turn:t0014 (nli, confidence 0.99) - prefer the newer chunk\n\n---\n\n[turns: t0007 t0008]\nuser: OK, add is_active and the job.\nassistant: Added `is_active boolean not null default true` and a pg_cron job that sets it from last_login every night at 03:00. The partial index is now `WHERE is_active`.\n\n---\n\n[turns: t0009 t0010]\nuser: Set up row level security for the support tool.\nassistant: Enabled RLS on users, a `support` role that can select id, email and full_name only through a security-barrier view, and a policy restricting rows to the support agent's region.\n\n[Recent turns]\nassistant: Migration `0042_rename_email.sql`:\n```sql\nALTER TABLE users RENAME COLUMN email_address TO email;\n```\nThe unique index follows the column automatically.\nuser: Backups: are we covered?\nassistant: Daily base backups with WAL archiving to object storage, 14-day retention, and a monthly restore test into a scratch instance that runs the app's smoke tests.\nuser: Write a migration to add a soft-delete column.\nassistant: Added `deleted_at timestamptz` and changed the unique constraint to a partial unique index on the address column `WHERE deleted_at IS NULL` so a deleted user's address can sign up again.\nuser: Add a view for the analytics team with signups per week.\nassistant: `CREATE VIEW signups_weekly AS SELECT date_trunc('week', created_at) AS week, count(*) FROM users WHERE deleted_at IS NULL GROUP BY 1;` granted to the analytics role.",
    "truncated": false
   },
   "raised": [],
   "traps": [
    {
     "name": "renamed column",
     "description": "email_address was renamed to email at exchange 2",
     "planted_at": 2,
     "kind": "rename",
     "adaptive": {
      "caught": true,
      "detail": "found `RENAME COLUMN email_address TO email`",
      "strategy": "hybrid"
     },
     "fixed_6_exchange_window": {
      "caught": false,
      "detail": "missing `RENAME COLUMN email_address TO email`"
     },
     "sliding_window": {
      "caught": true,
      "detail": "found `RENAME COLUMN email_address TO email`"
     },
     "summarization": {
      "caught": false,
      "detail": "missing `RENAME COLUMN email_address TO email`"
     },
     "rag": {
      "caught": false,
      "detail": "missing `RENAME COLUMN email_address TO email`"
     },
     "hybrid": {
      "caught": true,
      "detail": "found `RENAME COLUMN email_address TO email`"
     }
    }
   ]
  }
 ]
};
