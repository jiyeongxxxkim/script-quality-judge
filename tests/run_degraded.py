# -*- coding: utf-8 -*-
"""합성 훼손 데이터를 규칙 단계로 돌려 기대와 비교(LLM 훼손 Q01~Q04는 LLM 단계 대기). 실행: python3 -I tests/run_degraded.py"""
import sys, json, pathlib
ROOT = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
from judge import judge_rules, m2

d = json.loads((ROOT / "data/synthetic/degraded.json").read_text(encoding="utf-8"))
miss = 0
for c in d["degraded"]:
    r = judge_rules(c["text"]); res = []
    for k, v in c["expect"].items():
        if k == "verdict": got = r["verdict"]
        else: got = r["items"][k].get("severity", r["items"][k]["status"]) if k == "M1" else r["items"][k]["status"]
        res.append((k, v, got, "✓" if got == v else "✗"))
    miss += any(x[3] == "✗" for x in res)
    print(c["id"], c["src"], c["op"].ljust(26), " ".join(f"{k}:{g}{'' if m == '✓' else '(기대 ' + v + ')'}" for k, v, g, m in res), "" if all(x[3] == "✓" for x in res) else "← 불일치")
for c in d["llm"]:
    print(c["id"], c["op"], "LLM 대기", "| M2 힌트:", m2(c["text"], c["source"]))
print(f"규칙 단계 훼손 {len(d['degraded'])}건 중 기대와 다른 것 {miss}건")
