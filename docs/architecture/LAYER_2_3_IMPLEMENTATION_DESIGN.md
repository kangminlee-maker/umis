# Layer 2 & 3 구현 설계안

**작성일**: 2025-11-05  
**대상**: Multi-Layer Guestimation 완성  
**상태**: 📋 Design Document

---

## 🎯 목표

Layer 2 (LLM 직접 답변)과 Layer 3 (웹 검색)을 구현하여 **8개 레이어 100% 완성**

---

## 📐 Layer 2: LLM 직접 답변 설계

### 개요

**목적**: 간단한 사실 질문을 LLM에게 직접 물어서 즉시 답변

**적용 대상**:
- "한국 인구는?"
- "일반적인 식사 시간은?"
- "평균 통근 시간은?"

**제외 대상**:
- 복잡한 추론 필요
- 최신 데이터 필수 (2024년 특정 통계 등)
- 산업별 특화 데이터

---

### 구현 방법 (2가지 옵션)

#### 옵션 A: Native Mode (권장) ⭐

**원리**: Cursor Native LLM 활용 (비용 $0)

**구현**:
```python
def _try_llm_direct(self, question: str) -> EstimationResult:
    """Layer 2: LLM 직접 답변 (Native Mode)"""
    
    # 1. 간단한 사실 질문인지 판단
    if not self._is_simple_fact(question):
        return result  # Layer 3으로
    
    # 2. Native Mode: 사용자에게 안내
    result.logic_steps.append("💡 Layer 2: LLM 직접 답변 권장")
    result.logic_steps.append("   질문: \"{}\"".format(question))
    result.logic_steps.append("   → Cursor Composer/Chat에서 직접 질문하세요")
    
    # 3. 수동 입력 대기 (Interactive)
    if self.interactive_mode:
        print(f"\n❓ LLM에게 질문: {question}")
        user_input = input("답변 (숫자만 입력, 건너뛰려면 Enter): ")
        
        if user_input.strip():
            try:
                value = float(user_input.replace(',', ''))
                result.value = value
                result.confidence = 0.7
                result.logic_steps.append(f"✅ Layer 2: LLM 답변 = {value}")
                return result
            except:
                pass
    
    # 4. 자동 모드는 건너뜀
    result.logic_steps.append("⚠️ Layer 2: 자동 실행 비활성 → Layer 3으로")
    return result
```

**장점**:
- ✅ 비용 $0
- ✅ 최고 품질
- ✅ 간단한 구현

**단점**:
- 🚫 사용자 개입 필요
- 🚫 자동화 불가

---

#### 옵션 B: External API (자동화)

**원리**: OpenAI API 호출

**구현**:
```python
def _try_llm_direct(self, question: str) -> EstimationResult:
    """Layer 2: LLM 직접 답변 (External API)"""
    
    if not self._is_simple_fact(question):
        return result
    
    if not self.enable_llm_api:
        result.logic_steps.append("⚠️ Layer 2: API 비활성 → Layer 3으로")
        return result
    
    try:
        from openai import OpenAI
        import os
        
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # LLM에게 간결한 답변 요청
        prompt = f"""질문: {question}

간단한 숫자로만 답변하세요.
예: "한국 인구는?" → "5200만명" 또는 "52,000,000"

질문이 추정 불가능하면 "알 수 없음"이라고 답변하세요."""

        response = client.chat.completions.create(
            model="gpt-4o-mini",  # 저렴한 모델
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=50
        )
        
        answer = response.choices[0].message.content
        
        # 숫자 추출
        value = self._extract_number(answer)
        
        if value:
            result.value = value
            result.confidence = 0.7  # LLM 답변은 검증 권장
            result.logic_steps.append(f"✅ Layer 2: LLM 답변 = {answer}")
            result.logic_steps.append(f"   추출값: {value}")
            result.used_data.append({
                'source': 'LLM (GPT-4o-mini)',
                'raw_answer': answer,
                'extracted': value
            })
            return result
        else:
            result.logic_steps.append(f"⚠️ Layer 2: LLM 답변 '{answer}' (숫자 추출 실패) → Layer 3으로")
    
    except Exception as e:
        result.logic_steps.append(f"🚫 Layer 2: LLM API 에러 ({e}) → Layer 3으로")
    
    return result

def _extract_number(self, text: str) -> Optional[float]:
    """텍스트에서 숫자 추출"""
    import re
    
    # 패턴: "5200만", "52,000,000", "5.2천만" 등
    patterns = [
        r'([\d,]+\.?\d*)\s*만',     # 5200만
        r'([\d,]+\.?\d*)\s*억',     # 27억
        r'([\d,]+\.?\d*)\s*천만',   # 5천만
        r'([\d,]+\.?\d*)',          # 52000000
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            num_str = match.group(1).replace(',', '')
            value = float(num_str)
            
            # 단위 처리
            if '만' in text:
                value *= 10000
            elif '억' in text:
                value *= 100000000
            elif '천만' in text:
                value *= 10000000
            
            return value
    
    return None
```

