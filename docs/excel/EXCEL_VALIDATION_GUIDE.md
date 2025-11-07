# Excel 검증 가이드 (수동 + 자동)

**작성일**: 2025-11-04  
**목적**: 생성된 Excel 파일의 계산 결과 정확성 확인

---

## 🔍 문제 상황

```yaml
자동 검증 한계:
  - openpyxl: 수식만 저장, 계산값 없음
  - data_only=True: Excel에서 열어야 값 계산됨
  - 수식 패턴은 정상이지만 실제 계산 결과는 미확인

필요:
  - 실제 계산 결과 확인
  - Golden Workbook과 비교
  - 오차 < 1% 검증
```

---

## ✅ 수동 검증 가이드

### Step 1: Excel 파일 열기

```bash
# macOS
open examples/excel/financial_projection_korean_adult_education_example_20251104.xlsx
open examples/excel/golden_financial_projection.xlsx

# Windows
start examples/excel/financial_projection_korean_adult_education_example_20251104.xlsx
start examples/excel/golden_financial_projection.xlsx
```

### Step 2: 주요 셀 값 비교

#### Financial Projection

**생성 파일** (financial_projection_korean_adult_education_example_20251104.xlsx):

1. **Revenue_Buildup 시트** 확인
   ```
   셀 위치 → 확인할 값 (정답)
   
   B9 (Total Revenue Year 0): ₩125,000,000,000 (₩1,250억)
   C9 (Total Revenue Year 1): ₩160,000,000,000 (₩1,600억)
   D9 (Total Revenue Year 2): ₩204,800,000,000 (₩2,048억)
   E9 (Total Revenue Year 3): ₩262,144,000,000 (₩2,621억)
   G9 (Total Revenue Year 5): ₩429,496,729,600 (₩4,295억)
   
   확인:
   - 모든 셀에 값이 있는가? (빈 셀 없음)
   - Year 1 = Year 0 × 1.28 인가?
   - Golden과 오차 < 1%인가?
   ```

2. **Cost_Structure 시트** 확인
   ```
   B6 (COGS Year 0): ₩37,500,000,000 (₩375억)
     = Revenue × 30% (1 - Gross Margin 70%)
   
   C6 (COGS Year 1): ₩48,000,000,000 (₩480억)
     = Year 1 Revenue × 30%
   
   확인:
   - COGS가 같은 해 Revenue의 30%인가?
   - 다음 해 Revenue를 참조하지 않는가?
   ```

3. **PL_5Year 시트** 확인
   ```
   Revenue Year 5 → ₩4,295억
   Net Income Year 5 → ₩429억 (Revenue의 10%)
   
   확인:
   - Net Income = Revenue × 10%인가?
   - Golden과 일치하는가?
   ```

4. **Dashboard 시트** 확인
   ```
   B5 (Revenue Year 5): ₩4,295억
   B6 (Net Income Year 5): ₩429억
   B7 (CAGR): 28%
   
   확인:
   - 값이 표시되는가? (빈 셀 아님)
   - Golden과 일치하는가?
   ```

#### Unit Economics

**생성 파일** (unit_economics_music_streaming_example_20251104.xlsx):

1. **LTV_Calculation 시트** 확인
   ```
   B9 (LTV 방법 1): ₩78,750
     = 9,000 × 25 × 0.35
   
   B16 (LTV 방법 2): ₩78,750
     = 9,000 × 0.35 / 0.04
   
   B18 (LTV 평균): ₩78,750
     = (78,750 + 78,750) / 2
   
   확인:
   - 두 방법 모두 ₩78,750인가?
   - Golden과 일치하는가?
   ```

2. **LTV_CAC_Ratio 시트** 확인
   ```
   B7 (LTV/CAC Ratio): 3.15
     = 78,750 / 25,000
   
   확인:
   - 3.15인가?
   - 녹색 (Good)인가?
   - Golden과 일치하는가?
   ```

3. **Dashboard 시트** 확인
   ```
   B5 (LTV): ₩78,750
   B6 (CAC): ₩25,000
   B7 (LTV/CAC): 3.15
   
   확인:
   - 모두 값이 표시되는가?
   - Traffic Light가 녹색인가?
   ```

---

## 📋 검증 체크리스트

### Financial Projection ✅/🚫

- [ ] Revenue_Buildup
  - [ ] Year 0: ₩1,250억 (B9)
  - [ ] Year 1: ₩1,600억 (C9)
  - [ ] Year 5: ₩4,295억 (G9)
  - [ ] 빈 셀 없음

- [ ] Cost_Structure
  - [ ] COGS Year 0: ₩375억 (B6) = Revenue × 30%
  - [ ] COGS Year 1: ₩480억 (C6) = Year 1 Revenue × 30%
  - [ ] 컬럼이 밀리지 않음

- [ ] PL_5Year
  - [ ] Revenue Year 5: ₩4,295억
  - [ ] Net Income Year 5: ₩429억 (10%)
  - [ ] EBITDA Year 5: ₩644억 (15%)

- [ ] Dashboard
  - [ ] 값이 표시됨 (빈 셀 없음)
  - [ ] Golden과 일치

