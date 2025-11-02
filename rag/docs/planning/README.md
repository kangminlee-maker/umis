# UMIS RAG 구현 계획

**대상:** Cursor 사용자 (코딩 불필요)  
**방법:** Cursor Composer + Agent 모드  
**기간:** 12일

---

## 🎯 핵심 방식

```yaml
개발 방법:
  ❌ Cursor 명령
  ❌ Python 코딩
  
  ✅ Cursor Composer (Cmd+I)
  ✅ 대화로 요청
  ✅ AI가 자동 실행
  
  → 100% 대화! ✨
```

---

## 📋 12일 계획 요약

### Week 1: 기본 자동화

```
Day 1-2: Cursor 자동화
  → .cursorrules 설정
  → YAML → RAG 자동

Day 3-5: Knowledge Graph
  → Cursor에게 "패턴 조합 관계 만들어줘"
  → AI가 Neo4j + 관계 생성
```

### Week 2: Guardian 감시

```
Day 6-7: 순환 감지
  → "3회 반복 감지해줘"
  → AI가 Memory-RAG 구현

Day 8-9: 목표 정렬
  → "목표 이탈 경고해줘"
  → AI가 GoalMemory 구현
```

### Week 3: Multi-Agent

```
Day 10-12: 6-View RAG
  → "각 Agent별 관점으로 청킹해줘"
  → AI가 Modular RAG 구현
```

---

## 💡 실제 사용 예시

### 기능 추가

```
Cursor Composer:

"Guardian이 순환 패턴을 감지하게 해줘.
 같은 주제로 3번 반복하면 자동으로 경고"

→ AI가 구현
→ 테스트
→ 완료!

→ 대화 한 번! 🎯
```

### 데이터 추가

```
"코웨이에 해지율 데이터 추가해"

→ AI가 자동 처리
→ 즉시 반영

→ 30초! ⚡
```

---

## 📖 상세 문서

**Cursor 전용 계획:**
- CURSOR_IMPLEMENTATION_PLAN.md (이 폴더)
  - 12일 Cursor 워크플로우
  - 대화로 구현하는 방법

**백업 (개발자용):**
- DETAILED_TASK_LIST_DEV_ONLY.md.backup
- IMPLEMENTATION_PLAN_DEV_ONLY.md.backup
  - Cursor, Python 코드 등
  - 참조용으로만

---

## 🚀 시작

**Cursor Composer (Cmd+I):**

```
"UMIS RAG 개발을 시작하자.
 
 첫 번째로 .cursorrules를 설정해서
 YAML 수정 시 자동으로 RAG가 재구축되게 해줘"
```

**그게 전부!** 🎉

AI가 모든 것을 처리합니다!

