# 추정 정확도 문제 분석 및 해결방안

**날짜**: 2025-11-10  
**발견**: Validator OFF/ON 비교 테스트  
**평균 오차**: 69.9%

---

## 🚨 발견된 문제 3가지

### **문제 1: 단위 변환 누락** ⭐ 심각

```
케이스: 담배갑 판매량

질문: "하루에 판매되는 담배갑의 개수는?"
  └─ 필요 단위: 갑/일

Validator 반환:
  └─ 32,000,000,000 갑/년 (연간)
  └─ ❌ 단위 변환 없이 그대로 반환

추정 (Tier 3):
  └─ 5,310,500 갑/일
  
실제 정답:
  └─ 87,671,233 갑/일 (32,000,000,000 / 365)

문제:
  ⚠️  Validator가 잘못된 단위로 반환!
  ⚠️  추정이 더 정확한 단위 제공!
  ⚠️  Validator의 신뢰가 깨짐!
```

**책임**: Validator가 단위 변환해야 함!

---

### **문제 2: 하드코딩 값 (Native Mode)** ⚠️ 중요

```
케이스: 음식점 수

추정 로직:
  count = population / people_per_store
  count = 51,000,000 / 150 = 340,000개

실제값:
  680,000개 (식약처)

문제:
  ⚠️  people_per_store = 150 (하드코딩!)
  ⚠️  실제는 75명/점
  ⚠️  50% 오차!

Native Mode 코드:
```python
people_per_store = 150  # ← 하드코딩!
```

**해결책**: 재귀 추정으로 변경

```python
# Before (하드코딩)
people_per_store = 150

# After (재귀 추정)
people_per_store = estimator.estimate(
    "음식점 1개당 담당 인구는?",
    context=context,
    depth=depth+1
)
# → Tier 2/3로 추정하거나
# → Validator에서 벤치마크 발견
```

**책임**: Tier 3 Native Mode 개선

---

### **문제 3: Validator 잘못된 매칭** ⚠️⚠️ 매우 심각!

```
케이스: 음악 스트리밍 시장

질문: "한국 음악 스트리밍 시장 규모는?"

Validator 반환:
  └─ 1,800조원 (한국 GDP!)
  └─ ❌ 완전히 다른 데이터!

실제 정답:
  └─ 9,000억원 (콘텐츠진흥원)
  └─ Validator에 있지만 매칭 안됨

문제:
  ⚠️⚠️  "시장" 키워드로 GDP 매칭
  ⚠️⚠️  관련성(relevance) 검증 없음!
  ⚠️⚠️  잘못된 값을 confidence 1.0으로 반환

현재 스크리닝:
  ❌ 없음! (유사도만 체크)
```

**책임**: Validator가 relevance 검증해야!

---

## 🔧 해결 방안

### **해결 1: Validator 단위 변환 (최우선!)** ⭐

**책임**: Validator

**구현 위치**: `validator.py - search_definite_data()`

**로직**:
```python
def search_definite_data(question, context):
    # 1. 기존: 확정 데이터 검색
    result = self._search_registry(question, context)
    
    if result:
        # 2. NEW: 질문에서 요청 단위 추출
        requested_unit = self._extract_requested_unit(question)
        
        # 3. NEW: 단위 변환 필요 여부 확인
        if self._needs_conversion(result['unit'], requested_unit):
            converted = self._convert_unit(
                value=result['value'],
                from_unit=result['unit'],
                to_unit=requested_unit,
                formula=result.get('formula')
            )
            
            if converted:
                result['value'] = converted['value']
                result['unit'] = converted['unit']
                result['conversion_applied'] = True
                result['original_value'] = result['value']
                result['original_unit'] = result['unit']
        
        return result
```

**단위 변환 규칙**:
```python
UNIT_CONVERSIONS = {
    # 시간
    ('갑/년', '갑/일'): lambda x: x / 365,
    ('원/년', '원/월'): lambda x: x / 12,
    ('개/년', '개/일'): lambda x: x / 365,
    
    # 역방향
    ('갑/일', '갑/년'): lambda x: x * 365,
    ('원/월', '원/년'): lambda x: x * 12,
}
```

**예시**:
```python
질문: "하루에 판매되는 담배갑은?"
  → 요청 단위: 갑/일

Validator 발견: 32,000,000,000 갑/년
  ↓
단위 변환: 32,000,000,000 / 365 = 87,671,233
  ↓
반환: 87,671,233 갑/일 ✅
```

---

### **해결 2: Native Mode 재귀 추정** ⭐

**책임**: Tier 3 Native Mode

**구현 위치**: `tier3.py - _generate_native_models()`

**Before (하드코딩)**:
```python
if '음식점' in question:
    people_per_store = 150  # ← 하드코딩!
    
    return FermiModel(
        variables={
            'people_per_store': FermiVariable(
                value=150,  # ← 고정값!
                source='native_estimate'
            )
        }
    )
```

**After (재귀 추정)**:
```python
if '음식점' in question:
    # 재귀 추정 필요 표시
    return FermiModel(
        variables={
            'population': FermiVariable(
                value=51_000_000,
                source='native_constant'
            ),
            'people_per_store': FermiVariable(
                available=False,  # ← 재귀 추정 필요!
                need_estimate=True,
                estimation_question="음식점 1개당 담당 인구는?"
            )
        }
    )
