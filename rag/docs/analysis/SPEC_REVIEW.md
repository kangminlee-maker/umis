# UMIS RAG 스펙 검토 및 개선안

## 🔍 UMIS v6.2 핵심 원칙 vs 현재 RAG 스펙 대조

---

## ✅ 잘 반영된 것

### 1. Single Source with Multi-Perspective ✅
```yaml
UMIS 철학: "같은 사실을 다르게 본다"
RAG 구현: agent_view별 청킹

→ 정확히 일치! ✅
```

### 2. 검증 중심 (가설과 판단에는 근거가 필요) ✅
```yaml
UMIS: "모든 주장에 근거 링크"
RAG: Graph로 검증 체인 추적

→ 잘 반영됨! ✅
```

### 3. Agent 협업 (source_id 기반) ✅
```yaml
UMIS: "Explorer → Quantifier 자연스러운 질문"
RAG: source_id로 cross-reference

→ 구현 가능! ✅
```

---

## ⚠️ 누락되거나 보완 필요한 것

### 🔴 Critical 1: 순환 패턴 감지 (Guardian 핵심!)

**UMIS v6.2 명세:**
```yaml
Guardian 자율 개입:
  circular_motion:
    threshold: "동일 주제 3회 반복"
    detection: |
      Observer → Explorer → Quantifier → Observer (1회)
      Observer → Explorer → Quantifier → Observer (2회) [Guardian 주시]
      Observer → Explorer → Quantifier → ... [Guardian 개입: "순환 패턴 감지"]
    
    intervention: |
      🔄 순환 패턴 감지
      
      관찰: Observer ↔ Explorer 간 '시장 정의'에 대해 3회 순환
      영향: 시간 소비 4시간, 진전도 5%
      
      제안:
        1. 현재 가정/제약 재검토
        2. Owner 의사결정 요청
        3. 다른 접근법 시도
```

**현재 RAG 스펙:**
```yaml
feedback_loop_system:
  iteration_1, iteration_2, iteration_3...
  
⚠️  누락: 순환 "감지" 메커니즘 없음!
⚠️  누락: 3회 임계값 없음!
⚠️  누락: 자동 개입 트리거 없음!
```

**🔧 추가 필요:**
```yaml
# umis_rag_architecture_v1.0.yaml에 추가

stewart_circular_detection:
  _umis_principle: "동일 주제 3회 반복 시 자동 개입"
  
  detection_mechanism:
    query_tracking:
      database: "SQLite"
      table: "query_history"
      schema:
        - query_id: "TEXT"
        - agent: "TEXT"
        - topic: "TEXT (LLM 추출)"
        - timestamp: "TIMESTAMP"
        - target_agent: "TEXT (협업 대상)"
        - outcome: "['approved', 'revised', 'rejected']"
    
    circular_detection:
      algorithm: |
        # 슬라이딩 윈도우로 순환 감지
        
        window = last_10_queries
        
        for i in range(len(window)-2):
          pattern = [window[i].topic, 
                     window[i+1].topic, 
                     window[i+2].topic]
          
          if is_circular(pattern):
            circular_count[pattern] += 1
            
            if circular_count[pattern] >= 3:
              trigger_stewart_intervention(pattern)
      
      is_circular_definition: |
        # LLM으로 주제 동일성 판단
        
        topic_1 = "시장 정의"
        topic_2 = "시장 경계 설정"
        
        llm_query: "이 두 주제가 본질적으로 같은가?"
        → similarity > 0.85 이면 "circular"
  
  intervention_levels:
    repetition_2:
      level: "monitoring"
      action: "로그 기록, 경고 준비"
      message: "(없음 - 내부 모니터링)"
    
    repetition_3:
      level: "nudge"
      action: "가벼운 알림"
      message: |
        💡 Guardian: "{topic}에 대해 반복 논의 중입니다.
        다른 각도로 접근해보시겠어요?"
    
    repetition_4:
      level: "review"
      action: "Owner 에스컬레이션"
      message: |
        🔄 순환 패턴 감지
        
        주제: {topic}
        반복: {agents} 간 {count}회
        소요: {time}
        
        권고: Owner 의사결정 필요
  
  rag_integration:
    track_query_topic:
      - extract: "LLM으로 쿼리 주제 추출"
      - store: "query_history 테이블"
      - monitor: "실시간 순환 감지"
    
    prevent_circular_search:
      - check: "동일 패턴 재검색 전 확인"
      - warn: "이미 2회 검색한 패턴입니다"
      - suggest: "다른 패턴 시도하시겠어요?"
```

