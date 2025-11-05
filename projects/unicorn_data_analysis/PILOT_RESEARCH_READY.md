# 🚀 파일럿 리서치 준비 완료!

**작업 일시:** 2025-11-04  
**상태:** 리서치 시작 준비 완료  
**다음:** 수동 리서치 진행

---

## ✅ 완료된 준비 작업

### 1. 데이터 구조 개선 ✅

**v3.0 → v3.1 업그레이드**
- ❌ 비현실적 구조 제거 (unit_economics, key_metrics 독립 섹션)
- ✅ Performance Metrics 통합 구조
  - Financial (revenue, operating_profit 3개년)
  - Operational (mau, dau, gmv, arr 선택)
  - Unit Economics (공개시만)

---

### 2. 데이터 소스 발굴 ✅

**`DATA_SOURCES_GUIDE.md` 생성**

**Tier 1 소스 (⭐⭐⭐⭐⭐):**
- SEC EDGAR (상장사)
- 기업 공식 블로그/IR

**Tier 2 소스 (⭐⭐⭐⭐):**
- CB Insights, Crunchbase, PitchBook
- 유니콘 팩토리 (한국)

**Tier 3 소스 (⭐⭐⭐⭐):**
- TechCrunch, Bloomberg, WSJ
- The Information (유료)
- TechNode (중국), YourStory (인도)

**Tier 4-6 소스:**
- 산업 리포트 (Gartner, McKinsey)
- 소셜 미디어 (LinkedIn, Twitter)
- 간접 추정 (경쟁사 벤치마크)

---

### 3. 자동화 도구 개발 ✅

**`scripts/04_research_helper.py`**

**기능:**
- ✅ 검색 쿼리 자동 생성 (5개 카테고리 × 3-4개 쿼리)
- ✅ Google Search URL 자동 생성
- ✅ 직접 접근 URL (Crunchbase, SEC, 공식 사이트)
- ✅ 리서치 체크리스트 자동 생성
- ✅ 파일럿 10개 전부 자동 처리

---

### 4. 리서치 가이드 생성 ✅

**파일럿 10개 기업별로 생성됨:**

```
research/
├── 01_Stripe_guide.json              (4.6KB) - 검색 쿼리 & URL
├── 01_Stripe_checklist.md            (1.3KB) - 리서치 체크리스트
├── 02_SpaceX_guide.json
├── 02_SpaceX_checklist.md
├── ... (나머지 8개)
└── 10_DJI_Innovations_checklist.md
```

**각 가이드 파일 포함 내용:**
- 회사 기본 정보
- 경쟁사 리스트
- 카테고리별 검색 쿼리 (15-20개)
- 사이트별 검색 쿼리 (TechCrunch, Bloomberg 등)
- 직접 URL (Crunchbase, SEC, Google)

---

## 📋 리서치 워크플로우

### Step 1: 가이드 파일 열기

```bash
cd research/
open 01_Stripe_guide.json
open 01_Stripe_checklist.md
```

---

### Step 2: 검색 쿼리 사용

**JSON 파일에서 URL 복사 → 브라우저에서 열기**

예시:
```json
{
  "query": "\"Stripe\" revenue \"$\" billion million 2023 2024",
  "url": "https://www.google.com/search?q=..."
}
```

**또는 쿼리 직접 복사:**
```
"Stripe" revenue "$" billion million 2023 2024
```

---

### Step 3: 체크리스트 따라하기

`01_Stripe_checklist.md` 열기:

```markdown
## Phase 1: 기본 정보 수집 (10분)
- [ ] Crunchbase 프로필 확인
- [ ] 공식 웹사이트 방문
- [ ] 최신 뉴스 확인
- [ ] 상장 여부 확인

## Phase 2: 재무 정보 (20-30분)
...
```

---

### Step 4: 템플릿에 정보 입력

`scripts/03_research_template.md` 사용:
- Problem/Solution 작성
- Performance Metrics 입력
- 소스 URL 기록

---

### Step 5: JSON 업데이트

