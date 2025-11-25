# UMIS Architecture Blueprint
**Universal Market Intelligence System - 시스템 설계도**

---

## 📌 Version Info

| Item | Value |
|------|-------|
| **UMIS Version** | v7.8.1 |
| **Status** | Production Ready |
| **Last Updated** | 2025-11-24 |

**Purpose**: UMIS 전체 구조와 기능을 한눈에 파악할 수 있는 고수준 설계도

**변경 이력**: [CHANGELOG.md](../../CHANGELOG.md) 참조

---

## 🎯 System Overview

### What is UMIS?
시장 분석을 위한 **6-Agent 협업 시스템** + **Multi-Layer RAG 아키텍처** + **Excel 자동 생성**

### Key Characteristics
- ✅ **6-Agent 협업 시스템** 역할 분담 및 상호 검증
- ✅ **Estimator (Fermi) Agent** 5-Phase 재설계 (Phase 0-4)
- ✅ **Validator Priority** 확정 데이터 우선 검색 (85% 처리)
- ✅ **Boundary Intelligence** 개념 기반 동적 검증
- ✅ **Unit Conversion** 단위 자동 변환
- ✅ **Relevance Check** GDP 오류 방지
- ✅ **Web Search** DuckDuckGo/Google 선택
- ✅ **Single Source of Truth** 모든 값 추정은 Estimator만
- ✅ **Reasoning Transparency** 추정 근거 완전 투명화
- ✅ **Learning System** 사용할수록 빠름
- ✅ **Meta-RAG** Guardian 프로세스 자동 감시
- ✅ **System RAG** 31개 도구 Key-based 검색
- ✅ **RAG 기반 지식 활용** 360개 검증된 데이터 (54개 패턴/사례)
- ✅ **Knowledge Graph** 패턴 조합 자동 발견 (13 노드, 45 관계)
- ✅ **Excel 자동 생성** 3개 도구 (9-11 시트)
- ✅ **Native Mode** Cursor LLM 직접 활용, 비용 $0
- ✅ **완전한 추적성** 양방향 ID 시스템 (14개 Prefix)
- ✅ **재검증 가능** Excel 함수 100%, Named Range
- ✅ **자동 환경변수** .env 자동 로드

### Quick Start

**설치**: [INSTALL.md](docs/INSTALL.md) 참조 (AI 자동 / 스크립트 / 수동)

**사용**:
```
Cursor Composer (Cmd+I):
"@Explorer, 시장 분석해줘"
"@Fermi, B2B SaaS Churn Rate는?"
"@Validator, 확정 데이터 있나요?"
```

---

## 🏗️ System Architecture

### 3-Layer Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    LAYER 1: BUSINESS LAYER                          │
│                    (사용자 대면 - 분석 산출물)                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│  │ Observer │  │ Explorer │  │Quantifier│  │Validator │           │
│  │ (Albert) │  │ (Steve)  │  │  (Bill)  │  │ (Rachel) │           │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘           │
│       │             │             │             │                  │
│       └─────────────┴──────┬──────┴─────────────┘                  │
│                            │                                        │
│                   ┌────────▼────────┐                               │
│                   │   Estimator     │                               │
│                   │   (Fermi)       │ ◄── 값 추정 (협업 파트너)     │
│                   └────────┬────────┘                               │
│                            │                                        │
│                       ┌────▼────┐                                   │
│                       │Guardian │                                   │
│                       │(Stewart)│ ◄── 검증 & 메타 관리              │
│                       └─────────┘                                   │
│                                                                     │
│  산출물:                                                            │
│  - market_reality_report.md (Albert)                               │
│  - OPP_*.md (Steve)                                                │
│  - market_sizing.xlsx (Bill)                                       │
│  - source_registry.yaml (Rachel)                                   │
│  - EstimationResult (Fermi)                                        │
│  - .project_meta.yaml, deliverables_registry.yaml (Stewart)       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    LAYER 2: RAG DATA LAYER                          │
│                    (지식 저장 및 검색)                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Layer 1: Vector Indexes                                           │
│  ┌──────────────────┐  90% Rules   ┌──────────────────┐           │
│  │Canonical Index   │──────────────▶│Projected Index   │           │
│  │(CAN-*)           │  10% LLM      │(PRJ-*)           │           │
│  │                  │               │                  │           │
│  │정규화 청크        │               │Agent별 검색용 뷰  │           │
│  │업데이트용         │               │explorer_*        │           │
│  │                  │               │quantifier_*      │           │
│  └──────────────────┘               └──────────────────┘           │
│                                              │                      │
│  Layer 3: Knowledge Graph                    │                      │
│  ┌──────────────────────────────────────────▼─────┐                │
│  │Neo4j Graph Database                            │                │
│  │                                                 │                │
│  │(Pattern)-[COMBINES_WITH]->(Pattern)            │                │
│  │(Pattern)-[COUNTERS]->(Pattern)                 │                │
│  │                                                 │                │
│  │GND-*: Nodes | GED-*: Edges                     │                │
│  │Confidence: similarity × coverage × validation  │                │
│  └─────────────────────────────────────────────────┘                │
│                                                                     │
│  Layer 4: Memory                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │
│  │Query Memory  │  │Goal Memory   │  │RAE Memory    │            │
│  │(순환 감지)    │  │(목표 정렬)    │  │(평가 재사용)  │            │
│  │MEM-*         │  │MEM-*         │  │RAE-*         │            │
│  └──────────────┘  └──────────────┘  └──────────────┘            │
│                                                                     │
│  Knowledge Base:                                                   │
│  - 31개 비즈니스 모델 패턴                                          │
│  - 23개 파괴적 혁신 패턴                                            │
│  - 54개 성공 사례                                                   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    LAYER 3: RAG RUNTIME LAYER                       │
│                    (실행 환경 및 정책)                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Configuration Files:                                              │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐       │
│  │layer_config    │  │routing_policy  │  │runtime_config  │       │
│  │.yaml           │  │.yaml           │  │.yaml           │       │
│  │                │  │                │  │                │       │
│  │Overlay 관리    │  │Workflow 정의   │  │실행 모드       │       │
│  │core/team/      │  │Explorer        │  │hybrid          │       │
│  │personal        │  │Workflow 4단계  │  │Circuit Breaker │       │
│  └────────────────┘  └────────────────┘  └────────────────┘       │
│                                                                     │
│  ┌────────────────┐                                                │
│  │projection_rules│  Canonical → Projected 변환                    │
│  │.yaml           │  - 90% 규칙 기반                               │
│  │                │  - 10% LLM 판단 (학습 → 규칙화)                │
│  └────────────────┘                                                │
│                                                                     │
│  Execution:                                                        │
│  - Mode: yaml_only / hybrid / rag_full                            │
│  - Fail-Safe: Circuit Breaker (3회 실패 → 60초 차단)               │
│  - TTL: 24시간 캐시 (고빈도 → 영속화)                              │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 💡 Core Concepts

### 1. 6-Agent System (Business Layer)

#### Agent 역할 및 산출물

