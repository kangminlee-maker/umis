# Phase 3-4 구현 체크리스트 (v7.11.0)

> **목적**: v7.11.0 설계를 실제로 구현하기 위한 상세 작업 리스트
> **기간**: 5일 (+ 준비 1일, 정리 1일)
> **관련 문서**: `PHASE3_4_REDESIGN_PROPOSAL_v7_11_0.md`

---

## 0. 준비 작업 (Day 0)

### 0.1 현황 파악
- [ ] 기존 코드 의존성 분석
  - [ ] `phase3_guestimation.py` 호출 위치 파악
  - [ ] `phase4_fermi.py` 호출 위치 파악
  - [ ] `guardrail_analyzer.py` 사용처 확인
  - [ ] 다른 Agent들의 Estimator 사용 패턴 분석

- [ ] 기존 테스트 코드 확인
  ```bash
  find tests/ -name "*phase3*" -o -name "*phase4*" -o -name "*estimator*"
  ```

### 0.2 문서 작성
- [ ] `dev_docs/architecture/ESTIMATOR_DESIGN_PRINCIPLES_v7_11_0.md` 작성
  - [ ] 재귀 금지 원칙 명시
  - [ ] 공통 인터페이스 강제 규칙
  - [ ] 예산 기반 탐색 정책

- [ ] 마이그레이션 계획서 작성
  - [ ] 기존 API 호환성 유지 전략
  - [ ] Fallback 메커니즘 (v7.10.x 동작 보존)
  - [ ] 롤백 계획

### 0.3 브랜치 및 환경
- [ ] 새 브랜치 생성: `feature/v7.11.0-fusion-architecture`
- [ ] 기존 코드 백업
  ```bash
  cp -r umis_rag/agents/estimator umis_rag/agents/estimator.v7.10.2.backup
  ```

---

## 1. Day 1: 공통 인터페이스 + Evidence 계층

**목표**: 모든 추정 엔진이 사용할 공통 타입 정의 + Evidence 수집

### 1.1 models.py 업데이트

**파일**: `umis_rag/agents/estimator/models.py`

- [ ] `EstimationResult` 클래스 확장
  ```python
  @dataclass
  class EstimationResult:
      # 기존 필드 유지
      value: float
      value_range: Tuple[float, float]
      
      # 신규: certainty (confidence 대체)
      certainty: Literal['high', 'medium', 'low']  # 추가!
      
      # 신규: uncertainty (표준편차 느낌)
      uncertainty: float = 0.3  # 추가!
      
      # 신규: 비용 정보
      cost: Optional['Cost'] = None  # 추가!
      
      # 신규: Evidence 사용 정보
      used_evidence: Optional['Evidence'] = None  # 추가!
      
      # 신규: Fusion 가중치
      fusion_weights: Dict[str, float] = field(default_factory=dict)  # 추가!
      
      # 기존 confidence 필드는 deprecate (호환성 유지)
      confidence: float = 0.0  # @deprecated
  ```

- [ ] `Evidence` 클래스 정의
  ```python
  @dataclass
  class Evidence:
      """Stage 1: Evidence & Guardrails의 출력"""
      definite_value: Optional[float] = None
      hard_bounds: Tuple[float, float] = (0.0, float('inf'))
      logical_relations: List[str] = field(default_factory=list)
      soft_hints: List[str] = field(default_factory=list)
      source: str = "unknown"
  ```

- [ ] `Cost` 클래스 정의
  ```python
  @dataclass
  class Cost:
      """리소스 비용"""
      time_seconds: float = 0.0
      api_calls: int = 0
      tokens: int = 0
      estimated_cost_usd: float = 0.0
  ```

- [ ] 기존 코드와의 호환성
  - [ ] `confidence` → `certainty` 자동 변환 로직
  - [ ] 기존 테스트 코드 깨지지 않도록 보장

### 1.2 budget.py 구현

**파일**: `umis_rag/agents/estimator/budget.py` (신규)

