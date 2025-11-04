# UMIS Architecture Blueprint
**Universal Market Intelligence System - 시스템 설계도**

---

## 📌 Version Info

| Item | Value |
|------|-------|
| **UMIS Version** | v7.2.0 "Fermi" |
| **RAG Architecture** | v3.0 |
| **Excel Engine** | v1.0 (Phase 1 완료) |
| **Guestimation Framework** | v2.0 |
| **Schema Registry** | v1.0 |
| **Last Updated** | 2025-11-04 |
| **Status** | Stable Release |

**Purpose**: UMIS 전체 구조와 기능을 한눈에 파악할 수 있는 고수준 설계도

---

## 🎯 System Overview

### What is UMIS?
시장 분석을 위한 **5-Agent 협업 시스템** + **Multi-Layer RAG 아키텍처** + **Excel 자동 생성**

### Key Characteristics
- ✅ **5명의 전문 에이전트** 역할 분담 및 상호 검증
- ✅ **RAG 기반 지식 활용** (54개 패턴/사례 DB)
- ✅ **Excel 자동 생성** (Market Sizing, Unit Economics, Financial Projection)
- ✅ **Guestimation Framework** (Fermi Estimation, 8개 데이터 출처)
- ✅ **완전한 추적성** (모든 결론 → 원본 데이터 역추적, 양방향 ID)
- ✅ **재검증 가능** (Excel 함수 100%, Named Range, YAML 스키마)
- ✅ **학습 가능** (LLM 판단 → 자동 규칙화)
- ✅ **구조 독립성** (Builder Contract, Inline Validation)

### Quick Start

**설치**: [INSTALL.md](docs/INSTALL.md) 참조 (AI 자동 / 스크립트 / 수동)

**사용**:
```
Cursor Composer (Cmd+I):
"@Explorer, 시장 분석해줘"
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
│       └─────────────┴─────────────┴─────────────┘                  │
│                          │                                          │
│                     ┌────▼────┐                                     │
│                     │Guardian │                                     │
│                     │(Stewart)│ ◄── 검증 & 메타 관리                │
│                     └─────────┘                                     │
│                                                                     │
│  산출물:                                                            │
│  - market_reality_report.md (Albert)                               │
│  - OPP_*.md (Steve)                                                │
│  - market_sizing.xlsx (Bill)                                       │
│  - source_registry.yaml (Rachel)                                   │
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

### 1. 5-Agent System (Business Layer)

#### Agent 역할 및 산출물

| Agent ID | Name (기본) | Role | 산출물 | 검증자 |
|----------|------------|------|--------|--------|
| **observer** | Albert | 시장 구조 분석 | market_reality_report.md | quantifier, validator, guardian |
| **explorer** | Steve | 기회 발굴 (RAG) | OPP_*.md | observer, quantifier, validator |
| **quantifier** | Bill | 정량 분석 + Excel 생성 | market_sizing.xlsx (10 sheets)<br>unit_economics.xlsx (10 sheets)<br>financial_projection.xlsx (11 sheets) | validator, observer |
| **validator** | Rachel | 데이터 검증 | source_registry.yaml | - (검증자) |
| **guardian** | Stewart | 프로세스 관리 | .project_meta.yaml, deliverables_registry.yaml | - (메타 관리자) |

**핵심**: 
- **Agent ID 불변** (observer, explorer, ...) → 폴더/파일 경로
- **Name 변경 가능** (config/agent_names.yaml) → 사용자 UI
- **상호 검증** (각 산출물 2-3명 검증)

#### 데이터 흐름 (순차적 의존성)

```
Rachel (Validator)
  ↓ SRC_YYYYMMDD_NNN
  │ source_registry.yaml
  │ - SRC_20241031_001: "피아노 시장 1,500억"
  │ - 신뢰도 평가 (0-100)
  │ - Definition Gap 분석
  │
Bill (Quantifier)
  ↓ SAM 계산
  │ market_sizing.xlsx
  │ - Assumptions: SRC_ID 참조
  │ - Estimation_Details: EST_NNN (추정 논리 7단계 문서화)
  │ - 4가지 Method → Convergence (±30%)
  │ - 결과: SAM 270억 ± 30억
  │
Albert (Observer)
  ↓ 시장 구조 분석
  │ market_reality_report.md
  │ - 모든 주장에 SRC_ID 또는 Bill 계산 참조
  │ - 가치사슬 맵
  │ - 비효율성 정량화 (Bill 협업)
  │
Steve (Explorer)
  ↓ 기회 가설
  │ OPP_*.md
  │ - Albert 분석 참조
  │ - Bill SAM 참조
  │ - Rachel SRC_ID 참조
  │ - 3명 검증 (Albert, Bill, Rachel)
  │ - 우선순위 자동 계산 (5개 차원)
  │
