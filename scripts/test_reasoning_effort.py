#!/usr/bin/env python3
"""
GPT-5 reasoning_effort 옵션 테스트
동일 모델(gpt-5, gpt-5.1)에 다양한 reasoning_effort 적용
"""

import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.benchmark_comprehensive_2025 import ComprehensiveLLMBenchmark


def test_reasoning_effort_options():
    """reasoning_effort 옵션별 테스트"""
    print("=" * 80)
    print("GPT-5 reasoning_effort 옵션 테스트")
    print("=" * 80)
    print()
    
    benchmark = ComprehensiveLLMBenchmark()
    
    # 테스트 구성: (모델, reasoning_effort)
    test_configs = [
        # GPT-5 시리즈
        ('gpt-5', 'minimal'),
        ('gpt-5', 'low'),
        ('gpt-5', 'medium'),
        ('gpt-5', 'high'),
        ('gpt-5.1', 'minimal'),
        ('gpt-5.1', 'low'),
        ('gpt-5.1', 'medium'),
        ('gpt-5.1', 'high'),
    ]
    
    # Responses API 모델로 등록
    benchmark.responses_api_models.extend(['gpt-5', 'gpt-5.1'])
    
    print("📋 테스트 구성: 8개")
    print("   모델: gpt-5, gpt-5.1")
    print("   reasoning_effort: minimal, low, medium, high")
    print()
    
    scenarios = benchmark.get_test_scenarios()[:1]  # Phase 0만
    results = []
    
    for scenario in scenarios:
        print(f"📝 시나리오: {scenario['name']}")
        print()
        
        for model, effort in test_configs:
            config_name = f"{model} (effort={effort})"
            print(f"테스트: {config_name}")
            
            try:
                # reasoning_effort를 시나리오에 임시로 추가
                test_scenario = scenario.copy()
                test_scenario['reasoning_effort'] = effort
                
                start = time.time()
                
                # Responses API는 다르게 호출해야 함
                # 일단 수동으로 API 호출
                from openai import OpenAI
                client = OpenAI()
                
                input_text = scenario['prompt'] + "\n\n⚠️ 중요: 반드시 순수 JSON 형식으로만 응답하세요."
                
                # Responses API 호출
                response = client.responses.create(
                    model=model,
                    input=input_text,
                    reasoning_effort=effort
                )
                
                elapsed = time.time() - start
                
                # 응답 파싱
                if hasattr(response, 'output_text'):
                    content = response.output_text
                elif hasattr(response, 'output'):
                    content = response.output
                else:
                    content = str(response)
                
                # JSON 추출
                import json
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
                except:
                    parsed = {'raw': content, 'parse_error': True}
                
                # 토큰 및 비용
                tokens = {
                    'input': getattr(response, 'input_tokens', 0),
                    'output': getattr(response, 'output_tokens', 0),
                }
                
                if tokens['input'] == 0:
                    tokens['input'] = len(input_text) // 4
                    tokens['output'] = len(content) // 4
                
                cost = benchmark._calculate_cost(model, tokens['input'], tokens['output'])
                quality = benchmark._evaluate_quality(parsed, scenario.get('expected', {}), scenario['phase'])
                
                result = {
                    'model': model,
                    'reasoning_effort': effort,
                    'config_name': config_name,
                    'cost': cost,
                    'elapsed_seconds': elapsed,
                    'quality_score': quality,
                    'response': parsed,
                    'success': True
                }
                
                results.append(result)
                
                print(f"   ✅ 성공!")
                print(f"      비용: ${cost:.6f}")
                print(f"      시간: {elapsed:.2f}초")
                print(f"      품질: {quality['total_score']}/100")
                
                time.sleep(2)
            
            except Exception as e:
                print(f"   ❌ 오류: {str(e)[:80]}")
                results.append({
                    'model': model,
                    'reasoning_effort': effort,
                    'config_name': config_name,
                    'error': str(e),
                    'success': False
                })
                time.sleep(2)
            
            print()
    
    # 결과 분석
    print("=" * 80)
    print("📊 결과 분석")
    print("=" * 80)
    print()
    
    success = [r for r in results if r.get('success', False)]
    
    if success:
        print(f"총 테스트: {len(results)}개")
        print(f"성공: {len(success)}개")
        print()
        
        # 모델별 그룹화
        from collections import defaultdict
        
        by_model = defaultdict(list)
        for r in success:
            by_model[r['model']].append(r)
        
        for model in ['gpt-5', 'gpt-5.1']:
            if model not in by_model:
                continue
            
            print(f"{'='*80}")
            print(f"{model} - reasoning_effort별 비교")
            print(f"{'='*80}")
            print()
            
            model_results = by_model[model]
            
            print(f"{'effort':<10} | {'비용':<12} | {'시간':<10} | {'품질':<8} | {'가성비':<10}")
            print("-" * 70)
            
            for r in sorted(model_results, key=lambda x: ['minimal', 'low', 'medium', 'high'].index(x['reasoning_effort'])):
                effort = r['reasoning_effort']
                cost = r['cost']
                time_val = r['elapsed_seconds']
                quality = r['quality_score']['total_score']
                efficiency = quality / (cost * 1000) if cost > 0 else 0
                
                print(f"{effort:<10} | ${cost:<11.6f} | {time_val:<9.2f}초 | {quality:>6}/100 | {efficiency:>8.1f}")
            
            print()
            
            # 최적 옵션 추천
            best_efficiency = max(model_results, key=lambda r: r['quality_score']['total_score'] / (r['cost'] * 1000) if r['cost'] > 0 else 0)
            best_quality = max(model_results, key=lambda r: r['quality_score']['total_score'])
            fastest = min(model_results, key=lambda r: r['elapsed_seconds'])
            
            print(f"💡 {model} 권장 옵션:")
            print(f"   - 최고 가성비: {best_efficiency['reasoning_effort']} (가성비 {best_efficiency['quality_score']['total_score'] / (best_efficiency['cost'] * 1000):.1f})")
            print(f"   - 최고 품질: {best_quality['reasoning_effort']} ({best_quality['quality_score']['total_score']}/100)")
            print(f"   - 가장 빠름: {fastest['reasoning_effort']} ({fastest['elapsed_seconds']:.2f}초)")
            print()
    
    # 저장
    import json
    from datetime import datetime
    
    output_file = f"benchmark_reasoning_effort_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'test_type': 'reasoning_effort_comparison'
            },
            'results': results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 결과 저장: {output_file}")
    print()
    print("🎉 테스트 완료!")


if __name__ == "__main__":
    test_reasoning_effort_options()


