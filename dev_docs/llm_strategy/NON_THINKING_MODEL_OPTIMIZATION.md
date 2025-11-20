# UMIS 비-Thinking 모델 최적화 가이드
**일반 LLM(GPT-4o, Claude Sonnet)으로 효과적 사용을 위한 개선 방안**

---

## 📌 문제 정의

### Thinking 모델 vs 일반 LLM

```yaml
Thinking 모델 (o1, o1-mini):
  장점:
    - 복잡한 추론 가능 (Chain-of-Thought 내장)
    - 다단계 문제 해결
    - 불확실성 처리 우수
    - Self-correction 능력
  
  단점:
    - 비용 매우 높음 (일반 모델 대비 3-10배)
    - 응답 시간 느림 (10-60초)
    - API 제한 많음
  
  가격:
    - o1: ~$60/1M 입력 토큰 (~$200/1M 출력)
    - o1-mini: ~$12/1M 입력 토큰 (~$48/1M 출력)

일반 LLM (GPT-4o, Claude Sonnet):
  장점:
    - 비용 저렴 (일반 $3-10/1M 토큰)
    - 빠른 응답 (1-5초)
    - API 안정적
  
  단점:
    - 복잡한 추론 약함
    - 명확한 가이드 필요
    - 에러 복구 능력 낮음
  
  가격:
    - GPT-4o: ~$5/1M 입력 토큰 (~$15/1M 출력)
    - Claude Sonnet 4: ~$3/1M 입력 토큰 (~$15/1M 출력)
```

### UMIS에서 Thinking 모델이 필요한 순간

```yaml
현재 의존도:
  
  1. Estimator Phase 4 (Fermi 분해):
    난이도: ⭐⭐⭐⭐⭐ (매우 복잡)
    작업:
      - 모형 생성 (Top-down, 3-5개 후보)
      - 실행 가능성 체크 (재귀 추론)
      - 변수 선택 판단
      - Backtracking
    thinking 의존도: 80%
  
  2. Explorer 패턴 매칭:
    난이도: ⭐⭐⭐ (중간)
    작업:
      - 54개 패턴에서 유사도 판단
      - 조합 가능성 평가
    thinking 의존도: 40%
  
  3. Validator 정의 검증:
    난이도: ⭐⭐ (낮음-중간)
    작업:
      - Definition Gap 분석
      - 데이터 신뢰도 평가
    thinking 의존도: 30%
  
  4. Observer 비효율성 감지:
    난이도: ⭐⭐⭐⭐ (높음)
    작업:
      - 가치사슬 분석
      - 구조적 비효율 추론
    thinking 의존도: 60%
  
  5. Discovery Sprint:
    난이도: ⭐⭐⭐⭐⭐ (매우 복잡)
    작업:
      - 6-Agent 병렬 탐색 조율
      - 모호한 목표 구체화
    thinking 의존도: 70%
```

---

## 🎯 개선 전략 (5가지 접근)

### Strategy 1: 구조화된 의사결정 트리 ⭐⭐⭐

**핵심**: 복잡한 추론을 명확한 if-then 룰로 변환

#### Before (Thinking 모델 의존)

```yaml
Estimator Phase 4 (현재):
  "서울 음식점 수는?"
  
  → LLM에게 자유롭게 모형 생성 요청
  → Thinking 모델이 창의적으로 3-5개 모형 제시
  → 실행 가능성 스스로 판단
  → Backtracking 알아서 수행
  
  문제: 일반 LLM은 이런 고차원 추론 약함
```

#### After (명확한 의사결정 트리)

