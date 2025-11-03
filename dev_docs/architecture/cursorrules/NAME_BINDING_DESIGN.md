# Agent Name 바인딩 설계

**문제:** umis_guidelines.yaml name 필드 하드코딩

---

## 🔍 현재 문제

```yaml
umis_guidelines.yaml:
  agents:
    - id: Observer
      name: "Albert"  # 하드코딩!

config/agent_names.yaml:
  observer: Jane  # 커스터마이징

문제:
  • guidelines의 "Albert" 고정
  • agent_names의 "Jane" 무시됨
  • 불일치! 🚨
```

---

## 💡 해결 방법

### Option A: 참조 표시 (YAML 주석)

```yaml
# umis_guidelines.yaml

_meta:
  agent_names_source: config/agent_names.yaml
  note: "name 필드는 config/agent_names.yaml 값 사용 (동적 바인딩)"

agents:
  - id: Observer
    name: "Albert"  # @agent_names.observer (기본값)
    name_binding: "agent_names.observer"
```

**장점:**
```yaml
✅ YAML 구문 유지
✅ 참조 명시
✅ 기본값 표시

동작:
  AI가 읽을 때:
    1. umis_guidelines.yaml 읽기
    2. name_binding 발견
    3. config/agent_names.yaml 자동 읽기
    4. 실제 name 적용
```

---

### Option B: 메타데이터 참조

```yaml
# umis_guidelines.yaml 최상단

_agent_name_binding:
  description: "Agent name은 config/agent_names.yaml 동적 바인딩"
  mapping:
    Observer: "agent_names.observer"
    Explorer: "agent_names.explorer"
    Quantifier: "agent_names.quantifier"
    Validator: "agent_names.validator"
    Guardian: "agent_names.guardian"

agents:
  - id: Observer
    default_name: "Albert"  # 기본값 (config/agent_names.yaml 없을 때)
```

**장점:**
```yaml
✅ 중앙 집중 매핑
✅ 명확한 바인딩
✅ 기본값 Fallback
```

---

### Option C: 단순 주석 (추천!) ⭐

```yaml
# umis_guidelines.yaml

# ========================================
# Agent Names: config/agent_names.yaml에서 커스터마이징
# ========================================
# 
# 기본값: Albert, Steve, Bill, Rachel, Stewart
# 커스터마이징: config/agent_names.yaml 수정
# 
# AI 주의: name 필드는 config/agent_names.yaml 우선!
# ========================================

agents:
  - id: Observer
    name: "Albert"  # Default (agent_names.observer)
    role: "Market Structure Observer"
    ...
  
  - id: Explorer
    name: "Steve"  # Default (agent_names.explorer)
    role: "Market Explorer"
    ...
```

**장점:**
```yaml
✅ 가장 단순
✅ YAML 구문 깔끔
✅ AI가 주석 이해
✅ 기본값 명시

동작:
  AI:
    1. 주석 읽기
       "name 필드는 config/agent_names.yaml 우선!"
    
    2. config/agent_names.yaml 자동 읽기
       observer: Jane
    
    3. 실제 사용:
       Observer → Jane (agent_names 우선)
       Albert → 무시
```

---

## 🎯 최종 추천

**Option C: 단순 주석**

```yaml
umis_guidelines.yaml 수정:
  
  최상단 주석:
    # Agent Names: config/agent_names.yaml 우선!
  
  각 Agent:
    name: "Albert"  # Default (agent_names.observer)

.cursorrules:
  이미 반영됨:
    # name: Default name → config/agent_names.yaml로 커스터마이징

config/agent_names.yaml:
  변경 없음

AI 동작:
  1. umis_guidelines.yaml 읽기
  2. 주석 이해: "agent_names 우선"
  3. config/agent_names.yaml 읽기
  4. 실제 name 적용
```

**실행:**
```yaml
Step 4.5: umis.yaml 주석 추가
  # Agent Names 섹션 추가
  # 각 Agent name 필드에 참조 주석
```

---

**당신의 지적이 정확했습니다!** ✨

실행하시겠어요? 🚀

