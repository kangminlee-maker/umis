# Agent 아키텍처 핵심 의사결정

**질문:** 범용 Agent (Explorer 확장) vs 도메인별 전문 Agent?

---

## 🎯 당신의 3가지 고민 분석

### 1. 사용자 커스터마이징

```yaml
문제:
  "사용자가 자기 이름을 쓰고 싶을 수 있다"
  
  예시:
    • Observer → "Jane" (자기 이름)
    • Explorer → "Alex" (팀원 이름)
    • Quantifier → "DataBot"

해결책:
  agent_names.yaml (설정 파일)
  
  agents:
    observer:
      id: observer
      default_name: "Observer"
      display_name: "Jane"  # 사용자 설정!
      role: "Market Structure Analyst"
    
    explorer:
      id: explorer
      default_name: "Explorer"  
      display_name: "Alex"  # 사용자 설정!
      role: "Opportunity Finder"

  사용:
    Cursor: "@Jane, 시장 구조 분석해"
    내부: observer.search_structure()
    
    → 표시는 Jane, 내부는 observer! ✅
```

**판단:** ✅ 해결 가능! 설정 파일로 분리

---

### 2. 자기 설명적 이름

```yaml
문제:
  "Explorer가 뭘 하는지 문서 봐야 알 수 있다"
  
  비교:
    Observer → "뭘 관찰?"
    OpportunityExplorer → "아, 기회 탐색!"
    
    Explorer → 모호
    MarketExplorer → 명확!

해결책 비교:
  
  A. 짧고 모호:
     Explorer
     → 간결하지만 역할 불명확
  
  B. 길고 명확:
     OpportunityExplorer
     → 명확하지만 길고 장황
  
  C. Hybrid:
     Explorer (코드)
     + "Opportunity Explorer" (UI 표시)
     + agent_names.yaml에 역할 명시
```

**판단:** ✅ Hybrid 접근! 코드는 짧게, 표시는 명확하게

---

### 3. 확장성 (핵심!)

```yaml
당신의 질문:
  "Explorer를 확장? vs 새 Agent 추가?"
  
  Market Intelligence → Business Problem Solver
  
  두 가지 접근:
```

#### Approach A: Explorer 확장 (범용화)

```python
class Explorer:
    """범용 문제 해결 Agent"""
    
    def __init__(self, mode='market_intelligence'):
        self.mode = mode
        self.load_workflow(mode)
    
    def analyze(self, problem):
        if self.mode == 'market_intelligence':
            return self._analyze_market_opportunity(problem)
        
        elif self.mode == 'business_strategy':
            return self._analyze_strategy_option(problem)
        
        elif self.mode == 'product_optimization':
            return self._analyze_product_improvement(problem)

# 사용
market_explorer = Explorer(mode='market_intelligence')
strategy_explorer = Explorer(mode='business_strategy')
```

**장점:**
```yaml
✅ 재사용: 같은 Agent 다용도
✅ 통합: 하나의 클래스
✅ 간결: Agent 수 적음
```

**단점:**
```yaml
❌ 복잡도: 모든 모드 한 클래스에
❌ RAG 혼재: 시장 + 전략 + 제품 RAG 섞임
❌ Workflow 복잡: if-else 분기 많음
❌ 전문성 희석: 모든 것을 하려다 아무것도 못함
❌ 유지보수: 한 곳 수정이 모든 모드에 영향

실전 문제:
  • Market Intelligence RAG: 54개 패턴/사례
  • Business Strategy RAG: 다른 100개 전략 프레임워크
  • Product Optimization RAG: 또 다른 80개 최적화 패턴
  
  → 하나로 합치면? 234개 섞임!
  → 검색 품질 ↓, 혼란 ↑
```

---

#### Approach B: 도메인별 전문 Agent (추천!) ⭐⭐⭐⭐⭐

```python
# 각 도메인별 전문 Agent

class MarketExplorer:
    """Market Intelligence 전문"""
    
    def __init__(self):
        self.rag = load_rag('market_intelligence')
        self.patterns = load_patterns('business_models')
        self.workflow = MarketAnalysisWorkflow()
    
    def analyze_opportunity(self, market):
        # 시장 기회 전문
        ...

class StrategyExplorer:
    """Business Strategy 전문"""
    
    def __init__(self):
        self.rag = load_rag('business_strategy')
        self.frameworks = load_frameworks('strategy')
        self.workflow = StrategyAnalysisWorkflow()
    
    def analyze_strategy(self, situation):
        # 전략 분석 전문
        ...

class ProductExplorer:
    """Product Optimization 전문"""
    
    def __init__(self):
        self.rag = load_rag('product_optimization')
        self.criteria = load_criteria('product_quality')
        self.workflow = ProductAnalysisWorkflow()
    
    def analyze_improvement(self, product):
        # 제품 개선 전문
        ...

# 공통 기능은 Base 클래스로
class BaseExplorer:
    """공통 탐색 로직"""
    
    def search_patterns(self, ...):
        # 공통 메서드
    
    def search_cases(self, ...):
        # 공통 메서드
```

