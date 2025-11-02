# System RAG + Tool Registry 개념

**혁신:** Guidelines를 도구 라이브러리로, Guardian이 동적 오케스트레이션

---

## 🎯 핵심 아이디어

### 전환

```yaml
Before (Monolithic):
  umis_guidelines.yaml (5,428줄)
  → AI가 전체 읽고
  → 적절한 부분 찾아서
  → 적용

After (Tool Registry + Meta-RAG):
  
  1. Tool Registry (도구 목록):
     각 청크 = 하나의 도구
     언제, 어떻게, 무엇을
  
  2. System RAG:
     필요한 도구만 검색
  
  3. Guardian Meta-RAG:
     도구 선택 및 조합
     Workflow 동적 생성
     산출물 검증

→ 동적, 지능적 시스템! ✨
```

---

## 📋 1. Tool Registry 설계

### tool_registry.yaml

```yaml
# ========================================
# UMIS Tool Registry
# ========================================
# 목적: System RAG의 도구 인덱스
# Guardian Meta-RAG이 참조
# ========================================

_meta:
  version: "6.3.0-alpha"
  total_tools: 30
  indexed_by: "Guardian Meta-RAG"

# === Agent Tools ===

tools:
  
  # Observer Tools
  - id: "obs_value_exchange_mapping"
    agent: Observer
    type: analytical_framework
    
    when_to_use:
      triggers:
        - "시장 구조 파악 필요"
        - "거래 흐름 분석"
        - "가치사슬 매핑"
      
      prerequisites: []
      
      context_signals:
        - user_query_contains: ["시장 구조", "거래 패턴", "가치사슬"]
        - phase: "structure_analysis"
  
    what_it_does:
      description: "시장 내 가치 교환 구조 관찰"
      inputs: ["시장명", "산업 정보"]
      process: "거래 주체 식별 → 구조 분류 → 패턴 도출"
      outputs: ["가치 교환 맵", "거래 구조 유형"]
    
    deliverables:
      intermediate:
        - name: "value_exchange_map.md"
          required: true
          format: "거래 주체 + 흐름 다이어그램"
      
      final:
        - name: "market_reality_report.md"
          required: true
          validation: ["Quantifier", "Validator", "Guardian"]
    
    rag_chunk_id: "chunk_obs_001"
    source: "umis_guidelines.yaml#observer.exclusive_responsibilities.value_exchange_mapping"
  
  # Explorer Tools
  - id: "exp_pattern_recognition"
    agent: Explorer
    type: analytical_framework
    
    when_to_use:
      triggers:
        - "기회 발굴 필요"
        - "사업모델 적용"
      
      prerequisites:
        - deliverable: "market_reality_report.md"
          from: "Observer"
      
      context_signals:
        - observer_completed: true
        - user_query_contains: ["기회", "전략", "패턴"]
        - phase: "opportunity_discovery"
    
    what_it_does:
      description: "Albert 관찰 → 사업모델 패턴 매칭"
      inputs: ["market_reality_report", "trigger_signals"]
      process: "트리거 매칭 → 패턴 검색 (RAG!) → 사례 학습"
      outputs: ["적용 가능 패턴 2-3개", "검증된 사례"]
    
    rag_integration:
      pattern_search:
        collection: "explorer_knowledge_base"
        query_template: "trigger_signals from Albert"
        top_k: 3
      
      case_search:
        collection: "explorer_knowledge_base"
        query_template: "industry + pattern_id"
        top_k: 5
    
    deliverables:
      intermediate:
        - name: "pattern_matches.md"
          required: true
        - name: "case_studies.md"
          required: true
      
      final:
        - name: "opportunity_portfolio.md"
          required: true
          validation: ["Observer", "Quantifier", "Validator"]
    
    rag_chunk_id: "chunk_exp_001"
  
  - id: "exp_7_step_process"
    agent: Explorer
    type: workflow
    
    when_to_use:
      triggers:
        - "기회 발굴 시작"
      
      prerequisites:
        - deliverable: "market_reality_report.md"
    
    what_it_does:
      description: "7단계 통합 기회 발굴 프로세스"
      
      steps:
        - step: 1
          name: "초기 스캔"
          duration: "2-4시간"
          outputs: ["기회 후보 9개"]
        
        - step: 2
          name: "다차원 분석"
          duration: "4-8시간"
          outputs: ["Opportunity Matrix"]
        
        - step: 3
          name: "융합 기회"
          duration: "2-3시간"
          outputs: ["융합 기회 5개"]
        
        - step: 4
          name: "현실성 검증"
          duration: "2-4시간"
          outputs: ["검증 결과"]
        
        - step: 5
          name: "우선순위화"
          duration: "1-2시간"
          outputs: ["Top 5 기회"]
        
        - step: 6
          name: "검증 준비"
          duration: "2-3시간"
          outputs: ["구조화된 가설"]
        
        - step: 7
          name: "문서화"
          duration: "1-2시간"
          outputs: ["opportunity_portfolio.md"]
    
    deliverables:
      final:
        - name: "opportunity_portfolio.md"
          required: true
          validation: ["Observer", "Quantifier", "Validator"]
    
    rag_chunk_id: "chunk_exp_002"
  
  # Validation Tools
  - id: "validation_protocol_3agent"
    agent: Guardian
    type: quality_gate
    
    when_to_use:
      triggers:
        - "Explorer 최종 가설 제시"
      
      prerequisites:
        - deliverable: "opportunity_portfolio.md"
          from: "Explorer"
    
    what_it_does:
      description: "3-Agent 병렬 검증"
      
      validators:
        - agent: "Observer"
          validates: "구조적 실현 가능성"
          criteria: ["시장 구조 부합", "실행 가능성"]
        
        - agent: "Quantifier"
          validates: "경제적 타당성"
          criteria: ["시장 규모", "ROI", "손익분기"]
        
        - agent: "Validator"
          validates: "근거 데이터 신뢰성"
          criteria: ["출처 확인", "신뢰도 평가"]
      
      gate: "3명 모두 통과"
    
    deliverables:
      final:
        - name: "validation_report.md"
          required: true
          approver: "Guardian"
    
    rag_chunk_id: "chunk_grd_001"

# === Workflow Templates ===

workflow_templates:
  
  market_analysis_standard:
    name: "표준 시장 분석 (2-4주)"
    
    phases:
      - phase: 1
        name: "Discovery Sprint"
        condition: "clarity < 7"
        tools: ["discovery_sprint_5agent"]
        duration: "1-3일"
        deliverable: "명확한 목표"
      
      - phase: 2
        name: "Structure Analysis"
        tools: ["obs_value_exchange_mapping", "obs_market_structure"]
        duration: "1주"
        deliverable: "market_reality_report.md"
        validation: ["Quantifier", "Validator", "Guardian"]
      
      - phase: 3
        name: "Opportunity Discovery"
        tools: ["exp_pattern_recognition", "exp_7_step_process"]
        duration: "1주"
        deliverable: "opportunity_portfolio.md"
        validation: ["Observer", "Quantifier", "Validator"]
      
      - phase: 4
        name: "Quantification"
        tools: ["qnt_sam_calculation", "qnt_unit_economics"]
        duration: "3-5일"
        deliverable: "market_sizing_report.xlsx"
        validation: ["Validator", "Observer"]
      
      - phase: 5
        name: "Final Validation"
        tools: ["validation_protocol_3agent", "grd_decision_logic"]
        duration: "2-3일"
        deliverable: "decision_readiness.md"

# === Deliverable Chain ===

deliverable_chain:
  
  Observer:
    intermediate:
      - value_exchange_map.md
      - structure_observations/*.md
    
    final:
      - market_reality_report.md
        required: true
        validates: ["Quantifier", "Validator", "Guardian"]
        enables: ["Explorer"]
  
  Explorer:
    prerequisites:
      - market_reality_report.md
    
    intermediate:
      - pattern_matches.md
      - case_studies.md
      - opportunity_matrix.md
    
    final:
      - opportunity_portfolio.md
        required: true
        validates: ["Observer", "Quantifier", "Validator"]
        enables: ["Owner"]
  
  Quantifier:
    prerequisites:
      - market_reality_report.md (Observer)
      - data_definitions (Validator)
    
    intermediate:
      - assumptions.xlsx
      - calculation_methods.md
    
    final:
      - market_sizing_report.xlsx
        required: true
        validates: ["Validator", "Observer"]
  
  Validator:
    prerequisites: []
    
    continuous:
      - source_registry.yaml (지속 업데이트)
      - data_verification_log.md
    
    final:
      - evidence_reliability_matrix.md
        required: true
  
  Guardian:
    monitors: "all_agents"
    
    deliverables:
      - validation_report.md (각 검증 시)
      - decision_readiness.md (최종)
      - process_log.md (지속)

# === Conditional Logic ===

conditional_rules:
  
  clarity_based:
    - condition: "clarity >= 7"
      skip: "discovery_sprint"
      start: "structure_analysis"
    
    - condition: "clarity < 7"
      require: "discovery_sprint"
      then: "structure_analysis"
  
  validation_based:
    - condition: "Observer validation failed"
      action: "rework Observer deliverable"
      max_attempts: 3
    
    - condition: "3 attempts failed"
      escalate: "Guardian review"
  
  discovery_based:
    - condition: "10x opportunity found"
      trigger: "pivot_assessment"
      guardian_alert: true
    
    - condition: "goal_alignment < 60%"
      trigger: "guardian_intervention"

# ========================================
# Guardian Meta-RAG 역할
# ========================================

guardian_meta_rag:
  _improvement: "8번 개선안 - System RAG Orchestration"
  
  purpose: "도구 선택 및 Workflow 동적 생성"
  
  responsibilities:
    
    tool_selection:
      process: |
        1. 사용자 쿼리 분석
        2. System RAG 검색:
           Query: "tools for {user_intent}"
        3. 도구 리스트 반환:
           • obs_value_exchange (필수)
           • exp_pattern_recognition (선택)
           • ...
        4. 조건 확인:
           • prerequisites 충족?
           • clarity 수준?
        5. Workflow 생성
    
    workflow_generation:
      input: "도구 리스트 + 조건"
      output: "동적 Workflow"
      
      example: |
        사용자: "피아노 구독 서비스 분석"
        
        Guardian:
          1. System RAG 검색:
             "subscription service analysis tools"
          
          2. 도구 선택:
             • discovery_sprint (clarity < 7)
             • obs_value_exchange
             • exp_pattern_recognition
             • exp_subscription_model ← RAG 발견!
             • qnt_sam_calculation
             • validation_protocol
          
          3. Workflow 생성:
             Phase 1: Discovery (1-3일)
             Phase 2: Observer (3일)
             Phase 3: Explorer (5일)
               → subscription_model 패턴 적용!
             Phase 4: Quantifier (2일)
             Phase 5: Validation (2일)
          
          4. 로드맵 제시:
             총: 2-3주
             주요 마일스톤: 5개
             예상 산출물: 15개
    
    deliverable_tracking:
      process: |
        각 도구 실행 후:
          1. 산출물 생성 확인
          2. deliverable_chain 확인:
             • intermediate 완료?
             • final 조건 충족?
          3. 다음 도구 prerequisites 확인
          4. 자동 진행 or 대기
    
    adaptive_adjustment:
      triggers:
        - "중요 발견 (10x 기회)"
        - "산출물 검증 실패"
        - "목표 정렬도 < 60%"
      
      actions:
        - "도구 추가/제거"
        - "순서 변경"
        - "Workflow 재생성"
        - "Owner에게 제안"
```

