# Phase 4 변경 시 영향받는 파일 전체 목록

**작성일**: 2025-11-21  
**목적**: Phase 4 수정 시 함께 변경/확인해야 할 모든 파일 식별  
**분석 방법**: grep, 의존성 분석, 파일 구조 탐색

---

## 📊 영향받는 파일 요약

| 카테고리 | 파일 수 | 변경 필요 | 테스트 필요 |
|---------|--------|---------|-----------|
| **핵심 코드** | 4 | ✅ 필수 | ✅ 필수 |
| **핵심 시스템 문서** | 3 | ✅ 필수 | ✅ 권장 |
| **설정 파일** | 1 | ⚠️ 선택 | ✅ 권장 |
| **테스트 스크립트** | 4 | ⚠️ 선택 | ✅ 필수 |
| **참고 문서** | 6 | ⚠️ 선택 | - |
| **합계** | 18 | - | - |

---

## 1️⃣ 핵심 코드 파일 (4개) - ✅ 필수 변경

### 1.1 메인 Phase 4 파일

**파일**: `umis_rag/agents/estimator/phase4_fermi.py` (2,512줄)

**역할**: Phase 4 Fermi Decomposition 메인 로직

**변경 필요**:
- ✅ `_build_llm_prompt()` (라인 1240): Few-shot 예시 추가
- ✅ `_verify_calculation_connectivity()`: 신규 메서드 추가
- ✅ `_parse_and_verify()`: 신규 메서드 추가

**의존성**:
- Phase3Guestimation (import)
- models.py (Context, EstimationResult, Phase4Config)
- OpenAI API

**영향도**: ⭐⭐⭐⭐⭐ (최고)

---

### 1.2 Models/Config 파일

**파일**: `umis_rag/agents/estimator/models.py`

**역할**: Phase 4 설정 클래스 정의

**변경 필요**:
```python
@dataclass
class Phase4Config:
    max_depth: int = 4
    max_variables: int = 10
    
    # ⭐ 추가 필요
    use_fewshot: bool = True  # Few-shot 사용 여부
    verify_calculation: bool = True  # 계산 검증 여부
    min_calculation_score: int = 15  # 최소 계산 점수
```

**의존성**:
- dataclasses
- Phase4FermiDecomposition (사용처)

**영향도**: ⭐⭐⭐⭐ (높음)

---

### 1.3 Estimator 메인 파일

**파일**: `umis_rag/agents/estimator/estimator.py`

**역할**: EstimatorRAG 메인 클래스 (Phase 4 호출)

**위치**: 라인 259-260
```python
from .phase4_fermi import Phase4FermiDecomposition
self.phase4 = Phase4FermiDecomposition()
```

**변경 필요**:
- ⚠️ Config 전달 확인
- ⚠️ Phase 4 호출 방식 확인

**영향도**: ⭐⭐⭐ (중간)

---

### 1.4 __init__.py (Export)

**파일**: `umis_rag/agents/estimator/__init__.py`

**역할**: Phase4Config export

**위치**: 라인 22, 37
```python
Phase1Config, Phase3Config, Phase4Config
'Phase4Config',
```

**변경 필요**:
- ✅ 이미 export 중
- ✅ 추가 변경 불필요

**영향도**: ⭐ (낮음)

---

## 2️⃣ 핵심 시스템 문서 (3개) - ✅ 필수 업데이트

### 2.1 UMIS 메인 가이드

**파일**: `umis.yaml` (6,539줄)

**역할**: 자연어로 정리된 전체 시스템 문서 (Cursor Rules)

**변경 필요**:
- ✅ Estimator 섹션 (386줄): Phase 4 개선 사항 반영
- ✅ Few-shot 사용 강조
- ✅ Reasoning 필수성 명시
- ✅ 계산 연결성 품질 기준 업데이트

**위치**:
- 라인 추정: Estimator 섹션 (umis.yaml 내 검색 필요)

