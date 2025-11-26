# 실제 데이터 수집 가이드
**목적**: 검증 가능한 실제 profit margin 데이터 수집
**대상**: 한국 오프라인 비즈니스 우선

---

## 📊 데이터 소스 1: 통계청 기업경영분석

### 접근 방법

**1. 웹사이트 접속**
```
URL: https://kostat.go.kr
경로: 홈 → 국가통계포털 → 기업경영분석
또는: https://kosis.kr → 기업경영분석
```

**2. 데이터 찾기**
```
검색: "기업경영분석"
선택: "기업경영분석(전수조사)"
카테고리: "산업별 재무비율"
```

**3. 다운로드할 데이터**
```
산업분류 (KSIC):
  - 56: 음식점 및 주점업
  - 47: 소매업 (편의점 포함)
  - 55: 숙박업
  - 86: 보건업
  - 85: 교육 서비스업
  - 96: 미용, 욕탕, 유사서비스업
  - 10-33: 제조업
  - 41-42: 건설업

확인 항목:
  - 매출총이익률
  - 영업이익률
  - 매출액순이익률
  - 기업 수
```

**4. YAML 변환**
```yaml
예시 (음식점업):

- benchmark_id: "margin_korea_restaurant_kostat_001"
  industry: "음식점업"
  region: "한국"
  
  margins:
    gross_margin: {median: 0.XXX}  # 실제 값
    operating_margin: {median: 0.XXX}  # 실제 값
  
  data_source:
    type: "verified"
    primary: "통계청 기업경영분석 2024"
    ksic_code: "56"
    data_url: "https://kosis.kr/..."
    collection_date: "2025-11-12"
    verification_method: "통계청 웹사이트 직접 조회"
  
  reliability: "verified"
  sample_size: XXXXX  # 실제 샘플 수
  year: 2024
```

---

## 📊 데이터 소스 2: 프랜차이즈 정보공개서

### 접근 방법

**1. 협회 웹사이트**
```
URL: https://www.ikfa.or.kr (한국프랜차이즈협회)
경로: 정보공개서 → 브랜드별 검색
```

**2. 주요 브랜드 정보공개서**
```
편의점:
  - GS25: GS리테일 정보공개서
  - CU: BGF리테일 정보공개서
  - 세븐일레븐: 코리아세븐 정보공개서

치킨:
  - 교촌치킨
  - BBQ
  - BHC

카페:
  - 투썸플레이스
  - 이디야커피
  - 빽다방
```

**3. 정보공개서에서 추출**
```
확인 항목:
  - 가맹점 평균 매출액
  - 초기 투자 비용
  - 월 평균 비용
  - 로열티율
  - 광고 분담금

계산:
  OPM = (평균 매출 - 평균 비용 - 로열티) / 평균 매출
```

**4. YAML 변환**
```yaml
예시 (GS25):

- benchmark_id: "margin_korea_cvs_gs25_001"
  industry: "편의점"
  sub_category: "GS25"
  region: "한국"
  
  margins:
    operating_margin: {median: 0.12}  # 계산된 값
  
  cost_structure:
    cogs: 0.68
    labor: 0.10
    rent: 0.05
    royalty: 0.03
    utilities: 0.02
    operating_profit: 0.12
  
  data_source:
    type: "franchise_disclosure"
    primary: "GS25 정보공개서 2024"
    company: "GS리테일"
    disclosure_url: "ikfa.or.kr/..."
    
    extraction: |
      정보공개서 분석:
      - 평균 매출: 월 XX만원
      - 인건비: 월 XX만원
      - 임대료: 월 XX만원
      - 로열티: 3%
      - OPM 계산: 12%
    
    collection_date: "2025-11-12"
  
  reliability: "franchise_verified"
  sample_size: 1  # GS25 브랜드
  year: 2024
```

---

## 📊 데이터 소스 3: DART 상장사

### 접근 방법

**1. DART 접속**
```
URL: https://dart.fss.or.kr
```

