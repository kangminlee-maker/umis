# API 사용 방법 차이 분석 및 테스트 결과

**날짜**: 2025-11-23  
**목적**: 테스트되지 않은 모델의 API 사용 방법 확인 및 올바른 방법으로 재테스트

---

## 🔍 문제 분석

### ❌ 원래 실패한 모델들

| 모델 | Chat API 에러 | 실제 원인 |
|------|--------------|-----------|
| **o1-mini** | 404 model_not_found | ⚠️ **2025년 10월 27일 shutdown (deprecated)** |
| **o1-pro** | - | ✅ Responses API 전용 (Chat API 미지원) |
| **o1-pro-2025-03-19** | 404 + Responses API 전용 | ✅ Responses API 전용 |

---

## 🎯 올바른 API 사용 방법

### 1. o1-mini - DEPRECATED ❌

```yaml
상태: 2025년 10월 27일 완전히 shutdown
deprecated 날짜: 2025년 4월

이유:
  - o4-mini로 대체됨
  - 성능 향상된 모델 출시
  - OpenAI의 모델 라인업 정리

대체 모델:
  1. o4-mini (동일 가격, 성능↑)
  2. o3-mini (동일 가격, 안정성)
```

**웹 검색 결과**:
> "In April 2025, OpenAI announced the deprecation of o1-mini, with a scheduled shutdown date of October 27, 2025. Developers were advised to transition to the newer o4-mini model."

### 2. o1-pro / o1-pro-2025-03-19 - Responses API 전용 ✅

**잘못된 방법** (Chat API):
```python
# ❌ 404 Error
response = client.chat.completions.create(
    model='o1-pro',
    messages=[{"role": "user", "content": "..."}]
)
# Error: This model is only supported in v1/responses
```

**올바른 방법** (Responses API):
```python
# ✅ 성공
response = client.responses.create(
    model='o1-pro',
    input="...",  # messages 대신 input 사용
    reasoning={"effort": "low"},  # 추론 노력 수준 지정
    background=False  # 동기/비동기 선택
)

output = response.output_text
```

**주요 차이점**:
| 항목 | Chat API | Responses API |
|------|----------|---------------|
| 엔드포인트 | `/v1/chat/completions` | `/v1/responses` |
| 입력 | `messages` | `input` (문자열) |
| 파라미터 | `temperature`, `max_tokens` | `reasoning`, `background` |
| 출력 | `choices[0].message.content` | `output_text` |

---

## 📊 Responses API 테스트 결과

### 성공적으로 테스트된 모델 (2개)

| 모델 | API | 품질 | 시간 | 비용 | 토큰 | 평가 |
|------|-----|------|------|------|------|------|
| **o1-pro** | Responses | 100/100 | 6.77초 | $0.033900 | 145 | ⭐⭐⭐ 비쌈 |
| **o1-pro-2025-03-19** | Responses | 100/100 | 14.82초 | $0.110700 | 273 | ⭐ 매우 비쌈, 느림 |

### 비용 비교

```yaml
Phase 0 (단순 데이터 추출) 1,000회 비용:

초저가 모델:
  - gpt-4.1-nano: $0.03 ⭐⭐⭐⭐⭐
  - GPT-4o-mini: $0.045 ⭐⭐⭐⭐⭐
  - o4-mini-2025-04-16: $0.60 ⭐⭐⭐⭐

중가 모델:
  - o3-mini-2025-01-31: $0.87 ⭐⭐⭐
  - o1-2024-12-17: $8.01 ⭐⭐

고가 모델:
  - o1-pro: $33.90 ⭐ (Chat 대비 753배 비쌈!)
  - o1-pro-2025-03-19: $110.70 ❌ (Chat 대비 2,460배!)
```

### 핵심 발견

```yaml
o1-pro의 문제점:
  1. 비용: $33.90/1,000회 (gpt-4.1-nano 대비 1,130배!)
  2. 속도: 6.77-14.82초 (느림)
  3. 오버킬: Phase 0 같은 단순 작업에 불필요
  
  결론: Phase 0-3에는 절대 사용 금지!

o1-pro 적합한 경우:
  - 매우 복잡한 추론 (Phase 4 최고급만)
  - 비용 무시
  - 품질이 모든 것
  
  → UMIS에서는 비현실적!
```

---

## 🎯 모델별 사용 가능 여부 정리

### ✅ Chat API 사용 가능 (17개)

**OpenAI Standard:**
- gpt-4.1, gpt-4.1-mini, gpt-4.1-nano
- gpt-4o, gpt-4o-mini
- gpt-5, gpt-5.1, gpt-5-mini, gpt-5-nano, gpt-5-pro
- gpt-5-codex, gpt-5.1-codex

**OpenAI Thinking (Chat API):**
- o1, o1-2024-12-17
- o3, o3-2025-04-16
- o3-mini, o3-mini-2025-01-31
- o4-mini, o4-mini-2025-04-16

**Claude:**
- claude-haiku-3.5
- claude-sonnet-3.7, claude-sonnet-4
- claude-opus-4

### ✅ Responses API 전용 (2개)

- o1-pro
- o1-pro-2025-03-19

### ❌ Deprecated / 사용 불가 (1개)

- **o1-mini** (2025년 10월 27일 shutdown)
  - 대체: o4-mini, o3-mini

---

## 💡 API 사용 방법 요약

### Chat API (일반적)

