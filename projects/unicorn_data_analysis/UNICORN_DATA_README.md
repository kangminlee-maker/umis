# 🦄 유니콘 기업 데이터베이스

전 세계 800개 유니콘 기업의 구조화된 데이터베이스

**생성일:** 2025-11-04  
**데이터 버전:** 2.0  
**총 기업 수:** 800개  
**총 펀딩 라운드:** 2,709회  
**고유 투자자 수:** 1,731명

---

## 📁 파일 구조

```
dev_docs/
├── Unicorn Club_FV - 시트1.csv          # 원본 CSV 파일
├── unicorn_companies.json               # 기본 JSON 변환 (v1.0)
├── unicorn_companies_structured.json    # 구조화된 JSON (v2.0) ⭐
├── unicorn_companies_summary.md         # Markdown 요약본
├── unicorn_companies_comparison.md      # 변경 전후 비교
├── unicorn_types.ts                     # TypeScript 타입 정의
└── UNICORN_DATA_README.md              # 이 파일
```

---

## ⭐ 추천 파일

### **unicorn_companies_structured.json**
가장 최신의 구조화된 데이터. 프로그래밍 작업시 이 파일 사용 권장.

**주요 개선사항:**
- ✅ Funding History: 텍스트 → 구조화된 배열
- ✅ Business Info: 텍스트 → 요약 + 상세 항목
- ✅ Investors: 문자열 → 배열
- ✅ 메타데이터 추가

---

## 🚀 빠른 시작

### Python
```python
import json

# 데이터 로드
with open('unicorn_companies_structured.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 기본 정보
print(f"총 기업 수: {data['metadata']['total_companies']}")

# 첫 번째 기업 정보
company = data['companies'][0]
print(f"회사명: {company['company']}")
print(f"밸류에이션: {company['valuation']['amount_billion']}B")
print(f"국가: {company['location']['country']}")
print(f"펀딩 라운드: {len(company['funding_history'])}회")
```

### TypeScript/JavaScript
```typescript
import data from './unicorn_companies_structured.json';
import type { UnicornDatabase } from './unicorn_types';

// 타입 안정성
const db: UnicornDatabase = data;

// Top 10 밸류에이션
const top10 = db.companies
  .sort((a, b) => parseFloat(b.valuation.amount_billion) - 
                   parseFloat(a.valuation.amount_billion))
  .slice(0, 10);

console.table(top10.map(c => ({
  회사: c.company,
  밸류에이션: c.valuation.amount_billion,
  국가: c.location.country
})));
```

---

## 📊 데이터 구조

### UnicornCompany 객체
```typescript
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
    ...
  ],
  "funding_history": [
    {
      "date": "2014",
      "amount": "100M",
      "currency": "USD",
      "investors": ["Sequoia China"]
    },
    ...
  ],
  "business": {
    "summary": "숏폼 비디오 콘텐츠 SNS 틱톡 운영사",
    "details": []
  }
}
```

---

## 📈 주요 통계

### 국가별 분포 (Top 5)
1. 🇺🇸 **United States**: 402개 (50.3%)
2. 🇨🇳 **China**: 158개 (19.8%)
3. 🇮🇳 **India**: 40개 (5.0%)
4. 🇬🇧 **United Kingdom**: 29개 (3.6%)
5. 🇩🇪 **Germany**: 18개 (2.3%)

### 카테고리별 분포 (Top 5)
1. **Fintech**: 134개
2. **Internet software & services**: 127개
3. **E-commerce & direct-to-consumer**: 76개
4. **Health**: 59개
5. **Artificial intelligence**: 54개

### 밸류에이션 Top 5
1. **Bytedance** (중국): $140.00B
2. **Stripe** (미국): $95.00B
3. **SpaceX** (미국): $74.00B
4. **Klarna** (스웨덴): $45.60B
5. **Instacart** (미국): $39.00B

---

## 🔍 분석 예시

### 1. 투자자 분석
```python
# Sequoia Capital의 투자 포트폴리오
sequoia_portfolio = [
    c for c in data['companies']
    if any('Sequoia' in inv for inv in c['select_investors'])
]
print(f"Sequoia 투자 기업: {len(sequoia_portfolio)}개")
```

### 2. 펀딩 트렌드 분석
```python
from collections import defaultdict

funding_by_year = defaultdict(int)
for company in data['companies']:
    for round in company['funding_history']:
        year = round['date'].split('.')[0]
        if year.isdigit():
            funding_by_year[year] += 1

# 연도별 펀딩 라운드 수
for year in sorted(funding_by_year.keys()):
    print(f"{year}: {funding_by_year[year]}회")
```

### 3. 카테고리별 평균 밸류에이션
```python
from collections import defaultdict

category_valuations = defaultdict(list)
for company in data['companies']:
    val = float(company['valuation']['amount_billion'].replace('$', ''))
    category_valuations[company['category']].append(val)

# 평균 계산
for category, vals in category_valuations.items():
    avg = sum(vals) / len(vals)
    print(f"{category}: ${avg:.2f}B (n={len(vals)})")
```

### 4. 지역별 카테고리 특화
```python
from collections import Counter

# 미국 vs 중국 카테고리 비교
us_categories = Counter([
    c['category'] for c in data['companies']
    if c['location']['country'] == 'United States'
])

cn_categories = Counter([
    c['category'] for c in data['companies']
    if c['location']['country'] == 'China'
])

print("미국 Top 3:", us_categories.most_common(3))
print("중국 Top 3:", cn_categories.most_common(3))
```

---

## 🛠️ 유틸리티 함수

### 펀딩 금액 파싱
```python
def parse_funding_amount(amount: str) -> float:
    """펀딩 금액을 백만 달러로 변환"""
    value = float(amount.replace('M', '').replace('B', ''))
    if 'B' in amount:
        return value * 1000
    return value

# 사용 예시
total = sum(
    parse_funding_amount(r['amount']) 
    for c in data['companies'] 
    for r in c['funding_history']
)
print(f"총 펀딩 금액: ${total:,.0f}M")
```

### 투자자 네트워크
```python
from collections import defaultdict

investor_network = defaultdict(set)
for company in data['companies']:
    investors = set(company['select_investors'])
    for round in company['funding_history']:
        investors.update(round['investors'])
    
    # 동일 기업에 투자한 투자자들을 연결
    for inv1 in investors:
        for inv2 in investors:
            if inv1 != inv2:
                investor_network[inv1].add(inv2)

# 가장 많은 공동 투자자를 가진 투자자
top_networked = sorted(
    investor_network.items(),
    key=lambda x: len(x[1]),
    reverse=True
)[:10]
```

---

## 📚 추가 리소스

- **비교 문서**: `unicorn_companies_comparison.md` - 구조화 전후 비교
- **요약본**: `unicorn_companies_summary.md` - Markdown 형식 리스트
- **타입 정의**: `unicorn_types.ts` - TypeScript 타입 및 헬퍼 함수

---

## 🔄 데이터 업데이트 히스토리

| 버전 | 날짜 | 변경사항 |
|------|------|----------|
| 1.0 | 2025-11-04 | CSV → JSON 기본 변환 |
| 2.0 | 2025-11-04 | 구조화 (funding_history, business 객체화) |

---

## 💡 문의 및 기여

데이터 오류나 개선 사항이 있으면 이슈를 등록해주세요.

---

**Generated by UMIS v7.0.0**  
*Universal Market Intelligence System*

