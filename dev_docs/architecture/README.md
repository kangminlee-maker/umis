# UMIS RAG Architecture v3.0

**목적**: RAG v3.0 아키텍처 설계 문서 모음  
**버전**: v3.0  
**최종 업데이트**: 2025-11-03  
**상태**: Production (v7.0.0 적용됨)

---

## 📌 Architecture v3.0 개요

UMIS RAG는 **16개 개선안**을 통해 v3.0으로 진화했습니다.

**핵심 특징**:
- Dual-Index (Canonical + Projected)
- Knowledge Graph (Neo4j)
- Multi-Dimensional Confidence
- Projection Learning (90% 규칙 + 10% LLM)
- Overlay Layer (core/team/personal)
- Fail-Safe 3단계
- ID Namespace & Lineage
- Anchor Path + Content Hash

---

## 📁 폴더 구조

```
dev_docs/architecture/
├── README.md                    # 이 파일
│
├── 컴포넌트별 설계 (10개)
│   ├── 01_projection/           # Projection 메커니즘
│   ├── 02_schema_registry/      # Schema Registry
│   ├── 03_routing_yaml/         # Routing Policy
│   ├── 04_graph_confidence/     # Graph Confidence
│   ├── 05_rae_index/            # RAE Index
│   ├── 06_overlay_layer/        # Overlay Layer
│   ├── 07_fail_safe/            # Fail-Safe
│   ├── 08_system_rag/           # System RAG + Meta Index
│   ├── 09_id_lineage/           # ID & Lineage
│   └── 10_anchor_hash/          # Anchor Hash
│
├── 지원 폴더 (4개)
│   ├── versions/                # 아키텍처 버전들
│   │   ├── COMPLETE_ARCHITECTURE_V3.md
│   │   ├── umis_rag_architecture_v3.0.yaml
│   │   ├── umis_rag_architecture_v1.0.yaml
│   │   └── umis_rag_architecture_v1.1_enhanced.yaml
│   │
│   ├── expert_feedback/         # 전문가 피드백
│   │   ├── QA_RESULTS.md
│   │   ├── SYSTEM_QA_V2.md
│   │   ├── EXPERT_FEEDBACK_ADOPTION.md
│   │   └── EXPERT_FEEDBACK_V2_ANALYSIS.md
│   │
│   ├── planning/                # 계획 문서
│   │   ├── ARCHITECTURE_IMPROVEMENTS_CHECKLIST.md
│   │   ├── IMPLEMENTATION_ROADMAP_V2.md
│   │   └── IMMEDIATE_ACTIONS.md
│   │
│   └── cursorrules/             # Cursor Rules 설계
│       ├── CURSORRULES_COMPLETION_CHECK.md
│       ├── NAME_BINDING_DESIGN.md
│       └── TERMINOLOGY_STANDARD.md
```

---

## 🎯 주요 문서

### 전체 아키텍처

#### versions/COMPLETE_ARCHITECTURE_V3.md
**RAG v3.0 완성본**

**내용**:
- 16개 개선안 전체
- 컴포넌트 간 관계
- 구현 우선순위
- P0/P1 분류

#### versions/umis_rag_architecture_v3.0.yaml
**구조화된 스펙**

**내용**:
- YAML 형식 스펙
- 각 컴포넌트 정의
- Field 스키마

---

### 컴포넌트별 설계 (10개)

#### 01_projection/
**Projection 메커니즘**
- Canonical → Projected 변환
- 90% 규칙 + 10% LLM 학습
- 관련 파일: `config/projection_rules.yaml`

**주요 문서**:
- FINAL_DECISION.md
- IMPLEMENTATION_PLAN.md
- EXPERT_FEEDBACK.md

#### 02_schema_registry/
**Schema Registry**
- RAG 레이어 통합 스키마
- ID Namespace
- Validation Rules
- 관련 파일: `config/schema_registry.yaml`

#### 03_routing_yaml/
**Routing Policy**
- Explorer Workflow 4단계
- Layer 라우팅
- Intent 기반 검색
- 관련 파일: `config/routing_policy.yaml`

#### 04_graph_confidence/
**Multi-Dimensional Confidence**
- similarity (vector, 질적)
- coverage (distribution, 양적)
- validation (checklist, 검증)
- overall (종합 신뢰도 0-1)

