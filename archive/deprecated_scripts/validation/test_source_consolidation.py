#!/usr/bin/env python3
"""
Source 통합 테스트 (v7.8.0)

LLM + Web 통합 및 Constraints 재설계 검증
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from umis_rag.agents.estimator.source_collector import SourceCollector
from umis_rag.agents.estimator.models import Context
from umis_rag.agents.estimator.sources.soft import LegalNormSource, StatisticalPatternSource
from umis_rag.agents.estimator.sources.physical import UnifiedPhysicalConstraintSource
from umis_rag.utils.logger import logger


def test_ai_augmented_source():
    """AIAugmentedEstimationSource 테스트"""
    
    print("\n" + "=" * 70)
    print("🤖 AIAugmentedEstimationSource 테스트 (LLM + Web 통합)")
    print("=" * 70 + "\n")
    
    collector = SourceCollector(llm_mode="native")
    
    question = "한국 인구는?"
    context = Context(region="South Korea")
    
    # Value Sources 수집
    estimates = collector.ai_augmented.collect(question, context)
    
    if estimates:
        print(f"✅ {len(estimates)}개 estimate 반환")
        
        for est in estimates:
            print(f"\n타입: {est.source_type}")
            print(f"모드: {est.raw_data.get('mode')}")
            
            if 'instruction' in est.raw_data:
                instruction = est.raw_data['instruction']
                print(f"\nInstruction 길이: {len(instruction)}자")
                print(f"\nInstruction 샘플 (처음 300자):")
                print(instruction[:300] + "...")
    else:
        print("❌ estimate 없음")


def test_physical_constraints():
    """Physical Constraints 테스트 (개념 기반)"""
    
    print("\n" + "=" * 70)
    print("📐 Physical Constraints 테스트 (개념 기반)")
    print("=" * 70 + "\n")
    
    physical = UnifiedPhysicalConstraintSource()
    
    test_cases = [
        {
            "question": "SaaS Churn Rate는?",
            "expected_concept": "rate",
            "expected_boundary": (0.0, 1.0)
        },
        {
            "question": "한국 담배 판매량은?",
            "expected_concept": "consumption",
            "context": Context(region="한국")
        },
        {
            "question": "Payback Period는?",
            "expected_concept": "duration",
            "expected_boundary": (0.0, 120.0)
        },
        {
            "question": "한국 인구는?",
            "expected_concept": "count",
            "expected_boundary": None  # 너무 넓음
        }
    ]
    
    for idx, case in enumerate(test_cases, 1):
        print(f"\n테스트 {idx}: {case['question']}")
        print("-" * 70)
        
        context = case.get('context')
        boundaries = physical.collect(case['question'], context)
        
        if boundaries:
            b = boundaries[0]
            print(f"✅ Boundary 발견")
            min_val = b.min_value if b.min_value else 0
            max_val = b.max_value if b.max_value else 0
            print(f"  범위: [{min_val:,.0f}, {max_val:,.0f}]")
            print(f"  근거: {b.reasoning}")
        else:
            print(f"ℹ️  Boundary 없음 (범위 너무 넓거나 개념 파악 불가)")


def test_soft_knockouts():
    """Soft Constraints Knock-out 테스트"""
    
    print("\n" + "=" * 70)
    print("🚫 Soft Constraints Knock-out Gate 테스트")
    print("=" * 70 + "\n")
    
    legal = LegalNormSource()
    statistical = StatisticalPatternSource()
    
    test_cases = [
        {
            "question": "한국 소상공인 평균 시급은?",
            "values": [5000, 11000, 15000],
            "source": legal
        },
        {
            "question": "SaaS Churn Rate는?",
            "values": [0.02, 0.35, 0.60],
            "source": statistical
        }
    ]
    
    for case in test_cases:
        print(f"\n질문: {case['question']}")
        print("-" * 70)
        
        for value in case['values']:
            result = case['source'].validate(case['question'], value)
            
            value_str = f"{value:,.0f}" if value > 1 else f"{value:.2f}"
            
            if result:
                print(f"\n  값: {value_str}")
                print(f"  심각도: {result['severity']}")
                print(f"  메시지:\n{result['message']}")
                print(f"  사용자 확인 필요: {result['user_confirmation_needed']}")
            else:
                print(f"  {value_str} → ✅ 통과")


def test_source_collector():
    """SourceCollector 통합 테스트"""
    
    print("\n" + "=" * 70)
    print("🔄 SourceCollector 통합 테스트")
    print("=" * 70 + "\n")
    
    collector = SourceCollector(llm_mode="native")
    
    question = "한국 인구는?"
    context = Context(region="South Korea")
    
    print(f"질문: {question}")
    print(f"Context: region={context.region}\n")
    
    # 전체 수집
    result = collector.collect_all(question, context, mode="sequential")
    
    print(f"\n수집 결과:")
    print(f"  Physical Constraints: {len(result['boundaries'])}개")
    print(f"  Soft Guides: {len(result['soft_guides'])}개")
    print(f"  Value Estimates: {len(result['value_estimates'])}개")
    print(f"  실행 시간: {result['execution_time']:.2f}초")
    
    # Value Estimates 상세
    if result['value_estimates']:
        print(f"\nValue Estimates 상세:")
        for est in result['value_estimates']:
            print(f"  - {est.source_type.value}: {est.reasoning[:60]}...")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Source 통합 테스트")
    parser.add_argument(
        "--test",
        choices=["ai", "physical", "soft", "collector", "all"],
        default="all",
        help="테스트 유형"
    )
    
    args = parser.parse_args()
    
    if args.test in ["ai", "all"]:
        test_ai_augmented_source()
    
    if args.test in ["physical", "all"]:
        test_physical_constraints()
    
    if args.test in ["soft", "all"]:
        test_soft_knockouts()
    
    if args.test in ["collector", "all"]:
        test_source_collector()
    
    print("\n" + "=" * 70)
    print("테스트 완료")
    print("=" * 70 + "\n")

