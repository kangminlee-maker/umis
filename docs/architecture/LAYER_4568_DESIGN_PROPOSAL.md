# Layer 4, 5, 6, 8 확장 설계 제안

**작성일**: 2025-11-05  
**목적**: 부분 구현된 레이어들의 완성도 향상  
**현재 상태**: 30-80% → 목표 95%+

---

## 📐 Layer 4: 법칙 (물리/법률)

### 정의

**절대적이고 변하지 않는 제약 조건**
- 물리 법칙: 시간, 공간, 에너지
- 법률: 근로기준법, 최저임금법
- 수학: 확률 0-1, 각도 0-360°

**특징**:
- 신뢰도: 100% (절대적)
- 검증 불필요
- 시간/공간 제약으로 자주 사용

---

### 현재 구현 (80%)

**지원**: 시간 법칙 4개만

```python
time_laws = {
    r'\b하루\b': (24, '시간'),
    r'\b일주일\b|\b1주\b': (7, '일'),
    r'\b한 달\b|\b1개월\b': (30, '일'),
    r'\b1년\b|\b년간\b': (365, '일'),
}
```

**문제점**:
- 시간만 지원
- 법률 없음
- 물리 법칙 없음
- 확장 어려움 (하드코딩)

---

### 설계 제안: YAML 파일 분리

#### 파일 구조

**`config/law_rules.yaml`** (신규):

```yaml
# ========================================
# 법칙 규칙 (Layer 4)
# ========================================

version: "1.0"
updated: "2025-11-05"

# ========================================
# 시간 법칙
# ========================================

time_laws:
  - id: LAW_TIME_001
    pattern: "하루"
    value: 24
    unit: "시간"
    category: "시간"
    reliability: "절대적"
  
  - id: LAW_TIME_002
    pattern: "일주일|1주"
    value: 7
    unit: "일"
    category: "시간"
  
  - id: LAW_TIME_003
    pattern: "한 달|1개월"
    value: 30
    unit: "일"
    category: "시간"
  
  - id: LAW_TIME_004
    pattern: "1년|년간"
    value: 365
    unit: "일"
    category: "시간"
  
  - id: LAW_TIME_005
    pattern: "하루.*시간|일일.*근로"
    value: 8
    unit: "시간"
    category: "근로"
    note: "법정 근로시간 (1일)"
  
  - id: LAW_TIME_006
    pattern: "주.*근로시간|주간.*근로"
    value: 40
    unit: "시간/주"
    category: "근로"
    note: "주 40시간 (한국 근로기준법)"

# ========================================
# 법률 (한국 기준)
# ========================================

labor_laws:
  - id: LAW_LABOR_001
    pattern: "최저임금"
    value: 9860
    unit: "원/시간"
    year: 2024
    source: "고용노동부"
    category: "임금"
  
  - id: LAW_LABOR_002
    pattern: "법정.*공휴일|공휴일.*수"
    value: 15
    unit: "일/년"
    category: "휴일"
  
  - id: LAW_LABOR_003
    pattern: "연차.*일수|유급휴가"
    value: 15
    unit: "일/년"
    category: "휴가"
    note: "1년 근무 시 15일"

# ========================================
# 수학/물리 법칙
# ========================================

mathematical_laws:
  - id: LAW_MATH_001
    pattern: "확률"
    value_range: [0, 1]
    unit: "확률"
    category: "수학"
  
  - id: LAW_MATH_002
    pattern: "각도"
    value_range: [0, 360]
    unit: "도"
    category: "수학"
  
  - id: LAW_MATH_003
    pattern: "백분율|퍼센트"
    value_range: [0, 100]
    unit: "%"
    category: "수학"

physical_laws:
  - id: LAW_PHYS_001
    pattern: "절대영도"
    value: -273.15
    unit: "℃"
    category: "물리"
  
  - id: LAW_PHYS_002
    pattern: "광속|빛의.*속도"
    value: 299792458
    unit: "m/s"
    category: "물리"

# ========================================
# 비즈니스 제약 (논리적)
# ========================================

business_constraints:
  - id: LAW_BIZ_001
    pattern: "가격"
    value_range: [0, null]  # 0 이상
    unit: "원"
    category: "비즈니스"
  
  - id: LAW_BIZ_002
    pattern: "고객.*수|회원.*수"
    value_range: [0, null]
    unit: "명"
    category: "비즈니스"
```

