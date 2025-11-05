# Multi-Layer Guestimation 사용 예시

**버전**: v2.1  
**업데이트**: 2025-11-05  
**상태**: ✅ Production Ready

---

## 🎯 글로벌 설정으로 모드 변경

### 설정 파일 위치

**`config/multilayer_config.yaml`**

이 파일 하나만 수정하면 **UMIS 전체 시스템**에 반영됩니다!

---

## 📝 설정 변경 방법

### 1. 기본 설정 (Native Mode, 권장)

**`config/multilayer_config.yaml`**:
```yaml
global_modes:
  llm_mode: "native"         # ← 여기만 수정!
  web_search_mode: "native"  # ← 여기만 수정!
  interactive_mode: false
```

**효과**:
- Layer 2 (LLM): Native LLM 사용 안내 (자동 실행 안 함)
- Layer 3 (웹): 웹 검색 안내 (자동 실행 안 함)
- 비용: $0
- 품질: 최고

---

### 2. Interactive 모드 (사용자 입력)

**`config/multilayer_config.yaml`**:
```yaml
global_modes:
  llm_mode: "native"
  web_search_mode: "native"
  interactive_mode: true     # ← true로 변경!
```

**효과**:
```python
result = estimator.estimate("한국 인구는?")

# 출력:
# ❓ LLM에게 질문하세요: 한국 인구는?
#    (Cursor Composer/Chat에서 질문 후 답변만 입력)
#    답변 (숫자만 입력, 건너뛰려면 Enter): 5200만
#
# → 52,000,000 반환!
```

---

### 3. 완전 자동화 (External Mode)

**`config/multilayer_config.yaml`**:
```yaml
global_modes:
  llm_mode: "external"       # ← external로 변경!
  web_search_mode: "api"     # ← api로 변경!
  interactive_mode: false
```

**.env 파일 추가 필요**:
```bash
OPENAI_API_KEY=sk-proj-...
SERPAPI_KEY=your-serpapi-key
```

**효과**:
- Layer 2: OpenAI API 자동 호출 (GPT-4o-mini)
- Layer 3: SerpAPI 자동 호출 (상위 20개 검색)
- 비용: ~$0.001/질문 (LLM) + ~$0.01/검색 (월 100회 무료)
- 완전 자동화

---

## 🔧 고급 설정

### Layer 3 공통값 추출 조정

**`config/multilayer_config.yaml`**:
```yaml
layer_3_web_search:
  api:
    serpapi:
      results_count: 30      # 20 → 30개로 증가
  
  consensus_extraction:
    similarity_based:
      threshold: 0.8         # 0.7 → 0.8로 상향 (더 엄격)
    
    outlier_removal:
      threshold: 2.0         # 1.5 → 2.0 (이상치 기준 완화)
    
    clustering:
      min_cluster_size: 5    # 3 → 5 (더 엄격)
```

**효과**:
- 더 많은 검색 결과 (30개)
- 유사도 0.8 이상만 클러스터링 (더 엄격)
- 최소 클러스터 크기 5개

---

### Layer 2 LLM 모델 변경

**`config/multilayer_config.yaml`**:
```yaml
layer_2_llm:
  external:
    model: "gpt-4o"          # gpt-4o-mini → gpt-4o (고품질)
    max_tokens: 100          # 50 → 100 (더 긴 답변)
```

**효과**:
- 더 정확한 LLM 답변
- 비용 약간 증가 (~$0.005/질문)

---

## 💻 코드에서 사용

### 자동으로 글로벌 설정 사용

```python
from umis_rag.utils.multilayer_guestimation import MultiLayerGuestimation

# 자동으로 config/multilayer_config.yaml 로드!
estimator = MultiLayerGuestimation()

result = estimator.estimate("한국 인구는?")
# → global_modes에 따라 자동으로:
#    llm_mode='native' → Native LLM 안내
#    llm_mode='external' → OpenAI API 호출
```

### 일시적으로 설정 오버라이드

```python
# 글로벌 설정은 'native'지만, 이번만 'external' 사용
estimator = MultiLayerGuestimation(
    config_override={
        'llm_mode': 'external',
        'interactive_mode': True
    }
)

result = estimator.estimate("...")
# → 이번만 External API 사용
```

