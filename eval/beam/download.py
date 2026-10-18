"""Download the BEAM 100K split through the Hugging Face dataset-viewer API (no extra dependencies).

    python -m eval.beam.download

BEAM: Tavakoli et al., "Beyond a Million Tokens" (arXiv 2510.27246), CC BY-SA 4.0,
https://huggingface.co/datasets/Mohammadta/BEAM. The data is written to eval/beam/data/ and not committed.
"""

from __future__ import annotations

import json
import urllib.request
from pathlib import Path

DATA = Path(__file__).parent / "data"
API = "https://datasets-server.huggingface.co/rows?dataset=Mohammadta%2FBEAM&config=default&split={split}&offset={offset}&length={length}"


def main(split: str = "100K") -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    rows, offset = [], 0
    while True:
        with urllib.request.urlopen(API.format(split=split, offset=offset, length=5), timeout=120) as r:
            page = json.load(r)
        got = [x["row"] for x in page["rows"]]
        rows += got
        offset += len(got)
        if not got or offset >= page.get("num_rows_total", offset):
            break
    out = DATA / f"beam_{split}.json"
    out.write_text(json.dumps(rows), encoding="utf-8")
    print(f"{len(rows)} conversations -> {out}")


if __name__ == "__main__":
    main()
