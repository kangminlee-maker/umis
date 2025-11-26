# Phase 0-4 프로덕션 품질 개선 로드맵
**작성일**: 2025-11-23  
**버전**: v7.8.1 → v7.9.0  
**목표**: 프로덕션 수준의 안정성, 신뢰성, 유지보수성 확보

---

## 📋 현재 문제 분석

### 🔴 Critical Issues (즉시 수정 필요)

#### 1. LLM Mode 동적 변경 불가
**문제**:
```python
estimator = EstimatorRAG()  # llm_mode='cursor' 초기화 시점에 고정
os.environ['LLM_MODE'] = 'gpt-4o-mini'  # 환경변수 변경 무효
estimator.estimate(...)  # 여전히 cursor 모드로 동작
```

**영향**:
- 런타임 중 LLM 모드 변경 불가능
- 테스트 시나리오 제한
- 동적 모델 선택 불가 (예: Phase별 다른 모델 사용)

**근본 원인**:
```python
# umis_rag/agents/estimator/estimator.py Line 88
self.llm_mode = settings.llm_mode  # 초기화 시점에 고정

# Phase 3, 4로 전달
self.phase3 = Phase3Guestimation(llm_mode=self.llm_mode)
self.phase4 = Phase4FermiDecomposition(llm_mode=self.llm_mode)
```

**해결 방안**:
```python
# Option 1: Property 사용 (권장)
@property
def llm_mode(self):
    """동적으로 settings에서 읽기"""
    return settings.llm_mode

# Option 2: 명시적 재로드 메서드
def reload_config(self):
    """설정 재로드"""
    self.llm_mode = settings.llm_mode
    if self.phase3:
        self.phase3.llm_mode = self.llm_mode
    if self.phase4:
        self.phase4.llm_mode = self.llm_mode

# Option 3: Phase별 llm_mode 파라미터 (가장 유연)
def estimate(self, question: str, llm_mode: Optional[str] = None, ...):
    """각 estimate 호출 시 llm_mode 지정 가능"""
    mode = llm_mode or self.llm_mode
```

---

#### 2. Phase 간 llm_mode 전달 불일치
**문제**:
- `EstimatorRAG.llm_mode` (초기화 시점 고정)
- `Phase3Guestimation.llm_mode` (생성자 파라미터)
- `Phase4FermiDecomposition.llm_mode` (생성자 파라미터)
- `BoundaryValidator.llm_mode` (Phase 4 내부)
- `AIAugmentedEstimationSource.llm_mode` (Phase 3 내부)

**영향**:
- 각 Phase가 다른 llm_mode를 사용할 수 있음
- 디버깅 어려움
- 예상치 못한 동작

**해결 방안**:
```python
# 1. 중앙집중식 Config Manager
class LLMConfig:
    """LLM 설정 중앙 관리"""
    _instance = None
    
    @classmethod
    def get_mode(cls) -> str:
        """현재 LLM 모드 반환"""
        return settings.llm_mode
    
    @classmethod
    def set_mode(cls, mode: str):
        """LLM 모드 변경 (스레드 안전)"""
        settings.llm_mode = mode
        logger.info(f"LLM Mode 변경: {mode}")

# 2. 모든 Phase에서 동일하게 사용
class EstimatorRAG:
    def estimate(self, ...):
        mode = LLMConfig.get_mode()
        # Phase 3-4로 전달
```

---

#### 3. Cursor AI 모드 한계
**문제**:
- Phase 3-4에서 API 호출 필요
- Cursor AI는 instruction만 생성 (대화형)
- 자동화된 추정 불가능

**현상**:
```python
if self.llm_mode == "cursor":
    # instruction 생성만 하고 반환
    logger.warning("[Cursor AI] 대화 컨텍스트에서 직접 응답 필요")
    return []  # 빈 결과 → 추정 실패
```

**영향**:
- Phase 3: AI+Web Source가 빈 리스트 반환 → 증거 없음
- Phase 4: 모형 생성 실패 → Fallback → 추정 불가

