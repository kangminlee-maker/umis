# Data Source Priority 재설계 및 Fact-Check Protocol

**날짜**: 2025-11-28  
**버전**: v7.11.1  
**우선순위**: 🚨 CRITICAL  

---

## 🎯 문제 정의

### **발견된 근본 문제**

#### **1. 잘못된 Data Source 우선순위**

**현재 (문제):**
```
Agent → Estimator (추정) → Validator (보조) ❌
```

**문제점:**
- 검증되지 않은 추정치를 먼저 사용
- 실제 데이터가 있어도 추정치를 사용
- One Source of Truth 원칙 위반
- 의사결정 오류 유발

#### **2. Fact-Check Protocol 부재**

**현재 (문제):**
```
Observer → LLM 추정 → 즉시 사용자에게 보고 ❌
```

**문제점:**
- 검증 게이트 없음
- 데이터 출처 추적 불가
- 신뢰도 평가 없음

#### **3. Workflow 순서 문제**

**현재 (문제):**
```
Observer → 시장 구조 작성 → Estimator 추정 → 보고 ❌
```

**올바른 순서:**
```
Observer → LLM 초안 → Validator 데이터 수집 → Fact-check → 보고 ✅
```

---

## ✅ 해결 방안

### **1. Data Source Priority 재정의**

#### **새로운 우선순위 (Tier 시스템)**

```yaml
data_source_priority:
  tier_1_official_data:
    priority: 1 (최우선)
    agent: Validator
    sources:
      - 정부 공식 통계 (통계청, KOSIS, 한국은행)
      - 전자공시 (DART API)
      - 국제기구 (OECD, World Bank, IMF)
      - 업계 협회 공식 자료
    reliability: HIGH (⭐⭐⭐⭐⭐)
    protocol: 모든 Agent는 먼저 Validator에게 데이터 요청
    
  tier_2_verified_commercial:
    priority: 2
    agent: Validator
    sources:
      - 시장조사기관 (가트너, IDC, 유로모니터)
      - 컨설팅사 리포트 (맥킨지, BCG, 베인)
      - 증권사 리서치
    reliability: MEDIUM-HIGH (⭐⭐⭐⭐)
    protocol: Tier 1 없을 때만 사용
    
  tier_3_estimator_fallback:
    priority: 3 (fallback)
    agent: Estimator
    sources:
      - 4-Stage Fusion Architecture
      - Evidence → Prior → Fermi → Fusion
    reliability: MEDIUM (⭐⭐⭐)
    protocol: Tier 1-2 모두 없을 때만 사용
    note: Estimator는 Validator의 fallback
    
  tier_4_llm_baseline:
    priority: 4 (최후)
    agent: All
    sources:
      - LLM 일반 지식
    reliability: LOW (⭐⭐)
    protocol: 초안 작성용, 반드시 Fact-check 필요
```

#### **Protocol: Data Request Flow**

```
Step 1: Agent가 데이터 필요 감지
Step 2: Validator에게 데이터 요청 (Tier 1-2 시도)
  ├─ 데이터 있음 → 사용 ✅
  └─ 데이터 없음 → Step 3
Step 3: Estimator에게 추정 요청 (Tier 3)
  ├─ 추정 가능 → 추정치 사용 (신뢰도 명시) ✅
  └─ 추정 불가 → Step 4
Step 4: LLM 일반 지식 사용 (Tier 4)
  └─ 반드시 Fact-check 표시 ⚠️
```

---

### **2. Fact-Check Protocol 구축**

#### **Mandatory Fact-Check Gate**

```yaml
fact_check_protocol:
  trigger: 모든 Agent가 사용자에게 최종 보고하기 전
  
  gate_keeper: Validator (Rachel)
  
  process:
    step_1_data_audit:
      description: 사용된 모든 데이터의 출처 확인
      check:
        - 데이터 정의 일치 여부
        - 출처 신뢰도
        - 시점 적절성
      output: 데이터 신뢰도 매트릭스
    
    step_2_cross_verification:
      description: 핵심 수치의 교차 검증
      method:
        - 독립적인 소스로 재확인
        - Estimator 교차 추정
        - 논리적 상하한 테스트
      output: 검증 결과 및 신뢰 구간
    
    step_3_reliability_tagging:
      description: 모든 주장에 신뢰도 태그
      tags:
        - ✅ VERIFIED (공식 통계 확인)
        - ⚠️ ESTIMATED (추정치, ±범위 명시)
        - 🔍 UNVERIFIED (검증 필요)
        - ❌ CONFLICTING (모순 데이터)
      output: 태그된 보고서
    
    step_4_approval:
      description: Validator 승인
      pass: 사용자에게 보고 진행
      fail: Agent에게 반려 → 재작업
```