수집한 정보를 `unicorn_companies_rag_enhanced.json`에 반영

---

## 🎯 파일럿 10개 우선순위

### 그룹 A: 상장사 (쉬움) ⭐

1. **Rivian** (RIVN)
   - SEC 10-K 접근 가능
   - 예상 시간: 30분
   - 품질: ⭐⭐⭐⭐⭐

2. **Instacart** (CART)
   - SEC S-1/10-K 접근 가능
   - 예상 시간: 30분
   - 품질: ⭐⭐⭐⭐⭐

---

### 그룹 B: 상장 준비/풍부한 정보 (보통) ⭐⭐

3. **Stripe**
   - TechCrunch, Bloomberg 기사
   - 예상 시간: 45-60분
   - 품질: ⭐⭐⭐⭐

4. **Databricks**
   - 상장 준비, 언론 보도
   - 예상 시간: 45-60분
   - 품질: ⭐⭐⭐⭐

5. **Klarna**
   - 유럽 미디어, 상장 준비
   - 예상 시간: 45-60분
   - 품질: ⭐⭐⭐⭐

---

### 그룹 C: 비상장/제한적 정보 (어려움) ⭐⭐⭐

6. **Fanatics**
   - 스포츠 미디어, TechCrunch
   - 예상 시간: 60분
   - 품질: ⭐⭐⭐

7. **SpaceX**
   - 매우 제한적, 뉴스만
   - 예상 시간: 60-90분
   - 품질: ⭐⭐

---

### 그룹 D: 해외 (중국/인도) (매우 어려움) ⭐⭐⭐⭐

8. **Bytedance** (중국)
   - TechNode, Reuters
   - 예상 시간: 60-90분
   - 품질: ⭐⭐⭐

9. **BYJU's** (인도)
   - YourStory, Economic Times
   - 예상 시간: 60-90분
   - 품질: ⭐⭐⭐

10. **DJI** (중국)
    - 매우 제한적
    - 예상 시간: 90분+
    - 품질: ⭐⭐

---

## 📊 예상 소요 시간

| 그룹 | 기업 수 | 평균 시간 | 총 시간 |
|------|---------|----------|---------|
| A (상장사) | 2개 | 30분 | 1시간 |
| B (상장 준비) | 3개 | 50분 | 2.5시간 |
| C (비상장) | 2개 | 75분 | 2.5시간 |
| D (해외) | 3개 | 80분 | 4시간 |
| **합계** | **10개** | - | **10시간** |

**권장 일정:**
- Week 1: 그룹 A + B (5개) - 3.5시간
- Week 2: 그룹 C + D (5개) - 6.5시간

---

## 🛠️ 리서치 도구 활용법

### 방법 1: 가이드 JSON 활용

```python
import json
import webbrowser

# 가이드 로드
with open('research/01_Stripe_guide.json') as f:
    guide = json.load(f)

# Revenue 검색 쿼리 URL 자동 오픈
for query in guide['search_queries']['revenue_financial']:
    webbrowser.open(query['url'])
    input("다음 검색으로 이동하려면 Enter...")
```

---

### 방법 2: 체크리스트 사용

1. `research/01_Stripe_checklist.md` 열기
2. Phase별로 순서대로 진행
3. 체크박스 ✅ 표시하며 진행

---

### 방법 3: 수동 검색

1. 가이드 JSON에서 쿼리 복사
2. Google에 붙여넣기
3. 결과 확인 및 정보 수집

---

## 📝 리서치 결과 입력 방법

### Option A: Markdown 템플릿 사용

```
1. scripts/03_research_template.md 복사
2. research/01_Stripe_research.md로 저장
3. 각 섹션 채우기
4. 완료 후 JSON 변환 스크립트 실행
```

### Option B: 직접 JSON 수정

