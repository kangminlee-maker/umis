# Session Summary: Phase 4 Fermi 구조 변경

**날짜**: 2025-11-25
**작업**: `phase4_fermi.py` 벤치마크 패턴 적용
**버전**: v7.10.0

---

## 1. 작업 배경

사용자가 `phase4_fermi.py`의 Fermi 추정 방식이 벤치마크(`benchmarks/estimator/phase4/common.py`)와 다르다고 지적. 벤치마크 패턴을 기준으로 구조 변경 진행.

### 핵심 차이점 (분석 결과)

| 영역 | `common.py` (벤치마크) | `phase4_fermi.py` (기존) |
|------|------------------------|--------------------------|
| 프롬프트 | `concept` 필드 필수, `final_calculation`/`calculation_verification` 강제 | `concept` 없음, 필수 필드 불명확 |
| 평가 체계 | 110점 (내용 45 + 형식 5 + 정확도 25 + 분해 10 + 개념 15 + 논리 10) | 단순 점수화만 |
| 계산 검증 | `auto_verify_calculation()` + 마지막 단계=최종값 검증 | 단순 검증 |
| 후처리 | 누락 필드 자동 생성 + 추적 | 없음 |

---

## 2. 완료된 작업

### 2.1 프롬프트 개선 (`_build_llm_prompt`)

**파일**: `umis_rag/agents/estimator/phase4_fermi.py`
**라인**: 1138-1312

**변경 내용**:
- 필수 필드 강제 헤더 추가 (CRITICAL MANDATORY FIELDS)
- `concept` 필드 포함 Few-shot 예시 추가
- 마지막 단계 value = 최상위 value 정확히 일치 규칙 명시
- 기존 예시의 value 불일치 문제 수정 (70000 vs 66667 -> 66667로 통일)

```python
# 핵심 변경: 필수 필드 강제
mandatory_header = """
CRITICAL MANDATORY FIELDS (누락 시 실패!):
1. decomposition의 모든 단계에 "concept" 필드 필수!
2. 최상위 "final_calculation" 필드 필수!
3. 최상위 "calculation_verification" 필드 필수!
4. decomposition[-1]["value"] == JSON["value"] (정확히 일치!)
"""
```

### 2.2 응답 후처리 함수 추가

**새 메서드들** (라인 2622-3040):

1. **`_model_to_decomposition_list()`**: FermiModel을 평가용 Dict 리스트로 변환
2. **`_validate_and_postprocess_response()`**: 응답 검증 및 후처리
   - 필수 필드 자동 생성 (추적)
   - 마지막 단계 value = 최상위 value 검증 및 교정
3. **`_auto_verify_calculation()`**: 분해 값으로 최종값 자동 계산 시도

### 2.3 평가 함수 이식 (common.py -> phase4_fermi.py)

1. **`_evaluate_content_score()`** (45점)
   - 단계별 계산 완성도 (10점)
   - 계산 논리 연결 (10점)
   - 수치 정확성 (25점)

2. **`_evaluate_format_score()`** (5점)
   - `final_calculation` 필드 (2점)
   - `calculation_verification` 필드 (2점)
   - `concept` 필드 완성도 (1점)

3. **`_evaluate_conceptual_coherence()`** (15점)
   - 핵심 개념 포함 여부 (5점)
   - 논리적 연산 존재 (3점)
   - Pseudo-code 논리 구조 (7점)

### 2.4 `_step4_execute` 품질 평가 통합

**라인**: 1631-1783

**변경 내용**:
- decomposition을 Dict 형태로 변환하여 평가 함수에 전달
- 후처리 로직 호출 (필수 필드 자동 생성, value 교정)
- 품질 평가 로깅 추가
- `reasoning_detail`에 `quality_evaluation` 추가

```python
# 품질 평가 결과 예시
total_quality_score = content_score['score'] + format_score['score'] + conceptual_score['score']
logger.info(f"[품질] 내용: {content_score['score']:.1f}/45, "
           f"형식: {format_score['score']:.1f}/5, "
           f"개념: {conceptual_score['score']:.1f}/15 = {total_quality_score:.1f}/65")
```

---

## 3. 완료된 추가 작업 (2025-11-25 후속 세션)

### 3.1 `_parse_llm_models` 필수 필드 검증 추가

**상태**: COMPLETED

**설명**: LLM 응답 파싱 시 `concept` 필드 누락 경고 추가 완료.

**변경 위치**: 라인 1376-1401 (`_parse_llm_models` 메서드)

**구현 내용**:
```python
# v7.10.0: concept 필드 누락 검증
raw_variables = model_data.get('variables', [])
missing_concept = [
    v.get('name', 'unknown')
    for v in raw_variables
    if not v.get('concept')
]
if missing_concept:
    logger.warning(
        f"{'  ' * depth}        [Validate] concept 필드 누락: "
        f"{len(missing_concept)}개 변수 ({', '.join(missing_concept[:3])}...)"
    )
```

