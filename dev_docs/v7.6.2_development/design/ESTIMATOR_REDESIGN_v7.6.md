# Estimator 재설계안 (v7.6.0)

**날짜**: 2025-11-10  
**핵심 철학**: Validator 우선, Tier 3 가치 인정

---

## 🎯 설계 철학

### 1. **Built-in 상수 제거**
- ❌ Built-in Rules (YAML) 제거
- ✅ 학습형 RAG만 사용
- **이유**: 답변 일관성 확보

### 2. **Validator 우선 검색 강제**
- Estimator 요청 = "정확한 숫자가 없다"는 가정
- 하지만 **확인 필수!**
- Validator 검색 → 없으면 추정 시작

### 3. **Tier 3 비중 증가는 가치있음**
- 없는 숫자를 만드는 일 = 높은 가치
- 시간/비용 투자 정당화됨
- Tier 3 케이스 증가 = 긍정적 ✅

---

## 🏗️ 새로운 프로세스 (v7.6.0)

```
EstimatorRAG.estimate(question, context, project_data)
  ↓

┌─────────────────────────────────────────────────┐
│ 🔍 Phase 0: 프로젝트 확정 데이터                │
│                                                 │
│  if project_data contains answer:              │
│    return immediately (confidence 1.0)         │
│                                                 │
│  예: project_data = {                          │
│        "users": 10000,                         │
│        "churn_rate": 0.05                      │
│      }                                         │
│                                                 │
│  "이탈률은?" → 0.05 즉시 반환 ✅               │
└─────────────────────────────────────────────────┘
  ↓ 없음

┌─────────────────────────────────────────────────┐
│ ⚡ Phase 1: Tier 1 (학습 규칙만)               │
│                                                 │
│  ❌ Built-in Rules 제거!                       │
│  ✅ Learned Rules RAG만                        │
│                                                 │
│  projected_index.search(question, k=3)         │
│  threshold: 0.95+ similarity                   │
│                                                 │
│  처음 추정하는 숫자 → 무조건 통과              │
│  학습된 규칙만 히트                             │
└─────────────────────────────────────────────────┘
  ↓ 없음

┌─────────────────────────────────────────────────┐
│ 📋 Phase 2: Validator 검색 (강제) ⭐           │
│                                                 │
│  목적: "정말 확정 데이터가 없는가?"            │
│                                                 │
│  ValidatorRAG.search_definite_data(            │
│    question, context                           │
│  )                                             │
│                                                 │
│  검색 범위:                                     │
│  ├─ data_sources_registry (공식 통계)          │
│  ├─ 정부 데이터 (통계청, 질병관리청 등)        │
│  ├─ 업계 벤치마크                               │
│  └─ 학술 데이터                                 │
│                                                 │
│  발견 시:                                       │
│  └─ EstimationResult(                          │
│       value=...,                               │
│       confidence=1.0,                          │
│       tier=1.5,  # "Validator"                 │
│       source="통계청" 등                        │
│     )                                          │
│                                                 │
│  없음:                                          │
│  └─ 추정 시작 (Phase 3)                        │
└─────────────────────────────────────────────────┘
  ↓ 없음

┌─────────────────────────────────────────────────┐
│ 🧠 Phase 3: Tier 2 (추정 시작)                 │
│                                                 │
│  이제부터 "추정" 영역                           │
│  Validator도 없었음 = 데이터 없음 확정         │
│                                                 │
│  SourceCollector.collect_all()                 │
│  ├─ Physical (3)                               │
│  ├─ Soft (3)                                   │
│  └─ Value (5)                                  │
│                                                 │
│  Judgment.synthesize()                         │
│  └─ confidence 0.80+ 필요                      │
│                                                 │
│  성공 시:                                       │
│  └─ Learning Writer → Tier 1 학습             │
└─────────────────────────────────────────────────┘
  ↓ 실패 (confidence < 0.80)

┌─────────────────────────────────────────────────┐
│ 🧩 Phase 4: Tier 3 (Fermi 분해) ⭐⭐⭐         │
│                                                 │
│  "없는 숫자를 만드는 영역"                      │
│  → 가장 가치있는 작업!                          │
│  → 시간/비용 투자 정당화됨                      │
│                                                 │
│  Native/External Mode                          │
│  ├─ 질문 분석 → 모형 선택                      │
│  ├─ 재귀 분해 (depth 4)                        │
│  └─ 데이터 상속 & Context 전달                 │
│                                                 │
│  시간: 10-30초                                  │
│  비용: $0.01-0.05 (External)                   │
│                                                 │
│  비중 증가 = 자연스럽고 긍정적 ✅              │
└─────────────────────────────────────────────────┘
  ↓ 실패

  None 반환 (추정 불가)
```

---

## 📊 Before vs After 비교

