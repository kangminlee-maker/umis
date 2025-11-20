# Deprecated Features Archive

v7.7.0 기준으로 deprecated 된 기능들의 문서 보관소입니다.

## 디렉토리 구조

### domain_reasoner/
**Deprecated in:** v7.5.0  
**대체 기능:** Estimator Phase 3 (Guestimation)

Domain Reasoner는 v7.5.0에서 Estimator의 Phase 3으로 통합되었습니다.

**문서:**
- `DOMAIN_REASONER_ANALYSIS.md`
- `DOMAIN_REASONER_REMOVAL_V7.5.0.md`
- `domain_reasoner_analysis_20251104.md`

**이유:**
- Estimator Phase 3이 더 강력한 추정 능력 제공
- 중복 기능 제거로 시스템 단순화
- Phase 기반 아키텍처로 통합

---

### tier_system/
**Deprecated in:** v7.7.0  
**대체 기능:** Phase 0-4 시스템

3-Tier 시스템(Tier 1/2/3)은 v7.7.0에서 5-Phase 시스템(Phase 0-4)으로 완전히 대체되었습니다.

**문서:**
- `TIER1_COMPLETE_ROADMAP.md`
- `TIER2_TO_TIER1_UPGRADE_PLAN.md`
- `TIER2_UPGRADE_ACTION_PLAN.md`
- `TIER2_UPGRADE_EXECUTIVE_SUMMARY.md`
- `TIER3_COMPLETE.md`
- `TIER3_FINAL_SUMMARY.md`
- `TIER3_FIX_CORE.md`
- `TIER3_PROBLEM_ANALYSIS.md`
- `TIER3_VARIABLE_CONVERGENCE_DESIGN.md` (v7.5.0)
- `TIER3_OVERENGINEERING_CHECK.md` (v7.5.0)
- `TIER3_IMPLEMENTATION_PLAN.md` (v7.5.0)
- `TIER3_DESIGN_VERIFICATION.md` (v7.5.0)
- `TIER3_IMPLEMENTATION_COMPLETE.md` (v7.5.0)
- `TIER3_FINAL_REPORT.md` (v7.5.0)
- `TIER3_ACCURACY_IMPROVEMENT.md` (v7.6.2)
- `TIER1_BUILTIN_RULES_STATUS.md` (v7.6.2)
- `TIER2_TEST_RESULTS.md` (v7.6.2)
- `V7_6_2_TIER3_IMPROVEMENT.md` (v7.6.2)

**용어 변경:**
```
Tier 1 → Phase 1 (Direct RAG)
Tier 2 → Phase 2 (Validator Search)
Tier 3 → Phase 3 (Guestimation)
(없음) → Phase 0 (Literal Data)
(없음) → Phase 4 (Fermi Decomposition)
```

**이유:**
- 용어 명확화 (Tier는 계층, Phase는 단계)
- Phase 0/4 추가로 100% 커버리지 달성
- Fermi 내부 Step 1-4와 명확한 구분

---

### built_in_rules/
**Deprecated in:** v7.6.0  
**대체 기능:** Learned Rules (학습 기반)

Built-in Rules는 v7.6.0에서 제거되고 학습 기반 규칙으로 완전히 대체되었습니다.

**이유:**
- Built-in Rules는 답변 불일치 발생 (100% vs 0.06)
- 학습 규칙은 사용할수록 진화 (0 → 2,000개)
- Validator 우선 검색으로 정확도 100% 달성

---

### v7.4_and_earlier/
**Deprecated in:** v7.5.0+  
**대체 기능:** 최신 버전 기능

v7.4 이하 버전에서 사용되던 인터페이스 및 기능 문서들입니다.

**문서:**
- `DEPRECATED_INTERFACES_V7.5.0.md`

---

## 참고 문서

### 현재 시스템 (v7.7.0)

**Estimator 5-Phase Architecture:**
```
Phase 0: Literal (프로젝트 데이터, <0.1초)
Phase 1: Direct RAG (학습 규칙, <0.5초)
Phase 2: Validator (확정 데이터, <1초, 85% 처리!)
Phase 3: Guestimation (11개 Source, 3-8초)
Phase 4: Fermi Decomposition (Step 1-4, 10-30초)
```

**커버리지:**
- Phase 0: 10%
- Phase 1: 5%
- Phase 2: 85% ⭐
- Phase 3: 2%
- Phase 4: 3%
- **총: 100%**

**정확도:**
- Validator: 100% (0% 오차)
- Phase 4: 75% (25% 오차, 3배 개선)
- E2E Success: 95% (19/20)

### 마이그레이션 가이드

#### Tier → Phase 변환

| 구 용어 (Tier) | 신 용어 (Phase) | 설명 |
|---------------|----------------|------|
| Tier 1 | Phase 1 | Direct RAG (학습 규칙) |
| Tier 2 | Phase 2 | Validator Search |
| Tier 3 | Phase 3 | Guestimation |
| (없음) | Phase 0 | Literal (프로젝트 데이터) |
| (없음) | Phase 4 | Fermi Decomposition |

#### Built-in Rules → Learned Rules

```python
# 구 방식 (v7.5.x)
built_in_rules = {
    "B2B_SaaS_Churn_Rate": 0.06
}

# 신 방식 (v7.6.0+)
# 학습 규칙은 자동 축적 (0 → 2,000개)
# Validator 우선 검색 (85% 처리)
result = estimator.estimate("B2B SaaS Churn Rate?")
# → Phase 2 (Validator) → 정확도 100%
```

#### Domain Reasoner → Phase 3

```python
# 구 방식 (v7.4.x)
domain_reasoner.reason("시장 크기는?")

# 신 방식 (v7.5.0+)
estimator.estimate("시장 크기는?")
# → Phase 3 (Guestimation) 자동 선택
```

---

## 히스토리

### v7.7.0 (2025-11-10)
- 3-Tier 완전 Deprecated
- 5-Phase 시스템 확립
- 용어 명확화 (Phase + Step)

### v7.6.0 (2025-11-xx)
- Built-in Rules 제거
- Validator 우선 검색 (85% 처리)
- 학습 규칙 시스템 강화

### v7.5.0 (2025-11-10)
- Domain Reasoner 제거
- Estimator/Quantifier 역할 분리
- Tier → Phase 용어 변경 시작

---

**참고:**
- 현재 시스템: `docs/architecture/UMIS_ARCHITECTURE_BLUEPRINT.md`
- 개발 문서: `dev_docs/`
- 변경 이력: `CHANGELOG.md`

