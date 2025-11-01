# UMIS RAG 구현 계획

**목표:** UMIS v6.2 철학을 완전히 구현한 Multi-Agent RAG  
**기간:** 3-4주 (집중 개발)  
**우선순위:** 핵심 기능 > 통합/편의성 > 배포/패키징

---

## 📋 전체 작업 목록

### ✅ Phase 1: Vector RAG Prototype (완료!)

```yaml
Status: ✅ 100% 완료

구현:
  ✅ Python 환경 (LangChain + OpenAI + Chroma)
  ✅ YAML → 청크 변환 (54개)
  ✅ 벡터 인덱스 (text-embedding-3-large)
  ✅ Steve RAG 에이전트
  ✅ 검색 테스트
  ✅ query_rag.py 스크립트

완성도: Vector RAG 95%
UMIS 구현: 30%
```

---

### 🔄 Phase 2A: Hot-Reload 개발 환경

```yaml
Priority: 🔴 P0 (즉시 필요)
이유: 개발 생산성 10배 향상
기간: 1일
의존성: 없음 (독립적)

작업:
  1. dev_watcher.py 완성 및 테스트
     - watchdog 통합
     - 증분 업데이트 로직
     - 에러 핸들링
     - 시간: 4시간
  
  2. Makefile 완성
     - make dev (Hot-Reload)
     - make rebuild
     - make query
     - 시간: 2시간
  
  3. 실전 테스트
     - YAML 수정 → 자동 반영 검증
     - 여러 파일 동시 감시
     - 성능 최적화
     - 시간: 2시간

산출물:
  ✅ 작동하는 Hot-Reload
  ✅ YAML 수정 → 2초 → 반영
  ✅ 인라인 어셈블러 수준 경험

완료 기준:
  - YAML 저장 후 2초 내 반영
  - 에러 시 자동 복구
  - 안정적 작동
```

---

### 🔄 Phase 2B: Knowledge Graph 기본 구조

```yaml
Priority: 🔴 P0 (UMIS 핵심 가치)
이유: 패턴 조합, 검증 체인 필수
기간: 5일
의존성: Phase 1

작업:
  Day 1: Neo4j 설정 및 스키마
    □ Docker로 Neo4j 실행
    □ Python driver 설치 (py2neo)
    □ 기본 노드 타입 정의
      - Pattern, Case, AgentOutput, Data, Source
    □ 테스트 데이터 삽입
    시간: 8시간
  
  Day 2-3: 패턴 간 관계 정의
    □ COMBINES_WITH 관계 (30개)
      - platform + subscription
      - subscription + d2c
      - low_end + channel
      - ...
    □ COUNTERS 관계 (10개)
      - low_end → premium_trap
      - channel → middleman_dependency
    □ PREREQUISITE 관계 (5개)
    □ Graph에 import
    시간: 12시간
  
  Day 4: Hybrid 검색 엔진
    □ Vector search (기존)
    □ Graph query 통합
    □ 결과 병합 알고리즘
    □ hybrid_search() 메서드
    시간: 8시간
  
  Day 5: Steve 통합 및 테스트
    □ steve.search_hybrid_patterns()
    □ 패턴 조합 자동 제안
    □ E2E 테스트
    시간: 6시간

산출물:
  ✅ Neo4j Knowledge Graph
  ✅ 45개 패턴 관계
  ✅ Hybrid 검색 (Vector + Graph)
  ✅ 패턴 조합 자동 발견

완료 기준:
  - "플랫폼 + 구독" 쿼리 → Amazon Prime 제안
  - "저가" 쿼리 → 대항하는 "premium_trap" 발견
  - 검증 체인 추적 가능 (향후 사용)
```

---

### 🔄 Phase 2C: Stewart 순환 패턴 감지

