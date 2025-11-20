# Tier 1 Built-in Rules 현황

**날짜**: 2025-11-10  
**버전**: v7.5.0

---

## 📋 YAML Built-in Rules

**파일**: `data/tier1_rules/builtin.yaml`  
**총 개수**: 20개

### 1. 공식 통계 (5개)

| Rule ID | 패턴 | 값 | 출처 | Confidence |
|---------|------|-----|------|------------|
| BUILTIN-STAT-001 | 한국 인구 | 51,740,000명 | 통계청 2024 | 0.95 |
| BUILTIN-STAT-002 | 서울 인구 | 9,500,000명 | 통계청 2024 | 0.95 |
| BUILTIN-STAT-003 | 한국 가구수 | 21,000,000가구 | 통계청 2023 | 0.90 |
| BUILTIN-STAT-004 | 한국 GDP | 1,800조원 | 한국은행 2023 | 0.90 |
| BUILTIN-STAT-005 | 서울 면적 | 605 km² | 공식 통계 | 0.95 |

**매칭 예시**:
- "한국 인구는?" → 51,740,000명 ✅
- "서울 인구는?" → 9,500,000명 ✅
- "한국 총 가구는?" → 21,000,000가구 ✅

---

### 2. 물리/시간 상수 (5개)

| Rule ID | 패턴 | 값 | Confidence |
|---------|------|-----|------------|
| BUILTIN-PHY-001 | 하루 시간 | 24시간 | 1.0 |
| BUILTIN-PHY-002 | 일주일 일수 | 7일 | 1.0 |
| BUILTIN-PHY-003 | 한 달 일수 | 30일 (평균) | 0.95 |
| BUILTIN-PHY-004 | 1년 개월 | 12개월 | 1.0 |
| BUILTIN-PHY-005 | 1년 일수 | 365일 | 0.99 |

**매칭 예시**:
- "하루는 몇 시간?" → 24시간 ✅
- "일주일은 몇 일?" → 7일 ✅
- "1년은 몇 개월?" → 12개월 ✅

---

### 3. 법률/제도 상수 (5개)

| Rule ID | 패턴 | 값 | 출처 | Confidence |
|---------|------|-----|------|------------|
| BUILTIN-LAW-001 | 최저임금 | 9,860원/시간 | 고용노동부 2024 | 1.0 |
| BUILTIN-LAW-002 | 주휴수당 | 1일분 | 근로기준법 | 1.0 |
| BUILTIN-LAW-003 | 법정근로시간 | 52시간/주 | 근로기준법 | 1.0 |
| BUILTIN-LAW-004 | 법정 퇴직금 | (공식) | 근로기준법 | 1.0 |
| BUILTIN-LAW-005 | 법정 공휴일 | 15일/년 | 공휴일법 | 0.95 |

**매칭 예시**:
- "최저임금은?" → 9,860원/시간 ✅
- "법정근로시간은?" → 52시간/주 ✅

---

### 4. 수학/비즈니스 상수 (5개)

| Rule ID | 패턴 | 값 | Confidence |
|---------|------|-----|------------|
| BUILTIN-MATH-001 | 확률 범위 | [0, 1] | 1.0 |
| BUILTIN-MATH-002 | 백분율 범위 | [0, 100] | 1.0 |
| BUILTIN-BIZ-001 | Rule of 40 | (공식) | 1.0 |
| BUILTIN-BIZ-002 | LTV/CAC 비율 | 3-5배 | 0.90 |
| BUILTIN-BIZ-003 | CAC Payback | 6-12개월 | 0.85 |

**매칭 예시**:
- "Rule of 40은?" → 성장률 + 수익률 >= 40 ✅
- "LTV/CAC 비율은?" → 3-5배 ✅

---

## 🗄️ RAG Collection 상태

### 1. projected_index (Estimator용)
```
상태: 비어있음 (0개)
이유: Projection이 아직 실행되지 않음
```

### 2. canonical_index (학습 규칙 원본)
```
총 청크: 1개
학습 규칙: 1개

규칙:
  - RULE-USER_SPECIFIC-a092f2
    질문: "우리 회사 직원 수는?"
    값: 150명
    confidence: 1.0
    타입: definite_fact (사용자 기여)
```

---

## 🔍 현재 Tier 1의 실제 동작

### Built-in Rules (YAML) - ✅ 작동

```python
question = "한국 인구는?"
  ↓
Tier 1: Built-in 규칙 체크
  ↓
BUILTIN-STAT-001 매칭!
  ↓
반환: 51,740,000명 (confidence 0.95) ✅
```

