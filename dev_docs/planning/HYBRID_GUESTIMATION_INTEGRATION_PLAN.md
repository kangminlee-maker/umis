# Hybrid Guestimation 통합 계획
**프로젝트명**: UMIS Guestimation + Domain-Centric Reasoner 통합  
**버전**: UMIS v7.1.0 → v7.2.0  
**날짜**: 2025-11-04  
**담당**: AI + User  
**예상 기간**: 5주 (단계별 1-2주)

---

## 📋 목차
1. [프로젝트 개요](#프로젝트-개요)
2. [5단계 실행 계획](#5단계-실행-계획)
3. [파일 변경 목록](#파일-변경-목록)
4. [테스트 전략](#테스트-전략)
5. [품질 검증 기준](#품질-검증-기준)
6. [리스크 관리](#리스크-관리)

---

## 프로젝트 개요

### 🎯 목표
UMIS의 빠른 Guestimation과 Domain-Centric Reasoner의 정밀성을 결합한 하이브리드 시스템 구축

### 📊 현재 상태
```yaml
umis_guestimation:
  status: "운영 중"
  location: "umis.yaml#guestimation"
  accuracy: "±50%"
  time: "5-30분"
  agents: "all"

domain_reasoner:
  status: "문서화 완료"
  location: "data/raw/umis_domain_reasoner_methodology.yaml"
  accuracy: "±30%"
  time: "1-4시간"
  agents: "quantifier, validator"
```

### 🎯 목표 상태
```yaml
hybrid_system:
  phase_1: "UMIS Guestimation (빠른 스캔)"
  phase_2: "Domain Reasoner (정밀 분석)"
  auto_switch: "Guardian 자동 전환"
  
  integration:
    tool_registry: "2개 방법론 등록"
    guardian: "자동 전환 로직"
    bill: "Should/Will 분석"
    rachel: "KPI 정의 라이브러리"
    cursor: "@ 명령어 통합"
```

### 📈 성공 지표
1. **기능**:
   - ✅ Tool Registry에 2개 방법론 등록
   - ✅ Guardian 자동 전환 (신뢰도 < 50%)
   - ✅ Bill Should/Will Excel 시트
   - ✅ Rachel KPI 정의 100개+
   - ✅ Cursor @ 명령어 3개

2. **성능**:
   - Phase 1 속도: 5-30분 유지
   - Phase 2 정확도: ±30% 달성
   - 전환 정확도: 80%+ (올바른 방법론 선택)

3. **사용성**:
   - 문서화 완료 (README, 가이드)
   - 예시 3개 이상
   - 테스트 커버리지 80%+

---

## 5단계 실행 계획

### 📅 타임라인

```
Week 1: [Step 1 완료] Tool Registry 확장
Week 2: [Step 2 완료] Guardian 자동 전환
Week 3: [Step 3 시작] Bill Quantifier 확장
Week 4: [Step 3 완료, Step 4 시작] Rachel KPI Library
Week 5: [Step 4 완료, Step 5 완료] Cursor 통합 & 최종 검증
```

---

## Step 1: Tool Registry 확장 (즉시 - Day 1)

### 🎯 목표
두 방법론을 공식 도구로 등록하고 Agent별 사용 가이드 명시

### 📝 작업 항목

#### 1.1 tool_registry.yaml 업데이트
**파일**: `config/tool_registry.yaml`

**추가 내용**:
```yaml
# ========================================
# Universal Tools (범용 도구)
# ========================================

universal_tools:
  
  - tool_id: "TOOL_UNI_001"
    tool_key: "tool:universal:guestimation"
    name: "Guestimation (Fermi Estimation)"
    version: "2.0"
    category: "rapid_estimation"
    
    agents:
      primary: ["explorer", "quantifier"]
      secondary: ["observer", "validator", "guardian"]
    
    description: |
      Fermi 4원칙 기반 빠른 자릿수 추정.
      8가지 데이터 출처 자유 조합.
      Order of Magnitude (±50%) 목표.
    
    when_to_use:
      - "초기 탐색 (목표 불명확)"
      - "빠른 기회 우선순위 판단"
      - "성숙 시장 (데이터 풍부)"
      - "스타트업 환경 (속도 중시)"
    
    when_not_to_use:
      - "정밀 분석 필요 (±30% 이내)"
      - "규제 산업 (의료, 금융)"
      - "투자 심사 (재현성 필수)"
      - "신규 시장 (데이터 부족)"
    
    specifications:
      accuracy: "±50%"
      time: "5-30분"
      output: "EST_xxx (추정치 ID)"
      documentation: "7개 섹션 (Estimation_Details)"
    
    fermi_principles:
      - "모형: 추상 → 계산 가능 (시장 = 고객 × 단가)"
      - "분해: 큰 문제 → 작은 요소"
      - "제약: 물리적/시간적 한계"
      - "자릿수: 500억? 5000억?"
    
    data_sources:
      - "1. 프로젝트 데이터"
      - "2. LLM 직접 질문"
      - "3. 검색 공통 맥락"
      - "4. 법칙 (물리/법률)"
      - "5. 행동경제학"
      - "6. 통계 패턴"
      - "7. Rule of Thumb (RAG 12.5%)"
      - "8. 시공간 제약"
    
    file_references:
      main: "umis.yaml#methodologies.guestimation"
      guide: "docs/GUESTIMATION_FRAMEWORK.md"
      comparison: "docs/GUESTIMATION_COMPARISON.md"
    
    examples:
      - "피아노 전환율: 15% (RAG 검증)"
      - "휴일 여행: 2,500억 (분해)"
      - "자장면 배달: 42만 (제약)"
      - "전봇대: 716만 (Fermi)"
  
  - tool_id: "TOOL_UNI_002"
    tool_key: "tool:universal:domain_reasoner_10_signals"
    name: "Domain-Centric Reasoner (10-Signal)"
    version: "0.9-umis"
    category: "deep_reasoning"
    
    agents:
      primary: ["quantifier", "validator"]
      secondary: ["explorer", "observer"]
      coordinator: "guardian"
    
    description: |
      10가지 신호 우선순위 기반 정밀 추론.
      RAG 중심 (s2, s9, s10).
      합의 범위 + 전이 보정 + 검증 로그 (±30%).
    
    when_to_use:
      - "정밀 분석 (목표 명확)"
      - "신규 시장 (데이터 부족, 사례 전이)"
      - "규제 산업 (의료, 금융)"
      - "투자 심사 (재현성, 추적성)"
      - "대기업 환경 (정밀도 중시)"
    
    when_not_to_use:
      - "초기 탐색 (빠른 판단)"
      - "시간 제약 (< 1시간)"
      - "간단한 질문 (자릿수만 필요)"
    
    specifications:
      accuracy: "±30%"
      time: "1-4시간"
      output: "증거표 + 검증로그 + Should/Will"
      documentation: "7개 섹션 리포트"
    
    signal_stack:
      s1: "LLM Guess (0.15)"
      s2: "RAG Consensus (0.9) ← 핵심"
      s3: "Laws/Ethics/Physics (1.0) ← 최우선"
      s4: "Behavioral Econ (0.6)"
      s5: "Stat Patterns (0.75)"
      s6: "Math Relations (1.0) ← 최우선"
      s7: "Rules of Thumb (0.7)"
      s8: "Time/Space Bounds (1.0) ← 최우선"
      s9: "Case Analogies (0.85) ← RAG"
      s10: "Industry KPI Library (0.95) ← RAG"
    
    precedence_order: "s3 → s8 → s6 → s10 → s2 → s9 → s7 → s5 → s4 → s1"
    
    pipeline:
      step_1: "정의 고정 (s10)"
      step_2: "제약 확인 (s3, s8)"
      step_3: "구조 분해"
      step_4: "RAG 검색 (s2, s9, s10)"
      step_5: "융합 (우선순위 적용)"
      step_6: "행동경제학 보정 (s4)"
      step_7: "검증 (체크리스트)"
      step_8: "리포트 생성"
    
    file_references:
      main: "data/raw/umis_domain_reasoner_methodology.yaml"
      comparison: "docs/GUESTIMATION_COMPARISON.md"
    
    examples:
      - "배달 플랫폼 수수료율: 8.5% (범위 6-12%)"
      - "시니어 케어 로봇: 2,850억 (범위 1,500-5,000억)"

# ========================================
# Hybrid Strategy (자동 전환)
# ========================================

hybrid_strategy:
  description: "2단계 하이브리드 접근법"
  
  phase_1:
    tool: "TOOL_UNI_001 (Guestimation)"
    purpose: "빠른 스캔, 기회 필터링"
    time: "5-30분"
    output: "자릿수, 기회 우선순위"
  
  phase_2:
    tool: "TOOL_UNI_002 (Domain Reasoner)"
    purpose: "정밀 분석, 증거 기반 추론"
    time: "1-4시간"
    output: "±30% 수렴, 증거표, Should/Will"
  
  transition_triggers:
    - condition: "confidence < 0.5"
      action: "Phase 2 권고"
      reason: "신뢰도 낮음"
    
    - condition: "range_width > 1.5"
      action: "Phase 2 권고"
      reason: "범위 너무 넓음 (±75% 이상)"
    
    - condition: "opportunity_size > 100_000_000_000"
      action: "Phase 2 권고"
      reason: "기회 크기 > 1,000억 (중요도 높음)"
    
    - condition: "regulatory_industry == true"
      action: "Phase 2 필수"
      reason: "규제 산업 (정밀도 필수)"
    
    - condition: "new_market == true"
      action: "Phase 2 권고"
      reason: "신규 시장 (사례 전이 필요)"
  
  coordinator: "guardian"
```

#### 1.2 README 업데이트
**파일**: `README.md`

**추가 섹션**:
```markdown
## 🧮 Guestimation 방법론

UMIS는 2가지 추정 방법론을 제공합니다:

### 1. UMIS Guestimation (빠른 추정)
- **속도**: ⚡ 5-30분
- **정확도**: ±50% (자릿수)
- **적합**: 초기 탐색, 기회 우선순위

```bash
# 사용 예시
@Explorer, 구독 모델 시장 규모 guestimate해줘
```

### 2. Domain-Centric Reasoner (정밀 추정)
- **속도**: 🔬 1-4시간
- **정확도**: ±30% (수렴)
- **적합**: 정밀 분석, 투자 심사

```bash
# 사용 예시
@Quantifier, 시니어 케어 로봇 시장 규모를 Domain Reasoner로 분석해줘
```

### 하이브리드 전략 (권장)
1. **Phase 1**: Guestimation으로 빠른 스캔
2. **신뢰도 < 50% 또는 기회 > 1,000억** → Phase 2 진행
3. **Phase 2**: Domain Reasoner로 정밀 분석

자세한 비교: [GUESTIMATION_COMPARISON.md](docs/GUESTIMATION_COMPARISON.md)
```

### ✅ 완료 기준
- [ ] `config/tool_registry.yaml`에 2개 도구 등록
- [ ] `README.md`에 사용 가이드 추가
- [ ] 문서 링크 정합성 확인
- [ ] Git commit: "Add: Tool Registry - Hybrid Guestimation"

### ⏱️ 예상 시간
**30분 - 1시간**

---

## Step 2: Guardian 자동 전환 (1주 - Week 2)

### 🎯 목표
Guardian이 추정 결과를 평가하여 적절한 방법론을 자동 권고

### 📝 작업 항목

#### 2.1 Guardian Meta-RAG 확장
**파일**: `umis_rag/guardian/meta_rag.py`

**추가 기능**:
```python
# umis_rag/guardian/meta_rag.py

class GuardianMetaRAG:
    """Guardian Meta-RAG with Methodology Recommendation"""
    
    def __init__(self):
        self.query_memory = QueryMemory()
        self.goal_memory = GoalMemory()
        self.rae_index = RAEIndex()
        # 신규 추가
        self.methodology_recommender = MethodologyRecommender()
    
    def recommend_methodology(
        self,
        estimate_result: dict,
        context: dict
    ) -> dict:
        """
        추정 결과 기반 방법론 권고
        
        Args:
            estimate_result: {
                'value': float,
                'range': tuple,
                'confidence': float (0-1),
                'method': 'guestimation'
            }
            context: {
                'domain': str,
                'geography': str,
                'regulatory': bool
            }
        
        Returns:
            {
                'recommendation': str,
                'reason': str,
                'estimated_time': str,
                'priority': str
            }
        """
        
        confidence = estimate_result.get('confidence', 0)
        value = estimate_result.get('value', 0)
        range_tuple = estimate_result.get('range', (0, 0))
        current_method = estimate_result.get('method', 'guestimation')
        
        # 범위 폭 계산
        if range_tuple[0] > 0:
            range_width = range_tuple[1] / range_tuple[0]
        else:
            range_width = float('inf')
        
        # 규제 산업 체크
        is_regulatory = context.get('regulatory', False)
        is_new_market = context.get('new_market', False)
        
        # === 결정 로직 ===
        
        # 1. 규제 산업 → 무조건 Domain Reasoner
        if is_regulatory:
            return {
                'recommendation': 'domain_reasoner',
                'reason': '규제 산업 (의료/금융/교육) → 정밀 분석 필수 (s3 Laws/Ethics)',
                'estimated_time': '2-4시간',
                'priority': 'required',
                'trigger': 'regulatory_industry'
            }
        
        # 2. 신뢰도 낮음 (< 50%)
        if confidence < 0.5:
            return {
                'recommendation': 'domain_reasoner',
                'reason': f'신뢰도 {confidence*100:.0f}% → 50% 미만 → 정밀 분석 필요',
                'estimated_time': '1-4시간',
                'priority': 'high',
                'trigger': 'low_confidence'
            }
        
        # 3. 범위 너무 넓음 (±75% 이상, 즉 상한/하한 > 1.75)
        if range_width > 1.75:
            return {
                'recommendation': 'domain_reasoner',
                'reason': f'범위 폭 {(range_width-1)*100:.0f}% → 75% 초과 → RAG Consensus (s2) 필요',
                'estimated_time': '1-3시간',
                'priority': 'high',
                'trigger': 'wide_range'
            }
        
        # 4. 기회 크기 큼 (> 1,000억)
        if value > 100_000_000_000:
            value_b = value / 1_000_000_000
            return {
                'recommendation': 'domain_reasoner',
                'reason': f'기회 크기 {value_b:.0f}억 → 1,000억 초과 → 정밀 검증 필요',
                'estimated_time': '2-4시간',
                'priority': 'medium',
                'trigger': 'large_opportunity'
            }
        
        # 5. 신규 시장 (데이터 부족)
        if is_new_market:
            return {
                'recommendation': 'domain_reasoner',
                'reason': '신규 시장 → 직접 데이터 부족 → 사례 전이 (s9 Case Analogies) 필요',
                'estimated_time': '2-3시간',
                'priority': 'medium',
                'trigger': 'new_market'
            }
        
        # 6. 이미 Domain Reasoner 사용 중 → 계속 진행
        if current_method == 'domain_reasoner':
            return {
                'recommendation': 'continue',
                'reason': 'Domain Reasoner 진행 중 → 계속 진행',
                'estimated_time': 'N/A',
                'priority': 'continue'
            }
        
        # 7. Guestimation 충분
        return {
            'recommendation': 'guestimation_sufficient',
            'reason': f'신뢰도 {confidence*100:.0f}%, 범위 ±{(range_width-1)*50:.0f}% → Guestimation 충분',
            'estimated_time': 'N/A',
            'priority': 'low',
            'trigger': 'sufficient'
        }
    
    def evaluate_and_recommend(
        self,
        deliverable_id: str,
        content: dict
    ) -> dict:
        """
        산출물 평가 + 방법론 권고 통합
        """
        
        # 기존 품질 평가
        quality_result = self.evaluate_deliverable(deliverable_id, content)
        
        # 추정 결과 추출
        estimate_result = content.get('estimate', {})
        context = content.get('context', {})
        
        # 방법론 권고
        recommendation = self.recommend_methodology(estimate_result, context)
        
        # 결과 통합
        return {
            'quality': quality_result,
            'methodology_recommendation': recommendation,
            'next_action': self._generate_next_action(quality_result, recommendation)
        }
    
    def _generate_next_action(self, quality, recommendation):
        """다음 행동 생성"""
        
        rec = recommendation['recommendation']
        priority = recommendation['priority']
        
        if rec == 'domain_reasoner' and priority in ['required', 'high']:
            return {
                'action': 'initiate_domain_reasoner',
                'reason': recommendation['reason'],
                'estimated_time': recommendation['estimated_time'],
                'auto_trigger': True if priority == 'required' else False
            }
        
        elif rec == 'domain_reasoner' and priority == 'medium':
            return {
                'action': 'suggest_domain_reasoner',
                'reason': recommendation['reason'],
                'estimated_time': recommendation['estimated_time'],
                'user_choice': True
            }
        
        elif rec == 'guestimation_sufficient':
            return {
                'action': 'finalize_guestimation',
                'reason': recommendation['reason'],
                'confidence': quality.get('confidence', 'medium')
            }
        
        else:
            return {
                'action': 'continue',
                'reason': 'Process ongoing'
            }


class MethodologyRecommender:
    """방법론 추천 전용 클래스"""
    
    def __init__(self):
        self.decision_tree = self._build_decision_tree()
    
    def _build_decision_tree(self):
        """
        결정 트리 구조
        
        우선순위:
        1. 규제 산업 → Domain Reasoner (필수)
        2. 신뢰도 < 50% → Domain Reasoner (높음)
        3. 범위 > ±75% → Domain Reasoner (높음)
        4. 기회 > 1,000억 → Domain Reasoner (중간)
        5. 신규 시장 → Domain Reasoner (중간)
        6. 그 외 → Guestimation 충분
        """
        return {
            'regulatory': {
                'weight': 1.0,
                'threshold': True,
                'recommendation': 'domain_reasoner',
                'priority': 'required'
            },
            'confidence': {
                'weight': 0.9,
                'threshold': 0.5,
                'operator': '<',
                'recommendation': 'domain_reasoner',
                'priority': 'high'
            },
            'range_width': {
                'weight': 0.85,
                'threshold': 1.75,
                'operator': '>',
                'recommendation': 'domain_reasoner',
                'priority': 'high'
            },
            'opportunity_size': {
                'weight': 0.7,
                'threshold': 100_000_000_000,
                'operator': '>',
                'recommendation': 'domain_reasoner',
                'priority': 'medium'
            },
            'new_market': {
                'weight': 0.75,
                'threshold': True,
                'recommendation': 'domain_reasoner',
                'priority': 'medium'
            }
        }
```

#### 2.2 Bill Quantifier 통합
**파일**: `umis_rag/agents/quantifier.py`

**추가 메서드**:
```python
# umis_rag/agents/quantifier.py

class Quantifier:
    """Bill - Quantifier Agent"""
    
    def calculate_sam_with_hybrid(
        self,
        market_definition: dict,
        method: str = 'auto'
    ) -> dict:
        """
        SAM 계산 (하이브리드 모드)
        
        Args:
            market_definition: 시장 정의
            method: 'auto', 'guestimation', 'domain_reasoner'
        
        Returns:
            {
                'phase_1': {...},  # Guestimation 결과
                'phase_2': {...},  # Domain Reasoner 결과 (if triggered)
                'recommendation': {...},
                'final_result': {...}
            }
        """
        
        # Phase 1: Guestimation (항상 실행)
        phase_1_result = self._guestimation_sam(market_definition)
        
        # Guardian 평가
        from umis_rag.guardian import GuardianMetaRAG
        guardian = GuardianMetaRAG()
        
        recommendation = guardian.recommend_methodology(
            estimate_result=phase_1_result,
            context=market_definition.get('context', {})
        )
        
        # 자동 모드 & Phase 2 권고 → Domain Reasoner 실행
        if method == 'auto' and recommendation['recommendation'] == 'domain_reasoner':
            
            print(f"\n🔄 Guardian 권고: Phase 2 진행")
            print(f"   이유: {recommendation['reason']}")
            print(f"   예상 시간: {recommendation['estimated_time']}")
            
            if recommendation['priority'] == 'required':
                print(f"   → 자동 실행 (필수)")
                phase_2_result = self._domain_reasoner_sam(market_definition, phase_1_result)
            else:
                user_confirm = input(f"\n   Phase 2를 진행하시겠습니까? (y/n): ")
                if user_confirm.lower() == 'y':
                    phase_2_result = self._domain_reasoner_sam(market_definition, phase_1_result)
                else:
                    phase_2_result = None
        
        elif method == 'domain_reasoner':
            # 명시적 Domain Reasoner 요청
            phase_2_result = self._domain_reasoner_sam(market_definition, phase_1_result)
        
        else:
            phase_2_result = None
        
        # 최종 결과
        final_result = phase_2_result if phase_2_result else phase_1_result
        
        return {
            'phase_1': phase_1_result,
            'phase_2': phase_2_result,
            'recommendation': recommendation,
            'final_result': final_result,
            'method_used': 'domain_reasoner' if phase_2_result else 'guestimation'
        }
    
    def _guestimation_sam(self, market_definition: dict) -> dict:
        """Guestimation 방식 SAM 계산"""
        # 기존 로직
        pass
    
    def _domain_reasoner_sam(
        self,
        market_definition: dict,
        phase_1_result: dict
    ) -> dict:
        """Domain Reasoner 방식 SAM 계산"""
        
        from umis_rag.methodologies.domain_reasoner import DomainReasonerEngine
        
        engine = DomainReasonerEngine()
        
        result = engine.execute(
            question=f"{market_definition['market_name']} SAM",
            domain=market_definition.get('industry', 'general'),
            geography=market_definition.get('geography', 'KR'),
            time_horizon=market_definition.get('time_horizon', '2025-2030'),
            phase_1_context=phase_1_result
        )
        
        return result
```

#### 2.3 테스트 스크립트
**파일**: `scripts/test_hybrid_guestimation.py`

```python
# scripts/test_hybrid_guestimation.py

"""
Hybrid Guestimation 테스트 스크립트
"""

import sys
sys.path.append('.')

from umis_rag.guardian import GuardianMetaRAG
from umis_rag.agents.quantifier import Quantifier

def test_guardian_recommendation():
    """Guardian 방법론 권고 테스트"""
    
    guardian = GuardianMetaRAG()
    
    # Test Case 1: 신뢰도 낮음
    result1 = guardian.recommend_methodology(
        estimate_result={
            'value': 50_000_000_000,  # 500억
            'range': (20_000_000_000, 80_000_000_000),
            'confidence': 0.3,  # 30%
            'method': 'guestimation'
        },
        context={'domain': 'general'}
    )
    
    print("Test 1: 신뢰도 30%")
    print(f"  권고: {result1['recommendation']}")
    print(f"  이유: {result1['reason']}")
    assert result1['recommendation'] == 'domain_reasoner'
    assert result1['trigger'] == 'low_confidence'
    print("  ✅ Pass\n")
    
    # Test Case 2: 큰 기회
    result2 = guardian.recommend_methodology(
        estimate_result={
            'value': 500_000_000_000,  # 5,000억
            'range': (400_000_000_000, 600_000_000_000),
            'confidence': 0.7,
            'method': 'guestimation'
        },
        context={'domain': 'general'}
    )
    
    print("Test 2: 기회 5,000억")
    print(f"  권고: {result2['recommendation']}")
    print(f"  이유: {result2['reason']}")
    assert result2['recommendation'] == 'domain_reasoner'
    assert result2['trigger'] == 'large_opportunity'
    print("  ✅ Pass\n")
    
    # Test Case 3: 규제 산업
    result3 = guardian.recommend_methodology(
        estimate_result={
            'value': 10_000_000_000,  # 100억
            'range': (8_000_000_000, 12_000_000_000),
            'confidence': 0.8,
            'method': 'guestimation'
        },
        context={'domain': 'healthcare', 'regulatory': True}
    )
    
    print("Test 3: 규제 산업 (의료)")
    print(f"  권고: {result3['recommendation']}")
    print(f"  이유: {result3['reason']}")
    assert result3['recommendation'] == 'domain_reasoner'
    assert result3['priority'] == 'required'
    print("  ✅ Pass\n")
    
    # Test Case 4: Guestimation 충분
    result4 = guardian.recommend_methodology(
        estimate_result={
            'value': 10_000_000_000,  # 100억
            'range': (8_000_000_000, 12_000_000_000),
            'confidence': 0.75,
            'method': 'guestimation'
        },
        context={'domain': 'general'}
    )
    
    print("Test 4: 신뢰도 75%, 작은 기회")
    print(f"  권고: {result4['recommendation']}")
    print(f"  이유: {result4['reason']}")
    assert result4['recommendation'] == 'guestimation_sufficient'
    print("  ✅ Pass\n")
    
    print("=" * 50)
    print("✅ All Guardian tests passed!")
    print("=" * 50)

if __name__ == '__main__':
    test_guardian_recommendation()
```

### ✅ 완료 기준
- [ ] `umis_rag/guardian/meta_rag.py`에 `recommend_methodology()` 추가
- [ ] `umis_rag/agents/quantifier.py`에 `calculate_sam_with_hybrid()` 추가
- [ ] `scripts/test_hybrid_guestimation.py` 작성 및 테스트 통과
- [ ] 4개 테스트 케이스 모두 Pass
- [ ] Git commit: "Add: Guardian Auto-Switch for Hybrid Guestimation"

### ⏱️ 예상 시간
**1주 (5-8시간 작업)**

---

## Step 3: Bill Quantifier Should/Will 확장 (2주 - Week 3-4)

### 🎯 목표
행동경제학 기반 "Should (규범) vs Will (현실)" 분석 기능 추가

### 📝 작업 항목

#### 3.1 Domain Reasoner 엔진 구현
**파일**: `umis_rag/methodologies/domain_reasoner.py` (신규)

```python
# umis_rag/methodologies/domain_reasoner.py

"""
Domain-Centric Reasoner Engine
10-Signal Stack 기반 정밀 추론
"""

from typing import Dict, List, Tuple
import yaml
from pathlib import Path

class DomainReasonerEngine:
    """10-Signal Stack 추론 엔진"""
    
    def __init__(self):
        self.methodology = self._load_methodology()
        self.signal_stack = self._initialize_signals()
    
    def _load_methodology(self):
        """방법론 YAML 로드"""
        yaml_path = Path("data/raw/umis_domain_reasoner_methodology.yaml")
        with open(yaml_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _initialize_signals(self):
        """10가지 신호 초기화"""
        return {
            's1_llm_guess': Signal1_LLMGuess(weight=0.15),
            's2_rag_consensus': Signal2_RAGConsensus(weight=0.9),
            's3_laws_ethics_physics': Signal3_Laws(weight=1.0),
            's4_behavioral_econ': Signal4_BehavioralEcon(weight=0.6),
            's5_stat_patterns': Signal5_StatPatterns(weight=0.75),
            's6_math_relations': Signal6_MathRelations(weight=1.0),
            's7_rules_of_thumb': Signal7_RulesOfThumb(weight=0.7),
            's8_time_space_bounds': Signal8_TimeSpaceBounds(weight=1.0),
            's9_case_analogies': Signal9_CaseAnalogies(weight=0.85),
            's10_industry_kpi': Signal10_IndustryKPI(weight=0.95)
        }
    
    def execute(
        self,
        question: str,
        domain: str,
        geography: str = 'KR',
        time_horizon: str = '2025-2030',
        phase_1_context: dict = None
    ) -> dict:
        """
        6단계 파이프라인 실행
        
        Args:
            question: 추정 질문
            domain: 산업/영역
            geography: 지리
            time_horizon: 시간 범위
            phase_1_context: Guestimation 결과 (선택)
        
        Returns:
            {
                'point_estimate': float,
                'range_estimate': tuple,
                'should_vs_will': {...},
                'signal_breakdown': {...},
                'evidence_table': [...],
                'verification_log': {...},
                'confidence': str
            }
        """
        
        # Step 1: 정의 고정 (s10)
        definition = self.signal_stack['s10_industry_kpi'].clarify_definition(
            question, domain
        )
        
        # Step 2: 제약 확인 (s3, s8)
        constraints = self._check_constraints(definition)
        
        # Step 3: 구조 분해
        structure = self._decompose_structure(definition)
        
        # Step 4: RAG 검색
        rag_results = self._retrieve_from_rag(definition, domain, geography)
        
        # Step 5: 융합 (우선순위 적용)
        fused_result = self._fuse_signals(rag_results, constraints, structure)
        
        # Step 6: 행동경제학 보정 (Should vs Will)
        final_result = self.signal_stack['s4_behavioral_econ'].adjust_should_vs_will(
            fused_result
        )
        
        # Step 7: 검증
        verification = self._verify(final_result, constraints)
        
        # Step 8: 리포트 생성
        report = self._generate_report(
            definition,
            final_result,
            verification,
            rag_results
        )
        
        return report
    
    def _check_constraints(self, definition):
        """s3, s8 제약 확인"""
        
        laws = self.signal_stack['s3_laws_ethics_physics'].check(definition)
        bounds = self.signal_stack['s8_time_space_bounds'].calculate_bounds(definition)
        
        return {
            'laws': laws,
            'bounds': bounds
        }
    
    # ... (나머지 메서드는 실제 구현 시 작성)


class Signal4_BehavioralEcon:
    """s4: 행동경제학 보정"""
    
    def __init__(self, weight=0.6):
        self.weight = weight
        self.biases = {
            'loss_aversion': 2.5,  # 손실 = 이득 × 2.5
            'status_quo_bias': 0.5,
            'anchoring': (0.7, 1.3),
            'hyperbolic_discounting': 0.5
        }
    
    def adjust_should_vs_will(self, fused_result: dict) -> dict:
        """
        Should (규범) vs Will (현실) 분리
        
        Args:
            fused_result: {
                'value': float,
                'range': tuple,
                'context': dict
            }
        
        Returns:
            {
                'should': {...},
                'will': {...},
                'gap': {...}
            }
        """
        
        value = fused_result['value']
        context = fused_result.get('context', {})
        
        # Should: 편향 없는 이상적 값
        should = {
            'value': value,
            'rationale': '이상적/규범적 결론 (편향 제거)',
            'assumptions': ['합리적 의사결정', '완전 정보', '시간 일관성']
        }
        
        # Will: 현실적 예측 (편향 반영)
        will_value = value
        adjustments = []
        
        # 가격 인상/변경 → 손실회피
        if context.get('price_change', False):
            will_value *= 0.4  # 60% 저항
            adjustments.append({
                'bias': 'loss_aversion',
                'factor': 0.4,
                'reason': '가격 인상 저항 (손실회피)'
            })
        
        # 현상 유지 vs 전환 → 현상유지 편향
        if context.get('requires_switch', False):
            will_value *= 0.5  # 50% 전환율
            adjustments.append({
                'bias': 'status_quo_bias',
                'factor': 0.5,
                'reason': '전환 저항 (현상유지 편향)'
            })
        
        # 시장 지배력 → 가격 결정력
        if context.get('market_power', 0) > 0.7:
            will_value *= (1 + context['market_power'] * 0.3)
            adjustments.append({
                'bias': 'market_power',
                'factor': 1.3,
                'reason': '독과점 → 가격 결정력'
            })
        
        will = {
            'value': will_value,
            'rationale': '현실적 예측 (편향 반영)',
            'adjustments': adjustments
        }
        
        # Gap 분석
        gap = {
            'absolute': should['value'] - will['value'],
            'relative': (should['value'] - will['value']) / should['value'],
            'main_drivers': [adj['bias'] for adj in adjustments]
        }
        
        return {
            'should': should,
            'will': will,
            'gap': gap,
            'signal': 's4_behavioral_econ',
            'weight': self.weight
        }
```

#### 3.2 Excel 템플릿 확장
**파일**: `umis_rag/excel/generators/market_sizing_generator.py`

**Should_vs_Will 시트 추가**:
```python
def _create_should_vs_will_sheet(self, workbook, should_vs_will_data):
    """Should vs Will 분석 시트"""
    
    sheet = workbook.create_sheet("Should_vs_Will")
    
    # 헤더
    headers = ["항목", "Should (규범적)", "Will (현실적)", "Gap (%)", "주요 원인"]
    for col, header in enumerate(headers, 1):
        cell = sheet.cell(1, col, header)
        cell.font = Font(bold=True)
        cell.fill = PatternFill(start_color="4472C4", fill_type="solid")
        cell.font = Font(color="FFFFFF", bold=True)
    
    # 데이터
    row = 2
    for item in should_vs_will_data:
        sheet.cell(row, 1, item['metric'])
        sheet.cell(row, 2, item['should'])
        sheet.cell(row, 3, item['will'])
        sheet.cell(row, 4, f"=((B{row}-C{row})/B{row})*100")  # Gap %
        sheet.cell(row, 5, item['reason'])
        row += 1
    
    # 포맷팅
    for col in [2, 3]:  # Should, Will 열
        for row in range(2, row):
            cell = sheet.cell(row, col)
            cell.number_format = '#,##0'
    
    # Gap % 포맷
    for row in range(2, row):
        cell = sheet.cell(row, 4)
        cell.number_format = '0.0"%"'
        # Gap > 20% 빨강, < 10% 초록
        if cell.value and cell.value > 20:
            cell.fill = PatternFill(start_color="FF6B6B", fill_type="solid")
        elif cell.value and cell.value < 10:
            cell.fill = PatternFill(start_color="95E1D3", fill_type="solid")
    
    return sheet
```

#### 3.3 테스트 케이스
**파일**: `scripts/test_should_vs_will.py`

```python
# scripts/test_should_vs_will.py

"""Should vs Will 분석 테스트"""

from umis_rag.methodologies.domain_reasoner import Signal4_BehavioralEcon

def test_should_vs_will():
    """행동경제학 보정 테스트"""
    
    signal = Signal4_BehavioralEcon()
    
    # Test Case: 플랫폼 수수료율
    fused_result = {
        'value': 0.075,  # 7.5%
        'range': (0.06, 0.09),
        'context': {
            'market_power': 0.8,  # 독과점
            'price_change': False,
            'requires_switch': False
        }
    }
    
    result = signal.adjust_should_vs_will(fused_result)
    
    print("=" * 50)
    print("Should vs Will 분석 테스트")
    print("=" * 50)
    
    print(f"\nShould (규범적): {result['should']['value']*100:.1f}%")
    print(f"  근거: {result['should']['rationale']}")
    
    print(f"\nWill (현실적): {result['will']['value']*100:.1f}%")
    print(f"  근거: {result['will']['rationale']}")
    print(f"  조정:")
    for adj in result['will']['adjustments']:
        print(f"    - {adj['bias']}: ×{adj['factor']} ({adj['reason']})")
    
    print(f"\nGap: {result['gap']['relative']*100:.1f}%")
    print(f"  주요 원인: {', '.join(result['gap']['main_drivers'])}")
    
    print("\n✅ Test completed")

if __name__ == '__main__':
    test_should_vs_will()
```

### ✅ 완료 기준
- [ ] `umis_rag/methodologies/domain_reasoner.py` 구현
- [ ] `Signal4_BehavioralEcon` 클래스 완성
- [ ] Excel "Should_vs_Will" 시트 추가
- [ ] 테스트 통과
- [ ] Git commit: "Add: Should vs Will Analysis (Behavioral Economics)"

### ⏱️ 예상 시간
**2주 (10-15시간 작업)**

---

## Step 4: Rachel Validator KPI Library (2주 - Week 4-5)

### 🎯 목표
KPI 정의 표준화 라이브러리 구축 (100개 목표)

### 📝 작업 항목

#### 4.1 KPI 정의 YAML 생성
**파일**: `data/raw/kpi_definitions.yaml` (신규)

```yaml
# data/raw/kpi_definitions.yaml

_meta:
  version: "1.0.0"
  created: "2025-11-04"
  total_kpis: 100
  agent: "validator"
  purpose: "산업 KPI 정의 표준화 (s10 Industry KPI Library)"

# ========================================
# Platform Business KPIs
# ========================================

platform_kpis:
  
  - kpi_id: "KPI_PLT_001"
    metric_name: "플랫폼 수수료율"
    category: "platform"
    subcategory: "commission"
    
    definition:
      korean: "플랫폼이 거래 중개에 대해 공급자로부터 받는 수수료 비율"
      english: "Platform commission rate"
    
    formula:
      numerator: "플랫폼 중개 수수료 (KRW)"
      denominator: "거래 금액 (KRW)"
      calculation: "수수료 / 거래액 × 100"
    
    unit: "%"
    typical_range: "3-20%"
    
    scope:
      includes:
        - "중개 수수료"
        - "거래 촉진 수수료"
      excludes:
        - "광고비"
        - "배달비 (배달 플랫폼)"
        - "결제 수수료"
    
    common_variations:
      - name: "총 수수료율 (광고 포함)"
        adjustment: "+ 광고비 / 거래액"
        comparability: "낮음 (분자 다름)"
      
      - name: "수수료율 (배달비 포함)"
        adjustment: "분모에 배달비 포함"
        comparability: "낮음 (분모 다름)"
    
    industry_examples:
      - industry: "음식 배달"
        value: "6-12%"
        geography: "KR"
        source: "UMIS RAG"
        note: "배달의민족 기준"
      
      - industry: "차량 공유"
        value: "20-25%"
        geography: "Global"
        source: "Uber 공시"
      
      - industry: "숙박 공유"
        value: "14-16%"
        geography: "Global"
        source: "Airbnb 공시"
    
    validation_rules:
      - rule: "분자/분모 단위 일치 (KRW/KRW)"
      - rule: "제외 항목 일치 확인"
      - rule: "지리/시기 명시"
      - rule: "정의 불일치 시 비교 금지"
    
    related_kpis:
      - "KPI_PLT_002 (Take Rate)"
      - "KPI_PLT_003 (Net Revenue Retention)"
  
  - kpi_id: "KPI_PLT_002"
    metric_name: "Take Rate"
    category: "platform"
    subcategory: "revenue"
    
    definition:
      korean: "플랫폼 총 매출 / GMV (Gross Merchandise Value)"
      english: "Platform revenue as % of GMV"
    
    formula:
      numerator: "플랫폼 총 매출 (수수료 + 광고 + 구독)"
      denominator: "GMV (총 거래액)"
      calculation: "총 매출 / GMV × 100"
    
    unit: "%"
    typical_range: "10-30%"
    
    scope:
      includes:
        - "모든 플랫폼 수익원"
        - "수수료, 광고, 구독, 기타"
      excludes:
        - "환불"
    
    industry_examples:
      - industry: "이커머스"
        value: "3-5%"
        note: "Marketplace 모델"
      
      - industry: "음식 배달"
        value: "15-20%"
        note: "수수료 + 광고"
      
      - industry: "차량 공유"
        value: "20-25%"
        note: "높은 운영비"
    
    validation_rules:
      - rule: "GMV 정의 일치 (환불 제외)"
      - rule: "매출 인식 시점 일치 (발생주의)"
    
    difference_from_commission:
      commission: "중개 수수료만"
      take_rate: "모든 수익원 포함"
      note: "Take Rate >= Commission Rate"

# ========================================
# Subscription Business KPIs
# ========================================

subscription_kpis:
  
  - kpi_id: "KPI_SUB_001"
    metric_name: "월간 해지율 (Monthly Churn Rate)"
    category: "subscription"
    subcategory: "retention"
    
    definition:
      korean: "해당 월에 해지한 고객 수 / 월초 총 고객 수"
      english: "Monthly customer churn rate"
    
    formula:
      numerator: "월간 해지 고객 수"
      denominator: "월초 총 고객 수"
      calculation: "해지 수 / 월초 고객 수 × 100"
    
    unit: "%"
    typical_range: "2-10%"
    
    scope:
      includes:
        - "자발적 해지 (voluntary)"
        - "비자발적 해지 (involuntary, 결제 실패)"
      excludes:
        - "무료 체험 해지 (trial)"
    
    common_variations:
      - name: "자발적 해지율 (Voluntary Churn)"
        adjustment: "분자에서 결제 실패 제외"
        comparability: "중간"
      
      - name: "매출 기준 해지율 (Revenue Churn)"
        adjustment: "고객 수 대신 MRR 사용"
        comparability: "낮음 (분자/분모 다름)"
    
    industry_benchmarks:
      - industry: "B2C SaaS"
        value: "5-7%"
        geography: "Global"
      
      - industry: "B2B SaaS"
        value: "2-3%"
        geography: "Global"
      
      - industry: "Consumer Subscription"
        value: "3-5%"
        geography: "KR"
        examples: "넷플릭스, 멜론"
    
    validation_rules:
      - rule: "분자/분모 기준일 일치 (월초 vs 월말)"
      - rule: "trial 제외 여부 명시"
      - rule: "voluntary vs total 구분"
    
    related_kpis:
      - "KPI_SUB_002 (Retention Rate)"
      - "KPI_SUB_003 (LTV)"

# ... (나머지 98개 KPI)
```

#### 4.2 Rachel Validator 통합
**파일**: `umis_rag/agents/validator.py`

**추가 메서드**:
```python
# umis_rag/agents/validator.py

class Validator:
    """Rachel - Validator Agent"""
    
    def __init__(self):
        self.kpi_library = self._load_kpi_library()
    
    def _load_kpi_library(self):
        """KPI 정의 라이브러리 로드"""
        import yaml
        from pathlib import Path
        
        kpi_path = Path("data/raw/kpi_definitions.yaml")
        with open(kpi_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def validate_kpi_definition(
        self,
        metric_name: str,
        provided_definition: dict
    ) -> dict:
        """
        KPI 정의 검증 (s10)
        
        Args:
            metric_name: KPI 이름
            provided_definition: {
                'numerator': str,
                'denominator': str,
                'unit': str,
                'scope': {...}
            }
        
        Returns:
            {
                'status': 'match' | 'partial_match' | 'mismatch' | 'not_found',
                'standard_definition': {...},
                'gaps': [...],
                'recommendation': str
            }
        """
        
        # KPI 검색
        kpi = self._search_kpi(metric_name)
        
        if not kpi:
            return {
                'status': 'not_found',
                'message': f"KPI '{metric_name}'가 라이브러리에 없습니다",
                'recommendation': 'manual_review',
                'create_new': True
            }
        
        # 정의 비교
        gaps = []
        
        # 1. 분자 비교
        if provided_definition.get('numerator') != kpi['formula']['numerator']:
            gaps.append({
                'field': 'numerator',
                'provided': provided_definition.get('numerator'),
                'standard': kpi['formula']['numerator'],
                'severity': 'high'
            })
        
        # 2. 분모 비교
        if provided_definition.get('denominator') != kpi['formula']['denominator']:
            gaps.append({
                'field': 'denominator',
                'provided': provided_definition.get('denominator'),
                'standard': kpi['formula']['denominator'],
                'severity': 'high'
            })
        
        # 3. 단위 비교
        if provided_definition.get('unit') != kpi['unit']:
            gaps.append({
                'field': 'unit',
                'provided': provided_definition.get('unit'),
                'standard': kpi['unit'],
                'severity': 'medium'
            })
        
        # 4. Scope 비교
        scope_gaps = self._compare_scope(
            provided_definition.get('scope', {}),
            kpi['scope']
        )
        gaps.extend(scope_gaps)
        
        # 상태 결정
        if len(gaps) == 0:
            status = 'match'
        elif any(g['severity'] == 'high' for g in gaps):
            status = 'mismatch'
        else:
            status = 'partial_match'
        
        # 권고사항
        if status == 'match':
            recommendation = '표준 정의와 일치. 비교 가능'
        elif status == 'mismatch':
            recommendation = '정의 불일치. 비교 불가 → 표준화 필요'
        else:
            recommendation = '부분 일치. 주의하여 비교'
        
        return {
            'status': status,
            'kpi_id': kpi['kpi_id'],
            'standard_definition': kpi,
            'gaps': gaps,
            'recommendation': recommendation,
            'comparability_score': 1 - (len(gaps) * 0.2)  # 0-1
        }
    
    def _search_kpi(self, metric_name: str):
        """KPI 검색 (유사도 매칭)"""
        
        # 정확한 이름 매칭
        for category in ['platform_kpis', 'subscription_kpis']:  # 모든 카테고리
            if category in self.kpi_library:
                for kpi in self.kpi_library[category]:
                    if kpi['metric_name'].lower() == metric_name.lower():
                        return kpi
        
        # 유사 이름 매칭 (향후 구현)
        # TODO: fuzzy matching
        
        return None
    
    def _compare_scope(self, provided_scope, standard_scope):
        """Scope 비교"""
        gaps = []
        
        # Includes 비교
        provided_includes = set(provided_scope.get('includes', []))
        standard_includes = set(standard_scope.get('includes', []))
        
        missing_includes = standard_includes - provided_includes
        extra_includes = provided_includes - standard_includes
        
        if missing_includes:
            gaps.append({
                'field': 'scope.includes',
                'provided': list(provided_includes),
                'standard': list(standard_includes),
                'missing': list(missing_includes),
                'severity': 'medium'
            })
        
        # Excludes 비교
        provided_excludes = set(provided_scope.get('excludes', []))
        standard_excludes = set(standard_scope.get('excludes', []))
        
        missing_excludes = standard_excludes - provided_excludes
        
        if missing_excludes:
            gaps.append({
                'field': 'scope.excludes',
                'provided': list(provided_excludes),
                'standard': list(standard_excludes),
                'missing': list(missing_excludes),
                'severity': 'high'  # 제외 항목 중요
            })
        
        return gaps
```

#### 4.3 KPI 생성 스크립트
**파일**: `scripts/build_kpi_library.py` (신규)

```python
# scripts/build_kpi_library.py

"""
KPI 정의 라이브러리 구축 스크립트
100개 KPI 목표
"""

import yaml
from pathlib import Path

def generate_kpi_library():
    """KPI 라이브러리 생성"""
    
    kpi_library = {
        '_meta': {
            'version': '1.0.0',
            'created': '2025-11-04',
            'total_kpis': 0,
            'agent': 'validator',
            'purpose': '산업 KPI 정의 표준화 (s10 Industry KPI Library)'
        }
    }
    
    # Category 1: Platform (20개)
    kpi_library['platform_kpis'] = generate_platform_kpis()
    
    # Category 2: Subscription (15개)
    kpi_library['subscription_kpis'] = generate_subscription_kpis()
    
    # Category 3: E-commerce (15개)
    kpi_library['ecommerce_kpis'] = generate_ecommerce_kpis()
    
    # Category 4: SaaS (15개)
    kpi_library['saas_kpis'] = generate_saas_kpis()
    
    # Category 5: Marketplace (10개)
    kpi_library['marketplace_kpis'] = generate_marketplace_kpis()
    
    # Category 6: Finance (10개)
    kpi_library['finance_kpis'] = generate_finance_kpis()
    
    # Category 7: Marketing (10개)
    kpi_library['marketing_kpis'] = generate_marketing_kpis()
    
    # Category 8: General (5개)
    kpi_library['general_kpis'] = generate_general_kpis()
    
    # 총 개수 계산
    total = sum(
        len(kpi_library[cat])
        for cat in kpi_library
        if cat.endswith('_kpis')
    )
    kpi_library['_meta']['total_kpis'] = total
    
    # 저장
    output_path = Path("data/raw/kpi_definitions.yaml")
    with open(output_path, 'w', encoding='utf-8') as f:
        yaml.dump(kpi_library, f, allow_unicode=True, sort_keys=False)
    
    print(f"✅ KPI 라이브러리 생성 완료: {total}개")
    print(f"   저장 위치: {output_path}")
    
    return kpi_library

def generate_platform_kpis():
    """플랫폼 KPI 20개"""
    return [
        # (이미 작성한 KPI_PLT_001, KPI_PLT_002)
        # + 18개 추가
    ]

# ... (나머지 generate 함수들)

if __name__ == '__main__':
    generate_kpi_library()
```

### ✅ 완료 기준
- [ ] `data/raw/kpi_definitions.yaml` 생성 (100개 KPI)
- [ ] `umis_rag/agents/validator.py`에 `validate_kpi_definition()` 추가
- [ ] `scripts/build_kpi_library.py` 작성 및 실행
- [ ] KPI 8개 카테고리 완성
- [ ] Git commit: "Add: KPI Definition Library (100 KPIs)"

### ⏱️ 예상 시간
**2주 (12-20시간 작업)**

---

## Step 5: Cursor 통합 & 최종 검증 (1주 - Week 5)

### 🎯 목표
사용자 경험 개선 (@ 명령어) 및 전체 시스템 통합 테스트

### 📝 작업 항목

#### 5.1 Cursor Rules 업데이트
**파일**: `.cursorrules` (기존 파일 수정)

**추가 섹션**:
```yaml
# ========================================
# PART 8: Guestimation Commands
# ========================================

guestimation_commands:
  
  "@guestimate [질문]":
    description: "UMIS Guestimation 빠른 추정"
    method: "tool:universal:guestimation"
    time: "5-30분"
    accuracy: "±50%"
    
    example:
      - "@guestimate 음악 스트리밍 시장 규모"
      - "@guestimate 코웨이 해지율"
    
    output:
      - "EST_xxx (추정치 ID)"
      - "7개 섹션 문서화"
      - "Guardian 평가"
  
  "@reasoner [질문]":
    description: "Domain-Centric Reasoner 정밀 분석"
    method: "tool:universal:domain_reasoner_10_signals"
    time: "1-4시간"
    accuracy: "±30%"
    
    example:
      - "@reasoner 시니어 케어 로봇 시장 규모"
      - "@reasoner 배달 플랫폼 수수료율"
    
    output:
      - "증거표 (Evidence Table)"
      - "검증 로그 (Verification Log)"
      - "Should vs Will"
      - "민감도 분석"
  
  "@auto [질문]":
    description: "Guardian 자동 판단 → 최적 방법론 선택"
    method: "hybrid (Phase 1 → Phase 2)"
    
    logic:
      phase_1: "Guestimation 실행"
      decision:
        - "신뢰도 >= 50% → 완료"
        - "신뢰도 < 50% → Phase 2"
      phase_2: "Domain Reasoner 실행"
    
    example:
      - "@auto 국내 OTT 시장 규모"
  
  # Agent 명령어와 결합
  "@Explorer guestimate [질문]":
    description: "Explorer가 Guestimation 사용"
    common: true
  
  "@Quantifier reasoner [질문]":
    description: "Quantifier가 Domain Reasoner 사용"
    common: true
```

#### 5.2 통합 테스트 스위트
**파일**: `scripts/test_hybrid_integration.py` (신규)

```python
# scripts/test_hybrid_integration.py

"""
Hybrid Guestimation 통합 테스트
전체 플로우 검증
"""

import sys
sys.path.append('.')

from umis_rag.guardian import GuardianMetaRAG
from umis_rag.agents.quantifier import Quantifier
from umis_rag.agents.validator import Validator

def test_end_to_end_flow():
    """E2E 테스트: Guestimation → Guardian → Domain Reasoner"""
    
    print("=" * 60)
    print("통합 테스트: 시니어 케어 로봇 시장 규모 추정")
    print("=" * 60)
    
    # 1. Quantifier 초기화
    bill = Quantifier()
    
    # 2. 시장 정의
    market_def = {
        'market_name': '시니어 케어 로봇',
        'industry': 'healthcare',
        'geography': 'KR',
        'time_horizon': '2030',
        'context': {
            'regulatory': True,  # 의료기기법
            'new_market': True   # 신규 시장
        }
    }
    
    print("\n[Step 1] Phase 1: Guestimation")
    print("-" * 60)
    
    # 3. Hybrid SAM 계산 (자동 모드)
    result = bill.calculate_sam_with_hybrid(
        market_definition=market_def,
        method='auto'
    )
    
    phase_1 = result['phase_1']
    print(f"  추정값: {phase_1['value']/1e8:.0f}억 원")
    print(f"  범위: {phase_1['range'][0]/1e8:.0f}-{phase_1['range'][1]/1e8:.0f}억")
    print(f"  신뢰도: {phase_1['confidence']*100:.0f}%")
    
    print("\n[Step 2] Guardian 평가")
    print("-" * 60)
    
    recommendation = result['recommendation']
    print(f"  권고: {recommendation['recommendation']}")
    print(f"  이유: {recommendation['reason']}")
    print(f"  우선순위: {recommendation['priority']}")
    print(f"  트리거: {recommendation['trigger']}")
    
    # 규제 산업 → Phase 2 자동 실행 확인
    assert recommendation['recommendation'] == 'domain_reasoner'
    assert recommendation['priority'] == 'required'
    assert recommendation['trigger'] == 'regulatory_industry'
    
    print("\n[Step 3] Phase 2: Domain Reasoner (자동 실행)")
    print("-" * 60)
    
    phase_2 = result['phase_2']
    if phase_2:
        print(f"  추정값: {phase_2['point_estimate']/1e8:.0f}억 원")
        print(f"  범위: {phase_2['range_estimate'][0]/1e8:.0f}-{phase_2['range_estimate'][1]/1e8:.0f}억")
        print(f"  신뢰도: {phase_2['confidence']}")
        
        print(f"\n  Should vs Will:")
        print(f"    Should: {phase_2['should_vs_will']['should']['value']/1e8:.0f}억")
        print(f"    Will: {phase_2['should_vs_will']['will']['value']/1e8:.0f}억")
        print(f"    Gap: {phase_2['should_vs_will']['gap']['relative']*100:.0f}%")
    
    print("\n[Step 4] 최종 결과")
    print("-" * 60)
    
    final = result['final_result']
    print(f"  사용 방법론: {result['method_used']}")
    print(f"  최종 추정: {final.get('point_estimate', final.get('value'))/1e8:.0f}억 원")
    
    print("\n✅ 통합 테스트 완료")
    print("=" * 60)

def test_kpi_validation():
    """KPI 정의 검증 테스트"""
    
    print("\n" + "=" * 60)
    print("KPI 정의 검증 테스트")
    print("=" * 60)
    
    rachel = Validator()
    
    # Test: 플랫폼 수수료율
    result = rachel.validate_kpi_definition(
        metric_name="플랫폼 수수료율",
        provided_definition={
            'numerator': "플랫폼 중개 수수료 (KRW)",
            'denominator': "거래 금액 (KRW)",
            'unit': "%",
            'scope': {
                'includes': ["중개 수수료"],
                'excludes': ["광고비", "배달비"]
            }
        }
    )
    
    print(f"\n상태: {result['status']}")
    print(f"비교 가능성: {result['comparability_score']*100:.0f}%")
    print(f"권고: {result['recommendation']}")
    
    if result['gaps']:
        print(f"\nGap 발견: {len(result['gaps'])}개")
        for gap in result['gaps']:
            print(f"  - {gap['field']}: {gap['severity']}")
    
    assert result['status'] == 'match'
    
    print("\n✅ KPI 검증 테스트 완료")
    print("=" * 60)

if __name__ == '__main__':
    test_end_to_end_flow()
    test_kpi_validation()
```

#### 5.3 문서화 최종 정리
**파일**: `docs/HYBRID_GUESTIMATION_GUIDE.md` (신규)

```markdown
# Hybrid Guestimation 사용 가이드

## 🎯 개요

UMIS v7.2는 2가지 추정 방법론을 제공합니다:

1. **UMIS Guestimation**: 빠른 자릿수 (5-30분, ±50%)
2. **Domain-Centric Reasoner**: 정밀 분석 (1-4시간, ±30%)

Guardian이 자동으로 적절한 방법을 권고합니다.

## 📖 사용법

### 방법 1: @ 명령어 (권장)

```bash
# 자동 판단
@auto 국내 OTT 시장 규모

# 빠른 추정
@guestimate 음악 스트리밍 시장 규모

# 정밀 분석
@reasoner 시니어 케어 로봇 시장 규모
```

### 방법 2: Agent 지정

```bash
# Explorer + Guestimation
@Explorer guestimate 구독 모델 기회 크기

# Quantifier + Domain Reasoner
@Quantifier reasoner 배달 플랫폼 수수료율
```

## 🔄 하이브리드 플로우

```
1. Phase 1: Guestimation (5-30분)
   ↓
2. Guardian 평가
   ↓
3. 신뢰도 < 50% or 기회 > 1,000억?
   Yes → Phase 2: Domain Reasoner (1-4시간)
   No → 완료
```

## 📊 출력 비교

| 항목 | Guestimation | Domain Reasoner |
|------|-------------|-----------------|
| 추정값 | ✅ | ✅ |
| 범위 | ✅ | ✅ |
| 신뢰도 | ✅ | ✅ |
| 증거표 | ❌ | ✅ |
| 검증 로그 | ❌ | ✅ |
| Should/Will | ❌ | ✅ |
| 민감도 | ❌ | ✅ |

## 🎓 예시

[상세 예시 포함...]
```

### ✅ 완료 기준
- [ ] `.cursorrules`에 @ 명령어 추가
- [ ] `scripts/test_hybrid_integration.py` 작성 및 통과
- [ ] `docs/HYBRID_GUESTIMATION_GUIDE.md` 작성
- [ ] 전체 시스템 E2E 테스트 통과
- [ ] README 최종 업데이트
- [ ] Git commit: "Add: Cursor Integration & Final Documentation"

### ⏱️ 예상 시간
**1주 (5-8시간 작업)**

---

## 파일 변경 목록

### 📝 신규 파일 (8개)

1. `data/raw/umis_domain_reasoner_methodology.yaml` ✅ (이미 작성)
2. `docs/GUESTIMATION_COMPARISON.md` ✅ (이미 작성)
3. `data/raw/kpi_definitions.yaml` (Step 4)
4. `umis_rag/methodologies/domain_reasoner.py` (Step 3)
5. `scripts/test_hybrid_guestimation.py` (Step 2)
6. `scripts/test_should_vs_will.py` (Step 3)
7. `scripts/build_kpi_library.py` (Step 4)
8. `scripts/test_hybrid_integration.py` (Step 5)
9. `docs/HYBRID_GUESTIMATION_GUIDE.md` (Step 5)
10. `dev_docs/planning/HYBRID_GUESTIMATION_INTEGRATION_PLAN.md` ✅ (이 파일)

### ✏️ 수정 파일 (7개)

1. `config/tool_registry.yaml` (Step 1)
2. `README.md` (Step 1, Step 5)
3. `umis_rag/guardian/meta_rag.py` (Step 2)
4. `umis_rag/agents/quantifier.py` (Step 2, Step 3)
5. `umis_rag/agents/validator.py` (Step 4)
6. `umis_rag/excel/generators/market_sizing_generator.py` (Step 3)
7. `.cursorrules` (Step 5)

---

## 테스트 전략

### 🧪 테스트 레벨

#### 1. 단위 테스트
- `test_guardian_recommendation()` (Step 2)
- `test_should_vs_will()` (Step 3)
- `test_kpi_validation()` (Step 5)

#### 2. 통합 테스트
- `test_hybrid_guestimation.py` (Step 2)
- `test_hybrid_integration.py` (Step 5)

#### 3. E2E 테스트
- 실제 사용 시나리오 3개 (Step 5)
  1. 신규 시장 (시니어 케어 로봇)
  2. 성숙 시장 (배달 플랫폼)
  3. 규제 산업 (의료 기기)

### ✅ 테스트 커버리지 목표
- Guardian 자동 전환: 100% (4개 조건)
- Should/Will 분석: 80%+
- KPI 검증: 80%+
- 전체 통합: E2E 3개 통과

---

## 품질 검증 기준

### 📋 Step 완료 체크리스트

각 Step 완료 시 다음을 확인:

1. **코드 품질**:
   - [ ] Lint 에러 없음
   - [ ] Type hint 추가 (Python 3.8+)
   - [ ] Docstring 작성
   - [ ] 주석 명확

2. **테스트**:
   - [ ] 단위 테스트 통과
   - [ ] 통합 테스트 통과
   - [ ] 커버리지 80%+

3. **문서화**:
   - [ ] README 업데이트
   - [ ] 예시 코드 포함
   - [ ] 사용 가이드 작성

4. **Git**:
   - [ ] Commit 메시지 명확
   - [ ] 관련 파일만 포함
   - [ ] Conflict 없음

### 🎯 최종 검증 (Step 5 완료 후)

- [ ] 모든 @ 명령어 작동
- [ ] Guardian 자동 전환 정확도 80%+
- [ ] Should/Will 분석 정확
- [ ] KPI 라이브러리 100개+
- [ ] E2E 테스트 3개 통과
- [ ] 문서화 완료
- [ ] 성능: Phase 1 < 30분, Phase 2 < 4시간

---

## 리스크 관리

### ⚠️ 주요 리스크

#### 리스크 1: Domain Reasoner 복잡성
- **내용**: 10신호 체계 구현 복잡
- **영향**: 높음 (Step 3 지연)
- **완화**: 
  - 단계적 구현 (s1-s4 먼저)
  - 핵심 신호 우선 (s2, s9, s10)
  - 나머지는 Stub으로

#### 리스크 2: KPI 라이브러리 100개 목표
- **내용**: 100개 KPI 수집 시간 소요
- **영향**: 중간 (Step 4 지연)
- **완화**:
  - MVP: 50개로 시작
  - 우선순위: Platform(20) + Subscription(15) + SaaS(15)
  - 나머지는 점진적 추가

#### 리스크 3: Guardian 자동 전환 오판
- **내용**: 부적절한 방법론 권고
- **영향**: 높음 (사용자 경험)
- **완화**:
  - 사용자 확인 단계 추가 (priority != 'required')
  - 로그 수집 → 개선
  - 테스트 케이스 확대 (10개+)

#### 리스크 4: 성능 저하
- **내용**: Domain Reasoner 4시간 초과
- **영향**: 중간 (사용성)
- **완화**:
  - RAG 검색 최적화 (k=30 → 적정값)
  - 캐싱 활용
  - 병렬 처리 (신호별)

### 🔄 리스크 모니터링
- **Week 1**: Step 1 완료 검증
- **Week 2**: Guardian 자동 전환 정확도 측정
- **Week 3**: Domain Reasoner 성능 측정
- **Week 4**: KPI 라이브러리 진척도 확인
- **Week 5**: 전체 통합 테스트 → 이슈 수정

---

## 다음 단계 (Step 1 시작)

### 📅 즉시 실행

1. **tool_registry.yaml 업데이트** (30분)
   ```bash
   # config/tool_registry.yaml 열기
   # TOOL_UNI_001, TOOL_UNI_002 추가
   # hybrid_strategy 섹션 추가
   ```

2. **README.md 업데이트** (30분)
   ```bash
   # README.md 열기
   # "Guestimation 방법론" 섹션 추가
   # 사용 예시 추가
   ```

3. **Git Commit**
   ```bash
   git add config/tool_registry.yaml README.md
   git commit -m "Add: Tool Registry - Hybrid Guestimation (TOOL_UNI_001, TOOL_UNI_002)"
   ```

4. **Step 1 완료 체크리스트 확인**

---

## 요약

| Step | 기간 | 주요 산출물 | 완료 기준 |
|------|------|-----------|----------|
| 1 | Day 1 | Tool Registry, README | 2개 도구 등록, 문서화 |
| 2 | Week 2 | Guardian 자동 전환 | 테스트 4개 Pass |
| 3 | Week 3-4 | Should/Will 분석 | Excel 시트, 테스트 |
| 4 | Week 4-5 | KPI Library 100개 | 8개 카테고리 완성 |
| 5 | Week 5 | Cursor 통합 | E2E 3개 통과 |

**총 기간**: 5주  
**총 작업 시간**: 40-60시간  
**예상 완료일**: 2025-12-09

---

**작성**: 2025-11-04  
**문서**: `dev_docs/planning/HYBRID_GUESTIMATION_INTEGRATION_PLAN.md`  
**상태**: Ready to Execute (Step 1부터 시작)

