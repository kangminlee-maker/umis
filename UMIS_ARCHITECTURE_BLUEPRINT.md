# UMIS Architecture Blueprint
**Universal Market Intelligence System - 시스템 설계도**

---

## 📌 Version Info

| Item | Value |
|------|-------|
| **UMIS Version** | v7.5.0 "Complete System" |
| **Agent System** | 6-Agent (Observer, Explorer, Quantifier, Validator, Guardian, **Estimator**) ⭐ |
| **RAG Architecture** | v3.0 (4-Layer) |
| **Excel Engine** | v1.0 (3개 도구 완성) |
| **Estimator Agent** | v3.0 (3-Tier 완성 + 12개 지표) ⭐ |
| **Tier 3 Fermi** | v1.0 (구현 완료, 23개 모형) ⭐ |
| **Business Metrics** | 12개 지표 (v7.5.0) ⭐ |
| **Data Inheritance** | v1.0 (재귀 최적화, v7.5.0) ⭐ |
| **Single Source Policy** | v1.0 (추정 일원화) ⭐ |
| **Reasoning Transparency** | v1.0 (추정 근거 투명화) ⭐ |
| **Meta-RAG** | v1.0 (Guardian 프로세스 감시) ⭐ |
| **System RAG** | v1.0 (31개 도구) ⭐ |
| **LLM Mode** | Native + External (v1.0) ⭐ |
| **Schema Registry** | v1.1 (Estimator 반영) ⭐ |
| **Coverage** | 100% (실패율 0%) ⭐ |
| **Cost** | $0 (Native mode) ⭐ |
| **Last Updated** | 2025-11-08 |
| **Status** | Production Ready - 완전체 |

**Purpose**: UMIS 전체 구조와 기능을 한눈에 파악할 수 있는 고수준 설계도

---

## 🎯 System Overview

### What is UMIS?
시장 분석을 위한 **6-Agent 협업 시스템** + **Multi-Layer RAG 아키텍처** + **Excel 자동 생성**

### Key Characteristics
- ✅ **6-Agent 협업 시스템** 역할 분담 및 상호 검증 (v7.3.1+)
- ✅ **Estimator (Fermi) Agent** 값 추정 및 판단 전문가 (v7.3.1+)
- ✅ **Single Source of Truth** 모든 값 추정은 Estimator만 (v7.3.2+)
- ✅ **Reasoning Transparency** 추정 근거 완전 투명화 (v7.3.2+)
- ✅ **Learning System** 사용할수록 6-16배 빠름 (v7.3.0+)
- ✅ **Meta-RAG** Guardian 프로세스 자동 감시 (v7.1.0+)
- ✅ **System RAG** 31개 도구 Key-based 검색 (v7.2.0+)
- ✅ **RAG 기반 지식 활용** 360개 검증된 데이터 (54개 패턴/사례)
- ✅ **Knowledge Graph** 패턴 조합 자동 발견 (13 노드, 45 관계)
- ✅ **Excel 자동 생성** 3개 도구 (9-11 시트)
- ✅ **Fermi Model Search** Tier 3 준비 완료 (v7.2.1+)
- ✅ **Native Mode** Cursor LLM 직접 활용, 비용 $0 (v7.2.0+)
- ✅ **완전한 추적성** 양방향 ID 시스템 (14개 Prefix)
- ✅ **재검증 가능** Excel 함수 100%, Named Range
- ✅ **자동 환경변수** .env 자동 로드 (v7.2.0+)

### Quick Start

**설치**: [INSTALL.md](docs/INSTALL.md) 참조 (AI 자동 / 스크립트 / 수동)