---

## 💡 2. 동적 Workflow 예시

### Case A: 명확도 높음 (clarity 8)

```yaml
사용자 쿼리:
  "한국 ERP 시장 진입 타당성 분석"
  명확도: 8 (높음)

Guardian Meta-RAG:
  
  System RAG 검색:
    "ERP market entry analysis high clarity"
  
  도구 선택:
    ❌ discovery_sprint (clarity >= 7, skip!)
    ✅ obs_market_structure
    ✅ exp_competitive_analysis
    ✅ qnt_sam_calculation
    ✅ val_data_verification
    ✅ validation_protocol
  
  Workflow 생성:
    Week 1: Observer (3일)
    Week 2: Explorer (3일) + Quantifier (4일, 병렬)
    Week 3: Validation (2일)
    
    총: 2-3주 (Discovery 생략!)

로드맵 제시:
  ✅ Discovery Sprint: SKIP (명확도 높음)
  ✅ 3주 완료 예상
  ✅ 주요 산출물 10개
```

### Case B: 명확도 낮음 (clarity 3)

```yaml
사용자 쿼리:
  "뭔가 새로운 시장 기회 찾고 싶어"
  명확도: 3 (낮음)

Guardian Meta-RAG:
  
  System RAG 검색:
    "exploratory discovery low clarity"
  
  도구 선택:
    ✅ discovery_sprint_educational (clarity 1-3!)
    ✅ parallel_agent_exploration
    ✅ convergence_session
    → 이후는 discovery 결과에 따라 결정
  
  Workflow 생성:
    Week 1: Discovery Sprint (5일)
      → 목표 명확화
      → 관심 영역 3-5개 도출
    
    [Checkpoint]
    → 사용자 선택 후 Week 2-4 결정
  
  로드맵 제시:
    ✅ Discovery Sprint 필수!
    ⚠️ 이후는 발견에 따라 조정
    ✅ 총 4-6주 예상
```