```yaml
Priority: 🔴 P0 (UMIS 핵심 - 무한 루프 방지!)
이유: 순환 없으면 UMIS 아님
기간: 3일
의존성: Phase 1

작업:
  Day 1: Query History DB
    □ SQLite 테이블 설계
      - query_id, agent, query_text, topic, timestamp
    □ 모든 쿼리 자동 기록
    □ LLM으로 주제 추출
      - "플랫폼 비즈니스 검증"
      - → topic: "플랫폼 검증"
    시간: 6시간
  
  Day 2: 순환 감지 알고리즘
    □ 슬라이딩 윈도우 (최근 10개)
    □ 주제 유사도 계산 (벡터)
    □ 3회 반복 감지
    □ CircularPattern 노드 생성 (Graph)
    시간: 6시간
  
  Day 3: Stewart 개입 시스템
    □ 반복 2회: 모니터링 강화
    □ 반복 3회: Nudge 메시지
    □ 반복 4회: Owner 에스컬레이션
    □ 통합 테스트
    시간: 6시간

산출물:
  ✅ query_history.db
  ✅ 순환 감지 엔진
  ✅ Stewart 자동 개입
  ✅ UMIS v6.2 핵심 구현!

완료 기준:
  - 같은 주제 3회 반복 → 자동 감지
  - Stewart 메시지 출력
  - Graph에 CircularPattern 기록
```

---

### 🔄 Phase 2D: Stewart 목표 정렬도 모니터링

```yaml
Priority: 🔴 P0 (UMIS 핵심 - 목표 이탈 방지!)
이유: 목표 정렬 없으면 작업 낭비
기간: 2일
의존성: Phase 2C (query_history 공유)

작업:
  Day 1: 목표 임베딩 및 측정
    □ 프로젝트 시작 시 goal embedding
    □ 매 쿼리 alignment 계산
      - cosine_similarity(query, goal)
    □ query_history에 alignment 저장
    □ 5개 윈도우 평균 추적
    시간: 6시간
  
  Day 2: Stewart 모니터링 및 개입
    □ 평균 < 60% 감지
    □ 목표 이탈 경고
    □ 이탈 쿼리 리스트
    □ Owner 에스컬레이션
    □ 통합 테스트
    시간: 6시간

산출물:
  ✅ 목표 정렬도 실시간 측정
  ✅ 60% 기준 자동 모니터링
  ✅ Stewart 이탈 경고
  ✅ UMIS v6.2 핵심 구현!

완료 기준:
  - 프로젝트 목표 설정 자동
  - 매 쿼리 alignment 측정
  - < 60% 시 자동 경고
```

---

### 🟠 Phase 3A: Multi-View 청킹 (선택)

```yaml
Priority: 🟡 P1 (완전한 Multi-Agent 구현)
이유: Albert, Bill, Rachel view 필요
기간: 3일
의존성: Phase 1

작업:
  Day 1: 메타데이터 스키마 적용
    □ metadata_schema.py 완성
    □ UnifiedChunkMetadata 구현
    □ Core + Agent-Specific 구조
    시간: 6시간
  
  Day 2: 5-View 청킹 구현
    □ 01_convert_yaml.py 확장
    □ 같은 사례 → 5개 관점 청킹
      - albert_baemin_structure
      - steve_baemin_opportunity
      - bill_baemin_metrics
      - rachel_baemin_sources
      - stewart_baemin_validation
    □ Cross-reference 연결
    시간: 8시간
  
  Day 3: Agent별 Retriever
    □ AlbertRetriever
    □ BillRetriever
    □ RachelRetriever
    □ Cross-agent 협업 테스트
    시간: 8시간

산출물:
  ✅ 5개 agent view 청크
  ✅ Agent별 Retriever
  ✅ source_id 기반 협업
  ✅ 완전한 Multi-View 구현

완료 기준:
  - Steve → Bill (source_id로 정량 데이터 요청)
  - Steve → Rachel (출처 검증 요청)
  - 모두 자동 작동
```

---

### 🟠 Phase 3B: Stewart Meta-RAG (선택)

```yaml
Priority: 🟡 P1 (품질 자동화)
이유: 검증 자동화, 생산성 향상
기간: 4일
의존성: Phase 2B (Knowledge Graph), Phase 3A (선택)

작업:
  Day 1-2: 검증 규칙 Index
    □ validation_rules 청킹
      - Steve 가설 필수 규칙
      - Albert 구조 필수 규칙
      - Bill 계산 필수 규칙
    □ validation_rules_index 구축
    □ Rule-based 검증 엔진
    시간: 12시간
  
  Day 3: 품질 패턴 Index
    □ 좋은 예시 수집 (Grade A)
    □ 나쁜 예시 수집 (Grade D)
    □ quality_patterns_index 구축
    □ Pattern-based 검증 엔진
    시간: 6시간
  
  Day 4: Graph 검증 체인
    □ 논리 체인 추적 Cypher 쿼리
    □ Gap 자동 발견
    □ Stewart 3단계 검증 통합
    □ E2E 테스트
    시간: 8시간

산출물:
  ✅ validation_rules_index
  ✅ quality_patterns_index
  ✅ Stewart 3단계 자동 검증
  ✅ Gap 자동 발견

완료 기준:
  - Steve 가설 → 자동 검증
  - 누락 사항 자동 발견
  - Grade A/B/C/D 자동 부여
```