```python
# unicorn_companies_rag_enhanced.json 로드
with open('unicorn_companies_rag_enhanced.json') as f:
    data = json.load(f)

# Stripe 찾기
stripe = next(c for c in data['companies'] if c['company'] == 'Stripe')

# Performance Metrics 업데이트
stripe['business']['performance_metrics']['financial']['revenue'] = {
    "year_1": {"year": 2023, "amount_usd_million": 16000, "source": "Bloomberg 2024"},
    "year_2": {"year": 2022, "amount_usd_million": 14000, "source": "TechCrunch"},
    "year_3": {"year": 2021, "amount_usd_million": 12000, "source": "WSJ"}
}

# 저장
with open('unicorn_companies_rag_enhanced.json', 'w') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
```

---

## 🎯 리서치 목표 (파일럿 10개)

### 필수 정보 (모든 기업)

- ✅ Problem / Solution
- ✅ Business Model / Revenue Model
- ✅ Critical Success Factors (3-5개)
- ✅ Competitive Advantage (3-5개)

### 우선순위 정보 (가능한 기업)

- ⭐⭐⭐⭐⭐ Revenue (3년)
- ⭐⭐⭐⭐ Operating Profit
- ⭐⭐⭐⭐ MAU/DAU/Users
- ⭐⭐⭐ GMV/ARR

### 선택 정보 (공개시만)

- ⭐⭐ Unit Economics (ARPU, CAC, LTV)
- ⭐⭐ Gross Margin, EBITDA
- ⭐ Churn Rate

---

## 📁 프로젝트 현황

### 디렉토리 구조

```
projects/unicorn_data_analysis/
│
├── 📊 데이터
│   ├── unicorn_companies_rag_enhanced.json (v3.1) ⭐
│   ├── pilot_companies.json
│   └── unicorn_companies_structured_backup_*.json
│
├── 📝 문서
│   ├── README.md
│   ├── TRANSFORMATION_PLAN.md
│   ├── STRUCTURE_UPDATE_REPORT.md ⭐
│   ├── DATA_SOURCES_GUIDE.md ⭐
│   └── AUTOMATION_COMPLETE_REPORT.md
│
├── 🛠️ 스크립트
│   ├── 01_add_rag_metadata.py
│   ├── 02_select_pilot_companies.py
│   ├── 03_research_template.md
│   └── 04_research_helper.py ⭐
│
└── 🔍 리서치 (신규)
    ├── 01_Stripe_guide.json ⭐
    ├── 01_Stripe_checklist.md ⭐
    ├── 02_SpaceX_guide.json
    ├── ... (나머지 8개)
    └── 10_DJI_Innovations_checklist.md
```

**총 파일:** 20개 리서치 가이드 + 기존 파일들

---

## 🎨 생성된 리서치 가이드 구조

### 각 기업별로 2개 파일

#### 1. `{Company}_guide.json`
```json
{
  "company": "Stripe",
  "competitors": ["PayPal", "Square", "Adyen"],
  "search_queries": {
    "revenue_financial": [
      {
        "query": "\"Stripe\" revenue...",
        "url": "https://www.google.com/search?q=..."
      }
    ],
    "operational_metrics": [...],
    "business_model": [...],
    "problem_solution": [...],
    "competitive": [...]
  },
  "site_specific": {
    "techcrunch": {...},
    "bloomberg": {...},
    "sec": {...}
  },
  "direct_urls": {
    "crunchbase": "https://...",
    "sec": "https://...",
    "google_company": "https://..."
  }
}
```

**총 검색 쿼리:** 15-20개/기업  
**모두 URL로 변환되어 클릭만 하면 검색**

---

#### 2. `{Company}_checklist.md`
```markdown
# ✅ Stripe 리서치 체크리스트

## Phase 1: 기본 정보 수집 (10분)
- [ ] Crunchbase 프로필 확인
- [ ] 공식 웹사이트 방문
...

## Phase 2: 재무 정보 (20-30분)
- [ ] Revenue (3년) 추출
- [ ] Operating Profit 확인
...

## Phase 3-5: ...
```

**예상 시간:** 75-110분/기업  
**체계적인 프로세스**

---

## 🚀 리서치 시작 방법

### 권장 순서

**1주차 (쉬운 것부터):**

