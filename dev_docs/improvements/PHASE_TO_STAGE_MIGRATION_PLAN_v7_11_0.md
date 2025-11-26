# Phase 5 → Stage 4 Fusion Architecture 100% 전환 작업 리스트

**버전:** v7.11.0  
**작성일:** 2025-11-26  
**목표:** Phase 기반 레거시 아키텍처를 Stage 기반 Fusion Architecture로 100% 전환  
**난이도:** ★★★★★ (매우 높음)  
**예상 소요:** 4-6일 (집중 작업 시)

---

## 📋 Executive Summary

### 현재 상태
- **v7.11.0 Stage 4 아키텍처 완성:** 
  - `estimator.py`, `evidence_collector.py`, `prior_estimator.py`, `fermi_estimator.py`, `fusion_layer.py`
  - Stage 1-4 기반으로 100% 재설계 완료
  - 재귀 제거, Budget 기반 탐색, Sensor Fusion 구현
- **레거시 Phase 3-4 아직 존재:**
  - `phase3_guestimation.py`, `phase3_range_engine.py`, `phase4_fermi.py` (3,460줄!)
  - 다수의 테스트, 문서, Config 파일들이 Phase 3-4 참조
  - Import 의존성 다수

### 전환 전략
**점진적 제거 (Graceful Deprecation):**
1. **Phase 3-4 파일을 Archive로 이동** (즉시 삭제 X)
2. **Import 경로 리다이렉트** (`phase3_guestimation` → `prior_estimator`)
3. **테스트 100% 마이그레이션**
4. **문서 업데이트**
5. **Config 정리**
6. **최종 검증 후 제거**

### 핵심 리스크
1. **순환 참조:** `phase4_fermi.py`가 `phase3_guestimation.py`에 의존
2. **대규모 테스트 손실 가능성:** 38개 테스트 파일 영향
3. **문서 불일치:** 156개 문서에 Phase 3-4 언급
4. **Config 손상:** `model_configs.yaml`, `fermi_model_search.yaml` 등

---

## 🎯 Phase 1: 사전 분석 및 준비 (1일)

### Task 1.1: 의존성 트리 완전 분석
- [ ] **전체 Import 맵핑** (모든 `.py` 파일)
  ```bash
  rg "from.*phase[34]|import.*Phase[34]" --type py -l
  ```
- [ ] **순환 의존성 식별**
  - `phase4_fermi.py` → `phase3_guestimation.py`
  - `estimator_v7.10.2.py` → 둘 다
- [ ] **의존 컴포넌트 리스트 작성**
  - Source Collector
  - Judgment Synthesizer
  - Learning Writer
  - Boundary Validator
  - 기타 utilities

**출력:** `DEPENDENCY_ANALYSIS_v7_11_0.md`

---

### Task 1.2: 테스트 카탈로그 작성
- [ ] **Phase 3-4 관련 테스트 38개 분류**
  - Unit Tests: `test_phase3_guestimation.py`, `test_phase4_fermi.py`
  - Integration Tests: `test_phase_flow.py`, `test_hybrid_integration.py`
  - Benchmark Tests: `test_phase4_*.py` (10개+)
  - AB Testing: `test_ab_framework.py`
- [ ] **각 테스트의 전환 가능성 평가**
  - 자동 전환 가능: Stage 기반으로 리네이밍
  - 수동 재작성 필요: 로직 변경
  - 삭제 필요: 레거시 전용 테스트

**출력:** `TEST_MIGRATION_CATALOG_v7_11_0.md`

---

### Task 1.3: 문서 인벤토리
- [ ] **156개 문서 스캔**
  ```bash
  rg "Phase [34]|phase_[34]" --type md -l | wc -l
  ```
- [ ] **문서 유형별 분류**
  - 활성 문서 (docs/): API, Guide → 업데이트 필수
  - 개발 히스토리 (dev_docs/): 보존 (과거 기록)
  - Archive: 변경 불필요
- [ ] **업데이트 우선순위 지정**
  1. 사용자 대면 문서 (API, Guide)
  2. 시스템 설계 문서 (Architecture)
  3. 개발 히스토리 (참고용, 낮은 우선순위)

**출력:** `DOCS_UPDATE_PRIORITY_v7_11_0.md`

---

