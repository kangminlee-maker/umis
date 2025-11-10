# UMIS 전역 설정 설정 가이드

**버전**: v7.6.2  
**업데이트**: 2025-11-10  
**중요도**: ⭐⭐⭐⭐⭐

---

## 🎯 핵심 개념

**`.env` 파일 하나로 UMIS 전체 시스템의 LLM 모드를 제어합니다!**

---

## 📝 설정 파일: `.env`

### 위치
- 프로젝트 루트: `/path/to/umis/.env`

### 전역 설정 설정 (3개)

```bash
# ========================================
# UMIS 전역 설정 (전체 시스템 적용!)
# ========================================

# 1. UMIS 시스템 전체 모드
UMIS_MODE=native

# 2. 웹 검색 모드 (Guestimation Layer 3)
UMIS_WEB_SEARCH_MODE=native

# 3. Interactive 모드
UMIS_INTERACTIVE=false
```

---

## 🔧 UMIS_MODE (시스템 전역)

### 의미

**UMIS 전체 시스템의 LLM을 제어하는 마스터 스위치**

### 옵션

#### `UMIS_MODE=native` (기본, 권장) ⭐

**의미**: Cursor Agent LLM 사용

**영향 범위** (전체!):
- ✅ Explorer: 가설 생성 → Cursor LLM
- ✅ Quantifier: 계산 및 추정 → Cursor LLM
- ✅ Validator: 데이터 검증 → Cursor LLM
- ✅ Observer: 시장 분석 → Cursor LLM
- ✅ Guestimation Layer 2 → Cursor LLM
- ✅ 모든 LLM 호출 → Cursor LLM

**특징**:
- 비용: $0
- 품질: 최고 (Claude Sonnet 4.5, GPT-4o 등)
- 자동화: 불가 (대화형)

---

#### `UMIS_MODE=external`

**의미**: External API LLM 사용 (OpenAI, Anthropic)

**영향 범위** (전체!):
- ✅ Explorer: 가설 생성 → OpenAI API
- ✅ Quantifier: 계산 및 추정 → OpenAI API
- ✅ Validator: 데이터 검증 → OpenAI API
- ✅ Observer: 시장 분석 → OpenAI API
- ✅ Guestimation Layer 2 → OpenAI API
- ✅ 모든 LLM 호출 → OpenAI API

**특징**:
- 비용: $3-10/1M tokens
- 품질: 중상 (GPT-4 Turbo, GPT-4o 등)
- 자동화: 가능 (Python 스크립트 독립 실행)

---

## 🔍 UMIS_WEB_SEARCH_MODE (Layer 3 전용)

### 옵션

#### `UMIS_WEB_SEARCH_MODE=native` (기본)
- 사용자가 직접 웹 검색
- 비용: $0

#### `UMIS_WEB_SEARCH_MODE=api`
- SerpAPI 자동 호출
- 비용: 월 100회 무료, 초과 시 $0.01/검색

#### `UMIS_WEB_SEARCH_MODE=skip`
- Layer 3 건너뛰기

---

## 💡 UMIS_INTERACTIVE (사용자 입력)

### 옵션

#### `UMIS_INTERACTIVE=false` (기본)
- 안내만 하고 자동으로 다음 레이어
- 자동 워크플로우

#### `UMIS_INTERACTIVE=true`
- 사용자 입력 프롬프트 표시
- Layer 2, 3에서 값 직접 입력 가능

---

## 📋 설정 시나리오

### 시나리오 1: 일반 사용자 (권장) ⭐

**.env**:
```bash
UMIS_MODE=native
UMIS_WEB_SEARCH_MODE=native
UMIS_INTERACTIVE=false
```

**효과**:
- 모든 Agent가 Cursor LLM 사용
- 비용: $0
- 품질: 최고
- Guestimation: Layer 1, 4-8만 자동 사용

---

### 시나리오 2: Interactive 사용자

**.env**:
```bash
UMIS_MODE=native
UMIS_WEB_SEARCH_MODE=native
UMIS_INTERACTIVE=true  # ← 활성화!
```

**효과**:
- Layer 2, 3에서 사용자 입력 프롬프트
- 직접 값 확인 후 입력
- 더 정확한 결과

---

### 시나리오 3: 자동화 (배치 처리)

**.env**:
```bash
UMIS_MODE=external       # ← External!
UMIS_WEB_SEARCH_MODE=api # ← API!
UMIS_INTERACTIVE=false

# API 키 필수
OPENAI_API_KEY=sk-proj-...
SERPAPI_KEY=your-key
```

**효과**:
- 완전 자동화
- Python 스크립트 독립 실행
- 100개 시장 동시 분석 가능
- 비용: 발생

---

## 🔄 모드 변경 방법

