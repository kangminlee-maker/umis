# Estimator Agent 전환 작업 설계

**작성일**: 2025-11-07  
**목표**: Guestimation v3.0 → Estimator (Fermi) Agent 전환  
**예상 시간**: 3-4시간  
**우선순위**: P1 (아키텍처 일관성)

---

## 🎯 작업 목표

### 핵심 목표

```yaml
1. 아키텍처 일관성
   - 5-Agent → 6-Agent 시스템
   - agent_view="guestimation" → agent_view="estimator"
   - 통일된 구조

2. 명확한 역할
   - Agent ID: Estimator
   - 이름: Fermi
   - 역할: 값 추정 및 지능적 판단 전문가

3. 사용성 개선
   - @Fermi 호출 가능
   - EstimatorRAG() 통일된 인터페이스
   - 협업 인터페이스 명확화

4. Workflow 통합
   - 기존: Observer → Explorer → Quantifier → Validator → Guardian
   - 신규: Estimator는 모든 Agent의 협업 파트너
```

---

## 📋 전체 변경 목록 (8개 카테고리)

### 1. 폴더 및 파일 구조 (Critical!)

```yaml
이동:
  umis_rag/guestimation_v3/ → umis_rag/agents/estimator/
  
  Before:
    umis_rag/
      ├── agents/
      │   ├── observer.py
      │   ├── explorer.py
      │   ├── quantifier.py
      │   └── validator.py
      └── guestimation_v3/ ⚠️ (불일치)
          ├── tier1.py
          ├── tier2.py
          └── ...
  
  After:
    umis_rag/
      └── agents/
          ├── observer.py
          ├── explorer.py
          ├── quantifier.py
          ├── validator.py
          └── estimator/ ✅ (일관성)
              ├── __init__.py (EstimatorRAG export)
              ├── estimator.py (통합 클래스)
              ├── tier1.py
              ├── tier2.py
              ├── learning_writer.py
              ├── source_collector.py
              ├── judgment.py
              ├── models.py
              ├── rag_searcher.py
              └── sources/

변경 이유:
  - 아키텍처 일관성
  - 모든 Agent가 agents/ 폴더에
  - 동등한 위치
```

### 2. 클래스 구조 (New!)

