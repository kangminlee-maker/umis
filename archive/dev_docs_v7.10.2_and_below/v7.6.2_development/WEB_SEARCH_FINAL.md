# Web Search 동적 엔진 선택 구현 완료

**날짜**: 2025-11-10  
**버전**: v7.6.2  
**기능**: .env 기반 검색 엔진 선택

---

## ✅ 구현 완료

### **기능**

```
1. DuckDuckGo (기본, 무료)
   - API 키 불필요
   - 제한 없음
   - 비용: $0

2. Google Custom Search (선택, 유료)
   - .env에서 API 키 설정
   - 고품질 검색
   - 비용: $5/1000 쿼리

3. 동적 선택
   - .env의 WEB_SEARCH_ENGINE 설정
   - 자동으로 선택된 엔진 사용
```

---

## 🔧 구현 내용

### **1. config.py 설정 추가**

```python
# umis_rag/core/config.py

class Settings(BaseSettings):
    # Web Search 엔진 선택
    web_search_engine: str = "duckduckgo"
    
    # Google 설정 (선택)
    google_api_key: str | None = None
    google_search_engine_id: str | None = None
    
    # 활성화 여부
    web_search_enabled: bool = True
```

---

### **2. WebSearchSource 동적 초기화**

```python
# sources/value.py

class WebSearchSource:
    def __init__(self):
        from umis_rag.core.config import settings
        
        self.engine = settings.web_search_engine
        
        if self.engine == "google":
            self._init_google()
        else:
            self._init_duckduckgo()
    
    def _init_duckduckgo(self):
        from duckduckgo_search import DDGS
        self.ddgs = DDGS()
        logger.info("DuckDuckGo 준비 (무료)")
    
    def _init_google(self):
        from googleapiclient.discovery import build
        
        self.service = build(
            "customsearch", "v1",
            developerKey=settings.google_api_key
        )
        logger.info("Google Custom Search 준비 (유료)")
```

---

### **3. 엔진별 검색 실행**

```python
def collect(self, question, context):
    # 쿼리 구성
    query = self._build_search_query(question, context)
    
    # 엔진별 검색
    if self.engine == "google":
        results = self._search_google(query)
    else:
        results = self._search_duckduckgo(query)
    
    # 숫자 추출 (공통)
    numbers = self._extract_numbers(results)
    
    # Consensus (공통)
    consensus = self._find_consensus(numbers)
    
    return [ValueEstimate(...)]
```

---

## 📝 .env 설정 예시

### **Option 1: DuckDuckGo (기본)**

```bash
# .env
OPENAI_API_KEY=sk-...

# Web Search (DuckDuckGo, 무료)
WEB_SEARCH_ENGINE=duckduckgo
WEB_SEARCH_ENABLED=true
```

**결과**: DuckDuckGo 사용, 무료

---

### **Option 2: Google (고품질)**

```bash
# .env
OPENAI_API_KEY=sk-...

# Web Search (Google, 유료)
WEB_SEARCH_ENGINE=google
WEB_SEARCH_ENABLED=true

# Google 설정
GOOGLE_API_KEY=AIzaSyA...
GOOGLE_SEARCH_ENGINE_ID=a1b2c3d4e5...
```

**결과**: Google Custom Search 사용, 고품질

---

### **Option 3: 비활성화**

```bash
# .env
WEB_SEARCH_ENABLED=false
```

**결과**: Web Search 완전 비활성화

---

## 🎯 사용 예시

### **자동 선택**

```python
from umis_rag.agents.estimator import EstimatorRAG

estimator = EstimatorRAG()

# .env 설정에 따라 자동으로:
# - duckduckgo → DuckDuckGo 사용
# - google → Google 사용

result = estimator.estimate("한국 인구는?")

# Web Search Source가 설정된 엔진으로 작동
```

---

## 📊 비교 (실제 사용)

| 설정 | 엔진 | 비용 | 품질 | API 키 | 제한 |
|------|------|------|------|--------|------|
| duckduckgo | DuckDuckGo | **$0** | 중간 | **불필요** | **없음** |
| google | Google | $5/1000 | **최고** | 필요 | 100/일 (무료) |

---

## 🎊 최종 평가

**구현**:
- ✅ .env 기반 동적 선택
- ✅ DuckDuckGo (기본, 무료)
- ✅ Google Custom Search (선택, 유료)
- ✅ API 키 설정 지원

**유연성**:
- ✅ 간단히 엔진 변경 (WEB_SEARCH_ENGINE=google)
- ✅ 비활성화 가능 (WEB_SEARCH_ENABLED=false)
- ✅ 코드 수정 불필요

**문서**:
- `WEB_SEARCH_SETUP_GUIDE.md` - 설정 가이드
- `SEARCH_ENGINE_COMPARISON.md` - 엔진 비교
- `config/web_search.env.template` - 템플릿

---

**Web Search 동적 엔진 선택 완성!** 🚀

**사용자 요구사항 100% 구현**:
- ✅ .env에서 엔진 토글
- ✅ Google API 키 입력 지원
- ✅ 동적 선택 작동

모든 작업 완료! 🎊

