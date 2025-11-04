"""
Assumptions Sheet Builder
가정 시트 생성기

시트 구조:
  - 헤더: ID, Category, Description, Value, Unit, Data_Type, Source, Confidence, Notes
  - 데이터 행: 각 가정
  - Named Range: 각 가정의 Value 셀
  - 서식: 입력 셀 강조, 추정치 코멘트
"""

from typing import List, Dict
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Protection
from openpyxl.comments import Comment

from .formula_engine import FormulaEngine, ExcelStyles


class AssumptionsSheetBuilder:
    """
    Assumptions 시트 빌더
    
    기능:
      - 가정 목록 → Excel 시트
      - Named Range 자동 정의 (절대참조)
      - 입력 셀 서식
      - 추정치 코멘트
      - 시트 보호 (Value만 편집 가능)
    """
    
    def __init__(self, workbook: Workbook, formula_engine: FormulaEngine):
        """
        Args:
            workbook: openpyxl Workbook
            formula_engine: FormulaEngine 인스턴스
        """
        self.wb = workbook
        self.fe = formula_engine
    
    def create_sheet(self, assumptions: List[Dict]) -> None:
        """
        Assumptions 시트 생성
        
        Args:
            assumptions: 가정 목록
                [
                    {
                        'id': 'ASM_001',
                        'category': '인구',
                        'description': '타겟 고객 수',
                        'value': 10000,
                        'unit': '명',
                        'data_type': '직접데이터',  # or '추정치'
                        'source': 'SRC_20241031_001',
                        'confidence': 'High',
                        'notes': '통계청 공식'
                    },
                    ...
                ]
        """
        
        # 1. 시트 생성 (첫 번째 시트로)
        ws = self.wb.create_sheet("Assumptions", 0)
        
        # 2. 헤더 작성
        headers = [
            "ID", "Category", "Description", "Value",
            "Unit", "Data_Type", "Source", "Confidence", "Notes"
        ]
        
        for col_idx, header in enumerate(headers, start=1):
            cell = ws.cell(row=1, column=col_idx)
            cell.value = header
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill(
                start_color=ExcelStyles.HEADER_FILL,
                end_color=ExcelStyles.HEADER_FILL,
                fill_type="solid"
            )
            cell.alignment = Alignment(horizontal="center", vertical="center")
        
        # 열 너비 조정
        ws.column_dimensions['A'].width = 12  # ID
        ws.column_dimensions['B'].width = 15  # Category
        ws.column_dimensions['C'].width = 40  # Description
        ws.column_dimensions['D'].width = 15  # Value
        ws.column_dimensions['E'].width = 10  # Unit
        ws.column_dimensions['F'].width = 15  # Data_Type
        ws.column_dimensions['G'].width = 20  # Source
        ws.column_dimensions['H'].width = 12  # Confidence
        ws.column_dimensions['I'].width = 40  # Notes
        
        # 3. 데이터 행 작성
        for i, asm in enumerate(assumptions, start=2):
            ws.cell(row=i, column=1).value = asm.get('id')
            ws.cell(row=i, column=2).value = asm.get('category')
            ws.cell(row=i, column=3).value = asm.get('description')
            ws.cell(row=i, column=4).value = asm.get('value')
            ws.cell(row=i, column=5).value = asm.get('unit')
            ws.cell(row=i, column=6).value = asm.get('data_type')
            ws.cell(row=i, column=7).value = asm.get('source')
            ws.cell(row=i, column=8).value = asm.get('confidence')
            ws.cell(row=i, column=9).value = asm.get('notes', '')
            
            # Value 셀에 Named Range 정의 (절대참조!)
            asm_id = asm.get('id')
            if asm_id:
                self.fe.define_named_range(
                    name=asm_id,
                    sheet="Assumptions",
                    cell=f"D{i}",  # Value 컬럼
                    scope='workbook'  # Workbook-scope
                )
            
            # Value 셀 서식 (입력 셀)
            value_cell = ws.cell(row=i, column=4)
            value_cell.fill = PatternFill(
                start_color=ExcelStyles.INPUT_FILL,
                end_color=ExcelStyles.INPUT_FILL,
                fill_type="solid"
            )
            value_cell.number_format = '#,##0'
            value_cell.alignment = Alignment(horizontal="right")
            
            # 추정치인 경우 코멘트 추가
            if asm.get('data_type') == '추정치':
                comment_text = (
                    f"추정 논리:\n"
                    f"출처: {asm.get('source', 'N/A')}\n"
                    f"신뢰도: {asm.get('confidence', 'N/A')}\n\n"
                    f"Estimation_Details 시트 참조"
                )
                
                comment = Comment(comment_text, "Bill (Quantifier)")
                ws.cell(row=i, column=1).comment = comment
        
        # 4. 시트 보호 (선택적)
        # Note: 시트 보호는 사용자가 Excel에서 직접 설정 가능
        # ws.protection.sheet = True
        
        # Value 셀만 편집 가능하도록 설정 (시트 보호 시)
        # for row_idx in range(2, len(assumptions) + 2):
        #     ws.cell(row=row_idx, column=4).protection = Protection(locked=False)
        
        # 5. 상단 고정 (헤더 항상 보이게)
        ws.freeze_panes = 'A2'
        
        print(f"   ✅ Assumptions: {len(assumptions)}개 가정, {len(assumptions)}개 Named Range")


class EstimationDetailsBuilder:
    """
    Estimation Details 시트 빌더
    추정치의 논리를 상세히 기록
    """
    
    def __init__(self, workbook: Workbook):
        """
        Args:
            workbook: openpyxl Workbook
        """
        self.wb = workbook
    
    def create_sheet(self, estimations: List[Dict]) -> None:
        """
        Estimation Details 시트 생성
        
        Args:
            estimations: 추정치 목록 (data_type='추정치'인 가정들)
        """
        
        ws = self.wb.create_sheet("Estimation_Details")
        
        # 헤더
        headers = [
            "Estimation_ID", "Description", "Estimation_Logic",
            "Base_Data", "Calculation", "Result", "Source", "Confidence"
        ]
        
        for col_idx, header in enumerate(headers, start=1):
            cell = ws.cell(row=1, column=col_idx)
            cell.value = header
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill(
                start_color=ExcelStyles.HEADER_FILL,
                end_color=ExcelStyles.HEADER_FILL,
                fill_type="solid"
            )
        
        # 열 너비
        ws.column_dimensions['A'].width = 15
        ws.column_dimensions['B'].width = 30
        ws.column_dimensions['C'].width = 50
        ws.column_dimensions['D'].width = 30
        ws.column_dimensions['E'].width = 30
        ws.column_dimensions['F'].width = 15
        ws.column_dimensions['G'].width = 20
        ws.column_dimensions['H'].width = 12
        
        # 데이터
        for i, est in enumerate(estimations, start=2):
            ws.cell(row=i, column=1).value = est.get('id')
            ws.cell(row=i, column=2).value = est.get('description')
            ws.cell(row=i, column=3).value = est.get('estimation_logic', '')
            ws.cell(row=i, column=4).value = est.get('base_data', '')
            ws.cell(row=i, column=5).value = est.get('calculation', '')
            ws.cell(row=i, column=6).value = est.get('value')
            ws.cell(row=i, column=7).value = est.get('source')
            ws.cell(row=i, column=8).value = est.get('confidence')
        
        # 상단 고정
        ws.freeze_panes = 'A2'
        
        print(f"   ✅ Estimation Details: {len(estimations)}개 추정치")

