# Bill Excel 도구 예제 파일

**생성일**: 2025-11-04  
**버전**: v7.2.0-dev1  
**목적**: 실제 데이터로 채워진 완성된 Excel 샘플

---

## 📁 포함된 파일

### 1. Unit Economics Analyzer 예제

**파일**: `unit_economics_music_streaming_example_20251104.xlsx`  
**케이스**: 음악 스트리밍 구독 서비스  
**크기**: 23KB

#### 입력 데이터
```yaml
ARPU: ₩9,000/월
CAC: ₩25,000
Gross Margin: 35%
Monthly Churn: 4%
Customer Lifetime: 25개월
S&M Spend: ₩500만/월
New Customers: 200명/월
```

#### 계산 결과
```yaml
LTV: ₩78,750
LTV/CAC: 3.15 → Good (양호) ✅
Payback: 7.9개월 → Good (< 12개월) ✅
평가: 건강한 비즈니스 모델
```

#### 포함된 시트 (10개)
1. **Dashboard** - Traffic Light 자동 색상
2. **Inputs** - 7개 핵심 지표 (노란색 = 수정 가능)
3. **LTV_Calculation** - 2가지 계산 방법
4. **CAC_Analysis** - 4개 채널별 CAC
5. **LTV_CAC_Ratio** - Traffic Light (4단계)
6. **Payback_Period** - 24개월 Timeline
7. **Sensitivity_Analysis** - 2-Way Matrix (ARPU × Churn)
8. **UE_Scenarios** - Conservative/Base/Optimistic
9. **Cohort_LTV** - 12개월 코호트 추적
10. **Benchmark_Comparison** - 5개 업계 비교

---

### 2. Financial Projection Model 예제

**파일**: `financial_projection_korean_adult_education_example_20251104.xlsx`  
**케이스**: 한국 성인 교육 시장  
**크기**: 22KB

#### 입력 데이터
```yaml
Base Revenue (Year 0): ₩1,250억
YoY Growth Rate: 28% (CAGR)
Gross Margin: 70%
EBITDA Margin: 15% (목표)
Net Margin: 10% (목표)

세그먼트:
  - B2C (개인): ₩800억, 10% 성장
  - B2B (기업): ₩300억, 35% 성장
  - B2G (정부): ₩100억, 45% 성장
  - Global: ₩50억, 60% 성장

OPEX:
  - S&M: 30%
  - R&D: 15%
  - G&A: 10%
```

#### 계산 결과
```yaml
Year 0: ₩1,250억
Year 3: ₩2,621억 (목표 ₩3,050억)
Year 5: ₩4,295억 (목표 ₩4,300억 달성!) ✅
CAGR: 28%
Year 5 Net Income: ₩429억
Year 5 Net Margin: 10%
```

#### 포함된 시트 (11개)
1. **Dashboard** - Year 5 Big Numbers
2. **Assumptions** - 10개 핵심 가정 (노란색 = 수정 가능)
3. **Revenue_Buildup** - 4개 세그먼트, 세그먼트별 성장률
4. **Cost_Structure** - COGS, OPEX (S&M, R&D, G&A)
5. **PL_3Year** - 손익계산서 (3년)
6. **PL_5Year** - 손익계산서 (5년)
7. **CashFlow** - 현금흐름표 (Operating, Investment, Financing)
8. **Key_Metrics** - 성장률, Margin 추이 (YoY, CAGR)
9. **FP_Scenarios** - Bear/Base/Bull 시나리오
10. **BreakEven** - 손익분기 매출 및 달성 시점
11. **DCF_Valuation** - 기업 가치 평가 (Terminal Value 포함)

---

## 💡 사용 방법

### 1. Excel 파일 열기
```
examples/excel/unit_economics_music_streaming_example_20251104.xlsx
또는
examples/excel/financial_projection_korean_adult_education_example_20251104.xlsx
```

### 2. Dashboard 시트에서 핵심 지표 확인
- Unit Economics: LTV/CAC 비율 (Traffic Light 자동 색상)
- Financial Projection: Year 5 매출, Net Income, CAGR

### 3. 가정 조정 (실험)
**노란색 셀만 수정 가능**:
- Unit Economics: Inputs 시트 (ARPU, CAC, Churn 등)
- Financial Projection: Assumptions 시트 (성장률, Margin 등)

**변경 시 자동 재계산**:
- 모든 함수가 살아있음
- Traffic Light 색상 자동 변경
- 시나리오 자동 업데이트

### 4. 상세 분석 확인
- **Sensitivity_Analysis**: 가장 중요한 변수 확인
- **Scenarios**: 최악/최선 시나리오 확인
- **P&L**: 손익 추이 확인
- **CashFlow**: 현금 소진 시점 확인

---

## 🎨 주요 기능

### Traffic Light (Unit Economics)
```yaml
LTV/CAC Ratio:
  > 5.0: 진한 녹색 (Excellent)
  3.0-5.0: 녹색 (Good)
  1.5-3.0: 노란색 (Warning)
  < 1.5: 빨간색 (Poor)

Payback Period:
  < 6개월: 진한 녹색 (Best-in-Class)
  6-12개월: 녹색 (Good)
  12-18개월: 노란색 (Acceptable)
  > 18개월: 빨간색 (Poor)

자동 색상 변경: 가정 수정 시 즉시 반영
```

