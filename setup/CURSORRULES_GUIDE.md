# .cursorrules 가이드

**버전**: v7.6.2  
**대상**: Cursor 사용자, AI 개발자  
**파일**: `.cursorrules` (루트, 725줄)  
**목적**: UMIS Cursor 자동화 규칙 이해 및 활용

---

## 🎯 .cursorrules란?

### 개요

**Cursor AI가 UMIS를 이해하고 작동하는 핵심 규칙 파일**

```yaml
위치: /Users/kangmin/umis_main_1103/umis/.cursorrules
크기: 724줄
역할: Cursor AI 자동화 규칙 정의

효과:
  ✅ AI가 UMIS 구조 자동 이해
  ✅ Agent 멘션 (@Explorer, @Fermi) 자동 처리
  ✅ System RAG 자동 활용
  ✅ 컨텍스트 87% 절약
```

---

## 📋 주요 섹션 (7개)

### PART 1: UMIS 개념 (Line 1-75)

**내용**:
```yaml
system:
  version: 7.6.2
  agents: 6개 (Observer, Explorer, Quantifier, Validator, Guardian, Estimator)
  
  rag:
    architecture: v3.0 (4-Layer)
    collections: 6개 Agent별
    total_tools: 31개
```

**역할**: AI가 UMIS 전체 구조 파악

---

### PART 2: 자동화 규칙 (Line 76-164)

**내용**:
- 초기 설치 자동화
- Agent 이름 커스터마이징
- YAML 수정 → RAG 재구축
- Explorer RAG 자동 활용
- 데이터 추가 자동화

**역할**: 반복 작업 자동화

---

### PART 3: 경로 & 설정 (Line 166-186)

**내용**:
```yaml
paths:
  root, setup, scripts, data, docs, dev_docs, projects

files:
  umis.yaml, UMIS_ARCHITECTURE_BLUEPRINT.md, schema_registry.yaml
```

**역할**: 파일 위치 자동 인식

---

### PART 4: 메시지 템플릿 (Line 188-198)

**내용**:
- 한국어 응답
- 이모지 최소화
- progress, success, error 템플릿

**역할**: 일관된 사용자 경험

---

### PART 5: 폴더 구조 (Line 200-210)

**내용**: 각 폴더 역할 정의

**역할**: AI가 폴더 용도 이해

---

### PART 6: Guardian Meta-RAG (Line 212-260)

**내용**:
- 프로젝트 시작 시 자동 활성화
- 순환 감지
- 산출물 평가

**역할**: Guardian 자동 작동

---

### PART 7: System RAG (Line 262-658) ⭐ 핵심!

**내용**:
- AI 필수 실행 프로세스 (4단계)
- Agent 멘션 감지
- tool_key 자동 매핑
- System RAG 자동 실행
- 사용 예시 4개

**역할**: 컨텍스트 87% 절약

---

## 🆕 v7.6.2 주요 변경사항

### 1. Estimator 완전 통합

```yaml
agents.Estimator:
  role: value_estimation_3tier ⭐
  rag: true
  version: v7.6.2 (5-Phase ✅)

collections.estimator: ⭐ 신규
  - learned_rules
  - canonical_store
  - estimator (Agent View)

total_tools: 28 → 31 (+3개 Estimator)
```

---

### 2. Agent 감지 확장

```yaml
agent_detection:
  - "@Fermi" → estimator ⭐
  - "@Estimator" → estimator ⭐
  - "값 추정" → estimator ⭐
  - "LTV|CAC|Churn" → estimator ⭐
```

---

### 3. Estimator 도구 매핑

```yaml
tool_key_mapping.estimator: ⭐ 신규
  "추정": tool:estimator:estimate
  "LTV|CAC|Churn|ARPU": tool:estimator:estimate
  "Payback|Rule of 40|NRR": tool:estimator:estimate
  "교차검증": tool:estimator:cross_validation
  "학습": tool:estimator:learning_system
```

---

### 4. Estimator 사용 예시

```yaml
example_4_estimator: ⭐ 신규
  "@Fermi, SaaS LTV는?"
  → umis_core.yaml 읽기
  → tool:estimator:estimate 로드
  → Tier 1 → 2 → 3 자동 시도
  → 결과 반환
```

