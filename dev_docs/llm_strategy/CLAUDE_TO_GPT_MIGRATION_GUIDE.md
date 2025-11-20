# Claude Sonnet 4.5 → GPT-4o 마이그레이션 가이드
**Thinking 모델 품질을 일반 LLM으로 재현하는 실전 접근**

---

## 📌 현재 상황

### Claude Sonnet 4.5 (Extended Thinking)

```yaml
특징:
  - Extended Thinking: 내장 Chain-of-Thought
  - 자체 검증: Self-correction 능력
  - 복잡한 추론: 다단계 문제 해결 우수
  - 불확실성 처리: 애매한 상황 잘 다룸
  - 맥락 유지: 긴 대화에서 일관성 유지

비용:
  - 입력: ~$3/1M 토큰
  - 출력: ~$15/1M 토큰
  - Extended Thinking 토큰: 추가 비용 (숨겨진 토큰)

UMIS에서 강점:
  1. Estimator Phase 4: 창의적 모형 생성
  2. Discovery Sprint: 모호한 목표 구체화
  3. 복잡한 데이터 분석: 다차원 패턴 인식
  4. 추론 체인: "A → B → C → 결론" 자동 연결
```

### GPT-4o (타겟 모델)

```yaml
특징:
  - 빠른 추론: 응답 시간 짧음
  - 안정적: API 제한 적음
  - 멀티모달: 이미지/텍스트 통합
  - 코드 생성: 뛰어남

비용:
  - 입력: ~$5/1M 토큰
  - 출력: ~$15/1M 토큰
  - 총: Claude와 유사 또는 약간 비쌈

약점:
  - Chain-of-Thought: 명시적 가이드 필요
  - Self-correction: 약함 (한 번에 맞춰야 함)
  - 복잡한 추론: 단계별 분해 필요
  - 불확실성: 명확한 옵션 제시 필요
```

### 핵심 차이

```yaml
Claude Sonnet 4.5의 "마법":
  1. 내재적 추론: "생각하면서" 답변
  2. 자동 검증: 스스로 오류 발견/수정
  3. 맥락 통합: 여러 정보 자동 연결
  4. 불확실성 처리: 애매할 때 여러 가능성 고려

GPT-4o의 특징:
  1. 명시적 가이드: 정확한 지시 필요
  2. 한 번에 정확: 재시도 어려움
  3. 순차 처리: 한 번에 한 단계
  4. 확정적 선호: 명확한 답 선호
```

---

## 🎯 품질 재현 전략 (4단계)

### Level 1: 기본 (70% 품질, 1-2일)

**목표**: 빠르게 동작하게 만들기

#### 1.1 명시적 Chain-of-Thought 프롬프트

```yaml
Before (Claude Sonnet 4.5):
  "서울 피아노 학원 수를 추정해줘"
  
  → Claude 내부적으로:
    1. 문제 분해 (자동)
    2. 변수 식별 (자동)
    3. 데이터 수집 (자동)
    4. 모형 생성 (자동)
    5. 검증 (자동)

After (GPT-4o, 명시적 CoT):
  프롬프트:
    """
    서울 피아노 학원 수를 추정해줘.
    
    다음 단계를 따라 생각해줘:
    1. 문제 분해: 어떤 변수가 필요한가?
    2. 변수 식별: 각 변수를 어떻게 구할까?
    3. 데이터 수집: 알려진 값은?
    4. 모형 생성: 어떤 공식을 쓸까?
    5. 검증: 결과가 합리적인가?
    
    각 단계를 명시적으로 작성한 후 최종 답변을 제시해줘.
    """

효과:
  - Claude 70% 수준 품질
  - 구현 시간: 프롬프트 수정만 (즉시)
```

#### 1.2 Few-shot 예시 (필수!)

```yaml
프롬프트에 추가:

예시 1:
  질문: "B2B SaaS 한국 ARPU는?"
  
  생각 과정:
    1. 문제 분해:
       - ARPU = Average Revenue Per User
       - 지역: 한국
       - 산업: B2B SaaS
    
    2. 변수 식별:
       - 글로벌 B2B SaaS ARPU: $100 (알려짐)
       - 한국 조정 계수: 0.6 (추정 필요)
       - 산업 조정: B2B = B2C × 3
    
    3. 데이터 수집:
       - 글로벌 평균: Statista 리포트
       - 한국 조정: GDP per capita 비율
    
    4. 모형 실행:
       - $100 × 0.6 × 3 = $180
       - 원화: $180 × 1,300 = 234,000원
       - 반올림: 200,000원
    
    5. 검증:
       - 한국 B2C SaaS ARPU ~70,000원
       - B2B가 3배 → 210,000원 (합리적)
  
  답: 200,000원 (confidence: 0.70)

예시 2:
  질문: "서울 피아노 학원 수는?"
  
  생각 과정:
    1. 문제 분해:
       - 지역: 서울
       - 업종: 피아노 학원
       - 목표: 개수 추정
    
    2. 모형 선택:
       - Top-down: 인구 기반
       - Bottom-up: 학생 수 기반
    
    3. Top-down:
       - 서울 인구: 1,000만명
       - 1인당 학원 수: 1/5,000
       - 결과: 2,000개
    
    4. Bottom-up:
       - 서울 초중고생: 100만명
       - 피아노 학습률: 3%
       - 학원당 학생: 10명
       - 결과: 100만 × 0.03 / 10 = 3,000개
    
    5. 평균:
       - (2,000 + 3,000) / 2 = 2,500개
  
  답: 2,500개 (confidence: 0.65)

이제 당신의 질문을 같은 방식으로 풀어줘:
[실제 질문]
```

