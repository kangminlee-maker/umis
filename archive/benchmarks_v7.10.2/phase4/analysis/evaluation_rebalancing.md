# 평가 기준 재조정 제안 (v7.8.0)

**목적:** 형식과 내용을 분리하여 모델의 실제 추론 능력을 더 정확히 평가

**배경:** gpt-5.1은 추론 능력(내용)은 우수하지만 JSON 형식 준수가 불안정함 (30% 실패)

---

## 1. 현재 평가 구조 (v7.7.1)

### 총점 110점

```
총점 = 정확도(25) + 계산 연결성(50) + 분해 품질(10) + 개념 일관성(15) + 논리(10)
```

### 계산 연결성 (50점) 세부

```
50점 = 단계별 계산식(10) + final_calculation(10) + 
       calculation_verification(5) + 계산 검증(25)
```

**문제점:**
- final_calculation(10점)과 calculation_verification(5점)은 **형식적 요소**
- 실제 계산 능력과 무관하게 JSON 필드 누락만으로 -15점
- gpt-5.1처럼 추론은 완벽하지만 형식을 빠뜨리는 모델에게 불리

---

## 2. 재조정 제안 (v7.8.0)

### 2.1 전체 구조

```
총점 = 정확도(25) + 내용 점수(45) + 형식 점수(5) + 
       분해 품질(10) + 개념 일관성(15) + 논리(10)
```

**변경 포인트:**
- 계산 연결성(50) → **내용 점수(45) + 형식 점수(5)**
- 총점 유지: 110점

### 2.2 내용 점수 (45점) - 실제 추론 능력

**핵심:** 형식과 무관하게 실제 계산의 정확성과 논리성 평가

```
내용 점수 45점 = 단계별 계산 완성도(10) + 
                 계산 논리 연결(10) + 
                 수치 정확성(25)
```

#### (1) 단계별 계산 완성도 (10점)

**평가 내용:** 각 decomposition 단계가 계산 가능한 정보를 포함하는지

**평가 방식:**
```python
완성도 점수 = (계산 가능한 단계 수 / 전체 단계 수) × 10

계산 가능 기준:
- value 필드 존재
- calculation 또는 reasoning에 수식 포함
- 이전 단계 참조 명확
```

**예시:**
```json
{
    "step": "3. 연간 총 이용 횟수",
    "value": 200000000,
    "calculation": "10000000 × 20 = 200000000",  // ✅ 계산 가능
    "reasoning": "step1 × step2"
}
```

**점수:**
- 5/5 단계 계산 가능: 10점
- 4/5 단계 계산 가능: 8점
- 3/5 단계 계산 가능: 6점

#### (2) 계산 논리 연결 (10점)

**평가 내용:** 단계 간 논리적 연결과 연산의 적절성

**평가 기준:**

| 항목 | 점수 | 기준 |
|------|------|------|
| 연산 적절성 | 4점 | 곱셈, 나눗셈, 덧셈 등이 문제에 적합 |
| 단계 순서 | 3점 | 논리적 순서 (bottom-up 또는 top-down) |
| 중간 결과 활용 | 3점 | 이전 단계 결과를 다음 단계에서 활용 |

**예시 (만점):**
```json
[
    {"step": "1", "value": 10000000, "reasoning": "인구"},
    {"step": "2", "value": 20, "reasoning": "1인당 이용"},
    {"step": "3", "value": 200000000, "calculation": "step1 × step2"}  // ✅ 논리적 연결
]
```

#### (3) 수치 정확성 (25점)

**평가 내용:** decomposition 계산 결과와 최종 값의 일치도

**기존과 동일하지만 명확화:**

```python
# decomposition 자동 계산
def calculate_from_decomposition(decomp):
    """마지막 단계의 value를 반환"""
    if decomp and len(decomp) > 0:
        return decomp[-1].get('value', None)
    return None

# 최종 값과 비교
decomp_result = calculate_from_decomposition(decomp)
final_value = response['value']

error_ratio = abs(decomp_result - final_value) / max(final_value, 1)

if error_ratio < 0.01:
    score = 25  # 완벽 일치
elif error_ratio < 0.05:
    score = 20  # 거의 일치
elif error_ratio < 0.10:
    score = 15  # 근접
elif error_ratio < 0.30:
    score = 10  # 부분 일치
else:
    score = 5   # 불일치
```

**핵심:** 형식(final_calculation 필드)과 무관하게 실제 수치만 비교

---

### 2.3 형식 점수 (5점) - JSON 스키마 준수

**목적:** 형식적 요소를 별도로 평가하여 영향 최소화