### Task 1.4: Config 파일 변경점 설계
- [ ] **`model_configs.yaml` 리팩터링 설계**
  - `phase_3` → `stage_2_generative_prior`
  - `phase_4` → `stage_3_fermi`
  - 하위 호환성 유지 (Alias?)
- [ ] **`fermi_model_search.yaml` 처리 방침**
  - 1,544줄 대형 파일
  - Phase 4 설계 문서로 Archive 이동?
  - 또는 Stage 3 기반으로 재작성?
- [ ] **`tool_registry.yaml` 업데이트 범위**
  - Phase 3-4 참조 제거
  - Stage 1-4 기반으로 재정의

**출력:** `CONFIG_REFACTORING_DESIGN_v7_11_0.md`

---

## 🔧 Phase 2: 코드 리팩터링 (2일)

### Task 2.1: Phase 3-4 파일 Archive 이동
- [ ] **디렉터리 생성**
  ```bash
  mkdir -p archive/phase3_4_legacy_v7.10.2/
  ```
- [ ] **파일 이동 (즉시 삭제 X)**
  - `phase3_guestimation.py` → Archive
  - `phase3_range_engine.py` → Archive
  - `phase4_fermi.py` → Archive (3,460줄!)
  - `estimator_v7.10.2.py` → Archive (이미 존재하지만 재확인)
- [ ] **README.md 생성**
  - 이동 사유 기록
  - v7.11.0 Fusion Architecture로 대체됨
  - 복원 가능성 (만약을 위해)

**예상 시간:** 1시간

---

### Task 2.2: Import 리다이렉트 레이어 구현
**목적:** 기존 코드가 `phase3_guestimation`을 import해도 동작하도록

**구현 방안:**
1. **Compatibility Module 생성**
   - `umis_rag/agents/estimator/compat.py`
   ```python
   # 호환성 레이어 (v7.11.0)
   from .prior_estimator import PriorEstimator as Phase3Guestimation
   from .fermi_estimator import FermiEstimator as Phase4FermiDecomposition
   
   __all__ = ['Phase3Guestimation', 'Phase4FermiDecomposition']
   ```

2. **`__init__.py` 업데이트**
   ```python
   # 레거시 호환성 (Deprecated)
   from .compat import Phase3Guestimation, Phase4FermiDecomposition
   
   __all__ = [
       'EstimatorRAG',
       # ... (기존)
       'Phase3Guestimation',  # Deprecated, use PriorEstimator
       'Phase4FermiDecomposition',  # Deprecated, use FermiEstimator
   ]
   ```

3. **Deprecation Warning 추가**
   ```python
   import warnings
   warnings.warn(
       "Phase3Guestimation은 v7.11.0에서 Deprecated되었습니다. "
       "대신 PriorEstimator를 사용하세요.",
       DeprecationWarning,
       stacklevel=2
   )
   ```

**체크리스트:**
- [ ] `compat.py` 생성
- [ ] `__init__.py` 업데이트
- [ ] DeprecationWarning 추가
- [ ] 기존 Import 테스트 (실패 없이 동작)

**예상 시간:** 2시간

---

### Task 2.3: Source Collector & Utilities 마이그레이션
**현재 상황:**
- `source_collector.py`는 Phase 3 전용으로 설계
- Stage 2 (Prior)에서는 직접 LLM 호출, 11개 Source 불필요
- Stage 3 (Fermi)에서는 제한적으로만 사용

**전략:**
1. **Source Collector → Evidence Collector로 통합**
   - 이미 `evidence_collector.py` 존재
   - 11개 Source 로직을 Stage 1으로 통합?
   - 또는 별도 모듈로 유지하되 Stage 3에서만 사용

2. **Judgment Synthesizer 처리**
   - Stage 4 Fusion Layer가 이미 역할 대체
   - 삭제 또는 Archive

3. **Learning Writer 보존**
   - 학습 시스템은 여전히 필요
   - Stage 2-3 결과를 학습

**체크리스트:**
- [ ] Source Collector 재평가
  - Stage 3에서 필요 여부 확인
  - 필요시 리팩터링, 불필요시 Archive
- [ ] Judgment Synthesizer 제거
  - Fusion Layer로 대체 완료
- [ ] Learning Writer 보존 및 Stage 연결
  - `prior_estimator.py`, `fermi_estimator.py`에서 호출
- [ ] Boundary Validator 재평가
  - Stage 1 Guardrail Engine과 중복 여부 확인

**예상 시간:** 4시간

---