---

### 🟠 Critical 2: 목표 정렬도 (Goal Alignment)

**UMIS v6.2 명세:**
```yaml
Guardian 모니터링:
  goal_alignment:
    target: "60% 이상 유지"
    measurement: "현재 작업이 목표에 기여하는 정도"
    
    deviation_trigger:
      threshold: "< 60%"
      intervention: |
        🎯 목표 정렬도 경고
        
        현재: 48% (기준: 60%)
        이탈 영역: "경쟁사 분석"
        
        권고:
          1. 원래 목표 재확인
          2. 현재 작업의 목표 기여도 평가
          3. 우선순위 재조정
```

**현재 RAG 스펙:**
```yaml
⚠️  완전 누락!
```

**🔧 추가 필요:**
```yaml
goal_alignment_system:
  _umis_principle: "모든 작업이 목표에 기여해야 함"
  
  goal_tracking:
    project_goal_embedding:
      when: "[PROJECT_START]"
      action: "프로젝트 목표를 벡터화"
      example: "피아노 구독 서비스의 시장 가능성 평가"
      vector: "[0.23, -0.56, ..., 0.89] (3072 dim)"
    
    query_alignment_measurement:
      for_each_query:
        - vectorize: "현재 검색 쿼리"
        - calculate: "cosine_similarity(query, project_goal)"
        - alignment_score: "0-100%"
      
      example:
        project_goal: "피아노 구독 서비스 기회"
        
        query_1: "피아노 구독 모델 검증"
        alignment: 95% ✅ (매우 관련)
        
        query_2: "바이올린 시장 경쟁 구조"
        alignment: 45% ⚠️ (이탈!)
        
        stewart_alert: "목표에서 벗어나고 있습니다"
  
  stewart_monitoring:
    continuous_tracking:
      - measure: "최근 5개 쿼리 평균 alignment"
      - threshold: "< 60%"
      - action: "목표 이탈 경고"
    
    intervention_template: |
      🎯 목표 정렬도 경고
      
      현재 평균: {avg_alignment}% (기준: 60%)
      최근 이탈 쿼리:
        - "{query_1}" (alignment: {score_1}%)
        - "{query_2}" (alignment: {score_2}%)
      
      제안:
        1. 프로젝트 목표 재확인
        2. 현재 작업의 필요성 재평가
        3. 우선순위 재조정
```

---

### 🟠 Critical 3: 점진적 명확도 진화

**UMIS v6.2 명세:**
```yaml
Adaptive Intelligence:
  clarity_evolution:
    start: "20-30% (불확실성 수용)"
    process: "Discovery → 발견 → 구체화"
    end: "80-90% (실행 가능)"
    
    stages:
      discovery: "20-30% → 50-60%"
      analysis: "50-60% → 70-80%"
      execution: "70-80% → 85-95%"
```

**현재 RAG 스펙:**
```yaml
⚠️  명확도 개념 없음!
```

