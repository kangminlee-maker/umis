# Estimator Single Source of Truth 설계

**작성일**: 2025-11-07  
**업데이트**: 2025-11-07 23:30  
**원칙**: 모든 값 추정은 Estimator에게 위임  
**이유**: 데이터 일관성 (여러 Agent가 추정하면 무너짐)  
**우선순위**: P0 (Critical!)  
**상태**: v7.3.1 배포 후 v7.3.2로 구현

---

## 🎯 핵심 원칙

### Single Source of Truth for Value Estimation

```yaml
원칙:
  "모든 값/데이터 추정은 Estimator (Fermi) Agent만 수행한다"

정확한 의미:
  "추정 금지" = "데이터/값 추정 금지"
  
  금지: 값/데이터 직접 추정, 근사값 생성, 기본값, 하드코딩
  허용: 확정 데이터, 계산, 검증, 검색, Estimator 호출

참조: dev_docs/ESTIMATION_POLICY_CLARIFICATION.md

이유:
  1. 데이터 일관성
     - 같은 질문 → 같은 답
     - 여러 Agent가 다른 방법으로 추정 → 불일치!
  
  2. 학습 시스템 효율
     - 모든 추정이 한 곳에 축적
     - Tier 2 → Tier 1 학습
     - 재사용 극대화
  
  3. 근거 추적
     - 추정값의 출처 명확
     - Decomposition 이력
     - 재현 가능성

적용:
  ✅ Quantifier: 계산 OK, 추정 NO → Estimator 호출
  ✅ Validator: 검증 OK, 추정 NO → Estimator 호출
  ✅ Observer: 관찰 OK, 추정 NO → Estimator 호출
  ✅ Explorer: 가설 OK, 추정 NO → Estimator 호출
  ✅ Guardian: 평가 OK, 추정 NO → Estimator 호출
  ✅ Estimator: 추정 OK (유일한 권한)

결론 (MECE 분석):
  - Validator + Estimator 통합 검토 → 분리 유지 권장 (92% vs 60%)
  - 본질적 차이: Validation (확인) vs Estimation (생성)
  - 검색 중복은 문제 아님 (도구 공유, 목적 다름)
  
참조: dev_docs/VALIDATOR_ESTIMATOR_MERGE_ANALYSIS.md
```

---

## 📋 필요한 변경사항

### 1. EstimationResult 확장 (Critical!)

```python
# umis_rag/agents/estimator/models.py

@dataclass
class EstimationResult:
    """최종 추정 결과"""
    
    question: str
    
    # 최종 값
    value: Optional[float] = None
    value_range: Optional[Tuple[float, float]] = None
    unit: str = ""
    
    # 메타 정보
    tier: int = 0
    confidence: float = 0.0
    uncertainty: float = 0.3
    
    # 기존 필드들...
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # NEW: 추정 근거 및 Decomposition ⭐
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    # 추정 근거
    reasoning_detail: Dict[str, Any] = field(default_factory=dict)
    # {
    #   'method': 'weighted_average',
    #   'sources_used': ['statistical_pattern', 'rag_benchmark'],
    #   'why_this_method': '증거 3개, 신뢰도 높음'
    # }
    
    # Decomposition (분해 과정)
    decomposition: Optional['DecompositionTrace'] = None
    # Fermi처럼 분해했다면 기록
    # 예: ARPU = 월결제액 / 활성사용자
    #     월결제액 = 10,000원 (추정)
    #     활성사용자 = 1,000명 (추정)
    
    # 개별 요소 추정 논리
    component_estimations: List['ComponentEstimation'] = field(default_factory=list)
    # 분해된 각 요소의 추정 로직
    
    # 추적 가능성
    estimation_trace: List[str] = field(default_factory=list)
    # 추정 과정의 스텝별 기록


@dataclass
class DecompositionTrace:
    """
    Decomposition 추적
    
    Fermi처럼 분해한 경우의 이력
    """
    formula: str  # "ARPU = 월결제액 / 활성사용자"
    variables: Dict[str, 'EstimationResult']  # 각 변수의 추정 결과
    calculation_logic: str  # 계산 논리 설명
    depth: int = 0  # 재귀 깊이


@dataclass  
class ComponentEstimation:
    """
    개별 요소의 추정 논리
    
    예: "월결제액 = 10,000원"을 어떻게 추정했는지
    """
    component_name: str  # "월결제액"
    component_value: float  # 10,000
    estimation_method: str  # "statistical_pattern"
    reasoning: str  # "SaaS 평균 요금 분포"
    confidence: float  # 0.75
    sources: List[str]  # ["rag_benchmark", "soft_constraint"]
```