### Task 2.4: Models.py 정리
**현재 상황:**
- `Phase3Config`, `Phase4Config` 클래스 존재
- `EstimationResult.phase` 필드 (0-4)

**변경 사항:**
1. **Config 클래스 Deprecate**
   ```python
   # models.py
   
   # Deprecated (v7.11.0)
   Phase3Config = PriorEstimatorConfig  # Alias
   Phase4Config = FermiEstimatorConfig  # Alias
   ```

2. **EstimationResult.phase 처리**
   - 완전 제거? → Breaking Change 발생
   - Alias로 유지? → `source` 필드와 매핑
   ```python
   @property
   def phase(self) -> int:
       """Deprecated: Use 'source' instead."""
       warnings.warn("EstimationResult.phase는 Deprecated입니다.", DeprecationWarning)
       source_map = {
           'Literal': 0,
           'Direct RAG': 1,
           'Validator Search': 2,
           'Generative Prior': 2,
           'Fermi': 3,
           'Fusion': 4
       }
       return source_map.get(self.source, -1)
   ```

**체크리스트:**
- [ ] `Phase3Config`, `Phase4Config` → Alias 또는 Deprecate
- [ ] `EstimationResult.phase` → Property로 하위 호환성
- [ ] `DecompositionTrace` 확인 (Fermi 전용, 보존)
- [ ] 기타 Phase 관련 Enum/상수 정리

**예상 시간:** 2시간

---

### Task 2.5: 순환 의존성 해결
**문제:**
- Old `phase4_fermi.py` → `phase3_guestimation.py`
- 둘 다 Archive로 이동하면 해결되지만, 혹시 남은 참조 확인 필요

**체크리스트:**
- [ ] 전체 코드베이스 스캔
  ```bash
  rg "from.*phase[34]_" --type py
  ```
- [ ] 발견된 Import를 모두 리다이렉트 또는 제거
- [ ] Circular Import 테스트
  ```bash
  python -c "from umis_rag.agents.estimator import EstimatorRAG"
  ```

**예상 시간:** 1시간

---

## 🧪 Phase 3: 테스트 마이그레이션 (1일)

### Task 3.1: Unit Tests 전환
**대상 파일:**
- `tests/unit/test_phase3_guestimation.py`
- `tests/unit/test_phase4_fermi.py`

**전환 전략:**
1. **파일명 변경**
   - `test_phase3_guestimation.py` → `test_prior_estimator.py`
   - `test_phase4_fermi.py` → `test_fermi_estimator.py`

2. **Import 수정**
   ```python
   # Before
   from umis_rag.agents.estimator.phase3_guestimation import Phase3Guestimation
   
   # After
   from umis_rag.agents.estimator import PriorEstimator
   ```

3. **Assertion 수정**
   ```python
   # Before
   assert result.phase == 3
   
   # After
   assert result.source in ['Generative Prior', 'Fusion']
   ```

**체크리스트:**
- [ ] `test_prior_estimator.py` 생성 및 실행
- [ ] `test_fermi_estimator.py` 생성 및 실행
- [ ] Coverage 확인 (80% 이상 유지)
- [ ] 기존 테스트 Archive 이동

**예상 시간:** 3시간

---

### Task 3.2: Integration Tests 전환
**대상 파일:**
- `tests/integration/test_phase_flow.py`
- `tests/integration/test_hybrid_integration.py`

**전환 전략:**
1. **Flow 테스트 재설계**
   - Phase 0→1→2→3→4 → Stage 1→2→3→4
   - Early Return 테스트 강화

2. **Hybrid Architecture → Fusion Architecture**
   - 파일명 변경: `test_fusion_integration.py`
   - Stage 독립성 테스트 추가
   - Budget 소진 테스트 추가

**체크리스트:**
- [ ] `test_stage_flow_v7_11_0.py` 생성
- [ ] `test_fusion_integration.py` 수정
- [ ] End-to-End 시나리오 10개 검증
- [ ] 기존 테스트 Archive

**예상 시간:** 4시간

---

### Task 3.3: Benchmark Tests 정리
**대상 파일 (10개+):**
- `test_phase4_model_config.py`
- `test_phase4_creative.py`
- `test_phase4_parsing_fix.py`
- `test_phase4_quick.py`
- `test_phase4_quick_final.py`
- `test_phase_0_4_comprehensive.py`
- 기타 `benchmarks/estimator/phase4/` 내 파일들