#### 코드 수정

**`umis_rag/utils/law_loader.py`** (신규):

```python
import yaml
from pathlib import Path
from typing import Dict, List, Optional

class LawRulesLoader:
    """법칙 규칙 로더"""
    
    def __init__(self):
        config_path = Path(__file__).parent.parent.parent / "config" / "law_rules.yaml"
        
        with open(config_path, 'r', encoding='utf-8') as f:
            self.rules = yaml.safe_load(f)
    
    def find_law(self, question: str) -> Optional[Dict]:
        """질문에 맞는 법칙 찾기"""
        import re
        
        # 모든 카테고리 검색
        for category in ['time_laws', 'labor_laws', 'mathematical_laws', ...]:
            for law in self.rules.get(category, []):
                pattern = law.get('pattern', '')
                if re.search(pattern, question):
                    return law
        
        return None
```

**`multilayer_guestimation.py` 수정**:

```python
def _try_law_based(self, question):
    # YAML에서 법칙 로드
    from umis_rag.utils.law_loader import LawRulesLoader
    
    if not hasattr(self, 'law_loader'):
        self.law_loader = LawRulesLoader()
    
    law = self.law_loader.find_law(question)
    
    if law:
        result.value = law.get('value')
        result.value_range = law.get('value_range')
        result.confidence = 1.0
        result.logic_steps.append(f"✅ Layer 4: {law['id']} 적용")
        return result
    
    # 없으면 Layer 5로
    return result
```

#### 장점
- ✅ 확장 쉬움 (YAML 편집만)
- ✅ 카테고리별 관리
- ✅ ID 기반 추적
- ✅ 메타데이터 포함 (출처, 연도 등)

---

## 🧠 Layer 5: 행동경제학

### 정의

**예측 가능한 인간의 비합리적 행동 패턴**
- Loss Aversion: 손실 회피 > 이득 (2배)
- Temporal Discounting: 현재 > 미래
- Anchoring: 첫 정보에 고정
- Endowment Effect: 소유 가치 > 객관 가치

**특징**:
- 신뢰도: 70% (일반적 경향)
- 비율/배율 제공
- 기준값 필요

---

### 현재 구현 (30%)

**지원**: Loss Aversion **인식만**

```python
if '손실' in question or '해지' in question:
    result.logic_steps.append("💡 Loss Aversion 적용 가능")
    result.logic_steps.append("   → 2배")
    # 하지만 값은 반환 안 함!
    return result  # 실패 처리
```

**문제점**:
- 패턴만 인식
- 실제 값 미반환
- 1개 편향만 지원

---

### 설계 제안: 편향 + 기본값 시스템

#### 파일 구조

**`config/behavioral_rules.yaml`** (신규):

