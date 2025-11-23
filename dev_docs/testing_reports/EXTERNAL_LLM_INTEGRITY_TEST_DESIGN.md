# UMIS External LLM 모드 무결성 테스트 설계

**버전**: v7.7.0  
**날짜**: 2025-11-21  
**목적**: UMIS 전체 시스템에서 External LLM 모드가 제대로 작동하는지 검증

---

## 📋 목차

1. [테스트 개요](#테스트-개요)
2. [테스트 범위](#테스트-범위)
3. [테스트 카테고리](#테스트-카테고리)
4. [테스트 시나리오](#테스트-시나리오)
5. [실행 방법](#실행-방법)
6. [예상 결과](#예상-결과)
7. [문제 해결](#문제-해결)

---

## 테스트 개요

### 배경

UMIS v7.7.0는 두 가지 LLM 모드를 지원합니다:

1. **Native Mode** (기본, 권장)
   - Cursor Agent LLM 사용
   - RAG 검색만 수행 → Cursor가 분석
   - 비용: $0 (Cursor 구독 포함)
   - 용도: 일회성 심층 분석

2. **External Mode** (자동화 필요 시)
   - OpenAI/Anthropic API 호출
   - RAG 검색 + API 호출 → 완성된 결과
   - 비용: 토큰당 과금
   - 용도: 대량 자동화, 배치 처리

### 목적

External 모드가 시스템 전체에서 **올바르게 구현**되었는지, **모든 컴포넌트에서 일관되게 작동**하는지 검증합니다.

### 참고 문서

- `config/llm_mode.yaml`: LLM 모드 정책
- `docs/architecture/UMIS_ARCHITECTURE_BLUEPRINT.md`: 시스템 아키텍처
- `umis.yaml`: UMIS 전체 가이드 (6,176줄)
- `umis_rag/core/llm_provider.py`: LLMProvider 구현

---

## 테스트 범위

### 포함 영역

✅ **1. 설정 계층**
- `.env` 파일 로딩
- `UMIS_MODE` 환경변수 검증
- OpenAI API Key 유효성
- Phase별 LLM 모델 설정

✅ **2. LLMProvider 계층**
- `LLMProvider.create_llm()` 동작
- Native/External 모드 감지
- 모드별 LLM 객체 생성

✅ **3. Model Router 계층**
- Phase별 모델 자동 선택 (0-4)
- Phase 0-2 → `gpt-4.1-nano`
- Phase 3 → `gpt-4o-mini`
- Phase 4 → `o1-mini`
- 비용 추정 로직

✅ **4. Agent 계층**
- **Explorer**: 패턴 검색 + 가설 생성
- **Estimator**: 5-Phase 추정 (Phase 4 LLM 호출)
- **Guardian**: 3-Stage 평가 (Stage 3 LLM 호출)
- **Projector**: 10% LLM 판단

✅ **5. API 연결**
- OpenAI API 연결 테스트
- 간단한 완성 테스트 (gpt-4o-mini)
- 재시도 로직 (Exponential backoff)
- Rate limiting (1.5초)

### 제외 영역

❌ **Native 모드**
- Native 모드는 별도 테스트 (`scripts/test_native_mode.py`)

❌ **전체 워크플로우 E2E**
- E2E는 별도 통합 테스트

❌ **실제 데이터 처리**
- 테스트는 가벼운 샘플만 사용

---

## 테스트 카테고리

### 1. 설정 테스트 (config)

| 테스트 ID | 테스트명 | 검증 항목 | 통과 조건 |
|----------|---------|----------|----------|
| C-01 | env_file_exists | `.env` 파일 존재 | 파일이 존재함 |
| C-02 | umis_mode_set | `UMIS_MODE=external` 설정 | `external`로 설정됨 |
| C-03 | openai_api_key | OpenAI API Key | `sk-`로 시작하는 유효한 키 |
| C-04 | llm_models | Phase별 LLM 모델 | 모든 Phase 모델 설정됨 |
| C-05 | phase_routing | Phase 라우팅 활성화 | `use_phase_based_routing` 확인 |

### 2. LLMProvider 테스트 (provider)

| 테스트 ID | 테스트명 | 검증 항목 | 통과 조건 |
|----------|---------|----------|----------|
| P-01 | create_llm_external | LLM 객체 생성 | `ChatOpenAI` 인스턴스 생성 |
| P-02 | mode_detection | 모드 감지 메서드 | `is_external_mode()` = True |
| P-03 | mode_info | 모드 정보 반환 | `mode='external'`, `uses_api=True` |

### 3. Model Router 테스트 (router)

| 테스트 ID | 테스트명 | 검증 항목 | 통과 조건 |
|----------|---------|----------|----------|
| R-01 | initialization | Router 초기화 | `ModelRouter()` 성공 |
| R-02 | phase_selection | Phase별 모델 선택 | Phase 0-2: 같은 모델, Phase 3/4: 다른 모델 |
| R-03 | cost_estimation | 비용 추정 | 평균 비용: $0.0001 - $0.01 범위 |

### 4. Explorer Agent 테스트 (explorer)

| 테스트 ID | 테스트명 | 검증 항목 | 통과 조건 |
|----------|---------|----------|----------|
| E-01 | initialization | Explorer 초기화 | `ExplorerRAG()` 성공 |
| E-02 | llm_mode | LLM 모드 설정 | `explorer.mode='external'`, `llm` 객체 존재 |
| E-03 | pattern_search | 패턴 검색 (RAG만) | 검색 결과 1개 이상 |

### 5. Estimator Agent 테스트 (estimator)

| 테스트 ID | 테스트명 | 검증 항목 | 통과 조건 |
|----------|---------|----------|----------|
| S-01 | initialization | Estimator 초기화 | `EstimatorRAG()` 성공 |
| S-02 | phase4_llm | Phase 4 LLM 준비 | `openai` 패키지 import 성공 |

### 6. 기타 Agent 테스트 (agents)

| 테스트 ID | 테스트명 | 검증 항목 | 통과 조건 |
|----------|---------|----------|----------|
| A-01 | guardian_evaluator | Guardian 3-Stage Evaluator | `llm` 객체 존재 |
| A-02 | hybrid_projector | Hybrid Projector | `llm` 객체 존재 |

### 7. API 연결 테스트 (api)

| 테스트 ID | 테스트명 | 검증 항목 | 통과 조건 |
|----------|---------|----------|----------|
| I-01 | openai_connection | OpenAI API 연결 | 모델 목록 조회 성공 |
| I-02 | simple_completion | 간단한 완성 | "1+1은?" → 응답 성공 |

---

## 테스트 시나리오

### 시나리오 1: 기본 설정 검증

**목표**: External 모드가 올바르게 설정되었는지 확인

**단계**:
1. `.env` 파일 존재 확인
2. `UMIS_MODE=external` 확인
3. `OPENAI_API_KEY` 유효성 확인
4. Phase별 LLM 모델 설정 확인

**예상 결과**: 모든 설정이 올바르게 로드됨

---

### 시나리오 2: LLMProvider 동작 검증

**목표**: LLMProvider가 External 모드에서 올바른 LLM 객체를 생성하는지 확인

**단계**:
1. `LLMProvider.create_llm()` 호출
2. 반환된 객체가 `ChatOpenAI` 인스턴스인지 확인
3. `is_external_mode()` = True 확인
4. `get_mode_info()` 반환값 확인

**예상 결과**: `ChatOpenAI` 객체가 생성되고, 모드 정보가 올바름

---

### 시나리오 3: Model Router Phase별 선택

**목표**: Phase별로 최적 모델이 자동 선택되는지 확인

**단계**:
1. `ModelRouter()` 초기화
2. Phase 0, 1, 2 → `gpt-4.1-nano` 확인
3. Phase 3 → `gpt-4o-mini` 확인
4. Phase 4 → `o1-mini` 확인
5. 비용 추정 → 합리적인 범위 확인

**예상 결과**: Phase별로 다른 모델이 선택되고, 비용 추정이 정확함

---

### 시나리오 4: Explorer Agent 통합

**목표**: Explorer가 External 모드에서 RAG + API 호출을 수행하는지 확인

**단계**:
1. `ExplorerRAG()` 초기화
2. `explorer.mode='external'` 확인
3. `explorer.llm` 객체 존재 확인
4. `search_patterns()` → RAG 검색 성공
5. ~~`generate_opportunity_hypothesis()` → API 호출 (생략, 비용)~~

**예상 결과**: Explorer가 External 모드로 초기화되고, RAG 검색 성공

---

### 시나리오 5: Estimator Phase 4 LLM

**목표**: Estimator Phase 4 (Fermi)가 External 모드에서 LLM을 호출할 준비가 되었는지 확인

**단계**:
1. `EstimatorRAG()` 초기화
2. `Phase4FermiDecomposition` 모듈 import
3. `openai` 패키지 import 확인

**예상 결과**: Phase 4 모듈이 LLM 호출 준비 완료

---

### 시나리오 6: 실제 API 호출

**목표**: OpenAI API가 실제로 작동하는지 확인

**단계**:
1. OpenAI API 연결 (모델 목록 조회)
2. 가장 저렴한 모델 (`gpt-4o-mini`)로 간단한 완성
   - Prompt: "1+1은?"
   - Max tokens: 10
3. 응답 확인
4. 비용 계산

**예상 결과**: API 호출 성공, 응답 수신, 비용 $0.000001 미만

---

## 실행 방법

### 1. 환경 준비

```bash
# .env 파일 확인
cat .env | grep UMIS_MODE
# UMIS_MODE=external

cat .env | grep OPENAI_API_KEY
# OPENAI_API_KEY=sk-...
```

### 2. 전체 테스트 실행

```bash
cd /Users/kangmin/umis_main_1103/umis

# 전체 테스트
UMIS_MODE=external python scripts/test_external_llm_integrity.py

# 상세 로그
python scripts/test_external_llm_integrity.py --verbose
```

### 3. 카테고리별 테스트

```bash
# 설정만
python scripts/test_external_llm_integrity.py --category config

# LLMProvider만
python scripts/test_external_llm_integrity.py --category provider

# Model Router만
python scripts/test_external_llm_integrity.py --category router

# Explorer만
python scripts/test_external_llm_integrity.py --category explorer

# Estimator만
python scripts/test_external_llm_integrity.py --category estimator

# 기타 Agent만
python scripts/test_external_llm_integrity.py --category agents

# API 연결만
python scripts/test_external_llm_integrity.py --category api
```

### 4. 출력 예시

```
================================================================================
UMIS External LLM 모드 무결성 테스트 v7.7.0
================================================================================

🚀 전체 테스트 시작...

📋 [1/7] 설정 테스트
----------------------------------------
  ✅ env_file_exists: .env 파일 존재: /Users/kangmin/.../umis/.env (2ms)
  ✅ umis_mode_set: External 모드 설정됨 (1ms)
  ✅ openai_api_key: API Key 설정됨: sk-proj-... (1ms)
  ✅ llm_models: 모든 Phase 모델 설정됨 (1ms)
  ✅ phase_routing: Phase 라우팅: 활성화 (1ms)

🤖 [2/7] LLMProvider 테스트
----------------------------------------
  ✅ create_llm_external: LLM 객체 생성 성공: ChatOpenAI (50ms)
  ✅ mode_detection: 모드 감지 정상 (1ms)
  ✅ mode_info: 모드 정보 정상 (1ms)

🚦 [3/7] Model Router 테스트
----------------------------------------
  ✅ initialization: ModelRouter 초기화 성공 (10ms)
  ✅ phase_selection: Phase별 모델 선택 정상 (5ms)
  ✅ cost_estimation: 비용 추정 정상: $0.000285/작업 (2ms)

🔍 [4/7] Explorer Agent 테스트
----------------------------------------
  ✅ initialization: Explorer 초기화 성공 (150ms)
  ✅ llm_mode: External 모드 설정 확인 (1ms)
  ✅ pattern_search: 패턴 검색 성공: 3개 발견 (200ms)

📊 [5/7] Estimator Agent 테스트
----------------------------------------
  ✅ initialization: Estimator 초기화 성공 (100ms)
  ✅ phase4_llm: Phase 4 LLM 준비 완료 (50ms)

👥 [6/7] 기타 Agent 테스트
----------------------------------------
  ✅ guardian_evaluator: Guardian Evaluator LLM 설정 확인 (80ms)
  ✅ hybrid_projector: Hybrid Projector LLM 설정 확인 (60ms)

🌐 [7/7] API 연결 테스트
----------------------------------------
  ✅ openai_connection: OpenAI API 연결 성공 (500ms)
  ✅ simple_completion: 완성 테스트 성공: '2' (800ms)

================================================================================
테스트 결과 요약
================================================================================

📊 카테고리별 결과:
  ✅ config: 5/5 통과 (100%)
  ✅ provider: 3/3 통과 (100%)
  ✅ router: 3/3 통과 (100%)
  ✅ explorer: 3/3 통과 (100%)
  ✅ estimator: 2/2 통과 (100%)
  ✅ agents: 2/2 통과 (100%)
  ✅ api: 2/2 통과 (100%)

📈 전체 통계:
  총 테스트: 20개
  통과: 20개
  실패: 0개
  통과율: 100.0%
  소요 시간: 2.05초

================================================================================
🎉 모든 테스트 통과! External LLM 모드가 정상 작동합니다.
================================================================================
```

---

## 예상 결과

### 성공 케이스

모든 테스트가 통과하면:

```
🎉 모든 테스트 통과! External LLM 모드가 정상 작동합니다.
```

**의미**:
- External 모드 설정이 올바름
- LLMProvider가 정상 작동
- Model Router가 Phase별 모델을 자동 선택
- 모든 Agent가 External 모드 지원
- OpenAI API 연결 성공

### 실패 케이스

#### 1. 설정 문제

```
❌ [config] umis_mode_set: Native 모드가 설정되어 있습니다
```

**원인**: `.env`에서 `UMIS_MODE=native`로 설정됨

**해결**:
```bash
# .env 수정
UMIS_MODE=external
```

#### 2. API Key 문제

```
❌ [config] openai_api_key: OpenAI API Key가 설정되지 않았습니다
```

**원인**: `.env`에 `OPENAI_API_KEY` 없음

**해결**:
```bash
# .env에 추가
OPENAI_API_KEY=sk-proj-...
```

#### 3. LLM 객체 생성 실패

```
❌ [provider] create_llm_external: External 모드인데 LLM이 None입니다
```

**원인**: `LLMProvider.create_llm()`이 Native 모드로 동작

**해결**: `settings.umis_mode` 확인, `.env` 재확인

#### 4. Phase 모델 설정 누락

```
❌ [config] llm_models: 모델 설정 누락: phase0_2, phase3, phase4
```

**원인**: `.env`에 Phase별 모델 설정 없음

**해결**:
```bash
# .env에 추가
LLM_MODEL_PHASE0_2=gpt-4.1-nano
LLM_MODEL_PHASE3=gpt-4o-mini
LLM_MODEL_PHASE4=o1-mini
USE_PHASE_BASED_ROUTING=true
```

#### 5. API 연결 실패

```
❌ [api] openai_connection: API 연결 실패: Invalid API key
```

**원인**: 잘못된 API Key

**해결**: OpenAI 대시보드에서 새 Key 생성

---

## 문제 해결

### 공통 문제

#### Q1: "openai 패키지 없음" 오류

**증상**:
```
ImportError: No module named 'openai'
```

**해결**:
```bash
pip install openai
```

#### Q2: "ChromaDB 없음" 오류

**증상**:
```
ImportError: No module named 'chromadb'
```

**해결**:
```bash
pip install chromadb
```

#### Q3: Native 모드로 설정되어 있음

**증상**:
```
❌ External 모드가 아닙니다: native
```

**해결**:
```bash
# .env 수정
UMIS_MODE=external

# 테스트 재실행
python scripts/test_external_llm_integrity.py
```

#### Q4: API Rate Limit 초과

**증상**:
```
❌ API 연결 실패: Rate limit exceeded
```

**해결**:
- 1분 대기 후 재실행
- 테스트는 가벼운 호출만 수행하므로 보통 문제 없음

### 디버깅 팁

#### 1. 상세 로그 확인

```bash
python scripts/test_external_llm_integrity.py --verbose
```

#### 2. 특정 카테고리만 실행

```bash
# 문제가 있는 카테고리만
python scripts/test_external_llm_integrity.py --category config
```

#### 3. 설정 확인

```python
# Python 인터프리터에서
from umis_rag.core.config import settings

print(settings.umis_mode)          # 'external' 확인
print(settings.openai_api_key[:10])  # 'sk-proj-...' 확인
print(settings.llm_model)           # 모델명 확인
```

#### 4. LLMProvider 수동 테스트

```python
from umis_rag.core.llm_provider import LLMProvider

# LLM 생성
llm = LLMProvider.create_llm()
print(type(llm))  # <class 'langchain_openai.chat_models.base.ChatOpenAI'>

# 모드 확인
print(LLMProvider.is_external_mode())  # True
```

---

## 테스트 확장

### 추가할 수 있는 테스트

#### 1. E2E Workflow 테스트

전체 워크플로우를 External 모드로 실행:

```python
# scripts/test_external_e2e.py
# Observer → Explorer → Quantifier → Validator → Guardian
```

#### 2. 비용 모니터링

실제 사용 시 비용 추적:

```python
# scripts/monitor_external_costs.py
# API 호출 비용 실시간 모니터링
```

#### 3. 성능 벤치마크

Native vs External 성능 비교:

```python
# scripts/benchmark_native_vs_external.py
# 속도, 비용, 품질 비교
```

---

## 체크리스트

### 테스트 실행 전

- [ ] `.env` 파일 존재 확인
- [ ] `UMIS_MODE=external` 설정
- [ ] `OPENAI_API_KEY` 설정
- [ ] Phase별 LLM 모델 설정
- [ ] 필요한 패키지 설치 (`openai`, `chromadb`, `langchain-openai`)
- [ ] 인터넷 연결 확인

### 테스트 실행

- [ ] 전체 테스트 실행: `python scripts/test_external_llm_integrity.py`
- [ ] 모든 카테고리 통과 확인
- [ ] 실패한 테스트 없음 확인
- [ ] API 호출 성공 확인

### 테스트 후

- [ ] 결과 요약 캡처
- [ ] 실패한 테스트 문서화 (있는 경우)
- [ ] Native 모드로 복귀 (필요 시): `UMIS_MODE=native`

---

## 결론

이 테스트 설계는 UMIS 전체 시스템에서 External LLM 모드가 **올바르게 구현**되고 **일관되게 작동**하는지 검증합니다.

### 테스트 범위

- ✅ 7개 카테고리
- ✅ 20개 테스트
- ✅ 6개 Agent (Explorer, Estimator, Guardian, Projector, ...)
- ✅ 5개 Phase (Estimator)
- ✅ API 연결

### 실행 시간

- **전체**: ~2초 (API 호출 포함)
- **카테고리별**: ~0.2-0.8초

### 비용

- **전체 테스트**: $0.000001 미만 (API 호출 1회만)

---

**작성자**: AI Team  
**최종 업데이트**: 2025-11-21  
**다음 리뷰**: v7.8.0 릴리스 시


