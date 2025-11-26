# UMIS Native 모드 사용 가이드

**v7.11.1 업데이트: LLM Complete Abstraction & Stage 기반 아키텍처** ✅

---

## 📋 목차

1. [개요](#개요)
2. [Native vs External 모드](#native-vs-external-모드)
3. [설정 방법](#설정-방법)
4. [사용 방법](#사용-방법)
5. [비용 비교](#비용-비교)
6. [FAQ](#faq)

---

## 개요

### 문제점 (v7.10.2 이전)

```yaml
# .env 파일
LLM_MODE=cursor  # "Native 모드" 설정

# 하지만...
# 비즈니스 로직에 llm_mode 분기가 61개나 산재
# → 유지보수 어려움
# → 버그 발생 가능
# → 아키텍처 복잡도 증가
```

### 해결 (v7.11.1)

**LLM Complete Abstraction & Stage 기반 아키텍처!**

- **Native 모드 (cursor)**: Cursor LLM 직접 사용 → API 호출 없음, 비용 $0
- **External 모드 (external)**: OpenAI/Anthropic API → 완전 자동화 가능
- **LLM Provider 추상화**: 비즈니스 로직에서 llm_mode 분기 완전 제거
- **4-Stage Fusion Architecture**: Evidence → Prior → Fermi → Fusion

---

## Native vs External 모드

### Native 모드 (cursor) - 권장

**개념 (v7.11.1):**
- `CursorLLMProvider` 사용 → API 호출 없음
- Cursor의 UI/UX 그대로 활용
- **LLM 작업을 Cursor에게 위임**
- 로그 포맷팅 전용 (프롬프트 생성 없음)

**장점:**
- ✅ **비용 $0** (Cursor 구독에 포함)
- ✅ Cursor UI/UX 그대로 활용
- ✅ 추가 프로그램 설치 불필요
- ✅ 커스터마이징 용이 (Cursor Rules, @mentions)
- ✅ 최고 품질 (Claude Sonnet 4.5 등)

**단점:**
- ❌ 자동화 불가 (사용자 참여 필요)
- ❌ 배치 처리 불가
- ❌ 수동 실행만 가능

**사용 시나리오:**
- 일회성 시장 분석
- 탐색적 분석
- Interactive 작업
- Cursor Composer 활용

---

### External 모드 (external)

**개념 (v7.11.1):**
- `ExternalLLMProvider` 사용 → API 호출
- `ModelRouter`로 Stage별 모델 자동 선택
- OpenAI/Anthropic API 활용
- **완전 자동화된 워크플로우**

**장점:**
- ✅ 완전 자동화 가능
- ✅ 배치 처리 가능
- ✅ Cursor 독립 실행
- ✅ Stage별 최적 모델 선택 (config/model_configs.yaml)
- ✅ 스크립트 기반 워크플로우

**단점:**
- ❌ API 비용 발생 (~$0.01-0.10/요청)
- ❌ API Key 설정 필요
- ❌ 프로그래밍 지식 필요

**사용 시나리오:**
- 자동화 필요 (cron job)
- 대량 분석 (100개 이상)
- Cursor 없이 실행
- CI/CD 파이프라인 통합

---

## 설정 방법

### 1단계: .env 파일 설정

```bash
# .env 파일 (프로젝트 루트)

# Native 모드 (권장) - v7.11.1
LLM_MODE=cursor

# 또는 External 모드 (자동화 필요 시)
LLM_MODE=external
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key  # 선택사항
```

**중요 (v7.11.1):**
- `LLM_MODE` 값은 `cursor` 또는 `external`만 허용
- 특정 모델명 (예: `gpt-4o-mini`) 사용 불가
- Stage별 모델 선택은 `config/model_configs.yaml`에서 설정

### 2단계: 확인

```python
# Python으로 모드 확인
python -c "import umis_rag; print(f'LLM Mode: {umis_rag.get_llm_mode()}')"
```

**Native 모드 출력 예시:**

```
📊 현재 모드 정보:
  - 모드: native
  - API 사용: False
  - 비용: $0 (Cursor 구독 포함)
  - 자동화: False
  - 설명: RAG 검색만 수행 → Cursor LLM이 분석

🎯 Native 모드 결과:
  - 모드: native
  - 매칭 패턴 수: 2
  - 성공 사례 수: 0

📋 Cursor LLM 지시사항:
위 RAG 검색 결과(rag_context)를 바탕으로 기회 가설을 생성해주세요.

포함할 내용:
1. Observer 관찰 요약
2. 매칭된 패턴 분석
3. 유사 성공 사례 시사점
4. 기회 가설 3-5개 (구조화)
5. 각 가설의 검증 방향

💬 다음 단계:
Cursor Composer/Chat에서 위 instruction을 따라 분석하세요.
```

---

## 사용 방법

### Native 모드 워크플로우

#### 1단계: RAG 검색 (Python)

```python
from umis_rag.agents.explorer import ExplorerRAG

# Explorer 초기화
explorer = ExplorerRAG()

# 패턴 검색
trigger_signals = "구독 모델, 고객 유지, 정기 수익"
results = explorer.search_patterns(trigger_signals, top_k=3)

# 가설 생성 (Native 모드)
hypothesis = explorer.generate_opportunity_hypothesis(
    observer_observation="음악 스트리밍 시장 관찰...",
    matched_patterns=[doc for doc, _ in results],
    success_cases=[]
)

# 결과는 Dict (RAG 컨텍스트 + 지시사항)
print(hypothesis['instruction'])
print(hypothesis['rag_context'][:500])
```

#### 2단계: Cursor LLM 분석

Cursor Composer 또는 Chat에서:

```
위 RAG 검색 결과를 바탕으로 음악 스트리밍 시장의 기회 가설 3개를 생성해주세요.

각 가설에는 다음을 포함:
1. 기회 설명
2. 근거 (패턴 매칭 결과 기반)
3. 타겟 고객
4. 검증 방향
```

Cursor LLM이 RAG 컨텍스트를 활용하여 가설을 생성합니다.

---

### External 모드 워크플로우

#### 1단계: RAG + API 호출 (Python)

```python
from umis_rag.agents.explorer import ExplorerRAG

# Explorer 초기화 (External 모드)
explorer = ExplorerRAG()

# 패턴 검색
results = explorer.search_patterns("구독 모델, 고객 유지", top_k=3)

# 가설 생성 (External 모드 - API 호출)
hypothesis = explorer.generate_opportunity_hypothesis(
    observer_observation="음악 스트리밍 시장 관찰...",
    matched_patterns=[doc for doc, _ in results],
    success_cases=[]
)

# 결과는 str (완성된 가설 Markdown)
print(hypothesis)
```

출력:

```markdown
# 음악 스트리밍 시장 기회 가설

## 가설 1: 아티스트 직접 구독 플랫폼
...완성된 가설...

## 가설 2: 커뮤니티 기반 큐레이션
...완성된 가설...
```

---

## 비용 비교

### 시장 분석 1회 기준

| 모드 | RAG 임베딩 | LLM 호출 | 총 비용 |
|------|-----------|---------|--------|
| **Native** | $0.0001 | $0 (Cursor) | **$0.0001** |
| **External** | $0.0001 | $0.10 | **$0.1001** |

### 100회 분석 기준

| 모드 | RAG 임베딩 | LLM 호출 | 총 비용 |
|------|-----------|---------|--------|
| **Native** | $0.01 | $0 | **$0.01** |
| **External** | $0.01 | $10 | **$10.01** |

**절감액: $10!**

---

## FAQ

### Q1. Native 모드에서 어떤 Agent가 영향을 받나요?

**A1. (v7.11.1 업데이트)**

- **Estimator (Fermi)**: LLM Provider 사용 ✅
  - Native (cursor): Stage 2-3에서 Cursor LLM 활용
  - External (external): Stage 2-3에서 API 호출 (ModelRouter)
  - Stage 1 (Evidence): LLM 없음 (RAG 검색만)
  - Stage 4 (Fusion): Sensor Fusion (수학적 계산)

- **Explorer (Steve)**: Native/External 분기 구현 ✅
  - Native: RAG 검색 → Cursor 처리
  - External: RAG + API → 완성된 가설

- **Observer (Albert)/Quantifier (Bill)/Validator (Rachel)**: RAG만 사용
  - LLM 사용 안 함 (모드 무관)

- **Guardian (Stewart)**: Meta-RAG + LLM Provider
  - Native/External 모두 지원

### Q2. 기존 External 모드 스크립트는 어떻게 하나요?

**A2. (v7.11.1 업데이트)**

기존 스크립트는 약간의 수정이 필요할 수 있습니다.

```bash
# v7.11.1: LLM_MODE 환경변수 사용
# .env 파일에서 LLM_MODE=external로 설정

LLM_MODE=external python scripts/your_script.py
```

**마이그레이션 필요 (v7.10.2 → v7.11.1):**
- `Phase3Guestimation` → `PriorEstimator`
- `Phase4FermiDecomposition` → `FermiEstimator`
- `llm_mode` 파라미터 → `llm_provider` 파라미터

자세한 내용: `docs/MIGRATION_GUIDE_v7_11_0.md`

### Q3. Native 모드의 성능은?

**A3.**

사용자가 선택한 Cursor Agent 모델 성능을 그대로 사용합니다.

- Claude Sonnet 4.5: External GPT-4보다 우수
- GPT-4o: External GPT-4 Turbo와 유사 또는 우수

### Q4. 완전 오프라인 가능한가요?

**A4.**

불가능합니다.

- RAG 임베딩은 OpenAI API 필요 (저렴)
- 대안: Local Embeddings (Sentence Transformers)
  - 하지만 품질 저하 가능

### Q5. 언제 External 모드를 사용해야 하나요?

**A5.**

다음과 같은 경우에만:

- 매일 자동으로 100개 시장 분석
- cron job으로 주간 리포트 생성
- Cursor 없이 독립 실행 필요

일반적인 사용에는 Native 모드 권장!

---

## 구현 내역

### v7.11.1 (2025-11-26) - 최신

**LLM Complete Abstraction:**

1. `umis_rag/core/llm_interface.py`
   - `BaseLLM`: 모든 LLM 작업의 기본 인터페이스
   - `LLMProvider`: LLM 제공자 추상화

2. `umis_rag/core/llm_provider_factory.py`
   - `CursorLLMProvider`: Native 모드 구현
   - `ExternalLLMProvider`: External 모드 구현
   - Singleton 패턴으로 Provider 관리

3. `umis_rag/core/model_router.py`
   - Stage별 LLM 모델 자동 선택
   - `config/model_configs.yaml` 기반
   - TaskType별 파라미터 오버라이드

**Terminology Consistency:**

1. `literal_source.py`, `rag_source.py`, `validator_source.py`
   - 이전: `Phase0Literal`, `Phase1DirectRAG`, `Phase2ValidatorSearchEnhanced`
   - 변경: `LiteralSource`, `RAGSource`, `ValidatorSource`
   - Evidence Collector (Stage 1) 내부 구성 요소

**Legacy Cleanup:**

1. `compat.py` 제거
   - `Phase3Guestimation` → `PriorEstimator`
   - `Phase4FermiDecomposition` → `FermiEstimator`

### v7.11.0 (2025-11-26)

**4-Stage Fusion Architecture:**

1. Stage 1: Evidence Collection (`evidence_collector.py`)
2. Stage 2: Generative Prior (`prior_estimator.py`)
3. Stage 3: Structural Explanation (`fermi_estimator.py`)
4. Stage 4: Fusion & Validation (`fusion_layer.py`)

**LLM Abstraction 완료:**
- 61개 llm_mode 분기 → 0개 (100% 제거)
- DIP, SRP, OCP, ISP 원칙 준수
- Recursion 금지, Budget 기반 탐색

### v7.7.0 (2025-11-10) - 초기 구현

**Native 모드 구현:**
- `llm_provider.py` 도입
- Native/External 분기 처리

---

## 다음 단계

### Native 모드 (cursor) 사용

1. `.env` 파일에서 `LLM_MODE=cursor` 설정
2. Cursor Composer에서 `@umis.yaml` 활용
3. Agent 멘션: `@Steve, 시장 분석해줘`

### External 모드 (external) 사용

1. `.env` 파일에서 `LLM_MODE=external` 설정
2. API Key 설정 (OPENAI_API_KEY)
3. Python 스크립트 실행:

```python
from umis_rag.agents.estimator import EstimatorRAG

estimator = EstimatorRAG()
result = estimator.estimate("B2B SaaS ARPU는?")
print(result.value)
```

---

## 참고 문서

- `docs/architecture/LLM_ABSTRACTION_v7_11_0.md`: LLM 추상화 아키텍처
- `docs/architecture/LLM_STRATEGY.md`: LLM 전략
- `docs/MIGRATION_GUIDE_v7_11_0.md`: v7.11.0 마이그레이션 가이드
- `config/model_configs.yaml`: 모델 설정
- `env.template`: 환경변수 템플릿

---

**v7.11.1 - LLM Complete Abstraction & Terminology Consistency** ✅

