# Phase 5: 학습 시스템 구현 가이드

**목표**: Tier 2/3 결과를 Tier 1로 자동 편입하여 사용할수록 빨라지는 시스템 구축  
**기간**: 1-2일  
**상태**: 설계 완료, 구현 대기  
**우선순위**: P1 (핵심 기능)

---

## 🎯 목표 및 핵심 개념

### 학습 시스템의 목적

```yaml
Before (현재):
  매번 Tier 2 실행 → 느림 (3-8초)
  
After (Phase 5 완료):
  첫 실행: Tier 2 (3-8초) + 학습
  재실행: Tier 1 (<0.5초) ✨
  
선순환:
  사용 ↑ → 학습 ↑ → Tier 1 규칙 ↑ → 속도 ↑
```

### 핵심 컴포넌트

```yaml
1. Learning Writer:
   Tier 2 결과 → Canonical 저장

2. Projection Generator:
   Canonical → Projected (guestimation view)

3. Tier 1 RAG Searcher:
   학습된 규칙 검색 (이미 구현됨!)

4. User Contribution:
   사용자 확정 사실 즉시 저장
```

---

## 📋 구현 체크리스트

### Step 1: Learning Writer 구현 (3-4시간)

**파일 생성**: `umis_rag/guestimation_v3/learning_writer.py`

**기능**:
- [x] EstimationResult → LearnedRule 변환
- [x] Canonical Index에 저장
- [x] 메타데이터 추가 (domain, region, time)
- [x] 학습 가치 판단 (confidence >= 0.80)

**필요 작업**:

```python
class LearningWriter:
    """Tier 2 결과를 Canonical에 저장"""
    
    def __init__(self, canonical_collection):
        self.canonical = canonical_collection
    
    def save_learned_rule(
        self,
        question: str,
        result: EstimationResult,
        context: Context
    ) -> str:
        """
        학습된 규칙 저장
        
        Returns:
            rule_id: "RULE-DOMAIN-001" 형식
        """
        pass
    
    def should_learn(self, result: EstimationResult) -> bool:
        """학습 가치 판단 (tier2.py에서 가져옴)"""
        pass
```

**데이터 형식**:

```yaml
canonical_chunk_id: "CAN-rule-churn-001"

chunk_type: "learned_rule"  # 새 타입!

content: |
  질문: "B2B SaaS Churn Rate는?"
  값: 6%
  범위: 5-7%
  신뢰도: 0.85
  
  증거:
    - 통계 패턴: 정규분포 [5%, 7%], mean=6%
    - RAG 벤치마크: "5-7%" (3개)
    - Physical: 백분율 [0, 100]

metadata:
  # 핵심 메타데이터
  rule_type: "learned"
  value: 0.06
  unit: "percentage"
  confidence: 0.85
  
  # 맥락
  domain: "B2B_SaaS"
  region: null
  time_period: "2024"
  
  # 통계
  usage_count: 1
  created_at: "2024-11-07T10:30:00"
  last_used: "2024-11-07T10:30:00"
  
  # 증거
  evidence_sources: ["statistical_pattern", "rag_benchmark", "physical"]
  evidence_count: 5
  judgment_strategy: "weighted_average"

sections:
  - agent_view: "guestimation"
    anchor_path: "learned_rules.churn_rate"
    content_hash: "sha256:abc123..."
```

### Step 2: Projection Generator 구현 (2-3시간)

**파일 수정**: `umis_rag/projection/rule_based_projector.py`

**기능**:
- [x] Canonical의 "learned_rule" 타입 감지
- [x] Projected Index (agent_view=guestimation) 생성
- [x] 청킹: 1질문 = 1청크
- [x] 메타데이터 자동 추출

**Projection Rule 추가**:

```yaml
# config/projection_rules.yaml에 추가

chunk_type_rules:
  
  learned_rule:
    target_agents: ["guestimation"]
    
    strategy: "direct_projection"
    
    metadata_mapping:
      value: "value"
      unit: "unit"
      confidence: "confidence"
      domain: "domain"
      region: "region"
      time_period: "time_period"
    
    ttl: "persistent"  # 학습된 규칙은 영구 저장
```