**🔧 추가 필요:**
```yaml
clarity_evolution_system:
  _umis_principle: "불확실성을 수용하고 점진적으로 명확화"
  
  clarity_measurement:
    dimensions:
      - target_market: "타겟 시장 명확도"
      - value_proposition: "가치 제안 명확도"
      - business_model: "사업 모델 명확도"
      - execution_path: "실행 경로 명확도"
    
    calculation:
      each_dimension: "0-100%"
      overall_clarity: "평균값"
  
  rag_adaptation_by_clarity:
    
    low_clarity_20_40:
      name: "탐색 단계"
      
      rag_strategy:
        chunking: "pattern (큰 청크, 넓은 맥락)"
        top_k: 10  # 많이 검색
        diversity: "high (MMR 사용)"
        query_type: "broad (넓은 쿼리)"
      
      example:
        clarity: 25%
        query: "음악 관련 사업 기회" (넓음)
        results: 다양한 패턴 10개
        purpose: "가능성 탐색"
    
    medium_clarity_40_70:
      name: "분석 단계"
      
      rag_strategy:
        chunking: "section (중간 청크)"
        top_k: 5
        diversity: "medium"
        query_type: "focused"
      
      example:
        clarity: 55%
        query: "음악 구독 서비스 패턴" (구체)
        results: subscription_model 중심
        purpose: "패턴 검증"
    
    high_clarity_70_90:
      name: "실행 단계"
      
      rag_strategy:
        chunking: "case (작은 청크, 정밀)"
        top_k: 3
        diversity: "low (유사도 우선)"
        query_type: "precise"
      
      example:
        clarity: 85%
        query: "Spotify 프리미엄 전환율 벤치마크"
        results: 정확한 사례 1-2개
        purpose: "실행 계획"
  
  stewart_clarity_monitoring:
    track_clarity_progress:
      initial: "프로젝트 시작 시 명확도 측정"
      每_checkpoint: "각 체크포인트마다 재측정"
      expected_growth: "+10-20% per phase"
    
    alert_conditions:
      stagnation: "3개 쿼리 동안 명확도 변화 < 5%"
      regression: "명확도 감소"
      too_fast: "1회 쿼리로 +40% (과신 위험)"
```

---

### 🟠 Critical 4: 상태 기계 통합

**UMIS v6.2 명세:**
```yaml
information_flow_state_machine:
  states:
    - project_start
    - discovery
    - data_preparation
    - structure_analysis
    - opportunity_discovery
    - quantification
    - synthesis
    - decision
  
  각 상태마다:
    - active_agents
    - outputs
    - quality_gate
    - next_state
```

**현재 RAG 스펙:**
```yaml
⚠️  상태 개념 없음!
⚠️  각 상태별 RAG 전략 없음!
```

**🔧 추가 필요:**
```yaml
state_aware_rag:
  _umis_principle: "프로젝트 상태에 따라 RAG 전략 달라짐"
  
  state_specific_retrieval:
    
    discovery_state:
      active_agents: ["all_parallel"]
      
      albert_rag:
        focus: "넓은 시장 스캔"
        chunking: "macro"
        query_style: "broad"
        top_k: 20
      
      steve_rag:
        focus: "다양한 패턴 탐색"
        chunking: "pattern"
        diversity: "maximum"
        top_k: 15
    
    structure_analysis_state:
      active_agents: ["albert"]
      support_available: ["bill", "rachel"]
      
      albert_rag:
        focus: "구조 패턴 정밀 분석"
        chunking: "meso"
        query_style: "focused"
        top_k: 5
      
      bill_rachel_ready:
        mode: "on_demand"
        response: "Observer 질문 시 즉시 검색"
    
    opportunity_discovery_state:
      active_agents: ["steve"]
      
      steve_rag:
        focus: "패턴 매칭 + 사례 학습"
        chunking: "case"
        mandatory_validation: true
        
        multi_stage_required:
          stage_1: "패턴 매칭"
          stage_2: "사례 검색"
          stage_3: "검증 프레임워크"
          stage_4: "Quantifier 협업"
          stage_5: "Validator 협업"
  
  state_transitions:
    trigger_by_quality_gate:
      - from: "structure_analysis"
        to: "opportunity_discovery"
        condition: "Observer 결론 + 3명 검증 통과"
        
        rag_check:
          graph_query: |
            MATCH (a:ObserverConclusion)
                  -[:VERIFIED_BY]->(v:Verification)
            WHERE v.validators = ['bill', 'rachel', 'stewart']
            RETURN count(v) >= 3
      
      - from: "opportunity_discovery"
        to: "quantification"
        condition: "Explorer 가설 + 3명 검증 통과"
        
        rag_check:
          graph_query: |
            MATCH (s:ExplorerHypothesis)
                  -[:VERIFIED_BY]->(v:Validation)
            WHERE v.validators IN ['albert', 'bill', 'rachel']
            RETURN count(DISTINCT v.validator) >= 3
```

