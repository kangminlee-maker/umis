#!/usr/bin/env python3
"""
⚠️ DEPRECATED (v7.11.0) - Legacy Phase 4 공통 함수 모듈
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

이 파일은 v7.10.2의 Phase 기반 벤치마크를 위한 Legacy 코드입니다.

**v7.11.0 변경사항**:
- Phase 5 (0-4) → 4-Stage Fusion Architecture로 재설계
- 벤치마크는 `tests/unit/`, `tests/integration/`, `tests/e2e/`로 이동
- 이 파일의 기능은 `umis_rag/core/model_configs.py`로 대체됨

**권장사항**:
- 새로운 벤치마크: `tests/` 폴더 참조
- 모델 설정: `config/model_configs.yaml` 및 `umis_rag/core/model_configs.py`
- Legacy 벤치마크: `archive/benchmarks_v7.10.2/`

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Phase 4 공통 함수 모듈 (Legacy)
- 개선된 프롬프트 (연결성 강제)
- 개념적 일관성 평가 (신규)
- Fermi 추정 평가 시스템
- 모델별 API 엔드포인트 처리 (명시적 관리)
"""

import math


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 모델별 API 설정 (명시적 관리)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MODEL_API_CONFIGS = {
    # ===== o-series =====
    'o1-mini': {
        'api_type': 'responses',
        'reasoning_effort_support': True,
        'reasoning_effort_levels': ['low', 'medium', 'high'],
        'temperature_support': False,
        'max_output_tokens': 16000,  # 통일: 모든 모델 16K
        'notes': 'STEM 최적화, 80% 저렴'
    },
    'o1': {
        'api_type': 'responses',
        'reasoning_effort_support': True,
        'reasoning_effort_levels': ['low', 'medium', 'high'],
        'temperature_support': False,
        'max_output_tokens': 16000,  # 통일: 모든 모델 16K
        'notes': '기본 reasoning 모델, function calling 지원'
    },
    'o1-2024-12-17': {
        'api_type': 'responses',
        'reasoning_effort_support': True,
        'reasoning_effort_levels': ['low', 'medium', 'high'],
        'temperature_support': False,
        'max_output_tokens': 16000,  # 통일: 모든 모델 16K
        'notes': 'o1의 특정 버전'
    },
    'o1-pro': {
        'api_type': 'responses',
        'reasoning_effort_support': True,
        'reasoning_effort_levels': ['high'],  # high 고정
        'reasoning_effort_fixed': 'high',
        'temperature_support': False,
        'max_output_tokens': 16000,  # 통일: 모든 모델 16K
        'context_window': 200000,
        'notes': 'Responses API only, 최고 성능, 비용 높음 ($150/1M input)'
    },
    'o1-pro-2025-03-19': {
        'api_type': 'responses',
        'reasoning_effort_support': True,
        'reasoning_effort_levels': ['high'],  # high 고정
        'reasoning_effort_fixed': 'high',
        'temperature_support': False,
        'max_output_tokens': 16000,  # 통일: 모든 모델 16K
        'context_window': 200000,
        'notes': 'o1-pro의 특정 버전'
    },
    'o3': {
        'api_type': 'responses',
        'reasoning_effort_support': True,
        'reasoning_effort_levels': ['low', 'medium', 'high'],
        'temperature_support': False,
        'max_output_tokens': 16000,  # 통일: 모든 모델 16K
        'notes': 'o3 시리즈'
    },
    'o3-2025-04-16': {
        'api_type': 'responses',
        'reasoning_effort_support': True,
        'reasoning_effort_levels': ['low', 'medium', 'high'],
        'temperature_support': False,
        'max_output_tokens': 16000,  # 통일: 모든 모델 16K
        'notes': 'o3의 특정 버전'
    },
    'o3-mini': {
        'api_type': 'responses',
        'reasoning_effort_support': True,
        'reasoning_effort_levels': ['low', 'medium', 'high'],
        'temperature_support': False,
        'max_output_tokens': 16000,  # 통일: 모든 모델 16K
        'notes': 'o3 mini 버전'
    },
    'o3-mini-2025-01-31': {
        'api_type': 'responses',
        'reasoning_effort_support': True,
        'reasoning_effort_levels': ['low', 'medium', 'high'],
        'temperature_support': False,
        'max_output_tokens': 16000,  # 통일: 모든 모델 16K
        'notes': 'o3-mini의 특정 버전'
    },
    'o4-mini': {
        'api_type': 'responses',
        'reasoning_effort_support': True,
        'reasoning_effort_levels': ['low', 'medium', 'high'],
        'temperature_support': False,
        'max_output_tokens': 16000,  # 통일: 모든 모델 16K
        'notes': 'o4 mini 버전'
    },
    'o4-mini-2025-04-16': {
        'api_type': 'responses',
        'reasoning_effort_support': True,
        'reasoning_effort_levels': ['low', 'medium', 'high'],
        'temperature_support': False,
        'max_output_tokens': 16000,  # 통일: 모든 모델 16K
        'notes': 'o4-mini의 특정 버전'
    },

    # ===== gpt-5 series =====
    'gpt-5.1': {
        'api_type': 'responses',  # Chat Completions도 지원
        'reasoning_effort_support': True,
        'reasoning_effort_levels': ['none', 'low', 'medium', 'high'],
        'temperature_support': True,  # reasoning.effort=none일 때만
        'temperature_condition': 'reasoning_effort_none',
        'max_output_tokens': 16000,  # 통일: 모든 모델 16K
        'context_window': 196000,
        'notes': 'temperature/top_p는 reasoning.effort=none일 때만'
    },
    'gpt-5-pro': {
        'api_type': 'responses',  # Responses API only
        'reasoning_effort_support': True,
        'reasoning_effort_levels': ['high'],  # high 고정
        'reasoning_effort_fixed': 'high',
        'temperature_support': False,
        'max_output_tokens': 16000,  # 통일: 모든 모델 16K
        'context_window': 400000,
        'notes': 'Responses API only, reasoning.effort=high 고정, temperature 미지원'
    },

    # ===== gpt-4.1 series =====
    'gpt-4.1': {
        'api_type': 'responses',
        'reasoning_effort_support': False,
        'temperature_support': False,  # Responses API에서는 미지원
        'max_output_tokens': 16000,  # 통일: 모든 모델 16K
        'notes': 'reasoning 미지원'
    },
    'gpt-4.1-mini': {
        'api_type': 'responses',
        'reasoning_effort_support': False,
        'temperature_support': False,  # Responses API에서는 미지원
        'max_output_tokens': 16000,  # 통일: 모든 모델 16K
        'notes': 'reasoning 미지원'
    },
}


