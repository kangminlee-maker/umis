# Multi-Layer Guestimation 사용 가이드

**버전**: v2.0  
**구현일**: 2025-11-05  
**상태**: ✅ Production Ready

---

## 🎯 개요

**Multi-Layer Guestimation**은 8가지 데이터 출처를 계층적으로 시도하여, 최적의 추정 방법을 자동으로 선택하는 엔진입니다.

---

## 🏗️ 8개 레이어

| Layer | 출처 | 신뢰도 | 사용 시점 |
|-------|------|--------|----------|
| 1 | 프로젝트 데이터 | 100% | 확정 데이터 있음 |
| 2 | LLM 직접 답변 | 70% | 간단한 사실 질문 |
| 3 | 웹 검색 공통 맥락 | 80% | 최신 정보 필요 |
| 4 | 법칙 (물리/법률) | 100% | 절대적 제약 |
| 5 | 행동경제학 | 70% | 소비자 행동 |
| 6 | 통계 패턴 | 60% | 파레토, 정규분포 |
| 7 | RAG 벤치마크 | 30-80% | 유사 사례 비교 |
| 8 | 제약조건 | 50% | 경계값 (최소/최대) |

---

## 💻 사용 방법

### 기본 사용

```python
from umis_rag.utils.multilayer_guestimation import MultiLayerGuestimation

# 1. 엔진 초기화
estimator = MultiLayerGuestimation(
    project_context={'한국_인구': 52000000}
)

# 2. 추정
result = estimator.estimate("한국 인구는?")

# 3. 결과 확인
print(f"값: {result.value}")
print(f"출처: {result.source_layer.name}")
print(f"신뢰도: {result.confidence:.0%}")
```

### Quantifier Agent와 통합

```python
from umis_rag.agents.quantifier import QuantifierRAG
from umis_rag.utils.multilayer_guestimation import BenchmarkCandidate

# 1. Quantifier 초기화
quantifier = QuantifierRAG()

# 2. 타겟 프로필 정의
target = BenchmarkCandidate(
    name="한국 B2B SaaS Churn Rate",
    value=0,  # 추정할 값
    product_type="digital",
    consumer_type="B2B",
    price=500000,
    is_essential=False
)

# 3. Multi-Layer 추정
result = quantifier.estimate_with_multilayer(
    "한국 B2B SaaS 평균 Churn Rate는?",
    target_profile=target
)

# 4. 결과
print(f"결과: {result.get_display_value()}")
print(f"출처 레이어: {result.source_layer.name}")
```

### 빠른 추정 (편의 함수)

```python
from umis_rag.utils.multilayer_guestimation import quick_estimate

value = quick_estimate("하루는 몇 시간?")
# → 24 (Layer 4: 법칙)
```

---

## 📊 레이어별 작동 예시

### Layer 1: 프로젝트 데이터

**질문**: "한국 인구는?"

```python
project_data = {'한국_인구': 52000000}
estimator = MultiLayerGuestimation(project_context=project_data)
result = estimator.estimate("한국 인구는?")

# 결과:
# value: 52,000,000
# source_layer: PROJECT_DATA
# confidence: 100%
# logic: "✅ Layer 1: 프로젝트 데이터 '한국_인구' 사용"
```

### Layer 4: 법칙

**질문**: "하루는 몇 시간?"

```python
result = estimator.estimate("하루는 몇 시간?")

# 결과:
# value: 24
# source_layer: LAW
# confidence: 100%
# logic: "✅ Layer 4: 법칙 '하루' = 24 시간"
```

### Layer 6: 통계 패턴

**질문**: "상위 고객 비율은?"

```python
result = estimator.estimate("상위 고객 비율은?")

# 결과:
# value: 0.20 (20%)
# source_layer: STATISTICAL
# confidence: 60%
# logic: "✅ Layer 6: 파레토 법칙 (80-20)"
```

### Layer 7: RAG 벤치마크

**질문**: "한국 음식점 재방문 주기는?"

```python
# 타겟 정의
target = BenchmarkCandidate(
    name="한국 음식점 재방문",
    value=0,
    product_type="service",
    consumer_type="B2C",
    price=15000,
    is_essential=False
)

# RAG 후보들
candidates = [
    BenchmarkCandidate(name="한국 카페 재방문", value=30, ...),
    BenchmarkCandidate(name="미국 레스토랑 재방문", value=45, ...),
]

result = estimator.estimate(
    "한국 음식점 재방문 주기는?",
    target_profile=target,
    rag_candidates=candidates
)

# 결과:
# value: 30 (일)
# source_layer: RULE_OF_THUMB
# confidence: 75% (비교 가능성 3/4)
# logic: "✅ Layer 7: RAG 벤치마크 '한국 카페 재방문' 채택"
#        "→ 비교 가능성: 3/4"
#        "→ 근거: 제품 동일, 소비자 동일, 가격 유사, 맥락 동일"
```

---

## 🎯 사용 시나리오

### 시나리오 1: 시장 규모 추정

**목표**: 음식점 마케팅 SaaS 시장 규모

