#!/usr/bin/env python3
"""
실패 케이스 재시도 및 결과 병합
"""

import json
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.benchmark_comprehensive_2025 import ComprehensiveLLMBenchmark


def load_previous_results(filename: str):
    """이전 결과 로드"""
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)


def identify_failed_cases(results):
    """실패한 케이스 식별"""
    failed = []
    for r in results:
        if not r.get('success', False):
            model = r.get('model')
            scenario_id = r.get('scenario_id')
            error = r.get('error', '')
            
            # 404 에러는 제외 (모델이 존재하지 않음)
            if '404' in error:
                continue
            
            # codex, pro 모델은 제외 (접근 불가)
            if 'codex' in model or 'pro' in model:
                continue
            
            failed.append({
                'model': model,
                'scenario_id': scenario_id,
                'error': error
            })
    
    return failed


def retry_failed_cases(benchmark, failed_cases):
    """실패한 케이스들만 재시도"""
    print(f"\n🔄 실패 케이스 재시도 시작")
    print(f"   재시도할 케이스: {len(failed_cases)}개")
    print()
    
    retry_results = []
    scenarios = {s['id']: s for s in benchmark.get_test_scenarios()}
    
    for idx, case in enumerate(failed_cases, 1):
        model = case['model']
        scenario_id = case['scenario_id']
        
        print(f"\n[{idx}/{len(failed_cases)}] {model} @ {scenario_id}")
        
        scenario = scenarios.get(scenario_id)
        if not scenario:
            print(f"   ⚠️ 시나리오를 찾을 수 없음")
            continue
        
        try:
            if 'claude' in model.lower():
                result = benchmark.test_claude_model(model, scenario)
            else:
                result = benchmark.test_openai_model(model, scenario)
            
            retry_results.append(result)
            
            if result['success']:
                print(f"   ✅ 성공! 품질: {result['quality_score']['total_score']}/100")
            else:
                print(f"   ❌ 여전히 실패: {result.get('error', '')[:80]}")
            
            import time
            time.sleep(2)  # Rate limiting
        
        except Exception as e:
            print(f"   ❌ 예외 발생: {str(e)[:80]}")
            retry_results.append({
                'model': model,
                'scenario_id': scenario_id,
                'error': str(e),
                'success': False
            })
    
    return retry_results


def merge_results(original_data, retry_results):
    """결과 병합 (재시도 결과로 업데이트)"""
    print(f"\n📊 결과 병합 중...")
    
    # 원본 결과를 dict로 변환 (model + scenario_id를 키로)
    results_dict = {}
    for r in original_data['results']:
        key = (r.get('model'), r.get('scenario_id'))
        results_dict[key] = r
    
    # 재시도 결과로 업데이트
    updated_count = 0
    for r in retry_results:
        key = (r.get('model'), r.get('scenario_id'))
        if key in results_dict:
            results_dict[key] = r
            updated_count += 1
    
    # 최종 결과 생성
    merged_results = list(results_dict.values())
    
    print(f"   업데이트된 케이스: {updated_count}개")
    print(f"   최종 결과 수: {len(merged_results)}개")
    
    return {
        'metadata': {
            'timestamp': datetime.now().isoformat(),
            'total_tests': len(merged_results),
            'success_count': sum(1 for r in merged_results if r.get('success', False)),
            'original_file': 'benchmark_comprehensive_20251121_114452.json',
            'retry_count': len(retry_results),
            'updated_count': updated_count
        },
        'results': merged_results
    }