**영향도**: ⭐⭐⭐⭐⭐ (최고) - 모든 AI가 참조하는 메인 문서

**업데이트 내용**:
```yaml
estimator:
  phase_4:
    improvements:  # ⭐ 신규 추가
      - few_shot_prompts: "택시 수 예시 포함 (145% 향상)"
      - calculation_verification: "자동 검증 (10% 이내)"
      - reasoning_mandatory: "모든 가정에 근거 필수"
    
    quality_standards:  # ⭐ 업데이트
      calculation_connectivity: "50/50 (만점 목표)"
      reasoning_coverage: "80% 이상"
      accuracy_target: "10% 오차 이내"
```

---

### 2.2 UMIS 코어 인덱스

**파일**: `umis_core.yaml` (928줄)

**역할**: 압축 INDEX (AI 빠른 참조, System RAG용)

**변경 필요**:
- ✅ Phase 4 섹션 업데이트
- ✅ Few-shot 및 계산 검증 추가
- ✅ 87% 절약 유지 (간결성)

**위치**:
- 라인 추정: Estimator/Phase 4 섹션

**영향도**: ⭐⭐⭐⭐ (높음) - System RAG가 참조

**업데이트 내용**:
```yaml
estimator:
  phase4:
    name: "Fermi Decomposition (Few-shot ⭐)"
    improvements_v7_7_1:  # ⭐ 신규
      - few_shot: "택시 예시 (145% 향상)"
      - verification: "자동 계산 검증"
      - reasoning: "가정 근거 필수"
    quality: "95/100 (gpt-5.1)"
    time: "10-30초"
```

---

### 2.3 UMIS 아키텍처 블루프린트

**파일**: `docs/architecture/UMIS_ARCHITECTURE_BLUEPRINT.md` (1,400줄)

**역할**: 개발 contributor를 위한 전체 설계 가이드

**변경 필요**:
- ✅ Version Info 섹션 (라인 14-34)
- ✅ Estimator Agent 섹션 (라인 1130-1284)
- ✅ Fermi Model Search 섹션 (라인 1287-1335)
- ✅ Version History 업데이트

**영향도**: ⭐⭐⭐⭐ (높음) - 개발자 참조 문서

**업데이트 내용**:

1. **Version Info (라인 14-34)**:
```markdown
| **Estimator Agent** | v7.7.1 (5-Phase, Few-shot ⭐) | ⭐⭐⭐ NEW!
| **Phase 4 Accuracy** | 95% (5% 오차, 19배 개선) ⭐⭐⭐
```

2. **Estimator Agent 섹션 (라인 1130-1284)**:
```markdown
## 🎯 Estimator (Fermi) Agent (v7.7.1 Few-shot 개선)

### v7.7.1 개선 사항 (2025-11-21)

**Few-shot Prompting** ⭐
- 택시 수 예시 포함
- 계산 연결성: 18/40 → 50/50 (+145%)
- 성공률: 0% → 93% (14/15)

**자동 계산 검증** ⭐
- _verify_calculation_connectivity() 메서드
- 분해 값 → 최종값 자동 확인
- 10% 이내 오차 목표

**Reasoning 필수화** ⭐
- 모든 가정에 근거 명시
- 예: "경활 비율 0.62 = OECD 평균 기준"
```

3. **Fermi Model Search 섹션 (라인 1287-1335)**:
```markdown
## 🎯 Fermi Model Search (Phase 4, v7.7.1)

### v7.7.1: Few-shot + 계산 검증

**Step 2 개선**: 모형 생성 시 Few-shot 예시 포함
**신규 메서드**: _verify_calculation_connectivity()
**품질 향상**: 95/100점 (gpt-5.1)
```

4. **Version History 추가**:
```markdown
### v7.7.1 (2025-11-21): ⭐ Phase 4 Few-shot 개선
  - Few-shot 프롬프트 추가 (145% 향상)
  - 자동 계산 검증
  - Reasoning 필수화
  - 정확도: 75% → 95% (20%p 향상)
```