| Agent ID | Name (기본) | Role | 산출물 | 검증자 |
|----------|------------|------|--------|--------|
| **observer** | Albert | 시장 구조 분석 | market_reality_report.md | quantifier, validator, guardian |
| **explorer** | Steve | 기회 발굴 (RAG) | OPP_*.md | observer, quantifier, validator |
| **quantifier** | Bill | 계산 전문 (31개 방법론) + Excel | market_sizing.xlsx (10 sheets)<br>unit_economics.xlsx (10 sheets)<br>financial_projection.xlsx (11 sheets) | validator, observer |
| **validator** | Rachel | 데이터 검증 + DART API v1.0.0 | source_registry.yaml<br>DART 재무/공시 데이터 | - (검증자) |
| **guardian** | Stewart | 프로세스 관리 | .project_meta.yaml, deliverables_registry.yaml | - (메타 관리자) |
| **estimator** | **Fermi** | **값 추정 전문 (5-Phase)** | **EstimationResult** (값 + 근거 + phase) | - (협업 파트너) |

**핵심**: 
- **Agent ID 불변** (observer, explorer, quantifier, validator, guardian, **estimator**) → 폴더/파일 경로
- **Name 변경 가능** (config/agent_names.yaml) → 사용자 UI
- **상호 검증** (각 산출물 2-3명 검증)
- **Estimator 특수성**: 협업 파트너 (모든 Agent가 필요 시 호출, Workflow 독립)
- **MECE 원칙**: Estimator = 추정, Quantifier = 계산 (역할 명확 분리)

#### 데이터 흐름 (순차적 의존성)

```
Rachel (Validator)
  ↓ SRC_YYYYMMDD_NNN
  │ source_registry.yaml
  │ - SRC_20241031_001: "피아노 시장 1,500억"
  │ - 신뢰도 평가 (0-100)
  │ - Definition Gap 분석
  │ - 추정치 검증 필요 시 → Fermi 호출 (교차 검증)
  │
  ├─► Fermi (Estimator) 협업 파트너
  │   │ EstimationResult
  │   │ - 값 추정 (데이터 부족 시)
  │   │ - 교차 검증 (Validator 요청)
  │   │ - reasoning_detail (완전한 근거)
  │   │ - Phase 0-4 자동 선택
  │   │ - 학습 (confidence >= 0.80)
  │   └─ 모든 Agent에서 호출됨
  │
Bill (Quantifier)
  ↓ 계산 수행 (31개 방법론)
  │ market_sizing.xlsx
  │ - Assumptions: SRC_ID 참조
  │ - 필요한 값 (ARPU, Churn 등) → Fermi 호출
  │ - Fermi 추정 결과로 계산 수행 (LTV = ARPU / Churn)
  │ - Estimation_Details: EST-NNN (Fermi 추정 ID)
  │ - 4가지 Method → Convergence (±30%)
  │ - 결과: SAM 270억 ± 30억
  │
Albert (Observer)
  ↓ 시장 구조 분석
  │ market_reality_report.md
  │ - 모든 주장에 SRC_ID 또는 Bill 계산 참조
  │ - 가치사슬 마진 → Fermi 호출
  │ - 가치사슬 맵
  │ - 비효율성 정량화 (Bill + Fermi 협업)
  │
Steve (Explorer)
  ↓ 기회 가설
  │ OPP_*.md
  │ - Albert 분석 참조
  │ - 기회 크기 → Fermi 호출 (Order of Magnitude)
  │ - Bill SAM 참조
  │ - Rachel SRC_ID 참조
  │ - 3명 검증 (Albert, Bill, Rachel)
  │ - 우선순위 자동 계산 (5개 차원)
  │
Stewart (Guardian)
  │ .project_meta.yaml (프로젝트 진행 추적)
  │ deliverables_registry.yaml (산출물 자동 등록)
  │ - 프로젝트 리소스 → Fermi 호출
  │ - Meta-RAG (순환/목표/평가)
  └─ 검증 상태 집계, 품질 평가
```

### 2. 4-Layer RAG Architecture (Data Layer)

#### Layer 구조

```
Layer 1: Canonical Index (CAN-*)
  목적: 정규화 청크 (업데이트용)
  구조: Anchor Path + Content Hash
  예시:
    canonical_chunk_id: "CAN-baemin-001"
    sections:
      - agent_view: explorer
        anchor_path: "platform_model.trigger_observations"
        content_hash: "sha256:ab123456..."
        span_hint: {paragraphs: "12-18", tokens: 250}

         ↓ config/projection_rules.yaml (90% 규칙)
         ↓ LLM 판단 (10%) → data/llm_projection_log.jsonl

Layer 2: Projected Index (PRJ-*)
  목적: Agent별 검색용 Materialized View
  전략: on_demand (TTL 24h) → 고빈도면 persistent
  Agent Views: observer, explorer, quantifier, validator, guardian, estimator
  예시:
    projected_chunk_id: "PRJ-baemin-exp-001"
    agent_view: "explorer"
    canonical_chunk_id: "CAN-baemin-001"
    explorer_pattern_id: "platform_business_model"
    explorer_csf: ["network_effects", "switching_costs"]
    materialization:
      strategy: "on_demand"
      cache_ttl_hours: 24
      access_count: 0

         ↓ 필드 매핑 (explorer_pattern_id → pattern_id)

Layer 3: Knowledge Graph (GND-*, GED-*)
  Database: Neo4j
  Nodes:
    graph_node_id: "GND-platform-001"
    pattern_id: "platform_business_model"
    vector_chunk_id: "PRJ-baemin-exp-001"
  
  Edges:
    graph_edge_id: "GED-plat-sub-001"
    (GND-platform-001)-[COMBINES_WITH]->(GND-subscription-001)
    relationship_type: COMBINES_WITH / COUNTERS / PREREQUISITE / ENABLES
    confidence:
      similarity: {method: "embedding", value: 0.92}
      coverage: {method: "distribution", value: 0.10}
      validation: {method: "checklist", value: true}
      overall: 0.85
      reasoning:
        - "Best case similarity 0.92 (Amazon Prime)"
        - "10% of cases show pattern"
        - "Validator verified"
    evidence_ids: ["CAN-amazon-001", "PRJ-spotify-exp-002"]
    provenance: {source: "human_review", reviewer_id: "stewart"}

Layer 4: Memory (MEM-*, RAE-*, EST-*)
  Query Memory: 순환 감지 (repetition_count)
    - memory_id: "MEM-query-001"
  
  Goal Memory: 목표 정렬 (alignment_score)
    - memory_id: "MEM-goal-001"
  
  RAE Index: Guardian 평가 재사용 (일관성)
    - rae_id: "RAE-eval-001"
    - deliverable_id: "OPP-001"
    - grade: "A"
    - rationale: "구조적 실현성 높음, 근거 충분"
  
  Estimation Results: Estimator 추정 결과
    - estimation_id: "EST-churn-001"
    - value: 0.06, confidence: 0.85
    - reasoning_detail: {...}
    - phase: 0/1/2/3/4  #: tier → phase
```

### 3. ID Namespace System (양방향 추적)

모든 데이터 요소는 고유 ID를 가지며, **양방향 추적 가능**

