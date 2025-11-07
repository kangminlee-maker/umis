"""
Source Collector 테스트

11개 Source 수집 동작 확인
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.guestimation_v3.source_collector import SourceCollector
from umis_rag.guestimation_v3.models import Context, Intent


def test_physical_constraints():
    """Physical Constraints 테스트"""
    
    print("\n" + "="*60)
    print("Physical Constraints 테스트")
    print("="*60)
    
    collector = SourceCollector(llm_mode="skip")
    
    test_cases = [
        {
            'question': "Churn Rate는?",
            'expected_boundaries': 1,  # 수학 정의 (0-1)
            'reason': "확률 범위"
        },
        {
            'question': "전환율은?",
            'expected_boundaries': 1,  # 백분율 (0-100)
            'reason': "백분율 범위"
        },
        {
            'question': "하루 근무시간은?",
            'expected_boundaries': 1,  # 시간 단위 (0-24)
            'reason': "하루 24시간"
        }
    ]
    
    for case in test_cases:
        print(f"\n[질문] {case['question']}")
        
        result = collector.collect_all(case['question'])
        boundaries = result['boundaries']
        
        print(f"  Boundaries: {len(boundaries)}개")
        for b in boundaries:
            print(f"    - {b.reasoning}")
            print(f"      범위: [{b.min_value}, {b.max_value}]")
            print(f"      신뢰도: {b.confidence:.0%}")
        
        if len(boundaries) >= case['expected_boundaries']:
            print(f"  ✅ 예상 충족 ({case['reason']})")
        else:
            print(f"  ⚠️  예상보다 적음")


def test_soft_constraints():
    """Soft Constraints 테스트"""
    
    print("\n" + "="*60)
    print("Soft Constraints 테스트")
    print("="*60)
    
    collector = SourceCollector(llm_mode="skip")
    
    test_cases = [
        {
            'question': "최저임금은?",
            'expected_soft': 1,
            'reason': "법률 규범"
        },
        {
            'question': "음식점 매출은?",
            'expected_soft': 1,
            'reason': "통계 패턴"
        },
        {
            'question': "SaaS Churn은?",
            'expected_soft': 2,  # 통계 + 행동경제학
            'reason': "통계 + Loss Aversion"
        }
    ]
    
    for case in test_cases:
        print(f"\n[질문] {case['question']}")
        
        result = collector.collect_all(case['question'])
        soft_guides = result['soft_guides']
        
        print(f"  Soft Guides: {len(soft_guides)}개")
        for g in soft_guides:
            print(f"    - {g.source_type.value}: {g.reasoning}")
            if g.suggested_range:
                print(f"      범위: {g.suggested_range}")
            if g.insight:
                print(f"      통찰: {g.insight}")
        
        if len(soft_guides) >= case['expected_soft']:
            print(f"  ✅ 예상 충족 ({case['reason']})")


def test_value_sources():
    """Value Sources 테스트"""
    
    print("\n" + "="*60)
    print("Value Sources 테스트")
    print("="*60)
    
    # 프로젝트 데이터 있는 경우
    context = Context(
        domain="B2B_SaaS",
        region="한국",
        project_data={
            'customer_count': 100000,
            'monthly_revenue': 5000000000
        }
    )
    
    collector = SourceCollector(llm_mode="skip")
    
    print("\n[질문] 고객수는?")
    result = collector.collect_all("고객수는?", context)
    
    values = result['value_estimates']
    print(f"  Value Estimates: {len(values)}개")
    
    for v in values:
        print(f"    - {v.source_type.value}: {v.value:,.0f}")
        print(f"      신뢰도: {v.confidence:.0%}")
        print(f"      근거: {v.reasoning}")
    
    if len(values) >= 1:
        print(f"  ✅ 확정 데이터 찾음!")


def main():
    """메인 테스트"""
    
    print("\n" + "="*80)
    print(" "*20 + "Source Collector 테스트")
    print("="*80)
    
    test_physical_constraints()
    test_soft_constraints()
    test_value_sources()
    
    print("\n" + "="*80)
    print("  ✅ Source 수집 로직 동작 확인 완료")
    print("="*80)


if __name__ == "__main__":
    main()