---

## 🔧 사용 방법

### AI가 자동으로 읽음

```yaml
Cursor Composer 또는 Chat:
  "@Explorer, 시장 분석해줘"

→ Cursor AI가 자동으로:
  1. .cursorrules 읽기
  2. "@Explorer" 감지 → agent=explorer
  3. "시장 분석" → tool_key 식별
  4. System RAG 실행
  5. 로드된 도구로 작업
```

**사용자 개입**: 없음 (완전 자동)

---

### 수동 커스터마이징 (선택)

**파일 수정**:
```yaml
# .cursorrules 파일 열기

# 예: Agent 이름 변경 (대신 agent_names.yaml 권장)
agents:
  Explorer: {name: Alex, ...}  # Steve → Alex

# 예: 메시지 커스터마이징
messages:
  success: "🎉 {result} 완료!"  # 커스텀
```

**저장 후**: Cursor 재시작 (Cmd+Shift+P → Reload Window)

---

## 💡 활용 팁

### 1. Agent 멘션

```yaml
지원되는 멘션:
  @Explorer, @Steve      # Explorer
  @Quantifier, @Bill     # Quantifier
  @Validator, @Rachel    # Validator
  @Observer, @Albert     # Observer
  @Guardian, @Stewart    # Guardian
  @Fermi, @Estimator     # Estimator ⭐

자동 처리:
  → agent 식별
  → tool_key 매핑
  → System RAG 실행
```

---

### 2. 키워드 감지

```yaml
"패턴 매칭" → tool:explorer:pattern_search
"시장 규모" → tool:quantifier:sam_4methods
"LTV는?" → tool:estimator:estimate ⭐
"Payback" → tool:estimator:estimate ⭐
```

**자동**: AI가 키워드 감지 → 도구 로드

---

### 3. System RAG 자동 실행

```yaml
사용자: "@Fermi, LTV는?"

AI 자동 프로세스:
  1. .cursorrules 읽기
  2. "@Fermi" → estimator
  3. "LTV" → tool:estimator:estimate
  4. System RAG 실행:
     python3 scripts/query_system_rag.py tool:estimator:estimate
  5. 로드된 content (500줄) 활용
  6. LTV 추정 (Tier 1 → 2 → 3)

컨텍스트: 949 + 500 = 1,449줄 (vs 6,663줄, 78% 절약)
```

---

## ⚠️ 주의사항

### 수정 시

```yaml
❌ 하지 마세요:
  - .cursorrules 삭제 (AI가 UMIS 인식 못 함)
  - YAML 형식 깨뜨리기
  - 필수 섹션 제거 (PART 7 System RAG)

✅ 해도 됨:
  - 메시지 커스터마이징
  - 경로 조정 (프로젝트 구조 다르면)
  - 폴더 설명 추가
```

---

### 버전 업데이트

```yaml
새 버전 나오면:
  1. version 업데이트
  2. agents 섹션 확인
  3. total_tools 확인
  4. 신규 도구 tool_key 추가
  5. 사용 예시 추가
```

---

## 🎯 트러블슈팅

### AI가 Agent를 인식 못 함

**문제**: "@Fermi" 했는데 작동 안 함

**원인**: .cursorrules 손상 또는 최신 버전 아님

**해결**:
```bash
# .cursorrules 복구
git checkout .cursorrules

# 또는 v7.6.2 버전 확인
head -3 .cursorrules
# v7.6.2 확인
```

---

### System RAG가 작동 안 함

**문제**: System RAG 실행 안 됨

**원인**: Collection 없음

**해결**:
```bash
python3 scripts/build_system_knowledge.py
# 1분 소요, 31개 도구 인덱싱
```

---

### Estimator 도구가 없음

**문제**: tool:estimator:estimate 없음

**원인**: System RAG 구버전

**해결**:
```bash
# System RAG 재빌드
python3 scripts/build_system_knowledge.py

# 확인
python3 scripts/query_system_rag.py --list | grep estimator
# tool:estimator:estimate
# tool:estimator:cross_validation
# tool:estimator:learning_system
```

---

## 📚 관련 문서

### 이해