**장점:**
```yaml
✅ 전문성: 각 도메인에 최적화
✅ RAG 분리: 도메인별 독립 RAG
✅ Workflow 명확: 각자 프로세스
✅ 확장 용이: 새 도메인 = 새 Agent
✅ 유지보수: 독립적 수정
✅ 품질: 전문화로 높은 품질
✅ 재사용: BaseExplorer로 공통 로직 공유
```

**구조:**
```
umis_rag/
├── agents/
│   ├── base/
│   │   └── base_explorer.py (공통)
│   │
│   ├── market_intelligence/
│   │   ├── market_observer.py
│   │   ├── market_explorer.py
│   │   ├── market_quantifier.py
│   │   └── market_validator.py
│   │
│   ├── business_strategy/ (향후)
│   │   ├── strategy_observer.py
│   │   ├── strategy_explorer.py
│   │   └── ...
│   │
│   └── product_optimization/ (향후)
│       └── ...
│
└── rags/
    ├── market_intelligence_rag/
    │   ├── patterns/ (54개 시장 패턴)
    │   └── cases/ (시장 사례)
    │
    ├── business_strategy_rag/ (향후)
    │   ├── frameworks/ (전략 프레임워크)
    │   └── playbooks/
    │
    └── product_optimization_rag/ (향후)
```

---

## 💡 제 강력한 추천

### 🎯 Approach B (도메인별 전문 Agent)

**이유:**

```yaml
1. 전문성이 핵심:
   • Market Intelligence: 고유한 패턴 (플랫폼, 구독, ...)
   • Business Strategy: 고유한 프레임워크 (BCG, Porter, ...)
   • Product: 고유한 기준 (UX, 성능, ...)
   
   → 하나로 합치면 전문성 희석!

2. RAG 품질:
   • 시장 RAG: 코웨이, Netflix (사례)
   • 전략 RAG: McKinsey 플레이북 (프레임워크)
   • 제품 RAG: 디자인 패턴 (방법론)
   
   → 섞으면 검색 품질 ↓

3. Workflow 차이:
   • 시장: Observer → Explorer → Quantifier
   • 전략: Analyzer → Explorer → Evaluator
   • 제품: Researcher → Explorer → Tester
   
   → 프로세스가 다름!

4. 확장성:
   • 새 도메인 = 새 폴더
   • 기존 Agent 영향 없음
   • 독립적 개발
   
   → 확장 쉬움!

5. 공통 로직 재사용:
   • BaseExplorer: 공통 메서드
   • BaseRAG: 공통 검색
   • BaseWorkflow: 공통 프로세스
   
   → 중복 최소화!
```

---

## 🏗️ 제안하는 최종 아키텍처

### 구조

```
UMIS Framework (범용)
├── Core Components (공통)
│   ├── BaseAgent
│   ├── BaseRAG
│   └── BaseWorkflow
│
└── Domain Packages (도메인별)
    ├── market_intelligence/ ⭐ 현재
    │   ├── agents/
    │   │   ├── market_observer.py
    │   │   ├── opportunity_explorer.py
    │   │   ├── market_quantifier.py
    │   │   ├── data_validator.py
    │   │   └── quality_guardian.py
    │   │
    │   ├── rags/
    │   │   ├── business_model_patterns/
    │   │   └── disruption_patterns/
    │   │
    │   └── workflows/
    │       └── market_analysis_workflow.py
    │
    ├── business_strategy/ (향후)
    │   ├── agents/
    │   │   ├── situation_observer.py
    │   │   ├── strategy_explorer.py
    │   │   └── ...
    │   ├── rags/
    │   │   ├── strategy_frameworks/
    │   │   └── competitive_playbooks/
    │   └── workflows/
    │
    └── product_optimization/ (향후)
        └── ...
```

### 사용자 설정

```yaml
# user_config.yaml

active_domain: "market_intelligence"

domains:
  market_intelligence:
    enabled: true
    
    agent_names:
      observer:
        display_name: "Jane"  # 사용자 설정!
        role_description: "시장 구조 분석가"
      
      explorer:
        display_name: "Alex"
        role_description: "기회 발굴 전문가"
    
    rag_config:
      collection: "market_intel_v1"
      patterns: 54
  
  business_strategy:
    enabled: false  # 향후 활성화
```

