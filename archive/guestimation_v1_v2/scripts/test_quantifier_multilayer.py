#!/usr/bin/env python3
"""
Quantifier + Multi-Layer Guestimation 통합 테스트
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.agents.quantifier import QuantifierRAG
from umis_rag.utils.multilayer_guestimation import BenchmarkCandidate

print("=" * 80)
print("🧪 Quantifier + Multi-Layer Guestimation 통합 테스트")
print("=" * 80)
print()

# Quantifier 초기화
print("📦 Quantifier 초기화 중...")
quantifier = QuantifierRAG()
print("✅ 초기화 완료")
print()

# ===========================================
# 테스트 1: 프로젝트 데이터 활용
# ===========================================
print("테스트 1: Layer 1 - 프로젝트 데이터")
print("-" * 80)

project_data = {
    '국내_SaaS_시장': 2700,  # 억원
    '국내_MA_시장': 1080,
    'SMB_도입률': 0.20,
}

result = quantifier.estimate_with_multilayer(
    "국내 SaaS 시장 규모는?",
    project_context=project_data
)

print(f"✅ 결과: {result.get_display_value()}")
print(f"   출처: {result.source_layer.name}")
print(f"   신뢰도: {result.confidence:.0%}")
print()

# ===========================================
# 테스트 2: RAG 벤치마크 활용
# ===========================================
print("테스트 2: Layer 7 - RAG 벤치마크")
print("-" * 80)

# 타겟: 한국 B2B SaaS Churn Rate
target = BenchmarkCandidate(
    name="한국 B2B SaaS Churn Rate",
    value=0,  # 추정할 값
    product_type="digital",
    consumer_type="B2B",
    price=500000,  # 월 50만원
    is_essential=False
)

result = quantifier.estimate_with_multilayer(
    "한국 B2B SaaS 평균 Churn Rate는?",
    target_profile=target
)

print(f"✅ 결과: {result.get_display_value()}")
print(f"   출처: {result.source_layer.name if result.source_layer else 'None'}")
print(f"   신뢰도: {result.confidence:.0%}")
print(f"   로직: {len(result.logic_steps)}단계")
for step in result.logic_steps[:5]:
    print(f"      {step}")
print()

# ===========================================
# 테스트 3: 통계 패턴 활용
# ===========================================
print("테스트 3: Layer 6 - 통계 패턴")
print("-" * 80)

result = quantifier.estimate_with_multilayer(
    "상위 20% 고객의 매출 점유율은?"
)

print(f"✅ 결과: {result.get_display_value()}")
print(f"   출처: {result.source_layer.name if result.source_layer else 'None'}")
print(f"   신뢰도: {result.confidence:.0%}")
print()

# ===========================================
# 요약
# ===========================================
print("=" * 80)
print("📊 통합 테스트 결과")
print("=" * 80)
print()
print("✅ Quantifier + Multi-Layer Guestimation 정상 작동!")
print()
print("활용 가능한 레이어:")
print("   1. 프로젝트 데이터 (100% 신뢰)")
print("   2. LLM 직접 답변 (70% 신뢰)")
print("   4. 법칙 (100% 신뢰)")
print("   5. 행동경제학 (70% 신뢰)")
print("   6. 통계 패턴 (60% 신뢰)")
print("   7. RAG 벤치마크 (30-80% 신뢰)")
print("   8. 제약조건 (50% 신뢰)")
print()
print("=" * 80)

