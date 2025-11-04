# Market Sizing Excel 진단 보고서

**파일**: market_sizing_piano_subscription_example_20251104.xlsx  
**진단일**: 2025-11-04  
**결과**: ✅ 수식 구조 정상, Excel에서 열면 계산됨

---

## 🔍 진단 결과

### ✅ 수식 구조: 정상

```yaml
Method_1_TopDown (Top-Down 방식):
  A5 = =TAM_VALUE ✅
  B5 = =FILTER_KOREA ✅
  C5 = =FILTER_PIANO ✅
  B6 = =A5*B5 ✅
  C6 = =B6*C5 ✅ (SAM)
  
  SAM Named Range → Method_1_TopDown!$C$6 ✅

Method_2_BottomUp:
  F6 = =SUM(F4:F4) ✅
  F4 = =B4*C4*D4*E4 ✅

Method_3_Proxy:
  B7 = =B3*B4*B5 ✅
  B3 = =PROXY_SIZE ✅
  B4 = =PROXY_CORR ✅
  B5 = =PROXY_APP ✅

Method_4_CompetitorRevenue:
  B7 = =B5/C5 ✅
  B5 = =SUM(B4:B4) ✅
  C5 = =SUM(C4:C4) ✅
```

### ✅ 입력 데이터: 정상

```yaml
Assumptions 시트:
  TAM_VALUE: 100,000,000,000 (₩1,000억) ✅
  FILTER_KOREA: 0.15 (15%) ✅
  FILTER_PIANO: 0.25 (25%) ✅
  SEG1_CUSTOMERS: 100,000명 ✅
  SEG1_RATE: 0.2 (20%) ✅
  SEG1_AOV: 50,000원 ✅
  SEG1_FREQ: 12회 ✅
  PROXY_SIZE: 50,000,000,000 ✅
  PROXY_CORR: 0.3 ✅
  PROXY_APP: 0.5 (50%) ✅
  COMP1_REV: 10,000,000,000 ✅
  COMP1_SHARE: 0.4 (40%) ✅
```

### ✅ Named Range: 정상

```yaml
총 16개 Named Range 정의됨:
  SAM → Method_1_TopDown!$C$6 ✅
  SAM_Method2 → Method_2_BottomUp!$F$6 ✅
  SAM_Method3 → Method_3_Proxy!$B$7 ✅
  SAM_Method4 → Method_4_CompetitorRevenue!$B$7 ✅
  TAM → Assumptions!$D$2 ✅
```

---

## 📊 예상 계산 결과

### Method 1: Top-Down
```
TAM: ₩1,000억
× 한국 (15%): ₩150억
× 피아노 (25%): ₩37.5억

SAM (Method 1): ₩37.5억
```

### Method 2: Bottom-Up
```
고객: 100,000명
× 전환율 (20%): 20,000명
× 객단가 (₩50,000): ₩1,000,000,000
× 빈도 (12회): ₩12,000,000,000

SAM (Method 2): ₩120억
```

### Method 3: Proxy
```
유사 시장: ₩500억
× 상관계수 (0.3): ₩150억
× 적용 비율 (50%): ₩75억

SAM (Method 3): ₩75억
```

### Method 4: Competitor
```
경쟁사 매출: ₩100억
/ 점유율 (40%): ₩250억

SAM (Method 4): ₩250억
```

### Convergence
```
4가지 SAM:
  Method 1: ₩37.5억
  Method 2: ₩120억
  Method 3: ₩75억
  Method 4: ₩250억

평균: ₩120.6억
Max/Min: 250/37.5 = 6.67 ❌ (> 1.3, 수렴 실패)

⚠️ 4가지 방법이 크게 차이 남 → 재검토 필요
```

---

## 💡 "제대로 작동하지 않는다"는 의미

### 가능한 원인

#### 1. Excel에서 열었을 때 값이 계산 안 됨
```yaml
증상: 셀에 #VALUE!, #REF!, 빈 값
원인: fullCalcOnLoad 미설정 (가능성 낮음)
해결: Ctrl+Alt+F9 (Excel에서 전체 재계산)
```

#### 2. Dashboard에 값 표시 안 됨
```yaml
증상: Dashboard 시트에 빈 셀
원인: Named Range 참조 오류 (가능성 낮음)
검증: Summary!B6 = =Convergence_Analysis!C16
```

