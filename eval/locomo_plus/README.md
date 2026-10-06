# LoCoMo-Plus (supplementary only)

LoCoMo-Plus (arXiv 2602.10715) evaluates implicit / latent-constraint retention with an LLM judge.
It has no code content and **no per-turn strategy ground truth**, so (build guide sec. 8):

- it is never used as strategy-selection ground truth for the controller;
- summarization's Dual Q&A Consistency target lives on the synthetic developer traces
  (`eval/synthetic/summarization`), not here.

Status: **not run** (`# TODO: v2`). The dataset is not vendored and the judge needs Claude
credentials (`integration/llm_client.py`). When added, any LoCoMo-Plus conversation used for the
controller must get its oracle labels from the same objective protocol as
`eval/synthetic/controller` (plus the optional LLM-judge source), never from LoCoMo-Plus itself.
