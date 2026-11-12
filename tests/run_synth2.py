# -*- coding: utf-8 -*-
"""LLM 항목 확인: 진짜 N1·N1 아님·훼손(R1/R2/N2/N3/F1/F2)·통제를 항목 단위로 3회 돌린다. 결과: results/synth2.json. 실행: python3 -I tests/run_synth2.py"""
import sys, json, pathlib
from concurrent.futures import ThreadPoolExecutor
ROOT = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
import pipeline
cases = json.loads((ROOT / "data/synthetic/llm2.json").read_text(encoding="utf-8"))
LLM = ["F1", "F2", "F3", "R1", "R2", "N1", "N2", "N3"]

def status(it):
    return "pass" if it["status"] == "pass" else it.get("severity") == "fatal" and "fatal" or "warn"

def one(a):
    c, run = a
    r = pipeline.judge(c["text"], c["source"], run)
    return c["id"], run, {k: status(v) for k, v in r["items"].items() if k in LLM and v["status"] != "not_assessed"}

with ThreadPoolExecutor(4) as ex: rows = list(ex.map(one, [(c, r) for c in cases for r in range(3)]))
res = {}
for cid, run, st in rows: res.setdefault(cid, []).append(st)
(ROOT / "results/synth2.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
tot = {}
for c in cases:
    runs = res[c["id"]]; ok = 0; detail = []
    for st in runs:
        good = True
        for k, want in c["expect"].items():
            if k == "NOFATAL": good &= st.get(want) != "fatal"
            elif k == "ALL": good &= all(v == "pass" for v in st.values())
            elif want == "warn": good &= st.get(k) in ("warn", "fatal")
            else: good &= st.get(k) == want
        ok += good
        detail.append("".join(f"{k}:{v} " for k, v in st.items() if v != "pass") or "-")
    tot.setdefault(c["group"], []).append(ok)
    print(c["id"], c["group"], f"{ok}/3", "|", " / ".join(detail), flush=True)
print()
for g, v in tot.items(): print(f"{g}: {sum(v)}/{3 * len(v)}", flush=True)
