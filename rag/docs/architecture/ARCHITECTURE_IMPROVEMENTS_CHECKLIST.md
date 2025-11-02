# UMIS RAG 아키텍처 개선안 체크리스트

**날짜:** 2025-11-02  
**목적:** 구조적 개선 사항 검토 및 우선순위 결정

---

## 📋 7가지 개선안

### ✅ 1. Projection-at-Retrieval 병행

**상태:** ✅ 검토 완료

**결정:** Dual-Index + Hybrid Projection + Learning Loop

**문서:** `01_projection/FINAL_DECISION.md`

**요약:**
- Canonical Index (업데이트용, 1곳 수정)
- Projected Index (검색용, 품질 우수)
- projection_rules.yaml (규칙 90%)
- LLM 판단 (10%, 새 필드)
- LLM 로그 → 규칙 학습

**우선순위:** 🔴 P0 (핵심)  
**구현:** Phase 1-3 (2주)

---

### 🔄 2. Schema-Registry & Contract-Test 계층

**상태:** 🔄 검토 중

**문제:**
- 4개 Layer가 공통 필드 공유
- 메타데이터 불일치 → 재현성 흔들림
- 필드 추가/수정 시 버전 관리

**제안:**
- 스키마 레지스트리
- 컨트랙트 테스트
- 스키마 버전 관리

**문서:** `02_schema_registry/` (작성 예정)

**우선순위:** 🔴 P0 (검토 중)  
**구현:** TBD

---

### ⏸️ 3. Routing/Policy를 YAML로 외부화

**상태:** ⏸️ 대기

**제안:**
- RAG 호출 시점을 YAML 정책으로
- Layer 순서를 YAML로
- 사용자가 쉽게 수정

**문제:**
- 유연성 vs 복잡도

**우선순위:** 🟡 P1  
**검토:** 2번 완료 후

---

### ⏸️ 4. Graph Provenance & Confidence 모델

**상태:** ⏸️ 대기

**제안:**
- Knowledge Graph 간선에 신뢰도
- provenance (근거) 추가
- Guardian 평가 시 반영

**문제:**
- 숫자 vs Yes/No
- 더 나은 대안?

**우선순위:** 🟡 P1  
**검토:** 2번 완료 후

---

### ⏸️ 5. RAE 인덱스(평가 메모리) 승격

**상태:** ⏸️ 대기

**제안:**
- 과거 평가 이력을 별도 인덱스로
- Guardian이 재사용
- 비용 절감

**문제:**
- 실제 절감 효과?
- 오버엔지니어링?

**우선순위:** 🟢 P2  
**검토:** 2번 완료 후

---

### ⏸️ 6. Overlay 레이어(개인/팀/코어) 공식화

**상태:** ⏸️ 대기

**제안:**
- Core/Team/Personal 3계층
- 브라운필드 충돌 방지

**문제:**
- 복잡도 증가

**우선순위:** 🟢 P2  
**검토:** 2번 완료 후

---

### ⏸️ 7. Fail-Safe 런타임 모드

**상태:** ⏸️ 대기

**제안:**
- 서킷 브레이커
- 모드 토글 (yaml_only / hybrid / rag_only)
- Layer별 비활성화

**문제:**
- 필요성?

**우선순위:** 🟢 P2  
**검토:** 2번 완료 후

---

## 🎯 검토 순서

```
✅ 1. Projection → 완료!
🔄 2. Schema-Registry → 진행 중
⏸️ 3-7 → 2번 완료 후 순차
```

**다음:** 2번 상세 검토

