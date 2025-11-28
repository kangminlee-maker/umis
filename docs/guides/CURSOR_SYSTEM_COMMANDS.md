# Cursor IDE 시스템 명령어 가이드

## 🎯 설계 철학

### **자동 실행 vs 명시적 명령**

**❌ 자동 실행의 문제점:**
- LLM이 injection attack으로 오해할 수 있음
- 사용자 동의 없는 실행은 신뢰 문제
- 예측 불가능한 동작

**✅ 시스템 명령어의 장점:**
- 명확한 의도 표현
- 사용자 명시적 동의
- LLM 혼동 없음
- 안전하고 예측 가능

## 📋 시스템 명령어

### **Prefix: `/umis` 또는 `!umis`**

```bash
/umis setup     # 시스템 설치
/umis status    # 설치 상태 확인
/umis help      # 도움말
/umis rebuild   # System RAG 재구축
/umis tools     # 도구 목록
```

---

## 🚀 사용 시나리오

### **1. 신규 Fork 후 첫 사용**

```
👤 사용자: "@Explorer, 음악 스트리밍 시장 분석해줘"

🤖 AI (설치 감지):
   [자동 체크 실행]
   ls data/chroma_db/system_knowledge/ 2>&1
   
   ❌ 오류 감지: No such file or directory
   
   🚨 UMIS가 설치되지 않았습니다!
   
   신규 fork를 감지했습니다.
   사용하시려면 먼저 설치가 필요합니다 (2-3분 소요).
   
   다음 명령어를 입력해주세요:
   
   ```
   /umis setup
   ```
   
   또는
   
   ```
   !umis setup
   ```

👤 사용자: "/umis setup"

🤖 AI (설치 실행):
   [python setup/setup.py 실행]
   
   🚀 UMIS v7.11.1 설치 시작
   📦 Python 패키지 설치 중...
   🔧 System RAG 구축 중...
   ✅ 설치 완료!
   
   다음 단계:
   1. .env 파일에 OPENAI_API_KEY 입력
      받기: https://platform.openai.com/api-keys
   2. 원하는 작업을 다시 요청해주세요

👤 사용자: "@Explorer, 음악 스트리밍 시장 분석해줘"

🤖 AI:
   ✅ 설치 확인 완료
   
   [Onboarding 진행]
   → tool:onboarding:quick_start 로드
   → tool:explorer:complete 로드
   → 작업 수행
```

---

### **2. 설치 상태 확인**

```
👤 사용자: "/umis status"

🤖 AI:
   [체크 실행]
   ls data/chroma_db/system_knowledge/ 2>&1
   ls .env 2>&1
   python3 scripts/query_system_rag.py --list 2>&1
   
   ✅ UMIS 설치 완료
   
   📊 상태:
   - System RAG: 19개 도구
   - .env: 설정됨
   - ChromaDB: 정상
   
   사용 준비 완료!
```

---

### **3. System RAG 재구축**

```
👤 사용자: "/umis rebuild"

🤖 AI:
   [재구축 실행]
   python3 scripts/sync_umis_to_rag.py
   python3 scripts/build_system_knowledge.py
   
   🔧 System RAG 재구축 중...
   ✅ 완료! 19개 도구 업데이트됨
```

---

### **4. 도구 목록 확인**

```
👤 사용자: "/umis tools"

🤖 AI:
   [도구 목록 출력]
   python3 scripts/query_system_rag.py --list
   
   📋 사용 가능한 도구 키 (19개):
   
   Onboarding (4개):
   - tool:onboarding:quick_start
   - tool:onboarding:state_machine
   - tool:onboarding:agent_essentials
   - tool:onboarding:workflow_primer
   
   System (9개):
   - tool:system:system_architecture
   - tool:system:system
   - ...
   
   Complete (6개):
   - tool:observer:complete
   - tool:explorer:complete
   - ...
```

---

## 🔧 .cursorrules 구조