```python
# umis_rag/agents/estimator/estimator.py (신규)

class EstimatorRAG:
    """
    Estimator (Fermi) RAG Agent
    
    역할:
    -----
    - 값 추정 및 지능적 판단
    - 맥락 기반 증거 수집 (11개 Source)
    - 학습하는 시스템 (사용할수록 빠름)
    
    특징:
    -----
    - 3-Tier: Fast → Judgment → Fermi
    - Context-Aware: domain, region, time
    - 자동 학습: confidence >= 0.80
    
    핵심 메서드:
    -----------
    - estimate(): 통합 추정 (Tier 1→2→3 자동)
    - contribute(): 사용자 기여 (확정 사실)
    
    협업:
    -----
    - Observer: 비율 추정
    - Explorer: 시장 크기 감 잡기
    - Quantifier: 데이터 부족 시
    - Validator: 추정치 검증
    """
    
    def __init__(self):
        """Estimator RAG Agent 초기화"""
        logger.info("Estimator (Fermi) RAG Agent 초기화")
        
        # Tier 1: Fast Path
        self.tier1 = Tier1FastPath()
        logger.info("  ✅ Tier 1 (Built-in + 학습)")
        
        # Tier 2: Judgment Path
        self.learning_writer = None  # Lazy
        self.tier2 = None  # Lazy
        logger.info("  ✅ Tier 2 (11 Sources)")
        
        # Tier 3: Fermi (미래)
        self.tier3 = None
        
        # RAG Collections
        self.canonical_store = None  # Lazy
        self.projected_store = None  # Lazy
    
    def estimate(
        self,
        question: str,
        context: Optional[Context] = None,
        domain: Optional[str] = None,
        region: Optional[str] = None,
        time_period: Optional[str] = None
    ) -> EstimationResult:
        """
        통합 추정 메서드
        
        자동으로 Tier 1 → 2 → 3 시도
        
        Args:
            question: 질문 (예: "B2B SaaS Churn Rate는?")
            context: Context 객체 (선택)
            domain: 도메인 (예: "B2B_SaaS")
            region: 지역 (예: "한국")
            time_period: 시점 (예: "2024")
        
        Returns:
            EstimationResult
        
        Example:
            >>> estimator = EstimatorRAG()
            >>> result = estimator.estimate(
            ...     "B2B SaaS Churn Rate는?",
            ...     domain="B2B_SaaS"
            ... )
            >>> print(f"{result.value} (Tier {result.tier})")
        """
        # Context 생성
        if context is None:
            context = Context(
                domain=domain or "General",
                region=region,
                time_period=time_period or "2024"
            )
        
        logger.info(f"[Estimator] 추정 시작: {question}")
        
        # Tier 1 시도 (Fast)
        result = self.tier1.estimate(question, context)
        if result:
            logger.info(f"  ⚡ Tier 1 성공 ({result.execution_time:.2f}초)")
            return result
        
        # Tier 2 실행 (Judgment)
        self._ensure_tier2_initialized()
        result = self.tier2.estimate(question, context)
        
        if result:
            logger.info(f"  🧠 Tier 2 완료 ({result.execution_time:.2f}초)")
            return result
        
        # Tier 3 (Fermi - 미래)
        # ...
        
        logger.warning("  ❌ 추정 실패")
        return None
    
    def contribute(
        self,
        question: str,
        value: float,
        unit: str,
        context: Optional[Context] = None,
        contribution_type: str = "definite_fact"
    ) -> str:
        """
        사용자 기여 (확정 사실, 업계 상식 등)
        
        Returns:
            rule_id: 저장된 규칙 ID
        """
        from .learning_writer import UserContribution
        
        self._ensure_tier2_initialized()
        
        contribution = UserContribution(self.learning_writer)
        
        if contribution_type == "definite_fact":
            return contribution.add_definite_fact(
                question, value, unit, context
            )
        # ...
```

### 3. Import 경로 변경 (Breaking!)

```python
# Before (v7.3.0)
from umis_rag.guestimation_v3.tier1 import Tier1FastPath
from umis_rag.guestimation_v3.tier2 import Tier2JudgmentPath

# After (v7.3.1)
from umis_rag.agents.estimator import EstimatorRAG
# 또는
from umis_rag.agents.estimator.tier1 import Tier1FastPath
from umis_rag.agents.estimator.tier2 import Tier2JudgmentPath

# 권장
from umis_rag.agents.estimator import EstimatorRAG
estimator = EstimatorRAG()
result = estimator.estimate(...)  # Tier 1→2 자동
```

### 4. agent_view 변경 (Critical!)

```yaml
Projected Index:
  Before: agent_view="guestimation"
  After: agent_view="estimator"

영향받는 파일:
  1. ✅ learning_writer.py
     - sections: [agent_view: "guestimation"]
     → sections: [agent_view: "estimator"]
  
  2. ✅ rag_searcher.py
     - base_filter = {"agent_view": "guestimation"}
     → base_filter = {"agent_view": "estimator"}
  
  3. ✅ projection_rules.yaml
     - chunk_type_rules.learned_rule.target_agents: [guestimation]
     → target_agents: [estimator]
  
  4. ✅ metadata naming
     - guestimation_value → estimator_value
     - guestimation_domain → estimator_domain
     - guestimation_confidence → estimator_confidence

주의:
  - 기존 학습 데이터 migration 필요 (없으면 OK)
  - projected_index에서 agent_view 재구축
```

### 5. Agent 등록 및 설정