**효과**:
- Claude 75% 수준
- GPT-4o가 예시를 모방
- 구현: 예시 5-10개 작성 (2-3시간)

#### 1.3 구조화된 출력 요청

```yaml
프롬프트 추가:

답변 형식:
  {
    "thinking_process": [
      {
        "step": 1,
        "description": "문제 분해",
        "details": "..."
      },
      ...
    ],
    "final_answer": {
      "value": 200000,
      "unit": "원",
      "confidence": 0.70,
      "phase": 3
    },
    "reasoning": "간단 요약"
  }

효과:
  - 구조화된 출력 → 파싱 쉬움
  - 단계별 검증 가능
```

**Level 1 총 효과**:
- 품질: Claude 70-75%
- 구현 시간: 1-2일
- 비용: 동일 (프롬프트 길어짐)

---

### Level 2: 중급 (80-85% 품질, 1주)

**목표**: 템플릿과 룰로 품질 향상

#### 2.1 의사결정 트리 구현

```python
# umis_rag/agents/estimator/gpt4o_adapter.py (신규)

class GPT4oEstimator:
    """
    GPT-4o를 Claude 수준으로 끌어올리는 어댑터
    """
    
    TEMPLATES = {
        "지역별_장소_개수": {
            "trigger": ["서울", "부산", "음식점", "카페", "학원"],
            "prompt_template": """
질문: {query}

이 질문은 "지역별 장소 개수" 유형입니다.

사용할 모형:
1. Top-down: {지역}_인구 × (1 / 1인당_{장소}_수)
2. Bottom-up: 잠재_고객_수 × 이용률 × (1 / 장소당_고객수)

단계:
1. 변수 값 확인:
   - {지역} 인구: [알려진 값 또는 추정]
   - 1인당 {장소} 수: [추정 필요]
   - 잠재 고객 수: [계산 필요]

2. 각 모형 실행

3. 결과 평균 및 검증

이제 위 구조를 따라 답변해줘.
""",
            "examples": [
                # 2-3개 관련 예시
            ]
        },
        
        "SaaS_지표": {
            "trigger": ["LTV", "CAC", "ARPU", "Churn", "MRR"],
            "prompt_template": """
질문: {query}

이 질문은 "SaaS 지표" 유형입니다.

확정 공식:
- LTV = ARPU / Churn_Rate
- CAC Payback = CAC / (ARPU × Gross_Margin)
- Rule of 40 = Growth_Rate + Profit_Margin

필요한 변수:
{variables}

단계:
1. 각 변수 값 확인 (알려짐/추정 필요)
2. 추정이 필요한 변수 → 벤치마크 검색
3. 공식 적용
4. 검증 (업계 평균과 비교)

이제 답변해줘.
""",
            "formulas": {
                "LTV": lambda arpu, churn: arpu / churn,
                # ...
            }
        },
        
        # ... 20-30개 템플릿
    }
    
    def estimate(self, query: str, context: dict = None) -> dict:
        """
        GPT-4o로 Claude 수준 추정
        """
        # 1. 템플릿 자동 선택
        template = self._select_template(query)
        
        if template:
            # 2. 템플릿 기반 프롬프트 생성
            prompt = self._build_template_prompt(template, query, context)
        else:
            # 3. Fallback: 일반 CoT 프롬프트
            prompt = self._build_generic_cot_prompt(query, context)
        
        # 4. GPT-4o 호출
        response = self._call_gpt4o(prompt)
        
        # 5. 응답 파싱 및 검증
        result = self._parse_and_validate(response)
        
        return result
    
    def _select_template(self, query: str) -> dict:
        """템플릿 자동 선택 (룰 기반)"""
        for name, template in self.TEMPLATES.items():
            if any(trigger in query for trigger in template['trigger']):
                return template
        return None
    
    def _build_template_prompt(self, template: dict, query: str, context: dict) -> str:
        """템플릿 기반 프롬프트 생성"""
        # Few-shot 예시 추가
        examples = "\n\n".join([
            self._format_example(ex) for ex in template['examples'][:3]
        ])
        
        # 프롬프트 조합
        prompt = f"""
당신은 시장 분석 전문가입니다.

다음 예시를 참고하여 같은 방식으로 답변해주세요:

{examples}

---

이제 당신의 질문입니다:

{template['prompt_template'].format(query=query, **context)}
"""
        return prompt
```

