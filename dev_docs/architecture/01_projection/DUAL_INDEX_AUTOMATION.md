# Dual-Index 자동화 전략

**문제:** Canonical → Projected 자동 생성의 복잡도

---

## 🔍 복잡도 분석

### Projected Index 생성 시 결정 사항

```yaml
1. 정보 분배:
   어떤 정보를 어떤 Agent에?
   
   예: "해지율 3-5%"
     → Explorer? (기회 평가에 필요)
     → Quantifier? (당연!)
     → Guardian? (검증에 필요)
     → Observer? (불필요)
     → Validator? (불필요)

2. 청킹 크기:
   각 Agent별로 얼마나?
   
   예: 배달의민족
     → Observer: 600 토큰
     → Explorer: 800 토큰
     → Quantifier: 300 토큰

3. 섹션 우선순위:
   정보가 충돌하면?
   
   예: "플랫폼 전략"
     → Observer도 필요 (구조 분석)
     → Explorer도 필요 (기회 전략)
     → 둘 다 넣으면 중복!

4. 메타데이터:
   어떤 메타를 복사?
   
   예: CSF (핵심 성공 요인)
     → Explorer에만? 
     → Guardian에도?
```

**결정 사항: 최소 4가지 × 6 Agents = 24개 결정!**  
**사례마다 다를 수 있음 = 복잡도 폭발! 🚨**

---

## 💡 해결 방법

### Option 1: Rule-Based (YAML 정의)

```yaml
# config/projection_rules.yaml

agent_projection_rules:
  observer:
    sections:
      - market_structure
      - competitive_landscape
      - value_chain
    
    exclude:
      - detailed_metrics
      - source_citations
      - validation_status
    
    max_tokens: 600
    priority: ["structure", "dynamics"]
  
  explorer:
    sections:
      - opportunity_structure
      - execution_strategy
      - critical_success_factors
    
    include_from_others:
      - observer.triggers  # Observer에서 트리거만
      - quantifier.key_metrics  # Quantifier에서 핵심 지표만
    
    max_tokens: 800
    priority: ["opportunity", "strategy"]
  
  quantifier:
    sections:
      - quantitative_data
      - calculations
      - benchmarks
    
    format: "numbers_only"
    max_tokens: 500
```

**장점:**
```yaml
✅ 명확: 규칙이 YAML에
✅ 제어: 사용자가 수정 가능
✅ 일관성: 규칙 기반
✅ 디버깅: 쉬움

예시:
  사용자: "Explorer에 해지율도 추가"
  
  → config/projection_rules.yaml 수정:
    explorer:
      include_from_others:
        + quantifier.churn_rate
  
  → 재생성
  → 즉시 반영!
```

**단점:**
```yaml
❌ 초기 설정: 규칙 작성 복잡
❌ 유지보수: 새 필드마다 규칙 추가
❌ 경직성: 규칙으로만
```

---

### Option 2: LLM-Based (AI 자동 분류)

```python
def auto_project(canonical_chunk):
    """
    LLM이 자동으로 Agent별 투영 결정
    """
    
    prompt = f"""
    다음 사례를 6개 Agent 관점으로 분류하세요:
    
    사례: {canonical_chunk.content}
    
    각 Agent별로:
    1. 필요한 정보 추출
    2. 적절한 길이로 요약
    3. Agent 전용 메타데이터 생성
    
    Agent:
    - Observer: 시장 구조, 경쟁 구도
    - Explorer: 기회, 전략, CSF
    - Quantifier: 숫자, 계산, 메트릭
    - Validator: 출처, 신뢰도
    - Guardian: 검증 상태, 품질
    - Owner: 의사결정 인사이트
    
    JSON 형식으로 반환.
    """
    
    result = llm.invoke(prompt)
    
    # 6개 Agent 청크 생성
    projected_chunks = parse_llm_result(result)
    
    return projected_chunks
```

