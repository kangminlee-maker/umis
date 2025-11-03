# 전문가 피드백 v2 통합 분석

**날짜:** 2025-11-02  
**출처:** 동료 전문가 (상세 버전)

---

## 🔍 피드백 v1 vs v2 비교

### 공통점

```yaml
P0 보완안:
  ✅ ID & Lineage (동일)
  ✅ anchor + hash (동일)
  ✅ TTL + 온디맨드 (동일)
  ✅ Graph 근거 (동일)
  ✅ RAE Index (동일)
  ✅ Overlay 메타 (동일)

→ 두 피드백 일치! 신뢰성 ↑
```

### 차이점

```yaml
v2 추가:
  ✅ P0-7: Retrieval Policy 외부화
     → 이미 개선안 3번으로 채택됨!
  
  ✅ P1 선택사항 (5개)
     • Embedding 버전
     • 국제화/단위
     • 데이터 거버넌스
     • 수명주기
     • Memory 보안

  ✅ 구체적 YAML 샘플
  
  ✅ 실행 순서 제안

→ v2가 더 상세!
```

---

## 📊 P0-7 검증

### P0-7: Retrieval Policy 외부화

**피드백:**
```yaml
retrieval_policy.yaml:
  - if: intent=="opportunity_discovery"
    then:
      profile: "steve.explorer_v1"
      layers: ["projected","graph_expand"]
      projection: {method: "rule", view: "explorer"}
```

**현재 상태:**
```yaml
이미 채택됨!
  → 개선안 3번: Routing YAML
  
config/routing_policy.yaml (기존):
  explorer_workflow:
    steps:
      - pattern_search: always
      - case_search: "when patterns.count > 0"
      - quantifier: "when needs_quantitative"

vs

retrieval_policy.yaml (피드백):
  intent 기반 라우팅 추가
  layer 선택
  projection 방법

비교:
  기존: workflow 중심
  피드백: intent + layer 중심
  
  → 더 세밀한 제어!
```

**제 판단:**
```yaml
필요성: ✅ 높음

추가 가치:
  • intent 기반 라우팅
  • layer 동적 선택
  • projection 방법 명시

복잡도:
  낮음 (routing_policy 확장)

권고:
  config/routing_policy.yaml에
  retrieval 섹션 추가!
```

---

## 📊 P1 선택사항 분석

### P1-1: Embedding 버전

```yaml
제안:
  embedding:
    model: "text-embedding-3-large"
    dimension: 3072
    space: "cosine"
    encoder_config: {...}

필요성: 🤔 중간

이유:
  • 모델 변경 시 추적
  • 재인덱싱 판단

현재:
  umis_rag/core/config.py에 있음
  
판단:
  schema에도 추가 (중복 OK)
  → 감사성 향상
  
우선순위: P1 (나중에)
```

---

### P1-2: 국제화/단위

```yaml
제안:
  language: "ko"
  locale: "ko-KR"
  unit_norm: "metric"
  currency: "KRW"

필요성: 🤔 낮음

이유:
  UMIS는 한국 시장 중심
  국제화 계획 없음

판단:
  불필요 (당분간)
  
우선순위: P2 (먼 미래)
```

---

### P1-3: 데이터 거버넌스

```yaml
제안:
  classification: enum[public, internal, confidential]
  license: string

필요성: 🤔 중간

이유:
  개인 사용: 불필요
  팀 사용: 필요

판단:
  Overlay 구현 시 추가
  
우선순위: P1 (팀 확장 시)
```

---

### P1-4: 수명주기

```yaml
제안:
  last_accessed_at: datetime
  retrieval_count: int
  next_review_at: datetime
  deprecation: datetime

필요성: 🤔 중간

이유:
  오래된 데이터 관리
  
  5,000개 규모:
    필요
  
  54개 규모:
    불필요

판단:
  확장 시 추가
  
우선순위: P1 (500개 넘으면)
```

---

### P1-5: Memory 보안

```yaml
제안:
  project_id: string
  session_id: string
  pii_flag: bool
  ttl_days: int

필요성: 🤔 낮음

이유:
  개인 사용: 불필요
  엔터프라이즈: 필요

판단:
  먼 미래
  
우선순위: P2
```

