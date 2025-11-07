# UMIS Configuration Files

**목적**: 모든 UMIS 설정 파일 중앙 관리  
**버전**: v7.3.2

---

## 📁 Config 파일 (12개)

```
config/
├── README.md                  # 이 파일
├── agent_names.yaml           # Agent 이름 커스터마이징 (6-Agent)
├── schema_registry.yaml       # RAG 레이어 통합 스키마 ⭐
├── pattern_relationships.yaml # Knowledge Graph 관계 정의 ⭐
├── projection_rules.yaml      # Canonical → Projected 변환 규칙 (Estimator 포함)
├── routing_policy.yaml        # Workflow 정의 (Estimator 협업)
├── runtime.yaml               # 실행 모드 설정
├── overlay_layer.yaml         # Overlay 레이어 (core/team/personal)
├── llm_mode.yaml              # LLM 모드 설정 (Native/External)
├── tool_registry.yaml         # System RAG 도구 레지스트리 (31개) ⭐
├── tool_registry_sample.yaml  # 도구 레지스트리 샘플
└── fermi_model_search.yaml    # Tier 3 Fermi 로직 (통합 대기) ⭐
```

**⭐ v7.3.2 업데이트**: Estimator Agent 반영

---

## 📋 파일별 설명

### agent_names.yaml (Agent 이름 매핑)
**목적**: Agent 이름 커스터마이징

```yaml
observer: Albert    # 기본
explorer: Steve

# 변경 예시
explorer: Alex      # 1줄만 수정!
```

**사용**:
- `"@Alex, 기회 찾아봐"` → Explorer 실행
- 양방향 매핑 (입력/출력)

**참고**: [../UMIS_ARCHITECTURE_BLUEPRINT.md](../UMIS_ARCHITECTURE_BLUEPRINT.md) - Agent System

---

### schema_registry.yaml (RAG 스키마) ⭐
**목적**: RAG 레이어 통합 스키마 정의

**크기**: 845줄  
**버전**: v1.0  
**RAG Architecture**: v3.0

**내용**:
- ID 네임스페이스 (CAN-, PRJ-, GND-, GED-, MEM-, RAE-)
- Core Fields (모든 Collection 공통)
- Layer 1: Canonical Index
- Layer 1: Projected Index
- Layer 3: Knowledge Graph
- Layer 4: Memory
- RAE Index
- Field Mappings
- Validation Rules

**참고**: [../UMIS_ARCHITECTURE_BLUEPRINT.md](../UMIS_ARCHITECTURE_BLUEPRINT.md) - 4-Layer RAG

---

### pattern_relationships.yaml (Knowledge Graph 관계) ⭐
**목적**: Knowledge Graph 패턴 간 관계 정의

**크기**: 1,566줄  
**총 관계**: 45개

**내용**:
- Business Model 조합 (15개)
- Disruption + Business Model (15개)
- Disruption 간 관계 (10개)
- 전략적 관계 (5개)

**관계 유형**:
- COMBINES_WITH: 함께 사용 시 시너지
- COUNTERS: 약점 보완
- PREREQUISITE: 선행 조건
- ENABLES: 가능하게 함

**사용**: scripts/build_knowledge_graph.py에서 Neo4j 구축

---

### overlay_layer.yaml (Overlay 레이어)
**목적**: 3-Layer 데이터 관리 (core/team/personal)

**상태**: `enabled: false` (1인 개발)

**내용**:
- Layer 정의 (core/team/personal)
- 검색 순서 (personal > team > core)
- Merge 전략 (append/replace/patch)
- Promotion Workflow
- ACL (접근 제어)

**활성화**: 팀 3명+ 확장 시

---

### projection_rules.yaml (Projection 규칙)
**목적**: Canonical → Projected 변환 규칙 (90% 커버리지)

**크기**: 125줄  
**규칙 개수**: 15개 + Estimator 규칙

**내용**:
- 필드별 Agent 매핑
  ```yaml
  business_model → [explorer]
  trigger_observations → [observer, explorer]
  churn_rate → [explorer, quantifier, guardian]
  ```
- 패턴별 기본 매핑
- **v7.3.1+: Estimator Learned Rule 규칙**
  ```yaml
  learned_rule:
    target_agents: [estimator]
    strategy: "direct_projection"
    ttl: "persistent"
  ```
- LLM 학습 설정 (3회 일관성 → 규칙화)

**학습**: 10% LLM 판단 → 로그 → 자동 규칙 추가

---

### routing_policy.yaml (워크플로우 라우팅)
**목적**: Explorer Workflow 정의 및 Layer 라우팅 정책

**크기**: 194줄  
**v7.3.2**: Estimator 협업 추가

**내용**:
- Explorer Workflow (5단계)
  1. pattern_search (vector + graph)
  2. case_search (vector)
  3. **estimator_collaboration (조건부) ⭐ v7.3.2**
  4. quantifier_collaboration (조건부)
  5. hypothesis_generation (vector + memory)
