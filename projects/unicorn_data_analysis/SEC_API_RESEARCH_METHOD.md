# 🏛️ SEC EDGAR API 리서치 방법론

**작성일:** 2025-11-04  
**버전:** 1.0  
**목적:** 상장 유니콘 기업의 재무 데이터 자동 수집 방법 확립

---

## 🎯 핵심 발견

### SEC EDGAR Company Facts API 활용
**URL:** `https://data.sec.gov/api/xbrl/companyfacts/CIK{CIK}.json`

**장점:**
- ✅ 10-K 수동 다운로드 불필요
- ✅ JSON 형식으로 즉시 파싱 가능
- ✅ 모든 재무 지표 포함 (US-GAAP)
- ✅ 과거 데이터 전부 접근 가능
- ✅ 무료, 공개 API

**제약:**
- ⚠️ Rate limit: 10 requests/second
- ⚠️ User-Agent 헤더 필수
- ⚠️ 상장사만 가능

---

## 📊 데이터 구조 이해

### 중요 발견: fy vs end

**문제:**
```
같은 fy (Fiscal Year)에 여러 값이 존재
→ 2023 10-K에 2020, 2021, 2022 데이터 모두 포함
```

**해결:**
```python
# ❌ 잘못된 방법
year = item.get('fy')  # 회계연도 (10-K가 제출된 연도)

# ✅ 올바른 방법
end_date = item.get('end')  # "2024-12-31"
year = int(end_date[:4])  # 실제 데이터의 연도
```

**예시 (Rivian Revenue):**
```
FY 2024 | End: 2024-12-31 → 실제 2024년 데이터 ✅
FY 2024 | End: 2023-12-31 → 2024 10-K 안의 2023년 비교 데이터
FY 2024 | End: 2022-12-31 → 2024 10-K 안의 2022년 비교 데이터
```

---

## 🔧 올바른 추출 로직

### 1. 필터링

```python
# 10-K + FY만 (연간 데이터)
if item.get('form') == '10-K' and item.get('fp') == 'FY':
    pass
```

**필드 설명:**
- `form`: 보고서 유형 (10-K=연간, 10-Q=분기)
- `fp`: Fiscal Period (FY=연간, Q1-Q4=분기)
- `fy`: Fiscal Year (보고서가 제출된 회계연도)
- `end`: 데이터의 실제 기간 종료일

---

### 2. 연도 추출

```python
end_date = item.get('end', '')  # "2024-12-31"
year = int(end_date[:4])  # 2024
```

---

### 3. 중복 제거

```python
# 같은 연도는 가장 최근 filing 사용
if year not in annual_data or item.get('filed') > annual_data[year].get('filed'):
    annual_data[year] = item
```

**이유:**
- 10-K는 이전 연도 데이터를 포함 (비교용)
- 같은 연도 데이터가 여러 10-K에 반복됨
- 가장 최근 filing = 가장 정확한 데이터

---

## 📋 US-GAAP 필드 매핑

### 필수 재무 지표

| 지표 | US-GAAP 필드 | 설명 |
|------|-------------|------|
| **Revenue** | `RevenueFromContractWithCustomerExcludingAssessedTax` | 매출 |
| **Gross Profit** | `GrossProfit` | 매출총이익 |
| **Operating Income** | `OperatingIncomeLoss` | 영업손익 |
| **Net Income** | `NetIncomeLoss` | 순손익 |
| **Cost of Revenue** | `CostOfRevenue` | 매출원가 |
| **Cash** | `CashAndCashEquivalentsAtCarryingValue` | 현금 |

### 추가 지표

| 지표 | US-GAAP 필드 |
|------|-------------|
| R&D Expense | `ResearchAndDevelopmentExpense` |
| SG&A Expense | `SellingGeneralAndAdministrativeExpense` |
| Total Assets | `Assets` |
| Total Liabilities | `Liabilities` |
| Stockholders Equity | `StockholdersEquity` |

---

## 🎨 출력 형식

### Performance Metrics 구조