```yaml
# ========================================
# 행동경제학 규칙 (Layer 5)
# ========================================

version: "1.0"

# ========================================
# 편향 패턴
# ========================================

behavioral_biases:
  
  # Loss Aversion (손실 회피)
  - id: BEHAV_001
    name: "Loss Aversion"
    pattern_keywords:
      - "손실"
      - "해지"
      - "이탈"
      - "취소"
    
    context_keywords:
      - "가입"
      - "구독"
      - "유지"
    
    # 기본값 + 조정
    defaults:
      - context: "SaaS 구독"
        base_metric: "churn_rate"
        base_value: 0.05      # 일반 해지율 5%
        adjustment: 0.5       # Loss Aversion으로 절반
        final_value: 0.025    # 2.5%
      
      - context: "가격 인상"
        base_metric: "price_sensitivity"
        base_value: 1.0
        adjustment: 2.0       # 손실은 2배 민감
        final_value: 2.0
    
    multiplier: 2.0
    confidence: 0.7
  
  # Temporal Discounting (시간 할인)
  - id: BEHAV_002
    name: "Temporal Discounting"
    pattern_keywords:
      - "현재가치"
      - "할인율"
      - "시간가치"
    
    defaults:
      - context: "1년 후"
        discount_rate: 0.10   # 연 10% 할인
      
      - context: "5년 후"
        discount_rate: 0.40   # 연 10% * 5년 복리
    
    formula: "PV = FV / (1 + r)^n"
    confidence: 0.6
  
  # Anchoring (기준점 편향)
  - id: BEHAV_003
    name: "Anchoring"
    pattern_keywords:
      - "첫.*인상"
      - "기준.*가격"
      - "정가"
    
    defaults:
      - context: "할인 후 구매율"
        base_rate: 0.02       # 일반 구매율 2%
        with_anchor: 0.05     # Anchor 효과로 2.5배
    
    multiplier: 2.5
    confidence: 0.65
  
  # Endowment Effect (보유 효과)
  - id: BEHAV_004
    name: "Endowment Effect"
    pattern_keywords:
      - "보유.*가치"
      - "소유.*효과"
    
    defaults:
      - context: "보유 제품 평가"
        objective_value: 1.0
        perceived_value: 1.3  # 30% 높게 평가
    
    multiplier: 1.3
    confidence: 0.65
```

#### 코드 수정

**`umis_rag/utils/behavioral_loader.py`** (신규):

```python
class BehavioralRulesLoader:
    """행동경제학 규칙 로더"""
    
    def find_bias(self, question: str) -> Optional[Dict]:
        """질문에 맞는 편향 찾기"""
        
        for bias in self.rules['behavioral_biases']:
            # 패턴 매칭
            pattern_match = any(kw in question for kw in bias['pattern_keywords'])
            context_match = any(kw in question for kw in bias.get('context_keywords', []))
            
            if pattern_match and context_match:
                return bias
        
        return None
    
    def get_default_value(self, bias: Dict, question: str) -> Optional[float]:
        """기본값 + 조정 계산"""
        
        defaults = bias.get('defaults', [])
        
        for default in defaults:
            context = default.get('context', '')
            if any(word in question for word in context.split()):
                return default.get('final_value')
        
        # Fallback: 첫 번째 기본값
        if defaults:
            return defaults[0].get('final_value')
        
        return None
```

**`multilayer_guestimation.py` 수정**:

```python
def _try_behavioral(self, question, target_profile):
    from umis_rag.utils.behavioral_loader import BehavioralRulesLoader
    
    if not hasattr(self, 'behavioral_loader'):
        self.behavioral_loader = BehavioralRulesLoader()
    
    # 편향 찾기
    bias = self.behavioral_loader.find_bias(question)
    
    if bias:
        # 기본값 사용
        value = self.behavioral_loader.get_default_value(bias, question)
        
        if value:
            result.value = value
            result.confidence = bias.get('confidence', 0.7)
            result.logic_steps.append(f"✅ Layer 5: {bias['name']} 적용")
            result.logic_steps.append(f"   기본값: {value}")
            result.used_data.append({
                'source': '행동경제학',
                'bias': bias['name'],
                'value': value
            })
            return result
    
    return result  # Layer 6으로
```

#### 사용 예시

**질문**: "SaaS 구독 해지율은?"

**처리**:
1. Loss Aversion 패턴 매칭 (해지 + 구독)
2. 기본값 로드: SaaS 구독 context
3. base_value: 0.05 → adjustment: 0.5
4. **최종**: 0.025 (2.5%) 반환!

---

## 📊 Layer 6: 통계 패턴

### 정의

**널리 알려진 통계적 법칙과 경험 법칙**
- 파레토: 80-20 법칙
- 정규분포: 68-95-99.7 법칙
- 멱함수 분포: Long Tail
- 업계 평균: 전환율, 해지율 등

**특징**:
- 신뢰도: 60% (일반적 경향)
- 산업/맥락에 따라 다름
- 기본값 제공