---

### 🟢 Phase 4A: 명확도 진화 시스템 (선택)

```yaml
Priority: 🟢 P2 (Adaptive Intelligence)
이유: UMIS 철학, 하지만 수동도 가능
기간: 2일
의존성: Phase 2C, 2D

작업:
  Day 1: 명확도 측정
    □ 4개 차원 평가 (LLM)
      - target_market
      - value_proposition
      - business_model
      - execution_path
    □ 프로젝트별 추적
    □ 진화 패턴 분석
    시간: 6시간
  
  Day 2: 적응형 RAG 전략
    □ clarity_20_40: 탐색 모드
    □ clarity_40_70: 분석 모드
    □ clarity_70_95: 실행 모드
    □ 자동 전환 로직
    시간: 6시간

산출물:
  ✅ 명확도 측정 시스템
  ✅ 적응형 RAG 전략
  ✅ 자동 모드 전환

완료 기준:
  - 명확도 자동 측정
  - RAG 전략 자동 조정
  - Discovery → Analysis → Execution
```

---

### 🟢 Phase 4B: 피드백 학습 시스템 (선택)

```yaml
Priority: 🟢 P2 (장기 가치)
이유: 사용할수록 향상, 초기엔 선택
기간: 3일
의존성: Phase 2C (query_history)

작업:
  Day 1: Query Refinement
    □ LLM 기반 쿼리 개선
    □ Stewart 피드백 → 쿼리 재작성
    □ 반복 검색 로직
    시간: 6시간
  
  Day 2: Weighted Retrieval
    □ 청크별 가중치 추적
    □ 승인/거부 시 가중치 업데이트
    □ SQLite 영구 저장
    □ Re-ranking 통합
    시간: 6시간
  
  Day 3: 통합 및 테스트
    □ 전체 피드백 루프 테스트
    □ 학습 효과 검증
    □ 성능 벤치마크
    시간: 6시간

산출물:
  ✅ Query refinement 엔진
  ✅ Weighted retrieval
  ✅ 피드백 DB
  ✅ 자동 학습 시스템

완료 기준:
  - 1회 거부 → 쿼리 개선
  - 3회 반복 → Grade A 달성
  - 4회차부터 학습 효과
```

---

### 🟢 Phase 5: MCP Tool 통합 (나중에)

```yaml
Priority: 🟢 P3 (편의성, 급하지 않음)
이유: Dual Mode로도 충분, 나중에
기간: 1주
의존성: Phase 2A-2D 완료 후

→ 당분간 미룸! (Dual Mode 사용)
```

---

### 🔵 Phase 6: 배포/패키징 (최하위)

```yaml
Priority: 🔵 P4 (당분간 불필요)
이유: 본인만 사용, 나중에
기간: 1주

→ 훨씬 나중에!
```

---

## 🎯 추천 구현 순서

### 🥇 Track 1: 필수 핵심 (2주)

**"UMIS 본질 구현 - Stewart의 2가지 감시"**

```yaml
Week 1: Graph + 순환 감지
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Day 1: Hot-Reload 완성 (P0)
    → 개발 생산성 확보
  
  Day 2-3: Neo4j + 패턴 관계 (P0)
    → Knowledge Graph 기본
    → 패턴 조합 자동 발견
  
  Day 4-5: 순환 감지 시스템 (P0)
    → query_history DB
    → 3회 반복 자동 감지
    → Stewart 개입
  
  완성도: 50% → 70%
  UMIS 구현: 30% → 65%

Week 2: 목표 정렬 + Hybrid 검색
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Day 1-2: 목표 정렬도 모니터링 (P0)
    → goal embedding
    → 60% 기준 자동 경고
    → Stewart 이탈 방지
  
  Day 3-5: Hybrid 검색 완성
    → Vector + Graph 통합
    → Steve에 적용
    → 전체 테스트
  
  완성도: 70% → 85%
  UMIS 구현: 65% → 80%

🎯 2주 후 상태:
  ✅ Stewart 순환 감지 작동
  ✅ Stewart 목표 정렬 작동
  ✅ Knowledge Graph 기본
  ✅ Hybrid 검색 가능
  
  → UMIS 핵심 80% 구현!
  → 실전 사용 가능!
```

