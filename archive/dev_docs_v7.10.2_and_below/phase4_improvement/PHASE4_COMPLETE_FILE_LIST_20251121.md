# Phase 4 변경 영향 파일 - 최종 완전 목록

**작성일**: 2025-11-21  
**목적**: Phase 4 Few-shot 개선 시 변경할 모든 파일의 완전한 목록  
**총 파일**: 18개

---

## 📊 카테고리별 요약

| 카테고리 | 파일 수 | 변경 필요 | 테스트 필요 | 우선순위 |
|---------|--------|---------|-----------|---------|
| **핵심 코드** | 4 | ✅ 필수 | ✅ 필수 | ⭐⭐⭐⭐⭐ |
| **핵심 시스템 문서** | 3 | ✅ 필수 | ✅ 권장 | ⭐⭐⭐⭐⭐ |
| **설정 파일** | 1 | ⚠️ 선택 | ✅ 권장 | ⭐⭐ |
| **테스트 스크립트** | 4 | ⚠️ 선택 | ✅ 필수 | ⭐⭐⭐ |
| **참고 문서** | 6 | ⚠️ 선택 | - | ⭐ |
| **합계** | 18 | - | - | - |

---

## 📋 완전한 파일 목록

### Priority 1: 필수 변경 (7개)

#### A. 핵심 코드 (4개)

1. **`umis_rag/agents/estimator/phase4_fermi.py`** (2,512줄)
   - 영향도: ⭐⭐⭐⭐⭐
   - 변경: Few-shot 추가, 계산 검증 메서드
   - 위치: `_build_llm_prompt()` (라인 1240)
   - 신규: `_verify_calculation_connectivity()` 메서드

2. **`umis_rag/agents/estimator/models.py`**
   - 영향도: ⭐⭐⭐⭐
   - 변경: Phase4Config 옵션 추가
   - 추가: `use_fewshot`, `verify_calculation`

3. **`umis_rag/agents/estimator/estimator.py`**
   - 영향도: ⭐⭐⭐
   - 확인: Config 전달 방식
   - 테스트: Phase 4 호출 정상 작동

4. **`umis_rag/agents/estimator/__init__.py`**
   - 영향도: ⭐
   - 상태: ✅ 이미 완료 (변경 불필요)

#### B. 핵심 시스템 문서 (3개)

5. **`umis.yaml`** (6,139줄)
   - 영향도: ⭐⭐⭐⭐⭐
   - 역할: 자연어 전체 시스템 문서 (Cursor Rules)
   - 변경: Estimator 섹션 Phase 4 개선 사항 반영
   - 추가: Few-shot 사용, Reasoning 필수성, 계산 연결성 품질 기준

6. **`umis_core.yaml`** (157줄)
   - 영향도: ⭐⭐⭐⭐
   - 역할: 압축 INDEX (System RAG용)
   - 변경: Phase 4 섹션 간결 업데이트
   - 추가: v7.7.1 개선 사항 요약

7. **`docs/architecture/UMIS_ARCHITECTURE_BLUEPRINT.md`** (1,400줄)
   - 영향도: ⭐⭐⭐⭐
   - 역할: 개발 contributor 전체 설계 가이드
   - 변경: Version Info, Estimator 섹션, Version History
   - 라인: 14-34, 1130-1284, 806-821

---

### Priority 2: 테스트 필수 (4개)

8. **`scripts/test_fermi_final_fewshot.py`** (741줄)
   - 영향도: ⭐⭐⭐
   - 역할: Few-shot 효과 검증
   - 상태: ✅ 이미 수정 완료 (reasoning 출력)
   - 실행: Phase 4 변경 후 재실행

9. **`scripts/test_fermi_improved_calculation.py`**
   - 영향도: ⭐⭐
   - 역할: 계산 연결성 테스트
   - 실행: Phase 4 변경 후 재실행

10. **`scripts/test_fermi_comprehensive_ai_baseline.py`** (793줄)
    - 영향도: ⭐⭐
    - 역할: AI 기준선 설정
    - 실행: Phase 4 변경 후 재실행

11. **`scripts/test_gpt5_phase_0_4_advanced.py`**
    - 영향도: ⭐⭐⭐
    - 역할: GPT-5 Phase 0-4 전체 테스트
    - 실행: Phase 4 성능 확인

---

### Priority 3: 선택적 (7개)

#### C. 설정 파일 (1개)

