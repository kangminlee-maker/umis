# UMIS v6.3.0-alpha 시작하기

**버전:** 6.3.0-alpha  
**날짜:** 2025-11-02  
**대상:** Cursor 사용자

---

## ⚡ 30초 빠른 시작

```
Cursor Composer (Cmd+I):

@umis.yaml

"@Steve, 음악 스트리밍 구독 서비스 시장 기회 분석해줘"
```

**끝!** 🎉

---

## 🤖 UMIS Agent

```
Observer (Albert) → 시장 관찰
Explorer (Steve) → 기회 발굴 (RAG!) ⭐
Quantifier (Bill) → 정량 분석
Validator (Rachel) → 데이터 검증
Guardian (Stewart) → 품질 관리
Owner → 의사결정

현재: Explorer만 RAG 사용!
```

---

## 📁 프로젝트 구조

```
umis-main/
├── 핵심 YAML (4개)
│   ├── umis.yaml ⭐
│   ├── umis_deliverable_standards.yaml
│   ├── umis_examples.yaml
│   └── agent_names.yaml
│
├── RAG
│   ├── scripts/ (RAG 스크립트)
│   ├── umis_rag/ (Python 패키지)
│   └── data/ (청크 + Vector DB)
│
├── 문서
│   ├── docs/ (UMIS v6.2 문서)
│   └── rag/docs/ (RAG 설계 65개)
│
└── 설정
    ├── .cursorrules (자동화)
    ├── env.template (API 템플릿)
    └── SETUP.md (초기 설정)
```

---

## 🚀 사용 흐름

```
1. Cursor (Cmd+I)
2. @umis.yaml 첨부
3. "@Steve, 시장 분석해줘"

→ Explorer RAG 자동 검색
→ subscription_model 발견
→ 코웨이 사례 학습
→ 가설 생성

→ 대화만! ✨
```

---

## 📖 문서

**시작:**
- START_HERE.md (이 파일)
- SETUP.md (5분 초기 설정)
- README.md (프로젝트 개요)

**가이드:**
- rag/docs/guides/01_CURSOR_QUICK_START.md

**아키텍처:**
- rag/docs/architecture/COMPLETE_ARCHITECTURE_V2.md

---

**UMIS Team • 2025**