```python
from openai import OpenAI
client = OpenAI()

# 대부분의 모델
response = client.chat.completions.create(
    model='gpt-4o-mini',  # 또는 다른 Chat API 모델
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is 1+1?"}
    ],
    temperature=0.2,  # o1/o3/o4 시리즈는 미지원
    max_tokens=100
)

output = response.choices[0].message.content
```

### Responses API (o1-pro 전용)

```python
from openai import OpenAI
client = OpenAI()

# o1-pro, o1-pro-2025-03-19만
response = client.responses.create(
    model='o1-pro',
    input="What is 1+1?",  # messages 대신 input
    reasoning={"effort": "low"},  # low/medium/high
    background=False  # 동기 처리
)

output = response.output_text  # 직접 접근
```

### 파라미터 차이

| 파라미터 | Chat API | Responses API | 비고 |
|----------|----------|---------------|------|
| **입력** | `messages` (배열) | `input` (문자열) | 필수 |
| **온도** | `temperature` | ❌ 미지원 | - |
| **토큰** | `max_tokens` | ❌ 미지원 | - |
| **추론** | ❌ | `reasoning` | Responses 전용 |
| **비동기** | ❌ | `background` | Responses 전용 |
| **출력** | `choices[0].message.content` | `output_text` | - |

---

## 🏆 UMIS 최종 권장 (업데이트)

### Phase 0-2 (45% 작업)
```yaml
모델: gpt-4.1-nano ⭐⭐⭐⭐⭐
API: Chat API
비용: $0.03/1,000회
품질: 100/100
이유: 초저가, 빠름, 단순 작업에 완벽
```

### Phase 3 (48% 작업)
```yaml
모델: GPT-4o-mini ⭐⭐⭐⭐⭐
API: Chat API
비용: $0.06/1,000회 (템플릿 O)
품질: 100/100
이유: 가성비 최고, 프롬프트 개선으로 충분
```

### Phase 4 (7% 작업)
```yaml
1순위: o3-mini-2025-01-31 ⭐⭐⭐⭐⭐
  API: Chat API
  비용: $0.87/1,000회
  품질: 100/100
  이유: o1-mini 대체, 동일 가격, 안정적

2순위: o4-mini-2025-04-16 ⭐⭐⭐⭐⭐
  API: Chat API
  비용: $0.60/1,000회
  품질: 100/100 (Phase 0)
  이유: 가장 빠르고 저렴, Phase 0-2 최적

3순위: o3-2025-04-16 ⭐⭐⭐⭐
  API: Chat API
  비용: $1.61/1,000회
  품질: 100/100
  이유: 복잡한 추론 필요 시

❌ 비추천: o1-pro, o1-pro-2025-03-19
  이유: 33-110배 비쌈, Responses API 전용, 오버킬
```

### 총 비용 예상
```yaml
최적 구성:
  Phase 0-2 (45%): gpt-4.1-nano × 450 = $0.01
  Phase 3 (48%): GPT-4o-mini × 480 = $0.06
  Phase 4 (7%): o3-mini-2025-01-31 × 70 = $0.06
  
  총계: $0.13/1,000회 ⭐⭐⭐⭐⭐
  
vs o1-pro 사용 시:
  Phase 4 (7%): o1-pro × 70 = $2.37
  총계: $2.44/1,000회 (18.8배 증가!)
```

---

## 📝 체크리스트

### ✅ 확인 완료

- [x] o1-mini는 deprecated (2025년 10월 shutdown)
- [x] o1-pro는 Responses API 전용
- [x] o1-pro-2025-03-19도 Responses API 전용
- [x] Responses API 사용 방법 확인
- [x] o1-pro 테스트 성공 (100/100)
- [x] o1-pro-2025-03-19 테스트 성공 (100/100)
- [x] 비용 분석 완료 (33-110배 비쌈)
- [x] 대체 모델 확인 (o3-mini, o4-mini)

### ⏳ 남은 작업

- [ ] o3-mini-2025-01-31 전체 Phase 테스트 (권장)
- [ ] o4-mini-2025-04-16 전체 Phase 테스트 (선택)
- [ ] COMPLETE_LLM_MODEL_COMPARISON.md 업데이트
- [ ] UMIS_LLM_OPTIMIZATION_FINAL.md 업데이트
- [ ] 실제 UMIS에 o3-mini 통합

---

## 🎉 결론

### 원인 파악 완료

```yaml
o1-mini 실패:
  원인: Deprecated (2025년 10월 shutdown)
  해결: o4-mini 또는 o3-mini 사용

o1-pro 실패:
  원인: Responses API 전용 (Chat API 미지원)
  해결: client.responses.create() 사용
  결과: 테스트 성공 (100/100)

결론:
  - API 사용 방법이 달라서 실패한 것이 맞음!
  - Responses API로 테스트하니 정상 작동
  - 하지만 비용이 너무 비싸서 UMIS에는 부적합
```

### 최종 권장

```yaml
UMIS Phase 4 최적 모델:
  1위: o3-mini-2025-01-31 ⭐⭐⭐⭐⭐
  2위: o4-mini-2025-04-16 ⭐⭐⭐⭐⭐
  
비추천: o1-pro (비용 33-110배, 오버킬)
```

---

**작성일**: 2025-11-23  
**테스트 완료**: ✅ Chat API (4개) + Responses API (2개)  
**다음 단계**: o3-mini 전체 Phase 테스트

