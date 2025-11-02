# UMIS RAG 상세 작업 리스트

**접근법:** Memory-Augmented RAG Hybrid  
**기간:** 10일 (집중 개발)  
**목표:** UMIS 핵심 80% 구현 + 실전 사용 가능

---

## 📅 Day 1: Hot-Reload 개발 환경 (월요일)

**목표:** YAML 수정 → 2초 → 자동 반영  
**시간:** 8시간  
**중요도:** 🔴 P0 (개발 생산성 10배)

### Task 1.1: dev_watcher.py 완성 (3시간)

```yaml
□ 1.1.1 watchdog 통합 테스트 (30분)
  - watchdog.observers.Observer 설정
  - FileSystemEventHandler 구현
  - data/raw/ 디렉토리 감시 시작
  - 파일 변경 이벤트 수신 확인
  
  검증: YAML 저장 시 이벤트 출력됨

□ 1.1.2 중복 이벤트 필터링 (30분)
  - last_modified dict 구현
  - 1초 내 중복 이벤트 무시
  - YAML 파일만 필터링 (.yaml, .yml)
  - UMIS 파일만 처리 (business_model, disruption)
  
  검증: 한 번 저장 → 한 번만 처리

□ 1.1.3 증분 업데이트 로직 (1.5시간)
  - 변경된 파일 감지
  - 해당 청크만 재생성
  - Chroma.delete(where={"source_file": ...})
  - Chroma.add_documents(new_chunks)
  
  검증: business_model만 수정 → 31개만 업데이트

□ 1.1.4 에러 핸들링 (30분)
  - try-except로 안전하게
  - 에러 시 계속 감시 (중단 안 됨)
  - 에러 로그 출력
  - 복구 가능하게
  
  검증: 잘못된 YAML → 에러 출력, 계속 작동

□ 1.1.5 UI 개선 (30분)
  - Rich로 예쁘게 출력
  - 진행 상황 표시
  - 통계 정보 (업데이트 횟수)
  
  검증: 보기 좋은 출력
```

### Task 1.2: Makefile 완성 (1시간)

```yaml
□ 1.2.1 make dev 명령 (20분)
  - dev_watcher.py 백그라운드 실행
  - 시작 메시지 출력
  
  검증: make dev → Watcher 실행됨

□ 1.2.2 make dev-stop 명령 (10분)
  - pkill로 Watcher 중단
  - 안전한 종료
  
  검증: make dev-stop → 프로세스 종료

□ 1.2.3 기타 명령 검증 (30분)
  - make rebuild (전체 재구축)
  - make query QUERY="..." (빠른 검색)
  - make stats (통계)
  - make clean (정리)
  
  검증: 모든 명령 작동
```

### Task 1.3: 실전 테스트 및 안정화 (2시간)

```yaml
□ 1.3.1 실제 YAML 수정 테스트 (1시간)
  - 10가지 수정 시나리오
    - 텍스트 추가
    - 데이터 수정
    - 섹션 추가
    - 주석 변경
    - ...
  - 각 케이스 자동 반영 확인
  
  검증: 모든 수정 2초 내 반영

□ 1.3.2 동시 파일 수정 (30분)
  - business_model + disruption 동시 수정
  - 두 파일 모두 자동 반영
  - 순서 상관없이 작동
  
  검증: 동시 수정 처리됨

□ 1.3.3 버그 수정 및 최적화 (30분)
  - 발견된 버그 수정
  - 성능 최적화
  - 메모리 누수 확인
  
  검증: 1시간 연속 작동 안정
```

### Task 1.4: 문서화 (1시간)

```yaml
□ 1.4.1 사용 가이드 작성 (30분)
  - HOT_RELOAD_GUIDE.md
  - 명령어 설명
  - 트러블슈팅
  
□ 1.4.2 데모 영상/스크린샷 (30분)
  - YAML 수정 → 자동 반영 캡처
  - README에 추가
```

### Day 1 완료 기준

```yaml
✅ make dev 작동
✅ YAML 저장 → 2초 → 인덱스 업데이트
✅ 에러 시에도 계속 작동
✅ 10가지 수정 케이스 모두 통과
✅ 문서 완성

→ 개발 생산성 10배 확보! ⚡
```

---

## 📅 Day 2-3: Knowledge Graph 기본 (화-수요일)

**목표:** 패턴 간 관계 표현 + 검증 체인 기초  
**시간:** 16시간 (2일)  
**중요도:** 🔴 P0 (UMIS 핵심 가치)

### Task 2.1: Neo4j 설정 (4시간, Day 2 오전)

```yaml
□ 2.1.1 Neo4j Docker 설치 (1시간)
  - docker pull neo4j:5-community
  - docker run 설정
    - 포트: 7474 (UI), 7687 (Bolt)
    - 인증: neo4j/umis_rag_2024
  - 브라우저 접속 확인 (localhost:7474)
  
  검증: Neo4j UI 로그인 성공

□ 2.1.2 Python driver 설정 (1시간)
  - pip install neo4j
  - 연결 테스트
  - 간단한 쿼리 실행
    CREATE (n:Test {name: 'test'}) RETURN n
  
  검증: Python에서 Neo4j 연결됨

□ 2.1.3 기본 스키마 설계 (2시간)
  - umis_rag/graph/schema.py 작성
  
  노드 타입:
    - Pattern (패턴)
    - Case (사례)
    - Query (쿼리 메모리!) ← 신규
    - ProjectGoal (프로젝트 목표) ← 신규
  
  관계 타입:
    - COMBINES_WITH (패턴 조합)
    - COUNTERS (대항)
    - SIMILAR_TO (유사성) ← 신규
    - ALIGNS_WITH (정렬) ← 신규
  
  검증: 스키마 코드 작성 완료
```

### Task 2.2: 패턴 관계 데이터 (6시간, Day 2 오후 + Day 3 오전)

```yaml
□ 2.2.1 pattern_relationships.yaml 작성 (3시간)
  
  COMBINES_WITH (30개):
    - platform + subscription: "Amazon Prime"
    - subscription + d2c: "Dollar Shave Club"
    - platform + freemium: "Spotify"
    - low_end + channel: "쿠팡"
    - experience + price: "카카오뱅크"
    - ...
    
  각 관계마다:
    - synergy: "조합 시너지"
    - example: "성공 사례"
    - success_rate: 0.8
    - mechanism: "작동 원리"
  
  검증: 30개 관계 정의 완료

□ 2.2.2 COUNTERS 관계 (1시간)
  
  10개 대항 관계:
    - low_end_disruption → premium_trap
    - channel_disruption → middleman_dependency
    - experience_disruption → legacy_system_lock
    - ...
  
  검증: 10개 정의 완료

□ 2.2.3 선행 조건 관계 (1시간)
  
  PREREQUISITE (5개):
    - platform → network_effect
    - subscription → recurring_value
    - ...
  
  검증: 5개 정의 완료

□ 2.2.4 검증 및 조정 (1시간)
  - YAML 문법 확인
  - 관계 논리 검증
  - 예시 사례 확인
```

### Task 2.3: Graph import 및 검증 (6시간, Day 3)