```yaml
agent_names.yaml:
  observer: Albert
  explorer: Steve
  quantifier: Bill
  validator: Rachel
  guardian: Stewart
  estimator: Fermi  # 신규! ⭐

umis_rag/agents/__init__.py:
  from .estimator import EstimatorRAG, get_estimator_rag
  
  __all__ = [
      'ObserverRAG', 'get_observer_rag',
      'ExplorerRAG', 'ExplorerAgenticRAG',
      'QuantifierRAG', 'get_quantifier_rag',
      'ValidatorRAG', 'get_validator_rag',
      'EstimatorRAG', 'get_estimator_rag',  # 신규
  ]

싱글톤 패턴:
  def get_estimator_rag() -> EstimatorRAG:
      global _estimator_rag_instance
      if _estimator_rag_instance is None:
          _estimator_rag_instance = EstimatorRAG()
      return _estimator_rag_instance
```

### 6. Quantifier 통합 수정

```python
# umis_rag/agents/quantifier.py

# Before (v7.3.0)
from umis_rag.guestimation_v3.tier1 import Tier1FastPath
from umis_rag.guestimation_v3.tier2 import Tier2JudgmentPath

def estimate_with_guestimation(...):
    # 직접 Tier1/Tier2 사용

# After (v7.3.1)
from umis_rag.agents.estimator import get_estimator_rag

def estimate(...):  # 메서드명 간결화
    estimator = get_estimator_rag()
    return estimator.estimate(question, domain=domain, region=region)

# 더 간결하고 명확함!
```

### 7. Workflow 정의 (중요!)

```yaml
기존 Workflow (5-Agent):
  Observer → Explorer → Quantifier → Validator → Guardian

Estimator의 위치:
  
  옵션 A: 병렬 협업 파트너 (추천! ⭐)
    Observer ─┐
    Explorer ─┤
    Quantifier├─→ (필요 시) Estimator 호출 ─→ 값 추정
    Validator ─┤
    Guardian ─┘
  
  특징:
    - 독립적 Agent (6번째)
    - 다른 Agent들이 필요 시 호출
    - Workflow에 끼어들지 않음
    - "협업 파트너" 역할
  
  사용:
    - Observer: "이 비율 추정해줘" → @Fermi
    - Explorer: "시장 크기 감 잡아봐" → @Fermi
    - Quantifier: "데이터 없는데 추정해줘" → @Fermi
  
  옵션 B: Workflow에 통합
    Observer → Explorer → Estimator → Quantifier → Validator → Guardian
  
  문제:
    - Estimator는 필요 시만 사용 (항상 필요 X)
    - Workflow 복잡도 증가
    - 역할 혼란

결론: 옵션 A (병렬 협업 파트너) ✅
```

### 8. 문서 업데이트

```yaml
코어 문서:
  1. ✅ .cursorrules
     - agents: Estimator 추가
     - flow: 협업 파트너 명시
  
  2. ✅ UMIS_ARCHITECTURE_BLUEPRINT.md
     - 6-Agent 시스템
     - Estimator 역할 설명
  
  3. ✅ umis.yaml
     - agents 섹션에 Estimator 추가
     - universal_tools.guestimation → estimator 참조
  
  4. ✅ umis_core.yaml
     - Agent 목록 업데이트
  
  5. ✅ CURRENT_STATUS.md
     - v7.3.1 버전 업데이트
     - Estimator Agent 추가
  
  6. ✅ CHANGELOG.md
     - v7.3.1 변경사항 추가

Release:
  7. ✅ docs/release_notes/RELEASE_NOTES_v7.3.1.md
     - Agent화 설명
     - Breaking Changes
     - Migration Guide
```

---

## 🔧 상세 작업 단계 (10단계)

### Phase 1: 준비 (1시간)

#### Step 1: 폴더 구조 생성 (15분)