**해결 방안**:
```python
# Option 1: Cursor 모드에서 자동으로 Fallback (권장)
if self.llm_mode == "cursor":
    logger.info("Cursor 모드: Phase 3-4 자동 Fallback to gpt-4o-mini")
    fallback_mode = "gpt-4o-mini"
    # Phase 3-4만 fallback 모드 사용
    result = self._estimate_with_mode(question, fallback_mode)

# Option 2: Cursor 전용 간단한 추정 로직
if self.llm_mode == "cursor":
    # Rule-based 또는 통계 기반 간단한 추정
    return self._cursor_simple_estimation(question)

# Option 3: 명확한 에러 메시지
if self.llm_mode == "cursor" and phase >= 3:
    raise ValueError(
        "Cursor 모드는 Phase 3-4를 지원하지 않습니다. "
        "LLM_MODE를 'gpt-4o-mini' 또는 'o1-mini'로 설정하세요."
    )
```

---

#### 4. None 반환 처리 미흡
**문제**:
```python
# estimator.py
if not result:
    return None  # ❌ 호출자가 None 체크 필수

# 사용자 코드
result = estimator.estimate("...")
print(f"값: {result.value}")  # AttributeError: 'NoneType'
```

**영향**:
- 예상치 못한 크래시
- 에러 메시지 불명확
- 사용자 경험 저하

**해결 방안**:
```python
# Option 1: 항상 EstimationResult 반환 (권장)
def estimate(self, ...) -> EstimationResult:
    """항상 EstimationResult 반환 (실패 시 phase=-1)"""
    try:
        # ... 추정 로직
        return result
    except Exception as e:
        logger.error(f"추정 실패: {e}")
        return EstimationResult(
            phase=-1,
            value=0.0,
            confidence=0.0,
            reasoning=f"추정 실패: {str(e)}",
            error=str(e)
        )

# Option 2: 명시적 예외 발생
def estimate(self, ...) -> EstimationResult:
    """실패 시 EstimationError 발생"""
    result = self._try_estimate(...)
    if result is None:
        raise EstimationError(
            "모든 Phase에서 추정 실패",
            question=question,
            attempted_phases=[0, 1, 2, 3, 4]
        )
    return result
```

---

### 🟡 High Priority Issues (빠른 시일 내 수정)

#### 5. Phase 3 증거 수집 실패
**문제**:
```
[Judgment] 증거 없음 → 판단 실패
```

**원인**:
- Cursor 모드: AI+Web Source가 빈 리스트 반환
- API 모드에서도 Source가 실패할 수 있음
- Web Search, RAG Benchmark 등 모든 Source 실패

**영향**:
- Phase 3 추정 불가
- Phase 4로 넘어가야 하는데 실패로 처리

**해결 방안**:
```python
# Phase 3 Fallback 체계 강화
def estimate(self, question: str, context: Optional[Context] = None):
    """Phase 3 추정 (Fallback 강화)"""
    
    # 1. Source 수집
    evidence = self.collector.collect_all(question, context)
    
    # 2. 증거 없으면 최소한의 추정 시도
    if not evidence:
        logger.warning("[Phase 3] 증거 없음 → 기본 추정 시도")
        
        # Option A: Domain 기반 기본값
        if context and context.domain in DEFAULT_VALUES:
            return self._use_default_value(question, context)
        
        # Option B: 통계적 기본값 (중앙값, 평균 등)
        return self._statistical_fallback(question, context)
        
        # Option C: Phase 4로 명시적 위임
        logger.info("[Phase 3] Phase 4로 위임")
        return None  # Phase 4가 처리
    
    # 3. 판단 합성
    judgment = self.synthesizer.synthesize(evidence, question)
    
    if judgment['value'] is None:
        logger.warning("[Phase 3] 판단 실패 → Phase 4로 위임")
        return None
    
    return EstimationResult(...)
```

