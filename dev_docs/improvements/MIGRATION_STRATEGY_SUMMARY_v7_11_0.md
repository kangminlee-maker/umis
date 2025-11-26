# Phase → Stage 마이그레이션 전략 요약 (v7.11.0)

## 🎯 목표
Phase 5 기반 레거시 아키텍처를 **Stage 4 Fusion Architecture로 100% 전환**

---

## 📊 현황 분석

### 완료된 작업 ✅
- **v7.11.0 Stage 4 아키텍처 구현 완료**
  - `estimator.py`: Stage 1-4 오케스트레이션
  - `evidence_collector.py`: Stage 1 (Literal, Direct RAG, Validator, Guardrails)
  - `prior_estimator.py`: Stage 2 (Generative Prior)
  - `fermi_estimator.py`: Stage 3 (Structural Explanation, 재귀 금지)
  - `fusion_layer.py`: Stage 4 (Sensor Fusion)
- **재귀 제거, Budget 기반 탐색, Certainty 도입**
- **umis.yaml Estimator 섹션 Stage 기반 재작성**

### 제거 대상 ❌
| 파일 | 줄 수 | 상태 | 의존성 |
|-----|------|------|-------|
| `phase3_guestimation.py` | 466 | 레거시 | Source Collector, Judgment Synthesizer |
| `phase3_range_engine.py` | 131 | 레거시 | Source Collector |
| `phase4_fermi.py` | **3,460** | 레거시 | Phase3Guestimation (순환!) |
| `estimator_v7.10.2.py` | 1,200+ | 백업 존재 | Phase 3-4 둘 다 |

### 영향 범위
- **코드:** 38개 테스트 파일
- **문서:** 156개 문서 (dev_docs 포함)
- **Config:** `model_configs.yaml`, `fermi_model_search.yaml` (1,544줄), `tool_registry.yaml`

---

## 🔄 전환 전략: 점진적 제거 (Graceful Deprecation)

### 핵심 원칙
1. **즉시 삭제 X → Archive 이동**
2. **호환성 레이어 유지 (`compat.py`)**
3. **Deprecation Warning으로 안내**
4. **프로덕션 배포 후 2주 모니터링**
5. **완전 제거는 v7.11.1 패치에서**

### 6-Phase 접근법
```
Phase 1: 사전 분석 (1일)
   ↓
Phase 2: 코드 리팩터링 (2일)
   ↓
Phase 3: 테스트 전환 (1일)
   ↓
Phase 4: 문서 업데이트 (1일)
   ↓
Phase 5: Config 통합 (0.5일)
   ↓
Phase 6: 최종 검증 (0.5일)
```

---

## 🚨 3대 리스크 & 대응책

### Risk #1: 순환 의존성
**문제:**
```python
# phase4_fermi.py
from .phase3_guestimation import Phase3Guestimation

# phase3_guestimation.py
# (Phase 4에서 호출됨)
```

**대응:**
- Archive 이동 시 자동 해결 (둘 다 제거)
- `fermi_estimator.py`는 `prior_estimator.py` 직접 사용 (이미 구현됨)

---

### Risk #2: 테스트 대량 손실
**문제:**
- 38개 테스트 파일 중 다수가 Phase 3-4 참조
- 일부는 전환 불가능 (레거시 로직 전용)

**대응:**
1. **자동 전환 가능 (20개 예상)**
   - Import만 수정: `Phase3Guestimation` → `PriorEstimator`
   - Assertion 수정: `result.phase == 3` → `result.source == 'Generative Prior'`

2. **수동 재작성 필요 (10개)**
   - Stage 독립성 테스트
   - Budget 테스트
   - Fusion 테스트

3. **Archive 이동 (8개)**
   - Phase 4 재귀 전용 테스트
   - Step 1-4 세부 테스트

**목표:** Coverage 80% 유지

---

### Risk #3: Breaking Change
**문제:**
- 기존 코드가 `Phase3Guestimation`, `Phase4Config` 직접 사용
- `EstimationResult.phase` 필드 제거 시 호환성 깨짐

**대응:**
1. **호환성 레이어 (`compat.py`)**
   ```python
   # umis_rag/agents/estimator/compat.py
   from .prior_estimator import PriorEstimator as Phase3Guestimation
   from .fermi_estimator import FermiEstimator as Phase4FermiDecomposition
   
   import warnings
   warnings.warn(
       "Phase3Guestimation은 v7.11.0에서 Deprecated입니다.",
       DeprecationWarning
   )
   ```

2. **Property Alias**
   ```python
   # models.py EstimationResult
   @property
   def phase(self) -> int:
       """Deprecated: Use 'source' instead."""
       warnings.warn("...")
       return self._map_source_to_phase()
   ```