---

### 현재 구현 (40%)

**지원**: 파레토만

```python
if '상위' in question and '비율' in question:
    return 0.20  # 20% (하드코딩)
```

**문제점**:
- 파레토만 지원
- 정규분포: 인식만, 값 없음
- 업계 평균 없음

---

### 설계 제안: 통계 기본값 + 업계 평균

#### 파일 구조

**`config/statistical_defaults.yaml`** (신규):

```yaml
# ========================================
# 통계 패턴 및 기본값 (Layer 6)
# ========================================

version: "1.0"

# ========================================
# 통계 법칙
# ========================================

statistical_laws:
  
  # 파레토 법칙
  - id: STAT_PARETO_001
    name: "Pareto Principle (80-20)"
    pattern_keywords:
      - "상위"
      - "주요"
      - "핵심"
    
    value_keywords:
      - "비율"
      - "점유"
      - "%"
    
    values:
      top_20_percent: 0.20
      bottom_80_percent: 0.80
      top_contribution: 0.80  # 상위 20%가 80% 기여
    
    confidence: 0.6
  
  # 정규분포
  - id: STAT_NORMAL_001
    name: "Normal Distribution"
    pattern_keywords:
      - "대부분"
      - "보통"
      - "평균적"
    
    values:
      within_1sd: 0.68   # ±1SD
      within_2sd: 0.95   # ±2SD
      within_3sd: 0.997  # ±3SD
    
    confidence: 0.5

# ========================================
# 업계 평균 (Industry Averages)
# ========================================

industry_averages:
  
  # SaaS 업계
  saas:
    - metric: "conversion_rate"
      keywords: ["전환율", "가입률"]
      value: 0.02
      range: [0.01, 0.05]
      source: "SaaS 업계 평균"
      confidence: 0.6
    
    - metric: "churn_rate_monthly"
      keywords: ["월간.*해지율", "월.*이탈"]
      value: 0.05
      range: [0.03, 0.10]
      segment: "B2B SaaS"
      confidence: 0.6
    
    - metric: "churn_rate_annual"
      keywords: ["연간.*해지율", "연.*이탈"]
      value: 0.40
      range: [0.20, 0.60]
      confidence: 0.5
    
    - metric: "ltv_cac_ratio"
      keywords: ["LTV.*CAC", "고객가치.*획득비용"]
      value: 3.0
      range: [2.0, 5.0]
      source: "SaaS 건강 지표"
      confidence: 0.7
  
  # 이커머스
  ecommerce:
    - metric: "cart_abandonment"
      keywords: ["장바구니.*이탈", "카트.*포기"]
      value: 0.70
      range: [0.60, 0.80]
      confidence: 0.65
    
    - metric: "return_rate"
      keywords: ["반품률", "환불률"]
      value: 0.10
      range: [0.05, 0.20]
      confidence: 0.6
  
  # 마케팅
  marketing:
    - metric: "email_open_rate"
      keywords: ["이메일.*오픈", "메일.*열람"]
      value: 0.20
      range: [0.15, 0.25]
      confidence: 0.65
    
    - metric: "click_through_rate"
      keywords: ["클릭률", "CTR"]
      value: 0.03
      range: [0.02, 0.05]
      confidence: 0.6
    
    - metric: "social_engagement"
      keywords: ["참여율", "인게이지먼트"]
      value: 0.02
      range: [0.01, 0.05]
      confidence: 0.5
```

#### 코드 구현

