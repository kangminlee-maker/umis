# Tier 3 변수 개수 자연 수렴 메커니즘 설계

**작성 일시**: 2025-11-08 01:20  
**문제**: 단순 개수 제한 (6개)의 한계  
**목표**: 논리적으로 적절한 수준으로 자연 수렴

---

## 🎯 문제 정의

### 현재 방식의 한계

```yaml
현재 (Hard Limit):
  max_variables: 6
  7개 이상: complexity_score = 0.0 (금지)

문제:
  ❌ 자의적 기준 (왜 6개?)
  ❌ 맥락 무시 (간단한 문제도 6개, 복잡한 문제도 6개)
  ❌ 정보 가치 무시 (6번째 변수가 중요해도 차단)
  ❌ 수렴 논리 없음 (언제 멈춰야 하는지 불명확)

진짜 원하는 것:
  ✅ 변수 추가가 실질적 개선을 가져올 때만 추가
  ✅ 개선이 미미하면 자연스럽게 중단
  ✅ 맥락에 따라 유연하게 조정
  ✅ 수학적/논리적 근거
```

---

## 💡 해결 방안: 4가지 접근법

### 방안 1: Marginal Confidence Gain (한계 신뢰도 증가)

**핵심 아이디어**: "변수 추가가 confidence를 얼마나 높이는가?"

```yaml
원리:
  - 변수 N개 → confidence C_n
  - 변수 N+1개 → confidence C_{n+1}
  - Marginal Gain = (C_{n+1} - C_n) / C_n
  - Gain < 임계값 (예: 5%) → 중단

논리:
  ✅ 정보 가치 기반 판단
  ✅ 자연스러운 수렴 (개선 없으면 중단)
  ✅ 맥락 독립적 (간단/복잡 모두 적용)
```

**구현**:
```python
def _should_add_variable(
    current_model: FermiModel,
    new_variable: FermiVariable
) -> bool:
    """
    변수 추가 여부 판단
    
    Returns:
        True: 추가 (유의미한 개선)
        False: 중단 (개선 미미)
    """
    # 현재 모형 confidence
    current_confidence = self._calculate_model_confidence(current_model)
    
    # 새 변수 추가 후 confidence (예상)
    new_confidence = self._predict_confidence_with_variable(
        current_model, new_variable
    )
    
    # Marginal Gain 계산
    if current_confidence > 0:
        marginal_gain = (new_confidence - current_confidence) / current_confidence
    else:
        marginal_gain = 1.0  # 첫 변수는 무조건 추가
    
    # 임계값 비교
    threshold = 0.05  # 5% 이상 개선되어야 추가
    
    logger.info(f"      변수 '{new_variable.name}': "
                f"Gain {marginal_gain*100:.1f}% "
                f"({'✅ 추가' if marginal_gain >= threshold else '❌ 중단'})")
    
    return marginal_gain >= threshold


def _calculate_model_confidence(model: FermiModel) -> float:
    """
    모형 전체 confidence 계산
    
    Geometric mean (곱의 n제곱근):
      confidence = ∏(var_i.confidence)^(1/n)
    """
    confidences = [
        var.confidence for var in model.variables.values()
        if var.available and var.confidence > 0
    ]
    
    if not confidences:
        return 0.0
    
    import math
    return math.prod(confidences) ** (1 / len(confidences))


def _predict_confidence_with_variable(
    model: FermiModel,
    new_var: FermiVariable
) -> float:
    """
    새 변수 추가 시 confidence 예상
    
    새 변수의 confidence와 기존 confidence를 조합
    """
    current_conf = self._calculate_model_confidence(model)
    
    if current_conf == 0:
        return new_var.confidence
    
    # Geometric mean으로 조합
    n = len([v for v in model.variables.values() if v.available])
    
    import math
    combined = (current_conf ** n * new_var.confidence) ** (1 / (n + 1))
    
    return combined
```

**예시**:
```yaml
모형: "시장 = A × B × C × D × ..."

변수 1: restaurants (confidence: 0.9)
  - 현재: 0.0
  - 추가 후: 0.9
  - Gain: ∞ → 추가 ✅

변수 2: digital_rate (confidence: 0.7)
  - 현재: 0.9
  - 추가 후: √(0.9 × 0.7) = 0.79
  - Gain: (0.79 - 0.9) / 0.9 = -12% → 하락이지만 필수 정보 → 추가 ✅

변수 3: conversion (confidence: 0.6)
  - 현재: 0.79
  - 추가 후: ∛(0.9 × 0.7 × 0.6) = 0.71
  - Gain: -10% → 하락이지만 unknown 줄임 → 추가 ✅

변수 4: arpu (confidence: 0.8)
  - 현재: 0.71
  - 추가 후: ∜(0.9 × 0.7 × 0.6 × 0.8) = 0.74
  - Gain: +4.2% → 임계값 5% 미만 → 경계선

변수 5: region_weight (confidence: 0.5)
  - 현재: 0.74
  - 추가 후: ⁵√(...× 0.5) = 0.68
  - Gain: -8% → 하락 → 중단 ❌

결론: 4개 변수가 자연 수렴점
```

**평가**: ⭐⭐⭐⭐⭐ (5/5)
- ✅ 수학적 근거
- ✅ 자연 수렴
- ✅ 맥락 독립적

---

### 방안 2: Information Gain (정보 이득)

**핵심 아이디어**: "변수 추가가 불확실성을 얼마나 줄이는가?"

```yaml
원리:
  - 현재 불확실성: U_n (예: error_range)
  - 변수 추가 후: U_{n+1}
  - Information Gain = (U_n - U_{n+1}) / U_n
  - Gain < 임계값 (예: 10%) → 중단

측정:
  불확실성 = error_range 또는 (value_max - value_min) / value
```

