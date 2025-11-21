#!/usr/bin/env python3
"""
GPT-5 경량 모델 테스트 (Responses API)
gpt-5-low, gpt-5-minimalist 등
"""

import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.benchmark_comprehensive_2025 import ComprehensiveLLMBenchmark


def test_lightweight_gpt5_models():
    """GPT-5 경량 모델 테스트"""
    print("=" * 80)
    print("GPT-5 경량 모델 테스트 (Responses API)")
    print("=" * 80)
    print()
    
    benchmark = ComprehensiveLLMBenchmark()
    
    # 테스트할 경량 모델들
    lightweight_models = [
        'gpt-5-low',           # 저사양 버전
        'gpt-5-minimalist',    # 최소주의 버전
        'gpt-5',               # 기본 버전 (Responses API용)
        'gpt-5.1',             # 개선 버전 (Responses API용)
    ]
    
    # Responses API 모델 리스트에 추가
    original_responses_models = benchmark.responses_api_models.copy()
    benchmark.responses_api_models.extend(lightweight_models)
    
    print("✅ 경량 GPT-5 모델 테스트")
    print("   모델: 4개")
    print("   시나리오: Phase 0만 (빠른 검증)")
    print()
    print("테스트 모델:")
    for model in lightweight_models:
        print(f"  - {model}")
    print()
    
    scenarios = benchmark.get_test_scenarios()[:1]  # Phase 0만
    results = []
    
    for model in lightweight_models:
        print(f"📝 테스트: {model}")
        
        for scenario in scenarios:
            try:
                start = time.time()
                result = benchmark.test_openai_model(model, scenario)
                elapsed = time.time() - start
                
                results.append(result)
                
                if result['success']:
                    print(f"   ✅ 성공!")
                    print(f"      API: {result.get('api_type', 'chat')}")
                    print(f"      비용: ${result['cost']:.6f}")
                    print(f"      시간: {result['elapsed_seconds']:.2f}초")
                    print(f"      품질: {result['quality_score']['total_score']}/100")
                else:
                    error = result.get('error', '')
                    if '404' in error:
                        print(f"   ⚠️ 모델 없음 (404)")
                    elif 'not supported' in error.lower():
                        print(f"   ⚠️ Responses API 미지원")
                    else:
                        print(f"   ❌ 오류: {error[:80]}")
                
                time.sleep(2)  # Rate limiting
            
            except Exception as e:
                print(f"   ❌ 예외: {str(e)[:80]}")
                results.append({
                    'model': model,
                    'scenario_id': scenario['id'],
                    'error': str(e),
                    'success': False
                })
                time.sleep(2)
        
        print()
    
    # 결과 요약
    print("=" * 80)
    print("📊 결과 요약")
    print("=" * 80)
    print()
    
    success = [r for r in results if r.get('success', False)]
    failed = [r for r in results if not r.get('success', False)]
    
    print(f"총 테스트: {len(results)}개")
    print(f"성공: {len(success)}개")
    print(f"실패: {len(failed)}개")
    print()
    
    if success:
        print("✅ 성공한 모델:")
        for r in success:
            print(f"   - {r['model']}: ${r['cost']:.6f}, {r['elapsed_seconds']:.2f}초, {r['quality_score']['total_score']}/100")
        print()
    
    if failed:
        print("❌ 실패한 모델:")
        for r in failed:
            error = r.get('error', '')[:80]
            print(f"   - {r['model']}: {error}")
        print()
    
    # 비교 분석
    if success:
        print("=" * 80)
        print("💰 비용 비교")
        print("=" * 80)
        print()
        
        # gpt-4.1-nano 기준
        baseline_cost = 0.000023
        baseline_time = 1.32
        
        print(f"{'모델':<20} | {'비용':<12} | {'시간':<10} | {'품질':<8} | {'가성비':<10} | {'vs nano'}")
        print("-" * 90)
        print(f"{'gpt-4.1-nano (기준)':<20} | ${baseline_cost:<11.6f} | {baseline_time:<9.2f}초 | {'100':>6}/100 | {'4347.8':>8} | 기준")
        
        for r in sorted(success, key=lambda x: x['cost']):
            cost_ratio = r['cost'] / baseline_cost
            time_ratio = r['elapsed_seconds'] / baseline_time
            efficiency = r['quality_score']['total_score'] / (r['cost'] * 1000)
            
            print(f"{r['model']:<20} | ${r['cost']:<11.6f} | {r['elapsed_seconds']:<9.2f}초 | {r['quality_score']['total_score']:>6}/100 | {efficiency:>8.1f} | {cost_ratio:>4.1f}배")
    
    # 복원
    benchmark.responses_api_models = original_responses_models
    
    print()
    print("🎉 테스트 완료!")


if __name__ == "__main__":
    test_lightweight_gpt5_models()

