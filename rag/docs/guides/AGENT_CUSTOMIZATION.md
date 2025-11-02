# Agent 이름 커스터마이징

**대상:** 모든 UMIS 사용자  
**방법:** agent_names.yaml 파일 수정  
**적용:** Cursor에서 즉시

---

## 🎯 왜 필요한가?

```yaml
문제:
  "Observer, Explorer가 너무 기계적이야"
  "우리 팀원 이름으로 쓰고 싶어"
  "한국어로 표시하고 싶어"

해결:
  agent_names.yaml 파일 수정
  → Cursor가 자동 인식
  → 즉시 반영!
```

---

## ⚡ 30초 커스터마이징

### Step 1: 파일 열기

```
Cursor에서:
  agent_names.yaml 열기
```

### Step 2: 이름 변경

```yaml
agents:
  explorer:
    display_name: "Alex"  # ← 여기 수정!
```

### Step 3: 저장

```
Cmd+S
```

**끝!** 이제:
- 표시: "Alex가 패턴을 찾습니다..." ✅
- 호출: "@Alex, 패턴 찾아봐" ✅

**양방향 작동!** ✨

---

## 📝 커스터마이징 예시

### 예시 1: 팀원 이름

```yaml
agents:
  observer:
    display_name: "Jane"
  
  explorer:
    display_name: "Alex"
  
  quantifier:
    display_name: "Mike"
```

**사용:**
```
User: "@Jane, 시장 분석해"
→ Observer 실행

User: "@Alex, 기회 찾아봐"
→ Explorer 실행
```

**결과:**
```
Jane이 시장을 관찰합니다...
Alex가 subscription_model 패턴을 발견했습니다!
Mike가 시장 규모를 계산합니다...
```

**양방향:**
```
호출: "@Jane" → Observer
표시: Observer → "Jane"
→ 완벽! ✨
```

---

### 예시 2: 한국어

```yaml
agents:
  observer:
    display_name: "관찰자"
  
  explorer:
    display_name: "탐색자"
  
  quantifier:
    display_name: "계산가"
  
  validator:
    display_name: "검증가"
  
  guardian:
    display_name: "관리자"
```

**결과:**
```
관찰자가 시장을 관찰합니다...
탐색자가 패턴을 찾습니다...
계산가가 시장 규모를 계산합니다...
```

---

### 예시 3: 캐릭터/봇

```yaml
agents:
  observer:
    display_name: "MarketBot"
  
  explorer:
    display_name: "OpportunityFinder"
  
  quantifier:
    display_name: "NumberCruncher"
```

**결과:**
```
MarketBot이 시장을 관찰합니다...
OpportunityFinder가 기회를 찾습니다...
NumberCruncher가 계산합니다...
```

---

## 🔧 Cursor 통합

### .cursorrules 자동 반영

**이미 설정되어 있습니다!**

```yaml
Cursor가 자동으로:
  1. agent_names.yaml 읽기
  2. display_name 사용
  3. 메시지에 반영
  
사용자:
  YAML 수정만!
```

---

## 💡 고급 활용

### 프로젝트별 다른 이름

```yaml
# 프로젝트 A: 팀원 이름
display_name: "Jane", "Alex", ...

# 프로젝트 B: 한국어
display_name: "관찰자", "탐색자", ...

# 프로젝트 C: 공식 ID
display_name: "Observer", "Explorer", ...
```

**변경:**
```
Cursor에서 agent_names.yaml 수정
→ Cmd+S
→ 다음 분석부터 적용!
```

---

## 🎯 기본 vs 커스텀

```yaml
기본 (agent_names.yaml 안 건드림):
  Observer, Explorer, Quantifier, Validator, Guardian
  
  → 공식적, 명확함

커스텀 (agent_names.yaml 수정):
  자기 이름, 한국어, 봇 이름 등
  
  → 개인화, 친근함
  
둘 다:
  내부 ID는 observer, explorer (고정)
  표시만 바뀜!
```

---

## 📋 전체 에이전트 목록

```yaml
observer:
  역할: 시장 구조 관찰
  기본: Observer
  예시: Jane, 관찰자, MarketBot

explorer:
  역할: 기회 발굴
  기본: Explorer
  예시: Alex, 탐색자, OpportunityBot

quantifier:
  역할: 정량 분석
  기본: Quantifier
  예시: Mike, 계산가, DataBot

validator:
  역할: 데이터 검증
  기본: Validator
  예시: Sarah, 검증가, QualityBot

guardian:
  역할: 품질 관리
  기본: Guardian
  예시: Tom, 관리자, GuardBot
```

---

## 🚀 지금 바로 시도!

```
1. agent_names.yaml 열기
2. display_name 수정
3. Cmd+S
4. Cursor Composer로 분석
   → 변경된 이름으로 표시!
```

**개인화된 UMIS!** ✨

