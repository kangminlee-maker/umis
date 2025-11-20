# Deprecated 인터페이스 정리 v7.5.0

**작성일**: 2025-11-10  
**버전**: v7.5.0  
**상태**: ✅ 완료  

---

## 📋 전체 Deprecated 목록

### 🔴 코드 레벨 (제거 완료)

| 인터페이스 | 위치 | 상태 | 대체 |
|-----------|------|------|------|
| **calculate_sam_with_hybrid()** | quantifier.py | ✅ 제거 | estimator.estimate() |
| **_execute_guestimation()** | quantifier.py | ✅ 제거 | - |
| **_execute_domain_reasoner()** | quantifier.py | ✅ 제거 | - |
| **DomainReasonerEngine** | methodologies/domain_reasoner.py | ✅ Archive | EstimatorRAG |
| **GuestimationEngine** | utils/guestimation.py | ✅ Archive | EstimatorRAG |
| **recommend_methodology()** | guardian/meta_rag.py | ⚠️ Deprecated | 직접 Estimator 호출 |

---

### 🔴 Tool Registry (제거 완료)

| Tool Key | 상태 | 대체 |
|----------|------|------|
| **tool:universal:guestimation** | ✅ 제거 | tool:estimator:estimate |
| **tool:universal:domain_reasoner_10_signals** | ✅ 제거 | tool:estimator:estimate |

**Total Tools**: 31 → 29개

---

### ⚠️ 문서 레벨 (제거 필요)

#### umis.yaml

| 섹션 | Line | 줄 수 | 상태 | 비고 |
|------|------|-------|------|------|
| **guestimation** | 6048-6274 | 226줄 | 🔴 제거 필요 | Estimator로 완전 대체 |
| **domain_reasoner** | 6275-6494 | 219줄 | 🔴 제거 필요 | Archive 완료 |
| **hybrid_strategy** | 6495-6645 | 150줄 | 🔴 제거 필요 | 2-Phase 전략 폐지 |

**총 595줄 제거 가능**

---

## ✅ 정상 인터페이스 (유지)

### Estimator 호출 구조 (v7.5.0)

| Agent | 메서드 | 상태 | 비고 |
|-------|--------|------|------|
| **Quantifier** | `estimate(question, domain, region)` | ✅ 정상 | Estimator 호출 |
| **Validator** | `validate_estimation(question, claimed_value)` | ✅ 정상 | Estimator 교차 검증 |
| **Observer** | (Estimator 호출 필요 시) | ✅ 정상 | 직접 호출 |
| **Explorer** | (Estimator 호출 필요 시) | ✅ 정상 | 직접 호출 |
| **Guardian** | `recommend_methodology()` | ⚠️ Deprecated | 사용 안 함 |

---

## 🔧 Guardian recommend_methodology() 처리

### 현재 상태
```python
# umis_rag/guardian/meta_rag.py

def recommend_methodology():
    """DEPRECATED (v7.5.0)"""
    logger.warning("Domain Reasoner 제거됨")
    return {'recommendation': 'estimator_sufficient'}
```

**상태**: Deprecated 마킹 완료 ✅

**동작**: 
- 호출해도 에러 안 남 (호환성)
- 항상 'estimator_sufficient' 반환
- 경고 로그 출력

**향후**: 다음 메이저 버전(v8.0)에서 완전 제거 가능

---

## 📊 Cursor 명령어

### Deprecated 명령어

| 명령어 | 상태 | 대체 |
|--------|------|------|
| `@guestimate [질문]` | ❌ 작동 안 함 | `@Fermi [질문]` |
| `@reasoner [질문]` | ❌ 작동 안 함 | `@Fermi [질문]` |
| `@auto [질문]` | ❌ 작동 안 함 | `@Fermi [질문]` |

### 정상 명령어 (v7.5.0)

| 명령어 | Agent | 비고 |
|--------|-------|------|
| `@Fermi [질문]` | Estimator | 직접 추정 |
| `@Explorer [질문]` | Explorer | 내부에서 Estimator 호출 |
| `@Quantifier [질문]` | Quantifier | 내부에서 Estimator 호출 |
| `@Validator verify [값]` | Validator | Estimator 교차 검증 |

