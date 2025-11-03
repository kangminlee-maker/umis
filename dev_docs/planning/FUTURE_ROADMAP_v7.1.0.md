# UMIS v7.1.0 향후 로드맵
**작성일**: 2025-11-03  
**대상 버전**: v7.1.0 ~ v7.3.0  
**우선순위**: 3개 핵심 프로젝트

---

## 🎯 3대 핵심 프로젝트

### 1. Deliverable 자동 생성 시스템
**목표**: Spec → 실제 산출물 자동 생성

### 2. umis.yaml 모듈화 & AI 빠른 파악
**목표**: AI가 5분 내 UMIS 전체 구조 파악

### 3. RAG 데이터 추가 자동화
**목표**: 사용자가 쉽게 패턴/사례 추가

---

## 📋 프로젝트 1: Deliverable 자동 생성 시스템

### 🎯 목표

**현재 상태**:
```
deliverable_specs/
  ├── explorer/opportunity_hypothesis_spec.yaml (750줄, 스펙만)
  ├── observer/market_reality_report_spec.yaml (271줄)
  ├── quantifier/market_sizing_workbook_spec.yaml (301줄)
  └── ...

→ 정의만 있고, 실제 생성 코드 없음
```

**목표**:
```python
# AI가 이렇게 호출 가능
from umis_rag.deliverables import OpportunityHypothesis

opp = OpportunityHypothesis.from_analysis(
    hypothesis="피아노 구독 서비스",
    market_context=albert_report,
    validation_results={...}
)

opp.render()  # OPP_20251103_001_piano.md 자동 생성
```

---

### 🔍 현재 상태 분석

#### Spec 구조 (opportunity_hypothesis_spec.yaml 예시)

```yaml
frontmatter_schema:
  hypothesis:
    title: string
    target_customer: string
    problem: string
    solution: string
  
  scores:
    market_size: float (1-10)
    feasibility: float
    defensibility: float
    timing: float
    uniqueness: float
    total: float (자동 계산)
  
  validation:
    observer: {status, score, comment}
    quantifier: {status, score, comment}
    validator: {status, score, comment}
    overall: {status, passed_count}

markdown_sections:
  - section: "Hypothesis Statement"
    required_fields: [...]
  - section: "Market Context"
    ...
```

**장점**:
- ✅ 완전한 스키마 정의
- ✅ AI 파싱 용이 (100% YAML)
- ✅ 검증 규칙 명시

**단점**:
- ❌ 생성 코드 없음
- ❌ 렌더링 엔진 없음
- ❌ 검증 자동화 없음

---

### 💡 접근 방법

#### 방법 1: Template-based Generator (간단, 빠름)

```python
# umis_rag/deliverables/generator.py

class DeliverableGenerator:
    def __init__(self, spec_path: str):
        self.spec = load_yaml(spec_path)
    
    def generate_frontmatter(self, data: dict) -> str:
        """Spec에 따라 YAML frontmatter 생성"""
        # 1. 스키마 검증
        self.validate(data, self.spec['frontmatter_schema'])
        
        # 2. 자동 계산 (scores.total 등)
        data = self.auto_calculate(data)
        
        # 3. YAML 렌더링
        return yaml.dump(data)
    
    def generate_markdown(self, data: dict) -> str:
        """Spec에 따라 Markdown body 생성"""
        # 1. 템플릿 로드
        template = self.load_template()
        
        # 2. 데이터 채우기
        return template.render(**data)
    
    def generate(self, data: dict, output_path: str):
        """완전한 산출물 생성"""
        frontmatter = self.generate_frontmatter(data)
        body = self.generate_markdown(data)
        
        output = f"---\n{frontmatter}---\n\n{body}"
        
        with open(output_path, 'w') as f:
            f.write(output)
```

**사용**:
```python
gen = DeliverableGenerator('deliverable_specs/explorer/opportunity_hypothesis_spec.yaml')

gen.generate(
    data={
        'hypothesis': {...},
        'scores': {...},
        'validation': {...}
    },
    output_path='projects/20251103_piano/02_analysis/explorer/OPP_001.md'
)
```

