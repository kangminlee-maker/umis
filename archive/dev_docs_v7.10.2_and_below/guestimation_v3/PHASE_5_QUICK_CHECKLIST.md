# Phase 5 구현 빠른 체크리스트

**목표**: 학습 시스템 구현 (1-2일)  
**핵심**: Tier 2 결과 → Tier 1로 자동 편입

---

## 🎯 3줄 요약

```yaml
1. Tier 2가 답을 찾으면 → Canonical에 저장
2. Canonical → Projected (guestimation view) 자동 생성
3. 다음엔 Tier 1 RAG가 0.5초 안에 리턴! ✨
```

---

## ✅ 구현 체크리스트

### Step 1: Learning Writer (3-4시간)

```bash
[ ] 파일 생성: umis_rag/guestimation_v3/learning_writer.py
[ ] LearningWriter 클래스 구현
[ ] save_learned_rule() 메서드
[ ] LearnedRule → Canonical 변환
[ ] 테스트 작성 및 실행
```

**핵심 코드**:
```python
class LearningWriter:
    def save_learned_rule(self, question, result, context):
        # EstimationResult → Canonical 저장
        # chunk_type: "learned_rule"
        # sections: [agent_view: "guestimation"]
```

### Step 2: Projection Generator (2-3시간)

```bash
[ ] 수정: umis_rag/projection/rule_based_projector.py
[ ] learned_rule 타입 처리 추가
[ ] 수정: config/projection_rules.yaml
[ ] chunk_type_rules.learned_rule 추가
[ ] 테스트: Projected Index 생성 확인
```

**핵심 Rule**:
```yaml
chunk_type_rules:
  learned_rule:
    target_agents: ["guestimation"]
    strategy: "direct_projection"
    ttl: "persistent"
```

### Step 3: Tier 1 통합 (1-2시간)

```bash
[ ] 수정: umis_rag/guestimation_v3/tier1.py
[ ] search_learned_rule() 호출 추가
[ ] similarity_threshold: 0.85 설정
[ ] 맥락 필터링 (domain, region)
[ ] 테스트: RAG 검색 작동 확인
```

**핵심 로직**:
```python
# Built-in 실패 시
learned_result = self.rag_searcher.search_learned_rule(
    question, context, min_similarity=0.85
)
if learned_result:
    return result  # ✨ 0.5초 안에 리턴!
```

### Step 4: Tier 2 연결 (1시간)

```bash
[ ] 수정: umis_rag/guestimation_v3/tier2.py
[ ] LearningWriter 인스턴스 연결
[ ] 판단 후 학습 트리거 추가
[ ] 테스트: 학습 완료 메시지 확인
```

**핵심 로직**:
```python
if self._should_learn(result):
    rule_id = self.learning_writer.save_learned_rule(...)
    print(f"✅ 학습 완료: {rule_id}")
```

### Step 5: E2E 테스트 (1시간)

```bash
[ ] 테스트 작성: scripts/test_learning_e2e.py
[ ] 시나리오 1: 첫 실행(느림) → 재실행(빠름)
[ ] 시나리오 2: 맥락 필터링 검증
[ ] 성능 확인: 6-16배 개선
```

---

## 📊 성공 지표

```yaml
✅ 첫 실행: Tier 2 (3-8초)
✅ 재실행: Tier 1 (<0.5초)
✅ 개선: 6-16배 빠름
✅ False Positive: <1%
✅ 맥락 일치: >95%
```

---

## 🚀 바로 시작하기

```bash
# 1. 작업 디렉토리
cd /Users/kangmin/umis_main_1103/umis

# 2. Learning Writer 생성
touch umis_rag/guestimation_v3/learning_writer.py

# 3. 상세 가이드 열기
open PHASE_5_IMPLEMENTATION_GUIDE.md

# 4. 구현 시작! 🎯
```

---

## 💡 핵심 포인트

```yaml
1. False Positive 방지:
   - similarity_threshold: 0.85 (높게!)
   - domain 일치 필수

2. 메타데이터 완전성:
   - domain, value, unit, confidence 필수
   - time_period 권장

3. 학습 조건:
   - confidence >= 0.80
   - evidence_count >= 2

4. 데이터 형식:
   - chunk_type: "learned_rule"
   - agent_view: "guestimation"
   - 1질문 = 1청크
```

---

**예상 시간**: 1-2일  
**우선순위**: P1 (핵심!)  
**상세 가이드**: `PHASE_5_IMPLEMENTATION_GUIDE.md`

**시작!** 🚀

