#!/usr/bin/env python3
"""
개선된 Fermi 추정 평가 - 계산식 연결 필수
분해 값들이 최종 추정값으로 어떻게 계산되는지 명확히 요구
"""

import sys
import os
import time
import json
from datetime import datetime
import math
import re

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()


# =====================================
# 개선된 Fermi 문제 (계산식 포함)
# =====================================

FERMI_PROBLEM = {
    'name': '한국 전체 사업자 수',
    'ground_truth': 7837000,
    'unit': '개',
    
    # AI의 올바른 Fermi 분해 (계산식 명시)
    'ai_baseline': {
        'estimate': 6036000,
        'decomposition': [
            {
                'step': '1. 경제활동인구',
                'value': 20300000,
                'calculation': '5200만 × 0.60 × 0.65',
                'reasoning': '한국 인구 5200만, 경제활동가능인구 60%, 참가율 65%'
            },
            {
                'step': '2. 자영업자 수',
                'value': 4060000,
                'calculation': '20300000 × 0.20',
                'reasoning': '경제활동인구의 20%가 자영업'
            },
            {
                'step': '3. 법인 사업자 수',
                'value': 970000,
                'calculation': '(20300000 - 4060000) / 20 × 1.2',
                'reasoning': '근로자 1624만명 / 평균 20명 × 다중사업장 보정 1.2'
            },
            {
                'step': '4. 총 사업자 수',
                'value': 6036000,
                'calculation': '(4060000 + 970000) × 1.2',
                'reasoning': '자영업 + 법인 × 휴업/다중등록 보정'
            }
        ],
        'final_formula': '[(인구 × 경활비율 × 참가율 × 자영비율) + (근로자 / 기업규모 × 보정)] × 휴업보정',
        'calculation_chain': [
            '5200만 × 0.6 × 0.65 = 2030만 (경제활동인구)',
            '2030만 × 0.2 = 406만 (자영업자)',
            '(2030만 - 406만) / 20 × 1.2 = 97만 (법인)',
            '(406만 + 97만) × 1.2 = 603.6만 ≈ 600만'
        ]
    },
    
    'prompt': '''한국 전체 사업자 수를 추정하세요.

⚠️ 중요: 각 분해 단계의 숫자들이 최종 추정값으로 어떻게 계산되는지 명확히 제시해야 합니다.

힌트:
- 한국 인구, 경제활동인구 고려
- 자영업자, 법인 사업자 구분
- 다중 사업자등록 가능성 고려

반드시 다음 JSON 형식으로만 응답하세요:
{
    "value": <최종_추정값>,
    "unit": "개",
    "confidence": <0.3-0.7>,
    "method": "접근 방법",
    "decomposition": [
        {
            "step": "단계명",
            "value": <이 단계의 값>,
            "calculation": "이 값을 계산한 수식 (예: 5200만 × 0.6)",
            "reasoning": "가정 및 근거"
        }
    ],
    "final_calculation": "분해 값들을 조합하여 최종값을 계산한 수식 (예: step2 + step3)",
    "calculation_verification": "최종 계산 검증 (예: 406만 + 97만 = 503만 ≈ 500만)"
}

예시:
{
    "value": 500,
    "decomposition": [
        {"step": "A", "value": 100, "calculation": "1000 / 10"},
        {"step": "B", "value": 5, "calculation": "10 / 2"}
    ],
    "final_calculation": "A × B = 100 × 5 = 500",
    "calculation_verification": "100 × 5 = 500 ✓"
}'''
}


