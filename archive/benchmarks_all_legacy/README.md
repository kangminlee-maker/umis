# UMIS 벤치마크 시스템

**Version:** v2.0  
**Date:** 2025-11-26  
**Status:** v7.11.0 Stage Architecture 기반

---

## 🎯 개요

UMIS 시스템의 모든 Agent와 Workflow에 대한 **체계적인 벤치마크 및 평가 시스템**입니다.

### 목적

1. **Agent별 성능 평가**: 6개 Agent의 독립적 벤치마크
2. **Stage별 정밀 평가**: Estimator의 4-Stage Fusion Architecture 검증
3. **Workflow 통합 테스트**: 4가지 핵심 Workflow E2E 검증
4. **지속적 개선**: 버전별 성능 추적 및 비교

### 핵심 특징

- ✅ **모듈화**: 중복 코드 최소화, 재사용성 극대화
- ✅ **확장성**: 새로운 Agent/Phase/Workflow 추가 용이
- ✅ **추적성**: 결과, 로그, 분석 체계적 관리
- ✅ **자동화**: 벤치마크 자동 실행 및 리포트 생성

---

## 📁 폴더 구조

```
benchmarks/
├── README.md                    # 본 문서 (v2.0)
│
├── common/                      # 공통 모듈
│   ├── common.py                # 공통 유틸리티 (deprecated, v7.10.2)
│   └── __init__.py
│
├── estimator/                   # Estimator Agent ⭐ v7.11.0
│   ├── README.md                # Estimator 벤치마크 가이드
│   ├── MODEL_CONFIG_IMPLEMENTATION.md  # 모델 설정 (deprecated, v7.8.0)
│   └── __init__.py
│
├── observer/                    # Observer Agent (계획)
├── explorer/                    # Explorer Agent (계획)
├── quantifier/                  # Quantifier Agent (계획)
├── validator/                   # Validator Agent (계획)
├── guardian/                    # Guardian Agent (계획)
│
├── workflows/                   # Workflow 통합 (계획)
│   ├── discovery_sprint/
│   ├── comprehensive_study/
│   ├── rapid_assessment/
│   └── opportunity_discovery/
│
└── reports/                     # 벤치마크 리포트 (계획)
```

**Note**: v7.11.0에서 Estimator는 4-Stage Fusion Architecture로 재설계되었습니다.
- 테스트 위치: `tests/unit/`, `tests/integration/`, `tests/e2e/`
- Legacy Phase 4 벤치마크: `archive/benchmarks_v7.10.2/`

---

## 🚀 빠른 시작 (v7.11.0)

### Estimator 벤치마크 실행

**Unit Tests** (Stage 기반):
```bash
# Stage 2 (Prior Estimator)
pytest tests/unit/test_prior_estimator.py -v

# Stage 3 (Fermi Estimator)
pytest tests/unit/test_fermi_estimator.py -v
```

**Integration Tests** (Stage Flow):
```bash
# Stage 1→2→3→4 흐름 테스트
pytest tests/integration/test_stage_flow_v7_11_0.py -v
```

**E2E Tests** (10-Problem Fermi):
```bash
# 10개 Fermi 문제 벤치마크
pytest tests/test_v7_11_0_fermi_10problems.py -v
```

**AB Testing** (Budget 비교):
```bash
# Standard vs Fast Budget
pytest tests/ab_testing/test_stage_ab_framework_v7_11_0.py -v
```

### 결과 확인

```bash
# E2E 테스트 결과
cat tests/fermi_10problems_results_v7_11_0.json

# AB Testing 결과
cat tests/ab_testing/stage_ab_results_*.json
```

---

## 📊 현재 상태 (v7.11.0)

### Estimator: 4-Stage Fusion Architecture ✅

**구현 완료**:
- ✅ Stage 1 (Evidence Collection): Literal + Direct RAG
- ✅ Stage 2 (Generative Prior): LLM-based 추정
- ✅ Stage 3 (Structural Explanation): Fermi 분해
- ✅ Stage 4 (Fusion & Validation): 결과 통합

**테스트 현황**:
- Unit Tests: 22개 (19/22 통과, 86%)
- Integration Tests: 5개
- E2E Tests: 10-Problem Fermi Benchmark
- AB Testing: Budget 비교 프레임워크

**성능 지표 (v7.11.0)**:
- Stage 1 (Evidence): <0.5초
- Stage 2 (Prior): ~3초
- Stage 3 (Fermi): 3-5초 (재귀 제거로 3-10배 개선)
- Stage 4 (Fusion): <0.1초
- Pass Rate: 86%

**모델 추천**:
- Stage 2: `gpt-4o-mini`, `gpt-5.1`, `o1-mini`
- Stage 3: `o1-mini`, `o3-mini-2025-01-31`, `o4-mini-2025-04-16`

### 기타 Agent: 계획 단계 📋

- Observer, Explorer, Quantifier, Validator, Guardian
- 향후 v7.12.0 이후 단계적 구현 예정

---

## 📖 사용 가이드

### Phase 4 벤치마크 상세

**구조:**
```
estimator/phase4/
├── README.md                    # Phase 4 아키텍처
├── common.py                    # 공통 모듈 (v7.8.0)
├── scenarios.py                 # 시나리오 정의
├── tests/                       # 테스트 스크립트 (6개)
├── results/                     # 결과 JSON
├── logs/                        # 로그
└── analysis/                    # 분석 리포트
```

