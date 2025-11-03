# Fail-Safe 런타임 모드 검토

**제안:** Layer별 비활성화 + 모드 토글

---

## 🔍 문제 상황

### 시나리오 1: Knowledge Graph 다운

```yaml
상황:
  Neo4j 서버 다운 🚨
  
현재 구조:
  Explorer 워크플로우:
    1. Vector search ✅
    2. Graph 조합 검색 ❌ (실패!)
    
    → 전체 중단! 🚨

사용자:
  "시장 분석해줘"
  
  → 에러! (Graph 때문)
  → 아무것도 못 함! 🚨
```

### 시나리오 2: OpenAI API 장애

```yaml
상황:
  OpenAI API 타임아웃
  
현재:
  Vector search 시도
  → 임베딩 실패
  → 전체 실패! 🚨

대안:
  YAML만 사용?
  → 방법 없음!
```

### 시나리오 3: Memory DB 오류

```yaml
상황:
  QueryMemory 컬렉션 손상
  
현재:
  Guardian 순환 감지
  → Memory 접근 실패
  → Guardian 중단
  → 분석 멈춤? 🚨
```

**공통 문제:**
```yaml
한 Layer 실패 = 전체 실패
  
  → 취약함! 🚨
  → Fail-Safe 필요!
```

---

## 💡 제안 1: Circuit Breaker

```python
class LayerCircuitBreaker:
    """
    Layer별 Circuit Breaker
    """
    
    def __init__(self):
        self.failures = {
            'vector': 0,
            'graph': 0,
            'memory': 0,
            'meta': 0
        }
        
        self.threshold = 3  # 3회 실패 → OPEN
        self.state = {
            'vector': 'CLOSED',
            'graph': 'CLOSED',
            'memory': 'CLOSED',
            'meta': 'CLOSED'
        }
    
    def call_layer(self, layer, func, *args):
        """Layer 호출 with Circuit Breaker"""
        
        if self.state[layer] == 'OPEN':
            # Circuit OPEN → Skip!
            print(f"⚠️ {layer} 비활성화됨 (장애)")
            return None
        
        try:
            result = func(*args)
            
            # 성공 → 실패 카운트 리셋
            self.failures[layer] = 0
            
            return result
        
        except Exception as e:
            # 실패
            self.failures[layer] += 1
            
            if self.failures[layer] >= self.threshold:
                # Circuit OPEN!
                self.state[layer] = 'OPEN'
                print(f"🚨 {layer} Circuit OPEN! (3회 실패)")
            
            return None

# 사용
breaker = LayerCircuitBreaker()

# Graph 호출 (안전!)
combinations = breaker.call_layer(
    'graph',
    graph.find_combinations,
    pattern_id
)

if combinations is None:
    # Graph 실패 → 계속 진행!
    print("Graph 없이 계속...")
```

**효과:**
```yaml
Graph 다운:
  1회 실패 → 재시도
  2회 실패 → 재시도
  3회 실패 → Circuit OPEN
  
  → 이후 Graph skip!
  → Vector만으로 계속! ✅

복구:
  Graph 정상화
  → 다음 요청부터 자동 재시도
  → Circuit CLOSED
```

---

## 💡 제안 2: Mode Toggle (YAML)

```yaml
# config/runtime.yaml

mode: hybrid  # yaml_only / hybrid / rag_only

layer_enable:
  vector: true
  graph: false  # ← 수동 비활성화
  memory: false
  meta: false

fallback:
  vector_fail: "yaml_only"  # Vector 실패 → YAML로
  graph_fail: "skip"  # Graph 실패 → Skip
  memory_fail: "skip"
  meta_fail: "skip"
```

**사용:**
```python
config = load_yaml('config/runtime.yaml')

def explorer_analyze(triggers):
    # Vector search
    if config['layer_enable']['vector']:
        patterns = vector_search(triggers)
    else:
        patterns = yaml_fallback(triggers)  # ← Fallback!
    
    # Graph expansion
    if config['layer_enable']['graph']:
        combinations = graph_search(patterns)
    else:
        combinations = None  # ← Skip!
    
    # Memory tracking
    if config['layer_enable']['memory']:
        memory.record(query)
    # else: skip (계속 진행)
    
    return generate(patterns, combinations)
```