```python
from dataclasses import dataclass, field
from typing import Literal
import time

@dataclass
class Budget:
    """
    추정에 사용할 수 있는 리소스 예산
    
    v7.11.0: confidence threshold 대신 명시적 예산 제어
    """
    # 최대 제약
    max_llm_calls: int = 10
    max_variables: int = 8
    max_runtime_seconds: float = 60.0
    
    # 현재 상태 (내부 관리)
    used_calls: int = 0
    used_variables: int = 0
    start_time: float = field(default_factory=time.time)
    
    def consume(self, resource_type: Literal['llm_call', 'variable'], amount: int = 1):
        """리소스 소비"""
        # TODO: 구현
        
    def exhausted(self) -> bool:
        """예산 소진 여부"""
        # TODO: 구현
        
    def remaining_variables(self) -> int:
        """남은 변수 추정 가능 횟수"""
        # TODO: 구현
        
    def remaining_time(self) -> float:
        """남은 시간 (초)"""
        # TODO: 구현
```

- [ ] `consume()` 구현
- [ ] `exhausted()` 구현
- [ ] `remaining_variables()` 구현
- [ ] `remaining_time()` 구현
- [ ] Budget 단위 테스트 작성

### 1.3 evidence_collector.py 구현

**파일**: `umis_rag/agents/estimator/evidence_collector.py` (신규)

```python
class EvidenceCollector:
    """
    Stage 1: Evidence & Guardrails
    
    Phase 0-2 + GuardrailAnalyzer를 통합하여
    확정 데이터와 하드 제약을 수집
    """
    
    def __init__(self):
        # Phase 0: Literal (project_data)
        # Phase 1: Direct RAG
        # Phase 2: Validator
        # GuardrailAnalyzer
        pass
    
    def collect(self, question: str, context: Context) -> Evidence:
        """Evidence 수집"""
        # TODO: 구현
        pass
```

- [ ] 스켈레톤 작성
- [ ] Phase 0: project_data 확인 로직
- [ ] Phase 1: Direct RAG 통합
- [ ] Phase 2: Validator 통합
- [ ] GuardrailAnalyzer 통합
  - [ ] 기존 `guardrail_analyzer.py` 코드 재사용
  - [ ] hard_bounds 추출 로직
  - [ ] logical_relations 추출 로직

### 1.4 Day 1 테스트

**파일**: `tests/unit/test_evidence_collector.py` (신규)

- [ ] Evidence 수집 기본 테스트
- [ ] hard_bounds 추출 검증
- [ ] definite_value 있을 때 즉시 반환 테스트
- [ ] Budget 소비 테스트

---

## 2. Day 2: Generative Prior (Stage 2)

**목표**: LLM 확신 기반 직접 추정 구현

### 2.1 prior_estimator.py 구현

**파일**: `umis_rag/agents/estimator/prior_estimator.py` (신규)

```python
class PriorEstimator:
    """
    Stage 2: Generative Prior
    
    LLM이 "확신있게 말할 수 있는 값"을 직접 추정
    """
    
    def __init__(self, llm_mode: str = "gpt-4o-mini"):
        self.llm_mode = llm_mode
        
    def estimate(
        self, 
        question: str, 
        hard_bounds: Tuple[float, float],
        budget: Budget
    ) -> EstimationResult:
        """
        확신 기반 직접 추정
        
        Args:
            question: 추정할 질문
            hard_bounds: Evidence에서 제공한 하드 제약
            budget: 리소스 예산
        """
        # TODO: 구현
        pass
```

#### 2.1.1 프롬프트 설계

- [ ] "확신 기반" 프롬프트 템플릿 작성
  ```python
  PROMPT_TEMPLATE = """
  질문: {question}
  
  당신이 확신있게 말할 수 있는 값을 제시하세요.
  정확한 근거가 없어도 괜찮습니다.
  상식적으로 합의된 범위, 또는 당신이 가장 그럴듯하다고
  생각하는 값을 제시하세요.
  
  제약: 값은 {min} ~ {max} 사이여야 합니다.
  
  출력 (JSON):
  {{
    "value": <가장 그럴듯한 값>,
    "range": [<최소>, <최대>],
    "certainty": "<high|medium|low>",
    "reasoning": "<간단한 추론 과정>"
  }}
  """
  ```