---

### 2. Quantifier 완전 위임 정책

```python
# umis_rag/agents/quantifier.py

class QuantifierRAG:
    """
    역할 명확화:
    - 계산 방법론 선택 (어떻게 계산?)
    - 데이터 수집 (어디서?)
    - 공식 적용 (계산)
    
    금지:
    - 값 추정 ❌
    - 근사값 산정 ❌
    
    위임:
    - 모든 값 추정 → Estimator
    """
    
    def calculate_sam(
        self,
        market: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        SAM 계산
        
        원칙:
        -----
        1. 데이터 있음 → 계산
        2. 데이터 없음 → Estimator 호출 (필수!)
        3. 추정 금지 (직접 추정 ❌)
        """
        logger.info(f"[Quantifier] SAM 계산: {market}")
        
        # 방법론 선택
        methodology = self._select_methodology(market)
        
        # 필요 변수 확인
        required_vars = self._get_required_variables(methodology)
        
        # 데이터 수집
        collected_data = {}
        missing_vars = []
        
        for var in required_vars:
            if var in data:
                collected_data[var] = data[var]
                logger.info(f"  ✅ {var}: {data[var]} (제공됨)")
            else:
                missing_vars.append(var)
                logger.info(f"  ❌ {var}: 없음")
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 핵심: 데이터 부족 시 Estimator 호출 (필수!)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        if missing_vars:
            logger.info(f"  🔍 Estimator에게 {len(missing_vars)}개 변수 추정 요청")
            
            estimator = get_estimator_rag()
            
            for var in missing_vars:
                # Estimator에게 위임 (직접 추정 금지!)
                question = self._variable_to_question(var, market)
                
                est_result = estimator.estimate(
                    question=question,
                    domain=self._infer_domain(market),
                    region=data.get('region')
                )
                
                if est_result:
                    collected_data[var] = est_result.value
                    
                    # 추정 근거 기록 ⭐
                    collected_data[f'{var}_estimation'] = {
                        'value': est_result.value,
                        'confidence': est_result.confidence,
                        'tier': est_result.tier,
                        'reasoning': est_result.reasoning,
                        'decomposition': est_result.decomposition,  # NEW!
                        'components': est_result.component_estimations  # NEW!
                    }
                    
                    logger.info(f"  ✅ {var}: {est_result.value} (Estimator, 신뢰도 {est_result.confidence:.0%})")
                else:
                    logger.error(f"  ❌ {var} 추정 실패")
                    return {'error': f'{var} 추정 불가'}
        
        # 계산 (모든 데이터 확보 후)
        result = self._apply_formula(methodology, collected_data)
        
        # 결과에 추정 근거 포함 ⭐
        result['estimations_used'] = {
            var: collected_data.get(f'{var}_estimation')
            for var in missing_vars
        }
        
        return result
```

---

### 3. Validator Estimator 통합