**전략:**
1. **필수 벤치마크만 전환**
   - 10개 Fermi 문제 테스트 (`test_v7_11_0_fermi_10problems.py` 이미 존재!)
   - 전환 가능 테스트만 Stage 3 기반으로 리네이밍

2. **나머지는 Archive**
   - Phase 4 특정 로직 테스트 (재귀, Step 1-4 등)
   - 역사적 가치만 있는 벤치마크

**체크리스트:**
- [ ] 필수 벤치마크 5개 선정
- [ ] Stage 3 기반으로 전환
- [ ] 나머지 Archive 이동
- [ ] `benchmarks/estimator/phase4/` → `benchmarks/estimator/stage3/` 리네이밍

**예상 시간:** 2시간

---

### Task 3.4: AB Testing Framework 업데이트
**대상 파일:**
- `tests/ab_testing/test_ab_framework.py`

**변경 사항:**
- Phase 3-4 비교 → Stage 2-3 비교
- Metric 재정의 (certainty, budget)

**체크리스트:**
- [ ] AB Testing 로직 Stage 기반으로 수정
- [ ] 새로운 메트릭 추가 (LLM calls, budget 소진율)
- [ ] 테스트 실행 및 검증

**예상 시간:** 2시간

---

## 📄 Phase 4: 문서 업데이트 (1일)

### Task 4.1: 사용자 대면 문서 (최우선)
**대상 파일:**
- `docs/api/ESTIMATOR_API_v7_9_0.md`
- `docs/guides/ESTIMATOR_USER_GUIDE_v7_9_0.md`
- `umis.yaml` (이미 완료, 재확인)

**변경 사항:**
1. **API 문서**
   - Phase 0-4 → Stage 1-4 + Components
   - `EstimationResult.phase` → `EstimationResult.source`
   - `Phase3Config` → Deprecated, use `Budget`

2. **User Guide**
   - 5-Phase Architecture → 4-Stage Fusion Architecture
   - 예제 코드 업데이트
   - 마이그레이션 가이드 추가

**체크리스트:**
- [ ] `ESTIMATOR_API_v7_11_0.md` 생성
- [ ] `ESTIMATOR_USER_GUIDE_v7_11_0.md` 생성
- [ ] 마이그레이션 가이드 섹션 추가
- [ ] 기존 v7.9.0 문서 Archive

**예상 시간:** 3시간

---

### Task 4.2: 시스템 설계 문서
**대상 파일:**
- `docs/architecture/UMIS_ARCHITECTURE_BLUEPRINT.md`
- `dev_docs/improvements/PHASE3_4_REDESIGN_PROPOSAL_v7_11_0.md` (이미 최신)

**변경 사항:**
- Blueprint 업데이트 (Estimator 섹션)
- 다이어그램 재생성 (Phase → Stage)

**체크리스트:**
- [ ] Architecture Blueprint 수정
- [ ] 다이어그램 업데이트 (Mermaid 또는 ASCII art)
- [ ] v7.11.0 섹션 추가

**예상 시간:** 2시간

---

### Task 4.3: 개발 히스토리 문서 (선택)
**대상 파일 (156개):**
- `dev_docs/improvements/PHASE_3_4_IMPROVEMENTS_v7_8_1.md`
- `dev_docs/issues/PHASE3_PHASE4_DETAILED_ANALYSIS.md`
- 기타 다수

**전략:**
- **보존 원칙:** 과거 기록은 수정하지 않음
- **새 문서 추가:** `v7_11_0_MIGRATION_COMPLETE.md`

**체크리스트:**
- [ ] 156개 문서 보존 (수정 X)
- [ ] `v7_11_0_MIGRATION_COMPLETE.md` 작성
  - Before/After 비교
  - Breaking Changes 목록
  - 마이그레이션 체크리스트

**예상 시간:** 1시간

---

### Task 4.4: README 업데이트
**대상 파일:**
- `umis_rag/agents/estimator/README.md`
- `benchmarks/estimator/README.md` (존재 시)

**변경 사항:**
- Phase 3-4 언급 제거
- Stage 1-4 기반 설명
- 파일 구조 업데이트

**체크리스트:**
- [ ] Estimator README 전면 개편
- [ ] Benchmarks README 업데이트
- [ ] 기존 README Archive

**예상 시간:** 1시간

---

## ⚙️ Phase 5: Config & 시스템 통합 (0.5일)

