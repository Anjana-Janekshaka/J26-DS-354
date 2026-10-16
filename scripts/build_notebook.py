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
JUDGE_MODEL = "qwen2.5:7b-instruct"     # grades answers; 14B is better but crowds a free T4 (OK on Kaggle 2xT4)
CONVERSATIONS = 2                       # LoCoMo conversations (10 = full set)
MAX_QUESTIONS = 50                      # questions per conversation (None = all)
PARALLEL = 4                            # requests sent at once; Ollama batches them on the GPU
REPO_URL = ""                           # git URL if the repo is pushed; otherwise upload the zip
QA_TEST_QUESTIONS = 60                  # random LoCoMo test questions per test conversation for answer accuracy
RUN = {
    # FINAL RUN (frozen configuration). The val check gates everything after it: if the frozen system
    # scores below its own recorded val result, the notebook stops before touching any test split.
    # v2 hybrid, PRE-REGISTERED (docs/v2_hybrid_preregistration.md): dev/val gates, then each test split once
    # External baselines under identical conditions (docs/baselines_protocol.md):
    "baselines": True,
    "v2_preregistered": False,          # done 2026-10-15: gate G3 failed, so no v2 test runs (must stay off)
    # v2 retrieval options on the LoCoMo DEV split (done 2026-10-16):
    "v2_dev_retrieval": False,
    # FINAL RUN - already done on 2026-10-15 and frozen; leave off (results live in ceai_runs/final):
    "val_check": False,                 # synthetic controller val with the final code (re-records traces)
    "final_test": False,                # every test split, once: LoCoMo, in-stream LoCoMo, LoCoMo-Plus, controller
    "locomo_qa_test": False,            # answer accuracy (LLM + judge) on a random LoCoMo test sample
    "labelling_sheets": False,          # blind sheets from the test answers, for the human-agreement check
    # Development jobs (already done - leave off; tuning would overwrite the frozen config):
    "controller_tuning": False,
    "locomo_plus_routing_dev": False,
    "locomo_qa": False,                 # pilot: first conversations, not the test split
    "locomo_llm_summaries": False,
    "controller_judge": False,          # 7B judge is not usable for strategy labels (CLAUDE.md 12.3)
    "locomo_plus": False,
}
NEED_LLM = (RUN["locomo_qa"] or RUN["locomo_qa_test"] or RUN["locomo_llm_summaries"] or RUN["controller_judge"]
            or RUN["v2_preregistered"] or RUN["baselines"])

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
# Always start from a fresh copy: a code folder left over from an earlier session would silently run old code.
os.chdir("/tmp")
shutil.rmtree(CODE, ignore_errors=True)
if REPO_URL:
    subprocess.run(["git", "clone", "--depth", "1", REPO_URL, str(CODE)], check=True)
else:
    # Kaggle unzips uploaded datasets, so accept the extracted folder as well as the zip itself.
    # /kaggle/input is read-only, so copy to /tmp before the editable install.
    dirs = [pathlib.Path(p).parent for p in glob.glob("/kaggle/input/**/ceai-memory-middleware/pyproject.toml", recursive=True)]
    zips = (glob.glob("/kaggle/input/**/ceai-memory-middleware*.zip", recursive=True)
            + glob.glob("/content/ceai-memory-middleware*.zip") + glob.glob("/content/drive/MyDrive/ceai-memory-middleware*.zip"))
    if dirs:
        shutil.copytree(dirs[0], CODE)
    elif zips:
        newest = max(zips, key=os.path.getmtime)  # re-uploads can leave older copies next to the new one
        print("using", newest, "of", len(zips), "zip(s) found")
        shutil.unpack_archive(newest, "/tmp")
    else:
        raise FileNotFoundError("attach the ceai-memory-middleware dataset / upload the zip (or set REPO_URL)")
info = CODE / "BUILD_INFO.txt"
print("CODE VERSION:", info.read_text().strip() if info.exists() else "unknown (zip built before build stamps)")
os.chdir(CODE)
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-e", "."], check=True)
print("code ready at", CODE)
import torch
print("torch sees GPU:", torch.cuda.is_available(), torch.cuda.get_device_name(0) if torch.cuda.is_available() else "- switch the runtime to T4 GPU")
"""),
    code("""
# ---- install and start Ollama, pull the models ---------------------------------------------
if not NEED_LLM:
    print("no LLM job selected - skipping Ollama")
