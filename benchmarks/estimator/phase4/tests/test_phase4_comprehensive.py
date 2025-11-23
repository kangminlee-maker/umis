#!/usr/bin/env python3
"""
Phase 4 종합 모델 테스트 - Few-shot Fermi 추정
실제 통계 기반 3개 문제 (한국 사업자 수, 서울 인구, 커피전문점)
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
    
    # Few-shot 예시
    fewshot_example = '''
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
올바른 Fermi 추정 예시: 서울시 택시 수

{
    "value": 70000,
    "unit": "대",
    "confidence": 0.6,
    "method": "bottom-up",
    "decomposition": [
        {
            "step": "1. 서울 인구",
            "value": 10000000,
            "calculation": "약 1000만명으로 가정",
            "reasoning": "서울 통계 기준"
        },
        {
            "step": "2. 1인당 연간 택시 이용 횟수",
            "value": 20,
            "calculation": "월 1-2회 × 12개월 = 20회",
            "reasoning": "대중교통 중심 도시"
        },
        {
            "step": "3. 연간 총 이용 횟수",
            "value": 200000000,
            "calculation": "10000000 × 20 = 200000000",
            "reasoning": "step1 × step2"
        },
        {
            "step": "4. 택시 1대당 연간 운행 횟수",
            "value": 3000,
            "calculation": "일 10회 × 300일 = 3000",
            "reasoning": "2교대 운행 가정"
        },
        {
            "step": "5. 필요한 택시 수",
            "value": 66667,
            "calculation": "200000000 / 3000 = 66667",
            "reasoning": "step3 / step4"
        }
    ],
    "final_calculation": "step3 / step4 = 200000000 / 3000 = 66667 ≈ 70000",
    "calculation_verification": "인구(1000만) × 이용횟수(20) / 택시당운행(3000) = 66667 ✓"
}

핵심 규칙:
1. 각 step의 value는 이전 step들로부터 명확히 계산되어야 함
2. final_calculation은 step들의 value를 조합한 수식이어야 함
3. 계산을 검증할 수 있어야 함
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
'''
    
    return [
        {
            'id': 'phase4_korean_businesses',
            'name': 'Phase 4 - 한국 전체 사업자 수',
            'phase': 4,
            'prompt': f'''{fewshot_example}

이제 실제 문제를 풀어주세요:

문제: 한국 전체 사업자 수를 추정하세요.

⚠️ 중요: 각 분해 단계의 숫자들이 최종 추정값으로 어떻게 계산되는지 명확히 제시해야 합니다.

힌트:
- 한국 인구, 경제활동인구 고려
- 자영업자, 법인 사업자 구분
- 다중 사업자등록 가능성 고려

반드시 다음 JSON 형식으로만 응답하세요:
{{
    "value": <최종_추정값_숫자만>,
    "unit": "개",
    "confidence": <0.3-0.7>,
    "method": "bottom-up 또는 top-down",
    "decomposition": [
        {{
            "step": "단계 번호와 설명",
            "value": <이_단계의_숫자값>,
            "calculation": "이 값을 어떻게 계산했는지 (예: 5200만 × 0.6)",
            "reasoning": "가정 및 근거"
        }}
    ],
    "final_calculation": "분해 값들을 조합하여 최종값을 계산한 수식. 반드시 step의 값들을 사용할 것",
    "calculation_verification": "위 계산이 맞는지 검증 (예: step2 + step3 = 400만 + 100만 = 500만 ✓)"
}}

주의:
- value는 반드시 숫자만 입력 (단위 제외)
- final_calculation은 실제 decomposition의 value들을 참조해야 함
- calculation_verification으로 계산이 맞는지 확인할 것''',
            'expected_value': 7837000,
            'expected_unit': '개',
        },
        {
            'id': 'phase4_seoul_population',
            'name': 'Phase 4 - 서울시 인구',
            'phase': 4,
            'prompt': f'''{fewshot_example}

이제 실제 문제:

문제: 서울시 인구를 추정하세요.

힌트:
- 한국 전체 인구 대비 서울 비중
- 수도권 집중도 고려
- 또는 면적 기반 접근

반드시 같은 JSON 형식으로 응답하세요 (value는 숫자만, final_calculation 필수)''',
            'expected_value': 9668465,
            'expected_unit': '명',
        },
        {
            'id': 'phase4_coffee_shops',
            'name': 'Phase 4 - 한국 커피 전문점 수',
            'phase': 4,
            'prompt': f'''먼저 올바른 Fermi 추정 예시:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
예시: 서울시 택시 수

{{
    "value": 70000,
    "decomposition": [
        {{"step": "1. 인구", "value": 10000000, "calculation": "1000만"}},
        {{"step": "2. 이용횟수", "value": 20, "calculation": "월 2회 × 12"}},
        {{"step": "3. 총이용", "value": 200000000, "calculation": "step1 × step2"}},
        {{"step": "4. 택시운행", "value": 3000, "calculation": "일 10회 × 300일"}},
        {{"step": "5. 대수", "value": 66667, "calculation": "step3 / step4"}}
    ],
    "final_calculation": "step3 / step4 = 2억 / 3000 = 66667",
    "calculation_verification": "계산 확인 완료 ✓"
}}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

문제: 한국 커피 전문점 수를 추정하세요.

힌트:
- 커피 소비 인구
- 점포당 고객 수
- 브랜드 경쟁 및 상권 중복

반드시 같은 형식으로 응답 (final_calculation 필수)''',
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
    
    # 다양한 조합 시도
    results = []
    
    # 1. 마지막 값 (보통 최종 단계)
    if values[-1] > 0:
        error = abs(values[-1] - final_value) / max(final_value, 1)
        results.append(('마지막 단계', values[-1], error))
    
    # 2. 합계
    total = sum(values)
    if total > 0:
        error = abs(total - final_value) / max(final_value, 1)
        results.append(('모든 단계 합', total, error))
    
    # 3. 마지막 2개 합
    if len(values) >= 2:
        last_two = sum(values[-2:])
        if last_two > 0:
            error = abs(last_two - final_value) / max(final_value, 1)
            results.append(('마지막 2단계 합', last_two, error))
    
    # 가장 오차가 작은 것
    if results:
        best = min(results, key=lambda x: x[2])
        return best[1], f"{best[0]}: {best[1]:,.0f} (오차 {best[2]*100:.1f}%)"
    
    return None, "계산 불가"


def evaluate_fermi_response(model_name, response, expected_value):
    """
    Fermi 추정 평가
    
    100점 만점:
    - 정확도: 25점
    - 계산 연결성: 50점 (가장 중요!)
    - 분해 품질: 15점
    - 논리: 10점
    """
    result = {
        'model': model_name,
        'value': response.get('value', 0),
        'unit': response.get('unit', ''),
        'expected_value': expected_value
    }
    
    # 값 타입 체크
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
        # 2-1. 각 단계에 calculation 있는지 (10점)
        with_calc = sum(1 for s in decomp if s.get('calculation'))
        calc_ratio = with_calc / len(decomp)
        step_calc_score = calc_ratio * 10
        calc_score += step_calc_score
        calc_details.append(f"단계별 계산식: {with_calc}/{len(decomp)} ({step_calc_score:.0f}점)")
        
        # 2-2. final_calculation 존재 (10점)
        if final_calc:
            calc_score += 10
            calc_details.append(f"✅ 최종 계산식 제공 (10점)")
        else:
            calc_details.append(f"❌ 최종 계산식 누락 (0점)")
        
        # 2-3. calculation_verification 존재 (5점)
        if calc_verify:
            calc_score += 5
            calc_details.append(f"✅ 계산 검증 제공 (5점)")
        
        # 2-4. 자동 계산 검증 (25점)
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
    
    # 3. 분해 품질 (15점)
    if isinstance(decomp, list) and len(decomp) >= 3:
        decomp_score = 5
        complete = sum(1 for s in decomp 
                      if all(k in s for k in ['step', 'value', 'calculation', 'reasoning']))
        decomp_score += min(10, (complete / len(decomp)) * 10)
    else:
        decomp_score = 0
    
    result['decomposition'] = {
        'score': decomp_score,
        'count': len(decomp) if isinstance(decomp, list) else 0
    }
    
    # 4. 논리 (10점)
    logic_score = 0
    if response.get('method'):
        logic_score += 5
    if response.get('reasoning'):
        logic_score += 5
    
    result['logic'] = {'score': logic_score}
    
    # 총점
    result['total_score'] = (
        accuracy_score +
        calc_score +
        decomp_score +
        logic_score
    )
    
    return result


def test_model_responses_api(client, model_name, scenario, reasoning_effort='medium'):
    """Responses API로 모델 테스트"""
    
    try:
        start = time.time()
        
        api_params = {
            "model": model_name,
            "input": scenario['prompt'],
            "reasoning": {"effort": reasoning_effort},
            "text": {"verbosity": "low"}
        }
        
        response = client.responses.create(**api_params)
        content = getattr(response, 'output_text', None) or getattr(response, 'output', str(response))
        
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
            'response': parsed
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def run_phase4_comprehensive_test():
    """Phase 4 종합 테스트 실행"""
    print("=" * 120)
    print("Phase 4 종합 모델 테스트 - Few-shot Fermi 추정")
    print("=" * 120)
    print()
    
    client = OpenAI()
    
    # 테스트 모델 (Tier 1, 2 + gpt-5-pro, gpt-5.1)
    test_config = [
        # Tier 1 (o-series)
        {'model': 'o1', 'effort': 'high', 'tier': 'Tier 1'},
        {'model': 'o1-2024-12-17', 'effort': 'high', 'tier': 'Tier 1'},
        {'model': 'o1-pro', 'effort': 'high', 'tier': 'Pro'},
        {'model': 'o1-pro-2025-03-19', 'effort': 'high', 'tier': 'Pro'},
        {'model': 'o3', 'effort': 'high', 'tier': 'Tier 1'},
        {'model': 'o3-2025-04-16', 'effort': 'high', 'tier': 'Tier 1'},
        {'model': 'o3-mini', 'effort': 'high', 'tier': 'Tier 1'},
        {'model': 'o3-mini-2025-01-31', 'effort': 'high', 'tier': 'Tier 1'},
        {'model': 'o4-mini', 'effort': 'high', 'tier': 'Tier 1'},
        {'model': 'o4-mini-2025-04-16', 'effort': 'high', 'tier': 'Tier 1'},
        
        # Tier 2 (gpt-4.1)
        {'model': 'gpt-4.1', 'effort': 'high', 'tier': 'Tier 2'},
        {'model': 'gpt-4.1-mini', 'effort': 'high', 'tier': 'Tier 2'},
        
        # Premium
        {'model': 'gpt-5-pro', 'effort': 'high', 'tier': 'Premium'},
        {'model': 'gpt-5.1', 'effort': 'high', 'tier': 'Premium'},
    ]
    
    all_results = []
    scenarios = get_phase4_scenarios()
    
    # 각 문제 테스트
    for scenario in scenarios:
        print(f"\n{'='*120}")
        print(f"📋 {scenario['name']}")
        print(f"   정답: {scenario['expected_value']:,} {scenario['expected_unit']}")
        print(f"{'='*120}\n")
        
        problem_results = []
        
        for config in test_config:
            model_name = config['model']
            effort = config['effort']
            tier = config['tier']
            
            print(f"🔄 {model_name} ({tier}, effort={effort})")
            
            test_result = test_model_responses_api(client, model_name, scenario, effort)
            
            if test_result['success']:
                eval_result = evaluate_fermi_response(
                    f"{model_name} ({tier})",
                    test_result['response'],
                    scenario['expected_value']
                )
                
                eval_result['elapsed'] = test_result['elapsed']
                eval_result['response'] = test_result['response']
                eval_result['problem'] = scenario['name']
                eval_result['problem_id'] = scenario['id']
                eval_result['tier'] = tier
                eval_result['reasoning_effort'] = effort
                
                problem_results.append(eval_result)
                all_results.append(eval_result)
                
                print(f"   ✅ {eval_result['value']:,} {eval_result['unit']} | 총점: {eval_result['total_score']}/100 (연결성: {eval_result['calculation_connectivity']['score']}/50)")
            else:
                print(f"   ❌ 오류: {test_result['error'][:80]}")
            
            time.sleep(2)
        
        # 문제별 요약
        print(f"\n📊 {scenario['name']} 순위:\n")
        problem_results.sort(key=lambda x: x['total_score'], reverse=True)
        
        for i, r in enumerate(problem_results, 1):
            marker = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "  "
            print(f"{marker}{i}. {r['model']:<35} {r['total_score']:>3}/100 (정확도: {r['accuracy']['score']}/25, 연결성: {r['calculation_connectivity']['score']}/50)")
        
        print()
    
    # 전체 종합 결과
    print("\n" + "=" * 120)
    print("🏆 최종 종합 순위 (3개 문제 평균)")
    print("=" * 120)
    print()
    
    from collections import defaultdict
    
    by_model = defaultdict(list)
    for r in all_results:
        by_model[r['model']].append(r)
    
    model_averages = []
    for model_name, results in by_model.items():
        avg = {
            'model': model_name,
            'avg_total': sum(r['total_score'] for r in results) / len(results),
            'avg_accuracy': sum(r['accuracy']['score'] for r in results) / len(results),
            'avg_connectivity': sum(r['calculation_connectivity']['score'] for r in results) / len(results),
            'avg_decomp': sum(r['decomposition']['score'] for r in results) / len(results),
            'avg_logic': sum(r['logic']['score'] for r in results) / len(results),
            'count': len(results)
        }
        model_averages.append(avg)
    
    model_averages.sort(key=lambda x: x['avg_total'], reverse=True)
    
    print(f"{'순위':<4} | {'모델':<35} | {'평균':<10} | {'정확도':<10} | {'연결성':<10} | {'분해':<10} | {'논리':<8}")
    print("-" * 120)
    
    for i, m in enumerate(model_averages, 1):
        marker = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "  "
        print(f"{marker}{i:<3} | {m['model']:<35} | {m['avg_total']:>8.1f}/100 | {m['avg_accuracy']:>8.1f}/25 | {m['avg_connectivity']:>8.1f}/50 | {m['avg_decomp']:>8.1f}/15 | {m['avg_logic']:>6.1f}/10")
    
    # 저장
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f"phase4_comprehensive_test_{timestamp}.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'test_type': 'phase4_comprehensive_fewshot',
                'models': len(test_config),
                'problems': len(scenarios),
                'total_tests': len(all_results)
            },
            'problems': {
                s['id']: {
                    'name': s['name'],
                    'expected_value': s['expected_value'],
                    'expected_unit': s['expected_unit']
                } for s in scenarios
            },
            'results': all_results,
            'summary': model_averages
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 결과 저장: {output_file}")
    print("\n🎉 테스트 완료!")


if __name__ == "__main__":
    run_phase4_comprehensive_test()