### Task 5.1: model_configs.yaml 리팩터링
**변경 사항:**
```yaml
# Before
phases:
  phase_3:
    default_model: gpt-4o-mini
    ...
  phase_4:
    default_model: o1-mini
    ...

# After
stages:
  stage_2_generative_prior:
    default_model: gpt-4o-mini
    legacy_alias: phase_3  # 호환성
    ...
  stage_3_fermi:
    default_model: o1-mini
    legacy_alias: phase_4  # 호환성
    ...
```

**하위 호환성 유지:**
- `LLM_MODEL_PHASE3`, `LLM_MODEL_PHASE4` 환경변수 여전히 동작
- 내부적으로 Stage 2, 3으로 매핑

**체크리스트:**
- [ ] `model_configs.yaml` 백업
- [ ] Stage 기반 구조 작성
- [ ] Legacy alias 추가
- [ ] 환경변수 매핑 코드 수정 (`model_router.py`)
- [ ] 테스트 실행

**예상 시간:** 2시간

---

### Task 5.2: fermi_model_search.yaml 처리
**현재:** 1,544줄 대형 Phase 4 설계 문서

**옵션:**
1. **Archive 이동 (권장)**
   - `archive/phase3_4_legacy_v7.10.2/fermi_model_search.yaml`
   - 역사적 가치는 있으나 현재 Stage 3와 로직 차이 큼

2. **Stage 3 기반 재작성**
   - 재귀 제거, Budget 기반으로 재설계
   - 시간 소요 큼 (6-8시간)

**결정:** Archive 이동 (재작성 불필요, Stage 3는 단순함)

**체크리스트:**
- [ ] `fermi_model_search.yaml` Archive 이동
- [ ] README 작성 (이동 사유)

**예상 시간:** 30분

---

### Task 5.3: tool_registry.yaml 업데이트
**변경 사항:**
- Phase 3-4 언급 제거
- Stage 1-4 기반 설명

**체크리스트:**
- [ ] `tool_registry.yaml` 백업
- [ ] Estimator 섹션 수정
- [ ] System RAG 재구축 (필요 시)

**예상 시간:** 1시간

---

## ✅ Phase 6: 최종 검증 및 Clean-up (0.5일)

### Task 6.1: 전체 테스트 실행
```bash
# Unit Tests
pytest tests/unit/test_estimator*.py -v

# Integration Tests
pytest tests/integration/ -v

# v7.11.0 Fusion Tests
pytest tests/test_v7_11_0*.py -v

# Benchmarks (선택)
python tests/test_v7_11_0_fermi_10problems.py
```

**목표:**
- 100% Pass Rate
- 0 Deprecation Warnings (또는 예상된 Warning만)

**체크리스트:**
- [ ] 모든 테스트 통과
- [ ] Coverage 80% 이상 유지
- [ ] Linting 통과 (`ruff`, `mypy`)

**예상 시간:** 2시간

---

### Task 6.2: Import 검증
```bash
# Python 환경에서 Import 테스트
python -c "
from umis_rag.agents.estimator import (
    EstimatorRAG,
    PriorEstimator,
    FermiEstimator,
    FusionLayer,
    EvidenceCollector,
    Budget,
    EstimationResult
)
print('✅ All imports successful!')
"

# 레거시 호환성 테스트 (Deprecation Warning 예상)
python -c "
from umis_rag.agents.estimator import Phase3Guestimation, Phase4FermiDecomposition
print('✅ Legacy imports work (with warnings)')
"
```

**체크리스트:**
- [ ] 모든 Import 성공
- [ ] 레거시 Import도 동작 (Warning 포함)

**예상 시간:** 30분

---

### Task 6.3: E2E 시나리오 테스트
**시나리오 10개:**
1. Evidence Collection에서 즉시 반환 (Literal)
2. Prior만 사용 (Fermi 없이)
3. Fermi만 사용 (Prior 실패)
4. Fusion (Prior + Fermi 둘 다)
5. Budget 소진
6. Guardrails 적용
7. 학습 시스템 (Phase 1 Direct RAG)
8. Fast mode (`estimate_fast()`)
9. Thorough mode (`estimate_thorough()`)
10. Context 기반 추정

**체크리스트:**
- [ ] 각 시나리오 검증
- [ ] 결과 로그 확인
- [ ] 성능 메트릭 확인 (시간, LLM calls)