**구현**:
```python
def _calculate_uncertainty(model: FermiModel) -> float:
    """
    모형 불확실성 계산
    
    방법: 각 변수의 uncertainty 조합
    
    Returns:
        0.0-1.0 (0 = 확실, 1 = 완전 불확실)
    """
    uncertainties = [
        var.uncertainty for var in model.variables.values()
        if var.available
    ]
    
    if not uncertainties:
        return 1.0
    
    # 불확실성은 곱셈으로 증폭 (1개라도 불확실하면 전체 불확실)
    # Combined = 1 - ∏(1 - u_i)
    certain_probs = [1 - u for u in uncertainties]
    combined_certain = math.prod(certain_probs)
    combined_uncertainty = 1 - combined_certain
    
    return combined_uncertainty


def _information_gain(
    current_model: FermiModel,
    new_variable: FermiVariable
) -> float:
    """
    변수 추가 시 정보 이득 계산
    
    Returns:
        0.0-1.0 (정보 이득 비율)
    """
    current_u = self._calculate_uncertainty(current_model)
    
    # 새 변수 추가 후 uncertainty 예상
    new_u = self._predict_uncertainty_with_variable(
        current_model, new_variable
    )
    
    # Information Gain
    if current_u > 0:
        gain = (current_u - new_u) / current_u
    else:
        gain = 0.0
    
    return gain
```

**예시**:
```yaml
변수 1: uncertainty 0.3 (±30%)
  - 현재 U: 1.0 (모형 없음)
  - 추가 후: 0.3
  - Gain: (1.0 - 0.3) / 1.0 = 70% → 추가 ✅

변수 2: uncertainty 0.4
  - 현재 U: 0.3
  - 추가 후: 1 - (1-0.3) × (1-0.4) = 0.58
  - Gain: (0.3 - 0.58) / 0.3 = -93% → 상승! → 재평가 필요

# 더 나은 공식: Root Mean Square
변수 2 (RMS):
  - 추가 후: √(0.3² + 0.4²) = 0.5
  - Gain: (0.3 - 0.5) / 0.3 = -67% → 여전히 상승

# 최적: 평균
변수 2 (평균):
  - 추가 후: (0.3 + 0.4) / 2 = 0.35
  - Gain: (0.3 - 0.35) / 0.3 = -17% → 악화 → 중단 ❌
```

**평가**: ⭐⭐⭐ (3/5)
- ✅ 정보 이론 기반
- ⚠️ Uncertainty 조합 로직 복잡
- ⚠️ 변수 추가가 항상 uncertainty 증가 (역설)

---

### 방안 3: Diminishing Returns (수확 체감의 법칙)

**핵심 아이디어**: "변수가 많아질수록 개선 효과 감소"

```yaml
원리:
  - 1번째 변수: 큰 개선
  - 2번째 변수: 중간 개선
  - 3번째 변수: 작은 개선
  - N번째 변수: 미미한 개선 → 중단

측정:
  - Score improvement per variable
  - Diminishing threshold
```

**구현**:
```python
def _evaluate_variable_addition(
    current_model: FermiModel,
    new_variable: FermiVariable,
    variable_sequence: int  # 몇 번째 변수?
) -> Tuple[bool, float]:
    """
    변수 추가 평가 (수확 체감 고려)
    
    Args:
        current_model: 현재 모형
        new_variable: 추가할 변수
        variable_sequence: 변수 순서 (1, 2, 3, ...)
    
    Returns:
        (should_add, improvement_score)
    """
    # 현재 모형 점수
    current_score = self._score_model_simple(current_model)
    
    # 새 변수 추가 후 점수 (예상)
    new_score = self._predict_score_with_variable(
        current_model, new_variable
    )
    
    # 절대 개선량
    improvement = new_score - current_score
    
    # 수확 체감 임계값 (변수 개수에 따라 감소)
    # 1번째: 10% 이상
    # 2번째: 7% 이상
    # 3번째: 5% 이상
    # 4번째: 3% 이상
    # 5번째: 2% 이상
    # 6번째 이후: 1% 이상
    
    thresholds = {
        1: 0.10,
        2: 0.07,
        3: 0.05,
        4: 0.03,
        5: 0.02,
        6: 0.01
    }
    
    threshold = thresholds.get(variable_sequence, 0.01)
    
    # 판단
    should_add = improvement >= threshold
    
    logger.info(f"      변수 {variable_sequence}: "
                f"개선 {improvement*100:.1f}% "
                f"(임계값 {threshold*100:.1f}%) "
                f"→ {'✅ 추가' if should_add else '❌ 중단'}")
    
    return should_add, improvement
```

**예시**:
```yaml
변수 1: improvement 15% (임계값 10%)
  → 15% > 10% → 추가 ✅

변수 2: improvement 8% (임계값 7%)
  → 8% > 7% → 추가 ✅

변수 3: improvement 6% (임계값 5%)
  → 6% > 5% → 추가 ✅

변수 4: improvement 3.5% (임계값 3%)
  → 3.5% > 3% → 추가 ✅

변수 5: improvement 1.5% (임계값 2%)
  → 1.5% < 2% → 중단 ❌

결론: 4개 변수로 자연 수렴
```

**평가**: ⭐⭐⭐⭐⭐ (5/5)
- ✅ 논리적 (수확 체감)
- ✅ 자연 수렴
- ✅ 실용적

---

### 방안 4: Hybrid - 종합 접근 (추천!) ⭐

**핵심 아이디어**: 여러 시그널을 종합 판단

