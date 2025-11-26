# System RAG 사용 가이드 (v7.11.1)
**작성일**: 2025-11-26 (v7.11.1 업데이트)  
**버전**: v7.11.1  
**목적**: 2-Tier 구조 사용 가이드 (System + Complete)

---

## 📊 현재 구조 (2-Tier, v7.11.1)

**결정**: Complete 도구만 사용 (Task 도구 제거)  
**근거**: 유지보수 단순성 + 200K 모델 충분 + Vector Fallback 동작  
**상세**: `CONTEXT_WINDOW_STRATEGY.md`, `TASK_TOOLS_DECISION.md` 참조

---

### Tier 1: System 도구 (9개)
**목적**: UMIS 시스템 전체 이해  
**출처**: umis.yaml 시스템 섹션

| 도구 | 크기 | 사용 시점 |
|------|------|----------|
| tool:system:system_architecture | ~1,774 tokens | 시스템 구조 이해 |
| tool:system:implementation_guide | ~4,623 tokens | 구현 가이드 |
| tool:system:agents | ~16,578 tokens | 모든 Agent (매우 큼) |
| (6개 더) | ... | ... |

---

### Tier 2: Complete 도구 (6개)
**목적**: 실제 작업 수행 시 전체 컨텍스트 제공  
**출처**: umis.yaml Agent 섹션 0% 손실 ⭐ 실제 작업 권장!

| 도구 | 토큰 | 사용 시점 |
|------|------|----------|
| tool:observer:complete | ~1,676 | Observer 실제 작업 |
| tool:explorer:complete | ~3,559 | Explorer 실제 작업 |
| tool:quantifier:complete | ~2,998 | Quantifier 실제 작업 |
| tool:validator:complete | ~2,430 | Validator 실제 작업 |
| tool:guardian:complete | ~1,954 | Guardian 실제 작업 |
| tool:estimator:complete | ~3,584 | Estimator 실제 작업 |

**특징**:
- 평균 ~2,867 tokens (6개)
- 200K+ 모델에서 충분한 컨텍스트
- Vector Fallback으로 유연한 쿼리

---

## 🎯 사용 패턴

### 패턴 A: 단일 Agent 작업

**시나리오**: "@Observer, 음악 스트리밍 시장 분석"

```bash
# AI 실행 순서
1. umis_core.yaml 읽기 (INDEX)
2. python3 scripts/query_system_rag.py tool:observer:complete
   → 6,707자 로드 (~1,676 토큰)
3. 바로 실행 (umis.yaml 참조 불필요!)

컨텍스트:
  - umis_core: ~4,000 토큰
  - observer:complete: ~1,676 토큰
  - 합계: ~5,676 토큰

절약: 89% (vs umis.yaml 50,000 토큰)
```

---

### 패턴 B: 복합 작업 (Complete 여러 개)

**시나리오**: "음악 스트리밍 시장 분석" (Observer → Explorer → Quantifier)

```bash
# AI 실행 순서
1. umis_core.yaml 읽기
2. python3 scripts/query_system_rag.py tool:observer:complete
3. python3 scripts/query_system_rag.py tool:explorer:complete
4. python3 scripts/query_system_rag.py tool:quantifier:complete

컨텍스트:
  - umis_core: ~4,000 토큰
  - Complete 3개: ~8,233 토큰
  - 합계: ~12,233 토큰

절약: 76% (vs umis.yaml 50,000 토큰)
```

---

### 패턴 C: Discovery Sprint (6 Agents)

**시나리오**: "피아노 구독 서비스 시장" (목표 불명확)

```bash
# 6개 Complete 로드
python3 scripts/query_system_rag.py tool:observer:complete
python3 scripts/query_system_rag.py tool:explorer:complete
python3 scripts/query_system_rag.py tool:quantifier:complete
python3 scripts/query_system_rag.py tool:validator:complete
python3 scripts/query_system_rag.py tool:guardian:complete
python3 scripts/query_system_rag.py tool:estimator:complete

컨텍스트:
  - umis_core: ~4,000 토큰
  - Complete 6개: ~16,201 토큰
  - 합계: ~20,201 토큰

절약: 75% (vs umis.yaml 50,000 토큰)

권장 모델: claude-sonnet-3.5 (200K) 또는 gemini-1.5-pro (272K)
```

---

## 📋 도구 선택 가이드

### ✅ Complete 사용 (권장)

**언제 사용**:
1. 실제 작업 수행 (분석, 계산, 검증)
2. Agent 역할 전체 이해 필요
3. 협업 방식 파악 필요
4. 원칙, 프레임워크 숙지 필요

**예시**:
- "@Observer, 음악 스트리밍 시장 구조 분석" → tool:observer:complete
- "@Quantifier, SAM 계산" → tool:quantifier:complete
- "@Explorer, 기회 발굴" → tool:explorer:complete

