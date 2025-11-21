#!/usr/bin/env python3
"""
Responses API 통합 테스트 (시간 예측 포함)
모든 Responses API 모델을 체계적으로 테스트
"""

import sys
import os
import time
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.benchmark_comprehensive_2025 import ComprehensiveLLMBenchmark


# Phase 0 실측 데이터 (초)
PHASE0_TIMES = {
    'gpt-5-codex': 1.85,
    'gpt-5.1-codex': 1.44,
    'gpt-5': 8.71,
    'gpt-5.1': 1.84,
    'gpt-5-pro': 73.69,
    'o1-pro': 30.22
}

# Rate limiting (초)
RATE_LIMITING = {
    'codex': 2,
    'pro': 3,
    'thinking': 3,
    'standard': 2
}


def estimate_test_time(models, num_scenarios=1):
    """테스트 소요 시간 예측"""
    total_time = 0
    details = []
    
    for model in models:
        # Phase 0 실측 시간
        base_time = PHASE0_TIMES.get(model, 2.0)  # 기본값 2초
        
        # Rate limiting 결정
        if 'codex' in model:
            rl = RATE_LIMITING['codex']
        elif 'o1-pro' in model or 'o3-pro' in model:
            rl = RATE_LIMITING['thinking']
        elif 'pro' in model:
            rl = RATE_LIMITING['pro']
        else:
            rl = RATE_LIMITING['standard']
        
        # 시나리오당 시간
        time_per_scenario = base_time + rl
        
        # 전체 시간
        model_total = time_per_scenario * num_scenarios
        total_time += model_total
        
        details.append({
            'model': model,
            'per_test': base_time,
            'rate_limit': rl,
            'per_scenario': time_per_scenario,
            'total': model_total,
            'minutes': model_total / 60,
            'percentage': 0  # 나중에 계산
        })
    
    # 비율 계산
    for d in details:
        d['percentage'] = (d['total'] / total_time * 100) if total_time > 0 else 0
    
    return total_time, details


def print_time_estimate(models, num_scenarios=1):
    """예상 시간 출력"""
    total_time, details = estimate_test_time(models, num_scenarios)
    
    print(f"\n{'='*80}")
    print(f"⏱️  예상 소요 시간: {total_time:.0f}초 = {total_time/60:.1f}분")
    print(f"{'='*80}\n")
    
    print(f"{'모델':<20} | {'테스트':<8} | {'대기':<6} | {'시나리오당':<10} | {'전체':<12} | {'비율'}")
    print("-" * 80)
    
    for d in sorted(details, key=lambda x: x['total'], reverse=True):
        bar_length = int(d['percentage'] / 5)  # 20칸 바
        bar = '█' * bar_length + '░' * (20 - bar_length)
        
        print(f"{d['model']:<20} | {d['per_test']:>6.2f}초 | {d['rate_limit']:>4d}초 | "
              f"{d['per_scenario']:>8.2f}초 | {d['total']:>6.0f}초 ({d['minutes']:>4.1f}분) | "
              f"{bar} {d['percentage']:>4.1f}%")
    
    print()
    
    # 병목 구간 경고
    slow_models = [d for d in details if d['per_test'] > 10]
    if slow_models:
        print("⚠️  느린 모델 경고:")
        for d in slow_models:
            print(f"   - {d['model']}: {d['per_test']:.1f}초/테스트 "
                  f"(전체의 {d['percentage']:.0f}% 차지)")
        print()
    
    return total_time


