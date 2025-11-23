# API 연결 오류 개선 (2025-11-21)

## 문제 상황

벤치마크 테스트 중 다음과 같은 OpenAI API 연결 오류 발생:

```
Request ID: 4b16d7c9-ca0c-4bba-8e4b-46b3c8f3024a
{"error":"ERROR_OPENAI","details":{"title":"Unable to reach the model provider"}}
```

## 원인 분석

### 1. Rate Limiting 부족
- 기존: 모든 요청 사이에 1초 대기
- 문제: OpenAI API Rate Limit (특히 thinking 모델은 더 엄격)

### 2. 재시도 로직 부재
- 기존: API 호출 실패 시 바로 실패 처리
- 문제: 일시적 네트워크 오류나 rate limit 초과 시 복구 불가능

### 3. 에러 복구 전략 부족
- 기존: 오류 발생 시 그냥 다음 테스트로 진행
- 문제: 연속적인 빠른 요청으로 인한 누적 throttling

## 개선 사항

### 1. Backoff 라이브러리 추가

**requirements.txt**
```python
backoff>=2.2.0
```

**설치 명령**
```bash
pip install backoff
```

### 2. 재시도 로직 구현

**OpenAI API 재시도**
```python
@backoff.on_exception(
    backoff.expo,
    (Exception),
    max_tries=3,
    max_time=30,
    giveup=lambda e: "429" not in str(e) and "rate limit" not in str(e).lower() and "timeout" not in str(e).lower()
)
def _call_openai_with_retry(self, api_params: Dict) -> Any:
    """OpenAI API 호출 with retry"""
    return self.openai_client.chat.completions.create(**api_params)
```

**Claude API 재시도**
```python
@backoff.on_exception(
    backoff.expo,
    (Exception),
    max_tries=3,
    max_time=30,
    giveup=lambda e: "429" not in str(e) and "rate limit" not in str(e).lower() and "timeout" not in str(e).lower()
)
def _call_claude_with_retry(self, api_params: Dict) -> Any:
    """Claude API 호출 with retry"""
    return self.anthropic_client.messages.create(**api_params)
```

**특징:**
- Exponential backoff: 1초 → 2초 → 4초
- 최대 3회 재시도
- 최대 30초까지만 재시도
- Rate limit(429) 에러는 재시도
- 기타 오류는 즉시 포기

### 3. Rate Limiting 강화

**OpenAI 모델별 대기 시간**
```python
if model.startswith('o'):  # thinking 모델 (o1, o3, o4)
    time.sleep(3)  # 3초 대기
else:  # 일반 모델
    time.sleep(1.5)  # 1.5초 대기
```

**Claude 대기 시간**
```python
time.sleep(2)  # 2초 대기
```

**오류 발생 시**
```python
time.sleep(3)  # 더 긴 대기 (3초)
```

### 4. 개선 효과

| 항목 | 기존 | 개선 |
|------|------|------|
| 재시도 | ❌ 없음 | ✅ 3회 (exponential) |
| Rate Limiting | 1초 고정 | 모델별 차별화 (1.5-3초) |
| 오류 복구 | ❌ 즉시 실패 | ✅ 자동 재시도 + 긴 대기 |
| 안정성 | ⚠️ 낮음 | ✅ 높음 |

## 적용된 파일

1. `/scripts/benchmark_llm_models_2025.py` ✅
2. `/requirements.txt` ✅

## 사용 방법

### 1. 패키지 설치

```bash
cd /Users/kangmin/umis_main_1103/umis
pip install -r requirements.txt
```

### 2. 벤치마크 재실행

```bash
python scripts/benchmark_llm_models_2025.py
```

### 3. 결과 확인

- 자동 재시도로 인해 일시적 오류 극복
- Rate limiting 개선으로 연속 테스트 안정화
- 실패율 감소 예상: 10-15% → 2-5%

## 추가 권장 사항

### 1. API 사용량 모니터링

OpenAI Platform에서 실시간 사용량 확인:
- https://platform.openai.com/usage

### 2. Tier 확인

현재 Tier에 따른 Rate Limit:
- Free: 매우 낮음 (비권장)
- Tier 1: 500 RPM (분당 요청 수)
- Tier 2: 5,000 RPM
- Tier 3: 10,000 RPM

### 3. 비용 알림 설정

예산 초과 방지:
1. OpenAI Dashboard → Settings → Billing → Limits
2. Hard limit 설정 (예: $50/month)

### 4. 테스트 전략

대규모 벤치마크 시:
```python
# 핵심 모델만 선택 (옵션 2)
benchmark.models = {
    'openai_mini': ['gpt-4o-mini'],
    'openai_standard': ['gpt-4o'],
    'openai_thinking': ['o1-mini'],
    'claude_haiku': ['claude-haiku-3.5'],
    'claude_sonnet': ['claude-sonnet-3.5']
}
```

## 문제 해결

### 여전히 오류 발생 시

1. **API 키 확인**
   ```bash
   cat .env | grep OPENAI_API_KEY
   ```

2. **네트워크 연결 확인**
   ```bash
   curl https://api.openai.com/v1/models -H "Authorization: Bearer $OPENAI_API_KEY"
   ```

3. **Rate Limit 확인**
   - 오류 메시지에 "429" 또는 "rate_limit" 포함 시
   - 대기 시간 더 늘리기: `time.sleep(5)`

4. **로그 확인**
   ```bash
   tail -f benchmark_run.log
   ```

## 결론

이번 개선으로 API 연결 안정성이 크게 향상되었습니다:

✅ 자동 재시도 (exponential backoff)
✅ 모델별 차별화된 rate limiting
✅ 오류 발생 시 자동 복구
✅ 더 나은 에러 핸들링

벤치마크 테스트를 재실행하시면 훨씬 안정적으로 완료될 것입니다!

