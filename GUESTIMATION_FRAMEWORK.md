# Guestimation Framework

**버전**: 1.0  
**작성일**: 2025-11-04  
**적용**: UMIS 전체 (모든 Agent)

---

## 📘 정의

**Guestimation**: 기초적인 지식과 논리적 추론만으로 짧은 시간 안에 대략적인 근사치를 추정하는 방법

## 🎯 핵심 철학

> "정확하지 않아도 괜찮다. 하지만 근거 없이 추정하면 안 된다."

### 언제 사용하나?

- ✅ 직접 데이터가 없을 때
- ✅ 정확한 값을 알 수 없을 때
- ✅ 짧은 시간 내 판단이 필요할 때

### 언제 사용하지 말아야 하나?

- ❌ 직접 데이터가 있을 때
- ❌ 정확한 값이 필수일 때
- ❌ 추정 불가능할 때 (억지로 추정하지 말것)

---

## 🔑 두 가지 핵심 요소

### 1. 기초적인 지식 (Foundation Knowledge)

#### 프로젝트 데이터
- 주어진 모든 숫자들
- 확정된 사실들
- 검증된 데이터

#### 보편적 경험 (Universal Experience)
- 업계 벤치마크
- 일반적인 경험율
- 유사 사례
- **RAG에 저장된 패턴/데이터**

> **AI의 경우**: RAG 데이터 = 보편적 경험

### 2. 논리적 추론 (Logical Reasoning)

#### 논리의 연결
- A → B → C 형태의 단계별 추론
- 각 단계의 근거 명확화

#### 합리적 가정
- "A와 B가 유사하다면..."
- "보수적으로 가정하면..."

#### 변수 제거
- 영향이 작은 변수 무시
- 상쇄되는 요소 제거

#### Boundary 설정
- 상한(Upper Bound): 아무리 높아도 이 이상은 불가능
- 하한(Lower Bound): 아무리 낮아도 이 이하는 불가능
- 현실적 범위: 실제로는 이 범위 내에 있을 것

---

## 📝 7단계 프로세스

### Step 1: 문제 명확화
```
- 추정해야 할 것: [무엇을 알고 싶은가?]
- 사용 목적: [왜 필요한가?]
- 필요 정확도: [±X% 이내면 충분한가?]
```

### Step 2: 기초 지식 수집
```
프로젝트 데이터:
  - 확정된 숫자 1: [값]
  - 확정된 숫자 2: [값]

보편적 경험 (RAG):
  - 유사 사례 1: [벤치마크]
  - 업계 평균: [경험율]
```

### Step 3: 추론 경로 설계
```
논리 흐름:
  1. A를 알고 있다
  2. A와 B의 관계는 [경험적으로] X이다
  3. 따라서 B ≈ A × X
```

### Step 4: 변수 단순화
```
무시 가능한 변수:
  - 변수 X: 영향 < 5% → 무시
```

### Step 5: Boundary 체크
```
상한: [절대 불가능한 최대값]
하한: [절대 불가능한 최소값]
현실 범위: [유사 사례들의 범위]
우리 추정: [Value] → 범위 내 ✓
```

### Step 6: 검증
```
Cross-check:
  - 다른 방법으로 계산하면?
  - 유사 사례와 비교하면?

Sensitivity:
  - 핵심 가정이 ±20% 변하면?
```

### Step 7: 신뢰도 평가
```
Confidence Level:
  - High: 유사 데이터 많음, 논리 견고
  - Medium: 일부 가정 필요, 논리 타당
  - Low: 많은 가정, 데이터 부족

Error Range:
  - High → ±10%
  - Medium → ±20%
  - Low → ±30~50%
```

---

## 💡 실전 예시

### 예시: 피아노 구독 서비스 전환율 추정

```yaml
Step 1 문제:
  추정 대상: 구독 전환율
  사용 목적: Bottom-Up SAM 계산
  필요 정확도: ±20%

Step 2 기초 지식:
  프로젝트 데이터:
    - 가격: 월 50,000원
    - 타겟: 피아노 학습자
  
  보편적 경험 (RAG):
    - 기타 구독: 12%
    - 음악 앱 구독: 18%

Step 3 추론:
  1. 피아노 ≈ 기타 (악기, 구독, 고가)
  2. 중간값: (12% + 18%) / 2 = 15%

Step 4 단순화:
  무시: 지역별 차이 (데이터 없음)

Step 5 Boundary:
  상한: 25% (프리미엄 서비스)
  하한: 5% (최소)
  현실: 10~20%
  추정: 15% ✓

Step 6 검증:
  Cross-check: 5만원 × 15% = 합리적

Step 7 신뢰도:
  Confidence: Medium
  Error Range: ±20%
```

---

## ✅ 품질 기준

### Good Guestimation
- ✅ 논리적 연결 명확
- ✅ 각 단계 근거 있음
- ✅ Boundary 체크 완료
- ✅ 대안 방법 고려함
- ✅ 검증 가능

### Bad Guestimation
- ❌ "그냥 20%로 가정"
- ❌ 근거 없는 숫자
- ❌ 논리 비약
- ❌ Boundary 무시
- ❌ 검증 불가능

---

## 🔧 UMIS에서 사용법

### Agent별 활용

#### Quantifier (Bill)
- Market Sizing 추정
- 전환율, AOV, Frequency 추정
- 시장 필터 비율

#### Explorer (Steve)
- 기회 크기 추정
- TAM/SAM 대략 계산
- 트렌드 영향도

#### Validator (Rachel)
- 데이터 신뢰도 평가
- Error Range 계산
- Confidence Level 판단

#### Observer (Albert)
- 시장 구조 비율
- Value Chain 분배
- 경쟁 강도

### RAG 활용
```python
# Quantifier가 RAG 검색
query = "음악 구독 서비스 전환율"
results = search_benchmarks(query)

# 추정 로직 구성
estimation = build_guestimation(
    base_data=results,
    logic_steps=[...],
    boundaries=[...]
)
```

---

## 📚 추가 자료

- **Tool Registry**: `config/tool_registry.yaml` → `tool:universal:guestimation`
- **System RAG**: Key로 검색 가능
- **예제**: `scripts/test_market_sizing_v7_2.py`

---

## 🎓 핵심 원칙

1. **투명성**: 모든 추정 과정을 문서화
2. **검증 가능성**: 다른 사람이 재현 가능
3. **합리성**: 누구나 동의할 수 있는 논리
4. **보수성**: 불확실하면 보수적으로
5. **경계 인식**: 한계를 명확히 인지

---

**작성**: UMIS Team  
**버전**: 1.0 (2025-11-04)  
**다음 업데이트**: RAG 자동화 추가 예정

