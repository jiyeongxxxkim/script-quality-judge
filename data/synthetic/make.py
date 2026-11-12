# -*- coding: utf-8 -*-
"""합성 데이터 생성: base.json(규칙 검사용 기본 대본), degraded.json(합성 훼손).
라벨링된 17개는 사용하지 않는다(검증용). 실행: python3 data/synthetic/make.py"""
import json, re, pathlib

OUT = pathlib.Path(__file__).parent
A = [  # 전기요금 (뉴스체, 요체/습니다체가 섞인 허술한 문장)
 "다음 달부터 가정용 전기요금이 킬로와트시당 5원 오른다는 소식이 전해졌어요.",
 "한국전력은 연료비 부담이 커져서 어쩔 수 없었다고 설명했습니다.",
 "4인 가구 기준으로 한 달에 2,000원 정도 더 내게되는 셈입니다.",
 "정부는 취약계층에는 요금 할인을 그대로 유지하겠다고 밝혔죠.",
 "근데 소비자단체는 인상 폭이 너무 갑작스럽다며 반발하고 있습니다.",
 "전문가들은 겨울철 난방 수요가 몰리면 체감 부담이 더 커질 수 있다고 말합니다.",
 "한전은 누적 적자가 아직 크다며 추가 인상 가능성도 열어뒀어요.",
 "다음 분기 요금은 연료비 추이를 보고 다시 정해질 예정입니다.",
 "업계에서는 이번 인상이 다른 공공요금에 번질지 지켜보는 분위기예요.",
 "정부는 물가 상황을 점검하는 회의를 매주 열겠다고 했습니다.",
 "당장 내일부터 신청 창구가 열리니 할인 대상인지 먼저 확인해 보세요.",
 "자세한 내용은 한전 누리집에서 볼 수 있다고 합니다.",
]
B = [  # 앱 후기 (인상률 %가 들어간 문장 포함)
 "이 사진 정리 앱은 폴더를 직접 만들 필요가 없어서 편하다는 후기가 많아요.",
 "출시 첫 달에만 내려받은 사람이 12만 명을 넘었다고 합니다.",
 "사용자의 38%가 정리 기능 때문에 쓴다고 답했습니다.",
 "다만 무료 버전은 광고가 자주 떠서 거슬린다는 의견도 있어요.",
 "유료로 바꾸면 광고가 사라지고 한 달에 5,000원이 듭니다.",
 "개발사는 다음 업데이트에서 광고 빈도를 줄이겠다고 했습니다.",
]
j = lambda *p: " ".join(p)
BODY = A[:5]

base = [
 dict(id="S01", note="짧고 허술하지만 결격 없음(요체·습니다체 혼용, 띄어쓰기 오류)", text=j(*A[:5]),
      expect=dict(M1="pass", M3="pass", M4="pass", verdict="통과")),
 dict(id="S02", note="중간 길이 정상", text=j(*A[:8]),
      expect=dict(M1="pass", M3="pass", M4="pass", verdict="통과")),
 dict(id="S03", note="분량 45~60초(minor 1개)", text=j(*A[:11]),
      expect=dict(M1="minor", M3="pass", M4="pass", verdict="통과")),
 dict(id="S04", note="분량 60초 초과(fatal)", text=j(*A, *B[:2], *A[:3]),
      expect=dict(M1="fatal", M3="pass", M4="pass", verdict="실패")),
 dict(id="S05", note="숫자 훼손 1개만", text=j(*B[:3]).replace("38%", "38.%") + " " + B[3],
      expect=dict(M1="pass", M3="warn", M4="pass", verdict="통과")),
 dict(id="S06", note="숫자 훼손 + 존대→반말(minor 2개)", text=j(*B[:3]).replace("12만 명", "12만 명") .replace("38%", "38.%") + " 광고가 너무 많아서 별로다. 그냥 참고 쓰자.",
      expect=dict(M1="pass", M3="warn", M4="warn", verdict="보류")),
 dict(id="S07", note="존대→반말 1개만", text=j(*A[:4]) + " 솔직히 좀 비싼 것 같다. 그래도 어쩔 수 없지.",
      expect=dict(M1="pass", M3="pass", M4="warn", verdict="통과")),
 dict(id="S08", note="분량 minor + 존대→반말", text=j(*A[:11]) + " 이거 진짜 별로다.",
      expect=dict(M1="minor", M3="pass", M4="warn", verdict="보류")),
 dict(id="S09", note="따옴표 안 반말(정상)", text='시장에서는 "이번 인상은 시작일 뿐이야"라는 말이 나왔다고 합니다. ' + j(*A[1:4]),
      expect=dict(M1="pass", M3="pass", M4="pass", verdict="통과")),
 dict(id="S10", note="명사형 종결 섞임(중립)", text=j(*A[:3]) + " 인상 폭은 5원임. 적용 시기는 다음 달 1일부터임.",
      expect=dict(M1="pass", M3="pass", M4="pass", verdict="통과")),
 dict(id="S11", note="구두점 없음 + 습니다→반말 전환(80자 이상)",
      text=re.sub(r"[.?!]", "", j(*A[1:3], *A[7:8])) + " 근데 이게 맞냐",
      expect=dict(M1="pass", M3="pass", M4="warn", verdict="통과")),
 dict(id="S12", note="한 문장이 80자 이상(정보용)", text=A[0] + " 한국전력은 연료비 부담이 커졌고 환율도 올랐고 적자도 쌓였다는 이유를 들었는데 이 설명이 충분한지는 사람마다 평가가 다르고 정부도 아직 구체적인 입장을 내놓지 않았다고 합니다. " + A[7],
      expect=dict(M1="pass", M3="pass", M4="pass", verdict="통과", long_min=1)),
 dict(id="S13", note="fatal + minor 여러 개(실패가 우선)", text=j(*A, *B, *A[:2]).replace("38%", "38.%") + " 정말 별로다.",
      expect=dict(M1="fatal", M3="warn", M4="warn", verdict="실패")),
]

