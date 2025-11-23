# Phase 4 Fermi Estimation Benchmark - Complete Architecture

**Version:** v7.8.0  
**Date:** 2025-11-23  
**Purpose:** LLM Fermi 추정 능력 벤치마크 시스템

---

## 📑 목차

1. [시스템 개요](#1-시스템-개요)
2. [평가 시스템](#2-평가-시스템)
3. [모델 설정](#3-모델-설정)
4. [프롬프트 시스템](#4-프롬프트-시스템)
5. [배치 테스트 구조](#5-배치-테스트-구조)
6. [후처리 시스템](#6-후처리-시스템)
7. [파일 구조](#7-파일-구조)

---

## 1. 시스템 개요

### 1.1 목적

LLM의 **Fermi 추정 능력**을 다각도로 평가:
- **정확도**: 실제 값과의 근접도
- **내용 점수**: 실제 추론 능력 (계산 완성도, 논리 연결, 수치 정확성)
- **형식 점수**: JSON 스키마 준수도
- **개념적 일관성**: 도메인 특화 개념 활용 능력
- **분해 품질**: 문제 분해의 완성도
- **논리**: 추론 논리의 타당성

### 1.2 핵심 특징

- **110점 평가 시스템** (정확도 25 + 내용 45 + 형식 5 + 분해 10 + 개념 15 + 논리 10)
- **15개 모델 지원** (o-series, gpt-5, gpt-4.1)
- **API별 최적화** (Responses API vs Chat Completions API)
- **자동 후처리** (누락 필드 자동 생성)
- **Fast Mode** (pro 모델 속도 최적화)

### 1.3 테스트 문제

**3개 핵심 문제:**
1. 한국 전체 사업자 수
2. 서울시 인구
3. 한국 커피 전문점 수

**10개 확장 문제:**
- 배달 기사 수, 치킨 배달 건수, 택시 승객 수
- 신용카드 승인 건수, 병원 진료 건수, 사교육비
- 전세 계약 건수, OTT 구독자, 쿠팡 배송량, 일회용 컵

---

## 2. 평가 시스템

### 2.1 전체 구조 (110점)

```
총점 = 정확도(25) + 내용 점수(45) + 형식 점수(5) + 분해 품질(10) + 개념 일관성(15) + 논리(10)
```

### 2.2 정확도 (25점)

**계산 방법:**
```python
error = abs(log10(추정값) - log10(정답))
```

**점수 기준:**
| error | 오차율 | 점수 |
|-------|--------|------|
| < 0.05 | ±12% | 25점 |
| < 0.1  | ±26% | 20점 |
| < 0.3  | ±100% | 15점 |
| < 0.5  | ±220% | 10점 |
| ≥ 0.5  | ±220%+ | 5점 |

### 2.3 내용 점수 (45점) - v7.8.0

**구성:**
```
45점 = 단계별 계산 완성도(10) + 계산 논리 연결(10) + 수치 정확성(25)
```

**평가 항목:**

1. **단계별 계산 완성도 (10점)**
   - decomposition 각 단계가 계산 가능한지 평가
   - 조건: `value` 존재 + (`calculation` 또는 `reasoning`에 연산자)
   - 비율: `(계산 가능 단계 수 / 전체 단계 수) × 10`

2. **계산 논리 연결 (10점)**
   - 연산 적절성 (4점): 곱셈, 나눗셈 등 적절한 연산 사용
   - 논리적 순서 (3점): 마지막 단계가 "최종" 또는 "합계" 포함
   - 중간 결과 활용 (3점): 이전 단계 참조 (e.g., "step1", "step2")

3. **수치 정확성 (25점)**
   - decomposition 마지막 단계 `value`와 `final_value` 비교
   - error_ratio = `|last_value - final_value| / max(final_value, 1)`
   
   | error_ratio | 점수 |
   |-------------|------|
   | < 0.01 | 25점 |
   | < 0.05 | 20점 |
   | < 0.10 | 15점 |
   | < 0.30 | 10점 |
   | ≥ 0.30 | 5점 |

### 2.4 형식 점수 (5점) - v7.8.0

**구성:**
```
5점 = final_calculation(2) + calculation_verification(2) + concept 필드(1)
```

**평가 항목:**

1. **final_calculation (2점)**
   - JSON 최상위 `final_calculation` 필드 존재
   - **자동 생성 시 0점** (decomposition 마지막 단계 사용)
   - 모델이 직접 제공한 경우만 2점

2. **calculation_verification (2점)**
   - JSON 최상위 `calculation_verification` 필드 존재
   - **자동 생성 시 0점** (auto_verify_calculation 결과 사용)
   - 모델이 직접 제공한 경우만 2점

3. **concept 필드 완성도 (1점)**
   - decomposition 각 단계의 `concept` 필드 존재 여부
   
   | concept 비율 | 점수 |
   |--------------|------|
   | ≥ 80% | 1.0점 |
   | ≥ 50% | 0.5점 |
   | < 50% | 0점 |

### 2.5 분해 품질 (10점)

**기본 점수:**
- 3단계 이상 decomposition: 3점

**완성도 점수:**
```python
완성도 = (필수 필드 있는 단계 수 / 전체 단계 수) × 7
필수 필드: step, value, calculation, reasoning
```

### 2.6 개념적 일관성 (15점)

**v7.7.1 신규 추가**

**목적:** 도메인 특화 개념 활용 능력 평가

**평가 항목:**

1. **핵심 개념 활용 (7점)**
   - 문제별 핵심 개념 7개 정의
   - 사용한 개념 개수에 비례하여 점수 부여
   - 예: "사업자 수" → [인구, 경제활동인구, 자영업, 법인, 업종, 폐업률, 다중등록]

2. **논리적 연산 (3점)**
   - 곱셈, 나눗셈, 덧셈 등 적절한 연산 사용

3. **관련 없는 개념 페널티 (-1점)**
   - 문제와 무관한 개념 사용 시 감점

4. **최종 단계 명확성 (3점)**
   - 마지막 단계가 명확히 최종 계산인지 확인

5. **단계 간 참조 명확성 (4점)**
   - 이전 단계 참조가 명확한지 평가

**개념 정의 예시:**

```python
PROBLEM_CONCEPTS = {
    'phase4_korean_businesses': {
        'core_concepts': [
            '인구', '경제활동인구', '자영업', '법인',
            '업종', '폐업률', '다중등록'
        ],
        'irrelevant_keywords': ['GDP', '수출', '무역']
    }
}
```

### 2.7 논리 (10점)

**평가 기준:**
- method 필드 존재 (5점)
- reasoning 필드 존재 (5점)

---

## 3. 모델 설정

### 3.1 지원 모델 (15개)

```python
MODEL_API_CONFIGS = {
    # o-series (9개)
    'o1-mini': {...},
    'o1': {...},
    'o1-2024-12-17': {...},
    'o1-pro': {...},
    'o1-pro-2025-03-19': {...},
    'o3': {...},
    'o3-2025-04-16': {...},
    'o3-mini': {...},
    'o3-mini-2025-01-31': {...},
    'o4-mini': {...},
    'o4-mini-2025-04-16': {...},
    
    # gpt-5 series (2개)
    'gpt-5.1': {...},
    'gpt-5-pro': {...},
    
    # gpt-4.1 series (2개)
    'gpt-4.1': {...},
    'gpt-4.1-mini': {...},
}
```

### 3.2 모델별 설정 구조

```python
{
    'api_type': 'responses' | 'chat',
    'reasoning_effort_support': True | False,
    'reasoning_effort_levels': ['low', 'medium', 'high'] | ['high'] | [],
    'reasoning_effort_fixed': 'high' (선택적),
    'temperature_support': True | False,
    'temperature_condition': 'reasoning_effort_none' (선택적),
    'max_output_tokens': 16000,  # 통일
    'context_window': 200000 | 196000 | 400000 (선택적),
    'notes': '모델 특징 설명'
}
```

### 3.3 API 타입별 특징

#### Responses API
- 모델: 대부분의 o-series, gpt-5 시리즈
- 프롬프트 필드: `input`
- reasoning 토큰 포함
- 응답 형식: `response.output`

#### Chat Completions API
- 모델: 없음 (현재 모두 Responses API 사용)
- 프롬프트 필드: `messages`
- 응답 형식: `response.choices[0].message.content`

### 3.4 Reasoning Effort 설정

**지원 모델:**
- **full 조절 (low, medium, high):** o1, o1-mini, o3, o3-mini, o4-mini, gpt-5.1
- **high 고정:** o1-pro, o1-pro-2025-03-19, gpt-5-pro
- **미지원:** gpt-4.1, gpt-4.1-mini

**pro 모델 특징:**
- reasoning_effort='high' 고정 (API 제약)
- 변경 불가능
- Fast Mode로 간접 제어

### 3.5 max_output_tokens

**통일 정책 (v7.7.1):**
```python
모든 모델: 16,000 토큰
```

**이유:**
- 안전성 우선 (응답 잘림 방지)
- 관리 간소화
- Fermi 추정은 보통 2K 이내로 충분
- Fast Mode로 실제 출력 길이 제어

---

## 4. 프롬프트 시스템

### 4.1 기본 프롬프트 구조

```python
get_improved_fewshot_prompt()
```

**구성:**
1. **CRITICAL MANDATORY FIELDS** - 필수 필드 강조
2. **예시** - 완벽한 JSON 예시 (모든 필드 포함)
3. **MANDATORY RULES** - 6가지 절대 규칙
4. **체크리스트** - 제출 전 확인 사항

**필수 필드 3가지:**
```
1. decomposition 모든 단계에 "concept" 필드
2. 최상위 "final_calculation" 필드
3. 최상위 "calculation_verification" 필드
```

### 4.2 Fast Mode (v7.7.1)

**적용 대상:** pro 모델만 (`gpt-5-pro`, `o1-pro`, `o1-pro-2025-03-19`)

**제약 조건:**
```
⏱️ 목표 응답 시간: 60초 이내
📏 최대 출력 길이: 2,000자 이내 (약 500 토큰)
📋 decomposition: 3-5단계만 (필수 단계만 포함)
✂️ reasoning: 각 단계 15단어 이내

💡 빠르고 간결하게 핵심만 답변하세요!
   깊은 추론보다는 직관적 근사치를 우선하세요.
```

**효과:**
- gpt-5-pro: 8분 → 4~5분 (40~50% 단축)
- o1-pro: 5분 → 3~4분 (30~40% 단축)

**작동 방식:**
```python
def get_phase4_scenarios(model_name=None):
    fewshot = get_improved_fewshot_prompt()
    
    # pro 모델 감지
    if model_name in ['gpt-5-pro', 'o1-pro', 'o1-pro-2025-03-19']:
        fast_mode = get_fast_mode_constraint()
        print(f"🚀 [Fast Mode] {model_name}에 속도 최적화 프롬프트 적용")
    else:
        fast_mode = ""
    
    return [
        {
            'prompt': f'''{fast_mode}{fewshot}
실제 문제: ...
'''
        }
    ]
```

### 4.3 JSON 스키마

**요구 형식:**
```json
{
    "value": 66667,
    "unit": "대",
    "confidence": 0.6,
    "method": "bottom-up",
    "decomposition": [
        {
            "step": "1. 서울 인구",
            "concept": "population_seoul",
            "value": 10000000,
            "unit": "명",
            "calculation": "1000만명 (통계 기반)",
            "reasoning": "서울시 공식 인구 통계"
        },
        ...
    ],
    "final_calculation": "step5 = step3 ÷ step4 = 200000000 ÷ 3000 = 66667",
    "calculation_verification": "✓ 검증: 10,000,000명 × 20회 ÷ 3,000회 = 66,667대"
}
```

**필드 설명:**

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `value` | number | ✅ | 최종 추정값 (decomposition 마지막과 동일) |
| `unit` | string | ✅ | 단위 |
| `confidence` | number | ✅ | 신뢰도 (0.0~1.0) |
| `method` | string | ✅ | "bottom-up" 또는 "top-down" |
| `decomposition` | array | ✅ | 분해 단계들 |
| `decomposition[].step` | string | ✅ | 단계 설명 |
| `decomposition[].concept` | string | ✅ | 도메인 개념 (snake_case) |
| `decomposition[].value` | number | ✅ | 단계 값 |
| `decomposition[].unit` | string | ⭐ | 단계 단위 (권장) |
| `decomposition[].calculation` | string | ✅ | 계산 과정 |
| `decomposition[].reasoning` | string | ✅ | 근거 |
| `final_calculation` | string | ✅ | 최종 계산 재확인 |
| `calculation_verification` | string | ✅ | 계산 검증 |

---

## 5. 배치 테스트 구조

### 5.1 배치 구성

**Batch 1:** 최우선 후보 (3개)
- o3-mini-2025-01-31
- o4-mini-2025-04-16
- o3-2025-04-16

**Batch 2:** 2순위 후보 (5개)
- o1-mini
- o1
- o1-2024-12-17
- gpt-4.1
- gpt-4.1-mini
- o3-mini

**Batch 3:** 고성능 모델 (4개)
- gpt-5.1 (high)
- o4-mini (high)
- o1-pro
- gpt-5-pro
- o1-pro-2025-03-19

**Batch 4:** effort='medium' (2개)
- gpt-5.1 (medium)
- o4-mini (medium)

**Batch 5:** effort='low' (2개)
- gpt-5.1 (low)
- o4-mini (low)

**Batch 6:** 전용 테스트
- gpt-5.1 (high)

### 5.2 테스트 흐름

```python
def run_batch_test():
    for model_config in test_config:
        model_name = model_config['model']
        effort = model_config['effort']
        
        # 1. 모델별 scenarios 생성 (Fast Mode 자동 적용)
        scenarios = get_phase4_scenarios(model_name)
        
        # 2. 각 문제 테스트
        for scenario in scenarios:
            # 3. API 파라미터 구성
            api_type, api_params = build_api_params(
                model_name, 
                scenario['prompt'], 
                effort
            )
            
            # 4. API 호출
            response = call_model_api(client, api_type, api_params)
            
            # 5. 응답 파싱
            parsed = parse_response(response, api_type)
            
            # 6. 평가 (후처리 자동 실행)
            result = evaluate_fermi_response(
                model_name, 
                parsed, 
                scenario['expected_value'],
                problem_id=scenario['id']
            )
            
            # 7. 결과 저장
            all_results.append(result)
    
    # 8. JSON 파일 저장
    save_results(all_results)
```

### 5.3 스크립트 위치

```
scripts/
├── phase4_common.py          # 공통 함수 및 설정
├── test_phase4_batch1.py      # Batch 1 테스트
├── test_phase4_batch2.py      # Batch 2 테스트
├── test_phase4_batch3.py      # Batch 3 테스트
├── test_phase4_batch4.py      # Batch 4 테스트
├── test_phase4_batch5.py      # Batch 5 테스트
├── test_phase4_batch6.py      # Batch 6 테스트
└── test_phase4_extended_10problems.py  # 확장 10문제
```

---

## 6. 후처리 시스템

### 6.1 자동 필드 생성 (v7.7.1)

**실행 시점:** `evaluate_fermi_response()` 호출 시

**처리 내용:**

#### 1. final_calculation 자동 생성

```python
if not response.get('final_calculation') and decomp:
    last_step = decomp[-1]
    if last_step.get('calculation'):
        response['final_calculation'] = f"Auto-generated: {last_step['calculation']}"
        print("🔄 [후처리] final_calculation 자동 생성")
```

**효과:**
- 누락 시 자동 보완
- 10점 연결성 점수 획득

#### 2. calculation_verification 자동 생성

```python
if not response.get('calculation_verification'):
    auto_result, auto_msg = auto_verify_calculation(decomp, response['value'])
    if auto_result is not None:
        response['calculation_verification'] = f"✓ 자동 검증: {auto_msg}"
        print("🔄 [후처리] calculation_verification 자동 생성")
```

**효과:**
- 누락 시 자동 보완
- 5점 연결성 점수 획득

### 6.2 auto_verify_calculation()

**기능:** decomposition 단계별 계산 자동 검증

**알고리즘:**
```python
def auto_verify_calculation(decomp, final_value):
    if not decomp or len(decomp) == 0:
        return None, "decomposition 없음"
    
    # 마지막 단계 값 추출
    last_step_value = decomp[-1].get('value', 0)
    
    # 최종 값과 비교
    if abs(last_step_value - final_value) < 1:
        return last_step_value, f"decomp_last={last_step_value}, final={final_value}"
    else:
        return last_step_value, f"불일치: decomp={last_step_value} vs final={final_value}"
```

### 6.3 개념 일관성 평가

```python
def evaluate_conceptual_coherence(problem_id, decomp, final_calc):
    score = 0
    details = []
    
    # 1. 핵심 개념 활용 (7점)
    core_concepts = PROBLEM_CONCEPTS.get(problem_id, {}).get('core_concepts', [])
    used_concepts = count_used_concepts(decomp, core_concepts)
    concept_score = min(used_concepts, 7)
    score += concept_score
    
    # 2. 논리적 연산 포함 (3점)
    if has_logical_operations(decomp):
        score += 3
        details.append("✅ 논리적 연산 포함 (3점)")
    
    # 3. 관련 없는 개념 사용 (-1점)
    irrelevant = find_irrelevant_concepts(decomp, problem_id)
    if irrelevant:
        score -= 1
        details.append(f"⚠️ 관련 없는 개념 사용 ({irrelevant}) (-1점)")
    
    # 4. 최종 단계 명확성 (3점)
    if is_final_step_clear(decomp):
        score += 3
        details.append("✅ 최종 단계 명확 (3점)")
    
    # 5. 단계 간 참조 명확성 (4점)
    reference_score = evaluate_step_references(decomp)
    score += reference_score
    
    return {
        'score': max(0, min(score, 15)),  # 0-15점
        'details': details
    }
```

---

## 7. 파일 구조

### 7.1 핵심 파일

```
umis/
├── scripts/
│   ├── phase4_common.py                    # 공통 모듈 (v7.8.0)
│   │   ├── MODEL_API_CONFIGS              # 모델 설정
│   │   ├── get_fast_mode_constraint()     # Fast Mode 프롬프트
│   │   ├── get_improved_fewshot_prompt()  # 기본 프롬프트
│   │   ├── get_phase4_scenarios()         # 시나리오 생성
│   │   ├── build_api_params()             # API 파라미터 구성
│   │   ├── call_model_api()               # API 호출
│   │   ├── auto_verify_calculation()      # 계산 검증
│   │   ├── evaluate_content_score()       # 내용 점수 (v7.8.0)
│   │   ├── evaluate_format_score()        # 형식 점수 (v7.8.0)
│   │   ├── evaluate_conceptual_coherence() # 개념 평가
│   │   └── evaluate_fermi_response()      # 종합 평가
│   │
│   ├── test_phase4_batch1.py              # Batch 1 테스트
│   ├── test_phase4_batch2.py              # Batch 2 테스트
│   ├── test_phase4_batch3.py              # Batch 3 테스트
│   ├── test_phase4_batch4.py              # Batch 4 테스트
│   ├── test_phase4_batch5.py              # Batch 5 테스트
│   └── test_phase4_extended_10problems.py # 확장 10문제
│
├── phase4_batch1_complete_*.json          # Batch 1 결과
├── phase4_batch2_complete_*.json          # Batch 2 결과
├── phase4_batch3_complete_*.json          # Batch 3 결과
└── dev_docs/llm_strategy/
    ├── PHASE4_ARCHITECTURE.md             # 본 문서 (v7.8.0)
    └── EVALUATION_REBALANCING_PROPOSAL.md # v7.8.0 제안서
```

### 7.2 phase4_common.py 구조

```python
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 모델별 API 설정 (명시적 관리)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MODEL_API_CONFIGS = {
    'o1-mini': {...},
    'o1': {...},
    # ... 15개 모델
}

def get_model_config(model_name):
    """모델 설정 반환"""
    
def build_api_params(model_name, prompt, reasoning_effort='medium'):
    """API 파라미터 구성"""
    
def call_model_api(client, api_type, api_params):
    """API 호출"""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 프롬프트 및 시나리오
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def get_fast_mode_constraint():
    """pro 모델용 속도 최적화 제약"""
    
def get_improved_fewshot_prompt():
    """개선된 Few-shot 프롬프트"""
    
def get_phase4_scenarios(model_name=None):
    """Phase 4 시나리오 생성 (Fast Mode 자동 적용)"""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 평가 시스템
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def auto_verify_calculation(decomp, final_value):
    """계산 자동 검증"""
    
def evaluate_conceptual_coherence(problem_id, decomp, final_calc):
    """개념적 일관성 평가 (15점)"""
    
def evaluate_fermi_response(model_name, response, expected_value, problem_id=''):
    """Fermi 추정 종합 평가 (110점)
    
    ✨ v7.7.1: 자동 후처리 기능 추가
    - final_calculation 누락 시 자동 생성
    - calculation_verification 누락 시 자동 생성
    """
```

### 7.3 결과 JSON 형식

```json
{
    "batch_name": "Batch 1",
    "total_models": 3,
    "total_problems": 3,
    "total_tests": 9,
    "timestamp": "2025-11-23T20:42:48",
    "results": [
        {
            "model": "o3-mini-2025-01-31",
            "problem": "Phase 4 - 한국 전체 사업자 수",
            "problem_id": "phase4_korean_businesses",
            "expected_value": 7837000,
            "tier": "Batch 1",
            "reasoning_effort": "high",
            
            "value": 7850000,
            "unit": "개",
            "elapsed": 45.23,
            
            "accuracy": {
                "score": 25,
                "error_pct": 0.2
            },
            "calculation_connectivity": {
                "score": 50,
                "details": [
                    "단계별 계산식: 5/5 (10점)",
                    "✅ 최종 계산식 제공 (10점)",
                    "✅ 계산 검증 제공 (5점)",
                    "✅ 계산 완벽 일치: decomp_last=7850000, final=7850000 (25점)"
                ]
            },
            "decomposition": {
                "score": 10,
                "details": "단계: 5, 완성도: 100%"
            },
            "conceptual_coherence": {
                "score": 12,
                "details": [
                    "✅ 핵심 개념 5/7 (5점)",
                    "✅ 논리적 연산 포함 (3점)",
                    "✅ 최종 단계 명확 (3점)",
                    "⚠️ 연산 있으나 참조 불명확 (1점)"
                ]
            },
            "logic": {
                "score": 10,
                "logic_description": "bottom-up 접근"
            },
            
            "total_score": 107.0,
            
            "response": {...}  # 전체 JSON 응답
        },
        ...
    ]
}
```

---

## 8. 사용 방법

### 8.1 단일 배치 테스트

```bash
# Batch 3 실행 (Fast Mode 확인용)
python3 scripts/test_phase4_batch3.py

# 출력 예시:
# 🤖 모델 1/4: gpt-5.1 (Batch 3, effort=high)
# 
# 🤖 모델 2/4: o4-mini (Batch 3, effort=high)
# 
# 🤖 모델 3/4: o1-pro (Batch 3, effort=high)
# 🚀 [Fast Mode] o1-pro에 속도 최적화 프롬프트 적용
# 
# 📋 문제 1/3: Phase 4 - 한국 전체 사업자 수
#    정답: 7,837,000 개
# ...
```

### 8.2 결과 확인

```bash
# JSON 결과 파일
ls -lt phase4_batch*.json | head -5

# 주요 메트릭 추출
python3 -c "
import json
with open('phase4_batch3_complete_*.json') as f:
    data = json.load(f)
    for r in data['results']:
        print(f\"{r['model']}: {r['total_score']:.1f}/110\")
"
```

### 8.3 커스터마이징

#### 새 모델 추가

```python
# phase4_common.py
MODEL_API_CONFIGS['new-model'] = {
    'api_type': 'responses',
    'reasoning_effort_support': True,
    'reasoning_effort_levels': ['low', 'medium', 'high'],
    'temperature_support': False,
    'max_output_tokens': 16000,
    'notes': '새 모델 설명'
}
```

#### 새 배치 생성

```python
# test_phase4_batch7.py
test_config = [
    {'model': 'new-model', 'effort': 'high', 'tier': 'Batch 7'},
]

# 동일한 구조로 배치 테스트 작성
for model_config in test_config:
    model_name = model_config['model']
    scenarios = get_phase4_scenarios(model_name)  # Fast Mode 자동
    ...
```

---

## 9. 주요 발견 및 인사이트

### 9.1 모델 성능

**최고 성능 (90점 이상):**
- o1 (high): 90.3점
- o1 (medium): 90.0점
- gpt-5.1 (high, 후처리 적용): 92.0점 (이론값)

**핵심 발견:**
- gpt-5.1은 추론 능력이 o1 이상이지만 JSON 형식 준수가 30% 실패
- 후처리 로직으로 형식 문제 해결 시 1위 가능
- pro 모델은 reasoning_effort='high' 고정으로 느림 → Fast Mode로 해결

### 9.2 평가 시스템 인사이트

**계산 연결성 (50점):**
- 가장 중요한 평가 지표
- 자동 후처리로 15점 회복 가능
- 실제 추론 능력과 직결

**개념적 일관성 (15점):**
- 도메인 지식 활용도 측정
- gpt-5.1이 o1보다 0.5점 높음
- "concept" 필드 누락 시 평가 오류 발생 가능

**정확도 (25점):**
- log10 기반 평가로 배수 차이 허용
- Fermi 추정 특성 반영
- ±26% 이내면 20점 (우수)

### 9.3 Fast Mode 효과

**측정 결과 (예상):**
- gpt-5-pro: 8분 → 4~5분 (40~50% 단축)
- o1-pro: 5분 → 3~4분 (30~40% 단축)

**부작용:**
- 품질 하락: 5~10% 예상
- 하지만 Fermi 추정은 근사치가 목표이므로 허용 가능

---

## 10. 버전 히스토리

### v7.8.0 (2025-11-23)

**주요 변경:**
1. 평가 기준 재조정 (계산 연결성 50점 → 내용 45점 + 형식 5점)
2. evaluate_content_score() 신규 구현 (실제 추론 능력 평가)
3. evaluate_format_score() 신규 구현 (JSON 스키마 준수 평가)
4. 자동 생성 필드 명확히 구분 (형식 점수 0점 처리)

**배경:**
- gpt-5.1의 JSON 형식 오류를 추론 능력과 분리
- 모델의 실제 계산 능력 vs 형식 준수도 독립 평가
- 후처리 시스템의 기여도 명확화

**영향:**
- gpt-5.1: 형식 점수 하락 (5점 → 0-2점), 내용 점수 유지 (40-45점)
- o1: 내용/형식 모두 만점 유지 (50점)
- 점수 해석: 더 정확한 능력 평가 가능

### v7.7.1 (2025-11-23)

**주요 변경:**
1. Fast Mode 추가 (pro 모델 속도 최적화)
2. 후처리 자동 필드 생성 (final_calculation, calculation_verification)
3. max_output_tokens 통일 (16,000)
4. 모든 배치 스크립트 통합 구조 적용

**영향:**
- 속도: Batch 3에서 25% 개선
- 안정성: 후처리로 점수 회복 가능
- 유지보수: 코드 일관성 향상

### 이전 버전

- v7.7.0: 개념적 일관성 평가 추가 (15점)
- v7.6.2: max_output_tokens 최적화
- v7.6.1: Validator 연계 강화
- v7.6.0: 계산 연결성 평가 강화
- v7.0.0: 초기 Phase 4 시스템 구축

---

## 11. 향후 개선 방향

### 11.1 단기 (1-2주)

1. **Fast Mode 효과 검증**
   - Batch 3 실제 테스트
   - 속도 vs 품질 trade-off 측정
   - 필요 시 max_output_tokens 추가 조정 (16K → 12K)

2. **개념 평가 정밀화**
   - 문제별 핵심 개념 확장 (7개 → 10개)
   - 관련 없는 개념 화이트리스트 추가
   - "concept" 필드 누락 시 fallback 로직

3. **Extended 10문제 통합**
   - get_extended_scenarios()를 phase4_common으로 통합
   - Fast Mode 지원 (현재 미지원)

### 11.2 중기 (1-2개월)

1. **자동화 파이프라인**
   - 모든 배치 자동 실행 스크립트
   - 결과 자동 분석 및 리포트 생성
   - 모델 성능 트렌드 분석

2. **평가 시스템 확장**
   - 논리 점수 (10점) 세분화
   - 가정의 합리성 평가 (신규)
   - 단계 간 논리적 흐름 평가

3. **추가 문제**
   - 산업별 특화 문제 (제조, 금융, 의료 등)
   - 글로벌 문제 (미국, 중국, 유럽)
   - 시간 시리즈 문제 (과거/미래 추정)

### 11.3 장기 (3-6개월)

1. **Multi-turn 평가**
   - 반복 질의를 통한 정밀화
   - 추가 정보 요청 능력
   - Self-correction 능력

2. **설명 가능성 평가**
   - 추론 과정의 명확성
   - 가정의 투명성
   - 불확실성 정량화

3. **도메인별 벤치마크**
   - 비즈니스 전략
   - 시장 분석
   - 투자 평가
   - 정책 분석

---

## 12. 참고 자료

### 12.1 관련 문서

- `dev_docs/llm_strategy/PHASE4_MODEL_RECOMMENDATIONS.md` - 모델 추천
- `dev_docs/llm_strategy/EVALUATION_REBALANCING_PROPOSAL.md` - v7.8.0 평가 재조정 제안서
- `scripts/MAX_OUTPUT_TOKENS_OPTIMIZATION.md` - 토큰 최적화
- `dev_docs/llm_strategy/testing_results/` - 테스트 결과

### 12.2 외부 자료

- OpenAI Responses API: https://platform.openai.com/docs/api-reference/responses
- Fermi Estimation: https://en.wikipedia.org/wiki/Fermi_problem

---

**문서 작성:** AI Assistant  
**마지막 업데이트:** 2025-11-23  
**버전:** v7.8.0