---

### 🟡 Important 5: 자연스러운 협업 vs 의무 검증 구분

**UMIS v6.2 명세:**
```yaml
이중 구조:
  
  일상 지원 (자연스러움):
    - 언제든 질문 가능
    - 복잡한 프로토콜 없음
    - "Quantifier, 이 시장 규모는?" (간단)
  
  의무 검증 (엄격함):
    - 4개 체크포인트에서만
    - 필수 validators 지정
    - 3명 모두 통과 필요
```

**현재 RAG 스펙:**
```yaml
cross_agent_collaboration:
  workflow: ...
  
⚠️  "의무" vs "선택" 구분 없음!
⚠️  체크포인트 개념 없음!
```

**🔧 추가 필요:**
```yaml
collaboration_modes:
  _umis_dua_structure: "일상 지원 + 의무 검증"
  
  mode_1_daily_support:
    type: "optional"
    trigger: "자유롭게 (언제든)"
    protocol: "간단 (자연스러운 질문)"
    
    implementation:
      steve_asks_bill:
        method: "직접 retriever 호출"
        filter: "source_id={현재 사례}"
        no_formality: true
      
      code_example: |
        # Explorer 작업 중
        bill_data = steve.ask_bill(
          source_id=current_case.source_id
        )
        # → Quantifier retriever로 즉시 검색
        # → 간단!
  
  mode_2_mandatory_validation:
    type: "required"
    trigger: "4개 체크포인트에서만"
    protocol: "엄격 (전체 검증 체인)"
    
    checkpoints:
      checkpoint_1:
        phase: "Observer 구조 분석 완료"
        mandatory_validators: ["bill", "rachel", "stewart"]
        
        implementation:
          trigger_condition: "albert.complete_analysis()"
          
          validation_process:
            - stewart_initiate: "검증 요청 자동 발행"
            - bill_search: "Observer 결론의 정량 근거 검색"
            - rachel_search: "Observer 데이터의 출처 검색"
            - stewart_search: "검증 규칙 검색"
            
            - graph_check: |
                MATCH (a:ObserverConclusion)
                      -[:REQUIRES_VALIDATION]->(v1:QuantifierCheck),
                      (a)-[:REQUIRES_VALIDATION]->(v2:ValidatorCheck),
                      (a)-[:REQUIRES_VALIDATION]->(v3:GuardianCheck)
                WHERE v1.passed AND v2.passed AND v3.passed
                RETURN count(*) = 3
          
          pass_criteria: "3명 모두 통과"
          fail_action: "Observer 재작업 요청"
      
      checkpoint_2:
        phase: "Explorer 가설 생성 완료"
        mandatory_validators: ["albert", "bill", "rachel"]
        # ... 동일 패턴
```

---

### 🟡 Important 6: 10x 기회 감지

**UMIS v6.2 명세:**
```yaml
Guardian 개입:
  superior_opportunity:
    signal: "10x 이상 가치 차이 기회 발견"
    action: "즉시 피벗 검토 제안"
```

**현재 RAG 스펙:**
```yaml
⚠️  기회 가치 비교 개념 없음!
```

