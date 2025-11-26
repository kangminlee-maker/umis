# System RAG 인터페이스 가이드
**날짜**: 2025-11-05  
**버전**: UMIS v7.2.0  
**대상**: AI Assistant (Cursor, Claude 등)

---

## 🚨 중요: AI 필수 읽기!

이 문서는 **AI가 UMIS를 제대로 사용하기 위한** 필수 가이드입니다.

**문제 상황**:
- ❌ umis_core.yaml만 읽고 작업 시작 → 도구 content 없음 → 실패
- ❌ System RAG 실행 건너뜀 → Observer/Explorer만 사용 → Workflow 무시
- ❌ 도구 목록만 보고 실제 content 로드 안 함 → 기능 이해 부족

**해결책**:
- ✅ umis_core.yaml (INDEX) + System RAG (도구 content) 필수 조합
- ✅ 모든 프로젝트 시작 시 4단계 프로세스 실행
- ✅ Workflow 이해 → 올바른 Agent 순서

---

## 📋 목차
1. [System RAG란?](#system-rag란)
2. [AI 필수 실행 프로세스](#ai-필수-실행-프로세스)
3. [실제 사용 예시](#실제-사용-예시)
4. [자주 하는 실수](#자주-하는-실수)
5. [디버깅](#디버깅)

---

## System RAG란?

### 개념

```yaml
목적:
  UMIS 6,102줄 전체를 로드하지 않고
  필요한 도구만 정확히 로드하여 컨텍스트 절약

구조:
  umis_core.yaml (709줄):
    - INDEX (도구 목록, Agent 역할 요약)
    - 전체 개요
    - Decision Guide
  
  System RAG (28개 도구):
    - 각 도구의 상세 content (200-800줄)
    - tool_key로 정확 검색
    - 필요한 것만 로드

절약:
  간단한 작업: 82% (709 + 400 = 1,109줄 vs 6,102줄)
  중간 작업: 69% (709 + 1,200 = 1,909줄)
  복잡한 작업: 47% (709 + 2,500 = 3,209줄)
```

### 비유

```
❌ 나쁜 방식:
  도서관에서 백과사전 전권(6,102페이지) 다 읽기
  → 시간 오래 걸림, 비효율

✅ 좋은 방식:
  1. 목차(709페이지) 확인
  2. 필요한 챕터만 찾기 (tool_key)
  3. 해당 챕터만 읽기 (400페이지)
  → 빠름, 효율적
```

---

## AI 필수 실행 프로세스

### ⭐ 4단계 프로세스 (모든 프로젝트!)

```yaml
STEP 1: umis_core.yaml 읽기
  Tool: read_file
  File: umis_core.yaml
  Lines: 40-110 (Quick Start + Agent Selection)
  Output: 필요한 Agent와 도구 파악
  Mandatory: true

STEP 2: 쿼리 분석
  Action: 사용자 요청에서 agent + task + keywords 추출
  Refer: umis_core.yaml Lines 96-109 (agent_selection_flowchart)
  Output: tool_key 리스트
  Example: ["tool:explorer:pattern_search", "tool:quantifier:sam_4methods"]

STEP 3: System RAG 실행 ⭐⭐⭐
  Tool: run_terminal_cmd (필수!)
  Command: "python3 scripts/query_system_rag.py {tool_key}"
  Repeat: 필요한 모든 tool_key에 대해
  Output: 도구 content (200-800줄/개)
  Mandatory: true
  Skip Penalty: 작업 실패 (도구 없음)

STEP 4: 로드된 도구로 작업
  Action: System RAG 결과를 컨텍스트에 포함하여 작업 수행
  Context: umis_core.yaml + System RAG 결과
```

### 체크리스트

AI는 다음을 **반드시** 실행해야 합니다:

- [ ] 1. `read_file("umis_core.yaml")` 실행
- [ ] 2. Agent + tool_key 식별
- [ ] 3. `run_terminal_cmd("python3 scripts/query_system_rag.py {tool_key}")` 실행
- [ ] 4. 로드된 content 활용

**건너뛰면 안 됩니다!**

---

## 실제 사용 예시

### 예시 1: 단순 쿼리 (@Explorer 패턴 검색)

**사용자 요청**:
```
@Explorer, 구독 모델 패턴 찾아줘
```

**AI 실행 순서**:

```python
# Step 1: INDEX 로드
read_file("umis_core.yaml", offset=40, limit=110)

# 파악:
# - Agent: explorer
# - Task: pattern_search
# - Tool key: tool:explorer:pattern_search

# Step 2: System RAG 실행 (필수!)
run_terminal_cmd("python3 scripts/query_system_rag.py tool:explorer:pattern_search")

# 결과:
# - Content: ~400줄 (패턴 검색 도구 상세)
# - Match Type: exact_key
# - Latency: 0.25ms

# Step 3: 로드된 content 활용
# → Explorer RAG 패턴 검색 프로세스 이해
# → 실제 RAG 검색 실행
# → 구독 모델 패턴 분석

# Context 사용량:
# - umis_core.yaml: 709줄
# - System RAG: 400줄
# - Total: 1,109줄 (vs 6,102줄 전체)
# - 절약: 82%
```

---

### 예시 2: 복잡한 작업 (시장 분석)

**사용자 요청**:
```
음악 스트리밍 시장 분석해줘
```

**AI 실행 순서**:

```python
# Step 1: INDEX 로드
read_file("umis_core.yaml")

# 파악:
# - Lines 106: "시장 분석" = Observer → Explorer → Quantifier
# - Tool keys 필요:
#   1. tool:observer:market_structure
#   2. tool:explorer:pattern_search
#   3. tool:quantifier:sam_4methods

# Step 2: System RAG 실행 (3번!)
run_terminal_cmd("python3 scripts/query_system_rag.py tool:observer:market_structure")
run_terminal_cmd("python3 scripts/query_system_rag.py tool:explorer:pattern_search")
run_terminal_cmd("python3 scripts/query_system_rag.py tool:quantifier:sam_4methods")

# 결과:
# - 3개 도구 content (~1,200줄)
# - 각 도구의 상세 프로세스 파악

# Step 3: Workflow 실행
# 1. Observer (Albert):
#    - 로드된 market_structure 도구 참조
#    - 시장 구조 관찰
#    - 비효율성 발견

# 2. Explorer (Steve):
#    - 로드된 pattern_search 도구 참조
#    - RAG 패턴 매칭
#    - 기회 가설 생성

# 3. Quantifier (Bill):
#    - 로드된 sam_4methods 도구 참조
#    - SAM 4가지 방법 계산
#    - Excel 생성

# Context 사용량:
# - umis_core.yaml: 709줄
# - System RAG: 1,200줄
# - Total: 1,909줄 (vs 6,102줄)
# - 절약: 69%
```

---

### 예시 3: Discovery Sprint (5-Agent 병렬)

**사용자 요청**:
```
피아노 구독 서비스 시장 분석 (목표 불명확)
```

**AI 실행 순서**:

```python
# Step 1: INDEX 로드
read_file("umis_core.yaml")

# 판단:
# - 목표 불명확 → Discovery Sprint 필요
# - Lines 109: "Discovery Sprint" = framework + 모든 Agent

# Step 2: 필요한 도구 식별
tool_keys = [
    "tool:framework:discovery_sprint",      # Framework
    "tool:observer:market_structure",       # Observer
    "tool:explorer:pattern_search",         # Explorer
    "tool:explorer:7_step_process",         # Explorer (상세)
    "tool:quantifier:sam_4methods",         # Quantifier
    "tool:validator:data_definition",       # Validator
    "tool:guardian:progress_monitoring"     # Guardian
]

# Step 3: System RAG 실행 (7번!)
for key in tool_keys:
    run_terminal_cmd(f"python3 scripts/query_system_rag.py {key}")

# 결과:
# - 7개 도구 content (~2,500줄)
# - 각 Agent의 역할과 프로세스 파악

# Step 4: Discovery Sprint 실행
# → 5-Agent 병렬 탐색 (framework 도구 참조)
# → 각 Agent는 로드된 도구 활용
# → 목표 구체화
# → 다음 단계 결정

# Context 사용량:
# - umis_core.yaml: 709줄
# - System RAG: 2,500줄
# - Total: 3,209줄 (vs 6,102줄)
# - 절약: 47%
```

---

## 자주 하는 실수

### ❌ 실수 1: System RAG 건너뛰기

**잘못된 접근**:
```python
# 1. umis_core.yaml만 읽기
read_file("umis_core.yaml")

# 2. 바로 작업 시작
# "Observer가 시장을 관찰합니다..."

# 문제:
# - Observer가 어떻게 관찰하는지 모름
# - 도구 프로세스 불명확
# - Workflow 이해 부족
# → 작업 실패 또는 품질 낮음
```

**올바른 접근**:
```python
# 1. umis_core.yaml 읽기
read_file("umis_core.yaml")

# 2. tool_key 식별
tool_key = "tool:observer:market_structure"

# 3. System RAG 실행 (필수!)
run_terminal_cmd("python3 scripts/query_system_rag.py tool:observer:market_structure")

# 4. 로드된 content로 작업
# → Observer 프로세스 명확히 이해
# → 가치사슬 맵핑 방법 파악
# → 비효율성 감지 기준 적용
# → 성공!
```

---

### ❌ 실수 2: Workflow 무시

**잘못된 접근**:
```
사용자: "음악 스트리밍 시장 분석"

AI: "Explorer가 기회를 발굴하겠습니다..."

문제:
- Observer 단계 건너뜀
- 시장 구조 관찰 없이 기회 발굴
- 근거 부족
```

**올바른 접근**:
```
사용자: "음악 스트리밍 시장 분석"

AI:
1. umis_core.yaml 확인 → "시장 분석 = Observer → Explorer → Quantifier"
2. System RAG 3개 로드
3. Workflow 순서대로:
   - Observer: 시장 구조 관찰
   - Explorer: 기회 발굴 (Observer 결과 기반)
   - Quantifier: SAM 계산 (Explorer 기회 기반)
```

---

### ❌ 실수 3: 도구 선택 오류

**잘못된 접근**:
```
사용자: "@Explorer, 시장 규모 계산해줘"

AI: Explorer가 시장 규모를 계산...

문제:
- Explorer는 기회 발굴 Agent
- 시장 규모는 Quantifier 역할
- 잘못된 Agent 선택
```

**올바른 접근**:
```
사용자: "@Explorer, 시장 규모 계산해줘"

AI:
1. umis_core.yaml 확인
2. Lines 100: "시장 규모" = Quantifier
3. 사용자에게 안내:
   "시장 규모 계산은 Quantifier (Bill)의 역할입니다.
    Quantifier로 진행하시겠습니까?"
```

---

## 디버깅

### System RAG Collection 없음

**증상**:
```
❌ Collection [system_knowledge] does not exist
```

**해결**:
```bash
python3 scripts/build_system_knowledge.py
```

소요: 1분  
결과: 28개 도구 인덱싱

---

### 도구 검색 실패

**증상**:
```
❌ 도구 없음: tool:xxx:yyy
```

**확인**:
```bash
# 1. 사용 가능한 키 목록
python3 scripts/query_system_rag.py --list

# 2. 통계 확인
python3 scripts/query_system_rag.py --stats
```

**해결**:
- tool_key 오타 확인
- Agent ID 확인 (explorer, quantifier, validator, observer, guardian, framework, universal)
- 도구 존재 확인 (--list 결과)

---

### Content 로드 안 됨

**증상**:
```
AI가 "도구를 사용합니다"라고만 하고 실제 실행 안 함
```

**원인**:
- run_terminal_cmd 실행 안 함
- 명령만 언급하고 실제 실행 건너뜀

**해결**:
```python
# ❌ 틀린 방식 (언급만)
"tool:explorer:pattern_search를 사용하겠습니다"

# ✅ 올바른 방식 (실행!)
run_terminal_cmd("python3 scripts/query_system_rag.py tool:explorer:pattern_search")
# → Content 로드됨
# → Content 기반 작업
```

---

## Tool Key 매핑 (Quick Reference)

### Explorer (4개)

| Keywords | Tool Key |
|----------|----------|
| 패턴, 모델, 사례 | `tool:explorer:pattern_search` |
| 기회, 발굴, 7단계 | `tool:explorer:7_step_process` |
| 검증, 프로토콜 | `tool:explorer:validation_protocol` |
| 가설, 생성 | `tool:explorer:hypothesis_generation` |

### Quantifier (4개)

| Keywords | Tool Key |
|----------|----------|
| SAM, 시장 규모, TAM | `tool:quantifier:sam_4methods` |
| 성장률, 전망 | `tool:quantifier:growth_analysis` |
| 시나리오, 계획 | `tool:quantifier:scenario_planning` |
| 벤치마크, 비교 | `tool:quantifier:benchmark_analysis` |

### Validator (4개)

| Keywords | Tool Key |
|----------|----------|
| 정의, 검증 | `tool:validator:data_definition` |
| 출처, 신뢰도 | `tool:validator:source_verification` |
| 소싱, 창의적 | `tool:validator:creative_sourcing` |
| Gap, 조정 | `tool:validator:gap_analysis` |

### Observer (4개)

| Keywords | Tool Key |
|----------|----------|
| 구조, 시장 구조 | `tool:observer:market_structure` |
| 가치사슬, 흐름 | `tool:observer:value_chain` |
| 비효율, 감지 | `tool:observer:inefficiency_detection` |
| 파괴, 혁신 기회 | `tool:observer:disruption_opportunity` |

### Guardian (2개)

| Keywords | Tool Key |
|----------|----------|
| 진행, 모니터링 | `tool:guardian:progress_monitoring` |
| 품질, 평가 | `tool:guardian:quality_evaluation` |

### Framework (7개)

| Keywords | Tool Key |
|----------|----------|
| 시장 정의, 13차원 | `tool:framework:13_dimensions` |
| Discovery Sprint | `tool:framework:discovery_sprint` |
| 7 Powers | `tool:framework:7_powers` |
| 경쟁 분석 | `tool:framework:competitive_analysis` |
| Counter-Positioning | `tool:framework:counter_positioning` |
| 시장 정의 (일반) | `tool:framework:market_definition` |
| 가치사슬 분석 | `tool:framework:value_chain_analysis` |

### Universal (3개)

| Keywords | Tool Key |
|----------|----------|
| guestimate, 추정, 빠른 | `tool:universal:guestimation` |
| reasoner, 정밀, 증거 | `tool:universal:domain_reasoner_10_signals` |
| hybrid, auto, 자동 | `tool:universal:hybrid_strategy` |

---

## Workflow 가이드

### 시장 분석 Workflow

**순서**: Observer → Explorer → Quantifier → Validator → Guardian

```yaml
1. Observer (Albert):
   Tool: tool:observer:market_structure
   Role: 시장 구조 관찰, 비효율성 발견
   Output: 가치사슬 맵, 트리거 시그널
   Duration: 2-4시간

2. Explorer (Steve):
   Tool: tool:explorer:pattern_search
   Role: 패턴 매칭 (RAG), 기회 가설 생성
   Input: Observer의 트리거 시그널
   Output: OPP_xxx (기회 가설)
   Duration: 4-8시간

3. Quantifier (Bill):
   Tool: tool:quantifier:sam_4methods
   Role: SAM 4가지 방법 계산
   Input: Explorer의 기회 정의
   Output: market_sizing.xlsx
   Duration: 8-12시간

4. Validator (Rachel):
   Tool: tool:validator:data_definition
   Role: 데이터 정의 검증
   Input: Bill의 계산에 사용된 데이터
   Output: source_registry.yaml
   Duration: 4-8시간

5. Guardian (Stewart):
   Tool: tool:guardian:quality_evaluation
   Role: 품질 평가, 최종 승인
   Output: quality_report.md
   Duration: 2-4시간
```

**⚠️ 순서를 건너뛰지 마세요!**

---

### Discovery Sprint Workflow (목표 불명확 시)

**언제**: 명확도 < 7 (목표가 불명확할 때)

**Tool**: `tool:framework:discovery_sprint`

**Process**:
```yaml
1. System RAG 로드:
   - tool:framework:discovery_sprint (프로세스)
   - 모든 Agent 도구 (5-Agent 병렬 탐색)

2. 5-Agent 병렬 탐색 (2-8시간):
   - Albert: 시장 구조 관찰
   - Steve: 패턴 매칭
   - Bill: 시장 규모 대략 추정
   - Rachel: 데이터 현황 파악
   - Stewart: 진행 모니터링

3. 목표 구체화:
   - 5개 관점 통합
   - 명확도 7 이상 달성
   - 다음 단계 결정 (Comprehensive/Rapid/Quick)

4. Workflow 전환:
   - 목표 명확화됨 → 정규 Workflow
```

---

## 검증 테스트

### 테스트 1: System RAG Collection 확인

```bash
python3 scripts/query_system_rag.py --stats
```

**기대 결과**:
```
✅ 총 도구 수: 28개
✅ Agent별: explorer(4), quantifier(4), validator(4), ...
```

---

### 테스트 2: 도구 키 목록

```bash
python3 scripts/query_system_rag.py --list
```

**기대 결과**:
```
✅ 28개 tool_key 출력
✅ tool:agent:task 형식
```

---

### 테스트 3: 실제 도구 로드

```bash
python3 scripts/query_system_rag.py tool:explorer:pattern_search
```

**기대 결과**:
```
✅ Match Type: exact_key
✅ Latency: < 1ms
✅ Content: ~400줄 출력
```

---

## 요약

### ✅ AI가 반드시 해야 할 것

1. **umis_core.yaml 읽기** (INDEX)
2. **쿼리 분석** (agent + tool_key)
3. **System RAG 실행** (run_terminal_cmd) ⭐⭐⭐
4. **로드된 도구로 작업**

### ❌ AI가 하면 안 되는 것

1. umis_core.yaml만 읽고 작업 시작
2. System RAG 건너뛰기
3. Workflow 순서 무시
4. 잘못된 Agent 선택

### 🎯 핵심 명령

```bash
# Collection 확인
python3 scripts/query_system_rag.py --stats

# 도구 목록
python3 scripts/query_system_rag.py --list

# 도구 로드 (가장 중요!)
python3 scripts/query_system_rag.py tool:explorer:pattern_search
```

---

**작성**: 2025-11-05  
**파일**: `docs/SYSTEM_RAG_INTERFACE_GUIDE.md`  
**관련**: .cursorrules (PART 7), umis_core.yaml (Section 0)