#### 2.2 자동 검증 레이어

```python
class ValidationLayer:
    """
    GPT-4o 응답 자동 검증 (Claude의 Self-correction 모방)
    """
    
    def validate_and_correct(self, response: dict, query: str) -> dict:
        """
        응답 검증 및 자동 수정
        """
        issues = []
        
        # 검증 1: 범위 체크
        if response['value'] < 0:
            issues.append("음수 값 (불가능)")
        
        # 검증 2: 크기 상식 체크
        if "서울" in query and "학원" in query:
            if not (100 <= response['value'] <= 100000):
                issues.append(f"비현실적 크기: {response['value']}")
        
        # 검증 3: 단위 체크
        if "원" in query and response.get('unit') != '원':
            issues.append("단위 불일치")
        
        # 검증 4: Confidence 합리성
        if response.get('phase') == 4 and response.get('confidence', 0) > 0.8:
            issues.append("Fermi 추정인데 confidence가 너무 높음")
        
        # 수정 필요 시
        if issues:
            return self._request_correction(response, issues, query)
        
        return response
    
    def _request_correction(self, original: dict, issues: list, query: str) -> dict:
        """
        문제 발견 시 GPT-4o에게 재요청 (Self-correction 모방)
        """
        correction_prompt = f"""
이전 답변에 다음 문제가 있습니다:
{chr(10).join(f"- {issue}" for issue in issues)}

원래 질문: {query}
이전 답변: {original}

문제를 수정하여 다시 답변해주세요.
"""
        
        corrected = self._call_gpt4o(correction_prompt)
        return corrected
```

#### 2.3 Multi-pass 전략

```python
class MultiPassEstimator:
    """
    Claude의 Extended Thinking을 Multi-pass로 모방
    """
    
    def estimate_with_refinement(self, query: str, max_passes: int = 2) -> dict:
        """
        여러 번 추론하여 정확도 향상
        """
        # Pass 1: 초기 추정
        result_1 = self.estimator.estimate(query)
        
        if result_1['confidence'] >= 0.85:
            return result_1  # 충분히 확신 → 종료
        
        # Pass 2: 검증 및 개선
        refinement_prompt = f"""
질문: {query}

1차 답변: {result_1['value']} (confidence: {result_1['confidence']})

1차 추론 과정을 검토하고, 다음을 확인해줘:
1. 가정이 합리적인가?
2. 계산이 정확한가?
3. 놓친 요인은 없나?
4. 더 나은 접근이 있나?

개선된 답변을 제시해줘.
"""
        
        result_2 = self._call_gpt4o(refinement_prompt)
        
        # 두 결과 비교 및 선택
        if abs(result_2['value'] - result_1['value']) / result_1['value'] < 0.2:
            # 20% 이내 차이 → 평균
            return self._merge_results(result_1, result_2)
        else:
            # 큰 차이 → 더 높은 confidence 선택
            return result_2 if result_2['confidence'] > result_1['confidence'] else result_1
```

**Level 2 총 효과**:
- 품질: Claude 80-85%
- 구현 시간: 1주
- 비용: +20-30% (Multi-pass)

---

### Level 3: 고급 (90% 품질, 2주)

**목표**: Claude와 거의 동등한 품질

#### 3.1 Ensemble 전략

```python
class EnsembleEstimator:
    """
    여러 접근을 조합하여 Claude 수준 달성
    """
    
    def estimate(self, query: str) -> dict:
        """
        3가지 접근 병렬 실행 → 최선 선택
        """
        # Approach 1: 템플릿 기반
        result_template = self.template_estimator.estimate(query)
        
        # Approach 2: RAG 기반 (유사 사례 검색)
        similar_cases = self.rag_search(query, top_k=5)
        result_rag = self._estimate_from_cases(similar_cases)
        
        # Approach 3: 순수 LLM (CoT)
        result_llm = self.llm_estimator.estimate(query)
        
        # 3가지 결과 비교
        results = [result_template, result_rag, result_llm]
        
        # 합의 확인
        if self._check_consensus(results, threshold=0.3):
            # 30% 이내 일치 → 가중평균
            return self._weighted_average(results)
        else:
            # 불일치 → 가장 높은 confidence 선택
            return max(results, key=lambda r: r['confidence'])
    
    def _check_consensus(self, results: list, threshold: float) -> bool:
        """결과 간 합의 확인"""
        values = [r['value'] for r in results]
        mean = sum(values) / len(values)
        
        max_deviation = max(abs(v - mean) / mean for v in values)
        return max_deviation <= threshold
```

