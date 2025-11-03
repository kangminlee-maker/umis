# UMIS RAG 완전한 아키텍처 v3.0

**버전:** 3.0 (전문가 피드백 반영, 16개 개선안)  
**날짜:** 2025-11-02  
**상태:** 설계 완료 (감사성·재현성 강화)

---

## 🎯 아키텍처 철학

**핵심 원칙:**

```yaml
1. 품질 우선:
   • 검색 품질 > 저장 효율
   • 일관성 > 복잡도
   • 사용자 경험 > 기술적 완벽성

2. 단순성:
   • YAML 중심 (사용자 친화)
   • Cursor 기반 (코딩 불필요)
   • 점진적 복잡화 (필요 시만)

3. 실용성:
   • 오버엔지니어링 방지
   • 가치 있는 것만 구현
   • 미래 준비 (설계는 지금)

4. 안정성:
   • Fail-Safe 다층 방어
   • Layer 독립성
   • 항상 작동 보장

5. 감사성(A):
   • 재현 가능성 (추적 100%)
   • 설명 가능성 (근거 명시)
   • 장기 운영 안전
```

---

## 📊 전체 구조

### 4-Layer + 6개 횡단 관심사

```
┌─────────────────────────────────────────────────────────────┐
│  UMIS RAG Complete Architecture                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Layer 1: Dual-Index Modular RAG                       │ │
│  ├────────────────────────────────────────────────────────┤ │
│  │                                                         │ │
│  │  Canonical Index (업데이트용):                         │ │
│  │    • 정규화 청크 (5,000개)                             │ │
│  │    • Write: 1곳만 (일관성 보장!)                       │ │
│  │    • ID: CAN-xxxxxxxx (네임스페이스)                  │ │
│  │    • anchor_path + content_hash (안정 참조!)          │ │
│  │                                                         │ │
│  │  Projected Index (검색용, Materialized View):          │ │
│  │    • TTL + 온디맨드 (기본 지연 투영!)                 │ │
│  │    • ID: PRJ-xxxxxxxx (네임스페이스)                  │ │
│  │    • Lineage 추적 (CAN → PRJ)                         │ │
│  │    • Read: 품질 우수!                                  │ │
│  │                                                         │ │
│  │  Hybrid Projection (자동 변환):                        │ │
│  │    • 90% projection_rules.yaml                         │ │
│  │    • 10% LLM 판단                                      │ │
│  │    • LLM 로그 → 규칙 학습                             │ │
│  │                                                         │ │
│  └────────────────────────────────────────────────────────┘ │
│                          ↓                                   │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Layer 2: Guardian Meta-RAG                            │ │
│  ├────────────────────────────────────────────────────────┤ │
│  │                                                         │ │
│  │  3-Stage Evaluation:                                    │ │
│  │    Stage 1: Weighted Scoring (빠름, 80%)              │ │
│  │    Stage 2: Cross-Encoder (정밀, 15%)                 │ │
│  │    Stage 3: LLM + RAE Index (최종, 5%)                │ │
│  │                                                         │ │
│  │  RAE Index (평가 메모리) ⭐ 복원!                     │ │
│  │    • grade + rationale + evidence_ids                 │ │
│  │    • 유사 케이스 재사용 (일관성!)                     │ │
│  │    • 평가 학습 효과                                    │ │
│  │                                                         │ │
│  └────────────────────────────────────────────────────────┘ │
│                          ↓                                   │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Layer 3: Knowledge Graph                              │ │
│  ├────────────────────────────────────────────────────────┤ │
│  │                                                         │ │
│  │  Multi-Dimensional Confidence:                          │ │
│  │    • Similarity: Vector 임베딩 (질적)                 │ │
│  │    • Coverage: 분포 분석 (양적)                       │ │
│  │    • Validation: Yes/No (검증)                        │ │
│  │                                                         │ │
│  │  종합 판단: 0-1 숫자 (설명가능성!)                    │ │
│  │                                                         │ │
│  │  Evidence & Provenance ⭐ 신규!                        │ │
│  │    • evidence_ids (근거 추적)                         │ │
│  │    • provenance (reviewer, timestamp)                  │ │
│  │    • ID: GND/GED-xxxxxxxx                             │ │
│  │                                                         │ │
│  └────────────────────────────────────────────────────────┘ │
│                          ↓                                   │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Layer 4: Memory-Augmented                             │ │
│  ├────────────────────────────────────────────────────────┤ │
│  │                                                         │ │
│  │  QueryMemory + GoalMemory:                              │ │
│  │    • 순환 감지 (3회 반복)                             │ │
│  │    • 목표 정렬 (60% 기준)                             │ │
│  │    • Memory-RAG + LLM Hybrid                           │ │
│  │                                                         │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ═══════════════════════════════════════════════════════════ │
│                   횡단 관심사 (Cross-Cutting)                │
│  ═══════════════════════════════════════════════════════════ │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Schema Registry (중앙 집중)                           │ │
│  ├────────────────────────────────────────────────────────┤ │
│  │                                                         │ │
│  │  schema_registry.yaml:                                  │ │
│  │    • 모든 필드 정의                                    │ │
│  │    • Layer 간 매핑                                     │ │
│  │    • 타입 검증                                         │ │
│  │    • 버전 호환성                                       │ │
│  │                                                         │ │
│  │  Contract Tests:                                        │ │
│  │    • Layer 간 호환성 검증                              │ │
│  │    • 배포 시 자동 실행                                 │ │
│  │                                                         │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Routing Policy (워크플로우)                           │ │
│  ├────────────────────────────────────────────────────────┤ │
│  │                                                         │ │
│  │  routing_policy.yaml:                                   │ │
│  │    • 워크플로우 정의                                   │ │
│  │    • Layer 호출 순서                                   │ │
│  │    • 조건 실행 (when)                                  │ │
│  │    • 가독성 우수                                       │ │
│  │                                                         │ │
│  │  WorkflowExecutor (~30줄):                             │ │
│  │    • YAML 파싱 및 실행                                 │ │
│  │                                                         │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Fail-Safe System (안정성)                             │ │
│  ├────────────────────────────────────────────────────────┤ │
│  │                                                         │ │
│  │  Tier 1: Graceful Degradation                          │ │
│  │    • try-except 보호                                   │ │
│  │    • 실패해도 계속                                     │ │
│  │                                                         │ │
│  │  Tier 2: Mode Toggle                                   │ │
│  │    • runtime_config.yaml                               │ │
│  │    • Layer별 on/off                                    │ │
│  │                                                         │ │
│  │  Tier 3: Circuit Breaker                               │ │
│  │    • 3회 실패 → 자동 차단                             │ │
│  │    • 복구 시 재시도                                    │ │
│  │                                                         │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Overlay Layer (향후, 설계만)                          │ │
│  ├────────────────────────────────────────────────────────┤ │
│  │                                                         │ │
│  │  3-Layer:                                               │ │
│  │    • Core (공식, 검증됨)                               │ │
│  │    • Team (팀 표준)                                    │ │
│  │    • Personal (개인 실험)                              │ │
│  │                                                         │ │
│  │  검색 우선순위: Personal > Team > Core                 │ │
│  │                                                         │ │
│  │  승격 경로: Personal → Team → Core                     │ │
│  │                                                         │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Learning Loop (자동 개선)                             │ │
│  ├────────────────────────────────────────────────────────┤ │
│  │                                                         │ │
│  │  LLM 판단 로그:                                         │ │
│  │    • Projection 결정 기록                              │ │
│  │    • 패턴 분석 (주간)                                  │ │
│  │    • 자동 규칙 생성                                    │ │
│  │                                                         │ │
│  │  효과:                                                  │ │
│  │    • LLM 10% → 5% → 1%                                 │ │
│  │    • 비용 ↓, 속도 ↑                                   │ │
│  │    • 품질 ↑ (규칙 누적)                               │ │
│  │                                                         │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  System RAG (컨텍스트 최적화) ⭐ 신규!                │ │
│  ├────────────────────────────────────────────────────────┤ │
│  │                                                         │ │
│  │  Tool Registry:                                         │ │
│  │    • 30개 도구 정의                                    │ │
│  │    • 사용 조건 (when_to_use)                          │ │
│  │    • 산출물 체인 (deliverables)                       │ │
│  │    • 검증 규칙                                         │ │
│  │                                                         │ │
│  │  Guidelines RAG:                                        │ │
│  │    • umis.yaml → 30개 청크                            │ │
│  │    • 컨텍스트 95% 절감! (5,428줄 → 200줄)            │ │
│  │    • 필요한 도구만 검색                                │ │
│  │                                                         │ │
│  │  Guardian Meta-RAG Orchestration:                       │ │
│  │    • 도구 선택 (조건 기반)                             │ │
│  │    • Workflow 동적 생성                                │ │
│  │    • 실행 모니터링                                     │ │
│  │    • 적응적 조정 (10x 기회 시 pivot)                  │ │
│  │                                                         │ │
│  │  Universal Deliverables (향후):                        │ │
│  │    • 질문 유형 → 표준 산출물                          │ │
│  │    • 템플릿 자동 생성                                  │ │
│  │    • 품질 자동 검증                                    │ │
│  │                                                         │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 💡 왜 이런 구조인가?

### 1. Dual-Index + TTL (Layer 1) ⭐ 수정!

```yaml
문제:
  Pre-Projection: 일관성 위험 (6곳 동기화)
  Lazy Projection: 품질 저하 (노이즈 40%)