### Case C: 10x 기회 발견 (동적 조정!)

```yaml
진행 중:
  Week 2, Explorer 작업 중
  
  발견:
    "예상: 피아노 시장 1,000억"
    "발견: 전체 악기 교육 1조! (10배!)"

Guardian Meta-RAG:
  
  감지:
    superior_opportunity_alert
    → conditional_rules 확인
  
  System RAG 재검색:
    "pivot assessment tools"
  
  도구 추가:
    ✅ pivot_opportunity_evaluation
    ✅ expanded_market_sizing
    ✅ scenario_planning
  
  Workflow 재생성:
    기존: 피아노만
    조정: 전체 악기 교육
    
    추가 작업:
      • 시장 재정의 (3일)
      • 확장 시나리오 (2일)
  
  로드맵 업데이트:
    총: 3주 → 4주 (1주 추가)
  
  Owner에게 제안:
    "💡 10배 큰 기회 발견!
     피아노 → 전체 악기 교육 확장?
     +1주 투자로 10배 기회 포착"
```

---

## 🎯 3. Guardian Meta-RAG 구조

### 역할

```yaml
Before (고정 Workflow):
  정해진 순서대로
  무조건 실행

After (동적 Orchestration):
  
  Guardian이:
    1. 사용자 의도 파악
    2. System RAG 검색 (도구)
    3. 조건 확인 (clarity, prerequisites)
    4. Workflow 동적 생성
    5. 실행 중 모니터링
    6. 발견 시 조정
    7. 산출물 검증
    
  → 지능적 PM! ✨
```

