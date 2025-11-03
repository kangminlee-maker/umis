# Dual-Index 구현 현황

**날짜:** 2025-11-02  
**진행:** 2/7 단계

---

## ✅ 완료 (2/7)

```yaml
Step 1: SchemaRegistry 로더 ✅
  • umis_rag/core/schema.py
  • schema_registry.yaml 로드
  • 필드 검증
  • ID 생성

Step 2: projection_rules.yaml ✅
  • 필드 → Agent 매핑 (15개)
  • 학습 설정
  • 90% 커버리지 목표
```

---

## 🔄 다음 단계 (5/7)

```yaml
Step 3: Canonical Index 빌더
  → scripts/build_canonical_index.py
  
Step 4: Hybrid Projector
  → umis_rag/projection/hybrid_projector.py
  
Step 5: Projected Index 빌더
  → scripts/build_projected_index.py
  
Step 6: Contract Tests
  → tests/test_schema_contract.py
  
Step 7: Explorer 통합
  → umis_rag/agents/explorer.py 업데이트
```

---

## 🚀 Cursor로 완성

**Cursor (Cmd+I)에게:**

```
"Dual-Index 구현을 계속해줘.

완료:
  ✅ SchemaRegistry 로더
  ✅ projection_rules.yaml

다음:
  Step 3: Canonical Index 빌더
    - data/raw/*.yaml 읽기
    - Canonical 청크 생성
    - ID: CAN-xxx
    - anchor_path + content_hash
    - Lineage
    - Chroma에 저장

schema_registry.yaml 100% 준수!"
```

→ Cursor가 자동으로:
- scripts/build_canonical_index.py 생성
- 로직 구현
- 테스트
- 실행

**대화만으로 구현!** ✨

---

**현재 상태:** 기반 완성 (2/7)  
**다음:** Cursor로 나머지 구현