---

## 🧪 테스트 시나리오

### 시나리오 1: Native Interactive

**설정**:
```yaml
llm_mode: "native"
interactive_mode: true
```

**실행**:
```bash
python3 scripts/test_multilayer_guestimation.py
```

**프롬프트 나타남**:
```
❓ LLM에게 질문하세요: 한국 인구는?
   답변 (숫자만 입력): 5200만

✅ Layer 2: 사용자 입력 = 52,000,000
```

---

### 시나리오 2: External Automation

**설정**:
```yaml
llm_mode: "external"
web_search_mode: "api"

layer_2_llm:
  external:
    enabled: true           # ← 활성화!

layer_3_web_search:
  api:
    enabled: true           # ← 활성화!
```

**실행**:
```python
result = estimator.estimate("2024년 한국 GDP는?")

# 자동으로:
# Layer 1: 없음
# Layer 2: GPT-4o-mini API → "1.8조 달러" → 1.8 추출
# → 반환!
```

---

## 📊 모드별 비용/품질 비교

| 설정 | Layer 2 | Layer 3 | 비용 (100회) | 품질 |
|------|---------|---------|------------|------|
| **Native + Interactive=false** | 안내만 | 안내만 | $0 | N/A |
| **Native + Interactive=true** | 사용자 입력 | 사용자 입력 | $0 | ⭐⭐⭐⭐⭐ |
| **External API** | GPT-4o-mini | SerpAPI | ~$11 | ⭐⭐⭐⭐ |
| **Mixed** | External | Native | ~$0.10 | ⭐⭐⭐⭐ |

**권장**: Native + Interactive (사용자 확인, 비용 $0, 최고 품질)

---

## 🎓 Best Practice

### 1. 기본은 Native

대부분의 경우 Native Mode로 충분:
- Layer 1, 4-8이 대부분 해결
- Layer 2, 3 필요 시 사용자가 직접 확인
- 비용 $0, 품질 최고

### 2. 자동화 필요 시만 External

100개 이상 대량 분석:
```yaml
llm_mode: "external"
web_search_mode: "api"
```

### 3. 설정은 한 곳에서만

❌ 잘못된 방법:
```python
# 코드에서 직접 수정 (비권장)
estimator = MultiLayerGuestimation(
    config_override={'llm_mode': 'external'}
)
```

✅ 올바른 방법:
```yaml
# config/multilayer_config.yaml 수정 (권장)
global_modes:
  llm_mode: "external"  # ← 여기만!
```

---

## 📋 설정 체크리스트

### Native Mode 사용 시

- [ ] `config/multilayer_config.yaml`:
  ```yaml
  llm_mode: "native"
  web_search_mode: "native"
  ```
- [ ] `.env`: OPENAI_API_KEY (RAG용만 필요)
- [ ] 비용: $0 ✅

### External Mode 사용 시

- [ ] `config/multilayer_config.yaml`:
  ```yaml
  llm_mode: "external"
  web_search_mode: "api"
  
  layer_2_llm:
    external:
      enabled: true
  
  layer_3_web_search:
    api:
      enabled: true
  ```
- [ ] `.env`:
  ```bash
  OPENAI_API_KEY=sk-proj-...
  SERPAPI_KEY=your-key
  ```
- [ ] 비용: 발생 (추적 권장)

---

## 🔍 설정 디버깅

### 현재 설정 확인

```python
from umis_rag.core.multilayer_config import get_multilayer_config

config = get_multilayer_config()
modes = config.get_global_modes()

print(f"LLM Mode: {modes.llm_mode}")
print(f"Web Search Mode: {modes.web_search_mode}")
print(f"Interactive: {modes.interactive_mode}")
```

### 설정 변경 후 재시작

설정 파일 수정 후:
1. Python 프로세스 재시작
2. 또는 설정 리로드:
   ```python
   config._config = None
   config._load_config()
   ```

---

**작성**: 2025-11-05  
**버전**: v2.1  
**상태**: ✅ Production Ready