**장점**:
- ✅ 구현 간단 (~300줄)
- ✅ Spec 기반 자동 생성
- ✅ 검증 자동화

**단점**:
- ⚠️ 템플릿 관리 필요
- ⚠️ 복잡한 로직은 어려움 (Excel 등)

---

#### 방법 2: Class-based Builder (유연, 확장 가능)

```python
# umis_rag/deliverables/opportunity.py

from pydantic import BaseModel
from typing import Optional

class OpportunityHypothesis(BaseModel):
    """Opportunity Hypothesis Deliverable"""
    
    # Spec에서 정의한 필드
    hypothesis: HypothesisStatement
    scores: ScoreMatrix
    validation: ValidationStatus
    
    @classmethod
    def from_analysis(
        cls,
        hypothesis: str,
        market_context: dict,
        validation_results: dict
    ):
        """분석 결과에서 생성"""
        # 1. 데이터 구조화
        # 2. 자동 계산
        # 3. 검증
        return cls(...)
    
    def calculate_total_score(self):
        """우선순위 자동 계산"""
        weights = {'market_size': 0.2, 'feasibility': 0.25, ...}
        return sum(self.scores[k] * w for k, w in weights.items())
    
    def validate_hypothesis(self):
        """가설 검증 상태 확인"""
        return all([
            self.validation.observer.status == 'passed',
            self.validation.quantifier.status == 'passed',
            self.validation.validator.status == 'passed'
        ])
    
    def render_frontmatter(self) -> str:
        """YAML frontmatter 생성"""
        return self.model_dump_yaml()
    
    def render_markdown(self) -> str:
        """Markdown body 생성"""
        template = Template(OPPORTUNITY_TEMPLATE)
        return template.render(
            hypothesis=self.hypothesis,
            scores=self.scores,
            ...
        )
    
    def save(self, output_dir: Path):
        """파일로 저장"""
        filename = f"OPP_{date}_{id}_{slug}.md"
        content = f"---\n{self.render_frontmatter()}---\n\n{self.render_markdown()}"
        
        (output_dir / filename).write_text(content)
```

**사용**:
```python
opp = OpportunityHypothesis.from_analysis(
    hypothesis="피아노 구독 서비스",
    market_context=albert_report,
    validation_results=validations
)

# 자동 계산
opp.calculate_total_score()

# 검증
if opp.validate_hypothesis():
    opp.save(output_dir)
```

**장점**:
- ✅ Pydantic 타입 안전성
- ✅ 자동 계산 로직 내장
- ✅ 검증 자동화
- ✅ 확장 용이

**단점**:
- ⚠️ 구현 복잡 (~500줄/Agent)
- ⚠️ Spec과 코드 동기화 필요

---

### 🎯 추천 접근법

**Phase 1: Template Generator** (v7.1.0)
- 간단한 생성기 구현
- Markdown 산출물부터 (explorer, observer)
- ~2주

**Phase 2: Class Builder** (v7.2.0)
- Pydantic 모델 전환
- 자동 계산/검증 로직
- ~3주

**Phase 3: Excel Generator** (v7.3.0)
- Bill의 market_sizing.xlsx 자동 생성
- openpyxl 활용
- ~2주

---

### ⚠️ 고려사항

#### 1. Spec ↔ Code 동기화

**문제**: Spec 변경 시 코드도 수정 필요

**해결**:
```python
# Spec에서 자동 코드 생성
python scripts/generate_deliverable_classes.py

# deliverable_specs/*.yaml → umis_rag/deliverables/*.py
```

#### 2. Excel 생성의 복잡성

**Bill의 9개 시트**:
- Assumptions, Estimation_Details, Method 1-4, Convergence, Scenarios, Validation
- 함수, 색상, 코멘트, 보호 설정

**해결**:
- openpyxl 활용
- 템플릿 Excel 파일 사용
- 점진적 구현 (중요한 시트부터)

#### 3. AI 호출 인터페이스

**AI가 쉽게 사용**:
```python
# Cursor Agent Mode에서
from umis_rag.deliverables import generate_opportunity

generate_opportunity(
    hypothesis="피아노 구독",
    data={...}
)
→ OPP_*.md 자동 생성
```

