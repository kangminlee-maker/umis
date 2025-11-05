# 🔍 파일럿 유니콘 리서치

**폴더:** `projects/unicorn_data_analysis/research/`  
**목적:** 파일럿 10개 유니콘 기업 상세 리서치  
**상태:** 준비 완료, 리서치 대기 중

---

## 📁 파일 구조

### 각 기업별 2개 파일

```
research/
├── 01_Stripe_guide.json           - 검색 쿼리 15-20개 + URL
├── 01_Stripe_checklist.md         - 리서치 체크리스트
│
├── 02_SpaceX_guide.json
├── 02_SpaceX_checklist.md
│
├── ... (3-9번 생략)
│
├── 10_DJI_Innovations_guide.json
└── 10_DJI_Innovations_checklist.md
```

**총 20개 파일** (파일럿 10개 × 2)

---

## 🚀 빠른 시작

### 추천: Rivian부터 시작 (가장 쉬움)

```bash
# 1. 가이드 파일 열기
open 07_Rivian_guide.json
open 07_Rivian_checklist.md

# 2. SEC URL 방문 (guide.json의 direct_urls.sec)
# https://www.sec.gov/cgi-bin/browse-edgar?company=Rivian...

# 3. 최신 10-K 다운로드

# 4. Financial Highlights 추출
```

**예상 시간:** 30분  
**난이도:** ⭐ 매우 쉬움  
**품질:** ⭐⭐⭐⭐⭐

---

## 📋 파일 사용법

### A. `{Company}_guide.json` 사용

**구조:**
```json
{
  "company": "Stripe",
  "competitors": ["PayPal", "Square", ...],
  "search_queries": {
    "revenue_financial": [
      {
        "query": "검색어",
        "url": "https://www.google.com/search?q=..."
      }
    ],
    "operational_metrics": [...],
    "business_model": [...],
    ...
  },
  "site_specific": {
    "techcrunch": {...},
    "bloomberg": {...}
  },
  "direct_urls": {
    "crunchbase": "https://...",
    "sec": "https://..."
  }
}
```

**활용:**
1. JSON 파일 열기
2. `url` 필드 복사 → 브라우저에 붙여넣기
3. 자동으로 검색 실행됨
4. 결과에서 정보 수집

---

### B. `{Company}_checklist.md` 사용

**구조:**
```markdown
# ✅ Stripe 리서치 체크리스트

## Phase 1: 기본 정보 (10분)
- [ ] Crunchbase 확인
- [ ] 공식 사이트 방문
- [ ] 뉴스 검색

## Phase 2: 재무 정보 (20-30분)
- [ ] Revenue (3년) 추출
- [ ] Operating Profit 확인

## Phase 3-5: ...
```

**활용:**
1. Markdown 파일 열기
2. 체크박스 하나씩 체크하며 진행
3. 예상 시간 참고
4. Phase별로 순차 진행

---

## 🎯 리서치 우선순위

### 그룹 A: 상장사 (쉬움) ⭐

| # | 기업 | 티커 | 예상 시간 | 주요 소스 |
|---|------|------|-----------|-----------|
| 7 | **Rivian** | RIVN | 30분 | SEC 10-K |
| 4 | **Instacart** | CART | 30분 | SEC S-1/10-K |

**리서치 전략:**
1. SEC EDGAR 방문
2. 최신 10-K 다운로드
3. Part II, Item 8: Financial Statements
4. Item 7: MD&A (Key Metrics)
5. 템플릿에 입력

---

### 그룹 B: 상장 준비/풍부한 정보 (보통) ⭐⭐

| # | 기업 | 예상 시간 | 주요 소스 |
|---|------|-----------|-----------|
| 1 | **Stripe** | 50분 | TechCrunch, Bloomberg, Blog |
| 6 | **Databricks** | 50분 | TechCrunch, 언론 보도 |
| 3 | **Klarna** | 50분 | European media, Blog |

**리서치 전략:**
1. Crunchbase 기본 정보
2. Google 검색 (가이드 쿼리 사용)
3. TechCrunch 기사 검색
4. 공식 블로그 확인
5. 가능한 정보만 입력

---

### 그룹 C: 비상장/제한적 (어려움) ⭐⭐⭐

| # | 기업 | 예상 시간 | 주요 소스 |
|---|------|-----------|-----------|
| 8 | **Fanatics** | 60분 | TechCrunch, Sports media |
| 2 | **SpaceX** | 90분 | 뉴스 (매우 제한적) |

