"""
UMIS Financial Projection Model Module

Bill (Quantifier)의 재무 예측 모델 Excel 자동 생성

생성 시트 (12개):
  1. Dashboard - 요약 대시보드
  2. Assumptions - 성장률, Margin, 비용율
  3. Revenue_Buildup - 세그먼트별 매출
  4. Cost_Structure - COGS, OPEX
  5. PL_3Year - 손익계산서 (3년)
  6. PL_5Year - 손익계산서 (5년)
  7. CashFlow - 현금흐름표
  8. Key_Metrics - 핵심 재무 비율
  9. Scenarios - Base/Bull/Bear
  10. BreakEven - 손익분기 분석
  11. DCF_Valuation - 기업 가치 평가
  12. Sensitivity - 민감도 분석

모듈:
  - financial_projection_generator: 전체 통합 생성기
  - fp_assumptions_builder, revenue_builder, cost_builder
  - pl_builder, cashflow_builder, metrics_builder
  - fp_scenarios_builder, breakeven_builder
  - dcf_builder, fp_sensitivity_builder, fp_dashboard_builder
"""

from .financial_projection_generator import FinancialProjectionGenerator

__all__ = [
    'FinancialProjectionGenerator'
]