def verify_calculation_chain(decomp, final_value, final_calc, calc_verify):
    """
    분해 값들과 최종값의 계산 연결성 검증
    반환: (점수, 검증 결과 설명)
    """
    if not isinstance(decomp, list) or len(decomp) == 0:
        return 0, "분해 없음"
    
    if not final_calc:
        return 0, "최종 계산식 누락"
    
    score = 0
    details = []
    
    # 1. 각 단계에 calculation 필드 있는지 (10점)
    calc_present = sum(1 for step in decomp if 'calculation' in step and step['calculation'])
    calc_score = min(10, (calc_present / len(decomp)) * 10)
    score += calc_score
    details.append(f"단계별 계산식: {calc_present}/{len(decomp)} 존재 ({calc_score:.0f}점)")
    
    # 2. final_calculation에 step 값들이 참조되는지 (10점)
    final_calc_lower = final_calc.lower()
    step_values = [step.get('value', 0) for step in decomp if 'value' in step]
    
    referenced_count = 0
    for val in step_values:
        if val and (str(val) in final_calc or str(int(val)) in final_calc):
            referenced_count += 1
    
    if referenced_count >= 2:  # 최소 2개 단계 값 참조
        ref_score = 10
        details.append(f"✅ 최종 계산식이 분해 값 참조 ({referenced_count}개)")
    else:
        ref_score = 3
        details.append(f"❌ 최종 계산식이 분해 값 미참조")
    
    score += ref_score
    
    # 3. 계산 검증 시도 (20점)
    try:
        # 단순 산술식 평가 시도
        # 위험: eval 사용, 실제 프로덕션에서는 더 안전한 방법 필요
        
        # 분해 값들로 최종값 재계산 시도
        values = [step.get('value', 0) for step in decomp if 'value' in step]
        
        if len(values) >= 2 and final_value > 0:
            # 다양한 조합 시도
            combinations = [
                sum(values),  # 합
                sum(values[:-1]) if len(values) > 1 else 0,  # 마지막 제외 합
                values[-1] if values else 0,  # 마지막 값
            ]
            
            # 곱셈 조합
            if len(values) >= 2:
                product = 1
                for v in values[:3]:  # 최대 3개까지만
                    if v > 0 and v < 1000000000:  # 너무 큰 수 제외
                        product *= v
                combinations.append(product)
            
            # 가장 가까운 조합 찾기
            best_match = min(combinations, key=lambda x: abs(x - final_value) if x > 0 else float('inf'))
            
            if best_match > 0:
                error_ratio = abs(best_match - final_value) / final_value
                
                if error_ratio < 0.01:  # 1% 이내
                    calc_score = 20
                    details.append(f"✅ 계산 일치: {best_match:,.0f} ≈ {final_value:,.0f}")
                elif error_ratio < 0.1:  # 10% 이내
                    calc_score = 15
                    details.append(f"✅ 계산 근접: {best_match:,.0f} ≈ {final_value:,.0f} (오차 {error_ratio*100:.1f}%)")
                elif error_ratio < 0.5:  # 50% 이내
                    calc_score = 10
                    details.append(f"⚠️ 계산 부분 일치: {best_match:,.0f} vs {final_value:,.0f}")
                else:
                    calc_score = 5
                    details.append(f"❌ 계산 불일치: {best_match:,.0f} vs {final_value:,.0f}")
            else:
                calc_score = 0
                details.append("❌ 계산 검증 실패")
        else:
            calc_score = 0
            details.append("❌ 검증 불가 (값 부족)")
        
        score += calc_score
        
    except Exception as e:
        details.append(f"⚠️ 계산 검증 오류: {str(e)[:50]}")
    
    return min(score, 40), details