---

### 🥈 Track 2: 확장 기능 (선택, +2주)

**"완전한 Multi-Agent + 학습"**

```yaml
Week 3: Multi-View + Meta-RAG
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Day 1-3: Multi-View 청킹 (P1)
    → 5개 agent view
    → Cross-agent 협업
  
  Day 4-5: Stewart Meta-RAG (P1)
    → 검증 규칙/품질 패턴
    → 3단계 자동 검증
  
  완성도: 85% → 92%

Week 4: 학습 시스템
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Day 1-3: 피드백 학습 (P2)
    → Query refinement
    → Weighted retrieval
  
  Day 4-5: 명확도 적응 (P2)
    → 적응형 RAG 전략
    → 자동 모드 전환
  
  완성도: 92% → 95%
  UMIS 구현: 80% → 95%

🎯 4주 후 상태:
  ✅ 완전한 UMIS RAG!
  ✅ 프로덕션 레디
  ✅ 모든 핵심 기능
```

---

## 📊 작업 우선순위 매트릭스

| 작업 | UMIS 필수 | 즉시 가치 | 복잡도 | 의존성 | 우선순위 |
|------|----------|----------|--------|--------|----------|
| **Hot-Reload** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 낮음 | 없음 | 🔴 P0 |
| **순환 감지** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 중간 | 없음 | 🔴 P0 |
| **목표 정렬** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 중간 | 순환감지 | 🔴 P0 |
| **Knowledge Graph** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 높음 | 없음 | 🔴 P0 |
| Multi-View | ⭐⭐⭐ | ⭐⭐⭐ | 중간 | Graph | 🟡 P1 |
| Meta-RAG | ⭐⭐⭐ | ⭐⭐⭐⭐ | 중간 | Graph | 🟡 P1 |
| 명확도 적응 | ⭐⭐⭐ | ⭐⭐ | 낮음 | 순환/목표 | 🟢 P2 |
| 피드백 학습 | ⭐⭐⭐ | ⭐⭐ | 중간 | 순환/목표 | 🟢 P2 |
| MCP Tool | ⭐⭐ | ⭐⭐⭐ | 높음 | 모두 | 🟢 P3 |
| 배포/패키징 | ⭐ | ⭐ | 낮음 | 모두 | 🔵 P4 |

---

## 🚀 최종 추천 실행 계획

### 💡 집중 전략: Track 1만 (2주)

```yaml
목표:
  "UMIS 핵심 80% 구현 → 즉시 실사용"
  
Week 1:
  Day 1 (월): Hot-Reload ✅
  Day 2-3 (화수): Knowledge Graph 기본
  Day 4-5 (목금): 순환 감지 시스템
  
  주말: 통합 테스트 및 검증

Week 2:
  Day 1-2 (월화): 목표 정렬도
  Day 3-5 (수목금): Hybrid 검색 완성
  
  주말: E2E 테스트, 실전 프로젝트

결과:
  ✅ Stewart 2가지 핵심 (순환, 목표)
  ✅ Knowledge Graph (패턴 조합)
  ✅ Hybrid 검색 (Vector + Graph)
  ✅ UMIS 80% 구현
  
  → 실전 사용 가능!
  → Track 2는 필요성 재평가 후
```

---

## 📅 상세 일정 (Track 1: 2주)

### Week 1

