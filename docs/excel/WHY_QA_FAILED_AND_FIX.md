# 왜 QA가 오류를 못 잡았나? (근본 분석)

**작성일**: 2025-11-04  
**배경**: 사용자가 발견한 5가지 오류를 QA 시스템이 전혀 잡아내지 못함

---

## 🐛 발견된 오류 (사용자 피드백)

### 1. Summary C10~C13: 빈 셀 (B7) 참조
```yaml
오류:
  C10 = =B10/B7*100
  C11 = =B11/B7*100
  ...

문제: B7은 빈 셀!
정답: B6 (SAM 평균) 참조해야 함
```

### 2. Summary B18: 잘못된 행 참조
```yaml
오류: =Convergence_Analysis!C17
정답: =Convergence_Analysis!B9 (표준편차)

문제: C17은 존재하지 않거나 다른 값
```

### 3. Summary B19: 잘못된 행 참조
```yaml
오류: =Convergence_Analysis!C18
정답: =Convergence_Analysis!B10 (CV%)
```

### 4. Summary B29-B32: 잘못된 행 참조
```yaml
오류: =Validation_Log!B19, B20, B21, B22
정답: =Validation_Log!B15, B16, B17, B18
```

### 5. Estimation_Details C, D, E 컬럼: 비어있음
```yaml
오류: C, D, E 컬럼 모두 빈 셀
정답: estimation_logic, base_data, calculation 값 필요
```

---

## ❌ 왜 QA가 못 잡았나?

### 현재 QA 시스템의 맹점

#### Level 1: Syntax 검증 (ExcelValidator)
```yaml
확인하는 것:
  - 자기 참조 (C5 = =C5*2)
  - #REF!, #DIV/0! 오류
  
못 잡는 것:
  ❌ B7 빈 셀 참조 → Syntax 정상! (B7 셀은 존재함)
  ❌ C17 잘못된 행 → Syntax 정상! (C17 셀도 존재함)
  ❌ C, D, E 비어있음 → Syntax 무관

판정: 모든 오류가 "Syntax 정상" ✅
```

#### Level 2: Golden Test (결과 중심)
```yaml
확인하는 것:
  - 주요 셀 22개만 검증
  - B5 (TAM), B6 (SAM), B10-B13 (4가지 SAM)
  
못 잡는 것:
  ❌ B18, B19 (부수 셀, 검증 안 함)
  ❌ C10-C13 (% 계산, 검증 안 함)
  ❌ B29-B32 (Validation 셀, 검증 안 함)
  ❌ Estimation_Details (마이너 시트, 검증 안 함)

판정: 검증한 22개만 정상, 나머지 모름
```

#### Level 3: 수식 참조 검증
```yaml
확인하는 것:
  - 수식에서 참조 추출
  - 참조 셀 내용 확인 (피상적)
  
못 잡는 것:
  ❌ B7이 "빈 셀"인지 모름
  ❌ C17이 "잘못된 행"인지 모름
  ❌ 의미론적 검증 부족 (Stdev vs Proxy Corr)

판정: 수식 존재만 확인, 논리 검증 못 함
```

---

## 💡 근본 원인

### 1. 하드코딩된 행 번호 의존
```python
# summary_builder.py
avg_sam_cell = f'B{row-2}'  # ❌ 동적 계산 (틀릴 수 있음)
ws.cell(row, 2).value = "=Convergence_Analysis!C17"  # ❌ 하드코딩

# 문제:
# - Convergence 시트 구조가 예상과 다르면 즉시 오류
# - row-2가 항상 B6이 아닐 수 있음
# - C17, C18, B19-B22 모두 틀림
```

### 2. Python은 Excel 계산 엔진이 없음
```yaml
한계:
  - openpyxl은 수식만 생성, 계산 안 함
  - data_only=True도 Excel에서 열어야 계산됨
  - B7이 빈 셀인지 Python으로는 알 수 없음

결과:
  - 수식 파일: 값 없음 (검증 불가)
  - CALCULATED 파일: 수동으로 값 넣어야 함
```

### 3. 부분적 검증
```yaml
Golden Test: 22개 셀만
전체 셀: 수백 개

커버리지: < 10%
→ 90% 셀은 미검증
```

---

## ✅ 해결 방법

### 즉시 해결 (완료)
```yaml
1. 모든 하드코딩 수정:
   ✅ C10-C13: B7 → B6
   ✅ B18: C17 → B9
   ✅ B19: C18 → B10
   ✅ B29-B32: B19-B22 → B15-B18
   ✅ Estimation_Details: 필드 추가

2. Named Range 활용:
   ✅ AvgSAM_Best/Base/Worst 추가
   → 행 번호 대신 의미 기반 참조
```

### 장기 해결 (v7.3.0)

#### 1. 시트 구조 명세화 (Spec-driven)
```yaml
각 시트의 예상 구조를 YAML로 정의:

convergence_analysis_spec:
  row_8:
    A: "평균"
    B: "=AVERAGE(B4:B7)"
    type: "핵심"
  
  row_9:
    A: "표준편차"
    B: "=STDEV(B4:B7)"
    type: "핵심"

검증:
  - 실제 시트와 spec 비교
  - 행 번호 자동 매칭
  - 수식 패턴 검증
```

#### 2. 동적 행 찾기
```python
# Before (하드코딩)
ws.cell(row, 2).value = "=Convergence_Analysis!B9"

# After (동적 찾기)
stdev_row = find_row_by_label('Convergence_Analysis', '표준편차')
ws.cell(row, 2).value = f"=Convergence_Analysis!B{stdev_row}"
```