```python
class StatisticalDefaultsLoader:
    """통계 기본값 로더"""
    
    def find_average(self, question: str) -> Optional[Dict]:
        """업계 평균 찾기"""
        
        # 모든 산업 검색
        for industry in ['saas', 'ecommerce', 'marketing']:
            for avg in self.rules['industry_averages'][industry]:
                # 키워드 매칭
                if any(kw in question for kw in avg['keywords']):
                    return avg
        
        return None

def _try_statistical(self, question):
    from umis_rag.utils.statistical_loader import StatisticalDefaultsLoader
    
    if not hasattr(self, 'stat_loader'):
        self.stat_loader = StatisticalDefaultsLoader()
    
    # 1. 통계 법칙 확인 (파레토 등)
    # ... 기존 코드 ...
    
    # 2. 업계 평균 확인 (신규!)
    avg = self.stat_loader.find_average(question)
    
    if avg:
        result.value = avg['value']
        result.value_range = avg.get('range')
        result.confidence = avg.get('confidence', 0.6)
        result.logic_steps.append(f"✅ Layer 6: 업계 평균 '{avg['metric']}'")
        result.logic_steps.append(f"   평균: {avg['value']}")
        if avg.get('range'):
            result.logic_steps.append(f"   범위: {avg['range']}")
        result.used_data.append({
            'source': '통계 기본값',
            'metric': avg['metric'],
            'industry': question,  # 추론
            'value': avg['value']
        })
        return result
    
    return result
```

#### 사용 예시

**질문**: "SaaS 월간 해지율은?"

**처리**:
1. 업계 평균 매칭: "월간.*해지율"
2. SaaS 카테고리 확인
3. 기본값: 0.05 (5%)
4. **최종**: 5% 반환!

---

## 🔒 Layer 8: 제약조건

### 정의

**논리적, 물리적 경계값 (최소/최대)**
- 비율: 0-100%
- 가격: 0 이상
- 시장 점유율: 0-100%
- 성장률: 음수 가능, 상한 있음

**특징**:
- 신뢰도: 50% (범위만 제공)
- 정확한 값 아닌 Boundary
- 최후 수단

---

### 현재 구현 (60%)

**지원**: 비율, 시간 제약만

```python
if '비율' in question:
    return (0.0, 1.0)  # 0-100%

if '시간' in question and '재방문' in question:
    return (0, 90)  # 0-90일
```

**문제점**:
- 시간, 비율만
- 비즈니스 제약 없음
- 하드코딩

---

### 설계 제안: 제약 규칙 확대

#### 파일 구조

**`config/constraint_rules.yaml`** (신규):

```yaml
# ========================================
# 제약조건 규칙 (Layer 8)
# ========================================

version: "1.0"

# ========================================
# 일반 제약
# ========================================

general_constraints:
  
  - id: CONST_001
    pattern: "비율|점유율|%"
    min: 0
    max: 1
    unit: "비율"
    category: "일반"
  
  - id: CONST_002
    pattern: "가격|금액|매출"
    min: 0
    max: null  # 무제한
    unit: "원"
    category: "비즈니스"
  
  - id: CONST_003
    pattern: "고객.*수|회원.*수|사용자.*수"
    min: 0
    max: null
    unit: "명"
    category: "비즈니스"

# ========================================
# 시간 제약
# ========================================

time_constraints:
  - pattern: "하루"
    min: 0
    max: 24
    unit: "시간"
  
  - pattern: "주"
    min: 0
    max: 7
    unit: "일"
  
  - pattern: "재방문.*주기"
    min: 0
    max: 90
    unit: "일"
    note: "일반적으로 3개월 이내"
  
  - pattern: "구독.*기간"
    min: 1
    max: 60
    unit: "개월"
    note: "1개월 ~ 5년"

# ========================================
# 비즈니스 제약
# ========================================

business_constraints:
  - pattern: "성장률"
    min: -0.99  # -99% (거의 0)
    max: 10.0   # 1000% (10배)
    unit: "배율"
    note: "음수 가능 (축소)"
  
  - pattern: "시장.*점유율"
    min: 0
    max: 1
    unit: "비율"
    note: "독점도 100% 불가능 (99% 상한)"
  
  - pattern: "ARPU|객단가"
    min: 1000    # 최소 1,000원
    max: 10000000  # 현실적 상한 1,000만원
    unit: "원"
  
  - pattern: "CAC|고객획득비용"
    min: 1000
    max: 5000000  # 500만원 상한
    unit: "원"

# ========================================
# 산업별 제약
# ========================================

industry_specific:
  saas:
    - metric: "monthly_churn"
      min: 0.001   # 0.1%
      max: 0.20    # 20%
      typical: 0.05
    
    - metric: "annual_churn"
      min: 0.01
      max: 0.80
      typical: 0.40
  
  ecommerce:
    - metric: "conversion_rate"
      min: 0.001
      max: 0.10
      typical: 0.02
```

