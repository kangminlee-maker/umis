# SG&A 파서 정리 계획

**작성일**: 2025-11-14  
**목적**: 사용 중인 파서만 유지, 불필요한 파서 정리

---

## 📊 현재 파서 현황

### **개발된 파서 (8개)**

| 파일명 | 용도 | 상태 | 처리 |
|-------|-----|-----|-----|
| parse_sga_with_zip.py | 규칙 기반 (원조) | 대체됨 | ❌ 삭제 |
| parse_sga_llm_section_selector.py | LLM 섹션 선택 | 통합됨 | ❌ 삭제 |
| parse_sga_smart_signals.py | 스마트 시그널 | 실험용 | ❌ 삭제 |
| parse_sga_standard_accounts.py | 표준 계정 | 함수만 사용 | ⚠️ 유지 |
| parse_sga_final.py | 진화형 | 미사용 | ❌ 삭제 |
| parse_sga_optimized.py | 최적화 (규칙 기반) | **사용 중** | ✅ 유지 |
| parse_sga_llm_structure.py | LLM 구조 파싱 | 대체됨 | ❌ 삭제 |
| parse_sga_hybrid.py | Hybrid (복잡 구조) | **사용 중** | ✅ 유지 |

---

## ✅ **최종 사용 파서 (2개)**

### **1. parse_sga_optimized.py** ⭐⭐⭐
**용도**: 일반 기업 (간단한 구조)

**적용 기업**:
- ✅ GS리테일 (A등급, 4.1% 오차)
- ✅ LG생활건강 (A등급, 3.0% 오차)
- ✅ LG전자 (A등급, 4.6% 오차)
- ✅ 아모레퍼시픽 (A등급, 4.1% 오차)
- ✅ 유한양행 (B등급, 7.9% 오차)

**파이프라인**:
```
Step 1: 파서 4 - 표준 계정 10개+ 필터링
Step 2: 규칙 기반 1차 검증
Step 3: 파서 1 - 정규식 파싱
Step 4: 품질 검증 (A/B/C/D)
Step 5: C/D등급만 LLM 재검증
```

**비용**: $0 (A/B등급), $0.003 (C/D등급)  
**성공률**: 80% (5개 중 4개 A등급)

---

### **2. parse_sga_hybrid.py** ⭐⭐⭐
**용도**: 복잡한 구조 (소계 위/아래 의미 다름)

**적용 기업**:
- ✅ SK하이닉스 (A등급, 2.1% 오차)

**파이프라인**:
```
Step 1: 파서 4 - 표준 계정 필터 (또는 섹션 번호 지정)
Step 2: 당기 섹션만 추출 (전기 제외)
Step 3: 규칙으로 모든 항목 + 숫자 정확히 추출
Step 4: LLM으로 포함/제외 판단
Step 5: 결합
```

**핵심 특징**:
- 숫자 정확도 100% (규칙 기반)
- 구조 이해 100% (LLM 판단)
- 환각 방지 (LLM은 판단만)

**비용**: $0.005  
**성공률**: 100% (SK하이닉스 A등급)

---

## 📦 **보조 모듈 (유지)**

### **parse_sga_standard_accounts.py**
**이유**: 
- `extract_all_sga_sections()` 함수 제공
- `STANDARD_SGA_ACCOUNTS` 정의
- optimized와 hybrid가 import해서 사용

**처리**: ✅ 유지 (함수 라이브러리)

---

## ❌ **삭제 대상 (5개)**

### **1. parse_sga_with_zip.py**
- 이유: parse_sga_optimized.py로 대체
- 기능: 동일 (개선된 버전이 optimized)

### **2. parse_sga_llm_section_selector.py**
- 이유: optimized에 통합됨
- 기능: LLM 섹션 선택 + 3중 검증

### **3. parse_sga_smart_signals.py**
- 이유: 실험용, Production 미사용
- 기능: 급여 클러스터 패턴

### **4. parse_sga_final.py**
- 이유: 진화형 학습, 현재 미사용
- 기능: learned_sga_patterns.yaml 학습

### **5. parse_sga_llm_structure.py**
- 이유: parse_sga_hybrid.py로 대체
- 기능: LLM 구조 파싱

---

## 🎯 **사용 가이드 (최종)**

### **일반 기업 (80%)**
```bash
python3 scripts/parse_sga_optimized.py \
  --company GS리테일 \
  --year 2024 \
  --rcept-no 20250312000991
```

**예상 등급**:
- 80%: A/B등급 (LLM 비용 $0)
- 20%: C/D등급 (LLM 비용 $0.003)

---

### **복잡한 구조 (20%)**
```bash
python3 scripts/parse_sga_hybrid.py \
  --company SK하이닉스 \
  --year 2024 \
  --rcept-no 20250319000665
```

**적용 케이스**:
- 소계 위/아래 의미 다름
- 계산된 항목 (총지출액 - 자산화 = 경상개발비)
- 복잡한 테이블 구조

**비용**: $0.005

---

## 📁 **최종 파일 구조**

```
scripts/
  ├── parse_sga_optimized.py       ✅ 메인 (일반 기업)
  ├── parse_sga_hybrid.py          ✅ 메인 (복잡 구조)
  ├── parse_sga_standard_accounts.py ✅ 보조 (함수 제공)
  │
  ├── parse_sga_with_zip.py        ❌ 삭제
  ├── parse_sga_llm_section_selector.py ❌ 삭제
  ├── parse_sga_smart_signals.py   ❌ 삭제
  ├── parse_sga_final.py           ❌ 삭제
  └── parse_sga_llm_structure.py   ❌ 삭제
```

---

## 🚀 **다음 단계**

1. ❌ 5개 파서 삭제
2. ✅ 2개 메인 파서 + 1개 보조 모듈 유지
3. 📝 README 업데이트 (사용 가이드)
4. 🔄 배치 스크립트 업데이트 (optimized/hybrid 사용)