#### 2.1.2 certainty 판단 로직

- [ ] `_determine_certainty()` 함수 구현
  ```python
  def _determine_certainty(self, reasoning: str, range_width: float) -> str:
      """
      LLM의 reasoning과 range 폭을 보고 certainty 판단
      
      Rules:
      - range 폭 < 20%: high
      - "확실", "명확", "잘 알려진" 등 키워드: high
      - range 폭 > 100%: low
      - "추측", "대략" 등 키워드: low
      - 그 외: medium
      """
      # TODO: 구현
  ```

#### 2.1.3 hard_bounds 클리핑

- [ ] 값 생성 후 hard_bounds 내로 clipping
  ```python
  value = np.clip(llm_value, hard_bounds[0], hard_bounds[1])
  ```

#### 2.1.4 Budget 통합

- [ ] LLM 호출 전 budget.consume('llm_call', 1)
- [ ] 타임아웃 처리 (budget.remaining_time() 활용)

### 2.2 Day 2 테스트

**파일**: `tests/unit/test_prior_estimator.py` (신규)

- [ ] 기본 추정 테스트 (간단한 질문)
- [ ] certainty 레벨 일관성 테스트
  - [ ] "서울 인구"? → high
  - [ ] "특정 스타트업 매출"? → low
- [ ] hard_bounds 준수 테스트
- [ ] Budget 소비 검증

---

## 3. Day 3: Fermi 재설계 (Stage 3)

**목표**: 재귀 완전 제거 + Budget 기반 탐색

### 3.1 fermi_estimator.py 리팩토링

**파일**: `umis_rag/agents/estimator/fermi_estimator.py` (신규)

기존 `phase4_fermi.py`를 기반으로 리팩토링

#### 3.1.1 클래스 구조 변경

- [ ] `Phase4FermiDecomposition` → `FermiEstimator` 리네이밍
- [ ] 생성자 변경
  ```python
  def __init__(self, prior_estimator: PriorEstimator):
      self.prior_estimator = prior_estimator  # 의존성 주입!
      self.max_depth = 2  # 강제
      
      # v7.11.0: 정책 레벨 재귀 금지
      self._recursion_guard = False  # 재귀 감지용
  ```

#### 3.1.2 estimate() 메서드 재설계

- [ ] Budget 파라미터 추가
  ```python
  def estimate(
      self,
      question: str,
      evidence: Evidence,
      budget: Budget,
      depth: int = 0
  ) -> EstimationResult:
  ```

- [ ] max_depth 도달 또는 budget 소진 시 direct_estimate
  ```python
  if depth >= self.max_depth or budget.exhausted():
      return self._direct_estimate(question, budget)
  ```

- [ ] 변수 추정 시 재귀 호출 제거
  ```python
  # Before (v7.10.x) - 재귀 있음
  def _estimate_variable(self, var, depth):
      result = phase3.estimate(var)
      if result.confidence < threshold:
          return self.estimate(var, depth + 1)  # 재귀!
  
  # After (v7.11.0) - 재귀 없음
  def _estimate_variable(self, var, budget):
      return self._direct_estimate(var, budget)  # 재귀 없음!
  ```

#### 3.1.3 _direct_estimate() 구현

- [ ] PriorEstimator 호출
  ```python
  def _direct_estimate(self, question: str, budget: Budget) -> EstimationResult:
      """
      재귀 없이 직접 추정
      Stage 2 (PriorEstimator)와 동일한 메커니즘
      """
      # 재귀 감지 (정책 레벨 검증)
      if self._recursion_guard:
          raise RuntimeError("❌ 재귀 금지 위반! (v7.11.0 Design Principle)")
      
      self._recursion_guard = True
      try:
          result = self.prior_estimator.estimate(question, (0, inf), budget)
          return result
      finally:
          self._recursion_guard = False
  ```

