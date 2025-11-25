# Native/External LLM 분기 레거시 제거 분석
**작성일**: 2025-11-23  
**버전**: v7.8.1  
**목적**: Phase 0-4 전체에서 native/external 분기 처리 레거시 완전 제거

---

## 📋 요약

Phase 0-4에서 `llm_mode == "native"` / `llm_mode == "external"` 분기 로직이 남아있어 v7.8.1의 "LLM Mode 통합" 철학과 충돌합니다.

### v7.8.1 통합 철학
- **이전**: `native` (Cursor AI) vs `external` (OpenAI API) 명시적 분기
- **현재**: `llm_mode` 값만 존재 (`cursor`, `gpt-4o-mini`, `o1-mini` 등)
- **목표**: 분기 없이 `api_type` 기반 디스패치로 통일

---

## 🔍 현재 상황 분석

### 1. Phase 0 (Literal)
- **파일**: `phase0_literal.py` (존재하지 않음)
- **상태**: ✅ 분기 없음 (프로젝트 데이터만 사용)

### 2. Phase 1 (Direct RAG)
- **파일**: `phase1_direct_rag.py`
- **상태**: ✅ 분기 없음 (RAG 검색만 사용)

### 3. Phase 2 (Validator Search)
- **파일**: `phase2_validator_search_enhanced.py`
- **상태**: ✅ 분기 없음 (Validator RAG만 사용)

### 4. Phase 3 (Guestimation)
- **파일**: `phase3_guestimation.py`
- **상태**: ✅ 분기 없음 (Source Collector가 처리)
- **위임**: `sources/value.py`의 `AIAugmentedEstimationSource`

### 5. Phase 4 (Fermi Decomposition)
- **파일**: `phase4_fermi.py`
- **상태**: ✅ 분기 없음 (v7.8.1에서 통합됨)
- **로직**: `_generate_llm_models` 단일 메서드, `api_type` 디스패치

---

## ⚠️ 레거시 발견 위치

### 🔴 1. `boundary_validator.py` (Lines 611-619)
**문제**: `native`/`external` 명시적 분기

```python
def _llm_boundary_check(...):
    """
    LLM 기반 Boundary 검증 (비정형 사고)
    
    Native Mode: Cursor가 직접 판단
    External Mode: GPT API 호출
    """
    if self.llm_mode == "native":
        # Native Mode: 템플릿 기반 (빠름, 비용 $0)
        return self._native_boundary_check(question, value, unit, context)
    
    elif self.llm_mode == "external" and self.llm_client:
        # External Mode: GPT 호출 (정교, 비용 $0.001)
        return self._external_boundary_check(question, value, unit, context, formula)
    
    return None
```

**영향**:
- `cursor` 모드: `_native_boundary_check` 호출 (개념 기반)
- 다른 LLM: `_external_boundary_check` 호출 (API 기반)
- 로직이 완전히 다름 (문제!)

**제안 해결책**:
1. `_native_boundary_check` 로직을 `_external_boundary_check`에 통합
2. `llm_mode == "cursor"` 분기로 변경 (명시적)
3. 또는 `api_type == "cursor"` 디스패치 (권장)

---

### 🟡 2. `sources/value.py` - `AIAugmentedEstimationSource` (Lines 103-192)
**문제**: `llm_mode == "cursor"` 분기 존재 (하지만 정당한 이유)

