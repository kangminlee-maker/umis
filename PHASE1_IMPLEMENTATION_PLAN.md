# Phase 1 구현 계획: Unit Economics + Financial Projection

**시작일**: 2025-11-04  
**목표**: Bill의 핵심 Excel 도구 2개 완성  
**예상 공수**: 10-12일 (6 Batch)

---

## 🎯 Phase 1 목표

### 도구 1: Unit Economics Analyzer ⭐⭐⭐
```yaml
파일명: unit_economics_analyzer.xlsx
시트 수: 10개
예상 코드: 300-400줄
핵심 지표:
  - LTV (Customer Lifetime Value)
  - CAC (Customer Acquisition Cost)
  - LTV/CAC Ratio (목표 > 3.0)
  - Payback Period (목표 < 12개월)
```

### 도구 2: Financial Projection Model ⭐⭐⭐
```yaml
파일명: financial_projection_model.xlsx
시트 수: 12개
예상 코드: 500-600줄
핵심 산출물:
  - P&L Forecast (3-5년)
  - Cash Flow Forecast
  - Scenarios (Base/Bull/Bear)
  - DCF Valuation
```

---

## 📋 Batch 구성

### Batch 1: Unit Economics 기본 구조 ⭐
**예상 시간**: 2-3시간  
**상태**: 🟢 진행 중

**작업 항목**:
1. FormulaEngine 확장
   - LTV 계산 함수
   - CAC 계산 함수
   - 비율 계산 함수

2. InputsBuilder
   - Sheet 1: Inputs
   - 컬럼: ARPU, CAC, Gross Margin, Churn, Lifetime
   - Named Range 정의

3. LTVBuilder
   - Sheet 2: LTV Calculation
   - Formula: ARPU × Lifetime × Gross Margin
   - Alternative: ARPU × Margin / Churn
   - Confidence Interval

4. CACBuilder
   - Sheet 3: CAC Analysis
   - Total S&M Spend
   - New Customers
   - CAC by Channel

**산출물**:
```python
umis_rag/deliverables/excel/unit_economics/
  - __init__.py
  - inputs_builder.py (100줄)
  - ltv_builder.py (80줄)
  - cac_builder.py (80줄)
```

**검증**:
- [ ] Inputs 시트 생성
- [ ] Named Range 정의 (10개)
- [ ] LTV 계산 정확
- [ ] CAC 계산 정확

---

### Batch 2: Unit Economics 분석 시트
**예상 시간**: 2-3시간  
**상태**: ⏸️ 대기

**작업 항목**:
1. RatioBuilder
   - Sheet 4: LTV/CAC Ratio
   - 비율 계산
   - 업계 벤치마크 (3.0, 5.0)
   - Traffic Light (조건부 서식)

2. PaybackBuilder
   - Sheet 5: Payback Period
   - Formula: CAC / (ARPU × Margin)
   - Timeline (월별 Cash Flow)
   - 목표 대비 (12개월)

3. SensitivityBuilder
   - Sheet 7: Sensitivity Analysis
   - ARPU ±20%
   - CAC ±20%
   - Churn ±2%p
   - 2-Way Matrix

**산출물**:
```python
umis_rag/deliverables/excel/unit_economics/
  - ratio_builder.py (70줄)
  - payback_builder.py (80줄)
  - sensitivity_builder.py (120줄)
```

**검증**:
- [ ] LTV/CAC 비율 정확
- [ ] Payback 계산 정확
- [ ] Sensitivity 2-Way Matrix 작동

---

### Batch 3: Unit Economics 완성
**예상 시간**: 2-3시간  
**상태**: ⏸️ 대기

**작업 항목**:
1. CohortLTVBuilder
   - Sheet 6: Cohort LTV
   - 월별 코호트 LTV
   - Cohort Improvement Rate

2. ScenariosBuilder
   - Sheet 8: Scenarios
   - Conservative/Base/Optimistic
   - 각 시나리오별 LTV/CAC

3. BenchmarkBuilder
   - Sheet 9: Benchmark Comparison
   - 업계 평균
   - 경쟁사 Unit Economics
   - Gap Analysis

4. DashboardBuilder
   - Sheet 10: Dashboard
   - 핵심 지표 요약
   - Traffic Light
   - 권장사항

5. UnitEconomicsGenerator (통합)
   - 10개 시트 통합 생성
   - 테스트

**산출물**:
```python
umis_rag/deliverables/excel/unit_economics/
  - cohort_ltv_builder.py (90줄)
  - scenarios_builder.py (100줄)
  - benchmark_builder.py (80줄)
  - dashboard_builder.py (120줄)
  - unit_economics_generator.py (200줄)
```

**검증**:
- [ ] 10개 시트 모두 생성
- [ ] Excel 파일 열림
- [ ] 모든 함수 작동
- [ ] Dashboard 정상 표시

---

### Batch 4: Financial Projection 기본 구조
**예상 시간**: 2-3시간  
**상태**: ⏸️ 대기

**작업 항목**:
1. AssumptionsBuilder
   - Sheet 1: Assumptions
   - 성장률 (YoY, CAGR)
   - Margin (Gross, EBITDA, Net)
   - OPEX 비율 (S&M, R&D, G&A)
   - Tax Rate, Discount Rate

2. RevenueBuilder
   - Sheet 2: Revenue Build-up
   - 세그먼트별 (B2C, B2B, B2G, Global)
   - 월별/분기별/연간
   - 성장률 적용

3. CostStructureBuilder
   - Sheet 3: Cost Structure
   - COGS
   - S&M, R&D, G&A
   - % of Revenue