def get_model_config(model_name):
    """
    모델 이름에 맞는 API 설정 반환

    Args:
        model_name: 모델 이름 (예: 'o1', 'gpt-5.1')

    Returns:
        dict: 모델 API 설정
    """
    # 정확한 이름 매칭
    if model_name in MODEL_API_CONFIGS:
        return MODEL_API_CONFIGS[model_name]

    # Prefix 기반 폴백 (새로운 버전 모델 대비)
    if model_name.startswith('o1-pro'):
        return MODEL_API_CONFIGS['o1-pro']
    elif model_name.startswith('o1-mini'):
        return MODEL_API_CONFIGS['o1-mini']
    elif model_name.startswith('o1'):
        return MODEL_API_CONFIGS['o1']
    elif model_name.startswith('o3-mini'):
        return MODEL_API_CONFIGS['o3-mini']
    elif model_name.startswith('o3'):
        return MODEL_API_CONFIGS['o3']
    elif model_name.startswith('o4-mini'):
        return MODEL_API_CONFIGS['o4-mini']
    elif model_name.startswith('gpt-5.1'):
        return MODEL_API_CONFIGS['gpt-5.1']
    elif model_name.startswith('gpt-5-pro'):
        return MODEL_API_CONFIGS['gpt-5-pro']
    elif model_name.startswith('gpt-4.1-mini'):
        return MODEL_API_CONFIGS['gpt-4.1-mini']
    elif model_name.startswith('gpt-4.1'):
        return MODEL_API_CONFIGS['gpt-4.1']

    # 기본값 (Chat Completions fallback)
    return {
        'api_type': 'chat',
        'reasoning_effort_support': False,
        'temperature_support': True,
        'max_output_tokens': 16000,
        'notes': 'Unknown model, using Chat Completions fallback'
    }


def build_api_params(model_name, prompt, reasoning_effort='medium'):
    """
    모델 설정에 맞는 API 파라미터 생성

    Args:
        model_name: 모델 이름
        prompt: 프롬프트 텍스트
        reasoning_effort: reasoning effort 레벨 (기본: 'medium')

    Returns:
        tuple: (api_type, api_params_dict)
    """
    config = get_model_config(model_name)

    api_params = {
        "model": model_name,
        "max_output_tokens": config['max_output_tokens']
    }

    api_type = config['api_type']

    # API 타입별 prompt 필드명
    if api_type == 'responses':
        api_params["input"] = prompt
    else:  # 'chat'
        api_params["messages"] = [{"role": "user", "content": prompt}]

    # Reasoning effort 처리
    if config['reasoning_effort_support']:
        # 고정된 effort가 있으면 사용
        if 'reasoning_effort_fixed' in config:
            effort_to_use = config['reasoning_effort_fixed']
        else:
            # 지원되는 레벨인지 확인
            if reasoning_effort in config['reasoning_effort_levels']:
                effort_to_use = reasoning_effort
            else:
                # 지원 안 되면 가장 가까운 레벨 선택
                effort_to_use = config['reasoning_effort_levels'][-1]  # 기본적으로 가장 높은 레벨

        api_params["reasoning"] = {"effort": effort_to_use}

    # Temperature 처리 (Chat Completions에서만, 또는 특정 조건)
    if api_type == 'chat' and config.get('temperature_support'):
        api_params["temperature"] = 0.3  # 일관성을 위한 낮은 temperature

    return api_type, api_params


