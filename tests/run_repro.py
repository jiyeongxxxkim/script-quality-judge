# -*- coding: utf-8 -*-
"""재현성: 같은 입력을 3회(run 0,1,2) 돌려 판정·항목 상태가 같은지 본다. 결과: results/repro.json. 실행: python3 -I tests/run_repro.py"""
import sys, json, pathlib
from concurrent.futures import ThreadPoolExecutor
ROOT = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
import pipeline

b = json.loads((ROOT / "data/synthetic/base.json").read_text(encoding="utf-8"))["base"]
q = json.loads((ROOT / "data/synthetic/degraded.json").read_text(encoding="utf-8"))["llm"]
cases = [(c["id"], c["text"], None) for c in b] + [(c["id"], c["text"], c["source"]) for c in q]

def sig(r):  # 항목별 (상태, 심각도)
    return {k: (v["status"], v.get("severity")) for k, v in r["items"].items() if k[0] in "FRN" and v["status"] != "not_assessed"}

def one(a):
    (cid, text, src), run = a
    r = pipeline.judge(text, src, run)
    return cid, run, r["verdict"], sig(r), sum((m.get("usage") or {}).get("total_tokens", 0) for m in r["usage"] if not m.get("cached"))

jobs = [(c, run) for c in cases for run in range(3)]
with ThreadPoolExecutor(4) as ex: rows = list(ex.map(one, jobs))
out = {}
for cid, run, v, s, t in rows: out.setdefault(cid, []).append({"run": run, "verdict": v, "items": s, "new_tokens": t})
(ROOT / "results").mkdir(exist_ok=True)
(ROOT / "results/repro.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
same_v = same_i = 0
for cid, rs in out.items():
    vs = {r["verdict"] for r in rs}; its = {json.dumps(r["items"], sort_keys=True) for r in rs}
    same_v += len(vs) == 1; same_i += len(its) == 1
    flags = sorted({k for r in rs for k, x in r["items"].items() if x[0] == "warn"})
    note = "" if len(its) == 1 else " 항목차: " + ", ".join(k for k in flags if len({json.dumps(r["items"].get(k)) for r in rs}) > 1)
    print(cid, [r["verdict"] for r in rs], "" if len(vs) == 1 else "← 판정 흔들림", note, flush=True)
print(f"판정 일치 {same_v}/{len(out)}, 항목 상태까지 일치 {same_i}/{len(out)}, 신규 토큰 {sum(r['new_tokens'] for rs in out.values() for r in rs)}", flush=True)