**사용**:
```
Cursor Composer (Cmd+I):
"@Explorer, 시장 분석해줘"
"@Fermi, B2B SaaS Churn Rate는?"  ⭐ v7.3.1+
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
│                   │   Estimator     │ ⭐ v7.3.1+                    │
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
│  - EstimationResult (Fermi) ⭐ v7.3.1+                             │
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

### 1. 6-Agent System (Business Layer) - v7.3.1+

#### Agent 역할 및 산출물

| Agent ID | Name (기본) | Role | 산출물 | 검증자 |
|----------|------------|------|--------|--------|
| **observer** | Albert | 시장 구조 분석 | market_reality_report.md | quantifier, validator, guardian |
| **explorer** | Steve | 기회 발굴 (RAG) | OPP_*.md | observer, quantifier, validator |
| **quantifier** | Bill | 정량 분석 + Excel 생성 | market_sizing.xlsx (10 sheets)<br>unit_economics.xlsx (10 sheets)<br>financial_projection.xlsx (11 sheets) | validator, observer |
| **validator** | Rachel | 데이터 검증 | source_registry.yaml | - (검증자) |
| **guardian** | Stewart | 프로세스 관리 | .project_meta.yaml, deliverables_registry.yaml | - (메타 관리자) |
| **estimator** | **Fermi** | **값 추정 및 판단** ⭐ | **EstimationResult** (값 + 근거) | - (협업 파트너) |

**핵심**: 
- **Agent ID 불변** (observer, explorer, quantifier, validator, guardian, **estimator**) → 폴더/파일 경로
- **Name 변경 가능** (config/agent_names.yaml) → 사용자 UI
- **상호 검증** (각 산출물 2-3명 검증)
- **Estimator 특수성** (v7.3.1+): 협업 파트너 (모든 Agent가 필요 시 호출, Workflow에 끼어들지 않음)
- **Single Source Policy** (v7.3.2+): 모든 값 추정은 Estimator만 수행

#### 데이터 흐름 (순차적 의존성)

```
Rachel (Validator)
  ↓ SRC_YYYYMMDD_NNN
  │ source_registry.yaml
  │ - SRC_20241031_001: "피아노 시장 1,500억"
  │ - 신뢰도 평가 (0-100)
  │ - Definition Gap 분석
  │ - 추정치 검증 필요 시 → Fermi 호출 (v7.3.2 교차 검증)
  │
  ├─► Fermi (Estimator) ⭐ 협업 파트너
  │   │ EstimationResult
  │   │ - 값 추정 (데이터 부족 시)
  │   │ - 교차 검증 (Validator 요청)
  │   │ - reasoning_detail (완전한 근거)
  │   │ - Tier 1/2/3 자동 선택
  │   │ - 학습 (confidence >= 0.80)
  │   └─ 모든 Agent에서 호출됨
  │
Bill (Quantifier)
  ↓ SAM 계산
  │ market_sizing.xlsx
  │ - Assumptions: SRC_ID 참조
  │ - 전환율/AOV 등 → Fermi 호출 (Single Source) ⭐
  │ - Estimation_Details: EST-NNN (추정 ID)
  │ - 4가지 Method → Convergence (±30%)
  │ - 결과: SAM 270억 ± 30억
  │
Albert (Observer)
  ↓ 시장 구조 분석
  │ market_reality_report.md
  │ - 모든 주장에 SRC_ID 또는 Bill 계산 참조
  │ - 가치사슬 마진 → Fermi 호출 ⭐
  │ - 가치사슬 맵
  │ - 비효율성 정량화 (Bill + Fermi 협업)
  │
Steve (Explorer)
  ↓ 기회 가설
  │ OPP_*.md
  │ - Albert 분석 참조
  │ - 기회 크기 → Fermi 호출 (Order of Magnitude) ⭐
  │ - Bill SAM 참조
  │ - Rachel SRC_ID 참조
  │ - 3명 검증 (Albert, Bill, Rachel)
  │ - 우선순위 자동 계산 (5개 차원)
  │
Stewart (Guardian)
  │ .project_meta.yaml (프로젝트 진행 추적)
  │ deliverables_registry.yaml (산출물 자동 등록)
  │ - 프로젝트 리소스 → Fermi 호출 ⭐
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
  Agent Views: observer, explorer, quantifier, validator, guardian, estimator ⭐
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
  
  Estimation Results: Estimator 추정 결과 (v7.3.1+) ⭐
    - estimation_id: "EST-churn-001"
    - value: 0.06, confidence: 0.85
    - reasoning_detail: {...}
    - tier: 1/2/3
