# 📊 유니콘 데이터 구조화 비교

## 🎯 개선 사항

### 1️⃣ **Funding History** (펀딩 히스토리)
**변경 전:** 텍스트 문자열
```
"2014, 100M, Sequoia China\n2017 April, 1B, Sequoia China 외\n2017 Aug, 2B, General Atlantic"
```

**변경 후:** 구조화된 배열
```json
"funding_history": [
  {
    "date": "2014",
    "amount": "100M",
    "currency": "USD",
    "investors": ["Sequoia China"]
  },
  {
    "date": "2017.April",
    "amount": "1B",
    "currency": "USD",
    "investors": ["Sequoia China"]
  }
]
```

### 2️⃣ **Business** (비즈니스 설명)
**변경 전:** 텍스트 문자열
```
"- 숏폼 비디오 콘텐츠 SNS 틱톡 운영사"
```

**변경 후:** 구조화된 객체
```json
"business": {
  "summary": "숏폼 비디오 콘텐츠 SNS 틱톡 운영사",
  "details": []
}
```

### 3️⃣ **Select Investors** (주요 투자자)
**변경 전:** 쉼표로 구분된 문자열
```
"Sequoia Capital China, SIG Asia Investments, Sina Weibo, Softbank Group"
```

**변경 후:** 배열
```json
"select_investors": [
  "Sequoia Capital China",
  "SIG Asia Investments",
  "Sina Weibo",
  "Softbank Group"
]
```

---

## 📋 전체 구조 비교


### 예시 1: Bytedance

#### ❌ 변경 전 (원본)
```json
{
  "company": "Bytedance",
  "valuation_billion": "$140.00",
  "date_added": "2017.4.7",
  "country": "China",
  "category": "Artificial intelligence",
  "select_investors": "Sequoia Capital China, SIG Asia Investments, Sina Weibo, Softbank Group",
  "history": "2014, 100M, Sequoia China\n2017 April, 1B, Sequoia China 외\n2017 Aug, 2B, General Atlantic\n2018 Oct, 3B, Softbank Vision fund, KKR 외\n2019 Apr, 1.3B, Goldman Sachs, Morgan Stanley\n2020 Dec, 2B, KKR, Sequoia Capital",
  "business": "- 숏폼 비디오 콘텐츠 SNS 틱톡 운영사"
}
```

#### ✅ 변경 후 (구조화)
```json
{
  "company": "Bytedance",
  "valuation": {
    "amount_billion": "$140.00",
    "date_added": "2017.4.7"
  },
  "location": {
    "country": "China"
  },
  "category": "Artificial intelligence",
  "select_investors": [
    "Sequoia Capital China",
    "SIG Asia Investments",
    "Sina Weibo",
    "Softbank Group"
  ],
  "funding_history": [
    {
      "date": "2014",
      "amount": "100M",
      "currency": "USD",
      "investors": [
        "Sequoia China"
      ]
    },
    {
      "date": "2017.April",
      "amount": "1B",
      "currency": "USD",
      "investors": [
        "Sequoia China"
      ]
    },
    {
      "date": "2017.Aug",
      "amount": "2B",
      "currency": "USD",
      "investors": [
        "General Atlantic"
      ]
    },
    {
      "date": "2018.Oct",
      "amount": "3B",
      "currency": "USD",
      "investors": [
        "Softbank Vision fund",
        "KKR"
      ]
    },
    {
      "date": "2019.Apr",
      "amount": "1.3B",
      "currency": "USD",
      "investors": [
        "Goldman Sachs",
        "Morgan Stanley"
      ]
    },
    {
      "date": "2020.Dec",
      "amount": "2B",
      "currency": "BRL",
      "investors": [
        "KKR",
        "Sequoia Capital"
      ]
    }
  ],
  "business": {
    "summary": "숏폼 비디오 콘텐츠 SNS 틱톡 운영사",
    "details": []
  }
}
```

---

### 예시 2: Stripe

#### ❌ 변경 전 (원본)
```json
{
  "company": "Stripe",
  "valuation_billion": "$95.00",
  "date_added": "2014.1.23",
  "country": "United States",
  "category": "Fintech",
  "select_investors": "Khosla Ventures, LowercaseCapital, capitalG",
  "history": "2016 150M, CapitalG\n2018 245M, Tiger Global\n2019 100M, Tiger Global \n2019 250M, a16z\n2021 600M, Allianz X, AXA Group, Baillie Gifford, Fidelity Management 외",
  "business": "- 온라인 결제 솔루션 API 제공사 \n- 이후 확장하여, 법인카드 서비스, 스타트업 자금대출 서비스 등 다양한 금융 서비스를 제공\n- 지금까지 제공되고 있는 stripe 자체 프로덕트는 총 16개 (https://stripe.com/)"
}
```