```python
# 프로젝트 데이터
project_data = {
    '음식점_수': 700000,
    '디지털_도구_사용률': 0.30,
}

# 추정
result = estimator.estimate(
    "음식점 중 디지털 도구 사용 비율은?",
    project_context=project_data
)

# → Layer 1: 30% (프로젝트 데이터)
```

### 시나리오 2: Churn Rate 추정

**목표**: 한국 SaaS Churn Rate

```python
# 타겟
target = BenchmarkCandidate(
    name="한국 B2B SaaS",
    product_type="digital",
    consumer_type="B2B",
    price=500000
)

# Quantifier 활용
result = quantifier.estimate_with_multilayer(
    "한국 B2B SaaS Churn Rate는?",
    target_profile=target
)

# → Layer 7: RAG 벤치마크에서 유사 사례 찾아 채택
```

### 시나리오 3: 빠른 상식 확인

**목표**: 기본 시간 단위

```python
result = quick_estimate("일주일은 며칠?")
# → 7 (Layer 4: 법칙)
```

---

## 🔍 레이어 선택 로직

### Fallback 순서

```
Question 입력
    ↓
Layer 1: 프로젝트 데이터 확인
    ├─ 있음? → 반환 (신뢰도 100%)
    └─ 없음 → Layer 2
        ↓
Layer 2: LLM 직접 (간단한 사실?)
    ├─ 예 + 신뢰도 >= 70%? → 반환
    └─ 아니오 → Layer 3
        ↓
Layer 3: 웹 검색 (활성화?)
    ├─ 발견 + 신뢰도 >= 80%? → 반환
    └─ 없음 → Layer 4
        ↓
...
        ↓
Layer 7: RAG 벤치마크
    ├─ 비교 가능? → 반환
    └─ 없음 → Layer 8
        ↓
Layer 8: 제약조건
    ├─ 경계값? → 범위 반환
    └─ 없음 → 추정 실패
```

---

## 🛠️ 고급 활용

### 특정 레이어만 활성화

```python
estimator = MultiLayerGuestimation(
    enable_web_search=False,  # 웹 검색 비활성
    enable_llm=False          # LLM 비활성
)

# → Layer 1, 4, 5, 6, 7, 8만 사용
```

### 전체 추적 모드

```python
result = estimator.estimate_with_trace(
    "한국 음식점 재방문 주기는?",
    verbose=True
)

# 출력:
# ================================================================================
# 🎯 질문: 한국 음식점 재방문 주기는?
# ================================================================================
# 
# 📊 레이어 시도 과정:
#    ❌ Layer 1: 프로젝트 데이터 없음 → Layer 2로
#    ⚠️ Layer 2: 자동 실행 비활성 → Layer 3으로
#    ...
#    ✅ Layer 7: RAG 벤치마크 '한국 카페 재방문' 채택
# 
# ✅ 추정 성공!
#    출처: RULE_OF_THUMB
#    값: 30
#    신뢰도: 75%
```

---

## 📝 문서화 예시

### Estimation Details 7개 섹션 생성

```python
from umis_rag.utils.multilayer_guestimation import estimate_with_details

details = estimate_with_details(
    "한국 음식점 재방문 주기는?",
    project_data=project_data,
    target_profile=target,
    rag_candidates=candidates
)

# 결과 (Excel/Markdown 호환):
# {
#     'id': 'EST_한국 음식점 재방문 주기는?',
#     'description': '한국 음식점 재방문 주기는?',
#     'value': 30,
#     'confidence': '75%',
#     'reason': '직접 데이터 없음',
#     'base_data': [...],
#     'logic_steps': [...],
#     'source_layer': 'RULE_OF_THUMB',
#     ...
# }
```

---

## 🎓 Best Practices

### 1. 프로젝트 데이터 우선 제공

```python
# ✅ 좋은 예
project_data = {
    '고객_수': 10000,
    '평균_ARPU': 50000,
    '도입률': 0.20,
}

estimator = MultiLayerGuestimation(project_context=project_data)
```

### 2. 타겟 프로필 정확히 정의

```python
# ✅ 좋은 예
target = BenchmarkCandidate(
    name="한국 음식점 마케팅 SaaS",
    value=0,
    product_type="digital",      # 정확히!
    consumer_type="B2C",         # 정확히!
    price=100000,                # 월 10만원
    is_essential=False,          # 선택재
)
```

### 3. 결과 신뢰도 확인

```python
result = estimator.estimate(...)

if result.confidence >= 0.7:
    print("✅ 높은 신뢰도 - 사용 가능")
elif result.confidence >= 0.5:
    print("⚠️ 중간 신뢰도 - 검증 필요")
else:
    print("❌ 낮은 신뢰도 - 재추정 권장")
```

---

## 🔧 테스트

### 단위 테스트

```bash
python3 scripts/test_multilayer_guestimation.py
```

### 통합 테스트

```bash
python3 scripts/test_quantifier_multilayer.py
```

---

## 📚 관련 문서

- **프레임워크**: `docs/GUESTIMATION_FRAMEWORK.md`
- **명세서**: `docs/GUESTIMATION_MULTILAYER_SPEC.md`
- **코드**: `umis_rag/utils/multilayer_guestimation.py`

---

**작성일**: 2025-11-05  
**버전**: v2.0  
**상태**: ✅ Production Ready