| Prefix | 의미 | 예시 | Collection/파일 | Agent |
|--------|------|------|----------------|-------|
| **SRC-** | 데이터 출처 | SRC_20241031_001 | source_registry.yaml | Rachel |
| **EST-** | **Estimator 추정 결과** | **EST-churn-001** | **EstimationResult (Memory)** | **Fermi** |
| **ASM-** | 가정 | ASM_001 | market_sizing.xlsx (Assumptions) | Bill |
| **OPP-** | 기회 가설 | OPP_20241031_001 | OPP_*.md | Steve |
| **DEL-** | 산출물 | DEL_20241031_001 | deliverables_registry.yaml | Stewart |
| **CAN-** | Canonical 청크 | CAN-baemin-001 | canonical_index (ChromaDB) | RAG |
| **PRJ-** | Projected 청크 | PRJ-baemin-exp-001 | projected_index (ChromaDB) | RAG |
| **GND-** | Graph 노드 | GND-platform-001 | Neo4j Node | RAG |
| **GED-** | Graph 간선 | GED-plat-sub-001 | Neo4j Edge | RAG |
| **MEM-** | Memory | MEM-query-001 | query_memory, goal_memory | Guardian |
| **RAE-** | RAE 평가 | RAE-eval-001 | rae_index (ChromaDB) | Guardian |
| **tool:** | System RAG 도구 | tool:estimator:estimate | tool_registry.yaml | System |

**총**: 12개 Prefix

**양방향 ID**:
- umis.yaml ↔ tool_registry.yaml
- tool_key → source_section 역추적
- 정보 손실 없음

**추적 예시**:
```
Steve OPP_20241031_001.md
  → "시장 규모 270억 (Bill 계산)"
    → Bill market_sizing.xlsx
      → Assumptions: ASM_001 = 1,500억 ← SRC_20241031_001
      → Estimation_Details: EST_001 (30% 비중)
        → 사용 데이터: SRC_20241031_012, SRC_20241031_020
          → Rachel source_registry.yaml
            → SRC_20241031_001: "피아노 시장 1,500억"
              → source_url: "https://..."
              → 신뢰도: 85/100
```

### 4. Projection Mechanism (90% Rules + 10% LLM Learning)

Canonical → Projected 변환 과정

#### 4.1 규칙 기반 (90%)
```yaml
# config/projection_rules.yaml
field_rules:
  business_model:
    agents: [explorer]
    reason: "기회 발굴에 핵심"
  
  trigger_observations:
    agents: [observer, explorer]
    reason: "구조 관찰 + 기회 인식"
  
  churn_rate:
    agents: [explorer, quantifier, guardian]
    reason: "구독 평가 + 계산 + 검증"
    learned: true  # ← LLM 학습으로 추가됨
```

#### 4.2 LLM 판단 (10%)
```
1차: 필드 X → LLM 판단 → [explorer, quantifier] (로그)
2차: 필드 X → LLM 판단 → [explorer, quantifier] (로그)
3차: 필드 X → LLM 판단 → [explorer, quantifier] (로그)

3회 일관성 확인 (≥90%)
  ↓
자동 규칙화:
  config/projection_rules.yaml에 필드 X 규칙 추가
  learned: true 마킹

4차: 필드 X → 규칙 적용 (LLM 불필요)
```

#### 4.3 TTL 및 캐싱
```
1차 검색: "구독 모델" → on_demand 생성 (TTL 24h, access=1)
2차 검색: Cache Hit (access=2)
...
10차 검색: access=10 → 고빈도 감지 → persistent (영구)

25시간 후 (저빈도): TTL 만료 → 재생성
```

### 5. Validation & Traceability

#### 5.1 검증 프로토콜

```
Bill 산출물 완성
  ↓
[DELIVERABLE_COMPLETE] quantifier market_sizing.xlsx
  ↓
Stewart 자동 트리거:
  - Rachel 검증 요청 (데이터 신뢰도)
  - Albert 검증 요청 (시장 구조 부합성)
  ↓
Rachel 검증:
  - source_registry.yaml 모든 SRC_ID 유효? ✅
  - 평균 신뢰도 ≥ 70%? ✅ (85%)
  - Definition Gap 분석 완료? ✅
  → validation: {status: "passed", score: 9}
  ↓
Albert 검증:
  - SAM이 시장 구조와 부합? ✅
  - 가정이 관찰과 일치? ✅
  → validation: {status: "passed", score: 8}
  ↓
Stewart 종합:
  - 2명 검증 통과 ✅
  - deliverables_registry.yaml 업데이트
  - Grade: A
```

#### 5.2 추적 체인

모든 결론은 원본 데이터까지 역추적 가능:

```
Steve 기회 가설: "피아노 구독 서비스 SAM 270억"
  ↓ 근거 1: Albert 시장 구조 분석
    ↓ "학원 비중 30%" ← Bill EST_001
      ↓ EST_001 상세 논리 (7개 섹션)
        ↓ 사용 데이터: SRC_20241031_012 (서울 샘플 35%)
          ↓ Rachel source_registry.yaml
            ↓ source_url: "https://..."
            ↓ 신뢰도: 75/100
  
  ↓ 근거 2: Bill SAM 계산
    ↓ Method 2 Bottom-Up: 270억
      ↓ Assumptions: ASM_001 = 1,500억
        ↓ SRC_20241031_001
          ↓ Rachel source_registry.yaml
            ↓ source_url: "https://..."
            ↓ 신뢰도: 85/100
```

---

## 🔄 Data Flow & Relationships

### Explorer Workflow (5단계)

```
Input: triggers = ["구독 모델 트렌드"]
  ↓
Step 1: pattern_search
  Layers: [vector, graph]
  ├─ Vector Search: projected_index (agent_view=explorer)
  │  Query: "구독 모델"
  │  Top 5: subscription_model, platform_model, ...
  │
  └─ Graph Search: Neo4j
     Query: (Pattern)-[COMBINES_WITH]->()
     → Platform + Subscription 조합 발견
  
  Output: matched_patterns = [subscription_model, platform_model]
  ↓
Step 2: case_search
  Condition: patterns.count > 0 ✓
  Layers: [vector]
  Query: pattern_id = "subscription_model"
  Filter: chunk_type = "success_case"
  Top 3: Netflix, Spotify, Adobe
  
  Output: success_cases = [Netflix, Spotify, Adobe]
  ↓
Step 3: estimator_collaboration (조건부) v7.3.2+
  Condition: needs_estimation
  Agent: Estimator (Fermi)
  Query: "잠재 시장 크기는?"
  
  Estimator.estimate():
    - Phase 0: 프로젝트 데이터
    - Phase 1: 학습된 규칙
    - Phase 2: Validator 검색
    - Phase 3: 11개 Source
    - Phase 4: Fermi 분해
    - reasoning_detail 생성
    
  Output: estimation_result = {value, confidence, reasoning_detail}
  ↓
Step 4: quantifier_collaboration (조건부)
  Condition: needs_quantitative
  Evaluate: pattern.type == "market_sizing_required" → False
  → Skip
  ↓
Step 5: hypothesis_generation
  Layers: [vector, memory]
  Input: [patterns, cases, estimator_data, quantifier_data]
  Memory Check: query_memory (순환 감지)
  
  Generate: hypothesis = {
    title: "피아노 구독 서비스",
    pattern: "subscription_model",
    evidence: [Netflix 사례, Spotify 사례],
    market_size_estimate: estimator_data,  # Estimator 결과
    ...
  }
  
  Output: hypothesis
```