#### **Fact-Check 표시 형식**

```markdown
## 시장 규모

**전체 공연시장**: 1조 8,000억원 (2022)
- ✅ VERIFIED
- 출처: 한국콘텐츠진흥원 '공연산업 백서 2023'
- 정의: 티켓 판매액 기준, 국내 공연장 전체
- 신뢰도: ⭐⭐⭐⭐⭐

**2024년 추정**: 2조원 
- ⚠️ ESTIMATED (±10%)
- 방법: 2022년 기준 CAGR 5.4% 적용
- 근거: 콘텐츠진흥원 과거 5년 평균 성장률
- 신뢰도: ⭐⭐⭐⭐

**기업별 매출**: 하이브 콘서트 2,000억
- ❌ CONFLICTING - 철회 필요
- 문제: 정의 불명확 (콘서트 vs 전체, 국내 vs 해외)
- 조치: Validator 재수집 또는 범위로 제시
```

---

### **3. Observer Workflow 재설계**

#### **현재 워크플로우 (문제)**

```
Observer 활동:
1. LLM 지식으로 시장 구조 작성
2. Estimator에게 수치 요청
3. 바로 사용자에게 보고

문제점:
❌ Validator 우회
❌ Fact-check 없음
❌ 검증되지 않은 추정치 보고
```

#### **새로운 워크플로우 (해결)**

```
Phase 1: Draft (초안 작성)
├─ Observer: LLM 지식 기반 구조 초안 작성
├─ 출력: "Draft: 검증 전 초안" 명시
└─ 사용자에게 보고 금지

Phase 2: Data Collection (데이터 수집)
├─ Observer → Validator: 필요한 데이터 목록 전달
├─ Validator: Tier 1-2 데이터 수집
│   ├─ 공식 통계 검색
│   ├─ DART 재무 데이터
│   └─ 업계 리포트
├─ 데이터 있음 → Phase 3
└─ 데이터 없음 → Estimator fallback

Phase 3: Fact-Check (사실 확인)
├─ Validator: 수집된 데이터 검증
│   ├─ 정의 일치 여부
│   ├─ 신뢰도 평가
│   └─ 교차 검증
├─ Observer: 초안을 검증된 데이터로 업데이트
└─ 출력: Fact-checked 보고서

Phase 4: Final Report (최종 보고)
├─ 모든 데이터에 출처 및 신뢰도 명시
├─ Validator 승인 완료
└─ 사용자에게 보고 ✅
```

---

## 🔨 구현 계획

### **Step 1: umis.yaml 수정**

#### **1.1 universal_tools 섹션 추가 (모든 Agent)**

```yaml
universal_tools:
  data_request_protocol:
    tier_1_validator_first:
      priority: 1
      agent: Validator
      when: 데이터가 필요할 때 가장 먼저
      method: validator.search_data(query, domain, region)
      output: 공식 데이터 또는 None
    
    tier_2_estimator_fallback:
      priority: 2
      agent: Estimator
      when: Validator가 데이터를 찾지 못했을 때만
      method: estimator.estimate(question, domain, region)
      output: 추정치 (신뢰 구간 포함)
      note: ⚠️ 추정치는 반드시 신뢰도 명시
    
  fact_check_protocol:
    gate: 모든 최종 보고 전 Validator 검증 필수
    validator_approval_required: true
    reliability_tagging: mandatory
```

#### **1.2 Observer 섹션 수정**

```yaml
observer:
  workflow:
    phase_1_draft:
      description: LLM 기반 초안 작성
      output: "Draft 보고서 (검증 전)"
      user_report: false (사용자에게 보고 금지)
    
    phase_2_data_collection:
      step_1: Validator에게 데이터 요청 목록 전달
      step_2: Validator가 Tier 1-2 데이터 수집
      step_3: 데이터 없으면 Estimator fallback
    
    phase_3_fact_check:
      step_1: Validator 데이터 검증
      step_2: 초안을 검증된 데이터로 업데이트
      step_3: 신뢰도 태깅
    
    phase_4_final_report:
      validator_approval: required
      reliability_matrix: included
      user_report: true (승인 후 보고)
  
  data_source_priority:
    priority_1: Validator (공식 데이터)
    priority_2: Estimator (fallback)
    priority_3: LLM 지식 (초안만)
    
  mandatory_validation:
    before_report: true
    validator: Rachel
    tags: [VERIFIED, ESTIMATED, UNVERIFIED]
```