**Stewart 자동화**:
```python
# [DELIVERABLE_COMPLETE] 신호 발행
# deliverables_registry.yaml 자동 등록
```

---

## 📋 프로젝트 2: umis.yaml 모듈화 & AI 빠른 파악

### 🎯 목표

**현재 문제**:
```yaml
umis.yaml: 5,509줄

AI가 읽어야 할 것:
- SECTION 0: 시스템 개요
- SECTION 1-9: 전체 시스템 정의
- Agent 정의 (Observer, Explorer, ...)
- 프레임워크, 워크플로우...

문제:
  1. 너무 길어서 토큰 과다 소비
  2. 필요한 부분만 로드 불가
  3. 전체 파악에 시간 소요
  4. 단편적 이해 → 기능 누락
```

**목표**:
```
AI가 5분 내 파악:
  1. UMIS가 할 수 있는 것
  2. UMIS가 해야 하는 것
  3. UMIS 구조 (5-Agent, RAG, 워크플로우)
  
그 후:
  필요한 모듈만 로드 (Explorer, Quantifier 등)
```

---

### 🔍 모듈화 전략 분석

#### 방법 1: 계층적 모듈화 (Hierarchical)

```
umis/
├── umis_core.yaml                 # 핵심 개요 (500줄)
│   ├── system_overview
│   ├── 5-agent_summary
│   ├── rag_architecture_overview
│   ├── workflow_summary
│   └── quick_reference
│
└── modules/
    ├── agents/
    │   ├── observer.yaml          # Albert 상세 (800줄)
    │   ├── explorer.yaml          # Steve 상세 + RAG (900줄)
    │   ├── quantifier.yaml        # Bill 상세 (700줄)
    │   ├── validator.yaml         # Rachel 상세 (600줄)
    │   └── guardian.yaml          # Stewart 상세 (800줄)
    │
    ├── frameworks/
    │   ├── market_definition.yaml # 13 dimensions (1,000줄)
    │   ├── 7_powers.yaml          # 7 Powers 상세 (500줄)
    │   └── discovery_sprint.yaml  # Discovery 프로세스 (400줄)
    │
    └── workflows/
        ├── comprehensive_study.yaml  # 2-4주 워크플로우
        ├── rapid_assessment.yaml     # 1-3일 워크플로우
        └── quick_insights.yaml       # 1-2시간 워크플로우
```

**AI 사용**:
```
Step 1: umis_core.yaml 읽기 (5분)
  → 전체 구조 파악
  → 5-Agent 역할 이해
  → RAG 개념 파악

Step 2: 필요한 모듈만 로드
  "@Explorer 필요" → modules/agents/explorer.yaml
  "7 Powers 분석" → modules/frameworks/7_powers.yaml

Step 3: 분석 실행
  → 모든 기능 활용
  → 누락 없음
```

**장점**:
- ✅ AI 토큰 효율 (필요한 것만)
- ✅ 빠른 파악 (핵심만 먼저)
- ✅ 점진적 로드
- ✅ 유지보수 용이 (모듈별)

**단점**:
- ⚠️ 파일 개수 증가 (10+ 개)
- ⚠️ 참조 관리 필요
- ⚠️ 일관성 유지 필요

---

#### 방법 2: 레이어 기반 모듈화 (Layered)

```
umis/
├── layer_0_quickstart.yaml        # 빠른 시작 (200줄)
│   - 30초 사용법
│   - Agent 요약
│   - RAG 개요
│
├── layer_1_essentials.yaml        # 필수 (1,000줄)
│   - 5-Agent 정의
│   - 기본 워크플로우
│   - RAG 사용법
│
├── layer_2_frameworks.yaml        # 프레임워크 (2,000줄)
│   - 13 dimensions
│   - 7 Powers
│   - Discovery Sprint
│
└── layer_3_advanced.yaml          # 고급 (2,000줄)
    - Extended frameworks
    - Creative Boost
    - Token Management
```

**AI 로드 전략**:
```
Quick Mode:
  layer_0 + layer_1 (1,200줄)

Standard Mode:
  layer_0 + layer_1 + layer_2 (3,200줄)

Comprehensive Mode:
  모두 (5,200줄)
```