### 1. `.env` 파일 편집

```bash
# .env 파일 열기
vim .env

# 또는
code .env
```

### 2. UMIS_MODE 변경

```bash
# Before
UMIS_MODE=native

# After (자동화 필요 시)
UMIS_MODE=external
```

### 3. 저장 후 재시작

```bash
# Python 프로세스 재시작
# 또는 Jupyter 커널 재시작
```

### 4. 확인

```python
import umis_rag

print(f"현재 모드: {umis_rag.UMIS_MODE}")
# → 'external' 출력되면 성공!
```

---

## 💻 코드에서 사용

### 자동으로 전역 설정 적용

```python
from umis_rag.utils.multilayer_guestimation import MultiLayerGuestimation

# .env의 UMIS_MODE 자동 사용!
estimator = MultiLayerGuestimation()

result = estimator.estimate("한국 인구는?")
# → UMIS_MODE='native': Cursor LLM 안내
# → UMIS_MODE='external': OpenAI API 호출
```

### Explorer, Quantifier 등 모든 Agent

```python
from umis_rag.agents.explorer import ExplorerRAG
from umis_rag.agents.quantifier import QuantifierRAG

# 모두 동일한 UMIS_MODE 사용!
explorer = ExplorerRAG()
quantifier = QuantifierRAG()

# UMIS_MODE='native' → Cursor LLM
# UMIS_MODE='external' → OpenAI API
```

---

## 🎯 영향 범위 (UMIS_MODE)

### Native Mode (`UMIS_MODE=native`)

**모든 곳에서**:
- Explorer 가설 생성 → Cursor에서 직접
- Quantifier 계산 → Cursor에서 직접
- Validator 검증 → Cursor에서 직접
- Guestimation Layer 2 → 안내만 (또는 Interactive 입력)

---

### External Mode (`UMIS_MODE=external`)

**모든 곳에서**:
- Explorer 가설 생성 → OpenAI API 호출
- Quantifier 계산 → OpenAI API 호출
- Validator 검증 → OpenAI API 호출
- Guestimation Layer 2 → OpenAI API 호출

---

## 📊 비용 비교 (100회 작업)

| 모드 | 비용 | 품질 | 자동화 |
|------|------|------|--------|
| **native** | $0 | ⭐⭐⭐⭐⭐ | ❌ |
| **external** | ~$300-1,000 | ⭐⭐⭐⭐ | ✅ |

**권장**: Native (99% 경우 충분)

---

## 🚨 주의사항

### External Mode 사용 시

1. **API 키 필수**
   ```bash
   OPENAI_API_KEY=sk-proj-...
   ```

2. **비용 발생**
   - GPT-4 Turbo: ~$10/1M tokens
   - GPT-4o: ~$5/1M tokens
   - GPT-4o-mini: ~$0.15/1M tokens

3. **모니터링 권장**
   - OpenAI 대시보드에서 사용량 확인
   - 예산 제한 설정

---

## 📖 설정 파일 구조

### `.env` (전역 설정) ⭐

**역할**: UMIS 전체 시스템 모드 제어

```bash
UMIS_MODE=native           # ← 여기만 바꾸면 전체 변경!
UMIS_WEB_SEARCH_MODE=native
UMIS_INTERACTIVE=false
```

### `config/multilayer_config.yaml` (상세 설정)

**역할**: Layer별 세부 동작 제어

```yaml
layer_3_web_search:
  api:
    results_count: 20      # 웹 검색 결과 개수
  
  consensus_extraction:
    similarity_based:
      threshold: 0.7       # 유사도 임계값
```

**차이점**:
- `.env`: 모드 선택 (native vs external)
- `YAML`: 선택된 모드의 세부 동작

---

## 🎓 Best Practice

### 1. 기본은 Native

대부분의 경우:
```bash
UMIS_MODE=native
```

### 2. 자동화 필요 시만 External

100개 이상 대량 분석:
```bash
UMIS_MODE=external
```

### 3. 한 곳에서만 변경

❌ 잘못:
```python
# 코드에서 직접 변경
estimator = MultiLayerGuestimation(config_override={'llm_mode': 'external'})
```

✅ 올바름:
```bash
# .env에서 변경
UMIS_MODE=external  # ← 여기만!
```

---

## 🔍 현재 모드 확인

```python
import umis_rag

print(f"UMIS_MODE: {umis_rag.UMIS_MODE}")
print(f"WEB_SEARCH: {umis_rag.UMIS_WEB_SEARCH_MODE}")
print(f"INTERACTIVE: {umis_rag.UMIS_INTERACTIVE}")
```

---

**작성**: 2025-11-05  
**상태**: ✅ Production Ready  
**중요**: 모든 UMIS 사용자 필독!

