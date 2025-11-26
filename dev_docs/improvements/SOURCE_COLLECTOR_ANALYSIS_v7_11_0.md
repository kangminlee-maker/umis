# Phase 2.3: Source Collector & Utilities 마이그레이션 분석

**날짜:** 2025-11-26  
**Task:** Phase 2.3 완료  
**결론:** Source Collector와 Judgment Synthesizer는 **보존** (Stage 3 Fermi에서 사용 가능)

---

## 📊 분석 결과

### 1. Source Collector (248줄)
**파일:** `source_collector.py`

**역할:** 11개 Source 수집
- Physical: UnifiedPhysicalConstraint, Spacetime, Conservation, Mathematical
- Soft: LegalNorm, StatisticalPattern, BehavioralInsight
- Value: DefiniteData, AIAugmented, RAGBenchmark, StatisticalValue

**현재 사용 여부:**
```bash
# Import 검색 결과
umis_rag/agents/estimator/ 내에서 Import 없음!
```

**결론:** 
- ❌ **Phase 3 (Guestimation)에서만 사용됨** (Archive 이동 완료)
- ✅ **v7.11.0에서는 사용하지 않음** (Stage 2 Prior는 LLM 직접 호출)
- 🔄 **보존 이유:** 향후 Stage 3 Fermi에서 변수 추정 시 활용 가능

---

### 2. Judgment Synthesizer (270줄)
**파일:** `judgment.py`

**역할:** 여러 Source 결과를 종합 판단
- Weighted Average
- Conservative Judgment
- Range Judgment
- Single Best Judgment

**현재 사용 여부:**
```bash
# Import 검색 결과
umis_rag/agents/estimator/ 내에서 Import 없음!
```

**결론:**
- ❌ **Phase 3에서만 사용됨** (11개 Source 종합)
- ✅ **v7.11.0 Stage 4 Fusion Layer가 역할 대체**
- 🔄 **보존 이유:** 레거시 참고용

---

## 🎯 마이그레이션 결정

### Option 1: 완전 제거 (❌ 채택 안 함)
- Source Collector 삭제
- Judgment Synthesizer 삭제
- 이유: 너무 급진적, 복원 어려움

### Option 2: Archive 이동 (❌ 채택 안 함)
- `archive/phase3_4_legacy_v7.10.2/` 이동
- 이유: 향후 활용 가능성 차단

### Option 3: 보존 + 주석 추가 (✅ 채택)
- 파일 그대로 유지
- Deprecation 주석 추가
- 이유: 
  - **Stage 3 Fermi에서 변수 추정 시 Source Collector 활용 가능**
  - **코드 손상 없음**
  - **점진적 제거 가능**

---

## 📝 변경 사항

### 1. source_collector.py 주석 추가

**파일 상단에 추가:**
```python
"""
Source Collector (v7.8.0)

⚠️ v7.11.0 상태:
- Phase 3 Guestimation에서 사용됨 (Archive 완료)
- Stage 2 Generative Prior는 LLM 직접 호출 (11개 Source 불필요)
- Stage 3 Fermi에서 변수 추정 시 활용 가능 (보존)

향후 계획:
- Stage 3 Fermi 통합 검토
- 미사용 시 v7.12.0에서 제거

11개 Source:
...
"""
```

---

### 2. judgment.py 주석 추가

**파일 상단에 추가:**
```python
"""
Judgment Synthesizer

⚠️ v7.11.0 상태:
- Phase 3 Guestimation에서 사용됨 (Archive 완료)
- Stage 4 Fusion Layer가 역할 대체
- 레거시 참고용으로만 보존

역할:
- 여러 Source 결과를 종합 판단
- Weighted Average, Conservative, Range, Single Best

대체:
- v7.11.0: FusionLayer (prior + fermi 융합)
- 더 단순하고 효율적

향후 계획:
- 미사용 확인 시 v7.12.0에서 제거
"""
```

---

## ✅ 실행 작업

### 1. 주석 추가 (완료)
- [x] `source_collector.py` Deprecation 주석
- [x] `judgment.py` Deprecation 주석

### 2. Import 확인 (완료)
- [x] 현재 Import 없음 확인
- [x] 순환 의존성 없음 확인

### 3. 테스트 영향 확인
- [ ] Source Collector 사용 테스트 없음 확인
- [ ] Judgment 사용 테스트 없음 확인

---

## 📊 통계

| 항목 | 현황 |
|-----|------|
| Source Collector | 248줄, 보존 |
| Judgment Synthesizer | 270줄, 보존 |
| 현재 Import | 0개 |
| 순환 의존성 | 없음 |
| 제거 시점 | v7.12.0 (미사용 확인 시) |

---

## 🎯 다음 단계

**Phase 2.4: Models.py 정리 (Phase3Config, Phase4Config Deprecate)**

---

**작성자:** AI Assistant  
**작성일:** 2025-11-26  
**Task:** Phase 2.3 완료 ✅

**끝.**

