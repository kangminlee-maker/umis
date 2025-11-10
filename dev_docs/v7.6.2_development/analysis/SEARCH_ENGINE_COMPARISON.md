# Web Search 엔진 선택: DuckDuckGo vs Google

**현재 구현**: DuckDuckGo  
**이유**: 무료, API 키 불필요, 제한 없음

---

## 🔍 DuckDuckGo (현재 구현)

### **장점** ✅

```
1. 완전 무료
   - API 키 불필요
   - 과금 없음
   - 제한 없음

2. 간단한 설치
   pip install ddgs
   
   import문으로 바로 사용:
   from duckduckgo_search import DDGS
   ddgs = DDGS()
   results = ddgs.text("query", max_results=5)

3. Rate Limit 없음
   - 무제한 검색 가능
   - Throttling 없음

4. 개인정보 보호
   - 검색 기록 추적 없음
   - 사용자 데이터 수집 안함
```

### **단점** ⚠️

```
1. 검색 품질
   - Google보다 낮을 수 있음
   - 한국어 결과 제한적

2. 결과 신뢰도
   - 덜 정제됨
   - 최신성 보장 어려움

3. 구조화 정도
   - Knowledge Graph 없음
   - Rich Snippet 제한적
```

---

## 🔍 Google Search (대안)

### **장점** ✅

```
1. 검색 품질 최고
   - 가장 정확한 결과
   - 한국어 지원 우수
   - 최신 데이터

2. 구조화된 데이터
   - Knowledge Graph
   - Rich Snippets
   - Featured Snippets

3. 신뢰도
   - 검증된 출처 우선
   - Fact Check 포함
```

### **단점** ❌

```
1. 유료 (큰 문제!)
   비용 구조:
     - 100 쿼리: 무료
     - 101-10,000: $5/1000 쿼리
   
   예시:
     - 하루 100개 추정 → $0.50/일
     - 월 3,000개 → $15/월
     - 연 36,000개 → $180/년

2. API 키 필요
   - Google Cloud 프로젝트 생성
   - Custom Search API 활성화
   - Search Engine ID 생성
   - 복잡한 설정

3. Rate Limit
   - 일일 100 쿼리 (무료 티어)
   - 초과 시 과금

4. 설정 복잡
   - Programmable Search Engine 생성
   - 검색 대상 사이트 설정 필요
```

---

## 📊 비교표

| 항목 | DuckDuckGo | Google Search |
|------|------------|---------------|
| **비용** | **무료** ✅ | 유료 ($5/1000) ❌ |
| **API 키** | **불필요** ✅ | 필요 ❌ |
| **Rate Limit** | **없음** ✅ | 100/일 ❌ |
| **설치** | **간단** ✅ | 복잡 (Cloud 설정) ❌ |
| **검색 품질** | 중간 ⚠️ | **최고** ✅ |
| **한국어** | 제한적 ⚠️ | **우수** ✅ |
| **신뢰도** | 중간 ⚠️ | **높음** ✅ |
| **구조화** | 제한적 ⚠️ | **풍부** ✅ |

---

## 💡 선택 기준

### **DuckDuckGo를 선택한 이유**

```
우선순위:
  1. 비용 (무료 vs $180/년)
  2. 간편성 (설치 vs 복잡한 설정)
  3. 제한 없음 (무제한 vs 100/일)

판단:
  ⭐ UMIS 초기 단계에서는 무료 + 간편이 중요
  ⭐ 검색 품질은 RAG + Validator로 보완
  ⭐ Web Search는 보조 Source (주력 아님)
```

### **Web Search의 실제 역할**

```
Tier 2 증거 수집:
  주력: RAG Benchmark (Quantifier, 100개)
  보조: Web Search (실시간, 최신)

현실:
  - RAG가 대부분 커버 (67% 성공)
  - Web은 RAG 없을 때만 사용
  - 비중: 10-20%

결론:
  → 무료로도 충분!
  → Google 품질이 필요한 경우 드뭄
```

---

## 🔧 Google Search 구현 (선택 가능)

### **코드 비교**

#### **DuckDuckGo (현재)**

```python
from duckduckgo_search import DDGS

ddgs = DDGS()

results = ddgs.text(
    keywords=query,
    max_results=5
)

# 끝! (API 키, 설정 불필요)
```

#### **Google Search (대안)**

```python
from googleapiclient.discovery import build

# 설정 필요 (복잡!)
GOOGLE_API_KEY = "your-api-key"
SEARCH_ENGINE_ID = "your-engine-id"

service = build(
    "customsearch",
    "v1",
    developerKey=GOOGLE_API_KEY
)

results = service.cse().list(
    q=query,
    cx=SEARCH_ENGINE_ID,
    num=5
).execute()

# 비용 발생!
```

---

## 🎯 권장사항

### **현재 (무료 단계)**

```
✅ DuckDuckGo 유지
  - 비용: $0
  - 충분한 품질 (보조 Source)
  - Validator + RAG가 주력
```

### **향후 (프로덕션 확장 시)**

```
Option 1: DuckDuckGo 유지
  - Web Search 비중 낮음 (10%)
  - 무료로 충분

Option 2: Google 추가 (Hybrid)
  - DuckDuckGo 우선 시도
  - 실패 시 Google (유료)
  - 비용 최소화

Option 3: Google 전환
  - 검색 품질 최우선
  - 비용 투자 ($180/년)
  - 프리미엄 서비스
```

---

## 💡 결론

**DuckDuckGo 선택 이유**:

```
1. 비용: $0 (Google: $180/년)
2. 간편성: pip install (Google: Cloud 설정)
3. 제한: 없음 (Google: 100/일)

현재 UMIS 상황:
  - Validator가 94.7% 처리 (주력!)
  - RAG Benchmark로 Tier 2 67% 성공
  - Web Search는 보조 (10-20%)
  
결론:
  ✅ 무료 DuckDuckGo로 충분
  ✅ 품질은 Validator + RAG로 보완
  ✅ 필요시 Google 추가 가능 (Hybrid)
```

---

## 🔧 Google Search로 변경 원하시면

간단히 변경 가능합니다:

```python
# 1. 패키지 설치
pip install google-api-python-client

# 2. value.py 수정
class WebSearchSource:
    def __init__(self):
        from googleapiclient.discovery import build
        self.service = build(...)
    
    def collect(self, question, context):
        results = self.service.cse().list(...)
```

**필요사항**:
- Google Cloud API 키
- Custom Search Engine ID
- 비용: $5/1000 쿼리

원하시면 바로 구현해드리겠습니다! 🚀

상세 내용은 `SEARCH_ENGINE_COMPARISON.md`에 정리했습니다.