def evaluate_model_response(model_name, response, ground_truth, ai_baseline):
    """
    개선된 평가: 계산 연결성 중심
    
    100점 만점:
    - 정확도: 30점
    - 계산 연결성: 40점 (핵심!)
    - 분해 합리성: 20점
    - 논리 일관성: 10점
    """
    result = {
        'model': model_name,
        'value': response.get('value', 0),
        'unit': response.get('unit', ''),
        'ground_truth': ground_truth
    }
    
    # 값 타입 체크
    if isinstance(result['value'], dict):
        result['value'] = 0
    elif not isinstance(result['value'], (int, float)):
        result['value'] = 0
    
    # 1. 정확도 (30점)
    if result['value'] > 0 and ground_truth > 0:
        error = abs(math.log10(result['value']) - math.log10(ground_truth))
        
        if error < 0.05:  # 5% 이내
            accuracy_score = 30
        elif error < 0.1:  # 25% 이내
            accuracy_score = 25
        elif error < 0.3:  # 2배 이내
            accuracy_score = 20
        elif error < 0.5:  # 3배 이내
            accuracy_score = 15
        elif error < 1.0:  # 10배 이내
            accuracy_score = 10
        else:
            accuracy_score = 5
        
        error_pct = (10**error - 1) * 100
    else:
        accuracy_score = 0
        error_pct = 999
    
    result['accuracy'] = {
        'score': accuracy_score,
        'error_pct': error_pct
    }
    
    # 2. 계산 연결성 (40점) - 가장 중요!
    calc_score, calc_details = verify_calculation_chain(
        response.get('decomposition', []),
        result['value'],
        response.get('final_calculation', ''),
        response.get('calculation_verification', '')
    )
    
    result['calculation_connectivity'] = {
        'score': calc_score,
        'details': calc_details
    }
    
    # 3. 분해 합리성 (20점)
    decomp = response.get('decomposition', [])
    if isinstance(decomp, list) and len(decomp) >= 3:
        decomp_score = 10
        
        # 각 단계 완성도
        complete_count = sum(1 for step in decomp 
                           if all(k in step for k in ['step', 'value', 'calculation', 'reasoning']))
        decomp_score += min(10, (complete_count / len(decomp)) * 10)
    else:
        decomp_score = 0
    
    result['decomposition_quality'] = {
        'score': decomp_score,
        'step_count': len(decomp) if isinstance(decomp, list) else 0
    }
    
    # 4. 논리 일관성 (10점)
    logic_score = 0
    if response.get('method'):
        logic_score += 5
    if response.get('reasoning'):
        logic_score += 5
    
    result['logic'] = {
        'score': logic_score
    }
    
    # 총점
    result['total_score'] = (
        accuracy_score +
        calc_score +
        decomp_score +
        logic_score
    )
    
    return result


def test_model_on_fermi(client, model, api_type, problem_def, config=None):
    """모델 테스트"""
    
    prompt = problem_def['prompt']
    
    try:
        start = time.time()
        
        if api_type == 'responses':
            api_params = {
                "model": model,
                "input": prompt,
            }
            
            if config:
                api_params["reasoning"] = config.get("reasoning", {"effort": "medium"})
                api_params["text"] = config.get("text", {"verbosity": "low"})
            
            response = client.responses.create(**api_params)
            
            if hasattr(response, 'output_text'):
                content = response.output_text
            elif hasattr(response, 'output'):
                content = response.output
            else:
                content = str(response)
            
        else:
            api_params = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
            }
            
            if config and config.get('reasoning_effort'):
                api_params["reasoning_effort"] = config['reasoning_effort']
            
            response = client.chat.completions.create(**api_params)
            content = response.choices[0].message.content
        
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
            parsed = {'parse_error': str(e)}
        
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


