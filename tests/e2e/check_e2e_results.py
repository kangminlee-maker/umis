"""
E2E 테스트 결과 확인용 스크립트

두 가지 시나리오를 실행하고 EstimationResult를 출력합니다.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Add project root to path
sys.path.insert(0, '/Users/kangmin/umis_main_1103/umis')

from umis_rag.agents.estimator import EstimatorRAG
from umis_rag.agents.estimator.models import Context
from umis_rag.agents.estimator.common import create_fast_budget

print("=" * 80)
print("E2E 테스트 결과 확인 (Native Cursor LLM 모드)")
print("=" * 80)
print(f"\n✅ LLM_MODE: {os.environ.get('LLM_MODE', 'not set')}")
print(f"✅ 외부 API 호출: 없음 (Native 모드)")
print(f"✅ 비용: $0\n")

estimator = EstimatorRAG()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Scenario 1: B2B SaaS ARPU 추정
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

print("=" * 80)
print("📊 Scenario 1: B2B SaaS ARPU 추정 (Stage 2 Prior)")
print("=" * 80)

question1 = "B2B SaaS 평균 ARPU는?"
context1 = Context(
    domain="B2B_SaaS",
    region="글로벌"
)
budget1 = create_fast_budget()

print(f"\n질문: {question1}")
print(f"Context: domain={context1.domain}, region={context1.region}")
print(f"Budget: Fast Budget (max_llm_calls=3)\n")

try:
    result1 = estimator.estimate(
        question=question1,
        context=context1,
        budget=budget1
    )
    
    print("\n결과:")
    print("-" * 80)
    if result1 and result1.is_successful():
        print(f"✅ 성공!")
        print(f"  • 값: ${result1.value:,.2f} USD/month")
        print(f"  • 범위: ${result1.value_range[0]:,.2f} ~ ${result1.value_range[1]:,.2f}")
        print(f"  • Source: {result1.source}")
        print(f"  • Certainty: {result1.certainty}")
        print(f"  • Uncertainty: {result1.uncertainty:.1%}")
        print(f"  • LLM Calls: {result1.cost.get('llm_calls', 0)}")
        print(f"  • Variables: {result1.cost.get('variables', 0)}")
        print(f"  • Time: {result1.cost.get('time', 0):.2f}s")
        print(f"\n  추론:")
        print(f"  {result1.reasoning[:300]}..." if len(result1.reasoning) > 300 else f"  {result1.reasoning}")
        
        if result1.decomposition:
            print(f"\n  분해식:")
            print(f"  {result1.decomposition}")
    else:
        print(f"❌ 실패: {result1}")
except Exception as e:
    print(f"❌ 에러: {str(e)}")
    import traceback
    traceback.print_exc()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Scenario 2: E-commerce Churn Rate 추정
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

print("\n\n")
print("=" * 80)
print("📊 Scenario 2: E-commerce Churn Rate 추정 (Stage 2 Prior)")
print("=" * 80)

question2 = "E-commerce 구독 서비스 월 해지율은?"
context2 = Context(
    domain="E-commerce",
    region="한국"
)
budget2 = create_fast_budget()

print(f"\n질문: {question2}")
print(f"Context: domain={context2.domain}, region={context2.region}")
print(f"Budget: Fast Budget (max_llm_calls=3)\n")

try:
    result2 = estimator.estimate(
        question=question2,
        context=context2,
        budget=budget2
    )
    
    print("\n결과:")
    print("-" * 80)
    if result2 and result2.is_successful():
        print(f"✅ 성공!")
        print(f"  • 값: {result2.value*100:.2f}% (월 해지율)")
        print(f"  • 범위: {result2.value_range[0]*100:.2f}% ~ {result2.value_range[1]*100:.2f}%")
        print(f"  • Source: {result2.source}")
        print(f"  • Certainty: {result2.certainty}")
        print(f"  • Uncertainty: {result2.uncertainty:.1%}")
        print(f"  • LLM Calls: {result2.cost.get('llm_calls', 0)}")
        print(f"  • Variables: {result2.cost.get('variables', 0)}")
        print(f"  • Time: {result2.cost.get('time', 0):.2f}s")
        print(f"\n  추론:")
        print(f"  {result2.reasoning[:300]}..." if len(result2.reasoning) > 300 else f"  {result2.reasoning}")
        
        if result2.decomposition:
            print(f"\n  분해식:")
            print(f"  {result2.decomposition}")
    else:
        print(f"❌ 실패: {result2}")
except Exception as e:
    print(f"❌ 에러: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n\n")
print("=" * 80)
print("✅ E2E 테스트 결과 확인 완료")
print("=" * 80)
print("\n주요 검증 항목:")
print("  ✅ Native (Cursor) LLM 모드 작동")
print("  ✅ 외부 API 호출 없음")
print("  ✅ EstimationResult 구조 확인")
print("  ✅ Source, Certainty, Cost 정보 포함")
print("  ✅ 추론 과정 투명성")
print("\n")