# 정규식 반례. truth=완벽한 검사기라면 경고해야 하는지, known=현재 규칙이 어긋난다고 알려진 방향
m3_cases = [
 ("12.% 늘었다", True, None), ("3%% 가까이", True, None), ("1,,2", True, None), ("5.\n%", True, None), ("50 .%", True, None),
 ("7.7% 늘었다", False, None),
 ("버전 2.0. %s 포맷", False, "FP"),
 ("70..%", True, "FN"), ("영업손실은 %나 확대", True, "FN"), ("70퍼센트센트", True, "FN"),
]
m4_cases = [
 ("앱이 편리합니다. 근데 광고가 많다. 그냥 쓰자.", True, None),
 ("날씨 좋죠. 같이 가요. 기대돼요.", False, None),
 ("참았답니다. 대단하죠. 그랬습니다.", False, None),
 ("가격은 3만 원임. 가볍습니다.", False, None),
 ("꼬리가 길면 도움이 되고 땅에서는 필요가 없어서 짧아졌습니다 정말 귀엽지", True, "FN"),
 ("그는 집에 갔다. 나는 남았습니다.", True, None),
 ('그는 "집에 가자"라고 했습니다. 이후 조용했습니다.', False, None),
]

# ---- 합성 훼손: (base id, 연산) -> 기대 항목
def garble(t): return re.sub(r"(\d+)%", r"\1.%", t, count=1)
def double_pct(t): return t.replace("%", "%%", 1)
def banmal_tail(t):
    r = re.sub(r"(입니다|습니다|해요|예요|어요|보세요|합니다)\.?$", "다.", t.rstrip())
    assert r != t.rstrip(), "banmal_tail이 적용되지 않음: " + t[-20:]   # 훼손 연산이 실제로 적용됐는지 확인
    return r
def strip_punct(t): return re.sub(r"[.?!]", "", t)
def pad(t, extra): return t + " " + j(*extra)
by = {c["id"]: c["text"] for c in base}
deg = [
 dict(id="D01", src="S01", op="garble", text=garble(j(*B[:3])), expect=dict(M3="warn", verdict="통과")),
 dict(id="D02", src="S01", op="double_pct", text=double_pct(j(*B[:3])), expect=dict(M3="warn", verdict="통과")),
 dict(id="D03", src="S02", op="banmal_tail", text=banmal_tail(by["S02"]), expect=dict(M4="warn", verdict="통과")),
 dict(id="D04", src="S02", op="garble+banmal_tail", text=banmal_tail(garble(by["S02"] + " " + B[2])), expect=dict(M3="warn", M4="warn", verdict="보류")),
 dict(id="D05", src="S02", op="pad_to_minor", text=pad(by["S02"], A[8:11]), expect=dict(M1="minor", verdict="통과")),
 dict(id="D06", src="S02", op="pad_to_fatal", text=pad(by["S02"], A[8:] + B[:3] + A[:3]), expect=dict(M1="fatal", verdict="실패")),
 dict(id="D07", src="S02", op="strip_punct", text=strip_punct(by["S02"]), expect=dict(M4="pass", verdict="통과")),
 dict(id="D08", src="S02", op="strip_punct+banmal_tail", text=strip_punct(banmal_tail(by["S02"])), expect=dict(M4="warn", verdict="통과")),
 dict(id="D09", src="S02", op="pad_minor+banmal_tail", text=banmal_tail(pad(by["S02"], A[8:11])), expect=dict(M1="minor", M4="warn", verdict="보류")),
]