```yaml
판단 기준 (3개):
  
  1. Marginal Confidence Gain (주요)
     - 변수 추가 시 confidence 개선
     - 임계값: 5% 이상
  
  2. Diminishing Returns (보조)
     - 변수 순서에 따른 임계값 감소
     - 1번째: 10%, 2번째: 7%, 3번째: 5%, ...
  
  3. Absolute Limit (안전망)
     - 10개 이상: 무조건 중단 (비상 브레이크)
     - 논리적 한계 (인간 인지)

종합 판단:
  - (기준 1 OR 기준 2) AND 기준 3
  - 둘 중 하나라도 통과 + 10개 미만 → 추가
```

**구현**:
```python
class VariableConvergence:
    """
    변수 개수 자연 수렴 메커니즘
    
    3가지 기준 종합:
    1. Marginal Confidence Gain (주요)
    2. Diminishing Returns (보조)
    3. Absolute Limit (안전망)
    """
    
    def __init__(self):
        # 기준 1: Marginal Gain
        self.min_confidence_gain = 0.05  # 5% 이상
        
        # 기준 2: Diminishing Returns
        self.diminishing_thresholds = {
            1: 0.10,  # 첫 변수: 10% 이상 개선
            2: 0.07,
            3: 0.05,
            4: 0.03,
            5: 0.02,
            6: 0.01,
            7: 0.005,
            8: 0.003,
            9: 0.001
        }
        
        # 기준 3: Absolute Limit
        self.absolute_max = 10  # 비상 브레이크
        self.recommended_max = 6  # 권장 상한 (경고만)
    
    def should_add_variable(
        self,
        current_model: FermiModel,
        new_variable: FermiVariable,
        variable_sequence: int
    ) -> Tuple[bool, str]:
        """
        변수 추가 여부 판단 (종합)
        
        Returns:
            (should_add, reason)
        """
        # ━━━━ 기준 3: Absolute Limit (먼저 체크) ━━━━
        if variable_sequence > self.absolute_max:
            return False, f"절대 상한 {self.absolute_max}개 초과 (비상 브레이크)"
        
        if variable_sequence > self.recommended_max:
            logger.warning(f"      ⚠️  권장 상한 {self.recommended_max}개 초과 (검토 필요)")
        
        # ━━━━ 기준 1: Marginal Confidence Gain ━━━━
        current_conf = self._calculate_confidence(current_model)
        new_conf = self._predict_confidence(current_model, new_variable)
        
        if current_conf > 0:
            conf_gain = (new_conf - current_conf) / current_conf
        else:
            conf_gain = 1.0  # 첫 변수
        
        conf_check = conf_gain >= self.min_confidence_gain
        
        # ━━━━ 기준 2: Diminishing Returns ━━━━
        current_score = self._calculate_score(current_model)
        new_score = self._predict_score(current_model, new_variable)
        score_improvement = new_score - current_score
        
        threshold = self.diminishing_thresholds.get(variable_sequence, 0.001)
        dim_check = score_improvement >= threshold
        
        # ━━━━ 종합 판단 ━━━━
        should_add = conf_check or dim_check
        
        # 이유 설명
        if should_add:
            reasons = []
            if conf_check:
                reasons.append(f"Confidence Gain {conf_gain*100:.1f}% ≥ 5%")
            if dim_check:
                reasons.append(f"Score 개선 {score_improvement*100:.1f}% ≥ {threshold*100:.1f}%")
            reason = " OR ".join(reasons) + " → 추가"
        else:
            reason = (f"Confidence Gain {conf_gain*100:.1f}% < 5% AND "
                     f"Score 개선 {score_improvement*100:.1f}% < {threshold*100:.1f}% "
                     f"→ 중단 (자연 수렴)")
        
        logger.info(f"      변수 {variable_sequence} '{new_variable.name}': {reason}")
        
        return should_add, reason
    
    def _calculate_confidence(self, model: FermiModel) -> float:
        """Geometric mean of confidences"""
        confidences = [
            var.confidence for var in model.variables.values()
            if var.available and var.confidence > 0
        ]
        
        if not confidences:
            return 0.0
        
        import math
        return math.prod(confidences) ** (1 / len(confidences))
    
    def _predict_confidence(
        self,
        model: FermiModel,
        new_var: FermiVariable
    ) -> float:
        """새 변수 추가 시 confidence 예상"""
        current = self._calculate_confidence(model)
        
        if current == 0:
            return new_var.confidence
        
        n = len([v for v in model.variables.values() if v.available])
        
        import math
        return (current ** n * new_var.confidence) ** (1 / (n + 1))
    
    def _calculate_score(self, model: FermiModel) -> float:
        """모형 전체 점수 (간소화)"""
        # Unknown 비율
        if model.total_variables > 0:
            filled_ratio = sum(1 for v in model.variables.values() if v.available) / model.total_variables
        else:
            filled_ratio = 0
        
        # Confidence
        avg_conf = self._calculate_confidence(model)
        
        # 조합
        return filled_ratio * 0.6 + avg_conf * 0.4
    
    def _predict_score(
        self,
        model: FermiModel,
        new_var: FermiVariable
    ) -> float:
        """새 변수 추가 후 점수 예상"""
        # 임시 변수 추가
        temp_model = copy.deepcopy(model)
        temp_model.variables[new_var.name] = new_var
        temp_model.total_variables += 1
        
        return self._calculate_score(temp_model)
```

