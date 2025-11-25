# LLM Mode 리팩토링 완료 보고서 (v7.8.1)

**날짜**: 2025-11-25  
**버전**: v7.8.1  
**작업**: `umis_mode` → `llm_mode` 변경 및 단순화

---

## 📋 요약

UMIS의 LLM 모드 설정을 더 직관적이고 단순하게 개선했습니다.

### 주요 변경사항

1. **환경변수 명칭 변경**: `UMIS_MODE` → `LLM_MODE`
2. **설정 필드 변경**: `settings.umis_mode` → `settings.llm_mode`
3. **모드 값 단순화**: `native`/`external` → 직접 모델명 사용 (`cursor`, `gpt-4o-mini` 등)
4. **함수명 개선**: `is_native_mode()` → `is_cursor_mode()`
5. **Mixin 이름 변경**: `NativeModeMixin` → `CursorModeMixin`

---

## 🔄 변경 세부 사항

### 1. 환경변수 (`env.template`)

**Before**:
```bash
UMIS_MODE=native  # or external
```

**After**:
```bash
LLM_MODE=cursor  # or gpt-4o-mini, o1-mini, claude-3-sonnet 등
```

**장점**:
- 더 직관적: "LLM 모드"가 "UMIS 모드"보다 명확
- 직접적: 사용할 모델을 직접 지정
- 확장 가능: 새로운 모델 추가 시 명시적

---

### 2. 코드 변경 파일 목록

| 파일 | 변경 내용 | 상태 |
|------|-----------|------|
| `umis_rag/core/llm_provider.py` | umis_mode → llm_mode, native → cursor, 함수명 변경 | ✅ |
| `umis_rag/core/config.py` | umis_mode → llm_mode (Pydantic 설정) | ✅ |
| `umis_rag/__init__.py` | UMIS_MODE → LLM_MODE, 환경변수 UMIS_MODE → LLM_MODE | ✅ |
| `umis_rag/agents/explorer.py` | settings.umis_mode → settings.llm_mode | ✅ |
| `umis_rag/utils/fermi_model_search.py` | umis_rag.UMIS_MODE → umis_rag.LLM_MODE, native → cursor | ✅ |
| `env.template` | UMIS_MODE → LLM_MODE, 설명 개선 | ✅ |
| `config/model_configs.yaml` | cursor-native → cursor (이미 적용됨) | ✅ |

---

### 3. API 변경사항

#### LLMProvider 클래스

**Before**:
```python
LLMProvider.is_native_mode()  # → True/False
LLMProvider.is_external_mode()  # → True/False
```

**After**:
```python
LLMProvider.is_cursor_mode()  # → True/False
LLMProvider.is_external_mode()  # → True/False
```

#### Settings

**Before**:
```python
from umis_rag.core.config import settings

print(settings.umis_mode)  # 'native' or 'external'
```

**After**:
```python
from umis_rag.core.config import settings

print(settings.llm_mode)  # 'cursor' or 'gpt-4o-mini' or 'o1-mini' 등
```

#### Global Variable

**Before**:
```python
from umis_rag import UMIS_MODE

if UMIS_MODE == 'native':
    ...
```

**After**:
```python
from umis_rag import LLM_MODE

if LLM_MODE == 'cursor':
    ...
```

---

### 4. Mixin 클래스 변경

**Before**:
```python
from umis_rag.core.llm_provider import NativeModeMixin

class MyAgent(NativeModeMixin):
    def process(self):
        if self.is_native():
            return self.prepare_native_output(...)
```

**After**:
```python
from umis_rag.core.llm_provider import CursorModeMixin

class MyAgent(CursorModeMixin):
    def process(self):
        if self.is_cursor():
            return self.prepare_cursor_output(...)
```

---

## ✅ 테스트 결과

### 1. 기본 import 테스트
```bash
$ python3 -c "import os; os.environ['LLM_MODE'] = 'cursor'; from umis_rag import LLM_MODE; print(f'✅ LLM_MODE: {LLM_MODE}')"
✅ LLM_MODE: cursor
```

### 2. Settings 테스트
```bash
$ python3 -c "import os; os.environ['LLM_MODE'] = 'gpt-4o-mini'; from umis_rag.core.config import settings; print(f'✅ settings.llm_mode: {settings.llm_mode}')"
✅ settings.llm_mode: gpt-4o-mini
```

### 3. LLMProvider 함수 테스트
```bash
$ python3 -c "import os; os.environ['LLM_MODE'] = 'cursor'; from umis_rag.core.llm_provider import LLMProvider; print(f'✅ is_cursor_mode: {LLMProvider.is_cursor_mode()}'); print(f'✅ is_external_mode: {LLMProvider.is_external_mode()}')"
✅ is_cursor_mode: True
✅ is_external_mode: False
```

---

## 📝 사용 예시

### 1. Cursor 모드 (무료, 대화형)

**.env**:
```bash
LLM_MODE=cursor
```

**결과**:
- RAG 검색만 수행
- Cursor Composer/Chat에서 결과 활용
- 비용: $0

### 2. External LLM 모드 (자동화)

**.env**:
```bash
LLM_MODE=gpt-4o-mini
```

**결과**:
- RAG 검색 + API 호출
- 완성된 결과 자동 생성
- 비용: 토큰당 과금

---

## 🎯 장점

### 1. 직관성 향상
- ❌ Before: `UMIS_MODE=native` (무슨 의미?)
- ✅ After: `LLM_MODE=cursor` (명확!)

### 2. 확장성 개선
- ❌ Before: `native`/`external` 이분법
- ✅ After: 무한 확장 가능 (`cursor`, `gpt-4o-mini`, `o1-mini`, `claude-3-sonnet` 등)

### 3. One Source of Truth
- ✅ `settings.llm_mode`가 유일한 진실의 원천
- ✅ 모든 코드에서 일관되게 사용
- ✅ `native`/`external` 분기 제거

---

## 🚀 향후 작업

### 완료됨 ✅
1. ✅ 환경변수 변경 (`UMIS_MODE` → `LLM_MODE`)
2. ✅ Settings 변경 (`umis_mode` → `llm_mode`)
3. ✅ 함수명 변경 (`is_native_mode` → `is_cursor_mode`)
4. ✅ 테스트 및 검증
5. ✅ 문서화

### 다음 단계 (Phase 3/4 개선)
1. ⏳ Phase 3 External API 구현 (우선순위 1)
2. ⏳ Phase 4 파싱 에러 디버깅 (우선순위 2)
3. ⏳ 수식 실행 문제 해결 (우선순위 3)
4. ⏳ 순환 의존성 처리 개선 (우선순위 4)

---

## 📚 관련 문서

- `env.template`: 환경변수 설명
- `config/model_configs.yaml`: 모델별 설정
- `umis_rag/core/llm_provider.py`: LLM Provider 구현
- `umis_rag/core/config.py`: Settings 정의

---

**문서 종료**