### **00. SYSTEM COMMANDS (Line 7-66)**

```yaml
system_commands:
  prefix: "/umis"
  alternative_prefix: "!umis"
  
  commands:
    setup:
      triggers: ["/umis setup", "!umis setup"]
      action: "python setup/setup.py"
    
    status:
      triggers: ["/umis status"]
      checks: ["data/chroma_db/", ".env"]
    
    help:
      triggers: ["/umis help"]
      outputs: "명령어 도움말"
```

### **01. INSTALLATION CHECK (Line 68-114)**

```yaml
installation_check:
  when: "첫 사용자 요청 시 (시스템 명령어 제외)"
  
  detection:
    check_command: "ls data/chroma_db/system_knowledge/ 2>&1"
    
    signals:
      not_installed: "No such file or directory"
      installed: "chroma.sqlite3"
  
  response_when_not_installed:
    message: "🚨 UMIS 미설치 → /umis setup 실행 안내"
    block_other_requests: true
    allow_commands: ["/umis", "!umis"]
```

---

## ⚡ 핵심 개선사항

### **Before (강제 실행)**

```yaml
mandatory_preflight:
  rule: "NEVER process any user request without completing this check first"
  priority: "CRITICAL"
  
  if_any_fails:
    action: "즉시 설치 시작 (사용자 요청 무시)"
```

**문제점:**
- ❌ LLM injection 우려
- ❌ 사용자 동의 없음
- ❌ 예측 불가능

### **After (시스템 명령어)**

```yaml
system_commands:
  prefix: "/umis"
  
  setup:
    triggers: ["/umis setup"]
    action: "python setup/setup.py"
```

**장점:**
- ✅ 명확한 의도 표현
- ✅ 사용자 명시적 동의
- ✅ LLM 혼동 없음
- ✅ 안전하고 예측 가능

---

## 📊 사용자 경험 비교

### **강제 실행 방식**
```
사용자: "시장 분석해줘"
AI: [자동 설치 시작] ← 사용자 동의 없음
```

**문제:**
- 사용자가 뭔가 실행되는지 모름
- 신뢰 문제
- 중단 불가능

### **시스템 명령어 방식**
```
사용자: "시장 분석해줘"
AI: "설치가 필요합니다. '/umis setup'을 입력해주세요"
사용자: "/umis setup" ← 명시적 동의
AI: [설치 시작]
```

**장점:**
- 사용자가 무슨 일이 일어날지 명확히 앎
- 신뢰 확보
- 원하면 중단 가능

---

## 🎨 Prefix 선택 이유

### **`/umis` 선택**

**이유:**
- Discord, Slack 같은 채팅 도구의 표준
- 명확한 시스템 명령 구분
- 타이핑 편리 (Shift 불필요)

**대안:**
- `!umis` (IRC 스타일)
- `#umis:` (명시적이지만 긴 편)
- `@umis` (Agent 멘션과 혼동 가능)

---

## ✅ 최종 효과

### **안전성**
- LLM injection 우려 제거
- 명확한 명령 구분
- 예측 가능한 동작

### **사용성**
- 직관적인 명령어
- 명확한 피드백
- 쉬운 디버깅

### **신뢰성**
- 사용자 명시적 동의
- 투명한 프로세스
- 완전한 통제권

---

## 🚀 구현 완료

**파일 수정:**
- ✅ `.cursorrules` (330줄 → 290줄 예상)
- ✅ 시스템 명령어 섹션 추가
- ✅ 강제 실행 제거
- ✅ 명확한 감지 → 안내 → 실행 플로우

**사용자 경험:**
- ✅ 신규 fork: 감지 → `/umis setup` 안내 → 실행
- ✅ 설치 완료: 바로 작업 수행
- ✅ 상태 확인: `/umis status` 언제든지 가능

**보안 & 신뢰:**
- ✅ LLM injection 불가능
- ✅ 사용자 동의 필수
- ✅ 투명한 프로세스