def call_model_api(client, api_type, api_params):
    """
    API 타입에 맞게 모델 호출

    Args:
        client: OpenAI client
        api_type: 'responses' 또는 'chat'
        api_params: API 파라미터 dict

    Returns:
        API response object
    """
    if api_type == 'responses':
        return client.responses.create(**api_params)
    else:  # 'chat'
        return client.chat.completions.create(**api_params)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 프롬프트 및 시나리오
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def get_fast_mode_constraint():
    """pro 모델용 속도 최적화 제약 (v7.7.1)"""
    return '''
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔴 SPEED OPTIMIZATION MODE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⏱️ 목표 응답 시간: 60초 이내
📏 최대 출력 길이: 2,000자 이내 (약 500 토큰)
📋 decomposition: 3-5단계만 (필수 단계만 포함)
✂️ reasoning: 각 단계 15단어 이내

💡 빠르고 간결하게 핵심만 답변하세요!
   깊은 추론보다는 직관적 근사치를 우선하세요.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
'''


def get_improved_fewshot_prompt():
    """개선된 Few-shot 프롬프트 - 계산 연결성 + concept 필드 강제"""
    return '''
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔴 CRITICAL MANDATORY FIELDS (누락 시 0점!):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. decomposition의 모든 단계에 "concept" 필드 필수!
2. 최상위 "final_calculation" 필드 필수!
3. 최상위 "calculation_verification" 필드 필수!

⚠️ 이 3개 필드가 하나라도 누락되면 평가 점수가 크게 감점됩니다!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

올바른 예시: 서울시 택시 수

{
    "value": 66667,  ← 반드시 마지막 step의 value와 동일!
    "unit": "대",
    "confidence": 0.6,
    "method": "bottom-up",
    "decomposition": [
        {
            "step": "1. 서울 인구",
            "concept": "population_seoul",  ← 필수! 도메인 개념 명시
            "value": 10000000,
            "unit": "명",
            "calculation": "1000만명 (통계 기반)",
            "reasoning": "서울시 공식 인구 통계"
        },
        {
            "step": "2. 1인당 연간 택시 이용",
            "concept": "taxi_usage_per_capita",  ← 필수!
            "value": 20,
            "unit": "회",
            "calculation": "월 1.5회 × 12개월 ≈ 20",
            "reasoning": "대중교통 중심, 가끔 이용"
        },
        {
            "step": "3. 연간 총 이용 횟수",
            "concept": "total_taxi_rides",  ← 필수!
            "value": 200000000,
            "unit": "회",
            "calculation": "10000000 × 20 = 200000000",
            "reasoning": "step1 × step2"
        },
        {
            "step": "4. 택시 1대당 연간 운행",
            "concept": "rides_per_taxi",  ← 필수!
            "value": 3000,
            "unit": "회",
            "calculation": "일 10회 × 300일 = 3000",
            "reasoning": "2교대 기준"
        },
        {
            "step": "5. 최종: 필요 택시 수",
            "concept": "total_taxis_needed",  ← 필수! 마지막 단계도!
            "value": 66667,  ← 이 값이 최종 "value"가 됨!
            "unit": "대",
            "calculation": "200000000 ÷ 3000 = 66667",
            "reasoning": "총이용 ÷ 대당운행 = step3 ÷ step4"
        }
    ],
    "final_calculation": "step5 = step3 ÷ step4 = 200000000 ÷ 3000 = 66667",  ← 필수!
    "calculation_verification": "✓ 검증: 10,000,000명 × 20회 ÷ 3,000회 = 66,667대"  ← 필수!
}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MANDATORY RULES (절대 규칙):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. 🔴 "concept" 필드 - 모든 decomposition 단계에 필수!
   → 도메인 특화 개념을 영어 snake_case로 명시
   → 예: "population_seoul", "taxi_usage_per_capita"
   → 누락 시 개념 점수 0점!

2. 🔴 "final_calculation" 필드 - JSON 최상위에 필수!
   → decomposition 마지막 단계 계산을 실제 숫자로 재검증
   → 예: "step5 = step3 ÷ step4 = 200000000 ÷ 3000 = 66667"
   → 누락 시 연결성 점수 -10점!

3. 🔴 "calculation_verification" 필드 - JSON 최상위에 필수!
   → 전체 계산 과정 재확인
   → 예: "✓ 검증: 10,000,000명 × 20회 ÷ 3,000회 = 66,667대"
   → 누락 시 연결성 점수 -5점!

4. 최종 추정값 = decomposition 마지막 단계의 value
   → JSON의 "value": 66667 = decomposition[-1]["value"]: 66667

5. 마지막 단계는 반드시 최종 계산 단계
   → "step": "N. 최종: [추정 대상]"
   → 이 단계의 value가 곧 최종 답

6. 각 중간 단계는 명확한 사칙연산으로 연결
   → "calculation": "step3 ÷ step4 = 200000000 ÷ 3000 = 66667"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
'''


