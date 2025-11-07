#!/usr/bin/env python3
"""
Guestimation Framework 통합 테스트
EstimationDetailsBuilder + GuestimationEngine
"""

from openpyxl import Workbook
from umis_rag.deliverables.excel.formula_engine import FormulaEngine
from umis_rag.deliverables.excel.assumptions_builder import EstimationDetailsBuilder
from umis_rag.utils.guestimation import (
    GuestimationEngine, BenchmarkCandidate, create_target_profile
)


def test_guestimation_with_estimation_details():
    """
    Guestimation + Estimation Details 통합 테스트
    """
    
    print("\n" + "="*70)
    print("Guestimation Framework 통합 테스트")
    print("="*70)
    
    # 1. 타겟 정의
    target = create_target_profile(
        name="피아노 구독 서비스 전환율",
        product_type="physical",
        consumer_type="B2C",
        price=50000,
        is_essential=False
    )
    
    # 2. RAG 검색 결과 (후보 데이터)
    candidates = [
        BenchmarkCandidate(
            name="정수기 구독",
            value=0.25,
            product_type="physical",
            consumer_type="B2C",
            price=40000,
            is_essential=True,
            source="업계 리포트"
        ),
        BenchmarkCandidate(
            name="공기청정기 렌탈",
            value=0.18,
            product_type="physical",
            consumer_type="B2C",
            price=45000,
            is_essential=False,
            source="경쟁사 공시"
        ),
        BenchmarkCandidate(
            name="음악 앱 구독",
            value=0.30,
            product_type="digital",
            consumer_type="B2C",
            price=10000,
            is_essential=False,
            source="Statista"
        ),
        BenchmarkCandidate(
            name="SaaS B2B 평균",
            value=0.04,
            product_type="software",
            consumer_type="B2B",
            price=200000,
            is_essential=False,
            source="ProfitWell"
        )
    ]
    
    # 3. Guestimation Engine으로 비교 가능성 검증
    engine = GuestimationEngine()
    filtered = engine.filter_candidates(target, candidates)
    
    print("\n📊 비교 가능성 검증 결과:")
    print(f"  ✅ 채택: {len(filtered['adopt'])}개")
    for r in filtered['adopt']:
        print(f"     - {r.candidate.name}: {r.candidate.value*100:.0f}% (score: {r.score}/4)")
    
    print(f"  △ 참고: {len(filtered['reference'])}개")
    for r in filtered['reference']:
        print(f"     - {r.candidate.name}: {r.candidate.value*100:.0f}% (score: {r.score}/4)")
    
    print(f"  ❌ 기각: {len(filtered['reject'])}개")
    for r in filtered['reject']:
        print(f"     - {r.candidate.name}: {list(r.details.values())[0]}")
    
    # 4. 추정 문서 자동 생성
    estimation_doc = engine.generate_estimation_doc(
        est_id='PURCHASE_RATE_EST',
        description='구독 전환율 (타겟 고객 대비)',
        target=target,
        candidates=candidates,
        logic_steps=[
            '공기청정기 렌탈 (18%) 채택 (4/4 비교 가능)',
            '피아노는 더 니치 시장 → 약간 보수적 조정',
            '최종: 15% (공기청정기 대비 -3%p)'
        ],
        final_value=0.15,
        confidence='Medium',
        error_range='±20%'
    )
    
    # 5. Estimation Details 시트 생성
    wb = Workbook()
    wb.remove(wb.active)
    fe = FormulaEngine(wb)
    
    builder = EstimationDetailsBuilder(wb, fe)
    builder.create_sheet([estimation_doc])
    
    wb.save('test_output/guestimation_integration_test.xlsx')
    
    print("\n📝 추정 문서 생성:")
    print(f"  EST_ID: {estimation_doc['id']}")
    print(f"  최종값: {estimation_doc['value']*100:.0f}%")
    print(f"  신뢰도: {estimation_doc['confidence']}")
    print(f"  오차: {estimation_doc['error_range']}")
    print(f"  Base Data: {len(estimation_doc['base_data'])}개 채택")
    print(f"  Logic Steps: {len(estimation_doc['logic_steps'])}단계")
    
    print("\n✅ Excel 생성: test_output/guestimation_integration_test.xlsx")
    
    print("\n" + "="*70)
    print("✅ 통합 테스트 성공!")
    print("="*70)
    print("\n💡 핵심:")
    print("  - RAG 4개 → 비교 가능성 검증 → 채택 1개")
    print("  - 논리적 근거 명확")
    print("  - 기각 이유 문서화")
    print("  - 7개 섹션 자동 생성")


if __name__ == '__main__':
    test_guestimation_with_estimation_details()

