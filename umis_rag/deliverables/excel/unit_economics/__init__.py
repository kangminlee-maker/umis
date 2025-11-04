"""
UMIS Unit Economics Analyzer Module (완성)

Bill (Quantifier)의 단위 경제성 분석 Excel 자동 생성

생성 시트 (10개):
  1. Dashboard - 요약 대시보드
  2. Inputs - 입력 데이터
  3. LTV_Calculation - LTV 계산 (2가지 방법)
  4. CAC_Analysis - CAC 분석 (채널별)
  5. LTV_CAC_Ratio - 비율 분석 (Traffic Light)
  6. Payback_Period - 회수 기간 (Timeline)
  7. Sensitivity_Analysis - 민감도 분석 (2-Way Matrix)
  8. UE_Scenarios - 시나리오 분석 (Conservative/Base/Optimistic)
  9. Cohort_LTV - 코호트 추적
  10. Benchmark_Comparison - 업계 벤치마크

모듈:
  - unit_economics_generator: 전체 통합 생성기
  - inputs_builder, ltv_builder, cac_builder
  - ratio_builder, payback_builder, sensitivity_builder
  - ue_scenarios_builder, cohort_ltv_builder
  - benchmark_builder, dashboard_builder
"""

from .unit_economics_generator import UnitEconomicsGenerator

__all__ = [
    'UnitEconomicsGenerator'
]