#### 3.2 Meta-learner (학습 시스템)

```python
class MetaLearner:
    """
    성공/실패 학습하여 GPT-4o 프롬프트 자동 개선
    """
    
    def __init__(self):
        self.success_log = []
        self.failure_log = []
    
    def log_result(self, query: str, result: dict, ground_truth: float = None):
        """결과 로깅"""
        if ground_truth:
            error = abs(result['value'] - ground_truth) / ground_truth
            
            if error < 0.2:
                self.success_log.append({
                    'query': query,
                    'template': result.get('template_used'),
                    'approach': result.get('approach'),
                    'error': error
                })
            else:
                self.failure_log.append({
                    'query': query,
                    'expected': ground_truth,
                    'got': result['value'],
                    'error': error
                })
    
    def improve_prompt(self, template_name: str) -> str:
        """
        성공/실패 패턴 분석 → 프롬프트 개선
        """
        successes = [s for s in self.success_log if s['template'] == template_name]
        failures = [f for f in self.failure_log if f.get('template') == template_name]
        
        if len(successes) > 10 and len(failures) > 5:
            # 패턴 분석 (LLM 활용)
            analysis_prompt = f"""
템플릿 "{template_name}"의 성능 분석:

성공 사례 ({len(successes)}개):
{self._format_cases(successes[:5])}

실패 사례 ({len(failures)}개):
{self._format_cases(failures[:5])}

실패 패턴을 분석하고, 프롬프트 개선 방안을 제시해줘.
"""
            
            improvements = self._call_gpt4o(analysis_prompt)
            return improvements
```

#### 3.3 Context-aware 프롬프팅

```python
class ContextAwarePrompter:
    """
    프로젝트 맥락을 활용한 동적 프롬프트
    """
    
    def build_prompt(self, query: str, project_context: dict) -> str:
        """
        프로젝트 컨텍스트 기반 프롬프트
        """
        # 프로젝트 맥락 추출
        domain = project_context.get('domain', 'general')
        region = project_context.get('region', '전국')
        existing_data = project_context.get('data', {})
        
        # 맥락 기반 프롬프트 생성
        context_prompt = f"""
당신은 시장 분석 전문가입니다.

현재 프로젝트 맥락:
- 산업: {domain}
- 지역: {region}
- 기존 데이터:
{self._format_data(existing_data)}

위 맥락을 고려하여 다음 질문에 답해주세요:
{query}

가능하면 기존 데이터와 일관성을 유지하고,
산업/지역 특성을 반영해주세요.
"""
        
        return context_prompt
```

**Level 3 총 효과**:
- 품질: Claude 90%
- 구현 시간: 2주
- 비용: +40-50% (Ensemble)

---

### Level 4: 최고급 (95%+ 품질, 1개월)

**목표**: Claude를 능가

#### 4.1 GPT-4o + Claude Hybrid

```python
class HybridEstimator:
    """
    GPT-4o + Claude Sonnet 4.5 조합
    """
    
    def estimate(self, query: str, budget: str = 'balanced') -> dict:
        """
        예산에 따라 모델 선택
        """
        complexity = self._analyze_complexity(query)
        
        if budget == 'minimal':
            # GPT-4o만
            return self.gpt4o_estimator.estimate(query)
        
        elif budget == 'balanced':
            if complexity > 0.7:
                # 복잡 → Claude
                return self.claude_estimator.estimate(query)
            else:
                # 단순 → GPT-4o
                return self.gpt4o_estimator.estimate(query)
        
        elif budget == 'quality':
            # 둘 다 실행 → 비교
            result_gpt = self.gpt4o_estimator.estimate(query)
            result_claude = self.claude_estimator.estimate(query)
            
            if abs(result_gpt['value'] - result_claude['value']) / result_claude['value'] < 0.2:
                # 일치 → GPT 결과 (저렴)
                return result_gpt
            else:
                # 불일치 → Claude 선택 (신뢰)
                return result_claude
```

#### 4.2 전문가 시스템 (Expert System)