해결 (v3.0 수정):
  Dual-Index + TTL/온디맨드
  
  • Canonical: 1곳 수정 (일관성)
  • Projected: TTL + 온디맨드 (비용 ↓)
    - 기본: 지연 투영 (규칙+캐시)
    - 고빈도만: 영속화
    - TTL: 24시간

가치:
  품질 유지 + 비용 급감!
  
전문가 피드백:
  "Projected는 Materialized View로"
  → 당신의 원래 Lazy 제안 복원!
```

### 2. Schema Registry + 감사성 (횡단) ⭐ 강화!

```yaml
문제:
  4-Layer 공통 필드 → 불일치 위험
  추적성 부족 → 감사 어려움

해결 (v3.0 강화):
  중앙 집중 스키마 + ID/Lineage
  
  • 모든 필드 정의
  • Layer 간 매핑
  • Contract Tests
  
  + ID 네임스페이스:
    • CAN-xxx (Canonical)
    • PRJ-xxx (Projected)
    • GND/GED-xxx (Graph)
    • MEM-xxx (Memory)
  
  + Lineage 블록:
    • from, via, evidence_ids
    • 교차 추적 100%

가치:
  필드 일관성 + 감사성(A)!
  
전문가 피드백:
  "교차 레이어 추적성 강화"