def test_responses_api_unified():
    """Responses API 통합 테스트"""
    print("=" * 80)
    print("Responses API 통합 테스트")
    print("=" * 80)
    print()
    
    benchmark = ComprehensiveLLMBenchmark()
    
    # 테스트할 모든 Responses API 모델
    all_models = [
        'gpt-5-codex',
        'gpt-5.1-codex',
        'gpt-5',
        'gpt-5.1',
        'gpt-5-pro',
        'o1-pro'
    ]
    
    # 모델 리스트에 추가
    benchmark.responses_api_models = all_models
    
    print("📋 테스트 모델: 6개")
    for i, model in enumerate(all_models, 1):
        status = ""
        if 'pro' in model:
            status = "⚠️ 느림"
        elif model == 'gpt-5.1':
            status = "⭐ 권장"
        print(f"   {i}. {model:<20} {status}")
    print()
    
    # 테스트 옵션 선택
    print("테스트 옵션:")
    print("1. Phase 0만 (빠른 검증, ~2.5분)")
    print("2. 전체 시나리오 (완전한 평가, ~15분)")
    print("3. gpt-5.1만 (실용적, ~13초)")
    print("4. Pro 모델 제외 (추천, ~0.5분)")
    print()
    
    choice = input("선택 (1-4, 기본=1): ").strip() or "1"
    
    if choice == '2':
        num_scenarios = 7
        test_models = all_models
    elif choice == '3':
        num_scenarios = 1
        test_models = ['gpt-5.1']
    elif choice == '4':
        num_scenarios = 1
        test_models = ['gpt-5-codex', 'gpt-5.1-codex', 'gpt-5', 'gpt-5.1']
    else:
        num_scenarios = 1
        test_models = all_models
    
    # 예상 시간 출력
    estimated_time = print_time_estimate(test_models, num_scenarios)
    
    # 확인
    if estimated_time > 300:  # 5분 이상
        confirm = input(f"\n⚠️  예상 시간이 {estimated_time/60:.1f}분입니다. 계속하시겠습니까? (y/N): ")
        if confirm.lower() != 'y':
            print("\n❌ 테스트 취소됨")
            return
    
    print(f"\n🚀 테스트 시작...\n")
    
    # 테스트 실행
    scenarios = benchmark.get_test_scenarios()[:num_scenarios]
    results = []
    
    start_time = time.time()
    
    for scenario_idx, scenario in enumerate(scenarios, 1):
        print(f"\n{'='*80}")
        print(f"시나리오 {scenario_idx}/{num_scenarios}: {scenario['name']}")
        print(f"{'='*80}\n")
        
        for model_idx, model in enumerate(test_models, 1):
            print(f"[{model_idx}/{len(test_models)}] 테스트: {model}")
            
            try:
                result = benchmark.test_openai_model(model, scenario)
                results.append(result)
                
                if result['success']:
                    print(f"   ✅ 성공!")
                    print(f"      API: {result.get('api_type', 'chat')}")
                    print(f"      비용: ${result['cost']:.6f}")
                    print(f"      시간: {result['elapsed_seconds']:.2f}초")
                    print(f"      품질: {result['quality_score']['total_score']}/100")
                else:
                    error = result.get('error', '')[:80]
                    print(f"   ❌ 오류: {error}")
                
                # Rate limiting
                if 'pro' in model:
                    time.sleep(3)
                else:
                    time.sleep(2)
            
            except Exception as e:
                print(f"   ❌ 예외: {str(e)[:80]}")
                results.append({
                    'model': model,
                    'scenario_id': scenario['id'],
                    'error': str(e),
                    'success': False
                })
                time.sleep(2)
    
    elapsed_time = time.time() - start_time
    
    # 결과 요약
    print(f"\n{'='*80}")
    print("📊 테스트 결과 요약")
    print(f"{'='*80}\n")
    
    success = [r for r in results if r.get('success', False)]
    failed = [r for r in results if not r.get('success', False)]
    
    print(f"총 테스트: {len(results)}개")
    print(f"성공: {len(success)}개 ({len(success)/len(results)*100:.1f}%)")
    print(f"실패: {len(failed)}개")
    print(f"실제 소요 시간: {elapsed_time:.0f}초 ({elapsed_time/60:.1f}분)")
    print(f"예상 시간: {estimated_time:.0f}초 ({estimated_time/60:.1f}분)")
    print(f"오차: {abs(elapsed_time - estimated_time):.0f}초 ({abs(elapsed_time - estimated_time)/estimated_time*100:.1f}%)")
    print()
    
    if success:
        print("✅ 성공한 모델:")
        
        # 가성비 순 정렬
        success_sorted = sorted(success, 
                               key=lambda r: r['quality_score']['total_score'] / (r['cost'] * 1000) if r['cost'] > 0 else 0,
                               reverse=True)
        
        print(f"\n{'모델':<20} | {'비용':<12} | {'시간':<10} | {'품질':<8} | {'가성비'}")
        print("-" * 70)
        
        for r in success_sorted:
            efficiency = r['quality_score']['total_score'] / (r['cost'] * 1000) if r['cost'] > 0 else 0
            marker = "⭐" if r['model'] == 'gpt-5.1' else "  "
            print(f"{marker} {r['model']:<18} | ${r['cost']:<11.6f} | "
                  f"{r['elapsed_seconds']:<9.2f}초 | "
                  f"{r['quality_score']['total_score']:>6}/100 | {efficiency:>8.1f}")
        print()
    
    if failed:
        print("❌ 실패한 모델:")
        for r in failed:
            error = r.get('error', '')[:60]
            print(f"   - {r['model']}: {error}")
        print()
    
    # 저장
    output_file = f"benchmark_responses_unified_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    import json
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'total_tests': len(results),
                'success_count': len(success),
                'elapsed_time': elapsed_time,
                'estimated_time': estimated_time
            },
            'results': results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 결과 저장: {output_file}")
    print()
    print("🎉 테스트 완료!")


if __name__ == "__main__":
    test_responses_api_unified()

