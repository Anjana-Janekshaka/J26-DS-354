"""Generate notebooks/free_gpu_eval.ipynb (run evaluations with free open models on Kaggle / Colab).

    python scripts/build_notebook.py
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def md(text: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": text.strip("\n").splitlines(keepends=True)}


def code(text: str) -> dict:
    return {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": text.strip("\n").splitlines(keepends=True)}


CELLS = [
    md("""
# CEAI evaluations with free open models (Kaggle / Colab GPU)

Runs the LLM-backed parts of the benchmark suite at **zero cost**, using open models served by
[Ollama](https://ollama.com) on a free notebook GPU:

| job | what it adds |
|---|---|
| LoCoMo QA | answers with the *answer* model, token-F1 + LLM-judge grades (correct / partial / wrong) |
| LoCoMo with LLM summaries | L1/L2/L3 written by the model instead of the rule-based generator |
| controller judge | the LLM-judge half of the dual-source strategy oracle |
| LoCoMo-Plus | deterministic cue-in-context scoring (no LLM; GPU only speeds up embeddings) |
| labelling sheets | blind sheets for the human-vs-judge agreement check |

**Setup**
* **Kaggle:** *Settings → Accelerator → GPU T4 ×2* and *Internet → On*. Upload `dist/ceai-memory-middleware.zip`
  (from `python scripts/package_for_notebook.py`) as a Kaggle dataset and attach it, or set `REPO_URL`.
* **Colab:** *Runtime → Change runtime type → T4 GPU*. Upload the zip to `/content` or set `REPO_URL`.
  Results go to Google Drive so they survive disconnects.

Every LLM call is cached to disk next to the results, so if the session dies, re-run all cells and
it resumes without repeating calls. On Kaggle, save results between sessions with *Save Version*
(or download `ceai_results.zip` at the end) and re-attach them as input.

Rough timings on a T4: 7–8B answer model ~1–2 s per call, 14B judge ~2–4 s per call; the default
sample (3 conversations × 100 questions) is about 1–2 hours end to end.
"""),
    code("""
# ---- configuration ------------------------------------------------------------------------
ANSWER_MODEL = "qwen2.5:7b-instruct"    # answers questions / writes summaries
JUDGE_MODEL = "qwen2.5:14b-instruct"    # grades answers; keep it larger than the answer model
CONVERSATIONS = 3                       # LoCoMo conversations (10 = full set)
MAX_QUESTIONS = 100                     # questions per conversation (None = all)
REPO_URL = ""                           # git URL if the repo is pushed; otherwise upload the zip
RUN = {
    "locomo_qa": True,                  # answers + token-F1 + judge grades
    "locomo_llm_summaries": False,      # evidence metrics with LLM-written L1/L2/L3 (slower)
    "controller_judge": True,           # LLM-judge oracle on the synthetic controller set
    "locomo_plus": False,               # deterministic; slow on CPU-bound hosts
    "labelling_sheets": True,           # needs locomo_qa
}
"""),
    code("""
import os, sys, glob, json, time, shutil, pathlib, subprocess, urllib.request

ON_COLAB = "google.colab" in sys.modules
ON_KAGGLE = os.path.exists("/kaggle")
if ON_COLAB:
    from google.colab import drive
    drive.mount("/content/drive")
    WORK = pathlib.Path("/content/drive/MyDrive/ceai_runs")
elif ON_KAGGLE:
    WORK = pathlib.Path("/kaggle/working/ceai_runs")
else:
    WORK = pathlib.Path.cwd() / "ceai_runs"
WORK.mkdir(parents=True, exist_ok=True)
# Resume on Kaggle: copy cached results from an attached previous version, if any.
for prev in glob.glob("/kaggle/input/*/ceai_runs"):
    shutil.copytree(prev, WORK, dirs_exist_ok=True)
print("results directory:", WORK)
"""),
    code("""
# ---- get the code ---------------------------------------------------------------------------
CODE = pathlib.Path("/tmp/ceai-memory-middleware")
if not CODE.exists():
    if REPO_URL:
        subprocess.run(["git", "clone", "--depth", "1", REPO_URL, str(CODE)], check=True)
    else:
        # Kaggle unzips uploaded datasets, so accept the extracted folder as well as the zip itself.
        # /kaggle/input is read-only, so copy to /tmp before the editable install.
        dirs = [pathlib.Path(p).parent for p in glob.glob("/kaggle/input/**/ceai-memory-middleware/pyproject.toml", recursive=True)]
        zips = glob.glob("/kaggle/input/**/ceai-memory-middleware.zip", recursive=True) + glob.glob("/content/ceai-memory-middleware.zip") + glob.glob("/content/drive/MyDrive/ceai-memory-middleware.zip")
        if dirs:
            shutil.copytree(dirs[0], CODE)
        elif zips:
            shutil.unpack_archive(zips[0], "/tmp")
        else:
            raise FileNotFoundError("attach the ceai-memory-middleware dataset / upload the zip (or set REPO_URL)")
os.chdir(CODE)
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-e", "."], check=True)
print("code ready at", CODE)
"""),
    code("""
# ---- install and start Ollama, pull the models ---------------------------------------------
subprocess.run("apt-get install -y -qq zstd pciutils > /dev/null 2>&1 || true", shell=True)
if shutil.which("ollama") is None:
    subprocess.run("curl -fsSL https://ollama.com/install.sh | sh", shell=True, check=True)
env = {**os.environ, "OLLAMA_KEEP_ALIVE": "-1", "OLLAMA_NUM_PARALLEL": "2"}
server = subprocess.Popen(["ollama", "serve"], stdout=open(WORK / "ollama.log", "w"), stderr=subprocess.STDOUT, env=env)
for _ in range(120):
    try:
        urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=2)
        break
    except Exception:
        time.sleep(1)