```

### 3. Routing YAML (횡단)

```yaml
문제:
  Python 코드 → 가독성 낮음

해결:
  YAML 워크플로우
  
  • 순서 명확
  • 조건 가시적
  • 사용자 수정 쉬움

가치:
  가독성, 유연성
```

### 4. Multi-Dimensional Confidence + 근거 (Layer 3) ⭐ 강화!

```yaml
문제:
  단일 차원 → 예외 케이스
  근거 없음 → 설명 불가

해결 (v3.0 강화):
  질적 + 양적 + 검증 + 근거
  
  • Similarity (Vector): 0.92
  • Coverage (분포): 0.10
  • Validation (Yes/No): yes
  • Overall: 0.83 (0-1 숫자!)
  
  + Evidence & Provenance:
    • evidence_ids: ["CAN-...", "PRJ-..."]
    • provenance: {reviewer, timestamp}
    • 근거 역추적 100%

가치:
  예외 없음 + 설명가능성!
  
전문가 피드백:
  "그래프 써도 A(재현성) 유지"
```

### 5. Fail-Safe (횡단)

```yaml
문제:
  한 Layer 실패 = 전체 실패

해결:
  3-Tier 방어
  
  • Graceful Degradation
  • Mode Toggle
  • Circuit Breaker

가치:
  항상 작동, 안정성
