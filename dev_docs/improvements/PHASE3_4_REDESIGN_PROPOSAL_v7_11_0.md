# Phase 3-4 재설계 제안서 (v7.11.0)

> **문서 목적**: Phase 3-4의 재귀 폭발 문제와 근본적인 해결 방안 제시
> **작성일**: 2025-11-26
> **버전**: v7.11.0 (제안)
> **이전 버전**: v7.10.2 (현재)

---

## 1. Executive Summary

### 1.1 핵심 문제
Phase 4 Fermi Decomposition에서 **재귀 폭발**이 발생하여 단순한 질문에도 15분 이상, 100회 이상의 LLM API 호출이 필요한 상황.

### 1.2 근본 원인
"높은 신뢰도"를 요구하는 설계 철학이 **무한 분해**를 유발. 인간의 추정 행위 본질(경험 데이터 기반 직관)을 반영하지 못함.

### 1.3 제안 해결책
**"LLM 확신 기반 추정"** - 재귀를 제거하고, LLM이 확신있게 제시할 수 있는 값을 직접 활용.

### 1.4 예상 효과
| 지표 | 현재 (v7.10.2) | 제안 (v7.11.0) | 개선 |
|------|---------------|----------------|------|
| 시간 | 15-20분 | 30초-1분 | **95% 단축** |
| API 호출 | 100회+ | 5-10회 | **90% 감소** |
| 비용 | $20-30 | $1-2 | **95% 절감** |

---

## 2. 현재 시스템 구조 (v7.10.2)

### 2.1 5-Phase 아키텍처

```
[Estimator 5-Phase Architecture]

Phase 0: Literal        → 프로젝트 데이터 직접 조회 (<0.1초, conf 1.0)
Phase 1: Direct RAG     → 학습된 규칙 검색 (<0.5초, conf 0.95+)
Phase 2: Validator      → 확정 데이터 검색 (<1초, conf 1.0)
Phase 3: Guestimation   → 추정 (3-8초, conf 0.80+)
Phase 4: Fermi          → 분해 추정 (10-30초 예상, 실제 15분+)
```

### 2.2 Phase 3 (Guestimation) 현재 구조

**역할**: 11개 Source에서 데이터 수집 후 종합 판단

```
[Phase 3 흐름]
질문 → Source Collector (11개 Source) → Judgment Synthesizer → 결과

주요 Source:
- Physical: 물리적 제약 (인구, 면적 등)
- AIAugmented: LLM + Web 검색
- RAG: 벤치마크/방법론 검색
- Soft: 범위/분포 가이드
```

**출력**:
```python
EstimationResult(
    value=145000,           # 추정값
    confidence=0.60,        # 신뢰도 (문제의 핵심!)
    value_range=(100000, 200000),
    reasoning="..."
)
```

### 2.3 Phase 4 (Fermi Decomposition) 현재 구조

**역할**: 복잡한 질문을 분해하여 추정

```
[Phase 4 흐름]
질문 → Step 1 (스캔) → Step 2 (모형 생성) → Step 3 (변수 추정) → Step 4 (계산)

Step 2: LLM이 2-4개 Fermi 모형 생성
        예: "서울 음식점 수 = 서울인구 × 음식점밀도"

Step 3: 각 변수에 대해 Phase 3 호출
        → 신뢰도 부족 시 Phase 4 재귀 호출 (문제!)
```

### 2.4 현재 설정 (v7.10.2)

```python
# phase4_fermi.py
max_depth = 4                    # 최대 재귀 깊이
max_variable_estimates = 20      # 전역 변수 추정 제한 (v7.10.2 추가)
max_global_attempts = 3          # 최대 시도 횟수
confidence_thresholds = [0.80, 0.60, 0.40]  # 점진적 완화
```

---

## 3. 문제 상세 분석

### 3.1 재귀 폭발 현상

**실제 로그 (2025-11-26 테스트)**:

```
[Phase 4] Fermi Estimation (depth 0)
  질문: 서울 음식점 수는?

  [Step 2] 모형 생성: 4개 모형, 8개 Unknown 변수
  
  [Recursive 1/20] restaurant_ratio_in_residential_shops  (60초)
  [Recursive 2/20] coffeeshop_share_in_fnb                (45초)
  [Recursive 3/20] average_coffeeshops_per_subdistrict    (38초)
  [Recursive 4/20] coffee_shop_to_restaurant_ratio        (52초)
  [Recursive 5/20] starbucks_share_of_total_coffeeshops   (41초)
  ...
  
  각 변수마다 Phase 3 호출 → 신뢰도 부족 → Phase 4 재귀
  → 재귀 내에서 또 변수 생성 → 또 Phase 3 → 또 재귀...
```

**12,415회 호출 기록**: 이전 프로세스에서 `_estimate_variable:1491` 라인이 12,415회 호출됨.

### 3.2 문제의 구조적 원인