Stewart (Guardian)
  │ .project_meta.yaml (프로젝트 진행 추적)
  │ deliverables_registry.yaml (산출물 자동 등록)
  └─ 검증 상태 집계, 품질 평가
```

### 2. 5-Layer RAG Architecture (Data Layer)

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

Layer 1: Projected Index (PRJ-*)
  목적: Agent별 검색용 Materialized View
  전략: on_demand (TTL 24h) → 고빈도면 persistent
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

Layer 4: Memory (MEM-*)
  Query Memory: 순환 감지 (repetition_count)
  Goal Memory: 목표 정렬 (alignment_score)

RAE Index (RAE-*)
  목적: Guardian 평가 재사용 (일관성)
  예시:
    rae_id: "RAE-eval-001"
    deliverable_id: "OPP-001"
    grade: "A"
    rationale: "구조적 실현성 높음, 근거 충분"
    evidence_ids: ["CAN-1234", "PRJ-5678"]
    scorer_profile: "weighted"
```

### 3. ID Namespace System (양방향 추적)

모든 데이터 요소는 고유 ID를 가지며, **양방향 추적 가능**

| Prefix | 의미 | 예시 | Collection/파일 |
|--------|------|------|----------------|
| **SRC-** | Rachel 데이터 출처 | SRC_20241031_001 | source_registry.yaml |
| **EST-** | Bill 추정치 | EST_001 | market_sizing.xlsx (Estimation_Details) |
| **ASM-** | Bill 가정 | ASM_001 | market_sizing.xlsx (Assumptions) |
| **OPP-** | Steve 기회 가설 | OPP_20241031_001 | OPP_*.md |
| **DEL-** | 산출물 | DEL_20241031_001 | deliverables_registry.yaml |
| **CAN-** | Canonical 청크 | CAN-baemin-001 | canonical_index (ChromaDB) |
| **PRJ-** | Projected 청크 | PRJ-baemin-exp-001 | projected_index (ChromaDB) |
| **GND-** | Graph 노드 | GND-platform-001 | Neo4j Node |
| **GED-** | Graph 간선 | GED-plat-sub-001 | Neo4j Edge |
| **MEM-** | Memory | MEM-query-001 | query_memory, goal_memory |
| **RAE-** | RAE 평가 | RAE-eval-001 | rae_index (ChromaDB) |
| **tool:** | System RAG 도구 | tool:universal:guestimation | tool_registry.yaml → System RAG |

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

### Explorer Workflow (4단계)

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
Step 3: quantifier_collaboration (조건부)
  Condition: needs_quantitative
  Evaluate: pattern.type == "market_sizing_required" → False
  → Skip
  ↓