```

### 6. Overlay Layer (향후)

```yaml
문제:
  개인 실험 vs 팀 표준 충돌

해결:
  Core / Team / Personal
  
  • 격리, 안전
  • 승격 경로

가치:
  협업, 실험 자유
```

### 7. Learning Loop (횡단)

```yaml
문제:
  LLM 판단 → 비용

해결:
  로그 → 규칙 학습
  
  • 10% → 1%
  • 자동 개선

가치:
  비용 ↓, 품질 ↑
```

### 8. System RAG (횡단) ⭐ 혁명적!

```yaml
문제:
  umis.yaml 5,428줄 → 컨텍스트 부담

해결:
  Guidelines를 도구 라이브러리로!
  
  • Tool Registry (30개 도구)
  • System RAG (필요한 것만)
  • Guardian Meta-RAG (동적 오케스트레이션)

가치:
  컨텍스트 95% 절감!
  동적 Workflow
  지능적 시스템

예시:
  사용자: "@Explorer, 시장 분석"
  
  Guardian:
    1. System RAG 검색: "Explorer analysis tools"
    2. 도구 선택: [pattern_recognition, 7_step, ...]
    3. 조건 확인: clarity < 7 → discovery_sprint 추가
    4. Workflow 생성: Discovery(3일) → Analysis(5일) → ...
    5. 로드맵 제시: 2-3주 예상
    6. 실행 중 모니터링
    7. 10x 기회 발견 → pivot 도구 추가
  
  효과:
    5,428줄 전체 X
    200줄 필요한 것만 O
```

---

## 🔧 구현 우선순위

```yaml
즉시 (v7.0.0):
  ✅ Layer 1: Vector RAG (완료!)

Phase 1 (2주):
  🔴 Dual-Index (Layer 1)
  🔴 Schema Registry
  🔴 Routing YAML
  🔴 Fail-Safe Tier 1-2

Phase 2 (2주):
  🔴 Knowledge Graph (Layer 3)
  🔴 Multi-Dimensional Confidence
  🔴 Circuit Breaker

Phase 3 (2주):
  🟡 Guardian Memory (Layer 4)
  🟡 Learning Loop

Phase 4 (향후):
  🟢 Overlay Layer (팀 확장 시)
  🟡 System RAG (Guidelines 10K줄 넘으면)
```

---

## 🎯 핵심 가치

**이 아키텍처가 제공하는 것:**

```yaml
품질:
  ✅ 검색 정확도 (Dual-Index)
  ✅ 평가 신뢰성 (Multi-Dimensional)
  ✅ 일관성 (1곳 수정)

효율:
  ✅ 업데이트 간단 (Canonical)
  ✅ 자동 학습 (LLM → 규칙)
  ✅ 비용 최적화

안정성:
  ✅ 항상 작동 (Fail-Safe)
  ✅ Layer 독립성 (Toggle)
  ✅ 자동 복구 (Circuit)

확장성:
  ✅ 팀 협업 (Overlay)
  ✅ 개인 실험 (Personal)
  ✅ 점진적 (설계 먼저)

사용자:
  ✅ Cursor 중심
  ✅ YAML 수정
  ✅ 대화만!

지능:
  ✅ 동적 Workflow (System RAG)
  ✅ 적응적 조정 (Guardian)
  ✅ 자동 학습 (Learning Loop)
