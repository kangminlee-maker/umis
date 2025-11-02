# UMIS RAG 아키텍처 (향후 계획)

**⚠️ 주의:** 이 문서는 **향후 구현 계획**입니다!

**v6.3.0-alpha 현재:**
- ✅ Vector RAG (Explorer용, 54 chunks)

**향후 계획:**
- 📋 4-Layer 아키텍처 (아래 설명)

---

## 🎯 4-Layer RAG 아키텍처 (계획)

당신이 정리한 4-Layer RAG 구조:

```
Layer 1: Agent-Level Modular RAG      (agent별 최적화)
  → v6.3.0-alpha: Explorer만 부분 구현 ✅
  → 향후: 6개 Agent 전체 📋

Layer 2: Guardian Meta-RAG             (결과 평가/조합)
  → 향후 구현 예정 📋

Layer 3: Knowledge Graph RAG          (연결성/대안)
  → 향후 구현 예정 📋

Layer 4: Memory-Augmented RAG         (프로세스 감독)
  → 향후 구현 예정 📋
```

**이 문서는 향후 개발을 위한 설계 문서입니다.**

---

## 📊 현재 사용 가능 (v6.3.0-alpha)

```yaml
Explorer RAG:
  • Vector 검색
  • 54개 패턴/사례
  • text-embedding-3-large
  • Cursor 자동 활용

사용:
  Cursor (Cmd+I)
  "@Steve, 시장 분석해줘"
  
  → Explorer가 RAG 검색!
```

**상세 설계는 아래 참조 (향후 구현용)**

---

(기존 내용 유지...)
