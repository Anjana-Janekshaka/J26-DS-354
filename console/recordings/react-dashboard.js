window.CEAI_SESSIONS = window.CEAI_SESSIONS || {};
window.CEAI_SESSIONS["react-dashboard"] = {
 "scenario": "react-dashboard",
 "slug": "react-dashboard",
 "language": "typescript",
 "held_out": true,
 "system": "frozen",
 "mode": "full",
 "budget": 700,
 "recorded_at": "2026-10-19T11:21:42+00:00",
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
  "adaptive": 1,
  "fixed_6_exchange_window": 0,
  "sliding_window": 1,
  "summarization": 0,
  "rag": 1,
  "hybrid": 1
 },
 "turns": [
  {
   "exchange": 1,
   "turn_id": "t0001",
   "user": "We're adding a search page to the admin dashboard (React + TypeScript). Any structure advice?",
   "assistant": "Put the page in `src/pages/Search.tsx`, data fetching in a `useSearch` hook with React Query, and keep presentational components in `src/components/` without data logic.",
   "signal": {
    "turn_count": 1,
    "task_type": "chat",
    "matched_pattern": "carry_over",
    "topic_similarity": null,
    "shift": false,
    "recall_request": false,
    "tokens_used": 21,
    "budget": 700
   },
   "features": {
    "turn_count": 1,
    "token_budget_pressure": 0.03,
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
    "latency_ms": 0.0944,
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
     "latency_ms": 1.22,
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
   "user": "Write a debounce hook for the search box.",
   "assistant": "```tsx\nexport function useDebounce<T>(value: T, delayMs = 300): T {\n  const [debounced, setDebounced] = useState(value);\n  useEffect(() => {\n    const id = setTimeout(() => setDebounced(value), delayMs);\n    return () => clearTimeout(id);\n  }, [value, delayMs]);\n  return debounced;\n}\n```",
   "signal": {
    "turn_count": 3,
    "task_type": "chat",
    "matched_pattern": "carry_over",
    "topic_similarity": null,
    "shift": false,
    "recall_request": false,
    "tokens_used": 73,
    "budget": 700
   },
   "features": {
    "turn_count": 3,
    "token_budget_pressure": 0.1043,
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
    "latency_ms": 0.0702,
    "override": [],
    "full": "[history_fits] token pressure 0.10 < 0.90: full recent history fits, window is lossless | features: turn=3, pressure=0.10, task=chat, prior=sliding_window, since_switch=0",
    "rule": "history_fits",
    "rule_reason": "token pressure 0.10 < 0.90: full recent history fits, window is lossless",
    "dwell": [],
    "escalations": []
   },
   "candidates": {
    "sliding_window": {
     "tokens": 62,
     "latency_ms": 0.72,
     "quality": {
      "kept": 2,
      "relevance": 0.352,
      "freshness": 0.959,
      "importance": 0.1,
      "state": 1.0,
      "composite": 0.603
     }
    },
    "summarization": {
     "tokens": 66,
     "latency_ms": 1.06,
     "quality": {
      "tier_emitted": "L1",
      "loss_score": 0.0,
      "loss_threshold_exceeded": false,
      "symbol_retention_rate": null
     }
    },
    "rag": {
     "tokens": 79,
     "latency_ms": 1075.06,
     "quality": {
      "granularity_tag": "turn",
      "retrieved": 2,
      "stale_flags": 0
     }
    }
   },
   "prompt": {
    "tokens": 62,
    "context": "user: We're adding a search page to the admin dashboard (React + TypeScript). Any structure advice?\nassistant: Put the page in `src/pages/Search.tsx`, data fetching in a `useSearch` hook with React Query, and keep presentational components in `src/components/` without data logic.",
    "truncated": false
   },
   "raised": [],
   "traps": []
  },
  {
   "exchange": 3,
   "turn_id": "t0005",
   "user": "And a date picker component for the date filter.",
   "assistant": "```tsx\nexport function DatePicker({ value, onSelect }: DatePickerProps) {\n  return <input type=\"date\" value={value} onChange={e => onSelect(e.target.value)} />;\n}\n```",
   "signal": {
    "turn_count": 5,
    "task_type": "chat",
    "matched_pattern": "carry_over",
    "topic_similarity": null,
    "shift": false,
    "recall_request": false,
    "tokens_used": 167,
    "budget": 700
   },
   "features": {
    "turn_count": 5,
    "token_budget_pressure": 0.2386,
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
     "reason": "token pressure 0.24 < 0.90: full recent history fits, window is lossless"
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
    "latency_ms": 0.0749,
    "override": [],
    "full": "[history_fits] token pressure 0.24 < 0.90: full recent history fits, window is lossless | features: turn=5, pressure=0.24, task=chat, prior=sliding_window, since_switch=1",
    "rule": "history_fits",
    "rule_reason": "token pressure 0.24 < 0.90: full recent history fits, window is lossless",
    "dwell": [],
    "escalations": []
   },
   "candidates": {
    "sliding_window": {
     "tokens": 155,
     "latency_ms": 0.65,
     "quality": {
      "kept": 4,
      "relevance": 0.182,
      "freshness": 0.882,
      "importance": 0.175,
      "state": 1.0,
      "composite": 0.56
     }
    },
    "summarization": {
     "tokens": 159,
     "latency_ms": 0.95,
     "quality": {
      "tier_emitted": "L1",
      "loss_score": 0.0,
      "loss_threshold_exceeded": false,
      "symbol_retention_rate": null
     }
    },
    "rag": {
     "tokens": 93,
     "latency_ms": 870.73,
     "quality": {
      "granularity_tag": "segment",
      "retrieved": 2,
      "stale_flags": 0
     }
    }
   },
   "prompt": {
    "tokens": 155,
    "context": "user: We're adding a search page to the admin dashboard (React + TypeScript). Any structure advice?\nassistant: Put the page in `src/pages/Search.tsx`, data fetching in a `useSearch` hook with React Query, and keep presentational components in `src/components/` without data logic.\nuser: Write a debounce hook for the search box.\nassistant: ```tsx\nexport function useDebounce<T>(value: T, delayMs = 300): T {\n  const [debounced, setDebounced] = useState(value);\n  useEffect(() => {\n    const id = setTimeout(() => setDebounced(value), delayMs);\n    return () => clearTimeout(id);\n  }, [value, delayMs]);\n  return debounced;\n}\n```",
    "truncated": false
   },
   "raised": [],
   "traps": []
  },
  {
   "exchange": 4,
   "turn_id": "t0007",
   "user": "Results flicker when typing fast. Why?",
   "assistant": "Each keystroke starts a request and older responses can land after newer ones. Pass the debounced term into the query key and set `keepPreviousData: true` so the list does not blank between pages.",
   "signal": {
    "turn_count": 7,
    "task_type": "chat",
    "matched_pattern": "carry_over",
    "topic_similarity": 0.177,
    "shift": false,
    "recall_request": false,
    "tokens_used": 219,
    "budget": 700
   },
   "features": {
    "turn_count": 7,
    "token_budget_pressure": 0.3129,
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
    "latency_ms": 0.071,
    "override": [],
    "full": "[history_fits] token pressure 0.31 < 0.90: full recent history fits, window is lossless | features: turn=7, pressure=0.31, task=chat, prior=sliding_window, since_switch=2",
    "rule": "history_fits",
    "rule_reason": "token pressure 0.31 < 0.90: full recent history fits, window is lossless",
    "dwell": [],
    "escalations": []
   },
   "candidates": {
    "sliding_window": {
     "tokens": 208,
     "latency_ms": 0.6,
     "quality": {
      "kept": 6,
      "relevance": 0.113,
      "freshness": 0.814,
      "importance": 0.183,
      "state": 1.0,
      "composite": 0.528
     }
    },
    "summarization": {
     "tokens": 213,
     "latency_ms": 0.9,
     "quality": {
      "tier_emitted": "L1",
      "loss_score": 0.0,
      "loss_threshold_exceeded": false,
      "symbol_retention_rate": null
     }
    },
    "rag": {
     "tokens": 110,
     "latency_ms": 710.52,
     "quality": {
      "granularity_tag": "turn",
      "retrieved": 2,
      "stale_flags": 0
     }
    }
   },
   "prompt": {
    "tokens": 209,
    "context": "user: We're adding a search page to the admin dashboard (React + TypeScript). Any structure advice?\nassistant: Put the page in `src/pages/Search.tsx`, data fetching in a `useSearch` hook with React Query, and keep presentational components in `src/components/` without data logic.\nuser: Write a debounce hook for the search box.\nassistant: ```tsx\nexport function useDebounce<T>(value: T, delayMs = 300): T {\n  const [debounced, setDebounced] = useState(value);\n  useEffect(() => {\n    const id = setTimeout(() => setDebounced(value), delayMs);\n    return () => clearTimeout(id);\n  }, [value, delayMs]);\n  return debounced;\n}\n```\nuser: And a date picker component for the date filter.\nassistant: ```tsx\nexport function DatePicker({ value, onSelect }: DatePickerProps) {\n  return <input type=\"date\" value={value} onChange={e => onSelect(e.target.value)} />;\n}\n```",
    "truncated": false
   },
   "raised": [],
   "traps": []
  },
  {
   "exchange": 5,
   "turn_id": "t0009",
   "user": "Our design system uses onChange everywhere. Rename onSelect in the date picker.",
   "assistant": "```tsx\nexport function DatePicker({ value, onChange }: DatePickerProps) {\n  return <input type=\"date\" value={value} onChange={e => onChange(e.target.value)} />;\n}\n```\nUpdated the props type and the two existing usages.",
   "signal": {
    "turn_count": 9,
    "task_type": "code_refactor",
    "matched_pattern": "pattern:code_refactor",
    "topic_similarity": 0.325,
    "shift": false,
    "recall_request": false,
    "tokens_used": 279,
    "budget": 700
   },
   "features": {
    "turn_count": 9,
    "token_budget_pressure": 0.3986,
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
    "latency_ms": 0.0953,
    "override": [],
    "full": "[history_fits] token pressure 0.40 < 0.90: full recent history fits, window is lossless | features: turn=9, pressure=0.40, task=code_refactor, prior=sliding_window, since_switch=3",
    "rule": "history_fits",
    "rule_reason": "token pressure 0.40 < 0.90: full recent history fits, window is lossless",
    "dwell": [],
    "escalations": []
   },
   "candidates": {
    "sliding_window": {
     "tokens": 263,
     "latency_ms": 0.56,
     "quality": {
      "kept": 8,
      "relevance": 0.212,
      "freshness": 0.753,
      "importance": 0.144,
      "state": 1.0,
      "composite": 0.527
     }
    },
    "summarization": {
     "tokens": 269,
     "latency_ms": 0.86,
     "quality": {
      "tier_emitted": "L1",
      "loss_score": 0.0,
      "loss_threshold_exceeded": false,
      "symbol_retention_rate": null
     }
    },
    "rag": {
     "tokens": 176,
     "latency_ms": 569.01,
     "quality": {
      "granularity_tag": "turn",
      "retrieved": 3,
      "stale_flags": 0
     }
    }
   },
   "prompt": {
    "tokens": 265,
    "context": "user: We're adding a search page to the admin dashboard (React + TypeScript). Any structure advice?\nassistant: Put the page in `src/pages/Search.tsx`, data fetching in a `useSearch` hook with React Query, and keep presentational components in `src/components/` without data logic.\nuser: Write a debounce hook for the search box.\nassistant: ```tsx\nexport function useDebounce<T>(value: T, delayMs = 300): T {\n  const [debounced, setDebounced] = useState(value);\n  useEffect(() => {\n    const id = setTimeout(() => setDebounced(value), delayMs);\n    return () => clearTimeout(id);\n  }, [value, delayMs]);\n  return debounced;\n}\n```\nuser: And a date picker component for the date filter.\nassistant: ```tsx\nexport function DatePicker({ value, onSelect }: DatePickerProps) {\n  return <input type=\"date\" value={value} onChange={e => onSelect(e.target.value)} />;\n}\n```\nuser: Results flicker when typing fast. Why?\nassistant: Each keystroke starts a request and older responses can land after newer ones. Pass the debounced term into the query key and set `keepPreviousData: true` so the list does not blank between pages.",
    "truncated": false
   },
   "raised": [],
   "traps": []
  },
  {
   "exchange": 6,
   "turn_id": "t0011",
   "user": "Set up Storybook for the components folder.",
   "assistant": "Initialised Storybook 8 with the Vite builder, added stories for Button, Table and Badge, and a `storybook` script. Chromatic runs on pull requests for visual review.",
   "signal": {
    "turn_count": 11,
    "task_type": "code_refactor",
    "matched_pattern": "carry_over",
    "topic_similarity": 0.159,
    "shift": false,
    "recall_request": false,
    "tokens_used": 343,
    "budget": 700
   },
   "features": {
    "turn_count": 11,
    "token_budget_pressure": 0.49,
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
    "latency_ms": 0.0593,
    "override": [],
    "full": "[history_fits] token pressure 0.49 < 0.90: full recent history fits, window is lossless | features: turn=11, pressure=0.49, task=code_refactor, prior=sliding_window, since_switch=4",
    "rule": "history_fits",
    "rule_reason": "token pressure 0.49 < 0.90: full recent history fits, window is lossless",
    "dwell": [],
    "escalations": []
   },
   "candidates": {
    "sliding_window": {
     "tokens": 332,
     "latency_ms": 0.51,
     "quality": {
      "kept": 10,
      "relevance": 0.124,
      "freshness": 0.698,
      "importance": 0.165,
      "state": 1.0,
      "composite": 0.497
     }
    },
    "summarization": {
     "tokens": 253,
     "latency_ms": 1.11,
     "quality": {
      "tier_emitted": "L1",
      "loss_score": 0.0,
      "loss_threshold_exceeded": false,
      "symbol_retention_rate": null
     }
    },
    "rag": {
     "tokens": 138,
     "latency_ms": 455.82,
     "quality": {
      "granularity_tag": "segment",
      "retrieved": 2,
      "stale_flags": 0
     }
    }
   },
   "prompt": {
    "tokens": 334,
    "context": "user: We're adding a search page to the admin dashboard (React + TypeScript). Any structure advice?\nassistant: Put the page in `src/pages/Search.tsx`, data fetching in a `useSearch` hook with React Query, and keep presentational components in `src/components/` without data logic.\nuser: Write a debounce hook for the search box.\nassistant: ```tsx\nexport function useDebounce<T>(value: T, delayMs = 300): T {\n  const [debounced, setDebounced] = useState(value);\n  useEffect(() => {\n    const id = setTimeout(() => setDebounced(value), delayMs);\n    return () => clearTimeout(id);\n  }, [value, delayMs]);\n  return debounced;\n}\n```\nuser: And a date picker component for the date filter.\nassistant: ```tsx\nexport function DatePicker({ value, onSelect }: DatePickerProps) {\n  return <input type=\"date\" value={value} onChange={e => onSelect(e.target.value)} />;\n}\n```\nuser: Results flicker when typing fast. Why?\nassistant: Each keystroke starts a request and older responses can land after newer ones. Pass the debounced term into the query key and set `keepPreviousData: true` so the list does not blank between pages.\nuser: Our design system uses onChange everywhere. Rename onSelect in the date picker.\nassistant: ```tsx\nexport function DatePicker({ value, onChange }: DatePickerProps) {\n  return <input type=\"date\" value={value} onChange={e => onChange(e.target.value)} />;\n}\n```\nUpdated the props type and the two existing usages.",
    "truncated": false
   },
   "raised": [],
   "traps": []
  },
  {
   "exchange": 7,
   "turn_id": "t0013",
   "user": "Add end-to-end tests for login and search.",
   "assistant": "Added Playwright with a login fixture that stores auth state once per worker. The search test types a term, waits for the network to settle and asserts the first row. Runs headless in CI on Chromium.",
   "signal": {
    "turn_count": 13,
    "task_type": "code_generation",
    "matched_pattern": "pattern:code_generation",
    "topic_similarity": 0.191,
    "shift": false,
    "recall_request": false,
    "tokens_used": 395,
    "budget": 700
   },
   "features": {
    "turn_count": 13,
    "token_budget_pressure": 0.5643,
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
     "reason": "token pressure 0.56 < 0.90: full recent history fits, window is lossless"
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
    "latency_ms": 0.0912,
    "override": [],
    "full": "[history_fits] token pressure 0.56 < 0.90: full recent history fits, window is lossless | features: turn=13, pressure=0.56, task=code_generation, prior=sliding_window, since_switch=5",
    "rule": "history_fits",
    "rule_reason": "token pressure 0.56 < 0.90: full recent history fits, window is lossless",
    "dwell": [],
    "escalations": []
   },
   "candidates": {
    "sliding_window": {
     "tokens": 383,
     "latency_ms": 0.52,
     "quality": {
      "kept": 12,
      "relevance": 0.151,
      "freshness": 0.649,
      "importance": 0.146,
      "state": 1.0,
      "composite": 0.486
     }
    },
    "summarization": {
     "tokens": 304,
     "latency_ms": 1.29,
     "quality": {
      "tier_emitted": "L1",
      "loss_score": 0.0,
      "loss_threshold_exceeded": false,
      "symbol_retention_rate": null
     }
    },
    "rag": {
     "tokens": 166,
     "latency_ms": 365.36,
     "quality": {
      "granularity_tag": "turn",
      "retrieved": 4,
      "stale_flags": 0
     }
    }
   },
   "prompt": {
    "tokens": 385,
    "context": "user: We're adding a search page to the admin dashboard (React + TypeScript). Any structure advice?\nassistant: Put the page in `src/pages/Search.tsx`, data fetching in a `useSearch` hook with React Query, and keep presentational components in `src/components/` without data logic.\nuser: Write a debounce hook for the search box.\nassistant: ```tsx\nexport function useDebounce<T>(value: T, delayMs = 300): T {\n  const [debounced, setDebounced] = useState(value);\n  useEffect(() => {\n    const id = setTimeout(() => setDebounced(value), delayMs);\n    return () => clearTimeout(id);\n  }, [value, delayMs]);\n  return debounced;\n}\n```\nuser: And a date picker component for the date filter.\nassistant: ```tsx\nexport function DatePicker({ value, onSelect }: DatePickerProps) {\n  return <input type=\"date\" value={value} onChange={e => onSelect(e.target.value)} />;\n}\n```\nuser: Results flicker when typing fast. Why?\nassistant: Each keystroke starts a request and older responses can land after newer ones. Pass the debounced term into the query key and set `keepPreviousData: true` so the list does not blank between pages.\nuser: Our design system uses onChange everywhere. Rename onSelect in the date picker.\nassistant: ```tsx\nexport function DatePicker({ value, onChange }: DatePickerProps) {\n  return <input type=\"date\" value={value} onChange={e => onChange(e.target.value)} />;\n}\n```\nUpdated the props type and the two existing usages.\nuser: Set up Storybook for the components folder.\nassistant: Initialised Storybook 8 with the Vite builder, added stories for Button, Table and Badge, and a `storybook` script. Chromatic runs on pull requests for visual review.",
    "truncated": false
   },
   "raised": [],
   "traps": []
  },
  {
   "exchange": 8,
   "turn_id": "t0015",
   "user": "Bundle size jumped to 1.4 MB. Help.",
   "assistant": "The date library is imported whole. Switch to `date-fns` per-function imports and lazy-load the charts route with `React.lazy`; the main chunk drops to about 480 KB.",
   "signal": {
    "turn_count": 15,
    "task_type": "code_generation",
    "matched_pattern": "carry_over",
    "topic_similarity": 0.164,
    "shift": false,
    "recall_request": false,
    "tokens_used": 453,
    "budget": 700
   },
   "features": {
    "turn_count": 15,
    "token_budget_pressure": 0.6471,
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
     "reason": "token pressure 0.65 < 0.90: full recent history fits, window is lossless"
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
    "latency_ms": 0.0925,
    "override": [],
    "full": "[history_fits] token pressure 0.65 < 0.90: full recent history fits, window is lossless | features: turn=15, pressure=0.65, task=code_generation, prior=sliding_window, since_switch=6",
    "rule": "history_fits",
    "rule_reason": "token pressure 0.65 < 0.90: full recent history fits, window is lossless",
    "dwell": [],
    "escalations": []
   },
   "candidates": {
    "sliding_window": {
     "tokens": 439,
     "latency_ms": 0.51,
     "quality": {
      "kept": 14,
      "relevance": 0.043,
      "freshness": 0.605,
      "importance": 0.125,
      "state": 1.0,
      "composite": 0.443
     }
    },
    "summarization": {
     "tokens": 360,
     "latency_ms": 1.46,
     "quality": {
      "tier_emitted": "L1",
      "loss_score": 0.0,
      "loss_threshold_exceeded": false,
      "symbol_retention_rate": null
     }
    },
    "rag": {
     "tokens": 82,
     "latency_ms": 293.0,
     "quality": {
      "granularity_tag": "segment",
      "retrieved": 2,
      "stale_flags": 0
     }
    }
   },
   "prompt": {
    "tokens": 441,
    "context": "user: We're adding a search page to the admin dashboard (React + TypeScript). Any structure advice?\nassistant: Put the page in `src/pages/Search.tsx`, data fetching in a `useSearch` hook with React Query, and keep presentational components in `src/components/` without data logic.\nuser: Write a debounce hook for the search box.\nassistant: ```tsx\nexport function useDebounce<T>(value: T, delayMs = 300): T {\n  const [debounced, setDebounced] = useState(value);\n  useEffect(() => {\n    const id = setTimeout(() => setDebounced(value), delayMs);\n    return () => clearTimeout(id);\n  }, [value, delayMs]);\n  return debounced;\n}\n```\nuser: And a date picker component for the date filter.\nassistant: ```tsx\nexport function DatePicker({ value, onSelect }: DatePickerProps) {\n  return <input type=\"date\" value={value} onChange={e => onSelect(e.target.value)} />;\n}\n```\nuser: Results flicker when typing fast. Why?\nassistant: Each keystroke starts a request and older responses can land after newer ones. Pass the debounced term into the query key and set `keepPreviousData: true` so the list does not blank between pages.\nuser: Our design system uses onChange everywhere. Rename onSelect in the date picker.\nassistant: ```tsx\nexport function DatePicker({ value, onChange }: DatePickerProps) {\n  return <input type=\"date\" value={value} onChange={e => onChange(e.target.value)} />;\n}\n```\nUpdated the props type and the two existing usages.\nuser: Set up Storybook for the components folder.\nassistant: Initialised Storybook 8 with the Vite builder, added stories for Button, Table and Badge, and a `storybook` script. Chromatic runs on pull requests for visual review.\nuser: Add end-to-end tests for login and search.\nassistant: Added Playwright with a login fixture that stores auth state once per worker. The search test types a term, waits for the network to settle and asserts the first row. Runs headless in CI on Chromium.",
    "truncated": false
   },
   "raised": [],
   "traps": []
  },
  {
   "exchange": 9,
   "turn_id": "t0017",
   "user": "Make the table accessible.",
   "assistant": "Use a real `<table>` with `<th scope=\"col\">`, `aria-sort` on sortable headers, a visible focus ring, and announce result counts through an `aria-live=\"polite\"` region after each search.",
   "signal": {
    "turn_count": 17,
    "task_type": "code_generation",
    "matched_pattern": "carry_over",
    "topic_similarity": 0.194,
    "shift": false,
    "recall_request": false,
    "tokens_used": 500,
    "budget": 700
   },
   "features": {
    "turn_count": 17,
    "token_budget_pressure": 0.7143,
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
    "strategy": "sliding_window",
    "latency_ms": 0.0511,
    "override": [],
    "full": "[history_fits] token pressure 0.71 < 0.90: full recent history fits, window is lossless | features: turn=17, pressure=0.71, task=code_generation, prior=sliding_window, since_switch=7",
    "rule": "history_fits",
    "rule_reason": "token pressure 0.71 < 0.90: full recent history fits, window is lossless",
    "dwell": [],
    "escalations": []
   },
   "candidates": {
    "sliding_window": {
     "tokens": 493,
     "latency_ms": 0.47,
     "quality": {
      "kept": 16,
      "relevance": 0.1,
      "freshness": 0.565,
      "importance": 0.125,
      "state": 1.0,
      "composite": 0.448
     }
    },
    "summarization": {
     "tokens": 414,
     "latency_ms": 1.69,
     "quality": {
      "tier_emitted": "L1",
      "loss_score": 0.0,
      "loss_threshold_exceeded": false,
      "symbol_retention_rate": null
     }
    },
    "rag": {
     "tokens": 135,
     "latency_ms": 235.13,
     "quality": {
      "granularity_tag": "turn",
      "retrieved": 3,
      "stale_flags": 0
     }
    }
   },
   "prompt": {
    "tokens": 495,
    "context": "user: We're adding a search page to the admin dashboard (React + TypeScript). Any structure advice?\nassistant: Put the page in `src/pages/Search.tsx`, data fetching in a `useSearch` hook with React Query, and keep presentational components in `src/components/` without data logic.\nuser: Write a debounce hook for the search box.\nassistant: ```tsx\nexport function useDebounce<T>(value: T, delayMs = 300): T {\n  const [debounced, setDebounced] = useState(value);\n  useEffect(() => {\n    const id = setTimeout(() => setDebounced(value), delayMs);\n    return () => clearTimeout(id);\n  }, [value, delayMs]);\n  return debounced;\n}\n```\nuser: And a date picker component for the date filter.\nassistant: ```tsx\nexport function DatePicker({ value, onSelect }: DatePickerProps) {\n  return <input type=\"date\" value={value} onChange={e => onSelect(e.target.value)} />;\n}\n```\nuser: Results flicker when typing fast. Why?\nassistant: Each keystroke starts a request and older responses can land after newer ones. Pass the debounced term into the query key and set `keepPreviousData: true` so the list does not blank between pages.\nuser: Our design system uses onChange everywhere. Rename onSelect in the date picker.\nassistant: ```tsx\nexport function DatePicker({ value, onChange }: DatePickerProps) {\n  return <input type=\"date\" value={value} onChange={e => onChange(e.target.value)} />;\n}\n```\nUpdated the props type and the two existing usages.\nuser: Set up Storybook for the components folder.\nassistant: Initialised Storybook 8 with the Vite builder, added stories for Button, Table and Badge, and a `storybook` script. Chromatic runs on pull requests for visual review.\nuser: Add end-to-end tests for login and search.\nassistant: Added Playwright with a login fixture that stores auth state once per worker. The search test types a term, waits for the network to settle and asserts the first row. Runs headless in CI on Chromium.\nuser: Bundle size jumped to 1.4 MB. Help.\nassistant: The date library is imported whole. Switch to `date-fns` per-function imports and lazy-load the charts route with `React.lazy`; the main chunk drops to about 480 KB.",
    "truncated": false
   },
   "raised": [],
   "traps": []
  },
  {
   "exchange": 10,
   "turn_id": "t0019",
   "user": "Add dark mode.",
   "assistant": "Defined colour tokens as CSS variables on `:root` and `[data-theme=dark]`, read the OS preference with `prefers-color-scheme`, and persist the user's choice in localStorage.",
   "signal": {
    "turn_count": 19,
    "task_type": "code_generation",
    "matched_pattern": "carry_over",
    "topic_similarity": 0.254,
    "shift": false,
    "recall_request": false,
    "tokens_used": 553,
    "budget": 700
   },
   "features": {
    "turn_count": 19,
    "token_budget_pressure": 0.79,
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
     "reason": "token pressure 0.79 < 0.90: full recent history fits, window is lossless"
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
    "latency_ms": 0.0782,
    "override": [],
    "full": "[history_fits] token pressure 0.79 < 0.90: full recent history fits, window is lossless | features: turn=19, pressure=0.79, task=code_generation, prior=sliding_window, since_switch=8",
    "rule": "history_fits",
    "rule_reason": "token pressure 0.79 < 0.90: full recent history fits, window is lossless",
    "dwell": [],
    "escalations": []
   },
   "candidates": {
    "sliding_window": {
     "tokens": 547,
     "latency_ms": 0.48,
     "quality": {
      "kept": 18,
      "relevance": 0.12,
      "freshness": 0.529,
      "importance": 0.111,
      "state": 1.0,
      "composite": 0.44
     }
    },
    "summarization": {
     "tokens": 468,
     "latency_ms": 1.92,
     "quality": {
      "tier_emitted": "L1",
      "loss_score": 0.0,
      "loss_threshold_exceeded": false,
      "symbol_retention_rate": null
     }
    },
    "rag": {
     "tokens": 331,
     "latency_ms": 188.81,
     "quality": {
      "granularity_tag": "turn",
      "retrieved": 7,
      "stale_flags": 0
     }
    }
   },
   "prompt": {
    "tokens": 549,
    "context": "user: We're adding a search page to the admin dashboard (React + TypeScript). Any structure advice?\nassistant: Put the page in `src/pages/Search.tsx`, data fetching in a `useSearch` hook with React Query, and keep presentational components in `src/components/` without data logic.\nuser: Write a debounce hook for the search box.\nassistant: ```tsx\nexport function useDebounce<T>(value: T, delayMs = 300): T {\n  const [debounced, setDebounced] = useState(value);\n  useEffect(() => {\n    const id = setTimeout(() => setDebounced(value), delayMs);\n    return () => clearTimeout(id);\n  }, [value, delayMs]);\n  return debounced;\n}\n```\nuser: And a date picker component for the date filter.\nassistant: ```tsx\nexport function DatePicker({ value, onSelect }: DatePickerProps) {\n  return <input type=\"date\" value={value} onChange={e => onSelect(e.target.value)} />;\n}\n```\nuser: Results flicker when typing fast. Why?\nassistant: Each keystroke starts a request and older responses can land after newer ones. Pass the debounced term into the query key and set `keepPreviousData: true` so the list does not blank between pages.\nuser: Our design system uses onChange everywhere. Rename onSelect in the date picker.\nassistant: ```tsx\nexport function DatePicker({ value, onChange }: DatePickerProps) {\n  return <input type=\"date\" value={value} onChange={e => onChange(e.target.value)} />;\n}\n```\nUpdated the props type and the two existing usages.\nuser: Set up Storybook for the components folder.\nassistant: Initialised Storybook 8 with the Vite builder, added stories for Button, Table and Badge, and a `storybook` script. Chromatic runs on pull requests for visual review.\nuser: Add end-to-end tests for login and search.\nassistant: Added Playwright with a login fixture that stores auth state once per worker. The search test types a term, waits for the network to settle and asserts the first row. Runs headless in CI on Chromium.\nuser: Bundle size jumped to 1.4 MB. Help.\nassistant: The date library is imported whole. Switch to `date-fns` per-function imports and lazy-load the charts route with `React.lazy`; the main chunk drops to about 480 KB.\nuser: Make the table accessible.\nassistant: Use a real `<table>` with `<th scope=\"col\">`, `aria-sort` on sortable headers, a visible focus ring, and announce result counts through an `aria-live=\"polite\"` region after each search.",
    "truncated": false
   },
   "raised": [],
   "traps": []
  },
  {
   "exchange": 11,
   "turn_id": "t0021",
   "user": "Write a hook that delays updating the filter value until the user stops typing in the tag filter.",
   "assistant": "(scripted reply omitted - the check is on the context the model would receive)",
   "signal": {
    "turn_count": 21,
    "task_type": "code_generation",
    "matched_pattern": "carry_over",
    "topic_similarity": 0.159,
    "shift": false,
    "recall_request": false,
    "tokens_used": 616,
    "budget": 700
   },
   "features": {
    "turn_count": 21,
    "token_budget_pressure": 0.88,
    "task_type": "code_generation",
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
     "reason": "token pressure 0.88 < 0.90: full recent history fits, window is lossless"
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
    "latency_ms": 0.0699,
    "override": [],
    "full": "[history_fits] token pressure 0.88 < 0.90: full recent history fits, window is lossless | features: turn=21, pressure=0.88, task=code_generation, prior=sliding_window, since_switch=9",
    "rule": "history_fits",
    "rule_reason": "token pressure 0.88 < 0.90: full recent history fits, window is lossless",
    "dwell": [],
    "escalations": []
   },
   "candidates": {
    "sliding_window": {
     "tokens": 595,
     "latency_ms": 0.48,
     "quality": {
      "kept": 20,
      "relevance": 0.149,
      "freshness": 0.496,
      "importance": 0.102,
      "state": 1.0,
      "composite": 0.437
     }
    },
    "summarization": {
     "tokens": 516,
     "latency_ms": 2.03,
     "quality": {
      "tier_emitted": "L1",
      "loss_score": 0.0,
      "loss_threshold_exceeded": false,
      "symbol_retention_rate": null
     }
    },
    "rag": {
     "tokens": 447,
     "latency_ms": 151.67,
     "quality": {
      "granularity_tag": "turn",
      "retrieved": 8,
      "stale_flags": 0
     }
    }
   },
   "prompt": {
    "tokens": 597,
    "context": "user: We're adding a search page to the admin dashboard (React + TypeScript). Any structure advice?\nassistant: Put the page in `src/pages/Search.tsx`, data fetching in a `useSearch` hook with React Query, and keep presentational components in `src/components/` without data logic.\nuser: Write a debounce hook for the search box.\nassistant: ```tsx\nexport function useDebounce<T>(value: T, delayMs = 300): T {\n  const [debounced, setDebounced] = useState(value);\n  useEffect(() => {\n    const id = setTimeout(() => setDebounced(value), delayMs);\n    return () => clearTimeout(id);\n  }, [value, delayMs]);\n  return debounced;\n}\n```\nuser: And a date picker component for the date filter.\nassistant: ```tsx\nexport function DatePicker({ value, onSelect }: DatePickerProps) {\n  return <input type=\"date\" value={value} onChange={e => onSelect(e.target.value)} />;\n}\n```\nuser: Results flicker when typing fast. Why?\nassistant: Each keystroke starts a request and older responses can land after newer ones. Pass the debounced term into the query key and set `keepPreviousData: true` so the list does not blank between pages.\nuser: Our design system uses onChange everywhere. Rename onSelect in the date picker.\nassistant: ```tsx\nexport function DatePicker({ value, onChange }: DatePickerProps) {\n  return <input type=\"date\" value={value} onChange={e => onChange(e.target.value)} />;\n}\n```\nUpdated the props type and the two existing usages.\nuser: Set up Storybook for the components folder.\nassistant: Initialised Storybook 8 with the Vite builder, added stories for Button, Table and Badge, and a `storybook` script. Chromatic runs on pull requests for visual review.\nuser: Add end-to-end tests for login and search.\nassistant: Added Playwright with a login fixture that stores auth state once per worker. The search test types a term, waits for the network to settle and asserts the first row. Runs headless in CI on Chromium.\nuser: Bundle size jumped to 1.4 MB. Help.\nassistant: The date library is imported whole. Switch to `date-fns` per-function imports and lazy-load the charts route with `React.lazy`; the main chunk drops to about 480 KB.\nuser: Make the table accessible.\nassistant: Use a real `<table>` with `<th scope=\"col\">`, `aria-sort` on sortable headers, a visible focus ring, and announce result counts through an `aria-live=\"polite\"` region after each search.\nuser: Add dark mode.\nassistant: Defined colour tokens as CSS variables on `:root` and `[data-theme=dark]`, read the OS preference with `prefers-color-scheme`, and persist the user's choice in localStorage.",
    "truncated": false
   },
   "raised": [],
   "traps": [
    {
     "name": "duplicate debounce hook",
     "description": "useDebounce exists since exchange 2",
     "planted_at": 2,
     "kind": "duplicate",
     "adaptive": {
      "caught": true,
      "detail": "found `export function useDebounce<T>(`",
      "strategy": "sliding_window"
     },
     "fixed_6_exchange_window": {
      "caught": false,
      "detail": "missing `export function useDebounce<T>(`"
     },
     "sliding_window": {
      "caught": true,
      "detail": "found `export function useDebounce<T>(`"
     },
     "summarization": {
      "caught": false,
      "detail": "missing `export function useDebounce<T>(`"
     },
     "rag": {
      "caught": true,
      "detail": "found `export function useDebounce<T>(`"
     },
     "hybrid": {
      "caught": true,
      "detail": "found `export function useDebounce<T>(`"
     }
    }
   ]
  },
  {
   "exchange": 12,
   "turn_id": "t0023",
   "user": "Use the date picker for the 'created after' filter and wire up its change handler.",
   "assistant": "(scripted reply omitted - the check is on the context the model would receive)",
   "signal": {
    "turn_count": 23,
    "task_type": "code_generation",
    "matched_pattern": "carry_over",
    "topic_similarity": 0.19,
    "shift": false,
    "recall_request": false,
    "tokens_used": 655,
    "budget": 700
   },
   "features": {
    "turn_count": 23,
    "token_budget_pressure": 0.9357,
    "task_type": "code_generation",
    "prior_strategy": "sliding_window",
    "time_since_last_switch": 10
   },
   "rules": [
    {
     "fn": "fits",
     "matched": false,
     "fired": false,
     "rule": null,
     "strategy": null,
     "hard": null,
     "reason": null
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
     "fired": true,
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
    "latency_ms": 0.0741,
    "override": [],
    "full": "[build_request] task_type=code_generation (build-request pattern) -> hybrid: recent window + RAG to surface existing definitions before writing new code | features: turn=23, pressure=0.94, task=code_generation, prior=sliding_window, since_switch=10",
    "rule": "build_request",
    "rule_reason": "task_type=code_generation (build-request pattern) -> hybrid: recent window + RAG to surface existing definitions before writing new code",
    "dwell": [],
    "escalations": []
   },
   "candidates": {
    "sliding_window": {
     "tokens": 635,
     "latency_ms": 0.49,
     "quality": {
      "kept": 22,
      "relevance": 0.153,
      "freshness": 0.466,
      "importance": 0.093,
      "state": 1.0,
      "composite": 0.428
     }
    },
    "summarization": {
     "tokens": 596,
     "latency_ms": 2.52,
     "quality": {
      "tier_emitted": "L1",
      "loss_score": 0.0,
      "loss_threshold_exceeded": false,
      "symbol_retention_rate": null
     }
    },
    "rag": {
     "tokens": 249,
     "latency_ms": 122.13,
     "quality": {
      "granularity_tag": "turn",
      "retrieved": 5,
      "stale_flags": 0
     }
    }
   },
   "prompt": {
    "tokens": 666,
    "context": "[Retrieved memory]\n[turns: t0005 t0006]\nuser: And a date picker component for the date filter.\nassistant: ```tsx\nexport function DatePicker({ value, onSelect }: DatePickerProps) {\n  return <input type=\"date\" value={value} onChange={e => onSelect(e.target.value)} />;\n}\n```\n\n---\n\n[turns: t0009 t0010]\nuser: Our design system uses onChange everywhere. Rename onSelect in the date picker.\nassistant: ```tsx\nexport function DatePicker({ value, onChange }: DatePickerProps) {\n  return <input type=\"date\" value={value} onChange={e => onChange(e.target.value)} />;\n}\n```\nUpdated the props type and the two existing usages.\n\n---\n\n[turns: t0003]\nuser: Write a debounce hook for the search box.\n\n---\n\n[turns: t0008]\nassistant: Each keystroke starts a request and older responses can land after newer ones. Pass the debounced term into the query key and set `keepPreviousData: true` so the list does not blank between pages.\n\n[Recent turns]\nassistant: Put the page in `src/pages/Search.tsx`, data fetching in a `useSearch` hook with React Query, and keep presentational components in `src/components/` without data logic.\nassistant: ```tsx\nexport function useDebounce<T>(value: T, delayMs = 300): T {\n  const [debounced, setDebounced] = useState(value);\n  useEffect(() => {\n    const id = setTimeout(() => setDebounced(value), delayMs);\n    return () => clearTimeout(id);\n  }, [value, delayMs]);\n  return debounced;\n}\n```\nuser: Results flicker when typing fast. Why?\nuser: Set up Storybook for the components folder.\nassistant: Initialised Storybook 8 with the Vite builder, added stories for Button, Table and Badge, and a `storybook` script. Chromatic runs on pull requests for visual review.\nuser: Add end-to-end tests for login and search.\nassistant: Added Playwright with a login fixture that stores auth state once per worker. The search test types a term, waits for the network to settle and asserts the first row. Runs headless in CI on Chromium.\nuser: Bundle size jumped to 1.4 MB. Help.\nassistant: The date library is imported whole. Switch to `date-fns` per-function imports and lazy-load the charts route with `React.lazy`; the main chunk drops to about 480 KB.\nuser: Make the table accessible.\nassistant: Use a real `<table>` with `<th scope=\"col\">`, `aria-sort` on sortable headers, a visible focus ring, and announce result counts through an `aria-live=\"polite\"` region after each search.\nuser: Add dark mode.\nassistant: Defined colour tokens as CSS variables on `:root` and `[data-theme=dark]`, read the OS preference with `prefers-color-scheme`, and persist the user's choice in localStorage.\nuser: Write a hook that delays updating the filter value until the user stops typing in the tag filter.\nassistant: (scripted reply omitted - the check is on the context the model would receive)",
    "truncated": false
   },
   "raised": [],
   "traps": [
    {
     "name": "renamed prop",
     "description": "DatePicker prop onSelect -> onChange at exchange 5",
     "planted_at": 5,
     "kind": "rename",
     "adaptive": {
      "caught": false,
      "detail": "unmarked stale `DatePicker({ value, onSelect }` present",
      "strategy": "hybrid"
     },
     "fixed_6_exchange_window": {
      "caught": false,
      "detail": "missing `DatePicker({ value, onChange }`"
     },
     "sliding_window": {
      "caught": false,
      "detail": "unmarked stale `DatePicker({ value, onSelect }` present"
     },
     "summarization": {
      "caught": false,
      "detail": "missing `DatePicker({ value, onChange }`"
     },
     "rag": {
      "caught": false,
      "detail": "unmarked stale `DatePicker({ value, onSelect }` present"
     },
     "hybrid": {
      "caught": false,
      "detail": "unmarked stale `DatePicker({ value, onSelect }` present"
     }
    }
   ]
  }
 ]
};
