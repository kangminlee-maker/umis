"""
Unit Economics Workbook Generator (Batch 2 버전)
단위 경제성 분석 Excel 자동 생성

현재 버전: Batch 2 (Inputs + LTV + CAC + Ratio + Payback + Sensitivity + Scenarios)
향후 추가: Batch 3에서 나머지 3개 시트 (Benchmark, Cohort, Dashboard)
"""

from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from openpyxl import Workbook

from ..formula_engine import FormulaEngine
from .inputs_builder import InputsBuilder
from .ltv_builder import LTVBuilder
from .cac_builder import CACBuilder
from .ratio_builder import RatioBuilder
from .payback_builder import PaybackBuilder
from .sensitivity_builder import SensitivityBuilder
from .ue_scenarios_builder import UEScenariosBuilder


class UnitEconomicsGenerator:
    """
    Unit Economics Excel 자동 생성기 (Batch 2)
    
    현재 시트 (7개):
      1. Inputs
      2. LTV_Calculation
      3. CAC_Analysis
      4. LTV_CAC_Ratio
      5. Payback_Period
      6. Sensitivity_Analysis (2-Way Matrix 포함)
      7. UE_Scenarios
    
    향후 추가 (Batch 3):
      8. Cohort_LTV
      9. Benchmark_Comparison
      10. Dashboard
    """
    
    def __init__(self):
        """초기화"""
        self.formula_engine: Optional[FormulaEngine] = None
    
    def generate(
        self,
        market_name: str,
        inputs_data: Dict,
        channels_data: List[Dict] = None,
        output_dir: Path = Path('.')
    ) -> Path:
        """
        Unit Economics Workbook 생성 (Batch 1)
        
        Args:
            market_name: 시장/비즈니스 이름
            inputs_data: 입력 데이터
                {
                    'arpu': 9000,
                    'cac': 25000,
                    'gross_margin': 0.35,
                    'monthly_churn': 0.04,
                    'customer_lifetime': 25,
                    'sm_spend_monthly': 5000000,
                    'new_customers_monthly': 200
                }
            channels_data: 채널별 CAC 데이터 (선택)
            output_dir: 출력 디렉토리
        
        Returns:
            생성된 Excel 파일 경로
        """
        
        print(f"🚀 Unit Economics Workbook 생성 시작")
        print(f"   시장: {market_name}")
        print(f"   버전: Batch 2 (7개 시트)")
        
        # 1. 워크북 초기화
        wb = Workbook()
        self.formula_engine = FormulaEngine(wb)
        
        # 기본 시트 제거
        if 'Sheet' in wb.sheetnames:
            wb.remove(wb['Sheet'])
        
        # 2. Sheet 1: Inputs
        print(f"   1/7 Inputs...")
        inputs_builder = InputsBuilder(wb, self.formula_engine)
        inputs_builder.create_sheet(inputs_data)
        
        # 3. Sheet 2: LTV Calculation
        print(f"   2/7 LTV Calculation...")
        ltv_builder = LTVBuilder(wb, self.formula_engine)
        ltv_builder.create_sheet()
        
        # 4. Sheet 3: CAC Analysis
        print(f"   3/7 CAC Analysis...")
        cac_builder = CACBuilder(wb, self.formula_engine)
        cac_builder.create_sheet(channels_data)
        
        # 5. Sheet 4: LTV/CAC Ratio (Batch 2)
        print(f"   4/7 LTV/CAC Ratio...")
        ratio_builder = RatioBuilder(wb, self.formula_engine)
        ratio_builder.create_sheet()
        
        # 6. Sheet 5: Payback Period (Batch 2)
        print(f"   5/7 Payback Period...")
        payback_builder = PaybackBuilder(wb, self.formula_engine)
        payback_builder.create_sheet()
        
        # 7. Sheet 6: Sensitivity Analysis (Batch 2)
        print(f"   6/7 Sensitivity Analysis...")
        sensitivity_builder = SensitivityBuilder(wb, self.formula_engine)
        sensitivity_builder.create_sheet()
        
        # 8. Sheet 7: Scenarios (Batch 2)
        print(f"   7/7 UE Scenarios...")
        scenarios_builder = UEScenariosBuilder(wb, self.formula_engine)
        scenarios_builder.create_sheet()
        
        # 9. 강제 재계산 설정
        wb.calculation.calcMode = 'auto'
        wb.calculation.fullCalcOnLoad = True
        
        # 10. 저장
        filename = f"unit_economics_{market_name}_{datetime.now().strftime('%Y%m%d')}.xlsx"
        filepath = output_dir / filename
        
        output_dir.mkdir(parents=True, exist_ok=True)
        wb.save(filepath)
        
        print(f"\n✅ Excel 생성 완료: {filepath}")
        print(f"📊 시트: {len(wb.sheetnames)}개")
        print(f"📋 Named Range: {len(self.formula_engine.named_ranges)}개")
        print(f"📋 다음: Batch 3에서 Benchmark, Cohort, Dashboard 추가")
        
        return filepath


# 테스트는 별도 스크립트에서
# python scripts/test_unit_economics.py