### 3.2 `FermiVariable` 데이터클래스 `concept` 필드 추가

**라인**: 349

```python
concept: str = ""  # v7.10.0: 도메인 특화 개념
```

### 3.3 `_validate_and_postprocess_response` 검증 강화

**라인**: 2705-2722

- `final_calculation` 누락 시 경고 로그
- `calculation_verification` 누락 시 경고 로그
- decomposition의 각 step에서 `concept` 필드 누락 검증

---

## 4. 파일 변경 요약

| 파일 | 변경 유형 | 라인 수 변경 |
|------|----------|-------------|
| `umis_rag/agents/estimator/phase4_fermi.py` | 수정 | 2664 -> 3279 (+615) |

### 주요 추가 메서드

| 메서드 | 설명 | 라인 |
|--------|------|------|
| `_model_to_decomposition_list()` | 모델 -> Dict 변환 | 2622-2664 |
| `_validate_and_postprocess_response()` | 응답 후처리 | 2666-2719 |
| `_auto_verify_calculation()` | 자동 계산 검증 | 2721-2772 |
| `_evaluate_content_score()` | 내용 점수 (45점) | 2774-2894 |
| `_evaluate_format_score()` | 형식 점수 (5점) | 2896-2972 |
| `_evaluate_conceptual_coherence()` | 개념 일관성 (15점) | 2974-3083 |

---

## 5. 다음 세션 권장 작업

### 5.1 즉시 필요

1. ~~**`_parse_llm_models` 필수 필드 검증 추가** (TODO #5)~~ COMPLETED
2. ~~**Linter 에러 확인 및 수정**~~ COMPLETED (에러 없음)
3. ~~**단위 테스트 실행**~~ COMPLETED (20/20 통과)

### 5.2 추가 개선 (선택)

1. ~~**Pro 모델용 Fast Mode constraint 추가**~~ COMPLETED
   - `common.py`의 `get_fast_mode_constraint()` 참고
   - `_build_llm_prompt`에 조건부 적용

2. **시나리오별 키워드 확장**
   - `_evaluate_conceptual_coherence`의 동적 키워드 추출 개선

3. **벤치마크 테스트 실행**
   - `benchmarks/estimator/phase4/` 스크립트로 변경 효과 검증

---

## 6. 테스트 명령어

```bash
# Linter 확인
cd /Users/kangmin/umis_main_1103/umis
python -m py_compile umis_rag/agents/estimator/phase4_fermi.py

# 단위 테스트
pytest tests/unit/test_phase4_fermi.py -v

# 벤치마크 테스트 (선택)
python benchmarks/estimator/phase4/run_benchmark.py --model gpt-4o-mini
```

---

## 7. 참고 문서

- `benchmarks/estimator/phase4/common.py` - 벤치마크 평가 로직 원본
- `benchmarks/estimator/phase4/analysis/evaluation_rebalancing.md` - 평가 기준 설계
- `dev_docs/improvements/estimator_work_domain_v7_10_0.yaml` - v7.10.0 작업 범위

---

**작성자**: Claude (Cursor AI)
**다음 세션 키워드**: `phase4_fermi.py`, `벤치마크 테스트`, `시나리오별 키워드 확장`

---

## 8. 후속 세션 변경 이력 (2025-11-25)

| 시간 | 작업 | 결과 |
|------|------|------|
| 후속 | TODO #5 완료 | `_parse_llm_models` concept 검증 추가 |
| 후속 | `FermiVariable` 수정 | `concept` 필드 추가 |
| 후속 | `_validate_and_postprocess_response` 강화 | 필수 필드 누락 경고 추가 |
| 후속 | 테스트 통과 | 20/20 PASSED |
| 후속 | **Pro 모델 Fast Mode 추가** | `_build_llm_prompt`에 속도 최적화 constraint 적용 |
| 후속 | **LLMEstimationSource 제거** | `source_collector.py`에서 alias로 대체 |
| 후속 | **통합 테스트 완료** | 품질 평가, 필수 필드 검증, Boundary 검증 모두 정상 동작 |

### 8.1 Pro 모델용 Fast Mode constraint 추가 (선택 작업 #1)

**라인**: 1163-1183

**적용 모델**: `gpt-5-pro`, `o1-pro`, `o1-pro-2025-03-19`, `o1-preview`

**구현 내용**:
```python
# Pro 모델용 Fast Mode constraint
fast_mode_constraint = """
SPEED OPTIMIZATION MODE
- 목표 응답 시간: 60초 이내
- 최대 출력 길이: 2,000자 이내 (약 500 토큰)
- decomposition: 3-5단계만 (필수 단계만 포함)
- reasoning: 각 단계 15단어 이내
"""
```

**호출 수정** (라인 950-953):
- `_build_llm_prompt(question, available, model_name=model_name)` 형태로 변경
- `self.llm_mode`를 `model_name`으로 전달

**테스트 결과**: 20/20 PASSED