# LLM 단계용 훼손 (원문 대비). 규칙 단계에서는 실행하지 않는다.
llm = [
 dict(id="Q01", op="F1 유보→단정", source="전문가들은 이번 인상이 소비를 위축시킬 수 있다고 내다봤다.", text="이번 인상은 소비를 위축시킵니다.", expect=dict(F1="warn")),
 dict(id="Q02", op="F1+R1 효과 단정", source="시험에서 일부 참가자의 혈압이 낮아지는 경향이 관찰됐다.", text="이 차를 마시면 혈압이 내려갑니다.", expect=dict(F1="warn", R1="warn")),
 dict(id="Q03", op="F3 없던 내용 추가", source="새 보조배터리는 무게가 320g이다.", text="새 보조배터리는 320g입니다. 써본 사람들은 이틀은 간다고 해요.", expect=dict(F3="warn")),
 dict(id="Q04", op="F3 숫자 변경(M2 힌트)", source="이번 인상으로 4인 가구는 월 2,000원을 더 낸다.", text="이번 인상으로 4인 가구는 월 3,000원을 더 냅니다.", expect=dict(M2="mismatch", F3="fatal", verdict="실패")),
 dict(id="Q05", op="후기만 추가(치명 아님)", source="새 청소기는 흡입력이 두 단계로 조절된다.", text="새 청소기는 흡입력을 두 단계로 조절해요. 써본 사람들은 조용해서 좋대요.", expect=dict(F3="minor", verdict="통과")),
 dict(id="Q06", op="건강 효과 추가(치명)", source="이 두유는 국산 콩으로 만들었다.", text="이 두유는 국산 콩으로 만들었어요. 매일 마시면 콜레스테롤이 내려갑니다.", expect=dict(F3="fatal", verdict="실패")),
 dict(id="Q07", op="원문에 없는 수치 추가", source="시는 올해 자전거도로를 새로 냈다.", text="시는 올해 자전거도로를 새로 냈고 이용자가 40% 늘었어요.", expect=dict(M2="mismatch", F3="fatal", verdict="실패")),
 dict(id="Q08", op="정상(표기만 다름)", source="새 모델은 무게가 320g이고 가격은 12만 원이다.", text="새 모델은 무게가 320그램이고, 가격은 120,000원이에요.", expect=dict(F3="pass", verdict="통과")),
]
for name, obj in [("base", dict(base=base, m3_cases=m3_cases, m4_cases=m4_cases)), ("degraded", dict(degraded=deg, llm=llm))]:
    (OUT / f"{name}.json").write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")

# ---- LLM 항목 확인용 합성 세트(llm2.json). 판정이 아니라 항목 단위로 확인한다.
T = ["시립도서관이 다음 달 새 건물로 이전합니다.", "열람석은 기존보다 두 배로 늘어납니다.", "어린이 자료실은 1층에 따로 마련됩니다.",
     "개관 첫 주에는 대출 한도도 늘려 준다고 해요.", "이용 시간은 평일 아홉 시부터 저녁 여덟 시까지입니다."]
