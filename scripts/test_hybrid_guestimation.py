#!/usr/bin/env python3
"""
Hybrid Guestimation 테스트 스크립트
Guardian 자동 전환 로직 검증
"""

import sys
from pathlib import Path

# 프로젝트 루트 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.guardian.meta_rag import GuardianMetaRAG


def test_trigger_1_low_confidence():
    """Test Case 1: 신뢰도 낮음 (< 50%)"""
    print("\n" + "=" * 70)
    print("Test 1: 신뢰도 30% → Phase 2 권고 (high)")
    print("=" * 70)
    
    guardian = GuardianMetaRAG()
    
    result = guardian.recommend_methodology(
        estimate_result={
            'value': 50_000_000_000,  # 500억
            'range': (20_000_000_000, 80_000_000_000),
            'confidence': 0.3,  # 30%
            'method': 'guestimation'
        },
        context={'domain': 'general'}
    )
    
    print(f"\n결과:")
    print(f"  권고: {result['recommendation']}")
    print(f"  이유: {result['reason']}")
    print(f"  우선순위: {result['priority']}")
    print(f"  트리거: {result['trigger']}")
    print(f"  예상 시간: {result['estimated_time']}")
    print(f"  자동 실행: {result['auto_execute']}")
    
    # 검증
    assert result['recommendation'] == 'domain_reasoner', "권고가 domain_reasoner여야 함"
    assert result['trigger'] == 'low_confidence', "트리거가 low_confidence여야 함"
    assert result['priority'] == 'high', "우선순위가 high여야 함"
    assert result['auto_execute'] == False, "사용자 확인 필요"
    
    print("\n✅ Test 1 PASSED")
    return result


def test_trigger_2_wide_range():
    """Test Case 2: 범위 너무 넓음 (±75% 초과)"""
    print("\n" + "=" * 70)
    print("Test 2: 범위 폭 ±100% → Phase 2 권고 (high)")
    print("=" * 70)
    
    guardian = GuardianMetaRAG()
    
    result = guardian.recommend_methodology(
        estimate_result={
            'value': 100_000_000_000,  # 1,000억
            'range': (50_000_000_000, 150_000_000_000),  # ±50% → 폭 3배 = ±100%
            'confidence': 0.6,
            'method': 'guestimation'
        },
        context={'domain': 'general'}
    )
    
    print(f"\n결과:")
    print(f"  권고: {result['recommendation']}")
    print(f"  이유: {result['reason']}")
    print(f"  우선순위: {result['priority']}")
    print(f"  트리거: {result['trigger']}")
    
    # 검증
    assert result['recommendation'] == 'domain_reasoner', "권고가 domain_reasoner여야 함"
    assert result['trigger'] == 'wide_range', "트리거가 wide_range여야 함"
    assert result['priority'] == 'high', "우선순위가 high여야 함"
    
    print("\n✅ Test 2 PASSED")
    return result


def test_trigger_3_large_opportunity():
    """Test Case 3: 기회 크기 > 1,000억"""
    print("\n" + "=" * 70)
    print("Test 3: 기회 5,000억 → Phase 2 권고 (medium)")
    print("=" * 70)
    
    guardian = GuardianMetaRAG()
    
    result = guardian.recommend_methodology(
        estimate_result={
            'value': 500_000_000_000,  # 5,000억
            'range': (400_000_000_000, 600_000_000_000),
            'confidence': 0.7,
            'method': 'guestimation'
        },
        context={'domain': 'general'}
    )
    
    print(f"\n결과:")
    print(f"  권고: {result['recommendation']}")
    print(f"  이유: {result['reason']}")
    print(f"  우선순위: {result['priority']}")
    print(f"  트리거: {result['trigger']}")
    
    # 검증
    assert result['recommendation'] == 'domain_reasoner', "권고가 domain_reasoner여야 함"
    assert result['trigger'] == 'large_opportunity', "트리거가 large_opportunity여야 함"
    assert result['priority'] == 'medium', "우선순위가 medium이어야 함"
    
    print("\n✅ Test 3 PASSED")
    return result