#### 3.1.4 confidence threshold 로직 제거

- [ ] 모든 `if confidence < threshold` 분기 제거
- [ ] `_get_current_confidence_threshold()` 메서드 제거 또는 deprecate
- [ ] `max_global_attempts`, `_confidence_thresholds` 제거

#### 3.1.5 Budget 기반 변수 제한

- [ ] 변수 추정 루프에서 budget 확인
  ```python
  for var in model.variables[:budget.remaining_variables()]:
      budget.consume('variable', 1)
      var.value = self._direct_estimate(var.name, budget)
      
      if budget.exhausted():
          break  # 예산 소진 시 중단
  ```

### 3.2 재귀 감지 Assert 추가

- [ ] 모든 `estimate()` 호출 시작 부분에 assert
  ```python
  assert not self._recursion_guard, "재귀 호출 감지! (v7.11.0 위반)"
  ```

### 3.3 Day 3 테스트

**파일**: `tests/unit/test_fermi_estimator.py` (신규)

- [ ] 재귀 완전 제거 검증
  - [ ] `_recursion_guard` 트리거되는 케이스 없는지 확인
  - [ ] 모든 변수 추정이 `_direct_estimate()` 통과하는지 확인

- [ ] Budget 준수 테스트
  - [ ] max_variables 초과하지 않는지
  - [ ] max_runtime 초과하지 않는지

- [ ] "서울 음식점 수" 재실행 (이전 실패 케이스)
  - [ ] 60초 내 완료
  - [ ] 10회 이하 LLM 호출
  - [ ] 재귀 0회

---

## 4. Day 4: Fusion 레이어 (Stage 4)

**목표**: Evidence + Prior + Fermi를 센서 퓨전

### 4.1 fusion_layer.py 구현

**파일**: `umis_rag/agents/estimator/fusion_layer.py` (신규)

```python
class FusionLayer:
    """
    Stage 4: Fusion & Validation
    
    Evidence + Prior + Fermi를 weighted synthesis
    """
    
    def synthesize(
        self,
        evidence: Evidence,
        prior_result: EstimationResult,
        fermi_result: Optional[EstimationResult] = None
    ) -> EstimationResult:
        """
        모든 추정 결과를 합성
        
        Returns:
            최종 EstimationResult (fusion_weights 포함)
        """
        # TODO: 구현
```

#### 4.1.1 Weight 계산 함수

- [ ] `certainty_to_weight()` 구현
  ```python
  def certainty_to_weight(certainty: str) -> float:
      """
      certainty → weight 변환
      
      high: 1.0
      medium: 0.6
      low: 0.3
      """
      return {'high': 1.0, 'medium': 0.6, 'low': 0.3}[certainty]
  ```

- [ ] `range_to_weight()` 구현
  ```python
  def range_to_weight(value_range: Tuple[float, float]) -> float:
      """
      범위 폭 → weight 변환
      
      범위가 좁을수록 높은 weight
      """
      min_val, max_val = value_range
      if max_val == min_val:
          return 1.0
      
      relative_width = (max_val - min_val) / ((max_val + min_val) / 2)
      return 1.0 / (1.0 + relative_width)
  ```

#### 4.1.2 Weighted Synthesis

- [ ] 가중 평균 계산
  ```python
  candidates = [prior_result, fermi_result] if fermi_result else [prior_result]
  
  weighted_values = []
  weights = []
  
  for result in candidates:
      # Guardrail 밖이면 clip
      v = np.clip(result.value, evidence.hard_bounds[0], evidence.hard_bounds[1])
      
      # Weight 계산
      w = (
          certainty_to_weight(result.certainty) *
          range_to_weight(result.value_range)
      )
      
      weighted_values.append(v)
      weights.append(w)
  
  final_value = np.average(weighted_values, weights=weights)
  ```

#### 4.1.3 Range Intersection

