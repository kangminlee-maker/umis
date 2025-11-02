# RAG Core

**Cursor가 사용하는 Python 파일 모음**

---

## 📁 구조

```
rag_core/
├── scripts/          # RAG 스크립트
│   ├── 01_convert_yaml.py
│   ├── 02_build_index.py
│   ├── 03_test_search.py
│   └── query_rag.py
│
└── umis_rag/         # Python 패키지
    ├── agents/       # Agent 구현
    ├── core/         # 핵심 로직
    └── utils/        # 유틸리티
```

---

## 🎯 용도

**Cursor Agent 모드가 자동 실행:**

```
사용자 (Cmd+I):
  "@Steve, 패턴 찾아봐"

Cursor:
  [.cursorrules 확인]
  → python rag_core/scripts/query_rag.py ...
  → 자동 실행!
```

**사용자는 건드리지 않습니다!**

---

## 📝 추가 파일

**앞으로 추가되는 모든 Python 파일:**
```
rag_core/
├── scripts/
│   └── (새 스크립트 추가)
│
└── umis_rag/
    └── (새 모듈 추가)
```

**원칙:** 모든 Python 코드는 `rag_core/`에!