- Layer Toggle (vector/graph/memory)
- Retrieval Policy (Intent 기반)
- Fallback Policy
- **needs_estimation 조건 추가**

---

### runtime.yaml (실행 모드)
**목적**: RAG 실행 환경 설정

**크기**: 99줄

**내용**:
- Mode: `hybrid` (yaml_only/hybrid/rag_full)
- Layer 활성화 (vector: true, graph: true, memory: true)
- Circuit Breaker (Fail-Safe Tier 3)
  - failure_threshold: 3
  - timeout: 30초
  - recovery: 60초
- Performance (cache, concurrency)

---

## 🔄 파일 간 관계

```
runtime.yaml (실행 모드)
  ↓ Mode: hybrid
  ↓ Layers: vector, graph, memory

routing_policy.yaml (워크플로우)
  ↓ Explorer Workflow 4단계
  ↓ Layer 라우팅

projection_rules.yaml (변환)
  ↓ Canonical → Projected
  ↓ 90% 규칙 + 10% LLM

schema_registry.yaml (스키마)
  ↓ 모든 Layer 정의
  ↓ Validation Rules

overlay_layer.yaml (데이터 관리)
  ↓ core/team/personal
  ↓ 검색 순서

agent_names.yaml (사용자 UI)
  ↓ Agent 이름 매핑
```

---

## 🎯 사용 가이드

### 설정 확인
```bash
# 현재 실행 모드
cat config/runtime.yaml | grep "mode:"

# Agent 이름
cat config/agent_names.yaml

# Projection 규칙
cat config/projection_rules.yaml
```

### 설정 변경
```bash
# Agent 이름 변경
vim config/agent_names.yaml
# explorer: Steve → Alex 수정

# 실행 모드 변경
vim config/runtime.yaml
# mode: hybrid → rag_full
```

### 설정 검증
```bash
# 스키마 계약 테스트
python scripts/test_schema_contract.py

# RAG 빌드 (설정 적용)
python scripts/02_build_index.py --agent explorer
```

---

## ⚠️ 주의사항

### 수정 시 영향
- `agent_names.yaml`: 즉시 반영 (재빌드 불필요)
- `runtime.yaml`: 재시작 필요
- `projection_rules.yaml`: RAG 재빌드 필요
- `schema_registry.yaml`: RAG 재빌드 + 검증 필요
- `routing_policy.yaml`: 재시작 필요
- `overlay_layer.yaml`: 재시작 필요

### 백업 권장
```bash
# 설정 변경 전 백업
cp -r config/ config.backup/
```

---

## 🔗 관련 문서

- **[../UMIS_ARCHITECTURE_BLUEPRINT.md](../UMIS_ARCHITECTURE_BLUEPRINT.md)** - Configuration Reference
- **[../dev_docs/architecture/](../dev_docs/architecture/)** - 아키텍처 설계 문서
- **[../VERSION_UPDATE_CHECKLIST.md](../VERSION_UPDATE_CHECKLIST.md)** - 버전 업데이트 시 설정 변경

---

### tool_registry.yaml (도구 레지스트리) ⭐
**목적**: System RAG Key-based 도구 정의

**크기**: 1,710줄  
**도구 개수**: 31개 (v7.3.2)

**내용**:
- Explorer 도구 (4개): pattern_search, 7_step_process, validation_protocol, hypothesis_generation
- Quantifier 도구 (4개): sam_4methods, growth_analysis, scenario_planning, benchmark_analysis
- Validator 도구 (4개): data_definition, creative_sourcing, gap_analysis, source_verification
- Observer 도구 (4개): market_structure, value_chain, inefficiency_detection, disruption_opportunity
- Guardian 도구 (2개): progress_monitoring, quality_evaluation
- **Estimator 도구 (3개) ⭐ v7.3.1+**: estimate, cross_validation, learning_system
- Framework 도구 (7개): 13_dimensions, discovery_sprint, 7_powers, counter_positioning, etc.
- Universal 도구 (3개): guestimation (Deprecated), domain_reasoner, hybrid_strategy

**사용**: System RAG에서 tool_key로 정확 검색

---

### fermi_model_search.yaml (Tier 3 설계) ⭐
**목적**: Estimator Tier 3 (Fermi Decomposition) 로직 정의

**크기**: 1,258줄  
**상태**: ✅ 설계 완료, 통합 대기

**내용**:
- Phase 1-4: 모형 탐색 프로세스
- 재귀 추정 (Recursive Guestimation)
- 모형 선택 기준
- 비즈니스 지표 예시

**⚠️ Deprecated 아님!**
- Tier 3 구현을 위한 설계 문서
- v7.3.2 현재: Tier 1/2만 구현
- Tier 3는 통합 대기 (준비 완료)

**통합 대상**: umis_rag/agents/estimator/tier3.py (미래)

---

**구조 개선**: 2025-11-03  
**v7.3.2 업데이트**: 2025-11-08  
**통합**: 12개 config 파일을 config/ 폴더로 중앙 관리