**장점**:
- ✅ 깊이 조절 가능
- ✅ 파일 개수 적음 (4개)
- ✅ 명확한 학습 경로

**단점**:
- ⚠️ 모듈 간 중복 가능
- ⚠️ 세밀한 선택 불가

---

#### 방법 3: Index + Modules (추천!)

```
umis/
├── umis.yaml                      # INDEX (800줄) ⭐
│   ├── system_overview
│   ├── agent_summary (간단히)
│   ├── rag_architecture
│   ├── quick_reference
│   └── module_index:
│       - observer: "modules/agents/observer.yaml"
│       - explorer: "modules/agents/explorer.yaml"
│       - market_definition: "modules/frameworks/market.yaml"
│
└── modules/
    ├── agents/
    │   ├── observer.yaml
    │   ├── explorer.yaml (RAG 포함)
    │   ├── quantifier.yaml
    │   ├── validator.yaml
    │   └── guardian.yaml
    │
    └── frameworks/
        ├── market_definition.yaml
        ├── seven_powers.yaml
        └── discovery_sprint.yaml
```

**AI 사용 플로우**:
```
Step 1: umis.yaml (INDEX) 읽기
  "UMIS v7.0.0 - RAG 기반 5-Agent 시스템"
  
  Agent 요약:
    Observer (Albert): 시장 구조
    Explorer (Steve): 기회 발굴 (RAG)
    ...
  
  RAG 아키텍처:
    - 54개 패턴 자동 검색
    - Knowledge Graph
  
  Module Index:
    - 상세: modules/agents/explorer.yaml
    - 프레임워크: modules/frameworks/

Step 2: AI 판단
  "Explorer 필요 + 시장 정의 필요"
  → modules/agents/explorer.yaml 로드
  → modules/frameworks/market_definition.yaml 로드

Step 3: 실행
  전체 기능 활용
```

**장점**:
- ✅ **빠른 파악** (INDEX 800줄만)
- ✅ **필요한 것만** (선택적 로드)
- ✅ **누락 방지** (INDEX에 전체 맵)
- ✅ **토큰 효율** (점진적)
- ✅ **유지보수** (모듈별 독립)

**단점**:
- ⚠️ 구현 필요 (모듈 분리)
- ⚠️ INDEX 관리 중요

---

### 🎯 추천 접근법: 방법 3 (Index + Modules)

#### 구조

**umis.yaml** (INDEX, 800줄):
```yaml
# ========================================
# UMIS v7.0.0 - System Index
# ========================================

system:
  version: "7.0.0"
  
  quick_overview: |
    RAG 기반 5-Agent 협업 시스템
    - 54개 검증된 패턴/사례 자동 검색
    - 완전한 추적성
    - 재검증 가능

agents:
  observer:
    name: "Albert"
    role: "시장 구조 분석"
    rag: false
    module: "modules/agents/observer.yaml"
    
  explorer:
    name: "Steve"  
    role: "기회 발굴"
    rag: true  # ⭐ RAG 사용!
    module: "modules/agents/explorer.yaml"
    capabilities:
      - "패턴 자동 검색 (31개 비즈니스 모델)"
      - "사례 검색 (50+ 성공 사례)"
      - "패턴 조합 발견 (Knowledge Graph)"
  
  # ... 나머지 Agent 요약

rag_architecture:
  version: "v3.0"
  active_agent: "Explorer"
  
  what_it_does:
    - "패턴 자동 검색 (Vector RAG)"
    - "조합 발견 (Knowledge Graph)"
    - "사례 학습 (성공/실패)"
  
  how_to_use: |
    "@Explorer, 구독 모델 패턴 찾아줘"
    → 자동으로 31개 패턴에서 검색
    → 유사 사례 (Spotify, Netflix) 발견
    → 조합 패턴 제시 (구독 + 플랫폼)

frameworks:
  market_definition:
    description: "13개 차원 시장 정의"
    module: "modules/frameworks/market_definition.yaml"
  
  seven_powers:
    description: "지속 가능한 경쟁 우위"
    module: "modules/frameworks/seven_powers.yaml"

workflows:
  comprehensive_study:
    description: "2-4주 종합 연구"
    module: "modules/workflows/comprehensive.yaml"

# ========================================
# AI 사용 가이드
# ========================================

ai_quick_start: |
  1. 이 INDEX만 읽기 (5분)
     → UMIS 전체 파악
  
  2. 필요한 모듈만 로드
     - Explorer 필요 → modules/agents/explorer.yaml
     - 시장 정의 → modules/frameworks/market_definition.yaml
  
  3. 분석 실행
     → 모든 기능 활용

module_loading_guide:
  when_to_load:
    always: "umis.yaml (INDEX)"
    
    if_explorer_needed: "modules/agents/explorer.yaml"
    if_quantifier_needed: "modules/agents/quantifier.yaml"
    if_market_definition: "modules/frameworks/market_definition.yaml"
    if_7_powers: "modules/frameworks/seven_powers.yaml"
```

