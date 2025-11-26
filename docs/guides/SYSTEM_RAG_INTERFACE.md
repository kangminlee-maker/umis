# System RAG 인터페이스 가이드
**날짜**: 2025-11-26 (v7.11.1 업데이트)
**버전**: UMIS v7.11.1  
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
  UMIS 6,838줄 전체를 로드하지 않고
  필요한 Complete 도구만 로드하여 컨텍스트 절약

구조 (v7.11.1):
  umis_core.yaml:
    - INDEX (15개 도구: System 9 + Complete 6)
    - 전체 개요
    - Decision Guide
  
  System RAG (15개 도구):
    - Complete 도구: ~2,867 tokens (평균)
    - tool_key로 정확 검색
    - 필요한 것만 로드

절약:
  단일 Agent: 89% (~5,676 tokens vs ~50,000)
  3개 Agent: 76% (~12,233 tokens)
  6개 Agent: 75% (~20,201 tokens)
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
  Action: 사용자 요청에서 agent 추출
  Output: Complete tool_key 선택
  Example: "@Explorer" → tool:explorer:complete

STEP 3: System RAG 실행 ⭐⭐⭐
  Tool: run_terminal_cmd (필수!)
  Command: "python3 scripts/query_system_rag.py tool:{agent}:complete"
  Output: Complete 도구 content (~2,867 tokens 평균)
  Mandatory: true
  Skip Penalty: 작업 실패 (도구 없음)
  
  Note: Task 도구 쿼리 시 Vector Fallback으로 Complete 자동 매칭

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
run_terminal_cmd("python3 scripts/query_system_rag.py tool:explorer:complete")

# 결과:
# - Content: Complete 도구 (umis.yaml Explorer 섹션 전체)
# - Match Type: exact_key 또는 vector_fallback
# - Latency: 0.25ms

# Step 3: 로드된 content 활용
# → Explorer 전체 컨텍스트 확보
# → 7단계 프로세스 + RAG 패턴 검색 + 검증 프로토콜
# → 실제 작업 수행

# Context 사용량:
# - umis_core.yaml: ~4,000 tokens
# - Complete: ~3,559 tokens
# - Total: ~7,559 tokens (vs 50,000)
# - 절약: 85%
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
# - Tool keys 필요 (Complete):
#   1. tool:observer:complete
#   2. tool:explorer:complete
#   3. tool:quantifier:complete

# Step 2: System RAG 실행 (3번!)
run_terminal_cmd("python3 scripts/query_system_rag.py tool:observer:complete")
run_terminal_cmd("python3 scripts/query_system_rag.py tool:explorer:complete")
run_terminal_cmd("python3 scripts/query_system_rag.py tool:quantifier:complete")

# 결과:
# - 3개 Complete 도구 (~8,233 tokens)
# - 각 Agent의 전체 프로세스 파악

# Step 3: Workflow 실행
# 1. Observer (Albert):
#    - 로드된 complete 도구 참조
#    - 시장 구조 관찰 + 가치사슬 + 비효율성

# 2. Explorer (Steve):
#    - 로드된 complete 도구 참조
#    - 7단계 + RAG 패턴 + 가설 검증

# 3. Quantifier (Bill):
#    - 로드된 complete 도구 참조
#    - SAM 4가지 방법 + Estimator 협업 + Excel 생성

# Context 사용량:
# - umis_core.yaml: ~4,000 tokens
# - System RAG: ~8,233 tokens
# - Total: ~12,233 tokens (vs 50,000)
# - 절약: 76%
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

# Step 2: 필요한 도구 식별 (Complete 권장)
tool_keys = [
    "tool:observer:complete",
    "tool:explorer:complete", 
    "tool:quantifier:complete",
    "tool:validator:complete",
    "tool:guardian:complete",
    "tool:estimator:complete"
]

# Step 3: System RAG 실행 (6번!)
for key in tool_keys:
    run_terminal_cmd(f"python3 scripts/query_system_rag.py {key}")

# 결과:
# - 6개 Complete 도구 (~16,201 tokens)
# - 각 Agent의 역할과 전체 프로세스 파악

# Step 4: Discovery Sprint 실행
# → 5-Agent 병렬 탐색 (framework 도구 참조)
# → 각 Agent는 로드된 도구 활용
# → 목표 구체화
# → 다음 단계 결정

# Context 사용량:
# - umis_core.yaml: ~4,000 tokens
# - System RAG: ~16,201 tokens
# - Total: ~20,201 tokens (vs 50,000)
# - 절약: 75%

# 권장 모델:
# - claude-sonnet-3.5 (200K): 51% 사용 (안정적)
# - gemini-1.5-pro (272K): 38% 사용 (여유)
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
run_terminal_cmd("python3 scripts/query_system_rag.py tool:observer:complete")

