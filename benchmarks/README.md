# UMIS 벤치마크 시스템

**Version:** v1.0  
**Date:** 2025-11-23  
**Status:** Phase 1 완료 (Phase 4), Phase 2-4 계획 수립

---

## 🎯 개요

UMIS 시스템의 모든 Agent와 Workflow에 대한 **체계적인 벤치마크 및 평가 시스템**입니다.

### 목적

1. **Agent별 성능 평가**: 6개 Agent의 독립적 벤치마크
2. **Phase별 정밀 평가**: Estimator의 Phase 0-4 세분화
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
├── README.md                    # 본 문서
├── MIGRATION_PLAN.md            # 마이그레이션 계획 (Phase 1-4)
│
├── common/                      # 공통 모듈
│   ├── base_evaluator.py        # 기본 평가 클래스
│   ├── api_configs.py           # 모델 API 설정
│   ├── prompt_templates.py      # 프롬프트 템플릿
│   ├── scoring_systems.py       # 점수 계산
│   └── result_analyzer.py       # 결과 분석
│
├── estimator/                   # Estimator Agent ⭐ Phase 1 완료
│   ├── phase0/                  # Phase 0: Literal
│   ├── phase1/                  # Phase 1: Direct RAG
│   ├── phase2/                  # Phase 2: Validator Search
│   ├── phase3/                  # Phase 3: Guestimation
│   ├── phase4/                  # Phase 4: Fermi (✅ 완료)
│   └── integration/             # 통합 테스트
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
├── rag/                         # RAG 시스템 (계획)
│   ├── layer1_canonical/
│   ├── layer2_projected/
│   ├── layer3_graph/
│   └── layer4_memory/
│
├── integration/                 # E2E 통합 (계획)
├── reports/                     # 벤치마크 리포트
└── tools/                       # 벤치마크 도구
```

---

## 🚀 빠른 시작

### Phase 4 벤치마크 실행 (현재 사용 가능)

```bash
cd /Users/kangmin/umis_main_1103/umis

# Batch 1: o3-mini, o4-mini, o3
python benchmarks/estimator/phase4/tests/batch1.py

# Batch 2: o1-mini, o1, o1-2024-12-17
python benchmarks/estimator/phase4/tests/batch2.py

# Batch 3: o1-pro, gpt-5-pro (Fast Mode)
python benchmarks/estimator/phase4/tests/batch3.py

# Batch 4: gpt-5.1 (reasoning_effort=medium)
python benchmarks/estimator/phase4/tests/batch4.py

# Batch 5: gpt-5.1 (reasoning_effort=low)
python benchmarks/estimator/phase4/tests/batch5.py

# 확장 10문제
python benchmarks/estimator/phase4/tests/extended_10problems.py
```

### 결과 확인

```bash
# 결과 파일 (JSON)
ls benchmarks/estimator/phase4/results/

# 로그 파일
ls benchmarks/estimator/phase4/logs/

# 분석 리포트
cat benchmarks/estimator/phase4/analysis/model_recommendations.md
```

---

## 📊 현재 상태

### Phase 1: 완료 ✅

**Estimator Phase 4 (Fermi Decomposition)**
- 테스트 스크립트: 6개 (batch1-5, extended_10problems)
- 결과 파일: 8개 JSON
- 로그 파일: 6개
- 분석 리포트: 2개 (model_recommendations, evaluation_rebalancing)

**평가 시스템 (v7.8.0):**
- 총점: 110점
  - 정확도: 25점
  - 내용 점수: 45점 (계산 완성도, 논리 연결, 수치 정확성)
  - 형식 점수: 5점 (JSON 스키마 준수)
  - 분해 품질: 10점
  - 개념적 일관성: 15점
  - 논리: 10점

**지원 모델: 15개**
- o-series: 9개 (o1-mini, o1, o1-pro, o3, o3-mini, o4-mini 등)
- gpt-5 series: 2개 (gpt-5.1, gpt-5-pro)
- gpt-4.1 series: 2개 (gpt-4.1, gpt-4.1-mini)

### Phase 2-4: 계획 수립 완료 📋

자세한 내용은 `MIGRATION_PLAN.md` 참조

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

## 📈 마이그레이션 계획

### Phase 1: Phase 4 마이그레이션 ✅ 완료
- 날짜: 2025-11-23
- 내용: Estimator Phase 4 벤치마크 시스템 구축

### Phase 2: Phase 0-3 추가 📋 계획
- 예정: 2025-11-24 ~ 2025-12-07 (2주)
- 내용: Estimator의 나머지 Phase 벤치마크

### Phase 3: Agent 확장 📋 계획
- 예정: 2025-12-08 ~ 2026-01-04 (4주)
- 내용: 6개 Agent 전체 벤치마크

### Phase 4: Workflow 통합 📋 계획
- 예정: 2026-01-05 ~ 2026-03-01 (8주)
- 내용: 4가지 핵심 Workflow E2E 테스트

상세 계획: `MIGRATION_PLAN.md` 참조

---

## 📚 문서

### 핵심 문서
- `MIGRATION_PLAN.md`: 전체 마이그레이션 계획 (Phase 1-4)
- `estimator/phase4/README.md`: Phase 4 아키텍처
- `estimator/phase4/analysis/model_recommendations.md`: 모델 추천
- `estimator/phase4/analysis/evaluation_rebalancing.md`: v7.8.0 평가 재조정

### UMIS 문서
- `/docs/architecture/UMIS_ARCHITECTURE_BLUEPRINT.md`: UMIS 전체 구조
- `/docs/INSTALL.md`: 설치 가이드

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

**문서 작성:** AI Assistant  
**마지막 업데이트:** 2025-11-23  
**버전:** v1.0