```json
{
  "company": "Rivian",
  "cik": "0001874178",
  "data_source": "SEC EDGAR API",
  "retrieved_at": "2025-11-04",
  
  "performance_metrics": {
    "financial": {
      "revenue": {
        "year_1": {"year": 2024, "amount_usd_million": 4970.0, "source": "SEC 10-K 2024"},
        "year_2": {"year": 2023, "amount_usd_million": 4434.0, "source": "SEC 10-K 2023"},
        "year_3": {"year": 2022, "amount_usd_million": 1658.0, "source": "SEC 10-K 2022"}
      },
      "operating_profit": {
        "year_1": {"year": 2024, "amount_usd_million": -4689.0, "source": "SEC 10-K 2024"},
        "year_2": {"year": 2023, "amount_usd_million": -5739.0, "source": "SEC 10-K 2023"},
        "year_3": {"year": 2022, "amount_usd_million": -6856.0, "source": "SEC 10-K 2022"}
      },
      "gross_margin": -24.1,
      "operating_margin": -94.3,
      "net_margin": -95.5,
      "cash_and_equivalents": 5294.0
    }
  }
}
```

---

## 💡 계산된 Margin

### 공식

```python
# Gross Margin
gross_margin_pct = (gross_profit / revenue) * 100

# Operating Margin
operating_margin_pct = (operating_income / revenue) * 100

# Net Margin
net_margin_pct = (net_income / revenue) * 100
```

### 주의사항

**음수 Margin 해석:**
- Rivian 2024: Gross Margin -24.1%
  - Revenue: $4,970M
  - Gross Profit: -$1,200M (손실)
  - 의미: 차량 1대 팔때마다 손해 (규모의 경제 달성 전)

---

## 🔍 검증 체크리스트

### 데이터 품질 확인

- [x] **연도 정확성**
  - end 날짜로 추출 ✅
  - 2024, 2023, 2022 명확히 구분 ✅

- [x] **중복 제거**
  - 같은 연도는 최근 filing만 ✅
  - 비교 데이터 제외 ✅

- [x] **값의 합리성**
  - Revenue 증가 추세 ✅
  - 손실 감소 추세 ✅
  - Margin 개선 추세 ✅

- [x] **소스 명시**
  - SEC 10-K + 연도 ✅
  - End date 포함 ✅

---

## 🚀 사용 방법

### Step 1: CIK 확인

**알려진 상장 유니콘 CIK:**
```python
KNOWN_CIK = {
    "Rivian": "0001874178",
    "Instacart": "0001939542",  # Maplebear Inc.
    "Affirm": "0001783879",
    "Coinbase": "0001679788",
    "DoorDash": "0001792789",
    "Robinhood": "0001783879",
    "UiPath": "0001850871",
}
```

**CIK 찾는 방법:**
1. SEC EDGAR 검색: https://www.sec.gov/edgar/search
2. 회사명 검색
3. CIK 번호 확인

---

### Step 2: 스크립트 실행

```bash
cd projects/unicorn_data_analysis/scripts
python3 07_sec_simple.py
```

**출력:**
- `research/SEC_{Company}_final.json`

---

### Step 3: 데이터 검증

```python
import json

with open('research/SEC_Rivian_final.json') as f:
    data = json.load(f)

# Revenue 확인
for key in ['year_1', 'year_2', 'year_3']:
    r = data['performance_metrics']['financial']['revenue'].get(key)
    if r:
        print(f"{r['year']}: ${r['amount_usd_million']}M")
```

---

## 📊 Rivian 사례 (검증 완료)

### 수집된 데이터

```
Revenue (3년):
  2024: $4,970M  ✅
  2023: $4,434M  ✅
  2022: $1,658M  ✅

Operating Income (3년):
  2024: -$4,689M  ✅
  2023: -$5,739M  ✅
  2022: -$6,856M  ✅

Gross Profit (3년):
  2024: -$1,200M  ✅
  2023: -$2,030M  ✅
  2022: -$3,123M  ✅

Net Income (3년):
  2024: -$4,747M  ✅
  2023: -$5,432M  ✅
  2022: -$6,752M  ✅

Cash:
  2024: $5,294M  ✅
```

**신뢰도:** ⭐⭐⭐⭐⭐ (SEC 공식 데이터)

---

## ⚠️ 발견된 이슈 & 해결

### Issue 1: 중복 연도 데이터