- [ ] 범위 교차 로직
  ```python
  def _intersect_ranges(self, ranges: List[Tuple[float, float]]) -> Tuple[float, float]:
      """
      여러 범위의 교집합
      
      Example:
        [100, 200], [150, 250], [0, 500]
        → [150, 200] (교집합)
      """
      lower = max(r[0] for r in ranges)
      upper = min(r[1] for r in ranges)
      
      if lower > upper:
          # 교집합 없음 → 가장 넓은 범위 반환
          return (min(r[0] for r in ranges), max(r[1] for r in ranges))
      
      return (lower, upper)
  ```

#### 4.1.4 Sanity Check

- [ ] 물리적 제약 검증
  ```python
  def _sanity_check(self, value: float, evidence: Evidence) -> Tuple[bool, str]:
      """
      최종 값이 물리적으로 말이 되는지 검증
      
      Returns:
          (pass: bool, message: str)
      """
      # 1. 음수 불가능한 경우
      if value < 0 and "count" in evidence.source.lower():
          return False, "Count cannot be negative"
      
      # 2. 100% 초과 불가능한 경우
      if value > 1.0 and "rate" in evidence.source.lower():
          return False, "Rate cannot exceed 100%"
      
      # 3. logical_relations 검증
      for relation in evidence.logical_relations:
          # TODO: 관계식 파싱 및 검증
          pass
      
      return True, "Pass"
  ```

### 4.2 Day 4 테스트

**파일**: `tests/unit/test_fusion_layer.py` (신규)

- [ ] 가중 평균 계산 정확도 테스트
- [ ] Range intersection 로직 테스트
- [ ] Guardrail clipping 테스트
- [ ] Sanity check 테스트 (음수, 100% 초과 등)
- [ ] fusion_weights 출력 검증

---

## 5. Day 5: 통합 및 검증

**목표**: 4개 Stage를 하나로 통합 + 전체 흐름 검증

### 5.1 estimator.py 통합

**파일**: `umis_rag/agents/estimator/estimator.py` (기존 파일 수정)

#### 5.1.1 4-Stage 통합

- [ ] `estimate()` 메서드 재작성
  ```python
  def estimate(self, question: str, context: Context) -> EstimationResult:
      """
      v7.11.0: 4-Stage Architecture
      """
      # Budget 초기화
      budget = Budget(
          max_llm_calls=10,
          max_variables=8,
          max_runtime_seconds=60.0
      )
      
      # Stage 1: Evidence & Guardrails
      evidence = self.evidence_collector.collect(question, context)
      
      # 확정 값 있으면 즉시 반환 (Fast path)
      if evidence.definite_value is not None:
          return EstimationResult(
              value=evidence.definite_value,
              certainty='high',
              cost=Cost(time=0.1, calls=0)
          )
      
      # Stage 2: Direct Prior (항상 실행)
      prior_result = self.prior_estimator.estimate(
          question, 
          evidence.hard_bounds,
          budget
      )
      
      # Stage 3: Fermi (예산 있고, 복잡한 질문이면)
      fermi_result = None
      if not budget.exhausted() and self._should_use_fermi(question):
          fermi_result = self.fermi_estimator.estimate(
              question,
              evidence,
              budget
          )
      
      # Stage 4: Fusion (항상 실행)
      return self.fusion_layer.synthesize(
          evidence,
          prior_result,
          fermi_result
      )
  ```

#### 5.1.2 _should_use_fermi() 구현

- [ ] 질문 복잡도 분석
  ```python
  def _should_use_fermi(self, question: str) -> bool:
      """
      Fermi 사용 여부 결정
      
      Rules:
      - 숫자가 매우 큰 경우 (> 1M)
      - "수는?" 같은 counting 질문
      - 사용자가 명시적으로 요청
      """
      # 간단한 휴리스틱
      if any(word in question.lower() for word in ['몇 개', '수는', '몇 명']):
          return True
      
      return False
  ```

### 5.2 통합 테스트

**파일**: `tests/integration/test_v7_11_0_integration.py` (신규)

#### 5.2.1 10개 질문 테스트