else:
    subprocess.run("apt-get install -y -qq zstd pciutils > /dev/null 2>&1 || true", shell=True)
    if shutil.which("ollama") is None:
        subprocess.run("curl -fsSL https://ollama.com/install.sh | sh", shell=True, check=True)
    server = None

    def start_ollama(context=4096, parallel=PARALLEL):
        # (Re)start the Ollama server. A large context with several slots can push the model partly onto
        # the CPU on a T4 and stall every request, so long-context jobs restart it with one slot.
        global server
        if server is not None:
            server.terminate()
            server.wait(timeout=60)
        subprocess.run("pkill -f 'ollama serve' || true", shell=True)
        time.sleep(3)
        env = {**os.environ, "OLLAMA_KEEP_ALIVE": "-1", "OLLAMA_NUM_PARALLEL": str(parallel),
               "OLLAMA_CONTEXT_LENGTH": str(context)}  # controller-judge prompts exceed Ollama's small default context
        server = subprocess.Popen(["ollama", "serve"], stdout=open(WORK / "ollama.log", "a"), stderr=subprocess.STDOUT, env=env)
        for _ in range(120):
            try:
                urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=2)
                print(f"ollama running: context {context}, parallel {parallel}")
                return
            except Exception:
                time.sleep(1)
        raise RuntimeError("ollama did not start; see " + str(WORK / "ollama.log"))

    start_ollama()
    for model in {ANSWER_MODEL, JUDGE_MODEL}:
        subprocess.run(["ollama", "pull", model], check=True)
    # The single most common cause of very slow runs: Ollama silently running on the CPU.
    print(subprocess.run("nvidia-smi --query-gpu=name,memory.used,memory.total --format=csv", shell=True,
                         capture_output=True, text=True).stdout or "NO GPU VISIBLE - switch the runtime to T4 GPU")
    print("ollama ready")
"""),
    code("""
# ---- point the harnesses at the local endpoint and smoke-test ------------------------------
if not NEED_LLM:
    print("no LLM job selected - skipping Ollama")
else:
    os.environ["CEAI_LLM_BASE_URL"] = "http://127.0.0.1:11434/v1"
    os.environ["CEAI_LLM_MODEL"] = ANSWER_MODEL
    os.environ["CEAI_JUDGE_MODEL"] = JUDGE_MODEL
    os.environ["CEAI_LLM_CONCURRENCY"] = str(PARALLEL)
    sys.path[:0] = [str(CODE), str(CODE / "packages")]
    from concurrent.futures import ThreadPoolExecutor
    from integration.llm_client import get_llm
    from eval.judge import grade
    answer, judge = get_llm(), get_llm(role="judge")
    print("answer model:", answer("Reply with exactly: OK", "ping"))
    print("judge check (expect CORRECT):", grade(judge, "When did she move?", "7 May 2023", "She moved on May 7, 2023."))
    print(subprocess.run("ollama ps", shell=True, capture_output=True, text=True).stdout)  # PROCESSOR column should say GPU

    # ---- timing test: estimate the whole run before committing hours to it ----------------------
    context = "[Memory context] " + ("Caroline said she went to a support group on 7 May 2023 and felt welcomed. " * 60)
    t = time.time()
    with ThreadPoolExecutor(PARALLEL) as pool:
        list(pool.map(lambda i: answer("Answer with a short phrase.", f"{context} Question {i}: When did Caroline go to the group?"),
                      range(2 * PARALLEL)))
    per_call = (time.time() - t) / (2 * PARALLEL)
    n_q = 5 * QA_TEST_QUESTIONS if RUN["locomo_qa_test"] else CONVERSATIONS * (MAX_QUESTIONS or 200)
    n_answer = n_q * 0.8 * 4      # ~80% answerable, ~4 distinct contexts each
    estimate_h = (n_answer * per_call * 1.3 + 180 * per_call * 1.5) / 3600
    print(f"~{per_call:.1f} s per answer call (with {PARALLEL} in parallel) -> estimated run time ~{estimate_h:.1f} h")
    if per_call > 4:
        print("SLOW: check the GPU line above. If 'ollama ps' says CPU, restart the runtime with a T4 GPU.")
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
# ---- v2 retrieval options on the LoCoMo DEV split (dev previews; the frozen test results are untouched)
if RUN["v2_dev_retrieval"]:
    V2 = WORK / "dev_v2"
    for name, flags in {"V2_rerank_hybrid": ["--hybrid"],
                        "V3_rerank_mmr07": ["--mmr", "0.7"],
                        "V4_rerank_hybrid_mmr07": ["--hybrid", "--mmr", "0.7"],
                        "D_frozen_reference": []}.items():
        if (V2 / name / "summary.json").exists():
            print("already done:", name)
            continue
        run(["eval.locomo.run", "--split", "dev", "--no-nli", *flags, "--out", str(V2 / name)], f"dev_v2_{name}")

