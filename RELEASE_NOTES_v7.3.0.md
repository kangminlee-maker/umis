# UMIS v7.3.0 Release Notes
**"Guestimation v3.0 - Context-Aware Judgment"**

**Release Date**: 2025-11-07  
**Version**: v7.3.0  
**Status**: Design Complete + MVP Working

---

## 🎯 Release Highlights

### Guestimation v3.0 재설계 ⭐

**v2.1의 근본적 문제 해결**:
- ❌ Sequential Fallback (첫 성공만 사용)
- ❌ 판단 없음, 정보 종합 없음

**v3.0 혁신**:
- ✅ Context-Aware Judgment (맥락 기반 판단)
- ✅ 3-Tier 아키텍처 (Fast/Judgment/Fermi)
- ✅ 11개 Source (Physical/Soft/Value)
- ✅ 학습하는 시스템
- ✅ 사용자 기여 통합

---

## 🏗️ 아키텍처

### 3-Tier System

```
Tier 1: Fast Path (40-50%, <0.5초)
  - Built-in 규칙 20개
  - 학습된 규칙 RAG (0 → 2,000개 진화)
  - False Negative 허용 원칙

Tier 2: Judgment Path (45-55%, 3-8초)
  - 맥락 파악 (intent, domain, region, ...)
  - Source 수집 (11개 중 5-8개)
  - 증거 평가 (맥락 기반)
  - 종합 판단 (4가지 전략)
  - 학습 (Tier 1 편입)

Tier 3: Fermi Recursion (2-5%, 10-30초)
  - Fermi Model Search
  - 재귀 분해
```

### 11개 Source (3 Category)

**Physical Constraints** (절대 한계, 3개):
1. 시공간 법칙 - 광속 한계, 이동시간
2. 보존 법칙 - 부분<전체, 입력=출력
3. 수학 정의 - 확률[0,1], 백분율[0,100]

**Soft Constraints** (범위 제시, 3개):
4. 법률/규범 - 최저임금, 근로시간 (예외 포함)
5. 통계 패턴 - 7가지 분포 (정규, Power Law, ...)
6. 행동경제학 - Loss Aversion, Power Law (정성적)

**Value Sources** (값 결정, 5개):
7. 확정 데이터 - project_data
8. LLM 추정 - 시의성 조정
9. 웹 검색 - 최신 데이터
10. RAG 벤치마크 - Quantifier 100개 활용
11. 통계 패턴 값 - 분포에서 median/mean 추출

---

## ✨ 새로운 기능

### 1. 맥락 기반 판단

```yaml
같은 질문도 맥락에 따라 다른 답:

"음식점 월매출은?"
  
  맥락: intent=make_decision (창업 고려)
  → 전략: conservative
  → 답: 보수적 하한

  맥락: intent=understand_market (시장 분석)
  → 전략: weighted_average
  → 답: 평균값
```

### 2. 학습하는 시스템

```yaml
선순환:
  Tier 2/3 사용 → 결과 축적
  → 재사용 10회+ → Tier 1 편입
  → 다음엔 빠르게 (Tier 1)

진화:
  Week 1: 20개 규칙 → 45% 커버
  Month 1: 120개 → 75% 커버
  Year 1: 2,000개 (RAG) → 95% 커버

효과: 사용할수록 빨라짐!
```

### 3. Canonical-Projected RAG 통합

```yaml
Collection 증가 없음: 13개 유지

canonical_index:
  - 학습 규칙 추가 (chunk_type="learned_estimation_rule")

projected_index:
  - agent_view="guestimation" 추가
  - Filter로 격리 (성능 영향 없음)

청킹: 1질문 = 1청크 (200-300 tokens)
```

### 4. 사용자 기여

```yaml
3가지 유형:
  - 확정 사실: "우리 고객 10만명" → 즉시 사용
  - 업계 상식: "SaaS Churn 5%" → 검증 후 공유
  - 개인 경험: "음식점 2,000만원" → 참고용

검증:
  - 교차 검증 (여러 사용자)
  - 외부 검증 (Tier 2 재추정)
  - 논리 검증 (일관성)
```

---

## 💻 구현 상태

### 완성 (70% - MVP)

**Tier 1** (95%):
- ✅ Built-in 규칙 20개
- ✅ RAG 검색 인터페이스
- ✅ 테스트: 8/8 통과

**Tier 2** (90%):
- ✅ 맥락 파악
- ✅ Source 수집 (11개 골격)
- ✅ 판단 종합 (4가지 전략)
- ✅ End-to-End 작동

**Source** (70%):
- ✅ Physical 3개 (골격)
- ✅ Soft 3개 (샘플)
- ✅ Value 5개 (확정 데이터, 통계값, RAG)

### 남은 작업 (v7.3.1)