---

### 📐 구현 계획

#### Step 1: INDEX 생성 (2일)
```bash
# 1. 현재 umis.yaml 백업
mv umis.yaml modules/umis_full.yaml

# 2. INDEX 생성 (800줄)
# - System overview
# - Agent summary (각 100줄)
# - RAG architecture
# - Module index
# - AI quick start

# 3. 검증
# AI가 INDEX만으로 전체 파악 가능한지 테스트
```

#### Step 2: Agent 모듈 분리 (5일)
```bash
# 각 Agent를 별도 파일로
modules/agents/observer.yaml (800줄)
modules/agents/explorer.yaml (900줄, RAG 포함)
modules/agents/quantifier.yaml (700줄)
modules/agents/validator.yaml (600줄)
modules/agents/guardian.yaml (800줄)

# INDEX에서 참조
agents:
  explorer:
    module: "modules/agents/explorer.yaml"
```

#### Step 3: Framework 모듈 분리 (3일)
```bash
modules/frameworks/market_definition.yaml
modules/frameworks/seven_powers.yaml
modules/frameworks/discovery_sprint.yaml
```

#### Step 4: Workflow 모듈 분리 (2일)
```bash
modules/workflows/comprehensive.yaml
modules/workflows/rapid.yaml
modules/workflows/quick.yaml
```

#### Step 5: 테스트 & 최적화 (3일)
```bash
# AI 테스트
# - INDEX만으로 구조 파악 가능?
# - 필요한 모듈 식별 가능?
# - 점진적 로드 작동?

# 최적화
# - INDEX 크기 최소화
# - 모듈 간 중복 제거
```

**총 소요**: 15일

---

### ⚠️ 고려사항

#### 1. AI 로딩 전략

**Cursor .cursorrules에 명시**:
```yaml
umis_loading:
  step_1: "umis.yaml (INDEX) 먼저 읽기 (필수)"
  step_2: "필요한 모듈만 로드"
  
  example:
    - "Explorer 작업" → modules/agents/explorer.yaml 로드
    - "시장 정의" → modules/frameworks/market_definition.yaml 로드
```

#### 2. INDEX의 핵심

**반드시 포함**:
- ✅ 전체 시스템 개요 (What is UMIS?)
- ✅ 5-Agent 역할 요약 (각 100줄)
- ✅ RAG가 할 수 있는 것 (Explorer)
- ✅ 주요 프레임워크 목록
- ✅ Module Index (어디에 뭐가 있는지)

**AI Quick Start 시나리오**:
```yaml
scenario_1_explorer_analysis:
  user: "@Explorer, 시장 분석해줘"
  
  ai_action:
    1: "umis.yaml INDEX 읽기"
    2: "Explorer = RAG 활용 기회 발굴"
    3: "modules/agents/explorer.yaml 로드"
    4: "RAG 검색 실행"

scenario_2_quantifier_sam:
  user: "@Quantifier, SAM 계산해줘"
  
  ai_action:
    1: "umis.yaml INDEX 읽기"
    2: "Quantifier = 4가지 방법 SAM 계산"
    3: "modules/agents/quantifier.yaml 로드"
    4: "SAM 계산 실행"
```

#### 3. 모듈 간 참조