#### 05_rae_index/
**RAE Index**
- Guardian 평가 재사용
- 일관성 보장
- 평가 메모리

#### 06_overlay_layer/
**Overlay Layer**
- core / team / personal
- 검색 순서 및 병합
- Promotion Workflow
- 관련 파일: `config/overlay_layer.yaml`

#### 07_fail_safe/
**Fail-Safe 3단계**
- Tier 1: Fallback
- Tier 2: Mode Toggle
- Tier 3: Circuit Breaker
- 관련 파일: `config/runtime.yaml`

#### 08_system_rag/
**System RAG**
- System Knowledge RAG (향후)
- Tool Registry (향후)
- META_INDEX_DESIGN.md 포함

#### 09_id_lineage/
**ID & Lineage**
- ID Namespace (CAN-, PRJ-, GND-, ...)
- Lineage 추적
- Evidence & Provenance

#### 10_anchor_hash/
**Anchor Path + Content Hash**
- 재현성 보장
- line_range 대체
- 안정적 참조

---

### 지원 문서

#### versions/
**아키텍처 버전 관리**
- v1.0, v1.1, v3.0 스펙
- 버전별 진화 과정
- COMPLETE_ARCHITECTURE_V3.md (통합 문서)

#### expert_feedback/
**전문가 피드백 및 QA**
- P0 개선안 7개 채택
- 전문가 피드백 분석
- QA 결과

#### planning/
**구현 계획**
- ARCHITECTURE_IMPROVEMENTS_CHECKLIST (16개 개선안)
- IMPLEMENTATION_ROADMAP_V2
- IMMEDIATE_ACTIONS

#### cursorrules/
**Cursor Rules 설계**
- NAME_BINDING_DESIGN
- TERMINOLOGY_STANDARD
- CURSORRULES_COMPLETION_CHECK

---

## 🔄 개발 타임라인

### Phase 1: 초기 설계 (v1.0)
- 기본 RAG 구조
- Single Index

### Phase 2: 강화 (v1.1)
- Dual-Index 설계
- 개선안 도출

### Phase 3: 완성 (v3.0)
- 16개 개선안 통합
- P0 7개 우선 구현
- Production 적용

---

## 📖 참조

### 실제 구현
- **[../../config/schema_registry.yaml](../../config/schema_registry.yaml)** - RAG 스키마 (v1.0)
- **[../../config/projection_rules.yaml](../../config/projection_rules.yaml)** - Projection 규칙
- **[../../config/routing_policy.yaml](../../config/routing_policy.yaml)** - Routing Policy
- **[../../config/pattern_relationships.yaml](../../config/pattern_relationships.yaml)** - KG 관계

### 전체 시스템
- **[../../UMIS_ARCHITECTURE_BLUEPRINT.md](../../UMIS_ARCHITECTURE_BLUEPRINT.md)** - 시스템 전체 구조

### 개발 히스토리
- **[../dev_history/](../dev_history/)** - 주차별 개발 기록
- **[../dev_history/DEVELOPMENT_TIMELINE.md](../dev_history/DEVELOPMENT_TIMELINE.md)** - 전체 타임라인

---

## 🎓 학습 순서

### 신규 학습자
1. **versions/COMPLETE_ARCHITECTURE_V3.md** - 전체 개요 파악
2. **01_projection/** ~ **10_anchor_hash/** - 컴포넌트별 이해
3. **expert_feedback/** - 설계 의도 파악
4. **../../config/** - 실제 구현 확인

### 기여자
1. **planning/** - 향후 계획 파악
2. **versions/** - 버전 진화 이해
3. 특정 컴포넌트 폴더 - 상세 설계 확인

---

## ⚠️ 주의사항

이 폴더의 문서들은:
- ✅ 설계 과정 및 의사결정 기록
- ✅ 아키텍처 학습 자료
- ✅ 향후 개발 참조
- ❌ **시스템 동작과 무관** (실제 코드는 `../../umis_rag/`)

---

**작성일**: 2025-11-03  
**상태**: 정리 완료 (모든 루트 파일을 적절한 서브폴더로 이동)
