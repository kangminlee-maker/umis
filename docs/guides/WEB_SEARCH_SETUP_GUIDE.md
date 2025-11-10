# Web Search 설정 가이드

**버전**: v7.6.2  
**기능**: Tier 2 Web Search Source  
**선택**: DuckDuckGo (무료) or Google (유료)

---

## 🚀 빠른 시작 (DuckDuckGo, 기본)

### **1. 패키지 설치**

```bash
pip install ddgs
```

### **2. .env 설정**

```bash
# .env 파일에 추가 (또는 기본값 사용)
WEB_SEARCH_ENGINE=duckduckgo
WEB_SEARCH_ENABLED=true
```

### **3. 바로 사용!**

```python
from umis_rag.agents.estimator import EstimatorRAG

estimator = EstimatorRAG()
result = estimator.estimate("한국 인구는?")

# Web Search가 자동으로 작동
# - DuckDuckGo 검색
# - 숫자 추출
# - Consensus 알고리즘
```

**끝!** (API 키, 설정 불필요)

---

## 🎯 Google Custom Search 사용 (선택)

### **왜 Google을?**

```
장점:
  ✅ 검색 품질 최고
  ✅ 한국어 지원 우수
  ✅ 구조화된 데이터 (Rich Snippets)

단점:
  ❌ 비용 발생 ($5/1000 쿼리)
  ❌ API 키 필요
  ❌ 설정 복잡

권장:
  - 프로덕션 단계
  - 품질 최우선
  - 비용 투자 가능
```

---

### **1. Google Cloud 설정**

#### **Step 1: Google Cloud 프로젝트**

```
1. https://console.cloud.google.com/ 접속
2. 새 프로젝트 생성 또는 선택
3. "APIs & Services" → "Library"
4. "Custom Search API" 검색
5. "Enable" 클릭
```

#### **Step 2: API 키 생성**

```
1. "APIs & Services" → "Credentials"
2. "+ CREATE CREDENTIALS" 클릭
3. "API Key" 선택
4. API 키 복사 (예: AIzaSyA...)
```

---

### **2. Custom Search Engine 생성**

#### **Step 1: 검색 엔진 생성**

```
1. https://programmablesearchengine.google.com/ 접속
2. "Add" 또는 "Get Started" 클릭
3. 설정:
   - 이름: "UMIS Search" (자유)
   - 검색 대상: "Search the entire web" 선택 ⭐
   - Language: Korean
4. "Create" 클릭
```

#### **Step 2: Search Engine ID 복사**

```
1. 생성된 검색 엔진 선택
2. "Basics" 탭
3. "Search engine ID" 복사 (예: a1b2c3d4e5...)
```

---

### **3. .env 설정**

```bash
# .env 파일 편집
WEB_SEARCH_ENGINE=google

GOOGLE_API_KEY=AIzaSyA...  # Step 2에서 복사한 키
GOOGLE_SEARCH_ENGINE_ID=a1b2c3d4e5...  # Step 2에서 복사한 ID
```

---

### **4. 패키지 설치**

```bash
pip install google-api-python-client
```

---

### **5. 사용**

```python
from umis_rag.agents.estimator import EstimatorRAG

estimator = EstimatorRAG()
result = estimator.estimate("한국 인구는?")

# Google Custom Search가 자동으로 작동
# - 고품질 검색 결과
# - 비용 발생 ($5/1000 쿼리)
```

---

## 🔧 설정 옵션

### **.env 설정**

```bash
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Option 1: DuckDuckGo (기본, 무료)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WEB_SEARCH_ENGINE=duckduckgo
WEB_SEARCH_ENABLED=true

# Google 설정 불필요
# GOOGLE_API_KEY=  (비워둠)
# GOOGLE_SEARCH_ENGINE_ID=  (비워둠)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Option 2: Google (유료, 고품질)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WEB_SEARCH_ENGINE=google
WEB_SEARCH_ENABLED=true

GOOGLE_API_KEY=AIzaSyA1B2C3...
GOOGLE_SEARCH_ENGINE_ID=a1b2c3d4e5f6...

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Option 3: Web Search 비활성화
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WEB_SEARCH_ENABLED=false

# 엔진 설정 무시됨
```