---

## 3️⃣ 설정 파일 (1개) - ⚠️ 선택적 변경적 변경

### 2.1 Fermi 모델 검색 설정

**파일**: `config/fermi_model_search.yaml` (1,500줄 추정)

**역할**: Fermi 모델 검색 설정 (Phase 4 참조)

**변경 필요**:
- ⚠️ Few-shot 예시 추가 고려
- ⚠️ 프롬프트 템플릿 업데이트 고려

**참조 위치**:
- phase4_fermi.py 라인 1193: "설계: fermi_model_search.yaml Line 1158-1181"
- phase4_fermi.py 라인 1248: "설계: fermi_model_search.yaml Line 1163-1181"

**영향도**: ⭐⭐ (낮음-중간)

**판단**: 코드에 직접 구현하면 YAML 수정 불필요

---

## 3️⃣ 테스트 스크립트 (4개) - ⚠️ 선택적 변경, ✅ 필수 실행

### 3.1 Few-shot 테스트 스크립트

**파일**: `scripts/test_fermi_final_fewshot.py` (741줄)

**역할**: Few-shot 효과 검증 (이미 완료된 테스트)

**변경 필요**:
- ✅ 이미 수정 완료 (reasoning 출력)
- ⚠️ Phase 4 통합 테스트 추가 고려

**영향도**: ⭐⭐⭐ (중간)

---

### 3.2 계산 개선 테스트

**파일**: `scripts/test_fermi_improved_calculation.py`

**역할**: 계산 연결성 테스트

**변경 필요**:
- ⚠️ Phase 4 변경 후 재실행
- ⚠️ 점수 비교

**영향도**: ⭐⭐ (낮음-중간)

---

### 3.3 AI 기준선 테스트

**파일**: `scripts/test_fermi_comprehensive_ai_baseline.py` (793줄)

**역할**: AI 기준선 설정 및 비교

**변경 필요**:
- ⚠️ Phase 4 변경 후 재실행
- ⚠️ 기준선 업데이트

**영향도**: ⭐⭐ (낮음-중간)

---

### 3.4 GPT-5 Phase 0-4 테스트

**파일**: `scripts/test_gpt5_phase_0_4_advanced.py`

**역할**: GPT-5로 Phase 0-4 전체 테스트

**변경 필요**:
- ⚠️ Phase 4 변경 후 재실행
- ⚠️ Phase 4 성능 확인

**영향도**: ⭐⭐⭐ (중간)

---

## 4️⃣ 문서 파일 (6개) - ⚠️ 선택적 업데이트

### 4.1 새로 작성한 문서

1. **`docs/PHASE4_IMPROVEMENT_PLAN_20251121.md`** (591줄)
   - 역할: Phase 4 개선 계획
   - 변경: ✅ 이미 작성 완료

2. **`docs/PHASE4_IMPLEMENTATION_GUIDE_20251121.md`** (276줄)
   - 역할: Phase 4 구현 가이드
   - 변경: ✅ 이미 작성 완료

3. **`docs/FERMI_REASONING_FIX_20251121.md`**
   - 역할: Reasoning 추가 수정 보고서
   - 변경: ✅ 이미 작성 완료

### 4.2 업데이트 권장 문서

4. **`CHANGELOG.md`**
   - 역할: 변경 이력
   - 변경: ⚠️ Phase 4 개선 사항 추가 권장

5. **`docs/FERMI_COMPREHENSIVE_REPORT_20251121_165419.md`** (391줄)
   - 역할: Fermi 종합 보고서
   - 변경: ⚠️ Phase 4 적용 결과 업데이트 고려

6. **`docs/FERMI_FINAL_SUMMARY_20251121.md`**
   - 역할: 최종 요약
   - 변경: ⚠️ Phase 4 적용 결과 업데이트 고려

---