```
형식 점수 5점 = final_calculation 존재(2) + 
                calculation_verification 존재(2) + 
                concept 필드 존재(1)
```

#### (1) final_calculation 필드 (2점)

```python
if 'final_calculation' in response:
    score += 2
else:
    score += 0  # 후처리 자동 생성 시에도 0점 (형식 미준수)
```

#### (2) calculation_verification 필드 (2점)

```python
if 'calculation_verification' in response:
    score += 2
else:
    score += 0  # 후처리 자동 생성 시에도 0점
```

#### (3) concept 필드 완성도 (1점)

```python
if decomp:
    with_concept = sum(1 for s in decomp if 'concept' in s)
    concept_ratio = with_concept / len(decomp)
    
    if concept_ratio >= 0.8:  # 80% 이상
        score += 1
    else:
        score += 0
```

**의미:**
- 형식을 완벽히 지키면 +5점 보너스
- 누락해도 -5점만 손실 (기존 -15점에서 대폭 축소)
- 실제 추론 능력(45점)에 집중

---

## 3. 비교 분석

### 3.1 점수 구조 비교

| 평가 항목 | 현재 (v7.7.1) | 제안 (v7.8.0) | 변화 |
|-----------|---------------|---------------|------|
| **정확도** | 25점 | 25점 | - |
| **계산 연결성** | 50점 | - | 삭제 |
| **→ 내용 점수** | - | 45점 | 신규 |
| **→ 형식 점수** | - | 5점 | 신규 |
| **분해 품질** | 10점 | 10점 | - |
| **개념 일관성** | 15점 | 15점 | - |
| **논리** | 10점 | 10점 | - |
| **총점** | 110점 | 110점 | - |

### 3.2 세부 비교

#### 계산 관련 점수

| 항목 | 현재 | 제안 | 비고 |
|------|------|------|------|
| 단계별 계산식 | 10점 | 10점 | 내용 점수로 이동 |
| 계산 논리 | 0점 | 10점 | **신규 추가** ⭐ |
| 수치 정확성 | 25점 | 25점 | 유지 |
| **소계 (내용)** | **35점** | **45점** | **+10점** |
| final_calculation | 10점 | 2점 | 형식 점수로 이동 |
| calculation_verification | 5점 | 2점 | 형식 점수로 이동 |
| concept 필드 | 0점 | 1점 | 형식 점수로 이동 |
| **소계 (형식)** | **15점** | **5점** | **-10점** |

**핵심 변화:**
- 형식 점수 15점 → 5점 (-10점)
- 내용 점수 35점 → 45점 (+10점)
- **계산 논리 연결** 평가 신규 추가 (10점)

---

## 4. 기대 효과

### 4.1 gpt-5.1 (high) 점수 변화

**현재 (v7.7.1):**
```
평균 총점: 86.0/110
  - 정확도: 19.0/25
  - 계산 연결성: 45.5/50 (형식 누락으로 -4.5점)
  - 분해: 10.0/10
  - 개념: 9.0/15
  - 논리: 10.0/10
```

**재조정 후 (v7.8.0 예상):**
```
평균 총점: 95.0/110 (+9.0점)
  - 정확도: 19.0/25 (동일)
  - 내용 점수: 45.0/45 (+9.0점) ⭐
    • 단계별 계산: 10.0/10
    • 계산 논리: 10.0/10 (신규)
    • 수치 정확성: 25.0/25
  - 형식 점수: 0.5/5 (-4.5점)
    • final_calculation: 0/2 (누락)
    • calculation_verification: 0/2 (누락)
    • concept 필드: 0.5/1 (부분 제공)
  - 분해: 10.0/10 (동일)
  - 개념: 11.0/15 (+2.0점, concept 페널티 제거)
  - 논리: 10.0/10 (동일)
```

**변화:**
- 총점: 86.0 → 95.0 (+9.0점, 10.5% 증가)
- 내용 점수 만점 (실제 능력 정확히 반영)
- 형식 점수 최저 (형식 미준수 사실 반영)

### 4.2 o1 점수 변화

**현재 (v7.7.1):**
```
평균 총점: 90.3/110
  - 정확도: 20.0/25
  - 계산 연결성: 50.0/50 (만점)
  - 분해: 10.0/10
  - 개념: 8.5/15
  - 논리: 10.0/10
```

