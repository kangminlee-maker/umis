# UMIS RAG 구현 계획 (Cursor 기반)

**⚠️ 노트:** 초기 12일 계획 (참조용)  
**최신:** architecture/planning/IMPLEMENTATION_ROADMAP_V2.md 참조!

**현재 (v6.3.0-alpha):**
- ✅ Vector RAG (Explorer용)

**v2.0 계획 (ROADMAP_V2 참조):**
- 📋 8개 개선안 기반
- 📋 Phase 1-4 (6주)
- 📋 4-Layer + 6개 횡단 관심사

**대상:** 코딩 못 하는 UMIS 사용자  
**도구:** Cursor Composer + Agent 모드  
**업데이트:** 2025-11-02 (Architecture v2.0)

---

**⭐ 최신 로드맵:**  
`architecture/planning/IMPLEMENTATION_ROADMAP_V2.md`

---

## 🎯 핵심 철학

```yaml
개발 = 사용:
  • Cursor Composer로 UMIS 분석
  • 발견: "데이터 추가 필요"
  • Cursor에게: "추가해줘"
  • AI 자동 처리 (YAML 수정 + RAG 재구축)
  • 즉시 사용

피드백 루프:
  발견 → 요청 → 자동 처리 → 30초 → 사용
  
  → 대화만으로 개발! ✨
```

---

## 📅 12일 계획 (Cursor 중심)

### Day 1-2: Cursor 자동화 설정

**목표:** .cursorrules로 완전 자동화

```yaml
Cursor에게 요청:
  "YAML 수정 시 자동으로 RAG 재구축하는 
   .cursorrules를 만들어줘"

AI가 생성:
  ✅ YAML 저장 → 자동 재구축
  ✅ Explorer 패턴 필요 → 자동 RAG 검색
  ✅ "데이터 추가" 요청 → 자동 처리

완료 기준:
  ✅ Cursor Composer로 UMIS 분석
  ✅ RAG 자동 활용
  ✅ 데이터 추가 자동
```

### Day 3-5: Knowledge Graph (Cursor로!)

**목표:** 패턴 조합 관계 정의

```yaml
Cursor에게 요청:
  "platform + subscription 조합이 
   Amazon Prime처럼 시너지 있다는 걸
   Knowledge Graph로 표현해줘"

AI가 작업:
  1. Neo4j 설정 (Docker)
  2. pattern_relationships.yaml 생성
  3. Graph에 관계 저장
  4. 조합 검색 기능 구현

완료 기준:
  ✅ "플랫폼 + 구독" → Amazon Prime 제안
  ✅ Cursor 대화로 관계 추가 가능
```

### Day 6-7: Guardian 순환 감지 (Cursor로!)

**목표:** 3회 반복 자동 감지

```yaml
Cursor에게 요청:
  "같은 주제로 3번 반복하면 
   Guardian이 자동으로 감지하게 해줘"

AI가 구현:
  1. QueryMemory 컬렉션
  2. 유사 쿼리 검색 (Memory-RAG)
  3. LLM으로 순환 판단
  4. Guardian 개입 메시지

완료 기준:
  ✅ "플랫폼" 3회 → Guardian 경고
  ✅ Cursor 대화로 테스트
```

### Day 8-9: 목표 정렬 (Cursor로!)

**목표:** 60% 기준 자동 모니터링

```yaml
Cursor에게 요청:
  "프로젝트 목표에서 이탈하면
   Guardian이 경고하게 해줘"

AI가 구현:
  1. GoalMemory 컬렉션
  2. 정렬도 측정 (Memory-RAG)
  3. < 60% 자동 경고
  4. 이탈 이유 LLM 분석

완료 기준:
  ✅ "피아노" 목표인데 "바이올린" → 경고
  ✅ Cursor에서 즉시 확인
```

### Day 10-12: Modular RAG (Cursor로!)

**목표:** 6개 Agent view 청킹

```yaml
Cursor에게 요청:
  "배달의민족 사례를 
   Observer는 구조 관점,
   Explorer는 기회 관점,
   Quantifier는 정량 관점으로
   각각 다르게 청킹해줘"

AI가 구현:
  1. 6-View 청킹 로직
  2. Agent별 Retriever
  3. source_id 협업
  4. 통합 테스트

완료 기준:
  ✅ Explorer → Quantifier 자동 협업
  ✅ Cursor 대화로 모든 Agent 활용
```

---

## 💡 Cursor만으로 개발하는 방법

### 패턴 1: 기능 요청

```
Cursor Composer:

You: "Explorer가 패턴 조합을 찾을 수 있게 해줘.
     platform + subscription → Amazon Prime 같은 거"

AI: 알겠습니다. Knowledge Graph를 구축하겠습니다.
    
    1. Neo4j 설정 (Docker)
    2. 패턴 관계 정의
    3. 조합 검색 구현
    
    진행할까요?

You: "응"

AI: [Agent 모드로 자동 실행]
    • Docker Neo4j 실행
    • pattern_relationships.yaml 생성
    • Python 코드 작성
    • 테스트 완료
    
    ✅ 완료!

→ 대화만으로 기능 추가! 🎯
```

### 패턴 2: 데이터 추가

```
분석 중:

You: "코웨이 사례에 해지율 3-5% 추가해"

AI: [자동으로]
    1. YAML 열기
    2. 위치 찾기
    3. 추가
    4. 저장
    5. RAG 재구축
    
    ✅ 완료!

→ 즉시 사용 가능! ⚡
```

### 패턴 3: 버그 수정

```
You: "순환 감지가 너무 민감해. 
     3회가 아니라 4회로 바꿔줘"

AI: [자동으로]
    1. circular_detector.py 찾기
    2. 임계값 3 → 4 수정
    3. 테스트
    
    ✅ 변경 완료!

→ 대화로 조정! 🎯
```

---

## 📊 12일 요약 (Cursor 중심)

```
Day 1-2: .cursorrules 자동화
  → YAML → RAG 자동
  
Day 3-5: Knowledge Graph
  → Cursor 대화로 관계 정의
  
Day 6-7: 순환 감지
  → Cursor로 기능 요청
  
Day 8-9: 목표 정렬
  → Cursor로 구현
  
Day 10-12: Modular RAG
  → Cursor로 6-View 청킹

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
12일 후: UMIS RAG v1.0 완성!
방법: Cursor 대화만! 코딩 불필요! ✨
```

---

## 🎯 성공 기준

```yaml
기술:
  ✅ 기능 작동 (중요하지만 2순위)

사용자 경험 (최우선!):
  ✅ Cursor Composer로 모든 것
  ✅ 대화만으로 개발 가능
  ✅ 30초 피드백 루프
  ✅ 코딩 지식 불필요
  
  → 완벽한 인라인 어셈블러! ⚡
```

---

## 결론

**모든 개발을 Cursor 대화로!**

```
설정: .cursorrules (Cursor가 만들어줌)
구현: Cursor에게 요청
테스트: Cursor에서 확인
개선: Cursor에게 "수정해줘"

→ 12일 동안 대화만! 🎯
```

**다음:** `DETAILED_TASK_LIST.md`도 Cursor 중심으로 재작성

