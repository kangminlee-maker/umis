# UMIS Native 모드 사용 가이드

**v7.7.0 신규 기능: 진짜 Native 모드 구현 완료!** ✅

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

### 문제점 (v7.4.0 이전)

```yaml
# .env 파일
UMIS_MODE=native  # "Native 모드" 설정

# 하지만 실제로는...
# Explorer가 항상 OpenAI API 호출 (External 모드 동작)
# → umis_mode 설정 무용지물
# → 비용 발생
```

### 해결 (v7.7.0)

**진짜 Native 모드 구현!**

- **Native 모드**: RAG 검색만 수행 → Cursor LLM이 직접 분석
- **External 모드**: RAG 검색 + API 호출 → 완성된 결과
- **umis_mode 설정 실제 반영**: Explorer가 모드에 따라 다르게 동작

---

## Native vs External 모드

### Native 모드 (권장)

**개념:**
- Python이 RAG 검색만 수행
- 검색 결과를 Cursor LLM에게 전달
- **Cursor LLM이 직접 분석**

**장점:**
- ✅ **비용 $0** (Cursor 구독에 포함)
- ✅ 최고 품질 (Claude Sonnet 4.5 등)
- ✅ 빠른 응답 (API 왕복 없음)
- ✅ 자연스러운 사용 (Cursor에서 직접)

**단점:**
- ❌ 자동화 불가 (사용자 참여 필요)
- ❌ 배치 처리 불가

**사용 시나리오:**
- 일회성 시장 분석
- 탐색적 분석
- 품질 중시
- Interactive 작업

---

### External 모드

**개념:**
- Python이 RAG 검색 + OpenAI API 호출
- **완성된 가설 반환**

**장점:**
- ✅ 완전 자동화 가능
- ✅ 배치 처리 가능
- ✅ Cursor 독립 실행

**단점:**
- ❌ API 비용 발생 (~$0.10/요청)
- ❌ Native LLM보다 품질 낮을 수 있음

**사용 시나리오:**
- 자동화 필요 (cron job)
- 대량 분석 (100개 이상)
- Cursor 없이 실행

---

## 설정 방법

### 1단계: .env 파일 설정

```bash
# .env 파일 (프로젝트 루트)

# Native 모드 (권장)
UMIS_MODE=native

# 또는 External 모드 (자동화 필요 시)
UMIS_MODE=external
```

### 2단계: 확인

```bash
python scripts/test_native_mode.py
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

**A1.**

- **Explorer**: Native/External 분기 구현 ✅
  - Native: RAG만 → Cursor 처리
  - External: RAG + API → 완성된 가설

- **Observer/Quantifier/Validator**: RAG만 사용 (LLM 없음)
  - 모드 무관

- **Estimator**: Tier 1-2만 (템플릿 기반)
  - Native 모드에서도 LLM 사용 안 함
  - Tier 3 필요 시 Cursor에게 위임

### Q2. 기존 External 모드 스크립트는 어떻게 하나요?

**A2.**

기존 스크립트는 그대로 사용 가능합니다.

```bash
# External 모드로 실행하려면
# .env 파일에서 UMIS_MODE=external로 설정

UMIS_MODE=external python scripts/your_script.py
```

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

### v7.7.0 (2025-11-10)

**신규 파일:**

1. `umis_rag/core/llm_provider.py`
   - LLMProvider 클래스
   - umis_mode에 따라 LLM 생성
   - Native: None 반환
   - External: ChatOpenAI 반환

2. `scripts/test_native_mode.py`
   - Native/External 모드 테스트
   - 모드 정보 확인
   - RAG 검색 + 가설 생성 테스트

**수정 파일:**

1. `umis_rag/agents/explorer.py`
   - LLMProvider import
   - `__init__`: LLMProvider 사용
   - `generate_opportunity_hypothesis`: Native/External 분기

2. `config/llm_mode.yaml`
   - v7.7.0 업데이트
   - Native 모드 구현 완료 표시

3. `env.template`
   - Native 모드 설명 업데이트
   - v7.7.0 변경사항 추가

---

## 다음 단계

### 즉시 사용

1. `.env` 파일에서 `UMIS_MODE=native` 확인
2. `python scripts/test_native_mode.py` 실행
3. 결과 확인

### 실제 프로젝트

1. RAG 검색 스크립트 작성
2. Cursor Composer에서 결과 활용
3. 비용 $0으로 고품질 분석!

---

## 참고 문서

- `config/llm_mode.yaml`: 상세 설정 가이드
- `umis_rag/core/llm_provider.py`: 구현 코드
- `scripts/test_native_mode.py`: 테스트 예시

---

**v7.7.0 - Native 모드 진짜 구현 완료!** ✅