```yaml
Estimator Phase 4 (개선):
  "서울 음식점 수는?"
  
  Step 1: 템플릿 선택 (룰 기반)
    질문 분석:
      - 키워드: "서울" (지역), "음식점" (장소)
      - 타입: 개수 추정
    
    → 템플릿 자동 선택: "지역별 장소 개수"
    
    템플릿 구조:
      목표 = 지역_인구 × (장소_밀도 OR 1인당_장소_수)
      OR
      목표 = 지역_면적 × 단위면적당_장소_수
  
  Step 2: 변수 확인 (체크리스트)
    필수 변수:
      - [ ] 서울 인구 (알려짐)
      - [ ] 음식점 밀도 (추정 필요)
    
    대체 변수:
      - [ ] 서울 면적 (알려짐)
      - [ ] km²당 음식점 (추정 필요)
  
  Step 3: 모형 실행 (자동)
    모형 1: 인구 × 음식점/인 = 1,000만 × 1/200 = 50,000
    모형 2: 면적 × 음식점/km² = 605km² × 100 = 60,500
    
    → 평균: 55,250개
  
  LLM 역할: 템플릿 선택만 (단순 분류)
```

#### 구현 방안

```python
# umis_rag/agents/estimator/decision_tree.py (신규)

class FermiDecisionTree:
    """
    Thinking 모델 불필요한 구조화 추론
    """
    
    TEMPLATES = {
        "지역별_장소_개수": {
            "pattern": r"(서울|부산|대구|.*시).*(음식점|카페|편의점|.*점)",
            "models": [
                "{지역}_인구 × (1 / {1인당_장소_수})",
                "{지역}_면적 × {단위면적당_장소_수}"
            ],
            "variables": {
                "지역_인구": "statistical",  # Phase 2 (확정)
                "지역_면적": "statistical",  # Phase 2 (확정)
                "1인당_장소_수": "guestimation",  # Phase 3 (추정)
                "단위면적당_장소_수": "guestimation"  # Phase 3
            }
        },
        
        "총량_분해": {
            "pattern": r"전체.*(시장|규모|매출)",
            "models": [
                "총_사용자_수 × 1인당_지출",
                "거래_건수 × 건당_평균_금액"
            ]
        },
        
        "SaaS_지표": {
            "pattern": r"(LTV|CAC|Churn|ARPU|MRR)",
            "direct_formulas": {
                "LTV": "ARPU / Churn_Rate",
                "Payback": "CAC / (ARPU × Gross_Margin)",
                "Rule_of_40": "Growth_Rate + Profit_Margin"
            }
        }
        # ... 20-30개 템플릿
    }
    
    def select_template(self, query: str) -> dict:
        """
        질문 → 템플릿 자동 선택 (룰 기반)
        
        LLM 불필요! (단순 정규식 + 키워드)
        """
        import re
        
        for template_name, template in self.TEMPLATES.items():
            if re.search(template['pattern'], query):
                return {
                    'template_name': template_name,
                    'models': template['models'],
                    'variables': template['variables']
                }
        
        # 매칭 실패 시만 LLM 호출 (일반 모델로 충분)
        return self._llm_template_selection(query)
    
    def execute_template(self, template: dict, context: dict) -> dict:
        """
        템플릿 실행 (LLM 불필요!)
        """
        results = []
        
        for model_formula in template['models']:
            # 변수 값 수집
            variables = {}
            for var_name, var_source in template['variables'].items():
                if var_source == "statistical":
                    # Phase 2: Validator 검색 (확정 데이터)
                    variables[var_name] = self.phase2_search(var_name)
                elif var_source == "guestimation":
                    # Phase 3: 11개 Source 활용
                    variables[var_name] = self.phase3_estimate(var_name)
            
            # 수식 계산 (eval 또는 AST 파싱)
            result = self._evaluate_formula(model_formula, variables)
            results.append(result)
        
        # 평균 또는 가중평균
        return {
            'value': sum(results) / len(results),
            'confidence': 0.70,  # 템플릿 기반 = 중간 신뢰도
            'reasoning': f"템플릿 '{template['template_name']}' 사용, {len(results)}개 모형 평균"
        }
```

**효과**:
- Thinking 모델 의존도: 80% → 20%
- 일반 LLM으로 충분 (템플릿 선택만)
- 응답 시간: 10-60초 → 2-5초
- 비용: 1/10

---

### Strategy 2: Few-shot 예시 강화 ⭐⭐⭐

**핵심**: 명시적 예시로 LLM 가이드

#### Before (암묵적 기대)

