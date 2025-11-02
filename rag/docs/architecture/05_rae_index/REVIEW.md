# RAE 인덱스 (평가 메모리) 검토

**제안:** 과거 Guardian 평가를 별도 인덱스로 재사용

---

## 🔍 문제 상황

### 현재 (매번 LLM 호출)

```yaml
Guardian 평가:
  
  Explorer 가설 1:
    "피아노 구독 서비스"
    
    Guardian:
      LLM 호출 ($0.01)
      → Grade A
      → 시간: 2초

  Explorer 가설 2:
    "바이올린 구독 서비스"
    (거의 동일한 구조!)
    
    Guardian:
      다시 LLM 호출 ($0.01) ⚠️
      → Grade A (같은 결과)
      → 시간: 2초

비효율:
  • 거의 같은 가설
  • LLM 2번 호출
  • 비용 2배
  • 시간 2배
  
  → 낭비! ❌
```

---

## 💡 제안: RAE 인덱스

### Retrieval-Augmented Evaluation

```yaml
평가 메모리 Index:

청크 1:
  content: "피아노 구독 서비스 가설..."
  
  metadata:
    hypothesis_type: "subscription_service"
    pattern_applied: "subscription_model"
    
    guardian_evaluation:
      grade: "A"
      approved: true
      reasoning: "Observer 근거 명확, Quantifier 계산 정확..."
      timestamp: "2025-11-02"

청크 2:
  content: "바이올린 구독 서비스 가설..."
  ...
```

### 사용 (재사용!)

```python
def guardian_evaluate(new_hypothesis):
    # 1. 유사한 과거 평가 검색
    similar_past = rae_index.search(
        new_hypothesis.content,
        k=3
    )
    
    # 2. 유사도 확인
    if similar_past[0].similarity > 0.95:
        # 거의 동일!
        print(f"✅ 과거 평가 재사용: {similar_past[0].metadata['grade']}")
        
        return {
            'grade': similar_past[0].metadata['grade'],
            'reused': True,
            'similar_to': similar_past[0].content[:50],
            'reasoning': similar_past[0].metadata['reasoning']
        }
    
    # 3. 유사하지 않으면 LLM 호출
    evaluation = llm.invoke(f"평가: {new_hypothesis}")
    
    # 4. 평가 저장 (다음을 위해)
    rae_index.add({
        'content': new_hypothesis.content,
        'evaluation': evaluation
    })
    
    return evaluation
```

**효과:**
```yaml
피아노 → 바이올린:
  유사도: 0.97
  → 평가 재사용!
  
  절감:
    비용: $0.01 (50%)
    시간: 2초 (50%)

10개 유사 가설:
  재사용: 9개
  
  절감:
    비용: $0.09 (90%)
    시간: 18초 (90%)
```

---

## 📊 비용/시간 절감 분석

### 시나리오: 100개 프로젝트

```yaml
가설 패턴:
  • Subscription 변형: 30개 (유사)
  • Platform 변형: 20개 (유사)
  • D2C 변형: 15개 (유사)
  • 완전 새로운: 35개

RAE 없이 (매번 LLM):
  100개 × $0.01 = $1.00
  100개 × 2초 = 200초 (3.3분)

RAE 있으면 (재사용):
  새로운: 35개 × $0.01 = $0.35
  재사용: 65개 × $0 = $0
  
  총: $0.35 (65% 절감!)
  시간: 70초 (65% 절감!)

연간 (1,000개 프로젝트):
  절감: $6.50
  시간: 33분
```

---

## 🎯 유의미한가?

### 비용 절감

```yaml
연간: $6.50
  
  vs 개발 비용:
    RAE 인덱스 구현: 2일
    개발자 시급 $50 → $800
  
  회수 기간:
    $800 / $6.50 = 123년 ❌
  
  판단:
    비용 관점: 오버엔지니어링! 🚨
```

### 시간 절감

```yaml
연간: 33분

  vs 가치:
    Guardian 평가 대기 시간 단축
    사용자 경험 개선
  
  판단:
    33분/년은 미미
    → 오버엔지니어링! 🚨
```

### 품질 측면

```yaml
문제:
  "과거 평가 재사용 = 품질?"

위험:
  피아노 구독: Grade A
  바이올린 구독: 재사용 → Grade A
  
  하지만:
    • 시장 다를 수 있음
    • 경쟁 구조 다를 수 있음
    • 재평가 필요할 수도
  
  → 과거 답 재활용 위험! ⚠️

올바른 접근:
  매번 평가 (신중)
  vs
  재사용 (빠름, 위험)
  
  판단:
    Guardian은 품질 관리!
    → 재사용보다 정확성! ✅
```

---

## 💡 대안: Caching (간단한 캐싱)

### 정확히 같은 경우만

```python
# 간단한 캐싱 (복잡한 인덱스 불필요)

evaluation_cache = {}

def guardian_evaluate_cached(hypothesis):
    # 해시 생성
    key = hash(hypothesis.content)
    
    # 캐시 확인
    if key in evaluation_cache:
        print("✅ 캐시 재사용 (정확히 동일)")
        return evaluation_cache[key]
    
    # LLM 평가
    evaluation = llm.invoke(hypothesis)
    
    # 캐시 저장
    evaluation_cache[key] = evaluation
    
    return evaluation
```

**효과:**
```yaml
정확히 같은 가설:
  • 피아노 구독 (2번 평가)
  → 2번째는 캐시 ✅

거의 비슷한 가설:
  • 피아노 vs 바이올린
  → 각각 평가 (안전!)

절감:
  중복 평가만 (실제로는 드뭄)
  
구현:
  dict 하나 (5줄)
  
  vs RAE 인덱스:
    Vector DB, 검색 로직, ...
    → 100배 단순! ✨
```

---

## 🎯 최종 판단

**RAE 인덱스 제외!**

```yaml
이유:
  1. 비용: 연 $6.50 (미미)
     회수: 123년 ❌
  
  2. 시간: 연 33분 (미미)
     가치 낮음
  
  3. 품질: 재사용 위험
     Guardian은 신중해야 함
  
  4. 복잡도: 인덱스 구축 vs 캐싱
     100배 차이

대안:
  간단한 캐싱 (5줄)
  → 정확히 같은 것만
  → 안전! ✅

결론:
  오버엔지니어링!
  → 제외! ❌
```

**당신의 직관이 맞았습니다!**

"유의미한가?" → No!

---

## 📋 5번 최종 결정

**제외 (Not Needed)**

```yaml
채택:
  ❌ RAE 인덱스

대안:
  ✅ 간단한 캐싱 (정확히 동일만)

이유:
  • 비용 절감: 미미
  • 시간 절감: 미미
  • 복잡도: 높음
  • 품질 위험: 있음

우선순위: ❌ 제외

→ 오버엔지니어링 방지! ✨
```

---

**관련 문서:**
- 05_rae_index/REVIEW.md
- 이 파일 (최종 결정)

**다음:** 6번 (Overlay 레이어)