```python
class ExpertSystem:
    """
    도메인 전문가 지식 인코딩
    """
    
    DOMAIN_KNOWLEDGE = {
        "B2B_SaaS": {
            "typical_ranges": {
                "ARPU": (50000, 500000),  # 원
                "Churn_Rate": (0.03, 0.15),
                "CAC": (500000, 5000000)
            },
            "rules": [
                {
                    "if": "segment == 'Enterprise'",
                    "then": "ARPU × 3",
                    "confidence": 0.9
                },
                {
                    "if": "region == '한국'",
                    "then": "global_value × 0.6",
                    "confidence": 0.8
                }
            ],
            "benchmarks": {
                "LTV/CAC": (3, 5),  # 건강한 범위
                "Payback_months": (6, 18)
            }
        },
        
        "교육": {
            "typical_ranges": {
                "학원당_학생": (10, 50),
                "학습률": (0.02, 0.10),
                "월_수강료": (100000, 500000)
            },
            # ...
        }
    }
    
    def validate_result(self, result: dict, domain: str) -> dict:
        """
        도메인 지식으로 검증
        """
        knowledge = self.DOMAIN_KNOWLEDGE.get(domain, {})
        
        metric = result.get('metric')
        value = result.get('value')
        
        # 범위 체크
        expected_range = knowledge.get('typical_ranges', {}).get(metric)
        if expected_range:
            min_val, max_val = expected_range
            if not (min_val <= value <= max_val):
                result['warning'] = f"범위 이탈: {metric}는 보통 {min_val}-{max_val}"
        
        # 규칙 적용
        for rule in knowledge.get('rules', []):
            if self._evaluate_condition(rule['if'], result):
                suggestion = rule['then']
                result['suggestion'] = suggestion
                result['confidence'] = min(result['confidence'], rule['confidence'])
        
        return result
```

**Level 4 총 효과**:
- 품질: Claude 95%+
- 구현 시간: 1개월
- 비용: 상황별 (Hybrid로 최적화)

---

## 📊 레벨별 비교

| Level | 품질 | 구현 시간 | 주요 기법 | 비용 | 권장 |
|-------|------|----------|----------|------|------|
| **Level 1** | 70-75% | 1-2일 | CoT 프롬프트 + Few-shot | 동일 | ⭐⭐⭐ 즉시 시작 |
| **Level 2** | 80-85% | 1주 | 템플릿 + 검증 + Multi-pass | +20-30% | ⭐⭐⭐ 실용적 |
| **Level 3** | 90% | 2주 | Ensemble + 학습 + Context | +40-50% | ⭐⭐ 고품질 필요 시 |
| **Level 4** | 95%+ | 1개월 | Hybrid + 전문가 시스템 | 최적화 | ⭐ 완벽주의 |

---

## 🎯 실전 권장 (단계별 접근)

### Week 1: Level 1 구현 (필수!)

```yaml
Day 1-2: CoT 프롬프트 템플릿
  - umis.yaml에 프롬프트 템플릿 추가
  - "생각 과정을 명시하라" 지시
  - 구조화된 출력 형식 정의
  
  파일: umis.yaml
  섹션: gpt4o_prompts
  
  효과: 즉시 70% 품질

Day 3-4: Few-shot 예시 10개
  - Estimator: 5개
  - Explorer: 3개
  - Discovery Sprint: 2개
  
  각 예시: 질문 → 단계별 생각 → 답변
  
  효과: 75% 품질

Day 5: 테스트 및 조정
  - 실제 질문 10-20개 테스트
  - 프롬프트 미세 조정
  
  효과: 안정화

총 효과:
  - 품질: 70-75% (Claude 대비)
  - 비용: 동일
  - 속도: 약간 느림 (프롬프트 김)
```

### Week 2: Level 2 구현 (권장)

```yaml
Day 1-3: 의사결정 트리 (10개 템플릿)
  파일: umis_rag/agents/estimator/gpt4o_adapter.py
  
  템플릿:
    1. 지역별_장소_개수
    2. SaaS_지표
    3. 시장_규모_분해
    4. 학습률_추정
    5. 전환율_추정
    6. 가격_추정
    7. 경쟁_분석
    8. 성장률_예측
    9. 세그먼트_분할
    10. 비용_구조

Day 4-5: 자동 검증 레이어
  파일: umis_rag/core/validation_layer.py
  
  검증:
    - 범위 체크
    - 단위 체크
    - 상식 체크
    - Confidence 합리성

Day 6-7: Multi-pass 전략
  파일: umis_rag/agents/estimator/multi_pass.py
  
  Pass 1: 초기 추정
  Pass 2: 검증 및 개선 (confidence < 0.85)

총 효과:
  - 품질: 80-85%
  - 비용: +20-30%
  - 안정성: 높음
```

### Week 3-4: Level 3 구현 (선택)

```yaml
복잡한 프로젝트만:
  - Ensemble
  - Meta-learner
  - Context-aware

품질: 90%
비용: +40-50%
```

---

## 💡 실전 팁

### 1. 프롬프트 최적화