```yaml
umis.yaml (현재):
  "Estimator는 값을 추정합니다"
  
  → LLM이 스스로 어떻게 추정할지 고민 (Thinking 필요)
```

#### After (명시적 Few-shot)

```yaml
umis.yaml (개선):
  "Estimator 사용 예시 (10개):"
  
  예시 1:
    질문: "B2B SaaS 한국 ARPU는?"
    
    단계:
      1. 도메인 파악: B2B_SaaS, 한국
      2. Phase 2 검색: "B2B SaaS ARPU" → 없음
      3. Phase 3 Guestimation:
         - Statistical Source: 글로벌 평균 $100
         - Region Adjustment: 한국 = 글로벌 × 0.6
         - Segment Adjustment: B2B = B2C × 3
         - 결과: $100 × 0.6 × 3 = $180 = 200,000원
      4. 신뢰도: 0.70 (Phase 3)
    
    출력:
      value: 200000
      confidence: 0.70
      phase: 3
      reasoning_detail: {...}
  
  예시 2:
    질문: "서울 피아노 학원 수는?"
    
    단계:
      1. 템플릿 선택: "지역별_장소_개수"
      2. 모형 1: 서울_인구(1000만) × (1 / 1인당_학원수(5000))
         = 2,000개
      3. 모형 2: 서울_초중고생(100만) × 학원_참여율(0.3%)
         = 3,000개
      4. 평균: 2,500개
    
    출력:
      value: 2500
      confidence: 0.65
      phase: 4
  
  ... (10개 예시)

LLM이 예시를 보고 패턴 학습 → Thinking 불필요!
```

#### 구현

```yaml
# umis.yaml에 추가

estimator_examples:
  - id: EX-001
    category: saas_metrics
    question: "B2B SaaS 한국 ARPU는?"
    expected_steps: [...]
    expected_output: {...}
  
  - id: EX-002
    category: fermi_decomposition
    question: "서울 피아노 학원 수는?"
    expected_steps: [...]
    expected_output: {...}
  
  # ... 20-30개

# AI 호출 시 관련 예시 3개 자동 삽입
```

**효과**:
- LLM이 예시 모방 (Thinking 불필요)
- 정확도: 60% → 80%
- 비용: 동일 (예시 토큰은 캐싱 가능)

---

### Strategy 3: 단계별 체크리스트 ⭐⭐

**핵심**: 복잡한 작업을 작은 단계로 분해

#### Before (한 번에 처리)

```yaml
Explorer Workflow (현재):
  "구독 모델 기회 분석해줘"
  
  → LLM이 5단계를 한 번에 처리 (Thinking 필요)
    1. 패턴 검색
    2. 사례 검색
    3. Estimator 협업
    4. Quantifier 협업
    5. 가설 생성
```

#### After (단계별 명시)

```yaml
Explorer Workflow (개선):
  "구독 모델 기회 분석"
  
  → AI가 단계별로 진행 (각 단계는 단순)
  
  Step 1: 패턴 검색
    체크리스트:
      - [ ] RAG 검색 실행 (query: "구독 모델")
      - [ ] Top 5 패턴 확인
      - [ ] 유사도 >= 0.8 필터링
      - [ ] 결과: 3개 패턴 발견
    
    → 다음 단계로 (일반 LLM 충분)
  
  Step 2: 사례 검색
    체크리스트:
      - [ ] 각 패턴별 사례 검색
      - [ ] 산업별 필터링
      - [ ] Top 3 사례 선택
      - [ ] 결과: 9개 사례 (3 패턴 × 3 사례)
    
    → 다음 단계로
  
  Step 3: 추정 필요성 판단
    체크리스트:
      - [ ] "시장 규모 언급 있나?" → 없음
      - [ ] "정량적 기회 크기 필요?" → 필요
      - [ ] "Estimator 호출?" → YES
    
    → Estimator 호출 (별도 Agent)
  
  ... (각 단계 독립적, 단순)
```

**구현**:

```python
# umis_rag/agents/explorer.py (개선)

class ExplorerRAG:
    def analyze_opportunity(self, query: str) -> dict:
        """
        단계별 체크리스트 실행
        """
        # Step 1: 패턴 검색 (단순)
        checklist_1 = self._execute_checklist("pattern_search", query)
        if not checklist_1['passed']:
            return {'error': 'Step 1 실패'}
        
        # Step 2: 사례 검색 (단순)
        checklist_2 = self._execute_checklist("case_search", checklist_1['output'])
        
        # Step 3: 추정 판단 (단순 if-then)
        if self._needs_estimation(checklist_2['output']):
            estimator_result = self.estimator.estimate(...)
        
        # ... 각 단계 독립 실행
    
    def _execute_checklist(self, step_name: str, input_data: dict) -> dict:
        """
        체크리스트 실행 (일반 LLM으로 충분)
        """
        checklist = self.CHECKLISTS[step_name]
        
        results = {}
        for item in checklist['items']:
            # 각 항목은 단순 (Yes/No 또는 간단한 추출)
            results[item['id']] = self._check_item(item, input_data)
        
        return {
            'passed': all(results.values()),
            'output': self._aggregate(results)
        }
```

**효과**:
- 각 단계는 단순 → 일반 LLM 충분
- 전체 복잡도 분산
- 디버깅 쉬움 (어느 단계 실패 명확)

---

### Strategy 4: 룰 기반 시스템 강화 ⭐⭐⭐

**핵심**: LLM 호출 최소화, 확정적 로직 활용

#### 영역별 룰 강화

```yaml
1. Validator 정의 검증:
  Before (LLM 판단):
    "이 데이터의 정의가 일치하나요?"
    → LLM이 자유롭게 판단 (불확실)
  
  After (룰 기반):
    정의 일치 체크:
      - 시간 단위 일치? (연/월/일)
      - 지역 범위 일치? (전국/서울)
      - 세그먼트 일치? (B2B/B2C)
    
    불일치 발견 시:
      if 시간_단위_다름:
        자동_변환(원본_값, 원본_단위, 목표_단위)
      
      if 지역_범위_다름:
        경고("지역 불일치, 사용 주의")
    
    → LLM 불필요! (100% 룰 기반)

2. Estimator 단위 변환:
  Before:
    "갑/년을 갑/일로 변환"
    → LLM 계산 (오류 가능)
  
  After:
    UNIT_CONVERSIONS = {
      ('갑/년', '갑/일'): lambda x: x / 365,
      ('원/월', '원/년'): lambda x: x * 12,
      ('명', '천명'): lambda x: x / 1000,
      # ... 100개 변환 룰
    }
    
    → 즉시 계산 (LLM 불필요)

3. Quantifier 공식:
  Before:
    "LTV 계산해줘"
    → LLM이 공식 기억 (불확실)
  
  After:
    FORMULAS = {
      'LTV': lambda arpu, churn: arpu / churn,
      'Payback': lambda cac, arpu, margin: cac / (arpu * margin),
      'CAC_Ratio': lambda ltv, cac: ltv / cac,
      # ... 31개 공식
    }
    
    → 확정적 계산 (LLM 불필요)
```

**구현**:

```python
# umis_rag/core/rules_engine.py (신규)

class RulesEngine:
    """
    확정적 룰 기반 처리 (LLM 불필요)
    """
    
    UNIT_CONVERSIONS = {
        ('갑/년', '갑/일'): lambda x: x / 365,
        ('원/월', '원/년'): lambda x: x * 12,
        # ... 100개
    }
    
    FORMULAS = {
        'LTV': lambda arpu, churn: arpu / churn,
        'Payback': lambda cac, arpu, margin: cac / (arpu * margin),
        # ... 31개
    }
    
    DEFINITION_CHECKS = {
        '시간_단위': ['년', '월', '일', '시간'],
        '지역_범위': ['전국', '서울', '경기', '부산', ...],
        '세그먼트': ['B2B', 'B2C', 'B2B2C'],
    }
    
    def convert_unit(self, value: float, from_unit: str, to_unit: str) -> float:
        """단위 변환 (LLM 불필요)"""
        converter = self.UNIT_CONVERSIONS.get((from_unit, to_unit))
        if converter:
            return converter(value)
        else:
            raise ValueError(f"변환 불가: {from_unit} → {to_unit}")
    
    def calculate_metric(self, metric_name: str, **variables) -> float:
        """지표 계산 (LLM 불필요)"""
        formula = self.FORMULAS.get(metric_name)
        if formula:
            return formula(**variables)
        else:
            raise ValueError(f"공식 없음: {metric_name}")
    
    def check_definition(self, data: dict) -> list[str]:
        """정의 검증 (LLM 불필요)"""
        warnings = []
        
        for field, valid_values in self.DEFINITION_CHECKS.items():
            if data.get(field) not in valid_values:
                warnings.append(f"{field} 불일치: {data.get(field)}")
        
        return warnings
```