C = " ".join(T)
ALL = "ALL"   # 모든 LLM 항목(F/R/N)이 pass여야 함
def case(id, group, text, expect, source=None): return dict(id=id, group=group, text=text, source=source, expect=expect)
llm2 = [
 case("N1p1", "N1 진짜", j(T[0], "헐 저거 진짜 크다 ㅋㅋ", T[1], T[2]), {"N1": "warn"}),
 case("N1p2", "N1 진짜", j(T[0], T[1], "자막: 지금 보시는 화면은 신관 로비입니다.", T[2]), {"N1": "warn"}),
 case("N1p3", "N1 진짜", j(T[0], "여기 화면 보시면 열람석이 보이시죠?", T[1], T[4]), {"N1": "warn"}),
 case("N1p4", "N1 진짜", j(T[0], T[1], T[2], "댓글: 저는 벌써 설레요!"), {"N1": "warn"}),
 case("N1n1", "N1 아님", j(T[0], '이용객들은 "대박이다"라며 반겼다고 합니다.', T[1]), {"N1": "pass"}),
 case("N1n2", "N1 아님", j(T[0], "과연 얼마나 달라질까요?", T[1], T[2]), {"N1": "pass"}),
 case("N1n3", "N1 아님", j(T[0], "열람석이 두 배라니, 꽤 큰 변화죠.", T[2]), {"N1": "pass"}),
 case("N1n4", "N1 아님", j(T[0], "사실 이게 꽤 반가운 소식이거든요.", T[4]), {"N1": "pass"}),
 case("C0", "통제(결함 없음)", C, {ALL: "pass"}),
 case("R2d", "훼손 R2", j(C, "도서관 관장 한 명이 한마디 하자 이전 논란은 완전히 끝났습니다."), {"R2": "warn"}),
 case("N2d", "훼손 N2", j(C, "그래서 밤 열 시까지도 이용할 수 있어요."), {"N2": "warn"}),
 case("N3d", "훼손 N3", j(C, "이전을 반대하는 주민들은 변화가 두려운 한심한 사람들입니다."), {"N3": "warn"}),
 case("R1b", "훼손 R1(보증·수치)", j(C, "이용자 만족도 98%를 보장합니다."), {"R1": "warn"}),
 case("R1c", "훼손 R1(전문가 추천)", j(C, "사서 전문가들이 모두 이곳을 추천합니다."), {"R1": "warn"}),
 case("R1e1", "R1 경계(안전)", j(C, "새 보도블록은 낙상 사고를 막아 줍니다."), {"R1": "warn", "NOFATAL": "R1"}),
 case("R1e2", "R1 경계(폭염)", j(C, "그늘막은 폭염 피해를 줄여 줍니다."), {"R1": "warn", "NOFATAL": "R1"}),
 case("R1a", "훼손 R1 치명(건강)", j(C, "이 도서관을 다니면 시력이 좋아지고 치매가 예방됩니다."), {"R1": "fatal"}),
]
PA = "시는 이르면 다음 달 신청사 이전 일정을 확정할 것으로 보인다. 한 시의원은 이전이 시민 편의를 높일 것이라고 주장했다. 이전 비용은 약 300억 원으로 추산된다."
PB = "구는 올해 안에 공원 두 곳에 그늘막을 설치할 계획이다. 구청 관계자는 설치 시기가 예산 심의 결과에 따라 달라질 수 있다고 밝혔다. 한 주민 단체는 그늘막이 폭염 피해를 줄일 것이라고 말했다."
PC = "시는 노선 개편으로 출근 시간 배차 간격이 줄어들 수 있다고 전망했다. 다만 운전기사 부족 때문에 효과가 제한될 수 있다고 덧붙였다. 개편안은 다음 달 의회에 보고된다."
llm2 += [
 case("PA0", "통제(원문 일치)", "시는 이르면 다음 달 신청사 이전 일정을 정할 것으로 보여요. 한 시의원은 시민 편의가 높아질 거라고 주장했습니다. 비용은 약 300억 원으로 추산돼요.", {ALL: "pass"}, PA),
 case("PA1", "훼손 F1", "시는 다음 달 신청사 이전 일정을 확정합니다. 한 시의원은 시민 편의가 높아질 거라고 주장했습니다. 비용은 약 300억 원으로 추산돼요.", {"F1": "warn"}, PA),
 case("PA2", "훼손 F2", "시는 이르면 다음 달 신청사 이전 일정을 정할 것으로 보여요. 이전은 시민 편의를 높입니다. 비용은 약 300억 원으로 추산돼요.", {"F2": "warn"}, PA),
 case("PB0", "통제(원문 일치)", "구는 올해 안에 공원 두 곳에 그늘막을 설치할 계획이에요. 시기는 예산 심의 결과에 따라 달라질 수 있다고 합니다. 한 주민 단체는 폭염 피해가 줄 거라고 말했어요.", {ALL: "pass"}, PB),
 case("PB1", "훼손 F1", "구는 올해 안에 공원 두 곳에 그늘막을 설치합니다. 한 주민 단체는 폭염 피해가 줄 거라고 말했어요.", {"F1": "warn"}, PB),
 case("PB2", "훼손 F2", "구는 올해 안에 공원 두 곳에 그늘막을 설치할 계획이에요. 시기는 예산 심의 결과에 따라 달라질 수 있다고 합니다. 그늘막은 폭염 피해를 줄여 줍니다.", {"F2": "warn"}, PB),
 case("PC0", "통제(원문 일치)", "시는 노선 개편으로 출근 시간 배차 간격이 줄어들 수 있다고 전망했어요. 다만 운전기사가 부족해서 효과는 제한될 수 있다고 합니다. 개편안은 다음 달 의회에 보고됩니다.", {ALL: "pass"}, PC),
 case("PC1", "훼손 F1", "노선 개편으로 출근 시간 배차 간격이 줄어듭니다. 개편안은 다음 달 의회에 보고됩니다.", {"F1": "warn"}, PC),
]
(OUT / "llm2.json").write_text(json.dumps(llm2, ensure_ascii=False, indent=1), encoding="utf-8")
for c in base + deg: print(c["id"], len(c["text"]), round(len(c["text"]) / 7.3, 1), c["text"][:34].replace("\n", " "))
