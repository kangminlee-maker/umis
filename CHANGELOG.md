# Changelog

모든 주목할 만한 변경사항이 이 파일에 문서화됩니다.

형식은 [Keep a Changelog](https://keepachangelog.com/ko/1.0.0/)를 따르며,
이 프로젝트는 [Semantic Versioning](https://semver.org/lang/ko/)을 준수합니다.

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
