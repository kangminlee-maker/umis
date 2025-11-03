# Week 4: Memory (Guardian) 구현 계획

**날짜:** 2024-11-03  
**기간:** 5일 (예상)  
**우선순위:** P1

---

## 🎯 목표

### Guardian Memory System

```yaml
목적:
  • 순환 감지 (QueryMemory)
  • 목표 정렬 (GoalMemory)
  • 프로세스 자동 감시

기반:
  ✅ Dual-Index (Week 2)
  ✅ Knowledge Graph (Week 3)
  ✅ schema_registry.yaml (Memory 스키마 정의됨)
```

---

## 📋 작업 계획

### Day 1-2: QueryMemory (순환 감지)

```yaml
목표:
  반복되는 질문/쿼리 감지하여 순환 방지

구현:
  1. QueryMemory Collection (Chroma)
     • memory_id: MEM-xxxxxxxx
     • query_text: 질문 텍스트
     • query_embedding: 3072 dim
     • query_topic: 주제 추출
     • repetition_count: 반복 횟수
  
  2. 순환 감지 로직
     • Embedding 유사도 계산
     • 임계값 0.9 이상 = 유사 질문
     • repetition_count 증가
  
  3. Guardian 알림
     • 3회 이상 반복 → 경고
     • "같은 질문을 반복하고 있습니다"

파일:
  • umis_rag/guardian/__init__.py
  • umis_rag/guardian/query_memory.py
  • scripts/test_query_memory.py

산출물:
  ✅ QueryMemory 클래스
  ✅ 순환 감지 로직
  ✅ 테스트 통과
```

### Day 3-4: GoalMemory (목표 정렬)

```yaml
목표:
  사용자 목표와 현재 작업의 정렬도 평가

구현:
  1. GoalMemory Collection (Chroma)
     • memory_id: MEM-xxxxxxxx
     • goal_text: 목표 설명
     • goal_embedding: 3072 dim
     • alignment_score: 정렬도 (0-1)
  
  2. 정렬도 계산
     • 목표 embedding vs 현재 작업 embedding
     • Cosine similarity 계산
     • 0.7 미만 → 경고
  
  3. Guardian 가이드
     • "현재 작업이 목표에서 벗어났습니다"
     • "목표 재확인이 필요합니다"

파일:
  • umis_rag/guardian/goal_memory.py
  • scripts/test_goal_memory.py

산출물:
  ✅ GoalMemory 클래스
  ✅ 정렬도 계산 로직
  ✅ 테스트 통과
```

### Day 5: Memory-RAG 통합

```yaml
목표:
  Memory + RAG + LLM Hybrid로 Guardian 자동화

구현:
  1. GuardianMemory 통합 클래스
     • QueryMemory + GoalMemory
     • RAG 기반 과거 평가 검색
     • LLM으로 최종 판단
  
  2. Guardian 워크플로우
     • 입력: Deliverable
     • 순환 체크 (QueryMemory)
     • 목표 정렬 체크 (GoalMemory)
     • 과거 평가 검색 (RAE Index, 선택)
     • 최종 판단 (LLM)
  
  3. 자동 알림
     • 순환 감지 시
     • 목표 이탈 시
     • 품질 문제 시

파일:
  • umis_rag/guardian/memory.py
  • umis_rag/guardian/guardian_rag.py
  • scripts/test_guardian_memory.py

산출물:
  ✅ GuardianMemory 클래스
  ✅ Guardian RAG 통합
  ✅ 자동 감시 시스템
  ✅ 테스트 통과
```

---

## 📊 schema_registry.yaml 준수

### QueryMemory

```yaml
collection_name: "query_memory"

fields:
  memory_id: "MEM-[a-z0-9]{8}"
  query_text: string
  query_embedding: vector (3072)
  query_topic: string
  repetition_count: int (default: 1)
  version: string
  created_at: datetime
```

### GoalMemory

```yaml
collection_name: "goal_memory"

fields:
  memory_id: "MEM-[a-z0-9]{8}"
  goal_text: string
  goal_embedding: vector (3072)
  alignment_score: float (0-1)
  version: string
  created_at: datetime
```

---

## 🧪 테스트 계획

### QueryMemory Tests

```yaml
1. 순환 감지:
   • 같은 질문 3번 → repetition_count = 3
   • 유사 질문 감지 (similarity > 0.9)

2. 주제 추출:
   • 질문 → 주제 자동 추출

3. 메모리 조회:
   • 과거 질문 검색
```

### GoalMemory Tests

```yaml
1. 정렬도 계산:
   • 목표 vs 작업 similarity
   • 0-1 점수

2. 이탈 감지:
   • alignment < 0.7 → 경고

3. 목표 업데이트:
   • 새로운 목표 저장
```

### 통합 Tests

```yaml
1. Guardian 워크플로우:
   • QueryMemory 체크
   • GoalMemory 체크
   • 최종 판단

2. 자동 알림:
   • 순환 시
   • 이탈 시
```

---

## 💡 기대 효과

### 1. 순환 방지

```yaml
Before:
  "이미 여러 번 물어본 질문인데..."
  "또 같은 작업을 반복하고 있네"

After:
  Guardian: "이 질문은 3번째입니다"
  Guardian: "이전 답변을 참고하세요"
```

### 2. 목표 정렬

```yaml
Before:
  "지금 하는 작업이 목표와 맞나?"
  "너무 세부사항에 빠진 것 같은데"

After:
  Guardian: "현재 작업 정렬도: 0.65 (낮음)"
  Guardian: "목표를 재확인하시겠습니까?"
```

### 3. 프로세스 자동화

```yaml
Before:
  사용자가 직접 확인 필요

After:
  Guardian이 자동 감시
  문제 발생 시 자동 알림
  최적 경로 제안
```

---

## 🎯 완료 기준

```yaml
필수:
  ✅ QueryMemory 구현
  ✅ GoalMemory 구현
  ✅ Memory Collections 생성
  ✅ 순환 감지 작동
  ✅ 정렬도 계산 작동
  ✅ 테스트 통과

선택:
  □ RAE Index 통합 (향후)
  □ LLM 판단 강화 (향후)
  □ Learning Loop (향후)
```

---

## 🚀 시작

**지금 시작:**

```
"Week 4 Day 1-2 QueryMemory를 구현하자.
schema_registry.yaml의 query_memory 스펙을 따라서"
```

---

**작성:** UMIS Team  
**날짜:** 2024-11-03  
**상태:** Week 4 계획 완료, 시작 준비 ✅