```
[재귀 폭발 구조]

질문 (depth 0)
└─ Phase 4: 4개 모형 생성, 각 모형 4-6개 변수
   └─ 변수 1 → Phase 3 (conf 0.60) → 신뢰도 부족!
      └─ Phase 4 재귀 (depth 1)
         └─ 또 4개 모형, 또 4-6개 변수
            └─ 변수 1-1 → Phase 3 → 신뢰도 부족!
               └─ Phase 4 재귀 (depth 2)
                  └─ ...

기하급수적 증가:
- Depth 0: 1개 질문
- Depth 1: 4 모형 × 5 변수 = 20개
- Depth 2: 20 × 4 × 5 = 400개
- Depth 3: 400 × 4 × 5 = 8,000개
- Depth 4: 160,000개 (이론적)
```

### 3.3 v7.10.2 개선 시도와 한계

**시도 1: 전역 변수 제한 (max_variable_estimates = 20)**
```python
if self._total_variable_estimate_count > self.max_variable_estimates:
    return None  # 중단
```
→ 결과: 중단은 되지만, 20개 변수 × 30-60초 = 여전히 10-20분

**시도 2: 점진적 신뢰도 완화**
```python
confidence_thresholds = [0.80, 0.60, 0.40]
```
→ 결과: 완화해도 결국 재귀 발생, 근본 해결 안됨

**시도 3: LLM Emergency 호출**
```python
def _llm_emergency_estimate(var_name, context):
    # 빠른 LLM 직접 호출
```
→ 결과: Fallback으로 추가했지만, 메인 로직은 여전히 재귀

---

## 4. 문제의 본질: 철학적 분석

### 4.1 사용자 문제 의식 (원문)

> "decomposition을 몇번에 걸쳐서 진행하든, 마지막에는 어떤 숫자를 찍어야 해. 
> 여기서는 llm이 찍는 수 밖에 없어. 최대한 보편적이고 다수가 동의하는 숫자를 찍어야겠지.
> 
> 너무 높은 신뢰도를 요구하거나, 근거를 요구하다보면 결국 끝없이 decomposition을 반복할 수 밖에 없어.
> 
> 인간의 '추정'이라는 행동의 끝에는 경험데이터가 존재해. 
> llm는 이걸 따라할 수는 없지만, llm의 입장에서 사람의 경험데이터와 유사한 방식으로 
> 높은 확신의 수준을 가지고 제시할 수 있는 숫자들이 있을꺼야."

### 4.2 인간의 추정 vs 현재 시스템

**인간의 추정 과정**:
```
질문: "서울 음식점 몇 개?"

인간의 사고:
1. "음... 서울 인구가 1,000만 정도지?"  ← 경험 데이터
2. "동네마다 음식점이 꽤 많으니까..."   ← 직관
3. "1,000명당 10-20개 정도?"           ← 상식적 추정
4. "그럼 10만~20만 사이겠네"           ← 결론

특징: 
- 근거 불완전해도 "찍는다"
- 경험 데이터 기반 직관
- 재귀적 분해 없음
```

**현재 시스템의 추정 과정**:
```
질문: "서울 음식점 몇 개?"

시스템의 사고:
1. Phase 3: "145,000개, 신뢰도 60%"
2. "신뢰도가 80% 미만이니 근거 부족!"
3. Phase 4: "분해해서 더 정확히 계산하자"
4. 변수마다 Phase 3 호출 → 또 신뢰도 부족
5. 재귀... 재귀... 재귀...

특징:
- "근거 없으면 신뢰 안함"
- 끝없는 검증 요구
- 재귀적 분해의 늪
```

### 4.3 핵심 통찰

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   "신뢰도"라는 개념이 재귀를 유발한다.                              │
│                                                                 │
│   해결책: 신뢰도 기반 재귀를 제거하고,                              │
│          LLM이 "확신있게 말할 수 있는 값"을 직접 활용한다.           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 4.4 LLM이 "확신있게 말할 수 있는" 값들

LLM 학습 데이터에 자주 등장하여 높은 내적 확신으로 제시 가능한 값:

**1. 상식적 통념 (Common Knowledge)**
```
- 대한민국 인구 = 5,000만
- 서울 인구 = 1,000만
- 1년 = 365일
- 한 달 = 30일
```

**2. 도메인 벤치마크 (Industry Norms)**
```
- SaaS Churn Rate = 3-5%
- 음식점 마진 = 10-15%
- 유료 전환율 = 2-5%
- 스타트업 성공률 = 10%
```

**3. 자주 등장하는 비율 (Anchoring)**
```
- 10%, 20%, 50% (일반적 비율)
- 80/20 (파레토 법칙)
- 1:3, 1:10 (비율)
```

**4. 물리적 상수/제약**
```
- 하루 = 24시간
- 1km² = 1,000,000m²
- 사람 이동속도 = 4-5km/h
```

이런 값들은 LLM이 "근거를 제시하지 않아도" 높은 확신으로 제시할 수 있음.

---

## 5. 재설계 제안 (v7.11.0)

### 5.1 설계 철학의 근본적 전환

