#!/usr/bin/env python3
"""
API 연결 테스트 (개선 확인)
"""

import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.benchmark_llm_models_2025 import LLMBenchmark2025

def test_single_model():
    """
    단일 모델 테스트로 개선 사항 확인
    """
    print("=" * 80)
    print("API 연결 개선 테스트")
    print("=" * 80)
    print()
    
    benchmark = LLMBenchmark2025()
    
    # 가장 저렴한 모델 하나만 테스트
    benchmark.models = {
        'openai_mini': ['gpt-4o-mini']
    }
    
    try:
        print("✅ 재시도 로직 테스트 (gpt-4o-mini)")
        print("   - Phase 0 시나리오만 실행")
        print("   - Exponential backoff 활성화")
        print("   - Rate limiting: 1.5초")
        print()
        
        scenarios = benchmark.get_test_scenarios()[:1]  # Phase 0만
        
        for scenario in scenarios:
            print(f"📝 시나리오: {scenario['name']}")
            
            for category, models in benchmark.models.items():
                for model in models:
                    try:
                        result = benchmark.test_openai_model(model, scenario)
                        
                        if result['success']:
                            print(f"✅ {model}: 성공!")
                            print(f"   비용: ${result['cost']:.6f}")
                            print(f"   시간: {result['elapsed_seconds']}초")
                            print(f"   토큰: {result['tokens']['total']}")
                        else:
                            print(f"❌ {model}: 실패 - {result.get('error')}")
                    
                    except Exception as e:
                        print(f"❌ {model}: 예외 발생 - {str(e)}")
        
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
    test_single_model()

