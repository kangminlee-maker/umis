# Session Summary: Phase 4 재귀 폭발 문제 분석

**날짜**: 2025-11-26
**작업**: Phase 4 Fermi 테스트 분석 및 문제점 식별
**버전**: v7.10.0
**LLM 모델**: o1 (gpt-5.1)

---

## 1. 테스트 개요

### 테스트 실행 정보
- **시작 시간**: 2025-11-25 22:59:43
- **종료 시간**: 사용자가 중단 (약 1시간 30분+ 후)
- **테스트 문제**: 서울시 커피숍 수 추정
- **로그 파일**: `testlog.txt` (4,851줄)

### 문제 상황
사용자가 테스트가 너무 오래 걸려 중단. "무한루프" 같은 증상 발생.

---

## 2. 문제 분석

### 2.1 "무한루프" 문제 (실제: 재귀 폭발)

**핵심 원인**: Phase 4의 과도한 재귀 + 모든 변수에 대한 LLM API 호출

**실행 흐름**:
```
[Phase 4] 질문 수신
└─ [Step 2] LLM이 4개 모형 생성 (각 모형 4-6개 변수)
   └─ [Step 3] 각 모형의 각 변수 추정
      └─ [Phase 3] LLM API 호출 (10-30초)
         └─ 실패 시 → [Phase 4 재귀] (depth+1)
            └─ [Step 2] 또 4개 모형 생성...
               └─ max_depth=4까지 반복
```

**로그 증거**:
```
23:04:40 | [Step 3] 변수 'population_adjustment_factor' 추정 필요
23:04:40 | [Phase 3] retail에서 population_adjustment_factor는?
23:04:57 | ✅ 완료 (16.70초)

23:05:07 | [Step 3] 변수 'trend_adjustment_factor' 추정 필요
23:05:07 | 🔄 Phase 3 실패 → Fermi 재귀
23:05:07 | [Phase 4] Fermi Estimation (depth 1)
23:06:20 | [LLM] 응답 수신 (3378자) → 또 4개 모형 생성
...무한 반복...
```

**문제 규모**:
- 4개 모형 x 5개 변수 x max_depth 4 = **최대 80개+ Phase 3 호출**
- 각 Phase 3 호출 = **10-30초** (API 모드)
- 예상 총 시간: **80 x 15초 = 20분 이상** (단일 질문)

### 2.2 WARNING/ERROR 분류

| 유형 | 메시지 | 원인 | 조치 |
|------|--------|------|------|
| **ERROR** | `float() argument must be a string or a real number, not 'NoneType'` | LLM 응답에서 value 파싱 실패 | **수정 필요** |
| WARNING | `⚠️ Max depth 4 도달 → Phase 3 Fallback` | 정상 동작 (깊이 제한) | 정상 |
| WARNING | `[Judgment] 증거 없음` | Phase 3에서 증거 수집 실패 | 정상 |
| WARNING | `🔄 Phase 3 실패 → Fermi 재귀` | 낮은 신뢰도로 재귀 | **검토 필요** |
| WARNING | `[Fallback] xxx 값 없음` | fallback 값도 없음 | **검토 필요** |
| WARNING | `[Validate] calculation_verification 필드 누락!` | LLM 응답 불완전 | 정상 (자동 생성됨) |
| INFO | `LangChainDeprecationWarning: Chroma` | Chroma 패키지 deprecated | 낮은 우선순위 |

### 2.3 Phase 3 실패 조건 분석

**현재 실패 조건** (confidence < 0.70):
```python
# phase4_fermi.py의 _estimate_variable 메서드
if phase3_result.confidence < 0.70:
    logger.info("🔄 Phase 3 실패 → Fermi 재귀")
    return self._recursive_fermi(...)
```

**문제점**:
- 신뢰도 0.55~0.69인 경우도 재귀 발생
- 예: `1.0 (신뢰도 55%)` → 값은 있지만 재귀 시도
- 예: `0.1 (신뢰도 40%)` → 또 재귀 시도

---

## 3. 해결 방안 (권장)

### 3.1 즉시 조치 (권장)

#### A. 재귀 횟수 제한 추가
```python
# phase4_fermi.py
class Phase4FermiDecomposition:
    def __init__(self, ...):
        self.max_depth = 4  # 기존
        self.max_total_attempts = 50  # 신규: 전체 변수 추정 시도 제한
        self._attempt_count = 0  # 신규
```

#### B. Phase 3 실패 조건 완화
```python
# 현재: confidence < 0.70 → 재귀
# 개선: confidence < 0.50 → 재귀 (더 관대한 기준)

# 또는 값이 있으면 수용:
if phase3_result.value is not None and phase3_result.value != 0:
    return phase3_result  # 값이 있으면 수용
```

