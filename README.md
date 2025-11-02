# UMIS - Universal Market Intelligence System

**버전:** 6.3.0-alpha  
**날짜:** 2025-11-02  
**대상:** 코딩 못 하는 사용자 (Cursor만!)

---

## 🎯 UMIS v6.3.0-alpha란?

AI 에이전트 5명이 협업하여 시장을 분석하는 프레임워크입니다.

**v6.3.0-alpha 신규:**
- ✅ Explorer에게 RAG 추가!
- ✅ 54개 검증된 패턴/사례 자동 검색
- ✅ Cursor Composer 완전 통합
- ✅ Agent 이름 커스터마이징

---

## ⚡ 30초 빠른 시작

**Cursor Composer (Cmd+I):**

```
@umis_guidelines_v6.2.yaml

"@Steve, 음악 스트리밍 구독 서비스 시장 기회 분석해줘"
```

**끝!** 🎉

→ Steve (Explorer)가 RAG를 자동으로 활용합니다!

---

## 🤖 UMIS Agent (v6.3.0-alpha)

```
Observer (Albert) → 시장 관찰 (YAML)
Explorer (Steve) → 기회 발굴 (RAG!) ⭐
Quantifier (Bill) → 정량 분석 (YAML)
Validator (Rachel) → 데이터 검증 (YAML)
Guardian (Stewart) → 품질 관리 (YAML)
Owner → 의사결정

현재: Explorer만 RAG 사용!
향후: 전체 Agent RAG 확장 계획
```

---

## 🎨 Agent 커스터마이징

**agent_names.yaml 수정:**

```yaml
# 기본 (UMIS v6.2 전통)
observer: Albert
explorer: Steve
quantifier: Bill
validator: Rachel
guardian: Stewart

# 커스텀 (1줄 수정!)
explorer: Alex

# 한국어도 가능
explorer: 탐색자
```

**사용:**
```
Cursor:
  "@Alex, 기회 찾아봐"
  
  → Alex가 패턴을 검색합니다...
```

**양방향:**
- 입력: @Alex → Explorer
- 출력: Explorer → Alex

---

## 💡 v6.3.0-alpha 주요 기능

```yaml
Explorer RAG:
  ✅ 54개 검증된 패턴/사례
  ✅ text-embedding-3-large (고품질)
  ✅ 자동 검색 (Cursor Agent 모드)

Cursor 통합:
  ✅ .cursorrules 자동화
  ✅ 대화만! 코딩 불필요!
  ✅ 30초 피드백 루프

Agent 커스터마이징:
  ✅ agent_names.yaml
  ✅ Albert/Steve/... (기본)
  ✅ Jane/Alex/탐색자/... (커스텀)
```

---

## 📚 문서

**시작:**
- START_HERE.md (이 폴더)
- rag/docs/guides/01_CURSOR_QUICK_START.md

**참고:**
- rag/docs/ (RAG 설계 및 계획)
- docs/ (UMIS v6.2 가이드)

---

## 📁 프로젝트 구조

```
umis-main/
├── UMIS Core
│   ├── umis_guidelines_v6.2.yaml
│   ├── umis_business_model_patterns_v6.2.yaml
│   ├── umis_disruption_patterns_v6.2.yaml
│   └── ... (3개 더)
│
├── RAG (v6.3.0-alpha)
│   ├── .cursorrules (자동화)
│   ├── agent_names.yaml (커스터마이징)
│   ├── umis_rag/ (Python)
│   ├── scripts/ (4개)
│   ├── data/ (청크 + 벡터 DB)
│   └── rag/docs/ (문서)
│
└── docs/ (UMIS v6.2 문서)
```

---

## 🚀 사용 흐름

```
1. Cursor Composer (Cmd+I)
2. @umis_guidelines_v6.2.yaml 첨부
3. "@Steve, 시장 분석해줘"

→ Observer 관찰
→ Explorer RAG 검색 (자동!)
→ subscription_model 발견
→ 코웨이 사례 학습
→ 가설 생성

→ 대화만! ✨
```

---

## 📖 더 알아보기

- **UMIS v6.2:** docs/UMIS_v6.2_Complete_Guide.md
- **RAG 가이드:** rag/docs/guides/
- **Agent 커스터마이징:** agent_names.yaml

---

## 📄 라이선스

MIT License

---

**"불확실성을 기회로 전환하는 시장 분석 시스템"**

UMIS Team • 2025