- **UMIS_ARCHITECTURE_BLUEPRINT.md**: 전체 시스템 구조
- **umis_core.yaml**: System RAG INDEX
- **config/tool_registry.yaml**: 31개 도구 정의

### 설정

- **config/agent_names.yaml**: Agent 이름 커스터마이징 (권장)
- **config/runtime.yaml**: 실행 모드 (rag_full)
- **config/llm_mode.yaml**: LLM 모드 (Native/External)

### 사용

- **umis_examples.yaml**: UMIS 사용 예시
- **START_HERE.md**: 빠른 시작

---

## 🎊 v7.6.2 .cursorrules

### 현재 상태

```yaml
버전: v7.6.2
크기: 724줄
Agent: 6개 (Estimator 포함)
도구: 31개
예시: 4개 (Estimator 추가)

기능:
  ✅ 6-Agent 감지
  ✅ Estimator 완전 통합
  ✅ 12개 비즈니스 지표 지원
  ✅ System RAG 87% 절약
  ✅ Meta-RAG 자동화

상태: ✅ Production Ready
```

---

## 💡 Best Practices

### 1. 그대로 사용 (권장)

```yaml
.cursorrules는 건드리지 마세요!

이유:
  - 검증된 설정
  - v7.6.2 완벽 반영
  - AI 최적화 완료

커스터마이징 필요 시:
  → agent_names.yaml 사용 (Agent 이름)
  → runtime.yaml 사용 (실행 모드)
```

---

### 2. 백업

```yaml
수정 전:
  cp .cursorrules .cursorrules.backup
  
복구:
  cp .cursorrules.backup .cursorrules
```

---

### 3. 버전 확인

```yaml
현재 버전:
  head -3 .cursorrules
  # v7.6.2 확인

업데이트 필요 시:
  → GitHub에서 최신 버전 다운로드
  → 또는 git pull
```

---

## 🚀 실전 활용

### Estimator 사용 (v7.6.2)

```yaml
Cursor에서:
  "@Fermi, B2B SaaS LTV는?"

→ .cursorrules가 자동으로:
  1. @Fermi 감지 → estimator
  2. "LTV" → tool:estimator:estimate
  3. System RAG 실행 (500줄 로드)
  4. Tier 1 → 2 → 3 자동 시도
  5. 결과 반환

사용자: 질문만! ✨
```

---

### 비즈니스 지표 자동 계산

```yaml
지원되는 질문:
  "LTV는?"
  "CAC는?"
  "Churn Rate는?"
  "Payback Period는?"
  "Rule of 40은?"
  "NRR은?"
  "Gross Margin은?"

→ 모두 자동으로 Estimator 호출
→ 템플릿 매칭 (12개 지표)
→ Tier 3 재귀 추정
→ 100% 답변 가능
```

---

## 📊 성능

### 컨텍스트 절약

```yaml
.cursorrules 없이 (비효율):
  umis.yaml 전체 로드: 6,663줄

.cursorrules 사용 (효율):
  umis_core.yaml: 949줄
  + 필요한 도구만: 500줄
  = 1,449줄

절약: 78% (5,214줄 절약)
```

---

## ✅ 체크리스트

### .cursorrules 정상 작동 확인

- [ ] 버전 v7.6.2 확인
- [ ] @Fermi 멘션 작동
- [ ] System RAG 자동 실행
- [ ] Estimator 도구 3개 로드 가능
- [ ] 메시지 v7.6.2 표시

**모두 ✅**: 정상 작동  
**하나라도 ❌**: .cursorrules 업데이트 필요

---

## 🎯 결론

### .cursorrules는 필수!

```yaml
이유:
  ✅ UMIS 자동화의 핵심
  ✅ AI가 UMIS 이해하는 방법
  ✅ 컨텍스트 87% 절약
  ✅ System RAG 자동 실행

권장:
  → 수정하지 말 것
  → 백업 유지
  → 최신 버전 사용 (v7.6.2)

커스터마이징:
  → agent_names.yaml 사용
  → runtime.yaml 사용
```

---

**업데이트**: 2025-11-10  
**버전**: v7.6.2  
**상태**: ✅ Production Ready

🎉 **.cursorrules - UMIS 자동화의 핵심!**