```python
# umis_rag/agents/validator.py

class ValidatorRAG:
    """
    역할 명확화:
    - 정의 검증 (무엇을 측정?)
    - 소스 검증 (어디서 구할?)
    - 신뢰도 평가
    
    금지:
    - 값 추정 ❌
    
    협업:
    - Estimator: 추정치 합리성 검증 요청
    """
    
    def __init__(self):
        # 기존 초기화...
        
        # Estimator 연결
        self.estimator = None  # Lazy
    
    def validate_estimation(
        self,
        question: str,
        claimed_value: float,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        추정값의 합리성 검증
        
        원칙:
        -----
        1. 직접 추정 금지 ❌
        2. Estimator에게 교차 검증 요청 ✅
        3. 비교 및 판단
        
        Args:
            question: 질문
            claimed_value: 주장된 값
            context: 맥락
        
        Returns:
            검증 결과 + Estimator 교차 검증
        """
        logger.info(f"[Validator] 추정값 검증: {question} = {claimed_value}")
        
        # Estimator에게 교차 검증 요청
        if self.estimator is None:
            self.estimator = get_estimator_rag()
        
        est_result = self.estimator.estimate(
            question=question,
            domain=context.get('domain') if context else None
        )
        
        if not est_result:
            return {
                'validation': 'unable',
                'reason': 'Estimator 추정 실패'
            }
        
        # 비교
        diff_pct = abs(claimed_value - est_result.value) / est_result.value
        
        validation = {
            'claimed_value': claimed_value,
            'estimator_value': est_result.value,
            'estimator_confidence': est_result.confidence,
            'estimator_reasoning': est_result.reasoning_detail,  # NEW!
            'estimator_decomposition': est_result.decomposition,  # NEW!
            'difference_pct': diff_pct,
            
            'validation_result': (
                'pass' if diff_pct < 0.30 else
                'caution' if diff_pct < 0.50 else
                'fail'
            ),
            
            'recommendation': (
                f"Estimator 추정: {est_result.value} (신뢰도 {est_result.confidence:.0%})\n"
                f"주장값과 차이: {diff_pct:.0%}\n"
                f"근거: {est_result.reasoning}"
            )
        }
        
        return validation
```

---

### 4. 추정 근거 제공 메커니즘

```python
# umis_rag/agents/estimator/tier2.py

class Tier2JudgmentPath:
    
    def estimate(
        self,
        question: str,
        context: Optional[Context] = None
    ) -> Optional[EstimationResult]:
        """
        Tier 2 추정 (근거 포함 필수!)
        """
        # ... 기존 로직 ...
        
        # 결과 생성
        result = EstimationResult(
            question=question,
            tier=2,
            value=judgment['value'],
            
            # ... 기존 필드 ...
            
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            # NEW: 추정 근거 상세 ⭐
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            reasoning_detail={
                'method': judgment['strategy'],
                'sources_used': [est.source_type.value for est in value_estimates],
                'evidence_count': len(value_estimates),
                'why_this_method': self._explain_strategy(judgment['strategy']),
                
                # 각 증거의 상세
                'evidence_breakdown': [
                    {
                        'source': est.source_type.value,
                        'value': est.value,
                        'confidence': est.confidence,
                        'reasoning': est.reasoning,
                        'raw_data': est.raw_data
                    }
                    for est in value_estimates
                ],
                
                # 판단 과정
                'judgment_process': [
                    f"1. {len(value_estimates)}개 증거 수집",
                    f"2. 전략 선택: {judgment['strategy']}",
                    f"3. 계산: {judgment['reasoning']}",
                    f"4. 신뢰도: {judgment['confidence']:.0%}"
                ]
            },
            
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            # NEW: Decomposition (있다면) ⭐
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            decomposition=self._create_decomposition_trace(
                question, value_estimates, context
            ),
            
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            # NEW: 개별 요소 추정 ⭐
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            component_estimations=[
                ComponentEstimation(
                    component_name=est.source_type.value,
                    component_value=est.value,
                    estimation_method=est.source_type.value,
                    reasoning=est.reasoning,
                    confidence=est.confidence,
                    sources=[est.source_detail] if est.source_detail else []
                )
                for est in value_estimates
            ],
            
            # 추적 가능성
            estimation_trace=self._build_trace(value_estimates)
        )
        
        return result
    
    def _explain_strategy(self, strategy: str) -> str:
        """전략 선택 이유 설명"""
        explanations = {
            'weighted_average': '증거들의 신뢰도가 비슷하여 가중 평균 적용',
            'conservative': '의사결정용이므로 보수적 하한 선택',
            'range': '증거 분산이 커서 범위로 제시',
            'single_best': '하나의 증거가 압도적으로 신뢰도 높음'
        }
        return explanations.get(strategy, strategy)
    
    def _create_decomposition_trace(
        self,
        question: str,
        estimates: List,
        context: Context
    ) -> Optional[DecompositionTrace]:
        """
        Decomposition 이력 생성
        
        예: "ARPU는?" → "월결제액 / 활성사용자"
        각 요소를 재귀적으로 추정했다면 기록
        """
        # TODO: Tier 3 (Fermi) 통합 시 구현
        return None
    
    def _build_trace(self, estimates: List) -> List[str]:
        """추정 과정 추적"""
        trace = []
        trace.append(f"맥락 파악 완료")
        trace.append(f"{len(estimates)}개 Source 수집 완료")
        
        for est in estimates:
            trace.append(
                f"  - {est.source_type.value}: {est.value} "
                f"(신뢰도 {est.confidence:.0%})"
            )
        
        trace.append(f"종합 판단 완료")
        
        return trace
```

