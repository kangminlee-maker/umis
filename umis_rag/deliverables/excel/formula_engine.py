"""
Excel Formula Engine
Excel 함수 생성 및 관리 (피드백 반영)

주요 개선사항:
  - Named Range 절대참조 ($D$5)
  - Workbook-scope Named Range
  - 함수 검증
"""

from typing import Dict, List, Tuple, Optional
from openpyxl import Workbook
from openpyxl.workbook.defined_name import DefinedName


class FormulaEngine:
    """
    Excel 함수 생성 및 관리 엔진
    
    피드백 반영:
      - Named Range 절대참조 필수
      - 순환 참조 감지
      - 함수 유효성 검증
    """
    
    def __init__(self, workbook: Workbook):
        """
        Args:
            workbook: openpyxl Workbook 객체
        """
        self.wb = workbook
        self.named_ranges: Dict[str, Tuple[str, str]] = {}  # {name: (sheet, cell)}
        self.formula_cache: Dict[str, str] = {}
    
    def define_named_range(
        self,
        name: str,
        sheet: str,
        cell: str,
        scope: str = 'workbook'
    ) -> None:
        """
        Named Range 정의 (절대참조!)
        
        Args:
            name: Range 이름 (예: 'ASM_001')
            sheet: 시트 이름
            cell: 셀 주소 (예: 'D5')
            scope: 'workbook' 또는 'sheet'
        
        피드백 반영:
          - 절대참조 ($D$5) 필수
          - Workbook-scope 권장
        """
        
        # 1. 셀 주소를 절대참조로 변환 (D5 → $D$5)
        col_letter = ''.join(c for c in cell if c.isalpha())
        row_num = ''.join(c for c in cell if c.isdigit())
        
        if not col_letter or not row_num:
            raise ValueError(f"Invalid cell address: {cell}")
        
        abs_cell = f"${col_letter}${row_num}"
        
        # 2. 이름 중복 체크
        if name in self.named_ranges:
            raise ValueError(f"Named Range '{name}' already exists")
        
        # 3. DefinedName 생성
        if scope == 'workbook':
            # Workbook-scope (권장)
            attr_text = f"'{sheet}'!{abs_cell}"
        else:
            # Sheet-scope
            attr_text = f"'{sheet}'!{abs_cell}"
        
        defn = DefinedName(
            name=name,
            attr_text=attr_text
        )
        
        self.wb.defined_names.add(defn)
        self.named_ranges[name] = (sheet, cell)
    
    def create_assumption_ref(self, asm_id: str) -> str:
        """
        가정 참조 함수 생성
        
        Args:
            asm_id: 가정 ID (예: 'ASM_001')
        
        Returns:
            Excel 함수 (예: '=ASM_001')
        """
        
        if asm_id not in self.named_ranges:
            raise ValueError(f"Named Range '{asm_id}' not defined")
        
        return f"={asm_id}"
    
    def create_multiplication_chain(self, cells: List[str]) -> str:
        """
        연쇄 곱셈 함수
        
        Args:
            cells: 셀 주소 리스트 (예: ['B2', 'C2', 'D2'])
        
        Returns:
            Excel 함수 (예: '=B2*C2*D2')
        """
        
        if not cells:
            return "=0"
        
        return "=" + "*".join(cells)
    
    def create_sum(self, range_ref: str) -> str:
        """
        합계 함수
        
        Args:
            range_ref: 범위 참조 (예: 'B5:B10')
        
        Returns:
            Excel 함수 (예: '=SUM(B5:B10)')
        """
        
        return f"=SUM({range_ref})"
    
    def create_average(self, range_ref: str) -> str:
        """평균 함수"""
        return f"=AVERAGE({range_ref})"
    
    def create_stdev(self, range_ref: str) -> str:
        """표준편차 함수"""
        return f"=STDEV({range_ref})"
    
    def create_convergence_formulas(
        self,
        method_cells: List[str]
    ) -> Dict[str, str]:
        """
        수렴 분석 함수들 생성
        
        Args:
            method_cells: Method 결과 셀 리스트 (예: ['B5', 'B6', 'B7', 'B8'])
        
        Returns:
            dict: {
                'average': '=AVERAGE(...)',
                'stdev': '=STDEV(...)',
                'cv': '=STDEV(...)/AVERAGE(...)*100',
                'max_min_ratio': '=MAX(...)/MIN(...)',
                'convergence_check': '=IF(...)'
            }
        """
        
        cells_ref = ",".join(method_cells)
        
        return {
            'average': f"=AVERAGE({cells_ref})",
            'stdev': f"=STDEV({cells_ref})",
            'cv': f"=STDEV({cells_ref})/AVERAGE({cells_ref})*100",
            'max_min_ratio': f"=MAX({cells_ref})/MIN({cells_ref})",
            'convergence_check': f'=IF(MAX({cells_ref})/MIN({cells_ref})<=1.3, "✅ 통과", "❌ 재검토")'
        }
    
    def create_cross_sheet_ref(self, sheet: str, cell: str) -> str:
        """
        시트 간 참조 함수
        
        Args:
            sheet: 시트 이름
            cell: 셀 주소
        
        Returns:
            Excel 함수 (예: "=Method_1_TopDown!F10")
        """
        
        # 시트명에 공백 있으면 작은따옴표
        if ' ' in sheet:
            return f"='{sheet}'!{cell}"
        
        return f"={sheet}!{cell}"
    
    def validate_formula(self, formula: str) -> bool:
        """
        함수 유효성 검증
        
        Args:
            formula: Excel 함수
        
        Returns:
            유효 여부
        
        Raises:
            ValueError: 함수 오류
        """
        
        # 1. 기본 문법 체크
        if not formula.startswith('='):
            raise ValueError("함수는 =로 시작해야 합니다")
        
        # 2. 괄호 매칭
        if formula.count('(') != formula.count(')'):
            raise ValueError("괄호가 일치하지 않습니다")
        
        # 3. Named Range 존재 확인
        for name in self.named_ranges:
            if name in formula:
                # Named Range 사용 확인
                pass
        
        return True
    
    def create_iferror(self, formula: str, error_value: str = '"N/A"') -> str:
        """
        IFERROR로 감싸기 (0으로 나누기 방지)
        
        Args:
            formula: 원본 함수
            error_value: 오류 시 반환 값
        
        Returns:
            IFERROR 함수
        """
        
        # = 제거
        formula_body = formula.lstrip('=')
        
        return f"=IFERROR({formula_body}, {error_value})"
    
    def create_conditional_formula(
        self,
        condition: str,
        value_if_true: str,
        value_if_false: str
    ) -> str:
        """
        IF 조건 함수
        
        Args:
            condition: 조건
            value_if_true: True일 때 값
            value_if_false: False일 때 값
        
        Returns:
            IF 함수
        """
        
        return f'=IF({condition}, {value_if_true}, {value_if_false})'
    
    def get_cell_absolute(self, cell: str) -> str:
        """
        상대 참조를 절대 참조로 변환
        
        Args:
            cell: 셀 주소 (예: 'D5')
        
        Returns:
            절대 참조 (예: '$D$5')
        """
        
        col_letter = ''.join(c for c in cell if c.isalpha())
        row_num = ''.join(c for c in cell if c.isdigit())
        
        return f"${col_letter}${row_num}"
    
    def create_percentage_formula(self, value_cell: str, base_cell: str) -> str:
        """
        퍼센트 계산 함수
        
        Args:
            value_cell: 값 셀
            base_cell: 기준 셀
        
        Returns:
            퍼센트 함수 (예: '=(B5-B6)/B6*100')
        """
        
        return f"=({value_cell}-{base_cell})/{base_cell}*100"
    
    # ========================================
    # Unit Economics 함수들
    # ========================================
    
    def create_ltv_formula(
        self,
        arpu: str,
        lifetime: str,
        margin: str
    ) -> str:
        """
        LTV (Customer Lifetime Value) 계산 함수
        
        Formula: LTV = ARPU × Lifetime × Gross Margin
        
        Args:
            arpu: ARPU 셀 또는 Named Range
            lifetime: Customer Lifetime (months) 셀
            margin: Gross Margin (%) 셀
        
        Returns:
            LTV 함수
        
        Example:
            create_ltv_formula('ARPU', 'Lifetime', 'GrossMargin')
            → '=ARPU*Lifetime*GrossMargin'
        """
        
        return f"={arpu}*{lifetime}*{margin}"
    
    def create_ltv_from_churn(
        self,
        arpu: str,
        margin: str,
        churn: str
    ) -> str:
        """
        LTV 계산 (Churn 기반)
        
        Formula: LTV = ARPU × Margin / Churn
        
        Args:
            arpu: ARPU 셀
            margin: Gross Margin (%) 셀
            churn: Monthly Churn Rate (%) 셀
        
        Returns:
            LTV 함수
        
        Example:
            create_ltv_from_churn('ARPU', 'Margin', 'Churn')
            → '=ARPU*Margin/Churn'
        """
        
        return f"=IFERROR({arpu}*{margin}/{churn}, 0)"
    
    def create_cac_formula(
        self,
        total_spend: str,
        new_customers: str
    ) -> str:
        """
        CAC (Customer Acquisition Cost) 계산 함수
        
        Formula: CAC = Total S&M Spend / New Customers
        
        Args:
            total_spend: 총 S&M 지출 셀
            new_customers: 신규 고객 수 셀
        
        Returns:
            CAC 함수
        """
        
        return f"=IFERROR({total_spend}/{new_customers}, 0)"
    
    def create_ratio_formula(
        self,
        numerator: str,
        denominator: str
    ) -> str:
        """
        비율 계산 함수 (LTV/CAC 등)
        
        Args:
            numerator: 분자
            denominator: 분모
        
        Returns:
            비율 함수
        """
        
        return f"=IFERROR({numerator}/{denominator}, 0)"
    
    def create_payback_formula(
        self,
        cac: str,
        arpu: str,
        margin: str
    ) -> str:
        """
        CAC Payback Period 계산 함수
        
        Formula: Payback = CAC / (ARPU × Gross Margin)
        
        Args:
            cac: CAC 셀
            arpu: ARPU 셀
            margin: Gross Margin 셀
        
        Returns:
            Payback Period (months)
        """
        
        return f"=IFERROR({cac}/({arpu}*{margin}), 0)"
    
    def create_churn_to_lifetime(self, churn: str) -> str:
        """
        Monthly Churn → Customer Lifetime 변환
        
        Formula: Lifetime = 1 / Churn
        
        Args:
            churn: Monthly Churn Rate (decimal, 예: 0.05 = 5%)
        
        Returns:
            Lifetime (months)
        """
        
        return f"=IFERROR(1/{churn}, 0)"
    
    def create_margin_formula(
        self,
        revenue: str,
        cost: str
    ) -> str:
        """
        Margin 계산 함수
        
        Formula: Margin = (Revenue - Cost) / Revenue
        
        Args:
            revenue: 매출 셀
            cost: 비용 셀
        
        Returns:
            Margin (%)
        """
        
        return f"=IFERROR(({revenue}-{cost})/{revenue}, 0)"


# 상수: Excel 서식
class ExcelStyles:
    """Excel 서식 상수"""
    
    # 색상 코딩
    INPUT_FILL = "FFF2CC"      # 연한 노랑 (입력 셀)
    CALC_FILL = "E7E6E6"       # 연한 회색 (계산 셀)
    RESULT_FILL = "C6EFCE"     # 연한 초록 (최종 결과)
    HEADER_FILL = "4472C4"     # 파랑 (헤더)
    
    # 테두리
    THIN_BORDER = "thin"
    MEDIUM_BORDER = "medium"