**🔧 추가 필요:**
```yaml
opportunity_value_comparison:
  _umis_principle: "더 큰 기회 발견 시 피벗"
  
  value_estimation:
    when_steve_finds_opportunity:
      - estimate: "Quantifier에게 시장 규모 계산"
      - compare: "현재 목표 vs 새 기회"
      - ratio: "value_new / value_current"
    
    10x_detection:
      threshold: "ratio >= 10"
      
      stewart_intervention:
        trigger: "자동 (즉시)"
        message: |
          💡 주요 기회 발견!
          
          새 기회: {new_opportunity}
          예상 규모: {new_value}
          현재 목표: {current_value}
          비율: {ratio}x
          
          피벗 검토 권장:
            1. 기존 투자 vs 기회비용
            2. 실현 가능성 비교
            3. Owner 의사결정
      
      owner_escalation: true
  
  graph_tracking:
    create_node:
      label: "OpportunityComparison"
      properties:
        - current_opportunity
        - new_opportunity
        - value_ratio
        - stewart_recommendation
        - owner_decision: "null (대기 중)"
```

---

### 🟢 Nice to Have 7: Validator의 창의적 소싱

**UMIS v6.2 명세:**
```yaml
Validator 특성:
  creative_sourcing:
    - "전문가 용어로 찾을 수 없는 데이터 발굴"
    - "사용자 관점 검색으로 3배 더 많은 정보"
    - "다양한 각도에서 교차 검증"
  
  principle: "사용자 관점에서 검색어를 확장하여 정보의 사각지대 제거"
```

**현재 RAG 스펙:**
```yaml
rachel_retriever:
  search_by_source: ...
  
⚠️  "창의적 소싱" 개념 없음!
```

**🔧 추가 필요:**
```yaml
rachel_creative_sourcing:
  _umis_principle: "사용자 관점 검색어 확장"
  
  query_expansion:
    when_standard_search_insufficient:
      - standard_query: "낚시인구 통계"
      - standard_result: "750만명 (정부 통계)"
      
      - creative_expansion:
          - perspective_1: "낚시 장비 판매 데이터"
          - perspective_2: "낚시터 방문객 수"
          - perspective_3: "낚시 커뮤니티 회원 수"
          - perspective_4: "낚시 라이센스 발급 수"
      
      - cross_validation:
          - 4개 관점 데이터 수집
          - 범위 확인: "500만 ~ 1,000만"
          - 정의 조정: "낚시인구 = 연 1회 이상"
      
      - result: "3배 더 많은 데이터 포인트"
  
  rag_implementation:
    multi_query_search:
      - primary: "공식 통계 검색"
      - expansion: "LLM으로 5개 대안 쿼리 생성"
      - parallel: "6개 쿼리 동시 검색"
      - fusion: "결과 통합 및 교차 검증"
    
    llm_query_generation:
      prompt: |
        데이터: "낚시인구"
        공식 검색: "낚시인구 통계" → 750만 (1개 소스)
        
        사용자가 실제로 관심있는 것:
        - 얼마나 자주 낚시하는가?
        - 얼마나 돈을 쓰는가?
        - 어떤 장비를 사는가?
        
        이를 찾기 위한 5개 대안 검색어를 생성하세요.
      
      output:
        - "낚시 장비 연간 판매액"
        - "낚시터 이용객 통계"
        - "낚시 커뮤니티 활성 사용자"
        - "낚시 라이센스 발급 현황"
        - "낚시 관련 온라인 검색량"
```

---

### 🟢 Nice to Have 8: Discovery Sprint 적응형 전략

**UMIS v6.2 명세:**
```yaml
Discovery Sprint:
  routing:
    fast_track:
      condition: "명확도 >= 7"
      duration: "2-4시간"
    
    full_sprint:
      condition: "명확도 < 7"
      duration: "1-3일"
      activities: "5명 병렬 탐색"
```

**현재 RAG 스펙:**
```yaml
⚠️  Discovery 특화 전략 없음!
```