**리서치 전략:**
1. 언론 보도 위주
2. 공개된 정보 위주
3. 추정 금지
4. null 많아도 OK

---

### 그룹 D: 해외 (중국/인도) (매우 어려움) ⭐⭐⭐⭐

| # | 기업 | 국가 | 예상 시간 | 주요 소스 |
|---|------|------|-----------|-----------|
| 5 | **Bytedance** | 🇨🇳 | 80분 | TechNode, Reuters |
| 9 | **BYJU's** | 🇮🇳 | 80분 | YourStory, Economic Times |
| 10 | **DJI** | 🇨🇳 | 90분 | TechNode, Chinese media |

**리서치 전략:**
1. 지역 특화 미디어
2. 후룬 리포트
3. 글로벌 미디어 (Bloomberg, Reuters)
4. 제한적 정보 수용

---

## 📖 필수 참고 문서

### 시작 전

1. **`../DATA_SOURCES_GUIDE.md`** ⭐⭐⭐⭐⭐
   - 51개 데이터 소스 종합
   - 소스별 활용법
   - 검색 쿼리 패턴

2. **`../PILOT_RESEARCH_READY.md`** ⭐⭐⭐⭐⭐
   - 리서치 시작 가이드
   - 워크플로우 상세
   - 시간 추정

3. **`../scripts/03_research_template.md`** ⭐⭐⭐⭐⭐
   - 실제 입력 템플릿
   - Performance Metrics 구조

---

## 💡 사용 팁

### 1. URL 활용

**guide.json 파일에서:**
```json
"url": "https://www.google.com/search?q=..."
```

→ **복사 → 브라우저 붙여넣기** = 자동 검색!

---

### 2. 체크리스트 활용

**checklist.md 파일:**
```markdown
- [ ] Crunchbase 확인
```

→ **작업 완료하면 `[x]`로 변경**

```markdown
- [x] Crunchbase 확인 ✅
```

---

### 3. 시간 관리

- **30분 타이머 설정**
- 못 찾으면 → null로 유지
- **추정 금지!**

---

### 4. 소스 기록

**반드시 소스 URL 기록:**
```json
{
  "year": 2023,
  "amount_usd_million": 16000,
  "source": "Bloomberg - https://..."
}
```

---

## 🎯 목표

### 파일럿 10개 완료 시

**정량 목표:**
- ✅ 10개 기업 전부 리서치 완료
- ✅ 평균 Quality Grade B 이상
- ✅ 재무 정보 60%+ 확보
- ✅ 정성 정보 100% 확보

**정성 목표:**
- ✅ 리서치 프로세스 검증
- ✅ 소요 시간 실측
- ✅ 소스 유효성 확인
- ✅ 템플릿 개선점 도출

---

## 📊 진행 상황 추적

### 완료 현황 (0/10)

- [ ] 1. Stripe
- [ ] 2. SpaceX
- [ ] 3. Klarna
- [ ] 4. Instacart
- [ ] 5. Bytedance
- [ ] 6. Databricks
- [ ] 7. Rivian ⭐ (추천 첫 시작)
- [ ] 8. Fanatics
- [ ] 9. BYJU's
- [ ] 10. DJI

**업데이트:** 이 파일에 진행 상황 기록

---

## 📝 리서치 결과 저장

### 임시 저장 (Markdown)

```
research/01_Stripe_research.md
research/02_SpaceX_research.md
...
```

### 최종 저장 (JSON)

```
../unicorn_companies_rag_enhanced.json
```

**업데이트 스크립트 (추후 개발 예정):**
```bash
python3 ../scripts/05_update_from_research.py
```

---

## ⚠️ 주의사항

### DO ✅

- ✅ 소스 URL 반드시 기록
- ✅ 발표 날짜 명시
- ✅ 신뢰도 평가 (⭐⭐⭐⭐⭐)
- ✅ 못 찾으면 null

### DON'T ❌

- ❌ 추정값 사용
- ❌ 소스 없이 숫자 입력
- ❌ 오래된 정보 (2년 이상)
- ❌ 30분 넘게 한 지표 찾기

---

## 🎉 성공 기준

### 개별 기업

- Quality Grade A or B
- 필수 정보 80%+ 확보
- 모든 정보에 소스 명시

### 전체 파일럿

- 10개 모두 완료
- 평균 Quality Grade B+
- 리서치 방법론 확립
- Tier 1 (Top 100) 확장 준비

---

**준비 완료:** 2025-11-04  
**시작 대기:** 수동 리서치 시작  
**예상 완료:** 2주 내 (10시간)

