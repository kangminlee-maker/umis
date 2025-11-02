# UMIS - Universal Market Intelligence System

범용 시장 정보 분석 시스템

**버전:** 6.3.0-alpha  
**날짜:** 2025-11-02

---

## 🎯 무엇인가요?

**UMIS**는 AI 에이전트 5명이 협업하여 시장을 분석하는 프레임워크입니다.

**UMIS RAG (v6.3.0-alpha)**는 Explorer에게 검증된 패턴 라이브러리와 의미 검색을 제공하는 확장입니다.

---

## ⚡ 빠른 시작

### UMIS 기본 (YAML만)

```
Cursor Composer (Cmd+I):
  @umis_guidelines_v6.2.yaml
  
  "피아노 구독 서비스 시장 분석해줘"
  
→ Observer, Explorer, Quantifier, Validator가 협업!
```

### UMIS v6.3.0-alpha (RAG 추가!)

```
Cursor Composer (Cmd+I):
  @umis_guidelines_v6.2.yaml
  
  "@Steve, 음악 스트리밍 구독 기회 분석해줘"
  
  → Steve (Explorer)가 RAG 자동 활용!
  → 54개 검증된 패턴/사례 검색
  → subscription_model 발견!
  → 코웨이 사례 학습!
  
  → 대화만! 코딩 불필요! ✨
```

**Agent 커스터마이징:**
```yaml
agent_names.yaml:
  explorer: Alex  # ← 1줄!

Cursor:
  "@Alex, 기회 찾아봐"
  → Alex가 패턴을 검색합니다...
```

---

## 📚 주요 문서

### 사용자용
- **CURSOR_QUICK_START.md** - Cursor에서 즉시 사용
- **USAGE_COMPARISON.md** - 3가지 모드 비교
- **README_RAG.md** - RAG 시스템 개요

### 개발자용
- **DEPLOYMENT_STRATEGY.md** - 개발/배포 전략
- **USER_DEVELOPER_WORKFLOW.md** - Hot-Reload 개발
- **RAG_INTEGRATION_OPTIONS.md** - 통합 옵션 6가지

### 아키텍처
- **umis_rag_architecture_v1.1_enhanced.yaml** - 완전한 설계
- **SPEC_REVIEW.md** - UMIS 철학 대조
- **ADVANCED_RAG_CHALLENGES.md** - 3가지 핵심 도전

---

## 🛠️ 개발 모드 (Hot-Reload)

```bash
# YAML 수정 → 2초 → 자동 반영!

make dev

# → Watcher 실행
# → data/raw/ 감시
# → YAML 저장 시 자동 업데이트

# VS Code에서 YAML 수정
# Ctrl+S

# (2초 후)
# ✅ 자동 반영!
```

---

## 📦 배포 패키지 생성

```bash
# 배포 버전 만들기
python scripts/build_release.py --version 1.0.0 --include-index

# 생성:
# releases/umis-rag-v1.0.0.zip (150MB)
#   ├── YAML 파일
#   ├── Python 코드
#   ├── 사전 구축 인덱스
#   └── README
```

---

## 🎯 3가지 사용 모드

| 모드 | 첨부 | 설정 | 품질 | 사용자 |
|------|------|------|------|--------|
| YAML Only | 3개 | 없음 | ⭐⭐⭐ | 초보 |
| YAML + RAG | 1개 | 중간 | ⭐⭐⭐⭐⭐ | 고급 |
| MCP Tool | 1개 | 쉬움 | ⭐⭐⭐⭐⭐ | 모두 |

---

## 🏗️ 프로젝트 구조

```
umis-main/
├── umis_guidelines_v6.2.yaml          # 메인 가이드
├── umis_business_model_patterns_v6.2.yaml
├── umis_disruption_patterns_v6.2.yaml
│
├── umis_rag/                          # Python 패키지
│   ├── agents/steve.py                # Steve RAG
│   └── core/config.py
│
├── scripts/
│   ├── 01_convert_yaml.py             # YAML → 청크
│   ├── 02_build_index.py              # 인덱스 구축
│   ├── 03_test_search.py              # 검색 테스트
│   ├── query_rag.py                   # Cursor 통합
│   ├── dev_watcher.py                 # Hot-Reload
│   └── build_release.py               # 배포 패키지
│
├── data/
│   ├── raw/                           # 원본 YAML
│   ├── chunks/                        # 54개 청크
│   └── chroma/                        # 벡터 DB
│
└── docs/                              # 설계 문서
```

---

## 🚀 Makefile 명령어

```bash
make dev          # 개발 모드 (Hot-Reload)
make rebuild      # 전체 재구축
make test         # 검색 테스트
make query QUERY="플랫폼"  # 빠른 검색
make stats        # 인덱스 통계
make clean        # 정리
```

---

## 💡 핵심 특징

### 개발자 경험
```
✅ Hot-Reload: YAML 수정 → 2초 → 반영
✅ 빠른 피드백: 사용 = 개발
✅ Git 기반: 버전 관리 명확
```

### 사용자 경험
```
✅ 간단한 설치: ./setup.sh
✅ 선택적 RAG: YAML만 또는 YAML+RAG
✅ 자동 업데이트: git pull + make rebuild
```

### 기술 스택
```
✅ Vector RAG: Chroma + OpenAI
✅ Embeddings: text-embedding-3-large (3072 dim)
✅ 청크: 54개 (패턴 + 사례)
✅ Framework: LangChain 1.0
```

---

## 📖 더 알아보기

- [UMIS v6.2 Complete Guide](docs/UMIS_v6.2_Complete_Guide.md)
- [Cursor Quick Start](CURSOR_QUICK_START.md)
- [Architecture v1.1](umis_rag_architecture_v1.1_enhanced.yaml)

---

## 🤝 기여

개발에 참여하고 싶으시다면:

1. Fork the repository
2. Create feature branch
3. Make changes with Hot-Reload
4. Test thoroughly
5. Create Pull Request

---

## 📄 라이선스

MIT License

---

**"불확실성을 기회로 전환하는 시장 분석 시스템"**

UMIS Team • 2024
