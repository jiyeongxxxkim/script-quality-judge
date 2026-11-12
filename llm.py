# -*- coding: utf-8 -*-
"""OpenAI 호출 래퍼. 키는 .env 또는 환경변수에서만 읽는다. 결과는 results/cache/에 저장해 같은 입력은 다시 호출하지 않는다."""
import hashlib, json, os, pathlib, time, urllib.request, urllib.error

ROOT = pathlib.Path(__file__).parent
CACHE = ROOT / "results" / "cache"
USED = set()   # 이번 실행에서 사용한 캐시 키(공개용 캐시 선별에 사용)


def _env():
    f = ROOT / ".env"
    if f.exists():
        for line in f.read_text(encoding="utf-8").splitlines():
            k, _, v = line.partition("=")
            if k.strip() and not line.lstrip().startswith("#"):
                os.environ.setdefault(k.strip(), v.strip())


def call_llm(system, user, run=0, model=None):
    """system, user -> (dict, meta). run은 반복 번호(재현성 측정용, 캐시 키에 포함). 온도는 보내지 않는다."""
    _env()   # 키가 없어도 캐시된 결과는 재생할 수 있다. 키는 실제 호출 직전에 확인한다.
    model = model or os.environ.get("OPENAI_MODEL", "gpt-5")
    key = hashlib.sha256(json.dumps([model, system, user, run], ensure_ascii=False).encode()).hexdigest()[:20]
    USED.add(key)
    path = CACHE / f"{key}.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8")), {"cached": True}
    if not os.environ.get("OPENAI_API_KEY"):
        raise SystemExit("캐시에 없는 입력입니다. OPENAI_API_KEY를 .env 또는 환경변수에 설정하세요.")
    body = {"model": model, "response_format": {"type": "json_object"},
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}
    req = urllib.request.Request("https://api.openai.com/v1/chat/completions", json.dumps(body).encode(),
                                 {"Authorization": "Bearer " + os.environ["OPENAI_API_KEY"], "Content-Type": "application/json"})
    t0 = time.time()
    try:
        resp = json.load(urllib.request.urlopen(req, timeout=180))
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"OpenAI {e.code}: {e.read().decode()[:500]}") from None   # 응답 본문에는 키가 없다
    out = json.loads(resp["choices"][0]["message"]["content"])
    meta = {"cached": False, "model": resp.get("model"), "usage": resp.get("usage"), "sec": round(time.time() - t0, 1)}
    CACHE.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    (CACHE / f"{key}.meta.json").write_text(json.dumps({**meta, "run": run, "date": time.strftime("%Y-%m-%d %H:%M")}, ensure_ascii=False), encoding="utf-8")
    return out, meta


if __name__ == "__main__":   # 연결 확인: 합성 문장 하나만 보낸다
    r, m = call_llm('JSON으로만 답해. 형식: {"ok": true, "echo": "<입력>"}', "안녕")
    print(r, m)
