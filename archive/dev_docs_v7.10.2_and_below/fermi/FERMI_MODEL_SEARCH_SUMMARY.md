# Fermi Model Search 설계 요약

**파일**: `config/fermi_model_search.yaml` (1,040줄)  
**작성일**: 2025-11-05  
**상태**: ✅ 설계 완료

---

## 🎯 핵심 개념

**"논리의 퍼즐 맞추기"**

```
가용한 숫자 (Bottom-up) ⟷ 개념 분해 (Top-down)를
반복하며 "채울 수 있는 모형" 찾기
```

---

## 📐 주요 설계 결정

### 1️⃣ 변수 개수: 2-6개

```yaml
criterion_3_complexity:
  scoring:
    2_vars: 1.0   # 최선
    3_vars: 0.9
    4_vars: 0.7
    5_vars: 0.5
    6_vars: 0.3   # 허용
    7_plus: 0.0   # 금지 ❌
```

**이유**:
- 적을수록 좋음 (Occam's Razor)
- 하지만 6개까지 허용 (복잡한 모형 가능)
- 7개 이상은 관리 불가

---

### 2️⃣ 재귀 깊이: 최대 4단계

```yaml
max_depth: 4

depth_preference:
  depth_0: 1.0   # 재귀 없음 (최선!)
  depth_1: 0.8   # 1단계 (좋음)
  depth_2: 0.6   # 2단계 (괜찮음)
  depth_3: 0.4   # 3단계 (선호 낮음)
  depth_4: 0.2   # 4단계 (최대)
```

**재귀 예시**:
```
Depth 0: "LTV는?"
  ↓ ARPU unknown
Depth 1: "ARPU는?" (재귀!)
  ↓ 기본료 unknown
Depth 2: "기본료는?" (재귀!)
  ↓ Layer 7 발견 → 재귀 중단
```

**종료 조건**:
- depth >= 4
- 단일 값 발견 (Multi-Layer)
- 순환 의존성 (A → B → A)

---

### 3️⃣ 다양한 비즈니스 지표

```yaml
business_metrics_examples:
  - market_sizing    # 시장 규모
  - ltv              # 고객 생애 가치
  - cac              # 고객 획득 비용
  - conversion_rate  # 전환율
  - churn_rate       # 해지율
  - growth_rate      # 성장률
  - unit_economics   # LTV/CAC
  - arpu_detailed    # ARPU 상세 분해
```

**각 지표마다 여러 모형 제시**:
```yaml
ltv:
  models:
    - "LTV = ARPU × (1 / Churn)"
    - "LTV = ARPU × Average Lifetime"
    - "LTV = Σ(ARPU × (1-Churn)^n)"
```

---

## 🔄 4단계 프로세스

### Phase 1: 초기 스캔 (Bottom-up)
```
"내가 알고 있는 숫자" 파악
→ available_data, unknown_data
```

### Phase 2: 모형 생성 (Top-down)
```
LLM이 3-5개 후보 모형 생성
→ 각 모형은 다른 분해 방식
```

### Phase 3: 실행 가능성 체크 (퍼즐!)
```
각 모형의 변수 채울 수 있는가?
→ Multi-Layer로 시도
→ 재귀 호출 (변수도 Guestimation 대상)
→ 채울 수 있는 모형 선택
```

### Phase 4: 재조립
```
선택된 모형 + 변수 값들
→ 계산
→ Backtracking (재귀에서 복귀)
```

---

## 📊 모형 선택 기준 (4개)

| 기준 | 가중치 | 선호 |
|------|--------|------|
| Unknown 개수 | 50% | 적을수록 |
| Confidence | 30% | 높을수록 |
| 복잡도 (변수 개수) | 20% | 2-3개 (6개까지 허용) |
| Depth (재귀) | 10% | depth 0 (6개 허용) |

**총점**: 1.1 (depth 보너스 포함)

---

## 💡 Fermi 본질 반영 확인

### ✅ 1. 모형 만들기

```yaml
Phase 2: LLM이 여러 모형 생성
Model 1: 시장 = A × B × C
Model 2: 시장 = A × B × C × D
Model 3: 시장 = X × Y
```

### ✅ 2. Bottom-up ⟷ Top-down

```yaml
Phase 1: 가용 데이터 (Bottom-up)
  → [A, B, C] 있음

Phase 2: 모형 생성 (Top-down)
  → 모형 = f(A, B, C, D)

Phase 3: 퍼즐 맞추기
  → D를 구할 수 있나? (Bottom-up 검증)
  → 가능! → 선택
```

### ✅ 3. 재귀 (변수도 Guestimation)

```yaml
"ARPU는?" (unknown)
  ↓
"ARPU = 기본 + 추가" (모형 생성)
  ↓
"기본료는?" (재귀 호출!)
"추가료는?" (재귀 호출!)
  ↓
재조립
```

### ✅ 4. 다양한 지표

```yaml
- 시장 규모 (TAM, SAM, SOM)
- LTV, CAC, LTV/CAC
- Churn, Conversion, Growth
- ARPU (상세 분해 가능)
```

---

## 🎓 다음 단계

YAML 설계 확정되면:
1. Python 클래스 구현
2. LLM 프롬프트 구현
3. 재귀 로직 구현
4. Quantifier 통합

**예상 시간**: 2-3시간

---

**설계 문서**: `config/fermi_model_search.yaml` (1,040줄)  
**상태**: ✅ 검토 대기

이 설계가 Fermi 본질(모형 만들기, 퍼즐 맞추기)을 제대로 반영했나요?