**결과 형식**:

```yaml
projected_chunk_id: "PRJ-rule-churn-001"

agent_view: "guestimation"

canonical_chunk_id: "CAN-rule-churn-001"

content: |
  질문: "B2B SaaS Churn Rate는?"
  값: 6%
  범위: 5-7%

metadata:
  # Guestimation 특화
  guestimation_value: 0.06
  guestimation_unit: "percentage"
  guestimation_confidence: 0.85
  guestimation_domain: "B2B_SaaS"
  guestimation_time: "2024"
  
  # 원본 링크
  canonical_chunk_id: "CAN-rule-churn-001"
  
  # 검색용
  usage_count: 1
```

### Step 3: Tier 1-Learning 통합 (1-2시간)

**파일 수정**: `umis_rag/guestimation_v3/tier1.py`

**변경 사항**:

```python
# 이미 구현된 RAG 검색 활용!

class Tier1FastPath:
    
    def estimate(self, question: str, context: Context):
        
        # 1. Built-in 규칙 체크 (기존)
        result = self._check_builtin_rules(question, context)
        if result:
            return result
        
        # 2. 학습된 규칙 검색 (추가!)
        learned_result = self.rag_searcher.search_learned_rule(
            question=question,
            context=context,
            top_k=5,
            min_similarity=0.85  # 높은 threshold (False Positive 방지)
        )
        
        if learned_result and learned_result.similarity >= 0.85:
            return self._format_learned_result(learned_result)
        
        # 3. Tier 2로
        return None
```

**필요 작업**:
- RAG Searcher에 `search_learned_rule()` 메서드 구현
- similarity threshold 조정 (False Positive 방지)
- 맥락 필터링 (domain, region 일치)

### Step 4: Tier 2-Learning 연결 (1시간)

**파일 수정**: `umis_rag/guestimation_v3/tier2.py`

**변경 사항**:

```python
class Tier2JudgmentPath:
    
    def __init__(self, ..., learning_writer=None):
        # ...
        self.learning_writer = learning_writer
    
    def estimate(self, question: str, context: Context):
        
        # 기존 Tier 2 로직...
        result = self._make_judgment(...)
        
        # 학습 가치 판단
        if self._should_learn(result):
            if self.learning_writer:
                rule_id = self.learning_writer.save_learned_rule(
                    question=question,
                    result=result,
                    context=context
                )
                print(f"✅ 학습 완료: {rule_id}")
        
        return result
```

**이미 구현된 것**:
- `_should_learn()` 메서드 (confidence >= 0.80, 증거 2개 이상)

**추가 작업**:
- LearningWriter 인스턴스 연결만 하면 됨!

### Step 5: 사용자 기여 파이프라인 (2-3시간)

**파일 생성**: `umis_rag/guestimation_v3/user_contribution.py`

**기능**:
- [x] 사용자가 확정 사실 제공
- [x] 즉시 Canonical에 저장
- [x] Projected 자동 생성
- [x] 3가지 타입 구분

**사용자 기여 타입**:

```yaml
1. 확정 사실 (Definite Fact):
   예시: "우리 회사 직원 수: 150명"
   처리: 즉시 Canonical 저장 (confidence=1.0)
   검증: 없음
   
2. 업계 상식 (Domain Knowledge):
   예시: "한국 편의점 하루 매출: 150만원"
   처리: 임시 저장 → 3회 일치 시 확정
   검증: 교차 확인
   
3. 개인 경험 (Personal Experience):
   예시: "내가 아는 카페는 월 3000만원"
   처리: 참고용 (낮은 confidence)
   검증: 표시만
```

**API**:

```python
class UserContribution:
    
    def add_definite_fact(
        self,
        question: str,
        value: float,
        unit: str,
        source: str = "user_confirmed"
    ) -> str:
        """확정 사실 즉시 저장"""
        pass
    
    def add_domain_knowledge(
        self,
        question: str,
        value: float,
        source: str
    ) -> str:
        """업계 상식 임시 저장"""
        pass
    
    def add_personal_experience(
        self,
        question: str,
        value: float,
        context: str
    ) -> str:
        """개인 경험 참고용"""
        pass
```

---

## 🔧 구현 순서 (단계별)

### Day 1: 핵심 파이프라인

**Morning (4시간)**:
```bash
# 1. Learning Writer 구현
touch umis_rag/guestimation_v3/learning_writer.py

# 작성 내용:
# - LearningWriter 클래스
# - save_learned_rule() 메서드
# - LearnedRule → Canonical 변환

# 2. 테스트
python scripts/test_learning_writer.py
```

**Afternoon (4시간)**:
```bash
# 3. Projection Generator 수정
vim umis_rag/projection/rule_based_projector.py

# 추가:
# - learned_rule 타입 처리
# - guestimation view 생성

# 4. projection_rules.yaml 업데이트
vim config/projection_rules.yaml

# 5. 테스트
python scripts/test_projection_guestimation.py
```

### Day 2: 통합 및 검증

**Morning (3시간)**:
```bash
# 6. Tier 1-2 연결
vim umis_rag/guestimation_v3/tier1.py  # RAG 검색 추가
vim umis_rag/guestimation_v3/tier2.py  # 학습 트리거 추가

# 7. End-to-End 테스트
python scripts/test_learning_e2e.py
```

**Afternoon (3시간)**:
```bash
# 8. User Contribution 구현
touch umis_rag/guestimation_v3/user_contribution.py

# 9. 통합 테스트
python scripts/test_user_contribution.py

# 10. 문서 업데이트
```

---

## 📝 테스트 시나리오

### 시나리오 1: 학습 파이프라인

```python
# scripts/test_learning_e2e.py

# 1. 첫 실행 (Tier 2)
result1 = guestimation.estimate("SaaS Churn Rate는?")
# → Tier 2 실행 (3초)
# → 결과: 6% ± 1%
# → 학습 완료! ✅

# 2. 재실행 (Tier 1)
result2 = guestimation.estimate("SaaS Churn Rate는?")
# → Tier 1 RAG 검색 (0.1초) ✨
# → 결과: 6% ± 1%
# → 30배 빠름!

# 3. 유사 질문
result3 = guestimation.estimate("B2B SaaS의 해지율은?")
# → Tier 1 매칭 (similarity=0.88)
# → 결과: 6% ± 1%
# → 빠름!
```

### 시나리오 2: 맥락 필터링

```python
# 1. B2B SaaS
result1 = guestimation.estimate(
    "Churn Rate는?",
    context=Context(domain="B2B_SaaS")
)
# → 6%

# 2. B2C Mobile
result2 = guestimation.estimate(
    "Churn Rate는?",
    context=Context(domain="B2C_Mobile_App")
)
# → Tier 1 불일치 (domain 다름)
# → Tier 2 재실행
# → 15-20% (다른 값!)
```

### 시나리오 3: 사용자 기여

```python
# 확정 사실 추가
contribution.add_definite_fact(
    question="우리 회사 직원 수는?",
    value=150,
    unit="명",
    source="HR 시스템"
)

# 즉시 사용 가능
result = guestimation.estimate("우리 회사 직원 수는?")
# → Tier 1 즉시 리턴
# → 150명 (confidence=1.0)
```

---

## 📊 성공 지표

### 성능

```yaml
첫 실행:
  - Tier 2: 3-8초 (동일)
  - 학습: +0.1초 (저장)

재실행:
  - Tier 1: <0.5초 ✨
  - 개선: 6-16배 빠름

커버리지:
  Week 1: 45% (20개 규칙)
  Month 1: 75% (120개)
  Year 1: 95% (2,000개)
```

### 정확도