12. **`config/fermi_model_search.yaml`** (1,500줄 추정)
    - 영향도: ⭐⭐
    - 역할: Fermi 모델 검색 설정
    - 변경: 선택적 (코드에 구현하면 불필요)

#### D. 참고 문서 (6개)

13. **`docs/PHASE4_IMPROVEMENT_PLAN_20251121.md`** (591줄)
    - 상태: ✅ 이미 작성 완료
    
14. **`docs/PHASE4_IMPLEMENTATION_GUIDE_20251121.md`** (276줄)
    - 상태: ✅ 이미 작성 완료

15. **`docs/FERMI_REASONING_FIX_20251121.md`**
    - 상태: ✅ 이미 작성 완료

16. **`CHANGELOG.md`**
    - 변경: v7.7.1 추가 권장

17. **`docs/FERMI_COMPREHENSIVE_REPORT_20251121_165419.md`** (391줄)
    - 상태: ✅ 이미 수정 완료

18. **`docs/FERMI_FINAL_SUMMARY_20251121.md`**
    - 상태: ✅ 이미 작성 완료

---

## 🎯 작업 순서 및 예상 시간

### Step 1: 핵심 코드 수정 (1-1.5시간)

```
1. phase4_fermi.py (45분)
   └─ Few-shot 추가, 계산 검증 메서드

2. models.py (10분)
   └─ Phase4Config 옵션 추가

3. estimator.py (5분)
   └─ Config 전달 확인
```

### Step 2: 핵심 시스템 문서 업데이트 (30-45분)

```
4. umis.yaml (20분)
   └─ Estimator 섹션 업데이트 (Phase 4 개선)

5. umis_core.yaml (10분)
   └─ Phase 4 섹션 간결 업데이트

6. UMIS_ARCHITECTURE_BLUEPRINT.md (15분)
   └─ Version Info, Estimator 섹션, Version History
```

### Step 3: 테스트 및 검증 (30분)

```
7. test_fermi_final_fewshot.py 실행
8. test_gpt5_phase_0_4_advanced.py 실행
9. 계산 연결성 점수 확인 (40/50 이상 목표)
```

### Step 4: 정리 (20분)

```
10. CHANGELOG.md 업데이트
11. 문서 최종 확인
12. Git commit 준비
```

**총 예상 시간**: 2.5-3시간

---

## ✅ 최소 필수 작업

### 반드시 변경해야 할 파일 (7개)

**핵심 코드 (4개)**:
1. ✅ phase4_fermi.py
2. ✅ models.py
3. ✅ estimator.py
4. ✅ __init__.py (완료)

**핵심 시스템 문서 (3개)**:
5. ✅ umis.yaml
6. ✅ umis_core.yaml
7. ✅ UMIS_ARCHITECTURE_BLUEPRINT.md

### 반드시 실행해야 할 테스트 (2개)

8. ✅ test_fermi_final_fewshot.py
9. ✅ test_gpt5_phase_0_4_advanced.py

---

## 📊 파일별 상세 정보

| 파일 | 라인 수 | 영향도 | 변경 | 테스트 | 예상 시간 |
|------|--------|--------|------|--------|----------|
| phase4_fermi.py | 2,512 | ⭐⭐⭐⭐⭐ | ✅ | ✅ | 45분 |
| models.py | ? | ⭐⭐⭐⭐ | ✅ | ✅ | 10분 |
| estimator.py | ? | ⭐⭐⭐ | ⚠️ | ✅ | 5분 |
| umis.yaml | 6,139 | ⭐⭐⭐⭐⭐ | ✅ | - | 20분 |
| umis_core.yaml | 157 | ⭐⭐⭐⭐ | ✅ | - | 10분 |
| BLUEPRINT.md | 1,400 | ⭐⭐⭐⭐ | ✅ | - | 15분 |
| 테스트 × 4 | - | ⭐⭐⭐ | - | ✅ | 30분 |

**합계**: 7개 파일 + 4개 테스트 = 약 2.5시간

---

## 🚀 구현 체크리스트

### Phase 1: 핵심 코드 (1-1.5시간)

- [ ] `phase4_fermi.py`: Few-shot 예시 추가
- [ ] `phase4_fermi.py`: `_verify_calculation_connectivity()` 메서드
- [ ] `models.py`: Phase4Config 옵션 추가
- [ ] `estimator.py`: Config 전달 확인

### Phase 2: 핵심 문서 (30-45분)