**장점**:
- ✅ 완전 자동화
- ✅ 배치 처리 가능

**단점**:
- 🚫 API 비용 (~$0.001/질문)
- 🚫 Native LLM보다 품질 낮을 수 있음

---

### 하이브리드 접근 (권장) ⭐

```python
class MultiLayerGuestimation:
    def __init__(self, llm_mode='native', ...):
        self.llm_mode = llm_mode  # 'native' or 'external'
    
    def _try_llm_direct(self, question):
        if self.llm_mode == 'native':
            return self._llm_native(question)  # Interactive
        elif self.llm_mode == 'external':
            return self._llm_api(question)     # Automated
        else:
            return result  # Skip
```

---

## 📐 Layer 3: 웹 검색 설계

### 개요

**목적**: 웹에서 상위 5-10개 검색 결과의 공통값 추출

**적용 대상**:
- "2024년 한국 디지털 광고비는?"
- "음식점 평균 테이블 수는?"
- "스타벅스 평균 매출은?"

**제외 대상**:
- 검색 불가능한 질문
- 합의된 값이 없는 경우

---

### 구현 방법

#### 옵션 A: Cursor web_search tool (권장) ⭐

**원리**: Cursor 내장 web_search tool 활용

**구현**:
```python
def _try_web_consensus(self, question: str) -> EstimationResult:
    """Layer 3: 웹 검색 (Cursor tool)"""
    
    if not self.enable_web_search:
        return result
    
    # Native Mode: 사용자에게 안내
    if self.llm_mode == 'native':
        result.logic_steps.append("💡 Layer 3: 웹 검색 권장")
        result.logic_steps.append(f"   질문: \"{question}\"")
        result.logic_steps.append("   → Cursor에서 web_search tool 사용")
        result.logic_steps.append("   → 상위 5-10개 결과에서 공통값 확인")
        
        # Interactive: 사용자 입력 대기
        if self.interactive_mode:
            print(f"\n🔍 웹 검색 필요: {question}")
            user_input = input("검색 결과 (숫자 입력, 건너뛰려면 Enter): ")
            
            if user_input.strip():
                try:
                    value = float(user_input.replace(',', ''))
                    result.value = value
                    result.confidence = 0.8
                    result.logic_steps.append(f"✅ Layer 3: 웹 검색 결과 = {value}")
                    return result
                except:
                    pass
        
        return result
    
    # External Mode: 자동 웹 검색 (구현 옵션 B 참조)
    else:
        return self._web_search_api(question)
```

**장점**:
- ✅ Cursor 네이티브 기능 활용
- ✅ 추가 비용 없음
- ✅ 품질 좋음

**단점**:
- 🚫 자동화 불가
- 🚫 사용자 개입 필요

---

#### 옵션 B: Google Search API (자동화)

**원리**: SerpAPI 또는 Google Custom Search API