def get_phase4_scenarios(model_name=None):
    """Phase 4 시나리오 생성
    
    Args:
        model_name: 모델 이름 (pro 모델이면 Fast Mode 추가)
    """
    fewshot_example = get_improved_fewshot_prompt()
    
    # pro 모델이면 Fast Mode constraint 추가
    pro_models = ['gpt-5-pro', 'o1-pro', 'o1-pro-2025-03-19']
    if model_name and model_name in pro_models:
        fast_mode = get_fast_mode_constraint()
        print(f"  🚀 [Fast Mode] {model_name}에 속도 최적화 프롬프트 적용")
    else:
        fast_mode = ""

    return [
        {
            'id': 'phase4_korean_businesses',
            'name': 'Phase 4 - 한국 전체 사업자 수',
            'phase': 4,
            'prompt': f'''{fast_mode}{fewshot_example}

이제 실제 문제를 풀어주세요:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
문제: 한국 전체 사업자 수를 추정하세요.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

힌트:
- 한국 인구, 경제활동인구 고려
- 자영업자, 법인 사업자 구분
- 다중 사업자등록 가능성 고려

⚠️ CRITICAL: 반드시 아래 규칙을 따르세요!

1. decomposition의 마지막 단계 value = JSON 최상위 "value"
2. 마지막 step의 "step" 필드는 반드시 "N. 최종: 한국 전체 사업자 수"
3. 마지막 step의 "calculation"은 실제 사칙연산 (예: "4000000 + 3837000 = 7837000")
4. 반올림/근사치는 마지막에만 적용

JSON 형식 (엄격히 준수):
{{
    "value": <decomposition 마지막 단계의 value와 정확히 동일!>,
    "unit": "개",
    "confidence": <0.3-0.7>,
    "method": "bottom-up",
    "decomposition": [
        {{
            "step": "1. [첫 번째 구성요소]",
            "concept": "[도메인_개념_snake_case]",  ← 🔴 필수!
            "value": <숫자>,
            "unit": "[단위]",
            "calculation": "[계산 과정]",
            "reasoning": "[가정 및 근거]"
        }},
        {{
            "step": "2. [두 번째 구성요소]",
            "concept": "[도메인_개념_snake_case]",  ← 🔴 필수!
            "value": <숫자>,
            "unit": "[단위]",
            "calculation": "[계산 과정]",
            "reasoning": "[가정 및 근거]"
        }},
        ...
        {{
            "step": "N. 최종: 한국 전체 사업자 수",
            "concept": "total_businesses_korea",  ← 🔴 필수!
            "value": <이 값이 곧 최상위 "value"!>,
            "unit": "개",
            "calculation": "step1 + step2 + ... = <정확한 계산>",
            "reasoning": "모든 구성요소 합산"
        }}
    ],
    "final_calculation": "step1 + step2 + ... = <실제 숫자로 재계산>",  ← 🔴 필수!
    "calculation_verification": "✓ 검증: [전체 계산 과정 재확인]"  ← 🔴 필수!
}}

🔴 체크리스트 (반드시 확인!):
□ 모든 decomposition 단계에 "concept" 필드 있음 ← 누락 시 0점!
□ 최상위에 "final_calculation" 필드 있음 ← 누락 시 -10점!
□ 최상위에 "calculation_verification" 필드 있음 ← 누락 시 -5점!
□ decomposition[-1]["value"] == JSON["value"] ← 반드시 확인!
□ 마지막 step은 최종 계산 단계
□ 모든 calculation 필드에 실제 숫자 포함''',
            'expected_value': 7837000,
            'expected_unit': '개',
        },
        {
            'id': 'phase4_seoul_population',
            'name': 'Phase 4 - 서울시 인구',
            'phase': 4,
            'prompt': f'''{fast_mode}{fewshot_example}

이제 실제 문제:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
문제: 서울시 인구를 추정하세요.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

힌트:
- 한국 전체 인구 대비 서울 비중
- 수도권 집중도 고려
- 또는 면적 기반 접근

⚠️ CRITICAL: decomposition 마지막 단계의 value = JSON 최상위 "value" (정확히 일치!)

반드시 같은 JSON 형식으로 응답하세요.
마지막 step: "N. 최종: 서울시 인구", value는 이 단계의 계산 결과''',
            'expected_value': 9668465,
            'expected_unit': '명',
        },
        {
            'id': 'phase4_coffee_shops',
            'name': 'Phase 4 - 한국 커피 전문점 수',
            'phase': 4,
            'prompt': f'''{fast_mode}⚠️ CRITICAL RULE: 최종 추정값(value)은 반드시 decomposition의 마지막 단계 값과 정확히 일치해야 합니다!

올바른 예시:

{{
    "value": 66667,  ← 마지막 step의 value와 동일!
    "decomposition": [
        {{"step": "1. 인구", "value": 10000000, "calculation": "1000만"}},
        {{"step": "2. 이용횟수", "value": 20, "calculation": "월 2회 × 12"}},
        {{"step": "3. 총이용", "value": 200000000, "calculation": "10000000 × 20"}},
        {{"step": "4. 택시운행", "value": 3000, "calculation": "일 10회 × 300일"}},
        {{"step": "5. 최종: 택시 수", "value": 66667, "calculation": "200000000 ÷ 3000 = 66667"}}
    ],
    "final_calculation": "step3 ÷ step4 = 200000000 ÷ 3000 = 66667"
}}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
문제: 한국 커피 전문점 수를 추정하세요.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

힌트:
- 커피 소비 인구
- 점포당 고객 수
- 브랜드 경쟁 및 상권 중복

⚠️ 필수:
1. 마지막 step: "N. 최종: 커피 전문점 수"
2. 이 단계의 value = JSON 최상위 "value" (정확히 일치!)
3. calculation에 실제 사칙연산 포함

반드시 같은 형식으로 응답''',
            'expected_value': 100000,
            'expected_unit': '개',
        }
    ]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 평가 시스템 (v7.8.0 - 내용/형식 분리)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 헬퍼 함수들
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

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


