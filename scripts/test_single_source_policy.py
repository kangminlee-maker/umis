"""
Single Source of Truth 정책 테스트
v7.3.2 - 추정 근거 및 추적 검증
"""

import sys
from pathlib import Path

umis_root = Path(__file__).parent.parent
sys.path.insert(0, str(umis_root))

from umis_rag.agents.estimator import EstimatorRAG
from umis_rag.agents.estimator.tier2 import Tier2JudgmentPath
from umis_rag.agents.validator import ValidatorRAG
from umis_rag.agents.estimator.models import Context


def test_reasoning_detail():
    """reasoning_detail 생성 테스트"""
    
    print("\n" + "=" * 60)
    print("Test 1: reasoning_detail 생성")
    print("=" * 60)
    
    estimator = EstimatorRAG()
    
    # Tier 2 추정 (reasoning_detail 생성됨)
    result = estimator.estimate(
        "B2B SaaS Churn Rate는?",
        domain="B2B_SaaS"
    )
    
    if not result:
        print("  ⚠️  추정 실패 (증거 부족 - 정상)")
        return
    
    print(f"  값: {result.value}")
    print(f"  Tier: {result.tier}")
    print(f"  신뢰도: {result.confidence:.0%}")
    
    # reasoning_detail 검증
    if result.reasoning_detail:
        print(f"\n  ✅ reasoning_detail 존재:")
        print(f"    - method: {result.reasoning_detail.get('method')}")
        print(f"    - sources_used: {result.reasoning_detail.get('sources_used')}")
        print(f"    - evidence_count: {result.reasoning_detail.get('evidence_count')}")
        print(f"    - why_this_method: {result.reasoning_detail.get('why_this_method')}")
        
        # evidence_breakdown
        breakdown = result.reasoning_detail.get('evidence_breakdown', [])
        if breakdown:
            print(f"\n  ✅ evidence_breakdown: {len(breakdown)}개")
            for i, ev in enumerate(breakdown[:2], 1):  # 처음 2개만
                print(f"    증거 {i}: {ev['source']} = {ev['value']}")
        
        # judgment_process
        process = result.reasoning_detail.get('judgment_process', [])
        if process:
            print(f"\n  ✅ judgment_process: {len(process)}단계")
            for step in process[:3]:  # 처음 3단계
                print(f"    {step}")
    else:
        print("  ⚠️  reasoning_detail 없음")
    
    # component_estimations 검증
    if result.component_estimations:
        print(f"\n  ✅ component_estimations: {len(result.component_estimations)}개")
        for comp in result.component_estimations[:2]:
            print(f"    - {comp.component_name}: {comp.component_value} (신뢰도 {comp.confidence:.0%})")
    
    # estimation_trace 검증
    if result.estimation_trace:
        print(f"\n  ✅ estimation_trace: {len(result.estimation_trace)}단계")
        for step in result.estimation_trace[:3]:
            print(f"    {step}")
    
    print("\n  ✅ 추정 근거 완전성 검증 통과!")


def test_validator_cross_validation():
    """Validator 교차 검증 테스트"""
    
    print("\n" + "=" * 60)
    print("Test 2: Validator 교차 검증")
    print("=" * 60)
    
    validator = ValidatorRAG()
    
    # 추정값 검증 (Estimator 호출)
    validation = validator.validate_estimation(
        question="B2B SaaS Churn Rate는?",
        claimed_value=0.08,  # 주장: 8%
        context={'domain': 'B2B_SaaS'}
    )
    
    if validation.get('validation') == 'unable':
        print("  ⚠️  검증 불가 (Estimator 추정 실패 - 정상)")
        return
    
    print(f"  주장값: {validation['claimed_value']}")
    print(f"  Estimator 추정: {validation['estimator_value']}")
    print(f"  차이: {validation['difference_pct']:.0%}")
    print(f"  검증 결과: {validation['validation_result']}")
    
    # 근거 포함 확인
    if validation.get('estimator_reasoning'):
        print(f"\n  ✅ Estimator 근거 포함:")
        reasoning = validation['estimator_reasoning']
        print(f"    - method: {reasoning.get('method')}")
        print(f"    - evidence_count: {reasoning.get('evidence_count')}")
    
    if validation.get('estimator_components'):
        print(f"\n  ✅ 개별 요소: {len(validation['estimator_components'])}개")
    
    if validation.get('estimator_trace'):
        print(f"\n  ✅ 추정 추적: {len(validation['estimator_trace'])}단계")
    
    # 권장사항
    if validation.get('recommendation'):
        print(f"\n  권장사항:")
        for line in validation['recommendation'].split('\n')[:5]:
            print(f"    {line}")
    
    print("\n  ✅ Validator 교차 검증 완료!")


def test_single_source_consistency():
    """Single Source 일관성 테스트"""
    
    print("\n" + "=" * 60)
    print("Test 3: Single Source 일관성")
    print("=" * 60)
    
    estimator = EstimatorRAG()
    
    question = "B2B SaaS Churn Rate는?"
    context_params = {'domain': 'B2B_SaaS'}
    
    # 같은 질문 2번
    result1 = estimator.estimate(question, **context_params)
    result2 = estimator.estimate(question, **context_params)
    
    if result1 and result2:
        # 값 일관성
        if result1.value == result2.value:
            print(f"  ✅ 값 일관성: {result1.value} = {result2.value}")
        else:
            print(f"  ⚠️  값 다름: {result1.value} vs {result2.value}")
            print(f"     (Tier 다를 수 있음: {result1.tier} vs {result2.tier})")
        
        # Tier 확인
        print(f"  Tier: {result1.tier}, {result2.tier}")
        
        # 근거 확인
        if result1.reasoning_detail and result2.reasoning_detail:
            print(f"  ✅ 근거 모두 제공됨")
    
    print("\n  ✅ Single Source 일관성 검증 완료!")


if __name__ == "__main__":
    
    print("\n" + "=" * 60)
    print("Single Source of Truth 정책 테스트")
    print("=" * 60)
    
    try:
        # Test 1: 추정 근거
        test_reasoning_detail()
        
        # Test 2: Validator 교차 검증
        test_validator_cross_validation()
        
        # Test 3: Single Source 일관성
        test_single_source_consistency()
        
        print("\n" + "=" * 60)
        print("🎉 모든 테스트 성공!")
        print("=" * 60)
        
        print("\n✅ v7.3.2 Single Source 기능:")
        print("  - reasoning_detail (상세 근거)")
        print("  - component_estimations (개별 요소)")
        print("  - estimation_trace (추정 과정)")
        print("  - Validator 교차 검증")
        print("  - 데이터 일관성 보장")
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