3. **Config Alias**
   ```yaml
   # model_configs.yaml
   stages:
     stage_2_generative_prior:
       default_model: gpt-4o-mini
       legacy_alias: phase_3  # 환경변수 호환
   ```

---

## 📋 24-Task 체크리스트

### Phase 1: 사전 분석 (4 tasks)
- [ ] 1.1: 의존성 트리 분석
- [ ] 1.2: 테스트 카탈로그 (38개)
- [ ] 1.3: 문서 인벤토리 (156개)
- [ ] 1.4: Config 변경점 설계

### Phase 2: 코드 리팩터링 (5 tasks)
- [ ] 2.1: Archive 이동 (`phase3_*.py`, `phase4_*.py`)
- [ ] 2.2: `compat.py` 생성
- [ ] 2.3: Utilities 마이그레이션
- [ ] 2.4: `Models.py` 정리
- [ ] 2.5: 순환 의존성 해결

### Phase 3: 테스트 (4 tasks)
- [ ] 3.1: Unit Tests
- [ ] 3.2: Integration Tests
- [ ] 3.3: Benchmarks
- [ ] 3.4: AB Testing

### Phase 4: 문서 (4 tasks)
- [ ] 4.1: API 문서
- [ ] 4.2: Architecture
- [ ] 4.3: 마이그레이션 가이드
- [ ] 4.4: README

### Phase 5: Config (3 tasks)
- [ ] 5.1: `model_configs.yaml`
- [ ] 5.2: `fermi_model_search.yaml`
- [ ] 5.3: `tool_registry.yaml`

### Phase 6: 검증 (4 tasks)
- [ ] 6.1: 전체 테스트 (100% Pass)
- [ ] 6.2: Import 검증
- [ ] 6.3: E2E 시나리오
- [ ] 6.4: 최종 제거 (배포 후)

---

## 🎯 성공 기준

### 필수 (Must Have)
- ✅ 모든 테스트 통과
- ✅ Import 에러 0건
- ✅ API 문서 업데이트
- ✅ `umis.yaml` 일관성

### 권장 (Should Have)
- 🎯 Coverage 80% 이상
- 🎯 Deprecation Warning 최소화
- 🎯 마이그레이션 가이드

---

## 🛠️ 주요 파일 매핑

### Archive 대상
```
umis_rag/agents/estimator/
  phase3_guestimation.py       → archive/phase3_4_legacy_v7.10.2/
  phase3_range_engine.py       → archive/phase3_4_legacy_v7.10.2/
  phase4_fermi.py              → archive/phase3_4_legacy_v7.10.2/
  estimator_v7.10.2.py         → 이미 존재 (재확인)
```

### 신규 Stage 기반
```
umis_rag/agents/estimator/
  estimator.py                 ✅ Stage 1-4 오케스트레이션
  evidence_collector.py        ✅ Stage 1
  prior_estimator.py           ✅ Stage 2
  fermi_estimator.py           ✅ Stage 3
  fusion_layer.py              ✅ Stage 4
```

### 호환성 레이어
```
umis_rag/agents/estimator/
  compat.py                    🆕 생성 (Deprecation Warning)
```

---

## 📅 타임라인

### Week 1 (Days 1-5)
- **Day 1:** Phase 1 완료 (사전 분석)
- **Day 2-3:** Phase 2 완료 (코드 리팩터링)
- **Day 4:** Phase 3 완료 (테스트 전환)
- **Day 5:** Phase 4 완료 (문서 업데이트)

### Week 2 (Days 6-7)
- **Day 6 AM:** Phase 5 완료 (Config)
- **Day 6 PM:** Phase 6 검증
- **Day 7:** Buffer (디버깅)

### Week 3 (Days 8-10)
- **Day 8:** Pull Request 생성
- **Day 9-10:** 코드 리뷰 & 수정

### Week 4+
- **프로덕션 배포**
- **2주 모니터링**
- **v7.11.1 패치 (최종 제거)**

---

## 🔗 관련 문서

1. **Full Plan:** `dev_docs/improvements/PHASE_TO_STAGE_MIGRATION_PLAN_v7_11_0.md` (141줄)
2. **Quickstart:** `MIGRATION_QUICKSTART_v7_11_0.md` (132줄)
3. **v7.11.0 Design:** `dev_docs/improvements/PHASE3_4_REDESIGN_PROPOSAL_v7_11_0.md` (1,119줄)
4. **umis.yaml:** Lines 4880+ (Estimator 섹션, Stage 기반)

---

**작성일:** 2025-11-26  
**버전:** v1.0  
**작성자:** AI Assistant

**끝.**