**Cross-reference 문제**:
```yaml
# explorer.yaml에서 quantifier 참조 필요
explorer:
  step_3: "Quantifier에게 수익성 검증 요청"
  
  # 어떻게 처리?
  option_1: "modules/agents/quantifier.yaml 참조" (명시)
  option_2: "INDEX의 agent summary로 충분" (간단)
```

**해결**: INDEX에 충분한 요약 제공

---

## 📋 프로젝트 3: RAG 데이터 추가 자동화

### 🎯 목표

**현재 문제**:
```
패턴 추가하려면:
  1. data/raw/umis_business_model_patterns.yaml 열기
  2. 올바른 섹션 찾기
  3. 복잡한 YAML 구조 이해
  4. 수동 작성
  5. python scripts/01_convert_yaml.py
  6. python scripts/02_build_index.py

복잡하고 오류 가능성 높음!
```

**목표**:
```
사용자: "코웨이 해지율 4.2% 추가해줘"

AI: 자동으로
  1. 올바른 YAML 찾기 (subscription_model)
  2. 올바른 섹션 (critical_success_factors)
  3. 데이터 추가
  4. RAG 재구축
  5. 완료!

소요: 10초
```

---

### 🔍 접근 방법 분석

#### 방법 1: Cursor Agent Mode 활용 (현재 가능)

**.cursorrules에 추가**:
```yaml
data_add:
  detect: ["데이터 추가", "패턴 추가", "사례 추가", "넣어줘"]
  
  flow:
    step_1: "사용자 의도 파악"
      - 어떤 패턴? (subscription_model, platform, ...)
      - 어떤 데이터? (해지율, 매출, 사례, ...)
    
    step_2: "YAML 파일 열기"
      - data/raw/umis_business_model_patterns.yaml
      - 또는 umis_disruption_patterns.yaml
    
    step_3: "올바른 섹션 찾기"
      - subscription_model.critical_success_factors
      - 또는 success_cases
    
    step_4: "데이터 추가 (diff 제안)"
      before: |
        critical_success_factors:
          - "낮은 해지율 (<5%)"
      
      after: |
        critical_success_factors:
          - "낮은 해지율 (<5%)"
          - "코웨이 렌탈: 해지율 4.2% (업계 최저)"
    
    step_5: "사용자 승인 확인"
    
    step_6: "RAG 재구축"
      python scripts/01_convert_yaml.py
      python scripts/02_build_index.py --agent explorer
    
    step_7: "완료 메시지"
      "✅ 코웨이 해지율 데이터 추가 완료!"
```

**장점**:
- ✅ 즉시 구현 가능 (.cursorrules만 수정)
- ✅ 사용자 친화적 (대화로)
- ✅ 오류 감소 (AI가 구조 이해)

**단점**:
- ⚠️ Cursor 전용
- ⚠️ 수동 승인 필요

---

#### 방법 2: CLI 도구 (스크립트)

```python
# scripts/add_pattern.py

import click
import yaml

@click.command()
@click.option('--type', type=click.Choice(['business_model', 'disruption']))
@click.option('--pattern-id', help='패턴 ID (예: subscription_model)')
@click.option('--section', help='섹션 (예: success_cases)')
@click.option('--data', help='추가할 데이터')
def add_pattern_data(type, pattern_id, section, data):
    """RAG에 패턴 데이터 추가"""
    
    # 1. YAML 로드
    if type == 'business_model':
        yaml_path = 'data/raw/umis_business_model_patterns.yaml'
    else:
        yaml_path = 'data/raw/umis_disruption_patterns.yaml'
    
    with open(yaml_path) as f:
        patterns = yaml.safe_load(f)
    
    # 2. 패턴 찾기
    pattern = patterns[pattern_id]
    
    # 3. 섹션에 데이터 추가
    if section not in pattern:
        pattern[section] = []
    pattern[section].append(data)
    
    # 4. 저장
    with open(yaml_path, 'w') as f:
        yaml.dump(patterns, f)
    
    # 5. RAG 재구축
    os.system('python scripts/02_build_index.py --agent explorer')
    
    click.echo('✅ 데이터 추가 완료!')

# 사용
# python scripts/add_pattern.py \
#   --type business_model \
#   --pattern-id subscription_model \
#   --section critical_success_factors \
#   --data "코웨이 렌탈: 해지율 4.2%"
```

