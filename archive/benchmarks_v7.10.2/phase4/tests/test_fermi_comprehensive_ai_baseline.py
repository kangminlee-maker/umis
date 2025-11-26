#!/usr/bin/env python3
"""
Fermi 추정 종합 평가 - AI 기준선 비교
Phase 4에서 80점 이상 모델 대상, 3개 실제 데이터 문제 테스트
"""

import sys
import os
import time
import json
from datetime import datetime
import math

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()


# =====================================
# AI 기준선 Fermi 분해 (문서에서)
# =====================================

FERMI_PROBLEMS = {
    'korean_businesses': {
        'name': '한국 전체 사업자 수',
        'ground_truth': 7837000,
        'unit': '개',
        'ai_baseline': {
            'estimate': 6000000,
            'error_rate': 0.23,
            'decomposition': [
                {
                    'step': '경제활동인구',
                    'value': 20300000,
                    'assumption': '인구 5200만 × 60% × 65% = 2030만명'
                },
                {
                    'step': '자영업자 비율',
                    'value': 4060000,
                    'assumption': '경제활동인구의 20% = 406만명'
                },
                {
                    'step': '법인 사업자',
                    'value': 970000,
                    'assumption': '근로자 1624만 / 20명 × 1.2 = 97만개'
                },
                {
                    'step': '총 사업자',
                    'value': 6000000,
                    'assumption': '(406만 + 97만) × 1.2 = 600만개'
                }
            ],
            'strengths': [
                '명확한 4단계 분해',
                '인구 기반 bottom-up',
                '합리적인 가정'
            ],
            'weaknesses': [
                '실제보다 낮게 추정 (23% 오차)',
                '다중 사업자등록 미반영'
            ]
        },
        'prompt': '''한국 전체 사업자 수를 추정하세요.

힌트:
- 한국 인구, 경제활동인구 고려
- 자영업자, 법인 사업자 구분
- 다중 사업자등록 가능성 고려

반드시 다음 JSON 형식으로만 응답하세요:
{
    "value": <추정값>,
    "unit": "개",
    "confidence": <0.3-0.7>,
    "method": "접근 방법",
    "decomposition": [
        {"step": "단계명", "value": <값>, "assumption": "가정", "reasoning": "근거"}
    ],
    "reasoning": "전체 추정 논리"
}'''
    },
    
    'seoul_population': {
        'name': '서울시 인구',
        'ground_truth': 9668465,
        'unit': '명',
        'ai_baseline': {
            'estimate': 8700000,
            'estimate_range': [8000000, 9400000],
            'error_rate': 0.10,
            'decomposition': [
                {
                    'step': '한국 전체 인구',
                    'value': 52000000,
                    'assumption': '한국 인구 5200만명'
                },
                {
                    'step': '수도권 비중',
                    'value': 26000000,
                    'assumption': '수도권 집중도 50% = 2600만명'
                },
                {
                    'step': '서울 비중',
                    'value': 7440000,
                    'assumption': '서울:경기:인천 = 1:2:0.5, 서울 28.6%'
                },
                {
                    'step': '면적 기반 검증',
                    'value': 9360000,
                    'assumption': '서울 605km² × 밀집도 300배'
                }
            ],
            'strengths': [
                '두 가지 방법 제시 (비율 + 면적)',
                '범위 추정으로 불확실성 표현',
                '합리적 추정 (오차 10%)'
            ],
            'weaknesses': [
                '수도권 비율 가정 근거 부족'
            ]
        },
        'prompt': '''서울시 인구를 추정하세요.

힌트:
- 한국 전체 인구 대비 서울 비중
- 수도권 집중도 고려
- 또는 면적 기반 접근

반드시 다음 JSON 형식으로만 응답하세요:
{
    "value": <추정값>,
    "unit": "명",
    "confidence": <0.3-0.7>,
    "method": "접근 방법",
    "decomposition": [
        {"step": "단계명", "value": <값>, "assumption": "가정", "reasoning": "근거"}
    ],
    "reasoning": "전체 추정 논리"
}'''
    },
    
    'coffee_shops': {
        'name': '한국 커피 전문점 수',
        'ground_truth': 100000,
        'unit': '개',
        'ai_baseline': {
            'estimate': 78000,
            'error_rate': 0.22,
            'decomposition': [
                {
                    'step': '커피 소비층',
                    'value': 10400000,
                    'assumption': '20-60세 50% × 정기소비 40% = 1040만명'
                },
                {
                    'step': '점포당 고객',
                    'value': 800,
                    'assumption': '상권 반경 500m, 인구 2000명 × 40% = 800명'
                },
                {
                    'step': '필요 점포',
                    'value': 13000,
                    'assumption': '1040만 / 800 = 13000개'
                },
                {
                    'step': '경쟁 보정',
                    'value': 78000,
                    'assumption': '브랜드 다양성 × 6배 = 78000개'
                }
            ],
            'strengths': [
                '고객 중심 bottom-up',
                '상권 개념 도입',
                '경쟁 보정 고려'
            ],
            'weaknesses': [
                '중복 상권 계수 근거 부족',
                '실제보다 낮게 추정 (22% 오차)'
            ]
        },
        'prompt': '''한국 커피 전문점 수를 추정하세요.

힌트:
- 커피 소비 인구
- 점포당 고객 수
- 브랜드 경쟁 및 상권 중복

반드시 다음 JSON 형식으로만 응답하세요:
{
    "value": <추정값>,
    "unit": "개",
    "confidence": <0.3-0.7>,
    "method": "접근 방법",
    "decomposition": [
        {"step": "단계명", "value": <값>, "assumption": "가정", "reasoning": "근거"}
    ],
    "reasoning": "전체 추정 논리"
}'''
    }
}