def auto_verify_calculation(decomp, final_value):
    """분해 값들로 최종값 자동 계산 시도"""
    if not isinstance(decomp, list) or len(decomp) < 2:
        return None, "단계 부족"

    values = [step.get('value', 0) for step in decomp if isinstance(step.get('value'), (int, float))]

    if len(values) < 2:
        return None, "유효한 값 부족"

    results = []

    if values[-1] > 0:
        error = abs(values[-1] - final_value) / max(final_value, 1)
        results.append(('마지막 단계', values[-1], error))

    total = sum(values)
    if total > 0:
        error = abs(total - final_value) / max(final_value, 1)
        results.append(('모든 단계 합', total, error))

    if len(values) >= 2:
        last_two = sum(values[-2:])
        if last_two > 0:
            error = abs(last_two - final_value) / max(final_value, 1)
            results.append(('마지막 2단계 합', last_two, error))

    if results:
        best = min(results, key=lambda x: x[2])
        return best[1], f"{best[0]}: {best[1]:,.0f} (오차 {best[2]*100:.1f}%)"

    return None, "계산 불가"


def evaluate_content_score(decomp, final_value):
    """내용 점수 평가 (45점) - v7.8.0
    
    실제 추론 능력을 평가 (형식과 무관)
    
    Returns:
        dict: {
            'score': float (0-45),
            'details': list of str,
            'breakdown': {
                'step_completeness': float (0-10),
                'calculation_logic': float (0-10),
                'numerical_accuracy': float (0-25)
            }
        }
    """
    score = 0
    details = []
    breakdown = {}
    
    if not isinstance(decomp, list) or len(decomp) == 0:
        return {
            'score': 0,
            'details': ['❌ decomposition 없음'],
            'breakdown': {'step_completeness': 0, 'calculation_logic': 0, 'numerical_accuracy': 0}
        }
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 1. 단계별 계산 완성도 (10점)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    calculable_steps = 0
    for step in decomp:
        # 계산 가능 조건: value + (calculation 또는 reasoning에 연산)
        if (step.get('value') is not None and 
            (step.get('calculation') or 
             any(op in step.get('reasoning', '') for op in ['×', '÷', '+', '-', '*', '/']))):
            calculable_steps += 1
    
    completeness_score = (calculable_steps / len(decomp)) * 10
    score += completeness_score
    breakdown['step_completeness'] = round(completeness_score, 1)
    details.append(f"단계별 계산 완성도: {calculable_steps}/{len(decomp)} ({completeness_score:.1f}점)")
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 2. 계산 논리 연결 (10점)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    logic_score = 0
    
    # 2-1. 연산 적절성 (4점)
    if has_appropriate_operations(decomp):
        logic_score += 4
        details.append("✅ 연산 적절성 (4점)")
    else:
        details.append("❌ 연산 부족 (0점)")
    
    # 2-2. 단계 순서 (3점)
    if has_logical_order(decomp):
        logic_score += 3
        details.append("✅ 논리적 순서 (3점)")
    else:
        details.append("❌ 순서 불명확 (0점)")
    
    # 2-3. 중간 결과 활용 (3점)
    if uses_intermediate_results(decomp):
        logic_score += 3
        details.append("✅ 중간 결과 활용 (3점)")
    else:
        details.append("❌ 중간 결과 미활용 (0점)")
    
    score += logic_score
    breakdown['calculation_logic'] = logic_score
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 3. 수치 정확성 (25점)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    if len(decomp) > 0:
        last_value = decomp[-1].get('value', 0)
        
        if isinstance(last_value, (int, float)) and last_value > 0 and final_value > 0:
            error_ratio = abs(last_value - final_value) / max(final_value, 1)
            
            if error_ratio < 0.01:
                numerical_score = 25
                details.append(f"✅ 수치 완벽 일치 (25점)")
            elif error_ratio < 0.05:
                numerical_score = 20
                details.append(f"✅ 수치 거의 일치 (20점)")
            elif error_ratio < 0.10:
                numerical_score = 15
                details.append(f"⚠️ 수치 근접 (15점)")
            elif error_ratio < 0.30:
                numerical_score = 10
                details.append(f"⚠️ 수치 부분 일치 (10점)")
            else:
                numerical_score = 5
                details.append(f"❌ 수치 불일치 (5점)")
        else:
            numerical_score = 0
            details.append("❌ 수치 검증 불가 (0점)")
    else:
        numerical_score = 0
        details.append("❌ 마지막 단계 없음 (0점)")
    
    score += numerical_score
    breakdown['numerical_accuracy'] = numerical_score
    
    return {
        'score': min(score, 45),
        'details': details,
        'breakdown': breakdown
    }


