# LLM Mode 리팩토링 (v7.8.1)

## 개요

**목표**: LLM 모드 설정을 직관적이고 유지보수하기 쉽게 개선

**날짜**: 2025-11-24

**버전**: v7.8.1

---

## 주요 개선 사항

### 1. 명칭 통일: `umis_mode` → `llm_mode` ✅

**이전**:
```python
# config.py
umis_mode: str = "native"  # "umis_mode"는 직관적이지 않음

# 사용
settings.umis_mode
```

**개선 후**:
```python
# config.py
llm_mode: str = "cursor"  # "llm_mode"가 훨씬 직관적

# 사용
settings.llm_mode  # 일관성 있고 명확
```

**효과**:
- ✅ 직관적인 명칭
- ✅ 다른 LLM 관련 설정과 일관성
- ✅ 코드 가독성 향상

---

### 2. One Source of Truth ✅

**이전**:
```python
# 여러 곳에서 분산 읽기
self.llm_mode = getattr(settings, 'llm_mode', 'native')
self.llm_mode = os.environ.get('UMIS_MODE', 'native')
```

**개선 후**:
```python
# 단일 출처 (config.py)
from umis_rag.core.config import settings
self.llm_mode = settings.llm_mode  # One source of truth
```

**효과**:
- ✅ 단일 출처에서 모든 LLM 모드 읽기
- ✅ 설정 변경 시 일관성 보장
- ✅ 디버깅 용이

**적용 위치**:
- `umis_rag/agents/estimator/estimator.py` (Line 88)
- `umis_rag/agents/estimator/phase4_fermi.py` (Line 495)
- `umis_rag/agents/estimator/sources/value.py` (Line 109)

---

### 3. "native"/"external" 개념 제거 → 직접 모델명 사용 ✅

**이전**:
```bash
# .env
UMIS_MODE=native      # 또는 external
```

```python
if self.llm_mode == 'native':
    # Cursor AI 사용
elif self.llm_mode == 'external':
    # OpenAI API 사용
```

**개선 후**:
```bash
# .env
LLM_MODE=cursor          # Cursor AI
LLM_MODE=gpt-4o-mini     # OpenAI GPT-4o Mini
LLM_MODE=o1-mini         # OpenAI o1-mini
LLM_MODE=claude-3-sonnet # Anthropic Claude
```

```python
if self.llm_mode == 'cursor':
    # Cursor AI 사용 (무료, 대화형)
else:
    # External API 사용 (self.llm_mode를 모델로)
    model_name = self.llm_mode
```

**효과**:
- ✅ "native/external" 추상화 제거
- ✅ 직관적인 모델 선택
- ✅ `model_configs.yaml`과 직접 연계
- ✅ 복잡도 감소

---

## 변경 파일 목록

### 핵심 설정 파일

1. **`umis_rag/core/config.py`**
   - `umis_mode` → `llm_mode` 필드명 변경
   - 기본값: `"cursor"`
   - 코멘트 개선: 직접 모델명 사용 안내

2. **`config/model_configs.yaml`**
   - `cursor-native` → `cursor` 키 변경
   - 설명 개선: Cursor AI 사용법 명확화

3. **`env.template`**
   - `UMIS_MODE` → `LLM_MODE` 변경
   - 예시 값 변경: `native` → `cursor`
   - 사용 가능 모델 목록 추가 (cursor, gpt-4o-mini, o1-mini 등)

### Python 코드

4. **`umis_rag/agents/estimator/estimator.py`**
   - Line 88: `settings.umis_mode` → `settings.llm_mode`
   - One source of truth 적용

5. **`umis_rag/agents/estimator/phase4_fermi.py`**
   - Line 495: `settings.umis_mode` → `settings.llm_mode`
   - Line 511-519: `if self.llm_mode == 'external'` → `if self.llm_mode != 'cursor'`
   - Line 923-940: `if self.llm_mode == 'native'` → `if self.llm_mode == 'cursor'`
   - Line 945: `elif self.llm_mode == 'external'` → `else`

6. **`umis_rag/agents/estimator/sources/value.py`**
   - Line 109: `if self.llm_mode == "native"` → `if self.llm_mode == "cursor"`
   - Line 123: `else` (External API)

7. **`umis_rag/core/model_configs.py`**
   - Line 번호: `prefix_map`의 `'cursor': 'cursor-native'` → `'cursor': 'cursor'`

### 테스트 파일

8. **`tests/test_estimator_comprehensive.py`**
   - Line 16: `os.environ['UMIS_MODE'] = 'external'` → `os.environ['LLM_MODE'] = 'gpt-4o-mini'`
   - Line 400-412: `UMIS_MODE` → `LLM_MODE` 전역 변경

