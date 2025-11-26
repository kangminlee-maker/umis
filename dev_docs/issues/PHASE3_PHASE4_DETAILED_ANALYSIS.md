# Phase 3 & 4 문제 상세 분석

## 날짜
2025-11-25

## 요약
- **Phase 3**: External API 모드에서 ValueSource 수집이 구현되지 않음 (TODO 상태)
- **Phase 4**: Phase별 모델 라우팅이 잘못 설정됨 (gpt-5.1 존재하지 않음)

---

## 🔴 문제 1: Phase 3 - AIAugmentedEstimationSource (External API 모드)

### 증상
```
[AI+Web] External API 모드 (TODO: API 호출)
Value: 0개 추정
수집: Physical 0, Soft 0, Value 0
[Judgment] 증거 없음
판단 실패 (증거 없음)
```

### 원인

**파일**: `umis_rag/agents/estimator/sources/value.py`

```python
# Line 123-126
else:  # External API
    logger.info(f"  [AI+Web] External API 모드 (TODO: API 호출)")
    # TODO: LangChain + Tavily/SerpAPI
    return []  # ❌ 항상 빈 리스트 반환
```

### 상세 설명

1. **Phase 3 흐름**:
   ```
   Phase 3 시작
   ↓
   Source Collector: collect_all() 호출
   ↓
   AIAugmentedEstimationSource.collect() 호출
   ↓
   if llm_mode == "cursor":
       return []  # Cursor AI는 대화형
   else:  # External API
       return []  # ❌ TODO 상태 - 구현 안됨!
   ```

2. **설계 의도** (주석에서 확인):
   - LLM + Web Search 통합
   - LLM으로 먼저 추정 시도
   - 불확실하면 Web Search (Tavily/SerpAPI) 보강

3. **현재 상태**:
   - Cursor 모드: 빈 리스트 반환 (의도적, 대화형)
   - External API 모드: **TODO 주석만 있고 구현 안됨**

### 영향

- **Phase 3 완전 무용지물**: External API 모드에서 0개 증거 → 항상 실패
- **Phase 4로 Fallback 강제**: Phase 3를 건너뛰고 Phase 4로 이동
- **비용 증가**: Phase 3에서 해결 가능한 간단한 질문도 Phase 4 (고비용)로

### 해결 방법

#### Option 1: LLM으로 직접 추정 (간단)

```python
# umis_rag/agents/estimator/sources/value.py Line 123~
else:  # External API
    logger.info(f"  [AI+Web] External API: LLM 추정 시도")
    
    # LLM으로 직접 값 추정
    from umis_rag.core.llm_provider import get_llm
    llm = get_llm()
    
    prompt = f"""
질문: {question}

위 질문에 대한 수치 값을 추정하세요.
- 값만 숫자로 (단위 제외)
- 근거를 간단히 설명
"""
    
    try:
        response = llm.invoke(prompt)
        # 응답 파싱 후 ValueEstimate 반환
        value = parse_number(response.content)
        
        return [ValueEstimate(
            source_type=SourceType.AI_AUGMENTED,
            value=value,
            confidence=0.7,
            reasoning=response.content,
            source_detail="llm_estimation"
        )]
    except:
        return []
```

#### Option 2: Web Search 통합 (완전)

```python
else:  # External API
    logger.info(f"  [AI+Web] External API: LLM + Web Search")
    
    # 1. LLM으로 먼저 시도
    llm_estimate = try_llm_estimation(question)
    
    # 2. LLM이 불확실하면 Web Search
    if llm_estimate.confidence < 0.6:
        web_results = search_web(question)  # Tavily/SerpAPI
        llm_estimate = augment_with_web(llm_estimate, web_results)
    
    return [llm_estimate]
```

#### Option 3: 임시 우회 (최소)

Phase 3를 건너뛰고 Phase 4로 바로 가도록 설정 (현재 동작과 동일하지만 명시적)

---

## 🔴 문제 2: Phase 4 - 잘못된 모델 라우팅

### 증상
```
[LLM] 모형 생성 요청 (Mode: gpt-4o-mini)
[LLM] 모델: gpt-5.1  ❌ 존재하지 않는 모델!
[LLM] API: responses
[LLM] 응답 형식: list (converted)
⚠️ LLM 빈 응답
```

### 원인

**문제**: `LLM_MODE=gpt-4o-mini`로 설정했는데, Phase 4에서 `gpt-5.1` 사용

**원인**: Phase별 모델 라우팅 시스템

```python
# umis_rag/core/model_router.py (추정)
def select_model_with_config(phase: PhaseType):
    if phase == 4:
        model_name = settings.llm_model_phase4  # "gpt-5.1" 또는 "o1-mini"
        # ❌ settings.llm_mode (gpt-4o-mini)를 무시함!
```

### 상세 설명

1. **의도된 설계**:
   - Phase별 최적 모델 사용
   - Phase 0-2: 저비용 모델 (gpt-4.1-nano)
   - Phase 3: 중비용 모델 (gpt-4o-mini)
   - Phase 4: 고성능 모델 (o1-mini)

2. **현재 문제**:
   - `LLM_MODEL_PHASE4` 환경변수가 잘못 설정됨
   - 또는 기본값이 `gpt-5.1` (존재하지 않는 모델)

3. **gpt-5.1 문제**:
   - OpenAI에 `gpt-5.1` 모델 없음
   - API 호출 성공하지만 응답이 None 또는 빈 리스트
   - `response.output`이 빈 리스트 → `output_item = None` → 빈 응답

### 확인 필요 파일

1. **`.env` 파일**:
   ```bash
   LLM_MODEL_PHASE4=gpt-5.1  # ❌ 존재하지 않음!
   ```