---

### 5. Quantifier 추정 로직 제거

```python
# umis_rag/agents/quantifier.py

class QuantifierRAG:
    
    # ❌ 제거할 메서드들 (직접 추정)
    # def _estimate_arpu(self, ...):  # 삭제!
    # def _guess_churn_rate(self, ...):  # 삭제!
    # def _approximate_market_size(self, ...):  # 삭제!
    
    # ✅ 유지할 메서드들 (계산)
    def calculate_sam(self, ...):  # OK (계산)
    def search_methodology(self, ...):  # OK (검색)
    def search_benchmark(self, ...):  # OK (검색)
    
    # ✅ 추가할 원칙
    def _ensure_data(self, var_name: str, data: Dict) -> float:
        """
        데이터 확보 (없으면 Estimator 호출)
        
        원칙: 직접 추정 금지!
        """
        if var_name in data:
            return data[var_name]
        
        # Estimator에게 위임
        logger.info(f"  🔍 Estimator 호출: {var_name}")
        
        estimator = get_estimator_rag()
        result = estimator.estimate(
            question=f"{var_name}는?",
            domain=data.get('domain')
        )
        
        if not result:
            raise ValueError(f"{var_name} 추정 실패")
        
        # 근거 기록 ⭐
        data[f'{var_name}_estimation_detail'] = {
            'value': result.value,
            'confidence': result.confidence,
            'reasoning': result.reasoning_detail,  # 상세 근거
            'decomposition': result.decomposition,  # 분해 과정
            'components': result.component_estimations,  # 개별 요소
            'trace': result.estimation_trace  # 추적
        }
        
        return result.value
```

---

### 6. 정책 검증 메커니즘

```python
# umis_rag/agents/estimator/policy.py (신규)

class EstimationPolicy:
    """
    추정 정책 검증
    
    Single Source of Truth 원칙 강제
    """
    
    @staticmethod
    def validate_caller(caller_agent: str):
        """
        호출자 검증
        
        Estimator만 값 추정 가능
        다른 Agent는 금지
        """
        allowed_callers = [
            'estimator',  # 자기 자신
            'quantifier',  # Estimator 호출 (위임)
            'validator',   # Estimator 호출 (교차 검증)
            'observer',    # Estimator 호출 (비율 추정)
            'explorer',    # Estimator 호출 (시장 크기)
        ]
        
        if caller_agent not in allowed_callers:
            raise PermissionError(
                f"{caller_agent}는 값 추정 불가. "
                f"Estimator.estimate()를 호출하세요."
            )
    
    @staticmethod
    def ensure_reasoning_provided(result: EstimationResult):
        """
        근거 제공 강제
        
        추정 결과에 반드시 근거 포함
        """
        if not result.reasoning_detail:
            raise ValueError("추정 근거(reasoning_detail) 필수!")
        
        required_keys = ['method', 'sources_used', 'evidence_breakdown']
        
        for key in required_keys:
            if key not in result.reasoning_detail:
                raise ValueError(f"근거에 {key} 필수!")
        
        logger.info("  ✅ 추정 근거 완전성 검증 통과")
```

---

## 📊 변경 영향 분석

### 코드 변경

```yaml
신규 생성:
  - models.py: DecompositionTrace, ComponentEstimation 추가
  - estimator/policy.py (신규, 200줄)

수정 필요:
  - tier2.py: reasoning_detail, decomposition, components 추가
  - quantifier.py: 직접 추정 로직 제거, _ensure_data() 추가
  - validator.py: validate_estimation() 추가, Estimator 통합

테스트:
  - test_single_source_policy.py (신규)
  - test_reasoning_detail.py (신규)
  - 기존 테스트 업데이트

예상: 2-3시간
```

### 문서 변경

```yaml
필수:
  1. ✅ ESTIMATOR_SINGLE_SOURCE_DESIGN.md (이 문서)
  2. ✅ Agent 문서 (quantifier.py, validator.py docstring)
  3. ✅ UMIS_ARCHITECTURE_BLUEPRINT.md (원칙 명시)

선택:
  4. AGENT_COLLABORATION_GUIDE.md
  5. ESTIMATION_REASONING_SPEC.md
```

