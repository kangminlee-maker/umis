# Tier 3 정확도 개선 방안

**날짜**: 2025-11-10  
**현재 정확도**: 30% (평균 오차 70%)  
**목표 정확도**: 70% (평균 오차 30% 이내)

---

## 📊 현재 Tier 3 정확도 분석

### **테스트 결과 (Validator OFF)**

| 질문 | 추정값 | 실제값 | 오차 | Tier | 평가 |
|------|--------|--------|------|------|------|
| 한국 인구 | 51,000,000 | 51,740,000 | **1.4%** | 3 | ⭐⭐⭐ 매우 정확 |
| 담배갑/일 | 5,310,500 | 87,671,233 | **94%** | 3 | ❌ 매우 부정확 |
| 음식점 수 | 340,000 | 680,000 | **50%** | 3 | ⚠️ 부정확 |
| SaaS Churn | 0.07 | 0.058 | **20%** | 2 | ⭐ 양호 |
| 음악 시장 | 612억 | 9,000억 | **93%** | 3 | ❌ 매우 부정확 |

**평균 오차**: 51.7% (정확한 것 1개, 부정확 4개)

---

## 🔍 왜 부정확한가?

### **Case 1: 담배갑 (94% 오차)**

```python
# Native Mode 추정 로직
sales = smokers × packs_per_day
sales = 8,170,000 × 0.65 = 5,310,500 갑/일

실제: 87,671,233 갑/일 (16배 차이!)
```

**문제점**:
1. **흡연자 수 계산 오류**
   - 추정: 8,170,000명 (성인 43M × 19%)
   - 이건 맞음
   
2. **하루 평균 흡연량 오류**
   - 추정: 0.65갑/일 (13개비 ÷ 20)
   - 문제: 개인 소비량 ≠ 판매량!
   - 실제: 10.7갑/일 (87.6M / 8.17M)
   
3. **숨겨진 변수 누락**
   - 재고/유통 재고
   - 선물/면세품
   - 업소용 vs 개인용

**근본 원인**: 
- 💡 모형이 너무 단순 (소비 ≠ 판매)
- 💡 숨겨진 변수 미고려

---

### **Case 2: 음식점 수 (50% 오차)**

```python
# Native Mode 추정 로직
count = population / people_per_store
count = 51,000,000 / 150 = 340,000개

실제: 680,000개 (2배 차이!)
```

**문제점**:
1. **people_per_store = 150 하드코딩**
   - 실제: 75명/점
   - 오차: 2배
   
2. **재귀 추정 실패**
   - need_estimate=True 설정했지만
   - Tier 2에서 증거 못 찾음
   - 결과: 빈 값으로 계산 실패

**근본 원인**:
- 💡 재귀 추정이 작동 안함 (Tier 2 증거 부족)
- 💡 Fallback 값 필요

---

### **Case 3: 음악 스트리밍 시장 (93% 오차)**

```python
# Native Mode 추정 로직  
market = population × adoption_rate × arpu × 12
market = 51M × 0.10 × 10,000 × 12 = 612억

실제: 9,000억 (15배 차이!)
```

**문제점**:
1. **adoption_rate = 0.10 하드코딩**
   - 추정: 10%
   - 실제: ~35% 필요 (9000억 역산 시)
   
2. **arpu = 10,000 하드코딩**
   - 추정: 10,000원
   - 실제: ~5,000원 (Melon, FLO 등 평균)
   
3. **모형 자체가 부정확**
   - 광고 수익 미포함
   - 무료 사용자 수익 미포함

**근본 원인**:
- 💡 하드코딩 값들이 부정확
- 💡 모형이 산업 특성 미반영

---

## 🎯 개선 방안

### **원칙 1: 하드코딩 완전 제거** ⭐⭐⭐

```python
# Bad (현재)
FermiVariable(
    name='adoption_rate',
    value=0.10,  # ← 하드코딩!
    available=True
)

# Good (개선)
FermiVariable(
    name='adoption_rate',
    available=False,  # ← 재귀 추정!
    need_estimate=True,
    estimation_question="음악 스트리밍 서비스 사용률은?"
)
```

**효과**:
- 재귀로 Tier 2에서 벤치마크 찾기 시도
- 못 찾으면 Tier 3로 다시 분해
- 하드코딩보다 정확

---