#### C. 변수별 fallback 값 개선
```python
# _get_fallback_value 개선
def _get_fallback_value(self, var_name: str) -> Optional[float]:
    # 변수명 패턴 기반 기본값
    if 'rate' in var_name or 'ratio' in var_name:
        return 0.1  # 10%
    if 'share' in var_name:
        return 0.1  # 10%
    if 'factor' in var_name:
        return 1.0  # 보정 계수
    if 'per_' in var_name:
        return 1.0  # 단위당 값
    return None
```

### 3.2 중기 개선

#### D. 모형 수 제한
```python
# 현재: LLM이 4-5개 모형 생성
# 개선: 최대 2개 모형만 사용
models = models[:2]  # 상위 2개만
```

#### E. 변수 수 제한 강화
```python
# 현재: 권장 6개, 절대 10개
# 개선: 권장 3개, 절대 5개
self.max_variables_soft = 3
self.max_variables_hard = 5
```

### 3.3 API 호출 최적화

#### F. 캐싱 시스템 강화
```python
# 동일 변수 재요청 방지
self._variable_cache = {}

def _estimate_variable(self, var_name, ...):
    cache_key = f"{domain}:{var_name}"
    if cache_key in self._variable_cache:
        return self._variable_cache[cache_key]
```

---

## 4. 발견된 ERROR 상세

### 4.1 float() 파싱 에러

**위치**: `umis_rag/agents/estimator/sources/value.py:189`

**로그**:
```
00:23:01 | ERROR | [AI+Web] API 호출 실패: float() argument must be a string or a real number, not 'NoneType'
```

**원인**: LLM 응답에서 숫자 추출 실패

**수정 필요**: `value.py`의 예외 처리 강화

```python
# 현재 (추정)
value = float(response.get('value'))

# 개선
raw_value = response.get('value')
if raw_value is None:
    logger.warning("LLM 응답에 value 없음")
    return None
try:
    value = float(raw_value)
except (TypeError, ValueError) as e:
    logger.error(f"value 파싱 실패: {raw_value} ({e})")
    return None
```

---

## 5. 테스트 결과 요약

| 항목 | 결과 | 비고 |
|------|------|------|
| **테스트 질문** | 서울시 커피숍 수 | - |
| **실행 시간** | 1시간 30분+ | 사용자 중단 |
| **Phase 3 호출 수** | 100회+ | 과도함 |
| **LLM API 호출** | 100회+ | 비용 문제 |
| **성공 여부** | 미완료 | 중단됨 |

---

## 6. 다음 세션 권장 작업

### 6.1 필수 (즉시)

1. **전체 시도 횟수 제한 추가**
   - `_attempt_count` 변수 추가
   - 50회 초과 시 조기 종료

2. **Phase 3 실패 조건 완화**
   - confidence 0.70 → 0.50
   - 또는 값이 있으면 수용

3. **float() 파싱 에러 수정**
   - `value.py` 예외 처리 강화

### 6.2 권장 (단기)

4. **fallback 값 개선**
   - 변수명 패턴 기반 기본값

5. **모형/변수 수 제한**
   - 모형 2개, 변수 5개로 축소

6. **테스트 재실행**
   - gpt-4o-mini로 먼저 테스트 (비용 절감)
   - 단일 질문 timeout 설정

---

## 7. 파일 변경 예상

| 파일 | 변경 내용 |
|------|----------|
| `phase4_fermi.py` | 시도 횟수 제한, 실패 조건 완화 |
| `sources/value.py` | float() 파싱 예외 처리 |

---

## 8. 테스트 명령어

```bash
# 간단한 질문으로 테스트 (timeout 포함)
cd /Users/kangmin/umis_main_1103/umis
timeout 120 python3 -c "
from umis_rag.agents.estimator.phase4_fermi import Phase4FermiDecomposition
from umis_rag.agents.estimator.models import Context

phase4 = Phase4FermiDecomposition()
result = phase4.estimate('서울 인구수는?', Context(domain='General'))
print(f'결과: {result.value} (신뢰도: {result.confidence})')
"
```

---

**작성자**: Claude (Cursor AI)
**다음 세션 키워드**: `재귀 제한`, `Phase 3 실패 조건`, `fallback 개선`, `value.py 파싱`

---

## 9. 관련 문서

- `dev_docs/session_summaries/SESSION_SUMMARY_20251125_PHASE4_FERMI_RESTRUCTURE.md` - 이전 세션
- `umis_rag/agents/estimator/phase4_fermi.py` - 핵심 파일
- `testlog.txt` - 전체 로그 (4,851줄)