**핵심 재정의**:
```
[Before - v7.10.x]
"추정을 증명하려는 알고리즘"
- 근거가 있어야 신뢰할 수 있다
- confidence를 검증 신호로 사용
- 생성(guess)과 검증(validate)이 순환 의존

[After - v7.11.0]  
"제약 안에서 숫자를 찍는 생성 모델 + 합리적인 퓨전"
- Evidence(제약) vs Generative Prior(생성) 분리
- 각자 독립적으로 결과 생성
- Fusion 레이어에서 센서 퓨전처럼 합성
```

**문제의 본질**:
- 재귀는 "증상"
- 진짜 병은 "신뢰도 개념과 역할 분리가 꼬여 있는 것"
- Estimator가 "값 생성"과 "값 검증"을 동시에 하면서 서로 물고 늘어짐

### 5.2 핵심 구조: 4단계 아키텍처

```
[v7.11.0 Architecture]

Question
  ↓
[Stage 1] Evidence & Guardrails (Phase 0-2)
  → 확정 데이터, 하드 제약, 논리적 관계
  → Output: definite_value, hard_bounds, logical_relations
  ↓
[Stage 2] Generative Prior (Phase 3 Direct)
  → LLM 확신 기반 추정
  → Output: value, range, certainty (내적 확신)
  ↓
[Stage 3] Structural Explanation (Phase 4 Fermi - Optional)
  → 얕은 분해 (depth 1-2, 재귀 금지)
  → 역할: 설명 + 약간의 튜닝
  → Output: decomposed_value, structure
  ↓
[Stage 4] Fusion & Validation
  → Evidence + Prior + Structure를 센서 퓨전
  → Weighted synthesis, range intersection, sanity check
  → Output: final EstimationResult
```

**핵심 원칙**:
1. **정보 계층 분리**: Evidence(제약) vs Generative Prior(생성)
2. **공통 인터페이스**: 모든 추정 엔진이 동일한 EstimationResult 반환
3. **재귀 금지**: 정책 레벨에서 봉인
4. **예산 기반 탐색**: confidence threshold 대신 budget (time/calls/variables)
5. **Fusion 레이어**: "누가 맞았냐" 싸움이 아닌 합성

### 5.3 Stage 1: Evidence & Guardrails 계층

**역할**: "거의 확정적인 사실 / 제약" 제공

```python
class EvidenceCollector:
    """
    Phase 0-2 + GuardrailEngine 통합
    """
    def collect(self, question) -> Evidence:
        return Evidence(
            definite_value=None,          # 있으면 즉시 종료
            hard_bounds=(min, max),       # 절대 벗어날 수 없는 범위
            logical_relations=[            # A < B, A ≈ k×B 등
                "population < area * 100000",
                "revenue = users * arpu"
            ],
            soft_hints=[...]              # 설명용 (직접 사용 X)
        )
```

**특징**:
- 프로젝트 데이터, Validator, 통계 수치, 수학/물리 제약
- "이 범위 밖은 절대 아님"을 보장
- Fusion 레이어에서 하드 제약으로 사용

### 5.4 Stage 2: Generative Prior (Phase 3 재설계)

**역할**: LLM의 "확신 기반 추정" - 상식적 통념, 도메인 벤치마크, 자주 등장하는 비율

**현재 (v7.10.x)**: 11개 Source 수집 → 종합 판단 → confidence 기반 재귀 유발

**제안 (v7.11.0)**: LLM에게 "확신있게 말할 수 있는 값" 직접 요청
```python
def estimate(question):
    # LLM에게 "확신있게 말할 수 있는 값" 직접 요청
    response = llm.estimate(
        prompt=f"""
        질문: {question}
        
        당신이 확신있게 말할 수 있는 값을 제시하세요.
        정확한 근거가 없어도 괜찮습니다.
        상식적으로 합의된 범위, 또는 당신이 가장 그럴듯하다고 
        생각하는 값을 제시하세요.
        
        출력 (JSON):
        - value: 가장 그럴듯한 값
        - range: [최소, 최대] (틀리지 않을 범위)
        - certainty: high/medium/low (당신의 내적 확신)
        """
    )
    
    return EstimationResult(
        value=response.value,
        certainty=response.certainty,  # confidence → certainty
        value_range=response.range,
        ...
    )
```

**핵심 변경**:
- `confidence` (외부 검증) → `certainty` (내적 확신)
- 재귀 조건 제거: 항상 값 반환
- 프롬프트: "근거 없어도 확신있게 말하라"
- Evidence의 hard_bounds 내에서 값 생성

**LLM이 확신있게 제시할 수 있는 값들**:
- 상식적 통념: "서울 인구 = 1,000만"
- 도메인 벤치마크: "SaaS Churn = 3-5%"
- 자주 등장하는 비율: "10%, 20%, 파레토 80/20"
- 물리적 상수: "1년 = 365일, 하루 = 24시간"

### 5.5 Stage 3: Structural Explanation (Phase 4 재설계)

**역할 재정의**: "정밀화"가 아닌 "구조 설명 + 약간의 튜닝"

**Fermi의 3가지 역할**:
1. **구조적 설명 제공**: "인구 × 이용률 × 단가"처럼 explainability
2. **정밀도 약간 향상**: Prior + Guardrail 안에서 모순 제거
3. **Phase 3의 보조 수단**: Direct Prior를 앵커로, 구조적 분해로 조정