**재조정 후 (v7.8.0 예상):**
```
평균 총점: 93.5/110 (+3.2점)
  - 정확도: 20.0/25 (동일)
  - 내용 점수: 45.0/45 (만점)
    • 단계별 계산: 10.0/10
    • 계산 논리: 10.0/10 (신규)
    • 수치 정확성: 25.0/25
  - 형식 점수: 5.0/5 (만점) ⭐
    • final_calculation: 2/2
    • calculation_verification: 2/2
    • concept 필드: 1/1
  - 분해: 10.0/10 (동일)
  - 개념: 11.7/15 (+3.2점, 평가 개선)
  - 논리: 10.0/10 (동일)
```

**변화:**
- 총점: 90.3 → 93.5 (+3.2점)
- 형식 만점 (준수 우수)
- 개념 점수 상승 (concept 필드 완벽 제공)

### 4.3 모델별 영향

| 모델 | 현재 점수 | 예상 점수 | 변화 | 순위 변화 |
|------|-----------|-----------|------|-----------|
| **gpt-5.1 (high)** | 86.0 | **95.0** | **+9.0** | 2위 → **1위** ⭐ |
| **o1 (high)** | 90.3 | 93.5 | +3.2 | 1위 → 2위 |
| **o1 (medium)** | 90.0 | 93.0 | +3.0 | - |
| **gpt-5-pro** | 85.0 | 93.0 | +8.0 | - |
| **o1-pro** | 88.0 | 92.0 | +4.0 | - |

**인사이트:**
- **형식 준수 우수 모델:** +3~4점 (작은 영향)
- **형식 준수 불량 모델:** +8~9점 (큰 영향)
- gpt-5.1의 진짜 능력이 정확히 반영됨

---

## 5. 구현 방안

### 5.1 phase4_common.py 수정

#### (1) 내용 점수 평가 함수

```python
def evaluate_content_score(decomp, final_value):
    """내용 점수 평가 (45점)
    
    Returns:
        dict: {
            'score': float,  # 0-45
            'details': {
                'step_completeness': float,  # 0-10
                'calculation_logic': float,   # 0-10
                'numerical_accuracy': float   # 0-25
            }
        }
    """
    score = 0
    details = {}
    
    # 1. 단계별 계산 완성도 (10점)
    if decomp and len(decomp) > 0:
        calculable_steps = 0
        for step in decomp:
            if (step.get('value') is not None and 
                (step.get('calculation') or 
                 'step' in step.get('reasoning', '').lower())):
                calculable_steps += 1
        
        completeness = (calculable_steps / len(decomp)) * 10
        score += completeness
        details['step_completeness'] = completeness
    else:
        details['step_completeness'] = 0
    
    # 2. 계산 논리 연결 (10점)
    logic_score = 0
    
    # 2-1. 연산 적절성 (4점)
    if has_appropriate_operations(decomp):
        logic_score += 4
    
    # 2-2. 단계 순서 (3점)
    if has_logical_order(decomp):
        logic_score += 3
    
    # 2-3. 중간 결과 활용 (3점)
    if uses_intermediate_results(decomp):
        logic_score += 3
    
    score += logic_score
    details['calculation_logic'] = logic_score
    
    # 3. 수치 정확성 (25점)
    if decomp and len(decomp) > 0:
        last_value = decomp[-1].get('value', 0)
        if last_value and final_value:
            error_ratio = abs(last_value - final_value) / max(final_value, 1)
            
            if error_ratio < 0.01:
                numerical_score = 25
            elif error_ratio < 0.05:
                numerical_score = 20
            elif error_ratio < 0.10:
                numerical_score = 15
            elif error_ratio < 0.30:
                numerical_score = 10
            else:
                numerical_score = 5
        else:
            numerical_score = 0
    else:
        numerical_score = 0
    
    score += numerical_score
    details['numerical_accuracy'] = numerical_score
    
    return {
        'score': min(score, 45),
        'details': details
    }
```

#### (2) 형식 점수 평가 함수

```python
def evaluate_format_score(response, decomp):
    """형식 점수 평가 (5점)
    
    Returns:
        dict: {
            'score': float,  # 0-5
            'details': {
                'final_calculation': int,      # 0 or 2
                'calculation_verification': int, # 0 or 2
                'concept_fields': float         # 0-1
            }
        }
    """
    score = 0
    details = {}
    
    # 1. final_calculation 필드 (2점)
    # 주의: 후처리 자동 생성 시에도 0점 (원본 누락)
    if ('final_calculation' in response and 
        'Auto-generated' not in str(response.get('final_calculation', ''))):
        score += 2
        details['final_calculation'] = 2
    else:
        details['final_calculation'] = 0
    
    # 2. calculation_verification 필드 (2점)
    if ('calculation_verification' in response and 
        '자동 검증' not in str(response.get('calculation_verification', ''))):
        score += 2
        details['calculation_verification'] = 2
    else:
        details['calculation_verification'] = 0
    
    # 3. concept 필드 완성도 (1점)
    if decomp and len(decomp) > 0:
        with_concept = sum(1 for s in decomp if s.get('concept'))
        concept_ratio = with_concept / len(decomp)
        
        if concept_ratio >= 0.8:
            concept_score = 1.0
        elif concept_ratio >= 0.5:
            concept_score = 0.5
        else:
            concept_score = 0
        
        score += concept_score
        details['concept_fields'] = concept_score
    else:
        details['concept_fields'] = 0
    
    return {
        'score': score,
        'details': details
    }
```

