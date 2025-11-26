# Estimator API 문서 (v7.9.0)

**버전**: v7.9.0  
**최종 업데이트**: 2025-11-25

---

## 📋 목차

1. [개요](#개요)
2. [EstimatorRAG](#estimatorrag)
3. [Phase3Guestimation](#phase3guestimation)
4. [Phase4FermiDecomposition](#phase4fermiDecomposition)
5. [ValidatorRAG](#validatorrag)
6. [EstimationResult](#estimationresult)
7. [Context](#context)
8. [사용 예시](#사용-예시)

---

## 개요

Estimator는 5-Phase 아키텍처로 값을 추정하는 시스템입니다.

**Phase 순서**:
1. **Phase 0**: Literal (프로젝트 데이터)
2. **Phase 1**: Direct RAG (학습 규칙)
3. **Phase 2**: Validator (확정 데이터)
4. **Phase 3**: Guestimation (LLM + Web)
5. **Phase 4**: Fermi Decomposition (재귀 분해)

**자동 Fallback** (v7.9.0):
- Cursor 모드에서 Phase 3-4 필요 시 자동으로 `gpt-4o-mini`로 전환

---

## EstimatorRAG

### 클래스 정의

```python
class EstimatorRAG:
    """
    Fermi 추정 Agent (5-Phase Architecture)
    
    Phase 순서:
    0. Literal (프로젝트 데이터)
    1. Direct RAG (학습 규칙)
    2. Validator (확정 데이터)
    3. Guestimation (LLM + Web)
    4. Fermi Decomposition
    
    v7.9.0 주요 변경사항:
    - 항상 EstimationResult 반환 (None 불가)
    - Cursor Auto Fallback (Phase 3-4)
    - LLM Mode 동적 전환
    """
```

### estimate()

**시그니처**:
```python
def estimate(
    self,
    question: str,
    project_data: Optional[Dict] = None,
    context: Optional[Context] = None,
    force_phase: Optional[int] = None
) -> EstimationResult:  # v7.9.0: 항상 EstimationResult 반환
```

**파라미터**:

| 이름 | 타입 | 필수 | 기본값 | 설명 |
|------|------|------|--------|------|
| `question` | `str` | ✅ | - | 추정할 질문 (예: "B2B SaaS ARPU는?") |
| `project_data` | `Dict` | ❌ | `None` | 프로젝트 확정 데이터 (Phase 0) |
| `context` | `Context` | ❌ | `None` | 맥락 정보 (domain, region, time_period 등) |
| `force_phase` | `int` | ❌ | `None` | 특정 Phase 강제 실행 (테스트용) |

**반환값**: `EstimationResult`

**v7.9.0 변경사항**:
- ❌ **Before**: `Optional[EstimationResult]` (실패 시 `None`)
- ✅ **After**: `EstimationResult` (실패 시 `phase=-1`)

**반환값 구조**:
```python
EstimationResult(
    question="질문",
    value=1000.0,           # 추정값 (또는 None)
    unit="원",
    phase=3,                 # 사용된 Phase (0-4, 또는 -1: 실패)
    confidence=0.8,         # 신뢰도 (0.0-1.0)
    error=None,             # 실패 시 에러 메시지
    failed_phases=[],       # 실패한 Phase 목록
    execution_time=2.5,     # 실행 시간 (초)
    # ... 기타 필드 ...
)
```

**성능 특성**:
- **Phase 0**: <0.1초 (즉시)
- **Phase 1**: <0.5초 (RAG 검색)
- **Phase 2**: <1초 (Validator 검색)
- **Phase 3**: <5초 (LLM + Web)
- **Phase 4**: <10초 (단순 모형), <30초 (복잡한 모형)

**사용 예시**:

```python
from umis_rag.agents.estimator import EstimatorRAG
from umis_rag.agents.estimator.models import Context

estimator = EstimatorRAG()

# 예시 1: Phase 0 (프로젝트 데이터)
result = estimator.estimate(
    question="churn_rate",
    project_data={'churn_rate': 0.05}
)
print(f"Phase {result.phase}: {result.value}")  # Phase 0: 0.05

# 예시 2: Phase 3 (Guestimation)
result = estimator.estimate(
    question="B2B SaaS의 평균 ARPU는?",
    context=Context(domain='B2B_SaaS', region='한국')
)
if result.is_successful():
    print(f"Phase {result.phase}: {result.value} {result.unit}")
    print(f"신뢰도: {result.confidence:.0%}")
else:
    print(f"실패: {result.error}")

# 예시 3: Cursor 모드 (자동 Fallback)
from umis_rag.core.config import settings
settings.llm_mode = 'cursor'

result = estimator.estimate(
    question="AI 챗봇 ARPU는?",  # Phase 3 필요
    context=Context(domain='AI_Chatbot')
)
# 자동으로 gpt-4o-mini로 전환하여 실행
# 결과: Phase 3 성공
```

**에러 처리**:

```python
result = estimator.estimate(question="알 수 없는 질문?")

if not result.is_successful():
    print(f"실패: phase={result.phase}")
    print(f"에러: {result.error}")
    print(f"실패한 Phase: {result.failed_phases}")
    # 출력 예시:
    # 실패: phase=-1
    # 에러: 모든 Phase(0-4)에서 추정 실패
    # 실패한 Phase: [0, 1, 2, 3, 4]
```

---

## Phase3Guestimation

### 클래스 정의

```python
class Phase3Guestimation:
    """
    Phase 3: Guestimation (LLM + Web 통합 추정)
    
    특징:
    - LLM 지식 기반 추정
    - 웹 검색 통합 (Google Custom Search)
    - 다중 Source 종합 (Physical, Soft, Value)
    
    v7.9.0:
    - Cursor Auto Fallback 지원
    - LLM Mode 동적 전환
    """
```

### estimate()

**시그니처**:
```python
def estimate(
    self,
    question: str,
    context: Context
) -> EstimationResult:
```

**파라미터**:

| 이름 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `question` | `str` | ✅ | 추정할 질문 |
| `context` | `Context` | ✅ | 맥락 정보 (domain, region 등) |

**반환값**: `EstimationResult`

**성능**:
- 평균: 2-3초
- 최대: 5초 (목표)

**사용 예시**:

```python
from umis_rag.agents.estimator.phase3_guestimation import Phase3Guestimation
from umis_rag.agents.estimator.models import Context

phase3 = Phase3Guestimation()

result = phase3.estimate(
    question="2025년 AI 챗봇 서비스 ARPU는?",
    context=Context(domain='AI_Chatbot', region='한국', time_period='2025')
)

if result.phase == 3:
    print(f"값: {result.value}")
    print(f"신뢰도: {result.confidence:.0%}")
    print(f"추론: {result.reasoning}")
```

---

## Phase4FermiDecomposition

### 클래스 정의

```python
class Phase4FermiDecomposition:
    """
    Phase 4: Fermi Decomposition (재귀 분해 추정)
    
    특징:
    - LLM 기반 모형 생성
    - 재귀적 하위 질문 추정
    - 순환 의존성 감지
    
    v7.9.0:
    - Cursor Auto Fallback 지원
    - LLM Client 동적 생성
    """
```

### estimate()

**시그니처**:
```python
def estimate(
    self,
    question: str,
    context: Context,
    depth: int = 0
) -> Optional[EstimationResult]:  # None 가능 (Phase 3로 위임)
```

**파라미터**:

| 이름 | 타입 | 필수 | 기본값 | 설명 |
|------|------|------|--------|------|
| `question` | `str` | ✅ | - | 추정할 질문 |
| `context` | `Context` | ✅ | - | 맥락 정보 |
| `depth` | `int` | ❌ | `0` | 재귀 깊이 (순환 감지용) |

**반환값**: `Optional[EstimationResult]`
- `None`: Phase 3로 위임 (모형 생성 실패 등)
- `EstimationResult`: Phase 4 성공

**성능**:
- 단순 모형: 5-10초
- 복잡한 모형 (재귀 3+ 깊이): 20-30초

**사용 예시**:

```python
from umis_rag.agents.estimator.phase4_fermi import Phase4FermiDecomposition
from umis_rag.agents.estimator.models import Context

phase4 = Phase4FermiDecomposition()

result = phase4.estimate(
    question="서울 음식점 수는?",
    context=Context(region='서울')
)

if result and result.phase == 4:
    print(f"값: {result.value}")
    print(f"Fermi 모형: {result.fermi_model}")
    print(f"하위 변수: {result.variable_results}")
```

---

## ValidatorRAG

### 클래스 정의

```python
class ValidatorRAG:
    """
    Validator Agent (확정 데이터 검색)
    
    특징:
    - ChromaDB 기반 유사도 검색
    - 24개 데이터 소스 (v7.9.0)
    - L2 Distance < 0.85 (거의 완벽한 매칭만)
    
    v7.9.0:
    - 유사도 임계값 강화 (0.95 → 0.85)
    - Region 정보 포함 검색
    - 질문 정규화 준비
    """
```

### search_definite_data()

**시그니처**:
```python
def search_definite_data(
    self,
    question: str,
    context: Optional[Context] = None,
    top_k: int = 3
) -> Optional[EstimationResult]:
```

**파라미터**:

| 이름 | 타입 | 필수 | 기본값 | 설명 |
|------|------|------|--------|------|
| `question` | `str` | ✅ | - | 검색할 질문 |
| `context` | `Context` | ❌ | `None` | 맥락 정보 (domain, region) |
| `top_k` | `int` | ❌ | `3` | 상위 K개 결과 |

**반환값**: `Optional[EstimationResult]`
- `None`: 확정 데이터 없음 (Phase 3로 위임)
- `EstimationResult`: Phase 2 성공 (confidence=1.0)

**유사도 임계값** (v7.9.0):
```python
if distance < 0.85:
    # 거의 완벽한 매칭 (100% 신뢰도)
    return EstimationResult(phase=2, confidence=1.0, ...)
else:
    # Phase 3/4로 위임
    return None
```

**성능**:
- 평균: 0.5-1초

**사용 예시**:

```python
from umis_rag.agents.validator import ValidatorRAG
from umis_rag.agents.estimator.models import Context

validator = ValidatorRAG()

result = validator.search_definite_data(
    question="B2B SaaS의 평균 churn rate는?",
    context=Context(domain='B2B_SaaS')
)

if result:
    print(f"확정 데이터 발견! {result.value}")
    print(f"출처: {result.value_estimates[0].source_detail}")
else:
    print("확정 데이터 없음 → Phase 3로")
```

---

## EstimationResult

### 데이터 클래스

```python
@dataclass
class EstimationResult:
    """
    추정 결과 (v7.9.0)
    
    v7.9.0 변경사항:
    - error: Optional[str] 추가
    - failed_phases: List[int] 추가
    - is_successful() 메서드 추가
    """
    question: str
    value: Optional[float] = None
    value_range: Optional[Tuple[float, float]] = None
    unit: str = ""
    phase: int = 0  # 0, 1, 2, 3, 4, -1 (실패)
    confidence: float = 0.0
    uncertainty: float = 0.3
    error: Optional[str] = None  # v7.9.0
    failed_phases: List[int] = field(default_factory=list)  # v7.9.0
    # ... 기타 필드 ...
```

### is_successful()

**시그니처**:
```python
def is_successful(self) -> bool:
    """
    추정 성공 여부 (v7.9.0)
    
    Returns:
        True: phase >= 0 and value 존재
        False: phase == -1 또는 value 없음
    """
```

**사용 예시**:

```python
result = estimator.estimate("질문?")

if result.is_successful():
    print(f"성공: {result.value}")
else:
    print(f"실패: {result.error}")
    print(f"Phase {result.phase}")
    print(f"실패한 Phase: {result.failed_phases}")
```

---

## Context

### 데이터 클래스

```python
@dataclass
class Context:
    """
    추정 맥락 정보
    
    사용:
    - Phase 2: domain, region으로 검색 범위 좁히기
    - Phase 3-4: 추정 정확도 향상
    """
    intent: Intent = Intent.GET_VALUE
    domain: str = "General"
    granularity: Granularity = Granularity.MACRO
    region: Optional[str] = None
    time_period: str = "2024"
    parent_model: Optional[Any] = None
    variable_role: Optional[str] = None
    project_data: Dict = field(default_factory=dict)
    constraints: List = field(default_factory=list)
    depth: int = 0
    parent_question: Optional[str] = None
```

**주요 필드**:

| 필드 | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| `domain` | `str` | `"General"` | 도메인 (예: "B2B_SaaS", "E-commerce") |
| `region` | `str` | `None` | 지역 (예: "한국", "서울", "글로벌") |
| `time_period` | `str` | `"2024"` | 시간 (예: "2025", "2023Q4") |
| `project_data` | `Dict` | `{}` | 프로젝트 데이터 (Phase 0용) |

**사용 예시**:

```python
# 최소 Context
context = Context()

# 전체 Context
context = Context(
    domain='B2B_SaaS',
    region='한국',
    time_period='2025'
)

result = estimator.estimate("ARPU는?", context=context)
```

---

## 사용 예시

### 기본 사용법

```python
from umis_rag.agents.estimator import EstimatorRAG
from umis_rag.agents.estimator.models import Context

estimator = EstimatorRAG()

# Phase 0: 프로젝트 데이터
result = estimator.estimate(
    question="churn_rate",
    project_data={'churn_rate': 0.05}
)
print(f"Phase {result.phase}: {result.value}")  # Phase 0: 0.05

# Phase 2-3: Validator → Guestimation
result = estimator.estimate(
    question="B2B SaaS ARPU는?",
    context=Context(domain='B2B_SaaS')
)
print(f"Phase {result.phase}: {result.value} (신뢰도: {result.confidence:.0%})")
```

### 에러 처리

```python
result = estimator.estimate("알 수 없는 질문?")

if not result.is_successful():
    print(f"실패: {result.error}")
    print(f"실패한 Phase: {result.failed_phases}")
```

### LLM Mode 전환

```python
from umis_rag.core.config import settings

# Cursor 모드
settings.llm_mode = 'cursor'
result = estimator.estimate("ARPU?")  # 자동 Fallback

# API 모드
settings.llm_mode = 'gpt-4o-mini'
result = estimator.estimate("ARPU?")
```

### 배치 추정

```python
questions = [
    ("churn_rate", {"churn_rate": 0.05}),
    ("arpu", {"arpu": 50000}),
    ("B2B SaaS ARPU?", {}),
]

results = []
for question, project_data in questions:
    result = estimator.estimate(question, project_data=project_data)
    results.append(result)

for result in results:
    if result.is_successful():
        print(f"{result.question}: {result.value}")
```

---

## 참고 자료

- **CHANGELOG**: `CHANGELOG.md`
- **사용자 가이드**: `docs/guides/ESTIMATOR_USER_GUIDE.md` (신규 작성 예정)
- **아키텍처**: `docs/architecture/UMIS_ARCHITECTURE_BLUEPRINT.md`
- **테스트**: `tests/unit/`, `tests/integration/`

---

**작성일**: 2025-11-25  
**버전**: v7.9.0  
**작성자**: AI Assistant

---

**END OF API DOCUMENTATION**