**효과**:
- LLM 호출 50% 감소
- 정확도 100% (확정적 계산)
- 비용 대폭 절감

---

### Strategy 5: 하이브리드 모드 (선택적 Thinking) ⭐

**핵심**: 간단한 작업은 일반 LLM, 복잡한 작업만 Thinking

```yaml
작업별 모델 선택:

일반 LLM (GPT-4o, Claude Sonnet):
  - Phase 0-2 (확정 데이터)
  - Phase 3 (Guestimation, 템플릿 기반)
  - 체크리스트 실행
  - 패턴 검색
  - 정의 검증
  
  비율: 85-90% 작업

Thinking 모델 (o1-mini):
  - Phase 4 Step 2 (모형 생성, 창의적)
  - Discovery Sprint (모호한 목표 구체화)
  - 새로운 도메인 (템플릿 없음)
  
  비율: 10-15% 작업

효과:
  비용: Thinking 100% 대비 70% 절감
  속도: 평균 5배 향상
  정확도: 유지 (복잡한 부분만 Thinking)
```

**구현**:

```python
# umis_rag/core/llm_router.py (신규)

class LLMRouter:
    """
    작업 복잡도에 따라 모델 선택
    """
    
    COMPLEXITY_THRESHOLDS = {
        'simple': 0.3,     # 일반 LLM
        'moderate': 0.6,   # 일반 LLM (강화 프롬프트)
        'complex': 0.8,    # o1-mini
        'very_complex': 1.0  # o1 (최고 성능)
    }
    
    def select_model(self, task: dict) -> str:
        """
        작업 분석 → 모델 선택
        """
        complexity = self._analyze_complexity(task)
        
        if complexity < 0.3:
            return 'gpt-4o'  # 빠르고 저렴
        elif complexity < 0.6:
            return 'claude-sonnet-4'  # 균형
        elif complexity < 0.8:
            return 'o1-mini'  # 복잡한 추론
        else:
            return 'o1'  # 최고 성능
    
    def _analyze_complexity(self, task: dict) -> float:
        """
        복잡도 점수 계산 (룰 기반)
        """
        score = 0.0
        
        # 요인 1: 템플릿 존재 여부
        if self._has_template(task['query']):
            score += 0.0  # 템플릿 있음 = 단순
        else:
            score += 0.4  # 템플릿 없음 = 복잡
        
        # 요인 2: 변수 개수
        if task.get('num_variables', 0) > 5:
            score += 0.3  # 변수 많음 = 복잡
        
        # 요인 3: 재귀 필요성
        if task.get('needs_recursion', False):
            score += 0.3  # 재귀 = 복잡
        
        return min(score, 1.0)

# 사용 예시
router = LLMRouter()

# 간단한 작업
task_1 = {'query': 'B2B SaaS ARPU는?', 'num_variables': 2}
model_1 = router.select_model(task_1)  # → 'gpt-4o'

# 복잡한 작업
task_2 = {'query': '서울 음식점 수는?', 'num_variables': 6, 'needs_recursion': True}
model_2 = router.select_model(task_2)  # → 'o1-mini'
```

---

## 📊 종합 비교

### 개선 전후 비교