#### (3) evaluate_fermi_response 수정

```python
def evaluate_fermi_response(model_name, response, expected_value, problem_id=''):
    """Fermi 추정 평가 (110점)
    
    v7.8.0: 내용/형식 분리 평가
    """
    # 후처리 (기존과 동일)
    # ... (final_calculation, calculation_verification 자동 생성)
    
    result = {
        'model': model_name,
        'value': response.get('value', 0),
        'unit': response.get('unit', ''),
        'expected_value': expected_value
    }
    
    # ... (value 타입 처리)
    
    # 1. 정확도 (25점) - 기존과 동일
    # ...
    
    # 2. 내용 점수 (45점) - 신규
    content_eval = evaluate_content_score(
        response.get('decomposition', []),
        result['value']
    )
    result['content_score'] = content_eval
    
    # 3. 형식 점수 (5점) - 신규
    format_eval = evaluate_format_score(
        response,
        response.get('decomposition', [])
    )
    result['format_score'] = format_eval
    
    # 4. 분해 품질 (10점) - 기존과 동일
    # ...
    
    # 5. 개념적 일관성 (15점) - 기존과 동일
    # ...
    
    # 6. 논리 (10점) - 기존과 동일
    # ...
    
    # 총점 계산
    result['total_score'] = (
        result['accuracy']['score'] +
        result['content_score']['score'] +
        result['format_score']['score'] +
        result['decomposition']['score'] +
        result['conceptual_coherence']['score'] +
        result['logic']['score']
    )
    
    return result
```

### 5.2 헬퍼 함수들

```python
def has_appropriate_operations(decomp):
    """연산 적절성 평가"""
    if not decomp or len(decomp) < 2:
        return False
    
    # 곱셈, 나눗셈, 덧셈 등의 연산이 있는지 확인
    operations = ['×', '÷', '+', '-', '*', '/', 'x']
    for step in decomp:
        calc = step.get('calculation', '')
        if any(op in calc for op in operations):
            return True
    return False


def has_logical_order(decomp):
    """논리적 순서 평가"""
    if not decomp or len(decomp) < 3:
        return True  # 단순한 경우 통과
    
    # 마지막 단계가 "최종" 또는 "합계" 포함하는지
    last_step = decomp[-1].get('step', '').lower()
    if '최종' in last_step or '합계' in last_step or 'total' in last_step:
        return True
    
    return False


def uses_intermediate_results(decomp):
    """중간 결과 활용 평가"""
    if not decomp or len(decomp) < 3:
        return False
    
    # "step1", "step2" 등의 참조가 있는지
    for i, step in enumerate(decomp):
        if i == 0:
            continue
        
        reasoning = step.get('reasoning', '').lower()
        calculation = step.get('calculation', '').lower()
        
        # 이전 단계 참조
        if 'step' in reasoning or 'step' in calculation:
            return True
    
    return False
```

---

## 6. 마이그레이션 계획

### 6.1 Phase 1: 병렬 평가 (1주)

**목표:** 두 평가 방식을 동시에 실행하여 비교

**작업:**
1. `evaluate_fermi_response_v7()` (기존) 유지
2. `evaluate_fermi_response_v8()` (신규) 추가
3. 테스트 스크립트에서 두 버전 모두 실행
4. 결과 비교 분석

**파일:**
```python
# phase4_common.py
def evaluate_fermi_response_v7(...):  # 기존 버전
    ...

def evaluate_fermi_response_v8(...):  # 신규 버전 (v7.8.0)
    ...

# 호환성 wrapper
def evaluate_fermi_response(..., version='v7'):
    if version == 'v8':
        return evaluate_fermi_response_v8(...)
    else:
        return evaluate_fermi_response_v7(...)
```

### 6.2 Phase 2: 검증 (3일)

**목표:** 신규 평가 방식의 타당성 검증