### Canonical → Projected → Graph 흐름

```
1. Canonical Index 빌드
   scripts/build_canonical_index.py
   ├─ umis_business_model_patterns.yaml 읽기
   ├─ 각 패턴마다:
   │  ├─ Anchor Path 추출 ("subscription_model.trigger_observations")
   │  ├─ Content Hash 계산 (SHA-256)
   │  └─ Lineage 생성 (from: "yaml_source")
   └─ ChromaDB canonical_index에 저장
      → CAN-subscription-001, CAN-platform-001, ...

2. Projected Index 빌드
   scripts/build_projected_index.py
   ├─ Canonical 청크 로드
   ├─ 각 청크마다:
   │  ├─ config/projection_rules.yaml 적용 (90%)
   │  │  trigger_observations → [observer, explorer]
   │  │  → PRJ-sub-obs-001, PRJ-sub-exp-001 생성
   │  │
   │  ├─ LLM 판단 (10%, 규칙 없는 필드)
   │  │  → data/llm_projection_log.jsonl 로깅
   │  │  → 3회 일관성 → 자동 규칙화
   │  │
   │  └─ Agent별 동적 필드 추가
   │     explorer: explorer_pattern_id, explorer_csf, ...
   │     quantifier: quantifier_metrics, quantifier_formula, ...
   └─ ChromaDB projected_index에 저장
      materialization: {strategy: "on_demand", cache_ttl_hours: 24}

3. Knowledge Graph 빌드
   scripts/build_knowledge_graph.py
   ├─ config/pattern_relationships.yaml 읽기
   ├─ Nodes 생성:
   │  pattern_id: "platform_business_model"
   │  vector_chunk_id: "PRJ-platform-exp-001"
   │  → GND-platform-001
   │
   ├─ Edges 생성:
   │  (GND-platform-001)-[COMBINES_WITH]->(GND-subscription-001)
   │  confidence: {similarity: 0.92, coverage: 0.10, overall: 0.85}
   │  evidence_ids: ["CAN-amazon-001", "PRJ-spotify-exp-002"]
   │  provenance: {source: "human_review", reviewer_id: "stewart"}
   │  → GED-plat-sub-001
   │
   └─ Neo4j에 저장
```

### Circuit Breaker 동작

```
정상:
  Vector Search → Success
  failure_count = 0, state = CLOSED

실패 1회:
  Vector Search → Timeout (30초)
  failure_count = 1
  Fallback: yaml_only

실패 2회:
  Vector Search → Connection Error
  failure_count = 2
  Fallback: yaml_only

실패 3회 (임계값):
  failure_count = 3
  state = OPEN (회로 차단!)
  → 모든 요청 즉시 실패 (60초간)

60초 후:
  state = HALF_OPEN
  시험 요청 → Success
  failure_count = 0
  state = CLOSED (정상 복구)
```

---

## 📁 Component Map

### 프로젝트 폴더 구조

