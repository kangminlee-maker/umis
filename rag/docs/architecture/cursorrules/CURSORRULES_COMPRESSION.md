# .cursorrules 공격적 압축 전략

**목표:** 정보 손실 0, 최대 압축

---

## 📊 압축 방법 (공격적 → 극단적)

### Level 1: 구조적 압축 (50% 절감)

**현재 문제:**
```
When user mentions "umis 설치":
  Check if .env file exists:
    - If NO:
      1. Create .env from env.template:
         cp env.template .env
      
      2. Guide user:
         "✅ .env 파일을 생성했습니다!
         ...긴 메시지..."

→ 150줄
```

**압축:**
```yaml
# UMIS 설치 프로토콜
setup_detect: ["umis 설치", "설정", "setup"]
setup_flow:
  no_env: cp env.template .env → guide_api_key → build_index
  yes_env: ready_msg

# 70줄로 압축! (50% ↓)
```

---

### Level 2: 약어 시스템 (70% 절감)

**약어 정의:**
```yaml
# === ABBREVIATIONS ===
# Agents
OBS: Observer (Albert)
EXP: Explorer (Steve)
QNT: Quantifier (Bill)
VAL: Validator (Rachel)
GRD: Guardian (Stewart)

# Actions
BLD: build_index
SRC: search
VFY: verify
CVT: convert

# Patterns
P_BM: business_model_patterns
P_DP: disruption_patterns
```

**사용:**
```yaml
Before (100줄):
  When Explorer needs pattern matching:
    - Detect: "패턴 매칭 필요"
    - Run: python scripts/query_rag.py pattern
    - Show: "subscription_model 발견!"

After (30줄):
  EXP.pattern_search:
    detect: ["패턴 매칭", "트리거"]
    cmd: py scripts/query_rag.py pattern {q}
    msg: "{result} 발견!"

→ 70% 압축!
```

---

### Level 3: JSON 스키마 (80% 절감)

**YAML → 압축 JSON:**
```json
{
  "umis": {
    "v": "7.0.0",
    "agents": {
      "obs": {"name": "Albert", "role": "structure"},
      "exp": {"name": "Steve", "role": "opportunity", "rag": true},
      "qnt": {"name": "Bill", "role": "quantify"},
      "val": {"name": "Rachel", "role": "validate"},
      "grd": {"name": "Stewart", "role": "monitor"}
    },
    "flows": {
      "setup": {
        "detect": ["umis 설치"],
        "steps": ["env", "key", "build"]
      },
      "analyze": {
        "detect": ["@{agent}"],
        "rag": "auto if exp"
      }
    }
  }
}

→ 50줄! (80% ↓)
```

---

### Level 4: DSL (Domain Specific Language) (85% 절감)

**커스텀 언어:**
```
# UMIS DSL v1.0

@setup["umis 설치"] → !.env ? cp tpl→.env msg:api : msg:ready
@rag_rebuild[yaml_change] → py 01 → py 02
@analyze[@EXP] → detect:pattern → rag_search → integrate

# 30줄! (85% ↓)
```

---

### Level 5: 정규식 패턴 (90% 절감)

```yaml
# Pattern-based Rules

rules:
  - ^@(Steve|Explorer).*분석: 
      → rag_search(pattern) → rag_search(case) → generate
  
  - yaml_modified:
      → auto_rebuild if approved
  
  - ^umis\s+(설치|setup):
      → setup_flow

# 20줄! (90% ↓)
```

---

### Level 6: 시맨틱 압축 (극단, 95% 절감)

**핵심만:**
```yaml
# UMIS Core (AI-optimized)

system: 5-agent market analysis
  OBS→structure EXP→opportunity(RAG!) QNT→size VAL→verify GRD→monitor

user: non-coder, Cursor-only

auto:
  setup: detect→guide→build
  rag: yaml_change→rebuild
  search: @agent→rag_auto

flow:
  @Steve→pattern_rag→case_rag→hypothesis
  yaml_edit→01.py→02.py→ready

# 15줄! (95% ↓)
```

---

## 🎯 실용적 최적 압축

### Balanced Approach (70% 압축, 가독성 유지)

```yaml
# ========================================
# UMIS RAG Cursor Rules - AI Optimized
# v7.0.0 | Non-coder | Cursor-only
# ========================================

# === UMIS 개념 ===
system:
  agents: [OBS(Albert), EXP(Steve,RAG), QNT(Bill), VAL(Rachel), GRD(Stewart)]
  flow: Discovery→Structure→Opportunity→Quantify→Validate→Decision
  rag: Explorer only (54 patterns/cases)

# === 사용자 ===
user:
  skill: no-coding
  tool: Cursor Composer + Agent mode
  lang: 한국어

# === 자동화 ===
auto_setup:
  detect: ["umis 설치", "setup"]
  flow: check_env→(no?create+guide:ready)→build_index
  
auto_rag:
  yaml_change: ask→01.py→02.py→done
  pattern_search: @Steve→auto_rag_search
  
auto_agent:
  name_map: agent_names.yaml bidirectional
  @{custom_name}→{agent_id}

# === 워크플로우 ===
workflows:
  market_analysis:
    trigger: "@Steve, 시장 분석"
    flow: OBS(observe)→EXP(rag+hypothesis)→QNT(size)→VAL(verify)
  
  data_add:
    trigger: "데이터 추가"
    flow: find_section→suggest_diff→save→rag_rebuild

# === 경로 ===
paths:
  yaml: umis_*.yaml
  rag: scripts/query_rag.py
  chunks: data/chunks/explorer_*.jsonl
  index: data/chroma/

# 80줄! (현재 243줄 → 67% 압축)
```

---

## 💡 최종 추천

### Option A: Balanced (70% 압축) ⭐ 추천

```yaml
크기: 80줄
압축: 67%
가독성: 높음
유지보수: 쉬움

특징:
  • YAML 구조 유지
  • 약어 최소 사용
  • AI 이해 쉬움
  • 사람도 읽기 쉬움
```

### Option B: Aggressive (90% 압축)

```yaml
크기: 25줄
압축: 90%
가독성: AI만
유지보수: 어려움

특징:
  • 극단적 약어
  • DSL 사용
  • 정규식 패턴
  • 사람은 어려움
```

### Option C: Extreme (95% 압축)

```yaml
크기: 15줄
압축: 95%
가독성: 위험
유지보수: 매우 어려움

특징:
  • 시맨틱 압축
  • 정보 밀도 극대
  • AI 파싱 필요
  • 디버깅 불가능
```

---

## 🎯 제 추천

**Option A: Balanced (70% 압축)**

```yaml
이유:
  1. 충분한 압축 (243→80줄)
  2. AI 이해 쉬움
  3. 사람도 읽기 가능
  4. 유지보수 가능
  
  컨텍스트 절감:
    243줄 × 평균 50자 = 12,000자
    80줄 × 평균 30자 = 2,400자
    
    절감: 10,000자 (~2,500 토큰)
    
    → 충분! ✅

극단적 압축:
  95% 압축 (15줄)
  → 2,000자 더 절감
  → 하지만 유지보수 불가능
  → 가치 < 비용
```

---

**어떤 방식을 선호하시나요?**

A. Balanced (70%, 80줄) ⭐ 추천  
B. Aggressive (90%, 25줄)  
C. Extreme (95%, 15줄)

선택해주세요! 🚀