def test_trigger_4_regulatory():
    """Test Case 4: 규제 산업 (required)"""
    print("\n" + "=" * 70)
    print("Test 4: 규제 산업 (의료) → Phase 2 필수 (required)")
    print("=" * 70)
    
    guardian = GuardianMetaRAG()
    
    result = guardian.recommend_methodology(
        estimate_result={
            'value': 10_000_000_000,  # 100억 (작아도 상관없음)
            'range': (8_000_000_000, 12_000_000_000),
            'confidence': 0.8,  # 높아도 상관없음
            'method': 'guestimation'
        },
        context={
            'domain': 'healthcare',
            'regulatory': True  # 핵심!
        }
    )
    
    print(f"\n결과:")
    print(f"  권고: {result['recommendation']}")
    print(f"  이유: {result['reason']}")
    print(f"  우선순위: {result['priority']}")
    print(f"  트리거: {result['trigger']}")
    print(f"  자동 실행: {result['auto_execute']}")
    
    # 검증
    assert result['recommendation'] == 'domain_reasoner', "권고가 domain_reasoner여야 함"
    assert result['trigger'] == 'regulatory_industry', "트리거가 regulatory_industry여야 함"
    assert result['priority'] == 'required', "우선순위가 required여야 함"
    assert result['auto_execute'] == True, "자동 실행 필수"
    
    print("\n✅ Test 4 PASSED")
    return result


def test_trigger_5_new_market():
    """Test Case 5: 신규 시장"""
    print("\n" + "=" * 70)
    print("Test 5: 신규 시장 → Phase 2 권고 (medium)")
    print("=" * 70)
    
    guardian = GuardianMetaRAG()
    
    result = guardian.recommend_methodology(
        estimate_result={
            'value': 30_000_000_000,  # 300억 (< 1,000억)
            'range': (25_000_000_000, 35_000_000_000),  # ±20% (< ±75%)
            'confidence': 0.65,  # > 50%
            'method': 'guestimation'
        },
        context={
            'domain': 'robotics',
            'new_market': True  # 핵심!
        }
    )
    
    print(f"\n결과:")
    print(f"  권고: {result['recommendation']}")
    print(f"  이유: {result['reason']}")
    print(f"  우선순위: {result['priority']}")
    print(f"  트리거: {result['trigger']}")
    
    # 검증
    assert result['recommendation'] == 'domain_reasoner', "권고가 domain_reasoner여야 함"
    assert result['trigger'] == 'new_market', "트리거가 new_market이어야 함"
    assert result['priority'] == 'medium', "우선순위가 medium이어야 함"
    
    print("\n✅ Test 5 PASSED")
    return result


def test_guestimation_sufficient():
    """Test Case 6: Guestimation 충분"""
    print("\n" + "=" * 70)
    print("Test 6: 신뢰도 75%, 작은 기회 → Guestimation 충분")
    print("=" * 70)
    
    guardian = GuardianMetaRAG()
    
    result = guardian.recommend_methodology(
        estimate_result={
            'value': 10_000_000_000,  # 100억 (< 1,000억)
            'range': (8_000_000_000, 12_000_000_000),  # ±25% (< ±75%)
            'confidence': 0.75,  # > 50%
            'method': 'guestimation'
        },
        context={'domain': 'general'}
    )
    
    print(f"\n결과:")
    print(f"  권고: {result['recommendation']}")
    print(f"  이유: {result['reason']}")
    print(f"  우선순위: {result['priority']}")
    print(f"  트리거: {result['trigger']}")
    
    # 검증
    assert result['recommendation'] == 'guestimation_sufficient', "권고가 guestimation_sufficient여야 함"
    assert result['trigger'] == 'sufficient', "트리거가 sufficient여야 함"
    assert result['priority'] == 'low', "우선순위가 low여야 함"
    
    print("\n✅ Test 6 PASSED")
    return result