---

#### 6. Phase 4 모형 생성 실패
**문제**:
```
Step 2 실패 (모형 없음) → 전체 추정 실패
```

**원인**:
- LLM이 올바른 YAML/JSON을 생성하지 못함
- 파싱 실패
- 순환 의존성 감지

**영향**:
- Phase 4 추정 완전 실패
- 사용자에게 값 제공 불가

**해결 방안**:
```python
# Step 2 Fallback 체계
def _step2_generate_models(self, ...):
    """모형 생성 (Fallback 강화)"""
    
    # 1. LLM으로 모형 생성 시도
    models = self._generate_llm_models(question, available, depth)
    
    if models:
        return models
    
    # 2. Fallback: 템플릿 기반 모형
    logger.warning("[Phase 4] LLM 실패 → 템플릿 모형 사용")
    models = self._generate_template_models(question, available)
    
    if models:
        return models
    
    # 3. Fallback: 단순 곱셈 모형
    logger.warning("[Phase 4] 템플릿 실패 → 단순 모형 생성")
    return self._generate_simple_model(question, available)

def _generate_simple_model(self, question, available):
    """최소한의 모형 (변수 곱셈)"""
    # 질문에서 키워드 추출
    keywords = self._extract_keywords(question)
    
    # 가능한 변수 2-3개 선택
    vars = self._select_relevant_variables(keywords, available)
    
    # 단순 곱셈 모형
    return [FermiModel(
        variables=vars,
        formula=" * ".join([v.name for v in vars]),
        confidence=0.5,
        reasoning="자동 생성된 단순 모형"
    )]
```

---

#### 7. 에러 로깅 부족
**문제**:
- 실패 원인이 명확하지 않음
- 디버깅 어려움
- 사용자가 문제 파악 불가

**해결 방안**:
```python
# 구조화된 로깅
import structlog

logger = structlog.get_logger()

def estimate(self, question: str, ...):
    """추정 (구조화된 로깅)"""
    log = logger.bind(
        question=question,
        domain=context.domain if context else None,
        llm_mode=self.llm_mode
    )
    
    log.info("estimation_started")
    
    # Phase 0
    result = self._try_phase0(...)
    if result:
        log.info("estimation_completed", phase=0, value=result.value)
        return result
    
    log.debug("phase0_skipped", reason="no_project_data")
    
    # Phase 1
    try:
        result = self._try_phase1(...)
        if result:
            log.info("estimation_completed", phase=1, value=result.value)
            return result
    except Exception as e:
        log.error("phase1_failed", error=str(e), exc_info=True)
    
    # ...
    
    log.error("estimation_failed", attempted_phases=[0, 1, 2, 3, 4])
    return None
```

---

### 🟢 Medium Priority Issues (점진적 개선)

#### 8. 테스트 커버리지 부족
**현황**:
- Phase 0: ✅ 테스트 있음
- Phase 1: ✅ 테스트 있음
- Phase 2: ✅ 테스트 있음
- Phase 3: ⚠️ 부분 커버리지 (Cursor 모드 실패)
- Phase 4: ⚠️ 부분 커버리지 (Cursor 모드 실패)

**목표**:
- 각 Phase별 단위 테스트
- 통합 테스트
- 엣지 케이스 테스트
- 성능 테스트

**테스트 구조**:
```
tests/
├── unit/
│   ├── test_phase0_literal.py
│   ├── test_phase1_direct_rag.py
│   ├── test_phase2_validator.py
│   ├── test_phase3_guestimation.py
│   ├── test_phase4_fermi.py
│   └── test_boundary_validator.py
├── integration/
│   ├── test_phase_flow.py
│   ├── test_llm_mode_switching.py
│   └── test_error_handling.py
├── performance/
│   └── test_estimation_speed.py
└── fixtures/
    └── test_data.yaml
```

**커버리지 목표**:
- Line Coverage: 80% 이상
- Branch Coverage: 70% 이상
- Critical Path: 100%