**🔧 추가 필요:**
```yaml
discovery_sprint_rag:
  _umis_principle: "명확도에 따라 탐색 전략 다름"
  
  fast_track_mode:
    condition: "명확도 >= 70%"
    duration: "2-4시간"
    
    rag_strategy:
      albert:
        queries: 3  # 적게
        chunking: "meso"
        depth: "medium"
      
      steve:
        queries: 2
        chunking: "section"
        focus: "검증"
      
      parallel: false  # 순차 실행
  
  full_sprint_mode:
    condition: "명확도 < 70%"
    duration: "1-3일"
    
    rag_strategy:
      all_agents:
        queries: 10-15  # 많이
        chunking: ["macro", "pattern"]  # 큰 청크
        depth: "broad"
      
      parallel: true  # 5명 동시 탐색
      
      convergence:
        after: "4-6시간"
        stewart_role: |
          5개 agent의 발견 통합:
          - Vector: 5명의 발견 유사도 계산
          - Graph: 5명의 발견 간 관계 찾기
          - Synthesis: 공통점 추출 → 방향성
```

---

## 📊 추가/수정/삭제 요약

### ✅ 추가 필요 (Critical)

| 항목 | UMIS 원칙 | 현재 상태 | 추가 내용 | 우선순위 |
|------|-----------|-----------|-----------|----------|
| **순환 감지** | 3회 반복 자동 개입 | 없음 | query_history + 감지 알고리즘 | 🔴 P0 |
| **목표 정렬도** | 60% 이상 유지 | 없음 | goal embedding + alignment 측정 | 🔴 P0 |
| **명확도 진화** | 20-30% → 80-90% | 없음 | clarity tracking + adaptive RAG | 🟠 P1 |
| **상태 기계** | 7개 상태별 전략 | 없음 | state-aware retrieval | 🟠 P1 |
| **10x 감지** | 큰 기회 자동 알림 | 없음 | value comparison + escalation | 🟡 P2 |
| **창의적 소싱** | 5개 관점 확장 | 없음 | multi-query expansion | 🟡 P2 |

### 🔄 수정 필요

| 항목 | 현재 | 수정 후 | 이유 |
|------|------|---------|------|
| **feedback_loop** | 단순 반복 | + 순환 감지 | UMIS 필수 기능 |
| **stewart_validation** | 3단계만 | + 순환/목표 모니터링 | Guardian 역할 불완전 |
| **query_refinement** | 품질만 | + 정렬도/명확도 | UMIS 철학 반영 |

### ❌ 삭제 가능

```yaml
reinforcement_learning:
  _type: "optional"
  
→ 우선순위 낮음
→ P3로 하향 (나중에)
→ 순환 감지/목표 정렬이 더 중요!
```

---

## 🎯 개선된 우선순위

### Phase 2A: Knowledge Graph (Week 1) ⭐⭐⭐⭐⭐

**유지 + 추가:**
- ✅ 패턴 간 관계 (기존)
- ✅ 검증 체인 (기존)
- 🆕 상태 기계 통합
- 🆕 순환 패턴 감지용 쿼리

### Phase 2B: Guardian Meta-RAG (Week 2) ⭐⭐⭐⭐⭐

**유지 + 추가:**
- ✅ 3단계 검증 (기존)
- ✅ 품질 패턴 (기존)
- 🆕 순환 패턴 감지 시스템 ← UMIS 핵심!
- 🆕 목표 정렬도 모니터링 ← UMIS 핵심!
- 🆕 10x 기회 자동 감지

### Phase 2C: Adaptive RAG (Week 3) ⭐⭐⭐⭐

**수정:**
- ✅ Query refinement (유지)
- ✅ Weighted retrieval (유지)
- 🔄 명확도 기반 적응 (추가) ← UMIS 핵심!
- 🔄 상태별 전략 (추가)
- ❌ 강화학습 (하향 → P3)

---

## 💡 가장 Critical한 누락: Guardian의 2가지 핵심 역할

### 1. 순환 패턴 감지