### 실제 사용

```python
# Cursor에서

# Domain 선택 (한 번만)
from umis.domains import MarketIntelligence

umis = MarketIntelligence()

# 사용자 이름으로 표시
umis.set_agent_names({
    'observer': 'Jane',
    'explorer': 'Alex'
})

# 분석
umis.analyze("피아노 구독 서비스")

# 출력:
# Jane (Observer): "높은 초기 비용 관찰..."
# Alex (Explorer): "subscription_model 패턴 발견..."

→ 명확하고 개인화됨! ✨
```

---

## 🎯 최종 추천 아키텍처

### Level 1: Framework (범용)

```python
umis_framework/
├── core/
│   ├── base_agent.py       # 모든 Agent 기본
│   ├── base_rag.py         # 모든 RAG 기본
│   └── base_workflow.py    # 모든 Workflow 기본
│
└── config/
    └── user_config.yaml    # 사용자 설정
```

### Level 2: Domain Packages (전문화)

```python
umis_domains/
├── market_intelligence/    ⭐ 현재 UMIS
│   ├── agents/
│   │   ├── market_observer.py
│   │   ├── opportunity_explorer.py
│   │   └── ...
│   │
│   ├── rags/
│   │   ├── business_patterns_rag.py
│   │   └── case_studies_rag.py
│   │
│   └── workflow/
│       └── discovery_sprint.py
│
├── business_strategy/      (향후)
│   ├── agents/
│   │   ├── situation_observer.py
│   │   ├── strategy_explorer.py
│   │   └── ...
│   │
│   ├── rags/
│   │   ├── strategy_frameworks_rag.py
│   │   └── competitive_playbooks_rag.py
│   │
│   └── workflow/
│       └── strategy_analysis.py
│
└── product_optimization/   (향후)
```

**왜 이게 최선인가:**

```yaml
전문성:
  ✅ 각 도메인 고유 Agent
  ✅ 각 도메인 고유 RAG
  ✅ 각 도메인 고유 Workflow
  
  → 품질 최고!

확장성:
  ✅ 새 도메인 = 새 폴더
  ✅ 기존 영향 없음
  ✅ 독립 개발
  
  → 확장 쉬움!

명확성:
  ✅ market_intelligence.OpportunityExplorer
  → 뭘 하는지 명확!
  
  ✅ business_strategy.StrategyExplorer
  → 다른 Explorer임을 알 수 있음!

재사용:
  ✅ BaseExplorer 상속
  ✅ 공통 로직 공유
  ✅ 중복 최소화
```

---

## 🔬 구체적 예시

### 시나리오: UMIS 확장

```python
# 1. Market Intelligence (현재)

from umis.domains.market_intelligence import MarketIntelligence

mi = MarketIntelligence()
mi.analyze("피아노 구독 서비스")

# Observer: 시장 구조
# Explorer: 기회 발견 (플랫폼, 구독 패턴)
# Quantifier: TAM/SAM
```

```python
# 2. Business Strategy (향후)

from umis.domains.business_strategy import BusinessStrategy

bs = BusinessStrategy()
bs.analyze("디지털 전환 전략")

# Observer: 현재 상황 분석
# Explorer: 전략 옵션 탐색 (BCG Matrix, Porter's 5 Forces)
# Evaluator: 전략 평가
```

```python
# 3. Product Optimization (향후)

from umis.domains.product_optimization import ProductOptimization

po = ProductOptimization()
po.analyze("모바일 앱 UX 개선")

# Observer: 사용자 행동 관찰
# Explorer: 개선 옵션 탐색 (디자인 패턴, Best Practices)
# Tester: A/B 테스트 설계
```

**각각 독립:**
```yaml
RAG:
  • market_intelligence: 54개 시장 패턴
  • business_strategy: 100개 전략 프레임워크
  • product_optimization: 80개 UX 패턴
  
  → 섞이지 않음!
  → 검색 품질 최고!

Workflow:
  • 시장: Discovery → Analysis → Decision
  • 전략: Situation → Options → Evaluation
  • 제품: Research → Design → Test
  
  → 각자 최적화!

Agent:
  • 시장: Observer/Explorer/Quantifier/Validator/Guardian
  • 전략: Analyzer/Explorer/Evaluator/Validator/Advisor
  • 제품: Researcher/Explorer/Designer/Tester/Reviewer
  
  → 역할 맞춤!
```

