# UMIS v7.1.0 프로젝트 심층 분석
**작성일**: 2025-11-03  
**목적**: 3대 핵심 프로젝트 상세 분석  
**우선순위**: 재검토 필요

---

## 🎯 프로젝트 1: Deliverable 자동 생성 (Excel 중심)

### 💡 핵심: Excel 함수 구현이 전부

**사용자 피드백**:
> "엑셀 생성을 잘하는게 가장 중요해. 함수 구현에 문제가 없어야 문제 없이 사용할 수 있어."

**완전히 동의합니다!**

---

### 📊 Bill의 market_sizing.xlsx 분석

#### 9개 시트 구조

**핵심 시트** (함수 중요도 ⭐⭐⭐):
1. **Assumptions** - 모든 가정의 원천
   - 함수: 거의 없음 (입력 값)
   - 중요: 셀 참조 정확성

2. **Method_1_TopDown** - TAM → SAM 축소
   - 함수: `=B2*C2` (단계별 곱셈)
   - 중요: ⭐⭐⭐ (참조 체인)
   
3. **Method_2_BottomUp** - 세그먼트 합산
   - 함수: `=SUM(B5:B10)`, `=B5*C5*D5*E5`
   - 중요: ⭐⭐⭐ (복잡한 계산)

4. **Method_3_Proxy** - 벤치마크 조정
   - 함수: `=B2*C2*D2*E2`
   - 중요: ⭐⭐ (다단계 곱셈)

5. **Method_4_Competitor** - 경쟁사 역산
   - 함수: `=SUM(B5:B10)/C2`
   - 중요: ⭐⭐⭐ (역산 로직)

6. **Convergence_Analysis** - 수렴 분석
   - 함수: `=AVERAGE()`, `=STDEV()`, `=MAX()/MIN()`
   - 중요: ⭐⭐⭐ (통계 함수)

**지원 시트** (함수 중요도 ⭐⭐):
7. **Estimation_Details** - 추정 논리 (텍스트)
8. **Scenarios** - 시나리오별
9. **Validation_Log** - 검증 이력

---

### 🔧 Excel 생성의 핵심 도전과제

#### 도전 1: 셀 참조 정확성

**문제**:
```python
# Method 1에서:
=Assumptions!B5  # ASM_001 참조
=Assumptions!B8  # ASM_002 참조

# 만약 Assumptions에 행 추가되면?
# → 참조 깨짐!
```

**해결책**:
```python
# 옵션 A: Named Range 사용
# Assumptions에서 ASM_001에 이름 정의
# Method 1에서 =ASM_001 참조
# → 행 추가되어도 안전!

# 옵션 B: 절대 위치 고정
# =Assumptions!$B$5
# → 명시적이지만 유연성 낮음

# 옵션 C: VLOOKUP/XLOOKUP
# =VLOOKUP("ASM_001", Assumptions!A:B, 2)
# → 가장 안전, 약간 복잡
```

**추천**: Named Range (옵션 A)

#### 도전 2: 다단계 계산 체인

**Method 2 Bottom-Up 예시**:
```python
# 세그먼트 1
B5: 10,000 (고객 수)
C5: 0.15 (전환율)
D5: 50,000 (가격)
E5: 12 (개월)
F5: =B5*C5*D5*E5  # 세그먼트 1 매출

# 세그먼트 2
B6: 5,000
C6: 0.20
...
F6: =B6*C6*D6*E6

# 합계
F10: =SUM(F5:F9)  # 전체 Bottom-Up SAM

# Convergence에서 참조
Convergence!B5: =Method_2_BottomUp!F10
```

**복잡도**: 
- 시트 간 참조
- 동적 범위 (세그먼트 개수 가변)
- 수식 체인

**해결책**:
```python
class ExcelFormulaBuilder:
    def __init__(self, workbook):
        self.wb = workbook
        self.name_manager = NamedRangeManager(workbook)
    
    def create_assumption_ref(self, asm_id: str) -> str:
        """가정 참조 생성 (Named Range)"""
        return f"={asm_id}"  # Named Range로
    
    def create_segment_calc(self, row: int) -> str:
        """세그먼트 계산 함수"""
        return f"=B{row}*C{row}*D{row}*E{row}"
    
    def create_sum_range(self, start: int, end: int, col: str) -> str:
        """합계 범위"""
        return f"=SUM({col}{start}:{col}{end})"
    
    def create_cross_sheet_ref(self, sheet: str, cell: str) -> str:
        """시트 간 참조"""
        return f"='{sheet}'!{cell}"
```