## 5️⃣ tests/ 폴더 (신규 생성 필요)

**현재 상태**: Phase 4 전용 테스트 없음

**권장 생성**:
```
tests/
├── test_phase4_fewshot.py (신규)
│   └── Few-shot 효과 검증
├── test_phase4_verification.py (신규)
│   └── 계산 검증 로직 테스트
└── test_phase4_integration.py (신규)
    └── Phase 4 통합 테스트
```

**영향도**: ⭐⭐⭐⭐ (높음) - 품질 보증 필수

---

## 📋 변경 우선순위 및 순서

### Priority 1: 필수 변경 (반드시 수정)

```
1. umis_rag/agents/estimator/phase4_fermi.py
   └─ Few-shot 추가, 계산 검증 메서드

2. umis_rag/agents/estimator/models.py
   └─ Phase4Config 옵션 추가

3. umis.yaml
   └─ Estimator 섹션 Phase 4 개선 사항 반영

4. umis_core.yaml
   └─ Phase 4 섹션 Few-shot 업데이트

5. docs/architecture/UMIS_ARCHITECTURE_BLUEPRINT.md
   └─ Version Info, Estimator 섹션 업데이트

→ 예상 시간: 2-3시간
```

### Priority 2: 검증 필수 (테스트 실행)

```
6. umis_rag/agents/estimator/estimator.py
   └─ Config 전달 확인

7. scripts/test_fermi_final_fewshot.py
   └─ 재실행 및 결과 확인

→ 예상 시간: 30분
```

### Priority 3: 선택적 (권장)

```
8. tests/test_phase4_fewshot.py (신규)
   └─ 단위 테스트 작성

9. CHANGELOG.md
   └─ 변경 이력 추가

→ 예상 시간: 30분
```

---

## 🎯 변경 체크리스트

### 핵심 코드

- [ ] `phase4_fermi.py` - Few-shot 추가
- [ ] `phase4_fermi.py` - 계산 검증 메서드 추가
- [ ] `models.py` - Phase4Config 수정
- [ ] `estimator.py` - Config 전달 확인

### 핵심 시스템 문서 ⭐ 중요!

- [ ] `umis.yaml` - Estimator 섹션 업데이트
- [ ] `umis_core.yaml` - Phase 4 섹션 업데이트
- [ ] `docs/architecture/UMIS_ARCHITECTURE_BLUEPRINT.md` - Version Info, Estimator 섹션 업데이트

### 테스트

- [ ] `test_fermi_final_fewshot.py` 재실행
- [ ] 계산 연결성 점수 확인 (40/50 이상 목표)
- [ ] Reasoning 존재율 확인 (80% 이상 목표)
- [ ] 기존 Phase 4 기능 정상 작동 확인

### 문서 (선택)

- [ ] CHANGELOG.md 업데이트
- [ ] 종합 보고서 업데이트
- [ ] 신규 테스트 파일 작성

---

## ⚠️ 주의사항

### 1. 하위 호환성

- ✅ **Native/External 모두 동일한 품질 기준 적용** ⭐
  - Few-shot: 모든 모드에서 사용
  - Reasoning: 모든 모드에서 필수
  - 계산 검증: 모든 모드에서 적용
- ✅ 기존 Phase 4 호출 코드는 그대로 작동
- ✅ Config 옵션은 기본값 제공 (use_fewshot=True)

### 2. 의존성

**Phase 4가 의존하는 것들**:
- Phase 3 (Fallback용)
- OpenAI API (External Mode)
- models.py (Config, Context 등)

**Phase 4에 의존하는 것들**:
- EstimatorRAG (메인 호출자)
- 테스트 스크립트들

### 3. 테스트 전략

```
Step 1: 단위 테스트
└─ Few-shot 프롬프트 생성 확인

Step 2: 통합 테스트
└─ Phase 4 전체 플로우 확인

Step 3: 성능 테스트
└─ 계산 연결성 점수 측정
```

