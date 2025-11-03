# Dual-Index 구현 현황

**날짜:** 2025-11-02  
**진행:** 6/7 단계 (86%)  
**상태:** 핵심 완성

---

## ✅ 완료 (6/7)

```yaml
Step 1: SchemaRegistry 로더 ✅
  • umis_rag/core/schema.py (119줄)
  • schema 로드, 검증, ID 생성

Step 2: projection_rules.yaml ✅
  • 15개 필드 → Agent 매핑
  • 학습 설정 (3회 → 규칙화)

Step 3: build_canonical_index.py ✅
  • Canonical Index 구축
  • ID: CAN-xxx
  • anchor_path + content_hash

Step 4: HybridProjector ✅
  • 규칙 90% + LLM 10%
  • LLM 로그 저장

Step 5: build_projected_index.py ✅
  • Projected Index 구축
  • TTL + 온디맨드
  • ID: PRJ-xxx

Step 6: Contract Tests ✅
  • schema 준수 검증
  • Canonical ↔ Projected 무손실
```

---

## 🔄 남은 작업 (1/7)

```yaml
Step 7: Explorer 통합
  • 현재: explorer_knowledge_base 사용
  • 목표: projected_index 사용
  • 상태: 선택사항 (하위 호환)

실제 사용 시:
  새 스크립트 작성 또는
  Explorer 인스턴스 생성 시 collection 지정
```

---

## 🎯 핵심 완성!

**Dual-Index 동작:**
```
Canonical (업데이트용) ✅
  ↓
Hybrid Projection ✅
  ↓
Projected (검색용, TTL) ✅
```

**Week 2: 86% 완료!** 🎉

---

**다음:** Week 3 (Knowledge Graph)