# ---- FINAL RUN: val gate, then every test split exactly once ---------------------------------
FINAL = WORK / "final"
if RUN["val_check"]:
    run(["eval.synthetic.controller.run", "--split", "val", "--n-boot", "200",
         "--cache-dir", str(WORK / "controller_traces"), "--out", str(FINAL / "controller")], "final_val_check")
    got = json.load(open(FINAL / "controller" / "val" / "summary.json"))["evidence_hit_rate"]["adaptive"]["estimate"]
    want = json.load(open(CODE / "eval/synthetic/controller/frozen_rule_config.json"))["selected"]["val"]["hit"]
    print(f"VAL CHECK: adaptive evidence hit {got:.4f} (recorded when frozen: {want:.4f})")
    if got < want - 1e-9:
        raise RuntimeError("VAL CHECK FAILED - stop here and send the results folder; do not run the test splits")
    print("VAL CHECK PASSED - running the test splits")

def once(name, args):
    # Each test split runs exactly once: a finished result is never recomputed.
    if (FINAL / name / "summary.json").exists() or (FINAL / name / "test" / "summary.json").exists():
        print("already done:", name)
        return
    run([*args, "--out", str(FINAL / name)], f"final_{name}")

if RUN["final_test"]:
    once("locomo", ["eval.locomo.run", "--split", "test", "--no-nli"])
    once("locomo_stream", ["eval.locomo.stream", "--split", "test"])
    once("locomo_plus", ["eval.locomo_plus.run", "--split", "test", "--warmup-turns", "10"])
    if not (FINAL / "controller" / "test" / "summary.json").exists():
        run(["eval.synthetic.controller.run", "--split", "test", "--cache-dir", str(WORK / "controller_traces"),
             "--out", str(FINAL / "controller")], "final_controller_test")
if RUN["locomo_qa_test"]:
    once("locomo_qa", ["eval.locomo.run", "--split", "test", "--no-nli", "--llm", "--judge-answers",
                       "--max-questions", str(QA_TEST_QUESTIONS)])

# ---- external baselines on the LoCoMo test questions CEAI answered (resumes after a disconnect) ---
if RUN["baselines"]:
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "mem0ai", "ollama"], check=False)
    # CEAI's frozen test answers ship in the code zip; the Drive copy is only a fallback.
    ceai_q = CODE / "results" / "final" / "locomo_qa_test_questions.jsonl"
    if not ceai_q.exists():
        ceai_q = WORK / "final" / "locomo_qa" / "questions.jsonl"
    assert ceai_q.exists(), f"missing {ceai_q}: CEAI's frozen test answers are needed for the paired comparison"
    print("CEAI frozen answers:", ceai_q)
    # Phase 1: memory baselines at the normal server settings.
    run(["eval.baselines.run", "--ceai-questions", str(ceai_q), "--systems", "fixed_chunk_rag,summary_buffer,mem0",
         "--out", str(WORK / "baselines")], "baselines_phase1")
    # Phase 2: the full-context ceiling alone, with a 32k context, one slot and a long request timeout.
    start_ollama(context=32768, parallel=1)
    os.environ["CEAI_LLM_TIMEOUT"], os.environ["CEAI_LLM_CONCURRENCY"] = "1200", "1"
    run(["eval.baselines.run", "--ceai-questions", str(ceai_q), "--systems", "fixed_chunk_rag,summary_buffer,mem0,full_context",
         "--out", str(WORK / "baselines")], "baselines_phase2")
    os.environ["CEAI_LLM_TIMEOUT"], os.environ["CEAI_LLM_CONCURRENCY"] = "300", str(PARALLEL)
    start_ollama()

