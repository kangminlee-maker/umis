# UMIS v6.3.0-alpha 시작하기

**버전:** 6.3.0-alpha (Architecture v3.0 설계 완료)  
**날짜:** 2025-11-02  
**대상:** Cursor 사용자

---

## ⚡ 30초 빠른 시작

```
Cursor Composer (Cmd+I):

umis.yaml 첨부

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

## 📦 설치

```bash
git clone https://github.com/kangminlee-maker/umis.git
cd umis
```

**초기 설정:** [SETUP.md](SETUP.md) 참고 (5분)

---

## 📁 프로젝트 구조

```
umis/
├── 핵심 YAML
│   ├── umis.yaml ⭐ (메인 가이드라인)
│   ├── umis_deliverable_standards.yaml (산출물 표준)
│   ├── umis_examples.yaml (예제)
│   └── agent_names.yaml (커스터마이징)
│
├── RAG 데이터
│   └── data/
│       ├── raw/ (원본 YAML)
│       │   ├── umis_business_model_patterns.yaml (31 패턴)
│       │   └── umis_disruption_patterns.yaml (23 패턴)
│       ├── chunks/ (청크 JSONL)
│       └── chroma/ (벡터 DB, 54개 문서)
│
├── RAG 시스템
│   ├── scripts/ (RAG 빌드/검색)
│   ├── umis_rag/ (Python 패키지)
│   └── notebooks/ (프로토타입)
│
├── 문서
│   ├── docs/ (UMIS v6.2 가이드)
│   └── rag/docs/ (RAG 아키텍처 65개)
│
└── 설정
    ├── .cursorrules (UMIS 자동화 규칙)
    ├── env.template (API 키)
    └── SETUP.md (초기 설정)
```

---

## 🚀 사용 흐름

```
1. Cursor (Cmd+I)
2. umis.yaml 첨부
3. "@Steve, 시장 분석해줘"

→ Explorer RAG 자동 검색
→ subscription_model 발견
→ 코웨이 사례 학습
→ 가설 생성

→ 대화만! ✨
```

---

## 📖 더 알아보기

**시작:**
- [README.md](README.md) - 프로젝트 개요
- [SETUP.md](SETUP.md) - 초기 설정 (5분)

**가이드:**
- [Cursor Quick Start](rag/docs/guides/01_CURSOR_QUICK_START.md)
- [UMIS v6.2 Complete Guide](docs/UMIS_v6.2_Complete_Guide.md)

**아키텍처:**
- [RAG Architecture](rag/docs/architecture/COMPLETE_ARCHITECTURE_V2.md)
- [CHANGELOG.md](CHANGELOG.md)

---

## 🔗 링크

- **GitHub:** [kangminlee-maker/umis](https://github.com/kangminlee-maker/umis)
- **Issues:** [umis/issues](https://github.com/kangminlee-maker/umis/issues)

---

**UMIS Team • 2025**
