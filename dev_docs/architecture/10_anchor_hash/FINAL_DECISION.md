# anchor_path + hash 최종 결정

**날짜:** 2025-11-02  
**결론:** 경로 기반 안정 참조 채택 (P0)  
**출처:** 전문가 피드백

---

## 🎯 문제

```yaml
현재:
  sections: {start: 0, end: 150}
  
문제:
  • 오프셋 방식
  • YAML 수정 → 오프셋 깨짐
  • 토크나이저 변경 → 위치 틀어짐
  • Projected 참조 깨짐!
```

### 실제 시나리오

```yaml
1. 현재 sections:
   explorer: {start: 100, end: 300}

2. YAML 맨 앞에 한 줄 추가:
   # UMIS business_model_patterns - Compatible...

3. 모든 오프셋 +1 이동:
   explorer: {start: 101, end: 301}

4. Projected 참조:
   여전히 {start: 100, end: 300} 찾음
   
5. 결과:
   잘못된 섹션 추출!
   → 재현성 깨짐! 🚨
```

---

## 💡 해결책

### anchor_path + content_hash

```yaml
구조:
  sections:
    - anchor_path: "subscription_model.trigger_observations"
      content_hash: "sha256:ab123456..."
      span_hint: {paragraphs: "12-18"}

작동:
  1. anchor_path로 위치 찾기:
     "subscription_model.trigger_observations"
     
  2. content_hash로 검증:
     실제 내용 hash와 비교
     → 일치하면 올바른 위치!
  
  3. span_hint는 선택:
     성능 최적화용

안정성:
  YAML 수정해도:
    → 경로 동일
    → hash 동일
    → 위치 정확! ✅
  
  토크나이저 변경해도:
    → 경로로 찾고
    → hash로 검증
    → 안전! ✅
```

---

## 🎯 가치

```yaml
재현성(A):
  • 토크나이저 변경 안전
  • YAML 수정 안전
  • 참조 불변성

장기 운영:
  • 몇 년 후에도 재현
  • 도구 변경 무관
  • 안정적 참조
```

---

## 🔧 구현

### config/schema_registry.yaml

```yaml
canonical_fields:
  sections:
    type: array
    items:
      anchor_path:
        type: string
        description: "YAML 경로 (예: subscription.trigger)"
        required: true
      
      content_hash:
        type: string
        pattern: "sha256:[a-f0-9]{64}"
        description: "내용 SHA-256 해시"
        required: true
      
      span_hint:
        type: object
        description: "성능 힌트 (선택)"
        properties:
          paragraphs: string
          tokens: int
```

### 변환 로직

```python
def extract_section(canonical_chunk, anchor_path):
    # 1. 경로로 위치 찾기
    section = yaml_path_query(canonical_chunk.content, anchor_path)
    
    # 2. hash 검증
    actual_hash = sha256(section)
    expected_hash = canonical_chunk.metadata['content_hash']
    
    if actual_hash != expected_hash:
        raise ValueError("Content changed!")
    
    return section
```

---

## 📋 우선순위

```
P0: 즉시 (Week 1)
구현: config/schema_registry.yaml
가치: 재현성(A) 핵심
```

---

**전문가 피드백:**
"토크나이저/분절 변경에도 깨지지 않는 레퍼런스 확보"

