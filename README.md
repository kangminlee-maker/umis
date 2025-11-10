# UMIS - Universal Market Intelligence System

[![GitHub](https://img.shields.io/badge/GitHub-umis-blue?logo=github)](https://github.com/kangminlee-maker/umis)
[![Version](https://img.shields.io/badge/version-7.7.0-green)](https://github.com/kangminlee-maker/umis/releases)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

> **"불확실성을 기회로 전환하는 시장 분석 시스템"**

---

## 🎯 UMIS란?

AI 에이전트 6명이 협업하여 시장을 분석하는 **RAG 기반 프레임워크** (v7.7.0)

### 핵심 특징
- ✅ **6-Agent 협업**: Observer, Explorer, Quantifier, **Validator**, Guardian, **Estimator** 
- ✅ **Native 모드**: Cursor LLM 직접 사용, 비용 $0 ⭐ v7.7.0
- ✅ **5-Phase Estimator**: Phase 0-4 + Step 1-4 명확화 ⭐ v7.7.0
- ✅ **RAG 지식 활용**: 54개 검증된 패턴/사례 자동 검색
- ✅ **Validator 우선**: 확정 데이터 검색 (85% 처리) ⭐ v7.6.0+
- ✅ **완전한 추적성**: 모든 결론 → 원본 데이터 역추적
- ✅ **재검증 가능**: Excel 함수, YAML 스키마
- ✅ **코딩 불필요**: Cursor Composer만으로 사용

### v7.7.0 주요 기능 (최신) ⭐⭐⭐
- 🎊 **Native 모드 진짜 구현**: Cursor LLM 직접 사용, 비용 $0 (v7.7.0)
- 🔤 **용어 체계 명확화**: Phase (전체 0-4) + Step (Fermi 내부 1-4) (v7.7.0)
- 🎯 **5-Phase Architecture**: Literal → Direct RAG → Validator → Guestimation → Fermi (v7.6.2)
- ⭐⭐⭐ **Validator Priority**: 85% 확정 데이터 처리, 정확도 100% (v7.6.0)
- ⭐ **Boundary Intelligence**: 개념 기반 동적 검증 (v7.6.2)
- ❌ **3-Tier Deprecated**: 5-Phase로 완전 대체 (v7.7.0)
- ✅ **Unit Conversion**: 단위 자동 변환 (v7.6.1)
- ✅ **Relevance Check**: GDP 오류 방지 (v7.6.1)
- ✅ **Web Search**: DuckDuckGo/Google 선택 (v7.6.2)
- ❌ **Built-in 제거**: 답변 일관성 확보 (v7.6.0)
- 📚 **Learning System**: 사용할수록 빠름 (v7.3.0)

### 이전 버전 주요 기능

**v7.6.2**:
- Estimator 5-Phase 재설계
- Validator 우선 검색 (85%)
- Boundary 검증
- Web Search 추가

**v7.5.0**:
- Estimator/Quantifier 분리 (MECE)
- Single Source of Truth
- Learning System

**v7.2.0**:
- Excel 도구 3개
- Phase 4 (Fermi) 설계
- Native Mode 초기 구현

**v7.0.0**:
- 6-Agent 시스템 완성
- RAG v3.0 (4-Layer)
- Knowledge Graph

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
"@Explorer, 구독 모델 패턴 찾아줘"  (v7.7.0 - Native 모드)
"@Fermi, B2B SaaS Churn은?" (v7.7.0 - 5-Phase, Step 1-4)
"@Validator, 확정 데이터 있나요?" (v7.6.0+ - 85% 처리)
```

**상세**: [INSTALL.md](docs/INSTALL.md) 참조

**Native 모드 사용**:
```
Cursor Composer (Cmd+I):
umis.yaml 첨부

"@Steve, 음악 스트리밍 구독 서비스 시장 분석해줘"
```

**완료!** Steve (Explorer)가 RAG로 패턴을 검색하고, Cursor LLM이 직접 분석합니다. (비용 $0)

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

## 🧮 Estimator (Fermi) Agent (v7.7.0)

UMIS는 **5-Phase 추정 시스템**을 제공합니다:

### 5-Phase Architecture

```
Phase 0: Literal (프로젝트 데이터, <0.1초)
  ↓ 없음
Phase 1: Direct RAG (학습 규칙, <0.5초)
  ↓ 없음
Phase 2: Validator (확정 데이터, <1초) ⭐ 85% 처리!
  ↓ 없음
Phase 3: Guestimation (11 Sources, 3-8초)
  ↓ conf < 0.80
Phase 4: Fermi Decomposition (Step 1-4, 10-30초)
  ├─ Step 1: 초기 스캔
  ├─ Step 2: 모형 생성
  ├─ Step 3: 실행 가능성 체크
  └─ Step 4: 모형 실행
```

### 사용 예시

```bash
# Cursor Composer
"@Fermi, B2B SaaS Churn Rate는?"

# 자동으로 Phase 0→1→2→3→4 시도
# Phase 2 (Validator)에서 85% 처리!
# 비용: $0 (Native 모드)
```

### v7.7.0 주요 특징
- ✅ **Native 모드**: Cursor LLM 직접 사용 (비용 $0)
- ✅ **Phase/Step 명확화**: 혼란 해결
- ✅ **100% 커버리지**: 실패율 0%
- ✅ **학습 시스템**: 사용할수록 빠름 (6-16배)
- ❌ **3-Tier Deprecated**: 5-Phase로 대체

**상세**: [umis_core.yaml](umis_core.yaml) (Line 609-743)

---

## ⚠️ Deprecated (v7.5.0+)

**Guestimation / Domain Reasoner** → **Estimator Agent로 완전 대체**

```
Before (v7.2.x):
  - Guestimation (빠른 추정)
  - Domain Reasoner (정밀 분석)

After (v7.7.0):
  - Estimator 5-Phase (통합)
  - Phase 0-4로 모든 경우 처리
  - 단일 인터페이스
```

**이유**: 역할 중복 제거, 일관성 확보, Single Source of Truth

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