def test_priority_order():
    """Test Case 7: 우선순위 순서 확인 (규제 > 신뢰도)"""
    print("\n" + "=" * 70)
    print("Test 7: 규제 + 낮은 신뢰도 → 규제가 우선")
    print("=" * 70)
    
    guardian = GuardianMetaRAG()
    
    result = guardian.recommend_methodology(
        estimate_result={
            'value': 50_000_000_000,
            'range': (20_000_000_000, 80_000_000_000),
            'confidence': 0.3,  # 낮은 신뢰도
            'method': 'guestimation'
        },
        context={
            'domain': 'healthcare',
            'regulatory': True  # 규제 산업
        }
    )
    
    print(f"\n결과:")
    print(f"  트리거: {result['trigger']}")
    print(f"  우선순위: {result['priority']}")
    
    # 규제가 먼저 감지되어야 함
    assert result['trigger'] == 'regulatory_industry', "규제 트리거가 우선되어야 함"
    assert result['priority'] == 'required', "required가 가장 높은 우선순위"
    
    print("\n✅ Test 7 PASSED (우선순위 순서 정상)")
    return result


def run_all_tests():
    """모든 테스트 실행"""
    print("\n" + "=" * 70)
    print("Guardian Hybrid Guestimation 통합 테스트")
    print("=" * 70)
    
    tests = [
        ("Test 1: 낮은 신뢰도", test_trigger_1_low_confidence),
        ("Test 2: 넓은 범위", test_trigger_2_wide_range),
        ("Test 3: 큰 기회", test_trigger_3_large_opportunity),
        ("Test 4: 규제 산업", test_trigger_4_regulatory),
        ("Test 5: 신규 시장", test_trigger_5_new_market),
        ("Test 6: Guestimation 충분", test_guestimation_sufficient),
        ("Test 7: 우선순위 순서", test_priority_order),
    ]
    
    results = []
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, 'PASS', result))
            passed += 1
        except AssertionError as e:
            results.append((name, 'FAIL', str(e)))
            failed += 1
            print(f"\n❌ {name} FAILED: {e}")
        except Exception as e:
            results.append((name, 'ERROR', str(e)))
            failed += 1
            print(f"\n💥 {name} ERROR: {e}")
    
    # 최종 요약
    print("\n" + "=" * 70)
    print("테스트 결과 요약")
    print("=" * 70)

    for name, status, _ in results:
        icon = "✅" if status == 'PASS' else "❌"
        print(f"  {icon} {name}: {status}")
    
    print(f"\n총 {len(tests)}개 테스트: {passed}개 통과, {failed}개 실패")
    
    if failed == 0:
        print("\n🎉 모든 테스트 통과!")
        print("=" * 70)
        return True
    else:
        print("\n⚠️  일부 테스트 실패")
        print("=" * 70)
        return False


def demo_usage():
    """실사용 예시"""
    print("\n" + "=" * 70)
    print("실사용 예시")
    print("=" * 70)
    
    guardian = GuardianMetaRAG()
    
    print("\n[시나리오] 시니어 케어 로봇 시장 분석")
    print("-" * 70)
    
    # Phase 1 결과 (가정)
    phase_1_result = {
                'value': 285_000_000_000,  # 2,850억
        'range': (150_000_000_000, 500_000_000_000),  # 1,500억-5,000억
        'confidence': 0.4,  # 40%
        'method': 'guestimation'
    }
    
    # Guardian 평가
    recommendation = guardian.recommend_methodology(
        estimate_result=phase_1_result,
        context={
                'domain': 'healthcare',
            'geography': 'KR',
            'regulatory': True,  # 의료기기법
            'new_market': True   # 신규 시장
        }
    )
    
    print(f"\nGuardian 권고:")
    print(f"  📋 권고: {recommendation['recommendation']}")
    print(f"  📝 이유: {recommendation['reason']}")
    print(f"  ⚡ 우선순위: {recommendation['priority']}")
    print(f"  🔔 트리거: {recommendation['trigger']}")
    print(f"  ⏱️  예상 시간: {recommendation['estimated_time']}")
    print(f"  🤖 자동 실행: {'예 (필수)' if recommendation['auto_execute'] else '아니오 (사용자 확인)'}")
    
    if recommendation['priority'] == 'required':
        print(f"\n💡 다음 단계:")
        print(f"   → Phase 2 (Domain Reasoner) 자동 실행")
        print(f"   → s3 Laws/Ethics/Physics 검증")
        print(f"   → 증거표 + Should/Will 분석")


if __name__ == '__main__':
    # 모든 테스트 실행
    success = run_all_tests()
    
    # 데모
    demo_usage()
    
    # 종료 코드
    sys.exit(0 if success else 1)