**산출물**:
```python
umis_rag/deliverables/excel/financial_projection/
  - __init__.py
  - assumptions_builder.py (120줄)
  - revenue_builder.py (150줄)
  - cost_builder.py (100줄)
```

**검증**:
- [ ] Assumptions Named Range
- [ ] Revenue 세그먼트별 계산
- [ ] Cost 자동 계산 (% of Revenue)

---

### Batch 5: Financial Projection 재무제표
**예상 시간**: 3-4시간  
**상태**: ⏸️ 대기

**작업 항목**:
1. PLBuilder (P&L Forecast)
   - Sheet 4: P&L 3년
   - Sheet 5: P&L 5년
   - Revenue → COGS → Gross Profit
   - OPEX → EBITDA → EBIT
   - Tax → Net Income

2. CashFlowBuilder
   - Sheet 6: Cash Flow Forecast
   - Operating CF
   - Investment CF (CAPEX)
   - Financing CF
   - Ending Cash Balance

3. MetricsBuilder
   - Sheet 7: Key Metrics
   - Gross Margin %
   - EBITDA Margin %
   - Net Margin %
   - Revenue Growth (YoY)

**산출물**:
```python
umis_rag/deliverables/excel/financial_projection/
  - pl_builder.py (180줄)
  - cashflow_builder.py (120줄)
  - metrics_builder.py (100줄)
```

**검증**:
- [ ] P&L 3년/5년 정확
- [ ] Cash Flow 연결 정확
- [ ] Metrics 자동 계산

---

### Batch 6: Financial Projection 완성
**예상 시간**: 3-4시간  
**상태**: ⏸️ 대기

**작업 항목**:
1. ScenariosBuilder
   - Sheet 8: Scenarios (Base/Bull/Bear)
   - 각 시나리오별 P&L
   - 성장률/Margin 조정

2. BreakEvenBuilder
   - Sheet 9: Break-even Analysis
   - 손익분기 매출
   - 손익분기 시점
   - 필요 고객 수

3. DCFBuilder
   - Sheet 10: DCF Valuation
   - 현금흐름 할인
   - Terminal Value
   - Enterprise Value

4. SensitivityBuilder
   - Sheet 11: Sensitivity Matrix
   - Revenue Growth × Margin
   - 2-Way Sensitivity

5. DashboardBuilder
   - Sheet 12: Dashboard
   - 5개년 Trend
   - 핵심 재무 비율
   - 권장사항

6. FinancialProjectionGenerator (통합)
   - 12개 시트 통합
   - 테스트

**산출물**:
```python
umis_rag/deliverables/excel/financial_projection/
  - scenarios_builder.py (150줄)
  - breakeven_builder.py (100줄)
  - dcf_builder.py (120줄)
  - sensitivity_builder.py (100줄)
  - dashboard_builder.py (150줄)
  - financial_projection_generator.py (250줄)
```

**검증**:
- [ ] 12개 시트 모두 생성
- [ ] Scenarios 작동
- [ ] DCF 계산 정확
- [ ] Dashboard 정상

---

## 🧪 Phase 1 통합 테스트

**작업 항목**:
1. 실제 데이터 테스트
   - 음악 스트리밍 케이스
   - 성인 교육 케이스

2. Excel 검증
   - Excel에서 파일 열기
   - 모든 함수 작동 확인
   - Named Range 확인

3. 문서화
   - 사용 가이드 작성
   - 예제 데이터 추가

**검증**:
- [ ] 음악 스트리밍: LTV ₩80K, CAC ₩25K 재현
- [ ] 성인 교육: Year 5 매출 ₩4,300억 재현
- [ ] Excel에서 모든 함수 작동
- [ ] PDF 백업 생성

---

## 📊 진행 상황 추적

### Batch 완료 현황
- [🟢] Batch 1: Unit Economics 기본 (진행 중)
- [⏸️] Batch 2: Unit Economics 분석
- [⏸️] Batch 3: Unit Economics 완성
- [⏸️] Batch 4: Financial Projection 기본
- [⏸️] Batch 5: Financial Projection 재무제표
- [⏸️] Batch 6: Financial Projection 완성
- [⏸️] 통합 테스트

### 통계
```yaml
총 Batch: 7개
완료: 0개
진행 중: 1개
대기: 6개

예상 완료일: 2025-11-14 (10일 후)
실제 공수: TBD
```

---

## 📁 파일 구조 (완성 후)

```
umis_rag/deliverables/excel/
  - formula_engine.py (확장)
  - market_sizing/ (기존)
  
  - unit_economics/ (신규)
    - __init__.py
    - inputs_builder.py
    - ltv_builder.py
    - cac_builder.py
    - ratio_builder.py
    - payback_builder.py
    - cohort_ltv_builder.py
    - sensitivity_builder.py
    - scenarios_builder.py
    - benchmark_builder.py
    - dashboard_builder.py
    - unit_economics_generator.py
  
  - financial_projection/ (신규)
    - __init__.py
    - assumptions_builder.py
    - revenue_builder.py
    - cost_builder.py
    - pl_builder.py
    - cashflow_builder.py
    - metrics_builder.py
    - scenarios_builder.py
    - breakeven_builder.py
    - dcf_builder.py
    - sensitivity_builder.py
    - dashboard_builder.py
    - financial_projection_generator.py

scripts/
  - test_unit_economics.py (신규)
  - test_financial_projection.py (신규)
```

---

## 🎯 다음 단계

**현재**: Batch 1 시작
**목표**: Unit Economics Inputs, LTV, CAC 시트 완성

**준비 완료!** 시작하겠습니다.

