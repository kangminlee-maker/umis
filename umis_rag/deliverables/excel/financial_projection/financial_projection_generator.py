"""
Financial Projection Model Generator (Batch 4 버전)
재무 예측 모델 Excel 자동 생성

현재 버전: Batch 4 (Assumptions + Revenue + Cost)
향후 추가: Batch 5-6에서 나머지 9개 시트
"""

from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from openpyxl import Workbook

from ..formula_engine import FormulaEngine
from .fp_assumptions_builder import FPAssumptionsBuilder
from .revenue_builder import RevenueBuilder
from .cost_builder import CostBuilder


class FinancialProjectionGenerator:
    """
    Financial Projection Excel 자동 생성기 (Batch 4)
    
    현재 시트 (3개):
      1. Assumptions
      2. Revenue_Buildup
      3. Cost_Structure
    
    향후 추가 (Batch 5-6):
      4. PL_3Year
      5. PL_5Year
      6. CashFlow
      7. Key_Metrics
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
        print(f"   버전: Batch 4 (3개 시트)")
        print(f"   예측 기간: {years}년")
        
        # 1. 워크북 초기화
        wb = Workbook()
        self.formula_engine = FormulaEngine(wb)
        
        # 기본 시트 제거
        if 'Sheet' in wb.sheetnames:
            wb.remove(wb['Sheet'])
        
        # 2. Sheet 1: Assumptions
        print(f"   1/3 Assumptions...")
        assumptions_builder = FPAssumptionsBuilder(wb, self.formula_engine)
        assumptions_builder.create_sheet(assumptions_data)
        
        # 3. Sheet 2: Revenue Build-up
        print(f"   2/3 Revenue Build-up...")
        revenue_builder = RevenueBuilder(wb, self.formula_engine)
        revenue_builder.create_sheet(segments, years)
        
        # 4. Sheet 3: Cost Structure
        print(f"   3/3 Cost Structure...")
        cost_builder = CostBuilder(wb, self.formula_engine)
        cost_builder.create_sheet(years)
        
        # 5. 강제 재계산 설정
        wb.calculation.calcMode = 'auto'
        wb.calculation.fullCalcOnLoad = True
        
        # 6. 저장
        filename = f"financial_projection_{market_name}_{datetime.now().strftime('%Y%m%d')}.xlsx"
        filepath = output_dir / filename
        
        output_dir.mkdir(parents=True, exist_ok=True)
        wb.save(filepath)
        
        print(f"\n✅ Excel 생성 완료: {filepath}")
        print(f"📊 시트: {len(wb.sheetnames)}개 (Assumptions, Revenue_Buildup, Cost_Structure)")
        print(f"📋 Named Range: {len(self.formula_engine.named_ranges)}개")
        print(f"📋 다음: Batch 5에서 P&L, Cash Flow 추가")
        
        return filepath


# 테스트는 별도 스크립트에서
# python scripts/test_financial_projection_batch4.py

