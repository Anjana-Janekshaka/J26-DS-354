window.CEAI_SESSIONS = window.CEAI_SESSIONS || {};
window.CEAI_SESSIONS["invoice-service"] = {
 "scenario": "invoice-service",
 "slug": "invoice-service",
 "language": "python",
 "held_out": true,
 "system": "frozen",
 "mode": "full",
 "budget": 700,
 "recorded_at": "2026-10-19T11:20:53+00:00",
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
  "adaptive": 3,
  "fixed_6_exchange_window": 0,
  "sliding_window": 1,
  "summarization": 1,
  "rag": 3,
  "hybrid": 3
 },
 "turns": [
  {
   "exchange": 1,
   "turn_id": "t0001",
   "user": "Give me an overview of the invoice service before we start.",
   "assistant": "It is a FastAPI app. `billing/models.py` has `Invoice` and `LineItem` (SQLModel), `billing/api.py` exposes /invoices and /quotes, and `billing/pdf.py` renders invoices with WeasyPrint. Amounts are stored as integer cents in the database and converted at the API edge.",
   "signal": {
    "turn_count": 1,
    "task_type": "exploration",
    "matched_pattern": "pattern:exploration",
    "topic_similarity": null,
    "shift": false,
    "recall_request": false,
    "tokens_used": 14,
    "budget": 700
   },
   "features": {
    "turn_count": 1,
    "token_budget_pressure": 0.02,
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
    "latency_ms": 0.0865,
    "override": [],
    "full": "[history_fits] token pressure 0.02 < 0.90: full recent history fits, window is lossless | features: turn=1, pressure=0.02, task=exploration, prior=None, since_switch=0",
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
   "user": "Add a helper that computes a line item's total including tax.",
   "assistant": "Added to `billing/pricing.py`:\n```python\nTAX_RATE = 0.08\n\ndef compute_line_total(qty, unit_price, tax_rate=TAX_RATE):\n    subtotal = qty * unit_price\n    return round(subtotal * (1 + tax_rate), 2)\n```",
   "signal": {
    "turn_count": 3,
    "task_type": "code_generation",
    "matched_pattern": "pattern:code_generation",
    "topic_similarity": null,
    "shift": false,
    "recall_request": false,
    "tokens_used": 98,
    "budget": 700
   },
   "features": {
    "turn_count": 3,
    "token_budget_pressure": 0.14,
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
     "reason": "token pressure 0.14 < 0.90: full recent history fits, window is lossless"
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
    "latency_ms": 0.078,
    "override": [],
    "full": "[history_fits] token pressure 0.14 < 0.90: full recent history fits, window is lossless | features: turn=3, pressure=0.14, task=code_generation, prior=sliding_window, since_switch=0",
    "rule": "history_fits",
    "rule_reason": "token pressure 0.14 < 0.90: full recent history fits, window is lossless",
    "dwell": [],
    "escalations": []
   },
   "candidates": {
    "sliding_window": {
     "tokens": 83,
     "latency_ms": 0.71,
     "quality": {
      "kept": 2,
      "relevance": 0.315,
      "freshness": 0.959,
      "importance": 0.1,
      "state": 1.0,
      "composite": 0.593
     }
    },
    "summarization": {
     "tokens": 87,
     "latency_ms": 0.99,
     "quality": {
      "tier_emitted": "L1",
      "loss_score": 0.0,
      "loss_threshold_exceeded": false,
      "symbol_retention_rate": null
     }
    },
    "rag": {
     "tokens": 100,
     "latency_ms": 1.22,
     "quality": {
      "granularity_tag": "turn",
      "retrieved": 2,
      "stale_flags": 0
     }
    }
   },
   "prompt": {
    "tokens": 83,
    "context": "user: Give me an overview of the invoice service before we start.\nassistant: It is a FastAPI app. `billing/models.py` has `Invoice` and `LineItem` (SQLModel), `billing/api.py` exposes /invoices and /quotes, and `billing/pdf.py` renders invoices with WeasyPrint. Amounts are stored as integer cents in the database and converted at the API edge.",
    "truncated": false
   },
   "raised": [],
   "traps": []
  },
  {
   "exchange": 3,
   "turn_id": "t0005",
   "user": "Write the function that emails an invoice PDF to the customer.",
   "assistant": "Added to `billing/notify.py`:\n```python\ndef send_invoice_email(invoice_id, recipient):\n    pdf = render_invoice_pdf(invoice_id)\n    mailer.send(to=recipient, subject=f'Invoice {invoice_id}', attachment=pdf)\n```",
   "signal": {
    "turn_count": 5,
    "task_type": "code_generation",
    "matched_pattern": "pattern:code_generation",
    "topic_similarity": null,
    "shift": false,
    "recall_request": false,
    "tokens_used": 175,
    "budget": 700
   },
   "features": {
    "turn_count": 5,
    "token_budget_pressure": 0.25,
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
    "latency_ms": 0.0636,
    "override": [],
    "full": "[history_fits] token pressure 0.25 < 0.90: full recent history fits, window is lossless | features: turn=5, pressure=0.25, task=code_generation, prior=sliding_window, since_switch=1",
    "rule": "history_fits",
    "rule_reason": "token pressure 0.25 < 0.90: full recent history fits, window is lossless",
    "dwell": [],
    "escalations": []
   },
   "candidates": {
    "sliding_window": {
     "tokens": 161,
     "latency_ms": 0.64,
     "quality": {
      "kept": 4,
      "relevance": 0.309,
      "freshness": 0.882,
      "importance": 0.225,
      "state": 1.0,
      "composite": 0.604
     }
    },
    "summarization": {
     "tokens": 165,
     "latency_ms": 0.92,
     "quality": {
      "tier_emitted": "L1",
      "loss_score": 0.0,
      "loss_threshold_exceeded": false,
      "symbol_retention_rate": 1.0
     }
    },
    "rag": {
     "tokens": 197,
     "latency_ms": 1.6,
     "quality": {
      "granularity_tag": "turn",
      "retrieved": 4,
      "stale_flags": 0
     }
    }
   },
   "prompt": {
    "tokens": 161,
    "context": "user: Give me an overview of the invoice service before we start.\nassistant: It is a FastAPI app. `billing/models.py` has `Invoice` and `LineItem` (SQLModel), `billing/api.py` exposes /invoices and /quotes, and `billing/pdf.py` renders invoices with WeasyPrint. Amounts are stored as integer cents in the database and converted at the API edge.\nuser: Add a helper that computes a line item's total including tax.\nassistant: Added to `billing/pricing.py`:\n```python\nTAX_RATE = 0.08\n\ndef compute_line_total(qty, unit_price, tax_rate=TAX_RATE):\n    subtotal = qty * unit_price\n    return round(subtotal * (1 + tax_rate), 2)\n```",
    "truncated": false
   },
   "raised": [],
   "traps": []
  },
  {
   "exchange": 4,
   "turn_id": "t0007",
   "user": "test_invoice_total fails: expected 108.0 but got 107.99. What's wrong?",
   "assistant": "The fixture builds unit prices from floats like 0.1 * 3. Build them with `Decimal('0.30')` in the fixture, or compare with `pytest.approx`, the helper itself rounds correctly.",
   "signal": {
    "turn_count": 7,
    "task_type": "debugging",
    "matched_pattern": "pattern:debugging",
    "topic_similarity": 0.413,
    "shift": false,
    "recall_request": false,
    "tokens_used": 253,
    "budget": 700
   },
   "features": {
    "turn_count": 7,
    "token_budget_pressure": 0.3614,
    "task_type": "debugging",
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
     "reason": "token pressure 0.36 < 0.90: full recent history fits, window is lossless"
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
     "matched": true,
     "fired": false,
     "rule": "debugging",
     "strategy": "sliding_window",
     "hard": false,
     "reason": "task_type=debugging -> sliding window: latest edits and traces are local and recent"
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
    "latency_ms": 0.0661,
    "override": [],
    "full": "[history_fits] token pressure 0.36 < 0.90: full recent history fits, window is lossless | features: turn=7, pressure=0.36, task=debugging, prior=sliding_window, since_switch=2",
    "rule": "history_fits",
    "rule_reason": "token pressure 0.36 < 0.90: full recent history fits, window is lossless",
    "dwell": [],
    "escalations": []
   },
   "candidates": {
    "sliding_window": {
     "tokens": 230,
     "latency_ms": 0.58,
     "quality": {
      "kept": 6,
      "relevance": 0.339,
      "freshness": 0.814,
      "importance": 0.25,
      "state": 1.0,
      "composite": 0.601
     }
    },
    "summarization": {
     "tokens": 235,
     "latency_ms": 0.92,
     "quality": {
      "tier_emitted": "L1",
      "loss_score": 0.0,
      "loss_threshold_exceeded": false,
      "symbol_retention_rate": 1.0
     }
    },
    "rag": {
     "tokens": 311,
     "latency_ms": 1095.6,
     "quality": {
      "granularity_tag": "turn",
      "retrieved": 6,
      "stale_flags": 1
     }
    }
   },
   "prompt": {
    "tokens": 231,
    "context": "user: Give me an overview of the invoice service before we start.\nassistant: It is a FastAPI app. `billing/models.py` has `Invoice` and `LineItem` (SQLModel), `billing/api.py` exposes /invoices and /quotes, and `billing/pdf.py` renders invoices with WeasyPrint. Amounts are stored as integer cents in the database and converted at the API edge.\nuser: Add a helper that computes a line item's total including tax.\nassistant: Added to `billing/pricing.py`:\n```python\nTAX_RATE = 0.08\n\ndef compute_line_total(qty, unit_price, tax_rate=TAX_RATE):\n    subtotal = qty * unit_price\n    return round(subtotal * (1 + tax_rate), 2)\n```\nuser: Write the function that emails an invoice PDF to the customer.\nassistant: Added to `billing/notify.py`:\n```python\ndef send_invoice_email(invoice_id, recipient):\n    pdf = render_invoice_pdf(invoice_id)\n    mailer.send(to=recipient, subject=f'Invoice {invoice_id}', attachment=pdf)\n```",
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
   "exchange": 5,
   "turn_id": "t0009",
   "user": "Used pytest.approx, green now. The /invoices list endpoint is slow though.",
   "assistant": "It lazily loads line items per invoice, an N+1 pattern. Add `selectinload(Invoice.line_items)` to the query in `list_invoices` and the 200 queries collapse into 2.",
   "signal": {
    "turn_count": 9,
    "task_type": "debugging",
    "matched_pattern": "carry_over",
    "topic_similarity": 0.521,
    "shift": false,
    "recall_request": false,
    "tokens_used": 319,
    "budget": 700
   },
   "features": {
    "turn_count": 9,
    "token_budget_pressure": 0.4557,
    "task_type": "debugging",
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
     "matched": true,
     "fired": false,
     "rule": "debugging",
     "strategy": "sliding_window",
     "hard": false,
     "reason": "task_type=debugging -> sliding window: latest edits and traces are local and recent"
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
    "full": "[history_fits] token pressure 0.46 < 0.90: full recent history fits, window is lossless | escalation from t0007: 1 stale chunk(s) flagged -> hybrid so the superseding facts are retrievable next to the recent window | features: turn=9, pressure=0.46, task=debugging, prior=sliding_window, since_switch=3",
    "rule": "history_fits",
    "rule_reason": "token pressure 0.46 < 0.90: full recent history fits, window is lossless",
    "dwell": [],
    "escalations": [
     "escalation from t0007: 1 stale chunk(s) flagged -> hybrid so the superseding facts are retrievable next to the recent window"
    ]
   },
   "candidates": {
    "sliding_window": {
     "tokens": 300,
     "latency_ms": 0.53,
     "quality": {
      "kept": 8,
      "relevance": 0.351,
      "freshness": 0.753,
      "importance": 0.231,
      "state": 1.0,
      "composite": 0.584
     }
    },
    "summarization": {
     "tokens": 306,
     "latency_ms": 0.94,
     "quality": {
      "tier_emitted": "L1",
      "loss_score": 0.0,
      "loss_threshold_exceeded": false,
      "symbol_retention_rate": 1.0
     }
    },
    "rag": {
     "tokens": 426,
     "latency_ms": 916.06,
     "quality": {
      "granularity_tag": "turn",
      "retrieved": 8,
      "stale_flags": 2
     }
    }
   },
   "prompt": {
    "tokens": 400,
    "context": "[Retrieved memory]\n[turns: t0002]\nassistant: It is a FastAPI app. `billing/models.py` has `Invoice` and `LineItem` (SQLModel), `billing/api.py` exposes /invoices and /quotes, and `billing/pdf.py` renders invoices with WeasyPrint. Amounts are stored as integer cents in the database and converted at the API edge.\n[!] stale: superseded by turn:t0008 (nli, confidence 1.00) - prefer the newer chunk\n\n---\n\n[turns: t0001]\nuser: Give me an overview of the invoice service before we start.\n\n---\n\n[turns: t0003]\nuser: Add a helper that computes a line item's total including tax.\n\n---\n\n[turns: t0004]\nassistant: Added to `billing/pricing.py`:\n```python\nTAX_RATE = 0.08\n\ndef compute_line_total(qty, unit_price, tax_rate=TAX_RATE):\n    subtotal = qty * unit_price\n    return round(subtotal * (1 + tax_rate), 2)\n```\n[!] stale: superseded by turn:t0006 (nli, confidence 1.00) - prefer the newer chunk\n\n[Recent turns]\nuser: Write the function that emails an invoice PDF to the customer.\nassistant: Added to `billing/notify.py`:\n```python\ndef send_invoice_email(invoice_id, recipient):\n    pdf = render_invoice_pdf(invoice_id)\n    mailer.send(to=recipient, subject=f'Invoice {invoice_id}', attachment=pdf)\n```\nuser: test_invoice_total fails: expected 108.0 but got 107.99. What's wrong?\nassistant: The fixture builds unit prices from floats like 0.1 * 3. Build them with `Decimal('0.30')` in the fixture, or compare with `pytest.approx`, the helper itself rounds correctly.",
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
   "user": "Finance says the tax rate goes up to 9.5% from next month. Update it.",
   "assistant": "Updated `billing/pricing.py`:\n```python\nTAX_RATE = 0.095\n```\nOnly the constant changed; `compute_line_total` picks it up through its default argument.",
   "signal": {
    "turn_count": 11,
    "task_type": "debugging",
    "matched_pattern": "carry_over",
    "topic_similarity": 0.336,
    "shift": false,
    "recall_request": false,
    "tokens_used": 387,
    "budget": 700
   },
   "features": {
    "turn_count": 11,
    "token_budget_pressure": 0.5529,
    "task_type": "debugging",
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
     "reason": "token pressure 0.55 < 0.90: full recent history fits, window is lossless"
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
     "matched": true,
     "fired": false,
     "rule": "debugging",
     "strategy": "sliding_window",
     "hard": false,
     "reason": "task_type=debugging -> sliding window: latest edits and traces are local and recent"
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
    "latency_ms": 0.0688,
    "override": [],
    "full": "[history_fits] token pressure 0.55 < 0.90: full recent history fits, window is lossless | dwell: held hybrid (0 < 3 turns since last switch) | escalation from t0009 (contradiction_flagged) noted; no change for hybrid | features: turn=11, pressure=0.55, task=debugging, prior=hybrid, since_switch=0",
    "rule": "history_fits",
    "rule_reason": "token pressure 0.55 < 0.90: full recent history fits, window is lossless",
    "dwell": [
     "dwell: held hybrid (0 < 3 turns since last switch)"
    ],
    "escalations": [
     "escalation from t0009 (contradiction_flagged) noted; no change for hybrid"
    ]
   },
   "candidates": {
    "sliding_window": {
     "tokens": 365,
     "latency_ms": 0.51,
     "quality": {
      "kept": 10,
      "relevance": 0.197,
      "freshness": 0.698,
      "importance": 0.215,
      "state": 1.0,
      "composite": 0.527
     }
    },
    "summarization": {
     "tokens": 350,
     "latency_ms": 1.37,
     "quality": {
      "tier_emitted": "L1",
      "loss_score": 0.2667,
      "loss_threshold_exceeded": true,
      "symbol_retention_rate": 1.0
     }
    },
    "rag": {
     "tokens": 425,
     "latency_ms": 760.93,
     "quality": {
      "granularity_tag": "turn",
      "retrieved": 7,
      "stale_flags": 2
     }
    }
   },
   "prompt": {
    "tokens": 473,
    "context": "[Retrieved memory]\n[turns: t0003]\nuser: Add a helper that computes a line item's total including tax.\n\n---\n\n[turns: t0004]\nassistant: Added to `billing/pricing.py`:\n```python\nTAX_RATE = 0.08\n\ndef compute_line_total(qty, unit_price, tax_rate=TAX_RATE):\n    subtotal = qty * unit_price\n    return round(subtotal * (1 + tax_rate), 2)\n```\n[!] stale: superseded by turn:t0006 (nli, confidence 1.00) - prefer the newer chunk\n\n---\n\n[turns: t0006 | supersedes turn:t0004]\nassistant: Added to `billing/notify.py`:\n```python\ndef send_invoice_email(invoice_id, recipient):\n    pdf = render_invoice_pdf(invoice_id)\n    mailer.send(to=recipient, subject=f'Invoice {invoice_id}', attachment=pdf)\n```\n\n---\n\n[turns: t0002]\nassistant: It is a FastAPI app. `billing/models.py` has `Invoice` and `LineItem` (SQLModel), `billing/api.py` exposes /invoices and /quotes, and `billing/pdf.py` renders invoices with WeasyPrint. Amounts are stored as integer cents in the database and converted at the API edge.\n[!] stale: superseded by turn:t0008 (nli, confidence 1.00) - prefer the newer chunk\n\n[Recent turns]\nuser: Give me an overview of the invoice service before we start.\nuser: Write the function that emails an invoice PDF to the customer.\nuser: test_invoice_total fails: expected 108.0 but got 107.99. What's wrong?\nassistant: The fixture builds unit prices from floats like 0.1 * 3. Build them with `Decimal('0.30')` in the fixture, or compare with `pytest.approx`, the helper itself rounds correctly.\nuser: Used pytest.approx, green now. The /invoices list endpoint is slow though.\nassistant: It lazily loads line items per invoice, an N+1 pattern. Add `selectinload(Invoice.line_items)` to the query in `list_invoices` and the 200 queries collapse into 2.",
    "truncated": false
   },
   "raised": [
    {
     "kind": "loss_threshold_exceeded",
     "source_module": "summarization",
     "detail": {
      "loss_score": 0.2667,
      "tier_emitted": "L1",
      "symbol_retention_rate": 1.0
     }
    }
   ],
   "traps": []
  },
  {
   "exchange": 7,
   "turn_id": "t0013",
   "user": "Emails should go through the background queue instead of being sent inline. Rename the email function accordingly.",
   "assistant": "Replaced it in `billing/notify.py`:\n```python\ndef enqueue_invoice_email(invoice_id, recipient):\n    queue.enqueue('emails', {'invoice_id': invoice_id, 'to': recipient})\n```\nThe worker in `workers/email.py` now renders and sends. Both callers were updated.",
   "signal": {
    "turn_count": 13,
    "task_type": "code_refactor",
    "matched_pattern": "pattern:code_refactor",
    "topic_similarity": 0.256,
    "shift": false,
    "recall_request": false,
    "tokens_used": 450,
    "budget": 700
   },
   "features": {
    "turn_count": 13,
    "token_budget_pressure": 0.6429,
    "task_type": "code_refactor",
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
     "reason": "token pressure 0.64 < 0.90: full recent history fits, window is lossless"
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
    "strategy": "hybrid",
    "latency_ms": 0.0747,
    "override": [],
    "full": "[history_fits] token pressure 0.64 < 0.90: full recent history fits, window is lossless | dwell: held hybrid (1 < 3 turns since last switch) | escalation from t0011 (loss_threshold_exceeded) noted; no change for hybrid | features: turn=13, pressure=0.64, task=code_refactor, prior=hybrid, since_switch=1",
    "rule": "history_fits",
    "rule_reason": "token pressure 0.64 < 0.90: full recent history fits, window is lossless",
    "dwell": [
     "dwell: held hybrid (1 < 3 turns since last switch)"
    ],
    "escalations": [
     "escalation from t0011 (loss_threshold_exceeded) noted; no change for hybrid"
    ]
   },
   "candidates": {
    "sliding_window": {
     "tokens": 429,
     "latency_ms": 0.49,
     "quality": {
      "kept": 12,
      "relevance": 0.134,
      "freshness": 0.649,
      "importance": 0.221,
      "state": 1.0,
      "composite": 0.501
     }
    },
    "summarization": {
     "tokens": 414,
     "latency_ms": 1.67,
     "quality": {
      "tier_emitted": "L1",
      "loss_score": 0.2667,
      "loss_threshold_exceeded": true,
      "symbol_retention_rate": 1.0
     }
    },
    "rag": {
     "tokens": 138,
     "latency_ms": 609.42,
     "quality": {
      "granularity_tag": "turn",
      "retrieved": 3,
      "stale_flags": 0
     }
    }
   },
   "prompt": {
    "tokens": 457,
    "context": "[Retrieved memory]\n[turns: t0006]\nassistant: Added to `billing/notify.py`:\n```python\ndef send_invoice_email(invoice_id, recipient):\n    pdf = render_invoice_pdf(invoice_id)\n    mailer.send(to=recipient, subject=f'Invoice {invoice_id}', attachment=pdf)\n```\n\n---\n\n[turns: t0005]\nuser: Write the function that emails an invoice PDF to the customer.\n\n[Recent turns]\nuser: Give me an overview of the invoice service before we start.\nassistant: It is a FastAPI app. `billing/models.py` has `Invoice` and `LineItem` (SQLModel), `billing/api.py` exposes /invoices and /quotes, and `billing/pdf.py` renders invoices with WeasyPrint. Amounts are stored as integer cents in the database and converted at the API edge.\nuser: Add a helper that computes a line item's total including tax.\nassistant: Added to `billing/pricing.py`:\n```python\nTAX_RATE = 0.08\n\ndef compute_line_total(qty, unit_price, tax_rate=TAX_RATE):\n    subtotal = qty * unit_price\n    return round(subtotal * (1 + tax_rate), 2)\n```\nuser: test_invoice_total fails: expected 108.0 but got 107.99. What's wrong?\nassistant: The fixture builds unit prices from floats like 0.1 * 3. Build them with `Decimal('0.30')` in the fixture, or compare with `pytest.approx`, the helper itself rounds correctly.\nuser: Used pytest.approx, green now. The /invoices list endpoint is slow though.\nassistant: It lazily loads line items per invoice, an N+1 pattern. Add `selectinload(Invoice.line_items)` to the query in `list_invoices` and the 200 queries collapse into 2.\nuser: Finance says the tax rate goes up to 9.5% from next month. Update it.\nassistant: Updated `billing/pricing.py`:\n```python\nTAX_RATE = 0.095\n```\nOnly the constant changed; `compute_line_total` picks it up through its default argument.",
    "truncated": false
   },
   "raised": [
    {
     "kind": "loss_threshold_exceeded",
     "source_module": "summarization",
     "detail": {
      "loss_score": 0.2667,
      "tier_emitted": "L1",
      "symbol_retention_rate": 1.0
     }
    }
   ],
   "traps": []
  },
  {
   "exchange": 8,
   "turn_id": "t0015",
   "user": "Let's add database migrations properly. We have been creating tables by hand.",
   "assistant": "Initialised Alembic with `alembic init migrations`, pointed `env.py` at `SQLModel.metadata`, and autogenerated a baseline revision. `make migrate` runs `alembic upgrade head`; CI runs it against a throwaway Postgres container before the test step.",
   "signal": {
    "turn_count": 15,
    "task_type": "chat",
    "matched_pattern": "shift_default",
    "topic_similarity": 0.093,
    "shift": true,
    "recall_request": false,
    "tokens_used": 531,
    "budget": 700
   },
   "features": {
    "turn_count": 15,
    "token_budget_pressure": 0.7586,
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
     "reason": "token pressure 0.76 < 0.90: full recent history fits, window is lossless"
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
    "latency_ms": 0.0854,
    "override": [],
    "full": "[history_fits] token pressure 0.76 < 0.90: full recent history fits, window is lossless | dwell: held hybrid (2 < 3 turns since last switch) | escalation from t0013 (loss_threshold_exceeded) noted; no change for hybrid | features: turn=15, pressure=0.76, task=chat, prior=hybrid, since_switch=2",
    "rule": "history_fits",
    "rule_reason": "token pressure 0.76 < 0.90: full recent history fits, window is lossless",
    "dwell": [
     "dwell: held hybrid (2 < 3 turns since last switch)"
    ],
    "escalations": [
     "escalation from t0013 (loss_threshold_exceeded) noted; no change for hybrid"
    ]
   },
   "candidates": {
    "sliding_window": {
     "tokens": 514,
     "latency_ms": 0.47,
     "quality": {
      "kept": 14,
      "relevance": 0.037,
      "freshness": 0.605,
      "importance": 0.232,
      "state": 0.5,
      "composite": 0.344
     }
    },
    "summarization": {
     "tokens": 515,
     "latency_ms": 2.01,
     "quality": {
      "tier_emitted": "L1",
      "loss_score": 0.2667,
      "loss_threshold_exceeded": true,
      "symbol_retention_rate": 1.0
     }
    },
    "rag": {
     "tokens": 0,
     "latency_ms": 488.42,
     "quality": {
      "granularity_tag": "turn",
      "retrieved": 0,
      "stale_flags": 0
     }
    }
   },
   "prompt": {
    "tokens": 520,
    "context": "[Recent turns]\nuser: Give me an overview of the invoice service before we start.\nassistant: It is a FastAPI app. `billing/models.py` has `Invoice` and `LineItem` (SQLModel), `billing/api.py` exposes /invoices and /quotes, and `billing/pdf.py` renders invoices with WeasyPrint. Amounts are stored as integer cents in the database and converted at the API edge.\nuser: Add a helper that computes a line item's total including tax.\nassistant: Added to `billing/pricing.py`:\n```python\nTAX_RATE = 0.08\n\ndef compute_line_total(qty, unit_price, tax_rate=TAX_RATE):\n    subtotal = qty * unit_price\n    return round(subtotal * (1 + tax_rate), 2)\n```\nuser: Write the function that emails an invoice PDF to the customer.\nassistant: Added to `billing/notify.py`:\n```python\ndef send_invoice_email(invoice_id, recipient):\n    pdf = render_invoice_pdf(invoice_id)\n    mailer.send(to=recipient, subject=f'Invoice {invoice_id}', attachment=pdf)\n```\nuser: test_invoice_total fails: expected 108.0 but got 107.99. What's wrong?\nassistant: The fixture builds unit prices from floats like 0.1 * 3. Build them with `Decimal('0.30')` in the fixture, or compare with `pytest.approx`, the helper itself rounds correctly.\nuser: Used pytest.approx, green now. The /invoices list endpoint is slow though.\nassistant: It lazily loads line items per invoice, an N+1 pattern. Add `selectinload(Invoice.line_items)` to the query in `list_invoices` and the 200 queries collapse into 2.\nuser: Finance says the tax rate goes up to 9.5% from next month. Update it.\nassistant: Updated `billing/pricing.py`:\n```python\nTAX_RATE = 0.095\n```\nOnly the constant changed; `compute_line_total` picks it up through its default argument.\nuser: Emails should go through the background queue instead of being sent inline. Rename the email function accordingly.\nassistant: Replaced it in `billing/notify.py`:\n```python\ndef enqueue_invoice_email(invoice_id, recipient):\n    queue.enqueue('emails', {'invoice_id': invoice_id, 'to': recipient})\n```\nThe worker in `workers/email.py` now renders and sends. Both callers were updated.",
    "truncated": false
   },
   "raised": [
    {
     "kind": "loss_threshold_exceeded",
     "source_module": "summarization",
     "detail": {
      "loss_score": 0.2667,
      "tier_emitted": "L1",
      "symbol_retention_rate": 1.0
     }
    }
   ],
   "traps": []
  },
  {
   "exchange": 9,
   "turn_id": "t0017",
   "user": "Paginate the /invoices endpoint, some customers have thousands.",
   "assistant": "Switched to keyset pagination on (issued_at, id): the endpoint takes `after` and `limit` (default 50, max 200) and returns `next_cursor`. Offset pagination would get slower with every page on large accounts.",
   "signal": {
    "turn_count": 17,
    "task_type": "chat",
    "matched_pattern": "shift_default",
    "topic_similarity": 0.11,
    "shift": true,
    "recall_request": false,
    "tokens_used": 604,
    "budget": 700
   },
   "features": {
    "turn_count": 17,
    "token_budget_pressure": 0.8629,
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
     "reason": "token pressure 0.86 < 0.90: full recent history fits, window is lossless"
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
    "latency_ms": 0.0728,
    "override": [],
    "full": "[history_fits] token pressure 0.86 < 0.90: full recent history fits, window is lossless | escalation from t0015 (loss_threshold_exceeded) noted; no change for sliding_window | features: turn=17, pressure=0.86, task=chat, prior=hybrid, since_switch=3",
    "rule": "history_fits",
    "rule_reason": "token pressure 0.86 < 0.90: full recent history fits, window is lossless",
    "dwell": [],
    "escalations": [
     "escalation from t0015 (loss_threshold_exceeded) noted; no change for sliding_window"
    ]
   },
   "candidates": {
    "sliding_window": {
     "tokens": 590,
     "latency_ms": 0.45,
     "quality": {
      "kept": 16,
      "relevance": 0.282,
      "freshness": 0.565,
      "importance": 0.209,
      "state": 0.281,
      "composite": 0.335
     }
    },
    "summarization": {
     "tokens": 604,
     "latency_ms": 2.63,
     "quality": {
      "tier_emitted": "L1",
      "loss_score": 0.125,
      "loss_threshold_exceeded": false,
      "symbol_retention_rate": 1.0
     }
    },
    "rag": {
     "tokens": 617,
     "latency_ms": 456.36,
     "quality": {
      "granularity_tag": "turn",
      "retrieved": 11,
      "stale_flags": 3
     }
    }
   },
   "prompt": {
    "tokens": 592,
    "context": "user: Give me an overview of the invoice service before we start.\nassistant: It is a FastAPI app. `billing/models.py` has `Invoice` and `LineItem` (SQLModel), `billing/api.py` exposes /invoices and /quotes, and `billing/pdf.py` renders invoices with WeasyPrint. Amounts are stored as integer cents in the database and converted at the API edge.\nuser: Add a helper that computes a line item's total including tax.\nassistant: Added to `billing/pricing.py`:\n```python\nTAX_RATE = 0.08\n\ndef compute_line_total(qty, unit_price, tax_rate=TAX_RATE):\n    subtotal = qty * unit_price\n    return round(subtotal * (1 + tax_rate), 2)\n```\nuser: Write the function that emails an invoice PDF to the customer.\nassistant: Added to `billing/notify.py`:\n```python\ndef send_invoice_email(invoice_id, recipient):\n    pdf = render_invoice_pdf(invoice_id)\n    mailer.send(to=recipient, subject=f'Invoice {invoice_id}', attachment=pdf)\n```\nuser: test_invoice_total fails: expected 108.0 but got 107.99. What's wrong?\nassistant: The fixture builds unit prices from floats like 0.1 * 3. Build them with `Decimal('0.30')` in the fixture, or compare with `pytest.approx`, the helper itself rounds correctly.\nuser: Used pytest.approx, green now. The /invoices list endpoint is slow though.\nassistant: It lazily loads line items per invoice, an N+1 pattern. Add `selectinload(Invoice.line_items)` to the query in `list_invoices` and the 200 queries collapse into 2.\nuser: Finance says the tax rate goes up to 9.5% from next month. Update it.\nassistant: Updated `billing/pricing.py`:\n```python\nTAX_RATE = 0.095\n```\nOnly the constant changed; `compute_line_total` picks it up through its default argument.\nuser: Emails should go through the background queue instead of being sent inline. Rename the email function accordingly.\nassistant: Replaced it in `billing/notify.py`:\n```python\ndef enqueue_invoice_email(invoice_id, recipient):\n    queue.enqueue('emails', {'invoice_id': invoice_id, 'to': recipient})\n```\nThe worker in `workers/email.py` now renders and sends. Both callers were updated.\nuser: Let's add database migrations properly. We have been creating tables by hand.\nassistant: Initialised Alembic with `alembic init migrations`, pointed `env.py` at `SQLModel.metadata`, and autogenerated a baseline revision. `make migrate` runs `alembic upgrade head`; CI runs it against a throwaway Postgres container before the test step.",
    "truncated": false
   },
   "raised": [
    {
     "kind": "contradiction_flagged",
     "source_module": "rag",
     "detail": {
      "n_flags": 2
     }
    }
   ],
   "traps": []
  },
  {
   "exchange": 10,
   "turn_id": "t0019",
   "user": "Add rate limiting to the public quote endpoint.",
   "assistant": "Added slowapi with a Redis storage backend: 30 requests per minute per API key on /quotes, 429 with a Retry-After header beyond that. Internal service tokens are exempt through a key function.",
   "signal": {
    "turn_count": 19,
    "task_type": "code_generation",
    "matched_pattern": "pattern:code_generation",
    "topic_similarity": 0.368,
    "shift": false,
    "recall_request": false,
    "tokens_used": 667,
    "budget": 700
   },
   "features": {
    "turn_count": 19,
    "token_budget_pressure": 0.9529,
    "task_type": "code_generation",
    "prior_strategy": "sliding_window",
    "time_since_last_switch": 0
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
    "latency_ms": 0.0656,
    "override": [],
    "full": "[build_request] task_type=code_generation (build-request pattern) -> hybrid: recent window + RAG to surface existing definitions before writing new code | escalation from t0017 (contradiction_flagged) noted; no change for hybrid | features: turn=19, pressure=0.95, task=code_generation, prior=sliding_window, since_switch=0",
    "rule": "build_request",
    "rule_reason": "task_type=code_generation (build-request pattern) -> hybrid: recent window + RAG to surface existing definitions before writing new code",
    "dwell": [],
    "escalations": [
     "escalation from t0017 (contradiction_flagged) noted; no change for hybrid"
    ]
   },
   "candidates": {
    "sliding_window": {
     "tokens": 613,
     "latency_ms": 0.44,
     "quality": {
      "kept": 15,
      "relevance": 0.194,
      "freshness": 0.579,
      "importance": 0.237,
      "state": 0.383,
      "composite": 0.348
     }
    },
    "summarization": {
     "tokens": 670,
     "latency_ms": 2.9,
     "quality": {
      "tier_emitted": "L1",
      "loss_score": 0.125,
      "loss_threshold_exceeded": false,
      "symbol_retention_rate": 1.0
     }
    },
    "rag": {
     "tokens": 590,
     "latency_ms": 366.03,
     "quality": {
      "granularity_tag": "turn",
      "retrieved": 11,
      "stale_flags": 2
     }
    }
   },
   "prompt": {
    "tokens": 666,
    "context": "[Retrieved memory]\n[turns: t0011 t0012]\nuser: Finance says the tax rate goes up to 9.5% from next month. Update it.\nassistant: Updated `billing/pricing.py`:\n```python\nTAX_RATE = 0.095\n```\nOnly the constant changed; `compute_line_total` picks it up through its default argument.\n\n---\n\n[turns: t0002]\nassistant: It is a FastAPI app. `billing/models.py` has `Invoice` and `LineItem` (SQLModel), `billing/api.py` exposes /invoices and /quotes, and `billing/pdf.py` renders invoices with WeasyPrint. Amounts are stored as integer cents in the database and converted at the API edge.\n[!] stale: superseded by turn:t0008 (nli, confidence 1.00) - prefer the newer chunk\n\n---\n\n[turns: t0008 | supersedes turn:t0002]\nassistant: The fixture builds unit prices from floats like 0.1 * 3. Build them with `Decimal('0.30')` in the fixture, or compare with `pytest.approx`, the helper itself rounds correctly.\n\n---\n\n[turns: t0009]\nuser: Used pytest.approx, green now. The /invoices list endpoint is slow though.\n\n---\n\n[turns: t0003]\nuser: Add a helper that computes a line item's total including tax.\n\n---\n\n[turns: t0007]\nuser: test_invoice_total fails: expected 108.0 but got 107.99. What's wrong?\n\n[Recent turns]\nassistant: Added to `billing/notify.py`:\n```python\ndef send_invoice_email(invoice_id, recipient):\n    pdf = render_invoice_pdf(invoice_id)\n    mailer.send(to=recipient, subject=f'Invoice {invoice_id}', attachment=pdf)\n```\nassistant: It lazily loads line items per invoice, an N+1 pattern. Add `selectinload(Invoice.line_items)` to the query in `list_invoices` and the 200 queries collapse into 2.\nuser: Emails should go through the background queue instead of being sent inline. Rename the email function accordingly.\nassistant: Replaced it in `billing/notify.py`:\n```python\ndef enqueue_invoice_email(invoice_id, recipient):\n    queue.enqueue('emails', {'invoice_id': invoice_id, 'to': recipient})\n```\nThe worker in `workers/email.py` now renders and sends. Both callers were updated.\nuser: Let's add database migrations properly. We have been creating tables by hand.\nassistant: Initialised Alembic with `alembic init migrations`, pointed `env.py` at `SQLModel.metadata`, and autogenerated a baseline revision. `make migrate` runs `alembic upgrade head`; CI runs it against a throwaway Postgres container before the test step.\nuser: Paginate the /invoices endpoint, some customers have thousands.\nassistant: Switched to keyset pagination on (issued_at, id): the endpoint takes `after` and `limit` (default 50, max 200) and returns `next_cursor`. Offset pagination would get slower with every page on large accounts.",
    "truncated": false
   },
   "raised": [],
   "traps": []
  },
  {
   "exchange": 11,
   "turn_id": "t0021",
   "user": "Clean up the OpenAPI docs, the schemas have ugly auto names.",
   "assistant": "Gave every response model an explicit `title`, grouped routes with tags (invoices, quotes, admin), and added examples to the request bodies. /docs now reads well and the generated TypeScript client has stable type names.",
   "signal": {
    "turn_count": 21,
    "task_type": "code_refactor",
    "matched_pattern": "pattern:code_refactor",
    "topic_similarity": 0.106,
    "shift": true,
    "recall_request": false,
    "tokens_used": 727,
    "budget": 700
   },
   "features": {
    "turn_count": 21,
    "token_budget_pressure": 1.0,
    "task_type": "code_refactor",
    "prior_strategy": "hybrid",
    "time_since_last_switch": 0
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
     "fired": true,
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
    "strategy": "summarization",
    "latency_ms": 0.078,
    "override": [],
    "full": "[refactor_request] task_type=code_refactor -> summarization: merged L1 symbol table carries current signatures and renames | features: turn=21, pressure=1.00, task=code_refactor, prior=hybrid, since_switch=0",
    "rule": "refactor_request",
    "rule_reason": "task_type=code_refactor -> summarization: merged L1 symbol table carries current signatures and renames",
    "dwell": [],
    "escalations": []
   },
   "candidates": {
    "sliding_window": {
     "tokens": 489,
     "latency_ms": 0.47,
     "quality": {
      "kept": 12,
      "relevance": 0.125,
      "freshness": 0.617,
      "importance": 0.254,
      "state": 0.271,
      "composite": 0.317
     }
    },
    "summarization": {
     "tokens": 688,
     "latency_ms": 3.45,
     "quality": {
      "tier_emitted": "L2",
      "loss_score": 0.2812,
      "loss_threshold_exceeded": true,
      "symbol_retention_rate": 1.0
     }
    },
    "rag": {
     "tokens": 376,
     "latency_ms": 294.07,
     "quality": {
      "granularity_tag": "turn",
      "retrieved": 6,
      "stale_flags": 1
     }
    }
   },
   "prompt": {
    "tokens": 688,
    "context": "[Memory summary | tier L2 | intent & decisions | 1 records]\nProfile (L3): a developer in an ongoing coding session\nObjective: Progress on Invoice, compute_line_total, pricing.py, LineItem\nCurrent state: open: Add a helper that computes a line item's total including tax.; open: Write the function that emails an invoice PDF to the customer.\n- Coding work focused on Invoice, compute_line_total, pricing.py, LineItem, WeasyPrint\n  open goals: Add a helper that computes a line item's total including tax.; Write the function that emails an invoice PDF to the customer.\nRecent facts (L1, newest first):\n- def enqueue_invoice_email(invoice_id, recipient) (t0014)\n- def send_invoice_email(invoice_id, recipient) (t0006)\n- def compute_line_total(qty, unit_price, tax_rate=TAX_RATE) (t0004)\n- Only the constant changed; `compute_line_total` picks it up through its default argument. (t0012)\n- Finance says the tax rate goes up to 9.5% from next month. (t0011)\n- Add `selectinload(Invoice.line_items)` to the query in `list_invoices` and the 200 queries collapse into 2. (t0010)\n- It lazily loads line items per invoice, an N+1 pattern. (t0010)\n- Used pytest.approx, green now. (t0009)\n- The /invoices list endpoint is slow though. (t0009)\n- Build them with `Decimal('0.30')` in the fixture, or compare with `pytest.approx`, the helper itself rounds correctly. (t0008)\n- The fixture builds unit prices from floats like 0.1 * 3. (t0008)\n- test_invoice_total fails: expected 108.0 but got 107.99. (t0007)\n\n[Recent turns]\nuser: Emails should go through the background queue instead of being sent inline. Rename the email function accordingly.\nassistant: Replaced it in `billing/notify.py`:\n```python\ndef enqueue_invoice_email(invoice_id, recipient):\n    queue.enqueue('emails', {'invoice_id': invoice_id, 'to': recipient})\n```\nThe worker in `workers/email.py` now renders and sends. Both callers were updated.\nuser: Let's add database migrations properly. We have been creating tables by hand.\nassistant: Initialised Alembic with `alembic init migrations`, pointed `env.py` at `SQLModel.metadata`, and autogenerated a baseline revision. `make migrate` runs `alembic upgrade head`; CI runs it against a throwaway Postgres container before the test step.\nuser: Paginate the /invoices endpoint, some customers have thousands.\nassistant: Switched to keyset pagination on (issued_at, id): the endpoint takes `after` and `limit` (default 50, max 200) and returns `next_cursor`. Offset pagination would get slower with every page on large accounts.\nuser: Add rate limiting to the public quote endpoint.\nassistant: Added slowapi with a Redis storage backend: 30 requests per minute per API key on /quotes, 429 with a Retry-After header beyond that. Internal service tokens are exempt through a key function.",
    "truncated": false
   },
   "raised": [
    {
     "kind": "loss_threshold_exceeded",
     "source_module": "summarization",
     "detail": {
      "loss_score": 0.2812,
      "tier_emitted": "L2",
      "symbol_retention_rate": 1.0
     }
    }
   ],
   "traps": []
  },
  {
   "exchange": 12,
   "turn_id": "t0023",
   "user": "Hook up Sentry for the API and the worker.",
   "assistant": "Added `sentry_sdk.init` in both entry points with the FastAPI and RQ integrations, environment from APP_ENV, traces_sample_rate 0.1 in production, and a before_send hook that strips customer emails.",
   "signal": {
    "turn_count": 23,
    "task_type": "chat",
    "matched_pattern": "shift_default",
    "topic_similarity": 0.111,
    "shift": true,
    "recall_request": false,
    "tokens_used": 785,
    "budget": 700
   },
   "features": {
    "turn_count": 23,
    "token_budget_pressure": 1.0,
    "task_type": "chat",
    "prior_strategy": "summarization",
    "time_since_last_switch": 0
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
     "matched": true,
     "fired": true,
     "rule": "long_open_conversation",
     "strategy": "summarization",
     "hard": false,
     "reason": "task_type=chat with token pressure 1.00 -> summarization keeps the gist of the long history"
    }
   ],
   "decision": {
    "strategy": "rag",
    "latency_ms": 0.0998,
    "override": [],
    "full": "[long_open_conversation] task_type=chat with token pressure 1.00 -> summarization keeps the gist of the long history | escalation from t0021: summary loss 0.2812 > 0.15 (tier L2) -> switch summarization to RAG | features: turn=23, pressure=1.00, task=chat, prior=summarization, since_switch=0",
    "rule": "long_open_conversation",
    "rule_reason": "task_type=chat with token pressure 1.00 -> summarization keeps the gist of the long history",
    "dwell": [],
    "escalations": [
     "escalation from t0021: summary loss 0.2812 > 0.15 (tier L2) -> switch summarization to RAG"
    ]
   },
   "candidates": {
    "sliding_window": {
     "tokens": 466,
     "latency_ms": 0.5,
     "quality": {
      "kept": 11,
      "relevance": 0.175,
      "freshness": 0.624,
      "importance": 0.255,
      "state": 0.216,
      "composite": 0.317
     }
    },
    "summarization": {
     "tokens": 681,
     "latency_ms": 4.19,
     "quality": {
      "tier_emitted": "L2",
      "loss_score": 0.3404,
      "loss_threshold_exceeded": true,
      "symbol_retention_rate": 1.0
     }
    },
    "rag": {
     "tokens": 565,
     "latency_ms": 294.18,
     "quality": {
      "granularity_tag": "turn",
      "retrieved": 11,
      "stale_flags": 2
     }
    }
   },
   "prompt": {
    "tokens": 565,
    "context": "[turns: t0014]\nassistant: Replaced it in `billing/notify.py`:\n```python\ndef enqueue_invoice_email(invoice_id, recipient):\n    queue.enqueue('emails', {'invoice_id': invoice_id, 'to': recipient})\n```\nThe worker in `workers/email.py` now renders and sends. Both callers were updated.\n\n---\n\n[turns: t0020]\nassistant: Added slowapi with a Redis storage backend: 30 requests per minute per API key on /quotes, 429 with a Retry-After header beyond that. Internal service tokens are exempt through a key function.\n\n---\n\n[turns: t0002]\nassistant: It is a FastAPI app. `billing/models.py` has `Invoice` and `LineItem` (SQLModel), `billing/api.py` exposes /invoices and /quotes, and `billing/pdf.py` renders invoices with WeasyPrint. Amounts are stored as integer cents in the database and converted at the API edge.\n[!] stale: superseded by turn:t0008 (nli, confidence 1.00) - prefer the newer chunk\n\n---\n\n[turns: t0008 | supersedes turn:t0002]\nassistant: The fixture builds unit prices from floats like 0.1 * 3. Build them with `Decimal('0.30')` in the fixture, or compare with `pytest.approx`, the helper itself rounds correctly.\n\n---\n\n[turns: t0013]\nuser: Emails should go through the background queue instead of being sent inline. Rename the email function accordingly.\n\n---\n\n[turns: t0006]\nassistant: Added to `billing/notify.py`:\n```python\ndef send_invoice_email(invoice_id, recipient):\n    pdf = render_invoice_pdf(invoice_id)\n    mailer.send(to=recipient, subject=f'Invoice {invoice_id}', attachment=pdf)\n```\n[!] stale: superseded by turn:t0014 (nli, confidence 1.00) - prefer the newer chunk\n\n---\n\n[turns: t0001]\nuser: Give me an overview of the invoice service before we start.\n\n---\n\n[turns: t0022]\nassistant: Gave every response model an explicit `title`, grouped routes with tags (invoices, quotes, admin), and added examples to the request bodies. /docs now reads well and the generated TypeScript client has stable type names.\n\n---\n\n[turns: t0005]\nuser: Write the function that emails an invoice PDF to the customer.\n\n---\n\n[turns: t0019]\nuser: Add rate limiting to the public quote endpoint.\n\n---\n\n[turns: t0009]\nuser: Used pytest.approx, green now. The /invoices list endpoint is slow though.",
    "truncated": false
   },
   "raised": [
    {
     "kind": "loss_threshold_exceeded",
     "source_module": "summarization",
     "detail": {
      "loss_score": 0.3404,
      "tier_emitted": "L2",
      "symbol_retention_rate": 1.0
     }
    }
   ],
   "traps": []
  },
  {
   "exchange": 13,
   "turn_id": "t0025",
   "user": "Our tests create objects by hand everywhere. Can we use factories?",
   "assistant": "Added factory_boy factories for Customer, Invoice and LineItem in `tests/factories.py`, with a session-scoped database fixture and per-test transactions rolled back at teardown.",
   "signal": {
    "turn_count": 25,
    "task_type": "chat",
    "matched_pattern": "carry_over",
    "topic_similarity": 0.151,
    "shift": false,
    "recall_request": false,
    "tokens_used": 848,
    "budget": 700
   },
   "features": {
    "turn_count": 25,
    "token_budget_pressure": 1.0,
    "task_type": "chat",
    "prior_strategy": "rag",
    "time_since_last_switch": 0
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
     "matched": true,
     "fired": true,
     "rule": "long_open_conversation",
     "strategy": "summarization",
     "hard": false,
     "reason": "task_type=chat with token pressure 1.00 -> summarization keeps the gist of the long history"
    }
   ],
   "decision": {
    "strategy": "rag",
    "latency_ms": 0.1087,
    "override": [],
    "full": "[long_open_conversation] task_type=chat with token pressure 1.00 -> summarization keeps the gist of the long history | dwell: held rag (0 < 3 turns since last switch) | escalation from t0023 (loss_threshold_exceeded) noted; no change for rag | features: turn=25, pressure=1.00, task=chat, prior=rag, since_switch=0",
    "rule": "long_open_conversation",
    "rule_reason": "task_type=chat with token pressure 1.00 -> summarization keeps the gist of the long history",
    "dwell": [
     "dwell: held rag (0 < 3 turns since last switch)"
    ],
    "escalations": [
     "escalation from t0023 (loss_threshold_exceeded) noted; no change for rag"
    ]
   },
   "candidates": {
    "sliding_window": {
     "tokens": 526,
     "latency_ms": 0.55,
     "quality": {
      "kept": 13,
      "relevance": 0.039,
      "freshness": 0.591,
      "importance": 0.235,
      "state": 0.337,
      "composite": 0.3
     }
    },
    "summarization": {
     "tokens": 671,
     "latency_ms": 4.43,
     "quality": {
      "tier_emitted": "L2",
      "loss_score": 0.4468,
      "loss_threshold_exceeded": true,
      "symbol_retention_rate": 1.0
     }
    },
    "rag": {
     "tokens": 20,
     "latency_ms": 240.7,
     "quality": {
      "granularity_tag": "turn",
      "retrieved": 1,
      "stale_flags": 0
     }
    }
   },
   "prompt": {
    "tokens": 20,
    "context": "[turns: t0023]\nuser: Hook up Sentry for the API and the worker.",
    "truncated": false
   },
   "raised": [
    {
     "kind": "loss_threshold_exceeded",
     "source_module": "summarization",
     "detail": {
      "loss_score": 0.4468,
      "tier_emitted": "L2",
      "symbol_retention_rate": 1.0
     }
    }
   ],
   "traps": []
  },
  {
   "exchange": 14,
   "turn_id": "t0027",
   "user": "For the quote endpoint, write a function that returns a line item's total with tax applied.",
   "assistant": "(scripted reply omitted - the check is on the context the model would receive)",
   "signal": {
    "turn_count": 27,
    "task_type": "code_generation",
    "matched_pattern": "pattern:code_generation",
    "topic_similarity": 0.08,
    "shift": true,
    "recall_request": false,
    "tokens_used": 906,
    "budget": 700
   },
   "features": {
    "turn_count": 27,
    "token_budget_pressure": 1.0,
    "task_type": "code_generation",
    "prior_strategy": "rag",
    "time_since_last_switch": 1
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
    "latency_ms": 0.0896,
    "override": [],
    "full": "[build_request] task_type=code_generation (build-request pattern) -> hybrid: recent window + RAG to surface existing definitions before writing new code | escalation from t0025 (loss_threshold_exceeded) noted; no change for hybrid | features: turn=27, pressure=1.00, task=code_generation, prior=rag, since_switch=1",
    "rule": "build_request",
    "rule_reason": "task_type=code_generation (build-request pattern) -> hybrid: recent window + RAG to surface existing definitions before writing new code",
    "dwell": [],
    "escalations": [
     "escalation from t0025 (loss_threshold_exceeded) noted; no change for hybrid"
    ]
   },
   "candidates": {
    "sliding_window": {
     "tokens": 580,
     "latency_ms": 0.52,
     "quality": {
      "kept": 16,
      "relevance": 0.243,
      "freshness": 0.522,
      "importance": 0.209,
      "state": 0.199,
      "composite": 0.293
     }
    },
    "summarization": {
     "tokens": 676,
     "latency_ms": 4.52,
     "quality": {
      "tier_emitted": "L2",
      "loss_score": 0.4894,
      "loss_threshold_exceeded": true,
      "symbol_retention_rate": 1.0
     }
    },
    "rag": {
     "tokens": 661,
     "latency_ms": 193.63,
     "quality": {
      "granularity_tag": "turn",
      "retrieved": 13,
      "stale_flags": 3
     }
    }
   },
   "prompt": {
    "tokens": 625,
    "context": "[Retrieved memory]\n[turns: t0003]\nuser: Add a helper that computes a line item's total including tax.\n\n---\n\n[turns: t0004]\nassistant: Added to `billing/pricing.py`:\n```python\nTAX_RATE = 0.08\n\ndef compute_line_total(qty, unit_price, tax_rate=TAX_RATE):\n    subtotal = qty * unit_price\n    return round(subtotal * (1 + tax_rate), 2)\n```\n[!] stale: superseded by turn:t0012 (nli, confidence 0.98) - prefer the newer chunk\n\n---\n\n[turns: t0011 t0012 | supersedes turn:t0004]\nuser: Finance says the tax rate goes up to 9.5% from next month. Update it.\nassistant: Updated `billing/pricing.py`:\n```python\nTAX_RATE = 0.095\n```\nOnly the constant changed; `compute_line_total` picks it up through its default argument.\n\n---\n\n[turns: t0019]\nuser: Add rate limiting to the public quote endpoint.\n\n---\n\n[turns: t0002]\nassistant: It is a FastAPI app. `billing/models.py` has `Invoice` and `LineItem` (SQLModel), `billing/api.py` exposes /invoices and /quotes, and `billing/pdf.py` renders invoices with WeasyPrint. Amounts are stored as integer cents in the database and converted at the API edge.\n[!] stale: superseded by turn:t0008 (nli, confidence 1.00) - prefer the newer chunk\n\n[Recent turns]\nuser: Paginate the /invoices endpoint, some customers have thousands.\nassistant: Switched to keyset pagination on (issued_at, id): the endpoint takes `after` and `limit` (default 50, max 200) and returns `next_cursor`. Offset pagination would get slower with every page on large accounts.\nassistant: Added slowapi with a Redis storage backend: 30 requests per minute per API key on /quotes, 429 with a Retry-After header beyond that. Internal service tokens are exempt through a key function.\nuser: Clean up the OpenAPI docs, the schemas have ugly auto names.\nassistant: Gave every response model an explicit `title`, grouped routes with tags (invoices, quotes, admin), and added examples to the request bodies. /docs now reads well and the generated TypeScript client has stable type names.\nuser: Hook up Sentry for the API and the worker.\nassistant: Added `sentry_sdk.init` in both entry points with the FastAPI and RQ integrations, environment from APP_ENV, traces_sample_rate 0.1 in production, and a before_send hook that strips customer emails.\nuser: Our tests create objects by hand everywhere. Can we use factories?\nassistant: Added factory_boy factories for Customer, Invoice and LineItem in `tests/factories.py`, with a session-scoped database fixture and per-test transactions rolled back at teardown.",
    "truncated": false
   },
   "raised": [
    {
     "kind": "loss_threshold_exceeded",
     "source_module": "summarization",
     "detail": {
      "loss_score": 0.4894,
      "tier_emitted": "L2",
      "symbol_retention_rate": 1.0
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
     "name": "duplicate helper",
     "description": "the line-total helper exists since exchange 2",
     "planted_at": 2,
     "kind": "duplicate",
     "adaptive": {
      "caught": true,
      "detail": "found `def compute_line_total(`",
      "strategy": "hybrid"
     },
     "fixed_6_exchange_window": {
      "caught": false,
      "detail": "missing `def compute_line_total(`"
     },
     "sliding_window": {
      "caught": true,
      "detail": "found `def compute_line_total(`"
     },
     "summarization": {
      "caught": true,
      "detail": "found `def compute_line_total(`"
     },
     "rag": {
      "caught": true,
      "detail": "found `def compute_line_total(`"
     },
     "hybrid": {
      "caught": true,
      "detail": "found `def compute_line_total(`"
     }
    }
   ]
  },
  {
   "exchange": 15,
   "turn_id": "t0029",
   "user": "What tax rate does the quote preview apply? Show me the constant it uses.",
   "assistant": "(scripted reply omitted - the check is on the context the model would receive)",
   "signal": {
    "turn_count": 29,
    "task_type": "code_generation",
    "matched_pattern": "carry_over",
    "topic_similarity": 0.562,
    "shift": false,
    "recall_request": false,
    "tokens_used": 943,
    "budget": 700
   },
   "features": {
    "turn_count": 29,
    "token_budget_pressure": 1.0,
    "task_type": "code_generation",
    "prior_strategy": "hybrid",
    "time_since_last_switch": 0
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
    "latency_ms": 0.0622,
    "override": [],
    "full": "[build_request] task_type=code_generation (build-request pattern) -> hybrid: recent window + RAG to surface existing definitions before writing new code | escalation from t0027 (loss_threshold_exceeded) noted; no change for hybrid | escalation from t0027 (contradiction_flagged) noted; no change for hybrid | features: turn=29, pressure=1.00, task=code_generation, prior=hybrid, since_switch=0",
    "rule": "build_request",
    "rule_reason": "task_type=code_generation (build-request pattern) -> hybrid: recent window + RAG to surface existing definitions before writing new code",
    "dwell": [],
    "escalations": [
     "escalation from t0027 (loss_threshold_exceeded) noted; no change for hybrid",
     "escalation from t0027 (contradiction_flagged) noted; no change for hybrid"
    ]
   },
   "candidates": {
    "sliding_window": {
     "tokens": 567,
     "latency_ms": 0.49,
     "quality": {
      "kept": 16,
      "relevance": 0.219,
      "freshness": 0.528,
      "importance": 0.2,
      "state": 0.315,
      "composite": 0.315
     }
    },
    "summarization": {
     "tokens": 676,
     "latency_ms": 5.06,
     "quality": {
      "tier_emitted": "L2",
      "loss_score": 0.4167,
      "loss_threshold_exceeded": true,
      "symbol_retention_rate": 1.0
     }
    },
    "rag": {
     "tokens": 673,
     "latency_ms": 156.45,
     "quality": {
      "granularity_tag": "turn",
      "retrieved": 13,
      "stale_flags": 3
     }
    }
   },
   "prompt": {
    "tokens": 643,
    "context": "[Retrieved memory]\n[turns: t0011 t0012]\nuser: Finance says the tax rate goes up to 9.5% from next month. Update it.\nassistant: Updated `billing/pricing.py`:\n```python\nTAX_RATE = 0.095\n```\nOnly the constant changed; `compute_line_total` picks it up through its default argument.\n\n---\n\n[turns: t0019]\nuser: Add rate limiting to the public quote endpoint.\n\n---\n\n[turns: t0004]\nassistant: Added to `billing/pricing.py`:\n```python\nTAX_RATE = 0.08\n\ndef compute_line_total(qty, unit_price, tax_rate=TAX_RATE):\n    subtotal = qty * unit_price\n    return round(subtotal * (1 + tax_rate), 2)\n```\n[!] stale: superseded by turn:t0012 (nli, confidence 0.98) - prefer the newer chunk\n\n---\n\n[turns: t0003]\nuser: Add a helper that computes a line item's total including tax.\n\n---\n\n[turns: t0002]\nassistant: It is a FastAPI app. `billing/models.py` has `Invoice` and `LineItem` (SQLModel), `billing/api.py` exposes /invoices and /quotes, and `billing/pdf.py` renders invoices with WeasyPrint. Amounts are stored as integer cents in the database and converted at the API edge.\n[!] stale: superseded by turn:t0008 (nli, confidence 1.00) - prefer the newer chunk\n\n[Recent turns]\nassistant: Switched to keyset pagination on (issued_at, id): the endpoint takes `after` and `limit` (default 50, max 200) and returns `next_cursor`. Offset pagination would get slower with every page on large accounts.\nassistant: Added slowapi with a Redis storage backend: 30 requests per minute per API key on /quotes, 429 with a Retry-After header beyond that. Internal service tokens are exempt through a key function.\nuser: Clean up the OpenAPI docs, the schemas have ugly auto names.\nassistant: Gave every response model an explicit `title`, grouped routes with tags (invoices, quotes, admin), and added examples to the request bodies. /docs now reads well and the generated TypeScript client has stable type names.\nuser: Hook up Sentry for the API and the worker.\nassistant: Added `sentry_sdk.init` in both entry points with the FastAPI and RQ integrations, environment from APP_ENV, traces_sample_rate 0.1 in production, and a before_send hook that strips customer emails.\nuser: Our tests create objects by hand everywhere. Can we use factories?\nassistant: Added factory_boy factories for Customer, Invoice and LineItem in `tests/factories.py`, with a session-scoped database fixture and per-test transactions rolled back at teardown.\nuser: For the quote endpoint, write a function that returns a line item's total with tax applied.\nassistant: (scripted reply omitted - the check is on the context the model would receive)",
    "truncated": false
   },
   "raised": [
    {
     "kind": "loss_threshold_exceeded",
     "source_module": "summarization",
     "detail": {
      "loss_score": 0.4167,
      "tier_emitted": "L2",
      "symbol_retention_rate": 1.0
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
     "name": "changed tax constant",
     "description": "TAX_RATE changed 0.08 -> 0.095 at exchange 6",
     "planted_at": 6,
     "kind": "config",
     "adaptive": {
      "caught": true,
      "detail": "found `TAX_RATE = 0.095`",
      "strategy": "hybrid"
     },
     "fixed_6_exchange_window": {
      "caught": false,
      "detail": "missing `TAX_RATE = 0.095`"
     },
     "sliding_window": {
      "caught": false,
      "detail": "unmarked stale `TAX_RATE = 0.08` present"
     },
     "summarization": {
      "caught": false,
      "detail": "missing `TAX_RATE = 0.095`"
     },
     "rag": {
      "caught": true,
      "detail": "found `TAX_RATE = 0.095`"
     },
     "hybrid": {
      "caught": true,
      "detail": "found `TAX_RATE = 0.095`"
     }
    }
   ]
  },
  {
   "exchange": 16,
   "turn_id": "t0031",
   "user": "Quotes should show the currency symbol from the customer's locale.",
   "assistant": "Use Babel's `format_currency(amount, currency, locale=customer.locale)`; fall back to en_US.",
   "signal": {
    "turn_count": 31,
    "task_type": "code_generation",
    "matched_pattern": "carry_over",
    "topic_similarity": 0.379,
    "shift": false,
    "recall_request": false,
    "tokens_used": 976,
    "budget": 700
   },
   "features": {
    "turn_count": 31,
    "token_budget_pressure": 1.0,
    "task_type": "code_generation",
    "prior_strategy": "hybrid",
    "time_since_last_switch": 1
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
    "latency_ms": 0.0641,
    "override": [],
    "full": "[build_request] task_type=code_generation (build-request pattern) -> hybrid: recent window + RAG to surface existing definitions before writing new code | escalation from t0029 (loss_threshold_exceeded) noted; no change for hybrid | escalation from t0029 (contradiction_flagged) noted; no change for hybrid | features: turn=31, pressure=1.00, task=code_generation, prior=hybrid, since_switch=1",
    "rule": "build_request",
    "rule_reason": "task_type=code_generation (build-request pattern) -> hybrid: recent window + RAG to surface existing definitions before writing new code",
    "dwell": [],
    "escalations": [
     "escalation from t0029 (loss_threshold_exceeded) noted; no change for hybrid",
     "escalation from t0029 (contradiction_flagged) noted; no change for hybrid"
    ]
   },
   "candidates": {
    "sliding_window": {
     "tokens": 486,
     "latency_ms": 0.46,
     "quality": {
      "kept": 15,
      "relevance": 0.185,
      "freshness": 0.537,
      "importance": 0.187,
      "state": 0.45,
      "composite": 0.34
     }
    },
    "summarization": {
     "tokens": 680,
     "latency_ms": 5.1,
     "quality": {
      "tier_emitted": "L2",
      "loss_score": 0.4667,
      "loss_threshold_exceeded": true,
      "symbol_retention_rate": 1.0
     }
    },
    "rag": {
     "tokens": 681,
     "latency_ms": 126.27,
     "quality": {
      "granularity_tag": "turn",
      "retrieved": 14,
      "stale_flags": 3
     }
    }
   },
   "prompt": {
    "tokens": 677,
    "context": "[Retrieved memory]\n[turns: t0002]\nassistant: It is a FastAPI app. `billing/models.py` has `Invoice` and `LineItem` (SQLModel), `billing/api.py` exposes /invoices and /quotes, and `billing/pdf.py` renders invoices with WeasyPrint. Amounts are stored as integer cents in the database and converted at the API edge.\n[!] stale: superseded by turn:t0008 (nli, confidence 1.00) - prefer the newer chunk\n\n---\n\n[turns: t0008 | supersedes turn:t0002]\nassistant: The fixture builds unit prices from floats like 0.1 * 3. Build them with `Decimal('0.30')` in the fixture, or compare with `pytest.approx`, the helper itself rounds correctly.\n\n---\n\n[turns: t0019]\nuser: Add rate limiting to the public quote endpoint.\n\n---\n\n[turns: t0004]\nassistant: Added to `billing/pricing.py`:\n```python\nTAX_RATE = 0.08\n\ndef compute_line_total(qty, unit_price, tax_rate=TAX_RATE):\n    subtotal = qty * unit_price\n    return round(subtotal * (1 + tax_rate), 2)\n```\n[!] stale: superseded by turn:t0012 (nli, confidence 0.98) - prefer the newer chunk\n\n---\n\n[turns: t0005]\nuser: Write the function that emails an invoice PDF to the customer.\n\n[Recent turns]\nassistant: Updated `billing/pricing.py`:\n```python\nTAX_RATE = 0.095\n```\nOnly the constant changed; `compute_line_total` picks it up through its default argument.\nassistant: Replaced it in `billing/notify.py`:\n```python\ndef enqueue_invoice_email(invoice_id, recipient):\n    queue.enqueue('emails', {'invoice_id': invoice_id, 'to': recipient})\n```\nThe worker in `workers/email.py` now renders and sends. Both callers were updated.\nuser: Clean up the OpenAPI docs, the schemas have ugly auto names.\nassistant: Gave every response model an explicit `title`, grouped routes with tags (invoices, quotes, admin), and added examples to the request bodies. /docs now reads well and the generated TypeScript client has stable type names.\nuser: Hook up Sentry for the API and the worker.\nassistant: Added `sentry_sdk.init` in both entry points with the FastAPI and RQ integrations, environment from APP_ENV, traces_sample_rate 0.1 in production, and a before_send hook that strips customer emails.\nuser: Our tests create objects by hand everywhere. Can we use factories?\nassistant: Added factory_boy factories for Customer, Invoice and LineItem in `tests/factories.py`, with a session-scoped database fixture and per-test transactions rolled back at teardown.\nuser: For the quote endpoint, write a function that returns a line item's total with tax applied.\nassistant: (scripted reply omitted - the check is on the context the model would receive)\nuser: What tax rate does the quote preview apply? Show me the constant it uses.\nassistant: (scripted reply omitted - the check is on the context the model would receive)",
    "truncated": false
   },
   "raised": [
    {
     "kind": "loss_threshold_exceeded",
     "source_module": "summarization",
     "detail": {
      "loss_score": 0.4667,
      "tier_emitted": "L2",
      "symbol_retention_rate": 1.0
     }
    }
   ],
   "traps": []
  },
  {
   "exchange": 17,
   "turn_id": "t0033",
   "user": "When a refund is issued, notify the customer by email using our invoice email function.",
   "assistant": "(scripted reply omitted - the check is on the context the model would receive)",
   "signal": {
    "turn_count": 33,
    "task_type": "code_generation",
    "matched_pattern": "carry_over",
    "topic_similarity": 0.235,
    "shift": false,
    "recall_request": false,
    "tokens_used": 1020,
    "budget": 700
   },
   "features": {
    "turn_count": 33,
    "token_budget_pressure": 1.0,
    "task_type": "code_generation",
    "prior_strategy": "hybrid",
    "time_since_last_switch": 2
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
    "latency_ms": 0.0971,
    "override": [],
    "full": "[build_request] task_type=code_generation (build-request pattern) -> hybrid: recent window + RAG to surface existing definitions before writing new code | escalation from t0031 (loss_threshold_exceeded) noted; no change for hybrid | features: turn=33, pressure=1.00, task=code_generation, prior=hybrid, since_switch=2",
    "rule": "build_request",
    "rule_reason": "task_type=code_generation (build-request pattern) -> hybrid: recent window + RAG to surface existing definitions before writing new code",
    "dwell": [],
    "escalations": [
     "escalation from t0031 (loss_threshold_exceeded) noted; no change for hybrid"
    ]
   },
   "candidates": {
    "sliding_window": {
     "tokens": 456,
     "latency_ms": 0.49,
     "quality": {
      "kept": 14,
      "relevance": 0.19,
      "freshness": 0.558,
      "importance": 0.179,
      "state": 0.596,
      "composite": 0.381
     }
    },
    "summarization": {
     "tokens": 683,
     "latency_ms": 5.25,
     "quality": {
      "tier_emitted": "L2",
      "loss_score": 0.5333,
      "loss_threshold_exceeded": true,
      "symbol_retention_rate": 1.0
     }
    },
    "rag": {
     "tokens": 675,
     "latency_ms": 102.32,
     "quality": {
      "granularity_tag": "turn",
      "retrieved": 14,
      "stale_flags": 3
     }
    }
   },
   "prompt": {
    "tokens": 673,
    "context": "[Retrieved memory]\n[turns: t0005]\nuser: Write the function that emails an invoice PDF to the customer.\n\n---\n\n[turns: t0006]\nassistant: Added to `billing/notify.py`:\n```python\ndef send_invoice_email(invoice_id, recipient):\n    pdf = render_invoice_pdf(invoice_id)\n    mailer.send(to=recipient, subject=f'Invoice {invoice_id}', attachment=pdf)\n```\n[!] stale: superseded by turn:t0014 (nli, confidence 1.00) - prefer the newer chunk\n\n---\n\n[turns: t0014 | supersedes turn:t0006]\nassistant: Replaced it in `billing/notify.py`:\n```python\ndef enqueue_invoice_email(invoice_id, recipient):\n    queue.enqueue('emails', {'invoice_id': invoice_id, 'to': recipient})\n```\nThe worker in `workers/email.py` now renders and sends. Both callers were updated.\n\n---\n\n[turns: t0001]\nuser: Give me an overview of the invoice service before we start.\n\n---\n\n[turns: t0009]\nuser: Used pytest.approx, green now. The /invoices list endpoint is slow though.\n\n---\n\n[turns: t0013]\nuser: Emails should go through the background queue instead of being sent inline. Rename the email function accordingly.\n\n---\n\n[turns: t0017]\nuser: Paginate the /invoices endpoint, some customers have thousands.\n[!] stale: superseded by turn:t0026 (nli, confidence 1.00) - prefer the newer chunk\n\n[Recent turns]\nassistant: Added to `billing/pricing.py`:\n```python\nTAX_RATE = 0.08\n\ndef compute_line_total(qty, unit_price, tax_rate=TAX_RATE):\n    subtotal = qty * unit_price\n    return round(subtotal * (1 + tax_rate), 2)\n```\nassistant: Gave every response model an explicit `title`, grouped routes with tags (invoices, quotes, admin), and added examples to the request bodies. /docs now reads well and the generated TypeScript client has stable type names.\nuser: Hook up Sentry for the API and the worker.\nassistant: Added `sentry_sdk.init` in both entry points with the FastAPI and RQ integrations, environment from APP_ENV, traces_sample_rate 0.1 in production, and a before_send hook that strips customer emails.\nuser: Our tests create objects by hand everywhere. Can we use factories?\nassistant: Added factory_boy factories for Customer, Invoice and LineItem in `tests/factories.py`, with a session-scoped database fixture and per-test transactions rolled back at teardown.\nuser: For the quote endpoint, write a function that returns a line item's total with tax applied.\nassistant: (scripted reply omitted - the check is on the context the model would receive)\nuser: What tax rate does the quote preview apply? Show me the constant it uses.\nassistant: (scripted reply omitted - the check is on the context the model would receive)\nuser: Quotes should show the currency symbol from the customer's locale.\nassistant: Use Babel's `format_currency(amount, currency, locale=customer.locale)`; fall back to en_US.",
    "truncated": false
   },
   "raised": [
    {
     "kind": "loss_threshold_exceeded",
     "source_module": "summarization",
     "detail": {
      "loss_score": 0.5333,
      "tier_emitted": "L2",
      "symbol_retention_rate": 1.0
     }
    }
   ],
   "traps": [
    {
     "name": "renamed email function",
     "description": "send_invoice_email was replaced by enqueue_invoice_email at exchange 7",
     "planted_at": 7,
     "kind": "rename",
     "adaptive": {
      "caught": true,
      "detail": "found `def enqueue_invoice_email(`",
      "strategy": "hybrid"
     },
     "fixed_6_exchange_window": {
      "caught": false,
      "detail": "missing `def enqueue_invoice_email(`"
     },
     "sliding_window": {
      "caught": false,
      "detail": "unmarked stale `def send_invoice_email(` present"
     },
     "summarization": {
      "caught": false,
      "detail": "unmarked stale `def send_invoice_email(` present"
     },
     "rag": {
      "caught": true,
      "detail": "found `def enqueue_invoice_email(`"
     },
     "hybrid": {
      "caught": true,
      "detail": "found `def enqueue_invoice_email(`"
     }
    }
   ]
  }
 ]
};