**구현**:
```python
def _web_search_api(self, question: str) -> EstimationResult:
    """Layer 3: 웹 검색 (API)"""
    
    try:
        # SerpAPI 사용 (월 100회 무료)
        import requests
        
        api_key = os.getenv('SERPAPI_KEY')
        if not api_key:
            result.logic_steps.append("🚫 Layer 3: SERPAPI_KEY 없음 → Layer 4로")
            return result
        
        # 검색 실행
        params = {
            'q': question,
            'api_key': api_key,
            'num': 10  # 상위 10개
        }
        
        response = requests.get(
            'https://serpapi.com/search',
            params=params
        )
        
        data = response.json()
        results = data.get('organic_results', [])
        
        # 각 결과에서 숫자 추출
        numbers = []
        for r in results[:10]:
            snippet = r.get('snippet', '')
            num = self._extract_number(snippet)
            if num:
                numbers.append(num)
        
        # 공통값 찾기 (중앙값 또는 최빈값)
        if len(numbers) >= 3:
            # 중앙값 사용
            numbers.sort()
            median = numbers[len(numbers) // 2]
            
            result.value = median
            result.confidence = 0.8
            result.logic_steps.append(f"✅ Layer 3: 웹 검색 {len(numbers)}개 결과")
            result.logic_steps.append(f"   중앙값: {median}")
            result.used_data.append({
                'source': '웹 검색 (SerpAPI)',
                'results_count': len(numbers),
                'values': numbers,
                'median': median
            })
            return result
        else:
            result.logic_steps.append(f"⚠️ Layer 3: 충분한 결과 없음 ({len(numbers)}개) → Layer 4로")
    
    except Exception as e:
        result.logic_steps.append(f"🚫 Layer 3: 웹 검색 에러 ({e}) → Layer 4로")
    
    return result
```

**장점**:
- ✅ 완전 자동화
- ✅ 최신 데이터
- ✅ 복수 출처 (신뢰도 높음)

**단점**:
- 🚫 API 비용 (무료 100회/월)
- 🚫 API 키 필요

---

#### 옵션 C: 직접 스크래핑 (고급)

**원리**: requests + BeautifulSoup로 직접 파싱

**구현**:
```python
def _web_search_scraping(self, question: str) -> EstimationResult:
    """Layer 3: 웹 검색 (직접 스크래핑)"""
    
    import requests
    from bs4 import BeautifulSoup
    import urllib.parse
    
    # Google 검색 URL
    query = urllib.parse.quote(question)
    url = f"https://www.google.com/search?q={query}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
    }
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Featured Snippet 우선 (답변 박스)
        featured = soup.find('div', class_='BNeawe')
        if featured:
            text = featured.get_text()
            value = self._extract_number(text)
            
            if value:
                result.value = value
                result.confidence = 0.85  # Featured snippet 신뢰도 높음
                result.logic_steps.append(f"✅ Layer 3: Google Featured Snippet")
                result.logic_steps.append(f"   답변: {text}")
                result.used_data.append({
                    'source': 'Google Featured Snippet',
                    'text': text,
                    'value': value
                })
                return result
        
        # 일반 검색 결과에서 숫자 추출
        snippets = soup.find_all('div', class_='VwiC3b')
        numbers = []
        
        for snippet in snippets[:10]:
            text = snippet.get_text()
            num = self._extract_number(text)
            if num:
                numbers.append(num)
        
        # 공통값 (중앙값)
        if len(numbers) >= 3:
            numbers.sort()
            median = numbers[len(numbers) // 2]
            
            result.value = median
            result.confidence = 0.75
            result.logic_steps.append(f"✅ Layer 3: 웹 검색 {len(numbers)}개 결과 중앙값")
            return result
    
    except Exception as e:
        result.logic_steps.append(f"🚫 Layer 3: 스크래핑 에러 → Layer 4로")
    
    return result
```

**장점**:
- ✅ 무료
- ✅ API 키 불필요

**단점**:
- 🚫 불안정 (HTML 구조 변경 시)
- 🚫 Rate limit 위험
- 🚫 robots.txt 위반 가능성

---

### 권장 구현 (하이브리드)

```python
class MultiLayerGuestimation:
    def __init__(
        self,
        llm_mode='native',  # 'native', 'external', 'skip'
        web_search_mode='native',  # 'native', 'api', 'scraping', 'skip'
        ...
    ):
        self.llm_mode = llm_mode
        self.web_search_mode = web_search_mode
    
    def _try_llm_direct(self, question):
        if self.llm_mode == 'native':
            return self._llm_native_interactive(question)
        elif self.llm_mode == 'external':
            return self._llm_api(question)
        else:
            return result  # Skip
    
    def _try_web_consensus(self, question):
        if self.web_search_mode == 'native':
            return self._web_native_interactive(question)
        elif self.web_search_mode == 'api':
            return self._web_search_api(question)
        elif self.web_search_mode == 'scraping':
            return self._web_search_scraping(question)
        else:
            return result  # Skip
```

---

## 🔧 공통 유틸리티 함수

### 간단한 사실 질문 판단