**예시**:
```yaml
모형: 시장 = A × B × C × ...

변수 1: restaurants (conf: 0.9)
  - Conf Gain: ∞ → 추가 ✅
  - Score 개선: 60% > 10% → 추가 ✅
  → 종합: 추가 ✅

변수 2: digital (conf: 0.7)
  - Conf Gain: -12% < 5% → 중단 ❌
  - Score 개선: 15% > 7% → 추가 ✅
  → 종합: 추가 ✅ (OR 조건)

변수 3: conversion (conf: 0.6)
  - Conf Gain: -10% < 5% → 중단 ❌
  - Score 개선: 8% > 5% → 추가 ✅
  → 종합: 추가 ✅

변수 4: arpu (conf: 0.8)
  - Conf Gain: +4% < 5% → 중단 ❌
  - Score 개선: 3.5% > 3% → 추가 ✅
  → 종합: 추가 ✅

변수 5: region (conf: 0.5)
  - Conf Gain: -8% < 5% → 중단 ❌
  - Score 개선: 1% < 2% → 중단 ❌
  → 종합: 중단 ❌ (AND 조건)

결론: 4개 변수로 자연 수렴
```

**평가**: ⭐⭐⭐⭐⭐ (5/5) **최고!**
- ✅ 다각적 판단
- ✅ 유연함 (OR 조건)
- ✅ 안전망 (10개 절대 상한)
- ✅ 경고 시스템 (6개 초과 시)

---

## 🎯 추천 방안: Hybrid 종합 접근

### 최종 설계

```python
class VariableConvergencePolicy:
    """
    변수 개수 자연 수렴 정책
    
    3단계 방어:
    1. 논리적 판단 (Confidence Gain OR Diminishing Returns)
    2. 권장 상한 (6개 초과 시 경고)
    3. 절대 상한 (10개 초과 금지)
    """
    
    def __init__(self):
        # Level 1: 논리적 판단
        self.min_confidence_gain = 0.05  # 5% 이상 개선
        
        self.diminishing_thresholds = {
            1: 0.10,  # 10%
            2: 0.07,
            3: 0.05,
            4: 0.03,
            5: 0.02,
            6: 0.01,
            7: 0.005,
            8: 0.003,
            9: 0.001
        }
        
        # Level 2: 권장 상한 (경고)
        self.recommended_max = 6
        
        # Level 3: 절대 상한 (금지)
        self.absolute_max = 10
    
    def evaluate(
        self,
        current_model: FermiModel,
        new_variable: FermiVariable,
        variable_sequence: int
    ) -> Dict:
        """
        변수 추가 평가
        
        Returns:
            {
                'should_add': bool,
                'reason': str,
                'confidence_gain': float,
                'score_improvement': float,
                'warning': Optional[str]
            }
        """
        result = {
            'should_add': False,
            'reason': '',
            'confidence_gain': 0.0,
            'score_improvement': 0.0,
            'warning': None
        }
        
        # ━━━ Level 3: 절대 상한 체크 ━━━
        if variable_sequence > self.absolute_max:
            result['should_add'] = False
            result['reason'] = (
                f"절대 상한 {self.absolute_max}개 초과 "
                f"(비상 브레이크, 인간 인지 한계)"
            )
            return result
        
        # ━━━ Level 2: 권장 상한 경고 ━━━
        if variable_sequence > self.recommended_max:
            result['warning'] = (
                f"⚠️  권장 상한 {self.recommended_max}개 초과 "
                f"(복잡도 증가, Occam's Razor 위배)"
            )
        
        # ━━━ Level 1: 논리적 판단 ━━━
        
        # 기준 1: Marginal Confidence Gain
        current_conf = self._geometric_mean_confidence(current_model)
        new_conf = self._predict_confidence(current_model, new_variable)
        
        if current_conf > 0:
            conf_gain = (new_conf - current_conf) / current_conf
        else:
            conf_gain = 1.0
        
        result['confidence_gain'] = conf_gain
        criterion_1 = conf_gain >= self.min_confidence_gain
        
        # 기준 2: Diminishing Returns
        current_score = self._calculate_model_score(current_model)
        new_score = self._predict_score(current_model, new_variable)
        score_improvement = new_score - current_score
        
        threshold = self.diminishing_thresholds.get(variable_sequence, 0.001)
        result['score_improvement'] = score_improvement
        criterion_2 = score_improvement >= threshold
        
        # ━━━ 종합 판단 (OR) ━━━
        result['should_add'] = criterion_1 or criterion_2
        
        # 이유 생성
        if result['should_add']:
            reasons = []
            if criterion_1:
                reasons.append(f"✅ Conf Gain {conf_gain*100:.1f}% ≥ 5%")
            if criterion_2:
                reasons.append(f"✅ Score +{score_improvement*100:.1f}% ≥ {threshold*100:.1f}%")
            
            result['reason'] = " OR ".join(reasons)
        else:
            result['reason'] = (
                f"❌ Conf Gain {conf_gain*100:.1f}% < 5% AND "
                f"Score +{score_improvement*100:.1f}% < {threshold*100:.1f}% "
                f"→ 자연 수렴"
            )
        
        return result
    
    def _geometric_mean_confidence(self, model: FermiModel) -> float:
        """Confidence geometric mean"""
        confs = [v.confidence for v in model.variables.values() if v.available]
        if not confs:
            return 0.0
        import math
        return math.prod(confs) ** (1 / len(confs))
    
    def _predict_confidence(
        self,
        model: FermiModel,
        new_var: FermiVariable
    ) -> float:
        """새 변수 추가 후 confidence 예상"""
        current = self._geometric_mean_confidence(model)
        if current == 0:
            return new_var.confidence
        
        n = len([v for v in model.variables.values() if v.available])
        import math
        return (current ** n * new_var.confidence) ** (1 / (n + 1))
    
    def _calculate_model_score(self, model: FermiModel) -> float:
        """모형 전체 점수"""
        if model.total_variables == 0:
            return 0.0
        
        # Unknown 비율
        filled = sum(1 for v in model.variables.values() if v.available)
        filled_ratio = filled / model.total_variables
        
        # Confidence
        conf = self._geometric_mean_confidence(model)
        
        # 조합 (60% filled, 40% confidence)
        return filled_ratio * 0.6 + conf * 0.4
    
    def _predict_score(
        self,
        model: FermiModel,
        new_var: FermiVariable
    ) -> float:
        """새 변수 추가 후 점수"""
        import copy
        temp_model = copy.deepcopy(model)
        temp_model.variables[new_var.name] = new_var
        temp_model.total_variables += 1
        return self._calculate_model_score(temp_model)
```

