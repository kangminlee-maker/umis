# UMIS Guidelines 모듈화 검토

**날짜:** 2025-11-02  
**배경:** RAG 도입으로 모듈화 시작, Guidelines도 모듈화 필요

---

## 🔍 4가지 핵심 질문

### 1. umis_guidelines.yaml 모듈화 방법
### 2. umis_business_model_patterns.yaml 필요성
### 3. umis_ai_guide.yaml 필요성
### 4. "guidelines" 파일명 적합성

---

## 💡 1. Guidelines 모듈화 방법

### 현재 문제

```yaml
umis_guidelines.yaml:
  크기: 5,428줄!
  
  내용:
    • System Architecture
    • Adaptive Intelligence
    • Proactive Monitoring
    • Support & Validation
    • Data Integrity
    • Agents (5개)
    • Owner
    • Creative Boost
    • Implementation Guide
  
  문제:
    • 너무 큼 (5천 줄!)
    • 찾기 어려움
    • 수정 위험 (한 줄 실수 → 전체 영향)
```

### 모듈화 방안

**Option A: Section별 분리 (계층 유지)**

```
umis/
├── core/
│   ├── system.yaml (Section 1)
│   ├── adaptive.yaml (Section 2)
│   ├── monitoring.yaml (Section 3)
│   └── data_integrity.yaml (Section 5)
│
├── agents/
│   ├── observer.yaml (Albert)
│   ├── explorer.yaml (Steve)
│   ├── quantifier.yaml (Bill)
│   ├── validator.yaml (Rachel)
│   └── guardian.yaml (Stewart)
│
├── roles/
│   └── owner.yaml
│
├── modules/
│   ├── creative_boost.yaml
│   └── implementation_guide.yaml
│
└── index.yaml (전체 구조 + 순서)

사용:
  Cursor:
    @umis/index.yaml (전체 보기)
    @umis/agents/explorer.yaml (Steve만)
```

**장점:**
```yaml
✅ 명확한 구조
✅ 쉬운 탐색
✅ 안전한 수정
✅ 독립적 관리
```

**단점:**
```yaml
⚠️ 파일 많음 (15개)
⚠️ Cursor 첨부 복잡?
```

---

**Option B: 핵심만 분리 (최소 모듈화)**

```
umis/
├── umis_system.yaml (System + Architecture)
├── umis_agents.yaml (5 Agents)
├── umis_owner.yaml (Owner)
└── umis_protocols.yaml (나머지)

사용:
  Cursor:
    @umis/umis_agents.yaml (주로 사용)
    @umis/umis_system.yaml (필요 시)
```

**장점:**
```yaml
✅ 단순 (4개)
✅ Cursor 첨부 쉬움
✅ 빠른 접근
```

**단점:**
```yaml
⚠️ 여전히 큼 (각 1-2천 줄)
```

---

**Option C: Agent 중심 + Include**

```
umis/
├── agents/
│   ├── observer.yaml
│   ├── explorer.yaml
│   ├── quantifier.yaml
│   ├── validator.yaml
│   └── guardian.yaml
│
├── shared/
│   ├── system.yaml
│   ├── protocols.yaml
│   └── frameworks.yaml
│
└── umis.yaml (메인, include만)

umis.yaml:
  # 메인 파일 (100줄)
  version: "6.3.0-alpha"
  
  includes:
    - shared/system.yaml
    - shared/protocols.yaml
    - agents/observer.yaml
    - agents/explorer.yaml
    - agents/quantifier.yaml
    - agents/validator.yaml
    - agents/guardian.yaml
    - shared/frameworks.yaml

사용:
  Cursor:
    @umis/umis.yaml → 자동 include!
    @umis/agents/explorer.yaml → Steve만
```

**장점:**
```yaml
✅ 구조 명확
✅ 호환성 (include로 monolithic처럼)
✅ 선택적 접근 (Agent별)
✅ 기존 구조 파악 쉬움 (umis.yaml)
```

**추천:** ⭐ Option C!

---

## 💡 2. umis_business_model_patterns.yaml 필요성

### 현재 상태

```yaml
역할:
  Steve가 패턴 검색에 사용
  
RAG 도입 후:
  • 31개 패턴 → data/chunks/explorer_business_models.jsonl
  • RAG 자동 검색
  
  → 원본 YAML 불필요? 🤔
```

### 분석

**제거 시:**
```yaml
장점:
  ✅ 중복 제거
  ✅ 단순화

문제:
  ❌ 사용자가 수정?
     데이터 추가 시 어디에?
     
     Before:
       Cursor: "코웨이에 해지율 추가"
       → umis_business_model_patterns.yaml 수정
       → RAG 재구축
     
     After:
       data/chunks/explorer_*.jsonl 직접 수정?
       → 사용자가 JSONL 이해?
       → 복잡! ❌
```