- [ ] `umis.yaml`: Estimator Phase 4 섹션 업데이트
- [ ] `umis_core.yaml`: Phase 4 간결 업데이트
- [ ] `UMIS_ARCHITECTURE_BLUEPRINT.md`: Version Info 업데이트

### Phase 3: 테스트 (30분)

- [ ] `test_fermi_final_fewshot.py` 실행
- [ ] `test_gpt5_phase_0_4_advanced.py` 실행
- [ ] 계산 연결성 40/50 이상 확인
- [ ] Reasoning 80% 이상 확인

### Phase 4: 정리 (20분)

- [ ] CHANGELOG.md 업데이트 (v7.7.1)
- [ ] 문서 최종 확인
- [ ] 완료 보고서 작성

---

## ⚠️ 핵심 주의사항

### 1. 문서 일관성

**3개 핵심 문서는 반드시 동기화**:

```
umis.yaml (자연어)
  ↕️ 동기화
umis_core.yaml (INDEX)
  ↕️ 동기화
UMIS_ARCHITECTURE_BLUEPRINT.md (설계)
```

**예시**:
- umis.yaml: 상세 설명 + 예시 코드
- umis_core.yaml: 핵심 요약 (87% 절약)
- BLUEPRINT.md: 구조 다이어그램 + 기술 설명

### 2. System RAG 연동

**umis_core.yaml 변경 시**:
```bash
# System RAG 재구축 필요
python3 scripts/build_system_knowledge.py
```

**이유**: umis_core.yaml → System RAG → AI 참조

### 3. 버전 관리

**v7.7.1 태깅 필요**:
- VERSION.txt 업데이트
- CHANGELOG.md 추가
- 3개 문서에 v7.7.1 명시

---

## 📁 파일 위치 참조

```
umis_main_1103/umis/
├── 📄 umis.yaml (6,139줄) ⭐⭐⭐⭐⭐
├── 📄 umis_core.yaml (157줄) ⭐⭐⭐⭐
├── 📄 CHANGELOG.md ⚠️
├── 📄 VERSION.txt ⚠️
│
├── umis_rag/agents/estimator/
│   ├── 📄 phase4_fermi.py (2,512줄) ⭐⭐⭐⭐⭐
│   ├── 📄 models.py ⭐⭐⭐⭐
│   ├── 📄 estimator.py ⭐⭐⭐
│   └── 📄 __init__.py ✅ 완료
│
├── config/
│   └── 📄 fermi_model_search.yaml (1,500줄) ⚠️
│
├── scripts/
│   ├── 📄 test_fermi_final_fewshot.py (741줄) ✅ 수정완료
│   ├── 📄 test_fermi_improved_calculation.py
│   ├── 📄 test_fermi_comprehensive_ai_baseline.py (793줄)
│   └── 📄 test_gpt5_phase_0_4_advanced.py
│
└── docs/
    ├── architecture/
    │   └── 📄 UMIS_ARCHITECTURE_BLUEPRINT.md (1,400줄) ⭐⭐⭐⭐
    ├── 📄 PHASE4_IMPROVEMENT_PLAN_20251121.md ✅
    ├── 📄 PHASE4_IMPLEMENTATION_GUIDE_20251121.md ✅
    ├── 📄 FERMI_REASONING_FIX_20251121.md ✅
    ├── 📄 FERMI_COMPREHENSIVE_REPORT_*.md ✅
    └── 📄 FERMI_FINAL_SUMMARY_*.md ✅
```

---

## 🎯 작업 순서 (우선순위별)

### Priority 1: 핵심 코드 (필수, 1-1.5시간)

```
Step 1.1: phase4_fermi.py (45분)
  ├─ Few-shot 예시 작성 (택시 수 예시)
  ├─ _build_llm_prompt() 수정 (라인 1240)
  ├─ _verify_calculation_connectivity() 추가
  └─ _parse_and_verify() 추가

Step 1.2: models.py (10분)
  └─ Phase4Config 옵션 3개 추가

Step 1.3: estimator.py (5분)
  └─ Config 전달 확인 및 테스트
```

### Priority 2: 핵심 문서 (필수, 30-45분)

```
Step 2.1: umis.yaml (20분)
  ├─ Estimator 섹션 찾기 (grep으로)
  ├─ Phase 4 개선 사항 추가
  └─ Few-shot, Reasoning, 계산 검증 명시

Step 2.2: umis_core.yaml (10분)
  ├─ Estimator Phase 4 섹션 찾기
  └─ v7.7.1 개선 사항 요약 추가

Step 2.3: UMIS_ARCHITECTURE_BLUEPRINT.md (15분)
  ├─ Version Info 업데이트 (라인 14-34)
  ├─ Estimator 섹션 업데이트 (라인 1130-1284)
  └─ Version History 추가 (라인 806-821)
```