### Before (v7.5.0)

```
1. Tier 1: Built-in (20개) + Learned RAG
   ↓
2. Tier 2: 추정 시작 (바로!)
   ↓
3. Tier 3: Fermi 분해
```

**문제점**:
- Built-in이 일관성 해침
- Validator 검색 누락
- Tier 2에서 불필요한 추정

### After (v7.6.0)

```
0. Project Data (즉시)
   ↓
1. Tier 1: Learned RAG만
   ↓
2. Validator 검색 (강제) ⭐
   ↓
3. Tier 2: 추정 시작
   ↓
4. Tier 3: Fermi 분해 (비중↑)
```

**개선점**:
- ✅ 답변 일관성 (학습형만)
- ✅ Validator 우선 검색
- ✅ Tier 3 가치 인정

---

## 🔍 상세 설계

### Phase 0: 프로젝트 데이터 확인

```python
def estimate(question, context, project_data):
    # 프로젝트 확정 데이터 우선
    if project_data:
        answer = self._check_project_data(question, project_data)
        if answer:
            return EstimationResult(
                value=answer['value'],
                confidence=1.0,
                tier=0,  # "Project Data"
                source="project_confirmed",
                reasoning="프로젝트 확정 데이터"
            )
```

**예시**:
```python
project_data = {
    "total_users": 10000,
    "churn_rate": 0.05,
    "arpu": 9900
}

estimator.estimate("이탈률은?", project_data=project_data)
# → 0.05 (즉시, confidence 1.0) ✅
```

---

### Phase 1: Tier 1 (학습 규칙만)

```python
# ❌ Built-in Rules 제거
# self.builtin_rules = self._load_builtin_rules()  # 삭제!

# ✅ Learned RAG만
def estimate_tier1(question, context):
    # RAG 검색만
    results = self.rag_searcher.search(
        question, 
        context,
        threshold=0.95
    )
    
    if results and results[0].similarity >= 0.95:
        return EstimationResult(
            value=results[0].value,
            confidence=results[0].confidence,
            tier=1,
            source="learned_rule"
        )
    
    return None  # 다음 단계로
```

**효과**:
- 처음 추정하는 숫자 → Tier 1 통과 ✅
- 학습된 규칙만 히트
- 답변 일관성 확보

---

### Phase 2: Validator 검색 (강제)

```python
def estimate_tier1_5_validator(question, context):
    """
    Tier 1.5: Validator 확정 데이터 검색
    
    추정하기 전 마지막 확인!
    """
    logger.info("[Estimator] Validator 확정 데이터 검색")
    
    if self.validator is None:
        from umis_rag.agents.validator import get_validator_rag
        self.validator = get_validator_rag()
    
    # Validator 검색
    result = self.validator.search_definite_data(
        question, 
        context
    )
    
    if result:
        logger.info(f"  ✅ Validator 발견: {result.source}")
        return EstimationResult(
            value=result.value,
            confidence=1.0,
            tier=1.5,  # "Validator"
            source=result.source,
            reasoning="확정 데이터 (Validator)"
        )
    
    logger.info("  → Validator에도 없음 → 추정 시작")
    return None
```

**Validator 구현 필요**:
```python
# umis_rag/agents/validator.py

def search_definite_data(
    self, 
    question: str, 
    context: Context
) -> Optional[Dict]:
    """
    확정 데이터 검색
    
    Returns:
        {
            'value': 51740000,
            'source': '통계청 2024',
            'definition': '주민등록인구',
            'confidence': 1.0
        } 또는 None
    """
    # 1. data_sources_registry 검색
    sources = self.search_data_source(question, top_k=3)
    
    # 2. 실제 값 추출 (메타데이터에서)
    for doc, score in sources:
        if score > 0.85:
            metadata = doc.metadata
            if 'value' in metadata:
                return {
                    'value': metadata['value'],
                    'source': metadata['source_name'],
                    'definition': metadata.get('definition'),
                    'confidence': 1.0
                }
    
    return None  # 없음
```

---

### Phase 3: Tier 2 (추정 시작)

```python
def estimate_tier2(question, context):
    logger.info("[Estimator] Tier 2: 추정 시작")
    logger.info("  (Validator에도 없음 → 데이터 없음 확정)")
    
    # 11개 Source 수집
    collected = self.source_collector.collect_all(
        question, context
    )
    
    # 종합 판단
    result = self.judgment.synthesize(
        question, 
        collected,
        min_confidence=0.80
    )
    
    if result and result.confidence >= 0.80:
        # 학습
        if result.should_learn:
            self.learning_writer.save(question, result, context)
            logger.info("  📚 학습됨 → 다음엔 Tier 1로!")
        
        return result
    
    return None  # Tier 3로
```

---

### Phase 4: Tier 3 (Fermi 분해)