- 학습 시스템 (Tier 2 → Tier 1)
- Source 확장 (LLM API, 웹 검색)
- 사용자 기여 파이프라인

---

## 🔬 실제 동작 예시

### Example 1: SaaS Churn Rate

```
질문: "SaaS Churn Rate는?"

Tier 1:
  → Built-in 규칙 없음
  → Tier 2로

Tier 2:
  1. 맥락 파악:
     - intent: get_value
     - domain: B2B_SaaS (자동 인식!)
  
  2. Source 수집:
     - Physical: 백분율 [0, 100]
     - Soft: 정규분포 [5%, 7%]
     - Value: RAG 3개 (Quantifier 벤치마크)
  
  3. 판단:
     - 전략: range
     - 결과: 6% ± 1%
     - 신뢰도: 60%
  
  4. 시간: 2.15초

성공! ✅
```

### Example 2: 음식점 월매출

```
질문: "음식점 월매출은?"

Tier 2:
  1. 맥락: domain=Food_Service
  
  2. Source:
     - Physical: 음수 불가
     - Soft: Power Law 분포 [1,000-4,500만원]
     - Value: median 2,000만원 (자동 추출)
  
  3. 판단: 2,000만원
  
  4. 시간: 0.00초

성공! ✅
```

---

## 📁 새 파일

### 설계 문서 (13개, 15,000줄)

- `GUESTIMATION_V3_DESIGN.yaml` (3,474줄) ⭐
- `SOURCE_MECE_VALIDATION.yaml` (1,015줄)
- `GUESTIMATION_V3_FINAL_DESIGN.yaml` (1,089줄)
- 기타 10개 분석 문서

### 코드 (10개, 2,180줄)

- `umis_rag/guestimation_v3/models.py` (457줄)
- `tier1.py` (320줄), `tier2.py` (247줄)
- `sources/` (823줄) - 11개 Source
- `judgment.py` (240줄)
- `source_collector.py` (232줄)

### 데이터

- `data/tier1_rules/builtin.yaml` (20개 규칙)

### 테스트

- `scripts/test_tier1_guestimation.py`
- `scripts/test_tier2_guestimation.py`
- `scripts/test_source_collector.py`

---

## 🔑 핵심 원칙

```yaml
1. False Negative > False Positive
   → Tier 1은 확실한 것만

2. 규칙의 본질
   → 100% or 0% (중간값 없음)

3. 설계 방식
   → YAML + 자연어 (Python 탈피)

4. 학습하는 시스템
   → 사용할수록 빨라짐

5. 아키텍처 일관성
   → Canonical-Projected 활용

6. MECE 검증
   → 95% (실용적 충분)

7. 통계 분포 고려
   → Power Law는 median!
```

---

## 🎓 주요 학습

### 설계 방식 전환

```yaml
Before: Python 코드 중심
  - Python 문법에 갇힘
  - if-else, list, dict
  - LLM 활용 제한

After: YAML + 자연어
  - 논리 구조 집중
  - 구현 독립적
  - LLM 자유롭게 고려
```

### 규칙과 LLM의 본질

```yaml
규칙:
  - 매칭: confidence 100%
  - 불일치: confidence 0%
  - 중간값 없음!

LLM:
  - 항상 confidence 0-100%
  - 확률적 판단

혼동 금지!
```

---

## 📊 통계

### 작업량

- **설계 문서**: 15,000줄 (13개)
- **코드**: 2,180줄 (10개 파일)
- **테스트**: 3개 스크립트
- **작업 시간**: 6시간

### 완성도

- 설계: 100% ✅
- 구현: 70% (MVP)
- 테스트: 60%
- 문서화: 100% ✅

---

## ⚠️ Breaking Changes

### Deprecated

- `umis_rag.utils.multilayer_guestimation.MultiLayerGuestimation` (v2.1)
  → v7.3.1에서 제거 예정

### 새 API

```python
# v3.0 (권장)
from umis_rag.guestimation_v3 import estimate

result = estimate("SaaS Churn Rate는?")
print(result.value, result.confidence)
```

---

## 🚀 다음 버전

### v7.3.1 (예정)

**Phase 5: 학습 시스템**
- Tier 2 결과 → Canonical 저장
- Projected 자동 생성
- 재사용 감지
- 사용자 기여 파이프라인

**예상**: 1-2일

---

## 📚 참조

- 설계: `GUESTIMATION_V3_DESIGN.yaml`
- 세션 요약: `SESSION_SUMMARY_20251107_GUESTIMATION_V3_DESIGN.md`
- MVP 상태: `GUESTIMATION_V3_MVP_STATUS.md`
- 아키텍처: `UMIS_ARCHITECTURE_BLUEPRINT.md`

---

**Released by**: UMIS Development Team  
**Date**: 2025-11-07