```yaml
□ 2.3.1 Pattern 노드 생성 (2시간)
  - umis_rag/graph/builder.py 작성
  - 12개 패턴을 노드로
    - id: "platform_business_model"
    - name: "플랫폼 사업모델"
    - type: "business_model"
  
  Cypher:
    MERGE (p:Pattern {id: 'platform_business_model'})
    SET p.name = '플랫폼 사업모델',
        p.type = 'business_model'
  
  검증: Neo4j UI에서 12개 노드 확인

□ 2.3.2 관계 생성 (2시간)
  - pattern_relationships.yaml 읽기
  - 각 관계를 Cypher로 변환
  - Graph에 생성
  
  Cypher:
    MATCH (p1:Pattern {id: 'platform_business_model'})
    MATCH (p2:Pattern {id: 'subscription_model'})
    MERGE (p1)-[:COMBINES_WITH {
      synergy: '충성도 + 안정수익',
      example: 'Amazon Prime',
      success_rate: 0.8
    }]->(p2)
  
  검증: 45개 관계 생성 확인

□ 2.3.3 쿼리 테스트 (1.5시간)
  - 패턴 조합 검색
    MATCH (p1)-[r:COMBINES_WITH]->(p2)
    WHERE p1.id = 'platform_business_model'
    RETURN p2.id, r.synergy, r.example
  
  - 대항 관계 검색
    MATCH (d:Pattern {type: 'disruption'})
          -[r:COUNTERS]->()
    RETURN d, r
  
  검증: 쿼리 결과 정확

□ 2.3.4 Python 통합 (30분)
  - umis_rag/graph/query.py
  - find_pattern_combinations()
  - find_counter_strategies()
  
  검증: Python에서 쿼리 작동
```

### Day 2-3 완료 기준

```yaml
✅ Neo4j 실행 중
✅ 12개 Pattern 노드
✅ 45개 관계 (COMBINES_WITH, COUNTERS, PREREQUISITE)
✅ Python에서 Graph 쿼리 가능
✅ "플랫폼 + 구독" → Amazon Prime 발견

→ Knowledge Graph 기본 완성! 🔗
```

---

## 📅 Day 4: Memory-Augmented 순환 감지 (목요일)