```bash
# 1. 새 폴더 생성
mkdir -p umis_rag/agents/estimator
mkdir -p umis_rag/agents/estimator/sources

# 2. 파일 복사 (git mv는 나중에)
cp -r umis_rag/guestimation_v3/* umis_rag/agents/estimator/

# 3. 구조 확인
ls -la umis_rag/agents/estimator/
```

**검증**:
- ✅ 폴더 생성 확인
- ✅ 모든 파일 복사 확인
- ✅ sources/ 폴더 포함 확인

#### Step 2: EstimatorRAG 통합 클래스 작성 (30분)

```python
# umis_rag/agents/estimator/estimator.py (신규)

class EstimatorRAG:
    """
    Estimator (Fermi) RAG Agent
    
    6번째 Agent - 값 추정 및 지능적 판단 전문가
    """
    
    def __init__(self):
        # Tier 1, 2, 3 통합
        # Learning Writer 연결
        # RAG Collections 초기화
    
    def estimate(self, question, context=None, **kwargs):
        # Tier 1 → 2 → 3 자동
    
    def contribute(self, question, value, unit, **kwargs):
        # 사용자 기여
    
    def get_stats(self):
        # 학습 통계

# 싱글톤
_estimator_rag_instance = None

def get_estimator_rag() -> EstimatorRAG:
    global _estimator_rag_instance
    if _estimator_rag_instance is None:
        _estimator_rag_instance = EstimatorRAG()
    return _estimator_rag_instance
```

**검증**:
- ✅ EstimatorRAG 클래스 완성
- ✅ estimate() 메서드 통합
- ✅ 싱글톤 패턴 구현

#### Step 3: __init__.py 작성 (15분)

```python
# umis_rag/agents/estimator/__init__.py

"""
Estimator (Fermi) Agent - 값 추정 및 판단 전문가

역할:
- 맥락 기반 값 추정
- 11개 Source 통합 판단
- 학습하는 시스템 (6-16배 빠름)

사용:
    from umis_rag.agents.estimator import EstimatorRAG
    
    estimator = EstimatorRAG()
    result = estimator.estimate("B2B SaaS Churn Rate는?")
"""

from .estimator import EstimatorRAG, get_estimator_rag
from .tier1 import Tier1FastPath
from .tier2 import Tier2JudgmentPath
from .learning_writer import LearningWriter, UserContribution
from .models import Context, EstimationResult

__all__ = [
    'EstimatorRAG',
    'get_estimator_rag',
    'Tier1FastPath',
    'Tier2JudgmentPath',
    'LearningWriter',
    'UserContribution',
    'Context',
    'EstimationResult',
]
```

**검증**:
- ✅ Export 목록 완전
- ✅ Docstring 명확
- ✅ __all__ 정의

---

### Phase 2: agent_view 변경 (1시간)

#### Step 4: learning_writer.py 수정 (15분)

```python
# Before
'agent_view': 'guestimation'

# After
'agent_view': 'estimator'

# 파일 내 모든 "guestimation" → "estimator"
# 단, 주석/docstring은 신중히 (의미 확인)
```

**검증**:
- ✅ sections.agent_view 변경
- ✅ 주석 업데이트

#### Step 5: rag_searcher.py 수정 (15분)

```python
# Before
base_filter = {"agent_view": "guestimation"}

# After
base_filter = {"agent_view": "estimator"}

# metadata 필드명
# Before: guestimation_value, guestimation_domain
# After: estimator_value, estimator_domain
```

**검증**:
- ✅ agent_view 필터 변경
- ✅ metadata 필드명 일괄 변경

#### Step 6: projection_rules.yaml 수정 (15min)

```yaml
# config/projection_rules.yaml

chunk_type_rules:
  learned_rule:
    # Before
    target_agents: [guestimation]
    
    # After
    target_agents: [estimator]
    
    metadata_mapping:
      # Before
      value: "guestimation_value"
      domain: "guestimation_domain"
      
      # After
      value: "estimator_value"
      domain: "estimator_domain"
      # ... 19개 필드 모두 변경
```