#### 도전 3: 셀 서식 및 보호

**필요한 서식**:
- 색상 코딩 (입력 셀, 계산 셀, 결과 셀)
- 셀 코멘트 (출처, 근거)
- 시트 보호 (계산 셀만)
- 조건부 서식 (검증 통과/실패)

**구현**:
```python
from openpyxl.styles import PatternFill, Font, Border
from openpyxl.comments import Comment

# 색상 정의
INPUT_FILL = PatternFill(start_color="FFFF99", end_color="FFFF99", fill_type="solid")
CALC_FILL = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")
RESULT_FILL = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")

# 적용
ws['B5'].fill = INPUT_FILL
ws['B5'].comment = Comment("출처: SRC_20241031_001", "Rachel")

# 시트 보호
ws.protection.sheet = True
ws.protection.password = None  # 협업 용이
ws['B5'].protection = Protection(locked=False)  # 입력 셀만 편집 가능
```

---

### 🎯 구현 전략 (재검토)

#### Phase 1: 핵심 함수 엔진 (2주) ⭐

**목표**: 완벽한 Excel 함수 생성

```python
# umis_rag/deliverables/excel/formula_engine.py

class FormulaEngine:
    """Excel 함수 생성 엔진"""
    
    def __init__(self, workbook):
        self.wb = workbook
        self.named_ranges = {}
    
    def define_named_range(self, name: str, sheet: str, cell: str):
        """Named Range 정의"""
        self.wb.define_name(name, f"'{sheet}'!{cell}")
        self.named_ranges[name] = (sheet, cell)
    
    def create_assumption_ref(self, asm_id: str) -> str:
        """가정 참조 (Assumptions 시트)"""
        if asm_id in self.named_ranges:
            return f"={asm_id}"
        else:
            raise ValueError(f"Named range {asm_id} not found")
    
    def create_multiplication_chain(self, cells: list) -> str:
        """연쇄 곱셈"""
        return "=" + "*".join(cells)
    
    def create_sum(self, range_ref: str) -> str:
        """합계"""
        return f"=SUM({range_ref})"
    
    def create_convergence_formula(self, method_cells: list) -> dict:
        """수렴 분석 함수들"""
        return {
            'average': f"=AVERAGE({','.join(method_cells)})",
            'stdev': f"=STDEV({','.join(method_cells)})",
            'cv': f"=STDEV({','.join(method_cells)})/AVERAGE({','.join(method_cells)})",
            'max_min_ratio': f"=MAX({','.join(method_cells)})/MIN({','.join(method_cells)})"
        }
    
    def validate_formula(self, formula: str) -> bool:
        """함수 유효성 검증"""
        # 1. 문법 체크
        # 2. 순환 참조 체크
        # 3. 범위 유효성 체크
        return True

# 사용
engine = FormulaEngine(workbook)

# Named Range 정의
engine.define_named_range("ASM_001", "Assumptions", "B5")

# 함수 생성
formula = engine.create_assumption_ref("ASM_001")  # "=ASM_001"
ws['B2'].value = formula

# 검증
engine.validate_formula(formula)
```

**테스트**:
```python
def test_excel_functions():
    """Excel 함수 생성 테스트"""
    
    # 1. 간단한 참조
    assert engine.create_ref("B5") == "=B5"
    
    # 2. Named Range
    engine.define_named_range("ASM_001", "Assumptions", "B5")
    assert engine.create_assumption_ref("ASM_001") == "=ASM_001"
    
    # 3. 곱셈 체인
    assert engine.create_multiplication_chain(["B2", "C2", "D2"]) == "=B2*C2*D2"
    
    # 4. 수렴 분석
    convergence = engine.create_convergence_formula(["B5", "B6", "B7", "B8"])
    assert "AVERAGE" in convergence['average']
    
    # 5. 실제 Excel에서 작동 확인
    wb = create_test_workbook()
    ws = wb['Test']
    ws['B5'] = 100
    ws['B6'] = 120
    ws['B7'] = engine.create_sum("B5:B6")
    
    # 계산 확인
    assert ws['B7'].value == 220  # openpyxl은 계산 안함
    # → Excel에서 열어서 확인 필요
```