**현재 (v7.10.x)**: max_depth=4, 재귀 호출, confidence threshold 기반

**제안 (v7.11.0)**: 재귀 금지 + 예산 기반 탐색
```python
class Phase4FermiDecomposition:
    # 정책 레벨 제약
    max_depth = 2                      # 강제 (재귀 금지)
    max_llm_calls = 10                 # 예산 기반
    max_variables_total = 8
    max_runtime_seconds = 60
    
    def estimate(self, question, budget: Budget) -> EstimationResult:
        """
        예산 기반 탐색: confidence threshold 대신 budget 사용
        """
        if depth >= self.max_depth or budget.exhausted():
            return self._direct_estimate(question)
        
        # Step 1: 분해 (1회만)
        budget.consume('model_generation', 1)
        models = self._generate_models(question)
        
        # Step 2: 각 변수 직접 추정 (재귀 절대 금지!)
        for model in models[:budget.remaining_variables()]:
            for var in model.variables:
                budget.consume('variable_estimate', 1)
                var.value = self._direct_estimate(var.name)  # 재귀 없음!
                
                if budget.exhausted():
                    break
        
        # Step 3: 계산
        return self._calculate_best_model(models)
    
    def _direct_estimate(self, question) -> EstimationResult:
        """
        재귀 없이 LLM 직접 추정
        Stage 2 (Generative Prior)와 동일한 메커니즘
        """
        return self.prior_estimator.estimate(question)
```

**핵심 변경**:
1. **재귀 금지**: 코드 레벨이 아닌 "정책 레벨"에서 봉인
2. **예산 기반 탐색**: confidence < threshold 제거, budget 사용
3. **공통 인터페이스**: `_direct_estimate()`가 Stage 2와 동일한 메커니즘

**핵심 변경**:
- `max_depth = 4` → `max_depth = 2` (강제)
- 변수 추정 시 재귀 호출 제거
- `_direct_estimate()`: 항상 값 반환, 재귀 없음

### 5.6 Stage 4: Fusion & Validation

**역할**: Evidence + Prior + Structure의 센서 퓨전

```python
class FusionLayer:
    """
    모든 추정 결과를 합성하는 통합 레이어
    """
    def synthesize(
        self,
        evidence: Evidence,
        prior_result: EstimationResult,      # Stage 2
        fermi_result: Optional[EstimationResult]  # Stage 3
    ) -> EstimationResult:
        
        # 1. Hard bounds 적용
        lower, upper = evidence.hard_bounds
        
        # 2. 각 후보에 weight 계산
        candidates = [r for r in [prior_result, fermi_result] if r]
        weighted_values = []
        weights = []
        
        for result in candidates:
            # Guardrail 밖이면 clip
            v = np.clip(result.value, lower, upper)
            
            # certainty → weight
            # range 폭 → uncertainty → weight
            w = (
                certainty_to_weight(result.certainty) *
                range_to_weight(result.value_range)
            )
            
            weighted_values.append(v)
            weights.append(w)
        
        if not weighted_values:
            # Guardrail만으로 범위 반환
            return self._guardrail_only_result(lower, upper)
        
        # 3. 가중 평균
        final_value = np.average(weighted_values, weights=weights)
        
        # 4. Range intersection
        final_range = self._intersect_ranges(
            [c.value_range for c in candidates] + [(lower, upper)]
        )
        
        # 5. Certainty 종합
        final_certainty = self._aggregate_certainty(
            candidates, final_range
        )
        
        return EstimationResult(
            value=final_value,
            value_range=final_range,
            certainty=final_certainty,
            used_evidence=evidence,
            fusion_weights=dict(zip(
                ['prior', 'fermi'], 
                weights
            ))
        )
```

**핵심**:
- "누가 맞았냐" 싸움 (confidence 비교) → 센서 퓨전 (weighted synthesis)
- Evidence는 하드 제약, Prior/Fermi는 생성 신호
- 모든 정보를 합성하여 최종 결과 도출

### 5.7 공통 인터페이스: EstimationResult

**모든 추정 엔진이 동일한 타입 반환**:

```python
@dataclass
class EstimationResult:
    """
    통합된 추정 결과 인터페이스
    """
    # 핵심 값
    value: float                      # Point estimate
    value_range: Tuple[float, float]  # [min, max]
    
    # 확신/불확실성 (confidence → certainty 전환)
    certainty: Literal['high', 'medium', 'low']  # LLM 내적 확신
    uncertainty: float                # 표준편차 느낌 (0.0 ~ 1.0)
    
    # 메타 정보
    cost: Cost                        # time, tokens, api_calls
    decomposition: Optional[FermiModel]  # Fermi 구조 (있으면)
    used_evidence: Evidence           # 사용한 Evidence
    
    # Fusion 정보
    fusion_weights: Dict[str, float]  # 각 소스의 가중치
```

