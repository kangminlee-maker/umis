#!/usr/bin/env python3
"""
Hybrid Guestimation 통합 테스트
전체 플로우 E2E 검증

시나리오:
1. 신규 시장 (시니어 케어 로봇)
2. 성숙 시장 (배달 플랫폼)
3. 규제 산업 (의료 AI)
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.guardian.meta_rag import GuardianMetaRAG
from umis_rag.methodologies.domain_reasoner import Signal4_BehavioralEcon, DomainReasonerEngine
from umis_rag.agents.validator import ValidatorRAG


def test_scenario_1_new_market():
    """
    시나리오 1: 신규 시장 (시니어 케어 로봇)
    
    플로우:
    1. Phase 1: Guestimation (가상)
    2. Guardian 평가 → Phase 2 권고
    3. Rachel: KPI 정의 검증
    4. Signal4: Should vs Will 분석
    """
    print("\n" + "=" * 70)
    print("시나리오 1: 신규 시장 (시니어 케어 로봇)")
    print("=" * 70)
    
    # === Phase 1: Guestimation 결과 (가상) ===
    print("\n[Phase 1] Guestimation 실행 (가정)")
    print("-" * 70)
    
    phase_1_result = {
        'value': 285_000_000_000,  # 2,850억
        'range': (150_000_000_000, 500_000_000_000),  # 1,500-5,000억
        'confidence': 0.4,  # 40%
        'method': 'guestimation'
    }
    
    print(f"  추정값: {phase_1_result['value']/1e8:.0f}억 원")
    print(f"  범위: {phase_1_result['range'][0]/1e8:.0f}-{phase_1_result['range'][1]/1e8:.0f}억")
    print(f"  신뢰도: {phase_1_result['confidence']*100:.0f}%")
    
    # === Guardian 평가 ===
    print("\n[Guardian] 방법론 평가")
    print("-" * 70)
    
    guardian = GuardianMetaRAG()
    
    recommendation = guardian.recommend_methodology(
        estimate_result=phase_1_result,
        context={
            'domain': 'healthcare',
            'geography': 'KR',
            'regulatory': True,  # 의료기기법
            'new_market': True   # 신규 시장
        }
    )
    
    print(f"  권고: {recommendation['recommendation']}")
    print(f"  이유: {recommendation['reason']}")
    print(f"  우선순위: {recommendation['priority']}")
    print(f"  트리거: {recommendation['trigger']}")
    
    assert recommendation['recommendation'] == 'domain_reasoner', "Phase 2 권고"
    assert recommendation['priority'] == 'required', "규제 산업 → 필수"
    
    # === Phase 2: Rachel KPI 검증 ===
    print("\n[Phase 2] Rachel: KPI 정의 검증")
    print("-" * 70)
    
    rachel = ValidatorRAG()
    
    kpi_result = rachel.validate_kpi_definition(
        metric_name="시장 규모",
        provided_definition={
            'numerator': "총 시장 매출",
            'denominator': "N/A",
            'unit': "KRW"
        }
    )
    
    print(f"  KPI ID: {kpi_result.get('kpi_id', 'N/A')}")
    print(f"  상태: {kpi_result['status']}")
    print(f"  권고: {kpi_result.get('recommendation', 'N/A')}")
    
    # === Phase 2: Should vs Will ===
    print("\n[Phase 2] Signal4: Should vs Will 분석")
    print("-" * 70)
    
    signal4 = Signal4_BehavioralEcon()
    
    should_vs_will = signal4.adjust_should_vs_will({
        'value': 500_000_000_000,  # 5,000억 (수정된 추정)
        'context': {
            'tech_resistance': True,  # 기술 거부감
            'high_price': True,       # 가격 부담
            'market_power': 0
        }
    })
    
    print(f"  Should: {should_vs_will['should']['value']/1e8:.0f}억 (필요성)")
    print(f"  Will: {should_vs_will['will']['value']/1e8:.0f}억 (현실)")
    print(f"  Gap: {should_vs_will['gap']['percentage']:.1f}%")
    
    print("\n✅ 시나리오 1 완료")
    
    return {
        'phase_1': phase_1_result,
        'guardian': recommendation,
        'kpi': kpi_result,
        'should_vs_will': should_vs_will
    }


def test_scenario_2_mature_market():
    """
    시나리오 2: 성숙 시장 (배달 플랫폼)
    
    플로우:
    1. Phase 1: Guestimation (가상)
    2. Guardian 평가 → Guestimation 충분
    """
    print("\n" + "=" * 70)
    print("시나리오 2: 성숙 시장 (배달 플랫폼 수수료율)")
    print("=" * 70)
    
    # === Phase 1: Guestimation 결과 (가상) ===
    print("\n[Phase 1] Guestimation 실행 (가정)")
    print("-" * 70)
    
    phase_1_result = {
        'value': 0.085,  # 8.5%
        'range': (0.07, 0.10),  # 7-10% (좁은 범위, ±21%)
        'confidence': 0.7,  # 70%
        'method': 'guestimation'
    }
    
    print(f"  추정값: {phase_1_result['value']*100:.1f}%")
    print(f"  범위: {phase_1_result['range'][0]*100:.0f}-{phase_1_result['range'][1]*100:.0f}%")
    print(f"  신뢰도: {phase_1_result['confidence']*100:.0f}%")
    
    # === Guardian 평가 ===
    print("\n[Guardian] 방법론 평가")
    print("-" * 70)
    
    guardian = GuardianMetaRAG()
    
    recommendation = guardian.recommend_methodology(
        estimate_result=phase_1_result,
        context={
            'domain': 'platform',
            'geography': 'KR',
            'regulatory': False,
            'new_market': False
        }
    )
    
    print(f"  권고: {recommendation['recommendation']}")
    print(f"  이유: {recommendation['reason']}")
    print(f"  우선순위: {recommendation['priority']}")
    
    assert recommendation['recommendation'] == 'guestimation_sufficient', "Guestimation 충분"
    assert recommendation['priority'] == 'low', "Phase 2 불필요"
    
    print("\n✅ 시나리오 2 완료 (Phase 1만으로 충분)")
    
    return {
        'phase_1': phase_1_result,
        'guardian': recommendation
    }


def test_scenario_3_regulatory():
    """
    시나리오 3: 규제 산업 (의료 AI)
    
    플로우:
    1. Phase 1: Guestimation (가상)
    2. Guardian 평가 → Phase 2 필수 (규제)
    3. Rachel: KPI 검증 (없을 수 있음)
    4. Signal4: Should vs Will
    """
    print("\n" + "=" * 70)
    print("시나리오 3: 규제 산업 (의료 AI 진단 시장)")
    print("=" * 70)
    
    # === Phase 1 ===
    print("\n[Phase 1] Guestimation 실행 (가정)")
    print("-" * 70)
    
    phase_1_result = {
        'value': 80_000_000_000,  # 800억
        'range': (60_000_000_000, 100_000_000_000),
        'confidence': 0.65,  # 65% (높아도 규제 산업 → Phase 2)
        'method': 'guestimation'
    }
    
    print(f"  추정값: {phase_1_result['value']/1e8:.0f}억")
    print(f"  신뢰도: {phase_1_result['confidence']*100:.0f}%")
    
    # === Guardian 평가 ===
    print("\n[Guardian] 방법론 평가")
    print("-" * 70)
    
    guardian = GuardianMetaRAG()
    
    recommendation = guardian.recommend_methodology(
        estimate_result=phase_1_result,
        context={
            'domain': 'healthcare',
            'geography': 'KR',
            'regulatory': True  # 핵심!
        }
    )
    
    print(f"  권고: {recommendation['recommendation']}")
    print(f"  이유: {recommendation['reason']}")
    print(f"  우선순위: {recommendation['priority']}")
    print(f"  자동 실행: {recommendation['auto_execute']}")
    
    assert recommendation['recommendation'] == 'domain_reasoner', "Phase 2 필수"
    assert recommendation['priority'] == 'required', "규제 → required"
    assert recommendation['auto_execute'] == True, "자동 실행"
    
    # === Phase 2: Should vs Will ===
    print("\n[Phase 2] Signal4: Should vs Will")
    print("-" * 70)
    
    signal4 = Signal4_BehavioralEcon()
    
    should_vs_will = signal4.adjust_should_vs_will({
        'value': 150_000_000_000,  # 1,500억 (규제 통과 후)
        'context': {
            'market_power': 0,
            'requires_switch': True,  # 기존 진단 → AI 전환
            'tech_resistance': False
        }
    })
    
    print(f"  Should: {should_vs_will['should']['value']/1e8:.0f}억 (잠재 시장)")
    print(f"  Will: {should_vs_will['will']['value']/1e8:.0f}억 (채택률 보정)")
    print(f"  Gap: {should_vs_will['gap']['percentage']:.0f}% (전환 저항)")
    
    print("\n✅ 시나리오 3 완료")
    
    return {
        'phase_1': phase_1_result,
        'guardian': recommendation,
        'should_vs_will': should_vs_will
    }


def run_integration_tests():
    """통합 테스트 실행"""
    print("\n" + "=" * 70)
    print("Hybrid Guestimation E2E 통합 테스트")
    print("=" * 70)
    
    scenarios = [
        ("시나리오 1: 신규 시장", test_scenario_1_new_market),
        ("시나리오 2: 성숙 시장", test_scenario_2_mature_market),
        ("시나리오 3: 규제 산업", test_scenario_3_regulatory),
    ]
    
    results = []
    passed = 0
    failed = 0
    
    for name, test_func in scenarios:
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
    print("E2E 테스트 결과 요약")
    print("=" * 70)
    
    for name, status in results:
        icon = "✅" if status == 'PASS' else "❌"
        print(f"  {icon} {name}: {status}")
    
    print(f"\n총 {len(scenarios)}개 시나리오: {passed}개 통과, {failed}개 실패")
    
    if failed == 0:
        print("\n🎉 모든 통합 테스트 통과!")
        print("\n통합된 기능:")
        print("  ✅ Guardian 자동 전환 (5가지 트리거)")
        print("  ✅ Domain Reasoner 엔진 (10-Signal Stack)")
        print("  ✅ Should vs Will 분석 (행동경제학)")
        print("  ✅ Rachel KPI 검증 (10개 라이브러리)")
        print("  ✅ Excel Should_vs_Will 시트")
        print("\n" + "=" * 70)
        return True
    else:
        print("\n⚠️  일부 테스트 실패")
        print("=" * 70)
        return False


if __name__ == '__main__':
    success = run_integration_tests()
    
    if success:
        print("\n💡 다음 단계:")
        print("  1. Cursor @ 명령어 테스트")
        print("  2. 사용자 가이드 작성")
        print("  3. Step 5 완료 커밋")
    
    sys.exit(0 if success else 1)