**장점**:
- ✅ 프로그래매틱
- ✅ 자동화 가능
- ✅ 오류 처리

**단점**:
- ⚠️ 명령어 복잡
- ⚠️ 사용자 학습 필요
- ⚠️ GUI 없음

---

#### 방법 3: 대화형 추가 (추천!)

```python
# scripts/add_data_interactive.py

def interactive_add():
    """대화형 데이터 추가"""
    
    print("🎯 RAG 데이터 추가")
    print()
    
    # 1. 타입 선택
    type_choice = input("추가할 데이터 타입?\n1. 비즈니스 모델 패턴\n2. Disruption 패턴\n선택: ")
    
    # 2. 패턴 목록 표시
    print("\n사용 가능한 패턴:")
    for i, pattern_id in enumerate(patterns, 1):
        print(f"{i}. {pattern_id}")
    
    pattern_choice = input("\n패턴 선택: ")
    
    # 3. 섹션 선택
    print("\n추가할 섹션:")
    print("1. critical_success_factors (핵심 성공 요인)")
    print("2. success_cases (성공 사례)")
    print("3. trigger_observations (트리거 관찰)")
    
    section_choice = input("\n섹션 선택: ")
    
    # 4. 데이터 입력
    data = input("\n추가할 데이터:\n")
    
    # 5. 미리보기
    print("\n📋 미리보기:")
    print(f"  패턴: {selected_pattern}")
    print(f"  섹션: {selected_section}")
    print(f"  데이터: {data}")
    
    confirm = input("\n추가하시겠습니까? (y/N): ")
    
    if confirm.lower() == 'y':
        # 6. 추가
        add_to_yaml(...)
        
        # 7. RAG 재구축
        rebuild = input("\nRAG 재구축? (y/N): ")
        if rebuild.lower() == 'y':
            rebuild_rag()
        
        print("\n✅ 완료!")
```

**사용**:
```bash
python scripts/add_data_interactive.py

→ 대화형으로 단계별 진행
→ 실수 방지
→ 즉시 재구축
```

**장점**:
- ✅ 사용자 친화적
- ✅ 실수 방지 (단계별 확인)
- ✅ 학습 불필요

**단점**:
- ⚠️ 자동화 어려움
- ⚠️ CLI 환경 필요

---

#### 방법 4: Cursor Agent Mode + 스마트 검색 (최종 추천!)

**.cursorrules 강화**:
```yaml
data_add:
  detect: ["데이터 추가", "패턴 추가", "사례 추가"]
  
  smart_flow:
    step_1_understand:
      user: "코웨이 해지율 4.2% 추가해줘"
      
      ai_parse:
        entity: "코웨이"
        metric: "해지율 4.2%"
        context: "구독/렌탈 사업"
      
      ai_infer:
        pattern: "subscription_model (구독 모델)"
        section: "success_cases 또는 critical_success_factors"
    
    step_2_find_yaml:
      action: "data/raw/umis_business_model_patterns.yaml 열기"
      search: "subscription_model 섹션"
    
    step_3_suggest:
      show_current: |
        subscription_model:
          critical_success_factors:
            - "낮은 해지율 (<5%)"
            - "높은 LTV/CAC 비율"
      
      suggest_addition: |
        critical_success_factors:
          - "낮은 해지율 (<5%)"
          - "코웨이 렌탈: 해지율 4.2% (2023년 기준)" ← 추가
          - "높은 LTV/CAC 비율"
      
      ask_approval: "이렇게 추가할까요? (Y/n)"
    
    step_4_add:
      if_approved:
        - 파일 수정
        - git diff 확인
        - 저장
    
    step_5_rebuild:
      ask: "RAG 재구축? (2초 소요) (Y/n)"
      if_yes:
        - python scripts/01_convert_yaml.py
        - python scripts/02_build_index.py --agent explorer
        - "✅ RAG 업데이트 완료!"

shortcuts:
  - "rag에 {data} 추가": 자동으로 위 플로우 실행
  - "rag 재구축": scripts/01+02 실행
```