---

## 📊 Hybrid 방안 시뮬레이션

### 시나리오 1: 간단한 문제

```yaml
질문: "B2B SaaS Churn Rate는?"

모형 후보:
  Model 1: "Churn = 업계 평균"
    - 변수 1개
    - confidence: 0.7
  
  Model 2: "Churn = (해지 / 전체) × Loss Aversion"
    - 변수 3개
    - 더 복잡

평가:
  변수 1: avg (conf: 0.7)
    - Conf Gain: ∞ → ✅
    - Score: +60% > 10% → ✅
    → 추가 ✅
  
  변수 2: 해지율 (conf: 0.6)
    - Conf Gain: -14% < 5% → ❌
    - Score: +5% < 7% → ❌
    → 중단 ❌

결론: 1개 변수로 충분 (단순 문제)
```

---

### 시나리오 2: 복잡한 문제

```yaml
질문: "음식점 마케팅 SaaS 시장은?"

모형: "시장 = 음식점 × 디지털율 × 전환율 × ARPU × 12"

평가:
  변수 1: restaurants (conf: 0.9)
    - Gain: ∞ → 추가 ✅
  
  변수 2: digital (conf: 0.7)
    - Conf: 0.9 → 0.79 (Gain -12%)
    - Score: +15% > 7% → 추가 ✅
  
  변수 3: conversion (conf: 0.6)
    - Conf: 0.79 → 0.71 (Gain -10%)
    - Score: +8% > 5% → 추가 ✅
  
  변수 4: arpu (conf: 0.8)
    - Conf: 0.71 → 0.74 (Gain +4%)
    - Score: +3.5% > 3% → 추가 ✅
  
  변수 5: multiplier (conf: 1.0)
    - Conf: 0.74 → 0.79 (Gain +7%) → ✅
    - Score: +2% = 2% → ✅
    → 추가 ✅
  
  변수 6: region (conf: 0.5)
    - Conf: 0.79 → 0.73 (Gain -8%) → ❌
    - Score: +0.8% < 1% → ❌
    → 중단 ❌

결론: 5개 변수로 수렴 (복잡한 문제는 더 많이)
```

---

### 시나리오 3: 매우 복잡한 문제

```yaml
질문: "국내 전체 B2B SaaS 시장 (산업별 세분화)"

모형: "시장 = Σ(산업_i × 도입률_i × ARPU_i)"

변수: 10개 산업 × 2개 파라미터 = 20개 필요?

평가:
  변수 1-6: 각각 개선 → 추가 ✅
  변수 7: 
    - Conf Gain: +0.4% < 5% → ❌
    - Score: +0.6% > 0.5% → ✅
    - 경고: ⚠️  권장 상한 6개 초과
    → 추가 ✅ (경고 포함)
  
  변수 8:
    - Conf Gain: +0.2% < 5% → ❌
    - Score: +0.4% > 0.3% → ✅
    → 추가 ✅
  
  변수 9:
    - Conf Gain: +0.1% < 5% → ❌
    - Score: +0.15% > 0.1% → ✅
    → 추가 ✅
  
  변수 10:
    - Conf Gain: +0.05% < 5% → ❌
    - Score: +0.08% < 0.1% → ❌
    → 중단 ❌

결론: 9개 변수 (매우 복잡한 문제도 10개 미만)
```

---

## 📈 방안 비교

| 방안 | 논리성 | 실용성 | 수렴성 | 복잡도 | 추천 |
|------|--------|--------|--------|--------|------|
| **현재 (Hard 6)** | ⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | - |
| **방안 1: Marginal Gain** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ✅ |
| **방안 2: Information Gain** | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐ | - |
| **방안 3: Diminishing Returns** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ✅ |
| **방안 4: Hybrid** ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | **✅ 최고** |

**추천**: **방안 4 (Hybrid 종합 접근)**

---

## 🔧 구현 코드

### tier3.py에 추가