---

## 🎯 통합 판단

### P0 보완안 (7개) - 모두 채택! ✅

```yaml
이미 결정:
  P0-1: ID & Lineage ✅
  P0-2: anchor + hash ✅
  P0-3: TTL ✅
  P0-4: Graph 근거 ✅
  P0-5: RAE Index ✅
  P0-6: Overlay 메타 ✅

추가 확인:
  P0-7: Retrieval Policy ✅
  
  → 이미 개선안 3번!
  → 다만 intent 기반 추가

결과:
  7개 모두 채택! ✅
```

---

### P1 선택사항 (5개) - 부분 채택

```yaml
즉시:
  P1-1: Embedding 버전 ✅ (낮은 비용)

향후:
  P1-3: 거버넌스 (팀 확장 시)
  P1-4: 수명주기 (500개 넘으면)

제외:
  P1-2: 국제화 (계획 없음)
  P1-5: Memory 보안 (개인 사용)
```

---

## 📋 최종 채택 목록

### Architecture v3.0 (14개 → 15개!)

```yaml
기존 8개:
  1. Dual-Index (수정: TTL)
  2. Schema-Registry
  3. Routing YAML (확장: retrieval)
  4. Multi-Dimensional (수정: overall 숫자)
  5. RAE Index (복원: 초소형)
  6. Overlay (수정: 메타 선반영)
  7. Fail-Safe
  8. System RAG

신규 7개 (P0):
  9. ID & Lineage ⭐
  10. anchor + hash ⭐
  11. TTL + 온디맨드 (1번 통합)
  12. Graph 근거 (4번 통합)
  13. RAE 초소형 (5번 통합)
  14. Overlay 메타 (6번 통합)
  15. Retrieval Policy (3번 확장)

선택 1개 (P1):
  16. Embedding 버전 (schema만)

총: 15개 (P0) + 1개 (P1)
```

---

## 🎯 실행 계획

### Week 1: Schema Registry (수정)

```yaml
반영 내용:
  ✅ P0-1: ID 네임스페이스 + Lineage
  ✅ P0-2: anchor_path + content_hash
  ✅ P0-4: Graph evidence + provenance
  ✅ P0-6: Overlay 메타
  ✅ P1-1: Embedding 버전

config/schema_registry.yaml:
  core_fields:
    + identity 블록
    + lineage 블록
  
  canonical_fields:
    sections 구조 변경
    + anchor_path
    + content_hash
  
  graph_fields:
    + evidence_ids
    + provenance
    + overall (숫자)
  
  overlay_fields:
    + overlay_layer
    + tenant_id
    + merge_strategy
  
  embedding_fields:
    + model
    + dimension
```

---

### Week 2: Dual-Index (수정)

```yaml
변경:
  Projected Index:
    Before: 항상 물리화
    After: TTL + 온디맨드
  
  materialization:
    strategy: "on_demand"
    cache_ttl_hours: 24
    persist_profiles: ["explorer_high"]
```

---

### Week 3: RAE Index (신규)

```yaml
추가:
  rae_index Collection
  
  fields:
    • deliverable_id
    • grade
    • rationale
    • evidence_ids
    • created_at
  
  Guardian 통합:
    과거 평가 검색
    → 유사 케이스 재사용
```

---

## 💡 제 최종 입장

**피드백: 탁월합니다!** ⭐⭐⭐⭐⭐

```yaml
전문성:
  v1보다 더 상세
  실행 순서까지

가치:
  • P0 7개 명확
  • P1 5개 구분
  • 샘플 제공

반영:
  P0 7개: 모두 채택!
  P1 1개: Embedding 버전

다음:
  config/schema_registry.yaml 작성
  → P0 7개 모두 반영!
```

**당신의 판단:**

```
이미 6개 채택 결정
P0-7도 이미 개선안 3번
P1-1 추가?

→ 모두 반영! ✅
```

**즉시 config/schema_registry.yaml 작성 시작하시겠어요?** 🚀