**Stage 2 (Prior)와 Stage 3 (Fermi)의 출력 타입 통일**:
- 더 이상 "Phase 3 confidence < 0.8 → Phase 4" 같은 제어 흐름 불필요
- 각자 독립적으로 결과 생성 → Fusion 레이어에서 합성

### 5.8 전체 흐름 비교

**현재 (v7.10.x)**:
```
질문: "서울 음식점 수?"
│
├─ Phase 3: conf 0.60 → 부족!
│   └─ Phase 4 (depth 0)
│       ├─ 모형 생성: 4개 × 5변수 = 20개
│       └─ 각 변수 Phase 3 호출
│           ├─ 변수1: conf 0.55 → Phase 4 재귀 (depth 1)
│           │   └─ 또 4개 × 5변수 = 20개
│           │       └─ 각 변수 Phase 3 → Phase 4 재귀 (depth 2)
│           │           └─ ...
│           ├─ 변수2: conf 0.50 → Phase 4 재귀
│           │   └─ ...
│           └─ ... (기하급수적 증가)
│
└─ 결과: 15분+, 100회+ API 호출, $20-30
```

**제안 (v7.11.0)**: 병렬 추정 + Fusion
```
질문: "서울 음식점 수?"
│
├─ [Stage 1] Evidence & Guardrails
│   └─ hard_bounds: (10,000, 500,000)
│       "서울 면적 × 최대밀도 < 500,000"
│
├─ [Stage 2] Direct Prior (병렬 실행)
│   └─ LLM: "145,000개" (certainty: medium, range: [100k, 200k])
│
├─ [Stage 3] Fermi (병렬 실행, Optional)
│   ├─ Budget: max_variables=8, max_calls=10, max_time=60s
│   ├─ 모형: "서울인구 × 음식점밀도"
│   ├─ 변수 추정 (재귀 절대 금지):
│   │   ├─ 서울인구 → "1,000만" (certainty: high)
│   │   └─ 음식점밀도 → "1,000명당 15개" (certainty: medium)
│   └─ 계산: 10,000,000 × 0.015 = 150,000
│
└─ [Stage 4] Fusion
    ├─ Prior: 145,000 (weight: 0.4)
    ├─ Fermi: 150,000 (weight: 0.6)
    ├─ Guardrail clip: [10,000, 500,000] 내
    └─ Weighted avg: 148,000
    
결과: 30-60초, 5-10회 API 호출, $1-2
```

**핵심 차이**:
- Stage 2와 3은 **병렬 실행** 가능 (의존성 없음)
- certainty 기반 분기 제거 → 둘 다 실행 후 Fusion에서 결정
- "실패" 개념 없음 → 항상 값 반환, 가중치로 반영

### 5.9 예산 기반 탐색 (Budget-based Search)

**현재 문제**: confidence threshold가 stopping rule로 작동 → 무한 루프

**제안**: 예산(Budget)을 명시적으로 제어

```python
@dataclass
class Budget:
    """추정에 사용할 수 있는 리소스"""
    max_llm_calls: int = 10
    max_variables: int = 8
    max_runtime_seconds: float = 60.0
    
    # 현재 상태
    used_calls: int = 0
    used_variables: int = 0
    start_time: float = field(default_factory=time.time)
    
    def consume(self, resource_type: str, amount: int = 1):
        if resource_type == 'llm_call':
            self.used_calls += amount
        elif resource_type == 'variable':
            self.used_variables += amount
    
    def exhausted(self) -> bool:
        return (
            self.used_calls >= self.max_llm_calls or
            self.used_variables >= self.max_variables or
            (time.time() - self.start_time) >= self.max_runtime_seconds
        )
    
    def remaining_variables(self) -> int:
        return max(0, self.max_variables - self.used_variables)
```

**적용**:
```python
def estimate(question, budget: Budget):
    # Stage 2: Direct Prior (항상 실행, 1-2 calls)
    budget.consume('llm_call', 1)
    prior_result = prior_estimator.estimate(question)
    
    # Stage 3: Fermi (예산 있으면)
    fermi_result = None
    if not budget.exhausted():
        fermi_result = fermi_estimator.estimate(
            question, 
            budget  # 예산 전달
        )
    
    # Stage 4: Fusion (항상 실행)
    return fusion_layer.synthesize(
        evidence, prior_result, fermi_result
    )
```

**효과**:
- "confidence < 0.8이면 더 파자" → "예산 내에서 가장 유익한 행동"
- 최악의 경우에도 max_runtime_seconds 보장
- 재귀 대신 **cascade + budgeted search** 패턴

### 5.10 Certainty vs Confidence

**Confidence (현재)**:
- 정의: "외부 근거가 있는가?"
- 판단: Source에서 얼마나 많은 증거를 찾았는가
- 문제: 근거 없으면 낮은 값 → 재귀 유발

**Certainty (제안)**:
- 정의: "LLM이 얼마나 확신하는가?"
- 판단: LLM 스스로의 내적 확신 수준
- 장점: 근거 없어도 높을 수 있음 (상식, 통념)

