
# 벤치마크 데이터 검증 가이드

## 1. 신뢰도 등급별 출처

### S급 (공식 통계)
- 통계청, 한국은행, World Bank
- 정부 공시자료 (DART)
- 사용: 무조건 우선

### A급 (업계 표준)
- Gartner, IDC, Forrester
- McKinsey, BCG
- 사용: 신뢰 가능, 원출처 확인

### B급 (전문 조사)
- Baymard Institute (UX/전환율)
- ProfitWell (SaaS)
- Littledata (이커머스)
- 사용: 샘플 크기 확인 후 사용

### C급 (일반 블로그, 언론)
- 사용: 보조 참고만

## 2. 검증 프로세스 (3단계)

### Step 1: 출처 확인
- [ ] 최소 3개 출처에서 유사한 값?
- [ ] 출처의 신뢰도 등급?
- [ ] 데이터 수집 년도 (2023-2024)?

### Step 2: 정의 일치 확인
- [ ] 계산 방법 동일?
- [ ] 모집단 동일? (B2B vs B2C)
- [ ] 측정 기간 동일? (월간 vs 연간)

### Step 3: 논리적 검증
- [ ] 상식적으로 타당?
- [ ] 국가 간 차이 설명 가능?
- [ ] 산업 특성과 일치?

## 3. 국가별 검증 전략

### 한국
**주요 출처**:
1. 통계청 (kostat.go.kr)
   - 온라인쇼핑 동향조사
   - 월간, 무료
   
2. 기업 공시 (DART)
   - 쿠팡, 네이버, 카카오 실적
   - 분기별
   
3. 산업 협회
   - 한국콘텐츠진흥원
   - 전자상거래협회

**검증 팁**:
- 네이버, 쿠팡 IR 자료 참조
- "한국 전환율 높음" → 간편결제, 빠른 배송 근거
- 모바일 비중 80%+ → 과학기술정보통신부 통계

### 일본
**주요 출처**:
1. Ministry of Economy (METI)
2. 일본 전자상거래협회
3. Rakuten, Yahoo Japan 공시

**검증 팁**:
- "일본 전환율 낮음" → 현금 문화, 신중한 구매
- "일본 충성도 높음" → 문화적 요인

### 미국
**주요 출처**:
1. US Census Bureau (이커머스 통계)
2. eMarketer (디지털 마케팅)
3. 상장사 공시 (SEC EDGAR)

## 4. 의심 신호 (Red Flags)

⚠️ 다음 경우 재검증:
- 출처가 1개뿐
- 출처가 3년 이상 된 데이터
- 국가 간 차이가 5배 이상
- "업계 평균"이라고만 하고 출처 없음
- 블로그/언론 인용이 출처
- 너무 정확한 값 (예: "3.247%")

## 5. 실전 검증 예시

### 예시 1: 한국 이커머스 전환율

**주장**: "3.5-4.5%"

**검증**:
1. 통계청 전자상거래 동향
   → 거래액은 있지만 전환율 직접 발표 X
   
2. 쿠팡 IR (2023)
   → Active customers, 주문 수 공개
   → 역산 가능
   
3. Statista Korea E-commerce
   → "한국 모바일 전환율 글로벌 대비 높음" (정성적)
   
4. Baymard Institute
   → 글로벌 평균 2.5-3%
   → 한국이 1.5배 높다면 3.75-4.5%
   
**결론**: 합리적 범위 ✅

### 예시 2: 일본 Churn 낮음

**주장**: "0.8-1.5% (B2B SaaS)"

**검증**:
1. ProfitWell Global
   → B2B 평균 1-2%
   
2. 문화적 요인
   → 일본 고객 충성도 높음 (일반적 인식)
   
3. 일본 SaaS 기업 공시
   → Sansan, Freee 등 확인 가능
   
**결론**: 문화적으로 타당, 실제 데이터로 검증 필요 ⚠️

## 6. 자동화 가능 검증

```python
def quick_sanity_check(metric, value, country):
    '''빠른 상식 체크'''
    
    # 전환율은 0-100% 범위
    if 'conversion' in metric and extract_percent(value) > 50:
        return "ERROR: 전환율 > 50%는 비정상"
    
    # Churn은 0-100% 범위
    if 'churn' in metric and extract_percent(value) > 50:
        return "WARNING: Churn > 50%는 매우 높음"
    
    # 국가 간 차이가 10배 이상이면 의심
    if check_country_variance(metric) > 10:
        return "WARNING: 국가 간 차이 과다"
    
    return "PASS"
```

## 7. 권장 검증 프로세스

### 우선순위 1: 공식 통계 (있으면 사용)
→ 통계청, 한국은행, DART

### 우선순위 2: 업계 표준 리포트
→ Gartner, Statista (유료지만 신뢰)

### 우선순위 3: 전문 조사기관
→ Baymard, ProfitWell (특화 분야)

### 우선순위 4: 역산
→ 상장사 공시에서 역산
   예: MAU, Revenue → ARPU 계산

### 우선순위 5: 전문가 판단
→ 출처 없으면 "추정" 명시
   3개 이상 출처에서 범위 확인될 때까지

## 8. 메타데이터 추가 권장

각 벤치마크에 추가:
```yaml
- benchmark_id: "BMK_EC_001"
  metric: "Conversion Rate"
  value: "3.5-4.5%"
  
  validation:  # 추가!
    sources:
      - name: "Baymard Institute"
        year: 2024
        url: "..."
        value: "2.5-3% (글로벌)"
      
      - name: "통계청"
        year: 2023
        note: "역산 (거래액/방문자)"
        value: "3.8% 추정"
    
    confidence: "Medium"  # High/Medium/Low
    last_verified: "2025-11-03"
    notes: "한국 특화 간편결제 고려"
```

## 9. 즉시 검증 가능한 메트릭

### 웹에서 무료 확인 가능:
- Cart Abandonment: Baymard Institute
- SaaS Churn: ProfitWell
- 이커머스 전환율: Littledata
- Mobile vs Desktop: StatCounter

### 공시자료 역산 가능:
- ARPU: 매출 / MAU
- CAC: S&M Spend / New Customers
- LTV: ARPU × Lifetime

### 추정 필요 (출처 부족):
- 국가별 세부 차이
- 신생 산업 메트릭

## 10. 검증 우선순위

**즉시 검증 필요**:
1. 투자 의사결정에 사용
2. 고객에게 제시
3. 공개 발표

**나중 검증 가능**:
1. 내부 참고용
2. 대략적 추정
3. 방향성 파악

---

**원칙**: "출처 불명 > 추정 명시 > 나중에 검증"
        "확실하지 않으면 범위 넓게 + 출처 명시"