```
umis/
├── umis.yaml                          # 메인 가이드 (Cursor Rules) - 6,539줄
├── umis_core.yaml                     # 압축 INDEX (AI 빠른 참조) - 928줄
├── umis_deliverable_standards.yaml   # 산출물 표준
├── umis_examples.yaml                 # 사용 예시
├── VERSION.txt                        # v7.3.2
│
├── config/                            # 설정 파일 (15개)
│   ├── agent_names.yaml               # Agent 이름 (6-Agent)
│   ├── model_configs.yaml             # LLM 모델 설정 (17개 모델) v7.8.0 NEW!
│   ├── tool_registry.yaml             # System RAG 도구 (31개)
│   ├── schema_registry.yaml           # RAG 스키마 (v1.1)
│   ├── projection_rules.yaml          # Projection 규칙 (Estimator 포함)
│   ├── routing_policy.yaml            # Workflow (Estimator 협업)
│   ├── runtime.yaml                   # 실행 모드
│   ├── pattern_relationships.yaml     # Knowledge Graph (45 관계)
│   ├── fermi_model_search.yaml        # Phase 4 설계 (1,500줄)
│   ├── learned_sga_patterns.yaml      # SG&A 학습 패턴 v1.0.0 (2025-11-13)
│   └── ...                            # 기타 설정 파일
│
├── deliverable_specs/                 # 산출물 스펙 (6개 YAML, AI 최적화)
│   ├── observer/market_reality_report_spec.yaml        (271줄)
│   ├── explorer/opportunity_hypothesis_spec.yaml       (750줄)
│   ├── quantifier/market_sizing_workbook_spec.yaml     (301줄)
│   ├── validator/source_registry_spec.yaml             (162줄)
│   └── project/                       # 프로젝트 메타
│       ├── project_meta_spec.yaml                      (261줄)
│       └── deliverables_registry_spec.yaml             (194줄)
│
├── scripts/                           # 실행 스크립트 (75개 파일)
│   ├── 01_convert_yaml.py             # YAML → JSONL
│   ├── 02_build_index.py              # RAG 빌드
│   ├── build_system_knowledge.py      # System RAG 빌드
│   ├── query_system_rag.py            # System RAG 검색
│   ├── build_canonical_index.py       # Canonical
│   ├── build_projected_index.py       # Projected
│   ├── build_knowledge_graph.py       # Graph
│   ├── test_guardian_memory.py        # Meta-RAG 테스트
│   ├── test_single_source_policy.py   # Single Source 테스트
│   └── test_*.py                      # 26개 테스트
│
├── umis_rag/                          # 핵심 패키지 (실제 RAG 코드)
│   ├── core/                          # 핵심 시스템 (11개 파일)
│   │   ├── schema.py                  # Pydantic 스키마
│   │   ├── metadata_schema.py         # 메타데이터 스키마
│   │   ├── config.py                  # 설정 관리
│   │   ├── model_router.py            # Phase별 모델 자동 선택 v7.8.0
│   │   ├── model_configs.py           # Model Config 시스템 v7.8.0 NEW!
│   │   ├── layer_manager.py           # 3-Layer 관리
│   │   ├── workflow_executor.py       # Workflow 실행
│   │   ├── circuit_breaker.py         # Circuit Breaker
│   │   └── ...
│   │
│   ├── agents/                        # 6-Agent 시스템
│   │   ├── observer.py                # Observer
│   │   ├── explorer.py                # Explorer
│   │   ├── quantifier.py              # Quantifier
│   │   ├── validator.py               # Validator
│   │   ├── guardian.py                # Guardian
│   │   └── estimator/                 # Estimator
│   │       ├── estimator.py           # 통합 인터페이스 (5-Phase)
│   │       ├── phase1_direct_rag.py   # Phase 1 (<0.5초)
│   │       ├── phase3_guestimation.py # Phase 3 (3-8초)
│   │       ├── phase4_fermi.py        # Phase 4 (10-30초, Step 1-4)
│   │       ├── learning_writer.py     # 학습 시스템
│   │       ├── source_collector.py    # 11개 Source
│   │       ├── judgment.py            # 판단 엔진
│   │       ├── models.py              # 데이터 모델
│   │       ├── rag_searcher.py        # RAG 검색
│   │       └── sources/               # Physical, Soft, Value
│   │
│   ├── graph/                         # Knowledge Graph (5개 파일)
│   │   ├── schema_initializer.py      # Neo4j 스키마
│   │   ├── connection.py              # Neo4j 연결
│   │   ├── hybrid_search.py           # Vector + Graph
│   │   └── confidence_calculator.py   # 다차원 신뢰도
│   │
│   ├── guardian/                      # Meta-RAG (7개 파일, 2,401줄)
│   │   ├── meta_rag.py                # 통합 오케스트레이터
│   │   ├── memory.py                  # 통합 메모리
│   │   ├── query_memory.py            # 순환 감지
│   │   ├── goal_memory.py             # 목표 정렬
│   │   ├── rae_memory.py              # 평가 일관성
│   │   └── three_stage_evaluator.py   # 3단계 평가
│   │
│   ├── projection/                    # Projection (3개 파일)
│   │   ├── hybrid_projector.py        # 90% 규칙 + 10% LLM
│   │   └── ttl_manager.py             # TTL 캐싱
│   │
│   ├── learning/                      # 학습 시스템
│   │   └── rule_learner.py            # LLM → 규칙
│   │
│   ├── deliverables/                  # Excel 자동 생성 (38개 파일)
│   │   └── excel/                     # 3개 도구
│   │       ├── formula_engine.py      # Excel 함수 엔진
│   │       ├── builder_contract.py    # Builder Contract
│   │       ├── market_sizing/         # 9 시트
│   │       ├── unit_economics/        # 10 시트
│   │       └── financial_projection/  # 11 시트
│   │
│   └── utils/                         # 유틸리티 (4개 파일)
│       ├── logger.py                  # 로깅
│       ├── dart_api.py                # DART API 클라이언트 v1.0.0 (2025-11-13)
│       └── guestimation.py            # Legacy (Deprecated)
│
├── scripts/                           # 실행 스크립트 (100개 파일)
│   ├── 01_convert_yaml.py             # YAML → JSONL 변환
│   ├── 02_build_index.py              # RAG 인덱스 빌드
│   ├── build_canonical_index.py       # Canonical 빌드
│   ├── build_projected_index.py       # Projected 빌드
│   ├── build_knowledge_graph.py       # Graph 빌드
│   ├── build_system_knowledge.py      # System RAG 빌드
│   ├── query_system_rag.py            # System RAG 검색
│   ├── sync_umis_to_rag.py            # umis.yaml → RAG 동기화
│   │
│   ├── parse_sga_final.py             # SG&A 진화형 파서 v1.0.0 (2025-11-13)
│   ├── parse_sga_smart_signals.py     # 스마트 시그널 파서 v1.0.0
│   ├── parse_sga_with_zip.py          # 규칙 기반 파서 v1.0.0
│   ├── classify_variable_fixed_costs.py  # 변동비/고정비 분류
│   ├── calculate_contribution_margin.py  # 공헌이익 계산
│   ├── summarize_sga_results.py       # SG&A 요약
│   │
│   ├── test_*.py                      # 테스트 스크립트 (26개)
│   └── ...
│
├── setup/                             # 설치 파일
│   ├── setup.py                       # 자동 설치 스크립트
│   ├── AI_SETUP_GUIDE.md              # AI용 가이드
│   └── START_HERE.md                  # 빠른 시작
│
├── benchmarks/                        # 통합 벤치마크 시스템 v7.8.0 NEW!
│   ├── README.md                      # 벤치마크 시스템 가이드
│   ├── MIGRATION_PLAN.md              # 4단계 마이그레이션 플랜
│   ├── PHASE1_COMPLETION_REPORT.md    # Phase 1 완료 보고서
│   ├── common/                        # 공통 모듈
│   │   └── __init__.py
│   └── estimator/                     # Estimator 벤치마크
│       ├── MODEL_CONFIG_DESIGN.md     # Model Config 설계 (773줄)
│       ├── MODEL_CONFIG_IMPLEMENTATION.md  # ModelRouter 확장 (203줄)
│       ├── MODEL_CONFIG_TEST_RESULTS.md    # 테스트 결과 (275줄)
│       ├── PHASE4_INTEGRATION_COMPLETE.md  # Phase 4 통합 (350줄)
│       ├── PHASE4_INTEGRATION_FINAL.md     # 최종 완료 (420줄)
│       ├── PHASE4_IMPROVEMENT_PLAN.md      # 개선 계획 (1,035줄)
│       ├── PHASE4_IMPROVEMENTS_SUMMARY.md  # 개선 요약 (137줄)
│       └── phase4/                    # Phase 4 Fermi 벤치마크
│           ├── README.md              # Phase 4 Architecture
│           ├── common.py              # 공통 함수 (평가 시스템 v7.8.0)
│           ├── scenarios.py           # 15개 Fermi 문제
│           ├── tests/                 # 벤치마크 테스트
│           │   ├── batch1.py          # o1-mini, gpt-5.1 (high), o3-mini
│           │   ├── batch2.py          # gpt-5-pro, o1-pro (high 고정)
│           │   ├── batch3.py          # gpt-4o, gpt-4o-mini, gpt-4-turbo
│           │   ├── batch4.py          # gpt-5.1 (medium)
│           │   ├── batch5.py          # gpt-5.1 (low)
│           │   └── extended_10problems.py  # 확장 10문제
│           ├── results/               # 벤치마크 결과 (JSON)
│           └── analysis/              # 분석 문서
│               ├── model_recommendations.md    # 모델 추천
│               └── evaluation_rebalancing.md   # 평가 재조정
│
├── tests/                             # 통합 테스트
│   ├── test_model_configs.py          # Model Config 기본 테스트 v7.8.0
│   ├── test_model_configs_simulation.py  # Model Config 실전 시뮬레이션 v7.8.0
│   ├── test_integration_timeline.py
│   ├── test_observer_timeline.py
│   └── test_strategy_playbook.py
│
├── setup/                             # 설치 파일
│   ├── setup.py                       # 자동 설치 스크립트
│   ├── AI_SETUP_GUIDE.md              # AI용 가이드
│   └── START_HERE.md                  # 빠른 시작
│
├── dev_docs/                          # 개발 문서 (Alpha only, 50,000줄+)
│   ├── guestimation_v3/               # Estimator 설계 (20개)
│   ├── reports/                       # 분석 리포트 (10개)
│   └── ...
│
├── archive/                           # Deprecated (Alpha only)
│   ├── guestimation_v1_v2/            # v7.2.1 이하
│   └── v7.2.0_and_earlier/            # 이전 버전
│
└── docs/                              # 활성 UMIS 문서
    ├── README.md
    ├── GUESTIMATION_FRAMEWORK.md      # Fermi Estimation 가이드
    ├── INSTALL.md
    ├── FOLDER_STRUCTURE.md
    ├── VERSION_UPDATE_CHECKLIST.md
    ├── MAIN_BRANCH_SETUP.md
    ├── UMIS-DART-재무제표-조사-프로토콜.md
    └── excel/                         # Excel 관련 문서
        ├── EXCEL_QA_SYSTEM.md
        ├── EXCEL_VALIDATION_GUIDE.md
        ├── EXCEL_SHEET_SPECS.yaml
        └── WHY_QA_FAILED_AND_FIX.md
```