- [ ] 간단한 질문 (Fast path)
  - [ ] "대한민국 인구는?"
  - [ ] "서울 인구는?"

- [ ] Prior만으로 충분한 질문
  - [ ] "SaaS Churn Rate는?"
  - [ ] "음식점 평균 마진은?"

- [ ] Fermi 필요한 질문
  - [ ] "서울 음식점 수는?"
  - [ ] "한국 스타트업 수는?"

- [ ] 복잡한 질문
  - [ ] "서울 지역 SaaS 기업의 평균 LTV는?"

#### 5.2.2 이전 실패 케이스 재실행

- [ ] "서울 음식점 수는?" (재귀 폭발 케이스)
  - [ ] 실행 시간 < 60초
  - [ ] LLM 호출 < 10회
  - [ ] 재귀 호출 0회
  - [ ] 값이 합리적 범위 내 (10만~50만)

#### 5.2.3 Before/After 비교

**파일**: `tests/integration/test_v7_11_0_benchmark.py` (신규)

- [ ] 50개 질문 준비 (기존 Phase 4 테스트 세트)
- [ ] v7.10.2 vs v7.11.0 비교
  ```python
  def compare_versions():
      questions = load_test_questions(50)
      
      # v7.10.2 실행 (기존 코드)
      v10_results = run_v7_10_2(questions)
      
      # v7.11.0 실행 (새 코드)
      v11_results = run_v7_11_0(questions)
      
      # 비교
      comparison = {
          'time': {
              'v7.10.2': np.percentile([r.time for r in v10_results], [50, 95, 99]),
              'v7.11.0': np.percentile([r.time for r in v11_results], [50, 95, 99])
          },
          'calls': {
              'v7.10.2': np.mean([r.calls for r in v10_results]),
              'v7.11.0': np.mean([r.calls for r in v11_results])
          },
          'cost': { ... },
          'accuracy': { ... }
      }
      
      return comparison
  ```

#### 5.2.4 Ablation 테스트

- [ ] Evidence only
  - [ ] Fusion Layer에 prior/fermi 없이 호출
  - [ ] Guardrail 범위만으로 결과 생성

- [ ] Evidence + Prior
  - [ ] Fermi 없이 Prior만 사용
  - [ ] 정확도 측정

- [ ] Evidence + Prior + Fermi
  - [ ] 전체 시스템 사용
  - [ ] 각 Stage 기여도 분석

### 5.3 성능 모니터링

**파일**: `tests/integration/test_v7_11_0_performance.py` (신규)

- [ ] 1000회 반복 실행
  - [ ] max_llm_calls 초과 횟수 = 0
  - [ ] max_runtime 초과 횟수 = 0
  - [ ] 재귀 호출 발생 = 0

- [ ] Tail latency 분석
  - [ ] P50, P95, P99 측정
  - [ ] 최악의 경우 < 60초 보장

---

## 6. 정리 및 문서화

### 6.1 기존 코드 마이그레이션 표시

- [ ] `phase3_guestimation.py`에 deprecation 노트 추가
  ```python
  """
  @deprecated: v7.11.0
  이 파일은 prior_estimator.py로 마이그레이션되었습니다.
  호환성을 위해 유지되지만, 새 코드에서는 사용하지 마세요.
  """
  ```

- [ ] `phase4_fermi.py`에 deprecation 노트 추가

### 6.2 테스트 코드 업데이트

- [ ] 기존 테스트 중 깨진 것 수정
  ```bash
  pytest tests/unit/test_phase3*.py tests/unit/test_phase4*.py
  ```

- [ ] 새 인터페이스 적용

### 6.3 문서 작성

- [ ] `dev_docs/improvements/V7_11_0_IMPLEMENTATION_COMPLETE.md` 작성
  - [ ] 구현 완료 항목
  - [ ] 성능 개선 결과 (Before/After)
  - [ ] 알려진 제약사항
  - [ ] 향후 개선 방향

- [ ] README 업데이트
  - [ ] v7.11.0 아키텍처 설명 추가
  - [ ] 사용 예제 업데이트