# 4. 로드된 content로 작업
# → Observer 전체 프로세스 명확히 이해
# → 13차원 정의 + 가치사슬 + 8개 차원 + 협업 방식
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
2. System RAG 3개 Complete 로드
3. Workflow 순서대로:
   - Observer: 시장 구조 관찰 (complete 전체 활용)
   - Explorer: 기회 발굴 (complete 전체 활용)
   - Quantifier: SAM 계산 (complete 전체 활용)
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
"tool:explorer:complete를 사용하겠습니다"

# ✅ 올바른 방식 (실행!)
run_terminal_cmd("python3 scripts/query_system_rag.py tool:explorer:complete")
# → Content 로드됨
# → Complete 전체 컨텍스트로 작업
```

---

## Tool Key 매핑 (Quick Reference)

### Complete 도구 (v7.11.1) ⭐ 권장

| Agent | Tool Key | 토큰 | 사용 시점 |
|-------|----------|------|----------|
| Observer | `tool:observer:complete` | ~1,676 | 시장 구조 분석 |
| Explorer | `tool:explorer:complete` | ~3,559 | 기회 발굴 |
| Quantifier | `tool:quantifier:complete` | ~2,998 | 시장 규모 계산 |
| Validator | `tool:validator:complete` | ~2,430 | 데이터 검증 |
| Guardian | `tool:guardian:complete` | ~1,954 | 품질 평가 |
| Estimator | `tool:estimator:complete` | ~3,584 | 값 추정 (4-Stage Fusion) |

**Note**: Task 도구 쿼리 시 Vector Fallback으로 Complete 자동 매칭

---

## Workflow 가이드

### 시장 분석 Workflow

**순서**: Observer → Explorer → Quantifier → Validator → Guardian

```yaml
1. Observer (Albert):
   Tool: tool:observer:complete
   Role: 시장 구조 관찰, 가치사슬, 비효율성
   Output: market_reality_report.md
   Duration: 2-4시간

2. Explorer (Steve):
   Tool: tool:explorer:complete
   Role: 7단계 프로세스, RAG 패턴, 기회 가설
   Input: Observer의 트리거 시그널
   Output: OPP_xxx.md
   Duration: 4-8시간

3. Quantifier (Bill):
   Tool: tool:quantifier:complete
   Role: SAM 4가지 방법, Estimator 협업
   Input: Explorer의 기회 정의
   Output: market_sizing.xlsx
   Duration: 8-12시간

4. Validator (Rachel):
   Tool: tool:validator:complete
   Role: 데이터 정의 검증, 출처 확인
   Input: Bill의 계산 데이터
   Output: source_registry.yaml
   Duration: 4-8시간

5. Guardian (Stewart):
   Tool: tool:guardian:complete
   Role: 품질 평가, 최종 승인
   Output: quality_report.md
   Duration: 2-4시간
```

**⚠️ 순서를 건너뛰지 마세요!**

---

### Discovery Sprint Workflow (목표 불명확 시)

**언제**: 명확도 < 7 (목표가 불명확할 때)

**Process**:
```yaml
1. System RAG 로드:
   - 6개 Complete 도구 (모든 Agent)

2. 6-Agent 병렬 탐색 (2-8시간):
   - Albert: 시장 구조 관찰 (complete)
   - Steve: 패턴 매칭 (complete)
   - Bill: 시장 규모 추정 (complete)
   - Rachel: 데이터 현황 (complete)
   - Stewart: 진행 모니터링 (complete)
   - Fermi: 핵심 지표 추정 (complete)

3. 목표 구체화:
   - 6개 관점 통합
   - 명확도 7 이상 달성
   - 다음 단계 결정

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
✅ 총 도구 수: 15개 (System 9 + Complete 6)
✅ Agent별: observer, explorer, quantifier, validator, guardian, estimator
```

---

### 테스트 2: 도구 키 목록

```bash
python3 scripts/query_system_rag.py --list
```

**기대 결과**:
```
✅ 15개 tool_key 출력
✅ tool:agent:complete 형식
```

---

### 테스트 3: 실제 도구 로드

```bash
python3 scripts/query_system_rag.py tool:explorer:complete
```

**기대 결과**:
```
✅ Match Type: exact_key (또는 vector_fallback)
✅ Latency: < 1ms
✅ Content: Complete 도구 출력
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
python3 scripts/query_system_rag.py tool:explorer:complete

# Note: Task 도구 쿼리도 가능 (Vector Fallback)
python3 scripts/query_system_rag.py tool:explorer:pattern_search
# → tool:explorer:complete 자동 매칭
```

---

## v7.11.1 업데이트

**변경 사항**:
- Complete 도구만 사용 (Task 도구 제거)
- 총 15개 도구 (System 9 + Complete 6)
- Vector Fallback으로 Task 쿼리도 Complete 매칭
- 200K+ 모델 권장

**상세**: `CONTEXT_WINDOW_STRATEGY.md`, `TASK_TOOLS_DECISION.md`

---

**작성**: 2025-11-26  
**파일**: `docs/guides/SYSTEM_RAG_INTERFACE.md`  
**관련**: .cursorrules, umis_core.yaml

