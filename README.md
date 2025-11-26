# UMIS - Universal Market Intelligence System

[![GitHub](https://img.shields.io/badge/GitHub-umis-blue?logo=github)](https://github.com/kangminlee-maker/umis)
[![Version](https://img.shields.io/badge/version-7.11.0-green)](https://github.com/kangminlee-maker/umis/releases)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

> **"불확실성을 기회로 전환하는 시장 분석 시스템"**

---

## 🎯 UMIS란?

**AI 에이전트 6명이 협업하여 시장을 분석하는 RAG 기반 프레임워크**

UMIS는 불확실한 시장 상황에서 근거 있는 판단을 내리기 위한 **체계적 사고 시스템**입니다. 단순한 데이터 분석 도구가 아니라, 시장을 이해하고 기회를 발견하며 가치를 추정하는 **전체 프로세스를 자동화**합니다.

### 해결하는 문제

기존 시장 분석의 어려움:
- ❌ **데이터 부족**: "이 시장 규모는 얼마지?" → 공개 데이터 없음
- ❌ **불확실성**: "이 기회가 진짜 가치 있나?" → 검증 방법 모름
- ❌ **추적 불가**: "이 수치 어디서 나왔지?" → 출처 불명
- ❌ **재현 불가**: "같은 분석 다시 하려면?" → 처음부터 다시
- ❌ **높은 진입장벽**: 시장 분석 = 전문가 영역

UMIS의 접근:
- ✅ **데이터 부족 해결**: 54개 검증된 패턴/사례로 유추 → Validator가 크로스체크
- ✅ **불확실성 정량화**: 모든 판단에 certainty (high/medium/low) 명시
- ✅ **완전한 추적성**: 모든 결론 → 원본 데이터/RAG 패턴 역추적 가능
- ✅ **재현 가능성**: YAML 스키마 + Excel 함수로 프로세스 재실행
- ✅ **진입장벽 제거**: 코딩 불필요, 자연어 대화만으로 사용

### 핵심 철학

1. **"모든 판단에는 근거가 있어야 한다"**
   - 추측이 아니라 **근거 기반 추론**
   - 모든 수치에 source (출처) 명시

2. **"불확실성을 인정하고 명시한다"**
   - "확실하다"는 착각 대신 **certainty 수준 제시**
   - 확신도가 낮으면 → 추가 검증 자동 제안

3. **"프로세스를 재현 가능하게 만든다"**
   - Excel 함수로 계산 추적
   - YAML로 분석 과정 저장
   - 누구나 같은 결과를 재현 가능

---

## 🤖 6명의 AI 전문가

UMIS는 6개의 전문 Agent가 **역할을 명확히 분담**하여 협업합니다:

| Agent | 역할 | 주요 작업 | 예시 |
|-------|------|-----------|------|
| **Albert (Observer)** | 시장 구조 관찰 | 가치사슬, 비효율 감지 | "음악 스트리밍 시장의 3계층 구조 관찰" |
| **Steve (Explorer)** | 기회 발굴 | 54개 패턴 매칭, 가설 생성 | "구독 모델 + Counter-Positioning 패턴 발견" |
| **Bill (Quantifier)** | 시장 규모 계산 | SAM/TAM 4가지 방법, 성장률 | "한국 음악 스트리밍 SAM: 5,200억원" |
| **Rachel (Validator)** | 데이터 검증 | 출처 확인, Gap 분석 | "85% 케이스에서 확정 데이터 제공" |
| **Stewart (Guardian)** | 품질 관리 | 순환 감지, 목표 정렬 | "같은 질문 3회 반복 → 방향 전환 제안" |
| **Fermi (Estimator)** | 값 추정 | 4-Stage Fusion, 재귀 없음 | "B2B SaaS Churn: 5-8% (certainty: high)" |

### Agent 간 협업 흐름

```
1. 프로젝트 시작
   └─ Stewart (Guardian): 목표 명확도 평가
   
2. 시장 구조 이해
   └─ Albert (Observer): 가치사슬 분석
      └─ Bill (Quantifier): 구조 관련 정량 데이터 지원
      └─ Rachel (Validator): 데이터 검증

3. 기회 발굴
   └─ Steve (Explorer): RAG 패턴 검색 → 가설 생성
      └─ Bill: 수익성 검증
      └─ Rachel: 사례 데이터 확인

4. 가치 추정
   └─ Fermi (Estimator): 4-Stage 추정
      └─ Rachel: 확정 데이터 우선 제공 (85%)
      └─ Bill: Benchmark 데이터 제공

5. 최종 검증
   └─ Stewart: 품질 평가 + 일관성 체크
```

**특징**:
- 각 Agent는 **명확한 책임 영역** (MECE)
- 필요 시 **다른 Agent 호출** (상호 협력)
- 모든 판단은 **근거 기반** (추측 금지)

---

## ✨ 핵심 특징

### 1. RAG 기반 지식 활용

**54개 검증된 패턴/사례 자동 검색**:
- 31개 비즈니스 모델 패턴 (구독, 프리미엄, 마켓플레이스 등)
- 23개 파괴적 혁신 패턴 (Counter-Positioning, 7 Powers 등)
- 실제 사례 데이터 (Netflix, Spotify, Zoom 등)

**작동 방식**:
```
사용자: "@Steve, 음악 스트리밍 시장 분석해줘"

→ Steve (Explorer)가 RAG 검색:
  - "구독 모델" 패턴 발견
  - "3계층 가치사슬" 패턴 매칭
  - Netflix, Spotify 유사 사례 검색

→ 54개 패턴 중 관련 있는 8개 자동 선별
→ 각 패턴의 트리거 시그널 확인
→ 현재 시장에 적용 가능성 분석
```

### 2. 완전한 추적성 (Full Traceability)

**모든 결론을 원본 데이터까지 역추적**:
```yaml
# 예시: Excel 자동 생성
B2B SaaS Churn Rate: 5-8%
  ├─ source: Validator (확정 데이터)
  ├─ certainty: high
  ├─ 근거: 
  │   └─ data_sources_registry.yaml > business_metrics > churn_rate
  │       └─ "SaaS Capital Index 2023: 5-7%"
  ├─ 검증:
  │   └─ Cross-check: OpenView Partners (6-8%)
  └─ Excel 함수:
      =VLOOKUP("churn_rate", data_sources, 2)
```

**재현 가능성**:
- Excel에서 수식 클릭 → 원본 데이터 확인
- YAML 파일 열기 → 출처 URL 직접 접근
- 다른 사람이 같은 프로세스 재실행 가능

### 3. Native 모드 (Cursor 인터페이스 그대로 활용)

**핵심 장점: 별도 프로그램 설치 없이 Cursor에서 바로 사용**:
```bash
# .env 설정
LLM_MODE=cursor

# 사용
Cursor Composer (Cmd+I):
"@Steve, 시장 분석해줘"

→ Cursor의 UI/UX 그대로 활용
→ 새로운 프로그램 설치 불필요
→ 커스터마이징 용이 (Cursor Rules, @mentions)
→ 비용: $0 (Cursor 구독에 포함)
```

**External 모드와 비교**:
| 항목 | Native (Cursor) | External (OpenAI/Anthropic) |
|------|-----------------|------------------------------|
| 사용성 | ✅ Cursor 인터페이스 그대로 | 별도 API 설정 필요 |
| 설치 | ✅ 추가 설치 불필요 | API Key 설정 |
| 커스터마이징 | ✅ Cursor Rules, @mentions | 프로그래밍 필요 |
| 비용 | $0 (Cursor 구독) | $0.01-0.10 per request |
| 자동화 | 불가 (수동 실행) | 가능 (스크립트) |

### 4. Estimator: 4-Stage Fusion Architecture (v7.11.0)

**데이터가 없을 때 값을 추정하는 시스템**:

```
Stage 1: Evidence Collection (증거 수집, <1초)
  ├─ Literal: 프로젝트 데이터 확인
  ├─ RAG: 학습된 규칙 검색
  ├─ Validator: 확정 데이터 검색 (85% 처리!)
  └─ Guardrail: 논리적/경험적 제약 수집
  ↓ Early Return (확정값 발견 시 즉시 반환)

Stage 2: Generative Prior (생성적 사전, ~3초)
  └─ LLM에게 직접 값 요청 + certainty 평가
  ↓ certainty == high → 종료

Stage 3: Structural Explanation (구조적 설명, ~5초)
  └─ Fermi 분해 (재귀 없음, max_depth=2)
     - 변수 식별 → Stage 2로 각 변수 추정 → 공식 계산
  ↓

Stage 4: Fusion & Validation (융합, <1초)
  └─ 모든 Stage 결과를 가중 합성 → 최종 값
```

**예시**:
```
질문: "B2B SaaS Churn Rate는?"

Stage 1 (Evidence):
  - Validator 검색 → "SaaS Capital: 5-7%" 발견
  - certainty: high
  - Early Return: 즉시 반환 (Stage 2-3 스킵)

결과: 5-7% (source: Validator, certainty: high, 시간: 0.3초)
```

**특징**:
- ✅ **재귀 없음**: 속도 3-10배 향상 (10-30초 → 3-5초)
- ✅ **Budget 기반**: max_llm_calls, max_runtime 명시적 제어
- ✅ **Early Return**: 85% 케이스에서 Stage 1에서 종료
- ✅ **Certainty**: LLM 내부 확신도 (high/medium/low)

### 5. 코딩 불필요

**자연어 대화만으로 사용**:
```
비개발자도 사용 가능:
- Python 코드 작성 X
- API 호출 X
- 데이터 처리 X

→ 오직 대화만!

예시:
"@Steve, 구독 모델 패턴 찾아줘"
"@Fermi, B2B SaaS ARPU는?"
"@Bill, SAM 계산해줘"
```

---

## 💡 독특한 사용 방식: Cursor를 인터페이스로

UMIS는 **전통적인 CLI나 GUI가 아니라 Cursor IDE를 인터페이스로 활용**합니다.

### 왜 Cursor를?

| 기존 도구 | 문제점 | UMIS + Cursor | 장점 |
|----------|--------|---------------|------|
| CLI | 명령어 외우기 어려움 | 자연어 대화 | "@Steve, 시장 분석해줘" |
| GUI | 개발 비용 높음 | 설정 불필요 | Cursor만 있으면 OK |
| Jupyter | 코드 작성 필요 | 코딩 불필요 | 대화만으로 분석 |

### 실제 사용 예시

```bash
# 1. Cursor Composer 열기 (Cmd+I)
# 2. umis.yaml 첨부 (@umis.yaml)
# 3. 자연어로 요청

"@Steve, 음악 스트리밍 시장 분석해줘"
→ Steve (Explorer)가 RAG 패턴 검색 → 분석 → Markdown 저장

"@Bill, SAM 계산해줘"
→ Bill (Quantifier)이 4가지 방법으로 계산 → Excel 생성

"@Fermi, Churn Rate는?"
→ Fermi (Estimator)가 4-Stage 추정 → 근거 포함 반환
```

**TL;DR**: CLI/GUI가 아니라 **AI 협업 도구**. Cursor가 UMIS 지식을 읽고 대화하는 방식.

---

## 📦 빠른 시작

### 1. Clone

```bash
git clone https://github.com/kangminlee-maker/umis.git
cd umis
```

### 2. 설치 (최초 1회, 5분)

```bash
python setup/setup.py

# 자동으로:
# - 패키지 설치
# - .env 생성 (API Key 입력 필요)
# - RAG Collections 구축 (5분)
```

**필요**: OpenAI API Key (RAG 구축용, 최초 1회, 비용 ~$1-2)

### 3. 사용 (Native 모드, 비용 $0)

```bash
# .env 파일 설정
LLM_MODE=cursor  # Native 모드 (Cursor LLM 사용, 비용 $0)

# Cursor Composer 열기 (Cmd+I)
# umis.yaml 첨부 (@umis.yaml)
# 대화 시작:

"@Steve, 음악 스트리밍 시장 분석해줘"
```

**완료!** Steve가 RAG 패턴을 검색하고, Cursor LLM이 분석합니다. (비용 $0)

**상세**: [INSTALL.md](docs/INSTALL.md) 참조

---

## 🤖 Agent 커스터마이징

`config/agent_names.yaml` 파일 수정:

```yaml
# 기본 이름
explorer: Steve
quantifier: Bill

# 커스텀 이름으로 변경 (1줄만 수정!)
explorer: Alex
quantifier: 탐색자
```

사용:
```bash
"@Alex, 기회 찾아봐"  # Alex (Explorer) 호출
"@탐색자, SAM 계산해줘"  # 탐색자 (Quantifier) 호출
```

**양방향 매핑**: @Alex ↔ Explorer (자동 변환)

---

## 📚 문서

### 시작하기
- **[INSTALL.md](docs/INSTALL.md)** - 설치 가이드
- **[setup/START_HERE.md](setup/START_HERE.md)** - 30초 빠른 시작
- **[umis.yaml](umis.yaml)** - 메인 가이드라인 (Cursor 첨부용)

### 핵심 문서
- **[UMIS_ARCHITECTURE_BLUEPRINT.md](docs/architecture/UMIS_ARCHITECTURE_BLUEPRINT.md)** - 전체 아키텍처
- **[FOLDER_STRUCTURE.md](docs/FOLDER_STRUCTURE.md)** - 폴더 구조
- **[CHANGELOG.md](CHANGELOG.md)** - 버전 변경 이력

### Agent별 가이드
- **Observer (Albert)**: [observer_guide.md](docs/agents/observer_guide.md)
- **Explorer (Steve)**: [explorer_guide.md](docs/agents/explorer_guide.md)
- **Quantifier (Bill)**: [quantifier_guide.md](docs/agents/quantifier_guide.md)
- **Validator (Rachel)**: [validator_guide.md](docs/agents/validator_guide.md)
- **Guardian (Stewart)**: [guardian_guide.md](docs/agents/guardian_guide.md)
- **Estimator (Fermi)**: [ESTIMATOR_API_v7_11_0.md](docs/api/ESTIMATOR_API_v7_11_0.md) ⭐ v7.11.0

### 커스터마이징
- **[config/agent_names.yaml](config/agent_names.yaml)** - Agent 이름 변경
- **[.cursorrules](.cursorrules)** - Cursor 자동화 규칙
- **[config/model_configs.yaml](config/model_configs.yaml)** - Stage별 모델 설정

---

## 🆕 v7.11.0 업데이트 (2025-11-26)

### 주요 변경사항

#### 1. 4-Stage Fusion Architecture
- **Before**: Phase 0-4 (5단계)
- **After**: Stage 1-4 (4단계)
- **이유**: 개념적 명확성, 속도 향상

#### 2. 재귀 제거
- **Before**: Phase 4 재귀 (max_depth=4, 10-30초)
- **After**: Stage 3 Fermi (max_depth=2, 재귀 없음, 3-5초)
- **속도 향상**: 3-10배

#### 3. Budget 기반 탐색
```python
from umis_rag.agents.estimator.common import create_standard_budget

budget = create_standard_budget()  # max_llm_calls=10
result = estimator.estimate(question, budget=budget)
```

#### 4. 용어 개선
| 이전 | v7.11.0 | 의미 |
|------|---------|------|
| `phase` (0-4) | `source` (Literal/Prior/Fermi/Fusion) | 추정 소스 |
| `confidence` (0.0-1.0) | `certainty` (high/medium/low) | LLM 내부 확신도 |

#### 5. 성능 개선
- **속도**: 3-10배 향상 (10-30초 → 3-5초)
- **비용**: LLM 호출 평균 50% 감소
- **예측 가능성**: 실행 시간 예측 가능 (max_depth=2 고정)

### v7.11.0 문서
- **[ESTIMATOR_API_v7_11_0.md](docs/api/ESTIMATOR_API_v7_11_0.md)** - API 문서
- **[ESTIMATOR_USER_GUIDE_v7_11_0.md](docs/guides/ESTIMATOR_USER_GUIDE_v7_11_0.md)** - 사용자 가이드
- **[V7_11_0_MIGRATION_COMPLETE.md](dev_docs/improvements/V7_11_0_MIGRATION_COMPLETE.md)** - 마이그레이션 완료 보고서

### Deprecated (v7.11.0)
- ~~Phase 3-4 Architecture~~ → Stage 2-3 Fusion Architecture로 대체
- ~~Phase3Config/Phase4Config~~ → Budget로 대체
- 하위 호환성 제공 (compat.py, DeprecationWarning)

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