| 지표 | Before (Thinking 의존) | After (개선) | 개선율 |
|------|----------------------|-------------|--------|
| **LLM 비용** | $60/1M 토큰 (o1) | $8/1M 토큰 (평균) | **87% 절감** |
| **응답 시간** | 10-60초 | 2-10초 | **5-6배 빠름** |
| **정확도** | 85% (Thinking) | 80% (일반 LLM + 룰) | -5% (허용 가능) |
| **Thinking 사용** | 100% 작업 | 10-15% 작업 | **85% 감소** |
| **유지보수** | 어려움 (암묵적) | 쉬움 (명시적 룰) | ✅ |

### 작업별 개선 효과

```yaml
Estimator Phase 1-3:
  Before: o1 필요 (복잡한 판단)
  After: GPT-4o 충분 (템플릿 선택)
  비용 절감: 90%
  속도: 8배 빠름

Estimator Phase 4:
  Before: o1 필수 (창의적 모형 생성)
  After: 
    - Step 1,3,4: GPT-4o (템플릿 실행)
    - Step 2만: o1-mini (모형 생성)
  비용 절감: 75%
  속도: 4배 빠름

Explorer Workflow:
  Before: o1 권장 (5단계 한 번에)
  After: GPT-4o 충분 (단계별 체크리스트)
  비용 절감: 85%
  속도: 6배 빠름

Discovery Sprint:
  Before: o1 필수 (모호한 목표 구체화)
  After: o1-mini (복잡도 중간 수준)
  비용 절감: 80%
  속도: 3배 빠름
```

---

## 🚀 구현 로드맵

### Phase 1: 룰 강화 (즉시 실행, v7.8.0)

```yaml
작업:
  1. RulesEngine 구현
     - 단위 변환 100개 룰
     - 지표 공식 31개
     - 정의 검증 체크리스트
  
  2. Validator 룰 기반 전환
     - Definition Gap → 체크리스트
     - 단위 변환 → 자동
  
  3. Quantifier 공식 하드코딩
     - 31개 방법론 → Python 함수
  
  효과:
    - LLM 호출 30% 감소
    - 비용 30% 절감
    - 정확도 95% → 100% (확정적)
  
  소요: 1-2일
```

### Phase 2: 의사결정 트리 (1주, v7.9.0)

```yaml
작업:
  1. FermiDecisionTree 구현
     - 20-30개 템플릿 정의
     - 템플릿 선택 룰
     - 자동 실행 엔진
  
  2. Estimator 통합
     - Phase 4 → 템플릿 기반
     - Fallback: LLM (템플릿 없을 때만)
  
  효과:
    - Phase 4 LLM 의존 80% → 20%
    - 비용 60% 절감
    - 응답 시간 10배 빠름
  
  소요: 1주
```

### Phase 3: Few-shot 예시 (2-3일, v7.9.1)

```yaml
작업:
  1. umis.yaml에 예시 20-30개 추가
     - Estimator: 10개
     - Explorer: 5개
     - Observer: 5개
     - Discovery Sprint: 5개
  
  2. 자동 예시 삽입
     - 질문 유형별 관련 예시 3개 선택
     - 프롬프트에 자동 추가
  
  효과:
    - 정확도 60% → 80%
    - LLM 학습 효과 (암묵적 → 명시적)
  
  소요: 2-3일
```

### Phase 4: 체크리스트 시스템 (1주, v7.10.0)

```yaml
작업:
  1. 체크리스트 정의
     - Explorer: 5단계 × 5개 체크리스트
     - Observer: 구조 분석 체크리스트
     - Discovery Sprint: 목표 구체화 체크리스트
  
  2. Workflow 재설계
     - 한 번에 처리 → 단계별 독립 실행
     - 각 단계 pass/fail 명확
  
  효과:
    - 복잡도 분산 (일반 LLM 충분)
    - 디버깅 쉬움
  
  소요: 1주
```

### Phase 5: LLM Router (선택, v7.11.0)