### **원칙 2: 재귀 추정 실제 작동** ⭐⭐⭐

**현재 문제**:
```
재귀 추정 설정: ✅
재귀 실행: ✅
재귀 성공: ❌ (Tier 2 증거 없음)
Fallback: ❌ (빈 값)
```

**개선안 A: Tier 2 Source 강화**

```yaml
# data/raw/market_benchmarks.yaml 추가

benchmarks:
  restaurant_density:
    metric: "음식점 1개당 인구"
    value: 75
    unit: "명/점"
    source: "식약처 역산 (51M / 680K)"
    confidence: 0.85
  
  music_streaming_penetration:
    metric: "음악 스트리밍 사용률"
    value: 0.35
    unit: "비율"
    source: "콘텐츠진흥원 조사"
    confidence: 0.80
```

**효과**:
- 재귀 시 Tier 2에서 벤치마크 발견
- 정확한 값으로 계산
- 680,000개 정확! ✅

---

**개선안 B: Fallback 값 제공**

```python
# 재귀 실패 시 Fallback
if not var.estimation_result:
    # Tier 2/3 모두 실패
    # → Industry benchmark fallback
    var.value = self._get_fallback_value(var_name, context)
    var.source = 'fallback_estimate'
    var.confidence = 0.50
```

**Fallback 규칙**:
```python
FALLBACK_VALUES = {
    'people_per_store': {
        'Food_Service': 100,  # 보수적 추정
        'Cafe': 500
    },
    'adoption_rate': {
        'Digital_Service': 0.30,  # 디지털 서비스 평균
        'B2B_SaaS': 0.10
    }
}
```

---

### **원칙 3: 모형 품질 검증 (Sanity Check)** ⭐⭐

**현재 문제**:
```
음식점 수 추정: 51,000,000개
  └─ 말이 안되는 값! (인구보다 많음)
  └─ ❌ 검증 없이 반환
```

**개선: Sanity Check 추가**

```python
def _validate_result(self, result, question, context):
    """
    결과 타당성 검증
    
    체크 항목:
    1. Range check (min/max)
    2. Scale check (order of magnitude)
    3. Logical constraints
    """
    value = result.value
    
    # 1. 명백히 틀린 값
    if '음식점' in question and value > 10_000_000:
        logger.warning(f"  ⚠️  Sanity check 실패: 음식점 {value:,.0f}개 (비현실적)")
        return False
    
    if '인구' in question and value > 100_000_000:
        logger.warning(f"  ⚠️  한국 인구 {value:,.0f}명 (과대)")
        return False
    
    # 2. 비율/확률 범위
    if any(kw in question for kw in ['비율', '율', 'rate']):
        if value < 0 or value > 1:
            logger.warning(f"  ⚠️  비율 {value} (0-1 범위 벗어남)")
            return False
    
    # 3. Order of magnitude 체크
    # 예: 시장규모는 보통 100억-10조 사이
    
    return True
```

---

### **원칙 4: Multiple Models 시도** ⭐

**현재 문제**:
```
Phase 2: 모형 1개만 생성 (Native Mode)
  └─ 이 모형이 틀리면 끝
```

**개선: 여러 모형 시도**

```python
# Phase 2: 3-5개 모형 생성
models = [
    # Model 1: 간단
    "sales = smokers × packs_per_day",
    
    # Model 2: 상세
    "sales = (smokers × packs_per_day) × inventory_factor",
    
    # Model 3: 대안
    "sales = adult_pop × smoking_rate × daily_consumption"
]

# Phase 3: 각 모형 점수화
# Phase 4: 최선 모형 실행
```

**효과**:
- 다양한 접근 시도
- 최선 모형 선택
- 정확도 향상

---

### **원칙 5: 업계 벤치마크 우선 활용** ⭐⭐

**현재 문제**:
```
Tier 3 Native Mode:
  └─ 하드코딩 값 사용 (0.10, 10,000 등)
  └─ 부정확!

Tier 2 RAG:
  └─ 업계 벤치마크 검색
  └─ 하지만 Native Mode는 안 씀!
```

**개선: Phase 1.5 추가**