```python
def collect(self, question: str, context: Optional[Context] = None) -> List[ValueEstimate]:
    """AI 증강 추정"""
    
    if self.llm_mode == "skip":
        return []
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Cursor AI: instruction 생성 (Phase 3에서는 사용 불가)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    if self.llm_mode == "cursor":  # v7.8.1: cursor = Cursor AI
        logger.info(f"  [AI+Web] Cursor AI: instruction 생성 (Phase 3 스킵)")
        
        instruction = self._build_native_instruction(question, context)
        
        # v7.8.1: Cursor AI에서는 빈 리스트 반환
        # (대화 컨텍스트에만 instruction 추가, 실제 추정은 하지 않음)
        logger.info(f"  [AI+Web] Instruction 생성 완료 (Cursor AI용)")
        logger.info("  " + "="*50)
        logger.info(instruction)
        logger.info("  " + "="*50)
        return []
    
    else:  # External LLM
        logger.info(f"  [AI+Web] External LLM 모드 (모델: {self.llm_mode})")
        try:
            instruction = self._build_native_instruction(question, context)
            # ... API 호출 로직
            # ... 파싱 로직
            return [estimate]
        except Exception as e:
            logger.error(f"  [AI+Web] External API 호출 실패: {e}")
            return []
```

**상태**: ⚠️ **이 분기는 유지 필요!**

**이유**:
- Cursor AI는 **대화 컨텍스트 기반** (API 호출 불가)
- External LLM은 **API 호출 필수**
- 근본적으로 다른 작동 방식

**판단**: ✅ **정당한 분기** (제거 불필요)

---

### 🟢 3. `sources/value.py` - `LLMEstimationSource` (Lines 446-451)
**문제**: `llm_mode == "skip"` 분기 (deprecated)

```python
def collect(self, question: str, context: Optional[Context] = None) -> List[ValueEstimate]:
    """LLM 추정 (deprecated)"""
    
    if self.llm_mode == "skip":
        return []
```

**상태**: ✅ **삭제 예정 클래스** (deprecated 경고)

**제안**: 향후 버전에서 전체 클래스 삭제

---

### 🟡 4. `boundary_validator.py` - 초기화 (Line 103)
**문제**: `external` 문자열 사용

```python
def __init__(self, llm_mode: str = "external"):
    """BoundaryValidator 초기화"""
    self.llm_mode = llm_mode
    
    # External API 초기화
    if llm_mode == "external" and HAS_OPENAI:
        self.llm_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    else:
        self.llm_client = None
```

**영향**:
- `llm_mode != "external"` → `llm_client = None` (API 호출 불가)
- `cursor` 모드에서는 문제 없음 (API 필요 없음)
- 다른 LLM (`gpt-4o-mini` 등)에서는 API 필요!

**제안 해결책**:
```python
def __init__(self, llm_mode: str = "cursor"):
    """BoundaryValidator 초기화"""
    self.llm_mode = llm_mode
    
    # LLM API 초기화 (cursor 제외)
    if llm_mode != "cursor" and HAS_OPENAI:
        self.llm_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    else:
        self.llm_client = None
```

---

## 📊 레거시 정리 테이블

| 파일 | 위치 | 레거시 코드 | 심각도 | 제안 |
|------|------|------------|--------|------|
| `boundary_validator.py` | Lines 611-619 | `if llm_mode == "native"` / `"external"` | 🔴 **High** | `llm_mode == "cursor"` 분기 또는 통합 |
| `boundary_validator.py` | Line 103 | `if llm_mode == "external"` | 🟡 **Medium** | `if llm_mode != "cursor"` |
| `sources/value.py` | Lines 103-192 | `if llm_mode == "cursor"` | 🟢 **Low** (정당) | 유지 |
| `sources/value.py` | Line 446 | `if llm_mode == "skip"` (deprecated) | 🟢 **Low** | 향후 삭제 |

---

## 🎯 제거 전략

### Strategy 1: 점진적 제거 (권장)
1. **Phase 1** (1시간):
   - `boundary_validator.py` Line 103: `external` → `cursor` 외 모든 모드
   - `boundary_validator.py` Lines 611-619: `native` → `cursor`
   - 기존 로직 유지 (안전)

2. **Phase 2** (2시간):
   - `_native_boundary_check` + `_external_boundary_check` 통합
   - `api_type` 디스패치 적용
   - 테스트 검증

3. **Phase 3** (향후):
   - `LLMEstimationSource` 클래스 전체 삭제 (deprecated)

### Strategy 2: 급진적 통합 (높은 리스크)
1. 모든 `native`/`external` 분기를 `api_type` 디스패치로 즉시 교체
2. 광범위한 테스트 필요
3. 2-3일 소요