#### ✅ 변경 후 (구조화)
```json
{
  "company": "Stripe",
  "valuation": {
    "amount_billion": "$95.00",
    "date_added": "2014.1.23"
  },
  "location": {
    "country": "United States"
  },
  "category": "Fintech",
  "select_investors": [
    "Khosla Ventures",
    "LowercaseCapital",
    "capitalG"
  ],
  "funding_history": [
    {
      "date": "2016",
      "amount": "150M",
      "currency": "USD",
      "investors": [
        "CapitalG"
      ]
    },
    {
      "date": "2018",
      "amount": "245M",
      "currency": "USD",
      "investors": [
        "Tiger Global"
      ]
    },
    {
      "date": "2019",
      "amount": "100M",
      "currency": "USD",
      "investors": [
        "Tiger Global"
      ]
    },
    {
      "date": "2019",
      "amount": "250M",
      "currency": "USD",
      "investors": [
        "a16z"
      ]
    },
    {
      "date": "2021",
      "amount": "600M",
      "currency": "USD",
      "investors": [
        "Allianz X",
        "AXA Group",
        "Baillie Gifford",
        "Fidelity Management"
      ]
    }
  ],
  "business": {
    "summary": "온라인 결제 솔루션 API 제공사",
    "details": [
      "이후 확장하여, 법인카드 서비스, 스타트업 자금대출 서비스 등 다양한 금융 서비스를 제공",
      "지금까지 제공되고 있는 stripe 자체 프로덕트는 총 16개 (https://stripe.com/)"
    ]
  }
}
```

---

### 예시 3: SpaceX

#### ❌ 변경 전 (원본)
```json
{
  "company": "SpaceX",
  "valuation_billion": "$74.00",
  "date_added": "2012.12.1",
  "country": "United States",
  "category": "Other",
  "select_investors": "Founders Fund, Draper Fisher Jurvetson, Rothenberg Ventures",
  "history": "2019 273M, Founders Fund 외\n2019 500M, Baillie Gifford\n2019 314M, Vanedge Capital\n2020 221M, Unknown\n2020 1.9B, Unknown\n2021 850M, Unknown",
  "business": "- 항공우주 장비 제조/생산 및 우주 수송 회사"
}
```

#### ✅ 변경 후 (구조화)
```json
{
  "company": "SpaceX",
  "valuation": {
    "amount_billion": "$74.00",
    "date_added": "2012.12.1"
  },
  "location": {
    "country": "United States"
  },
  "category": "Other",
  "select_investors": [
    "Founders Fund",
    "Draper Fisher Jurvetson",
    "Rothenberg Ventures"
  ],
  "funding_history": [
    {
      "date": "2019",
      "amount": "273M",
      "currency": "USD",
      "investors": [
        "Founders Fund"
      ]
    },
    {
      "date": "2019",
      "amount": "500M",
      "currency": "USD",
      "investors": [
        "Baillie Gifford"
      ]
    },
    {
      "date": "2019",
      "amount": "314M",
      "currency": "USD",
      "investors": [
        "Vanedge Capital"
      ]
    },
    {
      "date": "2020",
      "amount": "221M",
      "currency": "USD",
      "investors": [
        "Unknown"
      ]
    },
    {
      "date": "2020",
      "amount": "1.9B",
      "currency": "USD",
      "investors": [
        "Unknown"
      ]
    },
    {
      "date": "2021",
      "amount": "850M",
      "currency": "USD",
      "investors": [
        "Unknown"
      ]
    }
  ],
  "business": {
    "summary": "항공우주 장비 제조/생산 및 우주 수송 회사",
    "details": []
  }
}
```

---


## 🚀 활용 예시

### Python에서 활용
```python
import json

# 데이터 로드
with open('unicorn_companies_structured.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 1. 특정 투자자가 투자한 기업 찾기
sequoia_companies = [
    c for c in data['companies'] 
    if 'Sequoia Capital' in str(c['select_investors'])
]

# 2. 펀딩 총액 계산
for company in data['companies']:
    total_funding = 0
    for round in company['funding_history']:
        if 'M' in round['amount']:
            total_funding += float(round['amount'].replace('M', ''))
        elif 'B' in round['amount']:
            total_funding += float(round['amount'].replace('B', '')) * 1000
    print(f"{company['company']}: ${total_funding}M")

# 3. 국가별 카테고리 분석
from collections import defaultdict
country_categories = defaultdict(set)
for company in data['companies']:
    country_categories[company['location']['country']].add(company['category'])
```

### JavaScript/TypeScript에서 활용
```typescript
import data from './unicorn_companies_structured.json';

// 1. 펀딩 라운드별 평균 금액
const avgFundingByYear = data.companies.reduce((acc, company) => {
  company.funding_history.forEach(round => {
    const year = round.date.split('.')[0];
    // 분석 로직...
  });
  return acc;
}, {});

// 2. 투자자 네트워크 분석
const investorNetwork = new Map();
data.companies.forEach(company => {
  company.select_investors.forEach(investor => {
    if (!investorNetwork.has(investor)) {
      investorNetwork.set(investor, []);
    }
    investorNetwork.get(investor).push(company.company);
  });
});
```

---

## 📈 데이터 통계


- **총 기업 수:** 800개
- **총 펀딩 라운드:** 2709회
- **상세 비즈니스 설명 보유 기업:** 733개
- **고유 투자자 수:** 1731개

---

## 🎯 구조화의 장점

1. **프로그래밍 용이성**: 텍스트 파싱 불필요, 바로 데이터 접근
2. **데이터 분석**: 펀딩 패턴, 투자자 네트워크 분석 가능
3. **타입 안정성**: TypeScript 등에서 타입 정의 가능
4. **쿼리 성능**: 필터링, 정렬, 집계 작업 효율적
5. **확장성**: 새로운 필드 추가 용이

---

## 📁 파일 정보

- **원본 파일:** `unicorn_companies.json` (8,005줄)
- **구조화 파일:** `unicorn_companies_structured.json`
- **이 문서:** `unicorn_companies_comparison.md`

생성 일자: 2025-11-04