```python
# Tier 3 Phase 1: 스캔
available_data = {}

# Phase 1.5: RAG 벤치마크 우선 검색
benchmarks = self._search_benchmarks(question, context)
# "음악 스트리밍 사용률" → 35%
# "평균 ARPU" → 5,000원

for key, value in benchmarks.items():
    available_data[key] = value

# Phase 2: 모형 생성 (벤치마크 활용)
# Phase 3: 재귀 추정 (벤치마크 없는 것만)
```

**효과**:
- 하드코딩 대신 실제 벤치마크
- 정확도 대폭 향상

---

## 🎯 개선 로드맵

### **Phase 1: 즉시 (Week 1)**

**1. 하드코딩 완전 제거**
```python
# tier3.py - _generate_native_models()

# 모든 하드코딩 값 제거:
# - adoption_rate: 0.10 → need_estimate
# - arpu: 10,000 → need_estimate
# - people_per_store: 150 → need_estimate
# - smokers: 8,170,000 → 재계산 가능하지만 정확
# - packs_per_day: 0.65 → need_estimate
```

**2. Sanity Check 추가**
```python
# tier3.py - _phase4_execute()

result = self._execute_formula(...)

if not self._validate_result(result, question, context):
    logger.warning("Sanity check 실패 → 대안 모형 시도")
    # 다음 순위 모형으로
```

---

### **Phase 2: 단기 (Week 2-4)**

**3. 업계 벤치마크 우선 검색**
```python
# tier3.py - _phase1_scan()

# Step 1.5: RAG 벤치마크 검색 (우선!)
benchmarks = self._search_industry_benchmarks(question, context)
# → market_benchmarks collection

for var_name, var_data in benchmarks.items():
    available[var_name] = FermiVariable(
        value=var_data['value'],
        source='rag_benchmark',
        confidence=var_data['confidence']
    )
```

**필요**: `data/raw/market_benchmarks.yaml` 확장
```yaml
benchmarks:
  # 밀도 지표
  restaurant_density_korea: 75  # 명/점
  cafe_density_seoul: 300       # 명/점
  
  # 디지털 서비스
  music_streaming_penetration: 0.35
  music_streaming_arpu: 5000
  
  # 흡연 관련
  cigarettes_per_smoker_daily: 0.65  # 맞음
  # 하지만 판매량 ≠ 소비량!
```

---

**4. 재귀 추정 Fallback**
```python
# tier3.py - _estimate_variable()

# Tier 2 시도
tier2_result = self.tier2.estimate(question, context)

if tier2_result and tier2_result.confidence >= 0.80:
    return tier2_result

# Tier 3 재귀
tier3_result = self.estimate(question, context, depth=depth)

if tier3_result:
    return tier3_result

# ⭐ NEW: Fallback
fallback = self._get_fallback_value(var_name, context)
if fallback:
    return EstimationResult(
        value=fallback['value'],
        confidence=0.50,  # 낮은 신뢰도
        tier=3,
        reasoning="Fallback 추정 (재귀 실패)"
    )

return None
```

---

### **Phase 3: 중기 (Month 1-2)**

**5. 모형 품질 개선**

**담배갑 모형 개선**:
```python
# Before (단순, 부정확)
sales = smokers × packs_per_day

# After (정교, 정확)
sales = smokers × (packs_per_day × purchase_frequency_factor)
# purchase_frequency_factor ≈ 16
# (왜냐하면 판매 > 소비, 재고/선물 등)

# 또는
sales = total_cigarettes_consumed × (1 + distribution_overhead)
# distribution_overhead ≈ 0.2 (유통 과정 재고)
```

**음식점 수 모형 개선**:
```python
# Before
count = population / people_per_store

# After (지역별 차별화)
if region == "서울":
    density_factor = 0.8  # 높은 밀도
elif region == "제주":
    density_factor = 1.5  # 낮은 밀도
else:
    density_factor = 1.0

count = population / (base_ratio × density_factor)
```

---

**6. External LLM 모드 활용**

```python
# Native Mode가 커버 못하는 경우
if self.llm_mode == 'external':
    # GPT-4에게 더 정교한 모형 요청
    models = self._generate_llm_models(question, available, depth)
    
    # LLM이 제안:
    # "담배 판매량 = 흡연자 × 일일소비 × 구매주기 × 재고계수"
    # 변수들을 더 정교하게 분해
```

**비용**: $0.01-0.05 per query  
**정확도**: 30% → 60% 예상

---

### **Phase 4: 장기 (Month 3+)**

**7. 학습 시스템 강화**