### Unit Economics ✅/🚫

- [ ] LTV_Calculation
  - [ ] LTV 방법 1: ₩78,750
  - [ ] LTV 방법 2: ₩78,750
  - [ ] LTV 평균: ₩78,750

- [ ] LTV_CAC_Ratio
  - [ ] Ratio: 3.15
  - [ ] 녹색 (Good)

- [ ] Dashboard
  - [ ] LTV: ₩78,750
  - [ ] CAC: ₩25,000
  - [ ] Ratio: 3.15
  - [ ] Traffic Light 녹색

---

## 🐛 자주 발생하는 오류 패턴

### 1. 자기 참조
```
오류: C5 = =C5*(1+$H$5)
정상: C5 = =B5*(1+$H$5)

원인: col_letter = chr(65 + col) (잘못)
수정: col_letter = chr(64 + col) (정확)
```

### 2. 컬럼 밀림
```
오류: COGS Year 0 = Revenue Year 1
정상: COGS Year 0 = Revenue Year 0

원인: col_letter = chr(65 + col)
수정: col_letter = chr(64 + col)
```

### 3. Named Range 참조 실패
```
오류: Dashboard에 값 없음
원인: Revenue_Y0가 정의 안 됨 또는 잘못된 셀 참조

확인: Named Range 정의 확인
```

---

## 💡 Excel 열어서 확인하는 방법

### 수식 확인 (F2 키)

```
1. Revenue_Buildup 시트 열기
2. C5 셀 클릭
3. F2 키 누르기 (수식 편집 모드)
4. 수식 확인: =B5*(1+$H$5)
   - B5: 이전 해 (Year 0)
   - H5: 성장률
   - C5 자기 참조 없음

정상 패턴:
  C5 = =B5*(1+$H$5)
  D5 = =C5*(1+$H$5)
  E5 = =D5*(1+$H$5)

비정상 패턴:
  C5 = =C5*(1+$H$5) 🚫 (자기 참조!)
```

### 계산 결과 확인

```
1. 셀 클릭
2. 값 확인
3. Golden Workbook의 같은 위치 값과 비교

예:
  생성: B9 = 125,000,000,000
  Golden: B5 = 125,000,000,000
  → 일치 ✅
```

### 자동 재계산 확인

```
1. Assumptions 시트 열기
2. B8 (GrowthRateYoY) 클릭
3. 28% → 35%로 변경
4. Enter
5. Revenue_Buildup으로 이동
6. Year 5 값이 자동 증가했는가?

정상: 자동 재계산 ✅
비정상: 값 그대로 (수식 오류)
```

---

## 🎯 권장 검증 프로세스

### 신규 Excel 생성 시

```
Step 1: 자동 검증 실행
  python scripts/qa_all_example_files.py
  → 자기 참조, 오류 수식 감지

Step 2: 수식 패턴 비교
  python scripts/compare_with_golden.py
  → 주요 수식 패턴 확인

Step 3: Excel 수동 확인 (최종)
  1. Excel 파일 열기
  2. 주요 셀 5-10개 값 확인
  3. Golden과 비교
  4. 가정 변경 → 자동 재계산 확인

모두 통과 → 배포 ✅
하나라도 실패 → Generator 수정
```

---

## 📊 현재 검증 상태 (2025-11-04)

### 자동 검증 (QA)
```yaml
Market Sizing: ✅ 통과
  - 자기 참조: 0개
  - 오류 수식: 0개

Unit Economics: ✅ 통과
  - 자기 참조: 0개
  - 오류 수식: 0개
  - 수식 패턴: 정상

Financial Projection: ✅ 통과 (QA)
  - 자기 참조: 0개
  - 오류 수식: 0개
  - 수식 패턴: 대부분 정상
```

### 수동 검증 (필요)
```yaml
실제 계산 결과:
  - Excel에서 열어서 확인 필요
  - Golden과 값 비교 필요
  - 자동 재계산 확인 필요

추천: 사용자가 직접 Excel 열어서 확인
```

---

## 🔗 관련 파일

```
Golden Workbooks (정답지):
  - examples/excel/golden_financial_projection.xlsx
  - examples/excel/golden_unit_economics.xlsx

생성 파일 (검증 대상):
  - examples/excel/financial_projection_korean_adult_education_example_20251104.xlsx
  - examples/excel/unit_economics_music_streaming_example_20251104.xlsx
  - examples/excel/market_sizing_piano_subscription_example_20251104.xlsx

검증 스크립트:
  - scripts/qa_all_example_files.py (자동 QA)
  - scripts/compare_with_golden.py (수식 패턴)
  - scripts/create_golden_workbook.py (Golden 생성)
```

---

**다음 단계**:

Excel 파일을 직접 열어서 다음을 확인해주세요:

1. `financial_projection_korean_adult_education_example_20251104.xlsx` 열기
2. Revenue_Buildup → B9, C9, G9 값 확인
3. `golden_financial_projection.xlsx` 열기
4. B5, C5, E5 값과 비교
5. 일치하면 ✅, 다르면 오류 위치 알려주세요

실제 값을 확인해야 정확한 문제를 찾을 수 있습니다!

