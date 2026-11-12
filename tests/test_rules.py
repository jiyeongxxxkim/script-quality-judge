# -*- coding: utf-8 -*-
"""설계대로 동작하는지 검사. 라벨링된 17개는 쓰지 않는다(검증용). 실행: python3 -I tests/test_rules.py"""
import sys, json, pathlib
ROOT = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
from judge import m1, m3, m4, m2, aggregate, judge_rules

def load(n): return json.loads((ROOT / "data/synthetic" / f"{n}.json").read_text(encoding="utf-8"))
bad = []
def ok(c, msg):
    if not c: bad.append(msg)

# --- 경계/집계 단위
ok(m1("가" * 328)["status"] == "pass", "M1 44.9s pass")
ok(m1("가" * 329)["severity"] == "minor", "M1 45.1s minor")
ok(m1("가" * 438)["severity"] == "minor", "M1 60.0s minor")
ok(m1("가" * 439)["severity"] == "fatal", "M1 60.1s fatal")
mn, ft = {"status": "warn", "severity": "minor"}, {"status": "warn", "severity": "fatal"}
ok(aggregate({"a": mn})[0] == "통과", "minor 1 -> 통과")
ok(aggregate({"a": mn, "b": mn})[0] == "보류", "minor 2 -> 보류")
ok(aggregate({"a": ft, "b": mn})[0] == "실패", "fatal -> 실패")
ok(aggregate({"a": {"status": "pass", "confidence": "low"}})[0] == "보류", "low confidence -> 보류")
ok(aggregate({"a": ft, "b": {"status": "pass", "confidence": "low"}})[0] == "실패", "low confidence는 실패 승급 근거 아님/fatal 우선")

# --- M2
ok(m2("월 3,000원을 더 냅니다", "월 2,000원을 더 낸다") == [(3000.0, "원")], "M2 숫자 불일치")
ok(m2("2조 7,600억 원", "2조7600억원") == [], "M2 단위 정규화")
ok(m2("38%", "38 %") == [], "M2 공백")
ok(m2("320그램", "320g") == [(320.0, "그램")] or m2("320그램", "320g") == [], "M2 그램/g 표기는 힌트 수준(알려진 한계)")

# --- 합성 기본 대본
got = []
for c in load("base")["base"]:
    r = judge_rules(c["text"]); e = c["expect"]
    sev = lambda k: r["items"][k].get("severity", r["items"][k]["status"])
    ok(sev("M1") == e["M1"], f'{c["id"]} M1 {sev("M1")}!={e["M1"]}')
    ok(r["items"]["M3"]["status"] == e["M3"], f'{c["id"]} M3')
    ok(r["items"]["M4"]["status"] == e["M4"], f'{c["id"]} M4')
    ok(r["verdict"] == e["verdict"], f'{c["id"]} verdict {r["verdict"]}!={e["verdict"]}')
    ok(r["info"]["long"] >= e.get("long_min", 0), f'{c["id"]} 긴 문장')
    got.append((c["id"], r["verdict"]))

# --- 정규식 반례: truth와 다른 방향이 known에 적힌 것과 일치해야 함(고치면 데이터도 갱신)
b = load("base")
for name, fn, cases in [("M3", m3, b["m3_cases"]), ("M4", m4, b["m4_cases"])]:
    for s, truth, known in cases:
        warned = fn(s)["status"] == "warn"
        dev = None if warned == truth else ("FN" if truth else "FP")
        ok(dev == known, f"{name} 반례 {s!r}: 기대 {known}, 실제 {dev}")

print("실패" if bad else "ok", *bad, sep="\n  ")
sys.exit(1 if bad else 0)
