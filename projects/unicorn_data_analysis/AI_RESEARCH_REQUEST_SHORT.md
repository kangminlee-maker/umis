# 🤖 유니콘 기업 리서치 요청 (간단 버전)

다른 AI 플랫폼에 복사-붙여넣기 하세요.

---

## 📋 요청 내용

안녕하세요! 유니콘 기업 비즈니스 사례 데이터베이스 구축을 위해 **파일럿 10개 기업의 리서치**를 요청합니다.

---

## 🎯 리서치 대상 기업

1. **Rivian** ($27.60B, 미국, Auto) - ⭐ 최우선 (상장사, 쉬움)
2. **Instacart** ($39.00B, 미국, Logistics) - ⭐ 최우선 (상장사, 쉬움)
3. **Stripe** ($95.00B, 미국, Fintech) - ⭐⭐ 우선
4. **Databricks** ($28.00B, 미국, Data) - ⭐⭐ 우선
5. **Klarna** ($45.60B, 스웨덴, Fintech) - ⭐⭐ 우선
6. Fanatics ($18.00B, 미국, E-commerce)
7. SpaceX ($74.00B, 미국, Aerospace)
8. Bytedance ($140.00B, 중국, AI/Social)
9. BYJU's ($16.50B, 인도, Edtech)
10. DJI ($15.00B, 중국, Hardware)

---

## 📊 수집할 정보

각 기업별로 아래 정보를 JSON 형식으로 제공해주세요:

### 1. Problem / Solution (필수)
```json
{
  "problem": "해결하려는 구체적인 문제",
  "solution": "제공하는 솔루션",
  "unique_value": "차별화 요소"
}
```

### 2. Revenue Model (필수)
```json
{
  "revenue_model": [
    {"type": "수익 유형", "description": "설명", "percentage": 70}
  ]
}
```

### 3. Financial (최우선!)
```json
{
  "revenue": {
    "year_1": {"year": 2023, "amount_usd_million": 16000, "source": "출처 URL"},
    "year_2": {"year": 2022, "amount_usd_million": 14000, "source": "출처 URL"},
    "year_3": {"year": 2021, "amount_usd_million": 12000, "source": "출처 URL"}
  },
  "operating_profit": {
    "year_1": {"year": 2023, "amount_usd_million": -500, "source": "출처 URL"},
    ...
  }
}
```

### 4. Operational Metrics (우선)
```json
{
  "users": 숫자 또는 null,
  "mau": 숫자 또는 null,
  "dau": 숫자 또는 null,
  "gmv_usd_million": 숫자 또는 null,
  "arr_usd_million": 숫자 또는 null
}
```

### 5. Competitive Advantage (필수)
```json
{
  "competitive_advantage": [
    "요소 1",
    "요소 2",
    "요소 3"
  ]
}
```

### 6. Critical Success Factors (필수)
```json
{
  "critical_success_factors": [
    "요인 1",
    "요인 2",
    "요인 3"
  ]
}
```

---

## ⚠️ 중요 원칙

1. **반드시 소스 URL 포함** - 모든 숫자에 출처 명시
2. **추정 금지** - 확인 안 되면 `null`
3. **최신 정보** - 2년 이내 우선
4. **신뢰도 표시** - ⭐⭐⭐⭐⭐ (공식) ~ ⭐ (추정)

---

## 🔍 추천 소스

**상장사 (Rivian, Instacart):**
- SEC EDGAR: https://www.sec.gov/edgar
- Form 10-K (연례 보고서)

**비상장사:**
- Crunchbase: https://www.crunchbase.com
- TechCrunch: https://techcrunch.com
- Bloomberg: https://www.bloomberg.com
- 공식 블로그

**검색 쿼리 예시:**
```
"Stripe" revenue "$" billion 2023 2024
"Stripe" payment volume GMV
site:techcrunch.com "Stripe" revenue
```

---

## 📤 제출 형식

각 기업별 JSON 파일 또는 통합 JSON 1개

**예시 (Stripe):**
```json
{
  "company": "Stripe",
  "problem_solution": {...},
  "business_model": {...},
  "performance_metrics": {
    "financial": {...},
    "operational": {...}
  },
  "competitive_advantage": [...],
  "critical_success_factors": [...]
}
```

---

## 🎯 기대

- **완성도:** 70%+ (10개 평균)
- **Quality Grade:** B+ (10개 평균)
- **소요 시간:** 10시간 (예상)
- **제출:** 가능한 빠르게

---

**상세 가이드:** 필요시 전체 버전 (`AI_RESEARCH_REQUEST.md`) 참고  
**검색 쿼리:** `research/XX_Company_guide.json` 파일에 150+개 준비됨

감사합니다! 🙏



