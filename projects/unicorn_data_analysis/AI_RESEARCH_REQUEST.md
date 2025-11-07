# 🤖 유니콘 기업 리서치 요청서 (For AI Assistant)

**요청 일자:** 2025-11-04  
**프로젝트:** UMIS 유니콘 비즈니스 사례 데이터베이스 구축  
**요청자:** UMIS Team  

---

## 📋 리서치 개요

### 목적
800개 유니콘 기업을 UMIS RAG 시스템의 비즈니스 사례 데이터로 활용하기 위해, 각 기업의 재무/운영 지표 및 비즈니스 분석 정보를 수집합니다.

### 범위
**파일럿 10개 유니콘 기업** (우선순위 순)

### 예상 시간
기업당 30-90분 (총 10시간)

---

## 🎯 리서치 대상 기업 (10개)

| # | 기업명 | 밸류에이션 | 국가 | 카테고리 | 우선순위 |
|---|--------|-----------|------|----------|----------|
| 1 | **Rivian** | $27.60B | 🇺🇸 | Auto & Transportation | ⭐ 최우선 (상장사) |
| 2 | **Instacart** | $39.00B | 🇺🇸 | Logistics & Delivery | ⭐ 최우선 (상장사) |
| 3 | **Stripe** | $95.00B | 🇺🇸 | Fintech | ⭐⭐ 우선 |
| 4 | **Databricks** | $28.00B | 🇺🇸 | Data Analytics | ⭐⭐ 우선 |
| 5 | **Klarna** | $45.60B | 🇸🇪 | Fintech | ⭐⭐ 우선 |
| 6 | **Fanatics** | $18.00B | 🇺🇸 | E-commerce | ⭐⭐⭐ 보통 |
| 7 | **SpaceX** | $74.00B | 🇺🇸 | Aerospace | ⭐⭐⭐⭐ 어려움 |
| 8 | **Bytedance** | $140.00B | 🇨🇳 | AI/Social | ⭐⭐⭐⭐ 어려움 |
| 9 | **BYJU's** | $16.50B | 🇮🇳 | Edtech | ⭐⭐⭐⭐ 어려움 |
| 10 | **DJI** | $15.00B | 🇨🇳 | Hardware/Drones | ⭐⭐⭐⭐⭐ 매우 어려움 |

---

## 📊 수집할 정보 (구조화된 형식)

### 1. Problem / Solution ⭐ (필수)

```json
{
  "problem": "해결하려는 구체적인 문제 (고객의 pain point)",
  "solution": "제공하는 솔루션 (제품/서비스)",
  "unique_value": "경쟁사와 차별화되는 고유 가치"
}
```

**예시 (Stripe):**
```json
{
  "problem": "온라인 결제 시스템 구현이 복잡하고 시간이 많이 걸림 (개발자 입장)",
  "solution": "7줄의 코드로 결제 시스템 통합 가능한 API 제공",
  "unique_value": "Developer-first approach, 글로벌 결제 인프라, 16+ 제품 생태계"
}
```

---

### 2. Business Model / Revenue Model ⭐ (필수)

```json
{
  "revenue_model": [
    {
      "type": "transaction_fee",
      "description": "거래당 수수료 (예: 2.9% + 30¢)",
      "percentage_of_total": 70
    },
    {
      "type": "subscription",
      "description": "월간 구독료 (Stripe Billing)",
      "percentage_of_total": 20
    },
    {
      "type": "other",
      "description": "기타 서비스 (Atlas, Capital 등)",
      "percentage_of_total": 10
    }
  ]
}
```

**찾을 정보:**
- 주요 수익원 (상위 3개)
- 각 수익원의 비중 (%)
- 가격 구조 (수수료율, 구독료 등)

---

### 3. Performance Metrics - Financial ⭐⭐⭐⭐⭐ (최우선)