1. **Rivian** (상장사, 30분)
   ```bash
   open research/07_Rivian_guide.json
   open research/07_Rivian_checklist.md
   # SEC EDGAR 방문 → 10-K 다운로드
   ```

2. **Instacart** (상장사, 30분)
   ```bash
   open research/04_Instacart_guide.json
   # SEC 방문 → S-1/10-K 확인
   ```

3. **Stripe** (50분)
   ```bash
   open research/01_Stripe_guide.json
   # TechCrunch, Bloomberg 검색
   ```

4. **Databricks** (50분)
5. **Klarna** (50분)

**예상:** 3.5시간

---

**2주차 (어려운 것):**

6. Fanatics (60분)
7. SpaceX (90분)
8. Bytedance (80분)
9. BYJU's (80분)
10. DJI (90분)

**예상:** 6.5시간

---

## 💡 효율화 팁

### 1. 병렬 탭 검색

```
탭 1: Crunchbase
탭 2: Google News
탭 3: TechCrunch
탭 4: SEC (상장사)
탭 5: 공식 블로그
```

동시에 열어놓고 정보 수집

---

### 2. 정보 우선순위

**30분 안에 못 찾으면:**
- Financial: null로 유지
- Operational: 확인된 것만
- Unit Economics: 거의 null

**추정 금지!**

---

### 3. 템플릿 재사용

첫 2-3개 완료 후:
- 패턴 파악
- 단축키 활용
- 템플릿 개선

---

## 📊 목표 품질

### Tier별 목표

| Tier | 기업 | Revenue | Operating Profit | Operational | Unit Econ |
|------|------|---------|-----------------|-------------|-----------|
| A | Rivian, Instacart | ✅✅✅ | ✅✅✅ | ✅✅ | ✅ |
| B | Stripe, Databricks, Klarna | ✅✅ | ✅ | ✅✅ | - |
| C | Fanatics, SpaceX | ✅ | - | ✅ | - |
| D | Bytedance, BYJU's, DJI | ✅ | - | ✅ | - |

**Overall 목표:**
- 모든 기업 Quality Grade B 이상
- 80% 이상 필수 정보 확보
- 소스 URL 100% 기록

---

## 📖 참고 문서

### 시작 전 필독

1. **`DATA_SOURCES_GUIDE.md`** ⭐
   - 소스별 활용법
   - 검색 쿼리 패턴
   - 플랫폼별 팁

2. **`STRUCTURE_UPDATE_REPORT.md`**
   - Performance Metrics 구조
   - 어떤 필드에 무엇을 넣어야 하는지

3. **`scripts/03_research_template.md`**
   - 실제 입력 템플릿

### 리서치 중 참고

- `{Company}_guide.json` - 검색 쿼리 & URL
- `{Company}_checklist.md` - 진행 상황 체크

---

## ✨ 준비 완료 요약

```
✅ 데이터 구조 개선 완료 (v3.1)
✅ 51개 데이터 소스 발굴 & 문서화
✅ 4개 자동화 스크립트 개발
✅ 20개 리서치 가이드 생성 (파일럿 10개 × 2)
✅ 검색 쿼리 150+ 개 자동 생성
✅ 체크리스트 10개 생성
✅ 워크플로우 완성

📁 모든 파일: projects/unicorn_data_analysis/
🚀 준비 완료: 리서치 즉시 시작 가능
⏱️ 예상 시간: 10시간 (10개 기업)
```

---

## 🎯 다음 액션

### Immediate (지금 바로)

```bash
# 1. 첫 번째 기업 선택 (Rivian 권장)
cd projects/unicorn_data_analysis/research
open 07_Rivian_guide.json
open 07_Rivian_checklist.md

# 2. SEC EDGAR 방문
# URL: https://www.sec.gov/cgi-bin/browse-edgar?company=Rivian&action=getcompany

# 3. 최신 10-K 다운로드

# 4. Financial Highlights 추출

# 5. 리서치 템플릿에 입력
```

---

**작업 완료:** 2025-11-04  
**상태:** 리서치 시작 대기  
**예상 완료:** 2주 내 (10시간 작업)


