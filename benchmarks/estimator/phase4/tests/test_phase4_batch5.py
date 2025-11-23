#!/usr/bin/env python3
"""
Phase 4 Batch 5: Low Effort 테스트 (필요 모델만)
- gpt-5.1 (reasoning_effort='low')
- o4-mini (reasoning_effort='low')

⚠️ 제외된 모델 (effort 조정 불가):
- gpt-5-pro (high 고정)
- o1-pro (high 고정)
- o1-pro-2025-03-19 (high 고정)

모델별 API 파라미터 명시적 관리 + 개념적 일관성 평가
"""

import os
import json
import time
import re
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

# phase4_common 모듈에서 공통 함수 import
from phase4_common import (
    get_model_config,
    build_api_params,
    call_model_api,
    get_phase4_scenarios,
    evaluate_fermi_response
)

load_dotenv()


def test_model_responses_api(client, model_name, scenario, reasoning_effort='low'):
    """Responses API로 모델 테스트 - phase4_common 사용"""

    try:
        start = time.time()

        # phase4_common에서 모델별 API 파라미터 생성
        api_type, api_params = build_api_params(
            model_name=model_name,
            prompt=scenario['prompt'],
            reasoning_effort=reasoning_effort
        )

        # 모델 설정 출력 (디버깅)
        config = get_model_config(model_name)
        print(f"\n🔧 {model_name} API 설정:")
        print(f"  - API 타입: {api_type}")
        print(f"  - reasoning 지원: {config['reasoning_effort_support']}")
        if config['reasoning_effort_support']:
            actual_effort = api_params.get('reasoning', {}).get('effort', 'N/A')
            print(f"  - reasoning.effort: {actual_effort} (요청: {reasoning_effort})")
        print(f"  - max_output_tokens: {api_params['max_output_tokens']}")

        # API 호출
        response = call_model_api(client, api_type, api_params)

        # 응답 텍스트 추출 (API 타입별)
        if api_type == 'responses':
            content = getattr(response, 'output_text', None) or getattr(response, 'output', str(response))
        else:  # 'chat'
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