**사용**:
```
Cursor:
"코웨이 해지율 4.2% RAG에 추가해줘"

→ AI가 자동으로:
  1. subscription_model 파악
  2. YAML 열기
  3. 적절한 위치 찾기
  4. diff 제안
  5. 승인 후 추가
  6. RAG 재구축

소요: 10초
```

**장점**:
- ✅ **가장 사용자 친화적**
- ✅ **자연어로 요청**
- ✅ **실수 방지** (AI가 구조 이해)
- ✅ **즉시 반영** (자동 재구축)

**구현**:
- ✅ .cursorrules만 업데이트 (즉시 가능)
- ✅ Cursor Agent Mode 활용
- ✅ 추가 코드 불필요

---

### 🎯 추가 고려사항

#### 1. 데이터 검증

**추가 전 검증**:
```yaml
validation:
  format_check:
    - "YAML 문법 오류 없는지"
    - "필수 필드 있는지"
  
  content_check:
    - "데이터 출처 명시했는지"
    - "날짜/버전 포함했는지"
  
  consistency_check:
    - "기존 데이터와 모순 없는지"
    - "스키마 준수하는지"
```

#### 2. 데이터 소스 추적

**추가할 때 메타데이터**:
```yaml
success_cases:
  - case: "코웨이 렌탈"
    metric: "해지율 4.2%"
    year: "2023"
    source: "공시자료"
    reliability: "95%"
    added_by: "user_kangmin"
    added_date: "2025-11-03"
```

#### 3. 버전 관리

**패턴 파일 버전**:
```bash
# 변경 전 자동 백업
data/raw/umis_business_model_patterns.yaml
→ data/raw/.backup/umis_business_model_patterns_20251103.yaml

# Git으로도 추적
git add data/raw/umis_business_model_patterns.yaml
git commit -m "data: add 코웨이 해지율 (subscription_model)"
```

---

## 📊 3개 프로젝트 비교

| 프로젝트 | 난이도 | 소요 | 우선순위 | 영향도 |
|---------|-------|------|---------|--------|
| **1. Deliverable 생성** | 중 | 2-7주 | P1 | 높음 (자동화) |
| **2. umis.yaml 모듈화** | 중-높 | 2-3주 | P0 | **매우 높음** (AI 효율) |
| **3. RAG 데이터 추가** | 낮 | 1-3일 | P1 | 중 (사용성) |

---

## 🎯 추천 순서

### v7.1.0 (1개월)
1. **RAG 데이터 추가 자동화** (1주)
   - .cursorrules 업데이트
   - 즉시 활용 가능
   
2. **umis.yaml 모듈화** (3주) ⭐
   - INDEX 생성 (2일)
   - Agent 모듈 분리 (5일)
   - Framework 모듈 (3일)
   - 테스트 (3일)

### v7.2.0 (1.5개월)
3. **Deliverable 자동 생성 Phase 1** (3주)
   - Template Generator
   - Markdown 산출물 (Explorer, Observer)

### v7.3.0 (1개월)
4. **Deliverable 자동 생성 Phase 2** (4주)
   - Class Builder
   - Excel 생성 (Quantifier)

---

## 💡 핵심 인사이트

### 프로젝트 2가 가장 중요한 이유

**현재 문제**:
```
AI가 umis.yaml 5,509줄 전체를 읽으면:
  1. 토큰 과다 소비
  2. 핵심 놓침 (너무 많은 정보)
  3. 부분만 이해 → 기능 누락
  
예: "@Explorer 시장 분석"
  AI가 RAG 활용법을 놓침
  → 수동으로 패턴 분석
  → RAG의 의미 없음!
```

**모듈화 후**:
```
AI가 umis.yaml (INDEX) 800줄만 읽으면:
  1. 5-Agent 역할 명확히 파악
  2. Explorer = RAG 자동 검색!
  3. 필요한 모듈만 로드
  4. 모든 기능 활용 ✅
```

**영향**:
- AI 효율: 5배 향상
- 기능 활용: 100%
- 토큰 절약: 70%

---

이 3가지 프로젝트를 순서대로 진행하면 UMIS가 완전한 자동화 시스템이 됩니다!

진행하시겠습니까?