```json
{
  "financial": {
    "revenue": {
      "year_1": {
        "year": 2023,
        "amount_usd_million": 16000,
        "source": "Bloomberg article, 2024-03-15, https://..."
      },
      "year_2": {
        "year": 2022,
        "amount_usd_million": 14000,
        "source": "TechCrunch, 2023-02-10, https://..."
      },
      "year_3": {
        "year": 2021,
        "amount_usd_million": 12000,
        "source": "The Information, 2022-01-20, https://..."
      }
    },
    "operating_profit": {
      "year_1": {"year": 2023, "amount_usd_million": -500, "source": "..."},
      "year_2": {"year": 2022, "amount_usd_million": -800, "source": "..."},
      "year_3": {"year": 2021, "amount_usd_million": -1000, "source": "..."}
    },
    "gross_margin": 65.5,
    "ebitda": null
  }
}
```

**중요:**
- **반드시 소스 URL 포함**
- **발표 날짜 명시**
- **못 찾으면 null** (추정 금지!)

**상장사 (Rivian, Instacart):**
- SEC EDGAR에서 10-K 다운로드
- Part II, Item 8: Financial Statements
- 최근 3년 Revenue, Operating Income 추출

**비상장사:**
- TechCrunch, Bloomberg, WSJ 기사 검색
- 공식 발표 (블로그, 보도자료)
- The Information 심층 기사 (유료)

---

### 4. Performance Metrics - Operational ⭐⭐⭐⭐ (우선)

```json
{
  "operational": {
    "users": 500000000,
    "mau": 300000000,
    "dau": 150000000,
    "transactions": null,
    "gmv_usd_million": 800000,
    "arr_usd_million": 1200,
    "subscribers": 50000000
  }
}
```

**찾을 정보 (확인 가능한 것만):**
- Total Users (총 사용자 수)
- MAU (Monthly Active Users)
- DAU (Daily Active Users)
- GMV (Gross Merchandise Value) - 커머스/마켓플레이스
- ARR (Annual Recurring Revenue) - SaaS
- Subscribers - 구독 모델

**소스:**
- 공식 발표 (블로그, IR)
- CEO 인터뷰
- 컨퍼런스 발표 (earnings call 등)

---

### 5. Performance Metrics - Unit Economics ⭐⭐ (선택)

```json
{
  "unit_economics": {
    "arpu_usd": 5.0,
    "cac_usd": null,
    "ltv_usd": null,
    "ltv_cac_ratio": null,
    "churn_rate_percent": 2.5,
    "payback_period_months": null
  }
}
```

**참고:**
- **대부분 비공개 정보**
- 공개된 경우에만 기재
- 못 찾아도 OK (null 유지)

**가능한 소스:**
- 상장사 10-K (일부)
- CEO/CFO 인터뷰
- 업계 리포트

---

### 6. Competitive Advantage ⭐⭐⭐⭐ (우선)

```json
{
  "competitive_advantage": [
    "강력한 AI 추천 알고리즘",
    "글로벌 확장 성공 (틱톡)",
    "콘텐츠 크리에이터 생태계",
    "네트워크 효과"
  ]
}
```

**찾을 정보:**
- 경쟁사 대비 차별화 요소 (3-5개)
- 모방하기 어려운 이유
- 진입 장벽 (moat)

---

### 7. Critical Success Factors ⭐⭐⭐⭐ (우선)

```json
{
  "critical_success_factors": [
    "Developer experience 최우선 (API 설계)",
    "글로벌 결제 인프라 구축",
    "제품 생태계 확장 (16+ products)",
    "네트워크 효과 (양측 시장)"
  ]
}
```

**찾을 정보:**
- 성공의 핵심 요인 (3-5개)
- Why 설명 필요
- 케이스 스터디, 분석 기사 참고

---

## 🔍 추천 리서치 소스

### Tier 1: 공식/1차 소스 (⭐⭐⭐⭐⭐)

**상장사:**
```
SEC EDGAR: https://www.sec.gov/edgar/searchedgar/companysearch
→ Form 10-K (연례 보고서)
→ Form S-1 (IPO 신청서)
```

**비상장사:**
```
공식 블로그:
- Stripe Blog: https://stripe.com/blog
- Databricks Blog: https://databricks.com/blog
- 각 회사 Press/News 섹션
```

---

### Tier 2: 전문 플랫폼 (⭐⭐⭐⭐)

```
Crunchbase: https://www.crunchbase.com
→ 기본 정보, 펀딩 히스토리

CB Insights: https://www.cbinsights.com
→ 유니콘 리스트, 분석

PitchBook: https://pitchbook.com (유료)
→ 재무 추정치
```

