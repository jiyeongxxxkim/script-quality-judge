# -*- coding: utf-8 -*-
"""전체 파이프라인: 규칙(M1~M4) + LLM①(원문 대조) + LLM②(읽기·위험) -> 집계 (DESIGN.md 2절 판정 방식)."""
import json, re, sys
from judge import judge_rules, aggregate, m2
from llm import call_llm
from prompts import SYSTEM1, SYSTEM2

def _norm(s): return re.sub(r"\s+", "", s)

def _items(res, ids, script):
    out = {}
    for k in ids:
        r = res.get(k) or {}
        if r.get("flag"):
            out[k] = {"status": "warn", "severity": "fatal" if r.get("fatal_candidate") else "minor",
                      "evidence": r.get("evidence", []), "source_quote": r.get("source_quote", []),
                      "reason": r.get("reason", ""), "confidence": r.get("confidence", "low"),
                      # 인용이 대본에 실제로 있는지 기록만 한다(판정에는 미사용)
                      "evidence_ok": all(_norm(e) in _norm(script) for e in r.get("evidence", []))}
        else:
            out[k] = {"status": "pass", "confidence": r.get("confidence", "high")}
    return out

def judge(script, source=None, run=0):
    r = judge_rules(script, source)
    items, usage = dict(r["items"]), []
    ids2 = ["R1", "R2", "N1", "N2", "N3"]
    if source:
        hint = m2(script, source)
        res1, m = call_llm(SYSTEM1, json.dumps({"source": source, "script": script, "numeric_hints": hint}, ensure_ascii=False), run)
        items.update(_items(res1, ["F1", "F2", "F3"], script)); usage.append(m)
    else:
        items.update({k: {"status": "not_assessed"} for k in ["F1", "F2", "F3"]})
    res2, m = call_llm(SYSTEM2, json.dumps({"script": script}, ensure_ascii=False), run)
    items.update(_items(res2, ids2, script)); usage.append(m)
    verdict, fatal, low = aggregate(items)
    h1 = res2.get("H1", {})
    not_eval = [k for k, v in items.items() if v["status"] == "not_assessed"]
    return {"verdict": verdict + ("(충실성 미평가)" if not source and verdict == "통과" else ""), "fatal": fatal,
            "coverage": {"evaluated": [k for k in items if k not in not_eval], "not_evaluated": not_eval},
            "items": items, "low_confidence_items": low, "hook": h1, "info": r["info"],
            "m2_hint": r.get("m2_hint"), "usage": usage}

if __name__ == "__main__":
    s = sys.stdin.read().strip()
    print(json.dumps(judge(s), ensure_ascii=False, indent=1))