Step 4: hypothesis_generation
  Layers: [vector, memory]
  Input: [patterns, cases, quantifier_data=None]
  Memory Check: query_memory (순환 감지)
  
  Generate: hypothesis = {
    title: "피아노 구독 서비스",
    pattern: "subscription_model",
    evidence: [Netflix 사례, Spotify 사례],
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
├── umis.yaml                          # 메인 가이드 (Cursor Rules) - 5,747줄
├── umis_core.yaml                     # 압축 INDEX (AI 빠른 참조) - 709줄
├── umis_deliverable_standards.yaml   # 산출물 표준
├── umis_examples.yaml                 # 사용 예시
├── config/agent_names.yaml            # Agent 이름 커스터마이징
├── config/tool_registry.yaml          # System RAG 도구 정의 (26개)
├── VERSION.txt                        # v7.2.0
│
├── deliverable_specs/                 # 산출물 스펙 (AI 최적화 YAML)
│   ├── observer/
│   │   └── market_reality_report_spec.yaml      (271줄)
│   ├── explorer/
│   │   └── opportunity_hypothesis_spec.yaml     (750줄) ⭐
│   ├── quantifier/
│   │   └── market_sizing_workbook_spec.yaml     (301줄)
│   ├── validator/
│   │   └── source_registry_spec.yaml            (162줄)
│   └── project/
│       ├── project_meta_spec.yaml               (261줄)
│       └── deliverables_registry_spec.yaml      (194줄)
│
├── umis_deliverable_standards.yaml   # 산출물 표준 (2,876줄)
│
├── config_config/schema_registry.yaml        # RAG 레이어 통합 스키마 (843줄)
├── config/overlay_layer.yaml                  # Overlay 레이어 설정
├── config/routing_policy.yaml                # 워크플로우 라우팅 정책
├── config/runtime.yaml                # 실행 모드 설정
├── config/projection_rules.yaml             # Projection 변환 규칙
├── data/llm_projection_log.jsonl           # LLM 판단 로그
│
├── data/
│   ├── raw/
│   │   ├── umis_business_model_patterns.yaml    # 31개 패턴
│   │   ├── umis_disruption_patterns.yaml        # 23개 패턴
│   │   └── umis_ai_guide.yaml                   # AI 가이드
│   ├── chunks/
│   │   ├── explorer_business_models.jsonl       # 변환된 청크
│   │   └── explorer_disruption_patterns.jsonl
│   ├── chroma/                        # ChromaDB (Vector Indexes)
│   │   ├── canonical_index/
│   │   ├── projected_index/
│   │   ├── query_memory/
│   │   ├── goal_memory/
│   │   └── rae_index/
│   └── config/pattern_relationships.yaml     # 패턴 관계 (Graph)
│
├── scripts/                           # 모든 실행 스크립트 (빌드 + 테스트)
│   ├── 01_convert_yaml.py             # YAML → JSONL 변환
│   ├── 02_build_index.py              # RAG 인덱스 빌드 (통합)
│   ├── build_canonical_index.py       # Canonical 빌드
│   ├── build_projected_index.py       # Projected 빌드
│   ├── build_knowledge_graph.py       # Graph 빌드
│   ├── query_rag.py                   # RAG 쿼리 CLI
│   ├── 03_test_search.py              # 검색 테스트
│   ├── test_neo4j_connection.py       # Neo4j 테스트
│   ├── test_hybrid_explorer.py        # Hybrid Search 테스트
│   ├── test_schema_contract.py        # 스키마 계약 테스트
│   └── test_*.py                      # 기타 테스트 스크립트
│
├── umis_rag/                          # 핵심 패키지 (실제 RAG 코드)
│   ├── core/
│   │   ├── schema.py                  # Pydantic 스키마 정의
│   │   ├── metadata_schema.py         # 메타데이터 스키마
│   │   ├── config.py                  # 설정 관리
│   │   ├── layer_manager.py           # 3-Layer 관리 (Overlay)
│   │   ├── workflow_executor.py       # 워크플로우 실행
│   │   ├── condition_parser.py        # 조건 파싱
│   │   ├── circuit_breaker.py         # Circuit Breaker (Fail-Safe)
│   │   └── error_handler.py           # 에러 핸들링
│   ├── graph/
│   │   ├── schema_initializer.py      # Neo4j 스키마 초기화
│   │   ├── connection.py              # Neo4j 연결
│   │   ├── hybrid_search.py           # Vector + Graph 통합 검색
│   │   └── confidence_calculator.py   # 다차원 신뢰도 계산
│   ├── projection/
│   │   ├── hybrid_projector.py        # 규칙 (90%) + LLM (10%)
│   │   └── ttl_manager.py             # TTL 캐싱 관리
│   ├── guardian/
│   │   ├── memory.py                  # Guardian 메모리
│   │   ├── query_memory.py            # Query Memory (순환 감지)
│   │   ├── goal_memory.py             # Goal Memory (목표 정렬)
│   │   ├── rae_memory.py              # RAE Memory (평가 재사용)
│   │   ├── meta_rag.py                # Meta-RAG
│   │   └── three_stage_evaluator.py   # 3단계 평가
│   ├── learning/
│   │   └── rule_learner.py            # LLM 로그 → 규칙 학습
│   ├── agents/
│   │   ├── explorer.py                # Explorer 에이전트 구현
│   │   ├── quantifier.py              # Quantifier 에이전트
│   │   ├── validator.py               # Validator 에이전트
│   │   ├── observer.py                # Observer 에이전트
│   │   └── guardian.py                # Guardian 에이전트
│   ├── deliverables/
│   │   └── excel/                     # Excel 자동 생성 시스템 (v7.2.0)
│   │       ├── formula_engine.py      # Excel 함수 엔진
│   │       ├── builder_contract.py    # Builder Contract 시스템
│   │       ├── assumptions_builder.py
│   │       ├── method_builders.py     # 4-Method SAM
│   │       ├── market_sizing/         # Market Sizing (10 시트)
│   │       ├── unit_economics/        # Unit Economics (10 시트)
│   │       └── financial_projection/  # Financial Projection (11 시트)
│   └── utils/
│       ├── logger.py                  # 로깅
│       └── guestimation.py            # Guestimation Engine (v7.2.0)
│
├── dev_docs/                          # RAG 개발 문서 (시스템 비의존)
│   ├── README.md
│   ├── architecture/                  # RAG v3.0 아키텍처 설계
│   ├── dev_history/                   # 주차별 개발 히스토리
│   ├── analysis/                      # 시스템 분석 문서
│   ├── guides/                        # 개발 가이드
│   ├── planning/                      # 계획 문서
│   └── summary/                       # 요약 문서
│
├── projects/                          # 실제 프로젝트 폴더 (Git 제외)
│   ├── README.md
│   ├── market_analysis/               # Legacy 프로젝트
│   │   ├── korean_adult_education_market_2024/
│   │   └── music_streaming_subscription_2024/
│   └── YYYYMMDD_project_name/         # v7.0.0 표준 구조
│       ├── 00_overview/
│       │   ├── .project_meta.yaml     # Stewart 자동 관리
│       │   └── deliverables_registry.yaml
│       └── 02_analysis/
│           ├── validator/             # Agent ID 기반 폴더
│           │   └── source_registry.yaml
│           ├── quantifier/
│           │   └── market_sizing.xlsx
│           ├── observer/
│           │   └── market_reality_report.md
│           └── explorer/
│               └── OPP_*.md
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

| 파일 | 역할 | 비고 |
|------|------|------|
| **umis.yaml** | Cursor Rules, 메인 가이드 | 5,747줄, Guestimation 포함 |
| **umis_core.yaml** | 압축 INDEX (AI 빠른 참조) | 709줄, 컨텍스트 77% 절약 |
| **config/tool_registry.yaml** | System RAG 도구 정의 (26개) | 양방향 ID, 자동 생성 |
| **config/schema_registry.yaml** | RAG 레이어 통합 스키마 | 845줄, v1.0 |
| **config/projection_rules.yaml** | Canonical → Projected 변환 규칙 | 90% 커버리지 |
| **config/routing_policy.yaml** | Explorer Workflow 정의 | 4단계 워크플로우 |
| **config/runtime.yaml** | 실행 모드 (hybrid) | Circuit Breaker 설정 |
| **config/overlay_layer.yaml** | Overlay (core/team/personal) | 현재 비활성 |
| **docs/GUESTIMATION_FRAMEWORK.md** | Fermi Estimation 가이드 | v7.2.0 핵심 방법론 |

---

## 📚 Version History

**현재 버전**: v7.2.0 "Fermi" (2025-11-04) - Stable Release

**상세 변경 이력**: [CHANGELOG.md](CHANGELOG.md) 참조

**주요 마일스톤**:
- **v7.2.0 (2025-11-04)**: 
  - Bill Excel 도구 3개 (작업 커버리지 4배)
  - Guestimation Framework (Fermi Estimation)
  - Named Range 100%, Builder Contract, Inline Validation
  - 양방향 ID 시스템
  - 데이터 검증 (5개 벤치마크)
- v7.0.0: RAG v3.0 완전 통합, 5-Agent 안정화
- v6.3.0-alpha: Projection 메커니즘, Circuit Breaker
- v6.2.0: Agent 산출물 표준화
- v6.0.0: 5-Agent 시스템 확립

---

## 🔧 Configuration Quick Reference

### 실행 모드 (config/runtime.yaml)

```yaml
mode: hybrid  # yaml_only / hybrid / rag_full

layers:
  vector: true   # ChromaDB Vector RAG
  graph: true    # Neo4j Knowledge Graph
  memory: true   # Guardian Memory
  meta: false    # Meta-RAG (미구현)

circuit_breaker:
  enabled: true
  failure_threshold: 3
  timeout_seconds: 30
  recovery_timeout: 60
```

**모드 선택 가이드**:
- `yaml_only`: RAG 없이 기본 YAML만 (안전, 느림)
- `hybrid`: Vector RAG만 (권장, 안정적) ← **기본값**
- `rag_full`: Vector + Graph + Memory (모든 기능, 실험적)

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

### 핵심 문서
- `umis.yaml`: 메인 가이드 (Cursor Rules)
- `config_config/schema_registry.yaml`: RAG 레이어 스키마
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
| 새 Agent 추가 | System Architecture, 5-Agent System, Data Flow |
| 새 RAG Layer 추가 | System Architecture, 5-Layer RAG Architecture |
| 스키마 변경 | Core Concepts, config/schema_registry.yaml 동기화 |
| 새 ID Prefix | ID Namespace System 테이블 |
| Projection 규칙 변경 | Projection Mechanism, config/projection_rules.yaml 동기화 |
| 워크플로우 변경 | Data Flow & Relationships, config/routing_policy.yaml 동기화 |
| 폴더 구조 변경 | Component Map, docs/FOLDER_STRUCTURE.md |

---

**Document Owner**: AI Team  
**Last Reviewed**: 2025-11-04  
**Next Review**: 버전 업데이트 시 (v7.3.0 예상)

---

*이 문서는 UMIS의 "살아있는 설계도"입니다. 모든 버전 업데이트 시 함께 업데이트되어야 합니다.*

