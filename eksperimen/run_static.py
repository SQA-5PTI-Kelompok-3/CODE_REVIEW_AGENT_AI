"""Baseline: Pylint (E/W), Bandit, Ruff (F,B,S). Output: results/static_<tool>.json"""
import json, subprocess, sys, time
from common import DATASET, RESULTS, files

RESULTS.mkdir(exist_ok=True)
paths = [str(DATASET / f) for f in files()]


def run(cmd):
    t = time.perf_counter()
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.stdout, time.perf_counter() - t


def pylint():
    out, dt = run([sys.executable, "-m", "pylint", "--output-format=json",
                   "--disable=C,R", *paths])
    return [{"file": m["path"].replace("\\", "/").split("/")[-1], "line": m["line"],
             "rule": f'{m["message-id"]} {m["symbol"]}', "message": m["message"]}
            for m in json.loads(out or "[]")], dt


def bandit():
    out, dt = run([sys.executable, "-m", "bandit", "-f", "json", "-q", *paths])
    return [{"file": r["filename"].replace("\\", "/").split("/")[-1], "line": r["line_number"],
             "rule": r["test_id"], "message": r["issue_text"]}
            for r in json.loads(out)["results"]], dt


def ruff():
    out, dt = run([sys.executable, "-m", "ruff", "check", "--select", "F,B,S",
                   "--output-format", "json", "--no-cache", *paths])
    return [{"file": r["filename"].replace("\\", "/").split("/")[-1], "line": r["location"]["row"],
             "rule": r["code"], "message": r["message"]} for r in json.loads(out)], dt


for name, fn in [("pylint", pylint), ("bandit", bandit), ("ruff", ruff)]:
    findings, dt = fn()
    (RESULTS / f"static_{name}.json").write_text(json.dumps(
        {"tool": name, "seconds": round(dt, 2), "findings": findings}, indent=1))
    print(name, len(findings), "findings", round(dt, 2), "s")