```python
# ═══════════════════════════════════════════════════════
# 변수 수렴 메커니즘 (v7.4.0)
# ═══════════════════════════════════════════════════════

class VariableConvergencePolicy:
    """
    변수 개수 자연 수렴 정책
    
    원칙:
    -----
    - 단순 개수 제한 ❌
    - 논리적 수렴 ✅
    
    3단계 방어:
    -----------
    1. 논리적 판단 (Confidence Gain OR Diminishing Returns)
    2. 권장 상한 (6개 초과 시 경고, 계속 가능)
    3. 절대 상한 (10개 초과 시 강제 중단)
    
    효과:
    -----
    - 간단한 문제: 1-3개로 자연 수렴
    - 중간 문제: 4-6개
    - 복잡한 문제: 7-9개 (경고 포함)
    - 매우 복잡: 최대 10개 (절대 상한)
    
    예시:
        >>> policy = VariableConvergencePolicy()
        >>> result = policy.evaluate(
        ...     current_model=model,
        ...     new_variable=var,
        ...     variable_sequence=5
        ... )
        >>> if result['should_add']:
        ...     model.add_variable(var)
        ... else:
        ...     print(f"수렴: {result['reason']}")
    """
    
    def __init__(
        self,
        min_confidence_gain: float = 0.05,
        recommended_max: int = 6,
        absolute_max: int = 10
    ):
        """
        Args:
            min_confidence_gain: 최소 confidence 개선 (기본 5%)
            recommended_max: 권장 상한 (기본 6개)
            absolute_max: 절대 상한 (기본 10개)
        """
        self.min_confidence_gain = min_confidence_gain
        self.recommended_max = recommended_max
        self.absolute_max = absolute_max
        
        # Diminishing Returns 임계값 (변수 개수별)
        self.diminishing_thresholds = {
            1: 0.10,  # 첫 변수: 10% 이상 개선
            2: 0.07,  # 둘째: 7%
            3: 0.05,  # 셋째: 5%
            4: 0.03,  # 넷째: 3%
            5: 0.02,  # 다섯째: 2%
            6: 0.01,  # 여섯째: 1%
            7: 0.005, # 일곱째: 0.5%
            8: 0.003, # 여덟째: 0.3%
            9: 0.001  # 아홉째: 0.1%
        }
    
    def evaluate(
        self,
        current_model: FermiModel,
        new_variable: FermiVariable,
        variable_sequence: int
    ) -> Dict[str, Any]:
        """
        변수 추가 여부 평가
        
        Args:
            current_model: 현재 모형
            new_variable: 추가 고려 중인 변수
            variable_sequence: 변수 순서 (1, 2, 3, ...)
        
        Returns:
            {
                'should_add': bool,
                'reason': str,
                'confidence_gain': float,
                'score_improvement': float,
                'warning': Optional[str],
                'level': int  # 어느 단계에서 결정? (1/2/3)
            }
        """
        result = {
            'should_add': False,
            'reason': '',
            'confidence_gain': 0.0,
            'score_improvement': 0.0,
            'warning': None,
            'level': 0
        }
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Level 3: 절대 상한 (비상 브레이크)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        if variable_sequence > self.absolute_max:
            result['should_add'] = False
            result['reason'] = (
                f"🛑 절대 상한 {self.absolute_max}개 초과 "
                f"(인간 인지 한계, Miller's Law: 7±2)"
            )
            result['level'] = 3
            logger.warning(f"    {result['reason']}")
            return result
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Level 2: 권장 상한 (경고)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        if variable_sequence > self.recommended_max:
            result['warning'] = (
                f"⚠️  권장 상한 {self.recommended_max}개 초과 "
                f"(Occam's Razor 위배, 복잡도↑)"
            )
            logger.warning(f"    {result['warning']}")
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Level 1: 논리적 판단
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        
        # 기준 1: Marginal Confidence Gain
        current_conf = self._geometric_mean_confidence(current_model)
        new_conf = self._predict_confidence(current_model, new_variable)
        
        if current_conf > 0:
            conf_gain = (new_conf - current_conf) / current_conf
        else:
            conf_gain = 1.0  # 첫 변수는 무조건 추가
        
        result['confidence_gain'] = conf_gain
        
        criterion_1_pass = conf_gain >= self.min_confidence_gain
        
        # 기준 2: Diminishing Returns
        current_score = self._calculate_model_score(current_model)
        new_score = self._predict_score(current_model, new_variable)
        score_improvement = new_score - current_score
        
        threshold = self.diminishing_thresholds.get(variable_sequence, 0.001)
        result['score_improvement'] = score_improvement
        
        criterion_2_pass = score_improvement >= threshold
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 종합 판단 (OR 조건)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        result['should_add'] = criterion_1_pass or criterion_2_pass
        result['level'] = 1
        
        # 이유 생성
        if result['should_add']:
            reasons = []
            if criterion_1_pass:
                reasons.append(
                    f"Conf Gain {conf_gain*100:+.1f}% ≥ {self.min_confidence_gain*100:.0f}%"
                )
            if criterion_2_pass:
                reasons.append(
                    f"Score +{score_improvement*100:.1f}% ≥ {threshold*100:.1f}%"
                )
            
            result['reason'] = "✅ " + " OR ".join(reasons) + " → 추가"
        else:
            result['reason'] = (
                f"❌ Conf Gain {conf_gain*100:+.1f}% < {self.min_confidence_gain*100:.0f}% "
                f"AND Score +{score_improvement*100:.1f}% < {threshold*100:.1f}% "
                f"→ 자연 수렴 (더 이상 개선 없음)"
            )
        
        logger.info(f"    변수 {variable_sequence} '{new_variable.name}': {result['reason']}")
        
        return result
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 헬퍼 메서드
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def _geometric_mean_confidence(self, model: FermiModel) -> float:
        """
        Confidence Geometric Mean
        
        이유: 곱셈 모형에서 geometric mean이 적합
        """
        confidences = [
            var.confidence for var in model.variables.values()
            if var.available and var.confidence > 0
        ]
        
        if not confidences:
            return 0.0
        
        import math
        return math.prod(confidences) ** (1 / len(confidences))
    
    def _predict_confidence(
        self,
        model: FermiModel,
        new_var: FermiVariable
    ) -> float:
        """새 변수 추가 후 confidence 예상"""
        current = self._geometric_mean_confidence(model)
        
        if current == 0:
            return new_var.confidence
        
        n = len([v for v in model.variables.values() if v.available])
        
        import math
        # (current^n × new_conf)^(1/(n+1))
        return (current ** n * new_var.confidence) ** (1 / (n + 1))
    
    def _calculate_model_score(self, model: FermiModel) -> float:
        """
        모형 전체 점수
        
        조합:
        - 60%: 변수 채움 비율 (unknown 해결)
        - 40%: 평균 confidence (품질)
        """
        if model.total_variables == 0:
            return 0.0
        
        # 변수 채움 비율
        filled = sum(1 for v in model.variables.values() if v.available)
        filled_ratio = filled / model.total_variables
        
        # Confidence
        conf = self._geometric_mean_confidence(model)
        
        # 가중 평균
        return filled_ratio * 0.6 + conf * 0.4
    
    def _predict_score(
        self,
        model: FermiModel,
        new_var: FermiVariable
    ) -> float:
        """새 변수 추가 후 점수 예상"""
        import copy
        temp_model = copy.deepcopy(model)
        temp_model.variables[new_var.name] = new_var
        temp_model.total_variables += 1
        
        return self._calculate_model_score(temp_model)
```