def save_partial_results(all_results, scenarios, test_config, error_info=None):
    """부분 결과 저장 (오류 발생 시 또는 정상 완료 시)"""
    from collections import defaultdict

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

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

    status = 'PARTIAL' if error_info else 'COMPLETE'
    output_file = f"phase4_batch5_low_{status.lower()}_{timestamp}.json"

    data = {
        'metadata': {
            'timestamp': datetime.now().isoformat(),
            'batch': 'Batch 5 - Low Effort Test',
            'reasoning_effort': 'low',
            'status': status,
            'models_tested': len(by_model),
            'total_models': len(test_config),
            'problems_tested': len(set(r['problem_id'] for r in all_results)),
            'total_problems': len(scenarios),
            'completed_tests': len(all_results)
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
    }

    if error_info:
        data['error'] = error_info

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return output_file, model_averages


def run_batch5_test():
    """Batch 5 테스트 실행 - Low Effort (필요 모델만)"""
    print("=" * 120)
    print("Phase 4 Batch 5 - Low Effort 테스트")
    print("=" * 120)
    print("✅ 테스트 모델: gpt-5.1, o4-mini (reasoning_effort='low')")
    print("❌ 제외 모델: gpt-5-pro, o1-pro 계열 (effort='high' 고정, Batch 3과 동일)")
    print()

    client = OpenAI()

    # Batch 5: effort='low' 테스트
    test_config = [
        {'model': 'gpt-5.1', 'effort': 'low', 'tier': 'Batch 5'},
        {'model': 'o4-mini', 'effort': 'low', 'tier': 'Batch 5'},
    ]

    all_results = []

    error_occurred = False
    error_info = None

    try:
        for model_idx, config in enumerate(test_config, 1):
            model_name = config['model']
            effort = config['effort']
            tier = config['tier']
            
            # 모델별로 scenarios 생성 (pro 모델은 Fast Mode 추가)
            scenarios = get_phase4_scenarios(model_name)
            
            print(f"\n{'='*120}")
            print(f"🤖 모델 {model_idx}/{len(test_config)}: {model_name} ({tier}, effort={effort})")
            print(f"{'='*120}\n")

            for scenario_idx, scenario in enumerate(scenarios, 1):
                print(f"\n📋 문제 {scenario_idx}/{len(scenarios)}: {scenario['name']}")
                print(f"   정답: {scenario['expected_value']:,} {scenario['expected_unit']}\n")

                try:
                    test_result = test_model_responses_api(client, model_name, scenario, effort)

                    if test_result['success']:
                        eval_result = evaluate_fermi_response(
                            model_name=f"{model_name}",
                            response=test_result['response'],
                            expected_value=scenario['expected_value'],
                            problem_id=scenario['id']  # 개념적 일관성 평가를 위해 추가
                        )

                        eval_result['elapsed'] = test_result['elapsed']
                        eval_result['response'] = test_result['response']
                        eval_result['problem'] = scenario['name']
                        eval_result['problem_id'] = scenario['id']
                        eval_result['tier'] = tier
                        eval_result['reasoning_effort'] = effort

                        problem_results.append(eval_result)
                        all_results.append(eval_result)

                        # 개념적 일관성 점수 추가 출력
                        conceptual_score = eval_result.get('conceptual_coherence', {}).get('score', 0)
                        print(f"   ✅ {eval_result['value']:,} {eval_result['unit']} | 총점: {eval_result['total_score']}/100")
                        print(f"      연결성: {eval_result['calculation_connectivity']['score']}/50 | 개념: {conceptual_score}/15")
                    else:
                        error_msg = test_result['error']
                        print(f"   ❌ API 오류: {error_msg[:100]}")

                        # 치명적 오류 (API 키, 권한 등)인 경우 즉시 중단
                        if any(key in error_msg.lower() for key in ['api_key', 'authentication', 'unauthorized', 'forbidden']):
                            raise Exception(f"치명적 API 오류: {error_msg}")

                        # 모델 지원 안 됨 등은 계속 진행
                        print(f"   ⚠️  모델 '{model_name}' 건너뜀")

                except KeyboardInterrupt:
                    print("\n\n⚠️  사용자에 의해 중단됨 (Ctrl+C)")
                    error_occurred = True
                    error_info = {
                        'type': 'USER_INTERRUPT',
                        'message': '사용자가 테스트를 중단했습니다',
                        'failed_at': {
                            'problem': scenario['name'],
                            'problem_id': scenario['id'],
                            'model': model_name,
                            'scenario_progress': f"{scenario_idx}/{len(scenarios)}",
                            'model_progress': f"{model_idx}/{len(test_config)}"
                        }
                    }
                    raise

                except Exception as e:
                    print(f"\n\n❌ 오류 발생!")
                    print(f"   오류 내용: {str(e)}")
                    error_occurred = True
                    error_info = {
                        'type': 'RUNTIME_ERROR',
                        'message': str(e),
                        'failed_at': {
                            'problem': scenario['name'],
                            'problem_id': scenario['id'],
                            'model': model_name,
                            'scenario_progress': f"{scenario_idx}/{len(scenarios)}",
                            'model_progress': f"{model_idx}/{len(test_config)}"
                        }
                    }
                    raise

                time.sleep(2)

            # 문제별 순위
            if problem_results:
                print(f"\n📊 {scenario['name']} 순위:\n")
                problem_results.sort(key=lambda x: x['total_score'], reverse=True)

                for i, r in enumerate(problem_results, 1):
                    marker = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "  "
                    print(f"{marker}{i}. {r['model']:<35} {r['total_score']:>3}/100 (정확도: {r['accuracy']['score']}/25, 연결성: {r['calculation_connectivity']['score']}/50)")

                print()

    except (KeyboardInterrupt, Exception) as e:
        error_occurred = True
        print("\n" + "=" * 120)
        print("⚠️  테스트 중단 - 부분 결과 저장 중")
        print("=" * 120)

    # 종합 결과 및 저장
    print("\n" + "=" * 120)
    if error_occurred:
        print(f"⚠️  Batch 5 부분 결과 ({len(all_results)}개 테스트 완료)")
    else:
        print("🏆 Batch 5 최종 순위 (3개 문제 평균)")
    print("=" * 120)
    print()

    if all_results:
        # 결과 저장
        output_file, model_averages = save_partial_results(all_results, scenarios, test_config, error_info)

        # 순위 출력
        print(f"{'순위':<4} | {'모델':<35} | {'평균':<10} | {'정확도':<10} | {'연결성':<10} | {'분해':<10} | {'논리':<8}")
        print("-" * 120)

        for i, m in enumerate(model_averages, 1):
            marker = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "  "
            print(f"{marker}{i:<3} | {m['model']:<35} | {m['avg_total']:>8.1f}/100 | {m['avg_accuracy']:>8.1f}/25 | {m['avg_connectivity']:>8.1f}/50 | {m['avg_decomp']:>8.1f}/15 | {m['avg_logic']:>6.1f}/10")

        print(f"\n✅ 결과 저장: {output_file}")
    else:
        print("⚠️  완료된 테스트가 없습니다.")

    # 오류 상세 출력
    if error_occurred and error_info:
        print("\n" + "=" * 120)
        print("❌ 오류 상세 정보")
        print("=" * 120)
        print(f"\n오류 유형: {error_info['type']}")
        print(f"오류 메시지: {error_info['message']}")
        print(f"\n실패 위치:")
        print(f"  - 문제: {error_info['failed_at']['problem']}")
        print(f"  - 모델: {error_info['failed_at']['model']}")
        print(f"  - 진행 상황: 문제 {error_info['failed_at']['scenario_progress']}, 모델 {error_info['failed_at']['model_progress']}")
        print(f"\n완료된 테스트: {len(all_results)}개")
        print()

    if error_occurred:
        print("\n⚠️  테스트가 중단되었습니다. 부분 결과를 확인하세요.")
    else:
        print("\n🎉 Batch 5 테스트 완료!")

    return not error_occurred


if __name__ == "__main__":
    run_batch5_test()

