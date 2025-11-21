#!/usr/bin/env python3
"""
Responses API 테스트
codex, pro 모델들을 Responses API로 테스트
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.benchmark_comprehensive_2025 import ComprehensiveLLMBenchmark


def test_responses_api():
    """Responses API 모델 테스트"""
    print("=" * 80)
    print("OpenAI Responses API 테스트")
    print("=" * 80)
    print()
    
    benchmark = ComprehensiveLLMBenchmark()
    
    # Responses API 모델만 테스트
    benchmark.models = {
        'openai_codex': [
            'gpt-5-codex',
            'gpt-5.1-codex'
        ],
        'openai_pro': [
            'gpt-5-pro'
        ],
        'openai_thinking_pro': [
            'o1-pro'
        ]
    }
    
    print("✅ Responses API 모델 테스트")
    print("   모델: 4개 (codex × 2, pro × 2)")
    print("   시나리오: Phase 0만 (빠른 테스트)")
    print()
    
    scenarios = benchmark.get_test_scenarios()[:1]  # Phase 0만
    
    for scenario in scenarios:
        print(f"📝 시나리오: {scenario['name']}")
        print()
        
        for category, models in benchmark.models.items():
            print(f"📦 {category}")
            
            for model in models:
                try:
                    result = benchmark.test_openai_model(model, scenario)
                    
                    if result['success']:
                        print(f"   ✅ {model}: 성공!")
                        print(f"      API 타입: {result.get('api_type', 'chat')}")
                        print(f"      비용: ${result['cost']:.6f}")
                        print(f"      시간: {result['elapsed_seconds']}초")
                        print(f"      품질: {result['quality_score']['total_score']}/100")
                    else:
                        error = result.get('error', '')[:100]
                        print(f"   ❌ {model}: {error}")
                
                except Exception as e:
                    print(f"   ❌ {model}: 예외 - {str(e)[:100]}")
                
                import time
                time.sleep(2)  # Rate limiting
            
            print()
    
    print("=" * 80)
    print("🎉 테스트 완료!")
    print("=" * 80)


if __name__ == "__main__":
    test_responses_api()

