"""Evaluasi baseline statis dan run LLM terhadap ground_truth.json.

Pemakaian:
    python evaluate.py                 # cetak semua tabel ke stdout
    python evaluate.py --md out.md     # juga tulis ringkasan Markdown

Aturan evaluasi:
- Temuan cocok (TP) jika file sama dan |baris - baris_GT| <= TOLERANCE (common.py),
  pencocokan satu-satu.
- Validasi semantik: temuan yang barisnya cocok tetapi isinya tidak membahas cacat
  tersebut dicatat di SEMANTIC_MISMATCH dan dihitung sebagai FP. Semua TP LLM sudah
  diperiksa manual (lihat docs/04); satu-satunya ketidakcocokan ada pada Pylint W1514.
- Review yang gagal (limit kuota / error CLI) tidak dihitung sebagai hasil.
  Run dengan file gagal dilaporkan sebagai run tidak lengkap.
"""
import argparse
import json
from statistics import mean, stdev

from common import RESULTS, files, ground_truth, match

GT = ground_truth()
CLEAN_FILES = {"money.py", "task_queue.py"}
RUNS = ("1", "2", "3")

# (tool/rule) yang barisnya kebetulan cocok dengan cacat tetapi membahas hal lain.
# W1514 = open() tanpa encoding; bukan "file tidak ditutup" (D19).
SEMANTIC_MISMATCH = {("pylint", "W1514")}


def _mismatch(f):
    rule = ((f.get("rule") or "").split() or [""])[0]
    return (f.get("tool"), rule) in SEMANTIC_MISMATCH


def metrics(findings, gt=None):
    gt = GT if gt is None else gt
    eligible = [f for f in findings if not _mismatch(f)]
    rejected = [f for f in findings if _mismatch(f)]
    tp, fp, fn = match(eligible, gt)
    fp = fp + rejected
    p = len(tp) / (len(tp) + len(fp)) if (tp or fp) else 0.0
    r = len(tp) / len(gt) if gt else 0.0
    f1 = 2 * p * r / (p + r) if (p + r) else 0.0
    return {
        "total": len(findings), "tp": len(tp), "fp": len(fp), "fn": len(fn),
        "precision": p, "recall": r, "f1": f1,
        "clean_fp": sum(1 for f in fp if f["file"] in CLEAN_FILES),
        "matched": sorted(gt[gi]["id"] for _, gi in tp),
        "missed": sorted(g["id"] for g in fn),
        "fp_list": fp,
    }


def is_failed(review):
    raw = (review.get("raw") or "").lower()
    return not review["findings"] and ("limit" in raw or not review.get("cost_usd"))


# ---------- loader ----------

def load_static(tool):
    d = json.loads((RESULTS / f"static_{tool}.json").read_text(encoding="utf-8"))
    return [dict(f, tool=tool) for f in d["findings"]], d["seconds"]


def load_static_union():
    seen, merged, sec = set(), [], 0.0
    for t in ("pylint", "bandit", "ruff"):
        fs, s = load_static(t)
        sec += s
        for f in fs:
            key = (f["file"], int(f["line"]))
            if key not in seen and not _mismatch(f):
                seen.add(key)
                merged.append(f)
    return merged, sec


def load_llm(cond, run, severities=None):
    path = RESULTS / f"llm_{cond}_run{run}.json"
    if not path.exists():
        return None
    reviews = json.loads(path.read_text(encoding="utf-8"))["reviews"]
    ok = [r for r in reviews if not is_failed(r)]
    fs = [f for r in ok for f in r["findings"]
          if severities is None or f.get("severity") in severities]
    return {
        "findings": fs,
        "complete": len(ok) == len(files()),
        "failed_files": sorted(r["file"] for r in reviews if is_failed(r)),
        "seconds": sum(r["seconds"] for r in ok),
        "cost": sum(r.get("cost_usd") or 0 for r in ok),
        "turns": mean(r.get("num_turns") or 0 for r in ok) if ok else 0,
    }


def majority(run_findings, k=2, tol=2):
    """Temuan run pertama yang juga muncul (file sama, baris +-tol) di >= k run."""
    base, out = run_findings[0], []
    for f in base:
        votes = sum(
            any(g["file"] == f["file"] and abs(int(g["line"]) - int(f["line"])) <= tol for g in fs)
            for fs in run_findings
        )
        if votes >= k:
            out.append(f)
    return out


def category_recall(matched):
    out = {}
    for g in GT:
        hit, tot = out.get(g["category"], (0, 0))
        out[g["category"]] = (hit + (g["id"] in matched), tot + 1)
    return out


# ---------- laporan ----------

def fmt(x):
    return f"{x:.3f}"