**검증**:
- ✅ target_agents 변경
- ✅ metadata_mapping 전체 변경 (19개)

#### Step 7: 내부 참조 일괄 변경 (15min)

```bash
# guestimation → estimator 일괄 변경
# 대상 파일들:
# - tier1.py, tier2.py, source_collector.py, judgment.py
# - models.py (주석)
# - sources/*.py (주석)

# 신중히 변경 (의미 확인)
# - "Guestimation v3.0" → "Estimator v3.0" (주석)
# - "guestimation_" prefix → "estimator_" (변수/필드명)
```

**검증**:
- ✅ grep으로 "guestimation" 검색 → 0개 (의도적 유지 제외)

---

### Phase 3: Agent 등록 및 통합 (30분)

#### Step 8: Agent 등록 (15min)

```yaml
# config/agent_names.yaml
estimator: Fermi  # 추가

# umis_rag/agents/__init__.py
from .estimator import EstimatorRAG, get_estimator_rag

__all__ = [
    # ... 기존 ...
    'EstimatorRAG',
    'get_estimator_rag',
]
```

**검증**:
- ✅ agent_names.yaml 업데이트
- ✅ agents/__init__.py export
- ✅ import 테스트

#### Step 9: Quantifier 수정 (15min)

```python
# umis_rag/agents/quantifier.py

# Before
from umis_rag.guestimation_v3.tier1 import Tier1FastPath
self.guestimation_tier1 = Tier1FastPath()

# After
from umis_rag.agents.estimator import get_estimator_rag

def estimate(self, question, domain=None, region=None):
    estimator = get_estimator_rag()
    return estimator.estimate(question, domain=domain, region=region)

# 간결하고 명확!
```

**검증**:
- ✅ Import 경로 변경
- ✅ 메서드 간결화
- ✅ 테스트 통과

---

### Phase 4: 테스트 및 문서 (1시간)

#### Step 10: 테스트 업데이트 (30min)

```python
# scripts/test_estimator_agent.py (신규)

from umis_rag.agents.estimator import EstimatorRAG

def test_estimator_agent():
    """EstimatorRAG 통합 테스트"""
    
    estimator = EstimatorRAG()
    
    # Test 1: 직접 호출
    result = estimator.estimate("B2B SaaS Churn Rate는?")
    
    # Test 2: Context 사용
    result = estimator.estimate(
        "음식점 월매출은?",
        domain="Food_Service",
        region="한국"
    )
    
    # Test 3: 사용자 기여
    rule_id = estimator.contribute(
        question="우리 회사 직원 수는?",
        value=150,
        unit="명"
    )

# 기존 테스트 수정
# - test_learning_writer.py → import 경로 변경
# - test_learning_e2e.py → import 경로 변경
# - test_tier1_guestimation.py → test_tier1_estimator.py
# - test_tier2_guestimation.py → test_tier2_estimator.py
# - test_quantifier_v3.py → import 경로 변경
```

**검증**:
- ✅ 모든 기존 테스트 통과
- ✅ 신규 EstimatorRAG 테스트 통과
- ✅ Quantifier 통합 테스트

#### Step 11: 문서 업데이트 (30min)

```yaml
우선순위 높음:
  1. ✅ .cursorrules
     - agents에 estimator 추가
     - agent_view 업데이트
  
  2. ✅ UMIS_ARCHITECTURE_BLUEPRINT.md
     - 6-Agent 시스템
     - Estimator 역할 추가
  
  3. ✅ umis.yaml
     - agents 섹션 Estimator 추가
  
  4. ✅ CURRENT_STATUS.md
     - v7.3.1 업데이트
  
  5. ✅ CHANGELOG.md
     - v7.3.1 추가

Release Notes:
  6. ✅ docs/release_notes/RELEASE_NOTES_v7.3.1.md
     - Agent화 설명
     - Breaking Changes (import 경로)
     - Migration Guide
```

