# -*- coding: utf-8 -*-
"""최종 검증: 사람이 라벨링한 17개에 판정기를 돌려 비교한다(구현 중에는 사용하지 않음).
라벨 CSV는 저장소에 없다. 실행: python3 -I validation/run_labels.py <라벨 CSV 경로>
열: 이름, 대본, 라벨, 입력원문, 치명. 결과: results/validation.json (대본·원문 전문은 저장하지 않음)"""
import sys, csv, json, pathlib
from concurrent.futures import ThreadPoolExecutor
ROOT = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
import pipeline

rows = list(csv.DictReader(open(sys.argv[1], encoding="utf-8-sig")))
rows = [r for r in rows if r["라벨"].strip()]
short = lambda v: v[:2]

def one(a):
    r, run = a
    src = r["입력원문"].strip()
    src = None if src in ("", "(없음)") else src   # 쇼츠는 입력 원문이 없다(최초 실행에서 "(없음)"을 원문으로 넘긴 버그 수정)
    res = pipeline.judge(r["대본"].strip(), src, run)
    return r["이름"], run, res

with ThreadPoolExecutor(4) as ex: out = list(ex.map(one, [(r, k) for r in rows for k in range(3)]))
by = {}
for i, run, res in out: by.setdefault(i, {})[run] = res
lab = {r["이름"]: r for r in rows}
summary, correct, same = {}, 0, 0
for i, r in lab.items():
    runs = by[i]; preds = [short(runs[k]["verdict"]) for k in range(3)]
    flags = {k: v.get("severity", "") for k, v in runs[0]["items"].items() if v["status"] == "warn"}
    ok = preds[0] == r["라벨"].strip(); correct += ok; same += len(set(preds)) == 1
    summary[i] = dict(label=r["라벨"].strip(), fatal_label=r["치명"].strip(), pred=preds, ok=ok, flags=flags,
                      reasons={k: v.get("reason", "") for k, v in runs[0]["items"].items() if v["status"] == "warn" and k[0] in "FRN"},
                      low=runs[0]["low_confidence_items"], m1=runs[0]["items"]["M1"].get("value"))
    print(i, r["라벨"].strip(), "→", preds, "✓" if ok else "✗", flags, flush=True)
labels = [s["label"] for s in summary.values()]
print(f"\n일치(1회차) {correct}/{len(summary)}, 3회 판정 동일 {same}/{len(summary)}")
cm = {}
for s in summary.values(): cm[(s["label"], s["pred"][0])] = cm.get((s["label"], s["pred"][0]), 0) + 1
print("혼동(라벨,예측):", {f"{a}->{b}": n for (a, b), n in sorted(cm.items())})
# 공개용: reason(원문 인용 가능)을 뺀 요약. 전체는 results/private/(저장소 제외)
(ROOT / "results/private").mkdir(exist_ok=True)
(ROOT / "results/private/validation.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
pub = {k: {a: b for a, b in v.items() if a != "reasons"} for k, v in summary.items()}
(ROOT / "results/validation.json").write_text(json.dumps(pub, ensure_ascii=False, indent=1), encoding="utf-8")
