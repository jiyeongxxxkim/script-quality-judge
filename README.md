# 대본 품질 판정기

생성된 쇼츠 대본을 렌더링 전에 **통과 / 보류 / 실패**로 판정한다. 규칙 검사 + LLM 2회 호출. 점수 대신 항목별 상태와 근거를 낸다.
기준·설계·결정 기록: `DESIGN.md`, 구현·검증·테스트 결과: `docs/validation.md`.

## 요구사항
Python 3.9+ (표준 라이브러리만 사용, 설치할 것 없음)

## 실행
```bash
# 1) 규칙 검사만 (키 불필요): 분량·숫자 훼손·존대 전환
echo "대본 텍스트" | python3 judge.py

# 2) 테스트 (키 불필요)
python3 -I tests/test_rules.py        # 설계대로 동작하는지 (경계값, 반례, 합성 대본 13개)
python3 -I tests/run_degraded.py      # 규칙 단계 합성 훼손 9건
python3 -I tests/test_no_secret.py    # 제출 전 키 유출 점검

# 3) 전체 파이프라인 (LLM 포함)
echo "대본 텍스트" | python3 pipeline.py
```
원문 대조까지 하려면 파이썬에서 `pipeline.judge(script, source)`를 호출한다.

## LLM 호출과 키
- `.env.example`을 `.env`로 복사하고 `OPENAI_API_KEY`를 채운다 (`.env`는 `.gitignore`에 있어 올라가지 않는다). 모델은 `OPENAI_MODEL`(기본 `gpt-5`).
- **키 없이도 캐시된 결과를 재생할 수 있다.** 호출 결과는 `results/cache/`에 저장되어 있고, 같은 입력이면 API를 부르지 않는다. 캐시에 없는 새 입력만 키가 필요하다.
- 온도는 보내지 않는다 (이 모델이 기본값 외 온도를 거부함). 재현성은 반복 실행으로 측정했다.

## 재현
```bash
python3 -I tests/run_synth2.py     # LLM 항목 합성 세트 23개 × 3회 (캐시 재생 시 무료)
python3 -I tests/run_repro.py      # 재현성 21개 × 3회
python3 data/synthetic/make.py     # 합성 데이터 재생성
```
`validation/run_labels.py`는 사람이 라벨링한 17개를 쓴다. 제3자 기사·영상 대본이 포함되어 있어 대본·원문 전문과 그 실행 캐시, 모델이 쓴 판정 이유는 저장소에 올리지 않았다. 평가자가 직접 실행할 수는 없고, 요약 결과만 `results/validation.json`에 있다. `results/cache/`에는 합성 데이터 실행 결과만 들어 있다.

## 구성
```
judge.py      규칙 M1~M4, 집계          prompts.py  LLM 지시문·예시
llm.py        OpenAI 호출·캐시          pipeline.py 전체 파이프라인
data/synthetic/  합성 대본·훼손 데이터   tests/      테스트
validation/   17개 라벨 검증 스크립트     results/    실행 결과·캐시
```