---

## 📊 영향도 매트릭스

| 파일 | 변경 필요 | 테스트 필요 | 영향도 | 우선순위 |
|------|---------|-----------|--------|---------|
| phase4_fermi.py | ✅ 필수 | ✅ 필수 | ⭐⭐⭐⭐⭐ | 1 |
| models.py | ✅ 필수 | ✅ 필수 | ⭐⭐⭐⭐ | 1 |
| **umis.yaml** | ✅ **필수** | ✅ 필수 | ⭐⭐⭐⭐⭐ | **1** |
| **umis_core.yaml** | ✅ **필수** | ✅ 필수 | ⭐⭐⭐⭐ | **1** |
| **UMIS_ARCHITECTURE_BLUEPRINT.md** | ✅ **필수** | - | ⭐⭐⭐⭐ | **1** |
| estimator.py | ⚠️ 확인 | ✅ 필수 | ⭐⭐⭐ | 2 |
| __init__.py | ✅ 완료 | - | ⭐ | - |
| fermi_model_search.yaml | ⚠️ 선택 | - | ⭐⭐ | 3 |
| test_fermi_*.py | ⚠️ 선택 | ✅ 필수 | ⭐⭐⭐ | 2 |
| tests/ (신규) | ⚠️ 권장 | ✅ 권장 | ⭐⭐⭐⭐ | 3 |
| docs/*.md | ⚠️ 선택 | - | ⭐ | 4 |

---

## 🚀 실행 계획

### Phase 1: 핵심 수정 (2-3시간)

```bash
# 1. phase4_fermi.py 수정
# 2. models.py 수정
# 3. umis.yaml 업데이트
# 4. umis_core.yaml 업데이트
# 5. UMIS_ARCHITECTURE_BLUEPRINT.md 업데이트
# 6. 기본 동작 확인
```

### Phase 2: 검증 (30분)

```bash
# 1. estimator.py 확인
# 2. 테스트 스크립트 실행
# 3. 결과 비교
```

### Phase 3: 정리 (30분)

```bash
# 1. 문서 업데이트
# 2. CHANGELOG 작성
# 3. 최종 확인
```

**총 예상 시간**: 3-4시간

---

## 📁 파일 위치 참조

```
umis_main_1103/umis/
├── umis_rag/agents/estimator/
│   ├── phase4_fermi.py ⭐ (핵심)
│   ├── models.py ⭐ (핵심)
│   ├── estimator.py (확인 필요)
│   └── __init__.py (완료)
├── config/
│   └── fermi_model_search.yaml (선택)
├── scripts/
│   ├── test_fermi_final_fewshot.py (실행)
│   ├── test_fermi_improved_calculation.py (실행)
│   └── test_gpt5_phase_0_4_advanced.py (실행)
├── tests/
│   └── (신규 파일 생성 권장)
└── docs/
    ├── PHASE4_*.md (참고)
    ├── FERMI_*.md (참고)
    └── CHANGELOG.md (업데이트)
```

---

## ✅ 결론

### 필수 변경 파일 (5개) ⭐

1. **phase4_fermi.py**: Few-shot + 계산 검증
2. **models.py**: Config 옵션 추가
3. **umis.yaml**: Estimator 섹션 (6,539줄 중 386줄) ⭐
4. **umis_core.yaml**: Phase 4 섹션 (928줄) ⭐
5. **UMIS_ARCHITECTURE_BLUEPRINT.md**: Version Info + Estimator 섹션 ⭐

### 필수 확인 파일 (2개)

6. **estimator.py**: Config 전달 확인
7. **test_fermi_final_fewshot.py**: 테스트 실행

### 선택적 파일 (나머지)

- 설정, 문서, 추가 테스트 등

**→ 최소 7개 파일만 수정/확인하면 Phase 4 개선 완료!**

---

**다음 단계**: 필수 변경 파일부터 순차적으로 수정 시작! 🚀