**중요**: **실제 Excel에서 열어서 함수 작동 확인 필수!**

#### Phase 2: 시트 생성기 (1주)

```python
class MarketSizingWorkbook:
    """Bill의 SAM 계산서 생성"""
    
    def __init__(self, market_name: str):
        self.wb = Workbook()
        self.market_name = market_name
        self.formula_engine = FormulaEngine(self.wb)
    
    def create_assumptions_sheet(self, assumptions: list):
        """Assumptions 시트 생성"""
        ws = self.wb.create_sheet("Assumptions")
        
        # 헤더
        headers = ["ID", "Category", "Description", "Value", "Unit", 
                   "Data_Type", "Source", "Confidence", "Notes"]
        ws.append(headers)
        
        # 데이터 + Named Range
        for i, asm in enumerate(assumptions, start=2):
            ws.append([asm['id'], asm['category'], ...])
            
            # Named Range 정의
            self.formula_engine.define_named_range(
                asm['id'],  # "ASM_001"
                "Assumptions",
                f"D{i}"  # Value 컬럼
            )
        
        # 서식
        self.apply_assumption_formatting(ws)
    
    def create_method1_sheet(self, tam: dict, narrowing_steps: list):
        """Method 1: Top-Down 시트"""
        ws = self.wb.create_sheet("Method_1_TopDown")
        
        # TAM
        ws['A1'] = "TAM"
        ws['A2'] = tam['value']
        
        # Narrowing steps
        col = ord('B')
        current_value = "A2"
        
        for step in narrowing_steps:
            # 축소 비율
            ratio_cell = f"{chr(col)}2"
            ws[ratio_cell] = self.formula_engine.create_assumption_ref(step['asm_id'])
            
            # 중간값 계산
            result_cell = f"{chr(col)}3"
            ws[result_cell] = f"={current_value}*{ratio_cell}"
            
            current_value = result_cell
            col += 1
        
        # 최종 SAM = 마지막 중간값
        ws['SAM'] = f"={current_value}"
    
    def create_convergence_sheet(self, method_results: dict):
        """Convergence Analysis 시트"""
        ws = self.wb.create_sheet("Convergence_Analysis")
        
        # Method 결과들
        methods = ['Method_1', 'Method_2', 'Method_3', 'Method_4']
        
        for i, method in enumerate(methods, start=5):
            ws[f'A{i}'] = method
            ws[f'B{i}'] = self.formula_engine.create_cross_sheet_ref(
                f"{method}_*",  # 시트 이름
                "SAM"  # 최종 SAM 셀
            )
        
        # 평균
        ws['A9'] = "평균"
        ws['B9'] = "=AVERAGE(B5:B8)"
        
        # 표준편차
        ws['A10'] = "표준편차"
        ws['B10'] = "=STDEV(B5:B8)"
        
        # 변동계수
        ws['A11'] = "변동계수 (CV%)"
        ws['B11'] = "=B10/B9*100"
        
        # Max/Min 비율
        ws['A12'] = "Max/Min 비율"
        ws['B12'] = "=MAX(B5:B8)/MIN(B5:B8)"
        
        # ±30% 수렴 확인
        ws['A13'] = "±30% 수렴?"
        ws['B13'] = '=IF(B12<=1.3, "✅ 통과", "❌ 재검토")'
```

**핵심**: 
- Named Range로 안정성
- 함수 체인 정확성
- 시트 간 참조 무결성

---

### ⚠️ 주요 함정

#### 1. openpyxl은 함수를 **계산하지 않음**

```python
ws['B5'] = 100
ws['B6'] = 200
ws['B7'] = "=B5+B6"

# openpyxl에서
print(ws['B7'].value)  # "=B5+B6" (문자열!)

# Excel에서 열면
# B7 = 300 (계산됨!)
```

**해결**: 
- Excel에서 열어서 검증 필수
- 또는 formulas 라이브러리 사용 (계산 가능)

#### 2. Estimation_Details는 텍스트

**7개 섹션 블록**:
```
============================================
EST_ID: EST_001
추정 항목: 피아노 학원 비중
최종 추정값: 30%
============================================

[1] 추정 필요 이유
...

[7] 사용 위치
============================================
```