---

## 🚨 Critical Points (주의사항)

### 1. agent_view 변경의 영향

```yaml
문제:
  - 기존 projected_index의 agent_view="guestimation"
  - 새 코드는 agent_view="estimator" 검색
  - 매칭 안 됨!

해결 방법:
  
  옵션 A: 재구축 (권장)
    - projected_index 재생성
    - agent_view="estimator"로 저장
    - 학습 데이터 리셋 (어차피 0개)
  
  옵션 B: 하위 호환
    - agent_view in ["guestimation", "estimator"] 검색
    - 복잡함 증가
  
  선택: 옵션 A (깨끗한 시작)
```

### 2. Import 경로 Breaking Change

```yaml
영향:
  - 외부 사용자 코드 (있다면)
  - 테스트 코드 (5개 파일)
  - Quantifier (내부)

대응:
  1. ✅ Migration Guide 작성
  2. ✅ v7.3.1 Release Notes 명시
  3. ✅ 기존 경로 deprecated 경고
  4. ✅ 모든 테스트 업데이트
```

### 3. Workflow 정의 명확화

```yaml
중요:
  - Estimator는 "협업 파트너"
  - Workflow 순서에 끼어들지 않음
  - 필요 시 호출

명시:
  - 문서에 명확히 설명
  - 다이어그램 업데이트
  - 예시 추가
```

---

## 📊 예상 영향 분석

### 파일 변경 (50개 이상)

```yaml
이동/이름 변경:
  - umis_rag/guestimation_v3/ → agents/estimator/ (10개 파일)

내용 수정:
  - agents/estimator/*.py (10개, agent_view 변경)
  - config/projection_rules.yaml (1개)
  - config/agent_names.yaml (1개)
  - umis_rag/agents/__init__.py (1개)
  - umis_rag/agents/quantifier.py (1개)
  - scripts/test_*.py (5개, import 경로)
  
  - .cursorrules (1개)
  - UMIS_ARCHITECTURE_BLUEPRINT.md (1개)
  - umis.yaml (1개)
  - umis_core.yaml (1개)
  - CURRENT_STATUS.md (1개)
  - CHANGELOG.md (1개)

신규 생성:
  - agents/estimator/estimator.py (1개, 통합 클래스)
  - scripts/test_estimator_agent.py (1개)
  - RELEASE_NOTES_v7.3.1.md (1개)

총: ~35개 파일
```

### Import 경로 변경 영향

```python
Before (v7.3.0):
  from umis_rag.guestimation_v3.tier1 import Tier1FastPath
  from umis_rag.guestimation_v3.tier2 import Tier2JudgmentPath
  from umis_rag.guestimation_v3.learning_writer import LearningWriter

After (v7.3.1):
  from umis_rag.agents.estimator import EstimatorRAG
  # 또는 상세 접근
  from umis_rag.agents.estimator.tier1 import Tier1FastPath

권장 (통합 사용):
  from umis_rag.agents.estimator import EstimatorRAG
  estimator = EstimatorRAG()
  result = estimator.estimate(...)
```

---

## ✅ 검증 체크리스트

### 코드 검증

```yaml
✅ Import 무결성
  - from umis_rag.agents.estimator import EstimatorRAG
  - 순환 의존성 없음
  - 모든 모듈 로드 성공

✅ 기능 검증
  - Tier 1: Built-in + 학습 규칙 작동
  - Tier 2: 11개 Source 수집 작동
  - Learning Writer: 저장 작동
  - Projection: agent_view="estimator" 생성

✅ 통합 검증
  - EstimatorRAG() 단독 실행
  - Quantifier에서 호출
  - 모든 테스트 통과
```

### 문서 검증

