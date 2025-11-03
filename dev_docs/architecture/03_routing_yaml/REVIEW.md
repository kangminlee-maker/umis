# Routing/Policy YAML 외부화 검토

**제안:** RAG 호출 시점, Layer 순서를 YAML 정책으로

---

## 🔍 현재 방식 (하드코딩)

### Python 코드에 로직

```python
# umis_rag/agents/explorer.py

def analyze_opportunity(self, triggers):
    # 하드코딩된 순서!
    
    # 1. 패턴 검색 (항상)
    patterns = self.search_patterns(triggers)
    
    # 2. 사례 검색 (항상)
    best_pattern = patterns[0]
    cases = self.search_cases(best_pattern.id)
    
    # 3. Quantifier 협업 (항상)
    bill_data = self.ask_quantifier(cases[0].source_id)
    
    # 4. 가설 생성
    return generate_hypothesis(patterns, cases, bill_data)
```

**문제:**
```yaml
경직성:
  • 순서 고정 (패턴 → 사례 → Quantifier)
  • 호출 시점 고정 (항상)
  • 조건 분기 코드에
  
  변경하려면:
    Python 코드 수정 필요
    → 사용자가 못 함! ❌

예시:
  "Quantifier는 필요 시만 호출하고 싶어"
  → 코드 수정 필요
  → Cursor에게 요청? 복잡!
```

---

## 💡 제안 방식 (YAML Policy)

### config/routing_policy.yaml

```yaml
# UMIS RAG Routing Policy

explorer_workflow:
  name: "기회 발굴 워크플로우"
  
  steps:
    - id: pattern_search
      layer: layer1_vector
      method: search_patterns
      when: always
      input: triggers
      output: patterns
    
    - id: case_search
      layer: layer1_vector
      method: search_cases
      when: patterns.count > 0
      input:
        pattern_id: patterns[0].id
        industry: context.industry
      output: cases
    
    - id: quantifier_collaboration
      layer: layer1_modular
      agent: quantifier
      method: search_metrics
      when: cases.count > 0 AND context.needs_quantitative  # ← 조건!
      input:
        source_id: cases[0].source_id
      output: quantifier_data
    
    - id: graph_expansion
      layer: layer3_graph
      method: find_combinations
      when: enable_graph AND patterns.count > 0  # ← 토글!
      input: patterns[0].id
      output: combinations
    
    - id: hypothesis_generation
      method: generate
      input:
        patterns: patterns
        cases: cases
        quantifier: quantifier_data
        combinations: combinations

layer_toggle:
  layer1_vector: true
  layer2_meta: false  # 미구현
  layer3_graph: false  # 미구현
  layer4_memory: false  # 미구현

conditions:
  needs_quantitative:
    - explorer.confidence < 0.7
    - cases[0].has_metrics == false
  
  enable_graph:
    - layer3_graph == true
    - patterns.count >= 2
```

### 사용

```python
# umis_rag/workflow/executor.py

class WorkflowExecutor:
    def __init__(self):
        self.policy = load_yaml('config/routing_policy.yaml')
    
    def execute(self, workflow_name, context):
        workflow = self.policy[workflow_name]
        
        results = {}
        
        for step in workflow['steps']:
            # when 조건 평가
            if not self._evaluate_condition(step['when'], results, context):
                continue  # Skip!
            
            # 메서드 실행
            result = self._execute_step(step, results, context)
            
            results[step['output']] = result
        
        return results
```

**장점:**
```yaml
✅ 유연성:
   • YAML만 수정
   • 순서 변경 쉬움
   • 조건 추가 쉬움

✅ 가시성:
   • 워크플로우가 YAML에
   • 한 눈에 파악
   • 문서화 자동

✅ 사용자 제어:
   • Cursor에서 YAML 수정
   • 즉시 반영
   • 실험 용이

예시:
  사용자: "Quantifier는 필요할 때만 호출하게 해줘"
  
  AI: config/routing_policy.yaml 수정
    when: always → when: needs_quantitative
  
  → 즉시 반영! ✨
```