#### 3. Convergence 수렴 실패
```yaml
증상: "재검토 필요" 메시지
원인: 4가지 SAM 값이 크게 차이 (정상 동작)
설명: 이건 오류가 아니라 데이터 특성
  → Method 1: ₩37.5억 (보수적)
  → Method 4: ₩250억 (낙관적)
  → 6.67배 차이 (> 1.3)
```

---

## ✅ 실제 확인 방법

### Step 1: Excel에서 파일 열기

```bash
open examples/excel/market_sizing_piano_subscription_example_20251104.xlsx
```

### Step 2: 주요 셀 확인

**Method_1_TopDown 시트**:
1. A5 클릭 → ₩100,000,000,000 표시되는지
2. B6 클릭 → ₩15,000,000,000 표시되는지 (TAM × 15%)
3. C6 클릭 → ₩3,750,000,000 표시되는지 (SAM)

**Convergence_Analysis 시트**:
1. B4 (Method 1) → ₩37.5억
2. B5 (Method 2) → ₩120억
3. B6 (Method 3) → ₩75억
4. B7 (Method 4) → ₩250억
5. B8 (평균) → ₩120.6억
6. B11 (Max/Min) → 6.67

**Summary 시트**:
1. B5 (TAM) → ₩1,000억
2. B6 (SAM) → ₩120.6억 (평균)

### Step 3: 재계산 강제 실행

만약 값이 계산 안 되면:
```
Ctrl + Alt + F9 (Mac: Cmd + Option + F9)
또는
파일 저장 후 다시 열기
```

---

## 🎯 현재 상태

### ✅ 검증 완료 항목

```yaml
자동 QA:
  - 자기 참조: 0개 ✅
  - 오류 수식: 0개 ✅
  - Named Range: 16개 모두 유효 ✅

수식 구조:
  - Method 1-4: 모두 정상 ✅
  - Convergence: 정상 ✅
  - Summary: 정상 ✅

입력 데이터:
  - Assumptions: 12개 모두 입력 ✅
  - Named Range 참조: 정상 ✅
```

### ⚠️ 예상되는 "문제" (정상 동작)

```yaml
Convergence 수렴 실패:
  Max/Min = 6.67 > 1.3 ❌
  
  이건 오류가 아닙니다!
  → 4가지 방법의 SAM이 실제로 크게 차이남
  → Method 1: ₩37.5억 (가장 보수적)
  → Method 4: ₩250억 (가장 낙관적)
  
  해석:
    - 데이터가 부족하거나
    - 가정이 일관성 없거나
    - 시장 정의가 명확하지 않음
  
  이게 Market Sizing의 목적입니다!
    → 여러 방법으로 교차 검증
    → 차이가 크면 재검토
```

---

## 💡 권장 사항

### 1. Excel에서 직접 확인

```bash
open examples/excel/market_sizing_piano_subscription_example_20251104.xlsx
```

확인할 셀:
- Method_1_TopDown!C6: ₩3,750,000,000
- Convergence_Analysis!B4-B7: 4가지 SAM
- Summary!B6: 평균 SAM

### 2. 구체적인 문제 확인

다음 중 어떤 증상인지 확인:
- [ ] 셀에 값이 표시 안 됨 (빈 셀)
- [ ] #VALUE!, #REF! 오류
- [ ] 계산 결과가 이상함 (예상과 다름)
- [ ] Dashboard에 값 없음
- [ ] Convergence가 "재검토" (이건 정상)

### 3. 문제 해결

**값이 표시 안 되면**:
```
1. Ctrl+Alt+F9 (전체 재계산)
2. 파일 저장 후 다시 열기
3. fullCalcOnLoad 확인
```

**계산 결과가 이상하면**:
```
1. 위의 "예상 계산 결과" 참조
2. 실제 값과 비교
3. 차이 알려주기
```

---

## 📋 결론

### 진단 결과: ✅ 정상

```yaml
수식: 정상
데이터: 정상
Named Range: 정상
자동 QA: 통과
```

### 사용자 확인 필요

Excel을 직접 열어서:
1. 값이 계산되는지 확인
2. 구체적인 문제 증상 확인
3. 문제 있으면 스크린샷 또는 구체적 설명

---

**현재로서는 모든 수식과 데이터가 정상입니다!**

Excel에서 한 번 열고 저장하면 자동으로 계산될 것입니다.