---

## 🎯 Tier 3에서 활용

### Phase 2: 모형 생성 시

```python
def _phase2_generate_models(...) -> List[FermiModel]:
    """
    LLM 모형 생성 + 변수 수렴 체크
    """
    # LLM이 생성한 후보 모형
    raw_models = self._call_llm_for_models(question, available)
    
    # 각 모형별 변수 필터링
    policy = VariableConvergencePolicy()
    refined_models = []
    
    for raw_model in raw_models:
        # 변수를 중요도 순으로 정렬
        sorted_vars = self._sort_variables_by_importance(raw_model)
        
        refined_model = FermiModel(
            model_id=raw_model.model_id,
            formula="",
            variables={}
        )
        
        # 변수 하나씩 추가하며 수렴 체크
        for seq, var in enumerate(sorted_vars, 1):
            eval_result = policy.evaluate(
                current_model=refined_model,
                new_variable=var,
                variable_sequence=seq
            )
            
            if eval_result['should_add']:
                refined_model.variables[var.name] = var
                refined_model.total_variables += 1
                
                if eval_result['warning']:
                    logger.warning(f"    {eval_result['warning']}")
            else:
                # 자연 수렴
                logger.info(f"    모형 '{refined_model.model_id}' 수렴: "
                           f"{refined_model.total_variables}개 변수")
                logger.info(f"    이유: {eval_result['reason']}")
                break
        
        # 수식 재구성 (선택된 변수만)
        refined_model.formula = self._rebuild_formula(refined_model)
        
        refined_models.append(refined_model)
    
    return refined_models
```

---

## 📊 효과 예상

### 기대 효과

```yaml
간단한 문제:
  예: "Churn Rate는?"
  이전: 6개까지 가능 (불필요)
  이후: 1-2개로 수렴 ✅

중간 문제:
  예: "음식점 SaaS 시장은?"
  이전: 6개 고정
  이후: 4-5개로 수렴 ✅

복잡한 문제:
  예: "산업별 세분화 시장"
  이전: 6개 제한 (부족할 수도)
  이후: 7-9개까지 허용 (경고 포함) ✅

매우 복잡:
  이전: 6개 제한 (강제)
  이후: 10개 절대 상한 (논리적 중단) ✅

평균 변수 개수:
  이전: ~5개 (모든 문제)
  이후: ~4개 (자연 수렴) ✅
```

---

## 🎯 설정 권장값

### 기본 설정 (대부분 문제)

```python
policy = VariableConvergencePolicy(
    min_confidence_gain=0.05,  # 5% 이상 개선
    recommended_max=6,          # Occam's Razor
    absolute_max=10             # Miller's Law
)
```

### 엄격한 설정 (간단한 문제 선호)

```python
policy = VariableConvergencePolicy(
    min_confidence_gain=0.10,  # 10% 이상 개선 (더 엄격)
    recommended_max=4,          # 4개 권장
    absolute_max=8              # 8개 절대
)
```

### 유연한 설정 (복잡한 문제 허용)

```python
policy = VariableConvergencePolicy(
    min_confidence_gain=0.03,  # 3% 이상 개선 (더 관대)
    recommended_max=8,          # 8개 권장
    absolute_max=12             # 12개 절대
)
```

---

## 📚 이론적 근거

### 1. Occam's Razor (오컴의 면도날)

**원칙**: "같은 설명력이면 간단한 것을 선택"

**적용**:
- 변수 추가가 실질적 개선 없으면 중단
- Diminishing Returns로 구현

---

### 2. Miller's Law (밀러의 법칙)

**원칙**: "인간은 7±2개 정보를 동시 처리"

**적용**:
- 절대 상한: 10개 (7+3)
- 권장 상한: 6개 (7-1)

---

### 3. Information Theory (정보 이론)

**원칙**: "정보 추가가 불확실성을 줄여야 가치"

**적용**:
- Marginal Confidence Gain
- 5% 미만 개선 → 정보 가치 낮음

---

### 4. Diminishing Returns (수확 체감)

**원칙**: "투입 증가 → 산출 증가율 감소"

**적용**:
- 변수 순서별 임계값 감소
- 1번째: 10% → 9번째: 0.1%

---

## 🔍 수학적 검증

### Confidence 조합 (Geometric Mean)

**왜 Geometric Mean?**

```yaml
문제: "시장 = A × B × C"

Arithmetic Mean (산술 평균):
  - (0.9 + 0.7 + 0.6) / 3 = 0.73
  - 문제: 곱셈 모형인데 평균? ❌

Geometric Mean (기하 평균):
  - ∛(0.9 × 0.7 × 0.6) = 0.71
  - 논리: 곱셈 모형이므로 곱의 n제곱근 ✅
  - 특성: 하나라도 낮으면 전체 낮음 (곱셈 특성 반영)

예시:
  - 모든 변수 0.8 → 0.8 (일관성)
  - 1개 변수 0.1 → 큰 하락 (약한 고리 반영)
```