---

## 🎯 Migration Guide

### AS-IS (v7.2.0)

```python
# 1. Guestimation 직접 사용 (Deprecated)
from umis_rag.utils.guestimation import GuestimationEngine
engine = GuestimationEngine()
result = engine.check_comparability(target, candidate)

# 2. Domain Reasoner 직접 사용 (Deprecated)
from umis_rag.methodologies.domain_reasoner import DomainReasonerEngine
engine = DomainReasonerEngine()
result = engine.execute(question, domain)

# 3. Quantifier Hybrid (Deprecated)
quantifier.calculate_sam_with_hybrid(market_def)

# 4. Guardian 판단 (Deprecated)
guardian.recommend_methodology(estimate_result)
→ 'domain_reasoner' 또는 'guestimation_sufficient'
```

### TO-BE (v7.5.0)

```python
# 모든 추정은 Estimator Agent로 통합
from umis_rag.agents.estimator import EstimatorRAG

estimator = EstimatorRAG()

# 1. 단순 추정
result = estimator.estimate(
    question="B2B SaaS ARPU는?",
    domain="B2B_SaaS",
    region="한국"
)
# → Tier 1 → 2 → 3 자동 선택

# 2. Quantifier 협업
quantifier = QuantifierRAG()
# 내부적으로 estimator.estimate() 호출

# 3. Validator 교차 검증
validator = ValidatorRAG()
validator.validate_estimation(question, claimed_value)
# 내부적으로 estimator.estimate() 호출

# 4. Guardian 판단 불필요
# Estimator가 자동으로 Tier 선택
```

---

## 📁 제거 대상 요약

### 코드 (이미 Archive)
1. ✅ `umis_rag/utils/guestimation.py`
2. ✅ `umis_rag/utils/multilayer_guestimation.py`
3. ✅ `umis_rag/methodologies/domain_reasoner.py`
4. ✅ `umis_rag/agents/quantifier.py` (Hybrid 메서드)
5. ⚠️ `umis_rag/guardian/meta_rag.py` (Deprecated 마킹)

### 데이터
6. ✅ `data/raw/umis_domain_reasoner_methodology.yaml`
7. ✅ `archive/v7.2.0_and_earlier/umis_ai_guide.yaml`

### Tool Registry
8. ✅ `tool:universal:guestimation` 제거
9. ✅ `tool:universal:domain_reasoner_10_signals` 제거

### 문서 (umis.yaml)
10. 🔴 **guestimation 섹션** (Line 6048-6274, 226줄) - 제거 필요
11. 🔴 **domain_reasoner 섹션** (Line 6275-6494, 219줄) - 제거 필요
12. 🔴 **hybrid_strategy 섹션** (Line 6495-6645, 150줄) - 제거 필요

**총 595줄 제거 가능**

---

## ✅ 검증 완료 사항

### Agent 인터페이스

| Agent | Deprecated 확인 | 정상 동작 | 비고 |
|-------|----------------|----------|------|
| **Observer** | ✅ 없음 | ✅ 정상 | - |
| **Explorer** | ✅ 없음 | ✅ 정상 | - |
| **Quantifier** | ✅ Hybrid 제거 | ✅ estimate() 정상 | - |
| **Validator** | ✅ 없음 | ✅ validate_estimation() 정상 | Estimator 호출 |
| **Guardian** | ⚠️ recommend_methodology | ✅ 정상 | Deprecated 마킹 |
| **Estimator** | ✅ 없음 | ✅ 3-Tier 정상 | - |

---

## 🎯 다음 단계

### 필수 작업
1. ✅ 코드 레벨 정리 완료
2. ✅ Tool Registry 정리 완료
3. 🔴 **umis.yaml 정리 필요** (595줄)

### 선택 작업
- Guardian recommend_methodology 완전 제거 (v8.0에서)
- umis_core.yaml 정리
- 테스트 케이스 정리

---

**다음 작업**: umis.yaml Line 6048-6645 (595줄) 제거

진행할까요? 🚀

---

**END**