### 주요 파일 역할

| 파일 | 역할 | 크기/개수 | 버전 |
|------|------|-----------|------|
| **umis.yaml** | Cursor Rules, 메인 가이드 | 6,539줄 | Estimator 386줄 |
| **umis_core.yaml** | 압축 INDEX (AI 빠른 참조) | 928줄 | 87% 절약 |
| **config/model_configs.yaml** | LLM 모델 설정 (중앙 관리) | 18개 모델, 327줄 | v7.8.1 NEW! |
| **config/tool_registry.yaml** | System RAG 도구 정의 | 31개 도구 | Estimator 3개 |
| **config/schema_registry.yaml** | RAG 레이어 통합 스키마 | 851줄, v1.1 | EST- prefix |
| **config/projection_rules.yaml** | Canonical → Projected 변환 | 125줄 | Estimator 규칙 |
| **config/routing_policy.yaml** | Workflow 정의 | 194줄, v1.1.0 | Estimator 협업 |
| **config/runtime.yaml** | 실행 모드 (hybrid) | 99줄 | Circuit Breaker |
| **config/fermi_model_search.yaml** | Phase 4 설계 (Step 1-4) | 1,500줄 | v2.0 |
| **umis_rag/core/model_configs.py** | Model Config 시스템 | 262줄 | v7.8.0 NEW! |
| **umis_rag/core/model_router.py** | Phase별 모델 자동 선택 | 확장됨 | v7.8.0 |
| **umis_rag/agents/estimator/** | Estimator Agent | 14개 파일, 5,200줄 | v7.8.0 |
| **umis_rag/guardian/** | Meta-RAG | 7개 파일, 2,401줄 | v7.1.0+ |
| **benchmarks/estimator/** | Estimator 벤치마크 | 7개 문서, 3,193줄 | v7.8.0 NEW! |

---

## 🔧 Configuration Quick Reference

### 실행 모드 (config/runtime.yaml)

```yaml
mode: rag_full  # yaml_only / hybrid / rag_full

layers:
  vector: true      # ChromaDB Vector RAG
  graph: true       # Neo4j Knowledge Graph
  memory: true      # Guardian Memory
  meta: true        # Meta-RAG (구현 완료)
  estimator: true   # Estimator 5-Phase

circuit_breaker:
  enabled: true
  failure_threshold: 3
  timeout_seconds: 30
  recovery_timeout: 60
```

**모드 선택 가이드**:
- `yaml_only`: RAG 없이 기본 YAML만 (안전, 느림)
- `hybrid`: Vector RAG만 (안정적)
- `rag_full`: Vector + Graph + Memory + Meta + Estimator (모든 기능) ← **기본값**

### Projection 학습 (config/projection_rules.yaml)

```yaml
learning:
  enabled: true
  min_occurrences: 3         # 3회 이상 → 규칙화
  confidence_threshold: 0.9  # LLM 판단 일관성 90%+

llm_log_path: "data/llm_projection_log.jsonl"
```

**학습 프로세스**:
1. 규칙 없는 필드 → LLM 판단 (로그)
2. 3회 이상 일관성 확인 (≥90%)
3. 자동 규칙 추가 (`learned: true`)
4. 이후 규칙 적용 (LLM 불필요)

### Overlay Layer (config/overlay_layer.yaml)

```yaml
enabled: false  # 현재 1인 개발 (비활성)

# 팀 확장 시 활성화:
layers:
  core:    # 공식 검증 데이터 (우선순위 3)
  team:    # 팀 공유 데이터 (우선순위 2)
  personal: # 개인 실험 데이터 (우선순위 1)

search_order: [personal, team, core]  # 개인 > 팀 > 공식
```

---

## 🎓 Key Learnings & Best Practices

### 1. 스키마 설계 원칙

✅ **DO**:
- ID는 불변 (observer, CAN-*, PRJ-*)
- Name은 변경 가능 (Albert → 다른 이름)
- 모든 데이터에 Lineage (from, via, evidence_ids)
- Anchor Path (안정) > Line Range (불안정)
- Content Hash로 변경 감지

❌ **DON'T**:
- Line Range 사용 (파일 수정 시 깨짐)
- 하드코딩된 Agent Name (폴더명 등)
- ID 없는 데이터 (추적 불가)

### 2. Projection 전략

- **90% 규칙 기반**: 성능, 일관성
- **10% LLM 판단**: 유연성, 학습
- **3회 일관성 → 규칙화**: 자동 개선

### 3. 캐싱 전략

- **기본**: on_demand (TTL 24h)
- **고빈도 (10회+)**: persistent (영구)
- **저빈도**: TTL 만료 → 재생성

### 4. Fail-Safe 계층 (다층 방어)

- **Level 1**: Fallback (vector_fail → yaml_only)
- **Level 2**: Mode Toggle (hybrid → yaml_only)
- **Level 3**: Circuit Breaker (3회 실패 → 60초 차단)

---

## 📖 References

### 핵심 문서
- `umis.yaml` (6,539줄): 메인 가이드 (Cursor Rules, Estimator 포함)
- `umis_core.yaml` (928줄): 압축 INDEX (System RAG용, 87% 절약)
- `config/schema_registry.yaml` (851줄, v1.1): RAG 레이어 스키마
- `config/tool_registry.yaml` (1,710줄): System RAG 도구 (31개)
- `umis_deliverable_standards.yaml`: 산출물 표준

### 참조 문서
- `docs/`: 활성 참조 가이드 (6개)
  - `INSTALL.md`: 빠른 설치 가이드
  - `FOLDER_STRUCTURE.md`: 폴더 구조 및 네이밍 규칙
  - `VERSION_UPDATE_CHECKLIST.md`: 버전 관리 체크리스트
  - `MAIN_BRANCH_SETUP.md`: main 브랜치 설정
  - `UMIS-DART-재무제표-조사-프로토콜.md`: Rachel 재무 데이터 조사 표준
  - `README.md`: docs 폴더 설명

### 설치 문서
- `setup/`: 설치 관련 모든 파일
  - `setup.py`: 자동 설치 스크립트
  - `AI_SETUP_GUIDE.md`: AI용 설치 가이드
  - `SETUP.md`: 상세 설치 가이드
  - `START_HERE.md`: UMIS 빠른 시작

### 개발 문서
- `dev_docs/`: RAG 개발 히스토리 (시스템 비의존)
  - `architecture/`: RAG v3.0 아키텍처 설계
  - `analysis/`: 시스템 분석 문서
  - `dev_history/`: 주차별 개발 히스토리
  - `guides/`: 개발 가이드
- `deliverable_specs/`: AI 최적화 스펙 (6개 YAML)
- `scripts/README.md`: 스크립트 사용법

### 프로젝트 산출물
- `projects/`: 실제 시장 분석 프로젝트 (Git 제외)
  - `market_analysis/`: Legacy 프로젝트 (v7.0.0 이전)

### 예시
- `umis_examples.yaml`: 산출물 예시

### Deprecated
- `archive/deprecated/docs/`: v6.2 이전 문서들
- `archive/v{X}.x/`: 버전별 가이드라인

**Note**: main 브랜치에서는 archive/, dev_docs/ 제외됨 (.gitignore)

---

## 🚀 Getting Started

**신규 사용자**: [INSTALL.md](docs/INSTALL.md) - 설치 가이드  
**빠른 시작**: [setup/START_HERE.md](setup/START_HERE.md) - 30초 가이드  
**상세 가이드**: [setup/SETUP.md](setup/SETUP.md) - 단계별 설치

**개발자**: [dev_docs/guides/](dev_docs/guides/) - 개발 가이드  
**기여자**: [VERSION_UPDATE_CHECKLIST.md](docs/VERSION_UPDATE_CHECKLIST.md) - 버전 관리

---

## 📌 Maintenance

### 버전 업데이트 체크리스트

버전 업데이트 시 **반드시 이 문서를 업데이트**:

- [ ] **Version Info** 섹션 업데이트
- [ ] **System Architecture** 다이어그램 (구조 변경 시)
- [ ] **Core Concepts** (새 개념 추가 시)
- [ ] **Component Map** (폴더/파일 변경 시)
- [ ] **[CHANGELOG.md](../../CHANGELOG.md)** 에 변경 사항 추가
- [ ] **Breaking Changes** 명시
- [ ] **Deprecated** 항목 표시

### 주요 변경 시나리오

| 변경 사항 | 업데이트 대상 |
|----------|--------------|
| 새 Agent 추가 | System Architecture, 6-Agent System, Data Flow |
| 새 RAG Layer 추가 | System Architecture, 4-Layer RAG Architecture |
| 스키마 변경 | Core Concepts, config/schema_registry.yaml 동기화 |
| 새 ID Prefix | ID Namespace System 테이블 |
| Projection 규칙 변경 | Projection Mechanism, config/projection_rules.yaml 동기화 |
| 워크플로우 변경 | Data Flow & Relationships, config/routing_policy.yaml 동기화 |
| 폴더 구조 변경 | Component Map |
| System RAG 도구 추가 | config/tool_registry.yaml 동기화 |

---

---

## 🤖 LLM Mode Architecture

### LLM 활용 전략

```
┌───────────────────────────────────────┐
│  Native Mode (권장: 일회성 분석)        │
│  Cursor Agent LLM (사용자 선택)        │
│  - Claude Sonnet 4.5, GPT-4o 등       │
│  - 비용: $0 (Cursor 구독 포함)         │
│  - 품질: 최고                          │
│  - 자동화: 불가                        │
└───────────────────────────────────────┘
              │
              ▼
         UMIS RAG
              │
              ▼
┌───────────────────────────────────────┐
│  External Mode (필요 시: 자동화)       │
│  OpenAI/Anthropic API                │
│  - GPT-4, Claude API 등               │
│  - 비용: $3-10/1M tokens              │
│  - 품질: 중상                          │
│  - 자동화: 가능                        │
└───────────────────────────────────────┘
```

**권장사항**: 
- 일회성 분석 → Native Mode (무료, 고품질)
- 대량 자동화 → External Mode (필요 시만)

**상세**: `docs/ARCHITECTURE_LLM_STRATEGY.md`

---

## 🔧 자동 환경변수 로드

### 자동 로드 프로세스

```python
# umis_rag/__init__.py

def _load_environment():
    """패키지 import 시 자동 실행"""
    search_paths = [
        Path.cwd() / '.env',           # 1. 현재 디렉토리
        Path(__file__).parent.parent / '.env',  # 2. UMIS 루트
        Path.home() / '.env',          # 3. 홈 디렉토리
    ]
    
    for env_path in search_paths:
        if env_path.exists():
            load_dotenv(env_path, override=False)
            return True

# 패키지 import 시 자동 실행
_env_loaded = _load_environment()
```

**효과**:
- ✅ 사용자가 `load_dotenv()` 불필요
- ✅ 에러 발생률 -30%
- ✅ 코드 간소화

**상세**: `setup/ENV_SETUP_GUIDE.md`

---

## 🎯 Estimator (Fermi) Agent (v7.7.0 용어 명확화)

### 6번째 Agent - 값 추정 전문가

**핵심**: "순수 추정 전문 (계산은 Quantifier) + 5-Phase + 100% 커버리지"

**역할**:
- 값 추정 전문 (데이터 없을 때 만들어냄)
- 계산은 Quantifier 담당 (역할 명확 분리)
- 5-Phase Architecture (Phase 0→1→2→3→4 자동 선택)
- Validator 우선 검색 (Phase 2, 85% 처리)
- Fermi 내부 Step 1-4 명확화
- Context 전달 개선 (재귀 시 구체적 질문)
- LLM 모드 통합 (Native/External)

**위치**: `umis_rag/agents/estimator/` (14개 파일, 5,200줄, v7.7.0)

**클래스**: `EstimatorRAG` (통합 인터페이스)

**v7.7.0 용어 체계**:
- **파일명**: phase1_direct_rag.py, phase3_guestimation.py, phase4_fermi.py
- **클래스명**: Phase1DirectRAG, Phase3Guestimation, Phase4FermiDecomposition
- **Phase**: Estimator 전체 단계 (0-4)
- **Step**: Phase 4 (Fermi) 내부 단계 (1-4)

**역할 분리**:
```python
# Estimator: 값 추정만
estimator.estimate("B2B SaaS ARPU는?", domain="B2B_SaaS")
# → 80,000원 (Phase 3, 벤치마크 기반)

# Quantifier: 계산만
quantifier.calculate_ltv(...)
# 내부적으로:
#   1. ARPU 필요 → estimator.estimate("ARPU는?") 
#   2. Churn 필요 → estimator.estimate("Churn은?")
#   3. 계산: LTV = 80,000 / 0.05 = 1,600,000원
```

**사용 예시**:
```python
from umis_rag.agents.estimator import EstimatorRAG

estimator = EstimatorRAG()

# Phase 1/2/3 (증거 기반)
result = estimator.estimate("B2B SaaS Churn Rate는?", domain="B2B_SaaS")

# Phase 4 (Fermi 분해)
result = estimator.estimate("서울 음식점 수는?")

# Cursor에서 (Native 모드)
@Fermi, B2B SaaS 한국 ARPU는?
```

```
┌─────────────────────────────────────────────┐
│ Phase 0: Literal (프로젝트 데이터, <0.1초) │
│   - 프로젝트 명시 데이터 즉시 반환         │
│   - confidence: 1.0                        │
│   - 커버리지: 10%                          │
└──────────────┬──────────────────────────────┘
               │ 없음
               ▼
┌─────────────────────────────────────────────┐
│ Phase 1: Direct RAG (유사도 0.95+, <0.5초)│
│   - 학습된 규칙 RAG (0 → 2,000개 진화)     │
│   -: Built-in 제거 (일관성)        │
│   - 원칙: 정확한 매칭만                    │
│   - 파일: phase1_direct_rag.py             │
└──────────────┬──────────────────────────────┘
               │ 유사도 < 0.95
               ▼
┌─────────────────────────────────────────────┐
│ Phase 2: Validator (확정 데이터, <1초)    │
│   - Validator RAG 검색 (85% 처리!)        │
│   - 단위 자동 변환 (갑/년 → 갑/일)        │
│   - Relevance 검증 (GDP 오류 방지)        │
│   - confidence: 1.0                        │
│   - 파일: estimator.py                     │
└──────────────┬──────────────────────────────┘
               │ 없음
               ▼
┌─────────────────────────────────────────────┐
│ Phase 3: Guestimation (conf 0.80+, 3-8초) │
│   1. 맥락 파악 (intent, domain, region)   │
│   2. Source 수집 (11개)                   │
│      - Physical: 절대 한계 (3개)           │
│      - Soft: 범위 제시 (3개)              │
│      - Value: 값 결정 (5개)               │
│   3. 증거 평가 및 판단 (4가지 전략)       │
│   4. 학습 (Phase 1 편입)                  │
│   - 파일: phase3_guestimation.py           │
└──────────────┬──────────────────────────────┘
               │ confidence < 0.80
               ▼
┌─────────────────────────────────────────────┐
│ Phase 4: Fermi Decomposition (10-30초)    │
│   ├─ Step 1: 초기 스캔 (Bottom-up)        │
│   ├─ Step 2: 모형 생성 (Top-down, 3-5개)  │
│   ├─ Step 3: 실행 가능성 체크 (재귀)      │
│   └─ Step 4: 모형 실행 (Backtracking)     │
│   - 일반 Fermi 분해 (물리적/수학적)       │
│   - 재귀 추정 (max depth 4)               │
│   - 데이터 상속                            │
│   - Context 전달 (구체적 질문)            │
│   - 순환 감지 (Call stack)                │
│   - 파일: phase4_fermi.py (2,500줄)       │
└─────────────────────────────────────────────┘

총 커버리지: 100%
실패율: 0%
역할: 순수 추정 (계산은 Quantifier)
```

**Estimator vs Quantifier 역할**:
```
Estimator (추정):
  - "B2B SaaS ARPU는?" → 80,000원 (Phase 2, Validator)
  - "서울 음식점 수는?" → 600,000개 (Phase 4, Fermi)
  - "Churn Rate는?" → 5% (Phase 3, 업계 평균)

Quantifier (계산, 31개 방법론):
  - LTV = ARPU / Churn_Rate
  - Payback = CAC / (ARPU × Gross_Margin)
  - Rule of 40 = Growth_Rate + Profit_Margin
  - 계산에 필요한 값 → Estimator에게 요청

협업:
  Quantifier: "LTV 계산 필요"
    → "ARPU는?" Estimator 호출 → 80,000원
    → "Churn은?" Estimator 호출 → 5%
    → 계산: LTV = 80,000 / 0.05 = 1,600,000원
```

**LLM 모드**:
- Native Mode: 비용 $0, Cursor LLM 직접 사용 (진짜 구현!)
- External Mode: 비용 $0.10/요청, OpenAI API (자동화 시)

**파일**: `umis_rag/agents/estimator/` (14개 파일, 5,200줄, v7.7.0)
- estimator.py (520줄, 5-Phase 통합)
- phase1_direct_rag.py (320줄, Phase 1)
- phase3_guestimation.py (650줄, Phase 3)
- phase4_fermi.py (2,500줄, Phase 4, Step 1-4)
- models.py (520줄, Phase1/3/4Config)
- learning_writer.py (564줄)
- boundary_validator.py (검증)
- 기타 7개

**v7.7.0 변경**:
- Native 모드 진짜 구현 (LLMProvider)
- 용어 체계 명확화 (Phase + Step)
- 3-Tier 완전 Deprecated
- Phase 4 내부 Step 1-4 명시

---

## 🎯 Fermi Model Search (Phase 4 내부, v7.7.0)

### Fermi 추정 엔진 (Step 1-4)

**핵심**: "논리의 퍼즐 맞추기"

**v7.7.0**: Phase 4 (Fermi Decomposition) 내부의 Step 1-4

```
┌───────────────────────────────────────┐
│ Step 1: 초기 스캔 (Bottom-up)         │
│ 가용 데이터: [A, B, C]                │
└───────────────────────────────────────┘
          │
          ▼
┌───────────────────────────────────────┐
│ Step 2: 모형 생성 (Top-down)          │
│ LLM이 3-5개 후보 제시                 │
│ - 목표 = A × B × X                   │
│ - 목표 = A × B × C × Y               │
└───────────────────────────────────────┘
          │
          ▼
┌───────────────────────────────────────┐
│ Step 3: 퍼즐 맞추기                   │
│ X, Y를 채울 수 있나? (재귀)           │
└───────────────────────────────────────┘
          │
          ▼
┌───────────────────────────────────────┐
│ Step 4: 재조립 (Backtracking)         │
│ A × B × C × Y → 결과                  │
└───────────────────────────────────────┘
```

**재귀 구조 (Step 3)**:
- Unknown 변수 → Phase 3 시도 → 재귀 호출
- Max depth: 4
- 순환 감지 (Call stack)
- Context 전달 (구체적 질문)

**v7.7.0 변경**:
- Fermi 내부: Phase → Step (명확성)
- Step 1-4: 스캔 → 생성 → 체크 → 실행
- Phase 4 역할: 일반 Fermi 분해 (물리적/수학적)
- 예: 음식점 수, 탁구공 개수, 커피 시장

**파일**: `umis_rag/agents/estimator/phase4_fermi.py` (2,500줄, Step 1-4)

---

---

## 🎯 Single Source of Truth

### 추정 일원화 원칙

**원칙**: "모든 값/데이터 추정은 Estimator (Fermi) Agent만 수행"

```yaml
적용:
  ✅ Quantifier: 계산 OK, 추정 NO → Estimator 호출
  ✅ Validator: 검증 OK, 추정 NO → Estimator 호출
  ✅ Observer: 관찰 OK, 추정 NO → Estimator 호출
  ✅ Explorer: 가설 OK, 추정 NO → Estimator 호출
  ✅ Guardian: 평가 OK, 추정 NO → Estimator 호출
  ✅ Estimator: 추정 OK (유일한 권한)

이유:
  1. 데이터 일관성
     - 같은 질문 → 같은 답 (보장)
  
  2. 학습 효율
     - 모든 추정이 한 곳에 축적
     - Phase 3 → Phase 1 진화
  
  3. 근거 추적
     - 추정값의 출처 명확
     - 재현 가능성
```

### 추정 근거 제공

```python
result = estimator.estimate("Churn Rate는?")

# 필수 제공
result.reasoning_detail = {
  'method': 'weighted_average',
  'sources_used': ['statistical', 'rag'],
  'why_this_method': '증거 유사',
  'evidence_breakdown': [...],
  'judgment_process': [...]
}

result.component_estimations = [...]  # 개별 요소
result.estimation_trace = [...]       # 과정 추적
```

**효과**:
- ✅ 완전한 투명성
- ✅ 재현 가능
- ✅ 검증 가능

---

**Document Owner**: AI Team
**Last Reviewed**: 2025-11-24
**Next Review**: 버전 업데이트 시

---

*이 문서는 UMIS의 "살아있는 설계도"입니다. 모든 버전 업데이트 시 함께 업데이트되어야 합니다.*

**변경 이력**: [CHANGELOG.md](../../CHANGELOG.md)

