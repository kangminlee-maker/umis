# Phase 3-4 의존성 분석 (v7.11.0)

**날짜:** 2025-11-26  
**Task:** Phase 1.1 - 의존성 트리 완전 분석  
**목적:** Phase 3-4 제거 영향 범위 파악

---

## 📊 전체 요약

### 영향받는 파일
- **총 22개 파일** (Archive 제외 시 **14개**)
- **코드:** 7개 (실제 사용 5개, 백업 2개)
- **테스트:** 4개
- **문서:** 3개

---

## 🎯 핵심 의존성 맵

### 1. Phase 3-4 레거시 파일 (제거 대상)

```
umis_rag/agents/estimator/
├── phase3_guestimation.py          ⛔ 466줄
├── phase3_range_engine.py          ⛔ 131줄
├── phase4_fermi.py                 ⛔ 3,460줄
└── estimator_v7.10.2.py            ⛔ 1,200+줄 (백업 존재)
```

**상태:** 모두 Archive 이동 예정

---

### 2. Phase 3-4를 Import하는 파일

#### A. 실제 코드 (5개)

| 파일 | Import | 영향도 |
|-----|--------|-------|
| `phase4_fermi.py` | `from .phase3_guestimation import Phase3Guestimation` | ⚠️ 순환 의존성 |
| `estimator_v7.10.2.py` | `from .phase3_guestimation import Phase3Guestimation` | 🔵 백업 파일 |
| `estimator_v7.10.2.py` | `from .phase4_fermi import Phase4FermiDecomposition` | 🔵 백업 파일 |
| `umis_rag/agents/estimator.py` | `from .estimator.phase3_guestimation import Phase3Guestimation` | ⚠️ 실제 영향 |
| `tests/test_phase4_parsing_fix.py` | `from umis_rag.agents.estimator.phase4_fermi import Phase4FermiDecomposition` | 🧪 테스트 |

**핵심 문제:**
- `phase4_fermi.py` → `phase3_guestimation.py` **순환 의존성**
- `umis_rag/agents/estimator.py` (최상위) → Phase3Guestimation Import

---

#### B. 테스트 파일 (4개)

| 파일 | 내용 | 전환 전략 |
|-----|------|---------|
| `tests/unit/test_phase3_guestimation.py` | Phase 3 Unit Test | → `test_prior_estimator.py` |
| `tests/unit/test_phase4_fermi.py` | Phase 4 Unit Test | → `test_fermi_estimator.py` |
| `tests/test_phase4_parsing_fix.py` | Phase 4 JSON Parsing 테스트 | Archive (레거시 전용) |
| `tests/integration/test_phase_flow.py` | Phase 0-4 Flow 테스트 | → `test_stage_flow_v7_11_0.py` |

---

#### C. 문서 (3개, 방금 생성된 마이그레이션 문서)

| 파일 | 내용 |
|-----|------|
| `dev_docs/improvements/MIGRATION_DESIGN_COMPLETE_v7_11_0.md` | 마이그레이션 완료 리포트 |
| `dev_docs/improvements/PHASE_TO_STAGE_MIGRATION_PLAN_v7_11_0.md` | 작업 계획 |
| `dev_docs/improvements/MIGRATION_STRATEGY_SUMMARY_v7_11_0.md` | 전략 요약 |

**처리:** 문서는 그대로 유지 (마이그레이션 기록)

---

#### D. Archive (백업 파일들, 제외)

```
umis_rag/agents/estimator.v7.10.2.backup/
├── estimator/
│   ├── estimator.py
│   ├── phase3_guestimation.py
│   ├── phase4_fermi.py
│   ├── phase3_range_engine.py
│   └── models.py
├── estimator.py
├── phase3_guestimation.py
├── phase4_fermi.py
├── phase3_range_engine.py
└── models.py
```

**처리:** 이미 백업이므로 제외

---

## 🔍 상세 의존성 분석

### 순환 의존성 (Critical!)

```python
# phase4_fermi.py (Line 43)
from umis_rag.agents.estimator.phase3_guestimation import Phase3Guestimation

class Phase4FermiDecomposition:
    def __init__(self, config=None):
        # Phase 3 의존성
        self.phase3 = Phase3Guestimation(llm_mode=None)
```

**문제:**
- Phase 4가 Phase 3에 의존
- 둘 다 Archive로 이동 시 자동 해결 ✅

**신규 아키텍처 (v7.11.0):**
```python
# fermi_estimator.py (Stage 3)
class FermiEstimator:
    def __init__(self, llm_mode, prior_estimator):
        # PriorEstimator를 주입받음 (의존성 역전)
        self.prior_estimator = prior_estimator
```

**결과:** 순환 의존성 완전 제거 ✅

---

### 최상위 Import (High Priority)

```python
# umis_rag/agents/estimator.py (Line 17)
from .estimator.phase3_guestimation import Phase3Guestimation
```

**문제:**
- 최상위 `__init__.py` 역할 파일
- Phase3Guestimation 노출 중

**해결책:**
```python
# Task 2.2: compat.py 생성 후
from .compat import Phase3Guestimation  # Deprecated
```

---

### 테스트 의존성

#### 1. Unit Tests

**`tests/unit/test_phase3_guestimation.py`:**
```python
from umis_rag.agents.estimator.phase3_guestimation import Phase3Guestimation

class TestPhase3Guestimation:
    def test_estimate(self):
        phase3 = Phase3Guestimation()
        result = phase3.estimate("...")
        assert result.phase == 3  # ⚠️ phase 필드 사용
```