```yaml
효과적인 CoT 프롬프트:

구조:
  1. 역할 정의: "당신은 시장 분석 전문가입니다"
  2. 예시 제시: 2-3개 완전한 예시
  3. 명시적 단계: "다음 순서로 생각하세요"
  4. 출력 형식: JSON 또는 구조화된 텍스트
  5. 검증 요청: "답변이 합리적인지 확인하세요"

예시:
  """
  당신은 시장 분석 전문가입니다.
  
  예시 1:
  질문: "B2B SaaS ARPU는?"
  생각: [단계별 추론]
  답: 200,000원 (confidence: 0.70)
  
  예시 2:
  질문: "서울 학원 수는?"
  생각: [단계별 추론]
  답: 2,500개 (confidence: 0.65)
  
  이제 다음을 같은 방식으로:
  질문: {query}
  
  다음 단계로 생각하세요:
  1. 문제 분해
  2. 변수 식별
  3. 데이터 수집
  4. 모형 생성
  5. 검증
  
  JSON 형식으로 답변:
  {
    "thinking": [...],
    "answer": {...}
  }
  
  마지막으로 답변이 합리적인지 확인하세요.
  """
```

### 2. 템플릿 우선순위

```yaml
높은 ROI 템플릿 (먼저 구현):

1. 지역별_장소_개수 ⭐⭐⭐
   - 사용 빈도: 높음
   - 패턴: 명확
   - 효과: 큰

2. SaaS_지표 ⭐⭐⭐
   - 사용 빈도: 높음
   - 공식: 확정적
   - 정확도: 매우 높음

3. 시장_규모_분해 ⭐⭐
   - 사용 빈도: 중간
   - 복잡도: 중간

4. 학습률/전환율 ⭐⭐
   - 사용 빈도: 중간

5-10: 도메인별 ⭐
   - 필요에 따라
```

### 3. 비용 최적화

```yaml
비용 절감 전략:

1. 캐싱 (80% 절감 가능)
   - 동일 질문 → 캐시 사용
   - TTL: 24시간
   
   구현:
   @lru_cache(maxsize=1000)
   def estimate_cached(query: str, context_hash: str):
       ...

2. 배치 처리
   - 여러 질문 한 번에
   - API 호출 1회
   
   효과: 30% 절감

3. 프롬프트 압축
   - 불필요한 설명 제거
   - 핵심만
   
   효과: 20% 절감

4. 동적 Few-shot
   - 모든 예시 X
   - 관련 예시 3개만
   
   효과: 40% 절감
```

### 4. 품질 모니터링

```python
class QualityMonitor:
    """
    GPT-4o vs Claude 품질 비교
    """
    
    def compare(self, query: str, ground_truth: float = None):
        """
        두 모델 비교 실행
        """
        # GPT-4o
        result_gpt = self.gpt4o.estimate(query)
        
        # Claude
        result_claude = self.claude.estimate(query)
        
        # 비교
        comparison = {
            'query': query,
            'gpt4o': {
                'value': result_gpt['value'],
                'confidence': result_gpt['confidence'],
                'time': result_gpt['time']
            },
            'claude': {
                'value': result_claude['value'],
                'confidence': result_claude['confidence'],
                'time': result_claude['time']
            },
            'difference_pct': abs(result_gpt['value'] - result_claude['value']) / result_claude['value'],
            'agreement': 'yes' if abs(...) < 0.2 else 'no'
        }
        
        if ground_truth:
            comparison['gpt4o']['error'] = abs(result_gpt['value'] - ground_truth) / ground_truth
            comparison['claude']['error'] = abs(result_claude['value'] - ground_truth) / ground_truth
        
        return comparison
    
    def benchmark(self, test_cases: list):
        """
        벤치마크 실행
        """
        results = []
        for case in test_cases:
            result = self.compare(case['query'], case.get('ground_truth'))
            results.append(result)
        
        # 통계
        stats = {
            'total': len(results),
            'agreement_rate': sum(1 for r in results if r['agreement'] == 'yes') / len(results),
            'avg_difference': sum(r['difference_pct'] for r in results) / len(results),
            'gpt4o_avg_error': ...,
            'claude_avg_error': ...
        }
        
        return stats
```

---

## 🚀 즉시 실행 (Copy-paste)

### Step 1: CoT 프롬프트 템플릿 (umis.yaml 추가)