**생성 방법**:
- openpyxl로 텍스트 블록 삽입
- 병합된 셀 활용
- 또는 별도 시트 (상세 설명용)

#### 3. PDF 백업

**요구사항**: Excel + PDF 모두 저장

**구현**:
```python
# Excel 저장
wb.save('market_sizing_piano.xlsx')

# PDF 변환
# 옵션 A: win32com (Windows만)
# 옵션 B: LibreOffice --headless (Linux/Mac)
# 옵션 C: 사용자에게 수동 저장 안내

# 추천: 옵션 C (간단)
print("✅ Excel 생성 완료!")
print("📋 다음 단계: Excel에서 열어 PDF로 저장")
```

---

### 🎯 구현 우선순위 (재조정)

**v7.1.0: Excel 함수 엔진** (3주)
1. FormulaEngine 클래스 (1주)
   - Named Range 관리
   - 함수 생성 메서드
   - 참조 검증
   
2. 9개 시트 생성기 (1주)
   - Assumptions
   - Method 1-4
   - Convergence
   
3. 테스트 + Excel 검증 (1주)
   - 함수 작동 확인
   - 실제 Excel에서 검증
   - 예시 프로젝트

**v7.2.0: Markdown 산출물** (2주)
- Explorer, Observer 산출물
- Template 기반

**v7.3.0: 전체 통합** (2주)
- Stewart 자동 생성
- deliverables_registry 연동

---

## 📋 프로젝트 2: umis.yaml 모듈화 (AI 빠른 파악)

### 💡 핵심 재정의

**사용자 피드백**:
> "AI가 매우 빠르게 UMIS의 전 기능을 파악해서 umis로 무엇을 할 수 있는지 파악한 다음, 무엇을 해야 사용자의 질문에 대한 최고의 결과를 낼 수 있는지 판단할 수 있게 하는 것이 핵심"

**핵심 요구사항**:
1. **빠른 파악**: 5분 내 전체 기능 이해
2. **능력 파악**: UMIS가 할 수 있는 것 (What)
3. **최적 방법 판단**: 해야 하는 것 (How)

**제약조건**:
1. 작은 컨텍스트 윈도우
2. 유지보수 복잡성

---

### 🔍 System RAG 재검토

**기존 분석** (dev_docs/architecture/08_system_rag/):

**System RAG 개념**:
```yaml
umis.yaml (5,509줄) → RAG Index
  ↓
AI 쿼리: "Explorer market analysis"
  ↓
검색 결과: 5개 청크 (~2,000줄)
  ↓
컨텍스트 63% 절감
```

**Tool Registry 개념**:
```yaml
각 Section = Tool
  • tool_id: "explorer_7_step_process"
  • when_to_use: "기회 발굴 시"
  • what_it_does: "7단계 프로세스"
  • prerequisites: ["market_structure_report"]
  • deliverables: ["opportunity_portfolio"]
  
Guardian Meta-RAG:
  • 상황 분석
  • 필요한 도구 검색
  • Workflow 동적 생성
  • 실행 모니터링
```

**장점**:
- ✅ 95% 토큰 절감
- ✅ 필요한 것만 로드
- ✅ 동적 workflow

**단점**:
- ⚠️ 검색 실수 위험
- ⚠️ 구현 복잡도
- ⚠️ RAG 하나 더 추가

---

### 💡 하이브리드 접근법 (최종 추천)

#### 구조