```python
# 현재 스펙에 없는 것!

class GuardianCircularDetector:
    """
    UMIS의 핵심: 3회 반복 자동 감지
    """
    
    def detect_circular_pattern(self):
        # 최근 10개 쿼리 분석
        recent_queries = self.get_recent_queries(10)
        
        # 주제 추출 (LLM)
        topics = [self.extract_topic(q) for q in recent_queries]
        
        # 순환 패턴 찾기
        for i in range(len(topics)-2):
            pattern = topics[i:i+3]
            
            if self.is_circular(pattern):
                # 3회 감지!
                return {
                    "circular": True,
                    "topic": pattern[0],
                    "agents": self.extract_agents(pattern),
                    "count": 3,
                    "intervention": "REQUIRED"
                }
        
        return {"circular": False}
    
    def is_circular(self, pattern: List[str]) -> bool:
        """
        LLM으로 주제 동일성 판단
        
        ["시장 정의", "시장 경계", "타겟 시장"]
        → 본질적으로 같은 주제? → True
        """
        prompt = f"""
        다음 3개 주제가 본질적으로 같은 것인가?
        1. {pattern[0]}
        2. {pattern[1]}
        3. {pattern[2]}
        
        본질적으로 같다 = 같은 문제를 다르게 표현
        다르다 = 서로 다른 문제
        """
        
        result = llm.invoke(prompt)
        return "같다" in result
```

### 2. 목표 정렬도 모니터링

```python
# 현재 스펙에 없는 것!

class GuardianGoalAlignmentMonitor:
    """
    UMIS의 핵심: 목표 이탈 자동 감지
    """
    
    def __init__(self, project_goal: str):
        # 프로젝트 목표를 벡터화
        self.goal_vector = embeddings.embed_query(project_goal)
    
    def measure_alignment(self, current_query: str) -> float:
        """
        현재 쿼리가 목표와 얼마나 정렬되었나?
        """
        query_vector = embeddings.embed_query(current_query)
        
        similarity = cosine_similarity(
            self.goal_vector,
            query_vector
        )
        
        # 0-1 → 0-100%
        alignment_score = similarity * 100
        
        return alignment_score
    
    def monitor_continuous(self):
        """
        최근 5개 쿼리 평균 정렬도
        """
        recent_queries = self.get_recent_queries(5)
        alignments = [
            self.measure_alignment(q) 
            for q in recent_queries
        ]
        
        avg_alignment = sum(alignments) / len(alignments)
        
        if avg_alignment < 60:
            # 목표 이탈!
            return {
                "alert": True,
                "avg_alignment": avg_alignment,
                "threshold": 60,
                "intervention": "REQUIRED"
            }
        
        return {"alert": False}
```

---

## 🚀 최종 권장 사항

### 반드시 추가해야 할 것 (P0)

1. **순환 패턴 감지 시스템**
   - UMIS의 핵심 차별점
   - Guardian 역할의 본질
   - 없으면 UMIS가 아님

2. **목표 정렬도 모니터링**
   - UMIS의 "목표 지향" 보장
   - 작업 효율성 핵심
   - Guardian의 가이드 역할

### 꼭 추가하면 좋을 것 (P1)

3. **명확도 진화 추적**
   - UMIS의 "Adaptive" 구현
   - RAG 전략 자동 조정

4. **상태 기계 통합**
   - 체계적 프로세스 보장
   - 각 단계별 최적 RAG

### 나중에 추가 (P2)

5. 10x 기회 감지
6. 창의적 소싱

---

## 결론

**현재 RAG 스펙 완성도:**
- 기술적 구현: 90% ✅
- UMIS 철학 반영: 60% ⚠️

**누락된 핵심:**
- Guardian의 2가지 감시 역할
  - 순환 감지
  - 목표 정렬
  
→ 이 2가지 없으면 "UMIS RAG"이 아님!
→ 반드시 추가 필요!

다음 스펙 업데이트에 반영하시겠습니까?