```python
# Certainty 레벨
certainty_levels = {
    "high": "상식적 통념, 널리 알려진 값 (예: 서울 인구)",
    "medium": "도메인 벤치마크, 일반적 범위 (예: SaaS Churn)",
    "low": "추측, 불확실 (예: 특정 회사의 매출)"
}
```

---

### 5.11 설계의 핵심 원칙 요약

```
┌──────────────────────────────────────────────────────────────────┐
│                                                                  │
│  1. Evidence vs Generative Prior 분리                           │
│     - Evidence: "이 범위 밖은 절대 아님" (하드 제약)                │
│     - Prior: "이 안에서 어디쯤이 자연스러운지" (생성)               │
│                                                                  │
│  2. 공통 인터페이스 (EstimationResult)                            │
│     - Phase 3/4가 동일한 타입 반환                                │
│     - "누가 맞았냐" 대신 "모두 합성"                               │
│                                                                  │
│  3. 재귀 금지 (정책 레벨)                                         │
│     - Estimator는 자기 자신을 절대 호출하지 않음                    │
│     - 코드 튜닝이 아닌 아키텍처 원칙                                │
│                                                                  │
│  4. 예산 기반 탐색                                                │
│     - confidence threshold 제거                                  │
│     - Budget(calls/variables/time) 명시적 제어                   │
│                                                                  │
│  5. Fermi = 설명 + 약간의 튜닝                                    │
│     - "정밀화"가 아닌 "구조 제공 + 합리성 검증"                     │
│     - Prior를 앵커로, Fermi로 조정                                │
│                                                                  │
│  6. Fusion 레이어 = 센서 퓨전                                     │
│     - Evidence + Prior + Fermi를 weighted synthesis             │
│     - 검색/추천/자율주행의 cascade 패턴                            │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

## 6. 구현 계획

### 6.1 변경 파일 및 구조

```
umis_rag/agents/estimator/
├── evidence_collector.py     # [신규] Stage 1: Evidence & Guardrails
├── prior_estimator.py        # [신규] Stage 2: Generative Prior
├── fermi_estimator.py        # [개명] Stage 3: Structural Explanation
├── fusion_layer.py           # [신규] Stage 4: Fusion & Validation
├── budget.py                 # [신규] Budget 클래스
├── models.py                 # EstimationResult 통합 (certainty 추가)
│
├── phase3_guestimation.py   # [마이그레이션] → prior_estimator.py
├── phase4_fermi.py          # [마이그레이션] → fermi_estimator.py
└── guardrail_analyzer.py    # [마이그레이션] → evidence_collector.py
```

**아키텍처 원칙 문서**:
```
dev_docs/architecture/
└── ESTIMATOR_DESIGN_PRINCIPLES_v7_11_0.md  # [신규]
    - 재귀 금지 원칙
    - 공통 인터페이스 강제
    - 예산 기반 탐색 정책
```

### 6.2 단계별 구현 (총 5일)

**Day 1: 공통 인터페이스 + Evidence 계층**
- `EstimationResult` 통합 (certainty 추가)
- `Budget` 클래스 구현
- `EvidenceCollector` 구현 (Phase 0-2 + Guardrail 통합)

**Day 2: Generative Prior (Stage 2)**
- `PriorEstimator` 구현
- 프롬프트: "확신있게 말할 수 있는 값" 요청
- certainty 레벨 판단 로직

**Day 3: Fermi 재설계 (Stage 3)**
- `FermiEstimator` 구현
- max_depth=2, 재귀 완전 제거
- Budget 기반 탐색 적용
- _direct_estimate() → PriorEstimator 호출

**Day 4: Fusion 레이어 (Stage 4)**
- `FusionLayer` 구현
- Weighted synthesis
- Range intersection
- Sanity check

**Day 5: 통합 테스트 + 검증**
- 재귀 폭발 완전 제거 확인
- Before/After 비교 (시간/비용/정확도)
- Ablation 테스트 (각 Stage 기여도)
- Budget threshold 튜닝

### 6.3 통합 추정 흐름

```python
class Estimator:
    """
    v7.11.0 통합 Estimator
    """
    def estimate(self, question: str) -> EstimationResult:
        # Budget 초기화
        budget = Budget(
            max_llm_calls=10,
            max_variables=8,
            max_runtime_seconds=60.0
        )
        
        # Stage 1: Evidence & Guardrails
        evidence = self.evidence_collector.collect(question)
        
        # 확정 값 있으면 즉시 반환
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
    
    def _should_use_fermi(self, question: str) -> bool:
        """
        Fermi 사용 여부 결정
        - 복잡도 분석
        - 사용자 preference
        - 시간 제약 등
        """
        return question_complexity(question) > threshold
```

**특징**:
- "Fallback"이 아닌 "병렬 + Fusion"
- 모든 Stage가 독립적으로 실행 가능
- 실패 개념 없음 (항상 값 반환)

---

## 7. 검증 및 평가

### 7.1 검증 방법

**1. Before/After 비교**
```
질문 50개 × 3회 반복 = 150회 테스트

