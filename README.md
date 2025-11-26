# UMIS - Universal Market Intelligence System

[![GitHub](https://img.shields.io/badge/GitHub-umis-blue?logo=github)](https://github.com/kangminlee-maker/umis)
[![Version](https://img.shields.io/badge/version-7.11.0-green)](https://github.com/kangminlee-maker/umis/releases)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

> **"불확실성을 기회로 전환하는 시장 분석 시스템"**

---

## 🎯 UMIS란?

AI 에이전트 6명이 협업하여 시장을 분석하는 **RAG 기반 프레임워크** (v7.11.0)

### 핵심 특징
- ✅ **6-Agent 협업**: Observer, Explorer, Quantifier, Validator, Guardian, **Estimator**
- ✅ **Native 모드**: Cursor LLM 직접 사용, 비용 $0
- ✅ **4-Stage Fusion**: Evidence → Prior → Fermi → Fusion ⭐ v7.11.0
- ✅ **재귀 없음**: max_depth=2, 속도 3-10배 향상 ⭐ v7.11.0
- ✅ **RAG 지식 활용**: 54개 검증된 패턴/사례 자동 검색
- ✅ **Budget 기반 탐색**: 자원 명시적 제어 ⭐ v7.11.0
- ✅ **완전한 추적성**: 모든 결론 → 원본 데이터 역추적
- ✅ **재검증 가능**: Excel 함수, YAML 스키마
- ✅ **코딩 불필요**: Cursor Composer만으로 사용

### v7.11.0 주요 기능 (최신) ⭐⭐⭐
- 🎊 **4-Stage Fusion Architecture**: Phase 0-4 (5단계) → Stage 1-4 (4단계) (v7.11.0)
- 🚀 **재귀 제거**: Phase 4 재귀 로직 완전 제거, 속도 3-10배 향상 (v7.11.0)
- 📊 **Budget 기반 탐색**: max_llm_calls, max_runtime 명시적 제한 (v7.11.0)
- 🎯 **용어 개선**: phase → source, confidence → certainty (v7.11.0)
- ✅ **하위 호환성**: Graceful Deprecation (compat.py) (v7.11.0)
- ⚡ **Early Return**: Stage 1에서 확정값 발견 시 즉시 반환 (v7.11.0)

### 이전 버전 주요 기능

**v7.7.0**:
- Native 모드 진짜 구현 (비용 $0)
- 5-Phase Architecture 명확화
- Phase/Step 용어 체계 확립

**v7.6.2**:
- Validator 우선 검색 (85%)
- Boundary Intelligence
- Web Search 추가

**v7.5.0**:
- Estimator/Quantifier 분리 (MECE)
- Single Source of Truth
- Learning System

**v7.0.0**:
- 6-Agent 시스템 완성
- RAG v3.0 (4-Layer)
- Knowledge Graph

---

## 💡 독특한 사용 방식

UMIS는 **전통적인 CLI나 GUI 대신 Cursor IDE를 인터페이스로 활용**합니다.

### 왜 Cursor를?

기존 도구들:
- ❌ **CLI**: 명령어 외우기 어려움, 결과 시각화 불편
- ❌ **GUI**: 개발 비용 높음, 복잡한 분석 표현 한계
- ❌ **Jupyter**: 코드 작성 필요, 재현성 낮음

**UMIS + Cursor**:
- ✅ **자연어로 대화**: `"@Explorer, 구독 모델 패턴 찾아줘"`
- ✅ **컨텍스트 유지**: 이전 대화 기억, 연속 작업 가능
- ✅ **자동화**: `.cursorrules`로 반복 작업 자동화
- ✅ **결과 저장**: Markdown/Excel/YAML 자동 생성
- ✅ **비용 $0**: Native 모드 (Cursor LLM 직접 사용)

### 실제 사용 흐름

```
1. Cursor Composer 열기 (Cmd+I / Ctrl+I)
2. umis.yaml 첨부 (@umis.yaml)
3. 자연어로 요청:
   "@Steve, 음악 스트리밍 시장 분석해줘"
4. Steve (Explorer)가 RAG 검색 → 패턴 발견 → 분석
5. 결과를 Markdown/Excel로 저장
6. 추가 질문: "@Bill, SAM 계산해줘"
7. Bill (Quantifier)이 계속 이어서 작업
```

### 코딩 불필요

```
비개발자도 사용 가능:
- Python 코드 작성 X
- API 호출 X
- 데이터 처리 X

→ 오직 대화만!
```

### 설정 한 번, 평생 사용

```bash
# 최초 1회 설정 (5분)
python setup/setup.py

# 이후 사용
Cmd+I → @umis.yaml → 대화 시작
```

**TL;DR**: UMIS는 Cursor가 읽는 지식 저장소입니다. CLI/GUI가 아니라 **AI 협업 도구**입니다.

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
"@Explorer, 구독 모델 패턴 찾아줘"  (Native 모드)
"@Fermi, B2B SaaS Churn은?" (v7.11.0 - 4-Stage Fusion)
"@Validator, 확정 데이터 있나요?" (85% 처리)
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

## 🧮 Estimator (Fermi) Agent (v7.11.0)

UMIS는 **4-Stage Fusion Architecture**를 제공합니다:

### 4-Stage Fusion Architecture (v7.11.0)

```
Stage 1: Evidence Collection (증거 수집, <1초)
  ├─ Literal (프로젝트 데이터)
  ├─ Direct RAG (학습 규칙)
  ├─ Validator Search (확정 데이터, 85% 처리!)
  └─ Guardrail Engine (제약 수집)
  ↓ Early Return (확정값 발견 시 즉시 반환)

Stage 2: Generative Prior (생성적 사전, ~3초)
  └─ LLM 직접 값 요청 + Certainty (high/medium/low)
  ↓ certainty == high

Stage 3: Structural Explanation (구조적 설명, ~5초)
  └─ Fermi 분해 (재귀 없음, max_depth=2)
  ↓

Stage 4: Fusion & Validation (융합, <1초)
  └─ 모든 Stage 결과 가중 합성
```

### v7.11.0 핵심 변경 사항

#### 재귀 제거 ✅
- **Before (v7.10.2)**: Phase 4 재귀 (max_depth=4, 10-30초)
- **After (v7.11.0)**: Stage 3 Fermi (max_depth=2, 3-5초)
- **속도 향상**: 3-10배

#### Budget 기반 탐색 ✅
```python
from umis_rag.agents.estimator.common import create_standard_budget

budget = create_standard_budget()  # max_llm_calls=10
result = estimator.estimate(question, budget=budget)
```

#### 용어 개선 ✅
| 이전 | v7.11.0 | 의미 |
|------|---------|------|
| `phase` (0-4) | `source` (Literal, Prior, Fermi, Fusion) | 추정 소스 |
| `confidence` (0.0-1.0) | `certainty` (high/medium/low) | LLM 내부 확신도 |

### 사용 예시

```bash
# Cursor Composer
"@Fermi, B2B SaaS Churn Rate는?"

# 자동으로 Stage 1 → 2 → 3 → 4 진행
# Stage 1 (Evidence)에서 85% 처리!
# 비용: $0 (Native 모드)
```

### v7.11.0 주요 특징
- ✅ **재귀 제거**: 속도 3-10배 향상
- ✅ **Budget 기반 탐색**: 자원 명시적 제어
- ✅ **Early Return**: Stage 1에서 확정값 발견 시 즉시 반환
- ✅ **Certainty**: LLM 내부 확신도 (high/medium/low)
- ✅ **하위 호환성**: compat.py를 통한 Graceful Deprecation

**상세**: 
- [API 문서](docs/api/ESTIMATOR_API_v7_11_0.md)
- [User Guide](docs/guides/ESTIMATOR_USER_GUIDE_v7_11_0.md)
- [Migration Plan](dev_docs/improvements/PHASE_TO_STAGE_MIGRATION_PLAN_v7_11_0.md)

---

## ⚠️ Deprecated (v7.11.0)

**Phase 3-4 Architecture** → **Stage 2-3 Fusion Architecture로 완전 대체**

```
Before (v7.10.2):
  - Phase 0-4 (5단계)
  - Phase 4 재귀 (max_depth=4)
  - Phase3Config/Phase4Config
  - confidence (0.0-1.0)

After (v7.11.0):
  - Stage 1-4 (4단계)
  - Stage 3 Fermi (max_depth=2, 재귀 없음)
  - Budget (max_llm_calls, max_runtime)
  - certainty (high/medium/low)
```

**마이그레이션**:
- `Phase3Guestimation` → `PriorEstimator` (Stage 2)
- `Phase4FermiDecomposition` → `FermiEstimator` (Stage 3)
- 하위 호환성 제공 (compat.py, DeprecationWarning)

**이유**: 재귀 제거, 속도 향상 (3-10배), 예측 가능성 개선

---

## 📚 문서

### 시작하기
- **[INSTALL.md](docs/INSTALL.md)** - 설치 가이드
- **[setup/START_HERE.md](setup/START_HERE.md)** - 30초 빠른 시작
- **[umis.yaml](umis.yaml)** - 메인 가이드라인 (Cursor 첨부용)

### Estimator v7.11.0 (신규)
- **[ESTIMATOR_API_v7_11_0.md](docs/api/ESTIMATOR_API_v7_11_0.md)** - API 문서 ⭐
- **[ESTIMATOR_USER_GUIDE_v7_11_0.md](docs/guides/ESTIMATOR_USER_GUIDE_v7_11_0.md)** - 사용자 가이드 ⭐
- **[V7_11_0_MIGRATION_COMPLETE.md](dev_docs/improvements/V7_11_0_MIGRATION_COMPLETE.md)** - 마이그레이션 완료 보고서

### 이해하기
- **[UMIS_ARCHITECTURE_BLUEPRINT.md](UMIS_ARCHITECTURE_BLUEPRINT.md)** - 전체 아키텍처
- **[FOLDER_STRUCTURE.md](docs/FOLDER_STRUCTURE.md)** - 폴더 구조
- **[CURRENT_STATUS.md](CURRENT_STATUS.md)** - 현재 상태
- **[CHANGELOG.md](CHANGELOG.md)** - 버전 변경 이력

### 커스터마이징
- **[config/agent_names.yaml](config/agent_names.yaml)** - Agent 이름 변경
- **[.cursorrules](.cursorrules)** - Cursor 자동화 규칙
- **[config/model_configs.yaml](config/model_configs.yaml)** - Stage별 모델 설정 (v7.11.0)

---

## 🚀 성능 개선 (v7.11.0)

### 속도 향상
- **Phase 4 재귀 (v7.10.2)**: 10-30초
- **Stage 3 Fermi (v7.11.0)**: 3-5초
- **속도 향상**: 3-10배

### 비용 절감
- **재귀 제거**: LLM 호출 횟수 평균 50% 감소
- **Budget 기반**: max_llm_calls 명시적 제한

### 예측 가능성 향상
- **재귀 없음**: max_depth=2 고정
- **실행 시간 예측 가능**: Stage별 명확한 시간 제한

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

**UMIS Team • 2025 • v7.11.0 Fusion Architecture**