```

---

---

## 🎯 v3.0 신규 개선안 (전문가 피드백)

### 9. ID & Lineage 표준화 ⭐ P0

```yaml
문제:
  source_id만 → 레이어 구분 없음

해결:
  ID 네임스페이스:
    • CAN-xxx, PRJ-xxx, GND-xxx, ...
  
  Lineage 블록:
    • from, via, evidence_ids
    • 교차 추적

가치:
  감사성(A) 핵심!
```

### 10. anchor_path + hash ⭐ P0

```yaml
문제:
  sections: {start, end} → 오프셋 깨짐

해결:
  anchor_path + content_hash:
    • 경로 기반 안정 참조
    • 토크나이저 변경 안전

가치:
  재현성(A) 핵심!
```

### 11. TTL + 온디맨드 (1번 통합)

```
Dual-Index에 통합
```

### 12. Graph 근거 (4번 통합)

```
Multi-Dimensional에 통합
```

### 13. RAE Index (5번 복원)

```
복원됨 (위 참조)
```

### 14. Overlay 메타 (6번 강화)

```yaml
변경:
  설계만 → 메타 선반영

추가:
  overlay_layer, tenant_id, merge_strategy
  → 지금 schema에!

가치:
  미래 마이그레이션 방지
```

### 15. Retrieval Policy (3번 확장)

```yaml
확장:
  routing_policy.yaml
  + retrieval 섹션
  
  intent 기반 라우팅
  layer 동적 선택

가치:
  더 세밀한 제어
```

### 16. Embedding 버전 (P1)

```yaml
추가:
  embedding.model, dimension

가치:
  모델 변경 추적
```

---

## 🎯 v3.0 개선안 요약

### 채택 (7개 → 8개!)

```yaml
1. Dual-Index + TTL ⭐ (v3.0 강화)
   우선순위: P0
   가치: 품질 + 일관성 + 비용↓

2. Schema-Registry + ID/Lineage ⭐ (v3.0 강화)
   우선순위: P0
   가치: 필드 일관성 + 감사성(A)

3. Routing + Retrieval Policy ⭐ (v3.0 확장)
   우선순위: P0
   가치: workflow + intent 라우팅

4. Multi-Dimensional + 근거 ⭐ (v3.0 강화)
   우선순위: P0
   가치: 평가 + 설명가능성

5. RAE Index (초소형) ⭐ (v3.0 복원!)
   우선순위: P0
   가치: 평가 일관성 (비용 X, 일관성 O)

6. Overlay (메타 선반영) ⭐ (v3.0 강화)
   우선순위: 메타 P0, 구현 P2
   가치: 미래 안전

7. Fail-Safe (3-Tier)
   우선순위: P0
   가치: 항상 작동

8. System RAG + Tool Registry
   우선순위: P1 (향후)
   가치: 컨텍스트 95% 절감
```

### 신규 (P0 보완, v3.0)

```yaml
9. ID & Lineage 표준화
   우선순위: P0
   가치: 감사성(A) 핵심

10. anchor_path + hash
    우선순위: P0
    가치: 재현성(A) 핵심
```

### 선택 (P1)

```yaml
11. Embedding 버전
    우선순위: P1
    가치: 모델 변경 추적
```

### 복원 (1개) ⭐ v3.0 변경!

```yaml
5. RAE Index (초소형)
   결정 변경: 제외 → 채택!
   
   이유:
     비용 X, 일관성 O
     유사 케이스 재사용
     평가 학습 효과
   
   초소형:
     • grade + rationale + evidence_ids만
     • 복잡도 낮음
     • 가치 충분
   
   전문가 피드백:
     "평가 일관성↑, 쓸수록 똑똑해지는 Guardian"
```

---

**관련 문서:**
- umis_rag_architecture_v2.0.yaml (YAML 스펙)
- ARCHITECTURE_IMPROVEMENTS_CHECKLIST.md (체크리스트)
- 01-08/ 폴더 (상세 검토 문서)

