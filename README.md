# UMIS - Universal Market Intelligence System

[![GitHub](https://img.shields.io/badge/GitHub-umis-blue?logo=github)](https://github.com/kangminlee-maker/umis)
[![Version](https://img.shields.io/badge/version-7.2.0-green)](https://github.com/kangminlee-maker/umis/releases)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

> **"불확실성을 기회로 전환하는 시장 분석 시스템"**

---

## 🎯 UMIS란?

AI 에이전트 5명이 협업하여 시장을 분석하는 **RAG 기반 프레임워크**

### 핵심 특징
- ✅ **5-Agent 협업**: Observer, Explorer, Quantifier, Validator, Guardian
- ✅ **RAG 지식 활용**: 54개 검증된 패턴/사례 자동 검색
- ✅ **완전한 추적성**: 모든 결론 → 원본 데이터 역추적
- ✅ **재검증 가능**: Excel 함수, YAML 스키마
- ✅ **코딩 불필요**: Cursor Composer만으로 사용

### v7.2.0 주요 기능 (최신)
- 🎉 **Native Mode**: Cursor LLM 직접 활용 (비용 $0, 최고 품질)
- 🎉 **자동 환경변수**: `.env` 자동 로드 (코드 간소화)
- ⭐ **Explorer 헬퍼**: RAG 검색 결과 사용 간편화
- ⭐ **Excel 도구 3개**: Market Sizing, Unit Economics, Financial Projection
- ⭐ **Guestimation Framework**: Fermi 추정 체계화
- ⭐ Explorer RAG (31개 비즈니스 모델 + 23개 Disruption 패턴)
- ⭐ Knowledge Graph (패턴 조합 자동 발견)

---

## 📦 빠른 시작

### 1. Clone

```bash
git clone https://github.com/kangminlee-maker/umis.git
cd umis
```

### 2. ChromaDB 설정 (두 가지 방법)

#### Option A: 자동 생성 (권장)

```bash
python setup/setup.py

# 자동으로:
# - 패키지 설치
# - .env 생성
# - RAG Collections 구축 (5분, API Key 필요)
```

**필요**:
- OpenAI API Key
- 소요 시간: ~5분
- 비용: ~$1-2 (최초 1회)

---

### 3. 사용

Cursor Composer에서:
```
"@Explorer, 구독 모델 패턴 찾아줘"
```

**상세**: [INSTALL.md](docs/INSTALL.md) 참조

### 2. 사용

```
Cursor Composer (Cmd+I):
umis.yaml 첨부

"@Steve, 음악 스트리밍 구독 서비스 시장 분석해줘"
```

**완료!** Steve (Explorer)가 RAG로 패턴을 자동 검색합니다.

---

## 🤖 Agent 커스터마이징

`config/agent_names.yaml` 파일 수정:

```yaml
# 기본
explorer: Steve

# 커스텀 (1줄만 수정!)
explorer: Alex
# 또는
explorer: 탐색자
```

사용:
```
"@Alex, 기회 찾아봐"  → Alex가 검색합니다
```

**양방향 매핑**: @Alex → Explorer / Explorer → Alex

---

## 🧮 Guestimation 방법론

UMIS는 **2가지 추정 방법론**을 제공합니다:

### 1️⃣ UMIS Guestimation (빠른 추정)

- **속도**: ⚡ 5-30분
- **정확도**: ±50% (자릿수)
- **적합**: 초기 탐색, 기회 우선순위

```bash
@Explorer guestimate 구독 모델 시장 규모
```

**특징**:
- Fermi 4원칙 (모형, 분해, 제약, 자릿수)
- 8가지 데이터 출처 활용
- 빠른 Order of Magnitude 파악

### 2️⃣ Domain-Centric Reasoner (정밀 분석)

- **속도**: 🔬 1-4시간
- **정확도**: ±30% (수렴)
- **적합**: 정밀 분석, 투자 심사, 규제 산업

```bash
@Quantifier reasoner 시니어 케어 로봇 시장 규모
```

**특징**:
- 10가지 신호 우선순위 (s3→s8→s6→s10→s2→...)
- RAG 중심 (s2 Consensus, s9 Case Analogies, s10 KPI)
- Should vs Will 분리 (행동경제학)
- 증거표 + 검증 로그

### 🔄 Hybrid Strategy (권장!)

Guardian이 자동으로 최적 방법론을 선택:

```bash
@auto 국내 OTT 시장 규모
```

**전환 트리거**:
1. **신뢰도 < 50%** → Domain Reasoner
2. **범위 폭 > ±75%** → Domain Reasoner
3. **기회 > 1,000억** → Domain Reasoner
4. **규제 산업** → Domain Reasoner (필수)
5. **신규 시장** → Domain Reasoner

**플로우**:
```
Phase 1: Guestimation (5-30분)
  ↓
Guardian 평가
  ↓
조건 충족 시 → Phase 2: Domain Reasoner (1-4시간)
```

**자세한 비교**: [GUESTIMATION_COMPARISON.md](docs/GUESTIMATION_COMPARISON.md)

---

## 📚 문서

### 시작하기
- **[INSTALL.md](docs/INSTALL.md)** - 설치 가이드
- **[setup/START_HERE.md](setup/START_HERE.md)** - 30초 빠른 시작
- **[umis.yaml](umis.yaml)** - 메인 가이드라인 (Cursor 첨부용)

### 이해하기
- **[UMIS_ARCHITECTURE_BLUEPRINT.md](UMIS_ARCHITECTURE_BLUEPRINT.md)** - 전체 아키텍처 ⭐
- **[FOLDER_STRUCTURE.md](docs/FOLDER_STRUCTURE.md)** - 폴더 구조
- **[CURRENT_STATUS.md](CURRENT_STATUS.md)** - 현재 상태
- **[CHANGELOG.md](CHANGELOG.md)** - 버전 변경 이력

### 커스터마이징
- **[config/agent_names.yaml](config/agent_names.yaml)** - Agent 이름 변경
- **[.cursorrules](.cursorrules)** - Cursor 자동화 규칙

---

## 🤝 기여

이슈와 PR을 환영합니다!

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

**기여 가이드**: [VERSION_UPDATE_CHECKLIST.md](docs/VERSION_UPDATE_CHECKLIST.md)

---

## 📄 라이선스

MIT License - 자유롭게 사용, 수정, 배포 가능합니다.

---

## 📞 문의

- **GitHub Issues**: [umis/issues](https://github.com/kangminlee-maker/umis/issues)
- **Discussions**: [umis/discussions](https://github.com/kangminlee-maker/umis/discussions)

---

**UMIS Team • 2025**
