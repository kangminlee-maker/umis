# UMIS 설정 아키텍처 (최종 정리)

**작성일**: 2025-11-05 21:00 KST  
**버전**: v7.2.1  
**상태**: ✅ 최종 확정

---

## 🎯 설정 파일 역할 분담 (3계층)

### 1️⃣ `.env` - UMIS 전역 설정 (시스템 전체)

**역할**: **모든 Agent의 LLM 제공자 선택**

```bash
# LLM 제공자 설정 (전체 시스템 적용)
UMIS_MODE=native
# 옵션: native (Cursor LLM) / external (OpenAI API)

# 영향 범위:
#   - Explorer 가설 생성
#   - Quantifier 계산 및 추정
#   - Validator 데이터 검증
#   - Observer 시장 분석
#   - Guestimation Layer 2
#   → 모든 LLM 호출
```

**변경 방법**:
```bash
vim .env

# UMIS_MODE=native → external로 변경
# → 전체 시스템이 OpenAI API로 전환!
```

---

### 2️⃣ `config/multilayer_config.yaml` - Guestimation 전용

**역할**: **Multi-Layer Guestimation 세부 설정**

```yaml
# 웹 검색 모드 (Layer 3 전용)
web_search_mode: "native"
# 옵션:
#   native   - Cursor web_search tool (브라우저 검색)
#   api      - SerpAPI 자동 호출
#   scraping - BeautifulSoup 스크래핑
#   skip     - Layer 3 건너뛰기

# Interactive 모드 (Layer 2, 3 전용)
interactive_mode: false
# true:  사용자 입력 프롬프트
# false: 안내만

# Layer 3 상세 설정
layer_3_web_search:
  api:
    results_count: 20        # 검색 결과 개수
  
  consensus_extraction:
    similarity_based:
      threshold: 0.7         # 유사도 임계값
```

**변경 방법**:
```bash
vim config/multilayer_config.yaml

# web_search_mode: native → api로 변경
# → Layer 3만 SerpAPI로 전환
```

---

### 3️⃣ `config/runtime.yaml` - UMIS 실행 모드

**역할**: **UMIS 시스템 실행 환경**

```yaml
# RAG 모드
mode: hybrid  # yaml_only / hybrid / rag_full

# 환경
environment: development  # development / production

# 레이어 활성화
layers:
  vector: true   # Vector RAG
  graph: true    # Knowledge Graph
  memory: true   # Guardian Memory
```

**변경 방법**:
```bash
vim config/runtime.yaml

# mode: hybrid → rag_full로 변경
# → Graph, Memory 모두 활성화
```

---

## 📊 설정 계층 구조

```
┌─────────────────────────────────────────┐
│  .env (UMIS 전역)                       │
│  UMIS_MODE=native                       │
│  ↓                                      │
│  영향: 모든 Agent의 모든 LLM 호출        │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  config/multilayer_config.yaml          │
│  (Guestimation 전용)                    │
│  - web_search_mode: native              │
│  - interactive_mode: false              │
│  - Layer 3, 2 세부 설정                 │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  config/runtime.yaml                    │
│  (UMIS 실행 환경)                        │
│  - mode: hybrid                         │
│  - environment: development             │
└─────────────────────────────────────────┘
```

---

## 🔍 웹 검색 모드 상세 (Layer 3)

### Native Mode (Cursor web_search tool) ⭐

**의미**: Cursor의 내장 브라우저 검색 tool 사용

**작동**:
```python
# Cursor에서 자동으로:
# 1. 질문을 웹 검색
# 2. 상위 20개 결과 수집
# 3. 공통값 추출
# 4. 반환
```

**설정**:
```yaml
web_search_mode: "native"

native:
  use_cursor_tool: true
  cursor_tool_params:
    max_results: 20
```

---

### API Mode (SerpAPI)

**의미**: SerpAPI를 통한 자동 웹 검색

**작동**:
```python
# SerpAPI 호출:
# 1. requests.get('serpapi.com/search', params={'q': question})
# 2. 상위 20개 organic_results 파싱
# 3. 숫자 추출 → 공통값 계산
```

**설정**:
```yaml
web_search_mode: "api"

api:
  enabled: true  # ← 활성화 필요
  serpapi:
    results_count: 20
```

**.env 필요**:
```bash
SERPAPI_KEY=your-key
```

---

### Scraping Mode (BeautifulSoup)

**의미**: 직접 HTML 파싱

**작동**:
```python
# requests + BeautifulSoup:
# 1. requests.get('google.com/search?q=...')
# 2. BeautifulSoup(html, 'html.parser')
# 3. CSS selector로 snippet 추출
```

**설정**:
```yaml
web_search_mode: "scraping"

scraping:
  enabled: true
  search_engines:
    - name: "Google"
      snippet_selector: "div.VwiC3b"
```

**주의**: 불안정, robots.txt 위반 가능성

---

### Skip Mode

**의미**: Layer 3 건너뛰기

```yaml
web_search_mode: "skip"
```

---

## 🎮 Interactive 모드

### 정의

**Guestimation Layer 2, 3에서 사용자 입력 프롬프트 활성화**

### Interactive = false (기본)

**작동**:
```python
result = estimator.estimate("한국 인구는?")

# Layer 2: "💡 Cursor에서 LLM에게 질문하세요" (안내만)
# → Layer 3으로 자동 넘어감

# Layer 3: "💡 웹 검색 권장" (안내만)
# → Layer 4로 자동 넘어감
```

---

### Interactive = true

**작동**:
```python
result = estimator.estimate("한국 인구는?")

# 출력:
# ❓ LLM에게 질문하세요: 한국 인구는?
#    답변 (숫자만 입력, 건너뛰려면 Enter): 5200만
#
# → 52,000,000 반환! (Layer 2에서)
```

**설정**:
```yaml
# config/multilayer_config.yaml
interactive_mode: true  # ← 활성화
```

---

## 🎯 최종 정리

### 전역 설정 (.env) - 1개만!

```bash
UMIS_MODE=native  # LLM 제공자 (전체 시스템)
```

**범위**: 모든 Agent, 모든 LLM 호출

---

### Guestimation 설정 (YAML) - 2개

```yaml
web_search_mode: "native"      # Layer 3
interactive_mode: false        # Layer 2, 3
```

**범위**: Guestimation 전용

---

### UMIS 실행 설정 (runtime.yaml)

```yaml
mode: hybrid              # RAG 모드
environment: development  # 환경
```

**범위**: UMIS 시스템 실행 환경

---

## 📝 사용자 가이드

### 시나리오 1: 기본 사용 (권장)

**.env**:
```bash
UMIS_MODE=native
```

**효과**:
- 모든 Agent가 Cursor LLM 사용
- 비용: $0
- 품질: 최고

---

### 시나리오 2: 완전 자동화

**.env**:
```bash
UMIS_MODE=external
OPENAI_API_KEY=sk-proj-...
SERPAPI_KEY=your-key
```

**config/multilayer_config.yaml**:
```yaml
web_search_mode: "api"

layer_2_llm:
  external:
    enabled: true

layer_3_web_search:
  api:
    enabled: true
```

**효과**:
- 모든 LLM: OpenAI API
- Layer 3: SerpAPI
- 완전 자동화

---

**작성**: 2025-11-05  
**최종 확정**: ✅