def evaluate_format_score(response, decomp, auto_generated_fields=None):
    """형식 점수 평가 (5점) - v7.8.0
    
    JSON 스키마 준수도 평가
    
    Args:
        response: 응답 dict
        decomp: decomposition 리스트
        auto_generated_fields: 자동 생성된 필드 목록 (선택적)
    
    Returns:
        dict: {
            'score': float (0-5),
            'details': list of str,
            'breakdown': {
                'final_calculation': int (0 or 2),
                'calculation_verification': int (0 or 2),
                'concept_fields': float (0-1)
            }
        }
    """
    score = 0
    details = []
    breakdown = {}
    auto_gen = auto_generated_fields or []
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 1. final_calculation 필드 (2점)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    if 'final_calculation' in response:
        # 자동 생성인지 확인
        if 'final_calculation' in auto_gen or 'Auto-generated' in str(response.get('final_calculation', '')):
            score += 0
            breakdown['final_calculation'] = 0
            details.append("❌ final_calculation 누락 (자동 생성, 0점)")
        else:
            score += 2
            breakdown['final_calculation'] = 2
            details.append("✅ final_calculation 제공 (2점)")
    else:
        score += 0
        breakdown['final_calculation'] = 0
        details.append("❌ final_calculation 누락 (0점)")
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 2. calculation_verification 필드 (2점)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    if 'calculation_verification' in response:
        # 자동 생성인지 확인
        if ('calculation_verification' in auto_gen or 
            '자동 검증' in str(response.get('calculation_verification', ''))):
            score += 0
            breakdown['calculation_verification'] = 0
            details.append("❌ calculation_verification 누락 (자동 생성, 0점)")
        else:
            score += 2
            breakdown['calculation_verification'] = 2
            details.append("✅ calculation_verification 제공 (2점)")
    else:
        score += 0
        breakdown['calculation_verification'] = 0
        details.append("❌ calculation_verification 누락 (0점)")
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 3. concept 필드 완성도 (1점)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    if decomp and len(decomp) > 0:
        with_concept = sum(1 for s in decomp if s.get('concept'))
        concept_ratio = with_concept / len(decomp)
        
        if concept_ratio >= 0.8:
            concept_score = 1.0
            score += 1.0
            breakdown['concept_fields'] = 1.0
            details.append(f"✅ concept 필드 완성 ({with_concept}/{len(decomp)}, 1점)")
        elif concept_ratio >= 0.5:
            concept_score = 0.5
            score += 0.5
            breakdown['concept_fields'] = 0.5
            details.append(f"⚠️ concept 필드 부분 ({with_concept}/{len(decomp)}, 0.5점)")
        else:
            concept_score = 0
            breakdown['concept_fields'] = 0
            details.append(f"❌ concept 필드 부족 ({with_concept}/{len(decomp)}, 0점)")
    else:
        breakdown['concept_fields'] = 0
        details.append("❌ concept 필드 없음 (0점)")
    
    return {
        'score': score,
        'details': details,
        'breakdown': breakdown
    }