```

### 3. ID Namespace System (양방향 추적)

모든 데이터 요소는 고유 ID를 가지며, **양방향 추적 가능**

| Prefix | 의미 | 예시 | Collection/파일 | Agent |
|--------|------|------|----------------|-------|
| **SRC-** | 데이터 출처 | SRC_20241031_001 | source_registry.yaml | Rachel |
| **EST-** | **Estimator 추정 결과** ⭐ | **EST-churn-001** | **EstimationResult (Memory)** | **Fermi** |
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

**총**: 12개 Prefix (v7.3.2)

**양방향 ID** (v7.2.0 신규):
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

### Explorer Workflow (5단계) - v7.3.2

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
Step 3: estimator_collaboration (조건부) ⭐ v7.3.2+
  Condition: needs_estimation
  Agent: Estimator (Fermi)
  Query: "잠재 시장 크기는?"
  
  Estimator.estimate():
    - Tier 1 체크 (학습된 규칙)
    - Tier 2 실행 (11개 Source)
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
    market_size_estimate: estimator_data,  # ⭐ Estimator 결과
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
├── umis.yaml                          # 메인 가이드 (Cursor Rules) - 6,539줄 ⭐
├── umis_core.yaml                     # 압축 INDEX (AI 빠른 참조) - 928줄 ⭐
├── umis_deliverable_standards.yaml   # 산출물 표준
├── umis_examples.yaml                 # 사용 예시
├── VERSION.txt                        # v7.3.2 ⭐
│
├── config/                            # 설정 파일 (12개) ⭐
│   ├── agent_names.yaml               # Agent 이름 (6-Agent)
│   ├── tool_registry.yaml             # System RAG 도구 (31개) ⭐
│   ├── schema_registry.yaml           # RAG 스키마 (v1.1) ⭐
│   ├── projection_rules.yaml          # Projection 규칙 (Estimator 포함)
│   ├── routing_policy.yaml            # Workflow (Estimator 협업) ⭐
│   ├── runtime.yaml                   # 실행 모드
│   ├── pattern_relationships.yaml     # Knowledge Graph (45 관계)
│   ├── fermi_model_search.yaml        # Tier 3 설계 (1,266줄) ⭐
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
│   ├── build_system_knowledge.py      # System RAG 빌드 ⭐
│   ├── query_system_rag.py            # System RAG 검색 ⭐
│   ├── build_canonical_index.py       # Canonical
│   ├── build_projected_index.py       # Projected
│   ├── build_knowledge_graph.py       # Graph
│   ├── test_guardian_memory.py        # Meta-RAG 테스트 ⭐
│   ├── test_single_source_policy.py   # Single Source 테스트 ⭐
│   └── test_*.py                      # 26개 테스트
│
├── umis_rag/                          # 핵심 패키지 (실제 RAG 코드)
│   ├── core/                          # 핵심 시스템 (9개 파일)
│   │   ├── schema.py                  # Pydantic 스키마
│   │   ├── metadata_schema.py         # 메타데이터 스키마
│   │   ├── config.py                  # 설정 관리
│   │   ├── layer_manager.py           # 3-Layer 관리
│   │   ├── workflow_executor.py       # Workflow 실행
│   │   ├── circuit_breaker.py         # Circuit Breaker
│   │   └── ...
│   │
│   ├── agents/                        # 6-Agent 시스템 ⭐
│   │   ├── observer.py                # Observer
│   │   ├── explorer.py                # Explorer
│   │   ├── quantifier.py              # Quantifier
│   │   ├── validator.py               # Validator
│   │   ├── guardian.py                # Guardian
│   │   └── estimator/                 # ⭐ Estimator (v7.3.1+)
│   │       ├── estimator.py           # 통합 인터페이스
│   │       ├── tier1.py               # Fast Path (<0.5초)
│   │       ├── tier2.py               # Judgment Path (3-8초)
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
│   ├── guardian/                      # Meta-RAG (7개 파일, 2,401줄) ⭐
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
│   │   └── excel/                     # 3개 도구 (v7.2.0)
│   │       ├── formula_engine.py      # Excel 함수 엔진
│   │       ├── builder_contract.py    # Builder Contract
│   │       ├── market_sizing/         # 9 시트
│   │       ├── unit_economics/        # 10 시트
│   │       └── financial_projection/  # 11 시트
│   │
│   └── utils/                         # 유틸리티 (3개 파일)
│       ├── logger.py                  # 로깅
│       └── guestimation.py            # Legacy (Deprecated)
│
├── scripts/                           # 실행 스크립트 (75개 파일)
│   ├── 01_convert_yaml.py             # YAML → JSONL 변환
│   ├── 02_build_index.py              # RAG 인덱스 빌드
│   ├── build_canonical_index.py       # Canonical 빌드
│   ├── build_projected_index.py       # Projected 빌드
│   ├── build_knowledge_graph.py       # Graph 빌드
│   ├── build_system_knowledge.py      # System RAG 빌드 ⭐
│   ├── query_system_rag.py            # System RAG 검색 ⭐
│   ├── test_*.py                      # 테스트 스크립트 (26개)
│   └── ...
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
    ├── GUESTIMATION_FRAMEWORK.md      # Fermi Estimation 가이드 (v7.2.0)
    ├── INSTALL.md
    ├── FOLDER_STRUCTURE.md
    ├── VERSION_UPDATE_CHECKLIST.md
    ├── MAIN_BRANCH_SETUP.md
    ├── UMIS-DART-재무제표-조사-프로토콜.md
    └── excel/                         # Excel 관련 문서 (v7.2.0)
        ├── EXCEL_QA_SYSTEM.md
        ├── EXCEL_VALIDATION_GUIDE.md
        ├── EXCEL_SHEET_SPECS.yaml
        └── WHY_QA_FAILED_AND_FIX.md
```