**장점:**
```yaml
✅ 자동: 규칙 불필요
✅ 유연: 새 필드 자동 처리
✅ 지능적: 문맥 이해

예시:
  "해지율 3-5%" 추가
  
  LLM 판단:
    → Explorer: 필요 (기회 평가)
    → Quantifier: 필요 (계산)
    → Guardian: 필요 (검증)
    → Observer: 불필요
  
  → 자동 분배! ✨
```

**단점:**
```yaml
❌ 비용: LLM 호출 (5,000개 × $0.01 = $50)
❌ 느림: 5,000개 × 2초 = 2.7시간
❌ 불안정: LLM 실수 가능
❌ 제어 어려움: 블랙박스
```

---

### Option 3: Hybrid (YAML + LLM) ⭐ 추천!

```yaml
# config/projection_rules.yaml (기본 규칙)

default_rules:
  observer:
    keywords: ["시장", "구조", "경쟁", "트렌드"]
    sections: ["market_*", "competitive_*"]
    max_tokens: 600
  
  explorer:
    keywords: ["기회", "전략", "패턴", "CSF"]
    sections: ["opportunity_*", "strategy_*"]
    max_tokens: 800
    
    # LLM 판단 영역
    llm_decision_for:
      - "새로운 필드 (규칙 없음)"
      - "애매한 경우 (여러 Agent 가능)"

# 사용
auto_projection:
  step_1: 규칙 기반 (빠름, 90%)
    → keywords, sections 매칭
    
  step_2: LLM 판단 (느림, 10%)
    → 규칙 없는 새 필드
    → 애매한 케이스
```

**구현:**

```python
class HybridProjector:
    def __init__(self):
        self.rules = load_yaml('config/projection_rules.yaml')
        self.llm = ChatOpenAI()
    
    def project(self, canonical):
        projected = {}
        
        # Step 1: 규칙 기반 (90%)
        for agent, rule in self.rules.items():
            # 키워드 매칭
            matched = self._match_keywords(
                canonical.content,
                rule['keywords']
            )
            
            # 섹션 추출
            sections = self._extract_sections(
                canonical.content,
                rule['sections']
            )
            
            if matched or sections:
                # 규칙으로 처리 가능!
                projected[agent] = {
                    'content': sections,
                    'metadata': {...}
                }
        
        # Step 2: LLM 판단 (10%)
        uncovered = self._find_uncovered(canonical, projected)
        
        if uncovered:
            # 규칙 없는 새 정보
            llm_projection = self.llm.invoke(f"""
            다음 정보를 적절한 Agent에 분배:
            {uncovered}
            
            Agent: Observer, Explorer, ...
            """)
            
            projected.update(llm_projection)
        
        return projected
```

**장점:**
```yaml
✅ 빠름: 90%는 규칙 (< 1초)
✅ 정확: 규칙 기반 일관성
✅ 유연: 새 필드는 LLM
✅ 비용: LLM 10%만 ($5)
✅ 제어: 규칙 수정 가능

예시:
  기존 필드: 규칙으로 (빠름)
  "해지율" → quantifier (규칙)
  
  새 필드: LLM으로
  "브랜드 인지도" → LLM 판단
  → Explorer? Guardian?
  → LLM이 결정!
```

---

## 🎯 최종 추천

**Dual-Index + Hybrid Projection**

```yaml
구조:
  1. Canonical Index (업데이트)
  2. Projected Index (검색)

자동화:
  YAML 수정
  ↓
  Canonical 업데이트 (1곳)
  ↓
  Hybrid Projector
    • 90% 규칙 기반 (빠름)
    • 10% LLM 판단 (유연)
  ↓
  Projected 자동 재생성 (6곳)
  
  → 완전 자동! ✨

결과:
  ✅ 품질: Pre 수준
  ✅ 일관성: 1곳 수정
  ✅ 자동화: 규칙 + LLM
  ✅ 비용: $5 (LLM 10%만)
```

---

**결정하시겠어요?**

그리고 **2번 (Schema-Registry)** 검토할까요? 🚀