---

## 🎯 구현 우선순위

### Phase 1: 데이터 모델 확장 (1시간)

```yaml
✅ EstimationResult 확장
  - reasoning_detail (Dict)
  - decomposition (DecompositionTrace)
  - component_estimations (List)
  - estimation_trace (List)

✅ 새 클래스 추가
  - DecompositionTrace
  - ComponentEstimation
```

### Phase 2: Tier 2 근거 제공 (1시간)

```yaml
✅ tier2.py 수정
  - reasoning_detail 생성
  - _explain_strategy()
  - _build_trace()
  - component_estimations 생성

✅ 테스트
  - 근거 완전성 검증
```

### Phase 3: Quantifier 완전 위임 (30분)

```yaml
✅ quantifier.py 수정
  - 직접 추정 로직 제거 (있다면)
  - _ensure_data() 구현
  - 추정 근거 기록

✅ 테스트
  - 위임 동작 확인
```

### Phase 4: Validator 통합 (30분)

```yaml
✅ validator.py 수정
  - validate_estimation() 추가
  - Estimator 연결

✅ 테스트
  - 교차 검증 동작
```

### Phase 5: 정책 검증 (선택, 30분)

```yaml
⏳ policy.py 신규 (선택)
  - validate_caller()
  - ensure_reasoning_provided()

⏳ 테스트
  - 정책 강제 확인
```

---

## ⚠️ Critical Issues

### Issue 1: 기존 코드에 직접 추정 로직 있는가?

```yaml
확인 필요:
  - Quantifier에 직접 추정 코드
  - Validator에 직접 추정 코드
  - Observer, Explorer에 추정 코드

조치:
  있으면 → Estimator 호출로 대체
  없으면 → OK (정책만 명시)
```

### Issue 2: Decomposition 복잡도

```yaml
현재:
  - Tier 2: 단순 값 추정
  - Decomposition 없음

미래 (Tier 3):
  - Fermi Decomposition
  - 재귀적 분해
  - 복잡한 이력

해결:
  Phase 1-2: reasoning_detail만 (간단)
  Phase 3: decomposition 추가 (Tier 3 준비)
```

### Issue 3: 성능 영향

```yaml
우려:
  - 근거 생성 오버헤드
  - 메모리 사용량

완화:
  - Lazy 생성 (요청 시만)
  - 간결한 구조
  - 측정: 예상 +0.1초 (무시 가능)
```

---

## 📋 작업 단계 (5단계)

### Step 1: 데이터 모델 확장 (1시간)

```python
models.py:
  - reasoning_detail: Dict 필드 추가
  - decomposition: DecompositionTrace 추가
  - component_estimations: List 추가
  - estimation_trace: List 추가
  - DecompositionTrace 클래스
  - ComponentEstimation 클래스
```

### Step 2: Tier 2 근거 생성 (1시간)

```python
tier2.py:
  - _explain_strategy() 메서드
  - _build_trace() 메서드
  - reasoning_detail 생성
  - component_estimations 생성
```

### Step 3: Quantifier 검증 및 위임 (30분)

```python
quantifier.py:
  - 직접 추정 코드 검색 및 제거
  - _ensure_data() 구현
  - 추정 근거 기록
  - 문서 업데이트
```

### Step 4: Validator 통합 (30min)

```python
validator.py:
  - validate_estimation() 추가
  - Estimator import
  - 교차 검증 로직
```

### Step 5: 정책 문서화 (30min)

```yaml
문서:
  - ESTIMATOR_SINGLE_SOURCE_DESIGN.md
  - Agent docstring 업데이트
  - UMIS_ARCHITECTURE_BLUEPRINT.md 원칙 추가
```

---

## 🎊 최종 구조

### Estimator의 책임

```yaml
유일한 추정 권한:
  ✅ 모든 값 추정
  ✅ 증거 수집
  ✅ 종합 판단
  ✅ 학습 시스템

필수 제공:
  ✅ 추정값 (value)
  ✅ 신뢰도 (confidence)
  ✅ 상세 근거 (reasoning_detail) ⭐
  ✅ 증거 분해 (evidence_breakdown) ⭐
  ✅ Decomposition (있다면) ⭐
  ✅ 개별 요소 논리 (component_estimations) ⭐
  ✅ 추적 이력 (estimation_trace) ⭐
```