# ---- v2 hybrid, pre-registered: gates on dev/val, then every test split exactly once -------------
if RUN["v2_preregistered"]:
    V2W = WORK / "v2_hybrid"
    G = V2W / "gates"

    def as_system(name):
        os.environ["CEAI_SYSTEM"] = name

    # Frozen references for the paired gates (frozen val reuses the final run when present).
    as_system("frozen")
    frozen_val = FINAL / "controller" / "val" if (WORK / "final" / "controller" / "val" / "probes.jsonl").exists() else G / "frozen_val" / "val"
    if not (frozen_val / "probes.jsonl").exists():
        run(["eval.synthetic.controller.run", "--split", "val", "--n-boot", "200", "--cache-dir", str(WORK / "controller_traces"),
             "--out", str(G / "frozen_val")], "v2_gate_frozen_val")
    if not (G / "plus_frozen" / "summary.json").exists():
        run(["eval.locomo_plus.run", "--split", "dev", "--warmup-turns", "10", "--out", str(G / "plus_frozen")], "v2_gate_plus_frozen")
    # v2 on the same dev/val items.
    as_system("v2_hybrid")
    if not (G / "v2_val" / "val" / "summary.json").exists():
        run(["eval.synthetic.controller.run", "--split", "val", "--n-boot", "200", "--cache-dir", str(WORK / "controller_traces"),
             "--out", str(G / "v2_val")], "v2_gate_v2_val")
    if not (G / "plus_v2" / "summary.json").exists():
        run(["eval.locomo_plus.run", "--split", "dev", "--warmup-turns", "10", "--out", str(G / "plus_v2")], "v2_gate_plus_v2")
    gate = subprocess.run([sys.executable, "-m", "eval.v2_gate", "--frozen-val", str(frozen_val), "--v2-val", str(G / "v2_val" / "val"),
                           "--frozen-plus", str(G / "plus_frozen"), "--v2-plus", str(G / "plus_v2"), "--out", str(G / "gates.json")],
                          cwd=CODE, capture_output=True, text=True)
    print(gate.stdout)
    if gate.returncode != 0:
        as_system("frozen")
        raise RuntimeError("v2 GATE FAILED - stop here and send the results folder; the v2 test splits must not be run")

    # Each test split exactly once (finished results are never recomputed).
    def once_v2(name, args):
        if (V2W / "final" / name / "summary.json").exists() or (V2W / "final" / name / "test" / "summary.json").exists():
            print("already done:", name)
            return
        run([*args, "--out", str(V2W / "final" / name)], f"v2_final_{name}")

    once_v2("locomo", ["eval.locomo.run", "--split", "test", "--no-nli"])
    once_v2("locomo_stream", ["eval.locomo.stream", "--split", "test"])
    once_v2("locomo_plus", ["eval.locomo_plus.run", "--split", "test", "--warmup-turns", "10"])
    if not (V2W / "final" / "controller" / "test" / "summary.json").exists():
        run(["eval.synthetic.controller.run", "--split", "test", "--cache-dir", str(WORK / "controller_traces"),
             "--out", str(V2W / "final" / "controller")], "v2_final_controller_test")
    once_v2("locomo_qa", ["eval.locomo.run", "--split", "test", "--no-nli", "--llm", "--judge-answers",
                          "--max-questions", str(QA_TEST_QUESTIONS)])
    as_system("frozen")
    print("v2 pre-registered runs complete:", V2W)

"""),
    code("""
# ---- GPU jobs without an LLM: controller tuning and LoCoMo-Plus dev routing -------------------
if RUN["controller_tuning"]:
    # Traces are cached in Drive and saved after every conversation, so a disconnect resumes.
    run(["eval.synthetic.controller.tune_rules", "--cache-dir", str(WORK / "controller_traces")], "controller_tuning")
    shutil.copy(CODE / "eval/synthetic/controller/frozen_rule_config.json", WORK / "frozen_rule_config.json")
    print("tuned rules saved to", WORK / "frozen_rule_config.json")
if RUN["locomo_plus_routing_dev"]:
    variants = {"R0_current": [], "R1_loss_to_hybrid": ["--loss-target", "hybrid"],
                "R2_chat_hybrid": ["--long-chat", "hybrid"], "R3_both": ["--loss-target", "hybrid", "--long-chat", "hybrid"]}
    for name, flags in variants.items():
        if (WORK / "locomo_plus_dev" / name / "summary.json").exists():
            print("already done:", name)
            continue
        run(["eval.locomo_plus.run", "--split", "dev", "--warmup-turns", "10", *flags,
             "--out", str(WORK / "locomo_plus_dev" / name)], f"locomo_plus_dev_{name}")
"""),
    code("""
# ---- blind labelling sheets for the human-vs-judge check -----------------------------------
if RUN["labelling_sheets"]:
    qa_dir = WORK / "final" / "locomo_qa" if RUN["locomo_qa_test"] else WORK / "locomo_qa"
    run(["eval.human_agreement.make_sheets", "--questions", str(qa_dir / "questions.jsonl"),
         "--out", str(qa_dir.parent / "human_agreement")], "labelling_sheets")
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