### 6.4 PR 준비

- [ ] Git commit 정리
  ```bash
  git log --oneline feature/v7.11.0-fusion-architecture
  ```

- [ ] PR 템플릿 작성
  ```markdown
  ## v7.11.0: Fusion Architecture
  
  ### Summary
  - 재귀 폭발 완전 제거
  - 4-Stage 아키텍처 (Evidence → Prior → Fermi → Fusion)
  - 95% 시간 단축, 90% 비용 절감
  
  ### Breaking Changes
  - EstimationResult에 certainty 필드 추가
  - confidence는 deprecated
  
  ### Test Results
  - Before: 15분, $20-30, 100회+ 호출
  - After: 30-60초, $1-2, 5-10회 호출
  ```

---

## 7. 성공 기준 (최종 검증)

### 필수 (Must-have)
- [ ] ✅ 재귀 완전 제거 (0% tolerance)
- [ ] ✅ 응답 시간 < 60초 (P95)
- [ ] ✅ API 호출 < 10회 (평균)

### 목표 (Should-have)
- [ ] 정확도 유지 (오차 < 2x)
- [ ] 비용 < $2/query
- [ ] 병렬화 가능 (Stage 2/3 독립 실행)

### 선택 (Nice-to-have)
- [ ] 실행 시간 < 30초 (P50)
- [ ] 정확도 향상 (일부 질문)

---

## 8. 체크포인트 (세션 간 연속성)

각 Day 종료 시:

1. **코드 커밋**
   ```bash
   git add .
   git commit -m "v7.11.0 Day N: [작업 내용]"
   git push origin feature/v7.11.0-fusion-architecture
   ```

2. **진행 상황 기록**
   - [ ] 이 체크리스트 업데이트
   - [ ] 막힌 부분 / 해결책 메모
   - [ ] 다음 세션 시작 포인트 명시

3. **테스트 결과 저장**
   ```bash
   pytest > test_results_day_N.txt
   ```

---

## 부록: 파일 구조 (v7.11.0)

```
umis_rag/agents/estimator/
├── models.py                # EstimationResult, Evidence, Budget 정의
├── budget.py                # [신규] Budget 클래스
│
├── evidence_collector.py    # [신규] Stage 1: Evidence & Guardrails
├── prior_estimator.py       # [신규] Stage 2: Generative Prior
├── fermi_estimator.py       # [신규] Stage 3: Structural Explanation
├── fusion_layer.py          # [신규] Stage 4: Fusion & Validation
│
├── estimator.py             # [수정] 4-Stage 통합 Estimator
│
├── phase3_guestimation.py   # [deprecated] → prior_estimator.py
├── phase4_fermi.py          # [deprecated] → fermi_estimator.py
└── guardrail_analyzer.py    # [마이그레이션] → evidence_collector.py

tests/
├── unit/
│   ├── test_evidence_collector.py  # [신규]
│   ├── test_prior_estimator.py     # [신규]
│   ├── test_fermi_estimator.py     # [신규]
│   └── test_fusion_layer.py        # [신규]
│
└── integration/
    ├── test_v7_11_0_integration.py   # [신규] 전체 흐름
    ├── test_v7_11_0_benchmark.py     # [신규] Before/After
    └── test_v7_11_0_performance.py   # [신규] 1000회 반복

dev_docs/
├── architecture/
│   └── ESTIMATOR_DESIGN_PRINCIPLES_v7_11_0.md  # [신규]
│
└── improvements/
    ├── PHASE3_4_REDESIGN_PROPOSAL_v7_11_0.md   # [기존]
    ├── PHASE3_4_IMPLEMENTATION_CHECKLIST_v7_11_0.md  # [현재 문서]
    └── V7_11_0_IMPLEMENTATION_COMPLETE.md      # [완료 후 작성]
```

---

*체크리스트 끝*

**다음 세션 시작 시**:
1. 이 문서 열기
2. 마지막 체크포인트 확인
3. 다음 Day 작업 시작