```yaml
작업:
  1. LLMRouter 구현
     - 복잡도 분석 룰
     - 모델 선택 로직
  
  2. 비용 최적화
     - 간단한 85%: GPT-4o
     - 복잡한 15%: o1-mini
  
  효과:
    - 비용 70% 절감 (Thinking 100% 대비)
    - 속도 5배 향상 (평균)
  
  소요: 3-5일
```

---

## 💡 우선순위 권장

### 즉시 실행 (ROI 최고)

```yaml
1. RulesEngine (Phase 1):
   ROI: ⭐⭐⭐⭐⭐
   - 구현 쉬움 (1-2일)
   - 효과 즉각적 (30% 비용 절감)
   - 부작용 없음 (확정적 로직)

2. FermiDecisionTree (Phase 2):
   ROI: ⭐⭐⭐⭐
   - 구현 중간 (1주)
   - 효과 큼 (60% 비용 절감)
   - Estimator 핵심 개선

3. Few-shot 예시 (Phase 3):
   ROI: ⭐⭐⭐⭐
   - 구현 쉬움 (2-3일)
   - 정확도 대폭 향상
   - 유지보수 쉬움
```

### 선택 실행 (필요 시)

```yaml
4. 체크리스트 시스템 (Phase 4):
   ROI: ⭐⭐⭐
   - 구현 중간 (1주)
   - 효과 중간
   - Workflow 복잡도 증가 가능

5. LLM Router (Phase 5):
   ROI: ⭐⭐
   - 구현 복잡 (3-5일)
   - 효과 상황별 다름
   - 추가 인프라 필요
```

---

## 🎯 최종 권장

### 당장 실행 (v7.8.0)

```yaml
최소 구현 (1주 이내):
  1. RulesEngine 구현 ⭐⭐⭐
     - 단위 변환
     - 공식 하드코딩
     - 정의 검증
  
  2. Few-shot 예시 10개 ⭐⭐⭐
     - Estimator 예시 5개
     - Explorer 예시 3개
     - Discovery Sprint 예시 2개
  
  효과:
    - 비용 40-50% 절감
    - Thinking 모델 의존 80% → 40%
    - 정확도 유지 또는 향상
    - 구현 시간: 3-5일
```

### 2주 내 완성 (v7.9.0)

```yaml
전체 구현:
  + FermiDecisionTree (20개 템플릿) ⭐⭐⭐
  + Few-shot 예시 30개 ⭐⭐⭐
  + 체크리스트 시스템 (선택) ⭐⭐
  
  최종 효과:
    - 비용: 87% 절감 (o1 대비)
    - Thinking 의존: 100% → 10-15%
    - 속도: 5-6배 향상
    - 정확도: 80% (일반 LLM 충분)
```

### 비교

```yaml
현재 (Thinking 100%):
  o1 모델: $60/1M 입력 + $200/1M 출력
  평균 작업: 2,000 입력 + 1,000 출력 = $0.32
  100회 작업: $32

개선 후 (일반 LLM 85%):
  GPT-4o: $5/1M 입력 + $15/1M 출력
  평균 작업: 2,000 입력 + 1,000 출력 = $0.025
  100회 작업: $2.5 (85회) + $4.8 (15회 o1-mini) = $7.3
  
  절감: $32 → $7.3 (77% 절감!)
```

---

## 📋 체크리스트

- [ ] 1. RulesEngine 구현 (단위 변환, 공식)
- [ ] 2. Few-shot 예시 10-30개 작성
- [ ] 3. FermiDecisionTree 템플릿 20개
- [ ] 4. Estimator 통합 테스트
- [ ] 5. 비용/성능 벤치마크
- [ ] 6. (선택) 체크리스트 시스템
- [ ] 7. (선택) LLM Router

---

**작성자**: AI Assistant
**작성일**: 2025-11-18
**목적**: Thinking 모델 의존도 감소, 비용 절감
**목표**: 일반 LLM(GPT-4o, Claude)으로 85-90% 작업 처리

---

*Thinking 모델은 강력하지만 비용이 높습니다. 명시적 룰, 템플릿, 예시를 활용하면 일반 LLM으로도 충분히 효과적인 시스템을 만들 수 있습니다.*