#### **1.3 Quantifier 섹션 수정**

```yaml
quantifier:
  sam_calculation:
    data_collection_protocol:
      step_0: Validator에게 데이터 요청 (최우선)
      step_1: 공식 통계 확인
      step_2: 없으면 Estimator 추정
      step_3: SAM 계산
      step_4: Validator Fact-check
    
  universal_tools:
    validator_collaboration:
      priority: 1 (최우선)
      when: 모든 데이터 필요 시
      frequency: ★★★★★ 항상 사용
    
    estimator_collaboration:
      priority: 2 (fallback)
      when: Validator가 데이터 없을 때만
      frequency: ★★★ 제한적 사용
```

#### **1.4 Explorer 섹션 수정**

```yaml
explorer:
  workflow:
    opportunity_discovery:
      step_1: Albert의 Market Reality Report 입력
      step_2: Validator에게 기회 관련 데이터 요청
      step_3: Estimator로 시장 크기 가늠 (fallback)
      step_4: Validator Fact-check
      step_5: 검증된 기회 포트폴리오 제출
```

---

### **Step 2: .cursorrules 업데이트**

```yaml
mandatory_protocols:
  data_source_priority:
    rule: Validator First, Estimator Fallback
    enforcement: 모든 Agent 필수 준수
    violation: Validator 우회 시 보고 반려
  
  fact_check_gate:
    rule: 최종 보고 전 Validator 승인 필수
    enforcement: 승인 없는 보고 금지
    violation: 사용자에게 보고 불가
```

---

### **Step 3: 검증 스크립트 작성**

```python
# scripts/validate_data_source_priority.py

def check_agent_workflow(agent_name):
    """Agent가 Data Source Priority를 준수하는지 확인"""
    
    checks = [
        {
            "name": "Validator First",
            "check": "Validator 먼저 호출하는가?",
            "required": True
        },
        {
            "name": "Estimator Fallback",
            "check": "Estimator는 Validator 실패 후만 호출하는가?",
            "required": True
        },
        {
            "name": "Fact-Check Gate",
            "check": "최종 보고 전 Validator 승인하는가?",
            "required": True
        }
    ]
    
    # 검증 로직
    ...
```

---

## 📊 예상 효과

### **Before (문제)**

```
Observer 보고서:
- 하이브 콘서트 매출: 2,000억원
- 출처: ❓ (없음)
- 신뢰도: ❓ (없음)
- 검증: ❌ (안함)
→ 의사결정 오류 발생 위험 ⚠️
```

### **After (해결)**

```
Observer 보고서:
- 전체 공연시장: 1조 8,000억원 (2022)
  ✅ VERIFIED
  출처: 한국콘텐츠진흥원
  신뢰도: ⭐⭐⭐⭐⭐
  
- 하이브 전체 매출: 2조 1,807억원 (2023)
  ✅ VERIFIED
  출처: DART 전자공시
  신뢰도: ⭐⭐⭐⭐⭐
  
- 하이브 콘서트 비중: 30-40% (추정)
  ⚠️ ESTIMATED (±10%)
  근거: 업계 평균 및 사업보고서 힌트
  신뢰도: ⭐⭐⭐
  
→ 신뢰할 수 있는 의사결정 기반 ✅
```

---

## ⏱️ 구현 일정

1. **umis.yaml 수정** (2시간)
   - universal_tools 추가
   - 모든 Agent에 Data Source Priority 반영
   
2. **.cursorrules 업데이트** (30분)
   - mandatory_protocols 추가
   
3. **검증 스크립트 작성** (1시간)
   - validate_data_source_priority.py
   
4. **통합 테스트** (1시간)
   - 전체 워크플로우 검증
   
5. **문서화** (30분)
   - 변경사항 정리

**총 소요 시간**: 약 5시간

---

## ✅ 체크리스트

- [ ] umis.yaml: universal_tools 추가
- [ ] umis.yaml: Observer workflow 재설계
- [ ] umis.yaml: Quantifier Data Source Priority 수정
- [ ] umis.yaml: Explorer Data Source Priority 수정
- [ ] .cursorrules: mandatory_protocols 추가
- [ ] 검증 스크립트 작성
- [ ] 통합 테스트
- [ ] 문서화
- [ ] CHANGELOG 업데이트

---

**우선순위**: 🚨 CRITICAL  
**담당**: AI Assistant  
**마감**: 2025-11-28  