**전환:**
```python
# tests/unit/test_prior_estimator.py
from umis_rag.agents.estimator import PriorEstimator

class TestPriorEstimator:
    def test_estimate(self):
        prior = PriorEstimator()
        result = prior.estimate("...")
        assert result.source == "Generative Prior"  # ✅ source 필드
```

---

#### 2. Integration Tests

**`tests/integration/test_phase_flow.py` (Lines 65, 85):**
```python
def test_phase3_guestimation(self):
    # Phase 3 테스트
    pass

def test_phase4_fermi_decomposition(self):
    # Phase 4 테스트
    pass
```

**전환:**
```python
# tests/integration/test_stage_flow_v7_11_0.py
def test_stage2_generative_prior(self):
    # Stage 2 테스트
    pass

def test_stage3_fermi(self):
    # Stage 3 테스트
    pass
```

---

## 🛠️ Config 파일 의존성

### `models.py` - Phase3Config, Phase4Config

**현재 (Lines 533-587):**
```python
@dataclass
class Phase3Config:
    """Phase 3 (Guestimation) 설정 (v7.7.0)"""
    pass

@dataclass
class Phase4Config:
    """Phase 4 (Fermi Decomposition) 설정 (v7.7.0+)"""
    pass

@dataclass
class EstimatorConfig:
    phase3: Phase3Config = field(default_factory=Phase3Config)
    phase4: Phase4Config = field(default_factory=Phase4Config)
```

**전환 (Task 2.4):**
```python
# Deprecated Alias
Phase3Config = PriorEstimatorConfig  # Alias for backward compatibility
Phase4Config = FermiEstimatorConfig  # Alias for backward compatibility

import warnings
warnings.warn("Phase3Config는 Deprecated입니다. PriorEstimatorConfig를 사용하세요.", DeprecationWarning)
```

---

### `EstimationResult.phase` 필드

**현재 (Line 312):**
```python
@dataclass
class EstimationResult:
    phase: int = 0  # 0, 1, 2, 3, 4 (-1: 전체 실패)
```

**전환 (Task 2.4):**
```python
@property
def phase(self) -> int:
    """Deprecated: Use 'source' instead."""
    warnings.warn("EstimationResult.phase는 Deprecated입니다.", DeprecationWarning)
    source_map = {
        'Literal': 0,
        'Direct RAG': 1,
        'Validator Search': 2,
        'Generative Prior': 2,  # Stage 2
        'Fermi': 3,             # Stage 3
        'Fusion': 4             # Stage 4
    }
    return source_map.get(self.source, -1)
```

---

## 📋 제거 우선순위

### Priority 1: Archive 이동 (Task 2.1)
- `phase3_guestimation.py`
- `phase3_range_engine.py`
- `phase4_fermi.py`
- `estimator_v7.10.2.py`

**이유:** 순환 의존성 해결

---

### Priority 2: 호환성 레이어 (Task 2.2)
- `compat.py` 생성
- `umis_rag/agents/estimator.py` Import 수정

**이유:** 기존 코드 Breaking Change 방지

---

### Priority 3: Models.py 정리 (Task 2.4)
- `Phase3Config`, `Phase4Config` → Alias
- `EstimationResult.phase` → Property

**이유:** 하위 호환성 유지

---

### Priority 4: 테스트 전환 (Task 3.1-3.2)
- Unit Tests
- Integration Tests

**이유:** Coverage 80% 유지

---

## 🔗 의존성 그래프

```
phase4_fermi.py (3,460줄)
    └──> phase3_guestimation.py (466줄)
            └──> source_collector.py
                └──> judgment.py

estimator_v7.10.2.py
    ├──> phase3_guestimation.py
    └──> phase4_fermi.py

umis_rag/agents/estimator.py (최상위)
    └──> phase3_guestimation.py

tests/
    ├──> unit/test_phase3_guestimation.py → Phase3Guestimation
    ├──> unit/test_phase4_fermi.py → Phase4FermiDecomposition
    ├──> test_phase4_parsing_fix.py → Phase4FermiDecomposition
    └──> integration/test_phase_flow.py → Phase 3-4 Flow
```

---

## ✅ 결론

### 핵심 발견
1. **순환 의존성:** `phase4_fermi.py` ↔ `phase3_guestimation.py`
   - **해결:** Archive 이동 시 자동 해결
2. **최상위 Import:** `umis_rag/agents/estimator.py` → Phase3Guestimation
   - **해결:** `compat.py` 생성
3. **테스트 영향:** 4개 테스트 파일
   - **해결:** 2개 전환, 2개 Archive
4. **Config 의존성:** `models.py` (Phase3Config, Phase4Config)
   - **해결:** Alias + Property

### 제거 가능 여부
✅ **안전하게 제거 가능**

**조건:**
1. Archive 이동 (백업 유지)
2. 호환성 레이어 (`compat.py`)
3. 테스트 전환
4. Deprecation Warning

---

## 📊 통계

| 항목 | 수량 |
|-----|-----|
| Phase 3-4 파일 | 4개 (5,257줄) |
| Import 발견 | 22개 파일 (Archive 제외 14개) |
| 실제 사용 코드 | 5개 |
| 테스트 파일 | 4개 |
| 순환 의존성 | 1개 (Critical!) |
| Config 의존성 | 2개 (Phase3Config, Phase4Config) |

---

## 🎯 다음 단계

**Phase 1.2: 테스트 카탈로그 작성**
- 38개 테스트 파일 전체 분류
- 자동 전환 가능 / 수동 재작성 / Archive 결정

---

**작성자:** AI Assistant  
**작성일:** 2025-11-26  
**Task:** Phase 1.1 완료 ✅

**끝.**

