"""
Tier 2 Judgment System 테스트
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.guestimation_v3.tier2 import Tier2JudgmentPath
from umis_rag.guestimation_v3.models import Context, Intent


def test_tier2_basic():
    """Tier 2 기본 동작 테스트"""
    
    print("\n" + "="*60)
    print("Tier 2 기본 동작 테스트")
    print("="*60)
    
    tier2 = Tier2JudgmentPath(llm_mode="skip")
    
    test_cases = [
        {
            'question': "SaaS Churn Rate는?",
            'expected_tier': 2,
            'has_boundaries': True,
            'has_soft': True
        },
        {
            'question': "음식점 월매출은?",
            'expected_tier': 2,
            'has_soft': True
        }
    ]
    
    for case in test_cases:
        print(f"\n[질문] {case['question']}")
        
        result = tier2.estimate(case['question'])
        
        if result:
            print(f"  ✅ Tier 2 처리 성공")
            print(f"     Tier: {result.tier}")
            print(f"     값: {result.get_display_value()}")
            print(f"     신뢰도: {result.confidence:.0%}")
            print(f"     전략: {result.judgment_strategy}")
            print(f"     시간: {result.execution_time:.2f}초")
            
            print(f"\n     수집된 증거:")
            print(f"       - Physical: {len(result.boundaries)}개")
            print(f"       - Soft: {len(result.soft_guides)}개")
            print(f"       - Value: {len(result.value_estimates)}개")
            
            if result.conflicts_detected:
                print(f"\n     ⚠️  충돌: {len(result.conflicts_detected)}개")
            
            if result.should_learn:
                print(f"     📚 학습 가치 있음!")
        else:
            print(f"  ❌ 실패")


def test_tier2_with_context():
    """맥락이 있는 경우"""
    
    print("\n" + "="*60)
    print("맥락 포함 테스트")
    print("="*60)
    
    tier2 = Tier2JudgmentPath(llm_mode="skip")
    
    # 프로젝트 데이터 포함
    context = Context(
        intent=Intent.MAKE_DECISION,
        domain="Food_Service",
        region="한국",
        project_data={
            'customer_per_day': 80
        }
    )
    
    print(f"\n[질문] 고객당 매출은?")
    print(f"  맥락: intent={context.intent.value}")
    print(f"  프로젝트 데이터: {context.project_data}")
    
    result = tier2.estimate("고객당 매출은?", context)
    
    if result:
        print(f"\n  ✅ 처리 완료")
        print(f"     전략: {result.judgment_strategy}")
        print(f"     (make_decision 의도 → conservative 전략 예상)")


def main():
    """메인 테스트"""
    
    print("\n" + "="*80)
    print(" "*20 + "Tier 2 Judgment System 테스트")
    print("="*80)
    
    test_tier2_basic()
    test_tier2_with_context()
    
    print("\n" + "="*80)
    print("  ✅ Tier 2 골격 동작 확인 완료")
    print("  ℹ️  LLM, 웹, RAG Source는 TODO")
    print("="*80)


if __name__ == "__main__":
    main()