```
월요일 (Day 1): Hot-Reload 개발 환경
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[ ] 09:00-10:00  dev_watcher.py 완성
[ ] 10:00-11:00  증분 업데이트 로직
[ ] 11:00-12:00  에러 핸들링

[ ] 13:00-14:00  Makefile 완성
[ ] 14:00-15:00  실전 테스트 (YAML 수정)
[ ] 15:00-16:00  성능 최적화

✅ 완료: Hot-Reload 작동
    → YAML 수정 → 2초 → 반영! ⚡

화요일-수요일 (Day 2-3): Knowledge Graph
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Day 2:
[ ] 09:00-12:00  Neo4j Docker 설정
                 - 설치, 연결 테스트
                 - Python driver
[ ] 13:00-17:00  노드/관계 스키마
                 - Pattern, Case, AgentOutput
                 - 기본 관계 정의

Day 3:
[ ] 09:00-12:00  패턴 관계 데이터 작성
                 - pattern_relationships.yaml
                 - COMBINES_WITH 30개
                 - COUNTERS 10개
[ ] 13:00-17:00  Graph import
                 - Cypher 쿼리
                 - 관계 생성
                 - 검증

✅ 완료: Knowledge Graph 기본
    → 45개 패턴 관계

목요일-금요일 (Day 4-5): 순환 패턴 감지
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Day 4:
[ ] 09:00-12:00  query_history DB
                 - SQLite 스키마
                 - 자동 기록 로직
                 - LLM 주제 추출
[ ] 13:00-17:00  순환 감지 알고리즘
                 - 슬라이딩 윈도우
                 - 주제 유사도

Day 5:
[ ] 09:00-12:00  Stewart 개입 로직
                 - 3회 감지 → Nudge
                 - 4회 → 에스컬레이션
                 - 메시지 템플릿
[ ] 13:00-17:00  통합 테스트
                 - 순환 시나리오
                 - Graph 연동

✅ 완료: 순환 패턴 감지
    → UMIS 핵심 #1 구현!

주말: Week 1 통합 검증
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[ ] E2E 테스트
[ ] 버그 수정
[ ] 문서 업데이트
```

### Week 2

```
월요일-화요일 (Day 1-2): 목표 정렬도
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Day 1:
[ ] 09:00-12:00  Goal embedding
                 - 프로젝트 시작 시 자동
                 - goal_vector 저장
[ ] 13:00-17:00  Alignment 측정
                 - 매 쿼리 계산
                 - 5개 윈도우 평균
                 - query_history 통합

Day 2:
[ ] 09:00-12:00  Stewart 모니터링
                 - < 60% 자동 감지
                 - 이탈 쿼리 분석
                 - 경고 메시지
[ ] 13:00-17:00  통합 테스트
                 - 목표 이탈 시나리오
                 - 복구 테스트

✅ 완료: 목표 정렬도 모니터링
    → UMIS 핵심 #2 구현!

수요일-금요일 (Day 3-5): Hybrid 검색 완성
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Day 3:
[ ] 09:00-12:00  Graph 쿼리 구현
                 - 패턴 조합 검색
                 - 검증 체인 추적
[ ] 13:00-17:00  Vector + Graph 통합
                 - 결과 병합 알고리즘
                 - hybrid_search() 메서드

Day 4:
[ ] 09:00-12:00  Steve 통합
                 - search_hybrid_patterns()
                 - 패턴 조합 제안
[ ] 13:00-17:00  테스트 케이스
                 - "플랫폼 + 구독"
                 - "저가 + 채널"

Day 5:
[ ] 09:00-12:00  성능 최적화
                 - 쿼리 속도
                 - 캐싱
[ ] 13:00-17:00  E2E 통합 테스트
                 - 실전 시나리오
                 - 버그 수정

✅ 완료: Hybrid 검색
    → Vector + Graph 통합!

주말: Week 2 최종 검증
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[ ] 전체 시스템 테스트
[ ] 실전 프로젝트 1개
[ ] 품질 검증
[ ] 문서 완성

🎉 Track 1 완성!
   UMIS 핵심 80% 구현
   실전 사용 가능
```

---

## 🎯 작업 간 의존성 그래프

```
Phase 1 (완료) ✅
    ↓
    ├─→ Phase 2A (Hot-Reload) → 즉시 시작 가능 ⚡
    │   ↓
    │   (개발 생산성 10배)
    │
    ├─→ Phase 2B (Knowledge Graph) → 독립 시작 가능
    │   ↓
    │   ├─→ Phase 2C (순환 감지) → 병행 가능
    │   │   ↓
    │   │   └─→ Phase 2D (목표 정렬) → 순차
    │   │       ↓
    │   │       (UMIS 핵심 완성!)
    │   │
    │   └─→ Hybrid 검색 (Graph + Vector)
    │       ↓
    │       (패턴 조합 자동!)
    │
    └─→ Phase 3A (Multi-View) → Graph 후
        ↓
        └─→ Phase 3B (Meta-RAG) → Multi-View 후
            ↓
            (품질 자동화)

Phase 4A, 4B (학습) → 모두 완료 후
    ↓
    (장기 가치)

Phase 5, 6 (통합, 배포) → 훨씬 나중에
```