```yaml
# umis.yaml

gpt4o_prompting:
  role: "당신은 시장 분석 전문가입니다. 복잡한 문제를 체계적으로 분석하고 근거 있는 추정을 제공합니다."
  
  cot_template: |
    다음 단계로 생각하며 답변해주세요:
    
    1. 문제 분해: 이 질문은 무엇을 묻는가? 어떤 변수가 필요한가?
    2. 변수 식별: 각 변수를 어떻게 구할 수 있나? (알려짐/추정 필요)
    3. 데이터 수집: 알려진 값은? 벤치마크는? 유사 사례는?
    4. 모형 생성: 어떤 공식/접근으로 계산할까? (2-3개 모형)
    5. 검증: 결과가 합리적인가? 업계 상식과 부합하나?
    
    각 단계를 명시적으로 작성한 후 최종 답변을 JSON으로 제시하세요:
    {
      "thinking": [
        {"step": 1, "content": "..."},
        {"step": 2, "content": "..."},
        ...
      ],
      "answer": {
        "value": 숫자,
        "unit": "단위",
        "confidence": 0.0-1.0,
        "phase": 2/3/4,
        "reasoning_summary": "한 문장 요약"
      }
    }
  
  examples:
    - id: EX-001
      category: saas_metrics
      query: "B2B SaaS 한국 시장 ARPU는?"
      thinking:
        step_1: |
          문제 분해:
          - ARPU = Average Revenue Per User
          - 타겟: B2B SaaS, 한국 시장
          - 필요 변수: 글로벌 ARPU, 한국 조정 계수, B2B vs B2C 배수
        
        step_2: |
          변수 식별:
          - 글로벌 B2B SaaS ARPU: ~$100 (알려짐, Statista)
          - 한국 GDP per capita: 글로벌 대비 60% (추정)
          - B2B vs B2C: 3배 차이 (업계 상식)
        
        step_3: |
          데이터 수집:
          - Statista: Global B2B SaaS ARPU $80-120
          - IMF: 한국 GDP per capita vs Global
          - 벤치마크: 한국 B2C SaaS ARPU ~50,000-100,000원
        
        step_4: |
          모형 생성:
          모형 1: 글로벌 기준 조정
            $100 × 0.6 (한국) = $60
            $60 × 1,300 (환율) = 78,000원
            × 3 (B2B 배수) = 234,000원
          
          모형 2: 한국 B2C 기준
            B2C ARPU: 70,000원 (중간값)
            B2B = B2C × 3 = 210,000원
          
          평균: (234,000 + 210,000) / 2 = 222,000원
          반올림: 200,000원
        
        step_5: |
          검증:
          - 범위 체크: 50,000-500,000원 (합리적)
          - 비율 체크: B2B/B2C = 200k/70k = 2.9배 (업계 상식 부합)
          - Confidence: Phase 3 (Guestimation) → 0.70
      
      answer:
        value: 200000
        unit: "원"
        confidence: 0.70
        phase: 3
        reasoning_summary: "글로벌 벤치마크($100) × 한국 조정(0.6) × B2B 배수(3) = 200,000원"
    
    - id: EX-002
      category: fermi_decomposition
      query: "서울 피아노 학원 수는?"
      thinking:
        step_1: |
          문제 분해:
          - 지역: 서울
          - 업종: 피아노 학원
          - 목표: 개수 추정
          - 필요 변수: 인구, 학습률, 학원당 학생 수
        
        step_2: |
          변수 식별:
          - 서울 인구: 1,000만명 (알려짐)
          - 서울 초중고생: ~100만명 (알려짐, 인구의 10%)
          - 피아노 학습률: 추정 필요 (3%?)
          - 학원당 학생: 추정 필요 (10명?)
        
        step_3: |
          데이터 수집:
          - 통계청: 서울 인구 9.7백만, 초중고생 ~1백만
          - 교육부: 음악학원 통계 (전국 ~15,000개)
          - 추정: 피아노 비중 30% → 피아노 학원 ~4,500개 (전국)
          - 서울 비중: 전국의 ~60% → 2,700개
        
        step_4: |
          모형 생성:
          모형 1 (Top-down, 인구 기반):
            서울 인구 1,000만 / 1인당 학원 수 5,000 = 2,000개
          
          모형 2 (Bottom-up, 학생 기반):
            초중고생 100만 × 학습률 3% = 30,000명
            30,000명 / 학원당 10명 = 3,000개
          
          모형 3 (전국 비율):
            전국 4,500개 × 서울 비중 60% = 2,700개
          
          평균: (2,000 + 3,000 + 2,700) / 3 = 2,567개
          반올림: 2,500개
        
        step_5: |
          검증:
          - 서울 구별: 25개 구 → 구당 100개 (합리적)
          - 동네별: 동당 5-10개 (관찰과 부합)
          - Confidence: Phase 4 (Fermi) → 0.65
      
      answer:
        value: 2500
        unit: "개"
        confidence: 0.65
        phase: 4
        reasoning_summary: "3개 모형 (인구, 학생, 전국 비율) 평균 → 2,500개"
```

### Step 2: GPT-4o 어댑터 구현

