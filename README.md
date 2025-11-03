# UMIS - Universal Market Intelligence System

[![GitHub](https://img.shields.io/badge/GitHub-umis-blue?logo=github)](https://github.com/kangminlee-maker/umis)
[![Version](https://img.shields.io/badge/version-6.3.0--alpha-orange)](https://github.com/kangminlee-maker/umis/releases)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

**버전:** 6.3.0-alpha  
**날짜:** 2025-11-03  
**대상:** 코딩 못 하는 사용자 (Cursor만!)

> **"불확실성을 기회로 전환하는 시장 분석 시스템"**

---

## 🎯 UMIS v6.3.0-alpha란?

AI 에이전트 5명이 협업하여 시장을 분석하는 프레임워크입니다.

**v6.3.0-alpha 신규:**
- ✅ Explorer에게 RAG 추가!
- ✅ 54개 검증된 패턴/사례 자동 검색
- ✅ Cursor Composer 완전 통합
- ✅ Agent 이름 커스터마이징
- ✅ Architecture v3.0 설계 (16개 개선안)
- ✅ schema_registry.yaml (감사성·재현성)

---

## 📦 설치

```bash
# 1. 레포 클론
git clone https://github.com/kangminlee-maker/umis.git
cd umis

# 2. 초기 설정 (5분)
# SETUP.md 참고
```

---

## ⚡ 30초 빠른 시작

**Cursor Composer (Cmd+I):**

```
umis.yaml 첨부

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

## 📚 주요 파일

**핵심 YAML:**
- **umis.yaml** - 메인 가이드라인 (Cursor에 첨부)
- **umis_deliverable_standards.yaml** - 산출물 표준
- **agent_names.yaml** - Agent 이름 커스터마이징

**RAG 데이터:**
- **data/raw/umis_business_model_patterns.yaml** - 31개 사업모델 패턴
- **data/raw/umis_disruption_patterns.yaml** - 23개 Disruption 패턴

---

## 📁 프로젝트 구조

```
umis/
├── 핵심 YAML
│   ├── umis.yaml (메인 가이드라인)
│   ├── umis_deliverable_standards.yaml (산출물 표준)
│   ├── umis_examples.yaml (예제)
│   └── agent_names.yaml (Agent 커스터마이징)
│
├── RAG 데이터
│   └── data/
│       ├── raw/ (원본 YAML)
│       │   ├── umis_business_model_patterns.yaml (31 패턴)
│       │   └── umis_disruption_patterns.yaml (23 패턴)
│       ├── chunks/ (청크 JSONL)
│       └── chroma/ (벡터 DB, 54개 문서)
│
├── RAG 시스템 (v6.3.0-alpha)
│   ├── umis_rag/ (Python 패키지)
│   ├── scripts/ (RAG 빌드/검색)
│   └── notebooks/ (프로토타입)
│
├── 문서
│   ├── docs/ (UMIS v6.2 가이드)
│   └── rag/docs/ (RAG 아키텍처 65개)
│
└── 설정
    ├── .cursorrules (UMIS 자동화 규칙)
    ├── SETUP.md (초기 설정)
    ├── START_HERE.md (빠른 시작)
    └── env.template (API 키)
```

---

## 🚀 사용 흐름

```
1. Cursor Composer (Cmd+I)
2. umis.yaml 첨부
3. "@Steve, 시장 분석해줘"

→ Observer 관찰
→ Explorer RAG 검색 (자동!)
→ subscription_model 발견
→ 코웨이 사례 학습
→ 가설 생성

→ 대화만! ✨
```

---

## 📖 문서 & 가이드

### 시작하기
- **[START_HERE.md](START_HERE.md)** - 30초 빠른 시작
- **[SETUP.md](SETUP.md)** - 초기 설정 가이드 (5분)
- **[rag/docs/guides/01_CURSOR_QUICK_START.md](rag/docs/guides/01_CURSOR_QUICK_START.md)** - Cursor 사용법

### 참고 문서
- **[UMIS v6.2 Complete Guide](docs/UMIS_v6.2_Complete_Guide.md)** - 전체 프레임워크
- **[RAG Architecture](rag/docs/architecture/)** - RAG 시스템 설계 (65개 문서)
- **[CHANGELOG.md](CHANGELOG.md)** - 버전 히스토리

### 커스터마이징
- **[agent_names.yaml](agent_names.yaml)** - Agent 이름 변경
- **[.cursorrules](.cursorrules)** - UMIS Cursor 자동화 규칙

---

## 🤝 기여

이슈와 PR을 환영합니다!

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 라이선스

MIT License - 자유롭게 사용, 수정, 배포 가능합니다.

---

## 📞 문의

- **GitHub Issues:** [umis/issues](https://github.com/kangminlee-maker/umis/issues)
- **Discussions:** [umis/discussions](https://github.com/kangminlee-maker/umis/discussions)

---

**UMIS Team • 2025**