def ms(xs):
    return f"{mean(xs):.3f} ± {stdev(xs):.3f}" if len(xs) > 1 else fmt(xs[0])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--md", help="tulis ringkasan Markdown ke file ini")
    args = ap.parse_args()
    lines = []

    def out(s=""):
        print(s)
        lines.append(s)

    out(f"Dataset: {len(files())} file, {len(GT)} cacat ground truth, "
        f"{len(CLEAN_FILES)} file bersih (kontrol negatif).\n")

    # 1. per metode / per run
    out("## Tabel 1. Hasil per metode dan per run\n")
    out("| Metode | Run | Temuan | TP | FP | FN | Precision | Recall | F1 | FP file bersih | Waktu (s) | Biaya (USD) | Rata-rata turn |")
    out("|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    matrix_cols = {}
    for t in ("pylint", "bandit", "ruff"):
        fs, sec = load_static(t)
        m = metrics(fs)
        matrix_cols[t] = m["matched"]
        out(f"| {t} | - | {m['total']} | {m['tp']} | {m['fp']} | {m['fn']} | {fmt(m['precision'])} | "
            f"{fmt(m['recall'])} | {fmt(m['f1'])} | {m['clean_fp']} | {sec:.2f} | 0 | - |")
    fs, sec = load_static_union()
    m = metrics(fs)
    matrix_cols["statis gabungan"] = m["matched"]
    out(f"| statis gabungan | - | {m['total']} | {m['tp']} | {m['fp']} | {m['fn']} | {fmt(m['precision'])} | "
        f"{fmt(m['recall'])} | {fmt(m['f1'])} | {m['clean_fp']} | {sec:.2f} | 0 | - |")

    agg, runs_ok = {}, {}
    for cond in ("single", "agent"):
        agg[cond] = {"p": [], "r": [], "f1": [], "cfp": [], "sec": [], "cost": [], "turns": [], "n": []}
        runs_ok[cond] = []
        for run in RUNS:
            d = load_llm(cond, run)
            if d is None:
                continue
            if not d["complete"]:
                out(f"| LLM {cond} | {run} | *tidak lengkap: gagal pada {', '.join(d['failed_files'])}* "
                    f"| | | | | | | | | | |")
                continue
            m = metrics(d["findings"])
            matrix_cols[f"{cond} r{run}"] = m["matched"]
            runs_ok[cond].append(d["findings"])
            a = agg[cond]
            a["p"].append(m["precision"]); a["r"].append(m["recall"]); a["f1"].append(m["f1"])
            a["cfp"].append(m["clean_fp"]); a["sec"].append(d["seconds"]); a["cost"].append(d["cost"])
            a["turns"].append(d["turns"]); a["n"].append(m["total"])
            out(f"| LLM {cond} | {run} | {m['total']} | {m['tp']} | {m['fp']} | {m['fn']} | {fmt(m['precision'])} | "
                f"{fmt(m['recall'])} | {fmt(m['f1'])} | {m['clean_fp']} | {d['seconds']:.1f} | {d['cost']:.3f} | {d['turns']:.2f} |")

    # 2. rata-rata
    out("\n## Tabel 2. Rata-rata ± simpangan baku (hanya run lengkap)\n")
    out("| Kondisi | Run lengkap | Temuan | Precision | Recall | F1 | FP file bersih | Waktu/run (s) | Biaya/run (USD) | Turn/file |")
    out("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for cond, a in agg.items():
        if not a["p"]:
            continue
        out(f"| LLM {cond} | {len(a['p'])} | {mean(a['n']):.1f} | {ms(a['p'])} | {ms(a['r'])} | {ms(a['f1'])} | "
            f"{mean(a['cfp']):.1f} | {mean(a['sec']):.1f} | {mean(a['cost']):.3f} | {mean(a['turns']):.2f} |")

    # 3. ablasi pasca-eksperimen
    out("\n## Tabel 3. Ablasi pasca-eksperimen (rata-rata run lengkap)\n")
    out("| Kondisi | Varian | Temuan | Precision | Recall | F1 | FP file bersih |")
    out("|---|---|---:|---:|---:|---:|---:|")
    for cond in ("single", "agent"):
        for label, sev in (("severity high+medium", {"high", "medium"}), ("severity high saja", {"high"})):
            ps, rs, fs1, ns, cf = [], [], [], [], []
            for run in RUNS:
                d = load_llm(cond, run, sev)
                if d and d["complete"]:
                    m = metrics(d["findings"])
                    ps.append(m["precision"]); rs.append(m["recall"]); fs1.append(m["f1"])
                    ns.append(m["total"]); cf.append(m["clean_fp"])
            if ps:
                out(f"| LLM {cond} | {label} | {mean(ns):.1f} | {ms(ps)} | {ms(rs)} | {ms(fs1)} | {mean(cf):.1f} |")
        if len(runs_ok[cond]) >= 3:
            m = metrics(majority(runs_ok[cond], k=2))
            out(f"| LLM {cond} | konsensus >= 2 dari 3 run | {m['total']} | {fmt(m['precision'])} | "
                f"{fmt(m['recall'])} | {fmt(m['f1'])} | {m['clean_fp']} |")

    # 4. recall per kategori
    out("\n## Tabel 4. Recall per kategori cacat\n")
    cols = list(matrix_cols)
    out("| Kategori | " + " | ".join(cols) + " |")
    out("|---|" + "---:|" * len(cols))
    cats = sorted({g["category"] for g in GT})
    cr = {c: category_recall(set(v)) for c, v in matrix_cols.items()}
    for cat in cats:
        out(f"| {cat} | " + " | ".join(f"{cr[c][cat][0]}/{cr[c][cat][1]}" for c in cols) + " |")

    # 5. matriks deteksi
    out("\n## Tabel 5. Matriks deteksi per cacat (Y = terdeteksi)\n")
    out("| ID | File | Baris | Kategori | Deskripsi | " + " | ".join(cols) + " |")
    out("|---|---|---:|---|---|" + ":---:|" * len(cols))
    for g in GT:
        flags = " | ".join("Y" if g["id"] in matrix_cols[c] else "." for c in cols)
        out(f"| {g['id']} | {g['file']} | {g['line']} | {g['category']} | {g['desc']} | {flags} |")

    if args.md:
        with open(args.md, "w", encoding="utf-8") as fh:
            fh.write("# Ringkasan Hasil Evaluasi (dibuat otomatis oleh evaluate.py)\n\n")
            fh.write("\n".join(lines) + "\n")
        print("\nRingkasan Markdown ditulis ke", args.md)


if __name__ == "__main__":
    main()
