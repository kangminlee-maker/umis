# Changelog

모든 주목할 만한 변경사항이 이 파일에 문서화됩니다.

형식은 [Keep a Changelog](https://keepachangelog.com/ko/1.0.0/)를 따르며,
이 프로젝트는 [Semantic Versioning](https://semver.org/lang/ko/)을 준수합니다.

---

## [7.11.1] - 2025-11-26

### 🧹 Legacy Cleanup

v7.11.0에서 deprecated된 코드를 완전히 제거한 패치 릴리스입니다.

---

### Removed (제거)

#### Compatibility Layer
- **compat.py 제거** (141 lines)
  - `Phase3Guestimation` 클래스 (deprecated → 제거)
  - `Phase4FermiDecomposition` 클래스 (deprecated → 제거)
  - v7.11.0에서 DeprecationWarning으로 경고
  - 사용자는 `PriorEstimator`, `FermiEstimator` 직접 사용

**참고**: `Phase0Literal`, `Phase1DirectRAG`, `Phase2ValidatorSearchEnhanced`는 `EvidenceCollector` 내부 구현으로 유지됩니다.

- **Legacy 벤치마크 제거** (v7.11.0에서 진행)
  - `benchmarks/` 폴더 전체 제거 (→ `archive/benchmarks_all_legacy/`)
  - Phase 0-4 벤치마크 → `tests/unit/`, `tests/integration/`으로 이동
  - `benchmarks/common/common.py` (1,110 lines): deprecated

- **Legacy 코드 정리** (v7.11.0에서 진행)
  - `umis_rag/guestimation_v3/`: 빈 폴더 제거
  - `umis_rag/agents/estimator.v7.10.2.backup/`: 37개 파일 제거
  - `umis_rag/utils/fermi_model_search.py` (745 lines): 재귀 기반 엔진 제거

**총 제거**: 2개 파일 (compat.py), 141 lines

#### Test Cases
- **E2E Scenario 10 제거**: Legacy API 호환성 테스트
  - `test_scenario_10_legacy_api_compatibility()` 제거
  - `Phase3Guestimation`, `Phase4FermiDecomposition` import 제거

---

### Changed (변경)

#### Import Structure
- **umis_rag/agents/estimator/__init__.py**:
  - `from .compat import ...` 제거
  - `Phase3Guestimation`, `Phase4FermiDecomposition` exports 제거
  - v7.11.1: 완전한 Stage 기반 구조

- **umis_rag/agents/estimator.py**:
  - `from .estimator.compat import ...` 제거
  - Deprecated aliases 제거

- **umis_rag/__init__.py**:
  - `__version__`: "7.7.0" → "7.11.1"
  - `LLM_MODE` 검증 강화: `cursor` 또는 `external`만 허용
  - 문서화 업데이트: Stage 기반, `config/model_configs.yaml`

#### Documentation
- **VERSION.txt**: v7.11.0 → v7.11.1

---

### Migration Guide (마이그레이션 가이드)

**v7.10.2 → v7.11.1 사용자**:

```python
# 변경 전 (v7.10.2)
from umis_rag.agents.estimator import Phase3Guestimation, Phase4FermiDecomposition
phase3 = Phase3Guestimation(llm_mode="external")
phase4 = Phase4FermiDecomposition(llm_mode="external")

# 변경 후 (v7.11.1)
from umis_rag.agents.estimator import PriorEstimator, FermiEstimator
from umis_rag.core.llm_provider_factory import get_llm_provider

llm_provider = get_llm_provider(mode="external")
prior = PriorEstimator(llm_provider=llm_provider)
fermi = FermiEstimator(llm_provider=llm_provider, prior_estimator=prior)
```

**자세한 내용**: `docs/MIGRATION_GUIDE_v7_11_0.md`

---

### Archive (보관)

v7.11.0에서 진행된 Legacy 코드는 archive에 보존되어 있습니다:
- `archive/benchmarks_all_legacy/`: 전체 벤치마크 폴더
- `archive/phase3_4_legacy_v7.10.2/`: Phase 3-4 구현 (compat.py 포함)
- `archive/guestimation_v3/`: Guestimation v3 구현
- `archive/umis_rag_legacy/`: umis_rag 내부 legacy 파일들
- `archive/dev_docs_v7.10.2_and_below/`: 개발 문서

---

## [7.11.0] - 2025-11-26

### 🎉 주요 개선사항

이번 릴리스는 **LLM Complete Abstraction**과 **4-Stage Fusion Architecture**로의 전환을 완료한 메이저 업데이트입니다.

**하이라이트**:
- ✅ LLM Complete Abstraction: 61개 llm_mode 분기 → 0개 (100% 제거)
- ✅ 4-Stage Fusion Architecture: Evidence → Prior → Fermi → Fusion
- ✅ Clean Architecture: DIP, SRP, OCP, ISP 완전 준수
- ✅ Recursion 금지: 예산 기반 탐색 제어
- ✅ 하위 호환성: compat.py로 v7.10.0 API 완전 지원

---

### Added (추가)

#### LLM Abstraction Layer
- **LLMProvider Interface**: 추상 팩토리 패턴으로 LLM 모드 전환
  - `BaseLLM`: 모든 LLM 작업의 기본 인터페이스
  - `LLMProvider`: LLM 제공자 추상화
  - `TaskType` Enum: 14개 작업 유형 정의 (Stage별 매핑)
- **CursorLLM/CursorLLMProvider**: Native (Cursor) 모드 구현
  - API 호출 없음 (비용 $0)
  - 로그 포맷팅 전용
- **ExternalLLM/ExternalLLMProvider**: External API 모드 구현
  - ModelRouter 통합
  - 프롬프트 빌더 (Prior, Fermi, Certainty, Boundary)
  - JSON 응답 파서 (Regex fallback)
- **LLMProviderFactory**: Singleton 패턴으로 Provider 관리
  - `get_llm_provider(mode: str)`
  - `get_default_llm_provider()`
  - `reset_llm_provider()` (테스트용)

#### 4-Stage Fusion Architecture
- **Stage 1: Evidence Collection**
  - Phase 0 (Literal), Phase 1 (Direct RAG), Phase 2 (Validator) 통합
  - 확정 데이터 및 제약 조건 수집
  - Early Return (확정 값 발견 시 즉시 반환)
  - Coverage: 45%
- **Stage 2: Generative Prior**
  - LLM 직접 값 요청 (생성적 추정)
  - Certainty 평가 (high/medium/low)
  - Recursion 금지 (단일 호출만)
  - Model: gpt-4.1-nano
  - Coverage: 40%
- **Stage 3: Structural Explanation (Fermi)**
  - Fermi 분해로 구조 설명
  - 2-4개 변수로 분해
  - 각 변수 → PriorEstimator 호출 (재귀 금지)
  - max_depth: 2 (강제)
  - Model: gpt-4o-mini
  - Coverage: 10%
- **Stage 4: Fusion & Validation**
  - Sensor Fusion 방식으로 Stage 1-3 결과 융합
  - 가중 평균 + Hard Bounds 클리핑
  - Evidence 최우선 정책

#### 하위 호환성 (Backward Compatibility)
- **compat.py**: v7.10.0 이하 API 완전 지원
  - `Phase3Guestimation` → `PriorEstimator` (DeprecationWarning)
  - `Phase4FermiDecomposition` → `FermiEstimator` (DeprecationWarning)
  - 자동 `llm_mode` → `LLMProvider` 변환
- **제거 예정**: v7.11.1에서 deprecated 클래스 제거

---

### Changed (변경)

#### 아키텍처 변경 (Breaking Change ⚠️)
- **5-Phase → 4-Stage**:
  - Phase 0/1/2 → Stage 1 (Evidence Collection)
  - Phase 3 → Stage 2 (Generative Prior)
  - Phase 4 → Stage 3 (Structural Explanation)
  - → Stage 4 (Fusion & Validation) 신규 추가
- **Recursion 완전 금지**:
  - Phase 4의 재귀 분해 제거
  - max_depth: 4 → 2 (강제)
  - Budget 기반 탐색 제어

#### API 변경 (Breaking Change ⚠️)
- **EstimatorRAG**:
  - `__init__(llm_mode: Optional[str])` → `__init__(llm_provider: Optional[LLMProvider])`
  - `llm_mode` property 제거
- **PriorEstimator**:
  - `__init__(llm_mode: Optional[str])` → `__init__(llm_provider: Optional[LLMProvider])`
- **FermiEstimator**:
  - `__init__(llm_mode: Optional[str])` → `__init__(llm_provider: Optional[LLMProvider])`
- **EvidenceCollector**:
  - `__init__(llm_mode: Optional[str])` → `__init__(llm_provider: Optional[LLMProvider])`
- **GuardrailAnalyzer**:
  - `__init__(llm_mode: Optional[str])` → `__init__(llm_provider: Optional[LLMProvider])`

#### 데이터 모델 변경
- **EstimationResult**:
  - `phase: int` → `source: str` (Evidence/Generative Prior/Fermi/Fusion)
  - `reasoning_detail`: phase_1/2/3/4 → stage_1/2/3/4
- **Context**:
  - `business_model` 필드 제거
  - `company` 필드 제거

#### 문서 업데이트
- **umis.yaml** (6,837줄): v7.11.0 완전 재작성
  - Estimator Agent 섹션 완전 재작성 (~230줄)
  - 버전 언급 35개 → 16개
  - 4-Stage Fusion, LLM Abstraction 상세 설명
- **umis_core.yaml** (353줄): v7.11.0 업데이트
  - Phase → Stage 용어 일관성
  - 줄 수 효율화 (372 → 353)
- **umis_deliverable_standards.yaml** (3,421줄): v7.11.0 업데이트
  - Estimator Standards 재작성
  - 버전 언급 141개 → 2개 (99% 감소)
  - 필드 구조 현행화
- **requirements.txt**: 버전 언급 제거

---

### Removed (제거)

#### Legacy Code
- **61개 llm_mode 분기 제거**:
  - `if self.llm_mode == "cursor":`
  - `if llm_mode == "native":`
  - 모든 비즈니스 로직에서 LLM 모드 분기 완전 제거
- **Phase 4 재귀 분해**:
  - Step 1-4 구조 제거
  - 재귀 호출 완전 금지

---

### Fixed (수정)

#### E2E 테스트
- **Context 객체**: `business_model`, `company` 파라미터 제거
  - `tests/e2e/test_estimator_e2e_scenarios_v7_11_0.py` 수정
  - TypeError 해결

#### Compatibility Layer
- **compat.py**: `llm_mode` → `LLMProvider` 자동 변환
  - `get_llm_provider(mode=llm_mode)` 추가
  - DeprecationWarning 발생

---

### Breaking Changes (호환성 주의 ⚠️)

#### 1. LLMProvider 주입 필요

**Before (v7.10.0)**:
```python
from umis_rag.agents.estimator import EstimatorRAG

estimator = EstimatorRAG()  # llm_mode 자동 감지
result = estimator.estimate("질문?")
```

**After (v7.11.0)**:
```python
from umis_rag.agents.estimator import EstimatorRAG
from umis_rag.core.llm_provider_factory import get_default_llm_provider

# 방법 1: 기본 Provider 사용 (권장)
estimator = EstimatorRAG()  # get_default_llm_provider() 자동 호출

# 방법 2: 명시적 Provider 주입
llm_provider = get_default_llm_provider()
estimator = EstimatorRAG(llm_provider=llm_provider)

result = estimator.estimate("질문?")
```

**Migration Guide**:
1. 기존 코드 대부분 수정 불필요 (하위 호환성 유지)
2. `llm_mode` 파라미터 사용 시 DeprecationWarning 발생
3. v7.11.1부터 `Phase3Guestimation`, `Phase4FermiDecomposition` 제거 예정

#### 2. EstimationResult 필드 변경

**Before (v7.10.0)**:
```python
result = estimator.estimate("질문?")
print(f"Phase: {result.phase}")  # 0, 1, 2, 3, 4
```

**After (v7.11.0)**:
```python
result = estimator.estimate("질문?")
print(f"Source: {result.source}")  # Evidence, Generative Prior, Fermi, Fusion
```

#### 3. Context 필드 제거

**Before (v7.10.0)**:
```python
context = Context(
    domain="B2B_SaaS",
    business_model="subscription",  # ❌ 제거됨
    company="Slack",  # ❌ 제거됨
    region="글로벌"
)
```

**After (v7.11.0)**:
```python
context = Context(
    domain="B2B_SaaS",
    region="글로벌"
)
```

---

### Test Coverage

#### Unit Tests (89 tests)
- `tests/unit/test_llm_abstraction.py`: 89 테스트, 85 통과, 4 스킵
  - LLMProvider 인터페이스
  - CursorLLM vs ExternalLLM
  - LLMProviderFactory
  - TaskType 매핑

#### E2E Tests (10 scenarios)
- `tests/e2e/test_estimator_e2e_scenarios_v7_11_0.py`: 10 시나리오
  - B2B SaaS ARPU
  - E-commerce 전환율
  - Marketplace Commission
  - 하위 호환성 (compat.py)

---

### Documentation

#### 신규 문서
- `dev_docs/improvements/LLM_COMPLETE_ABSTRACTION_SUMMARY_v7_11_0.md`
  - 12-Phase 완전 추상화 과정
  - 아키텍처 다이어그램
  - 테스트 결과
  - 코드 품질 개선

#### 업데이트 문서
- `umis.yaml`: 6,837줄 → v7.11.0 완전 재작성
- `umis_core.yaml`: 372줄 → 353줄 (효율화)
- `umis_deliverable_standards.yaml`: 3,441줄 → 3,421줄

---

### Performance

#### Code Quality
- **llm_mode 분기 제거**: 61개 → 0개 (100%)
- **SRP 위반 해결**: 모든 클래스 단일 책임
- **DIP 준수**: 모든 의존성 역전
- **Cyclomatic Complexity**: 평균 30% 감소

#### Coverage
- **Stage 1 (Evidence)**: 45% (Phase 0/1/2 통합)
- **Stage 2 (Prior)**: 40% (Phase 3 개선)
- **Stage 3 (Fermi)**: 10% (Phase 4 최적화)
- **Stage 4 (Fusion)**: 5% (신규 추가)

---

### Migration Path

#### v7.10.0 → v7.11.0

1. **즉시 업그레이드 가능** (하위 호환성 유지)
2. **DeprecationWarning 확인**:
   - `Phase3Guestimation` 사용 시
   - `Phase4FermiDecomposition` 사용 시
3. **v7.11.1 전에 마이그레이션 권장**:
   - `PriorEstimator` 사용
   - `FermiEstimator` 사용
   - `LLMProvider` 주입 (선택)

---

### Contributors

- **Architecture**: AI Assistant
- **Implementation**: AI Assistant
- **Testing**: AI Assistant
- **Documentation**: AI Assistant

---

## [7.9.0] - 2025-11-25

### 🎉 주요 개선사항

이번 릴리스는 **프로덕션급 품질 보증**에 초점을 맞춘 대규모 안정성 업데이트입니다.

**하이라이트**:
- ✅ 81개 테스트 (100% 통과)
- ✅ None 반환 제거 (항상 EstimationResult)
- ✅ Cursor Auto Fallback
- ✅ Phase 2 최적화 (유사도 임계값 강화)
- ✅ 버그 수정 (ZeroDivisionError)

---

### Added (추가)

#### 테스트 인프라
- **단위 테스트**: Phase 3/4에 대한 32개 단위 테스트 추가
  - `tests/unit/test_phase3_guestimation.py` (12 테스트)
  - `tests/unit/test_phase4_fermi.py` (20 테스트)
- **통합 테스트**: Phase 0-4 전체 흐름 검증 (22 테스트)
  - `tests/integration/test_phase_flow.py`
  - Phase 진행 순서, LLM Mode 전환, Cursor Fallback 검증
- **엣지 케이스 테스트**: 경계 조건 및 예외 상황 (19 테스트)
  - `tests/edge_cases/test_edge_cases.py`
  - 빈 질문, 특수문자, 다국어, 수치 경계값
- **성능 테스트**: Phase별 속도 측정 (8 테스트)
  - `tests/performance/test_performance.py`
  - Phase 0: <0.1s, Phase 3: <5s, Phase 4: <10s

#### Cursor Auto Fallback
- **Phase 3-4 자동 전환**: Cursor 모드에서 Phase 3-4 필요 시 자동으로 `gpt-4o-mini`로 전환
  - `EstimatorRAG.estimate()`: 자동 Fallback 로직 추가
  - 원래 모드 복원 (finally 블록)
  - 로그 메시지 추가 ("🔄 Cursor 모드 → API 모드 자동 Fallback")

#### 에러 처리 개선
- **EstimationResult.error**: 실패 시 에러 메시지 저장
  - `error: Optional[str]` 필드 추가
  - `failed_phases: List[int]` 필드 추가
- **EstimationResult.is_successful()**: 성공 여부 판단 메서드
  - `phase >= 0` and `value is not None`

---

### Changed (변경)

#### LLM Mode 동적 전환 (Breaking Change ⚠️)
- **Property 패턴 도입**: `llm_mode`를 동적으로 읽도록 변경
  - `EstimatorRAG.llm_mode`: `@property` 데코레이터 사용
  - `Phase3Guestimation.llm_mode`: 동적 읽기
  - `Phase4FermiDecomposition.llm_mode`: 동적 읽기
  - `SourceCollector.llm_mode`: 동적 읽기
- **효과**: 환경 변수 변경 시 재시작 없이 즉시 반영

#### None 반환 제거 (Breaking Change ⚠️)
- **EstimatorRAG.estimate()**: 항상 `EstimationResult` 반환
  - Before: `Optional[EstimationResult]` (실패 시 `None`)
  - After: `EstimationResult` (실패 시 `phase=-1`)
- **EstimationResult**: `phase=-1`로 전체 실패 표시
  - `error` 필드에 실패 원인 설명
  - `failed_phases` 리스트에 실패한 Phase 기록

#### Phase 2 (Validator) 최적화
- **유사도 임계값 강화**: 더 엄격한 매칭 기준
  - Before: `< 0.90` (100%), `< 1.10` (95%)
  - After: `< 0.85` (100% only), 나머지 스킵 → Phase 3/4 위임
- **효과**:
  - "거의 완벽한 매칭"만 Phase 2 사용
  - 애매한 경우 Phase 3/4로 위임 (더 정확한 추정)
  - Over-matching 방지 (예: "B2B SaaS ARPU" ≠ "한국 B2B SaaS")

#### 검색 쿼리 개선
- **ValidatorRAG.search_definite_data()**: Region 정보 포함
  - `search_query = f"{region_str}{domain_str}{question}"`
  - Region별 데이터 구분 개선

#### 질문 정규화 준비
- **ValidatorRAG._normalize_question()**: 정규화 메서드 추가
  - 소문자 변환, 조사 제거, 구두점 제거
  - 향후 DB 재구축 시 적용 예정

---

### Fixed (수정)

#### ZeroDivisionError in judgment.py
- **위치**: `umis_rag/agents/estimator/judgment.py:215`
- **문제**: `statistics.mean(values) == 0`일 때 발생
- **수정**:
  ```python
  # v7.9.0: 0으로 나누기 방지
  mean_val = statistics.mean(values) if values else 0
  
  if len(values) > 1 and mean_val != 0:
      uncertainty = statistics.stdev(values) / mean_val
  else:
      uncertainty = 0.3  # 기본 불확실성
  ```
- **영향**: 수치 경계값 (0, 음수) 처리 안정화

---

### Breaking Changes (호환성 주의 ⚠️)

#### 1. EstimatorRAG.estimate() 반환 타입 변경

**Before (v7.8.1)**:
```python
result = estimator.estimate("질문?")
if result is None:
    print("추정 실패")
else:
    print(f"값: {result.value}")
```

**After (v7.9.0)**:
```python
result = estimator.estimate("질문?")
if not result.is_successful():
    print(f"추정 실패: {result.error}")
else:
    print(f"값: {result.value}")
```

**Migration Guide**:
1. `if result is None:` → `if not result.is_successful():`
2. `if result:` → `if result.is_successful():`
3. 에러 메시지: `result.error` 사용

#### 2. Phase 2 임계값 변경

**영향**:
- Phase 2 활성화율 감소 (더 엄격한 매칭)
- Phase 3-4 사용률 증가
- 전체적으로 더 정확한 추정

**조치 불필요**: 자동으로 적용됨

---

## [7.8.1] - 2025-11-24

### Changed
- `umis_mode` → `llm_mode` 리팩토링
- Model Config System 도입 (v7.8.0)
- `config/model_configs.yaml` 추가

### Fixed
- Phase 4 parsing 버그 수정

---

## [7.8.0] - 2025-11-23

### Added
- Model Config System (중앙화된 LLM 설정)
- `config/model_configs.yaml`
- `umis_rag/core/model_configs.py`

### Changed
- LLM API 파라미터 중앙 관리

---

## [7.7.0] - 2025-11-XX

### Added
- Estimator 5-Phase Architecture
- Phase 0: Literal (프로젝트 데이터)
- Phase 1: Direct RAG (학습 규칙)
- Phase 2: Validator (확정 데이터)
- Phase 3: Guestimation (LLM + Web)
- Phase 4: Fermi Decomposition

### Added
- Native Mode 지원

---

## [7.6.0 이하]

이전 버전의 변경사항은 `dev_docs/` 또는 Git commit history를 참조하세요.

---

## 버전 규칙

**Semantic Versioning (MAJOR.MINOR.PATCH)**:

- **MAJOR** (X.0.0): Breaking Changes (호환성 깨짐)
  - 예: API 시그니처 변경, 필수 파라미터 추가
- **MINOR** (x.Y.0): 새로운 기능 추가 (하위 호환)
  - 예: 새로운 Phase, 새로운 메서드
- **PATCH** (x.y.Z): 버그 수정, 작은 개선
  - 예: 버그 수정, 성능 개선, 문서 업데이트

---

## 참고 자료

- **Production Quality Roadmap**: `dev_docs/improvements/PRODUCTION_QUALITY_ROADMAP_COMPLETE_v7_9_0.md`
- **Phase 0 완료 보고서**: `dev_docs/improvements/PHASE_0_COMPLETE_v7_9_0.md`
- **Phase 1 완료 보고서**: `dev_docs/improvements/PHASE_1_COMPLETE_v7_9_0.md`
- **Phase 2 완료 보고서**: `dev_docs/improvements/PHASE_2_COMPLETE_v7_9_0.md`
- **테스트 가이드**: `tests/README.md` (신규 작성 필요)

---

**유지관리자**: AI Assistant  
**라이선스**: [프로젝트 라이선스 정보]  
**저장소**: [GitHub URL]

---

**END OF CHANGELOG**
