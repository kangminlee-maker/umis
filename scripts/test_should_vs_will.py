#!/usr/bin/env python3
"""
Should vs Will 분석 테스트
행동경제학 보정 검증
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.methodologies.domain_reasoner import Signal4_BehavioralEcon


def test_case_1_platform_commission():
    """Test Case 1: 플랫폼 수수료율 (시장 지배력)"""
    print("\n" + "=" * 70)
    print("Test 1: 플랫폼 수수료율 - 시장 지배력 80%")
    print("=" * 70)
    
    signal = Signal4_BehavioralEcon()
    
    fused_result = {
        'value': 0.075,  # 7.5%
        'range': (0.06, 0.09),
        'context': {
            'market_power': 0.8,  # 독과점 80%
            'price_change': False,
            'requires_switch': False
        }
    }
    
    result = signal.adjust_should_vs_will(fused_result)
    
    print(f"\n📊 결과:")
    print(f"  Should (규범적): {result['should']['value']*100:.2f}%")
    print(f"    근거: {result['should']['rationale']}")
    print(f"    용도: {result['should']['use_case']}")
    
    print(f"\n  Will (현실적): {result['will']['value']*100:.2f}%")
    print(f"    근거: {result['will']['rationale']}")
    print(f"    용도: {result['will']['use_case']}")
    
    if result['will']['adjustments']:
        print(f"\n    조정 내역:")
        for adj in result['will']['adjustments']:
            print(f"      - {adj['bias']}: ×{adj['factor']} ({adj['reason']})")
            print(f"        영향: {adj['impact']}")
    
    print(f"\n  Gap:")
    print(f"    절대값: {result['gap']['absolute']*100:.2f}%p")
    print(f"    상대값: {result['gap']['percentage']:.1f}%")
    print(f"    해석: {result['gap']['interpretation']}")
    print(f"    주요 원인: {', '.join(result['gap']['main_drivers'])}")
    
    # 검증
    assert result['should']['value'] == 0.075, "Should는 원래 값 유지"
    assert result['will']['value'] > result['should']['value'], "시장 지배력 → Will 증가"
    assert 'market_power' in result['gap']['main_drivers'], "시장 지배력이 원인"
    
    print("\n✅ Test 1 PASSED")
    return result


def test_case_2_senior_care_robot():
    """Test Case 2: 시니어 케어 로봇 (기술 거부감 + 가격 부담)"""
    print("\n" + "=" * 70)
    print("Test 2: 시니어 케어 로봇 - 기술 거부감 + 가격 부담")
    print("=" * 70)
    
    signal = Signal4_BehavioralEcon()
    
    fused_result = {
        'value': 500_000_000_000,  # 5,000억 (Should)
        'range': (300_000_000_000, 700_000_000_000),
        'context': {
            'tech_resistance': True,  # 노인층 기술 거부감
            'high_price': True,       # 500만원 고가
            'market_power': 0
        }
    }
    
    result = signal.adjust_should_vs_will(fused_result)
    
    print(f"\n📊 결과:")
    print(f"  Should (규범적): {result['should']['value']/1e8:.0f}억 원")
    print(f"    의미: 사회적 필요성 (돌봄 공백)")
    
    print(f"\n  Will (현실적): {result['will']['value']/1e8:.0f}억 원")
    print(f"    의미: 실제 채택 예상")
    
    print(f"\n    조정 내역:")
    for adj in result['will']['adjustments']:
        print(f"      - {adj['bias']}: ×{adj['factor']} ({adj['reason']})")
        print(f"        영향: {adj['impact']}")
    
    print(f"\n  Gap:")
    print(f"    절대값: {result['gap']['absolute']/1e8:.0f}억 원")
    print(f"    상대값: {result['gap']['percentage']:.1f}%")
    print(f"    해석: {result['gap']['interpretation']}")
    
    # 검증
    assert result['should']['value'] == 500_000_000_000, "Should는 원래 값"
    assert result['will']['value'] < result['should']['value'], "장벽 → Will 감소"
    assert len(result['will']['adjustments']) == 2, "2개 편향 적용"
    assert result['gap']['percentage'] > 50, "Gap > 50% (매우 큰 차이)"
    
    # 계산 검증: 0.3 (tech) × 0.6 (price) = 0.18
    expected_will = 500_000_000_000 * 0.3 * 0.6
    assert abs(result['will']['value'] - expected_will) < 1e6, "계산 정확성"
    
    print("\n✅ Test 2 PASSED")
    return result


def test_case_3_subscription_switch():
    """Test Case 3: 구독 전환 (현상유지 편향)"""
    print("\n" + "=" * 70)
    print("Test 3: 구독 전환 - 현상유지 편향")
    print("=" * 70)
    
    signal = Signal4_BehavioralEcon()
    
    fused_result = {
        'value': 0.3,  # 이론적 전환율 30%
        'range': (0.25, 0.35),
        'context': {
            'requires_switch': True,  # 기존 → 신규 전환
            'price_change': False,
            'market_power': 0
        }
    }
    
    result = signal.adjust_should_vs_will(fused_result)
    
    print(f"\n📊 결과:")
    print(f"  Should: {result['should']['value']*100:.0f}% (이론적 전환율)")
    print(f"  Will: {result['will']['value']*100:.0f}% (현실 전환율)")
    print(f"  Gap: {result['gap']['percentage']:.0f}% (현상유지 편향)")
    
    # 검증
    expected_will = 0.3 * 0.5  # 30% × 0.5 = 15%
    assert abs(result['will']['value'] - expected_will) < 0.01, "전환율 50% 적용"
    assert result['gap']['percentage'] == 50.0, "Gap 50%"
    
    print("\n✅ Test 3 PASSED")
    return result


def test_case_4_no_bias():
    """Test Case 4: 편향 없음 (Should = Will)"""
    print("\n" + "=" * 70)
    print("Test 4: 편향 없음 - Should = Will")
    print("=" * 70)
    
    signal = Signal4_BehavioralEcon()
    
    fused_result = {
        'value': 100_000_000_000,  # 1,000억
        'range': (80_000_000_000, 120_000_000_000),
        'context': {
            # 모든 편향 요인 없음
            'price_change': False,
            'requires_switch': False,
            'market_power': 0.5,  # < 0.7 (임계값 미만)
            'tech_resistance': False,
            'high_price': False
        }
    }
    
    result = signal.adjust_should_vs_will(fused_result)
    
    print(f"\n📊 결과:")
    print(f"  Should: {result['should']['value']/1e8:.0f}억")
    print(f"  Will: {result['will']['value']/1e8:.0f}억")
    print(f"  Gap: {result['gap']['percentage']:.1f}%")
    
    # 검증
    assert result['should']['value'] == result['will']['value'], "편향 없으면 동일"
    assert len(result['will']['adjustments']) == 0, "조정 내역 없음"
    assert result['gap']['percentage'] == 0, "Gap 0%"
    assert result['gap']['interpretation'] == "작은 차이 (< 10%)", "차이 없음"
    
    print("\n✅ Test 4 PASSED")
    return result


def test_case_5_multiple_biases():
    """Test Case 5: 복합 편향 (가격 인상 + 전환)"""
    print("\n" + "=" * 70)
    print("Test 5: 복합 편향 - 가격 인상 + 전환 요구")
    print("=" * 70)
    
    signal = Signal4_BehavioralEcon()
    
    fused_result = {
        'value': 0.2,  # 20% (이론적 전환율)
        'range': (0.15, 0.25),
        'context': {
            'price_change': True,      # 가격 인상
            'requires_switch': True,   # 전환 필요
            'market_power': 0
        }
    }
    
    result = signal.adjust_should_vs_will(fused_result)
    
    print(f"\n📊 결과:")
    print(f"  Should: {result['should']['value']*100:.0f}%")
    print(f"  Will: {result['will']['value']*100:.0f}%")
    print(f"  Gap: {result['gap']['percentage']:.0f}%")
    
    print(f"\n  복합 효과:")
    cumulative_factor = 1.0
    for adj in result['will']['adjustments']:
        cumulative_factor *= adj['factor']
        print(f"    - {adj['bias']}: ×{adj['factor']}")
    print(f"  누적: ×{cumulative_factor}")
    
    # 검증
    expected_will = 0.2 * 0.4 * 0.5  # 20% × 0.4 (손실회피) × 0.5 (현상유지) = 4%
    assert abs(result['will']['value'] - expected_will) < 0.001, "복합 효과 계산 정확"
    assert len(result['will']['adjustments']) == 2, "2개 편향"
    assert result['gap']['percentage'] == 80.0, "Gap 80% (복합 효과)"
    
    print("\n✅ Test 5 PASSED")
    return result


def run_all_tests():
    """모든 테스트 실행"""
    print("\n" + "=" * 70)
    print("Should vs Will 분석 테스트")
    print("=" * 70)
    
    tests = [
        ("Test 1: 플랫폼 수수료율", test_case_1_platform_commission),
        ("Test 2: 시니어 케어 로봇", test_case_2_senior_care_robot),
        ("Test 3: 구독 전환", test_case_3_subscription_switch),
        ("Test 4: 편향 없음", test_case_4_no_bias),
        ("Test 5: 복합 편향", test_case_5_multiple_biases),
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
        print("=" * 70)
        return True
    else:
        print("\n⚠️  일부 테스트 실패")
        print("=" * 70)
        return False


def demo_real_world_example():
    """실제 사용 예시"""
    print("\n" + "=" * 70)
    print("실제 사용 예시: 배달 플랫폼 수수료율")
    print("=" * 70)
    
    signal = Signal4_BehavioralEcon()
    
    # 시나리오: 배달 플랫폼 수수료율
    fused_result = {
        'value': 0.08,  # 8% (Guestimation + RAG 합의)
        'range': (0.06, 0.10),
        'context': {
            'market_power': 0.85,  # 배민/쿠팡이츠 과점
            'description': '국내 음식 배달 플랫폼'
        }
    }
    
    result = signal.adjust_should_vs_will(fused_result)
    
    print(f"\n[분석 결과]")
    print(f"  📋 메트릭: 플랫폼 수수료율")
    print(f"  🌍 지역: 한국")
    print(f"  📅 시점: 2025")
    
    print(f"\n  Should (규범적 권고):")
    print(f"    값: {result['should']['value']*100:.1f}%")
    print(f"    의미: 공정 거래 관점에서 적정 수수료")
    print(f"    근거: 편향 제거, 공급-수요 균형")
    
    print(f"\n  Will (현실적 예측):")
    print(f"    값: {result['will']['value']*100:.1f}%")
    print(f"    의미: 실제 시장에서 책정될 수수료")
    print(f"    근거: 시장 지배력 {fused_result['context']['market_power']*100:.0f}%")
    
    print(f"\n  Gap 분석:")
    print(f"    차이: {result['gap']['percentage']:.1f}%")
    print(f"    원인: {result['gap']['main_drivers'][0]}")
    print(f"    해석: {result['gap']['interpretation']}")
    
    print(f"\n💡 의사결정 시사점:")
    print(f"    - 정책 목표: {result['should']['value']*100:.1f}% (공정성)")
    print(f"    - 현실 예상: {result['will']['value']*100:.1f}% (시장 지배력)")
    print(f"    - 개선 방향: 시장 경쟁 촉진 → {result['gap']['percentage']:.1f}% Gap 축소")


if __name__ == '__main__':
    # 모든 테스트 실행
    success = run_all_tests()
    
    # 실사용 예시
    demo_real_world_example()
    
    # 종료 코드
    sys.exit(0 if success else 1)