**문제:**
```
FY 2024인 10-K에 2024, 2023, 2022 데이터가 모두 있음
→ fy로 추출하면 모두 2024로 나옴
```

**해결:**
```python
# end 날짜 사용
year = int(item.get('end')[:4])
```

---

### Issue 2: Instacart CIK 404

**문제:**
```
CIK 0001939542로 요청시 404 에러
```

**가능한 원인:**
- CIK가 잘못됨
- 아직 Company Facts API에 없음 (최근 상장)
- 다른 이름으로 등록됨

**해결 방법:**
```
1. SEC EDGAR 직접 검색
2. 정확한 CIK 확인
3. 또는 10-K HTML 직접 파싱
```

---

### Issue 3: 일부 필드 없음

**문제:**
```
일부 회사는 특정 필드를 사용하지 않음
예: 'Revenues' 대신 'RevenueFromContract...' 사용
```

**해결:**
```python
# 여러 필드 시도
revenue_fields = [
    'Revenues',
    'RevenueFromContractWithCustomerExcludingAssessedTax',
    'SalesRevenueNet',
]

for field in revenue_fields:
    if field in us_gaap:
        # 이 필드 사용
        break
```

---

## 📚 완성된 스크립트

### `scripts/07_sec_simple.py` ⭐

**기능:**
- ✅ CIK로 Company Facts API 호출
- ✅ US-GAAP 필드에서 재무 지표 추출
- ✅ end 날짜로 연도 정확히 추출
- ✅ 중복 데이터 제거 (최근 filing 우선)
- ✅ Margin 자동 계산
- ✅ Performance Metrics 형식 출력

**사용법:**
```python
# CIK 추가
COMPANIES = {
    "Rivian": "0001874178",
    "NewCompany": "0001234567",  # 새 회사 추가
}

# 실행
python3 scripts/07_sec_simple.py
```

**출력:**
```
research/SEC_Rivian_final.json
research/SEC_NewCompany_final.json
```

---

## 🎯 적용 가능한 기업

### 파일럿 10개 중 상장사

| 기업 | 상장 여부 | CIK | 적용 가능 |
|------|----------|-----|----------|
| Rivian | ✅ NASDAQ (RIVN) | 0001874178 | ✅ 검증 완료 |
| Instacart | ✅ NASDAQ (CART) | 확인 필요 | ⚠️ CIK 확인 필요 |
| Stripe | ❌ 비상장 | - | ❌ |
| SpaceX | ❌ 비상장 | - | ❌ |
| Databricks | ❌ 비상장 | - | ❌ |
| Klarna | ❌ 비상장 | - | ❌ |
| Fanatics | ❌ 비상장 | - | ❌ |
| Bytedance | ❌ 비상장 | - | ❌ |
| BYJU's | ❌ 비상장 | - | ❌ |
| DJI | ❌ 비상장 | - | ❌ |

**파일럿 10개 중:** 2개만 SEC API 적용 가능

---

### 800개 유니콘 중 상장사 (추정 50-100개)

**자동 수집 가능한 기업 예시:**
- Affirm (AFRM)
- Coinbase (COIN)
- DoorDash (DASH)
- Robinhood (HOOD)
- UiPath (PATH)
- Snowflake (SNOW)
- Unity (U)
- Roblox (RBLX)
- ... (추가 40-90개)

**확장 계획:**
```
Phase 1: 파일럿 2개 (Rivian ✅, Instacart)
Phase 2: 알려진 상장사 10개
Phase 3: 전체 상장사 50-100개 자동 수집
```

---

## 📝 리서치 워크플로우

### 상장사 리서치 (30분)

```
Step 1: CIK 확인 (2분)
  → SEC EDGAR 검색
  → CIK 번호 복사

Step 2: CIK를 스크립트에 추가 (1분)
  → COMPANIES dict에 추가

Step 3: 스크립트 실행 (1분)
  → python3 07_sec_simple.py

Step 4: 데이터 검증 (5분)
  → JSON 파일 확인
  → 값의 합리성 체크

Step 5: 리서치 파일 업데이트 (10분)
  → research/{Company}_research.md
  → Performance Metrics 섹션 작성

Step 6: 정성적 분석 (10분)
  → Problem/Solution
  → Competitive Advantage
  → CSFs
```