```python
def _is_simple_fact(self, question: str) -> bool:
    """간단한 사실 질문인지 판단"""
    
    # 간단한 사실 패턴
    simple_patterns = [
        r'인구',
        r'평균.*시간',
        r'일반적',
        r'보통',
        r'통상',
        r'몇\s*(명|개|시간|일)',
    ]
    
    # 복잡한 질문 패턴 (제외)
    complex_patterns = [
        r'왜',
        r'어떻게',
        r'~한다면',
        r'비교',
        r'분석',
    ]
    
    has_simple = any(re.search(p, question) for p in simple_patterns)
    has_complex = any(re.search(p, question) for p in complex_patterns)
    
    return has_simple and not has_complex
```

### 숫자 추출 (강화 버전)

```python
def _extract_number(self, text: str) -> Optional[float]:
    """
    텍스트에서 숫자 추출
    
    지원 형식:
    - "5200만명" → 52,000,000
    - "52,000,000" → 52,000,000
    - "5.2천만" → 52,000,000
    - "27억원" → 2,700,000,000
    - "30일" → 30
    - "15%" → 0.15
    """
    import re
    
    # 패턴 우선순위
    patterns = [
        # 억 단위
        (r'([\d,]+\.?\d*)\s*억', 100000000),
        # 천만 단위
        (r'([\d,]+\.?\d*)\s*천만', 10000000),
        # 만 단위
        (r'([\d,]+\.?\d*)\s*만', 10000),
        # 천 단위
        (r'([\d,]+\.?\d*)\s*천', 1000),
        # 퍼센트
        (r'([\d,]+\.?\d*)\s*%', 0.01),
        # 일반 숫자
        (r'([\d,]+\.?\d*)', 1),
    ]
    
    for pattern, multiplier in patterns:
        match = re.search(pattern, text)
        if match:
            num_str = match.group(1).replace(',', '')
            try:
                value = float(num_str) * multiplier
                return value
            except:
                continue
    
    return None
```

### 공통값 추출 (합의 알고리즘)

```python
def _find_consensus(self, numbers: List[float]) -> Optional[float]:
    """
    여러 값에서 공통값/합의값 추출
    
    방법:
    1. Clustering (±20% 범위)
    2. 가장 큰 클러스터의 중앙값
    """
    if len(numbers) < 3:
        return None
    
    # 1. 정렬
    sorted_nums = sorted(numbers)
    
    # 2. 클러스터링 (±20% 범위)
    clusters = []
    current_cluster = [sorted_nums[0]]
    
    for num in sorted_nums[1:]:
        # 현재 클러스터 중앙값과 비교
        cluster_median = current_cluster[len(current_cluster)//2]
        
        if abs(num - cluster_median) / cluster_median <= 0.2:
            current_cluster.append(num)
        else:
            clusters.append(current_cluster)
            current_cluster = [num]
    
    clusters.append(current_cluster)
    
    # 3. 가장 큰 클러스터 선택
    largest_cluster = max(clusters, key=len)
    
    # 4. 중앙값 반환
    largest_cluster.sort()
    median = largest_cluster[len(largest_cluster) // 2]
    
    return median
```

---

## 📋 구현 계획

### Phase 1: 기본 구현 (30분)

**Layer 2 - Native Interactive**:
- [ ] `_is_simple_fact()` 함수
- [ ] `_llm_native_interactive()` (사용자 입력)
- [ ] `_extract_number()` 강화

**Layer 3 - Native Interactive**:
- [ ] `_web_native_interactive()` (사용자 입력)
- [ ] `_find_consensus()` 함수

---

### Phase 2: API 구현 (30분)

**Layer 2 - External API**:
- [ ] `_llm_api()` (OpenAI API)
- [ ] GPT-4o-mini 호출
- [ ] 응답 파싱

**Layer 3 - SerpAPI**:
- [ ] `_web_search_api()` (SerpAPI)
- [ ] 결과 파싱
- [ ] 공통값 추출

---

### Phase 3: 테스트 (20분)

**테스트 케이스**:
- [ ] "한국 인구는?" (Layer 2)
- [ ] "2024년 한국 GDP는?" (Layer 3)
- [ ] "평균 식사 시간은?" (Layer 2)
- [ ] "음식점 평균 테이블 수는?" (Layer 3)

---

## 🎯 최종 구조

### 완성 후 모습