**2. 상장사 검색**
```
산업별 대표 기업:
  음식점:
    - 스타벅스코리아
    - 놀부
    - 아웃백스테이크하우스코리아
  
  소매:
    - 이마트
    - 롯데쇼핑
    - GS리테일 (편의점)
  
  헬스케어:
    - 차병원
    - 메디포스트
```

**3. 재무제표 확인**
```
사업보고서 → 재무제표:
  - 매출액
  - 매출원가
  - 매출총이익
  - 영업이익
  
계산:
  - Gross Margin = 매출총이익 / 매출액
  - Operating Margin = 영업이익 / 매출액
```

**4. YAML 변환**
```yaml
- benchmark_id: "margin_korea_coffee_starbucks_001"
  industry: "커피전문점"
  sub_category: "프리미엄 커피"
  region: "한국"
  
  margins:
    gross_margin: {value: 0.XX}  # 실제 계산
    operating_margin: {value: 0.XX}  # 실제 계산
  
  data_source:
    type: "verified"
    primary: "DART 전자공시"
    company: "스타벅스코리아"
    report: "2024년 사업보고서"
    
    calculation: |
      2024년 재무제표:
      - 매출액: XXX억원
      - 매출원가: XXX억원
      - 매출총이익: XXX억원
      - 영업이익: XXX억원
      
      계산:
      - Gross Margin: XXX / XXX = XX%
      - Operating Margin: XXX / XXX = XX%
    
    dart_url: "https://dart.fss.or.kr/..."
    collection_date: "2025-11-12"
  
  reliability: "verified"
  sample_size: 1  # 스타벅스코리아
  year: 2024
```

---

## 📊 한국 오프라인 비즈니스 우선순위

### Phase 1: 실제 데이터 확보 (15개)
```yaml
통계청 verified (10개):
  1. ✅ 음식점업 (KSIC 56)
  2. ✅ 소매업 (KSIC 47)
  3. ✅ 미용업 (KSIC 96)
  4. ✅ 병원 (KSIC 861)
  5. ✅ 의원 (KSIC 862)
  6. ✅ 학원 (KSIC 856)
  7. ✅ 세탁업 (KSIC 96)
  8. ✅ 숙박업 (KSIC 55)
  9. ✅ 제조업 (KSIC 10-33)
  10. ✅ 건설업 (KSIC 41-42)

프랜차이즈 정보공개서 (5개):
  1. ✅ GS25 (편의점)
  2. ✅ 교촌치킨
  3. ✅ 투썸플레이스 (카페)
  4. ✅ 파리바게뜨
  5. ✅ 애니타임피트니스 (헬스장)
```

### Phase 2: 투명 추정 (15개)
```yaml
추정 필요 (한국 오프라인):
  1. 헬스장 일반 (애니타임 기준 + 통계청)
  2. 네일샵 (미용업 세분)
  3. PC방 (협회 데이터)
  4. 노래방
  5. 분식점 (음식점 세분)
  6. 한식당 (음식점 세분)
  7. 중식당
  8. 일식당
  9. 치과 (협회)
  10. 스터디카페
  11. 코인세탁
  12. 애견샵
  13. 꽃집
  14. 문구점
  15. 찜질방

각각:
  - 추정 로직 명시
  - 통계청 상위 카테고리 참조
  - 교차 검증
  - Confidence range
```

---

## 🚀 실행 계획

### 즉시 (오늘):
1. 통계청 웹사이트 접속하여 실제 데이터 5개 확보
2. 프랜차이즈협회 정보공개서 3개 확인
3. YAML에 실제 데이터로 작성

제가 지금 시작하시겠습니까?

**Option A**: 제가 웹 검색으로 실제 데이터 찾기
**Option B**: 사용자님이 통계청 직접 확인 후 알려주기
**Option C**: 우선 10-15개 투명 추정으로 시작 (검증은 나중에)

어떤 방식이 좋을까요?





