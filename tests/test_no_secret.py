# -*- coding: utf-8 -*-
"""제출 전 안전 점검: .env가 무시되는지, 저장소 파일에 API 키 모양 문자열이 없는지. 실행: python3 -I tests/test_no_secret.py"""
import re, sys, pathlib
ROOT = pathlib.Path(__file__).parent.parent
ign = (ROOT / ".gitignore").read_text(encoding="utf-8").split()
bad = [f"{p} 이(가) .gitignore에 없음" for p in (".env", "data/private/") if p not in ign]
KEY = re.compile(r"sk-[A-Za-z0-9_\-]{20,}")
for f in ROOT.rglob("*"):
    if f.is_file() and f.name != ".env" and ".git" not in f.parts and f.suffix not in {".pyc"}:
        try: t = f.read_text(encoding="utf-8")
        except UnicodeDecodeError: continue
        if KEY.search(t): bad.append(f"API 키 모양 문자열: {f.relative_to(ROOT)}")
print("실패" if bad else "ok", *bad, sep="\n  ")
sys.exit(1 if bad else 0)
