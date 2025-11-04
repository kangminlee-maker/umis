#!/usr/bin/env python3
"""
Hybrid Guestimation 테스트 스크립트
Guardian의 방법론 자동 전환 로직 검증

Usage:
    python scripts/test_hybrid_guestimation.py
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.guardian import GuardianMetaRAG


def test_guardian_recommendation():
    """Guardian 방법론 권고 테스트 (5가지 트리거)"""
    
    print("\n" + "=" * 70)
    print("Guardian 방법론 권고 테스트")
    print("=" * 70)
    
    guardian = GuardianMetaRAG()
    
    # ===== Test Case 1: 신뢰도 낮음 (Trigger 1) =====
    print("\n" + "-" * 70)
    print("Test 1: 신뢰도 낮음 (30% < 50%)")
    print("-" * 70)
    
    result1 = guardian.recommend_methodology(
        estimate_result={
            'value': 50_000_000_000,  # 500억
            'range': (20_000_000_000, 80_000_000_000),  # 200억-800억
            'confidence': 0.3,  # 30%
            'method': 'guestimation'
        },
        context={'domain': 'general'}
    )
    
    print(f"\n결과:")
    print(f"  권고: {result1['recommendation']}")
    print(f"  이유: {result1['reason']}")
    print(f"  우선순위: {result1['priority']}")
    print(f"  트리거: {result1['trigger']}")
    print(f"  예상 시간: {result1['estimated_time']}")
    
    assert result1['recommendation'] == 'domain_reasoner', "신뢰도 낮음 → Domain Reasoner 권고 실패"
    assert result1['trigger'] == 'low_confidence', "트리거 불일치"
    assert result1['priority'] == 'high', "우선순위 불일치"
    
    print("\n  ✅ Test 1 Pass")
    
    # ===== Test Case 2: 범위 넓음 (Trigger 2) =====
    print("\n" + "-" * 70)
    print("Test 2: 범위 폭 과다 (±100% > ±75%)")
    print("-" * 70)
    
    result2 = guardian.recommend_methodology(
        estimate_result={
            'value': 100_000_000_000,  # 1,000억
            'range': (50_000_000_000, 200_000_000_000),  # 500억-2,000억 (4배 = ±100%)
            'confidence': 0.6,  # 60% (충분하지만 범위 넓음)
            'method': 'guestimation'
        },
        context={'domain': 'general'}
    )
    
    print(f"\n결과:")
    print(f"  권고: {result2['recommendation']}")
    print(f"  이유: {result2['reason']}")
    print(f"  우선순위: {result2['priority']}")
    print(f"  트리거: {result2['trigger']}")
    
    assert result2['recommendation'] == 'domain_reasoner', "범위 넓음 → Domain Reasoner 권고 실패"
    assert result2['trigger'] == 'wide_range', "트리거 불일치"
    assert result2['priority'] == 'high', "우선순위 불일치"
    
    print("\n  ✅ Test 2 Pass")
    
    # ===== Test Case 3: 큰 기회 (Trigger 3) =====
    print("\n" + "-" * 70)
    print("Test 3: 큰 기회 (5,000억 > 1,000억)")
    print("-" * 70)
    
    result3 = guardian.recommend_methodology(
        estimate_result={
            'value': 500_000_000_000,  # 5,000억
            'range': (400_000_000_000, 600_000_000_000),  # 4,000-6,000억 (±25%)
            'confidence': 0.7,  # 70% (신뢰도 양호)
            'method': 'guestimation'
        },
        context={'domain': 'general'}
    )
    
    print(f"\n결과:")
    print(f"  권고: {result3['recommendation']}")
    print(f"  이유: {result3['reason']}")
    print(f"  우선순위: {result3['priority']}")
    print(f"  트리거: {result3['trigger']}")
    
    assert result3['recommendation'] == 'domain_reasoner', "큰 기회 → Domain Reasoner 권고 실패"
    assert result3['trigger'] == 'large_opportunity', "트리거 불일치"
    assert result3['priority'] == 'medium', "우선순위 불일치"
    
    print("\n  ✅ Test 3 Pass")
    
    # ===== Test Case 4: 규제 산업 (Trigger 4, 최우선) =====
    print("\n" + "-" * 70)
    print("Test 4: 규제 산업 (의료) - 최우선 트리거")
    print("-" * 70)
    
    result4 = guardian.recommend_methodology(
        estimate_result={
            'value': 10_000_000_000,  # 100억 (작은 기회)
            'range': (8_000_000_000, 12_000_000_000),  # 80-120억 (±25%)
            'confidence': 0.8,  # 80% (신뢰도 높음)
            'method': 'guestimation'
        },
        context={
            'domain': 'healthcare',
            'regulatory': True  # ← 핵심!
        }
    )
    
    print(f"\n결과:")
    print(f"  권고: {result4['recommendation']}")
    print(f"  이유: {result4['reason']}")
    print(f"  우선순위: {result4['priority']}")
    print(f"  트리거: {result4['trigger']}")
    print(f"  자동 실행: {result4['auto_execute']}")
    
    assert result4['recommendation'] == 'domain_reasoner', "규제 산업 → Domain Reasoner 권고 실패"
    assert result4['trigger'] == 'regulatory_industry', "트리거 불일치"
    assert result4['priority'] == 'required', "우선순위 불일치 (required 필수)"
    assert result4['auto_execute'] == True, "자동 실행 플래그 불일치"
    
    print("\n  ✅ Test 4 Pass (최우선 트리거)")
    
    # ===== Test Case 5: 신규 시장 (Trigger 5) =====
    print("\n" + "-" * 70)
    print("Test 5: 신규 시장 (직접 데이터 부족)")
    print("-" * 70)
    
    result5 = guardian.recommend_methodology(
        estimate_result={
            'value': 30_000_000_000,  # 300억
            'range': (25_000_000_000, 35_000_000_000),  # 250-350억 (±20%, 범위 좁음)
            'confidence': 0.6,  # 60% (충분)
            'method': 'guestimation'
        },
        context={
            'domain': 'robotics',
            'new_market': True  # ← 핵심!
        }
    )
    
    print(f"\n결과:")
    print(f"  권고: {result5['recommendation']}")
    print(f"  이유: {result5['reason']}")
    print(f"  우선순위: {result5['priority']}")
    print(f"  트리거: {result5['trigger']}")
    
    assert result5['recommendation'] == 'domain_reasoner', "신규 시장 → Domain Reasoner 권고 실패"
    assert result5['trigger'] == 'new_market', "트리거 불일치"
    assert result5['priority'] == 'medium', "우선순위 불일치"
    
    print("\n  ✅ Test 5 Pass")
    
    # ===== Test Case 6: Guestimation 충분 (트리거 없음) =====
    print("\n" + "-" * 70)
    print("Test 6: Guestimation 충분 (모든 트리거 통과)")
    print("-" * 70)
    
    result6 = guardian.recommend_methodology(
        estimate_result={
            'value': 50_000_000_000,  # 500억 (작음)
            'range': (40_000_000_000, 60_000_000_000),  # 400-600억 (±25%)
            'confidence': 0.75,  # 75% (양호)
            'method': 'guestimation'
        },
        context={
            'domain': 'general',
            'regulatory': False,
            'new_market': False
        }
    )
    
    print(f"\n결과:")
    print(f"  권고: {result6['recommendation']}")
    print(f"  이유: {result6['reason']}")
    print(f"  우선순위: {result6['priority']}")
    print(f"  트리거: {result6['trigger']}")
    
    assert result6['recommendation'] == 'guestimation_sufficient', "Guestimation 충분 판단 실패"
    assert result6['trigger'] == 'sufficient', "트리거 불일치"
    assert result6['priority'] == 'low', "우선순위 불일치"
    
    print("\n  ✅ Test 6 Pass")
    
    # ===== 전체 결과 =====
    print("\n" + "=" * 70)
    print("✅ 모든 테스트 통과!")
    print("=" * 70)
    
    print("\n[테스트 요약]")
    print(f"  ✅ Trigger 1 (신뢰도 낮음): Pass")
    print(f"  ✅ Trigger 2 (범위 넓음): Pass")
    print(f"  ✅ Trigger 3 (큰 기회): Pass")
    print(f"  ✅ Trigger 4 (규제 산업, 최우선): Pass")
    print(f"  ✅ Trigger 5 (신규 시장): Pass")
    print(f"  ✅ Guestimation 충분 (트리거 없음): Pass")
    
    print("\n[우선순위 검증]")
    print(f"  required: 규제 산업 (자동 실행) ✓")
    print(f"  high: 신뢰도 낮음, 범위 넓음 ✓")
    print(f"  medium: 큰 기회, 신규 시장 ✓")
    print(f"  low: Guestimation 충분 ✓")
    
    return True


def test_edge_cases():
    """엣지 케이스 테스트"""
    
    print("\n" + "=" * 70)
    print("엣지 케이스 테스트")
    print("=" * 70)
    
    guardian = GuardianMetaRAG()
    
    # Edge Case 1: 범위 하한이 0 (division by zero 방지)
    print("\n[Edge 1] 범위 하한 0 (무한대 폭)")
    
    result_edge1 = guardian.recommend_methodology(
        estimate_result={
            'value': 100_000_000_000,
            'range': (0, 200_000_000_000),  # 하한 0
            'confidence': 0.7
        }
    )
    
    print(f"  권고: {result_edge1['recommendation']}")
    print(f"  트리거: {result_edge1['trigger']}")
    
    assert result_edge1['recommendation'] == 'domain_reasoner', "범위 무한대 → Domain Reasoner"
    print("  ✅ Pass")
    
    # Edge Case 2: 여러 트리거 동시 (우선순위 테스트)
    print("\n[Edge 2] 여러 트리거 동시 (규제 + 낮은 신뢰도)")
    
    result_edge2 = guardian.recommend_methodology(
        estimate_result={
            'value': 200_000_000_000,  # 2,000억 (큰 기회도 해당)
            'range': (50_000_000_000, 400_000_000_000),  # ±100%
            'confidence': 0.2  # 20% (매우 낮음)
        },
        context={
            'regulatory': True,  # 규제 산업
            'new_market': True   # 신규 시장
        }
    )
    
    print(f"  권고: {result_edge2['recommendation']}")
    print(f"  트리거: {result_edge2['trigger']}")
    print(f"  우선순위: {result_edge2['priority']}")
    
    # 규제 산업이 최우선 → regulatory_industry 트리거
    assert result_edge2['trigger'] == 'regulatory_industry', "우선순위 로직 실패 (규제 최우선)"
    assert result_edge2['priority'] == 'required', "규제 산업 → required"
    
    print("  ✅ Pass (규제 산업 최우선 확인)")
    
    # Edge Case 3: 경계값 테스트 (정확히 50%)
    print("\n[Edge 3] 경계값: 신뢰도 정확히 50%")
    
    result_edge3 = guardian.recommend_methodology(
        estimate_result={
            'value': 50_000_000_000,
            'range': (40_000_000_000, 60_000_000_000),
            'confidence': 0.5  # 정확히 50%
        }
    )
    
    print(f"  권고: {result_edge3['recommendation']}")
    print(f"  트리거: {result_edge3['trigger']}")
    
    # confidence < 0.5 이므로 0.5는 충분
    assert result_edge3['recommendation'] == 'guestimation_sufficient', "경계값 0.5 → 충분"
    print("  ✅ Pass")
    
    # Edge Case 4: 정확히 1,000억
    print("\n[Edge 4] 경계값: 기회 정확히 1,000억")
    
    result_edge4 = guardian.recommend_methodology(
        estimate_result={
            'value': 100_000_000_000,  # 정확히 1,000억
            'range': (80_000_000_000, 120_000_000_000),
            'confidence': 0.7
        }
    )
    
    print(f"  권고: {result_edge4['recommendation']}")
    print(f"  트리거: {result_edge4['trigger']}")
    
    # value > 100_000_000_000 이므로 1,000억은 충분
    assert result_edge4['recommendation'] == 'guestimation_sufficient', "경계값 1,000억 → 충분"
    print("  ✅ Pass")
    
    print("\n" + "=" * 70)
    print("✅ 모든 엣지 케이스 통과!")
    print("=" * 70)


def test_priority_scenarios():
    """우선순위별 시나리오 테스트"""
    
    print("\n" + "=" * 70)
    print("우선순위별 시나리오 테스트")
    print("=" * 70)
    
    guardian = GuardianMetaRAG()
    
    scenarios = [
        {
            'name': '시니어 케어 로봇 (규제 + 신규)',
            'estimate': {
                'value': 285_000_000_000,  # 2,850억
                'range': (150_000_000_000, 500_000_000_000),
                'confidence': 0.4
            },
            'context': {
                'domain': 'healthcare',
                'regulatory': True,
                'new_market': True
            },
            'expected_trigger': 'regulatory_industry',
            'expected_priority': 'required'
        },
        {
            'name': '배달 플랫폼 수수료율 (성숙 시장)',
            'estimate': {
                'value': 0.085,  # 8.5%
                'range': (0.075, 0.095),  # 7.5%-9.5% (±12%, 범위 좁음)
                'confidence': 0.7
            },
            'context': {
                'domain': 'platform',
                'regulatory': False,
                'new_market': False
            },
            'expected_trigger': 'sufficient',
            'expected_priority': 'low'
        },
        {
            'name': '글로벌 AI 시장 (큰 기회)',
            'estimate': {
                'value': 50_000_000_000_000,  # 50조
                'range': (45_000_000_000_000, 55_000_000_000_000),  # 45-55조 (±11%, 범위 좁음)
                'confidence': 0.65
            },
            'context': {
                'domain': 'ai',
                'regulatory': False,
                'new_market': False
            },
            'expected_trigger': 'large_opportunity',
            'expected_priority': 'medium'
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n[Scenario {i}] {scenario['name']}")
        print("-" * 70)
        
        result = guardian.recommend_methodology(
            estimate_result=scenario['estimate'],
            context=scenario['context']
        )
        
        print(f"  권고: {result['recommendation']}")
        print(f"  트리거: {result['trigger']}")
        print(f"  우선순위: {result['priority']}")
        
        assert result['trigger'] == scenario['expected_trigger'], \
            f"시나리오 {i}: 트리거 불일치 (기대: {scenario['expected_trigger']}, 실제: {result['trigger']})"
        
        assert result['priority'] == scenario['expected_priority'], \
            f"시나리오 {i}: 우선순위 불일치"
        
        print(f"  ✅ Pass")
    
    print("\n" + "=" * 70)
    print("✅ 모든 시나리오 통과!")
    print("=" * 70)


if __name__ == '__main__':
    try:
        # 기본 테스트
        test_guardian_recommendation()
        
        # 엣지 케이스
        test_edge_cases()
        
        # 실전 시나리오
        test_priority_scenarios()
        
        # 최종 요약
        print("\n" + "=" * 70)
        print("🎉 Step 2: Guardian 자동 전환 테스트 완료!")
        print("=" * 70)
        print("\n[검증 완료]")
        print("  ✅ 5가지 트리거 모두 작동")
        print("  ✅ 우선순위 로직 정상 (required > high > medium > low)")
        print("  ✅ 엣지 케이스 처리 (경계값, 복수 트리거)")
        print("  ✅ 실전 시나리오 통과 (3개)")
        print("\n다음: Step 3 (Bill Quantifier Should/Will 확장)")
        
    except AssertionError as e:
        print(f"\n❌ 테스트 실패: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 에러 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