def evaluate_conceptual_coherence(problem_id, decomp, final_calc):
    """개념적 일관성 평가 (15점)

    Pseudo-code의 논리적 타당성 평가:
    - 각 단계가 최종 목표와 개념적으로 연결되는지
    - 도메인 지식에 부합하는지
    - 불필요한 단계는 없는지
    """
    score = 0
    details = []

    if not isinstance(decomp, list) or len(decomp) < 2:
        return {
            'score': 0,
            'details': ['❌ decomposition 없음 또는 부족']
        }

    # 단계별 개념 추출
    steps_text = ' '.join([
        f"{s.get('step', '')} {s.get('reasoning', '')} {s.get('calculation', '')}"
        for s in decomp
    ]).lower()

    # 문제별 핵심 개념 키워드
    concept_keywords = {
        'phase4_korean_businesses': {
            'essential': ['인구', '경제활동', '자영업', '법인', '사업자', '기업', '창업'],
            'operations': ['합', '더하', '+', '곱', '×', '*', '비율', '%'],
            'irrelevant': ['키', '몸무게', '날씨', '온도', '택시', '커피'],
            'logic': '경제활동인구 기반 또는 업종별 합산'
        },
        'phase4_seoul_population': {
            'essential': ['인구', '서울', '비중', '비율', '수도권', '전국'],
            'operations': ['곱', '×', '*', '비율', '%'],
            'irrelevant': ['사업자', '커피', '택시'],
            'logic': '전국 인구 × 서울 비중'
        },
        'phase4_coffee_shops': {
            'essential': ['인구', '소비', '고객', '점포', '커피', '매장', '수요'],
            'operations': ['나누', '÷', '/', '곱', '×'],
            'irrelevant': ['택시', '사업자등록', '법인'],
            'logic': '소비인구 ÷ 점포당 고객 수'
        }
    }

    keywords = concept_keywords.get(problem_id, concept_keywords['phase4_korean_businesses'])

    # 1. 핵심 개념 포함 여부 (5점)
    essential_found = sum(1 for kw in keywords['essential'] if kw in steps_text)
    essential_ratio = essential_found / len(keywords['essential'])

    if essential_ratio >= 0.4:  # 40% 이상 포함
        essential_score = 5
        details.append(f"✅ 핵심 개념 포함 ({essential_found}/{len(keywords['essential'])}) (5점)")
    elif essential_ratio >= 0.2:
        essential_score = 3
        details.append(f"⚠️ 핵심 개념 일부 ({essential_found}/{len(keywords['essential'])}) (3점)")
    else:
        essential_score = 0
        details.append(f"❌ 핵심 개념 부족 ({essential_found}/{len(keywords['essential'])}) (0점)")

    score += essential_score

    # 2. 논리적 연산 존재 (3점)
    operations_found = any(op in steps_text or op in final_calc.lower() for op in keywords['operations'])
    if operations_found:
        score += 3
        details.append("✅ 논리적 연산 포함 (3점)")
    else:
        details.append("❌ 논리적 연산 없음 (0점)")

    # 3. 관련 없는 개념 사용 (-3점, 감점)
    irrelevant_found = [kw for kw in keywords['irrelevant'] if kw in steps_text]
    if irrelevant_found:
        penalty = min(3, len(irrelevant_found))
        score -= penalty
        details.append(f"⚠️ 관련 없는 개념 사용 ({', '.join(irrelevant_found[:2])}) (-{penalty}점)")
    else:
        details.append("✅ 관련 없는 개념 없음 (0점)")

    # 4. Pseudo-code 논리 구조 (7점)
    # 마지막 단계가 최종 계산 단계인지
    last_step = decomp[-1].get('step', '').lower()
    if '최종' in last_step or 'total' in last_step or '합계' in last_step:
        score += 3
        details.append("✅ 최종 단계 명확 (3점)")
    else:
        details.append("⚠️ 최종 단계 불명확 (0점)")

    # 중간 단계들이 논리적으로 연결되는지 (간단한 휴리스틱)
    # calculation 필드에 이전 step 참조가 있는지
    has_step_ref = any('step' in s.get('calculation', '').lower() for s in decomp[1:])
    if has_step_ref:
        score += 4
        details.append("✅ 단계 간 참조 명확 (4점)")
    else:
        # calculation에 실제 숫자 연산이 있는지
        has_calc = any(op in s.get('calculation', '') for s in decomp for op in ['+', '-', '*', '×', '/', '÷'])
        if has_calc:
            score += 2
            details.append("⚠️ 연산 있으나 참조 불명확 (2점)")
        else:
            details.append("❌ 단계 간 연결 불명확 (0점)")

    return {
        'score': max(0, min(score, 15)),  # 0-15점 범위
        'details': details,
        'logic_description': keywords['logic']
    }