---

## 사용 예시

### Cursor AI 모드 (무료, 대화형)

```bash
# .env
LLM_MODE=cursor
```

```python
from umis_rag.agents.estimator import EstimatorRAG

estimator = EstimatorRAG()
# estimator.llm_mode = "cursor"

# Phase 4에서 Cursor AI instruction 생성
result = estimator.estimate("한국 커피 전문점 수는?")
# → Cursor AI가 대화 컨텍스트에서 직접 응답
```

### External API 모드 (OpenAI GPT-4o Mini)

```bash
# .env
LLM_MODE=gpt-4o-mini
OPENAI_API_KEY=sk-xxx
```

```python
from umis_rag.agents.estimator import EstimatorRAG

estimator = EstimatorRAG()
# estimator.llm_mode = "gpt-4o-mini"

# Phase 4에서 OpenAI API 호출
result = estimator.estimate("한국 커피 전문점 수는?")
# → OpenAI GPT-4o Mini API 호출
```

### External API 모드 (OpenAI o1-mini)

```bash
# .env
LLM_MODE=o1-mini
OPENAI_API_KEY=sk-xxx
```

```python
from umis_rag.agents.estimator import EstimatorRAG

estimator = EstimatorRAG()
# estimator.llm_mode = "o1-mini"

# Phase 4에서 OpenAI o1-mini API 호출
result = estimator.estimate("한국 전체 사업자 수는?")
# → OpenAI o1-mini API 호출 (Phase 4 권장 모델)
```

---

## 검증 결과

### Cursor AI 모드

```bash
$ python3 -c "
import os
os.environ['LLM_MODE'] = 'cursor'

from umis_rag.agents.estimator import EstimatorRAG
estimator = EstimatorRAG()
print(f'LLM Mode: {estimator.llm_mode}')
"

# 출력:
# 📌 LLM Mode: cursor
# ✅ Cursor AI Mode (비용 $0)
# ✅ Phase 4 (Fermi Decomposition) 로드
# LLM Mode: cursor
```

### External API 모드

```bash
$ python3 -c "
import os
os.environ['LLM_MODE'] = 'gpt-4o-mini'

from umis_rag.agents.estimator import EstimatorRAG
estimator = EstimatorRAG()
print(f'LLM Mode: {estimator.llm_mode}')
"

# 출력:
# 📌 LLM Mode: gpt-4o-mini
# ✅ External LLM (OpenAI API) 준비: gpt-4o-mini
# ✅ Phase 4 (Fermi Decomposition) 로드
# LLM Mode: gpt-4o-mini
```

---

## 마이그레이션 가이드

### 기존 사용자

**이전 설정**:
```bash
# .env
UMIS_MODE=native
```

**새로운 설정**:
```bash
# .env
LLM_MODE=cursor
```

**이전 설정**:
```bash
# .env
UMIS_MODE=external
```

**새로운 설정**:
```bash
# .env
LLM_MODE=gpt-4o-mini  # 또는 o1-mini, claude-3-sonnet 등
```

### 코드 변경 불필요

- ✅ 사용자 코드는 변경 불필요
- ✅ `.env` 파일만 업데이트
- ✅ 기존 기능 완전 호환

---

## 주요 이점

### 1. 직관성
- ✅ "native/external" 추상화 제거
- ✅ 모델명 직접 사용 → 명확한 의도

### 2. 단순성
- ✅ 조건문 간소화: `if llm_mode != 'cursor'`
- ✅ 설정 계층 감소

### 3. 확장성
- ✅ 새 모델 추가 시 `model_configs.yaml`에만 정의
- ✅ 코드 변경 불필요

### 4. 일관성
- ✅ One source of truth: `settings.llm_mode`
- ✅ 전역 일관성 보장

---

## 향후 계획

### 1. 문서 업데이트
- [ ] `NATIVE_MODE_GUIDE.md` → `CURSOR_AI_GUIDE.md`로 개명
- [ ] `umis.yaml` 및 `umis_core.yaml` 업데이트
- [ ] API 문서 갱신

### 2. 추가 개선
- [ ] Anthropic Claude 모델 지원 확대
- [ ] 모델별 성능 벤치마크 문서화

---

## 참고

- **설정 우선순위**: `LLM_MODE` 환경변수 → `config.py` 기본값
- **One source of truth**: `umis_rag/core/config.py:Settings.llm_mode`
- **모델 정의**: `config/model_configs.yaml`
- **버전**: v7.8.1

---

**작성자**: AI Assistant  
**검토**: Kangmin  
**날짜**: 2025-11-24