```

**프로세스**:
```
질문: "한국 음식점 수는?"
  ↓
Tier 3: 모형 생성
  └─ count = population / people_per_store
  
변수 확보:
  - population: 51,000,000 (상수)
  - people_per_store: Unknown
  
재귀 추정:
  질문: "음식점 1개당 담당 인구는?"
    ↓
  Tier 2: 통계 패턴 검색
    └─ "음식점 밀도" 벤치마크
    └─ 75명/점 발견 ✅
  
최종 계산:
  51,000,000 / 75 = 680,000개 ✅
```

**장점**: 
- ✅ 하드코딩 제거
- ✅ 데이터 기반 추정
- ✅ 정확도 향상

---

### **해결 3: Validator Relevance 검증** ⭐⭐ 매우 중요!

**책임**: Validator

**구현 위치**: `validator.py - search_definite_data()`

**문제**:
```python
# 현재
def search_definite_data(question, context):
    results = search(question, k=3)
    
    for doc, score in results:
        if score > 0.75:  # 유사도만 체크
            return doc  # ← 바로 반환! (위험!)
```

**개선**:
```python
def search_definite_data(question, context):
    results = search(question, k=3)
    
    for doc, score in results:
        if score > 0.75:
            # ⭐ NEW: Relevance 검증!
            if self._is_relevant(question, doc, context):
                return doc
            else:
                logger.warning(f"유사도 높지만 관련성 낮음: {doc.metadata.get('data_point')}")
                continue
    
    return None
```

**Relevance 검증 로직**:
```python
def _is_relevant(question, doc, context):
    """
    관련성(Relevance) 검증
    
    검증 항목:
    1. Domain 일치
    2. 키워드 매칭
    3. 의미적 관련성
    """
    
    # 1. Domain 체크
    doc_category = doc.metadata.get('category', '')
    
    # 매우 다른 카테고리면 제외
    INCOMPATIBLE = {
        ('시장규모', 'GDP'),  # 시장 ≠ 전체 경제
        ('음식점수', '인구통계'),
        ('수업료', '최저임금')
    }
    
    question_type = self._classify_question(question)
    
    for q_type, d_type in INCOMPATIBLE:
        if q_type in question_type and d_type in doc_category:
            logger.warning(f"  ⚠️  비호환: {q_type} vs {d_type}")
            return False
    
    # 2. 키워드 필수 매칭
    required_keywords = self._extract_keywords(question)
    doc_content = doc.page_content.lower()
    
    # 핵심 키워드가 하나라도 있어야
    if required_keywords:
        if not any(kw in doc_content for kw in required_keywords):
            logger.warning(f"  ⚠️  키워드 불일치: {required_keywords}")
            return False
    
    # 3. Scale 체크 (order of magnitude)
    # 예: "학원 수업료" 수십만원 vs "GDP" 수천조원
    if self._scale_mismatch(question, doc.metadata.get('value')):
        logger.warning(f"  ⚠️  Scale 불일치")
        return False
    
    return True
```

**예시**:
```python
질문: "음악 스트리밍 시장 규모는?"
키워드: ['음악', '스트리밍', '시장']

후보 1: GDP (1,800조원)
  └─ 키워드: ['GDP', '국내총생산', '경제']
  └─ 매칭: ❌ '음악', '스트리밍' 없음
  └─ 제외!

후보 2: 음악 스트리밍 시장 (9,000억원)
  └─ 키워드: ['음악', '스트리밍', '콘텐츠']
  └─ 매칭: ✅ 모두 포함
  └─ 반환! ✅
```

---

## 🎯 책임 분담

| 문제 | 책임자 | 이유 |
|------|--------|------|
| 1. 단위 변환 | **Validator** | 확정 데이터 제공자로서 올바른 단위 제공 책임 |
| 2. 하드코딩 제거 | **Tier 3** | Native Mode 품질 개선 |
| 3. Relevance 검증 | **Validator** | 잘못된 데이터 제공 방지 책임 |

---

## 🔧 구현 우선순위

### 1단계: Validator Relevance 검증 (최우선!)
- 잘못된 데이터 반환 = 치명적
- GDP를 시장규모로 반환하는 것 방지

### 2단계: Validator 단위 변환
- 사용자 경험 개선
- 정확한 단위 제공

### 3단계: Tier 3 하드코딩 제거
- 추정 정확도 향상
- 재귀 추정 활용

---

## 📊 예상 개선 효과

### Before (현재)
```
1. 담배갑: 32,000,000,000 (잘못된 단위) ❌
2. 음식점: 340,000 (50% 오차) ❌
3. 시장규모: GDP 반환 (완전히 틀림) ❌

평균 오차: 69.9%
```

### After (개선 후)
```
1. 담배갑: 87,671,233 (단위 변환 ✅) → 정확!
2. 음식점: 680,000 (재귀 추정 ✅) → 정확!
3. 시장규모: 9,000억 (relevance ✅) → 정확!

평균 오차: <10% 목표
```

---

## 🎯 구현 시작

지금부터 세 가지를 순서대로 구현하겠습니다!

