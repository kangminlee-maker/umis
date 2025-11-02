# UMIS 프로젝트

Universal Market Intelligence System v6.2

---

## 📁 프로젝트 구조

```
umis-main/
├── 📚 UMIS Core (기존)
│   ├── umis_guidelines.yaml
│   ├── umis_business_model_patterns.yaml
│   ├── umis_disruption_patterns.yaml
│   ├── umis_ai_guide.yaml
│   ├── umis_deliverable_standards.yaml
│   ├── umis_examples.yaml
│   ├── CHANGELOG.md
│   └── docs/ (기존 시장 분석 등)
│
└── 🤖 UMIS RAG (신규)
    └── rag/ ⭐
        ├── quick_umis.sh (30초 시작)
        ├── Makefile
        ├── docs/ (26개 문서)
        ├── code/ (scripts, umis_rag)
        └── config/ (설정)
```

---

## 🚀 사용 방법

### UMIS 기본 (YAML만)

```
Cursor Composer (Cmd+I):
  @umis_guidelines.yaml
  "피아노 구독 서비스 시장 분석해줘"
```

### UMIS v6.3.0-alpha (RAG 자동 활용!)

```
Cursor Composer (Cmd+I):
  @umis_guidelines.yaml
  
  "@Steve, 음악 스트리밍 구독 기회 분석해줘"
  
  → Steve (Explorer)가 RAG 자동 활용!
  → 대화만! 코딩 불필요! ✨
```

---

## 📖 문서

- **UMIS 기존:** `docs/UMIS_v6.2_Complete_Guide.md`
- **UMIS RAG:** `rag/docs/INDEX.md`

---

**UMIS:** 기존 YAML 기반 시스템  
**RAG:** 검색 증강 확장 (선택적)