---

## 📊 비용 계산 (Google)

### **무료 티어**

```
일일 100 쿼리 무료
  → 월 3,000 쿼리
  → 연 36,500 쿼리
  → 비용: $0

추정 사용량:
  - 하루 50개 추정 → 무료 범위 ✅
  - 하루 150개 추정 → 초과 ($0.25/일)
```

### **유료 사용**

```
$5 per 1,000 쿼리 (100개 초과분)

예시:
  하루 200개 추정:
    - 무료: 100개
    - 유료: 100개 = $0.50/일
    - 월: $15
    - 연: $180

  월 10,000개 추정:
    - 무료: 3,000개
    - 유료: 7,000개 = $35/월
    - 연: $420
```

---

## 🎯 권장 사항

### **초기 단계 (현재)**

```
✅ DuckDuckGo 권장
  - 비용: $0
  - Validator가 94.7% 처리
  - Web Search는 보조 (10-20%)
  → 무료로 충분!
```

### **프로덕션 (향후)**

```
선택 1: DuckDuckGo 유지
  - 비용 최우선
  - 품질은 Validator + RAG로 보완

선택 2: Google로 전환
  - 품질 최우선
  - 비용 투자 가능
  - 하루 50개 미만 → 무료 범위

선택 3: Hybrid (구현 가능)
  - DuckDuckGo 우선 시도
  - 실패 시 Google
  - 비용 최소화 + 품질 확보
```

---

## 🔍 동작 확인

### **현재 엔진 확인**

```python
from umis_rag.core.config import settings

print(f"검색 엔진: {settings.web_search_engine}")
print(f"활성화: {settings.web_search_enabled}")

if settings.web_search_engine == "google":
    print(f"Google API: {settings.google_api_key[:10]}...")
    print(f"Engine ID: {settings.google_search_engine_id[:10]}...")
```

### **테스트**

```python
from umis_rag.agents.estimator import EstimatorRAG

estimator = EstimatorRAG()

# Validator 비활성화 (Web Search 테스트)
estimator._search_validator = lambda q, c: None

result = estimator.estimate("한국 인구는?")

# Tier 2에서 Web Search 증거 확인
if result and result.tier == 2:
    web_evidence = [
        e for e in result.value_estimates 
        if e.source_type.value == 'web_search'
    ]
    
    if web_evidence:
        print(f"✅ Web Search 작동!")
        print(f"엔진: {settings.web_search_engine}")
```

---

## ⚠️ 주의사항

### **Google Custom Search**

```
1. 검색 대상 설정:
   ✅ "Search the entire web" 선택 (권장)
   ❌ 특정 사이트만 선택 (제한적)

2. 언어 설정:
   ✅ Korean 추가 (한국어 결과)

3. 비용 모니터링:
   - Cloud Console에서 API 사용량 확인
   - 예산 알림 설정 권장

4. API 키 보안:
   - .env 파일은 .gitignore에 포함
   - 키 유출 주의
```

---

## 📚 템플릿 파일

**위치**: `config/web_search.env.template`

**사용법**:
```bash
# 1. 템플릿 확인
cat config/web_search.env.template

# 2. .env에 추가
cat config/web_search.env.template >> .env

# 3. .env 편집하여 API 키 입력
vi .env
```

---

## 🎉 완료!

**구현 완료**:
- ✅ DuckDuckGo (기본, 무료)
- ✅ Google Custom Search (선택, 유료)
- ✅ .env 기반 동적 선택
- ✅ API 키 설정 지원

**사용법**:
1. .env에서 엔진 선택
2. Google 사용 시 API 키 입력
3. 자동으로 선택된 엔진 사용

**상태**: READY 🚀