**테스트 시나리오:**
- 핵심 3문제: 한국 사업자 수, 서울 인구, 커피 전문점 수
- 확장 10문제: 배달 기사, 치킨 배달, 택시 승객 등

**평가 지표:**
- 정확도: Log10 기반 오차율
- 내용 점수: 실제 추론 능력 평가
- 형식 점수: JSON 스키마 준수도
- 개념적 일관성: 도메인 특화 개념 활용
- 분해 품질: 문제 분해 완성도

**모델 추천:**
- 최우선: o3-mini-2025-01-31, o4-mini-2025-04-16
- 프리미엄: o3-2025-04-16, o1-pro-2025-03-19
- 실험적: gpt-5.1 (높은 추론 능력, 낮은 형식 준수)

상세 내용: `estimator/phase4/README.md` 참조

---

## 🔧 개발 가이드

### 새로운 Agent 벤치마크 추가

1. **폴더 구조 생성:**
```bash
mkdir -p benchmarks/{agent_name}/{tests,results,logs}
```

2. **기본 파일 생성:**
```bash
touch benchmarks/{agent_name}/README.md
touch benchmarks/{agent_name}/common.py
touch benchmarks/{agent_name}/scenarios.py
```

3. **공통 모듈 활용:**
```python
from benchmarks.common import base_evaluator, api_configs
```

4. **테스트 작성:**
- `tests/` 폴더에 테스트 스크립트 작성
- `scenarios.py`에서 시나리오 정의
- `common.py`에 Agent 특화 유틸리티 구현

### 새로운 Phase 추가 (Estimator)

1. **Phase 폴더 생성:**
```bash
mkdir -p benchmarks/estimator/phase{n}/{tests,results,logs}
```

2. **기본 파일:**
- `README.md`: Phase 아키텍처
- `common.py`: Phase 특화 유틸리티
- `scenarios.py`: 시나리오

3. **평가 기준 정의:**
- 정확도, 속도, 커버리지
- Phase 특화 지표

---

## 📈 버전 히스토리

### v2.0 (2025-11-26): v7.11.0 Fusion Architecture ✅
- Estimator: Phase 5 → 4-Stage Fusion 전환
- 재귀 제거, Budget 기반 탐색
- Unit/Integration/E2E/AB Testing 프레임워크 구축
- Legacy Phase 4 벤치마크 → archive 이동

### v1.0 (2025-11-23): Phase 4 벤치마크 ✅
- Estimator Phase 4 (Fermi Decomposition) 벤치마크
- 15개 모델 지원
- 평가 시스템 v7.8.0 (110점 만점)
- → Deprecated: `archive/benchmarks_v7.10.2/`

### 향후 계획 📋

**v2.1 (2025-12-01)**: Agent 확장
- Observer, Explorer, Quantifier 벤치마크 추가

**v2.2 (2026-01-01)**: Workflow 통합
- 4가지 핵심 Workflow E2E 테스트

---

## 📚 문서

### 핵심 문서 (v7.11.0)
- `estimator/README.md`: Estimator 벤치마크 가이드 (v7.11.0)
- `tests/unit/`: Unit Test 코드
- `tests/integration/`: Integration Test 코드
- `tests/e2e/`: E2E Test 코드 (10-Problem Fermi)

### UMIS 문서
- `/docs/architecture/UMIS_ARCHITECTURE_BLUEPRINT.md`: UMIS 전체 구조
- `/docs/MIGRATION_GUIDE_v7_11_0.md`: v7.11.0 마이그레이션 가이드
- `/docs/guides/BUDGET_CONFIGURATION_GUIDE.md`: Budget 설정 가이드

### Legacy 문서 (Archive)
- `archive/benchmarks_v7.10.2/`: Phase 4 벤치마크 (deprecated)
- `archive/benchmarks_v7.10.2/phase4/analysis/model_recommendations.md`
- `archive/benchmarks_v7.10.2/MIGRATION_PLAN.md`

---

## 🤝 기여

### 코드 스타일
- Python: PEP 8
- 문서: Markdown
- import 경로: 상대 경로 최소화, 절대 경로 사용

### 테스트 규칙
- 모든 테스트는 독립 실행 가능
- 결과는 JSON 형식으로 저장
- 로그는 타임스탬프 포함

### 문서화 규칙
- 각 폴더에 README.md 필수
- 코드에 docstring 작성
- 변경 사항은 CHANGELOG 업데이트

---

## 📞 문의

- Issue: UMIS GitHub Repository
- 문서: `MIGRATION_PLAN.md`, `estimator/phase4/README.md`

---

## ⚠️ Legacy (Archive)

**Phase 4 재귀 벤치마크 (v7.10.2)** → **Archive 이동**

- **위치**: `archive/benchmarks_v7.10.2/`
- **이유**: v7.11.0에서 4-Stage Fusion Architecture로 재설계
- **Legacy 내용**: Phase 0-4 벤치마크, 재귀 기반 Fermi 테스트

---

**문서 작성:** AI Assistant  
**마지막 업데이트:** 2025-11-26  
**버전:** v2.0 (v7.11.0 Fusion Architecture)

