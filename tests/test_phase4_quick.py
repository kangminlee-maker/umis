"""빠른 Phase 4 테스트 (1개 질문만)"""

import os
import sys
sys.path.insert(0, '.')

from umis_rag.agents.estimator import EstimatorRAG

# 간단한 질문 1개
question = "양자 컴퓨터는 2030년에 몇 대?"

print("\n" + "="*80)
print("🚀 Phase 4 빠른 테스트")
print("="*80)
print(f"\n질문: {question}\n")

estimator = EstimatorRAG()
result = estimator.estimate(question)

if result:
    print(f"\n✅ 완료!")
    print(f"  Phase: {result.phase}")
    print(f"  값: {result.value}")
    print(f"  단위: {result.unit}")
    
    if result.phase == 4:
        print(f"\n🎉 Phase 4 성공!")
else:
    print(f"\n❌ 실패")