---

## ✅ 검증 계획

### 1. 단위 테스트
```python
# tests/test_boundary_validator_llm_modes.py

def test_cursor_mode_boundary():
    """Cursor 모드에서 Boundary 검증"""
    validator = BoundaryValidator(llm_mode="cursor")
    result = validator.validate(
        question="서울 음식점 수는?",
        estimated_value=100_000,
        unit="개",
        context=None,
        formula="N = 인구 × 밀도"
    )
    assert result['passed']

def test_gpt4o_mini_mode_boundary():
    """GPT-4o-mini 모드에서 Boundary 검증"""
    validator = BoundaryValidator(llm_mode="gpt-4o-mini")
    result = validator.validate(...)
    assert result['passed']
```

### 2. 통합 테스트
```python
# tests/test_phase4_comprehensive_llm_modes.py

def test_fermi_estimation_all_llm_modes():
    """모든 LLM 모드에서 Fermi 추정 검증"""
    llm_modes = ["cursor", "gpt-4o-mini", "o1-mini"]
    
    for mode in llm_modes:
        os.environ['LLM_MODE'] = mode
        estimator = EstimatorRAG()
        
        result = estimator.estimate("서울 음식점 수는?")
        
        assert result.value > 0
        assert result.phase == 4
        assert result.reasoning
```

---

## 📝 작업 체크리스트

### Phase 1: 기본 수정 (1시간)
- [ ] `boundary_validator.py` Line 103 수정
  - `if llm_mode == "external"` → `if llm_mode != "cursor"`
- [ ] `boundary_validator.py` Lines 611-619 수정
  - `if self.llm_mode == "native"` → `if self.llm_mode == "cursor"`
  - `elif self.llm_mode == "external"` → `else` (또는 `!= "cursor"`)
- [ ] 주석 업데이트
  - "Native Mode" → "Cursor Mode"
  - "External Mode" → "API Mode"

### Phase 2: 테스트 검증 (30분)
- [ ] 기존 테스트 실행
  - `tests/test_estimator_comprehensive.py`
  - `tests/test_phase4_parsing_fix.py`
- [ ] 새 테스트 작성
  - `test_boundary_validator_llm_modes.py`
- [ ] 모든 Phase (0-4) 검증
  - `cursor` 모드
  - `gpt-4o-mini` 모드
  - `o1-mini` 모드

### Phase 3: 문서화 (30분)
- [ ] `UMIS_ARCHITECTURE_BLUEPRINT.md` 업데이트
- [ ] `umis_core.yaml` 주석 업데이트
- [ ] 변경 로그 작성

---

## 🚨 리스크 평가

### High Risk
- **`boundary_validator.py` 로직 변경**: Boundary 검증 실패 시 부정확한 추정값 통과 가능

### Medium Risk
- **초기화 로직 변경**: `llm_client` 생성 실패 시 API 호출 불가

### Low Risk
- **주석 및 문서 업데이트**: 기능 영향 없음

---

## 💡 권장 사항

1. **Strategy 1 (점진적 제거) 선택**
   - 안정성 우선
   - 단계별 검증 가능

2. **`sources/value.py`의 `cursor` 분기는 유지**
   - 근본적으로 다른 작동 방식
   - 제거 시 Cursor AI 사용 불가

3. **테스트 우선 접근**
   - 수정 전 테스트 작성
   - 수정 후 즉시 검증

4. **문서화 동시 진행**
   - 코드 수정과 문서 업데이트 동시 진행
   - 미래 유지보수 용이

---

## 📌 다음 단계

1. **즉시 실행**: Phase 1 기본 수정 (1시간)
2. **테스트**: 모든 LLM 모드 검증 (30분)
3. **검토**: 결과 분석 및 추가 개선 사항 도출

**예상 소요 시간**: 2시간  
**예상 효과**: Native/External 레거시 완전 제거, v7.8.1 철학 완성