```python
def estimate_tier3(question, context, project_data):
    logger.info("[Estimator] Tier 3: Fermi 분해")
    logger.info("  💎 가치있는 작업 시작!")
    
    # 시간/비용 투자 정당화됨
    result = self.tier3.estimate(
        question, 
        context, 
        project_data,
        depth=0
    )
    
    if result:
        logger.info(f"  ✅ 완료: {result.value}")
        logger.info(f"  ⏱️  시간: {result.execution_time:.2f}초")
        
        # 비용 로깅 (External Mode)
        if result.cost:
            logger.info(f"  💰 비용: ${result.cost:.4f}")
            logger.info(f"  💡 투자 가치: 없는 숫자 생성!")
        
        return result
    
    return None
```

---

## 📈 예상 Tier 분포 변화

### Before (v7.5.0)

```
Tier 1: 40%  (Built-in 20개 + Learned)
Tier 2: 40%  (추정)
Tier 3: 20%  (Fermi)
```

### After (v7.6.0)

```
Tier 0: 5%   (Project Data)
Tier 1: 10%  (Learned만, 초기엔 적음)
Tier 1.5: 30% (Validator 검색) ⭐
Tier 2: 25%  (추정)
Tier 3: 30%  (Fermi) ⭐ 증가!
```

**Tier 3 증가 이유**:
- Built-in 제거 → Tier 1 축소
- Validator가 많이 잡음 → Tier 2 축소
- 결과적으로 Tier 3 비중↑
- **이것은 긍정적!** ✅

---

## 🎯 핵심 변경사항 요약

### 1. **Built-in Rules 완전 제거**

```python
# ❌ 삭제
# data/tier1_rules/builtin.yaml (20개)
# tier1.py: _load_builtin_rules()
# tier1.py: _try_builtin_rules()

# ✅ 유지
# tier1.py: _try_rag_search()  # Learned만
```

### 2. **Validator 검색 추가**

```python
# estimator.py

def estimate(question, context, project_data):
    # 0. Project Data
    # 1. Tier 1 (Learned)
    
    # 2. Validator 검색 ⭐ NEW!
    result = self._estimate_tier1_5_validator(question, context)
    if result:
        return result
    
    # 3. Tier 2 (추정)
    # 4. Tier 3 (Fermi)
```

### 3. **Tier 3 가치 강조**

```python
# tier3.py

logger.info("💎 Tier 3: 없는 숫자를 만드는 가장 가치있는 작업")
logger.info("⏱️  예상 시간: 10-30초")
logger.info("💰 비용 투자: 정당화됨")
logger.info("📊 결과 가치: 매우 높음")
```

---

## 🔧 구현 우선순위

### 1단계: Validator 검색 구현 ⭐ 최우선

```python
# umis_rag/agents/validator.py

def search_definite_data(question, context):
    # 구현
```

### 2단계: Estimator 통합

```python
# umis_rag/agents/estimator/estimator.py

def _estimate_tier1_5_validator():
    # Validator 호출
```

### 3단계: Built-in 제거

```python
# tier1.py
# - _load_builtin_rules() 삭제
# - _try_builtin_rules() 삭제

# data/tier1_rules/builtin.yaml
# - 파일 삭제 또는 deprecated/로 이동
```

### 4단계: 테스트 & 검증

```python
# 처음 추정 → Tier 3 도달 확인
# Validator 검색 → 발견 확인
# 학습 → Tier 1 재사용 확인
```

---

## 📊 예상 효과

### 답변 일관성 ✅

```
Before: 
  "한국 인구는?" → Built-in 51,740,000 (고정)
  학습 후 → Learned 51,800,000 (최신)
  → 불일치! ❌

After:
  "한국 인구는?" → Validator 51,800,000 (최신, 통계청)
  → 항상 일관! ✅
```

### Validator 활용도 ✅

```
Before:
  Validator 검색 = 선택적 (누락 가능)

After:
  Validator 검색 = 강제 (Phase 2)
  → Validator 가치 극대화! ✅
```

### Tier 3 가치 인정 ✅

```
Before:
  Tier 3 = "최후의 수단" (부정적)

After:
  Tier 3 = "가장 가치있는 작업" (긍정적) ✅
  → 시간/비용 투자 정당화
```

---

## 🎉 결론

**v7.6.0 핵심**:
1. ❌ Built-in 제거 → 학습형만
2. ⭐ Validator 검색 강제
3. 💎 Tier 3 가치 인정

**철학**:
- 답변 일관성 (학습형)
- 확정 데이터 우선 (Validator)
- 창조적 추정의 가치 (Tier 3)

**다음 단계**:
1. Validator.search_definite_data() 구현
2. Estimator에 Phase 2 추가
3. Built-in Rules 제거
4. 테스트 & 검증