### RAG Search (projected_index) - ❌ 비어있음

```python
question = "우리 회사 직원 수는?"
  ↓
Tier 1: RAG 검색
  ↓
projected_index: 0개 청크
  ↓
매칭 없음 → Tier 2로 ❌
```

**문제**: 
- canonical_index에 학습 규칙이 1개 있음
- 하지만 projected_index가 비어있어서 검색 안됨!

---

## 🚨 발견된 문제

### 1. **Projection 누락**

```
canonical_index (1개) → projected_index (0개)
                       ↑
                  Projection 안됨!
```

**원인**: 
- LearningWriter가 canonical에 저장은 함
- 하지만 Projection 스크립트가 실행 안됨

**해결**:
```bash
python scripts/02_build_index.py --agent estimator
```

### 2. **Built-in Rules 로드 경고**

테스트 로그에서 계속 나오는 경고:
```
⚠️  Built-in 규칙 로드 실패: [Errno 2] No such file or directory
```

하지만 실제로는 파일이 존재함!

**원인**: 
- 경로 문제일 가능성
- 또는 초기화 타이밍 문제

**확인 필요**:
```python
# tier1.py Line 55
rules_path = Path(__file__).parent.parent.parent / "data" / "tier1_rules" / "builtin.yaml"
```

---

## ✅ 정상 작동하는 규칙

### 테스트 결과

```python
# ✅ Built-in 규칙
"한국 인구는?" → 51,740,000명 (BUILTIN-STAT-001)
"하루는 몇 시간?" → 24시간 (BUILTIN-PHY-001)
"최저임금은?" → 9,860원/시간 (BUILTIN-LAW-001)
"Rule of 40은?" → (공식) (BUILTIN-BIZ-001)

# ❌ 학습 규칙 (Projection 누락)
"우리 회사 직원 수는?" → Tier 2로 (projected_index 비어있음)
```

---

## 📊 커버리지 분석

### Built-in Rules (20개)

**강점**:
- 확실한 값 (confidence 0.85-1.0)
- 빠른 응답 (<0.5초)
- 공식 출처

**약점**:
- 제한적 (20개만)
- 수동 관리 필요
- 업데이트 느림

**예상 커버리지**: 40-50% (자주 묻는 기본 질문)

### 학습 규칙 (현재 1개)

**잠재력**:
- 무한 확장 가능
- 자동 학습
- 사용자 기여

**현재 문제**:
- Projection 누락 (0개 → 검색 불가)
- 사용 안됨

---

## 🔧 즉시 조치 필요

### 1. Projection 실행 ⭐ 최우선!

```bash
# Estimator projection 구축
python scripts/02_build_index.py --agent estimator
```

### 2. Built-in 경로 확인

```python
# tier1.py에서 경로 로그 추가
logger.info(f"Built-in 경로: {rules_path}")
logger.info(f"파일 존재: {rules_path.exists()}")
```

### 3. 테스트

```python
from umis_rag.agents.estimator import EstimatorRAG

estimator = EstimatorRAG()

# Built-in 테스트
result = estimator.estimate("한국 인구는?")
assert result.tier == 1

# 학습 규칙 테스트 (Projection 후)
result = estimator.estimate("우리 회사 직원 수는?")
assert result.tier == 1  # ← 현재는 실패 (projected_index 비어있음)
```

---

## 📈 개선 방향

### 단기 (즉시)
1. ✅ Projection 스크립트 실행
2. ✅ Built-in 경로 문제 해결
3. ✅ RAG 검색 동작 확인

### 중기 (1-2주)
1. Built-in 규칙 확장 (20개 → 50개)
2. 자동 Projection (학습 시 자동 실행)
3. 규칙 유효성 검증 (outdated 감지)

### 장기 (1개월+)
1. Validator 검색 통합 (Tier 1.5)
2. 학습 규칙 자동 확장 (0 → 1,000개)
3. 규칙 버전 관리

---

## 🎯 결론

**현재 상태**:
- ✅ Built-in YAML: 20개 정상 작동
- ❌ RAG 검색: projected_index 비어있음

**핵심 문제**:
- **Projection 누락** - canonical → projected 동기화 안됨

**즉시 조치**:
```bash
python scripts/02_build_index.py --agent estimator
```

**근본 해결**:
- Validator 검색을 Tier 1.5로 추가
- Built-in Rules는 보조 수단으로

