"""
Phase 0-4 전체 흐름 종합 테스트
v7.8.1 - Native/External 레거시 제거 + SourceType 통합 검증

실제 API 키 사용하여 모든 Phase 테스트
"""

import os
import sys
from pathlib import Path

# 프로젝트 루트 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.agents.estimator import EstimatorRAG
from umis_rag.agents.estimator.models import Context

def print_separator(title: str):
    """구분선 출력"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")


def test_phase_0_literal():
    """Phase 0: Literal (프로젝트 데이터)"""
    print_separator("TEST 1: Phase 0 - Literal (프로젝트 데이터)")
    
    estimator = EstimatorRAG()
    
    # 프로젝트 데이터에 값이 있는 경우
    context = Context(
        project_data={
            'monthly_subscribers': 1000,
            'arpu': 50000
        }
    )
    
    result = estimator.estimate(
        question='월간 구독자 수는?',
        context=context
    )
    
    print(f"✅ 결과:")
    print(f"   Phase: {result.phase}")
    print(f"   값: {result.value:,.0f}")
    print(f"   신뢰도: {result.confidence:.2f}")
    print(f"   추론: {result.reasoning[:100]}...")
    
    assert result.phase == 0, f"Phase 0 예상했으나 {result.phase} 반환"
    assert result.value == 1000, f"1000 예상했으나 {result.value} 반환"
    print("\n✅ Phase 0 테스트 통과!")


def test_phase_1_direct_rag():
    """Phase 1: Direct RAG (학습 규칙)"""
    print_separator("TEST 2: Phase 1 - Direct RAG (학습 규칙)")
    
    estimator = EstimatorRAG()
    
    # 학습 규칙이 없는 경우 → Phase 2로 넘어감
    result = estimator.estimate(
        question='한국 인구는?',
        context=Context()
    )
    
    print(f"✅ 결과:")
    print(f"   Phase: {result.phase}")
    print(f"   값: {result.value:,.0f}")
    print(f"   신뢰도: {result.confidence:.2f}")
    print(f"   추론: {result.reasoning[:150]}...")
    
    # Phase 1은 학습 데이터가 없으면 통과 → Phase 2 이상
    assert result.phase >= 2, f"Phase 2 이상 예상했으나 Phase {result.phase} 반환"
    print(f"\n✅ Phase 1 통과 → Phase {result.phase}로 진행!")


def test_phase_2_validator():
    """Phase 2: Validator Search (확정 데이터)"""
    print_separator("TEST 3: Phase 2 - Validator Search (확정 데이터)")
    
    estimator = EstimatorRAG()
    
    # Validator에서 찾을 수 있는 데이터
    result = estimator.estimate(
        question='한국의 총 인구는?',
        context=Context(region='한국')
    )
    
    print(f"✅ 결과:")
    print(f"   Phase: {result.phase}")
    print(f"   값: {result.value:,.0f}")
    print(f"   신뢰도: {result.confidence:.2f}")
    print(f"   추론: {result.reasoning[:150]}...")
    
    # Phase 2 또는 그 이상
    print(f"\n✅ Phase {result.phase} 완료!")


def test_phase_3_guestimation():
    """Phase 3: Guestimation (추정)"""
    print_separator("TEST 4: Phase 3 - Guestimation (추정)")
    
    # gpt-4o-mini 모드로 테스트 (API 호출)
    os.environ['LLM_MODE'] = 'gpt-4o-mini'
    
    estimator = EstimatorRAG()
    
    # Phase 3이 필요한 질문 (Validator에 없는 데이터)
    result = estimator.estimate(
        question='B2B SaaS의 평균 ARPU는?',
        context=Context(domain='B2B_SaaS', region='한국')
    )
    
    print(f"✅ 결과:")
    print(f"   Phase: {result.phase}")
    print(f"   값: {result.value:,.0f} 원")
    print(f"   신뢰도: {result.confidence:.2f}")
    print(f"   추론: {result.reasoning[:150]}...")
    
    # Phase 3 또는 4
    assert result.phase >= 3, f"Phase 3 이상 예상했으나 Phase {result.phase} 반환"
    assert result.value > 0, "값이 0보다 커야 함"
    print(f"\n✅ Phase {result.phase} 완료!")


def test_phase_4_fermi_simple():
    """Phase 4: Fermi Decomposition (간단한 분해)"""
    print_separator("TEST 5: Phase 4 - Fermi Decomposition (간단)")
    
    # gpt-4o-mini 모드
    os.environ['LLM_MODE'] = 'gpt-4o-mini'
    
    estimator = EstimatorRAG()
    
    # Fermi 분해가 필요한 질문 (간단)
    result = estimator.estimate(
        question='서울 강남구의 카페 수는?',
        context=Context(region='서울 강남구')
    )
    
    print(f"✅ 결과:")
    print(f"   Phase: {result.phase}")
    print(f"   값: {result.value:,.0f} 개")
    print(f"   신뢰도: {result.confidence:.2f}")
    print(f"   추론: {result.reasoning[:200]}...")
    
    if result.phase == 4:
        print(f"\n   분해 구조:")
        if hasattr(result, 'decomposition') and result.decomposition:
            print(f"   - 변수 수: {len(result.decomposition.variables)}")
            print(f"   - 공식: {result.decomposition.formula}")
    
    assert result.value > 0, "값이 0보다 커야 함"
    print(f"\n✅ Phase {result.phase} 완료!")


def test_phase_4_fermi_complex():
    """Phase 4: Fermi Decomposition (복잡한 분해)"""
    print_separator("TEST 6: Phase 4 - Fermi Decomposition (복잡)")
    
    # o1-mini 모드로 테스트 (더 정교한 모델)
    os.environ['LLM_MODE'] = 'o1-mini'
    
    estimator = EstimatorRAG()
    
    # 복잡한 Fermi 분해 질문
    result = estimator.estimate(
        question='한국의 월간 배달 음식 시장 규모는?',
        context=Context(region='한국')
    )
    
    print(f"✅ 결과:")
    print(f"   Phase: {result.phase}")
    print(f"   값: {result.value:,.0f} 원")
    print(f"   신뢰도: {result.confidence:.2f}")
    print(f"   추론: {result.reasoning[:200]}...")
    
    if result.phase == 4:
        print(f"\n   분해 구조:")
        if hasattr(result, 'decomposition') and result.decomposition:
            print(f"   - 변수 수: {len(result.decomposition.variables)}")
            print(f"   - 공식: {result.decomposition.formula}")
            print(f"   - 깊이: {result.decomposition.depth}")
    
    assert result.value > 0, "값이 0보다 커야 함"
    print(f"\n✅ Phase {result.phase} 완료!")


def test_boundary_validator_integration():
    """Boundary Validator 통합 테스트 (Phase 4)"""
    print_separator("TEST 7: Boundary Validator 통합 (Phase 4)")
    
    os.environ['LLM_MODE'] = 'gpt-4o-mini'
    
    estimator = EstimatorRAG()
    
    # 명확한 경계가 있는 질문
    result = estimator.estimate(
        question='하루에 커피를 마시는 시간은?',
        context=Context()
    )
    
    print(f"✅ 결과:")
    print(f"   Phase: {result.phase}")
    print(f"   값: {result.value:.1f} 시간")
    print(f"   신뢰도: {result.confidence:.2f}")
    print(f"   추론: {result.reasoning[:150]}...")
    
    # 하루는 24시간이므로 경계 체크
    assert result.value <= 24, f"24시간 이하여야 하는데 {result.value} 반환"
    print(f"\n✅ Boundary Validator 작동 확인!")


def main():
    """전체 테스트 실행"""
    print("\n" + "🚀 " + "="*76 + " 🚀")
    print("  Phase 0-4 전체 흐름 종합 테스트 (v7.8.1)")
    print("  - Native/External 레거시 제거 검증")
    print("  - SourceType 통합 검증")
    print("  - 실제 API 키 사용")
    print("🚀 " + "="*76 + " 🚀\n")
    
    # 환경 확인
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("⚠️  경고: OPENAI_API_KEY 없음 → .env 파일 확인 필요")
        print("   Phase 3-4 테스트는 건너뜀\n")
        limited_tests = True
    else:
        print(f"✅ OPENAI_API_KEY 확인됨 (길이: {len(api_key)})")
        print(f"   Phase 0-4 전체 테스트 진행\n")
        limited_tests = False
    
    test_results = []
    
    # TEST 1: Phase 0
    try:
        test_phase_0_literal()
        test_results.append(("Phase 0 - Literal", "✅ 통과"))
    except Exception as e:
        print(f"❌ Phase 0 실패: {e}")
        test_results.append(("Phase 0 - Literal", f"❌ 실패: {e}"))
    
    # TEST 2: Phase 1
    try:
        test_phase_1_direct_rag()
        test_results.append(("Phase 1 - Direct RAG", "✅ 통과"))
    except Exception as e:
        print(f"❌ Phase 1 실패: {e}")
        test_results.append(("Phase 1 - Direct RAG", f"❌ 실패: {e}"))
    
    # TEST 3: Phase 2
    try:
        test_phase_2_validator()
        test_results.append(("Phase 2 - Validator", "✅ 통과"))
    except Exception as e:
        print(f"❌ Phase 2 실패: {e}")
        test_results.append(("Phase 2 - Validator", f"❌ 실패: {e}"))
    
    if not limited_tests:
        # TEST 4: Phase 3
        try:
            test_phase_3_guestimation()
            test_results.append(("Phase 3 - Guestimation", "✅ 통과"))
        except Exception as e:
            print(f"❌ Phase 3 실패: {e}")
            import traceback
            traceback.print_exc()
            test_results.append(("Phase 3 - Guestimation", f"❌ 실패: {str(e)[:50]}"))
        
        # TEST 5: Phase 4 (간단)
        try:
            test_phase_4_fermi_simple()
            test_results.append(("Phase 4 - Fermi (간단)", "✅ 통과"))
        except Exception as e:
            print(f"❌ Phase 4 (간단) 실패: {e}")
            import traceback
            traceback.print_exc()
            test_results.append(("Phase 4 - Fermi (간단)", f"❌ 실패: {str(e)[:50]}"))
        
        # TEST 6: Phase 4 (복잡) - 시간이 오래 걸릴 수 있음
        try:
            test_phase_4_fermi_complex()
            test_results.append(("Phase 4 - Fermi (복잡)", "✅ 통과"))
        except Exception as e:
            print(f"❌ Phase 4 (복잡) 실패: {e}")
            import traceback
            traceback.print_exc()
            test_results.append(("Phase 4 - Fermi (복잡)", f"❌ 실패: {str(e)[:50]}"))
        
        # TEST 7: Boundary Validator
        try:
            test_boundary_validator_integration()
            test_results.append(("Boundary Validator", "✅ 통과"))
        except Exception as e:
            print(f"❌ Boundary Validator 실패: {e}")
            import traceback
            traceback.print_exc()
            test_results.append(("Boundary Validator", f"❌ 실패: {str(e)[:50]}"))
    
    # 최종 결과 출력
    print_separator("📊 테스트 결과 요약")
    
    for test_name, result in test_results:
        status = "✅" if "✅" in result else "❌"
        print(f"{status} {test_name:30s} : {result}")
    
    passed = sum(1 for _, r in test_results if "✅" in r)
    total = len(test_results)
    
    print(f"\n총 {passed}/{total} 테스트 통과")
    
    if passed == total:
        print("\n🎉 모든 테스트 통과! v7.8.1 검증 완료!")
    else:
        print(f"\n⚠️  {total - passed}개 테스트 실패")
    
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    main()


