"""
Revenue Build-up Sheet Builder
세그먼트별 매출 구축 시트

Sheet 3: Revenue_Buildup
- Year 0 ~ Year 5 매출
- 세그먼트별 (B2C, B2B, B2G, Global 등)
- 성장률 적용
- 총 매출 계산
"""

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

from ..formula_engine import FormulaEngine, ExcelStyles


class RevenueBuilder:
    """
    Revenue Build-up 시트 빌더
    
    기능:
      - 세그먼트별 매출 예측
      - 연도별 성장률 적용
      - 총 매출 자동 계산
    """
    
    def __init__(self, workbook: Workbook, formula_engine: FormulaEngine):
        """
        Args:
            workbook: openpyxl Workbook
            formula_engine: FormulaEngine 인스턴스
        """
        self.wb = workbook
        self.fe = formula_engine
    
    def create_sheet(
        self,
        segments: list = None,
        years: int = 5
    ) -> None:
        """
        Revenue Build-up 시트 생성
        
        Args:
            segments: 세그먼트 목록
                [
                    {'name': 'B2C', 'y0_revenue': 80_0000_0000, 'growth': 0.15},
                    {'name': 'B2B', 'y0_revenue': 30_0000_0000, 'growth': 0.35},
                    {'name': 'B2G', 'y0_revenue': 15_0000_0000, 'growth': 0.45},
                ]
            years: 예측 년수 (기본 5년)
        """
        
        # 기본 세그먼트
        if segments is None:
            segments = [
                {'name': 'B2C (개인)', 'y0_revenue': 700_0000_0000, 'growth': 0.10},
                {'name': 'B2B (기업)', 'y0_revenue': 200_0000_0000, 'growth': 0.30},
                {'name': 'B2G (정부)', 'y0_revenue': 100_0000_0000, 'growth': 0.40},
            ]
        
        ws = self.wb.create_sheet("Revenue_Buildup")
        
        # === 1. 제목 ===
        ws['A1'] = "Revenue Build-up (세그먼트별)"
        ws['A1'].font = Font(size=14, bold=True, color="FFFFFF")
        ws['A1'].fill = PatternFill(start_color=ExcelStyles.HEADER_FILL, end_color=ExcelStyles.HEADER_FILL, fill_type="solid")
        ws['A1'].alignment = Alignment(horizontal='center', vertical='center')
        ws.merge_cells('A1:H1')
        ws.row_dimensions[1].height = 30
        
        ws['A2'] = f"Year 0 ~ Year {years} 매출 예측 (세그먼트별 성장률)"
        ws['A2'].font = Font(size=10, italic=True, color="666666")
        ws.merge_cells('A2:H2')
        
        # 컬럼 폭
        ws.column_dimensions['A'].width = 20
        for col in ['B', 'C', 'D', 'E', 'F', 'G', 'H']:
            ws.column_dimensions[col].width = 15
        
        # === 2. 컬럼 헤더 ===
        row = 4
        header_font = Font(size=10, bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color=ExcelStyles.HEADER_FILL, end_color=ExcelStyles.HEADER_FILL, fill_type="solid")
        
        # 헤더 (Segment, Year 0 ~ Year 5, Growth)
        year_headers = ['Segment'] + [f'Year {y}' for y in range(years + 1)] + ['Growth %']
        
        for col_idx, header in enumerate(year_headers, start=1):
            cell = ws.cell(row=row, column=col_idx)
            cell.value = header
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal='center')
        
        # === 3. 세그먼트별 매출 ===
        input_fill = PatternFill(start_color=ExcelStyles.INPUT_FILL, end_color=ExcelStyles.INPUT_FILL, fill_type="solid")
        
        segment_rows = []
        
        for seg in segments:
            row += 1
            segment_rows.append(row)
            
            # A: Segment 이름
            ws.cell(row=row, column=1).value = seg['name']
            ws.cell(row=row, column=1).font = Font(size=10, bold=True)
            
            # B: Year 0 (입력)
            ws.cell(row=row, column=2).value = seg['y0_revenue']
            ws.cell(row=row, column=2).fill = input_fill
            ws.cell(row=row, column=2).number_format = '#,##0'
            
            # C-G: Year 1-5 (성장률 적용)
            for year in range(1, years + 1):
                col = 2 + year  # C=3, D=4, ...
                prev_col_letter = chr(65 + col - 1)  # B, C, D, ...
                
                # 세그먼트별 성장률 사용
                growth_cell = f'${chr(65 + years + 2)}${row}'  # Last column (Growth %)
                ws.cell(row=row, column=col).value = f'={prev_col_letter}{row}*(1+{growth_cell})'
                ws.cell(row=row, column=col).number_format = '#,##0'
            
            # H: Growth % (입력)
            ws.cell(row=row, column=years + 2).value = seg['growth']
            ws.cell(row=row, column=years + 2).fill = input_fill
            ws.cell(row=row, column=years + 2).number_format = '0.0%'
        
        # === 4. 총 매출 (Total Revenue) ===
        row += 1
        ws.cell(row=row, column=1).value = "Total Revenue"
        ws.cell(row=row, column=1).font = Font(size=11, bold=True, color="FFFFFF")
        ws.cell(row=row, column=1).fill = PatternFill(start_color="2E75B6", end_color="2E75B6", fill_type="solid")
        
        # Year 0 ~ Year 5 합계
        for year in range(years + 1):
            col = 2 + year
            col_letter = chr(65 + col)  # B, C, D, ...
            
            # 세그먼트 합계
            first_seg_row = segment_rows[0]
            last_seg_row = segment_rows[-1]
            
            ws.cell(row=row, column=col).value = f'=SUM({col_letter}{first_seg_row}:{col_letter}{last_seg_row})'
            ws.cell(row=row, column=col).number_format = '#,##0'
            ws.cell(row=row, column=col).font = Font(size=11, bold=True, color="FFFFFF")
            ws.cell(row=row, column=col).fill = PatternFill(start_color="2E75B6", end_color="2E75B6", fill_type="solid")
            
            # Named Range (Year별 총 매출)
            if year == 0:
                self.fe.define_named_range('Revenue_Y0', 'Revenue_Buildup', f'{col_letter}{row}')
            elif year <= 5:
                self.fe.define_named_range(f'Revenue_Y{year}', 'Revenue_Buildup', f'{col_letter}{row}')
        
        # === 5. YoY 성장률 (계산) ===
        row += 1
        ws.cell(row=row, column=1).value = "YoY Growth %"
        ws.cell(row=row, column=1).font = Font(size=10, italic=True)
        
        # Year 1-5 성장률
        for year in range(1, years + 1):
            col = 2 + year
            col_letter = chr(65 + col)
            prev_col_letter = chr(65 + col - 1)
            
            ws.cell(row=row, column=col).value = f'=({col_letter}{row-1}-{prev_col_letter}{row-1})/{prev_col_letter}{row-1}'
            ws.cell(row=row, column=col).number_format = '0.0%'
            ws.cell(row=row, column=col).font = Font(italic=True)
        
        # === 6. 가이드 ===
        row += 2
        ws.cell(row=row, column=1).value = "💡 해석 가이드"
        ws.cell(row=row, column=1).font = Font(size=10, bold=True)
        
        row += 1
        ws.cell(row=row, column=1).value = "• 세그먼트별 성장률을 다르게 설정 가능 (마지막 컬럼 수정)"
        ws.cell(row=row, column=1).font = Font(size=9)
        ws.merge_cells(f'A{row}:H{row}')
        
        row += 1
        ws.cell(row=row, column=1).value = "• 총 매출은 자동 계산 (세그먼트 합계)"
        ws.cell(row=row, column=1).font = Font(size=9)
        ws.merge_cells(f'A{row}:H{row}')
        
        row += 1
        ws.cell(row=row, column=1).value = "• YoY %는 전년 대비 성장률 (자동 계산)"
        ws.cell(row=row, column=1).font = Font(size=9)
        ws.merge_cells(f'A{row}:H{row}')
        
        print(f"   ✅ Revenue Build-up 시트 생성 완료")
        print(f"      - {len(segments)}개 세그먼트")
        print(f"      - {years+1}개년 매출 (Year 0 ~ Year {years})")
        print(f"      - Named Range: Revenue_Y0 ~ Revenue_Y{years}")


# 테스트는 별도 스크립트에서

