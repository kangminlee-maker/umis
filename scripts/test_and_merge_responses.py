#!/usr/bin/env python3
"""
Responses API 모델 전체 테스트 + 기존 결과 병합
"""

import json
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.benchmark_comprehensive_2025 import ComprehensiveLLMBenchmark


def test_responses_api_full():
    """Responses API 모델 전체 시나리오 테스트"""
    print("=" * 100)
    print("Responses API 모델 전체 테스트")
    print("=" * 100)
    print()
    
    benchmark = ComprehensiveLLMBenchmark()
    
    # Responses API 모델만
    benchmark.models = {
        'openai_codex': ['gpt-5-codex', 'gpt-5.1-codex'],
        'openai_pro': ['gpt-5-pro'],
        'openai_thinking_pro': ['o1-pro']
    }
    
    print("✅ Responses API 모델 전체 테스트")
    print("   모델: 4개")
    print("   시나리오: 7개 (Phase 0-4)")
    print("   예상 소요 시간: ~10분")
    print()
    
    try:
        benchmark.run_benchmark(category_filter=['openai_codex', 'openai_pro', 'openai_thinking_pro'])
        
        # 결과 저장
        output_file = f"benchmark_responses_api_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        benchmark.save_results(output_file)
        
        # 통계
        success = [r for r in benchmark.results if r.get('success', False)]
        print(f"\n{'='*100}")
        print("📊 Responses API 테스트 결과")
        print(f"{'='*100}\n")
        print(f"총 테스트: {len(benchmark.results)}개")
        print(f"성공: {len(success)}개 ({len(success)/len(benchmark.results)*100:.1f}%)")
        print(f"실패: {len(benchmark.results) - len(success)}개")
        
        return output_file
    
    except KeyboardInterrupt:
        print("\n\n⚠️ 중단됨")
        return None


def merge_with_previous(responses_file: str, previous_file: str = 'benchmark_merged_20251121_120819.json'):
    """Responses API 결과와 기존 결과 병합"""
    print(f"\n{'='*100}")
    print("결과 병합")
    print(f"{'='*100}\n")
    
    # 기존 결과 로드
    with open(previous_file, 'r') as f:
        previous_data = json.load(f)
    
    # Responses API 결과 로드
    with open(responses_file, 'r') as f:
        responses_data = json.load(f)
    
    print(f"기존 결과: {len(previous_data['results'])}개")
    print(f"Responses API 결과: {len(responses_data['results'])}개")
    
    # 병합 (Responses API 모델의 기존 실패 결과를 새 결과로 교체)
    results_dict = {}
    for r in previous_data['results']:
        key = (r.get('model'), r.get('scenario_id'))
        results_dict[key] = r
    
    # Responses API 결과로 업데이트
    updated_count = 0
    for r in responses_data['results']:
        key = (r.get('model'), r.get('scenario_id'))
        if key in results_dict:
            results_dict[key] = r
            updated_count += 1
        else:
            results_dict[key] = r  # 새 결과 추가
    
    # 최종 결과
    merged_results = list(results_dict.values())
    
    merged_data = {
        'metadata': {
            'timestamp': datetime.now().isoformat(),
            'total_tests': len(merged_results),
            'success_count': sum(1 for r in merged_results if r.get('success', False)),
            'previous_file': previous_file,
            'responses_file': responses_file,
            'updated_count': updated_count
        },
        'results': merged_results
    }
    
    # 저장
    output_file = f"benchmark_final_with_responses_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 병합 완료: {output_file}")
    print(f"   총 결과: {len(merged_results)}개")
    print(f"   성공: {merged_data['metadata']['success_count']}개")
    print(f"   업데이트: {updated_count}개")
    
    # 최종 리포트
    generate_final_report(merged_data)
    
    return output_file


def generate_final_report(data):
    """최종 리포트 생성"""
    results = data['results']
    success = [r for r in results if r.get('success', False)]
    
    print(f"\n{'='*100}")
    print("📊 최종 종합 리포트 (Responses API 포함)")
    print(f"{'='*100}\n")
    
    print(f"총 테스트: {len(results)}개")
    print(f"성공: {len(success)}개 ({len(success)/len(results)*100:.1f}%)")
    
    # Responses API 모델 성공률
    responses_models = ['gpt-5-codex', 'gpt-5.1-codex', 'gpt-5-pro', 'o1-pro']
    
    print(f"\n{'='*100}")
    print("Responses API 모델 성공률")
    print(f"{'='*100}\n")
    
    from collections import defaultdict
    model_stats = defaultdict(lambda: {'success': 0, 'total': 0})
    
    for r in results:
        model = r.get('model')
        if model in responses_models:
            model_stats[model]['total'] += 1
            if r.get('success', False):
                model_stats[model]['success'] += 1
    
    for model, stats in model_stats.items():
        success_rate = stats['success'] / stats['total'] * 100 if stats['total'] > 0 else 0
        status = "✅" if success_rate == 100 else "⚠️" if success_rate >= 50 else "❌"
        print(f"{status} {model:20s} | {stats['success']:2d}/{stats['total']:2d} | {success_rate:5.1f}%")
    
    # 가성비 분석 (Responses API 포함)
    print(f"\n{'='*100}")
    print("전체 모델 가성비 TOP 15 (Responses API 포함)")
    print(f"{'='*100}\n")
    
    model_perf = defaultdict(lambda: {'costs': [], 'quality': []})
    
    for r in success:
        model = r['model']
        model_perf[model]['costs'].append(r.get('cost', 0))
        model_perf[model]['quality'].append(r.get('quality_score', {}).get('total_score', 0))
    
    model_avg = []
    for model, data_dict in model_perf.items():
        if not data_dict['costs']:
            continue
        
        avg_cost = sum(data_dict['costs']) / len(data_dict['costs'])
        avg_quality = sum(data_dict['quality']) / len(data_dict['quality'])
        efficiency = avg_quality / (avg_cost * 1000) if avg_cost > 0 else 0
        
        model_avg.append({
            'model': model,
            'avg_cost': avg_cost,
            'avg_quality': avg_quality,
            'efficiency': efficiency,
            'count': len(data_dict['costs'])
        })
    
    model_avg.sort(key=lambda x: x['efficiency'], reverse=True)
    
    for idx, m in enumerate(model_avg[:15], 1):
        print(f"   {idx:2d}. {m['model']:30s} | 가성비: {m['efficiency']:7.1f} | 품질: {m['avg_quality']:5.1f} | 비용: ${m['avg_cost']:.6f}")


def main():
    """메인 실행"""
    # 1. Responses API 모델 전체 테스트
    responses_file = test_responses_api_full()
    
    if not responses_file:
        print("\n❌ 테스트 실패 또는 중단됨")
        return
    
    # 2. 기존 결과와 병합
    merge_with_previous(responses_file)
    
    print("\n🎉 완료!")


if __name__ == "__main__":
    main()