**유지 시:**
```yaml
역할 변경:
  Before: Steve가 직접 읽음
  After: RAG 소스!
  
  흐름:
    사용자 수정 (YAML)
    ↓
    scripts/01_convert_yaml.py (자동)
    ↓
    data/chunks/ (자동)
    ↓
    RAG 재구축 (자동)
    ↓
    Steve 사용

  → 사용자 친화! ✅
```

**결론:** ✅ 유지!

**이유:**
- 사용자 수정 소스
- RAG 빌드 소스
- YAML = 사용자 친화

**위치:**
```
umis/sources/ (신규 폴더)
  ├── business_model_patterns.yaml
  └── disruption_patterns.yaml
```

---

## 💡 3. umis_ai_guide.yaml 필요성

### 현재 상태

```yaml
umis_ai_guide.yaml:
  크기: 1,084줄
  
  내용:
    • AI 사용법
    • Cursor 가이드
    • Token 관리
    • 프롬프트 팁
```

### 분석

**vs .cursorrules:**

```yaml
umis_ai_guide.yaml:
  • 일반적 AI 가이드
  • Cursor 특정 아님
  • 긴 설명 (1,084줄)

.cursorrules:
  • Cursor 전용!
  • 자동화 규칙
  • 간결 (243줄)

중복:
  Token 관리 (양쪽에)
  Agent 사용법 (양쪽에)
  
  → 90% 중복! ⚠️
```

**제거 시:**

```yaml
대체:
  1. .cursorrules (Cursor 자동화)
  2. umis/agents/*.yaml (Agent별 상세)
  3. README.md (빠른 시작)

효과:
  ✅ 중복 제거
  ✅ 단순화
  ✅ Cursor 최적화

문제:
  ❌ 일반 AI 사용?
     Claude Desktop, ChatGPT 등?
     
     하지만:
       v6.3.0-alpha = Cursor 전용!
       → 일반 AI 사용 안 함
       → 문제 없음! ✅
```

**결론:** ❌ 제거!

**이유:**
- 90% .cursorrules와 중복
- Cursor 전용이므로 불필요
- 단순화

---

## 💡 4. "guidelines" 파일명

### 검토

```yaml
현재: umis_guidelines.yaml

문제:
  "guidelines" = 가이드라인?
  
  실제 내용:
    • System 정의
    • Agent 스펙
    • 프로토콜
    • 프레임워크
  
  → "Guidelines"는 부적절! ⚠️
```

### 대안

```yaml
Option A: umis_system.yaml
  의미: 시스템 정의
  명확도: 높음
  적합성: ⭐⭐⭐⭐

Option B: umis_framework.yaml
  의미: 프레임워크
  명확도: 높음
  적합성: ⭐⭐⭐⭐

Option C: umis_spec.yaml
  의미: 스펙
  명확도: 중간
  적합성: ⭐⭐⭐

Option D: umis.yaml (모듈화 시)
  의미: 메인 인덱스
  명확도: 최고
  적합성: ⭐⭐⭐⭐⭐
```

**추천:**

```yaml
모듈화 시:
  umis/umis.yaml (메인)
  
  간결:
    # UMIS v6.3.0-alpha
    
    includes:
      - core/system.yaml
      - agents/*.yaml
      - ...

비모듈화 시:
  umis_system.yaml

이유:
  "guidelines"보다 "system"이 정확
```

---

## 🎯 최종 추천

### 구조

```
umis/
├── umis.yaml (메인, 100줄)
│   → includes로 전체 통합
│
├── core/
│   ├── system.yaml
│   ├── adaptive.yaml
│   ├── monitoring.yaml
│   └── data_integrity.yaml
│
├── agents/
│   ├── observer.yaml
│   ├── explorer.yaml
│   ├── quantifier.yaml
│   ├── validator.yaml
│   └── guardian.yaml
│
├── roles/
│   └── owner.yaml
│
├── modules/
│   ├── creative_boost.yaml
│   └── implementation.yaml
│
└── sources/ (RAG 소스!)
    ├── business_model_patterns.yaml
    └── disruption_patterns.yaml
```

### 사용

```
Cursor:
  @umis/umis.yaml (전체)
  @umis/agents/explorer.yaml (Steve만)

사용자 수정:
  umis/sources/*.yaml
  → RAG 자동 재구축
```

### 삭제

```yaml
❌ umis_ai_guide.yaml
   이유: .cursorrules로 대체

❌ umis_examples.yaml
   이유: 각 Agent yaml에 통합

유지:
  ✅ umis/sources/ (RAG 소스)
```

---

**실행할까요?**