---

#### 9. 성능 최적화
**현재 성능**:
- Phase 0: <0.1초
- Phase 1: <0.5초
- Phase 2: 0.3-1초 (Validator 검색)
- Phase 3: 3-8초 (Source 수집 + 판단)
- Phase 4: 10-30초 (재귀 추정)

**병목 구간**:
1. Validator RAG 검색 (Embedding + 유사도 계산)
2. Phase 3 Source 수집 (API 호출)
3. Phase 4 LLM 모형 생성 (API 호출)
4. Phase 4 재귀 추정 (중첩 호출)

**개선 방안**:
```python
# 1. 캐싱
import functools
from cachetools import TTLCache

# Validator 결과 캐싱 (5분)
@functools.lru_cache(maxsize=100)
def search_definite_data(self, question: str, context: Context):
    """캐싱된 Validator 검색"""
    cache_key = (question, context.domain, context.region)
    if cache_key in self._cache:
        logger.debug(f"Cache hit: {question}")
        return self._cache[cache_key]
    
    result = self._do_search(question, context)
    self._cache[cache_key] = result
    return result

# 2. 병렬 처리
import asyncio

async def collect_all_parallel(self, question, context):
    """Source 병렬 수집"""
    tasks = [
        self._collect_physical(question, context),
        self._collect_value(question, context),
        self._collect_soft(question, context)
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # 성공한 결과만 반환
    return [r for r in results if not isinstance(r, Exception)]

# 3. Early Stopping
def estimate(self, question, context, confidence_threshold=0.9):
    """높은 신뢰도 발견 시 조기 종료"""
    
    # Phase 2에서 100% 신뢰도 발견
    result = self._search_validator(...)
    if result and result.confidence >= 0.95:
        logger.info("High confidence result → Early stop")
        return result
    
    # Phase 3 계속...
```

---

#### 10. 관찰성 (Observability) 강화
**목표**:
- 추정 과정 추적
- 성능 모니터링
- 에러 분석

**구현**:
```python
# 1. Metrics 수집
from prometheus_client import Counter, Histogram

estimation_counter = Counter(
    'estimator_requests_total',
    'Total estimation requests',
    ['phase', 'llm_mode', 'status']
)

estimation_duration = Histogram(
    'estimator_duration_seconds',
    'Estimation duration',
    ['phase']
)

def estimate(self, ...):
    start = time.time()
    
    try:
        result = self._do_estimate(...)
        estimation_counter.labels(
            phase=result.phase,
            llm_mode=self.llm_mode,
            status='success'
        ).inc()
        return result
    except Exception as e:
        estimation_counter.labels(
            phase=-1,
            llm_mode=self.llm_mode,
            status='error'
        ).inc()
        raise
    finally:
        duration = time.time() - start
        estimation_duration.labels(phase=result.phase if result else -1).observe(duration)

# 2. Tracing
import opentelemetry

@trace
def estimate(self, question: str, ...):
    """분산 추적"""
    span = trace.get_current_span()
    span.set_attribute("question", question)
    span.set_attribute("llm_mode", self.llm_mode)
    
    # ...
    
    span.set_attribute("result.phase", result.phase)
    span.set_attribute("result.confidence", result.confidence)
```

---

## 🎯 프로덕션 체크리스트

### Phase 0: 설계 & 아키텍처
- [ ] LLM Mode 동적 변경 지원
- [ ] Phase 간 llm_mode 일관성 보장
- [ ] Fallback 체계 정의
- [ ] 에러 처리 전략 수립

### Phase 1: 핵심 기능 구현
- [ ] Cursor 모드 Fallback 구현
- [ ] None 반환 제거 (항상 EstimationResult)
- [ ] Phase 3 증거 없을 때 Fallback
- [ ] Phase 4 모형 생성 Fallback

### Phase 2: 품질 보증
- [ ] 단위 테스트 (각 Phase 80% 커버리지)
- [ ] 통합 테스트 (전체 흐름)
- [ ] 엣지 케이스 테스트
- [ ] 성능 테스트 (<5초 목표)

