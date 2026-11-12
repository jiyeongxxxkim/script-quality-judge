# -*- coding: utf-8 -*-
"""규칙 검사 M1~M4와 집계 (DESIGN.md 2절 판정 방식). LLM 항목은 같은 형식의 dict로 aggregate()에 넘긴다."""
import re

CPS = 7.3                    # 공백 포함 글자 수 / 초. 근거가 두 점뿐이라 쇼츠 실측으로 재보정 필요
WARN_SEC, FATAL_SEC = 45, 60
LONG_SENT = 80               # 정보용


def split_sentences(t):
    out = []
    for p in re.split(r'(?<=[.?!])\s+|\n+', t):
        if len(p) > 80 and not re.search(r'[.?!]', p):   # 구두점 없는 긴 덩어리만 존대 종결 뒤에서 추가 분리
            out += re.split(r'(?:(?<=니다)|(?<=까요)|(?<=네요)|(?<=죠))\s+', p)
        else:
            out.append(p)
    return [x for x in out if x.strip()]


def m1(t):
    sec = round(len(t) / CPS, 1)
    if sec > FATAL_SEC:
        return {"status": "warn", "severity": "fatal", "value": sec}
    if sec > WARN_SEC:
        return {"status": "warn", "severity": "minor", "value": sec}
    return {"status": "pass", "value": sec}


M3_PATTERNS = [r'\d\s*\.\s*%', r'%\s*%', r'\d,\s*,']

def m3(t):
    hits = [m.group() for p in M3_PATTERNS for m in re.finditer(p, t)]
    return {"status": "warn", "severity": "minor", "evidence": hits} if hits else {"status": "pass"}


def _strip_quotes(t):
    return re.sub(r'["“”‘’「」『』][^"“”‘’「」『』]*["“”‘’「」『』]', '', t)

def _ending(s):
    s = re.sub(r'[\s.?!…~"“”\'‘’)\]]+$', '', s)
    if re.search(r'(니다|니까|요|죠)$', s):
        return 'P'
    if re.search(r'(다|냐|야|어|지|자|라|네|군|걸|래|거든|잖아|까)$', s):
        return 'B'
    return 'N'               # 명사형·연결어미 등은 중립

def m4(t):
    ends = [(_ending(s), s) for s in split_sentences(_strip_quotes(t))]
    if {k for k, _ in ends} >= {'P', 'B'}:
        return {"status": "warn", "severity": "minor", "evidence": [s for k, s in ends if k == 'B']}
    return {"status": "pass"}


_NUM = r'\d[\d,]*(?:\.\d+)?'
_UNIT = r'(%|원|명|대|건|배|개|곳|kg|km|그램|g|초|분|시간|일|월|년)?'
_TOK = re.compile(r'((?:' + _NUM + r'\s*[조억만]\s*)+)' + _UNIT + '|(' + _NUM + r')\s*' + _UNIT)
_SCALE = {'조': 1e12, '억': 1e8, '만': 1e4}

def numbers(t):
    out = set()
    for m in _TOK.finditer(t):
        if m.group(1):
            v = sum(float(n.replace(',', '')) * _SCALE[u] for n, u in re.findall('(' + _NUM + r')\s*([조억만])', m.group(1)))
            out.add((v, m.group(2) or ''))
        else:
            out.add((float(m.group(3).replace(',', '')), m.group(4) or ''))
    return out

def m2(script, source):
    """대본에만 있는 숫자. LLM① 힌트용이며 판정에는 쓰지 않는다."""
    return sorted(numbers(script) - numbers(source))


def sentence_info(t):
    L = [len(s) for s in split_sentences(t)]
    return {"max": max(L), "mean": round(sum(L) / len(L), 1), "long": sum(n >= LONG_SENT for n in L)}


def aggregate(items):
    """items: {id: {status, severity?, confidence?}} -> (verdict, fatal, low_confidence_ids)"""
    warns = [v for v in items.values() if v["status"] == "warn"]
    low = [k for k, v in items.items() if v.get("confidence") == "low"]
    if any(v.get("severity") == "fatal" for v in warns):
        return "실패", True, low
    minors = sum(v.get("severity") == "minor" for v in warns)
    return ("보류" if minors >= 2 or low else "통과"), False, low


def judge_rules(script, source=None):
    items = {"M1": m1(script), "M3": m3(script), "M4": m4(script)}
    verdict, fatal, low = aggregate(items)
    r = {"verdict": verdict, "fatal": fatal, "items": items, "low_confidence_items": low, "info": sentence_info(script)}
    if source:
        r["m2_hint"] = m2(script, source)
    return r


if __name__ == "__main__":
    import json, sys
    print(json.dumps(judge_rules(sys.stdin.read().strip()), ensure_ascii=False, indent=1))