2. **`config/llm_mode.yaml`**:
   ```yaml
   phase4:
     model: gpt-5.1  # ❌
   ```

3. **`umis_rag/core/config.py`**:
   ```python
   llm_model_phase4: str = Field(default="gpt-5.1")  # ❌
   ```

### 해결 방법

#### 즉시 수정: `.env` 파일 업데이트

```bash
# .env
LLM_MODEL_PHASE4=o1-mini  # ✅ 실제 존재하는 모델
# 또는
LLM_MODEL_PHASE4=gpt-4o-mini  # ✅
```

#### 영구 수정: `config.py` 기본값 변경

```python
# umis_rag/core/config.py
llm_model_phase4: str = Field(default="o1-mini")  # ✅
```

#### 테스트용 임시 수정

Phase 4 비활성화하고 Phase 3만 테스트:

```python
# 테스트 스크립트
os.environ['DISABLE_PHASE4'] = 'true'
```

---

## 📊 문제 영향 분석

### 현재 워크플로우 (12/13 실패)

```
Phase 0 → 실패 (프로젝트 데이터 없음)
↓
Phase 1 → 실패 (학습 규칙 없음)
↓
Phase 2 → 실패 (Validator에 없음)
↓
Phase 3 → 실패 ❌ (Value 0개, TODO 상태)
↓
Phase 4 → 실패 ❌ (gpt-5.1 빈 응답)
↓
결과: ❌ 실패
```

### 수정 후 예상 워크플로우

#### Phase 3 수정 후:
```
Phase 3 → 성공 ✅ (LLM 추정, confidence 0.7~0.9)
↓
결과: ✅ 성공 (예상: 8-10/13)
```

#### Phase 4 수정 후:
```
Phase 3 → 실패 (증거 부족)
↓
Phase 4 → 성공 ✅ (o1-mini로 Fermi 분해)
↓
결과: ✅ 성공 (예상: 10-12/13)
```

---

## 🎯 권장 조치 순서

### 1단계: 긴급 (Phase 4 모델 수정)

**목표**: Phase 4를 작동시켜 최소한의 성공률 확보

```bash
# .env 파일 수정
LLM_MODEL_PHASE4=o1-mini  # gpt-5.1 → o1-mini
```

**예상 효과**:
- Phase 4 성공률: 0% → 80-90%
- 전체 성공률: 7.7% (1/13) → 40-50% (5-7/13)

**시간**: 1분

---

### 2단계: 중기 (Phase 3 External API 구현)

**목표**: Phase 3를 실제로 작동시켜 성공률 대폭 향상

**구현 방법 1 - 간단 (LLM만)**:

```python
# umis_rag/agents/estimator/sources/value.py
def collect(self, question: str, context: Optional[Context] = None) -> List[ValueEstimate]:
    if self.llm_mode == "cursor":
        return []  # 대화형
    
    else:  # External API
        return self._estimate_with_llm(question, context)

def _estimate_with_llm(self, question, context):
    """LLM으로 직접 값 추정"""
    from umis_rag.core.llm_provider import get_llm
    
    llm = get_llm()
    prompt = f"""질문: {question}
    
위 질문에 대한 수치 값을 추정하고 근거를 제시하세요."""
    
    response = llm.invoke(prompt)
    value = self._parse_number(response.content)
    
    return [ValueEstimate(
        source_type=SourceType.AI_AUGMENTED,
        value=value,
        confidence=0.75,
        reasoning=response.content[:200],
        source_detail="llm_estimation"
    )]
```

**예상 효과**:
- Phase 3 성공률: 0% → 70-80%
- 전체 성공률: 7.7% → 70-80% (9-10/13)

**시간**: 1-2시간

---

### 3단계: 장기 (Web Search 통합)

**목표**: Phase 3 정확도 극대화

- Tavily API 또는 SerpAPI 통합
- LLM + Web Search 하이브리드

**예상 효과**:
- Phase 3 정확도: 75% → 90%+
- 전체 성공률: 80% → 90%+

**시간**: 1-2일

---

## 💡 즉시 테스트 가능한 수정

### 방법 1: Phase 4 모델만 수정

```bash
cd /Users/kangmin/umis_main_1103/umis

# .env 파일에 추가
echo "LLM_MODEL_PHASE4=o1-mini" >> .env

# 또는 테스트 스크립트에서
export LLM_MODEL_PHASE4=o1-mini
python tests/test_estimator_comprehensive.py
```

### 방법 2: Phase 3 최소 구현

```python
# umis_rag/agents/estimator/sources/value.py Line 124 수정
else:  # External API
    logger.info(f"  [AI+Web] External API: 간단 추정 (v7.8.1)")
    
    # 임시: 항상 고정값 반환 (테스트용)
    return [ValueEstimate(
        source_type=SourceType.AI_AUGMENTED,
        value=100000,  # 임시값
        confidence=0.5,
        reasoning="임시 구현 (테스트용)",
        source_detail="temporary"
    )]
```

---

## 📌 요약

| 문제 | 원인 | 해결 | 우선순위 | 시간 |
|------|------|------|----------|------|
| Phase 3 실패 | External API 모드 TODO | LLM 추정 구현 | 중 | 1-2시간 |
| Phase 4 실패 | gpt-5.1 존재하지 않음 | o1-mini로 변경 | **긴급** | **1분** |

**권장 순서**:
1. ✅ Phase 4 모델 수정 (1분) → 즉시 40-50% 성공률
2. ✅ Phase 3 LLM 추정 구현 (1-2시간) → 70-80% 성공률
3. ✅ Web Search 통합 (1-2일) → 90%+ 성공률

---

**작성**: AI Assistant  
**일시**: 2025-11-25