**단점:**
```yaml
❌ 복잡도:
   • YAML 파싱
   • 조건 평가 엔진
   • 동적 실행

❌ 디버깅:
   • 워크플로우 추적 어려움
   • YAML 오류 시?
   • 성능 측정 복잡

❌ 제약:
   • 복잡한 로직은 YAML로 어려움
   • Python이 더 표현력 좋음
```

---

## 🔍 실용성 분석

### UMIS 실제 사용

```yaml
현재:
  Explorer 워크플로우:
    1. 패턴 검색
    2. 사례 검색
    3. Quantifier 협업
    4. 가설 생성
  
  변경 빈도:
    • 거의 없음 (표준 프로세스)
    • 99% 케이스 동일

예외:
  "Quantifier 건너뛰고 싶어"
  
  빈도: 월 1회?
  
  해결:
    Option A: config/routing_policy.yaml 수정
    Option B: Cursor: "Quantifier 생략하고 분석해줘"
    
    → Option B가 더 간단! 🤔
```

### 복잡도 vs 가치

```yaml
YAML Routing 추가:
  복잡도:
    • config/routing_policy.yaml 작성
    • WorkflowExecutor 구현
    • 조건 평가 엔진
    • 테스트 케이스
    
    예상: 1주 개발

  가치:
    • 순서 변경: 월 0-1회
    • 조건 변경: 월 0-1회
    • 토글: 개발 시만
    
    실제 사용: 거의 없음?

  판단:
    복잡도 > 가치
    → 오버엔지니어링? 🤔
```

---

## 💡 대안: .cursorrules로 충분?

### 현재 방식

```yaml
# .cursorrules

When Explorer needs pattern matching:
  - Automatically run RAG search
  
When Explorer needs cases:
  - Automatically run case search
  
When Explorer needs Quantifier:
  - Call quantifier.search()
```

**사용자:**
```
Cursor: "@Steve, 분석해줘 (Quantifier 생략)"

AI:
  [.cursorrules 해석]
  → Quantifier 단계 skip
  
  → 유연함! ✅
```

**vs YAML Routing:**
```yaml
.cursorrules (현재):
  • 자연어로 제어
  • "Quantifier 생략" 말로 지시
  • Cursor가 이해
  
  장점:
    ✅ 극도로 단순
    ✅ 사용자 친화
    ✅ 추가 개발 없음

YAML Routing (제안):
  • YAML로 제어
  • config/routing_policy.yaml 수정
  • 구조화됨
  
  장점:
    ✅ 명시적
    ✅ 재현 가능
  
  단점:
    ❌ 복잡
    ❌ 개발 필요
```

---

## 🎯 제 판단

### 현 단계에서는 불필요!

```yaml
이유:
  1. 빈도:
     • 워크플로우 변경: 거의 없음
     • 표준 프로세스 고정
  
  2. 대안:
     • .cursorrules로 충분
     • "생략해줘" 말로 지시
     • Cursor가 이해
  
  3. 복잡도:
     • YAML Routing: 1주 개발
     • 가치: 월 0-1회 사용
     
     복잡도 >> 가치
     → 오버엔지니어링

결론:
  지금은 .cursorrules로 충분!
  
  향후 고려:
    • 워크플로우 수십 개
    • 변경 빈번
    • 표준화 필요
    
    → 그때 YAML Routing!
```

---

## 🎯 3번 최종 결정

**제외 (Not Now)**

```yaml
채택:
  ❌ YAML Routing (현재 불필요)

대안:
  ✅ .cursorrules (충분)

이유:
  • 단순 > 완벽
  • 실용 > 구조
  • 빈도 낮음

보류:
  향후 워크플로우 복잡해지면
  재검토
```

**당신의 의견은?**

필요하다고 생각하시면 구현하고,  
불필요하다면 **4번 (Graph Provenance)** 검토할까요? 🚀