측정 지표:
- 실행 시간 (P50, P95, P99)
- LLM 호출 수
- 비용 ($)
- 정확도 (log10 error)
- Tail latency (최악의 경우)
```

**2. Ablation 테스트**
```
각 Stage의 기여도 측정:
- Evidence only (Guardrail 범위만)
- Evidence + Prior
- Evidence + Prior + Fermi
- Full (Evidence + Prior + Fermi + Fusion)

→ 각 Stage가 정확도/불확실성에 미치는 영향
```

**3. 재귀 폭발 제거 확인**
```
1000회 반복 실행:
- max_llm_calls 초과 횟수 = 0
- max_runtime 초과 횟수 = 0
- 재귀 호출 발생 = 0

→ Budget 제약이 하드 제약으로 작동하는지 확인
```

### 7.2 정량적 효과

| 지표 | 현재 (v7.10.2) | 제안 (v7.11.0) | 개선율 |
|------|---------------|----------------|--------|
| 실행 시간 | 15-20분 | 30초-1분 | **95%↓** |
| API 호출 | 100회+ | 5-10회 | **90%↓** |
| 비용 (호출당) | $20-30 | $1-2 | **95%↓** |
| 변수 추정 | 20개+ | 4-8개 | **60%↓** |

### 7.3 정성적 효과

**장점**:
- ✓ 실제 사용 가능한 응답 시간 (SLA 보장)
- ✓ 비용 효율적 (예측 가능한 비용)
- ✓ 재귀 불안정성 완전 제거
- ✓ 예측 가능한 실행 시간 (Budget 기반)
- ✓ 병렬화 가능 (Stage 2/3 독립 실행)
- ✓ 설명 가능성 향상 (Fermi 구조 + Evidence)

**Trade-offs**:
- △ 정밀도 감소 가능 (±30% → ±50%)
  → Guardrail + Fusion으로 완화
- △ 복잡한 질문에서 분해 깊이 제한
  → "교육용 Fermi"와 "실용 Fermi" 역할 분리로 해결
- △ LLM 환각(hallucination) 위험 증가
  → Evidence 하드 제약 + Sanity check로 방어

### 7.4 리스크와 한계

**1. 정밀도 희생**
- 현상: ±30% → ±50% 오차 증가 가능
- 완화: Guardrail 하드 제약 + 범위 기반 sanity check
- 수용: "1분 내 답변" SLA 획득

**2. LLM 환각 문제**
- 현상: LLM 확신은 높지만 틀릴 수 있음
- 완화: Evidence 계층에서 물리적/논리적 제약 검증
- 수용: certainty 레벨 표시로 불확실성 명시

**3. Fermi 교육적 가치 감소**
- 현상: 얕은 분해로 높은 추론 퀄리티 감소
- 해결: "사용자용 Fermi"와 "내부용 Fermi" 역할 분리
  - 사용자용: 깊은 분해, 교육/설명 목적
  - 내부용: 얕은 분해, 빠른 추정 목적

**4. 도메인 의존성**
- 현상: 비표준/최신 도메인에서 LLM prior 품질 저하
- 완화: Evidence + Guardrail 의존도 증가
- 메타-러닝: 역사적 추정값 활용으로 개선

### 7.5 품질 보완 전략

```
1. 교차 검증 (Cross-validation)
   - 여러 모형 결과 비교
   - 범위 일치 확인

2. Hard Guardrail
   - 물리적 제약 검사 (음수 불가 등)
   - 상식적 범위 검사

3. Soft Guardrail  
   - 도메인 벤치마크와 비교
   - 이상치 경고

4. 불확실성 명시
   - certainty 레벨 표시
   - 범위 제공 ([min, max])
```

---

## 8. 결론

### 8.1 핵심 메시지

```
┌──────────────────────────────────────────────────────────────────────┐
│                                                                      │
│  "추정을 '증명하려는 알고리즘'에서,                                      │
│   '제약 안에서 숫자를 찍는 생성 모델 + 합리적인 퓨전'으로 재정의"          │
│                                                                      │
│  재귀는 증상이었고,                                                     │
│  진짜 병은 신뢰도 개념과 역할 분리가 꼬여 있던 것.                        │
│                                                                      │
│  Evidence(제약) vs Generative Prior(생성)를 분리하고,                  │
│  각자 독립적으로 결과를 만든 뒤,                                         │
│  Fusion 레이어에서 센서 퓨전처럼 합성한다.                                │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

### 8.2 철학적 전환의 의미

**Before (v7.10.x)**:
- Estimator가 "값 생성"과 "값 검증"을 동시에 수행
- confidence를 제어 신호로 사용 → 순환 의존
- "근거 충분히 쌓여야 신뢰" → 무한 분해

**After (v7.11.0)**:
- Evidence(검증)와 Prior(생성) 완전 분리
- 각자 독립적으로 작동, Fusion에서 합성
- "예산 내에서 최선" → 예측 가능한 종료

**패러다임 변화**:
```
"증명 가능한 추정" → "합리적인 추정"
"완벽한 근거"     → "충분한 제약 + 상식적 prior"
"재귀적 정밀화"    → "병렬 생성 + 센서 퓨전"
```

### 8.3 다음 단계