def run_improved_fermi_test():
    """개선된 Fermi 테스트 실행"""
    print("=" * 120)
    print("개선된 Fermi 추정 평가 - 계산식 연결 필수")
    print("=" * 120)
    print()
    
    client = OpenAI()
    
    problem_def = FERMI_PROBLEM
    
    print(f"📋 문제: {problem_def['name']}")
    print(f"   정답: {problem_def['ground_truth']:,} {problem_def['unit']}")
    print()
    
    print("🔍 AI 기준선 (올바른 Fermi 분해):\n")
    print(f"추정값: {problem_def['ai_baseline']['estimate']:,}")
    print("\n계산 과정:")
    for calc in problem_def['ai_baseline']['calculation_chain']:
        print(f"  {calc}")
    print(f"\n최종 공식: {problem_def['ai_baseline']['final_formula']}")
    print()
    
    # 테스트 모델
    test_configs = [
        ('gpt-4.1-nano', 'chat', None),
        ('gpt-4o-mini', 'chat', None),
        ('gpt-4.1-mini', 'chat', None),
        ('gpt-5.1', 'chat', {'reasoning_effort': 'medium'}),
        ('gpt-5.1', 'responses', {
            'reasoning': {'effort': 'medium'},
            'text': {'verbosity': 'low'}
        }),
    ]
    
    results = []
    
    print("=" * 120)
    print("모델 테스트 시작")
    print("=" * 120)
    print()
    
    for model, api_type, config in test_configs:
        config_name = f"{model} ({api_type})"
        print(f"테스트: {config_name}")
        
        test_result = test_model_on_fermi(client, model, api_type, problem_def, config)
        
        if test_result['success']:
            eval_result = evaluate_model_response(
                config_name,
                test_result['response'],
                problem_def['ground_truth'],
                problem_def['ai_baseline']
            )
            
            eval_result['response'] = test_result['response']
            results.append(eval_result)
            
            print(f"  ✅ 완료 ({test_result['elapsed']}초)")
            print(f"     추정값: {eval_result['value']:,}")
            print(f"     정확도: {eval_result['accuracy']['score']}/30")
            print(f"     🔗 계산 연결성: {eval_result['calculation_connectivity']['score']}/40")
            print(f"     분해 품질: {eval_result['decomposition_quality']['score']}/20")
            print(f"     논리: {eval_result['logic']['score']}/10")
            print(f"     총점: {eval_result['total_score']}/100")
        else:
            print(f"  ❌ 오류: {test_result['error'][:50]}")
        
        print()
        time.sleep(2)
    
    # 결과 분석
    print("=" * 120)
    print("🏆 최종 결과")
    print("=" * 120)
    print()
    
    results.sort(key=lambda x: x['total_score'], reverse=True)
    
    print(f"{'순위':<4} | {'모델':<30} | {'추정값':<15} | {'총점':<8} | {'정확도':<8} | {'연결성':<8} | {'분해':<8} | {'논리':<8}")
    print("-" * 120)
    
    for i, r in enumerate(results, 1):
        marker = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "  "
        print(f"{marker}{i:<3} | {r['model']:<30} | {r['value']:>13,}{r['unit']:<2} | {r['total_score']:>6}/100 | {r['accuracy']['score']:>6}/30 | {r['calculation_connectivity']['score']:>6}/40 | {r['decomposition_quality']['score']:>6}/20 | {r['logic']['score']:>6}/10")
    
    # 상세 분석
    print("\n\n" + "=" * 120)
    print("📋 상세 분석")
    print("=" * 120)
    
    for r in results:
        print(f"\n{'='*120}")
        print(f"{r['model']}")
        print(f"{'='*120}\n")
        
        print(f"**추정값**: {r['value']:,} {r['unit']}")
        print(f"**총점**: {r['total_score']}/100\n")
        
        # 정확도
        print(f"**정확도** ({r['accuracy']['score']}/30):")
        if r['accuracy']['score'] > 0:
            print(f"  오차: {r['accuracy']['error_pct']:.1f}%\n")
        else:
            print("  값 없음\n")
        
        # 계산 연결성 (핵심!)
        print(f"**🔗 계산 연결성** ({r['calculation_connectivity']['score']}/40):")
        for detail in r['calculation_connectivity']['details']:
            print(f"  {detail}")
        print()
        
        # 분해
        print(f"**분해 품질** ({r['decomposition_quality']['score']}/20):")
        print(f"  단계 수: {r['decomposition_quality']['step_count']}\n")
        
        # 실제 응답
        if 'response' in r:
            resp = r['response']
            
            if 'decomposition' in resp and isinstance(resp['decomposition'], list):
                print("**분해 과정**:")
                for i, step in enumerate(resp['decomposition'][:4], 1):
                    print(f"  {i}. {step.get('step', 'N/A')}")
                    print(f"     값: {step.get('value', 'N/A')}")
                    print(f"     계산: {step.get('calculation', 'N/A')}")
                print()
            
            if 'final_calculation' in resp:
                print(f"**최종 계산식**: {resp['final_calculation']}")
            else:
                print("**최종 계산식**: ❌ 누락")
            print()
    
    # 저장
    output_file = f"fermi_improved_evaluation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'evaluation_focus': '계산식 연결성',
                'scoring': {
                    'accuracy': '30점',
                    'calculation_connectivity': '40점 (핵심!)',
                    'decomposition': '20점',
                    'logic': '10점'
                }
            },
            'problem': problem_def,
            'results': results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 결과 저장: {output_file}")
    print("\n🎉 테스트 완료!")


if __name__ == "__main__":
    run_improved_fermi_test()