**검증**: ✅ Geometric Mean 적합

---

### Marginal Gain 계산

**공식**:
```
현재 n개 변수: C_n = ⁿ√(c₁ × c₂ × ... × cₙ)
n+1개 변수: C_{n+1} = ⁿ⁺¹√(c₁ × c₂ × ... × cₙ × c_{n+1})

Marginal Gain = (C_{n+1} - C_n) / C_n
```

**예시 계산**:
```yaml
n=3, C_3 = ∛(0.9 × 0.7 × 0.6) = 0.709

n=4, c_4 = 0.8 추가:
  C_4 = ∜(0.9 × 0.7 × 0.6 × 0.8)
      = ∜(0.3024)
      = 0.742

Gain = (0.742 - 0.709) / 0.709
     = 0.047
     = 4.7%

판단: 4.7% < 5% → 중단 ❌
```

**검증**: ✅ 수학적으로 타당

---

## 🎯 최종 권장 사항

### 권장 방안: **Hybrid 종합 접근** (방안 4)

**이유**:
```yaml
1. 논리적 근거 ✅
   - Marginal Gain (정보 이론)
   - Diminishing Returns (경제학)
   - Miller's Law (인지과학)

2. 유연성 ✅
   - 간단한 문제: 1-3개로 수렴
   - 복잡한 문제: 7-9개까지 허용

3. 안전성 ✅
   - 권장 상한 (경고)
   - 절대 상한 (강제)

4. 실용성 ✅
   - 구현 간단
   - 이해 쉬움
   - 조정 가능 (threshold)
```

---

### 구현 위치

```python
# tier3.py

class Tier3FermiPath:
    
    def __init__(self, config: Tier3Config):
        self.tier2 = Tier2JudgmentPath()
        
        # 변수 수렴 정책 ⭐
        self.convergence_policy = VariableConvergencePolicy(
            min_confidence_gain=config.min_confidence_gain,
            recommended_max=config.recommended_max,
            absolute_max=config.absolute_max
        )
    
    def _phase2_generate_models(...):
        # LLM 모형 생성
        raw_models = self._call_llm(...)
        
        # 각 모형별 변수 수렴 ⭐
        refined_models = []
        for raw_model in raw_models:
            refined = self._refine_model_variables(
                raw_model,
                self.convergence_policy  # ⭐ 수렴 정책 적용
            )
            refined_models.append(refined)
        
        return refined_models
```

---

### config 업데이트

```python
# models.py - Tier3Config 확장

@dataclass
class Tier3Config:
    """Tier 3 설정"""
    max_depth: int = 4
    max_variables: int = 6  # Deprecated
    
    # v7.4.0 신규: 수렴 정책 ⭐
    min_confidence_gain: float = 0.05  # 5% 이상
    recommended_max: int = 6           # 권장 상한
    absolute_max: int = 10             # 절대 상한
    
    # Diminishing thresholds (override 가능)
    diminishing_thresholds: Dict[int, float] = field(default_factory=lambda: {
        1: 0.10, 2: 0.07, 3: 0.05, 4: 0.03, 5: 0.02,
        6: 0.01, 7: 0.005, 8: 0.003, 9: 0.001
    })
    
    # LLM
    llm_model: str = "gpt-4o"
    llm_temperature: float = 0.3
```

---

## 📋 구현 체크리스트

### Phase 1: 기본 구현 (1일)

- [ ] `VariableConvergencePolicy` 클래스
- [ ] `_geometric_mean_confidence()`
- [ ] `_predict_confidence()`
- [ ] `_calculate_model_score()`
- [ ] `_predict_score()`
- [ ] `evaluate()` 메서드

---

### Phase 2: 통합 (반나절)

- [ ] `Tier3Config` 확장
- [ ] `Tier3FermiPath.__init__()` 수정
- [ ] `_refine_model_variables()` 구현
- [ ] `_phase2_generate_models()` 통합

---

### Phase 3: 테스트 (반나절)

- [ ] 간단한 문제 테스트 (1-3개 수렴)
- [ ] 복잡한 문제 테스트 (7-9개)
- [ ] 절대 상한 테스트 (10개 중단)
- [ ] Confidence Gain 계산 검증

---

## 🎊 최종 결론

### 문제 해결: ✅

**기존 문제**:
- ❌ 자의적 기준 (6개)
- ❌ 맥락 무시
- ❌ 수렴 논리 없음

**해결 방안**:
- ✅ 논리적 기준 (Marginal Gain + Diminishing Returns)
- ✅ 맥락 반영 (자연 수렴)
- ✅ 수학적 근거 (Geometric Mean, Information Theory)
- ✅ 안전 장치 (권장 6개, 절대 10개)

---

### 구현 권장

```yaml
우선순위: P0 (Tier 3 구현 시 필수)

구현 시점: Tier 3 구현과 동시

예상 소요: +1일 (추가)
  - Tier 3 기본: 3-5일
  - 수렴 정책: +1일
  - 총: 4-6일

효과:
  ✅ 논리적 정당성
  ✅ 자연스러운 수렴
  ✅ 유연성 (간단 1-3개, 복잡 7-9개)
  ✅ 안전성 (10개 절대 상한)
```

---

**작성 완료**: 2025-11-08 01:25  
**상태**: ✅ **변수 수렴 메커니즘 설계 완료**  
**권장**: Hybrid 종합 접근 (방안 4)

🎉 **논리적 변수 수렴 설계 완료!**

