"""
Financial Projection Model Generator (Batch 5 버전)
재무 예측 모델 Excel 자동 생성

현재 버전: Batch 5 (Assumptions + Revenue + Cost + P&L + CashFlow + Metrics)
향후 추가: Batch 6에서 나머지 6개 시트
"""

from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from openpyxl import Workbook

from ..formula_engine import FormulaEngine
from .fp_assumptions_builder import FPAssumptionsBuilder
from .revenue_builder import RevenueBuilder
from .cost_builder import CostBuilder
from .pl_builder import PLBuilder
from .cashflow_builder import CashFlowBuilder
from .metrics_builder import MetricsBuilder


class FinancialProjectionGenerator:
    """
    Financial Projection Excel 자동 생성기 (Batch 5)
    
    현재 시트 (7개):
      1. Assumptions
      2. Revenue_Buildup
      3. Cost_Structure
      4. PL_3Year
      5. PL_5Year
      6. CashFlow
      7. Key_Metrics
    
    향후 추가 (Batch 6):
      8. Scenarios
      9. BreakEven
      10. DCF_Valuation
      11. Sensitivity
      12. Dashboard
    """
    
    def __init__(self):
        """초기화"""
        self.formula_engine: Optional[FormulaEngine] = None
    
    def generate(
        self,
        market_name: str,
        assumptions_data: Dict,
        segments: List[Dict],
        years: int = 5,
        output_dir: Path = Path('.')
    ) -> Path:
        """
        Financial Projection Workbook 생성 (Batch 4)
        
        Args:
            market_name: 시장/비즈니스 이름
            assumptions_data: 가정 데이터
                {
                    'base_revenue_y0': 1250_0000_0000,
                    'growth_rate_yoy': 0.28,
                    'gross_margin': 0.70,
                    'ebitda_margin': 0.15,
                    'net_margin': 0.10,
                    'sm_percent': 0.30,
                    'rd_percent': 0.15,
                    'ga_percent': 0.10,
                    'tax_rate': 0.25,
                    'discount_rate': 0.12
                }
            segments: 세그먼트 목록
                [
                    {'name': 'B2C', 'y0_revenue': 800_0000_0000, 'growth': 0.15},
                    {'name': 'B2B', 'y0_revenue': 300_0000_0000, 'growth': 0.35},
                    {'name': 'B2G', 'y0_revenue': 150_0000_0000, 'growth': 0.45}
                ]
            years: 예측 년수 (기본 5년)
            output_dir: 출력 디렉토리
        
        Returns:
            생성된 Excel 파일 경로
        """
        
        print(f"🚀 Financial Projection Model 생성 시작")
        print(f"   시장: {market_name}")
        print(f"   버전: Batch 5 (7개 시트)")
        print(f"   예측 기간: {years}년")
        
        # 1. 워크북 초기화
        wb = Workbook()
        self.formula_engine = FormulaEngine(wb)
        
        # 기본 시트 제거
        if 'Sheet' in wb.sheetnames:
            wb.remove(wb['Sheet'])
        
        # 2. Sheet 1: Assumptions
        print(f"   1/7 Assumptions...")
        assumptions_builder = FPAssumptionsBuilder(wb, self.formula_engine)
        assumptions_builder.create_sheet(assumptions_data)
        
        # 3. Sheet 2: Revenue Build-up
        print(f"   2/7 Revenue Build-up...")
        revenue_builder = RevenueBuilder(wb, self.formula_engine)
        revenue_builder.create_sheet(segments, years)
        
        # 4. Sheet 3: Cost Structure
        print(f"   3/7 Cost Structure...")
        cost_builder = CostBuilder(wb, self.formula_engine)
        cost_builder.create_sheet(years)
        
        # 5. Sheet 4: P&L 3 Year (Batch 5)
        print(f"   4/7 P&L 3 Year...")
        pl_3year_builder = PLBuilder(wb, self.formula_engine)
        pl_3year_builder.create_sheet('PL_3Year', years=3, start_year=0, define_named_ranges=False)
        
        # 6. Sheet 5: P&L 5 Year (Batch 5, Named Range 정의)
        print(f"   5/7 P&L 5 Year...")
        pl_5year_builder = PLBuilder(wb, self.formula_engine)
        pl_5year_builder.create_sheet('PL_5Year', years=5, start_year=0, define_named_ranges=True)
        
        # 7. Sheet 6: Cash Flow (Batch 5)
        print(f"   6/7 Cash Flow...")
        cashflow_builder = CashFlowBuilder(wb, self.formula_engine)
        cashflow_builder.create_sheet(years)
        
        # 8. Sheet 7: Key Metrics (Batch 5)
        print(f"   7/7 Key Metrics...")
        metrics_builder = MetricsBuilder(wb, self.formula_engine)
        metrics_builder.create_sheet(years, 'PL_5Year')
        
        # 9. 강제 재계산 설정
        wb.calculation.calcMode = 'auto'
        wb.calculation.fullCalcOnLoad = True
        
        # 10. 저장
        filename = f"financial_projection_{market_name}_{datetime.now().strftime('%Y%m%d')}.xlsx"
        filepath = output_dir / filename
        
        output_dir.mkdir(parents=True, exist_ok=True)
        wb.save(filepath)
        
        print(f"\n✅ Excel 생성 완료: {filepath}")
        print(f"📊 시트: {len(wb.sheetnames)}개")
        print(f"📋 Named Range: {len(self.formula_engine.named_ranges)}개")
        print(f"📋 다음: Batch 6에서 Scenarios, DCF, Dashboard 추가")
        
        return filepath


# 테스트는 별도 스크립트에서
# python scripts/test_financial_projection_batch4.py