**목표:** RAG로 순환 패턴 자동 감지  
**시간:** 8시간  
**중요도:** 🔴 P0 (UMIS 핵심 #1)

### Task 4.1: Query Memory Index (3시간)

```yaml
□ 4.1.1 QueryMemory 컬렉션 생성 (1시간)
  - umis_rag/memory/query_memory.py
  
  class QueryMemoryRAG:
      def __init__(self):
          self.index = Chroma(
              collection_name="query_memory",
              embedding_function=embeddings
          )
  
  - record_query() 메서드
  - search_similar_queries() 메서드
  
  검증: 쿼리 저장 및 검색 작동

□ 4.1.2 자동 메타데이터 추출 (1.5시간)
  - LLM으로 주제 추출 (캐싱!)
    
    def extract_topic(query: str) -> str:
        # 캐시 확인 (중복 호출 방지)
        if query in topic_cache:
            return topic_cache[query]
        
        # LLM 호출
        result = llm.invoke(f"주제 추출: {query}")
        topic_cache[query] = result
        return result
  
  - intent 분류 (탐색/분석/검증)
  - agent 자동 태깅
  
  검증: 메타데이터 자동 생성

□ 4.1.3 시간 기반 필터링 (30분)
  - 최근 N개만 검색
  - 프로젝트별 격리
  - timestamp 인덱싱
  
  검증: 최근 쿼리만 검색됨
```

### Task 4.2: Hybrid 순환 감지 엔진 (3시간)

```yaml
□ 4.2.1 Memory-RAG 기반 후보 검색 (1.5시간)
  
  def detect_circular_candidates(current_query: str):
      # 유사 쿼리 검색
      similar = query_memory.search(
          current_query,
          k=10,
          filter={"timestamp": {"$gte": recent_time}}
      )
      
      # 매우 유사한 것만 (distance < 0.3)
      candidates = [
          doc for doc, dist in similar
          if dist < 0.3
      ]
      
      if len(candidates) < 3:
          return {"circular": False}  # 빠른 종료
      
      return {"candidates": candidates}
  
  검증: 유사 쿼리 3개 이상 찾기

□ 4.2.2 LLM 정밀 검증 (1시간)
  
  def verify_circular_with_llm(candidates):
      # 3개 후보 분석
      prompt = f"""
      다음 3개 쿼리가 본질적으로 같은 문제를 반복하는가?
      
      1. {candidates[0]}
      2. {candidates[1]}
      3. {candidates[2]}
      
      판단 기준:
      - 같은 문제를 다른 표현 = Yes (순환)
      - 같은 주제의 다른 측면 = No (진전)
      
      답: Yes/No + 이유
      """
      
      result = llm.invoke(prompt)
      
      return {
          "circular": "yes" in result.lower(),
          "reason": result
      }
  
  검증: 순환/비순환 정확히 구분

□ 4.2.3 통합 및 최적화 (30분)
  - 두 단계 통합
  - 캐싱 (같은 후보 재검증 방지)
  - 성능 측정
  
  검증: < 200ms 응답 시간
```

### Task 4.3: Guardian 개입 로직 (2시간)

```yaml
□ 4.3.1 반복 횟수 추적 (1시간)
  - Graph에 CircularPattern 노드 생성
  
  CREATE (c:CircularPattern {
      pattern_id: 'circular_001',
      topic: '플랫폼 검증',
      repetition_count: 3,
      first_detected: '...',
      agents_involved: ['steve', 'bill']
  })
  
  - 반복 횟수 자동 증가
  
  검증: Graph에 순환 기록됨

□ 4.3.2 Guardian 메시지 생성 (30분)
  - 반복 2회: 로그만
  - 반복 3회: Nudge 메시지
  - 반복 4회: 에스컬레이션
  
  템플릿:
    🔄 순환 패턴 감지
    
    주제: {topic}
    반복: {count}회
    쿼리들:
      1. {query_1}
      2. {query_2}
      3. {query_3}
    
    제안:
      - 다른 각도 접근
      - Owner 의사결정
  
  검증: 메시지 정확히 생성

□ 4.3.3 통합 테스트 (30분)
  - 순환 시나리오 재현
  - 자동 감지 확인
  - Guardian 개입 확인
  
  검증: E2E 작동
```

### Day 4 완료 기준

```yaml
✅ QueryMemory 컬렉션 작동
✅ Memory-RAG로 유사 쿼리 검색
✅ LLM으로 순환 정밀 검증
✅ 3회 반복 자동 감지
✅ Guardian Nudge 메시지 출력
✅ Graph에 CircularPattern 기록

→ UMIS 순환 감지 완성! 🔄
```

---

## 📅 Day 5: Memory-Augmented 목표 정렬 (금요일)

**목표:** RAG로 목표 이탈 자동 감지  
**시간:** 8시간  
**중요도:** 🔴 P0 (UMIS 핵심 #2)

### Task 5.1: Project Goal Memory (3시간)

```yaml
□ 5.1.1 GoalMemory 컬렉션 생성 (1시간)
  - umis_rag/memory/goal_memory.py
  
  class GoalMemoryRAG:
      def __init__(self):
          self.index = Chroma(
              collection_name="project_goals",
              embedding_function=embeddings
          )
  
  - store_project_goal() 메서드
  - search_goal() 메서드
  
  검증: 목표 저장 및 검색 작동

□ 5.1.2 프로젝트 목표 자동 저장 (1시간)
  - [PROJECT_START] 감지
  - 사용자 목표 입력 받기
  
  Document:
    content: """
      프로젝트: 피아노 구독 서비스
      
      핵심 질문:
      - 시장 규모는?
      - 구독 전환 가능성은?
      - 수익 모델은?
      
      목표: 시장 기회 평가
    """
    
    metadata:
      project_id: "piano_subscription_20241101"
      created_at: "..."
  
  검증: 목표 자동 저장됨

□ 5.1.3 목표 업데이트 로직 (1시간)
  - 목표 진화 지원
  - 버전 관리 (v1, v2, ...)
  - 이력 추적
  
  검증: 목표 업데이트 가능
```

### Task 5.2: Hybrid 정렬도 측정 (3시간)

```yaml
□ 5.2.1 Memory-RAG 기반 초기 점수 (1.5시간)
  
  def check_alignment_rag(project_id, current_query):
      # 목표 검색 (자동 유사도!)
      result = goal_memory.search(
          current_query,
          k=1,
          filter={"project_id": project_id}
      )
      
      goal_doc, distance = result[0]
      
      # 거리 → 정렬도 변환
      alignment = (1 / (1 + distance)) * 100
      
      return {
          "score": alignment,
          "goal": goal_doc.page_content
      }
  
  검증: 정렬도 자동 계산

□ 5.2.2 LLM 이탈 분석 (1시간)
  
  def analyze_deviation(goal, current_query, score):
      if score >= 60:
          return None  # 정렬됨, 분석 불필요
      
      # LLM 분석 (이탈 시만)
      prompt = f"""
      프로젝트 목표:
      {goal}
      
      현재 쿼리:
      {current_query}
      
      정렬도: {score}% (기준: 60%)
      
      왜 이탈했는지, 어떻게 복귀할지 분석하세요.
      """
      
      analysis = llm.invoke(prompt)
      
      return {
          "deviation_reason": analysis,
          "recommendation": "목표 재확인 필요"
      }
  
  검증: 이탈 이유 명확히 분석

□ 5.2.3 통합 및 최적화 (30분)
  - check_goal_alignment_hybrid()
  - Stage 1: RAG (빠름)
  - Stage 2: LLM (정확)
  - 캐싱
  
  검증: < 100ms (정렬 시), < 2s (이탈 시)
```

### Task 5.3: Guardian 모니터링 통합 (2시간)

```yaml
□ 5.3.1 실시간 모니터링 (1시간)
  - 5개 쿼리 윈도우 평균
  - 연속 모니터링
  - Graph 기록
  
  CREATE (a:Alignment {
      project_id: '...',
      avg_score: 52,
      timestamp: '...',
      alert: true
  })
  
  검증: 평균 정렬도 추적됨

□ 5.3.2 Guardian 경고 메시지 (30분)
  
  템플릿:
    🎯 목표 정렬도 경고
    
    현재 평균: 52% (기준: 60%)
    
    최근 이탈 쿼리:
      - "바이올린 시장" (38%)
      - "현악기 제조" (45%)
    
    프로젝트 목표:
      "피아노 구독 서비스"
    
    이탈 이유:
      {LLM 분석 결과}
    
    권고: 목표 재확인
  
  검증: 명확한 메시지

□ 5.3.3 통합 테스트 (30분)
  - 정렬 → 이탈 → 복귀 시나리오
  - 자동 감지 확인
  
  검증: E2E 작동
```

### Day 5 완료 기준

```yaml
✅ GoalMemory 컬렉션 작동
✅ 프로젝트 목표 자동 저장
✅ Memory-RAG로 정렬도 측정
✅ LLM으로 이탈 이유 분석
✅ 60% 기준 자동 경고
✅ Graph에 Alignment 기록

→ UMIS 목표 정렬 완성! 🎯
```

---

## 📅 Day 6: Agent별 Modular RAG (토요일)

**목표:** 같은 데이터를 6개 agent 관점으로 청킹  
**시간:** 8시간  
**중요도:** 🔴 P0 (Multi-Agent 핵심!)

### Task 6.1: Multi-View 메타데이터 스키마 (2시간)

```yaml
□ 6.1.1 UnifiedChunkMetadata 구현 (1시간)
  - umis_rag/core/metadata_schema.py (이미 작성됨)
  - 검증 및 테스트
  
  구조:
    Core Metadata (공통):
      - source_id: "baemin_case"
      - domain: "case_study"
      - quality_grade: "A"
    
    Agent-Specific:
      - albert_view_type: "structural"
      - steve_pattern_id: "platform_business_model"
      - bill_metrics: "[...]"
      - rachel_sources: "[...]"
      - stewart_quality: "A"
  
  검증: Pydantic 모델 작동

□ 6.1.2 Chroma 호환 변환 (1시간)
  - to_chroma_metadata() 메서드
  - list → JSON string 변환
  - Flat dict 생성
  
  검증: Chroma에 저장 가능
```

### Task 6.2: 5-View 청킹 구현 (4시간)

```yaml
□ 6.2.1 Observer View 청킹 (1시간)
  - convert_to_albert_view()
  
  배달의민족 → Observer 청크:
    chunk_id: "albert_baemin_market_structure"
    content: """
      시장 구조 변화 (2010-2020)
      
      기존: 음식점 → 전화주문 → 개별배달
           (파편화, 비효율)
      
      플랫폼 삽입 후: 3면 시장
           음식점 ↔ 플랫폼 ↔ 고객 ↔ 배달원
           (집중화, 효율)
      
      구조적 변화:
      - Power shift: 개별 → 플랫폼
      - 진입장벽: 양측 네트워크
    """
    
    metadata:
      agent_view: "albert"
      albert_view_type: "structural"
      albert_patterns: '["중개_플랫폼", "3면_시장"]'
      albert_chunking_level: "meso"
      source_id: "baemin_case"
  
  검증: Observer 관점 청크 생성

□ 6.2.2 Explorer View 청킹 (1시간)
  - convert_to_steve_view()
  
  배달의민족 → Explorer 청크:
    chunk_id: "steve_baemin_platform_opportunity"
    content: """
      플랫폼 비즈니스 모델 실행 사례
      
      기회 인식:
      - 트리거: 음식점 찾기 어려움
      - 트리거: 배달 추적 불가
      
      전략 실행:
      1. 양측 확보 (무료 등록 → 수수료)
      2. 지역별 밀도 (30분 배달)
      3. 수수료 모델 (6-12%)
      
      CSF:
      - 양측 임계 질량
      - 배달 속도
      - 수수료 밸런스
    """
    
    metadata:
      agent_view: "steve"
      steve_pattern_id: "platform_business_model"
      steve_csf: '["양측확보", "밀도전략"]'
      source_id: "baemin_case"
  
  검증: Explorer 관점 청크 생성

□ 6.2.3 Quantifier View 청킹 (30분)
  - convert_to_bill_view()
  
  배달의민족 → Quantifier 청크들:
    
    청크 1 (성장 지표):
      chunk_id: "bill_baemin_growth_metrics"
      content: """
        성장 지표:
        - 2015: 가맹점 1만, MAU 300만
        - 2018: 가맹점 3만, MAU 800만
        - 2020: MAU 1,000만, 점유율 60%
      """
      
      metadata:
        agent_view: "bill"
        bill_view_type: "quantitative"
        bill_metrics: '[{"name":"MAU","value":10000000}]'
        bill_chunking_level: "metric"
    
    청크 2 (수익 계산):
      chunk_id: "bill_baemin_revenue_calc"
      content: """
        수익 계산:
        
        GMV = MAU × 빈도 × 객단가 × 12
            = 1,000만 × 2.5 × 2만 × 12
            = 6조원
        
        매출 = GMV × 수수료율
             = 6조 × 8%
             = 4,800억
      """
      
      metadata:
        bill_view_type: "calculation"
        bill_formulas: '["GMV = MAU × 빈도 × 객단가"]'
  
  검증: Quantifier 관점 청크 생성 (여러 개)

□ 6.2.4 Validator View 청킹 (30분)
  - convert_to_rachel_view()
  
  배달의민족 → Validator 청크들:
    
    청크 1 (Wikipedia):
      chunk_id: "rachel_baemin_src001"
      content: """
        [SRC_001] Wikipedia - 배달의민족
        
        출처: https://ko.wikipedia.org/...
        신뢰도: Medium (공개 편집)
        정보: 연혁, 주요 지표
        한계: 최신 데이터 부족
      """
      
      metadata:
        agent_view: "rachel"
        rachel_view_type: "source"
        rachel_reliability: "medium"
        rachel_chunking_level: "source"
    
    청크 2 (공식 발표):
      chunk_id: "rachel_baemin_src002"
      content: """
        [SRC_002] 우아한형제들 공식 발표
        
        출처: 회사 보도자료
        신뢰도: High (1차 출처)
        정보: MAU, 가맹점 수
      """
      
      metadata:
        rachel_reliability: "high"
  
  검증: Validator 관점 청크 생성

□ 6.2.5 Guardian View 청킹 (30분)
  - convert_to_stewart_view()
  
  배달의민족 → Guardian 청크:
    chunk_id: "stewart_baemin_validation"
    content: """
      검증 상태 요약
      
      등급: A
      검증: Observer, Explorer, Quantifier, Validator ✅
      사용 승인:
        - Phase 2 (패턴 매칭) ✅
        - Phase 5 (사례 참조) ✅
      
      주의사항:
        - 거래액은 추정치
        - 최신 데이터 2021년 기준
    """
    
    metadata:
      agent_view: "stewart"
      stewart_quality: "A"
      stewart_validated: true
      stewart_chunking_level: "summary"
  
  검증: Guardian 관점 청크

□ 6.2.6 Owner View 청킹 (30분)
  - convert_to_owner_view()
  
  배달의민족 → Owner 청크:
    chunk_id: "owner_baemin_decision_insights"
    content: """
      의사결정 인사이트
      
      투자 가치:
      - 플랫폼 모델 검증됨
      - 4조원 인수 (2021)
      - 높은 성공률 (80%)
      
      핵심 리스크:
      - 수수료 갈등
      - 규제 변화
      
      적용 가능성:
      - 유사 구조 시장
      - 3면 시장 기회
    """
    
    metadata:
      agent_view: "owner"
      owner_view_type: "decision"
      owner_value_score: 8
  
  검증: Owner 관점 청크
```

### Task 6.3: Cross-Reference 연결 (1.5시간)

```yaml
□ 6.3.1 related_chunks 생성 (1시간)
  
  각 청크에 연결:
    albert_baemin_structure:
      related_chunks: [
        "steve_baemin_opportunity",
        "bill_baemin_growth_metrics",
        "rachel_baemin_src001"
      ]
    
    steve_baemin_opportunity:
      related_chunks: [
        "albert_baemin_structure",  # 구조 참조
        "bill_baemin_revenue_calc",  # 정량 근거
        "rachel_baemin_src002"       # 출처 검증
      ]
  
  → source_id로 자동 연결!
  
  검증: 모든 청크 연결됨

□ 6.3.2 연결 무결성 검증 (30분)
  - 모든 related_chunks가 실제 존재하는가?
  - 순환 참조는 없는가?
  - source_id 일관성
  
  검증: 무결성 100%
```

### Task 6.4: 통합 인덱스 구축 (30분)

```yaml
□ 6.4.1 umis_knowledge_base 생성
  - 기존 steve_knowledge_base 삭제
  - 새로운 통합 컬렉션 생성
  - 6-view 청크 모두 저장
  
  예상 청크 수:
    - 기존 54개 (Explorer only)
    - → 6-view: ~200개
      - Observer view: 40개
      - Explorer view: 54개 (기존)
      - Quantifier view: 60개 (계산 단위)
      - Validator view: 30개 (출처별)
      - Guardian view: 10개 (요약)
      - Owner view: 10개 (의사결정)
  
  검증: 200개 청크 인덱싱 완료
```

### Day 6 완료 기준

```yaml
✅ 6-View 청킹 로직 완성
✅ 배달의민족 → 6개 관점 청크
✅ Cross-reference 연결
✅ umis_knowledge_base 구축 (~200 청크)
✅ source_id로 협업 가능

→ Modular RAG 완성! 👥
```

---

## 📅 Day 7: Agent별 Retriever (일요일)

**목표:** 각 Agent가 자기 view만 검색  
**시간:** 8시간  
**중요도:** 🔴 P0 (Multi-Agent 핵심!)

### Task 7.1: Base Retriever 구현 (2시간)

```yaml
□ 7.1.1 BaseAgentRetriever 클래스 (1.5시간)
  - umis_rag/retrievers/base.py
  
  class BaseAgentRetriever:
      def __init__(self, agent_name: str):
          self.agent_name = agent_name
          self.vectorstore = Chroma(
              collection_name="umis_knowledge_base"
          )
      
      def _base_filter(self):
          """기본 필터: agent_view"""
          return {"agent_view": self.agent_name}
      
      def search(self, query, additional_filter=None):
          """기본 검색"""
          filter_dict = self._base_filter()
          
          if additional_filter:
              filter_dict = {
                  "$and": [
                      filter_dict,
                      additional_filter
                  ]
              }
          
          return self.vectorstore.similarity_search(
              query,
              filter=filter_dict
          )
  
  검증: 기본 클래스 작동

□ 7.1.2 Chroma 필터 헬퍼 (30분)
  - AND, OR 조건 자동 생성
  - 복잡한 필터 간편하게
  
  검증: 복잡한 필터 작동
```

### Task 7.2: Agent별 Retriever 구현 (4시간)

```yaml
□ 7.2.1 ObserverRetriever (1시간)
  - umis_rag/retrievers/albert.py
  
  class ObserverRetriever(BaseAgentRetriever):
      def __init__(self):
          super().__init__("albert")
      
      def search_structure(self, market: str):
          """시장 구조 검색"""
          return self.search(
              market,
              additional_filter={
                  "albert_view_type": "structural",
                  "albert_chunking_level": {"$in": ["macro", "meso"]}
              }
          )
      
      def search_dynamics(self, pattern: str):
          """시장 역학 검색"""
          return self.search(
              pattern,
              additional_filter={
                  "albert_view_type": "dynamics",
                  "albert_chunking_level": "micro"
              }
          )
  
  검증: Observer 전용 검색 작동

□ 7.2.2 ExplorerRetriever (1시간)
  - umis_rag/retrievers/steve.py
  
  class ExplorerRetriever(BaseAgentRetriever):
      def __init__(self):
          super().__init__("steve")
      
      def search_by_trigger(self, triggers: str):
          """트리거 → 패턴"""
          return self.search(
              triggers,
              additional_filter={
                  "steve_view_type": "opportunity",
                  "steve_chunking_level": {"$in": ["pattern", "section"]}
              }
          )
      
      def search_cases(self, industry: str, pattern_id: str):
          """산업 → 사례"""
          return self.search(
              industry,
              additional_filter={
                  "steve_view_type": "case_learning",
                  "steve_pattern_id": pattern_id,
                  "steve_chunking_level": "case"
              }
          )
      
      def ask_bill_for_metrics(self, source_id: str):
          """Quantifier에게 정량 데이터 요청"""
          bill = QuantifierRetriever()
          return bill.search(
              "",  # 쿼리 없음
              additional_filter={"source_id": source_id}
          )
      
      def ask_rachel_for_sources(self, source_id: str):
          """Validator에게 출처 확인"""
          rachel = ValidatorRetriever()
          return rachel.search(
              "",
              additional_filter={"source_id": source_id}
          )
  
  검증: Explorer 협업 검색 작동

□ 7.2.3 QuantifierRetriever (30분)
  - umis_rag/retrievers/bill.py
  
  class QuantifierRetriever(BaseAgentRetriever):
      def search_metric(self, metric_name: str):
          """특정 메트릭만"""
          return self.search(
              metric_name,
              additional_filter={
                  "bill_chunking_level": "metric",
                  "bill_has_numbers": True
              },
              k=1  # 하나만!
          )
      
      def search_calculation(self, calc_type: str):
          """계산 과정"""
          return self.search(
              calc_type,
              additional_filter={
                  "bill_chunking_level": "calculation"
              }
          )
  
  검증: Quantifier 빠른 검색

□ 7.2.4 ValidatorRetriever (30min)
  - umis_rag/retrievers/rachel.py
  
  class ValidatorRetriever(BaseAgentRetriever):
      def search_by_source(self, source_id: str):
          """특정 데이터의 출처"""
          return self.search(
              "",
              additional_filter={
                  "source_id": source_id,
                  "rachel_chunking_level": "source"
              }
          )
      
      def verify_data_point(self, data: str):
          """데이터 검증"""
          return self.search(
              data,
              additional_filter={
                  "rachel_view_type": "verification"
              }
          )
  
  검증: Validator 검증 검색

□ 7.2.5 GuardianRetriever (30분)
  - umis_rag/retrievers/stewart.py
  
  class GuardianRetriever(BaseAgentRetriever):
      def check_validation_status(self, source_id: str):
          """검증 상태 빠른 확인"""
          return self.search(
              "",
              additional_filter={
                  "source_id": source_id,
                  "stewart_chunking_level": "summary"
              },
              k=1
          )
      
      def search_quality_patterns(self, grade: str):
          """품질 패턴 검색"""
          return self.search(
              "",
              additional_filter={
                  "stewart_quality": grade
              }
          )
  
  검증: Guardian 품질 검색

□ 7.2.6 OwnerRetriever (30min)
  - umis_rag/retrievers/owner.py
  
  class OwnerRetriever(BaseAgentRetriever):
      def search_decision_insights(self, topic: str):
          """의사결정 인사이트"""
          return self.search(
              topic,
              additional_filter={
                  "owner_view_type": "decision"
              }
          )
  
  검증: Owner 의사결정 검색
```

### Task 7.3: Cross-Agent 협업 테스트 (2시간)

```yaml
□ 7.3.1 Explorer → Quantifier 협업 (1시간)
  
  시나리오:
    1. Explorer: "배달의민족 사례" 검색
       → steve_baemin_opportunity 발견
       → source_id: "baemin_case" 획득
    
    2. Explorer: "정량 데이터 필요"
       → steve.ask_bill_for_metrics("baemin_case")
       → Quantifier retriever 호출
    
    3. Quantifier: source_id로 검색
       → bill_baemin_growth_metrics 반환
       → "MAU: 1,000만" 획득
    
    4. Explorer: Quantifier 데이터로 가설 생성
       → "국내 배달앱 MAU 1,000만 검증됨"
  
  검증: 자동 협업 성공! ✨

□ 7.3.2 Explorer → Validator 협업 (30분)
  
  시나리오:
    1. Explorer: Quantifier 데이터 사용
       → "출처 신뢰도 확인 필요"
    
    2. Explorer → Validator:
       → steve.ask_rachel_for_sources("baemin_case")
    
    3. Validator: 출처 반환
       → rachel_baemin_src002
       → "공식 발표 (High 신뢰도)"
    
    4. Explorer: 신뢰도 확인하여 가설 작성
  
  검증: 출처 확인 자동

□ 7.3.3 Guardian 검증 체인 (30분)
  
  시나리오:
    1. Guardian: "steve_baemin_opportunity" 검증
       → source_id 확인
    
    2. Guardian: Quantifier/Validator 검증 확인
       → bill_retriever.search(source_id)
       → rachel_retriever.search(source_id)
    
    3. 모두 존재 → 검증 완료
       → Grade A 부여
  
  검증: 검증 체인 작동
```

### Day 7 완료 기준

```yaml
✅ 6개 Agent Retriever 작동
✅ 각 Agent가 자기 view만 검색
✅ Explorer → Quantifier 자동 협업
✅ Explorer → Validator 자동 협업
✅ Guardian 검증 체인 확인
✅ source_id 기반 협업 완벽

→ Modular RAG 완성! 👥
```

---

## 📅 Day 8-9: Hybrid 검색 기초 (월-화요일)

**목표:** Vector + Graph 통합 검색  
**시간:** 12시간  
**중요도:** 🔴 P0 (완전한 검색)

### Task 6.1: Graph 쿼리 구현 (4시간)

```yaml
□ 6.1.1 패턴 조합 쿼리 (2시간)
  - umis_rag/graph/pattern_queries.py
  
  def find_pattern_combinations(pattern_id: str):
      query = """
      MATCH (p:Pattern {id: $pattern_id})
            -[r:COMBINES_WITH]->(p2:Pattern)
      RETURN p2.id as combined_pattern,
             r.synergy as synergy,
             r.example as example,
             r.success_rate as success_rate
      ORDER BY r.success_rate DESC
      """
      
      return graph.run(query, pattern_id=pattern_id)
  
  검증: "platform" → subscription 조합 발견

□ 6.1.2 검증 체인 쿼리 (기초) (1.5시간)
  - 향후 사용을 위한 기본 구조
  
  def trace_validation_chain(hypothesis_id: str):
      # 간단한 버전 (향후 확장)
      query = """
      MATCH path = (:Hypothesis {id: $id})
                   -[:BASED_ON*1..5]->()
      RETURN nodes(path)
      """
  
  검증: 기본 추적 작동

□ 6.1.3 대항 전략 쿼리 (30분)
  - Counter-Positioning 검색
  
  def find_counter_strategies(weakness: str):
      # 1등 약점 → 대항 전략
      ...
  
  검증: "premium_trap" → low_end 발견
```

### Task 6.2: Vector + Graph 통합 (4시간)

```yaml
□ 6.2.1 HybridRetriever 구현 (2시간)
  - umis_rag/retrievers/hybrid.py
  
  class HybridRetriever:
      def search(self, query: str):
          # Stage 1: Vector search
          vector_results = chroma.search(query, k=10)
          
          # Stage 2: Graph expansion
          for doc in vector_results:
              pattern_id = doc.metadata["pattern_id"]
              
              # Graph로 조합 찾기
              combinations = graph.find_combinations(pattern_id)
              
              # 결과에 추가
              doc.metadata["combinations"] = combinations
          
          return vector_results
  
  검증: Vector + Graph 통합 결과

□ 6.2.2 결과 병합 및 Re-ranking (1.5시간)
  - Vector 유사도 + Graph 관계 점수
  - 최종 점수 계산
    
    final_score = (
        vector_similarity × 0.7 +
        graph_relevance × 0.3
    )
  
  - Re-ranking
  
  검증: 조합 패턴이 상위로

□ 6.2.3 캐싱 및 최적화 (30분)
  - Graph 쿼리 결과 캐싱
  - 중복 검색 방지
  - 성능 측정
  
  검증: < 300ms
```

### Task 6.3: 테스트 케이스 (4시간)

```yaml
□ 6.3.1 단일 패턴 검색 (1시간)
  Query: "플랫폼 비즈니스"
  Expected: platform_business_model
  
  검증: 정확히 찾음

□ 6.3.2 조합 패턴 검색 (1.5시간)
  Query: "플랫폼 + 구독 조합"
  Expected:
    - platform + subscription
    - Synergy: "충성도 + 안정수익"
    - Example: "Amazon Prime"
  
  검증: 조합 자동 발견! ✨

□ 6.3.3 대항 전략 검색 (1시간)
  Query: "고가 전략의 약점"
  Expected:
    - premium_trap 발견
    - COUNTERS: low_end_disruption
    - Mechanism: "Good Enough 제품"
  
  검증: 대항 전략 발견

□ 6.3.4 엣지 케이스 (30분)
  - 존재하지 않는 패턴
  - 관계 없는 패턴
  - 빈 결과 처리
  
  검증: 에러 없이 처리
```

### Day 6-7 완료 기준

```yaml
✅ HybridRetriever 작동
✅ Vector + Graph 통합 검색
✅ 패턴 조합 자동 발견
✅ "플랫폼 + 구독" → Amazon Prime
✅ 성능 < 300ms

→ Hybrid 검색 기초 완성! 🔍
```

---

## 📅 Day 8-9: Explorer 통합 및 고도화 (월-화요일)

**목표:** Explorer에 모든 기능 통합  
**시간:** 12시간  
**중요도:** 🔴 P0 (사용자 인터페이스)

### Task 8.1: Explorer 메서드 확장 (4시간)

```yaml
□ 8.1.1 search_hybrid_patterns() (2시간)
  - HybridRetriever 통합
  - 조합 패턴 자동 제안
  
  steve.search_hybrid_patterns("플랫폼 + 구독")
  → {
      "primary": "platform_business_model",
      "combines_with": "subscription_model",
      "synergy": "충성도 + 안정수익",
      "example": "Amazon Prime",
      "success_rate": 0.8
    }
  
  검증: 조합 제안 작동

□ 8.1.2 ask_bill_for_data() (1시간)
  - Quantifier Retriever 호출 (향후 구현)
  - 현재는 기본 검색
  
  검증: source_id로 Quantifier 데이터 찾기

□ 8.1.3 ask_rachel_for_verification() (1시간)
  - Validator Retriever 호출 (향후)
  - 현재는 기본 검색
  
  검증: source_id로 Validator 검증 찾기
```

### Task 8.2: Guardian 통합 (4시간)

```yaml
□ 8.2.1 GuardianMonitor 클래스 (2시간)
  - umis_rag/agents/stewart.py
  
  class GuardianMonitor:
      def __init__(self):
          self.query_memory = QueryMemoryRAG()
          self.goal_memory = GoalMemoryRAG()
          self.circular_detector = CircularDetector()
          self.alignment_checker = AlignmentChecker()
      
      def monitor(self, query, project_id):
          # 순환 감지
          circular = self.circular_detector.detect(query)
          
          # 목표 정렬
          alignment = self.alignment_checker.check(
              project_id, 
              query
          )
          
          # 통합 판단
          return self.generate_alerts(circular, alignment)
  
  검증: 통합 모니터링 작동

□ 8.2.2 자동 개입 로직 (1.5시간)
  - 순환 3회 → Nudge
  - 정렬 < 60% → 경고
  - 둘 다 발생 → 긴급
  
  검증: 우선순위 정확

□ 8.2.3 메시지 통합 (30분)
  - 여러 알림 통합
  - 우선순위 정렬
  - 명확한 액션 제안
  
  검증: 알림 명확함
```

### Task 8.3: E2E 통합 (4시간)

```yaml
□ 8.3.1 전체 워크플로우 테스트 (2시간)
  
  시나리오:
    1. [PROJECT_START] "피아노 구독"
       → Goal 저장됨
    
    2. Explorer: "플랫폼 기회" 검색
       → Query 기록됨
       → Alignment: 95% ✅
    
    3. Explorer: "플랫폼 검증" 검색 (2회)
       → Query 기록됨
       → 유사 쿼리 1개 발견
    
    4. Explorer: "플랫폼 수익성" 검색 (3회)
       → 순환 감지! 🔄
       → Guardian Nudge
    
    5. Explorer: "바이올린" 검색
       → Alignment: 42% ⚠️
       → 목표 이탈 경고! 🎯
    
    6. Owner: 목표 재확인
       → 피아노로 복귀
  
  검증: 전체 시나리오 작동

□ 8.3.2 복잡한 시나리오 (1.5시간)
  - 순환 + 이탈 동시
  - 패턴 조합 + 순환
  - 여러 프로젝트 동시
  
  검증: 모두 정확히 처리

□ 8.3.3 성능 최적화 (30분)
  - 병목 지점 파악
  - 캐싱 추가
  - 불필요한 LLM 호출 제거
  
  검증: 전체 < 500ms
```

### Day 8-9 완료 기준

```yaml
✅ Explorer Hybrid 검색 작동
✅ Guardian 순환 감지 통합
✅ Guardian 목표 정렬 통합
✅ E2E 시나리오 통과
✅ 복잡한 케이스 처리

→ 핵심 기능 완성! 🎉
```

---

## 📅 Day 10: 통합 테스트 및 실전 프로젝트 (수요일)

**목표:** 실제 프로젝트로 검증  
**시간:** 8시간  
**중요도:** 🔴 P0 (품질 보증)

### Task 10.1: 시스템 테스트 (4시간)

```yaml
□ 10.1.1 단위 테스트 작성 (2시간)
  - tests/test_query_memory.py
  - tests/test_goal_alignment.py
  - tests/test_circular_detection.py
  - tests/test_hybrid_search.py
  
  검증: pytest 통과

□ 10.1.2 통합 테스트 (1.5시간)
  - tests/test_stewart_monitoring.py
  - 전체 워크플로우
  - 엣지 케이스
  
  검증: 모두 통과

□ 10.1.3 성능 벤치마크 (30분)
  - 100개 쿼리 처리 시간
  - 메모리 사용량
  - API 비용 측정
  
  목표:
    - 평균 응답: < 200ms
    - 메모리: < 1GB
    - 비용: < $0.01 / 100 queries
```

### Task 10.2: 실전 프로젝트 테스트 (3시간)

```yaml
□ 10.2.1 프로젝트 1: "음악 스트리밍 구독" (1.5시간)
  - Cursor에서 전체 분석
  - YAML + RAG 활용
  - 순환/목표 감지 확인
  - 패턴 조합 활용
  
  검증: 고품질 분석 완성

□ 10.2.2 프로젝트 2: "피트니스 앱 D2C" (1.5시간)
  - 다른 도메인 테스트
  - Guardian 개입 시나리오
  - Hybrid 검색 활용
  
  검증: 도메인 무관 작동
```

### Task 10.3: 문서화 및 정리 (1시간)

```yaml
□ 10.3.1 사용 가이드 업데이트 (30분)
  - CURSOR_QUICK_START.md
  - 실전 예시 추가
  - 스크린샷
  
□ 10.3.2 CHANGELOG 작성 (30분)
  - v1.0.0 릴리즈 노트
  - 주요 기능 리스트
  - 알려진 제한사항
```

### Day 10 완료 기준

```yaml
✅ 모든 테스트 통과
✅ 2개 실전 프로젝트 성공
✅ 성능 목표 달성
✅ 문서 업데이트 완료

→ UMIS RAG v1.0 완성! 🎉
```

---

## 📅 Day 10-11: Explorer & Guardian 통합 (수-목요일)

**목표:** 모든 기능을 Agent에 통합  
**시간:** 12시간  
**중요도:** 🔴 P0

### Task 10.1: Explorer 전체 통합 (6시간)

```yaml
□ 10.1.1 search_hybrid_patterns() (2시간)
  - HybridRetriever 사용
  - Vector + Graph 조합
  - 패턴 조합 자동 제안
  
□ 10.1.2 Multi-Agent 협업 메서드 (2시간)
  - ask_albert()
  - ask_bill()
  - ask_rachel()
  - source_id 기반 자동 협업
  
□ 10.1.3 E2E 워크플로우 (2시간)
  - 트리거 → 패턴 → 사례 → 협업 → 가설
  - 전체 흐름 테스트
```

### Task 10.2: Guardian 전체 통합 (6시간)

```yaml
□ 10.2.1 GuardianMonitor 통합 (3시간)
  - QueryMemory + GoalMemory
  - CircularDetector + AlignmentChecker
  - 자동 모니터링
  
□ 10.2.2 개입 로직 완성 (2시간)
  - 순환 + 이탈 동시 감지
  - 우선순위 판단
  - 메시지 생성
  
□ 10.2.3 Graph 연동 (1시간)
  - CircularPattern 노드
  - Alignment 노드
  - 이력 추적
```

### Day 10-11 완료 기준

```yaml
✅ Explorer 모든 기능 통합
✅ Guardian 자동 모니터링
✅ 순환 + 목표 동시 작동
✅ Cross-agent 협업 자동

→ 통합 완성! 🎨
```

---

## 📅 Day 12: 통합 테스트 및 실전 프로젝트 (금요일)

**목표:** 실제 프로젝트로 검증  
**시간:** 8시간  
**중요도:** 🔴 P0

### Task 12.1: 시스템 테스트 (4시간)

```yaml
□ 12.1.1 단위 테스트 (2시간)
  - tests/test_multi_view.py
  - tests/test_agent_retrievers.py
  - tests/test_memory_rag.py
  
□ 12.1.2 통합 테스트 (1.5시간)
  - E2E 워크플로우
  - Cross-agent 협업
  
□ 12.1.3 성능 벤치마크 (30분)
  - 응답 시간
  - 메모리 사용
  - API 비용
```

### Task 12.2: 실전 프로젝트 (3시간)

```yaml
□ 12.2.1 프로젝트 1 (1.5시간)
  - "음악 스트리밍 구독"
  - 전체 agent 활용
  
□ 12.2.2 프로젝트 2 (1.5시간)
  - "피트니스 앱 D2C"
  - Guardian 개입 시나리오
```

### Task 12.3: 문서화 (1시간)

```yaml
□ 12.3.1 사용 가이드
□ 12.3.2 CHANGELOG
□ 12.3.3 README 업데이트
```

---

## 📊 전체 작업 요약

### 우선순위별 집계

```yaml
🔴 P0 - 필수 (12일, 96시간) ← 수정됨!
  Day 1: Hot-Reload (8h)
  Day 2-3: Knowledge Graph (16h)
  Day 4: 순환 감지 Hybrid (8h)
  Day 5: 목표 정렬 Hybrid (8h)
  Day 6: Modular RAG - 6-View 청킹 (8h) ⭐ 추가!
  Day 7: Agent별 Retriever (8h) ⭐ 추가!
  Day 8-9: Hybrid 검색 (12h)
  Day 10-11: Agent 통합 (12h)
  Day 12: 통합 테스트 (8h)
  
  → UMIS 핵심 85% 구현!

🟡 P1 - 확장 (선택, +14일):
  Multi-View 청킹 (3일)
  Meta-RAG 검증 (4일)
  
  → UMIS 95% 구현

🟢 P2 - 고급 (선택, +5일):
  명확도 적응 (2일)
  피드백 학습 (3일)

🔵 P3-P4 - 미룸:
  MCP Tool
  배포 패키징
```

### 산출물

```yaml
코드:
  ✅ umis_rag/memory/ (QueryMemory, GoalMemory)
  ✅ umis_rag/graph/ (Knowledge Graph)
  ✅ umis_rag/retrievers/ (HybridRetriever)
  ✅ umis_rag/agents/stewart.py (Monitor)
  ✅ scripts/dev_watcher.py (Hot-Reload)
  
데이터:
  ✅ Neo4j Graph (45개 관계)
  ✅ QueryMemory Index
  ✅ GoalMemory Index
  ✅ 기존 54개 청크
  
문서:
  ✅ 구현 가이드
  ✅ API 문서
  ✅ 테스트 리포트
```

---

## 🎯 각 Day별 핵심 목표

```
Day 1 ⚡: Hot-Reload
  → YAML 수정 → 2초 → 반영

Day 2-3 🔗: Knowledge Graph
  → 패턴 조합 자동 발견

Day 4 🔄: 순환 감지
  → 3회 반복 자동 감지

Day 5 🎯: 목표 정렬
  → 60% 기준 자동 경고

Day 6 👥: Modular RAG (6-View 청킹) ⭐
  → Observer, Explorer, Quantifier, Validator, Guardian, Owner
  → 같은 사례를 6개 관점으로!

Day 7 🔗: Agent별 Retriever ⭐
  → 각 Agent가 자기 view만 검색
  → source_id로 협업 자동!

Day 8-9 🔍: Hybrid 검색
  → Vector + Graph 통합

Day 10-11 🎨: Agent 통합
  → 모든 기능 사용 가능

Day 12 ✅: 검증
  → 실전 프로젝트 성공

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
12일 후: UMIS RAG v1.0 완성!
완성도: 85% (Multi-Agent 포함!)
```

---

## 🔄 병렬 작업 가능

```yaml
Day 2-3 병렬:
  Track A: Knowledge Graph (Neo4j + 관계)
  Track B: QueryMemory 구현 (Day 4 준비)
  
  → 16시간 → 12시간으로 단축 가능!

실제 일정 최적화:
  Day 1: Hot-Reload (8h)
  Day 2: Graph + QueryMemory (병렬, 8h)
  Day 3: Graph 완성 + 순환 감지 시작 (8h)
  Day 4: 순환 감지 완성 + 목표 정렬 (8h)
  Day 5-6: Hybrid 검색 (12h)
  Day 7-8: Explorer 통합 (12h)
  Day 9: 테스트 (8h)
  
  총: 9일! (1일 단축)
```

---

## 📋 체크리스트 (인쇄용)

### Week 1 (Day 1-5)

```
Day 1 - Hot-Reload:
  [ ] dev_watcher.py 완성
  [ ] Makefile 명령어
  [ ] 실전 테스트
  [ ] 문서화
  
Day 2 - Neo4j + QueryMemory:
  [ ] Neo4j 설치 및 설정
  [ ] Python driver 연동
  [ ] 스키마 정의
  [ ] QueryMemory 컬렉션
  
Day 3 - Graph 관계 + 순환 기초:
  [ ] pattern_relationships.yaml (45개)
  [ ] Graph import
  [ ] 쿼리 테스트
  [ ] 순환 감지 후보 검색
  
Day 4 - 순환 감지 완성:
  [ ] LLM 정밀 검증
  [ ] Guardian 개입 로직
  [ ] Graph CircularPattern
  [ ] 통합 테스트
  
Day 5 - 목표 정렬:
  [ ] GoalMemory 컬렉션
  [ ] 정렬도 측정 (RAG)
  [ ] 이탈 분석 (LLM)
  [ ] Guardian 경고
```

### Week 2 (Day 6-10)

```
Day 6-7 - Hybrid 검색:
  [ ] Graph 쿼리 구현
  [ ] Vector + Graph 통합
  [ ] Re-ranking
  [ ] 테스트 케이스
  
Day 8-9 - Explorer 통합:
  [ ] search_hybrid_patterns()
  [ ] Guardian 모니터링 통합
  [ ] E2E 워크플로우
  [ ] 복잡한 시나리오
  
Day 10 - 검증:
  [ ] 단위 테스트
  [ ] 통합 테스트
  [ ] 실전 프로젝트 2개
  [ ] 성능 벤치마크
  [ ] 문서 완성
```

---

## 💰 예상 비용

```yaml
개발 비용:
  Neo4j: 무료 (Community)
  OpenAI API:
    - 인덱스 구축: $0.006
    - 개발 테스트: $0.10 (100회)
    - LLM 검증: $0.50 (50회)
    총: $0.61 (약 800원)

운영 비용 (월):
  - 쿼리 100회: $0.01
  - LLM 검증 20회: $0.20
  총: $0.21 (약 300원/월)
```

---

## 🎯 완료 후 상태

### 기능 완성도

```yaml
Vector RAG: ████████████████████░ 95%
  ✅ 54개 청크
  ✅ text-embedding-3-large
  ✅ 검색 품질 우수

Knowledge Graph: ████████████░░░░░░░░ 60%
  ✅ 패턴 관계 45개
  ✅ 조합 검색
  ⚠️  검증 체인 (기초만)

Memory-Augmented: ████████████████████░ 95%
  ✅ QueryMemory
  ✅ GoalMemory
  ✅ Hybrid 순환 감지
  ✅ Hybrid 목표 정렬

Guardian Monitoring: ████████████████░░░░ 80%
  ✅ 순환 감지
  ✅ 목표 정렬
  ⚠️  명확도 진화 (미구현)
  ⚠️  Meta-RAG (미구현)

전체 UMIS 구현: ████████████████░░░░░ 80%
```

### 사용 가능성

```yaml
✅ Cursor에서 즉시 사용
✅ YAML + RAG Dual Mode
✅ Hot-Reload 개발
✅ 실전 프로젝트 가능

제한사항:
  ⚠️  Explorer view만 (Observer, Quantifier, Validator 미구현)
  ⚠️  자동 검증 부분적 (Meta-RAG 미구현)
  ⚠️  MCP Tool 없음 (수동 query_rag.py)
```

---

## 📅 데일리 체크포인트

각 Day 종료 시 확인:

```yaml
체크리스트:
  [ ] 목표한 기능 작동하는가?
  [ ] 테스트 통과하는가?
  [ ] 성능 기준 만족하는가?
  [ ] 문서 업데이트했는가?
  [ ] Git 커밋했는가?
  
  → 모두 ✅ → 다음 Day 진행
  → 하나라도 ❌ → 해결 후 진행
```

---

## 🚀 시작 준비

### 즉시 (오늘)

```bash
# Hot-Reload 테스트
make dev

# (작동 확인)
# VS Code에서 YAML 수정
# → 자동 반영 확인

# 문제 있으면 수정
# 안정화
```

### 내일 (Day 2)

```bash
# Neo4j 시작
docker run -d \
  --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/umis_rag_2024 \
  neo4j:5-community

# 접속 확인
# http://localhost:7474

# Python driver
pip install neo4j

# 시작!
```

---

## 📊 최종 체크리스트

### Pre-flight Check

```
환경 준비:
  [✅] Python 3.11+ venv
  [✅] OpenAI API Key
  [✅] 54개 청크 인덱스
  [✅] text-embedding-3-large
  [ ] Docker 설치 (Neo4j용)
  [ ] Neo4j 실행

도구:
  [✅] make 명령
  [✅] watchdog 패키지
  [ ] neo4j Python 패키지

문서:
  [✅] IMPLEMENTATION_PLAN.md
  [✅] MEMORY_AUGMENTED_RAG_ANALYSIS.md
  [✅] umis_rag_architecture_v1.1_enhanced.yaml
  [✅] 이 문서 (DETAILED_TASK_LIST.md)
```

---

## 🎯 성공 기준

### 10일 후 반드시 달성

```yaml
필수:
  ✅ Hot-Reload 안정 작동
  ✅ 순환 패턴 3회 감지
  ✅ 목표 정렬 60% 경고
  ✅ 패턴 조합 자동 제안
  ✅ 실전 프로젝트 2개 성공

성능:
  ✅ 평균 응답 < 200ms
  ✅ 순환 감지 정확도 > 95%
  ✅ 목표 정렬 정확도 > 95%
  ✅ 비용 < $0.01 / 100 queries

경험:
  ✅ YAML 수정 즉시 반영
  ✅ Cursor 사용 자연스러움
  ✅ Guardian 개입 명확함
```

---

## 📁 파일 구조 (10일 후)

```
umis-main/
├── umis_rag/
│   ├── memory/                    # 🆕 Memory-Augmented
│   │   ├── __init__.py
│   │   ├── query_memory.py        # QueryMemory RAG
│   │   ├── goal_memory.py         # GoalMemory RAG
│   │   └── decision_memory.py     # (향후)
│   │
│   ├── graph/                     # 🆕 Knowledge Graph
│   │   ├── __init__.py
│   │   ├── schema.py              # 노드/관계 정의
│   │   ├── builder.py             # Graph 구축
│   │   ├── query.py               # Cypher 쿼리
│   │   └── pattern_relationships.yaml  # 관계 데이터
│   │
│   ├── retrievers/                # 🆕 Hybrid Retriever
│   │   ├── __init__.py
│   │   ├── hybrid.py              # Vector + Graph
│   │   └── base.py
│   │
│   ├── agents/
│   │   ├── steve.py               # 🔄 확장됨
│   │   └── stewart.py             # 🆕 Monitor
│   │
│   └── core/
│       └── ...
│
├── scripts/
│   ├── dev_watcher.py             # 🔄 완성됨
│   └── ...
│
├── data/
│   └── chroma/
│       ├── steve_knowledge_base/  # 기존
│       ├── query_memory/          # 🆕
│       └── project_goals/         # 🆕
│
└── tests/                         # 🆕 테스트
    ├── test_query_memory.py
    ├── test_goal_alignment.py
    ├── test_circular_detection.py
    └── test_hybrid_search.py
```

---

## 🔧 개발 환경 설정

### Day 1 시작 전

```bash
# 1. 가상환경 활성화
cd /Users/kangmin/Documents/AI_dev/umis-main
source venv/bin/activate

# 2. 추가 패키지 설치
pip install neo4j watchdog

# 3. 현재 상태 확인
make stats
# → steve_knowledge_base: 54 docs

# 4. Hot-Reload 시작
make dev

# 5. 새 터미널 (작업용)
# VS Code에서 개발 시작
```

---

## 📊 진행 상황 추적

### 일일 리포트 양식

```markdown
## Day N 리포트 (YYYY-MM-DD)

### 완료한 작업
- [x] Task N.M.K: 설명
- [x] Task N.M.K: 설명

### 발견 사항
- 문제: ...
- 해결: ...
- 학습: ...

### 내일 계획
- [ ] Task ...

### 블로커
- 없음 / 있음: ...

### 시간
- 계획: Xh
- 실제: Yh
- 차이: (Y-X)h
```

---

## 🎯 최종 체크리스트 (간략)

```
✅ Phase 1: Vector RAG (완료!)

P0 (10일):
  [ ] Day 1: Hot-Reload
  [ ] Day 2-3: Knowledge Graph
  [ ] Day 4: 순환 감지 (Memory-RAG Hybrid)
  [ ] Day 5: 목표 정렬 (Memory-RAG Hybrid)
  [ ] Day 6-7: Hybrid 검색
  [ ] Day 8-9: Explorer 통합
  [ ] Day 10: 통합 테스트

P1 (선택):
  [ ] Multi-View
  [ ] Meta-RAG

P2 (선택):
  [ ] 명확도 적응
  [ ] 피드백 학습

P3-P4 (미룸):
  [ ] MCP Tool
  [ ] 배포
```

---

## 🚀 시작!

**준비되셨습니까?**

```bash
# Day 1 시작
make dev

# 개발 시작!
```

모든 작업이 구체적으로 정의되었습니다! 🎯