---

### Tier 3: Tech 미디어 (⭐⭐⭐⭐)

```
TechCrunch: https://techcrunch.com
→ 펀딩 뉴스, 제품 런칭

Bloomberg: https://www.bloomberg.com
→ 재무 분석

WSJ: https://www.wsj.com
→ 비즈니스 분석

The Information: https://www.theinformation.com (유료 $399/년)
→ 독점 재무 정보, 심층 분석
```

---

### 지역 특화 소스

**중국 (Bytedance, DJI):**
```
TechNode: https://technode.com
36Kr: https://36kr.com
Reuters China
```

**인도 (BYJU's):**
```
YourStory: https://yourstory.com
Economic Times India
```

**유럽 (Klarna):**
```
Sifted: https://sifted.eu
Financial Times
```

---

## 📝 출력 형식 (JSON)

### 각 기업별로 아래 JSON 형식으로 제공

```json
{
  "company": "Stripe",
  "research_date": "2025-11-04",
  "researcher": "AI Assistant Name",
  
  "problem_solution": {
    "problem": "온라인 결제 시스템 구현이 복잡함",
    "solution": "7줄 코드로 결제 통합 가능한 API",
    "unique_value": "Developer-first, 글로벌 인프라"
  },
  
  "business_model": {
    "revenue_model": [
      {"type": "transaction_fee", "description": "2.9% + 30¢", "percentage": 70},
      {"type": "subscription", "description": "Billing 서비스", "percentage": 20},
      {"type": "other", "description": "Atlas, Capital 등", "percentage": 10}
    ]
  },
  
  "performance_metrics": {
    "financial": {
      "revenue": {
        "year_1": {"year": 2023, "amount_usd_million": 16000, "source": "Bloomberg, https://..."},
        "year_2": {"year": 2022, "amount_usd_million": 14000, "source": "TechCrunch, https://..."},
        "year_3": {"year": 2021, "amount_usd_million": 12000, "source": "WSJ, https://..."}
      },
      "operating_profit": {
        "year_1": {"year": 2023, "amount_usd_million": -500, "source": "추정 또는 null"},
        "year_2": {"year": 2022, "amount_usd_million": null, "source": null},
        "year_3": {"year": 2021, "amount_usd_million": null, "source": null}
      },
      "gross_margin": 65.5,
      "ebitda": null
    },
    
    "operational": {
      "users": null,
      "mau": null,
      "dau": null,
      "transactions": null,
      "gmv_usd_million": 800000,
      "arr_usd_million": null,
      "subscribers": null
    },
    
    "unit_economics": {
      "arpu_usd": null,
      "cac_usd": null,
      "ltv_usd": null,
      "ltv_cac_ratio": null,
      "churn_rate_percent": null,
      "payback_period_months": null
    }
  },
  
  "competitive_advantage": [
    "Developer experience (API 우선 설계)",
    "글로벌 결제 인프라 (46개국)",
    "제품 생태계 (16+ products)",
    "네트워크 효과"
  ],
  
  "critical_success_factors": [
    "개발자 커뮤니티 구축",
    "글로벌 확장 전략",
    "제품 다각화",
    "파트너십 네트워크"
  ],
  
  "data_quality": {
    "completeness": "80%",
    "reliability": "⭐⭐⭐⭐",
    "notes": "Revenue는 언론 보도 기반, Operating Profit은 비공개"
  }
}
```

---

## ⚠️ 중요 지침

### ✅ 반드시 지켜야 할 원칙

1. **소스 URL 필수**
   - 모든 숫자에 출처 명시
   - 발표 날짜 포함
   - 예: "Bloomberg, 2024-03-15, https://..."

2. **추정 금지**
   - 확인된 정보만 기재
   - 못 찾으면 `null`로 유지
   - 추정시 반드시 "추정" 명시 + 근거

3. **최신 정보 우선**
   - 2년 이내 정보 권장
   - 발표 날짜 명시

4. **신뢰도 평가**
   - ⭐⭐⭐⭐⭐: 공식 발표 (SEC, IR)
   - ⭐⭐⭐⭐: 주요 미디어 (Bloomberg, WSJ)
   - ⭐⭐⭐: Tech 미디어 (TechCrunch)
   - ⭐⭐: 업계 리포트
   - ⭐: 추정

---

## 🎯 우선순위별 리서치 전략

### 최우선 (⭐): 상장사 (Rivian, Instacart)

**시간:** 30분/기업  
**난이도:** 매우 쉬움

**단계:**
1. SEC EDGAR 방문: https://www.sec.gov/edgar
2. 회사명 검색 → 최신 10-K 클릭
3. Financial Statements 섹션에서 Revenue, Operating Income 추출
4. MD&A 섹션에서 Key Metrics 확인 (users, subscribers 등)
5. JSON 형식으로 정리

**예시 URL:**
- Rivian: https://www.sec.gov/cgi-bin/browse-edgar?company=Rivian&action=getcompany
- Instacart: https://www.sec.gov/cgi-bin/browse-edgar?company=Instacart&action=getcompany

---

### 우선 (⭐⭐): 상장 준비사 (Stripe, Databricks, Klarna)

**시간:** 45-60분/기업  
**난이도:** 보통

**단계:**
1. Crunchbase에서 기본 정보 확인
2. Google 검색: "{Company} revenue 2023 2024 billion"
3. TechCrunch 펀딩 기사 검색
4. Bloomberg/WSJ 분석 기사
5. 공식 블로그에서 발표 지표 확인

**검색 쿼리 예시:**
```
"Stripe" revenue "$" billion 2023 2024
"Stripe" payment volume processed annually
"Stripe" customers merchants businesses million
"Databricks" ARR revenue $1 billion
"Klarna" users MAU 2024
```

---

### 보통 (⭐⭐⭐): 비상장 (Fanatics, SpaceX)

**시간:** 60-90분/기업  
**난이도:** 어려움

**단계:**
1. Google News 검색
2. 언론 보도 위주
3. 공개된 정보 위주 수집
4. null 많아도 OK

---

### 어려움 (⭐⭐⭐⭐): 해외 (Bytedance, BYJU's, DJI)

**시간:** 80-90분/기업  
**난이도:** 매우 어려움

**단계:**
1. 지역 특화 미디어 (TechNode, YourStory)
2. 글로벌 미디어 (Reuters, Bloomberg)
3. 후룬 리포트
4. 제한적 정보 수용

---

## 📚 검색 쿼리 가이드

### Revenue (매출)

```
"{Company}" revenue "$14 billion" OR "$16 billion" 2023 2024
"{Company}" annual revenue growth rate financial performance
"{Company}" revenue breakdown by product segment
site:techcrunch.com "{Company}" revenue
site:bloomberg.com "{Company}" financial performance
```

---

### Operational Metrics (운영 지표)

```
"{Company}" MAU million users 2024 statistics
"{Company}" announces XX million customers subscribers
"{Company}" GMV gross merchandise value billion
"{Company}" ARR annual recurring revenue $
"{Company}" daily active users DAU
```

---

### Business Model

```
"{Company}" business model how does make money
"{Company}" revenue model pricing strategy
"{Company}" fee structure commission rate percentage
"{Company}" vs {Competitor} business model comparison
```

---

### Problem/Solution

```
"{Company}" problem solving value proposition why
"{Company}" founder story startup journey why started
"{Company}" customer pain point solution
"{Company}" before after disruption innovation
```

---

## 🎯 품질 기준

### 각 기업별 목표

**필수 정보 (100%):**
- ✅ Problem / Solution
- ✅ Revenue Model
- ✅ Competitive Advantage (3-5개)
- ✅ Critical Success Factors (3-5개)

**우선 정보 (60%+):**
- ✅ Revenue (최근 3년)
- ⚠️ Operating Profit (가능하면)
- ✅ Operational Metrics (1-2개 이상)

**선택 정보 (10-20%):**
- ⚠️ Unit Economics (공개시만)
- ⚠️ Gross Margin, EBITDA

**Overall Quality Grade:**
- A: 90%+ 완성도, 모든 소스 신뢰도 ⭐⭐⭐⭐ 이상
- B: 70%+ 완성도, 대부분 신뢰도 ⭐⭐⭐ 이상
- C: 50%+ 완성도
- D: 50% 미만

---

## 📤 제출 형식

### Option 1: 개별 JSON 파일 (권장)

```
01_Stripe_research_result.json
02_SpaceX_research_result.json
...
10_DJI_research_result.json
```

각 파일은 위의 JSON 구조 따름

---

### Option 2: 통합 JSON

```json
{
  "research_batch": "pilot_10_unicorns",
  "research_date": "2025-11-04",
  "total_companies": 10,
  "companies": [
    {
      "company": "Stripe",
      "problem_solution": {...},
      "business_model": {...},
      "performance_metrics": {...},
      ...
    },
    {
      "company": "SpaceX",
      ...
    }
  ]
}
```

---

### Option 3: Markdown 리포트

각 기업별 Markdown 파일 (구조화된 형식)

---

## 📊 예상 결과물

### 데이터 완성도 예상

| 기업 | Revenue | Operating Profit | Operational | Unit Econ | Overall |
|------|---------|-----------------|-------------|-----------|---------|
| Rivian | 100% | 100% | 80% | 50% | A |
| Instacart | 100% | 100% | 80% | 50% | A |
| Stripe | 80% | 30% | 60% | 10% | B |
| Databricks | 70% | 20% | 60% | 10% | B |
| Klarna | 70% | 30% | 60% | 20% | B |
| Fanatics | 50% | 10% | 40% | 0% | C |
| SpaceX | 30% | 0% | 30% | 0% | C |
| Bytedance | 60% | 20% | 50% | 5% | B |
| BYJU's | 50% | 10% | 40% | 5% | C |
| DJI | 40% | 0% | 30% | 0% | C |

---

## ⏱️ 예상 시간

| 그룹 | 기업 수 | 평균 시간 | 총 시간 |
|------|---------|----------|---------|
| 최우선 (상장사) | 2 | 30분 | 1시간 |
| 우선 (상장 준비) | 3 | 50분 | 2.5시간 |
| 보통 (비상장) | 2 | 75분 | 2.5시간 |
| 어려움 (해외) | 3 | 80분 | 4시간 |
| **합계** | **10** | **60분** | **10시간** |

---

## 💡 추가 요청사항

### 1. 소스 신뢰도 평가

각 정보마다 신뢰도 표시:
```json
{
  "year": 2023,
  "amount_usd_million": 16000,
  "source": "Bloomberg, 2024-03-15, https://...",
  "reliability": "⭐⭐⭐⭐"
}
```

---

### 2. 정보 부재 명시

못 찾은 정보는:
```json
{
  "operating_profit": {
    "year_1": {
      "year": 2023,
      "amount_usd_million": null,
      "source": null,
      "note": "비공개, 여러 소스 검색했으나 찾지 못함"
    }
  }
}
```

---

### 3. 추가 인사이트

가능하면 추가:
```json
{
  "additional_insights": [
    "2024년 상장 준비 중 (S-1 filing 예상)",
    "최근 레이오프 10% 진행 (2024-01)",
    "신제품 Stripe Financial Connections 출시"
  ]
}
```

---

## 📧 결과 제출

**이메일 또는 파일 공유:**
- JSON 파일 10개
- 또는 통합 JSON 1개
- 소스 URL 리스트 별도 제공 (선택)

**기대:**
- 완성도 70%+ (10개 평균)
- Quality Grade B+ (10개 평균)
- 모든 정보에 소스 명시

---

## 🙏 감사 인사

이 리서치는 **800개 유니콘 기업을 UMIS RAG 시스템에 통합**하는 대형 프로젝트의 첫 단계입니다.

AI의 웹 검색 및 정보 수집 능력을 활용하여:
- ✅ 리서치 시간 단축
- ✅ 데이터 품질 향상
- ✅ 체계적인 정보 수집

이 파일럿의 성공으로 **Tier 1 (Top 100)** 확장 및 **전체 800개** 완성을 목표로 합니다.

---

## 📎 첨부 참고 자료

1. **DATA_SOURCES_GUIDE.md** - 51개 데이터 소스 상세
2. **research/XX_Company_guide.json** - 검색 쿼리 150+개
3. **scripts/03_research_template.md** - 상세 템플릿

---

**요청자:** UMIS v7.0.0  
**연락처:** kangmin@umis (example)  
**프로젝트:** projects/unicorn_data_analysis/  
**마감:** 가능한 빠르게 (2주 권장)