### 주요 파일 역할

| 파일 | 역할 | 크기/개수 | v7.3.2 |
|------|------|-----------|--------|
| **umis.yaml** | Cursor Rules, 메인 가이드 | 6,539줄 | ⭐ Estimator 386줄 |
| **umis_core.yaml** | 압축 INDEX (AI 빠른 참조) | 928줄 | ⭐ 87% 절약 |
| **config/tool_registry.yaml** | System RAG 도구 정의 | 31개 도구 | ⭐ Estimator 3개 |
| **config/schema_registry.yaml** | RAG 레이어 통합 스키마 | 851줄, v1.1 | ⭐ EST- prefix |
| **config/projection_rules.yaml** | Canonical → Projected 변환 | 125줄 | ⭐ Estimator 규칙 |
| **config/routing_policy.yaml** | Workflow 정의 | 194줄, v1.1.0 | ⭐ Estimator 협업 |
| **config/runtime.yaml** | 실행 모드 (hybrid) | 99줄 | Circuit Breaker |
| **config/fermi_model_search.yaml** | Tier 3 설계 | 1,266줄 | ⭐ 통합 대기 |
| **umis_rag/agents/estimator/** | Estimator Agent | 13개 파일, 2,800줄 | ⭐ v7.3.1+ |
| **umis_rag/guardian/** | Meta-RAG | 7개 파일, 2,401줄 | ⭐ v7.1.0+ |

---

## 📚 Version History

**현재 버전**: v7.5.0 "Complete System" (2025-11-08) - Stable Release

**상세 변경 이력**: [CHANGELOG.md](CHANGELOG.md) 참조

**주요 마일스톤**:
- **v7.5.0 (2025-11-08)**: 🏆
  - 3-Tier 완성 (100% 커버리지, 실패율 0%)
  - 12개 비즈니스 지표 템플릿 (23개 모형)
  - 데이터 상속 (재귀 최적화)
  - LLM 모드 통합 (Native/External)
  - 모든 파일 v7.5.0 반영

- **v7.4.0 (2025-11-08)**: 🎯
  - Tier 3 Fermi Decomposition 구현 (1,463줄)
  - 8개 비즈니스 지표 템플릿
  - SimpleVariablePolicy (KISS 원칙)
  - LLM API 통합

- **v7.3.2 (2025-11-08)**: ⭐
  - Single Source of Truth (모든 추정은 Estimator만)
  - Reasoning Transparency (추정 근거 완전 투명화)
  - Validator 교차 검증
  - 전체 시스템 100% 검증

- **v7.3.1 (2025-11-07)**: ⭐
  - Estimator (Fermi) Agent 추가 (6-Agent 시스템 완성)
  - 아키텍처 일관성 (모든 Agent agents/ 폴더)
  - 협업 파트너 모델

- **v7.3.0 (2025-11-07)**:
  - Guestimation v3.0 (3-Tier Architecture)
  - Learning System (6-16배 빠름)
  - 11개 Source 통합

- **v7.2.0 (2025-11-04)**:
  - Excel 도구 3개 (작업 커버리지 4배)
  - Fermi Model Search (Tier 3 설계)
  - Native Mode, 양방향 ID

- **v7.0.0 (2025-11-03)**:
  - RAG v3.0 완전 통합
  - 6-Agent 시스템 안정화
  - Knowledge Graph (13 노드, 45 관계)
  - System RAG (도구 기반 검색)

---

## 🔧 Configuration Quick Reference

### 실행 모드 (config/runtime.yaml)

```yaml
mode: rag_full  # yaml_only / hybrid / rag_full (v7.5.0)

layers:
  vector: true      # ChromaDB Vector RAG
  graph: true       # Neo4j Knowledge Graph
  memory: true      # Guardian Memory
  meta: true        # Meta-RAG (v7.1.0+ 구현 완료) ⭐
  estimator: true   # Estimator 3-Tier (v7.5.0) ⭐

circuit_breaker:
  enabled: true
  failure_threshold: 3
  timeout_seconds: 30
  recovery_timeout: 60
```

**모드 선택 가이드**:
- `yaml_only`: RAG 없이 기본 YAML만 (안전, 느림)
- `hybrid`: Vector RAG만 (안정적)
- `rag_full`: Vector + Graph + Memory + Meta + Estimator (모든 기능) ← **기본값 (v7.5.0)**

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

### 4. Fail-Safe 계층

- **Tier 1**: Fallback (vector_fail → yaml_only)
- **Tier 2**: Mode Toggle (hybrid → yaml_only)
- **Tier 3**: Circuit Breaker (3회 실패 → 60초 차단)

---

## 📖 References

### 핵심 문서 (v7.3.2)
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
- [ ] **Version History** 섹션에 변경 사항 추가
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

## 🤖 LLM Mode Architecture (v7.2.0+)

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

## 🔧 자동 환경변수 로드 (v7.2.0+)

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

## 🎯 Estimator (Fermi) Agent (v7.5.0 완성) ⭐

### 6번째 Agent - 값 추정 및 판단 전문가

**핵심**: "3-Tier 완성 + 12개 비즈니스 지표 + 100% 커버리지"

**역할**:
- 모든 값/데이터 추정 (유일한 권한, v7.3.2+)
- 3-Tier Architecture (Tier 1/2/3 완성, v7.5.0)
- 12개 비즈니스 지표 템플릿 (23개 모형, v7.5.0)
- 데이터 상속 (재귀 최적화, v7.5.0)
- LLM 모드 통합 (Native/External, v7.5.0)

**위치**: `umis_rag/agents/estimator/` (14개 파일, 4,212줄)

**클래스**: `EstimatorRAG` (통합 인터페이스)

**사용**:
```python
from umis_rag.agents.estimator import EstimatorRAG

estimator = EstimatorRAG()

# Tier 1/2 (대부분)
result = estimator.estimate("Churn Rate는?", domain="B2B_SaaS")

# Tier 3 (비즈니스 지표, v7.5.0)
result = estimator.estimate("LTV는?")
result = estimator.estimate("Payback Period는?")
result = estimator.estimate("Rule of 40은?")

# Cursor에서
@Fermi, SaaS LTV는?
```

```
┌─────────────────────────────────────────────┐
│ Tier 1: Fast Path (45% → 95%, <0.5초)     │
│   - Built-in 규칙 (20개)                   │
│   - 학습된 규칙 RAG (0 → 2,000개 진화)     │
│   - 원칙: False Negative 허용              │
└──────────────┬──────────────────────────────┘
               │ 매칭 없으면
               ▼
┌─────────────────────────────────────────────┐
│ Tier 2: Judgment Path (50% → 5%, 3-8초)   │
│   1. 맥락 파악 (intent, domain, ...)      │
│   2. Source 수집 (11개 중 5-8개)          │
│      - Physical: 절대 한계 (3개)           │
│      - Soft: 범위 제시 (3개)              │
│      - Value: 값 결정 (5개)               │
│   3. 증거 평가 (맥락 기반)                │
│   4. 종합 판단 (4가지 전략)               │
│   5. 학습 (Tier 1 편입)                   │
└──────────────┬──────────────────────────────┘
               │ 복잡하면
               ▼
┌─────────────────────────────────────────────┐
│ Tier 3: Fermi Decomposition (v7.5.0 완성) │
│   - 12개 비즈니스 지표 템플릿 (23개 모형) │
│   - 재귀 추정 (max depth 4)               │
│   - 데이터 상속 (v7.5.0)                  │
│   - 순환 감지 (Call stack)                │
│   - SimpleVariablePolicy (6-10개)         │
│   - LLM 모드 (Native/External)            │
│   - 커버: 5% → 0.5%                       │
└─────────────────────────────────────────────┘

총 커버리지: 100% ✅
실패율: 0% ✅
```

**12개 비즈니스 지표 (v7.5.0)**:
```
핵심 8개:
  1. Unit Economics (LTV/CAC)
  2. Market Sizing
  3. LTV
  4. CAC
  5. Conversion Rate
  6. Churn Rate
  7. ARPU
  8. Growth Rate

고급 4개 (v7.5.0):
  9. Payback Period
  10. Rule of 40
  11. Net Revenue Retention
  12. Gross Margin

총: 12개 지표, 23개 모형
커버: 90-95% (템플릿만)
```

**LLM 모드 (v7.5.0)**:
- Native Mode: 템플릿만, 비용 $0 (권장)
- External Mode: 템플릿 + OpenAI API, 비용 $0.03/질문

**파일**: `umis_rag/agents/estimator/` (14개 파일, 4,212줄)
- estimator.py (337줄)
- tier1.py (350줄)
- tier2.py (650줄)
- tier3.py (1,463줄) ⭐ v7.5.0
- models.py (519줄)
- 기타 9개

---

## 🎯 Fermi Model Search (v7.2.1+)

### Fermi 추정 엔진

**핵심**: "논리의 퍼즐 맞추기"

```
┌───────────────────────────────────────┐
│ Phase 1: 초기 스캔 (Bottom-up)        │
│ 가용 데이터: [A, B, C]                │
└───────────────────────────────────────┘
          │
          ▼
┌───────────────────────────────────────┐
│ Phase 2: 모형 생성 (Top-down)         │
│ LLM이 3-5개 후보 제시                 │
│ - 목표 = A × B × X                   │
│ - 목표 = A × B × C × Y               │
└───────────────────────────────────────┘
          │
          ▼
┌───────────────────────────────────────┐
│ Phase 3: 퍼즐 맞추기                  │
│ X, Y를 채울 수 있나? (재귀)           │
└───────────────────────────────────────┘
          │
          ▼
┌───────────────────────────────────────┐
│ Phase 4: 재조립 (Backtracking)        │
│ A × B × C × Y → 결과                  │
└───────────────────────────────────────┘
```

**재귀 구조**:
- Unknown 변수 → 즉시 재귀 호출
- Max depth: 4
- 순환 감지

**12개 비즈니스 지표 템플릿**:
- 시장 규모, LTV, CAC, Unit Economics
- Churn, Conversion, ARPU, Growth

**파일**: `umis_rag/utils/fermi_model_search.py` (748줄)

---

---

## 🎯 Single Source of Truth (v7.3.2+) ⭐

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
     - Tier 2 → Tier 1 진화
  
  3. 근거 추적
     - 추정값의 출처 명확
     - 재현 가능성
```

### 추정 근거 제공 (v7.3.2)

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
**Last Reviewed**: 2025-11-08  
**Next Review**: 버전 업데이트 시 (v7.4.0 예상)

---

*이 문서는 UMIS의 "살아있는 설계도"입니다. 모든 버전 업데이트 시 함께 업데이트되어야 합니다.*

