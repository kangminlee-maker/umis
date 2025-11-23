#!/usr/bin/env python3
"""
GPT-5.1 단독 테스트 (3개 문제 전체)
"""

import os
import json
import time
import math
import re
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


def get_phase4_scenarios():
    """Phase 4 Fermi 시나리오 - Few-shot 예시 포함"""
    
    fewshot_example = '''
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ CRITICAL RULE: 최종 추정값(value)은 반드시 decomposition의 마지막 단계 값과 정확히 일치해야 합니다!

올바른 예시: 서울시 택시 수

{
    "value": 66667,  ← 반드시 마지막 step의 value와 동일!
    "unit": "대",
    "confidence": 0.6,
    "method": "bottom-up",
    "decomposition": [
        {
            "step": "1. 서울 인구",
            "value": 10000000,
            "calculation": "1000만명 (통계 기반)",
            "reasoning": "서울시 공식 인구 통계"
        },
        {
            "step": "2. 1인당 연간 택시 이용",
            "value": 20,
            "calculation": "월 1.5회 × 12개월 ≈ 20",
            "reasoning": "대중교통 중심, 가끔 이용"
        },
        {
            "step": "3. 연간 총 이용 횟수",
            "value": 200000000,
            "calculation": "10000000 × 20 = 200000000",
            "reasoning": "step1 × step2"
        },
        {
            "step": "4. 택시 1대당 연간 운행",
            "value": 3000,
            "calculation": "일 10회 × 300일 = 3000",
            "reasoning": "2교대 기준"
        },
        {
            "step": "5. 최종: 필요 택시 수",
            "value": 66667,  ← 이 값이 최종 "value"가 됨!
            "calculation": "200000000 ÷ 3000 = 66667",
            "reasoning": "총이용 ÷ 대당운행 = step3 ÷ step4"
        }
    ],
    "final_calculation": "step5 = step3 ÷ step4 = 200000000 ÷ 3000 = 66667",
    "calculation_verification": "✓ 검증: 10,000,000명 × 20회 ÷ 3,000회 = 66,667대"
}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MANDATORY RULES (절대 규칙):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. 최종 추정값 = decomposition 마지막 단계의 value
   → JSON의 "value": 66667 = decomposition[-1]["value"]: 66667

2. 마지막 단계는 반드시 최종 계산 단계
   → "step": "5. 최종: [추정 대상]"
   → 이 단계의 value가 곧 최종 답

3. 각 중간 단계는 명확한 사칙연산으로 연결
   → "calculation": "step3 ÷ step4 = 200000000 ÷ 3000 = 66667"

4. final_calculation에서 재검증
   → 실제 숫자로 계산 과정 재확인

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
'''
    
    return [
        {
            'id': 'phase4_korean_businesses',
            'name': 'Phase 4 - 한국 전체 사업자 수',
            'phase': 4,
            'prompt': f'''{fewshot_example}

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
            "value": <숫자>,
            "calculation": "[계산 과정]",
            "reasoning": "[가정 및 근거]"
        }},
        {{
            "step": "2. [두 번째 구성요소]",
            "value": <숫자>,
            "calculation": "[계산 과정]",
            "reasoning": "[가정 및 근거]"
        }},
        ...
        {{
            "step": "N. 최종: 한국 전체 사업자 수",
            "value": <이 값이 곧 최상위 "value"!>,
            "calculation": "step1 + step2 + ... = <정확한 계산>",
            "reasoning": "모든 구성요소 합산"
        }}
    ],
    "final_calculation": "step1 + step2 + ... = <실제 숫자로 재계산>",
    "calculation_verification": "✓ 검증: [전체 계산 과정 재확인]"
}}

체크리스트:
□ decomposition[-1]["value"] == JSON["value"] ← 반드시 확인!
□ 마지막 step은 최종 계산 단계
□ 모든 calculation 필드에 실제 숫자 포함
□ final_calculation에서 재검증''',
            'expected_value': 7837000,
            'expected_unit': '개',
        },
        {
            'id': 'phase4_seoul_population',
            'name': 'Phase 4 - 서울시 인구',
            'phase': 4,
            'prompt': f'''{fewshot_example}

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
            'prompt': f'''⚠️ CRITICAL RULE: 최종 추정값(value)은 반드시 decomposition의 마지막 단계 값과 정확히 일치해야 합니다!

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
    """Fermi 추정 평가 (100점)"""
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
    
    # 2. 계산 연결성 (50점)
    decomp = response.get('decomposition', [])
    final_calc = response.get('final_calculation', '')
    calc_verify = response.get('calculation_verification', '')
    
    calc_score = 0
    calc_details = []
    
    if not isinstance(decomp, list) or len(decomp) == 0:
        calc_details.append("❌ decomposition 없음")
    else:
        with_calc = sum(1 for s in decomp if s.get('calculation'))
        calc_ratio = with_calc / len(decomp)
        step_calc_score = calc_ratio * 10
        calc_score += step_calc_score
        calc_details.append(f"단계별 계산식: {with_calc}/{len(decomp)} ({step_calc_score:.0f}점)")
        
        if final_calc:
            calc_score += 10
            calc_details.append(f"✅ 최종 계산식 제공 (10점)")
        else:
            calc_details.append(f"❌ 최종 계산식 누락 (0점)")
        
        if calc_verify:
            calc_score += 5
            calc_details.append(f"✅ 계산 검증 제공 (5점)")
        
        auto_result, auto_msg = auto_verify_calculation(decomp, result['value'])
        
        if auto_result is not None:
            error_ratio = abs(auto_result - result['value']) / max(result['value'], 1)
            
            if error_ratio < 0.01:
                verify_score = 25
                calc_details.append(f"✅ 계산 완벽 일치: {auto_msg} (25점)")
            elif error_ratio < 0.05:
                verify_score = 20
                calc_details.append(f"✅ 계산 거의 일치: {auto_msg} (20점)")
            elif error_ratio < 0.1:
                verify_score = 15
                calc_details.append(f"⚠️ 계산 근접: {auto_msg} (15점)")
            elif error_ratio < 0.3:
                verify_score = 10
                calc_details.append(f"⚠️ 계산 부분 일치: {auto_msg} (10점)")
            else:
                verify_score = 5
                calc_details.append(f"❌ 계산 불일치: {auto_msg} (5점)")
        else:
            verify_score = 0
            calc_details.append(f"❌ 계산 검증 실패: {auto_msg} (0점)")
        
        calc_score += verify_score
    
    result['calculation_connectivity'] = {
        'score': min(calc_score, 50),
        'details': calc_details
    }
    
    # 3. 분해 품질 (10점) - 15점에서 10점으로 조정
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
    
    # 4. 개념적 일관성 (15점) - 새로 추가!
    conceptual = evaluate_conceptual_coherence(
        problem_id,
        decomp,
        final_calc
    )
    result['conceptual_coherence'] = conceptual
    
    # 5. 논리 (10점)
    logic_score = 0
    if response.get('method'):
        logic_score += 5
    if response.get('reasoning'):
        logic_score += 5
    
    result['logic'] = {'score': logic_score}
    
    result['total_score'] = (
        accuracy_score +
        calc_score +
        decomp_score +
        conceptual['score'] +
        logic_score
    )
    
    return result


def test_gpt51_single_problem(client, scenario):
    """gpt-5.1 단일 문제 테스트"""
    try:
        start = time.time()
        
        api_params = {
            "model": "gpt-5.1",
            "input": scenario['prompt'],
            "max_output_tokens": 16000,
            "reasoning": {"effort": "medium"}  # high → medium (일관성 향상)
            # 주의: Responses API는 seed 파라미터 미지원
        }
        
        response = client.responses.create(**api_params)
        content = getattr(response, 'output_text', None) or getattr(response, 'output', str(response))
        
        # system_fingerprint 확인 (재현성 보장 여부)
        system_fingerprint = getattr(response, 'system_fingerprint', 'N/A')
        
        elapsed = time.time() - start
        
        # JSON 파싱
        try:
            if '```json' in content:
                json_start = content.find('```json') + 7
                json_end = content.find('```', json_start)
                content = content[json_start:json_end].strip()
            elif '```' in content:
                json_start = content.find('```') + 3
                json_end = content.find('```', json_start)
                content = content[json_start:json_end].strip()
            
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', content, re.DOTALL)
            if json_match:
                content = json_match.group(0)
            
            parsed = json.loads(content)
        except Exception as e:
            parsed = {'parse_error': str(e), 'raw': content[:200]}
        
        return {
            'success': True,
            'elapsed': round(elapsed, 2),
            'response': parsed,
            'system_fingerprint': system_fingerprint
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def main():
    print("=" * 120)
    print("GPT-5.1 전체 테스트 (3개 문제) - 일관성 최적화")
    print("설정: reasoning.effort=medium (high→medium으로 변경)")
    print("주의: Responses API는 seed 파라미터 미지원")
    print("=" * 120)
    print()
    
    client = OpenAI()
    scenarios = get_phase4_scenarios()
    all_results = []
    
    for scenario_idx, scenario in enumerate(scenarios, 1):
        print(f"\n{'='*120}")
        print(f"📋 문제 {scenario_idx}/{len(scenarios)}: {scenario['name']}")
        print(f"   정답: {scenario['expected_value']:,} {scenario['expected_unit']}")
        print(f"{'='*120}\n")
        
        print(f"🔄 gpt-5.1 (reasoning.effort: medium)")
        
        test_result = test_gpt51_single_problem(client, scenario)
        
        if test_result['success']:
            eval_result = evaluate_fermi_response(
                "gpt-5.1",
                test_result['response'],
                scenario['expected_value'],
                scenario['id']  # problem_id 추가
            )
            
            eval_result['elapsed'] = test_result['elapsed']
            eval_result['response'] = test_result['response']
            eval_result['problem'] = scenario['name']
            eval_result['problem_id'] = scenario['id']
            eval_result['system_fingerprint'] = test_result.get('system_fingerprint', 'N/A')
            
            all_results.append(eval_result)
            
            fingerprint = eval_result.get('system_fingerprint', 'N/A')
            fingerprint_short = fingerprint[:12] if isinstance(fingerprint, str) and len(fingerprint) > 12 else fingerprint
            conceptual_score = eval_result.get('conceptual_coherence', {}).get('score', 0)
            print(f"   ✅ {eval_result['value']:,} {eval_result['unit']} | 총점: {eval_result['total_score']}/100 (연결성: {eval_result['calculation_connectivity']['score']}/50, 개념: {conceptual_score}/15) | {eval_result['elapsed']}초")
        else:
            print(f"   ❌ 오류: {test_result['error'][:100]}")
        
        time.sleep(2)
    
    # 최종 결과
    print("\n" + "=" * 120)
    print("🏆 GPT-5.1 최종 결과")
    print("=" * 120)
    print()
    
    if all_results:
        avg_total = sum(r['total_score'] for r in all_results) / len(all_results)
        avg_accuracy = sum(r['accuracy']['score'] for r in all_results) / len(all_results)
        avg_connectivity = sum(r['calculation_connectivity']['score'] for r in all_results) / len(all_results)
        avg_decomp = sum(r['decomposition']['score'] for r in all_results) / len(all_results)
        avg_conceptual = sum(r['conceptual_coherence']['score'] for r in all_results) / len(all_results)
        avg_logic = sum(r['logic']['score'] for r in all_results) / len(all_results)
        
        print(f"평균 총점:    {avg_total:.1f}/100")
        print(f"평균 정확도:  {avg_accuracy:.1f}/25")
        print(f"평균 연결성:  {avg_connectivity:.1f}/50")
        print(f"평균 개념:    {avg_conceptual:.1f}/15 ⭐ 신규")
        print(f"평균 분해:    {avg_decomp:.1f}/10")
        print(f"평균 논리:    {avg_logic:.1f}/10")
        
        print("\n문제별 점수:")
        for r in all_results:
            conceptual_score = r.get('conceptual_coherence', {}).get('score', 0)
            print(f"  - {r['problem']}: {r['total_score']}/100 (개념: {conceptual_score}/15)")
        
        # 결과 저장
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"gpt51_complete_{timestamp}.json"
        
        output_data = {
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'model': 'gpt-5.1',
                'reasoning_effort': 'medium',
                'optimization': 'consistency (medium effort, no seed support in Responses API)',
                'problems_completed': len(all_results),
                'system_fingerprints': [r.get('system_fingerprint', 'N/A') for r in all_results]
            },
            'summary': {
                'avg_total': avg_total,
                'avg_accuracy': avg_accuracy,
                'avg_connectivity': avg_connectivity,
                'avg_conceptual': avg_conceptual,
                'avg_decomp': avg_decomp,
                'avg_logic': avg_logic
            },
            'results': all_results
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 결과 저장: {output_file}")
    
    print("\n🎉 GPT-5.1 테스트 완료!")


if __name__ == "__main__":
    main()