def test_model_on_problem(client, model, api_type, problem_id, problem_def, config=None):
    """특정 문제에서 모델 테스트"""
    
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
            
            tokens = {
                'input': getattr(response, 'input_tokens', len(prompt) // 4),
                'output': getattr(response, 'output_tokens', len(content) // 4),
            }
            tokens['total'] = tokens['input'] + tokens['output']
            
        else:
            api_params = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
            }
            
            if config and config.get('reasoning_effort'):
                api_params["reasoning_effort"] = config['reasoning_effort']
            
            response = client.chat.completions.create(**api_params)
            content = response.choices[0].message.content
            
            tokens = {
                'input': response.usage.prompt_tokens,
                'output': response.usage.completion_tokens,
                'total': response.usage.total_tokens
            }
        
        elapsed = time.time() - start
        
        # JSON 파싱
        import re
        
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
            parsed = {'raw': content[:500], 'parse_error': str(e)}
        
        return {
            'success': True,
            'elapsed_seconds': round(elapsed, 2),
            'tokens': tokens,
            'response': parsed,
            'raw_content': content
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def evaluate_accuracy(model_value, ground_truth, ai_baseline_value):
    """
    정확도 평가 (40점)
    - 실제값 대비 오차
    - AI 기준선 대비 비교
    """
    # value가 dict인 경우 처리
    if isinstance(model_value, dict):
        model_value = 0
    
    if not isinstance(model_value, (int, float)) or model_value <= 0 or ground_truth <= 0:
        return {
            'score': 0,
            'details': '유효하지 않은 값'
        }
    
    # 로그 스케일 오차
    model_error = abs(math.log10(model_value) - math.log10(ground_truth))
    ai_error = abs(math.log10(ai_baseline_value) - math.log10(ground_truth))
    
    # 절대 정확도 (25점)
    if model_error < 0.05:  # 5% 이내
        abs_score = 25
    elif model_error < 0.1:  # 25% 이내
        abs_score = 20
    elif model_error < 0.3:  # 2배 이내
        abs_score = 15
    elif model_error < 0.5:  # 3배 이내
        abs_score = 10
    elif model_error < 1.0:  # 10배 이내
        abs_score = 5
    else:
        abs_score = 0
    
    # AI 대비 상대 평가 (15점)
    if model_error < ai_error * 0.5:  # AI보다 2배 정확
        relative_score = 15
    elif model_error < ai_error * 0.8:  # AI보다 1.25배 정확
        relative_score = 12
    elif model_error < ai_error:  # AI보다 정확
        relative_score = 10
    elif model_error < ai_error * 1.5:  # AI와 유사
        relative_score = 7
    else:  # AI보다 부정확
        relative_score = 3
    
    total = abs_score + relative_score
    
    return {
        'score': total,
        'absolute_score': abs_score,
        'relative_score': relative_score,
        'model_error_pct': round((10**model_error - 1) * 100, 1),
        'ai_error_pct': round((10**ai_error - 1) * 100, 1),
        'vs_ai': 'better' if model_error < ai_error else 'worse'
    }


def evaluate_decomposition_quality(decomp, ai_baseline_decomp):
    """
    분해 합리성 평가 (30점)
    - 단계 수 및 구조
    - 가정의 합리성
    - AI 기준선 대비
    """
    if not isinstance(decomp, list) or len(decomp) == 0:
        return {
            'score': 0,
            'details': 'decomposition 없음'
        }
    
    score = 0
    details = []
    
    # 1. 단계 수 (10점)
    ai_steps = len(ai_baseline_decomp)
    model_steps = len(decomp)
    
    if model_steps >= ai_steps:
        step_score = 10
        details.append(f"✅ 단계 충분 ({model_steps}단계, AI: {ai_steps}단계)")
    elif model_steps >= ai_steps * 0.75:
        step_score = 7
        details.append(f"⚠️ 단계 부족 ({model_steps}단계, AI: {ai_steps}단계)")
    else:
        step_score = 3
        details.append(f"❌ 단계 매우 부족 ({model_steps}단계, AI: {ai_steps}단계)")
    
    score += step_score
    
    # 2. 각 단계의 완성도 (20점)
    quality_score = 0
    for step in decomp:
        # 기본 구조 (각 2점)
        if 'step' in step and step['step']:
            quality_score += 2
        if 'assumption' in step and step['assumption']:
            quality_score += 2
        if 'value' in step and step['value']:
            quality_score += 1
    
    max_quality = min(len(decomp), 4) * 5
    quality_score = min(quality_score, 20)
    score += quality_score
    
    details.append(f"각 단계 완성도: {quality_score}/20")
    
    return {
        'score': min(score, 30),
        'details': details
    }


def evaluate_logic_coherence(decomp, final_value, method):
    """
    목표 정의 근접성 평가 (30점)
    - 계산 로직 일관성
    - 방법론 적절성
    """
    if not isinstance(decomp, list) or len(decomp) == 0:
        return {
            'score': 0,
            'details': '분해 없음'
        }
    
    score = 0
    details = []
    
    # 1. 계산 일관성 (20점)
    try:
        values = [step.get('value', 0) for step in decomp if 'value' in step and step['value']]
        
        if len(values) >= 2 and final_value > 0:
            # 곱셈 또는 합산 체크
            product = 1
            total_sum = 0
            
            for v in values:
                if v > 0:
                    product *= v
                    total_sum += v
            
            # 다양한 단위 조정 시도
            test_values = [
                product,
                product / 10000,
                product / 100000000,
                total_sum,
                values[-1] if values else 0
            ]
            
            best_match = min([
                abs(math.log10(tv / final_value)) if tv > 0 and final_value > 0 else 999
                for tv in test_values
            ])
            
            if best_match < 0.1:  # 25% 이내
                score += 20
                details.append("✅ 계산 로직 완벽")
            elif best_match < 0.3:  # 2배 이내
                score += 15
                details.append("✅ 계산 로직 양호")
            elif best_match < 1.0:  # 10배 이내
                score += 10
                details.append("⚠️ 계산 로직 부분 일치")
            else:
                score += 5
                details.append("❌ 계산 로직 불일치")
    except:
        details.append("⚠️ 계산 검증 실패")
    
    # 2. 방법론 명시 (10점)
    if method and method.lower() in ['top-down', 'bottom-up', 'hybrid']:
        score += 10
        details.append(f"✅ 방법론 명시: {method}")
    else:
        score += 5
        details.append("⚠️ 방법론 불명확")
    
    return {
        'score': min(score, 30),
        'details': details
    }


def comprehensive_evaluate(model_name, response, problem_def):
    """종합 평가"""
    
    ground_truth = problem_def['ground_truth']
    ai_baseline = problem_def['ai_baseline']
    
    result = {
        'model': model_name,
        'problem': problem_def['name'],
        'value': response.get('value', 0),
        'unit': response.get('unit', ''),
        'ground_truth': ground_truth
    }
    
    # 1. 정확도 (40점)
    accuracy = evaluate_accuracy(
        response.get('value', 0),
        ground_truth,
        ai_baseline['estimate']
    )
    result['accuracy'] = accuracy
    
    # 2. 분해 합리성 (30점)
    decomp_quality = evaluate_decomposition_quality(
        response.get('decomposition', []),
        ai_baseline['decomposition']
    )
    result['decomposition_quality'] = decomp_quality
    
    # 3. 목표 근접성 (30점)
    logic = evaluate_logic_coherence(
        response.get('decomposition', []),
        response.get('value', 0),
        response.get('method', '')
    )
    result['logic_coherence'] = logic
    
    # 총점
    result['total_score'] = (
        accuracy['score'] +
        decomp_quality['score'] +
        logic['score']
    )
    
    return result


def run_comprehensive_fermi_test():
    """전체 테스트 실행"""
    print("=" * 120)
    print("Fermi 추정 종합 평가 - AI 기준선 비교")
    print("Phase 4에서 80점 이상 모델 × 3개 실제 데이터 문제")
    print("=" * 120)
    print()
    
    client = OpenAI()
    
    # 테스트 모델 (Phase 4에서 80점 이상)
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
    
    all_results = []
    
    # 각 문제에 대해 테스트
    for problem_id, problem_def in FERMI_PROBLEMS.items():
        print(f"\n{'='*120}")
        print(f"📋 문제: {problem_def['name']}")
        print(f"   정답: {problem_def['ground_truth']:,} {problem_def['unit']}")
        print(f"   AI 추정: {problem_def['ai_baseline']['estimate']:,} {problem_def['unit']} (오차: {problem_def['ai_baseline']['error_rate']*100:.1f}%)")
        print(f"{'='*120}\n")
        
        problem_results = []
        
        for model, api_type, config in test_configs:
            config_name = f"{model} ({api_type})"
            print(f"테스트: {config_name}")
            
            test_result = test_model_on_problem(
                client, model, api_type, problem_id, problem_def, config
            )
            
            if test_result['success']:
                response = test_result['response']
                
                # value 타입 체크 및 보정
                if isinstance(response.get('value'), dict):
                    # dict인 경우 0으로 처리
                    response['value'] = 0
                elif not isinstance(response.get('value'), (int, float)):
                    response['value'] = 0
                
                # 평가
                eval_result = comprehensive_evaluate(
                    config_name, response, problem_def
                )
                
                eval_result['test_info'] = {
                    'elapsed': test_result['elapsed_seconds'],
                    'tokens': test_result['tokens']
                }
                eval_result['raw_response'] = response
                
                problem_results.append(eval_result)
                all_results.append(eval_result)
                
                print(f"  ✅ 완료")
                print(f"     추정값: {response.get('value', 0):,} {response.get('unit', '')}")
                print(f"     정확도: {eval_result['accuracy']['score']}/40")
                print(f"     분해 품질: {eval_result['decomposition_quality']['score']}/30")
                print(f"     논리 일관성: {eval_result['logic_coherence']['score']}/30")
                print(f"     총점: {eval_result['total_score']}/100")
            else:
                print(f"  ❌ 오류: {test_result['error'][:50]}")
            
            print()
            time.sleep(2)
        
        # 문제별 요약
        if problem_results:
            print(f"\n📊 {problem_def['name']} 결과 요약\n")
            problem_results.sort(key=lambda x: x['total_score'], reverse=True)
            
            print(f"{'순위':<4} | {'모델':<30} | {'추정값':<15} | {'총점':<8} | {'정확도':<8} | {'분해':<8} | {'논리':<8}")
            print("-" * 120)
            
            for i, r in enumerate(problem_results, 1):
                marker = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "  "
                print(f"{marker}{i:<3} | {r['model']:<30} | {r['value']:>13,}{r['unit']:<2} | {r['total_score']:>6}/100 | {r['accuracy']['score']:>6}/40 | {r['decomposition_quality']['score']:>6}/30 | {r['logic_coherence']['score']:>6}/30")
    
    # 최종 종합 결과
    print("\n\n" + "=" * 120)
    print("🏆 최종 종합 결과 (3개 문제 평균)")
    print("=" * 120)
    print()
    
    # 모델별 평균 계산
    from collections import defaultdict
    
    by_model = defaultdict(list)
    for r in all_results:
        by_model[r['model']].append(r)
    
    model_averages = []
    for model_name, results in by_model.items():
        avg_score = sum(r['total_score'] for r in results) / len(results)
        avg_accuracy = sum(r['accuracy']['score'] for r in results) / len(results)
        avg_decomp = sum(r['decomposition_quality']['score'] for r in results) / len(results)
        avg_logic = sum(r['logic_coherence']['score'] for r in results) / len(results)
        
        model_averages.append({
            'model': model_name,
            'avg_total': avg_score,
            'avg_accuracy': avg_accuracy,
            'avg_decomp': avg_decomp,
            'avg_logic': avg_logic,
            'results': results
        })
    
    model_averages.sort(key=lambda x: x['avg_total'], reverse=True)
    
    print(f"{'순위':<4} | {'모델':<30} | {'평균 총점':<10} | {'정확도':<10} | {'분해':<10} | {'논리':<10}")
    print("-" * 120)
    
    for i, m in enumerate(model_averages, 1):
        marker = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "  "
        print(f"{marker}{i:<3} | {m['model']:<30} | {m['avg_total']:>8.1f}/100 | {m['avg_accuracy']:>8.1f}/40 | {m['avg_decomp']:>8.1f}/30 | {m['avg_logic']:>8.1f}/30")
    
    # 상세 문서 저장
    output_file = f"fermi_comprehensive_evaluation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'test_type': 'fermi_comprehensive_ai_baseline',
                'models_tested': len(test_configs),
                'problems': list(FERMI_PROBLEMS.keys()),
                'evaluation_criteria': {
                    'accuracy': '40점 (절대 25점 + 상대 15점)',
                    'decomposition': '30점 (구조 및 합리성)',
                    'logic': '30점 (계산 일관성 + 방법론)'
                }
            },
            'problems': FERMI_PROBLEMS,
            'results': all_results,
            'summary': {
                'by_model': model_averages
            }
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n\n✅ 결과 저장: {output_file}")
    
    # 상세 분석 문서 생성
    generate_detailed_report(all_results, model_averages, FERMI_PROBLEMS)
    
    print("\n🎉 테스트 완료!")


def generate_detailed_report(all_results, model_averages, problems):
    """상세 분석 마크다운 문서 생성"""
    
    report_file = f"docs/FERMI_TEST_DETAILED_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# Fermi 추정 종합 평가 - 상세 보고서\n\n")
        f.write(f"**작성일**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")
        
        # 개요
        f.write("## 📋 개요\n\n")
        f.write(f"- **테스트 모델**: {len(model_averages)}개\n")
        f.write(f"- **문제 수**: {len(problems)}개\n")
        f.write("- **평가 방식**: AI 기준선 비교\n\n")
        
        # 문제별 상세 결과
        for problem_id, problem_def in problems.items():
            f.write(f"\n## 🎯 문제: {problem_def['name']}\n\n")
            f.write(f"**정답**: {problem_def['ground_truth']:,} {problem_def['unit']}\n\n")
            
            # AI 기준선
            ai = problem_def['ai_baseline']
            f.write(f"### AI 기준선 (Assistant)\n\n")
            f.write(f"- **추정값**: {ai['estimate']:,} {problem_def['unit']}\n")
            f.write(f"- **오차율**: {ai['error_rate']*100:.1f}%\n\n")
            
            f.write("**분해 과정**:\n")
            for i, step in enumerate(ai['decomposition'], 1):
                f.write(f"{i}. {step['step']}: {step['value']:,}\n")
                f.write(f"   - 가정: {step['assumption']}\n")
            
            f.write("\n")
            
            # 모델별 결과
            problem_results = [r for r in all_results if r['problem'] == problem_def['name']]
            problem_results.sort(key=lambda x: x['total_score'], reverse=True)
            
            f.write(f"### 모델 결과\n\n")
            f.write(f"| 순위 | 모델 | 추정값 | 오차 | 총점 | 정확도 | 분해 | 논리 |\n")
            f.write(f"|------|------|--------|------|------|--------|------|------|\n")
            
            for i, r in enumerate(problem_results, 1):
                error_pct = r['accuracy'].get('model_error_pct', 0) if r['accuracy']['score'] > 0 else 999
                f.write(f"| {i} | {r['model']} | {r['value']:,} | {error_pct:.1f}% | {r['total_score']}/100 | {r['accuracy']['score']}/40 | {r['decomposition_quality']['score']}/30 | {r['logic_coherence']['score']}/30 |\n")
            
            f.write("\n#### 상세 분석\n\n")
            
            for r in problem_results:
                f.write(f"**{r['model']}**\n\n")
                f.write(f"- 추정값: {r['value']:,} {r['unit']}\n")
                f.write(f"- 총점: {r['total_score']}/100\n\n")
                
                # 정확도
                acc = r['accuracy']
                f.write(f"**정확도** ({acc['score']}/40):\n")
                f.write(f"- 절대 오차: {acc['model_error_pct']:.1f}% (AI: {acc['ai_error_pct']:.1f}%)\n")
                f.write(f"- AI 대비: {acc['vs_ai']}\n\n")
                
                # 분해
                decomp = r['decomposition_quality']
                f.write(f"**분해 합리성** ({decomp['score']}/30):\n")
                for detail in decomp['details']:
                    f.write(f"- {detail}\n")
                f.write("\n")
                
                # 논리
                logic = r['logic_coherence']
                f.write(f"**논리 일관성** ({logic['score']}/30):\n")
                for detail in logic['details']:
                    f.write(f"- {detail}\n")
                
                # 실제 분해 내용
                if 'decomposition' in r['raw_response']:
                    f.write("\n**분해 과정**:\n")
                    for i, step in enumerate(r['raw_response']['decomposition'][:5], 1):
                        f.write(f"{i}. {step.get('step', 'N/A')}\n")
                        if 'value' in step:
                            f.write(f"   - 값: {step['value']}\n")
                        if 'assumption' in step:
                            f.write(f"   - 가정: {step['assumption'][:100]}\n")
                
                f.write("\n---\n\n")
        
        # 최종 종합
        f.write("\n## 🏆 최종 종합 순위\n\n")
        f.write(f"| 순위 | 모델 | 평균 점수 | 정확도 | 분해 | 논리 |\n")
        f.write(f"|------|------|----------|--------|------|------|\n")
        
        for i, m in enumerate(model_averages, 1):
            f.write(f"| {i} | {m['model']} | {m['avg_total']:.1f}/100 | {m['avg_accuracy']:.1f}/40 | {m['avg_decomp']:.1f}/30 | {m['avg_logic']:.1f}/30 |\n")
        
        f.write("\n## 💡 결론\n\n")
        f.write("이 평가는 AI(Assistant)가 직접 작성한 Fermi 분해를 기준선으로 사용했습니다.\n\n")
        f.write("**장점**:\n")
        f.write("- 투명한 평가 기준\n")
        f.write("- 상대적 비교 가능\n")
        f.write("- 실제 데이터 기반\n\n")
        
        f.write("**한계**:\n")
        f.write("- AI 기준선도 완벽하지 않음 (10-23% 오차)\n")
        f.write("- 더 나은 접근법이 있을 수 있음\n\n")
    
    print(f"📄 상세 보고서 저장: {report_file}")


if __name__ == "__main__":
    run_comprehensive_fermi_test()

