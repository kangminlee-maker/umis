#!/usr/bin/env python3
"""
전체 벤치마크 재실행 (Responses API 포함)
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.benchmark_comprehensive_2025 import ComprehensiveLLMBenchmark


def run_full_benchmark_with_responses():
    """Responses API 포함 전체 벤치마크"""
    print("=" * 100)
    print("전체 벤치마크 재실행 (Responses API 포함)")
    print("=" * 100)
    print()
    
    # API 키 확인
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OPENAI_API_KEY가 설정되지 않았습니다.")
        return
    
    print("✅ API 키 확인 완료")
    print()
    print("테스트 옵션:")
    print("1. 전체 모델 (Responses API 포함, 느림, ~40분)")
    print("2. Responses API 모델만 (빠름, ~10분)")
    print("3. 핵심 모델만 (기존 성공 모델 제외, ~5분)")
    print()
    
    choice = input("선택 (1-3): ").strip()
    
    benchmark = ComprehensiveLLMBenchmark()
    
    if choice == '2':
        # Responses API 모델만
        categories = ['openai_codex', 'openai_pro', 'openai_thinking_pro']
    elif choice == '3':
        # 기존 실패 모델만 (Responses API)
        categories = ['openai_codex', 'openai_pro', 'openai_thinking_pro']
    else:
        # 전체
        categories = None
    
    try:
        benchmark.run_benchmark(category_filter=categories)
    except KeyboardInterrupt:
        print("\n\n⚠️ 중단됨")
        if benchmark.results:
            benchmark.save_results('benchmark_with_responses_partial.json')
    
    print("\n🎉 완료!")


if __name__ == "__main__":
    run_full_benchmark_with_responses()