**예상 시간:** 2시간

---

### Task 6.4: 레거시 파일 최종 제거 (선택)
**타이밍:** v7.11.0 프로덕션 배포 후 1-2주

**제거 대상:**
- `archive/phase3_4_legacy_v7.10.2/` 전체
- `compat.py` (호환성 레이어)
- `EstimationResult.phase` Property

**체크리스트:**
- [ ] 프로덕션 모니터링 2주
- [ ] 레거시 Import 사용 로그 확인 (없어야 함)
- [ ] 최종 제거 실행
- [ ] v7.11.1 패치 릴리즈

**예상 시간:** 1시간 (미래)

---

## 📊 진행 상황 추적

### Overall Progress
```
Phase 1: 사전 분석 및 준비      [ ] 0/4 tasks
Phase 2: 코드 리팩터링          [ ] 0/5 tasks
Phase 3: 테스트 마이그레이션    [ ] 0/4 tasks
Phase 4: 문서 업데이트          [ ] 0/4 tasks
Phase 5: Config & 시스템 통합   [ ] 0/3 tasks
Phase 6: 최종 검증             [ ] 0/4 tasks

Total: 0/24 major tasks
```

---

## 🚨 리스크 관리

### High Risk
1. **순환 의존성 미해결**
   - **대응:** Task 2.5에서 철저히 검증
   - **Fallback:** Archive 파일 임시 복원

2. **테스트 대량 손실**
   - **대응:** Task 3.1-3.3에서 커버리지 80% 유지
   - **Fallback:** 기존 테스트 Archive에서 복원

3. **프로덕션 Breaking Change**
   - **대응:** Deprecation Warning + 호환성 레이어 유지
   - **Fallback:** v7.11.0 롤백 가능하도록 Git Tag

### Medium Risk
1. **문서 불일치**
   - **대응:** Task 4.1 우선 처리 (사용자 대면)
   - **Fallback:** Phase 3-4 언급은 "Legacy" 표시

2. **Config 손상**
   - **대응:** 모든 Config 파일 백업
   - **Fallback:** `config/backups/` 복원

### Low Risk
1. **개발 히스토리 문서 혼란**
   - **대응:** 보존 원칙 (수정 X)
   - **영향:** 없음 (과거 기록)

---

## 📈 성공 기준

### Mandatory (필수)
- [ ] 모든 테스트 통과 (100% Pass Rate)
- [ ] 0 Import Errors
- [ ] API 문서 업데이트 완료
- [ ] `umis.yaml` 일관성 유지

### Recommended (권장)
- [ ] Coverage 80% 이상
- [ ] Deprecation Warning 최소화
- [ ] 마이그레이션 가이드 제공

### Stretch Goals (추가)
- [ ] Stage 3 Fermi 성능 개선 (Budget 최적화)
- [ ] Learning System 강화 (Year 1 목표 달성)
- [ ] 새로운 벤치마크 추가

---

## 📅 예상 일정

| Phase | 소요 시간 | 누적 |
|-------|---------|-----|
| Phase 1 | 1일 | 1일 |
| Phase 2 | 2일 | 3일 |
| Phase 3 | 1일 | 4일 |
| Phase 4 | 1일 | 5일 |
| Phase 5 | 0.5일 | 5.5일 |
| Phase 6 | 0.5일 | 6일 |

**총 예상:** 6일 (집중 작업 시)  
**현실적:** 7-10일 (병렬 작업 + 디버깅 시간)

---

## 🎯 Next Steps

### Immediate (지금 바로)
1. **Phase 1.1 시작:** 의존성 트리 분석
2. **환경 백업:** Git branch 생성
   ```bash
   git checkout -b feature/phase-to-stage-migration-v7.11.0
   ```

### After Completion
1. **Pull Request 생성**
2. **코드 리뷰 (48시간)**
3. **프로덕션 배포**
4. **모니터링 2주**
5. **v7.11.1 패치 (레거시 최종 제거)**

---

## 📝 Notes

- **점진적 접근:** 한 번에 모든 것을 바꾸지 않음
- **하위 호환성:** 최대한 유지 (DeprecationWarning 활용)
- **테스트 우선:** 코드 변경 전 테스트 마이그레이션
- **문서 동기화:** 코드와 문서 동시 업데이트

**작성자:** AI Assistant  
**검토자:** [To be assigned]  
**승인자:** [To be assigned]

---

**끝.**

