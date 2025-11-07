"""
Quantifier + Guestimation v3.0 통합 테스트
"""

import sys
from pathlib import Path

umis_root = Path(__file__).parent.parent
sys.path.insert(0, str(umis_root))

from umis_rag.agents.quantifier import QuantifierRAG
from umis_rag.agents.estimator import EstimatorRAG


def test_quantifier_estimator():
    """Quantifier + Estimator Agent 통합 테스트"""
    
    print("\n" + "=" * 60)
    print("Quantifier + Estimator (Fermi) Agent 통합 테스트")
    print("=" * 60)
    
    # Quantifier 초기화
    quantifier = QuantifierRAG()
    print("✅ Quantifier 초기화")
    
    # Test Case 1: SaaS Churn Rate
    print("\n" + "-" * 60)
    print("Test Case 1: SaaS Churn Rate")
    print("-" * 60)
    
    result = quantifier.estimate(
        question="B2B SaaS Churn Rate는?",
        domain="B2B_SaaS"
    )
    
    print(f"  Tier: {result.get('tier')}")
    print(f"  값: {result.get('value')}")
    print(f"  신뢰도: {result.get('confidence'):.0%}")
    print(f"  시간: {result.get('execution_time', 0):.2f}초")
    
    if result.get('tier') == 1:
        print(f"  ⚡ Tier 1 (Built-in 또는 학습된 규칙)")
    elif result.get('tier') == 2:
        print(f"  🧠 Tier 2 (종합 판단)")
        print(f"  증거: {result.get('evidence_count')}개")
        print(f"  전략: {result.get('judgment_strategy')}")
        
        if result.get('learned'):
            print(f"  📚 학습됨 (다음엔 Tier 1로 빠름!)")
    
    assert result.get('value') is not None or result.get('tier') == 0, "❌ 추정 실패"
    print("  ✅ 추정 성공")
    
    # Test Case 2: 한국 음식점 월매출
    print("\n" + "-" * 60)
    print("Test Case 2: 한국 음식점 월매출")
    print("-" * 60)
    
    result2 = quantifier.estimate(
        question="한국 음식점 월매출은?",
        domain="Food_Service",
        region="한국"
    )
    
    print(f"  Tier: {result2.get('tier')}")
    print(f"  값: {result2.get('value'):,.0f}원" if result2.get('value') else "  값: None")
    print(f"  신뢰도: {result2.get('confidence'):.0%}")
    
    if result2.get('tier') == 2:
        print(f"  증거: {result2.get('evidence_count')}개")
        print(f"  Boundaries: {result2.get('boundaries')}개")
        print(f"  Soft Guides: {result2.get('soft_guides')}개")
    
    print("  ✅ 추정 완료")
    
    # Test Case 3: 한국 인구 (Built-in)
    print("\n" + "-" * 60)
    print("Test Case 3: 한국 인구 (Built-in)")
    print("-" * 60)
    
    result3 = quantifier.estimate(
        question="한국 인구는?",
        region="한국"
    )
    
    print(f"  Tier: {result3.get('tier')}")
    print(f"  값: {result3.get('value'):,.0f}명" if result3.get('value') else "  값: None")
    print(f"  신뢰도: {result3.get('confidence'):.0%}")
    
    if result3.get('tier') == 1:
        print(f"  ⚡ Tier 1 (Built-in 규칙 매칭)")
        print(f"  추론: {result3.get('reasoning')}")
    
    print("  ✅ 추정 완료")
    
    print("\n" + "=" * 60)
    print("🎉 Quantifier v3.0 통합 테스트 완료!")
    print("=" * 60)
    
    print("\n✅ v7.3.1 개선 사항:")
    print("  - Estimator (Fermi) Agent 통합")
    print("  - 6-Agent 시스템 완성")
    print("  - 간결한 API (estimate)")
    print("  - 학습하는 시스템")


if __name__ == "__main__":
    try:
        test_quantifier_estimator()
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