### Phase 3: 안정성
- [ ] 구조화된 로깅
- [ ] 에러 추적 (Sentry 등)
- [ ] Metrics 수집 (Prometheus)
- [ ] Health Check 엔드포인트

### Phase 4: 운영 준비
- [ ] 문서화 (API Spec, 사용 가이드)
- [ ] 배포 파이프라인
- [ ] 모니터링 대시보드
- [ ] 알림 설정

---

## 📊 우선순위별 로드맵

### Sprint 1 (1주) - Critical Issues
**목표**: 핵심 동작 안정화
1. LLM Mode 동적 변경 지원
2. Cursor 모드 Fallback 구현
3. None 반환 제거
4. 구조화된 에러 로깅

**예상 공수**: 20시간

### Sprint 2 (1주) - High Priority
**목표**: Fallback 체계 완성
1. Phase 3 증거 없을 때 처리
2. Phase 4 모형 생성 Fallback
3. 단위 테스트 (Phase 0-2)
4. 통합 테스트 (기본 흐름)

**예상 공수**: 25시간

### Sprint 3 (1주) - Medium Priority
**목표**: 품질 & 성능
1. 테스트 커버리지 80%
2. 캐싱 구현
3. 병렬 처리 (Phase 3)
4. 성능 벤치마크

**예상 공수**: 20시간

### Sprint 4 (1주) - Production Ready
**목표**: 운영 준비
1. Metrics & Monitoring
2. 문서화
3. Health Check
4. 배포 자동화

**예상 공수**: 15시간

**총 예상 공수**: 80시간 (4주)

---

## 💡 Quick Wins (즉시 적용 가능)

### 1. LLM Mode Property (30분)
```python
@property
def llm_mode(self):
    return settings.llm_mode
```

### 2. Cursor Fallback (1시간)
```python
if self.llm_mode == "cursor" and phase >= 3:
    logger.info("Cursor → gpt-4o-mini Fallback")
    return self._estimate_with_mode(question, "gpt-4o-mini")
```

### 3. None 체크 추가 (30분)
```python
result = estimator.estimate(...)
if result is None:
    result = EstimationResult(phase=-1, value=0.0, error="추정 실패")
```

### 4. 상세 로깅 (1시간)
```python
logger.info(f"[Phase {phase}] {status}: {detail}")
```

**총 3시간으로 주요 문제 해결 가능!**

---

## 📌 권장 사항

### 즉시 조치
1. **LLM Mode Property 구현** (동적 변경 지원)
2. **Cursor 모드 Fallback** (자동화된 추정 가능)
3. **None 반환 제거** (안정성 향상)

### 단기 (1-2주)
4. **Phase 3-4 Fallback 강화** (실패율 감소)
5. **단위 테스트 80%** (품질 보증)
6. **구조화된 로깅** (디버깅 용이)

### 중기 (1개월)
7. **성능 최적화** (캐싱, 병렬화)
8. **통합 테스트** (전체 흐름 검증)
9. **Metrics 수집** (모니터링)

### 장기 (2-3개월)
10. **프로덕션 배포** (CI/CD, 모니터링)
11. **A/B 테스트** (Phase별 모델 비교)
12. **지속적 개선** (사용자 피드백 반영)

---

## 🎉 기대 효과

### 안정성
- ❌ 모든 Phase 실패 → None 반환
- ✅ Fallback으로 최소한의 추정 제공

### 사용성
- ❌ Cursor 모드에서 Phase 3-4 실패
- ✅ 자동 Fallback으로 모든 모드에서 작동

### 신뢰성
- ❌ 에러 원인 불명
- ✅ 구조화된 로깅으로 명확한 추적

### 성능
- ❌ 매번 전체 검색
- ✅ 캐싱으로 3-5배 속도 향상

**프로덕션 준비 완료!**