### 다른 Agent의 책임

```yaml
Quantifier:
  ✅ 계산 (데이터 있을 때)
  ✅ 방법론 선택
  ❌ 추정 금지 → Estimator 호출

Validator:
  ✅ 정의 검증
  ✅ 소스 검증
  ❌ 추정 금지 → Estimator 호출

협업:
  모든 Agent → Estimator (필요 시)
  Estimator → 근거 포함 EstimationResult 반환
```

---

## 💡 예상 효과

### 1. 데이터 일관성

```yaml
Before (위험):
  Quantifier: "Churn Rate = 5%" (자체 추정)
  Estimator: "Churn Rate = 6%" (다른 방법)
  → 불일치! ⚠️

After (안전):
  Quantifier → Estimator 호출
  Estimator: "Churn Rate = 6%"
  → 일관성! ✅

효과:
  - 같은 질문 → 같은 답
  - 추정 이력 공유
  - 학습 효율 ↑
```

### 2. 추적 가능성

```yaml
Before:
  값: 6%
  근거: "종합 판단"
  → 애매함 ⚠️

After:
  값: 6%
  근거:
    - Method: weighted_average (3개 증거 유사)
    - Evidence:
      * Statistical: 6% (신뢰도 80%)
      * RAG: 5-7% (신뢰도 75%)
      * Soft: 5-7% 범위 (신뢰도 70%)
    - Process:
      1. 증거 수집 완료
      2. 가중 평균 선택 (신뢰도 유사)
      3. 계산: (6*0.8 + 6*0.75 + 6*0.7) / 2.25
    - Trace: [맥락 파악, 수집, 판단]
  
  → 완전 투명! ✅

효과:
  - 재현 가능
  - 검증 가능
  - 학습 가능
```

### 3. 학습 효율

```yaml
Before (분산):
  Quantifier: 자체 추정 (학습 X)
  Estimator: 추정 (학습 O)
  → 학습 비효율

After (집중):
  모든 추정 → Estimator
  → 모두 학습됨
  → Tier 1 규칙 ↑↑

효과:
  - 학습 데이터 집중
  - 재사용 극대화
  - 빠른 진화
```

---

## 🚀 작업 타임라인

```yaml
Phase 1: 데이터 모델 (1시간)
  - EstimationResult 확장
  - 새 클래스 추가
  - 테스트

Phase 2: Tier 2 근거 (1시간)
  - reasoning_detail 생성
  - component_estimations
  - 테스트

Phase 3-4: Agent 위임 (1시간)
  - Quantifier 위임 확인
  - Validator 통합
  - 테스트

Phase 5: 문서화 (30분)
  - 정책 문서
  - Agent docstring
  - 테스트

총: 3.5시간
```

---

**설계 완료!** ✅

**핵심 원칙**: **Single Source of Truth for Value Estimation**

- ✅ **Estimator만 추정**
- ✅ **근거 필수 제공**
- ✅ **데이터 일관성**

---

## 🚀 배포 전략 (옵션 3: 병행)

### Stage 1: v7.3.1 Main 배포 (10분) - 진행 중

```bash
현재 완료:
  ✅ Estimator (Fermi) Agent
  ✅ 6-Agent 시스템
  ✅ 아키텍처 일관성
  ✅ Alpha 통합 완료

배포:
  1. git checkout main
  2. git merge alpha --no-ff
  3. git rm -r archive/ dev_docs/
  4. Release v7.3.1
  5. git push origin main
```

### Stage 2: Single Source 구현 (3.5시간) - 다음

```bash
Feature Branch:
  - feature/single-source-policy
  
작업:
  Phase 1: 데이터 모델 확장 (1시간)
  Phase 2: Tier 2 근거 생성 (1시간)
  Phase 3: Quantifier 위임 확인 (30분)
  Phase 4: Validator 통합 (30분)
  Phase 5: 문서화 (30분)
```

### Stage 3: v7.3.2 배포 - 이후

```bash
검증 후 Main 배포
```

---

**다음**: v7.3.1 Main 배포 진행! 🚀