#### 코드 구현

```python
class ConstraintRulesLoader:
    """제약조건 로더"""
    
    def find_constraint(self, question: str) -> Optional[Dict]:
        """제약조건 찾기"""
        
        # 일반 제약
        for const in self.rules['general_constraints']:
            if re.search(const['pattern'], question):
                return const
        
        # 시간 제약
        for const in self.rules['time_constraints']:
            if re.search(const['pattern'], question):
                return const
        
        # 비즈니스 제약
        for const in self.rules['business_constraints']:
            if re.search(const['pattern'], question):
                return const
        
        return None

def _try_constraint_boundary(self, question):
    from umis_rag.utils.constraint_loader import ConstraintRulesLoader
    
    if not hasattr(self, 'constraint_loader'):
        self.constraint_loader = ConstraintRulesLoader()
    
    constraint = self.constraint_loader.find_constraint(question)
    
    if constraint:
        result.value_range = (constraint['min'], constraint['max'])
        result.confidence = 0.5
        result.logic_steps.append(f"✅ Layer 8: {constraint['id']} 적용")
        result.logic_steps.append(f"   범위: {constraint['min']} ~ {constraint['max']} {constraint['unit']}")
        result.used_data.append({
            'source': '제약조건',
            'constraint': constraint['id'],
            'range': (constraint['min'], constraint['max'])
        })
        return result
    
    # 추정 불가
    return result
```

---

## 📋 구현 계획

### Phase 1: YAML 파일 생성 (20분)

1. `config/law_rules.yaml` - Layer 4용
2. `config/behavioral_rules.yaml` - Layer 5용
3. `config/statistical_defaults.yaml` - Layer 6용
4. `config/constraint_rules.yaml` - Layer 8용

### Phase 2: 로더 클래스 (30분)

1. `umis_rag/utils/law_loader.py`
2. `umis_rag/utils/behavioral_loader.py`
3. `umis_rag/utils/statistical_loader.py`
4. `umis_rag/utils/constraint_loader.py`

### Phase 3: 통합 (20분)

1. `multilayer_guestimation.py` 수정
2. Lazy 로딩 구조
3. 테스트

**총 예상 시간**: 70분

---

## 🎯 완성 후 효과

### Before (현재)
- Layer 1, 2, 3, 7: 100%
- Layer 4, 5, 6, 8: 30-80%
- **종합**: 82%

### After (완성 시)
- Layer 1-8 모두: 95%+
- **종합**: 97%

### 실전 효과
- ✅ 해지율 질문 → Layer 5 (행동경제학) 즉시 답변
- ✅ 업계 평균 질문 → Layer 6 (통계) 즉시 답변
- ✅ 최저임금 질문 → Layer 4 (법률) 즉시 답변
- ✅ 가격 범위 질문 → Layer 8 (제약) 경계값 제공

---

## 💡 우선순위 추천

### 즉시 구현 (권장) ⭐
- **Layer 6**: 업계 평균 (가장 유용)
  - SaaS 해지율, 전환율 등
  - 자주 질문되는 지표

### 중기 구현
- **Layer 4**: 법칙 확대
  - 최저임금, 근로시간 등
  - 한국 법률 중심

### 장기 구현
- **Layer 5**: 행동경제학 기본값
- **Layer 8**: 제약 규칙 확대

---

지금 Layer 4, 5, 6, 8을 확장하시겠습니까? 아니면 현재 상태(82%)로 v7.2.1 릴리즈하시겠습니까?

**제 추천**: 현재 상태로 릴리즈 후, Layer 6 (업계 평균)만 v7.2.2에서 추가하는 것이 효율적일 것 같습니다!
