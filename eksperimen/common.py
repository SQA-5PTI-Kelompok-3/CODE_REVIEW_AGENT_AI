"""Shared helpers: dataset paths, ground truth, matching."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATASET = ROOT / "dataset" / "shopapp"
RESULTS = ROOT / "results"
TOLERANCE = 2  # finding cocok jika |line - line_gt| <= TOLERANCE


def files():
    return sorted(p.name for p in DATASET.glob("*.py"))


def ground_truth():
    gt = json.loads((ROOT / "ground_truth.json").read_text(encoding="utf-8"))
    for d in gt:
        lines = (DATASET / d["file"]).read_text(encoding="utf-8").splitlines()
        hits = [i + 1 for i, ln in enumerate(lines) if d["anchor"] in ln]
        assert hits, d
        d["line"] = hits[0]
    return gt


def match(findings, gt):
    """Pencocokan satu-satu (greedy, jarak baris terdekat lebih dulu)."""
    pairs = []
    for fi, f in enumerate(findings):
        for gi, g in enumerate(gt):
            if f["file"] == g["file"] and abs(int(f["line"]) - g["line"]) <= TOLERANCE:
                pairs.append((abs(int(f["line"]) - g["line"]), fi, gi))
    pairs.sort()
    used_f, used_g, tp = set(), set(), []
    for _, fi, gi in pairs:
        if fi in used_f or gi in used_g:
            continue
        used_f.add(fi); used_g.add(gi); tp.append((fi, gi))
    fp = [findings[i] for i in range(len(findings)) if i not in used_f]
    fn = [gt[i] for i in range(len(gt)) if i not in used_g]
    return tp, fp, fn
