"""Zip the repo for upload as a Kaggle dataset / Colab file (code + benchmark data, no venv/caches).

    python scripts/package_for_notebook.py      ->  dist/ceai-memory-middleware.zip
"""

from __future__ import annotations

import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".venv", "runs", "dist", "__pycache__", ".pytest_cache", ".git", "results", "results_no_nli", "results_b100"}
SKIP_SUFFIXES = {".pyc", ".egg-info"}


def include(path: Path) -> bool:
    rel = path.relative_to(ROOT)
    if any(part in SKIP_DIRS or part.endswith(".egg-info") for part in rel.parts):
        return False
    return path.suffix not in SKIP_SUFFIXES


def main() -> None:
    out = ROOT / "dist" / "ceai-memory-middleware.zip"
    out.parent.mkdir(exist_ok=True)
    n = 0
    import datetime
    import subprocess

    commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(["git", "status", "--porcelain", "--untracked-files=no"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    stamp = f"commit {commit or '?'}{' + uncommitted changes' if dirty else ''}, packaged {datetime.datetime.now():%Y-%m-%d %H:%M}"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("ceai-memory-middleware/BUILD_INFO.txt", stamp + "\n")
        for p in sorted(ROOT.rglob("*")):
            if p.is_file() and include(p):
                z.write(p, Path("ceai-memory-middleware") / p.relative_to(ROOT))
                n += 1
    print(f"wrote {out} ({n} files, {out.stat().st_size / 1e6:.1f} MB) - {stamp}")


if __name__ == "__main__":
    main()