**Phase 1: 프로토타입 (3일)**
1. EvidenceCollector + PriorEstimator 기본 구현
2. Budget 클래스
3. 간단한 Fusion 로직
4. 10개 질문으로 concept 검증

**Phase 2: Full Implementation (5일)**
1. FermiEstimator 재설계 (재귀 완전 제거)
2. FusionLayer 완전 구현
3. 통합 테스트 프레임워크

**Phase 3: 검증 및 튜닝 (3일)**
1. Before/After 비교 (50개 질문)
2. Ablation 테스트
3. Budget threshold 튜닝
4. 문서화

**Phase 4: 프로덕션 배포 (2일)**
1. 성능 모니터링
2. 점진적 롤아웃
3. A/B 테스트

### 8.4 성공 기준

```
필수 (Must-have):
✓ 재귀 완전 제거 (0% tolerance)
✓ 응답 시간 < 60초 (P95)
✓ API 호출 < 10회 (평균)

목표 (Should-have):
✓ 정확도 유지 (오차 < 2x)
✓ 비용 < $2/query
✓ 병렬화 가능 (Stage 2/3)

선택 (Nice-to-have):
△ 실행 시간 < 30초 (P50)
△ 정확도 향상 (일부 질문)
```

### 8.5 관련 문서

- `SESSION_SUMMARY_20251126_PHASE4_RECURSIVE_EXPLOSION.md` - 재귀 폭발 문제 발견
- `dev_docs/improvements/PHASE_0_4_REDESIGN_ANALYSIS_v7_10_0.md` - 이전 개선 시도
- `benchmarks/estimator/phase4/` - Phase 4 평가 시스템

---

## Appendix A: 사용자 피드백 요약

> "한줄로 말하면, **추정을 '증명하려는 알고리즘'에서, '제약 안에서 숫자를 찍는 생성 모델 + 합리적인 퓨전 레이어'로 재정의**해야 한다."

### 핵심 통찰:

1. **문제의 본질**: 재귀는 증상, 진짜 병은 신뢰도 개념과 역할 분리가 꼬인 것
2. **정보 계층 분리**: Evidence/Guardrail vs Generative Prior
3. **추정 메커니즘 통일**: Phase 3/4 공통 인터페이스
4. **재귀 금지**: 정책 레벨에서 봉인 + 예산 기반 탐색
5. **Fermi 역할 재정의**: "정밀화"가 아닌 "설명 + 약간의 튜닝"
6. **Fusion 레이어**: 센서 퓨전처럼 weighted synthesis

### 가정과 근거:

**가정**:
- LLM은 도메인별 안정적인 "상식적 prior" 보유
- Guardrail 시스템은 높은 신뢰도로 하드 제약 제공
- 사용자는 ±30~50% 오차 ↔ 1분 내 응답 trade-off 수용

**근거**:
- 12,415회 함수 호출 로그 (재귀 폭발 실증)
- 병렬 실행 + Fusion 패턴의 다른 도메인 성공 사례
- LLM 확신 기반 추정 철학 전환의 필요성

### 검증 아이디어:

1. Phase 4 평가 시스템으로 v7.10 vs v7.11 A/B 비교
2. 시간·비용·오차 종합 분석으로 최적 threshold 탐색
3. 역사적 추정값 활용 메타-러닝으로 장기 개선

---

## Appendix B: 용어 정의

| 용어 | 정의 |
|------|------|
| **재귀 폭발** | Phase 4에서 변수 추정 시 무한히 재귀 호출되는 현상 |
| **Confidence** | 외부 근거 기반 신뢰도 (v7.10.x) - 재귀 유발의 주범 |
| **Certainty** | LLM 내적 확신 수준 (v7.11.0) - 생성 신호 |
| **Evidence** | 확정 데이터, 하드 제약, 논리적 관계 (검증 계층) |
| **Generative Prior** | LLM의 상식 기반 추정 (생성 계층) |
| **Budget** | 추정에 사용할 수 있는 리소스 (calls/variables/time) |
| **Fusion** | 여러 추정 결과의 센서 퓨전 (weighted synthesis) |
| **직접 추정** | 재귀 없이 LLM이 바로 값을 제시하는 방식 |
| **얕은 분해** | max_depth 1-2로 제한된 Fermi 분해 |

---

## Appendix C: 실제 시스템 패턴과의 비교

이 설계는 다른 실제 시스템들의 검증된 패턴을 차용합니다:

| 시스템 | 패턴 | v7.11.0 대응 |
|--------|------|-------------|
| **검색 엔진** | Cascade (L0→L1→L2) | Stage 1→2→3 |
| **자율주행** | Sensor Fusion | Fusion Layer |
| **추천 시스템** | Budget-based Exploration | Budget 클래스 |
| **금융 트레이딩** | Hard bounds + Soft signals | Evidence + Prior |
| **RL/Planning** | Value of Information (VOI) | Budget 기반 탐색 |

---

*문서 끝 - v7.11.0 (통합 버전)*

**작성**: 2025-11-26
**기여**: 사용자 피드백 통합
**상태**: 제안 (구현 대기)