else:
    raise RuntimeError("ollama did not start; see " + str(WORK / "ollama.log"))
for model in {ANSWER_MODEL, JUDGE_MODEL}:
    subprocess.run(["ollama", "pull", model], check=True)
print("ollama ready")
"""),
    code("""
# ---- point the harnesses at the local endpoint and smoke-test ------------------------------
os.environ["CEAI_LLM_BASE_URL"] = "http://127.0.0.1:11434/v1"
os.environ["CEAI_LLM_MODEL"] = ANSWER_MODEL
os.environ["CEAI_JUDGE_MODEL"] = JUDGE_MODEL
sys.path[:0] = [str(CODE), str(CODE / "packages")]
from integration.llm_client import get_llm
from eval.judge import grade
print("answer model:", get_llm()("Reply with exactly: OK", "ping"))
print("judge check (expect CORRECT):", grade(get_llm(role="judge"), "When did she move?", "7 May 2023", "She moved on May 7, 2023."))
"""),
    code("""
def run(args, name):
    log = WORK / f"{name}.log"
    print(">>", " ".join(args))
    with open(log, "w") as f:
        p = subprocess.run([sys.executable, "-m", *args], stdout=f, stderr=subprocess.STDOUT, cwd=CODE)
    print("".join(open(log).readlines()[-30:]))
    if p.returncode:
        raise RuntimeError(f"{name} failed, see {log}")

q = ["--max-questions", str(MAX_QUESTIONS)] if MAX_QUESTIONS else []
if RUN["locomo_qa"]:
    run(["eval.locomo.run", "--conversations", str(CONVERSATIONS), *q, "--no-nli", "--llm", "--judge-answers",
         "--out", str(WORK / "locomo_qa")], "locomo_qa")
"""),
    code("""
if RUN["locomo_llm_summaries"]:
    run(["eval.locomo.run", "--conversations", str(CONVERSATIONS), *q, "--no-nli", "--llm-summaries",
         "--out", str(WORK / "locomo_llm_summaries")], "locomo_llm_summaries")
if RUN["controller_judge"]:
    run(["eval.synthetic.controller.run", "--judge", "--out", str(WORK / "controller_judge")], "controller_judge")
if RUN["locomo_plus"]:
    run(["eval.locomo_plus.run", "--out", str(WORK / "locomo_plus")], "locomo_plus")
"""),
    code("""
# ---- blind labelling sheets for the human-vs-judge check -----------------------------------
if RUN["labelling_sheets"]:
    run(["eval.human_agreement.make_sheets", "--questions", str(WORK / "locomo_qa" / "questions.jsonl"),
         "--out", str(WORK / "human_agreement")], "labelling_sheets")
    print("Send each annotator their annotator_N.csv + eval/human_agreement/LABELLING_GUIDE.md.")
    print("Keep key.json private. Score later with: python -m eval.human_agreement.score --sheets <folder>")
"""),
    code("""
# ---- bundle everything for download -------------------------------------------------------
archive = shutil.make_archive(str(WORK.parent / "ceai_results"), "zip", WORK)
print("download:", archive)
"""),
]


def main() -> None:
    nb = {
        "cells": CELLS,
        "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                     "language_info": {"name": "python"}, "accelerator": "GPU"},
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    out = ROOT / "notebooks" / "free_gpu_eval.ipynb"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(nb, indent=1), encoding="utf-8")
    print(f"wrote {out} ({len(CELLS)} cells)")


if __name__ == "__main__":
    main()