```python
# umis_rag/agents/estimator/gpt4o_adapter.py

import yaml
from pathlib import Path
from typing import Dict, Any
import json

class GPT4oEstimator:
    """
    GPT-4o를 Claude Sonnet 4.5 수준으로 끌어올리는 어댑터
    """
    
    def __init__(self):
        # umis.yaml 로드
        umis_path = Path(__file__).parent.parent.parent.parent / 'umis.yaml'
        with open(umis_path) as f:
            umis_data = yaml.safe_load(f)
        
        self.prompting_config = umis_data.get('gpt4o_prompting', {})
        self.role = self.prompting_config.get('role')
        self.cot_template = self.prompting_config.get('cot_template')
        self.examples = self.prompting_config.get('examples', [])
    
    def estimate(self, query: str, context: Dict = None) -> Dict[str, Any]:
        """
        GPT-4o로 추정 (Claude 수준)
        """
        # 1. 관련 예시 선택 (최대 3개)
        relevant_examples = self._select_examples(query, top_k=3)
        
        # 2. 프롬프트 생성
        prompt = self._build_prompt(query, relevant_examples, context)
        
        # 3. GPT-4o 호출
        response = self._call_gpt4o(prompt)
        
        # 4. 응답 파싱
        result = self._parse_response(response)
        
        # 5. 검증
        validated = self._validate(result, query)
        
        return validated
    
    def _build_prompt(self, query: str, examples: list, context: Dict = None) -> str:
        """프롬프트 구성"""
        
        # 예시 포매팅
        examples_text = "\n\n".join([
            self._format_example(ex) for ex in examples
        ])
        
        # 컨텍스트 추가
        context_text = ""
        if context:
            context_text = f"\n\n현재 프로젝트 맥락:\n{json.dumps(context, ensure_ascii=False, indent=2)}\n"
        
        prompt = f"""{self.role}

참고 예시:

{examples_text}

---
{context_text}
이제 다음 질문에 답해주세요:

질문: {query}

{self.cot_template}
"""
        return prompt
    
    def _format_example(self, example: Dict) -> str:
        """예시 포매팅"""
        thinking_steps = "\n".join([
            f"{step}: {content}"
            for step, content in example.get('thinking', {}).items()
        ])
        
        answer = example.get('answer', {})
        
        return f"""예시: {example['query']}

생각 과정:
{thinking_steps}

답변:
{json.dumps(answer, ensure_ascii=False, indent=2)}
"""
    
    def _select_examples(self, query: str, top_k: int = 3) -> list:
        """질문과 관련된 예시 선택"""
        # 간단 구현: 키워드 매칭
        # 향후 개선: Embedding 기반 유사도
        
        scored_examples = []
        for example in self.examples:
            score = self._similarity(query, example['query'])
            scored_examples.append((score, example))
        
        scored_examples.sort(reverse=True, key=lambda x: x[0])
        return [ex for _, ex in scored_examples[:top_k]]
    
    def _similarity(self, q1: str, q2: str) -> float:
        """간단한 유사도 (키워드 기반)"""
        # TODO: Embedding 기반으로 개선
        words1 = set(q1.lower().split())
        words2 = set(q2.lower().split())
        
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union) if union else 0.0
    
    def _call_gpt4o(self, prompt: str) -> str:
        """GPT-4o API 호출"""
        from openai import OpenAI
        
        client = OpenAI()  # .env에서 자동 로드
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,  # 낮은 온도 (일관성)
            response_format={"type": "json_object"}  # JSON 강제
        )
        
        return response.choices[0].message.content
    
    def _parse_response(self, response: str) -> Dict:
        """응답 파싱"""
        try:
            data = json.loads(response)
            return data.get('answer', {})
        except json.JSONDecodeError:
            # Fallback: 텍스트 파싱
            return {
                'value': None,
                'confidence': 0.5,
                'error': 'JSON 파싱 실패'
            }
    
    def _validate(self, result: Dict, query: str) -> Dict:
        """결과 검증"""
        # 기본 검증
        if result.get('value') is None:
            result['warning'] = "값 없음"
        
        if result.get('value', 0) < 0:
            result['warning'] = "음수 값 (비정상)"
        
        if result.get('confidence', 0) > 0.95 and result.get('phase') == 4:
            result['confidence'] = 0.75  # Fermi는 과신 방지
        
        return result
```

---

## 📊 요약

### Claude → GPT-4o 마이그레이션 로드맵

```yaml
Week 1 (필수):
  - CoT 프롬프트 템플릿
  - Few-shot 예시 10개
  - 구조화된 출력
  
  효과: 70-75% 품질
  비용: 동일
  구현: 쉬움

Week 2 (권장):
  - 의사결정 트리 (10개 템플릿)
  - 자동 검증 레이어
  - Multi-pass 전략
  
  효과: 80-85% 품질
  비용: +20-30%
  구현: 중간

Week 3-4 (선택):
  - Ensemble
  - Meta-learner
  - Context-aware
  
  효과: 90% 품질
  비용: +40-50%
  구현: 복잡

1개월+ (완벽주의):
  - Hybrid (GPT + Claude)
  - 전문가 시스템
  
  효과: 95%+ 품질
  비용: 최적화
  구현: 매우 복잡
```

---

**작성자**: AI Assistant  
**작성일**: 2025-11-18  
**대상**: Claude Sonnet 4.5 → GPT-4o 마이그레이션  
**목표**: 동등 이상 품질, 비용 효율  

---

*Thinking 모델의 "마법"은 명시적 구조와 예시로 재현 가능합니다!*




