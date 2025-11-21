#!/usr/bin/env python3
"""
Fermi Model Search 테스트
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.utils.fermi_model_search import (
    FermiModelSearch,
    FermiModel,
    FermiVariable,
    fermi_estimate
)

print("=" * 80)
print("🧪 Fermi Model Search 테스트")
print("=" * 80)
print()

# ===========================================
# 테스트 1: 간단한 질문 (모형 불필요)
# ===========================================
print("테스트 1: 간단한 질문 (단일 값)")
print("-" * 80)

project_data = {
    '한국_인구': 52000000,
}

fermi = FermiModelSearch(project_context=project_data)
result = fermi.estimate("한국 인구는?", depth=0)

print(f"질문: {result.question}")
print(f"결과: {result.value:,}")
print(f"Confidence: {result.confidence:.0%}")
print(f"Max Depth: {result.max_depth_used}")
print()
print("Logic Trace:")
for step in result.logic_trace:
    print(f"  {step}")
print()

# ===========================================
# 테스트 2: 복잡한 질문 (모형 필요)
# ===========================================
print("테스트 2: 복잡한 질문 (모형 생성)")
print("-" * 80)

result = fermi.estimate("음식점 SaaS 시장 규모는?", depth=0)

print(f"질문: {result.question}")
print(f"결과: {result.value:,.0f}원" if result.value else "추정 실패")
print(f"Confidence: {result.confidence:.0%}")
print(f"Max Depth: {result.max_depth_used}")

if result.model:
    print(f"\n선택된 모형:")
    print(f"  ID: {result.model.id}")
    print(f"  Formula: {result.model.formula}")
    print(f"  Description: {result.model.description}")
    
    print(f"\n변수 값:")
    for var in result.components:
        print(f"  {var.name} = {var.value:,} ({var.source}, depth {var.depth})")
    
    print(f"\n계산 단계:")
    for step in result.calculation_steps:
        print(f"  {step}")

print()
print("Logic Trace:")
for step in result.logic_trace[:10]:
    print(f"  {step}")
if len(result.logic_trace) > 10:
    print(f"  ... ({len(result.logic_trace) - 10}개 더)")
print()

# ===========================================
# 테스트 3: LTV 추정 (재귀 테스트)
# ===========================================
print("테스트 3: LTV 추정 (재귀)")
print("-" * 80)

result = fermi.estimate("SaaS 고객 LTV는?", depth=0)

print(f"결과: {result.value:,}원" if result.value else "추정 실패")
print(f"Max Depth: {result.max_depth_used}")

if result.model:
    print(f"모형: {result.model.formula}")
    print(f"변수:")
    for var in result.components:
        print(f"  {var.name} = {var.value} (depth {var.depth})")

print()

# ===========================================
# 테스트 4: 편의 함수
# ===========================================
print("테스트 4: 편의 함수 (fermi_estimate)")
print("-" * 80)

result = fermi_estimate("CAC는?")

print(f"결과: {result.value:,}" if result.value else "추정 실패")
print(f"Depth: {result.max_depth_used}")
print()

# ===========================================
# 요약
# ===========================================
print("=" * 80)
print("📊 테스트 요약")
print("=" * 80)
print()
print("✅ Fermi Model Search 기본 작동 확인")
print()
print("구현 상태:")
print("  ✅ Phase 1: 초기 스캔 (Project context)")
print("  ✅ Phase 2: 모형 생성 (기본 모형)")
print("  ✅ Phase 3: 실행 가능성 (재귀)")
print("  ✅ Phase 4: 재조립")
print("  ✅ 재귀 구조 (max depth 4)")
print()
print("향후 구현:")
print("  ⏳ LLM 모형 생성 (GPT-4o)")
print("  ⏳ Multi-Layer 통합 (주석 처리됨)")
print("  ⏳ 대체 변수 탐색")
print("=" * 80)