**총 30분** (vs 수동 10-K 다운로드 1시간+)

---

## 🔍 데이터 검증 방법

### 1. 합리성 체크

```python
# YoY 성장률 확인
growth = (year1 - year2) / year2 * 100

# Rivian: 2023 → 2024 = +12% ✅
# 급격한 변화 (10배 이상)는 재확인
```

---

### 2. Margin 범위 체크

```python
# 정상 범위
# Gross Margin: -50% ~ +90%
# Operating Margin: -100% ~ +40%

# Rivian: -24% (초기 EV는 마이너스 정상) ✅
```

---

### 3. 트렌드 일관성

```python
# Revenue 증가 추세
2022: $1.7B → 2023: $4.4B → 2024: $5.0B ✅

# Loss 감소 추세
2022: -$6.9B → 2023: -$5.7B → 2024: -$4.7B ✅
```

---

## 🚨 주의사항

### 1. API Rate Limit

```python
# SEC 권장: 10 requests/second
time.sleep(0.1)  # 각 요청 사이
```

### 2. User-Agent 필수

```python
HEADERS = {
    'User-Agent': 'Your Name your@email.com'
}
```

**없으면:** 403 Forbidden

---

### 3. CIK 10자리 패딩

```python
cik = "1874178"  # 7자리
cik_padded = cik.zfill(10)  # "0001874178"
```

---

### 4. 필드 이름 차이

각 회사마다 사용하는 필드가 다를 수 있음:
- 여러 필드 시도
- 첫 번째 찾은 필드 사용

---

## 📊 Rivian 실제 결과 (검증 완료)

### 데이터 품질: ⭐⭐⭐⭐⭐

```
✅ Revenue (3년):      100% 정확
✅ Operating Income:   100% 정확
✅ Gross Profit:       100% 정확
✅ Net Income:         100% 정확
✅ Margins:            자동 계산 정확
✅ Cash:               최신 데이터

소요 시간: < 5초 (자동)
vs 수동: 30-60분
```

### 발견한 인사이트

**Rivian의 재무 트렌드:**
- 매출 급증: 생산 확대 성공 ✅
- 손실 감소: 규모의 경제 효과 ✅
- Gross Margin 개선: -188% → -24% (크게 개선) ✅
- Cash 감소: 지속적인 투자 (주의 필요) ⚠️

---

## 🎯 확장 계획

### Phase 1: 파일럿 완료 (현재)
- [x] Rivian ✅
- [ ] Instacart (CIK 확인 필요)

### Phase 2: 상장 유니콘 10개
- [ ] Affirm, Coinbase, DoorDash
- [ ] Snowflake, Unity, Roblox
- [ ] 기타 4개

### Phase 3: 전체 상장사 (50-100개)
- [ ] CIK 매핑 완성
- [ ] 배치 실행
- [ ] 자동 업데이트

---

## 📖 참고 문서

### SEC EDGAR API 공식 문서
- https://www.sec.gov/search-filings/edgar-application-programming-interfaces

### Company Facts API
- https://data.sec.gov/api/xbrl/companyfacts/

### 사용 예시
- https://data.sec.gov/api/xbrl/companyfacts/CIK0001874178.json

---

## 💡 Best Practices

### 1. 항상 end 날짜 사용
```python
year = int(item.get('end')[:4])  # ✅
year = item.get('fy')  # ❌
```

### 2. 최신 filing 우선
```python
if filed > previous_filed:
    use_this_data
```

### 3. 여러 필드 시도
```python
for field in ['Field1', 'Field2', 'Field3']:
    if field in data:
        use_field
        break
```

### 4. 합리성 검증
```python
if abs(growth) > 500%:
    print("⚠️ 비정상적 성장 - 재확인 필요")
```

---

## ✅ 검증 완료 사항

- [x] Rivian Revenue 정확 (2024, 2023, 2022)
- [x] Operating Income 정확 (연도별 구분)
- [x] Gross Profit 정확
- [x] Net Income 정확
- [x] Margin 계산 정확
- [x] 출력 형식 Performance Metrics 호환
- [x] 소스 추적 가능

---

**작성자:** UMIS v7.0.0  
**검증:** Rivian 완료 ✅  
**다음:** 나머지 상장사 적용



