#!/usr/bin/env python3
"""
Quantifier Hybrid Guestimation 테스트
E2E 통합 플로우 검증
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.agents.quantifier import QuantifierRAG


def test_auto_mode_low_confidence():
    """Test 1: Auto 모드 - 낮은 신뢰도 → Phase 2"""
    print("\n" + "=" * 70)
    print("Test 1: Auto 모드 - 낮은 신뢰도 (Phase 1→2)")
    print("=" * 70)
    
    bill = QuantifierRAG()
    
    market_def = {
        'market_name': '시니어 케어 로봇 시장',
        'industry': 'healthcare',
        'geography': 'KR',
        'time_horizon': '2030',
        'context': {
            'regulatory': True,  # 규제 산업
            'new_market': True
        }
    }
    
    result = bill.calculate_sam_with_hybrid(
        market_definition=market_def,
        method='auto'
    )
    
    print(f"\n📊 결과:")
    print(f"  Phase 1: {result['phase_1'].get('confidence', 0)*100:.0f}%")
    print(f"  Guardian 권고: {result['recommendation']['recommendation']}")
    print(f"  우선순위: {result['recommendation']['priority']}")
    print(f"  Phase 2 실행 여부: {'예' if result['phase_2'] else '아니오'}")
    print(f"  최종 방법론: {result['method_used']}")
    
    # 검증
    assert result['recommendation']['recommendation'] == 'domain_reasoner', "Phase 2 권고"
    assert result['recommendation']['priority'] == 'required', "규제 → required"
    assert result['phase_2'] is not None, "Phase 2 실행됨"
    assert result['method_used'] == 'domain_reasoner', "Domain Reasoner 사용"
    
    print("\n✅ Test 1 PASSED")
    return result


def test_guestimation_sufficient():
    """Test 2: Auto 모드 - Guestimation 충분"""
    print("\n" + "=" * 70)
    print("Test 2: Auto 모드 - Guestimation 충분 (Phase 1만)")
    print("=" * 70)
    
    bill = QuantifierRAG()
    
    # Phase 1 결과를 높은 신뢰도로 모킹
    bill._execute_guestimation = lambda x: {
        'value': 100_000_000_000,
        'range': (80_000_000_000, 120_000_000_000),
        'confidence': 0.75,  # 높은 신뢰도
        'method': 'guestimation'
    }
    
    market_def = {
        'market_name': '국내 OTT 시장',
        'industry': 'streaming',
        'geography': 'KR',
        'context': {
            'regulatory': False,
            'new_market': False
        }
    }
    
    result = bill.calculate_sam_with_hybrid(
        market_definition=market_def,
        method='auto'
    )
    
    print(f"\n📊 결과:")
    print(f"  Phase 1: {result['phase_1'].get('confidence', 0)*100:.0f}%")
    print(f"  Guardian 권고: {result['recommendation']['recommendation']}")
    print(f"  Phase 2 실행 여부: {'예' if result['phase_2'] else '아니오'}")
    print(f"  최종 방법론: {result['method_used']}")
    
    # 검증
    assert result['recommendation']['recommendation'] == 'guestimation_sufficient', "Guestimation 충분"
    assert result['phase_2'] is None, "Phase 2 실행 안 됨"
    assert result['method_used'] == 'guestimation', "Guestimation 사용"
    
    print("\n✅ Test 2 PASSED")
    return result


def test_explicit_domain_reasoner():
    """Test 3: 명시적 Domain Reasoner 요청"""
    print("\n" + "=" * 70)
    print("Test 3: 명시적 Domain Reasoner 요청")
    print("=" * 70)
    
    bill = QuantifierRAG()
    
    market_def = {
        'market_name': '배달 플랫폼 수수료 시장',
        'industry': 'platform',
        'geography': 'KR',
        'context': {}
    }
    
    result = bill.calculate_sam_with_hybrid(
        market_definition=market_def,
        method='domain_reasoner'  # 명시적 요청
    )
    
    print(f"\n📊 결과:")
    print(f"  Phase 2 실행 여부: {'예' if result['phase_2'] else '아니오'}")
    print(f"  최종 방법론: {result['method_used']}")
    
    if result['phase_2']:
        print(f"  Phase 2 결과:")
        print(f"    - Point Estimate: {result['phase_2'].get('point_estimate', 'N/A')}")
        print(f"    - Should vs Will: {result['phase_2'].get('should_vs_will', 'N/A')}")
    
    # 검증
    assert result['phase_2'] is not None, "Phase 2 실행됨"
    assert result['method_used'] == 'domain_reasoner', "Domain Reasoner 사용"
    
    print("\n✅ Test 3 PASSED")
    return result


def run_all_tests():
    """모든 테스트 실행"""
    print("\n" + "=" * 70)
    print("Quantifier Hybrid Guestimation 통합 테스트")
    print("=" * 70)
    
    tests = [
        ("Test 1: Auto - Phase 2 전환", test_auto_mode_low_confidence),
        ("Test 2: Auto - Phase 1만", test_guestimation_sufficient),
        ("Test 3: 명시적 Domain Reasoner", test_explicit_domain_reasoner),
    ]
    
    results = []
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, 'PASS'))
            passed += 1
        except AssertionError as e:
            results.append((name, 'FAIL'))
            failed += 1
            print(f"\n❌ {name} FAILED: {e}")
        except Exception as e:
            results.append((name, 'ERROR'))
            failed += 1
            print(f"\n💥 {name} ERROR: {e}")
            import traceback
            traceback.print_exc()
    
    # 최종 요약
    print("\n" + "=" * 70)
    print("테스트 결과 요약")
    print("=" * 70)
    
    for name, status in results:
        icon = "✅" if status == 'PASS' else "❌"
        print(f"  {icon} {name}: {status}")
    
    print(f"\n총 {len(tests)}개 테스트: {passed}개 통과, {failed}개 실패")
    
    if failed == 0:
        print("\n🎉 모든 테스트 통과!")
        print("\n✅ Quantifier Hybrid 통합 완료:")
        print("  - calculate_sam_with_hybrid() 구현")
        print("  - Phase 1: Guestimation")
        print("  - Guardian 자동 평가")
        print("  - Phase 2: Domain Reasoner (조건부)")
        print("  - 3가지 모드 (auto, guestimation, domain_reasoner)")
        print("=" * 70)
        return True
    else:
        print("\n⚠️  일부 테스트 실패")
        print("=" * 70)
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)