### Priority 3: 테스트 및 검증 (필수, 30분)

```
Step 3.1: 테스트 실행
  ├─ test_fermi_final_fewshot.py
  └─ test_gpt5_phase_0_4_advanced.py

Step 3.2: 결과 확인
  ├─ 계산 연결성: 40/50 이상
  └─ Reasoning: 80% 이상
```

### Priority 4: 정리 (선택, 20분)

```
Step 4.1: 버전 관리
  ├─ VERSION.txt → v7.7.1
  └─ CHANGELOG.md 추가

Step 4.2: 문서 정리
  └─ 최종 확인
```

---

## 💡 각 문서별 업데이트 가이드

### umis.yaml 업데이트

**검색 키워드**: `estimator:`, `phase_4:`, `phase4:`

**추가 섹션**:
```yaml
estimator:
  phase_4:
    v7_7_1_improvements:  # ⭐ 신규
      few_shot:
        enabled: true
        example: "서울 택시 수 (145% 향상)"
        effect: "계산 연결성 18/40 → 50/50"
      
      calculation_verification:
        enabled: true
        auto_check: "분해 값 → 최종값 일치 확인"
        threshold: "10% 오차 이내"
        score: "0-25점"
      
      reasoning:
        mandatory: true
        requirement: "모든 가정에 합리적 근거"
        examples:
          - "경활 비율 0.62 → OECD 수준 + 한국 통계"
          - "자영업 0.2 → 한국 높은 편, 5명 중 1명"
    
    quality_standards:  # ⭐ 업데이트
      calculation_connectivity: "50/50 (만점)"
      reasoning_coverage: "80% 이상"
      accuracy: "10% 오차 이내"
      total_score: "85/100 (gpt-5.1)"
```

### umis_core.yaml 업데이트

**검색 키워드**: `estimator:`, `phase4:`

**추가 섹션**:
```yaml
estimator:
  phase4:
    v7_7_1:  # ⭐ 신규
      few_shot: "택시 예시 (145% 향상)"
      verification: "자동 검증"
      reasoning: "근거 필수"
      quality: "95/100"
```

### UMIS_ARCHITECTURE_BLUEPRINT.md 업데이트

**위치 1**: Version Info (라인 14-34)
```markdown
| **Estimator Phase 4** | v7.7.1 (Few-shot + Verification) ⭐ NEW! |
```

**위치 2**: Version History (라인 806-821)
```markdown
- **v7.7.1 (2025-11-21)**: ⭐ Phase 4 Few-shot 개선
  - Few-shot 예시 추가 (계산 연결성 145% 향상)
  - 자동 계산 검증 (분해 → 최종값 일치)
  - Reasoning 필수화 (모든 가정에 근거)
  - 테스트 결과: 85/100 (gpt-5.1)
```

**위치 3**: Estimator 섹션 (라인 1130-1284)
```markdown
**v7.7.1 Few-shot 개선**:
- Few-shot 예시: 계산 연결성 145% 향상 (18/40 → 50/50)
- 자동 검증: 분해 값과 최종값 일치 확인
- Reasoning: 모든 가정에 합리적 근거 필수
```

---

## 🎉 최종 체크리스트

### 필수 작업 (9개)

- [ ] 1. phase4_fermi.py 수정
- [ ] 2. models.py 수정
- [ ] 3. estimator.py 확인
- [ ] 4. umis.yaml 업데이트
- [ ] 5. umis_core.yaml 업데이트
- [ ] 6. UMIS_ARCHITECTURE_BLUEPRINT.md 업데이트
- [ ] 7. test_fermi_final_fewshot.py 실행
- [ ] 8. test_gpt5_phase_0_4_advanced.py 실행
- [ ] 9. 결과 검증

### 선택 작업 (3개)

- [ ] 10. CHANGELOG.md 업데이트
- [ ] 11. VERSION.txt → v7.7.1
- [ ] 12. System RAG 재구축 (umis_core 변경 시)

---

**완전한 파일 목록 확정**: 18개 파일 (필수 9개, 선택 9개)

**다음 단계**: Priority 1 (핵심 코드) 수정부터 시작! 🚀