```yaml
False Positive:
  - Tier 1 threshold: 0.85 (높음)
  - 목표: <1%
  
맥락 일치:
  - Domain 필터링: 필수
  - Region 필터링: 선택
  - 목표: >95%

재사용률:
  - 동일 질문: 100%
  - 유사 질문: 60-80%
```

---

## 🚨 주의사항

### 1. False Positive 방지

```yaml
원칙: 확실하지 않으면 Tier 2로!

구현:
  - similarity_threshold: 0.85 (높음)
  - domain 일치 필수
  - time 차이 3년 이상 → 경고
```

### 2. 메타데이터 완전성

```yaml
필수 필드:
  - domain (핵심!)
  - value, unit
  - confidence
  - time_period

선택 필드:
  - region
  - industry
```

### 3. Canonical 데이터 품질

```yaml
저장 조건:
  - confidence >= 0.80
  - evidence_count >= 2
  - 충돌 없음

검증:
  - boundary 위반 체크
  - 분포 타입 확인
```

---

## 📁 생성/수정 파일 목록

### 신규 생성 (3개)

```bash
umis_rag/guestimation_v3/learning_writer.py         # 핵심!
umis_rag/guestimation_v3/user_contribution.py       # 사용자 기여
scripts/test_learning_e2e.py                        # E2E 테스트
```

### 수정 (4개)

```bash
umis_rag/guestimation_v3/tier1.py                   # RAG 검색 추가
umis_rag/guestimation_v3/tier2.py                   # 학습 트리거
umis_rag/projection/rule_based_projector.py         # Projection
config/projection_rules.yaml                        # Rule 추가
```

---

## 🎯 완료 체크리스트

```yaml
Day 1:
  ✅ LearningWriter 구현
  ✅ Canonical 저장 테스트
  ✅ Projection Rule 추가
  ✅ Projected Index 생성 확인

Day 2:
  ✅ Tier 1 RAG 검색 연결
  ✅ Tier 2 학습 트리거
  ✅ E2E 테스트 (첫 실행 → 재실행)
  ✅ 맥락 필터링 검증

선택 (Day 3):
  ⏳ User Contribution
  ⏳ 시점 조정
  ⏳ 통합 테스트 확장
```

---

## 💡 Quick Start (바로 시작!)

### 1분만에 시작하기

```bash
# 1. 파일 생성
cd /Users/kangmin/umis_main_1103/umis
mkdir -p scripts/learning_tests

# 2. Learning Writer 골격
cat > umis_rag/guestimation_v3/learning_writer.py << 'EOF'
"""Tier 2 결과를 Canonical에 저장하는 학습 시스템"""

from typing import Optional
from .models import EstimationResult, Context, LearnedRule
import hashlib
from datetime import datetime

class LearningWriter:
    """학습된 규칙을 Canonical Index에 저장"""
    
    def __init__(self, canonical_collection):
        self.canonical = canonical_collection
    
    def save_learned_rule(
        self,
        question: str,
        result: EstimationResult,
        context: Context
    ) -> str:
        """
        학습된 규칙 저장
        
        Returns:
            rule_id: "RULE-DOMAIN-001" 형식
        """
        # TODO: 구현
        pass
    
    def should_learn(self, result: EstimationResult) -> bool:
        """학습 가치 판단"""
        if result.confidence < 0.80:
            return False
        if len(result.value_estimates) < 2:
            return False
        return True

EOF

# 3. 테스트 파일
cat > scripts/learning_tests/test_basic.py << 'EOF'
"""학습 시스템 기본 테스트"""

from umis_rag.guestimation_v3.learning_writer import LearningWriter

# TODO: 테스트 작성

print("✅ Learning Writer 골격 생성!")
EOF

# 4. 실행
python scripts/learning_tests/test_basic.py
```

---

**준비 완료!** 이제 바로 구현을 시작할 수 있습니다. 🚀

**다음 단계**: `learning_writer.py`의 `save_learned_rule()` 메서드 구현부터 시작하세요!

