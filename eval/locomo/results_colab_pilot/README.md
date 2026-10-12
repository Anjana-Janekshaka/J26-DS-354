# Colab pilot (LoCoMo answer accuracy)

- **Run:** 2026-10-12 on a free Colab T4, with Ollama serving `qwen2.5:7b-instruct` as both the answer
  model and the judge. Produced by `notebooks/free_gpu_eval.ipynb`.
- **Pilot only, not a final result.**
  - The code was mid-fix.
  - The LoCoMo sample was the *first* 50 questions of 2 conversations, which over-represents
    temporal questions. The harness now draws a seeded random sample instead.
- **Not committed:** the LLM caches, the labelling sheets and the judge key.