def evaluate_fermi_response(model_name, response, expected_value, problem_id=''):
    """Fermi 추정 평가 (110점) - v7.8.0
    
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    평가 기준 (총 110점):
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    1. 정확도 (25점): Log10 기반 오차율
    2. 내용 점수 (45점):
       - 단계별 계산 완성도 (10점)
       - 계산 논리 연결 (10점)
       - 수치 정확성 (25점)
    3. 형식 점수 (5점):
       - final_calculation (2점)
       - calculation_verification (2점)
       - concept 필드 (1점)
    4. 분해 품질 (10점)
    5. 개념적 일관성 (15점)
    6. 논리 (10점)
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    ✨ v7.8.0 주요 변경:
    - 계산 연결성 (50점) → 내용 점수 (45점) + 형식 점수 (5점)
    - 자동 생성된 필드는 형식 점수 0점 처리
    """
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔄 후처리: 필수 필드 자동 생성
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    decomp = response.get('decomposition', [])
    auto_generated_fields = []
    
    if not response.get('final_calculation') and decomp and len(decomp) > 0:
        # decomposition 마지막 단계의 calculation 사용
        last_step = decomp[-1]
        if last_step.get('calculation'):
            response['final_calculation'] = f"Auto-generated: {last_step['calculation']}"
            auto_generated_fields.append('final_calculation')
            print(f"  🔄 [후처리] final_calculation 자동 생성: {last_step.get('step', 'N/A')}")
    
    if not response.get('calculation_verification'):
        # 자동 검증 결과 사용
        if decomp and len(decomp) > 0:
            auto_result, auto_msg = auto_verify_calculation(decomp, response.get('value', 0))
            if auto_result is not None:
                response['calculation_verification'] = f"✓ 자동 검증: {auto_msg}"
                auto_generated_fields.append('calculation_verification')
                print(f"  🔄 [후처리] calculation_verification 자동 생성")
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 평가 시작
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    result = {
        'model': model_name,
        'value': response.get('value', 0),
        'unit': response.get('unit', ''),
        'expected_value': expected_value
    }

    if isinstance(result['value'], dict):
        result['value'] = 0
    elif not isinstance(result['value'], (int, float)):
        try:
            result['value'] = float(str(result['value']).replace(',', ''))
        except:
            result['value'] = 0

    # 1. 정확도 (25점)
    if result['value'] > 0 and expected_value > 0:
        error = abs(math.log10(result['value']) - math.log10(expected_value))

        if error < 0.05:
            accuracy_score = 25
        elif error < 0.1:
            accuracy_score = 20
        elif error < 0.3:
            accuracy_score = 15
        elif error < 0.5:
            accuracy_score = 10
        else:
            accuracy_score = 5

        error_pct = (10**error - 1) * 100
    else:
        accuracy_score = 0
        error_pct = 999

    result['accuracy'] = {
        'score': accuracy_score,
        'error_pct': round(error_pct, 1)
    }

    # 2. 내용 점수 (45점) - v7.8.0
    content_eval = evaluate_content_score(decomp, result['value'])
    result['content_score'] = content_eval

    # 3. 형식 점수 (5점) - v7.8.0
    format_eval = evaluate_format_score(response, decomp, auto_generated_fields)
    result['format_score'] = format_eval

    # 4. 분해 품질 (10점)
    if isinstance(decomp, list) and len(decomp) >= 3:
        decomp_score = 3
        complete = sum(1 for s in decomp
                      if all(k in s for k in ['step', 'value', 'calculation', 'reasoning']))
        decomp_score += min(7, (complete / len(decomp)) * 7)
    else:
        decomp_score = 0

    result['decomposition'] = {
        'score': decomp_score,
        'count': len(decomp) if isinstance(decomp, list) else 0
    }

    # 5. 개념적 일관성 (15점)
    conceptual = evaluate_conceptual_coherence(
        problem_id,
        decomp,
        response.get('final_calculation', '')
    )

    result['conceptual_coherence'] = conceptual

    # 6. 논리 (10점)
    logic_score = 0
    if response.get('method'):
        logic_score += 5
    if response.get('reasoning'):
        logic_score += 5

    result['logic'] = {'score': logic_score}

    # 총점 계산 (110점)
    result['total_score'] = (
        accuracy_score +
        content_eval['score'] +
        format_eval['score'] +
        decomp_score +
        conceptual['score'] +
        logic_score
    )

    return result