**umis_core.yaml** (INDEX, 1,000줄):
```yaml
# ========================================
# UMIS v7.1.0 Core Index
# ========================================

system:
  version: "7.1.0"
  
  # === AI 5분 파악 ===
  quick_understanding:
    what_umis_can_do:
      rag_capabilities:
        - "54개 검증된 패턴/사례 자동 검색 (Explorer)"
        - "Knowledge Graph 조합 발견"
        - "완전한 추적성 (ID Namespace)"
        - "재검증 가능 (Excel 함수)"
      
      agent_capabilities:
        observer: "시장 구조 분석 (가치사슬, 거래 패턴)"
        explorer: "기회 발굴 (RAG 패턴 검색) ⭐"
        quantifier: "SAM 계산 (4가지 방법, Excel)"
        validator: "데이터 검증 (정의 Gap 분석)"
        guardian: "프로세스 관리 (검증, 문서화)"
      
      frameworks:
        - "13 dimensions 시장 정의"
        - "7 Powers 지속 우위"
        - "Discovery Sprint (명확도 <7)"
        - "Counter-Positioning (1등 추월)"
    
    what_to_do_for_best_results:
      decision_tree:
        user_asks_market_analysis:
          step_1: "명확도 평가 (1-10)"
          
          if_clarity_lt_7:
            action: "Discovery Sprint"
            agents: "모든 Agent 병렬 탐색"
            duration: "1-3일"
            load: "modules/workflows/discovery_sprint.yaml"
          
          if_clarity_gte_7:
            action: "Rapid Validation"
            agents: "Albert, Steve, Bill 순차"
            duration: "2-3일"
            load: "modules/workflows/rapid.yaml"
        
        user_asks_opportunity:
          action: "Explorer RAG 검색"
          load: "modules/agents/explorer.yaml"
          tools:
            - "RAG pattern search"
            - "Graph combination discovery"
            - "7-step process"
        
        user_asks_market_size:
          action: "Quantifier SAM calculation"
          load: "modules/agents/quantifier.yaml"
          tools:
            - "4 methods (Top-Down, Bottom-Up, Proxy, Competitor)"
            - "Excel 자동 생성"
            - "Convergence ±30%"
  
  # === Module Index ===
  modules:
    agents:
      explorer: 
        file: "modules/agents/explorer.yaml"
        size: "900줄"
        when: "기회 발굴, RAG 검색 필요 시"
      
      quantifier:
        file: "modules/agents/quantifier.yaml"
        size: "700줄"
        when: "시장 규모 계산, SAM/TAM 필요 시"
      
      # ... 나머지
    
    frameworks:
      market_definition:
        file: "modules/frameworks/market_definition.yaml"
        size: "1,000줄"
        when: "시장 경계 정의 필요 시"
      
      seven_powers:
        file: "modules/frameworks/seven_powers.yaml"
        size: "500줄"
        when: "경쟁 우위 분석 필요 시"

# ========================================
# AI Loading Strategy
# ========================================

ai_loading:
  step_1_always:
    read: "umis_core.yaml (이 파일, 1,000줄)"
    time: "2-3분"
    result: "전체 기능 파악 + 최적 방법 판단"
  
  step_2_conditional:
    if_explorer_needed:
      load: "modules/agents/explorer.yaml"
      when: "기회 발굴, 패턴 검색"
    
    if_quantifier_needed:
      load: "modules/agents/quantifier.yaml"
      when: "SAM 계산, 시장 규모"
  
  step_3_optional:
    if_deep_framework:
      load: "modules/frameworks/*.yaml"
      when: "상세 프레임워크 적용"

# ========================================
# System RAG (선택, 향후)
# ========================================

system_rag:
  status: "planned (v7.2.0+)"
  
  concept: |
    umis.yaml → Vector RAG
    → AI가 필요한 섹션 검색
    → 컨텍스트 90% 절감
  
  when_to_implement: |
    - umis.yaml > 10,000줄
    - 또는 모듈 > 20개
    - 현재는 모듈화로 충분
```

**AI 사용 플로우**:
```
사용자: "@Explorer, 음악 스트리밍 시장 분석"

AI:
  1. umis_core.yaml 읽기 (1,000줄, 2분)
     → Explorer = RAG 패턴 검색
     → 7단계 프로세스
     → modules/agents/explorer.yaml 로드 필요
  
  2. 판단:
     "Explorer + RAG로 패턴 검색이 최적"
  
  3. modules/agents/explorer.yaml 로드 (900줄, 1분)
     → 상세 워크플로우
     → RAG 사용법
  
  4. 실행:
     RAG 검색 → 패턴 발견 → 가설 생성
  
총 컨텍스트: 1,900줄 (vs 5,509줄)
절감: 65%
시간: 3분 파악 + 즉시 실행
```

---

### 🎯 하이브리드 vs System RAG

| 방법 | 컨텍스트 | 구현 | 유지보수 | 정확성 |
|------|---------|------|---------|--------|
| **하이브리드** (INDEX + Modules) | 1,900줄 (65% ↓) | 중 (2주) | 쉬움 | 높음 |
| **System RAG** | 200줄 (96% ↓) | 높음 (4주) | 복잡 | 중 (검색 실수) |