---

## 🎯 제 강력한 추천

### 도메인별 전문 Agent (Approach B)

**현재 구조:**
```python
umis_rag/
└── agents/
    └── steve.py  # 현재
```

**목표 구조:**
```python
umis_rag/
├── core/
│   ├── base_agent.py
│   └── base_rag.py
│
└── domains/
    └── market_intelligence/
        ├── agents/
        │   └── opportunity_explorer.py  # 이름도 명확!
        │
        └── rags/
            └── market_patterns_rag.py
```

**이름 제안:**
```yaml
market_intelligence 도메인:
  MarketObserver (시장 관찰자)
  OpportunityExplorer (기회 탐색자)
  MarketQuantifier (시장 정량화)
  DataValidator (데이터 검증자)
  QualityGuardian (품질 수호자)

향후 business_strategy 도메인:
  SituationObserver
  StrategyExplorer
  OptionEvaluator
  ...

→ 도메인 + 역할로 명확! ✨
```

---

## 💡 사용자 커스터마이징 통합

```yaml
# user_config.yaml

domains:
  market_intelligence:
    agents:
      market_observer:
        display_name: "Jane"  # 개인화!
        personality: "analytical"
      
      opportunity_explorer:
        display_name: "Alex"
        personality: "creative"

# Cursor 사용:
"@Jane, 시장 구조 분석해"
"@Alex, 기회를 찾아봐"

# 내부:
market_observer.analyze()
opportunity_explorer.search()

→ 표시는 Jane/Alex, 코드는 명확한 ID! ✅
```

---

## 📋 구현 계획

### Phase 1: 현재 (Market Intelligence)

```yaml
구조:
  umis_rag/domains/market_intelligence/
  
Agent 이름:
  MarketObserver
  OpportunityExplorer
  MarketQuantifier
  DataValidator
  QualityGuardian

파일명:
  market_observer.py
  opportunity_explorer.py
  market_quantifier.py
  data_validator.py
  quality_guardian.py

→ 명확하고 확장 가능! ✅
```

### Phase 2: 확장 (향후)

```yaml
새 도메인 추가 시:
  1. umis_rag/domains/business_strategy/ 생성
  2. 전용 Agent 개발
  3. 전용 RAG 구축
  4. 독립 Workflow
  
  → 기존 영향 없음!
  → 안전한 확장!
```

---

## 🎯 최종 답변

### 당신의 질문: "Explorer 확장 vs 새 Agent?"

**답: 새 Agent (도메인별 전문화)!**

```yaml
이유:
  1. 전문성 = 품질
     각 도메인은 고유 지식/프로세스
     
  2. RAG 분리 = 검색 품질
     섞으면 노이즈
     
  3. 확장성 = 안전
     새 도메인 추가가 기존에 영향 없음
     
  4. 유지보수 = 쉬움
     독립적 수정

결론:
  → Explorer는 Market Intelligence 전용
  → 새 도메인은 새 *Explorer
  → Base 클래스로 재사용
```

### ID 이름 최종 제안

```yaml
현재: Observer, Explorer, ...
목표: MarketObserver, OpportunityExplorer, ...

이유:
  ✅ 도메인 + 역할 = 자기 설명적
  ✅ 확장 시 명확 (StrategyExplorer vs OpportunityExplorer)
  ✅ 사용자 설정으로 표시명 커스터마이징
```

---

## 🚀 즉시 실행 제안

**지금 할 것:**

```yaml
1. 현재 유지:
   Observer, Explorer, ... (간결)
   
2. 향후 확장 시:
   도메인 폴더 구조로 전환
   MarketObserver, OpportunityExplorer, ...
   
3. 지금은:
   프로토타입 완성에 집중
   
4. 나중에:
   확장 필요 시 리팩토링
```

**또는 지금 바로 리팩토링:**

```yaml
구조:
  umis_rag/domains/market_intelligence/
  
이름:
  MarketObserver
  OpportunityExplorer
  MarketQuantifier
  DataValidator
  QualityGuardian
  
실행:
  ./BACKUP_AND_RENAME.sh
  → Option B 선택
```

---

## 🎯 제 최종 추천

**지금: 현재 유지 (Observer, Explorer)**  
**이유:** 프로토타입 단계, UMIS v6.2 표준

**향후: 도메인 구조로 리팩토링**  
**시기:** 새 도메인 추가 필요 시

**어떻게 하시겠어요?** 🚀

1. 현재 유지 (간단)
2. 지금 리팩토링 (완벽)
3. 다른 제안?
