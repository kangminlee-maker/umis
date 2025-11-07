#!/usr/bin/env python3
"""
Multi-Layer Guestimation 테스트
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.utils.multilayer_guestimation import (
    MultiLayerGuestimation,
    BenchmarkCandidate,
    DataSource,
    quick_estimate
)

print("=" * 80)
print("🧪 Multi-Layer Guestimation 테스트")
print("=" * 80)
print()

# ===========================================
# 테스트 1: Layer 1 (프로젝트 데이터)
# ===========================================
print("테스트 1: Layer 1 - 프로젝트 데이터")
print("-" * 80)

project_data = {
    '한국_인구': 52000000,
    '서울_인구': 9500000,
    '음식점_수': 700000,
}

estimator = MultiLayerGuestimation(project_context=project_data)
result = estimator.estimate_with_trace("한국 인구는?")

print()

# ===========================================
# 테스트 2: Layer 4 (법칙)
# ===========================================
print("테스트 2: Layer 4 - 법칙 (시간 제약)")
print("-" * 80)

estimator = MultiLayerGuestimation()
result = estimator.estimate_with_trace("하루는 몇 시간?")

print()

# ===========================================
# 테스트 3: Layer 6 (통계 패턴)
# ===========================================
print("테스트 3: Layer 6 - 통계 패턴 (파레토)")
print("-" * 80)

result = estimator.estimate_with_trace("상위 고객 비율은?")

print()

# ===========================================
# 테스트 4: Layer 7 (RAG 벤치마크)
# ===========================================
print("테스트 4: Layer 7 - RAG 벤치마크 + 비교 검증")
print("-" * 80)

# 타겟: 한국 음식점 재방문 주기
target = BenchmarkCandidate(
    name="한국 음식점 재방문",
    value=0,  # 추정할 값
    product_type="service",
    consumer_type="B2C",
    price=15000,  # 평균 식사 가격
    is_essential=False  # 선택재
)

# RAG에서 검색한 벤치마크 후보들
candidates = [
    BenchmarkCandidate(
        name="미국 레스토랑 재방문",
        value=45,  # 45일
        product_type="service",
        consumer_type="B2C",
        price=25,  # $25
        is_essential=False,
        source="US Restaurant Association"
    ),
    BenchmarkCandidate(
        name="한국 카페 재방문",
        value=30,  # 30일
        product_type="service",
        consumer_type="B2C",
        price=5000,
        is_essential=False,
        source="한국외식산업연구원"
    ),
    BenchmarkCandidate(
        name="코웨이 정수기 해지율",
        value=0.15,  # 15%
        product_type="physical",
        consumer_type="B2C",
        price=35000,
        is_essential=True,  # 필수재
        source="코웨이 IR"
    ),
]

result = estimator.estimate_with_trace(
    "한국 음식점 평균 재방문 주기는?",
    target_profile=target,
    rag_candidates=candidates
)

print()
print("📊 상세 결과:")
print(f"   채택된 벤치마크: {len(result.used_data)}개")
print(f"   기각된 벤치마크: {len(result.rejected_data)}개")
for rejected in result.rejected_data:
    print(f"      - {rejected['name']}: {rejected['reason']}")
print()

# ===========================================
# 테스트 5: Layer 8 (제약조건)
# ===========================================
print("테스트 5: Layer 8 - 제약조건 (Boundary)")
print("-" * 80)

result = estimator.estimate_with_trace("음식점 재방문 주기는?")

print()

# ===========================================
# 테스트 6: quick_estimate 함수
# ===========================================
print("테스트 6: quick_estimate 함수 (편의 함수)")
print("-" * 80)

value = quick_estimate(
    "한국 음식점 재방문 주기는?",
    rag_candidates=candidates
)

print(f"결과: {value}")
print()

# ===========================================
# 레이어 순서 확인
# ===========================================
print("=" * 80)
print("📋 활성화된 레이어 순서:")
print("=" * 80)

sequence = estimator.get_layer_sequence()
for item in sequence:
    print(f"   {item}")

print()
print("=" * 80)
print("✅ 테스트 완료!")
print("=" * 80)