**추천**: 
- **v7.1.0**: 하이브리드 (INDEX + Modules)
  - 빠른 구현
  - 충분한 효율
  - 안정적
  
- **v7.2.0+**: System RAG 검토
  - umis.yaml > 10,000줄 되면
  - 또는 모듈 > 20개
  - 더 필요하면

---

### 🔑 핵심 인사이트: "능력 파악 → 최적 판단"

**umis_core.yaml의 핵심 섹션**:

```yaml
decision_guide:
  description: "사용자 질문 → 최적 Agent/도구 판단"
  
  question_patterns:
    
    market_analysis:
      keywords: ["시장 분석", "산업 분석", "경쟁 구조"]
      
      decision_logic:
        1_check_clarity:
          if_low: "Discovery Sprint (모든 Agent)"
          if_high: "Structured Analysis (Albert → Steve)"
        
        2_check_scope:
          if_broad: "13 dimensions 전체"
          if_focused: "핵심 차원만"
        
        3_determine_agents:
          primary: "Albert (구조)"
          secondary: "Steve (기회)"
          support: "Bill (규모), Rachel (데이터)"
    
    opportunity_discovery:
      keywords: ["기회", "아이디어", "새로운", "혁신"]
      
      primary_agent: "Explorer (Steve)"
      
      decision_logic:
        1_check_rag:
          action: "RAG 패턴 검색 우선"
          load: "modules/agents/explorer.yaml"
        
        2_check_market_context:
          if_no_context: "Observer 먼저 (Albert)"
          if_has_context: "Explorer 바로"
        
        3_tools:
          - "RAG pattern search"
          - "7-step process"
          - "Validation protocol"
    
    market_sizing:
      keywords: ["시장 규모", "SAM", "TAM", "크기"]
      
      primary_agent: "Quantifier (Bill)"
      
      decision_logic:
        1_check_data:
          action: "Validator 먼저 (Rachel)"
          ensure: "데이터 정의 검증"
        
        2_calculate:
          load: "modules/agents/quantifier.yaml"
          methods: "4가지 방법 모두"
          deliverable: "Excel workbook"
        
        3_validate:
          convergence: "±30% 확인"
          validators: "Rachel, Albert"
```

**AI가 이것만 보면**:
- ✅ 어떤 질문에 어떤 Agent
- ✅ 어떤 도구를 어떤 순서로
- ✅ 어떤 모듈을 로드해야
- ✅ 최적 결과 내는 방법

---

## 📋 프로젝트 3: RAG 데이터 추가 자동화

### (사용자 입력 중단, 대기 중)

---

## 🎯 최종 우선순위 (재조정)

### v7.1.0 (1.5개월)

**Week 1-2: umis.yaml 모듈화** ⭐⭐⭐
- umis_core.yaml (INDEX) 생성
- decision_guide 핵심 구현
- modules/agents/ 분리 (5개)
- 소요: 2주

**Week 3-5: Excel 함수 엔진** ⭐⭐⭐
- FormulaEngine 클래스
- 9개 시트 생성기
- Excel 검증
- 소요: 3주

**Week 6: RAG 데이터 추가** ⭐⭐
- .cursorrules 업데이트
- 대화형 추가
- 소요: 1주

---

## 💡 핵심 인사이트

### 1. Excel이 가장 어렵고 중요

**왜?**:
- 함수 참조 정확성
- 시트 간 관계
- openpyxl 제약
- 실제 Excel 검증 필수

**대응**:
- Named Range 필수
- 철저한 테스트
- 실제 Excel 검증

### 2. umis.yaml 모듈화가 최우선

**왜?**:
- AI 효율 직결
- 기능 누락 방지
- 모든 프로젝트 기반

**대응**:
- decision_guide 핵심
- 1,000줄 INDEX
- 선택적 모듈 로드

### 3. System RAG는 향후

**왜 지금 안 하나?**:
- 5,509줄은 모듈화로 충분
- 구현 복잡도 vs 효과
- 검색 실수 위험

**언제 하나?**:
- umis.yaml > 10,000줄
- 모듈 > 20개
- 더 극단적 최적화 필요 시

---

**상세 분석 완료!**

3번 프로젝트 입력을 계속하시겠습니까? 아니면 이대로 진행하시겠습니까?