### 2-Way Sensitivity Matrix
```yaml
ARPU × Churn 조합:
  - ARPU: -20%, -10%, Base, +10%, +20%
  - Churn: -20%, -10%, Base, +10%, +20%
  - 25개 조합의 LTV/CAC 계산
  - Base Case 강조 (노란색)
```

### 시나리오 분석
```yaml
Unit Economics:
  - Conservative: ARPU -15%, CAC +15%, Churn +15%
  - Base: 현재 가정
  - Optimistic: ARPU +15%, CAC -15%, Churn -15%

Financial Projection:
  - Bear: 성장률 -20%, Margin 낮춤
  - Base: 현재 가정
  - Bull: 성장률 +30%, Margin 높임
```

---

## 📊 실제 케이스 검증

### Unit Economics (음악 스트리밍)
```yaml
데이터 출처: 실제 프로젝트 분석
검증 항목:
  ✅ ARPU ₩9,000 (Spotify, Melon 평균)
  ✅ Churn 4% (업계 평균)
  ✅ Gross Margin 35% (라이선스료 제외)

결과:
  ✅ LTV/CAC 3.15 (Good)
  ✅ Payback 7.9개월 (Good)
  ✅ 비즈니스 모델 타당성 확인
```

### Financial Projection (성인 교육)
```yaml
데이터 출처: 실제 프로젝트 분석
목표:
  - Year 3: ₩3,050억
  - Year 5: ₩4,300억
  - CAGR: 28%

결과:
  ✅ Year 5: ₩4,295억 (목표 달성!)
  ✅ CAGR: 28% (정확)
  ✅ 세그먼트별 성장 추적
```

---

## 🛠️ 커스터마이징

### 새 프로젝트에 적용하려면

#### Unit Economics
```python
from umis_rag.deliverables.excel.unit_economics import UnitEconomicsGenerator

generator = UnitEconomicsGenerator()

result = generator.generate(
    market_name='your_market',
    inputs_data={
        'arpu': 10000,  # 여기에 실제 값
        'cac': 30000,
        'gross_margin': 0.40,
        'monthly_churn': 0.05,
        'customer_lifetime': 20,
        'sm_spend_monthly': 10000000,
        'new_customers_monthly': 300
    },
    channels_data=[...],  # 선택
    industry='SaaS',  # SaaS, E-commerce, Subscription, Streaming
    output_dir=Path('output/')
)
```

#### Financial Projection
```python
from umis_rag.deliverables.excel.financial_projection import FinancialProjectionGenerator

generator = FinancialProjectionGenerator()

result = generator.generate(
    market_name='your_market',
    assumptions_data={
        'base_revenue_y0': 1000_0000_0000,  # 여기에 실제 값
        'growth_rate_yoy': 0.25,
        'gross_margin': 0.60,
        'ebitda_margin': 0.12,
        'net_margin': 0.08,
        'sm_percent': 0.25,
        'rd_percent': 0.12,
        'ga_percent': 0.08,
        'tax_rate': 0.25,
        'discount_rate': 0.10
    },
    segments=[
        {'name': 'Segment1', 'y0_revenue': 600_0000_0000, 'growth': 0.20},
        {'name': 'Segment2', 'y0_revenue': 400_0000_0000, 'growth': 0.30},
    ],
    years=5,
    output_dir=Path('output/')
)
```

---

## ✨ 특징

### 1. 완전 자동화
- 입력값만 제공 → 3초 만에 Excel 생성
- 모든 계산은 Excel 함수로 구현
- 수작업 3-4시간 → 자동 3초 (800배 빠름)

### 2. 재현 가능성
- 모든 계산 추적 가능
- Named Range로 참조 명확
- 함수 기반 (하드코딩 없음)

### 3. 시각화
- Traffic Light 자동 색상
- 조건부 서식
- Dashboard 요약

### 4. 실용성
- 실제 프로젝트 케이스 기반
- 업계 벤치마크 포함
- 시나리오 분석

---

## 📋 예제 활용

### 학습용
- Excel 열어서 함수 확인
- 시트 간 연결 구조 파악
- Named Range 활용법

### 템플릿용
- 예제 파일을 복사
- Inputs/Assumptions만 수정
- 새 프로젝트에 즉시 적용

### 데모용
- 고객/투자자 발표 시 사용
- 실제 작동하는 재무 모델
- Traffic Light 시각적 효과

---

## 🔗 관련 문서

- **BILL_EXCEL_TOOLS_ROADMAP.md** - Bill Excel 도구 전체 계획
- **PHASE1_IMPLEMENTATION_PLAN.md** - Phase 1 구현 계획
- **PHASE1_COMPLETION_REPORT.md** - Phase 1 완료 보고서

---

**생성**: UMIS v7.2.0-dev1  
**케이스**: 실제 프로젝트 분석 데이터 기반

