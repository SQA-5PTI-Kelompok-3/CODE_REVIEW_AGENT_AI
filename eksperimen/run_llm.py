"""Jalankan dua kondisi LLM via Claude Code headless (claude -p):
  single  = LLM single-shot: kode ditempel di prompt, tanpa tools
  agent   = code review agent: hanya diberi nama file, boleh memakai Read/Grep/Glob
Pemakaian: python run_llm.py <run_id> [model] [--retry-failed]
  --retry-failed  hanya mengulang file yang gagal karena limit kuota pada run tsb,
                  lalu menggabungkannya ke file hasil yang sudah ada.
"""
import json, re, shutil, subprocess, sys, tempfile, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from common import DATASET, RESULTS, ROOT, files

ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
RETRY = "--retry-failed" in sys.argv
RUN = ARGS[0] if ARGS else "1"
MODEL = ARGS[1] if len(ARGS) > 1 else "sonnet"
CLAUDE = shutil.which("claude")
# Salinan terisolasi: agent tidak bisa melihat ground_truth.json di folder induk
WORKDIR = Path(tempfile.mkdtemp(prefix="crx_")) / "shopapp"
shutil.copytree(DATASET, WORKDIR)
PROMPTS = {k: (ROOT / "prompts" / f"{k}.txt").read_text(encoding="utf-8") for k in ("single_shot", "agent")}


def build(cond, f):
    if cond == "single":
        code = (DATASET / f).read_text(encoding="utf-8").splitlines()
        numbered = "\n".join(f"{i + 1:3d}  {ln}" for i, ln in enumerate(code))
        return PROMPTS["single_shot"].format(file=f, numbered_code=numbered), ["--tools", ""]
    return PROMPTS["agent"].format(file=f), ["--tools", "Read,Grep,Glob", "--allowedTools", "Read,Grep,Glob"]


def parse(text):
    m = re.search(r"\[.*\]", text, re.S)
    try:
        return json.loads(m.group(0)) if m else []
    except json.JSONDecodeError:
        return []


def review(job):
    cond, f = job
    prompt, extra = build(cond, f)
    cmd = [CLAUDE, "-p", "--output-format", "json", "--model", MODEL,
           "--no-session-persistence", *extra]
    t = time.perf_counter()
    p = subprocess.run(cmd, input=prompt, capture_output=True, text=True,
                       encoding="utf-8", cwd=WORKDIR, timeout=900)
    dt = time.perf_counter() - t
    try:
        meta = json.loads(p.stdout)
    except json.JSONDecodeError:
        meta = {"result": p.stdout, "error": p.stderr[-500:]}
    findings = [dict(x, file=f) for x in parse(meta.get("result", "")) if "line" in x]
    return {"cond": cond, "file": f, "seconds": round(dt, 1), "num_turns": meta.get("num_turns"),
            "cost_usd": meta.get("total_cost_usd"), "raw": meta.get("result", ""),
            "findings": findings}


def failed(r):
    """Review gagal karena limit kuota / error CLI (bukan hasil review)."""
    raw = (r.get("raw") or "").lower()
    return not r["findings"] and ("limit" in raw or "error" in r or not r.get("cost_usd"))


RESULTS.mkdir(exist_ok=True)
old = {}
if RETRY:
    for cond in ("single", "agent"):
        path = RESULTS / f"llm_{cond}_run{RUN}.json"
        if path.exists():
            old[cond] = json.loads(path.read_text(encoding="utf-8"))["reviews"]
    jobs = [(c, r["file"]) for c, rows in old.items() for r in rows if failed(r)]
else:
    jobs = [(c, f) for c in ("single", "agent") for f in files()]
print("jobs:", len(jobs))
with ThreadPoolExecutor(max_workers=4) as ex:
    out = list(ex.map(review, jobs))
for cond in ("single", "agent"):
    new = {r["file"]: r for r in out if r["cond"] == cond}
    rows = [new.get(r["file"], r) for r in old.get(cond, [])] if RETRY else list(new.values())
    (RESULTS / f"llm_{cond}_run{RUN}.json").write_text(json.dumps(
        {"cond": cond, "run": RUN, "model": MODEL, "reviews": rows}, indent=1, ensure_ascii=False),
        encoding="utf-8")
    print(cond, sum(len(r["findings"]) for r in rows), "findings")