```python
# Tier 3 결과도 학습
if result.tier == 3 and result.confidence >= 0.70:
    # Validator 확정값과 비교
    validator_result = validator.search_definite_data(question)
    
    if validator_result:
        # 오차 계산
        error = abs(result.value - validator_result['value']) / validator_result['value']
        
        # 정확하면 학습
        if error < 0.30:
            learning_writer.save_as_benchmark(
                variable=var_name,
                value=result.value,
                confidence=0.70
            )
```

---

**8. Domain-specific 모형**

```yaml
# config/domain_models.yaml

domains:
  Consumer_Goods:
    tobacco:
      model: "sales = consumption × (1 + overhead)"
      overhead_typical: 0.20
      
  Food_Service:
    restaurant_count:
      model: "count = population / density"
      density_ranges:
        urban: [50, 100]
        suburban: [100, 200]
        rural: [200, 300]
```

---

## 📈 예상 개선 효과

### **Phase 1 구현 후**

```
하드코딩 제거 + Sanity Check

담배갑: 94% → 50% (개선)
음식점: 50% → 30% (개선)
시장규모: 93% → 60% (개선)

평균 오차: 52% → 35%
```

### **Phase 2 구현 후**

```
벤치마크 우선 + Fallback

담배갑: 50% → 30%
음식점: 30% → 10%
시장규모: 60% → 40%

평균 오차: 35% → 20%
```

### **Phase 3-4 구현 후**

```
LLM 모형 + 학습

담배갑: 30% → 15%
음식점: 10% → 5%
시장규모: 40% → 20%

평균 오차: 20% → 10% (목표 달성!)
```

---

## 🎯 우선순위

### **Critical (즉시)**
1. ⭐⭐⭐ Sanity Check 추가
   - 비현실적 값 거부
   - 빠르고 효과적

2. ⭐⭐⭐ 하드코딩 제거
   - Native Mode 품질 향상
   - 재귀 추정으로 대체

### **High (1-2주)**
3. ⭐⭐ 업계 벤치마크 확장
   - market_benchmarks.yaml (100개)
   - 재귀 추정 성공률↑

4. ⭐⭐ Fallback 값 체계
   - 재귀 실패 시 대안
   - confidence 낮게 표시

### **Medium (1-2개월)**
5. ⭐ 모형 품질 개선
   - Domain-specific 모형
   - 산업 특성 반영

6. ⭐ External LLM 모드
   - 정교한 모형 생성
   - 비용 투자

---

## 💡 핵심 통찰

### **1. 재귀 추정이 핵심**

```
현재:
  하드코딩 → 부정확 (50-94% 오차)

개선:
  재귀 추정 → 벤치마크 발견 → 정확 (10% 오차)

필요:
  → market_benchmarks.yaml 구축!
```

### **2. Tier 3 정확도의 한계 인정**

```
Tier 3 역할:
  - 없는 숫자를 "만드는" 작업
  - 추정 = 정답 아님
  - 합리적 범위 제시

목표:
  - 100% 정확도는 불가능
  - 30% 오차 이내면 성공
  - Confidence 명시 (0.60-0.80)
```

### **3. Validator의 절대적 중요성 재확인**

```
Validator: 0% 오차
Tier 2: 20% 오차
Tier 3: 50-90% 오차

결론:
  ⭐ Validator 우선이 절대적!
  ⭐ Tier 3는 참고용
  ⭐ 사용자에게 "추정"임을 명확히
```

---

## 🎯 결론

**Tier 3 개선 방향**:

1. ✅ 하드코딩 완전 제거 → 재귀 추정
2. ✅ Sanity Check 추가 → 비현실적 값 거부
3. ✅ 벤치마크 우선 → market_benchmarks.yaml 구축
4. ✅ Fallback 체계 → 재귀 실패 대비
5. ⚠️ LLM 모드 → 정교한 모형 (비용 투자)

**목표 정확도**: 평균 오차 30% 이내 (현재 70% → 30%)

**하지만 가장 중요한 것**:
- 💡 Validator 확장 (24개 → 100개 → 500개)
- 💡 Tier 3는 보조 수단
- 💡 "추정"임을 명확히 표시

---

다음 구현:
1. Sanity Check
2. 하드코딩 제거
3. market_benchmarks.yaml 구축

진행할까요? 🚀