**장점**:
- umis.yaml 참조 불필요 (0% 손실)
- 여전히 75-89% 절약
- 200K+ 모델에서 안정적

---

## 🎯 AI 실행 프로세스

### Step 1: umis_core.yaml 읽기 (INDEX)
```
Lines 40-110 읽기
→ Agent 선택, 도구 식별
```

### Step 2: System RAG 검색
```bash
python3 scripts/query_system_rag.py tool:{agent}:complete
```

### Step 3: 로드된 컨텍스트로 작업
```
Complete: umis.yaml 참조 불필요 ✅
Vector Fallback: 유사 쿼리도 자동 매칭
```

---

## 📊 컨텍스트 효율성

### Before (기존 방식)
```
umis.yaml 전체 읽기
→ 6,050줄, ~200KB, ~50,000 토큰
→ 비효율
```

### After (Complete 사용)
```
단일 Agent: ~5,676 토큰 (89% 절약)
3개 Agent: ~12,233 토큰 (76% 절약)
6개 Agent: ~20,201 토큰 (75% 절약)

→ 여전히 매우 효율적!
```

---

## ⚠️ 모델별 권장사항

### 200K 모델 (claude-sonnet-3.5) ⭐ 권장
- Discovery Sprint: 51% 사용 (안정적)
- 일반 작업: 20-30% 사용 (여유)

### 272K-400K 모델 (gemini-1.5-pro, gpt-4.1)
- 모든 작업 안정적
- Discovery Sprint: 25-38% 사용

### 128K 모델 (gpt-4o-mini)
- Discovery Sprint: 79% 사용 (주의)
- 작업 분할 권장

---

## ✅ 권장 사항

### 1. 기본적으로 Complete 사용 (권장!)

**이유**:
- umis.yaml 참조 불필요 (0% 손실)
- 여전히 75-89% 절약
- 작업 오류 최소화
- 200K+ 모델에서 충분

### 2. 필요한 Agent만 로드

```
❌ 모든 Agent Complete 로드 (6개 = ~16,201 토큰)
✅ 필요한 Agent만 Complete 로드 (2-3개 = ~8,000 토큰)
```

### 3. Vector Fallback 활용

```python
# Task 도구 쿼리해도 자동으로 Complete 매칭
query_system_rag.py tool:observer:market_structure
→ tool:observer:complete 자동 fallback ✅
```

---

## 📚 사용 예시

### 예시 1: Observer 단독 작업

```bash
# 쿼리: "@Observer, 미용 MRO 시장 구조 분석"

# Complete 로드
python3 scripts/query_system_rag.py tool:observer:complete

# 획득 컨텍스트:
- 관찰 원칙 5가지
- 3가지 exclusive_responsibilities 상세
- 8개 extended_frameworks
- 4개 산업별 concrete_examples
- role_boundaries, support_requests
- validation 프로토콜

→ umis.yaml 참조 불필요! 바로 실행 가능!
```

---

### 예시 2: 시장 분석 (3 Agents)

```bash
# 쿼리: "음악 스트리밍 시장 분석"

# 3개 Complete 로드
python3 scripts/query_system_rag.py tool:observer:complete
python3 scripts/query_system_rag.py tool:explorer:complete
python3 scripts/query_system_rag.py tool:quantifier:complete

# 획득:
- Observer: 전체 관찰 방식, 8개 차원, 협업 방식
- Explorer: 7단계 프로세스, 8개 프레임워크, RAG 활용
- Quantifier: SAM 4가지 방법, 계산 원칙, Estimator 협업

→ 3개 Agent 모두 전체 컨텍스트로 완벽한 협업!
```

---

## 🎯 결론

### ✅ 목표 달성

**문제**: "rag 도구가 너무 짧아서 umis.yaml 참조 필요 / 너무 길면 컨텍스트 부담"

**해결**: **2-Tier 구조 (System + Complete)**
- System: 시스템 이해 (9개)
- Complete: 실제 작업 (6개, 0% 손실)

**결과**:
- ✅ umis.yaml 참조 불필요 (Complete 사용 시)
- ✅ 여전히 75-89% 컨텍스트 절약
- ✅ 200K+ 모델에서 안정적
- ✅ Vector Fallback으로 유연한 쿼리

---

## 🔗 관련 문서

- **CONTEXT_WINDOW_STRATEGY.md**: 컨텍스트 윈도우 전략 상세
- **TASK_TOOLS_DECISION.md**: Task 도구 제거 결정 근거
- **umis_core.yaml**: System RAG INDEX
- **SYSTEM_RAG_INTERFACE.md**: AI Assistant 인터페이스

---

**문서 끝**
