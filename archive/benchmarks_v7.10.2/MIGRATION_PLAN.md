# UMIS 벤치마크 시스템 마이그레이션 계획

**Version:** v1.0  
**Date:** 2025-11-23  
**Status:** Phase 1 완료, Phase 2-4 계획 수립

---

## 📋 목차

1. [시스템 개요](#1-시스템-개요)
2. [Phase 1: Phase 4 마이그레이션 (완료)](#2-phase-1-phase-4-마이그레이션-완료)
3. [Phase 2: Phase 0-3 추가 (계획)](#3-phase-2-phase-0-3-추가-계획)
4. [Phase 3: 다른 Agent 확장 (계획)](#4-phase-3-다른-agent-확장-계획)
5. [Phase 4: Workflow 통합 (계획)](#5-phase-4-workflow-통합-계획)
6. [전체 폴더 구조](#6-전체-폴더-구조)

---

## 1. 시스템 개요

### 1.1 목적

UMIS의 모든 Agent와 Workflow에 대한 **체계적인 벤치마크 시스템** 구축:
- Agent별 독립 벤치마크
- Phase별 세분화 (Estimator)
- Workflow 통합 테스트
- 결과 추적 및 분석

### 1.2 핵심 원칙

**계층적 구조:**
```
benchmarks/
├── common/              # 공통 모듈 (모든 벤치마크 재사용)
├── {agent}/             # Agent별 독립 벤치마크
│   ├── phase{n}/        # Phase별 세분화 (Estimator만)
│   │   ├── tests/       # 테스트 스크립트
│   │   ├── results/     # 결과 JSON
│   │   ├── logs/        # 실행 로그
│   │   └── analysis/    # 분석 리포트
│   └── common.py        # Agent 특화 유틸리티
├── workflows/           # Workflow 통합 테스트
└── reports/             # 전체 벤치마크 리포트
```

**주요 특징:**
1. **모듈화**: 중복 코드 최소화, 재사용성 극대화
2. **확장성**: 새로운 Agent/Phase/Workflow 추가 용이
3. **추적성**: 결과, 로그, 분석 체계적 관리
4. **문서화**: 각 폴더에 README.md, 아키텍처 문서 통합

---

## 2. Phase 1: Phase 4 마이그레이션 (완료)

### 2.1 실행 내역

**완료 날짜:** 2025-11-23

**이동된 파일:**

```bash
# 공통 모듈
scripts/phase4_common.py 
  → benchmarks/estimator/phase4/common.py

# 테스트 스크립트 (6개)
scripts/test_phase4_batch1.py 
  → benchmarks/estimator/phase4/tests/batch1.py
scripts/test_phase4_batch2.py 
  → benchmarks/estimator/phase4/tests/batch2.py
scripts/test_phase4_batch3.py 
  → benchmarks/estimator/phase4/tests/batch3.py
scripts/test_phase4_batch4.py 
  → benchmarks/estimator/phase4/tests/batch4.py
scripts/test_phase4_batch5.py 
  → benchmarks/estimator/phase4/tests/batch5.py
scripts/test_phase4_extended_10problems.py 
  → benchmarks/estimator/phase4/tests/extended_10problems.py

# 결과 파일 (8개)
phase4_batch*_complete_*.json 
  → benchmarks/estimator/phase4/results/

# 로그 파일 (6개)
batch*_output.log 
  → benchmarks/estimator/phase4/logs/

# 문서 파일 (3개)
dev_docs/llm_strategy/PHASE4_ARCHITECTURE.md 
  → benchmarks/estimator/phase4/README.md
dev_docs/llm_strategy/PHASE4_MODEL_RECOMMENDATIONS.md 
  → benchmarks/estimator/phase4/analysis/model_recommendations.md
dev_docs/llm_strategy/EVALUATION_REBALANCING_PROPOSAL.md 
  → benchmarks/estimator/phase4/analysis/evaluation_rebalancing.md
```

**코드 수정:**
- 모든 테스트 파일의 import 경로 수정:
  ```python
  # 변경 전
  from phase4_common import (...)
  
  # 변경 후
  import os
  import sys
  project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))
  sys.path.insert(0, project_root)
  from benchmarks.estimator.phase4.common import (...)
  ```

**생성된 파일:**
- `benchmarks/__init__.py`
- `benchmarks/common/__init__.py`
- `benchmarks/estimator/__init__.py`
- `benchmarks/estimator/phase4/__init__.py`
- `benchmarks/estimator/phase4/tests/__init__.py`
- `benchmarks/estimator/phase4/scenarios.py`

### 2.2 현재 구조

```
benchmarks/
├── __init__.py
├── common/
│   └── __init__.py
└── estimator/
    ├── __init__.py
    └── phase4/                           # Phase 4 Fermi Decomposition
        ├── __init__.py
        ├── README.md                     # PHASE4_ARCHITECTURE.md
        ├── common.py                     # 공통 모듈 (v7.8.0)
        ├── scenarios.py                  # 시나리오 정의
        │
        ├── tests/                        # 테스트 스크립트
        │   ├── __init__.py
        │   ├── batch1.py                 # o3-mini, o4-mini, o3
        │   ├── batch2.py                 # o1-mini, o1, o1-2024-12-17
        │   ├── batch3.py                 # o1-pro, gpt-5-pro (Fast Mode)
        │   ├── batch4.py                 # gpt-5.1 (reasoning_effort=medium)
        │   ├── batch5.py                 # gpt-5.1 (reasoning_effort=low)
        │   └── extended_10problems.py    # 확장 10문제
        │
        ├── results/                      # 결과 JSON (8개)
        │   ├── batch1_complete_20251123_*.json
        │   ├── batch2_complete_20251123_*.json
        │   ├── batch3_complete_20251123_*.json
        │   ├── batch4_medium_complete_20251123_*.json
        │   └── batch5_low_complete_20251123_*.json
        │
        ├── logs/                         # 로그 파일 (6개)
        │   ├── batch1_output.log
        │   ├── batch2_output.log
        │   ├── batch3_output.log
        │   ├── batch4_output.log
        │   └── batch5_output.log
        │
        └── analysis/                     # 분석 리포트
            ├── model_recommendations.md  # 모델 추천
            └── evaluation_rebalancing.md # v7.8.0 평가 재조정
```

### 2.3 테스트 방법

```bash
# Phase 4 벤치마크 실행
cd /Users/kangmin/umis_main_1103/umis

# Batch 1 실행
python benchmarks/estimator/phase4/tests/batch1.py

# Batch 2 실행
python benchmarks/estimator/phase4/tests/batch2.py

# 전체 실행 (순차)
for batch in batch{1..5}.py extended_10problems.py; do
    python benchmarks/estimator/phase4/tests/$batch
done
```

---

## 3. Phase 2: Phase 0-3 추가 (계획)

### 3.1 목표

Estimator의 나머지 Phase(0-3) 벤치마크 추가:
- Phase 0: Literal (프로젝트 데이터)
- Phase 1: Direct RAG (학습된 규칙)
- Phase 2: Validator Search (확정 데이터)
- Phase 3: Guestimation (11개 Source)

### 3.2 폴더 구조

```
benchmarks/estimator/
├── phase0/                               # Phase 0: Literal
│   ├── README.md
│   ├── common.py
│   ├── scenarios.py
│   ├── tests/
│   │   ├── test_literal_extraction.py
│   │   └── test_project_data_priority.py
│   ├── results/
│   └── logs/
│
├── phase1/                               # Phase 1: Direct RAG
│   ├── README.md
│   ├── common.py
│   ├── scenarios.py
│   ├── tests/
│   │   ├── test_learned_rules.py
│   │   ├── test_similarity_threshold.py  # 0.95+ 테스트
│   │   └── test_learning_evolution.py    # 0 → 2,000개 진화
│   ├── results/
│   └── logs/
│
├── phase2/                               # Phase 2: Validator Search
│   ├── README.md
│   ├── common.py
│   ├── scenarios.py
│   ├── tests/
│   │   ├── test_validator_rag.py         # 85% 처리 검증
│   │   ├── test_unit_conversion.py       # 갑/년 → 갑/일
│   │   ├── test_relevance_check.py       # GDP 오류 방지
│   │   └── test_boundary_validation.py   # 개념 기반 검증
│   ├── results/
│   └── logs/
│
└── phase3/                               # Phase 3: Guestimation
    ├── README.md
    ├── common.py
    ├── scenarios.py
    ├── tests/
    │   ├── test_guestimation_full.py     # 전체 프로세스
    │   ├── test_11_sources.py            # Source 수집
    │   │   ├── test_physical_sources.py  # 절대 한계 (3개)
    │   │   ├── test_soft_sources.py      # 범위 제시 (3개)
    │   │   └── test_value_sources.py     # 값 결정 (5개)
    │   ├── test_judgment_engine.py       # 4가지 전략
    │   └── test_learning_system.py       # Phase 1 편입
    ├── results/
    └── logs/
```

### 3.3 구현 계획

**Step 1: Phase 0 (1일)**
- [ ] 프로젝트 메타데이터 기반 시나리오 작성
- [ ] Literal 추출 테스트 구현
- [ ] confidence = 1.0 검증

**Step 2: Phase 1 (2일)**
- [ ] 학습된 규칙 RAG 테스트
- [ ] 유사도 임계값(0.95) 검증
- [ ] 학습 시스템 진화 추적 (0 → 2,000개)

**Step 3: Phase 2 (3일)**
- [ ] Validator RAG 검색 테스트 (85% 처리 검증)
- [ ] 단위 자동 변환 테스트
- [ ] Relevance 검증 테스트
- [ ] Boundary Validation 테스트

**Step 4: Phase 3 (5일)**
- [ ] 11개 Source 수집 테스트
  - Physical Sources (3개)
  - Soft Sources (3개)
  - Value Sources (5개)
- [ ] Judgment Engine 4가지 전략 테스트
- [ ] 학습 시스템 테스트 (Phase 1 편입)

**Step 5: 통합 테스트 (2일)**
- [ ] Phase 0 → 1 → 2 → 3 → 4 자동 라우팅 테스트
- [ ] 재귀 호출 테스트 (max depth 4)
- [ ] Context 전달 테스트

### 3.4 평가 기준

각 Phase별 평가 지표:

**Phase 0:**
- 추출 정확도: 100%
- 응답 속도: <0.1초
- 커버리지: 10%

**Phase 1:**
- 매칭 정확도: 95%+
- 응답 속도: <0.5초
- 커버리지: 5% (초기) → 40% (진화)

**Phase 2:**
- 검색 정확도: 100% (확정 데이터)
- 처리 비율: 85%
- 응답 속도: <1초

**Phase 3:**
- 추정 정확도: 80%+
- Source 수집률: 11개 중 7개 이상
- 응답 속도: 3-8초
- 학습 비율: confidence >= 0.80

---

## 4. Phase 3: 다른 Agent 확장 (계획)

### 4.1 목표

6개 Agent 전체에 대한 벤치마크 시스템 구축:
- Observer (Albert): 시장 구조 분석
- Explorer (Steve): 기회 발굴
- Quantifier (Bill): 계산 및 Excel
- Validator (Rachel): 데이터 검증
- Guardian (Stewart): 프로세스 관리
- Estimator (Fermi): 값 추정 (Phase 1 완료)

### 4.2 폴더 구조

```
benchmarks/
├── observer/                             # Observer Agent
│   ├── README.md
│   ├── common.py
│   ├── scenarios.py
│   ├── tests/
│   │   ├── test_market_structure.py
│   │   ├── test_value_chain.py
│   │   ├── test_inefficiency_detection.py
│   │   └── test_disruption_opportunity.py
│   ├── results/
│   └── logs/
│
├── explorer/                             # Explorer Agent
│   ├── README.md
│   ├── common.py
│   ├── scenarios.py
│   ├── tests/
│   │   ├── test_pattern_matching.py      # RAG 패턴 검색 (54개)
│   │   ├── test_hypothesis_generation.py
│   │   ├── test_7_step_process.py
│   │   ├── test_validation_protocol.py
│   │   └── test_31_business_models.py    # 31개 패턴
│   ├── results/
│   └── logs/
│
├── quantifier/                           # Quantifier Agent
│   ├── README.md
│   ├── common.py
│   ├── scenarios.py
│   ├── tests/
│   │   ├── test_sam_calculation.py       # 31개 방법론
│   │   ├── test_unit_economics.py
│   │   ├── test_financial_projection.py
│   │   ├── test_excel_generation/
│   │   │   ├── test_market_sizing.py     # 10 sheets
│   │   │   ├── test_unit_economics.py    # 10 sheets
│   │   │   └── test_financial_projection.py  # 11 sheets
│   │   └── test_estimator_collaboration.py   # Estimator 협업
│   ├── results/
│   └── logs/
│
├── validator/                            # Validator Agent
│   ├── README.md
│   ├── common.py
│   ├── scenarios.py
│   ├── tests/
│   │   ├── test_data_definition.py
│   │   ├── test_dart_api.py              # DART API 통합
│   │   │   ├── test_financial_data.py    # 재무 데이터
│   │   │   ├── test_disclosure_data.py   # 공시 데이터
│   │   │   └── test_sga_parser.py        # SG&A Parser
│   │   ├── test_creative_sourcing.py
│   │   ├── test_priority_search.py       # 85% 처리
│   │   └── test_gap_analysis.py
│   ├── results/
│   └── logs/
│
└── guardian/                             # Guardian Agent
    ├── README.md
    ├── common.py
    ├── scenarios.py
    ├── tests/
    │   ├── test_meta_rag/
    │   │   ├── test_query_memory.py      # 순환 감지
    │   │   ├── test_goal_memory.py       # 목표 정렬
    │   │   └── test_rae_memory.py        # 평가 재사용
    │   ├── test_quality_evaluation.py
    │   └── test_progress_monitoring.py
    ├── results/
    └── logs/
```

### 4.3 구현 우선순위

**Priority 1 (1-2주):**
1. **Explorer** (가장 중요, RAG 핵심)
   - 54개 패턴 검색 정확도
   - 31개 비즈니스 모델 매칭
   - 7단계 프로세스 완성도

2. **Quantifier** (Excel 엔진 검증)
   - 31개 계산 방법론 정확도
   - Excel 자동 생성 (3개 도구)
   - Estimator 협업 테스트

**Priority 2 (2-3주):**
3. **Validator** (데이터 품질 핵심)
   - DART API 통합 검증
   - 우선 검색 85% 달성
   - Creative Sourcing 효율성

4. **Observer** (분석 품질)
   - 시장 구조 분석 정확도
   - 비효율성 감지 능력
   - 가치사슬 완성도

**Priority 3 (3-4주):**
5. **Guardian** (프로세스 안정성)
   - Meta-RAG 정확도
   - 순환 감지 효율
   - 품질 평가 일관성

### 4.4 평가 기준

Agent별 핵심 지표:

**Observer:**
- 시장 구조 분석 완성도: 80%+
- 비효율성 감지율: 70%+
- SRC_ID 참조 비율: 100%

**Explorer:**
- 패턴 매칭 정확도: 85%+
- 가설 생성 품질: 80%+
- 7단계 완성도: 90%+

**Quantifier:**
- 계산 정확도: 95%+
- Excel 생성 성공률: 100%
- Convergence 달성률: ±30%

**Validator:**
- 검색 정확도: 100% (확정 데이터)
- DART API 성공률: 95%+
- 우선 검색 처리율: 85%+

**Guardian:**
- 순환 감지 정확도: 100%
- 품질 평가 일관성: 90%+
- Meta-RAG 효율: 80%+

---

## 5. Phase 4: Workflow 통합 (계획)

### 5.1 목표

UMIS의 4가지 핵심 Workflow에 대한 E2E 테스트:
1. Discovery Sprint (목표 불명확 시)
2. Comprehensive Study (상세 분석)
3. Rapid Assessment (빠른 파악)
4. Opportunity Discovery (기회 발굴)

### 5.2 폴더 구조

```
benchmarks/workflows/
├── README.md
│
├── discovery_sprint/                     # Discovery Sprint
│   ├── README.md
│   ├── scenarios.py
│   ├── tests/
│   │   ├── test_6_agent_parallel.py      # 6-Agent 병렬 탐색
│   │   ├── test_estimator_collaboration.py  # Estimator 협업
│   │   ├── test_goal_clarification.py    # 목표 구체화
│   │   └── test_full_workflow.py         # 전체 워크플로우
│   ├── results/
│   └── logs/
│
├── comprehensive_study/                  # 상세 분석
│   ├── README.md
│   ├── scenarios.py
│   ├── tests/
│   │   ├── test_observer_explorer_flow.py
│   │   ├── test_quantifier_validator_flow.py
│   │   ├── test_guardian_approval.py
│   │   └── test_full_workflow.py
│   ├── results/
│   └── logs/
│
├── rapid_assessment/                     # 빠른 파악
│   ├── README.md
│   ├── scenarios.py
│   ├── tests/
│   │   ├── test_quick_observer.py
│   │   ├── test_quick_explorer.py
│   │   ├── test_guestimation_priority.py
│   │   └── test_full_workflow.py
│   ├── results/
│   └── logs/
│
└── opportunity_discovery/                # 기회 발굴
    ├── README.md
    ├── scenarios.py
    ├── tests/
    │   ├── test_explorer_7_step.py
    │   ├── test_pattern_validation.py
    │   └── test_full_workflow.py
    ├── results/
    └── logs/
```

### 5.3 Workflow별 테스트 케이스

**Discovery Sprint:**
```yaml
scenario_1:
  name: "피아노 구독 서비스 시장"
  clarity_score: 3/10
  expected_agents: 6 (병렬)
  expected_duration: "1-3일"
  success_criteria:
    - 목표 명확화: 7/10 이상
    - 6-Agent 모두 실행
    - Estimator 3회 이상 협업

scenario_2:
  name: "음악 스트리밍 시장"
  clarity_score: 5/10
  expected_agents: 5 (Observer, Explorer, Quantifier, Validator, Estimator)
  expected_duration: "2-4일"
```

**Comprehensive Study:**
```yaml
scenario_1:
  name: "B2B SaaS 시장 상세 분석"
  clarity_score: 8/10
  expected_agents: 5 (순차)
  expected_duration: "2-4주"
  deliverables:
    - market_reality_report.md (Observer)
    - OPP_*.md (Explorer)
    - market_sizing.xlsx (Quantifier)
    - source_registry.yaml (Validator)
  
scenario_2:
  name: "교육 시장 분석"
  clarity_score: 9/10
  expected_agents: 4 (Observer, Explorer, Quantifier, Validator)
```

**Rapid Assessment:**
```yaml
scenario_1:
  name: "배달 시장 빠른 파악"
  expected_duration: "1-3일"
  expected_agents: 3 (Observer, Explorer, Estimator)
  focus: Order of Magnitude

scenario_2:
  name: "커피 시장 크기"
  expected_duration: "1일"
  expected_agents: 2 (Observer, Estimator)
```

**Opportunity Discovery:**
```yaml
scenario_1:
  name: "구독 모델 기회 발굴"
  expected_duration: "3-5일"
  expected_agents: 3 (Explorer, Validator, Estimator)
  focus: 7-Step Process

scenario_2:
  name: "플랫폼 비즈니스 기회"
  expected_duration: "4-6일"
  focus: Pattern Matching + Validation
```

### 5.4 평가 기준

Workflow별 성공 지표:

**Discovery Sprint:**
- 목표 명확화: 3/10 → 7/10 이상
- Agent 협업: 6개 모두 실행
- Estimator 협업: 3회 이상
- 소요 시간: 계획 대비 ±20%

**Comprehensive Study:**
- 산출물 완성도: 90%+ (4개 산출물)
- 상호 검증: 2-3명
- SRC_ID 참조: 100%
- 소요 시간: 2-4주

**Rapid Assessment:**
- Order of Magnitude: 정확도 80%+
- 소요 시간: 1-3일
- Agent 효율: 최소 인원 활용

**Opportunity Discovery:**
- 7-Step 완성도: 90%+
- 패턴 매칭: 85%+
- 가설 검증: 3명 검증 완료

### 5.5 구현 계획

**Week 1-2: Discovery Sprint**
- [ ] 6-Agent 병렬 실행 로직
- [ ] Estimator 협업 추적
- [ ] 목표 명확화 측정

**Week 3-4: Comprehensive Study**
- [ ] 순차 실행 로직
- [ ] 산출물 완성도 측정
- [ ] 상호 검증 추적

**Week 5-6: Rapid Assessment**
- [ ] Quick Mode 구현
- [ ] Order of Magnitude 평가
- [ ] 효율성 측정

**Week 7-8: Opportunity Discovery**
- [ ] 7-Step Process 추적
- [ ] 패턴 매칭 평가
- [ ] 가설 검증 완성도

---

## 6. 전체 폴더 구조

### 6.1 최종 구조 (Phase 1-4 완료 후)

```
umis/
├── benchmarks/                           # 🆕 통합 벤치마크 시스템
│   ├── README.md                         # 시스템 개요
│   ├── MIGRATION_PLAN.md                 # 본 문서
│   │
│   ├── common/                           # 공통 모듈
│   │   ├── __init__.py
│   │   ├── base_evaluator.py
│   │   ├── api_configs.py
│   │   ├── prompt_templates.py
│   │   ├── scoring_systems.py
│   │   └── result_analyzer.py
│   │
│   ├── estimator/                        # Estimator Agent (완료)
│   │   ├── __init__.py
│   │   ├── README.md
│   │   ├── common.py
│   │   │
│   │   ├── phase0/                       # Phase 0: Literal
│   │   ├── phase1/                       # Phase 1: Direct RAG
│   │   ├── phase2/                       # Phase 2: Validator Search
│   │   ├── phase3/                       # Phase 3: Guestimation
│   │   ├── phase4/                       # Phase 4: Fermi (완료)
│   │   │   ├── README.md
│   │   │   ├── common.py
│   │   │   ├── scenarios.py
│   │   │   ├── tests/
│   │   │   ├── results/
│   │   │   ├── logs/
│   │   │   └── analysis/
│   │   │
│   │   └── integration/                  # 통합 테스트
│   │
│   ├── observer/                         # Observer Agent
│   ├── explorer/                         # Explorer Agent
│   ├── quantifier/                       # Quantifier Agent
│   ├── validator/                        # Validator Agent
│   ├── guardian/                         # Guardian Agent
│   │
│   ├── workflows/                        # Workflow 통합
│   │   ├── discovery_sprint/
│   │   ├── comprehensive_study/
│   │   ├── rapid_assessment/
│   │   └── opportunity_discovery/
│   │
│   ├── rag/                              # RAG 시스템
│   │   ├── layer1_canonical/
│   │   ├── layer2_projected/
│   │   ├── layer3_graph/
│   │   └── layer4_memory/
│   │
│   ├── integration/                      # E2E 통합
│   │   ├── test_full_workflow.py
│   │   ├── test_agent_collaboration.py
│   │   └── scenarios/
│   │
│   ├── reports/                          # 벤치마크 리포트
│   │   ├── OVERALL_BENCHMARK.md
│   │   ├── agent_comparison.md
│   │   └── model_recommendations/
│   │
│   └── tools/                            # 벤치마크 도구
│       ├── run_all_benchmarks.py
│       ├── generate_report.py
│       ├── compare_versions.py
│       └── visualize_results.py
│
├── scripts/                              # 기존 스크립트
│   ├── [Agent별 스크립트 유지]
│   └── [설정 스크립트 유지]
│
├── umis_rag/                             # 실제 시스템 코드
│   ├── agents/
│   ├── core/
│   ├── deliverables/
│   └── ...
│
└── dev_docs/                             # 개발 문서
    ├── architecture/
    └── ...
```

### 6.2 디렉토리 규칙

**각 Agent/Phase/Workflow 폴더:**
- `README.md`: 아키텍처 및 사용 가이드
- `common.py`: Agent/Phase 특화 유틸리티
- `scenarios.py`: 테스트 시나리오 정의
- `tests/`: 테스트 스크립트
- `results/`: 결과 JSON 파일
- `logs/`: 실행 로그
- `analysis/`: 분석 및 리포트 (선택적)

**공통 모듈:**
- `benchmarks/common/`: 모든 벤치마크에서 재사용
- 중복 코드 최소화
- 버전 관리 및 호환성 유지

**문서화:**
- 각 폴더에 README.md 필수
- 아키텍처 문서 통합
- 사용 예시 및 가이드 포함

---

## 7. 타임라인

### Phase 1 (완료)
- ✅ 2025-11-23: Phase 4 마이그레이션 완료

### Phase 2 (계획)
- Week 1-2 (2025-11-24 ~ 2025-12-07): Phase 0-3 추가
  - Phase 0: 1일
  - Phase 1: 2일
  - Phase 2: 3일
  - Phase 3: 5일
  - 통합 테스트: 2일

### Phase 3 (계획)
- Week 3-6 (2025-12-08 ~ 2026-01-04): Agent 확장
  - Explorer + Quantifier: 2주
  - Validator + Observer: 2주
  - Guardian: 1주
  - 통합 테스트: 1주

### Phase 4 (계획)
- Week 7-14 (2026-01-05 ~ 2026-03-01): Workflow 통합
  - Discovery Sprint: 2주
  - Comprehensive Study: 2주
  - Rapid Assessment: 2주
  - Opportunity Discovery: 2주

### 유지보수 (지속)
- 월간 벤치마크 실행
- 분기별 리포트 생성
- 버전별 비교 분석

---

## 8. 참고 자료

### 관련 문서
- `benchmarks/estimator/phase4/README.md` - Phase 4 아키텍처
- `benchmarks/estimator/phase4/analysis/model_recommendations.md` - 모델 추천
- `docs/architecture/UMIS_ARCHITECTURE_BLUEPRINT.md` - UMIS 전체 구조

### 실행 가이드
- Phase 4 테스트: `benchmarks/estimator/phase4/README.md` 참조
- 벤치마크 도구: `benchmarks/tools/` 참조

---

**문서 작성:** AI Assistant  
**마지막 업데이트:** 2025-11-23  
**버전:** v1.0