#### 3. 전수 검증 (모든 셀)
```yaml
Golden Test 확장:
  - 주요 셀 22개 → 모든 계산 셀 검증
  - 빈 셀 검증 (B7 같은 거)
  - 수식 패턴 검증 (=B10/B6 vs =B10/B7)

커버리지: 10% → 90%+
```

#### 4. Excel 계산 엔진 통합
```yaml
옵션 A: xlwings 사용
  - 실제 Excel 실행
  - 계산 결과 자동 획득
  - 느림, Excel 설치 필요

옵션 B: formulas 라이브러리
  - Python Excel 엔진
  - 계산 가능
  - 완벽하지 않음

옵션 C: 현재 방식 유지
  - CALCULATED 버전 생성
  - Golden Test로 검증
  - 수동 보완
```

---

## 📊 개선 효과 예상

### Before (현재)
```yaml
자동 감지:
  - 자기 참조: ✅
  - #REF! 오류: ✅
  - 잘못된 셀 참조: ❌ (못 잡음)
  - 빈 셀 참조: ❌
  - 행 번호 오류: ❌

커버리지: ~30%
수동 확인: 필수
```

### After (v7.3.0 목표)
```yaml
자동 감지:
  - 자기 참조: ✅
  - #REF! 오류: ✅
  - 잘못된 셀 참조: ✅ (Spec 비교)
  - 빈 셀 참조: ✅ (전수 검증)
  - 행 번호 오류: ✅ (동적 찾기)

커버리지: ~90%
수동 확인: 최소화
```

---

## 💡 당장 사용 가능한 해결책

### 1. 시트 구조 문서화
```yaml
각 Builder가 자신의 구조 export:

convergence_builder.py:
  def get_layout(self):
      return {
          'avg_sam_row': 8,
          'stdev_row': 9,
          'cv_row': 10,
          'max_min_row': 11,
          ...
      }

summary_builder.py:
  conv_layout = convergence_builder.get_layout()
  ws.cell(row, 2).value = f"=Convergence_Analysis!B{conv_layout['stdev_row']}"
```

### 2. Named Range 확대
```yaml
더 많은 Named Range 정의:

Convergence에서:
  - Avg_SAM (B8)
  - StdDev_SAM (B9)
  - CV_SAM (B10)
  - MaxMin_Ratio (B11)

Summary에서:
  =Convergence_Analysis!StdDev_SAM
  → 행 번호 무관, 의미 기반
```

### 3. 검증 레벨 추가
```yaml
Level 4: 빈 셀 검증
  - 계산 결과 셀이 None이면 오류
  - B7 참조 → B7 = None → 오류!

Level 5: 수식 패턴 매칭
  - "% of Avg" → =B{row}/B6*100 패턴 기대
  - "Stdev" → =Convergence!B9 패턴 기대
  - 패턴 불일치 → 오류
```

---

## 🎯 실용적 결론

### 현실적 접근 (v7.2.0)
```yaml
완벽한 자동 검증: 불가능 (Excel 엔진 한계)

실용적 해결:
  1. 주요 셀 Golden Test (22개) ✅
  2. 사용자 수동 확인 1회
  3. 발견된 오류 → Generator 수정
  4. 재생성 → 다시 Golden Test
  
반복:
  사용자 피드백 → 수정 → 검증
  → 점점 안정화
```

### 완전 자동화 (v7.3.0+)
```yaml
투자 필요:
  - 시트 구조 명세 (YAML)
  - 동적 행 찾기 시스템
  - Named Range 확대
  - 전수 검증

효과:
  - 자동 감지율: 30% → 90%
  - 개발 시간: +2주
```

---

## 📋 현재 상태 (v7.2.0-dev3)

### 수정 완료 ✅
```yaml
사용자 발견 5가지:
  1. ✅ C10-C13: B7 → B6
  2. ✅ B18: C17 → B9
  3. ✅ B19: C18 → B10
  4. ✅ B29-B32: B19-B22 → B15-B18
  5. ✅ Estimation_Details: 필드 추가

모든 Dashboard/Summary 값: 정상 출력
```

### QA 시스템
```yaml
Syntax: 자기 참조, #REF! ✅
Golden: 22개 주요 셀 ✅
수식 참조: 부분적 ✅

한계: 하드코딩 오류 못 잡음 ❌
→ 사용자 피드백 필수
```

---

## 💡 권장 사용법

### 신규 Excel 개발 시
```
1. Generator 코드 작성
2. 예제 생성
3. Golden Test 실행 → 주요 셀만 검증
4. Excel 수동 열기 → 5-10분 확인
   - Summary/Dashboard 모든 셀 값 확인
   - 빈 셀 없는지
   - 이상한 값 없는지
5. 문제 발견 → Generator 수정
6. 재생성 → 다시 Golden Test
7. 반복 3-4회 → 안정화
```

### 현재 상태
```yaml
Market Sizing: 안정화 ✅ (5가지 오류 수정)
Unit Economics: 안정화 ✅
Financial Projection: 안정화 ✅

추가 테스트: 사용자 수동 확인 권장
```

---

## 🔗 관련 커밋

```yaml
오류 발견: 사용자 피드백
수정 커밋:
  - 680d27d: Summary 참조 수정 (1차)
  - 473fa8c: 예제 재생성
  - (현재): 5가지 모두 수정

검증: check_all_dashboards.py
```

---

**결론**: 

완벽한 자동 검증은 Python + openpyxl로는 불가능합니다.

**실용적 해결책**:
1. ✅ 주요 셀 Golden Test (22개)
2. ✅ 사용자 1회 수동 확인
3. ✅ 발견 → 즉시 수정
4. ✅ 재생성 → 재검증

현재: **5가지 오류 모두 수정 완료** ✅