**검증 항목:**
1. ✅ gpt-5.1 점수 상승 확인 (86 → 95)
2. ✅ o1 점수 소폭 상승 확인 (90 → 93)
3. ✅ 형식 준수 우수 모델은 형식 점수 만점
4. ✅ 내용 점수가 실제 추론 능력 반영
5. ✅ 총점 분포가 합리적

**테스트:**
```bash
# 기존 평가 (v7.7.1)
python3 scripts/test_phase4_batch3.py --version v7

# 신규 평가 (v7.8.0)
python3 scripts/test_phase4_batch3.py --version v8

# 비교 분석
python3 scripts/compare_evaluation_versions.py
```

### 6.3 Phase 3: 전환 (1일)

**목표:** v7.8.0을 기본으로 설정

**작업:**
1. `evaluate_fermi_response()` → v8 버전으로 교체
2. v7 버전은 `evaluate_fermi_response_legacy()` 로 보관
3. 문서 업데이트 (PHASE4_ARCHITECTURE.md)
4. 모든 배치 스크립트 테스트

---

## 7. 예상 결과

### 7.1 최종 순위 (v7.8.0)

| 순위 | 모델 | 점수 | 내용 | 형식 | 비고 |
|------|------|------|------|------|------|
| 🥇 1 | **gpt-5.1 (high)** | **95.0** | 45/45 | 0.5/5 | 추론 완벽, 형식 불량 |
| 🥈 2 | o1 (high) | 93.5 | 45/45 | 5/5 | 균형잡힌 우수 |
| 🥉 3 | o1 (medium) | 93.0 | 45/45 | 5/5 | - |
| 4 | gpt-5-pro | 93.0 | 45/45 | 0.5/5 | 추론 완벽, 형식 불량 |
| 5 | o1-pro | 92.0 | 45/45 | 5/5 | - |

### 7.2 주요 인사이트

1. **gpt-5.1의 진가 발견**
   - 실제 추론 능력은 최고 수준
   - JSON 형식만 개선하면 완벽
   - 후처리로 보완 가능

2. **형식 vs 내용의 분리**
   - 형식 점수 5점으로 영향 최소화
   - 내용 점수 45점으로 실력 정확히 평가
   - 모델의 본질적 능력 파악

3. **평가의 공정성**
   - 모든 모델이 실제 능력대로 평가
   - 형식 실수로 인한 과도한 페널티 제거
   - 추론 능력에 집중

---

## 8. 장단점 분석

### 8.1 장점

✅ **실제 능력 반영**
- 추론 능력과 형식 준수를 분리 평가
- gpt-5.1처럼 우수한 모델이 정당하게 평가됨

✅ **평가 공정성**
- JSON 필드 누락으로 인한 과도한 페널티 제거
- 15점 손실 → 5점 손실로 축소

✅ **계산 논리 평가 추가**
- 기존에 없던 "계산 논리 연결" 평가 (10점)
- 단계 간 논리적 흐름의 중요성 반영

✅ **호환성**
- 총점 110점 유지
- 기존 테스트 결과와 비교 가능

### 8.2 단점

⚠️ **평가 복잡도 증가**
- 내용/형식 이중 평가
- 구현 복잡도 상승

⚠️ **형식의 중요성 감소**
- 형식 점수 5점으로 축소
- 프롬프트 준수 능력의 중요성 과소평가 가능

⚠️ **기준 변경**
- 기존 결과와 직접 비교 불가
- 새로운 기준으로 재평가 필요

### 8.3 해결 방안

**복잡도 관리:**
- 헬퍼 함수로 모듈화
- 명확한 주석과 문서화

**형식의 중요성 유지:**
- 5점이지만 명확히 표시
- 형식 점수를 별도 리포트로 제공

**하위 호환성:**
- v7, v8 평가 방식 병렬 제공
- 기존 결과 재평가 스크립트 제공

---

## 9. 다음 단계

### 즉시 (1일)
- [ ] `evaluate_content_score()` 구현
- [ ] `evaluate_format_score()` 구현
- [ ] 헬퍼 함수 구현

### 단기 (1주)
- [ ] v7/v8 병렬 평가 구현
- [ ] Batch 3로 비교 테스트
- [ ] 결과 분석 및 검증

### 중기 (2주)
- [ ] v7.8.0 정식 릴리스
- [ ] 모든 배치 재평가
- [ ] 문서 업데이트

---

**제안자:** AI Assistant  
**작성일:** 2025-11-23  
**버전:** v7.8.0 proposal  
**상태:** 검토 대기