---

## 💡 핵심 의사결정 포인트

### 2주 후 (Track 1 완료 시)

```yaml
평가 질문:
  1. 순환 감지가 실제로 유용한가?
  2. 목표 정렬이 작업 품질 향상시키는가?
  3. Knowledge Graph가 패턴 조합 잘 제안하는가?
  4. 2주 투자 대비 가치는?

결정:
  높은 가치:
    → Track 2 진행 (Multi-View + Meta-RAG)
    → 완전한 UMIS 구현
  
  충분함:
    → Track 1에서 멈춤
    → 실전 사용 집중
    → 필요 시 개선
```

### 4주 후 (Track 2 완료 시)

```yaml
평가 질문:
  1. Multi-View가 필요한가?
  2. 자동 검증이 시간 절약하는가?
  3. 피드백 학습 효과 있는가?
  
결정:
  MCP Tool 개발 여부
  배포 패키징 여부
  추가 기능 개발 여부
```

---

## 🎯 즉시 실행 (지금!)

### Step 1: Hot-Reload 완성 (오늘, 2시간)

```bash
# 1. dev_watcher.py 테스트
make dev

# 새 터미널에서
# VS Code: data/raw/umis_business_model_patterns_v6.2.yaml
# 아무거나 수정 (주석 추가)
# Ctrl+S

# 원래 터미널에서 자동 업데이트 확인!

# 2. 검증
make query QUERY="플랫폼"
# → 변경 사항 반영됨?

# 3. 버그 수정 및 안정화
```

### Step 2: Week 1 시작 (내일부터)

```bash
# Day 2-3: Neo4j
docker run -d \
  --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/umis_rag_2024 \
  neo4j:5-community

# 패턴 관계 정의
# umis_rag/graph/pattern_relationships.yaml 작성

# Day 4-5: 순환 감지
# umis_rag/stewart/circular_detector.py 구현
```

---

## 📋 체크리스트 요약

### P0 (필수, 2주)

```
Week 1:
  [ ] Day 1: Hot-Reload 완성
  [ ] Day 2-3: Knowledge Graph 기본
  [ ] Day 4-5: 순환 패턴 감지

Week 2:
  [ ] Day 1-2: 목표 정렬도 모니터링
  [ ] Day 3-5: Hybrid 검색 완성
  
  [ ] 주말: 전체 통합 테스트

✅ 완료 시: UMIS 핵심 80% 구현!
```

### P1 (선택, +2주)

```
Week 3:
  [ ] Multi-View 청킹
  [ ] Meta-RAG 검증

Week 4:
  [ ] 피드백 학습
  [ ] 명확도 적응

✅ 완료 시: UMIS 95% 구현!
```

### P2-P4 (나중에)

```
훨씬 나중에:
  [ ] MCP Tool 통합
  [ ] 배포 패키징
  [ ] 문서 완성
```

---

## 🎯 최종 추천

```yaml
즉시 (오늘):
  ✅ Hot-Reload 완성 및 테스트
  ✅ 실전 사용 시작 (Dual Mode)
  
  → 개발 환경 확보
  → 피드백 루프 체감

이번 주:
  🔄 Day 1 완료 (Hot-Reload)
  🔄 주말 계획 수립
  
  → Week 1 준비

다음 2주:
  🔄 Track 1 집중 개발
  
  → UMIS 핵심 80% 완성
  → 실전 사용 시작

그 후:
  ⏸️  Track 2 필요성 재평가
  
  → 실사용 경험 기반 결정
```

---

## 결론

**당신의 요구사항에 최적화된 계획:**

```yaml
✅ 패키징/배포: 최하위 (P4)
✅ 핵심 기능: 최우선 (P0)
   - 순환 감지
   - 목표 정렬
   - Knowledge Graph
   
✅ 개발 환경: 즉시 (Hot-Reload)
✅ 명확한 순서: 의존성 기반
✅ 유연한 결정: 2주 후 재평가
```

**Track 1 (2주)로 시작하시겠어요?** 🚀

오늘 Hot-Reload부터 완성할까요?
