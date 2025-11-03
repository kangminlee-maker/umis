# UMIS RAG 아키텍처

**⚠️ 주의:** 이 폴더의 문서는 **향후 구현 계획**입니다!

---

## 🎯 v7.0.0 현재 구현

```yaml
구현됨:
  ✅ Vector RAG (Layer 1 일부)
     • 54개 검증된 패턴/사례
     • text-embedding-3-large
     • Explorer만 RAG 사용!
```

---

## 📋 4-Layer 아키텍처 (계획)

이 폴더의 문서들은 **향후 개발 계획**입니다:

### COMPLETE_RAG_ARCHITECTURE.md
- 4-Layer 완전 설계
- Modular/Meta/Graph/Memory
- **상태:** 📋 계획 (미구현)

### umis_rag_architecture_v1.1_enhanced.yaml
- YAML 스펙
- **상태:** 📋 계획 (미구현)

### AGENT_ARCHITECTURE_DECISION.md
- 도메인별 Agent 구조
- **상태:** 📋 계획 (미구현)

---

## ✅ 현재 사용

**Cursor (Cmd+I):**
```
@umis_guidelines.yaml
"@Steve, 시장 분석해줘"
```

→ Steve (Explorer)만 RAG 사용!  
→ 나머지 Agent는 YAML 기반!

---

**향후 개발:** `planning/CURSOR_IMPLEMENTATION_PLAN.md` 참조