def generate_comprehensive_report(data):
    """종합 리포트 생성"""
    results = data['results']
    success = [r for r in results if r.get('success', False)]
    failed = [r for r in results if not r.get('success', False)]
    
    print(f"\n{'='*100}")
    print("📊 최종 종합 리포트")
    print(f"{'='*100}\n")
    
    print(f"총 테스트: {len(results)}개")
    print(f"성공: {len(success)}개 ({len(success)/len(results)*100:.1f}%)")
    print(f"실패: {len(failed)}개 ({len(failed)/len(results)*100:.1f}%)")
    
    # 실패 케이스 분류
    print(f"\n실패 원인 분류:")
    
    error_types = {}
    for r in failed:
        error = r.get('error', 'unknown')
        if '404' in error:
            error_type = '404 (모델 없음)'
        elif 'codex' in r.get('model', ''):
            error_type = 'Codex (접근 불가)'
        elif 'pro' in r.get('model', ''):
            error_type = 'Pro (접근 불가)'
        else:
            error_type = error[:50]
        
        error_types[error_type] = error_types.get(error_type, 0) + 1
    
    for error_type, count in sorted(error_types.items(), key=lambda x: -x[1]):
        print(f"   - {error_type}: {count}개")
    
    # 모델별 성공률
    print(f"\n{'='*100}")
    print("모델별 성공률")
    print(f"{'='*100}\n")
    
    from collections import defaultdict
    model_stats = defaultdict(lambda: {'success': 0, 'total': 0})
    
    for r in results:
        model = r.get('model')
        model_stats[model]['total'] += 1
        if r.get('success', False):
            model_stats[model]['success'] += 1
    
    # 성공률 순으로 정렬
    sorted_models = sorted(
        model_stats.items(),
        key=lambda x: (x[1]['success'] / x[1]['total'], x[1]['success']),
        reverse=True
    )
    
    print(f"{'모델':30s} | {'성공':>6s} / {'총계':>6s} | {'성공률':>8s}")
    print("-" * 60)
    
    for model, stats in sorted_models:
        success_rate = stats['success'] / stats['total'] * 100
        status = "✅" if success_rate == 100 else "⚠️" if success_rate >= 50 else "❌"
        print(f"{status} {model:27s} | {stats['success']:6d} / {stats['total']:6d} | {success_rate:7.1f}%")
    
    # 가성비 TOP 10
    print(f"\n{'='*100}")
    print("🏆 최고 가성비 TOP 10 (성공한 모델만)")
    print(f"{'='*100}\n")
    
    model_perf = defaultdict(lambda: {'costs': [], 'quality': [], 'times': []})
    
    for r in success:
        model = r['model']
        model_perf[model]['costs'].append(r.get('cost', 0))
        model_perf[model]['quality'].append(r.get('quality_score', {}).get('total_score', 0))
        model_perf[model]['times'].append(r.get('elapsed_seconds', 0))
    
    model_avg = []
    for model, data in model_perf.items():
        if not data['costs']:
            continue
        
        avg_cost = sum(data['costs']) / len(data['costs'])
        avg_quality = sum(data['quality']) / len(data['quality'])
        avg_time = sum(data['times']) / len(data['times'])
        efficiency = avg_quality / (avg_cost * 1000) if avg_cost > 0 else 0
        
        model_avg.append({
            'model': model,
            'avg_cost': avg_cost,
            'avg_quality': avg_quality,
            'avg_time': avg_time,
            'efficiency': efficiency,
            'count': len(data['costs'])
        })
    
    model_avg.sort(key=lambda x: x['efficiency'], reverse=True)
    
    for idx, m in enumerate(model_avg[:10], 1):
        print(f"   {idx:2d}. {m['model']:30s} | 가성비: {m['efficiency']:7.1f} | 품질: {m['avg_quality']:5.1f} | 비용: ${m['avg_cost']:.6f}")
    
    # Phase별 최적 모델
    print(f"\n{'='*100}")
    print("Phase별 최적 모델")
    print(f"{'='*100}\n")
    
    phase_results = defaultdict(list)
    for r in success:
        phase = r.get('phase', -1)
        phase_results[phase].append(r)
    
    for phase in sorted(phase_results.keys()):
        results_list = phase_results[phase]
        
        # 가성비 순 정렬
        sorted_results = sorted(
            results_list,
            key=lambda r: (r['quality_score']['total_score'] / (r['cost'] * 1000) if r['cost'] > 0 else 0),
            reverse=True
        )
        
        print(f"🔹 Phase {phase}")
        print(f"   TOP 3 (가성비):")
        
        for idx, r in enumerate(sorted_results[:3], 1):
            efficiency = r['quality_score']['total_score'] / (r['cost'] * 1000) if r['cost'] > 0 else 0
            print(f"   {idx}. {r['model']:30s} | 가성비: {efficiency:7.1f} | 품질: {r['quality_score']['total_score']:3d}/100 | ${r['cost']:.6f}")
        print()


def main():
    """메인 실행"""
    print("=" * 100)
    print("실패 케이스 재시도 및 결과 병합")
    print("=" * 100)
    
    # 1. 이전 결과 로드
    previous_file = 'benchmark_comprehensive_20251121_114452.json'
    print(f"\n📂 이전 결과 로드: {previous_file}")
    
    try:
        original_data = load_previous_results(previous_file)
    except FileNotFoundError:
        print(f"❌ 파일을 찾을 수 없습니다: {previous_file}")
        return
    
    print(f"   총 테스트: {original_data['metadata']['total_tests']}개")
    print(f"   성공: {original_data['metadata']['success_count']}개")
    
    # 2. 실패 케이스 식별
    failed_cases = identify_failed_cases(original_data['results'])
    
    print(f"\n🔍 재시도할 케이스 식별")
    print(f"   총 실패: {len([r for r in original_data['results'] if not r.get('success', False)])}개")
    print(f"   재시도 대상: {len(failed_cases)}개 (404/접근불가 제외)")
    
    if not failed_cases:
        print("\n✅ 재시도할 케이스가 없습니다!")
        print("   (모든 실패는 404 또는 접근 불가 모델)")
        
        # 그래도 리포트는 생성
        generate_comprehensive_report(original_data)
        return
    
    # 3. 재시도
    benchmark = ComprehensiveLLMBenchmark()
    retry_results = retry_failed_cases(benchmark, failed_cases)
    
    # 4. 결과 병합
    merged_data = merge_results(original_data, retry_results)
    
    # 5. 저장
    output_file = f"benchmark_merged_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 병합 결과 저장: {output_file}")
    
    # 6. 종합 리포트
    generate_comprehensive_report(merged_data)
    
    print("\n🎉 완료!")


if __name__ == "__main__":
    main()

