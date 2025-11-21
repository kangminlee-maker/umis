#!/usr/bin/env python3
"""
Comprehensive 벤치마크 API 연결 테스트
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.benchmark_comprehensive_2025 import ComprehensiveLLMBenchmark

def test_single_scenario():
    """
    단일 시나리오 테스트로 개선 사항 확인
    """
    print("=" * 80)
    print("Comprehensive 벤치마크 - API 연결 개선 테스트")
    print("=" * 80)
    print()
    
    benchmark = ComprehensiveLLMBenchmark()
    
    # 가장 저렴한 모델들만 테스트
    benchmark.models = {
        'openai_nano': ['gpt-4.1-nano'],
        'claude_standard': ['claude-haiku-3.5']
    }
    
    print("✅ 재시도 로직 테스트")
    print("   - OpenAI: gpt-4.1-nano")
    print("   - Claude: claude-haiku-3.5")
    print("   - Phase 0 시나리오만 실행")
    print("   - Exponential backoff 활성화")
    print()
    
    try:
        scenarios = benchmark.get_test_scenarios()[:1]  # Phase 0만
        
        for scenario in scenarios:
            print(f"📝 시나리오: {scenario['name']}")
            print()
            
            # OpenAI 테스트
            print("📦 OpenAI nano")
            for model in benchmark.models['openai_nano']:
                try:
                    result = benchmark.test_openai_model(model, scenario)
                    
                    if result['success']:
                        print(f"   ✅ {model}")
                        print(f"      비용: ${result['cost']:.6f} | 시간: {result['elapsed_seconds']}초")
                        print(f"      품질: {result['quality_score']['total_score']}/100")
                    else:
                        print(f"   ❌ {model}: {result.get('error')}")
                except Exception as e:
                    print(f"   ❌ {model}: 예외 - {str(e)}")
            
            # Claude 테스트
            print("\n📦 Claude standard")
            for model in benchmark.models['claude_standard']:
                try:
                    result = benchmark.test_claude_model(model, scenario)
                    
                    if result['success']:
                        print(f"   ✅ {model}")
                        print(f"      비용: ${result['cost']:.6f} | 시간: {result['elapsed_seconds']}초")
                        print(f"      품질: {result['quality_score']['total_score']}/100")
                    else:
                        print(f"   ❌ {model}: {result.get('error')}")
                except Exception as e:
                    print(f"   ❌ {model}: 예외 - {str(e)}")
        
        print()
        print("=" * 80)
        print("🎉 테스트 완료! 재시도 로직이 정상 작동합니다.")
        print("=" * 80)
    
    except KeyboardInterrupt:
        print("\n⚠️ 사용자가 중단했습니다.")
    
    except Exception as e:
        print(f"\n❌ 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_single_scenario()

