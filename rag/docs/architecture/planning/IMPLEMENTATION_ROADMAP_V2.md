# UMIS RAG 구현 로드맵 v2.0

**버전:** 2.0 (Architecture v2.0 기반)  
**날짜:** 2025-11-02  
**기반:** 8개 개선안 반영

---

## 🎯 전체 구조

### 4-Layer + 6개 횡단 관심사

```yaml
구현 완료 (v7.0.0):
  ✅ Layer 1: Vector RAG (Explorer만)

구현 예정:
  📋 Layer 1: Dual-Index (완전판)
  📋 Layer 2: Guardian Meta-RAG
  📋 Layer 3: Knowledge Graph
  📋 Layer 4: Memory-Augmented
  
  📋 횡단: Schema Registry
  📋 횡단: Routing Policy
  📋 횡단: Fail-Safe
  📋 횡단: Learning Loop
  📋 횡단: Overlay Layer (향후)
  📋 횡단: System RAG (향후)
```

---

## 📋 Phase 1: Core Foundation (2주)

### 우선순위: P0

```yaml
Week 1-2:
  
  1. Dual-Index (5일)
     현재: Pre-Projection (54 chunks)
     목표: Canonical + Projected
     
     작업:
       Day 1-2: Canonical Index 설계 및 구축
       Day 3-4: Hybrid Projection 구현
       Day 5: 테스트 및 통합
     
     산출물:
       • canonical_index/ (정규화 청크)
       • projected_index/ (Agent별 청크)
       • projection_rules.yaml (규칙 90%)
     
     가치:
       품질 유지 + 일관성 보장
  
  2. Schema Registry (3일)
     목표: 중앙 집중 필드 관리
     
     작업:
       Day 1-2: schema_registry.yaml 작성
       Day 3: Contract Tests 구축
     
     산출물:
       • schema_registry.yaml
       • tests/test_schema_contract.py
     
     가치:
       필드 일관성, 버전 안전
  
  3. Routing YAML (2시간!)
     목표: 워크플로우 가시화
     
     작업:
       • routing_policy.yaml (20줄)
       • workflow_executor.py (30줄)
     
     가치:
       가독성, YAML 친화
  
  4. Fail-Safe Tier 1-2 (2일)
     목표: 기본 안정성
     
     작업:
       Day 1: Graceful Degradation (try-except)
       Day 2: runtime_config.yaml + Toggle
     
     가치:
       항상 작동 보장
```

---

## 📋 Phase 2: Advanced Features (2주)

### 우선순위: P0

```yaml
Week 3-4:
  
  1. Knowledge Graph (5일)
     목표: 패턴 조합 발견
     
     작업:
       Day 1: Neo4j 설치 및 설정
       Day 2-3: 패턴 관계 정의 (45개)
       Day 4: Hybrid Graph+Vector 검색
       Day 5: Explorer 통합
     
     산출물:
       • umis_rag/graph/knowledge_graph.py
       • pattern_relationships.yaml
       • 검색 API
     
     가치:
       패턴 조합, 대안 발견
  
  2. Multi-Dimensional Confidence (2일)
     목표: 관계 신뢰도 평가
     
     작업:
       Day 1: Vector Similarity 계산
       Day 2: Coverage + Validation 통합
     
     산출물:
       • confidence_calculator.py
       • verification_criteria.yaml
     
     가치:
       예외 없는 평가 (질적+양적+검증)
  
  3. Circuit Breaker (2일)
     목표: 자동 보호
     
     작업:
       Day 1: Circuit Breaker 구현
       Day 2: 자동 복구 로직
     
     가치:
       무한 재시도 방지, 자동 복구
```

---

## 📋 Phase 3: Intelligence (2주)

### 우선순위: P1

```yaml
Week 5-6:
  
  1. Guardian Memory (5일)
     목표: 순환 감지, 목표 정렬
     
     작업:
       Day 1-2: QueryMemory 구축
       Day 3-4: GoalMemory 구축
       Day 5: Memory-RAG + LLM Hybrid
     
     산출물:
       • umis_rag/guardian/memory.py
       • Memory Collections (2개)
     
     가치:
       프로세스 감시 자동화
  
  2. Learning Loop (3일)
     목표: LLM → 규칙 자동 학습
     
     작업:
       Day 1: LLM 판단 로그 시스템
       Day 2: 패턴 분석 로직
       Day 3: 자동 규칙 생성
     
     산출물:
       • llm_projection_log.jsonl
       • rule_learner.py
     
     효과:
       LLM 10% → 1%, 비용 ↓
```

---

## 📋 Phase 4: Future (향후)

### 우선순위: P2

```yaml
트리거 기반:
  
  1. Overlay Layer
     트리거: 팀 확장 (3명+)
     기간: 2일
     
     작업:
       • team/ 폴더 생성
       • personal/ 폴더 생성
       • layer_priority.yaml
     
     가치:
       협업, 실험 격리
  
  2. System RAG
     트리거: umis.yaml > 10,000줄
     기간: 2주
     
     작업:
       Week 1: Tool Registry + Guidelines 청킹
       Week 2: Guardian Meta-RAG Orchestration
     
     가치:
       컨텍스트 95% 절감
       동적 Workflow
       Universal Deliverables
```

---

## 🎯 즉시 실행 항목 (현재)

### 파일 정리 및 최적화

```yaml
완료:
  ✅ umis_guidelines.yaml → umis.yaml
  ✅ name 필드 제거 (Clean Design)
  ✅ patterns → data/raw/
  ✅ ai_guide → data/raw/
  ✅ .cursorrules 최적화 (40% 압축)
  ✅ architecture/ 폴더 정리

루트 YAML:
  7개 → 4개
  
  • umis.yaml
  • umis_deliverable_standards.yaml
  • umis_examples.yaml
  • agent_names.yaml
```

---

## 📊 전체 타임라인

```yaml
현재 (v7.0.0):
  Vector RAG (Explorer)
  
Phase 1 (2주):
  Dual-Index, Schema, Routing, Fail-Safe

Phase 2 (2주):
  Knowledge Graph, Confidence, Circuit

Phase 3 (2주):
  Guardian Memory, Learning Loop

Phase 4 (향후):
  Overlay, System RAG

총: 6주 핵심 구현
향후: 트리거 기반 활성화
```

---

**관련 문서:**
- ../COMPLETE_ARCHITECTURE_V2.md (전체 설계)
- ../umis_rag_architecture_v2.0.yaml (YAML 스펙)
- ../ARCHITECTURE_IMPROVEMENTS_CHECKLIST.md (체크리스트)

