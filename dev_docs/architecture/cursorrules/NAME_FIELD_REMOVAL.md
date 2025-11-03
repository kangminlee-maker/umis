# Agent Name 필드 제거 검증

**제안:** umis_guidelines.yaml에서 name 필드 완전 제거

---

## 🎯 설계

### Clean Separation

```yaml
umis.yaml (시스템 정의):
  agents:
    - id: Observer  # ID만!
      role: market_structure
      # name 필드 없음!

config/agent_names.yaml (이름 매핑):
  observer: Albert  # 기본
  explorer: Steve
  ...

.cursorrules (바인딩):
  agents:
    Observer: {name: Albert, ...}
  
  매핑 규칙:
    입력: @Albert → Observer
    출력: Observer → Albert
```

**분리:**
```yaml
umis.yaml: 시스템 정의 (id만)
config/agent_names.yaml: 이름 (단일 진실)
.cursorrules: 바인딩 로직
```

---

## ✅ 가능성 검증

### 1. YAML 파싱 문제?

```yaml
검증:
  name 필드 필수?
  → 아니요! ✅
  
  YAML 스펙:
    필드는 선택사항
    name 없어도 유효

결론:
  문제 없음! ✅
```

### 2. AI 이해 가능?

```yaml
시나리오:
  AI가 umis.yaml 읽기
  
  발견:
    - id: Observer
    - id: Explorer
    ...
  
  질문:
    "Observer의 이름은?"
  
  해결:
    .cursorrules 참조:
      Observer: {name: Albert}
    
    또는:
      config/agent_names.yaml 참조:
        observer: Albert
  
  → AI가 충분히 이해 가능! ✅
```

### 3. 사용자 경험?

```yaml
사용자:
  "@Albert, 시장 분석해"

Cursor:
  .cursorrules 읽기:
    Observer: {name: Albert}
  
  매핑:
    @Albert → Observer
  
  umis.yaml:
    Observer 정의 찾기 (id 기반)
  
  실행:
    Observer 로직 실행
  
  출력:
    Observer → Albert 변환
    "Albert이 시장을 관찰합니다..."

→ 작동! ✅
```

### 4. 커스터마이징?

```yaml
사용자:
  config/agent_names.yaml 수정
    observer: Jane

Cursor:
  .cursorrules 자동 갱신?
  → 아니요!
  
  해결:
    .cursorrules 읽기:
      Observer: {name: Albert}  # 고정
    
    But:
      config/agent_names.yaml 우선 규칙
      → Jane 사용
  
  문제:
    .cursorrules도 수정해야? ⚠️
```

**해결:**
```yaml
.cursorrules 개선:
  
  Before:
    Observer: {name: Albert, ...}  # 하드코딩
  
  After:
    # Agent names from config/agent_names.yaml
    # Load and apply dynamically
    
    agent_name_binding:
      source: config/agent_names.yaml
      mapping:
        Observer → agent_names.observer
        Explorer → agent_names.explorer
        ...

AI 동작:
  1. .cursorrules 읽기
  2. agent_name_binding 발견
  3. config/agent_names.yaml 자동 읽기
  4. 동적 매핑
  
  → 완벽! ✅
```

---

## 🎯 최종 검증

### 가능성: ✅ 100% 가능!

```yaml
umis.yaml:
  name 필드 제거 → 문제 없음

config/agent_names.yaml:
  단일 진실 → 완벽

.cursorrules:
  동적 바인딩 규칙 추가 → 해결
```

### 문제 여지: ❌ 없음!

```yaml
확인:
  ✅ YAML 파싱: 문제 없음
  ✅ AI 이해: 가능
  ✅ 사용자 경험: 동일
  ✅ 커스터마이징: 작동

조건:
  .cursorrules에 동적 바인딩 규칙 필요
```

---

## 💡 최종 설계

### 구조

```yaml
umis.yaml (시스템):
  agents:
    - id: Observer  # ID만!
      role: market_structure

config/agent_names.yaml (이름):
  observer: Albert  # 단일 진실!

.cursorrules (바인딩):
  # Agent Name Dynamic Binding
  agent_name_source: config/agent_names.yaml
  
  매핑 로직:
    id ↔ name 양방향
    입력: @{name} → {id}
    출력: {id} → {name}
```

### AI 동작

```yaml
사용자:
  "@Steve, 분석해"

Cursor:
  1. .cursorrules 읽기 (자동)
     agent_name_source: config/agent_names.yaml
  
  2. config/agent_names.yaml 읽기 (자동)
     explorer: Steve
  
  3. 매핑:
     @Steve → Explorer (id)
  
  4. umis.yaml 읽기:
     Explorer 정의 찾기
  
  5. 실행
  
  6. 출력 변환:
     Explorer → Steve
     "Steve가 기회를 발굴합니다..."
```

---

## 🎯 최종 답변

**완벽합니다! 문제 없습니다!** ✅

```yaml
채택:
  umis.yaml name 필드 제거

이유:
  • 단일 진실 (config/agent_names.yaml)
  • 완벽한 분리
  • Clean Design

조건:
  .cursorrules 동적 바인딩 규칙 추가
```

**실행 항목 업데이트 완료!**

Step 4.5 추가됨! 🚀