```python
class MultiLayerGuestimation:
    def __init__(
        self,
        project_context=None,
        llm_mode='native',         # 'native', 'external', 'skip'
        web_search_mode='native',  # 'native', 'api', 'scraping', 'skip'
        interactive_mode=False,    # True: 사용자 입력 대기
    ):
        ...
    
    # 8개 레이어 모두 구현됨!
    def _try_project_data(...)     # ✅ 완성
    def _try_llm_direct(...)        # 🔄 구현 필요
    def _try_web_consensus(...)     # 🔄 구현 필요
    def _try_law_based(...)         # ✅ 완성
    def _try_behavioral(...)        # ✅ 완성
    def _try_statistical(...)       # ✅ 완성
    def _try_rag_benchmark(...)     # ✅ 완성
    def _try_constraint_boundary(...) # ✅ 완성
```

---

## 💡 사용 시나리오 (완성 후)

### 시나리오 1: 완전 자동 (External Mode)

```python
estimator = MultiLayerGuestimation(
    llm_mode='external',      # API 자동 호출
    web_search_mode='api',    # SerpAPI 사용
)

result = estimator.estimate("2024년 한국 GDP는?")
# Layer 1: 없음
# Layer 2: LLM API 호출 → "약 1.8조 달러" → 1.8 추출
# → 반환!
```

### 시나리오 2: Native Interactive (권장)

```python
estimator = MultiLayerGuestimation(
    llm_mode='native',
    web_search_mode='native',
    interactive_mode=True,    # 사용자 입력 대기
)

result = estimator.estimate("한국 평균 통근 시간은?")
# Layer 1: 없음
# Layer 2: 
#   → 출력: "💡 LLM에게 질문: 한국 평균 통근 시간은?"
#   → 입력 대기: "60분" 입력
#   → 60 반환!
```

### 시나리오 3: Mixed Mode

```python
estimator = MultiLayerGuestimation(
    llm_mode='external',      # LLM은 API
    web_search_mode='native', # 웹은 수동
)

result = estimator.estimate("한국 인구는?")
# Layer 1: 없음
# Layer 2: GPT-4o-mini API → "5200만명" → 52,000,000
# → 반환!
```

---

## 🔐 환경변수 추가

### .env 파일

```bash
# 기존
OPENAI_API_KEY=sk-proj-...

# 신규 (Layer 2, 3용)
SERPAPI_KEY=your-serpapi-key  # 웹 검색용 (선택)
ENABLE_LLM_API=true           # Layer 2 API 활성화 (기본 false)
ENABLE_WEB_API=false          # Layer 3 API 활성화 (기본 false)
```

---

## 📊 비용 분석 (100회 추정 기준)

| 모드 | Layer 2 | Layer 3 | 총 비용 |
|------|---------|---------|---------|
| **Native** | 사용자 입력 | 사용자 입력 | $0 |
| **External** | GPT-4o-mini | SerpAPI | ~$0.15 |
| **Mixed** | GPT-4o-mini | 사용자 입력 | ~$0.10 |

**권장**: Native (비용 $0, 품질 동일)

---

## 🎯 우선순위 추천

### 즉시 구현 (권장)

**Layer 2 - Native Interactive**:
- 사용자 입력으로 답변 받기
- 구현 간단 (10분)
- 비용 $0

**Layer 3 - Native Interactive**:
- 사용자가 웹 검색 후 입력
- 구현 간단 (10분)
- 비용 $0

**총 시간**: 20분

---

### 향후 구현 (선택)

**Layer 2 - External API**:
- OpenAI API 자동 호출
- 완전 자동화
- v7.3.0에서

**Layer 3 - SerpAPI**:
- 웹 검색 API
- 완전 자동화
- v7.3.0에서

---

## 🚀 구현 제안

**옵션 A: 즉시 구현 (20분)** ⭐
- Layer 2, 3 Native Interactive만
- 사용자 입력 기반
- 비용 $0, 간단

**옵션 B: 완전 구현 (60분)**
- Layer 2, 3 모든 모드
- Native + External + Scraping
- 완전 자동화 가능

**옵션 C: 나중에**
- v7.2.1은 현재 상태로
- v7.3.0에서 구현

---

어떤 옵션을 선택하시겠습니까?

**제 추천**: **옵션 A (20분, Native Interactive만)** - 빠르게 완성하고 v7.2.1 릴리즈!
