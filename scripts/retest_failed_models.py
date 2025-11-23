#!/usr/bin/env python3
"""
실패한 모델들만 재테스트
"""
import sys
sys.path.insert(0, '/Users/kangmin/umis_main_1103/umis')

from scripts.benchmark_comprehensive_2025 import LLMBenchmark2025Comprehensive

def main():
    """실패/저품질 모델만 재테스트"""
    
    benchmark = LLMBenchmark2025Comprehensive()
    
    # 실패하거나 품질이 낮았던 모델들
    failed_models = {
        'openai_nano': ['gpt-5-nano'],
        'openai_mini': ['gpt-5-mini'],
        'openai_standard': ['gpt-5', 'gpt-5.1'],
        'openai_thinking': ['o1', 'o3', 'o3-mini', 'o4-mini']
    }
    
    # 모델 목록 교체
    benchmark.models = failed_models
    
    print("="*100)
    print("실패 모델 재테스트 (개선된 프롬프트 + 파싱)")
    print("="*100)
    print()
    print("재테스트 모델:")
    for cat, models in failed_models.items():
        print(f"  {cat}: {', '.join(models)}")
    print()
    print("개선사항:")
    print("  ✅ reasoning 모델 프롬프트에 JSON 강조 추가")
    print("  ✅ 정규식으로 JSON 객체 추출")
    print("  ✅ 중첩 구조 지원")
    print()
    
    # 벤치마크 실행
    benchmark.run_benchmark()
    
    # 결과 저장
    output_file = 'benchmark_failed_models_retest.json'
    benchmark.save_results(output_file)
    
    # 간단한 리포트
    print("\n" + "="*100)
    print("📊 재테스트 결과")
    print("="*100)
    
    success = [r for r in benchmark.results if r.get('success')]
    
    # 모델별 평균 품질
    model_scores = {}
    for r in success:
        model = r['model']
        if model not in model_scores:
            model_scores[model] = []
        model_scores[model].append(r['quality_score']['total_score'])
    
    print("\n모델별 평균 품질:")
    for model, scores in sorted(model_scores.items()):
        avg = sum(scores) / len(scores) if scores else 0
        improvement = "개선" if avg > 20 else "여전히 낮음"
        print(f"  {model:15} {avg:5.1f}점 ({len(scores)}/7 성공) - {improvement}")
    
    # Phase별 분석
    print("\nPhase별 개선 현황:")
    phase_improve = {}
    for r in success:
        phase = r['phase']
        score = r['quality_score']['total_score']
        if phase not in phase_improve:
            phase_improve[phase] = []
        phase_improve[phase].append(score)
    
    for phase in sorted(phase_improve.keys()):
        scores = phase_improve[phase]
        avg = sum(scores) / len(scores)
        print(f"  Phase {phase}: {avg:.1f}점 (개선 전 대비)")
    
    print(f"\n✅ 결과 저장: {output_file}")
    print("🎉 재테스트 완료!")

if __name__ == "__main__":
    main()