**장점:**
```yaml
✅ 제어:
   • YAML 수정으로 토글
   • 즉시 적용
   
✅ 실험:
   • "Graph 끄고 테스트"
   • config/runtime.yaml:
       graph: false
   
✅ 디버깅:
   • Layer 하나씩 활성화
   • 문제 격리

예시:
  Graph 버그 의심
  
  → config/runtime.yaml:
      graph: false
  
  → Graph 없이 실행
  → 정상 작동?
  → Graph 문제 확인! ✅
```

---

## 💡 제안 3: Graceful Degradation

```python
def explorer_analyze_robust(triggers):
    """
    Layer 실패해도 계속 진행
    """
    
    results = {}
    
    # Layer 1: Vector (필수)
    try:
        results['patterns'] = vector_search(triggers)
    except Exception as e:
        # 치명적! Fallback to YAML
        log.error(f"Vector failed: {e}")
        results['patterns'] = yaml_fallback(triggers)
        results['degraded'] = True
    
    # Layer 3: Graph (선택)
    try:
        if results.get('patterns'):
            results['combinations'] = graph_search(results['patterns'])
    except Exception as e:
        # 경고만, 계속 진행
        log.warning(f"Graph failed: {e}, continuing without combinations")
        results['combinations'] = None
    
    # Layer 4: Memory (선택)
    try:
        memory.record(triggers)
    except Exception as e:
        # 무시하고 계속
        log.warning(f"Memory failed: {e}, continuing...")
    
    # 가설 생성 (필수 정보만)
    return generate(
        results['patterns'],
        results.get('combinations'),  # 없을 수도
        degraded=results.get('degraded', False)
    )
```

**효과:**
```yaml
Vector 실패:
  → YAML Fallback
  → 품질 ↓ 하지만 작동! ✅

Graph 실패:
  → 조합 없이
  → 기본 패턴만
  → 작동! ✅

Memory 실패:
  → 기록 안 됨
  → 분석은 계속! ✅

→ 항상 작동! 🎯
```

---

## 🎯 최종 추천: 3가지 조합

### Tier 1: Circuit Breaker (자동)

```yaml
기능:
  • 3회 실패 → 자동 비활성화
  • 복구 시 자동 재활성화

장점:
  ✅ 자동 (사용자 몰라도)
  ✅ 안전 (무한 재시도 방지)

구현: 1일
```

### Tier 2: Mode Toggle (수동)

```yaml
기능:
  • config/runtime.yaml
  • Layer별 on/off
  • 모드 전환 (yaml_only/hybrid/rag_only)

장점:
  ✅ 제어 (사용자가 선택)
  ✅ 디버깅 (Layer 격리)

구현: 1일
```

### Tier 3: Graceful Degradation (기본)

```yaml
기능:
  • try-except로 보호
  • 실패해도 계속 진행
  • 경고만 출력

장점:
  ✅ 항상 작동
  ✅ 단순 (기본 에러 처리)

구현: 즉시 (코드 패턴)
```

---

## 📋 7번 최종 결정

**3-Tier Fail-Safe 채택!**

```yaml
우선순위:
  1. Graceful Degradation: P0 (즉시)
  2. Mode Toggle: P0 (1일)
  3. Circuit Breaker: P1 (1주)

구현:
  Phase 1: Graceful (try-except)
  Phase 2: Mode Toggle (config/runtime.yaml)
  Phase 3: Circuit Breaker (자동화)

효과:
  ✅ 항상 작동 (Degradation)
  ✅ 사용자 제어 (Toggle)
  ✅ 자동 보호 (Circuit Breaker)

→ 완벽한 Fail-Safe! 🛡️
```

---

**관련 문서:**
- 07_fail_safe/REVIEW.md
- 이 파일 (FINAL_DECISION.md)

**상태:** ✅ 검토 완료