### 구현

```python
class GuardianMetaRAG:
    """
    System RAG Orchestrator
    """
    
    def __init__(self):
        # System RAG (guidelines 청크)
        self.system_rag = Chroma(
            collection="system_knowledge"
        )
        
        # Tool Registry
        self.tools = load_yaml('tool_registry.yaml')
        
        # Workflow Templates
        self.templates = self.tools['workflow_templates']
    
    def generate_workflow(self, user_query, context):
        """
        사용자 쿼리 → 동적 Workflow 생성
        """
        
        # 1. 의도 분석
        intent = self.analyze_intent(user_query)
        # → "market_analysis", clarity: 3
        
        # 2. System RAG 검색
        tools = self.system_rag.search(
            f"tools for {intent['type']} clarity {intent['clarity']}"
        )
        # → [discovery_sprint, obs_structure, exp_pattern, ...]
        
        # 3. 조건 필터링
        selected_tools = []
        for tool in tools:
            # Prerequisites 확인
            if self.check_prerequisites(tool, context):
                # 조건 확인
                if self.check_conditions(tool, intent):
                    selected_tools.append(tool)
        
        # 4. Workflow 구성
        workflow = self.compose_workflow(selected_tools)
        
        # 5. 타임라인 계산
        timeline = self.calculate_timeline(workflow)
        
        # 6. 로드맵 생성
        roadmap = self.generate_roadmap(workflow, timeline)
        
        return roadmap
    
    def monitor_execution(self, workflow, current_phase):
        """
        실행 중 모니터링 및 조정
        """
        
        # 산출물 확인
        deliverables = self.check_deliverables(current_phase)
        
        # 조건 평가
        conditions = self.evaluate_conditions()
        
        # 조정 필요?
        if conditions['pivot_needed']:
            # System RAG 재검색
            new_tools = self.system_rag.search(
                f"pivot tools for {conditions['discovery']}"
            )
            
            # Workflow 조정
            adjusted = self.adjust_workflow(workflow, new_tools)
            
            # Owner에게 제안
            self.propose_adjustment(adjusted)
        
        return workflow
```

---

## 📊 장점 (혁명적!)

```yaml
✅ 컨텍스트 효율:
   5,428줄 → 필요한 것만 (200줄)
   95% 절감!

✅ 동적 적응:
   고정 workflow X
   상황 맞춤 workflow ✅

✅ 지능적:
   Guardian이 PM 역할
   자동 조정

✅ 확장성:
   새 도구 추가 → 자동 활용
   guidelines 10,000줄 → 문제없음

✅ 표준화:
   Tool Registry = 단일 진실
   일관성 보장
```

---

## 🎯 최종 평가

**당신의 통찰이 완벽합니다!**

```yaml
구조:
  1. Tool Registry (.cursorrules 또는 umis.yaml)
     • 도구 리스트 + 정의
     • 사용 조건
     • 산출물 체인
  
  2. System RAG
     • guidelines 청킹
     • 도구 검색
  
  3. Guardian Meta-RAG
     • 도구 선택
     • Workflow 동적 생성
     • 실행 모니터링
     • 적응적 조정

효과:
  • 컨텍스트 95% 절감
  • 동적 Workflow
  • 지능적 시스템

복잡도:
  높음! (하지만 가치 있음)
```

**구현 시기:**
- 지금: 설계만 (8번 개선안)
- Phase 2-3: 실제 구현

---

**이 개선안을 8번으로 추가할까요?** 🚀