```yaml
✅ Agent 등록
  - agent_names.yaml: estimator: Fermi
  - .cursorrules 업데이트
  - umis.yaml 업데이트

✅ 아키텍처 문서
  - UMIS_ARCHITECTURE_BLUEPRINT.md (6-Agent)
  - 역할 설명 추가
  - Workflow 명확화

✅ Release Notes
  - v7.3.1 작성
  - Breaking Changes 명시
  - Migration Guide 완전
```

---

## 🎯 작업 순서 (권장)

### Day 1 (3-4시간)

```yaml
Morning (2시간):
  1. ✅ 폴더 구조 생성 및 파일 복사
  2. ✅ EstimatorRAG 통합 클래스 작성
  3. ✅ __init__.py 작성
  4. ✅ agent_view 일괄 변경 (learning_writer, rag_searcher)

Afternoon (2시간):
  5. ✅ projection_rules.yaml 수정
  6. ✅ Agent 등록 (agent_names.yaml, agents/__init__.py)
  7. ✅ Quantifier 수정 (간결화)
  8. ✅ 테스트 파일 import 경로 변경
  9. ✅ 모든 테스트 실행 및 통과
  10. ✅ 문서 업데이트 (6개)
```

### 커밋 전략

```yaml
작은 커밋 (추적 용이):
  1. refactor: 폴더 구조 (guestimation_v3 → agents/estimator)
  2. feat: EstimatorRAG 통합 클래스 추가
  3. refactor: agent_view "guestimation" → "estimator"
  4. config: Agent 등록 (estimator: Fermi)
  5. refactor: Quantifier 간결화
  6. test: 모든 테스트 경로 업데이트
  7. docs: 6-Agent 시스템 업데이트
  8. release: v7.3.1 Release Notes

또는 큰 커밋:
  1. refactor: Guestimation → Estimator Agent 전환 (v7.3.1)
```

---

## 🎊 최종 결과 (v7.3.1)

### 6-Agent 시스템

```yaml
1. Observer (Albert): 시장 구조 관찰
2. Explorer (Steve): 기회 발굴
3. Quantifier (Bill): 정량 분석
4. Validator (Rachel): 데이터 검증
5. Guardian (Stewart): 품질 관리
6. Estimator (Fermi): 값 추정 및 판단 ⭐ NEW!

특징:
  - 완전한 일관성 (모두 agents/)
  - 통일된 RAG 패턴
  - 명확한 역할 분담
  - 협업 인터페이스
```

### 사용 예시

```python
# 1. 독립 사용
from umis_rag.agents.estimator import EstimatorRAG

estimator = EstimatorRAG()
result = estimator.estimate("Churn Rate는?", domain="B2B_SaaS")

# 2. Cursor에서
@Fermi, B2B SaaS Churn Rate는?

# 3. Agent 협업
quantifier = QuantifierRAG()
quantifier.estimator.estimate(...)  # 내부 협업

# 4. 사용자 기여
estimator.contribute(
    question="우리 회사 직원 수는?",
    value=150,
    unit="명"
)
```

---

## 💡 제 의견 (강력 추천!)

```yaml
추천도: ⭐⭐⭐⭐⭐ (5/5)

이유:
  1. 이미 Agent임:
     - agent_view 사용 중
     - 독립적 역할
     - RAG 구조
  
  2. 일관성 극대화:
     - 6개 Agent 완전 통일
     - agents/ 폴더 통합
     - 동일 패턴
  
  3. 장기적 이득:
     - 유지보수성 ↑
     - 확장성 ↑
     - 명확한 구조
  
  4. 작업량 적절:
     - 3-4시간
     - Breaking Change 최소
     - 이득 >> 비용

결론: 지금이 최적 타이밍!
  - v7.3.0 방금 출시
  - 사용자 적음
  - 구조 정리 중
```

---

**다음 단계**: 작업 진행 여부 확인 후 즉시 시작 가능! 🚀

진행하시겠습니까? 단계별로 꼼꼼히 진행하겠습니다.
