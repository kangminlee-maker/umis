# 다음 세션 작업 가이드
**작성일**: 2025-11-12
**목적**: 이전 세션 작업 이어서 진행
**우선순위**: DART SG&A 파싱 완성

---

## 📊 이전 세션 완료 사항

### ✅ 완료된 작업 (엄청남!)

**1. Gap #1, #2, #3 모두 완료**
```yaml
Gap #1 (시계열 분석):
  - 코드: 1,030줄
  - 30개 진화 패턴
  - Q3, Q4-5, Q11 → Tier 1

Gap #2 (이익률 추정):
  - Fictional 200개 (백업)
  - Phase2Enhanced: 540줄
  - DART API 통합
  - Q7 → Tier 1

Gap #3 (실행 전략):
  - 코드: 800줄
  - Strategy Playbook 자동 생성
  - Q14, Q15 → Tier 1

Tier 1: 53% → 93% ✅
```

**2. 실제 데이터 시스템 구축**
```yaml
API 통합:
  ✓ DART API (상장사 재무)
  ✓ KOSIS API (통계청)
  ✓ Validator 메서드 추가
  ✓ OpenDartReader 통합

수집된 데이터:
  ✓ 10개 상장사 기본 (주요 계정)
  ✓ BGF리테일 완전 (21개 SG&A!)

파일:
  - dart_collected_benchmarks.yaml (10개)
  - bgf_retail_FINAL_complete.yaml (완전!)
```

**3. BGF리테일 완전 벤치마크 ⭐⭐⭐**
```yaml
완성도: 100%

주요 계정:
  ✓ 매출액: 81,317억원 (2023)
  ✓ 매출원가: 66,408억원 (81.7%)
  ✓ 판매비와관리비: 13,491억원 (2024)
  ✓ 영업이익: ~2,400억원 (3.0%)

SG&A 세부 (21개):
  ✓ 지급수수료: 5,216억원 (38.7%)
  ✓ 사용권자산상각비: 3,111억원 (23.1%)
  ✓ 급여: 1,957억원 (14.5%)
  ✓ 감가상각비: 1,807억원 (13.4%)
  ✓ 기타 17개

변동비/고정비 분류: ✅
공헌이익: 8.8% ✅

상태: Production Ready!
```

---

## 🎯 다음 세션 목표

### 우선순위 1: 다른 회사 SG&A 파싱 (5-10개)

**방법 A: 사용자 수동 확인** (가장 빠름!)
```yaml
절차:
  1. DART 웹사이트 접속
  2. 기업 검색 (예: 삼성전자)
  3. 2023년 또는 2024년 사업보고서
  4. "재무제표 주석" → "판매비와관리비" 또는 "영업비용" 섹션
  5. 세부 항목 테이블 복사
  6. 제공

추천 기업:
  - 삼성전자 (제조)
  - 이마트 (유통)
  - 아모레퍼시픽 (화장품)
  - LG생활건강 (화장품)
  - 하이브 (엔터)
  - CJ ENM (미디어)

소요: 기업당 10분
효과: 완전 벤치마크 즉시 생성
```

**방법 B: DART API 재시도** (자동화)
```yaml
스크립트: parse_sga_with_zip.py

이슈:
  - list API: 간헐적 900 오류
  - 밤 시간대 불안정 추정

해결:
  - 낮 시간대 (10:00-18:00) 재시도
  - 또는 rcept_no 직접 입력

명령:
  python scripts/parse_sga_with_zip.py --company "삼성전자" --year 2023
```

---

## 📁 주요 파일 위치

### 완성된 데이터
```yaml
data/raw/bgf_retail_FINAL_complete.yaml:
  - BGF리테일 완전 벤치마크
  - 21개 SG&A 세부
  - 변동비/고정비 분류
  - 공헌이익 8.8%
  - ⭐ 참고 템플릿!

data/raw/dart_collected_benchmarks.yaml:
  - 10개 상장사 기본 (주요 계정만)
  - BGF, GS리테일, 이마트, 삼성, LG 등
```

### 스크립트
```yaml
scripts/parse_sga_with_zip.py: ⭐ 최종 Robust 파서
  - ZIP 압축 해제
  - 숫자 무관 섹션 찾기
  - 영업비용 패턴 포함
  - 단위 자동 감지
  - 모든 항목 자동 추출

scripts/collect_dart_financials.py:
  - 주요 계정만 수집
  - 15개 기업 대상

scripts/collect_dart_with_notes.py:
  - OpenDartReader 활용
  - OFS/CFS 구분
```

### 설정
```yaml
.env:
  ✓ DART_API_KEY: 설정됨
  ✓ KOSIS_API_KEY: 설정됨 (따옴표 처리)

env.template:
  - API Key 필드 추가
  - '=' 문자 처리 가이드
```

---

## 🔧 핵심 개념 (중요!)

### 1. OFS vs CFS
```yaml
OFS (개별/별도 재무제표):
  - 자회사 제외
  - 단일 비즈니스 economics 파악 가능
  - ✅ 우선 사용!

CFS (연결재무제표):
  - 자회사 포함
  - 복합 비즈니스
  - ⚠️ Economics 파악 어려움

→ 항상 OFS 먼저 시도!
```

### 2. 변동비 vs 고정비
```yaml
매출원가:
  - 항상 변동비 (100%)

판매비와관리비 (SG&A):
  - 비즈니스 특성에 따라 다름!
  
  예) 편의점 (BGF):
    - 지급수수료: 변동비 (거래량 비례)
    - 사용권자산상각: 준변동비 (가맹점 수)
    - 급여: 고정비 (본부 직원)
  
  예) 온라인 플랫폼:
    - 광고비: 변동비 (고객 모집)
    - 서버비: 변동비 (트래픽)
    - 인건비: 고정비

→ Observer가 비즈니스 분석 후 분류!
```

### 3. 공헌이익 (Contribution Margin)
```yaml
공식:
  CM = Gross Profit - (SG&A 중 변동비)

중요성:
  - 영업이익: 고정비 포함 (회사별 천차만별)
  - 공헌이익: 비즈니스 본질 (Unit Economics)
  - BGF: CM 8.8% (영업이익 3.0%보다 의미 있음)

→ 공헌이익이 핵심!
```

### 4. 주석 필수
```yaml
손익계산서만:
  - 판매비와관리비 총액만 (예: 13,491억)
  - 세부 항목 없음

주석 (필수!):
  - "재무제표 주석" > "판매비와관리비"
  - 세부 항목 테이블 (급여, 광고비, 임차료 등)
  - 회사마다 위치 다름 (BGF는 30, 삼성은 22 등)

→ 주석 파싱 필수!
```

---

## 🚀 다음 세션 실행 계획

### Step 1: DART API 재시도 (낮 시간)

```bash
cd /Users/kangmin/umis_main_1103/umis

# 다른 회사 시도 (예: 이마트)
python3 scripts/parse_sga_with_zip.py --company "이마트" --year 2023

# 성공하면:
# - 주요 계정 ✓
# - SG&A 세부 항목 ✓
# - 자동 YAML 저장

# 실패하면 → Step 2
```

### Step 2: 수동 확인 방식 (확실!)

**절차:**
```yaml
1. DART 웹사이트:
   https://dart.fss.or.kr

2. 기업 검색:
   예) 삼성전자

3. 2023년 사업보고서 클릭

4. 목차에서 "재무제표 주석" 찾기

5. "판매비와관리비" 또는 "영업비용" 섹션

6. 세부 항목 테이블 복사:
   급여, XXXXX
   광고선전비, XXXXX
   ...

7. 제공 → 제가 즉시 YAML 변환
```

**목표 기업 (우선순위):**
```yaml
제조:
  - 삼성전자
  - LG전자

유통:
  - 이마트

화장품:
  - 아모레퍼시픽
  - LG생활건강

엔터/미디어:
  - 하이브
  - CJ ENM

목표: 5-10개 완전 벤치마크
```

### Step 3: 한국 오프라인 비즈니스

```yaml
통계청 기반 투명 추정:
  - 음식점, 헬스장, 미용실 등
  - 30-40개
  - 로직 100% 공개
  
소요: 2-3시간
```

---

## 📋 알려진 이슈

### DART API
```yaml
문제:
  - list API: 간헐적 900 오류
  - 밤 시간대 (22:00+) 불안정
  
해결:
  - 낮 시간대 재시도
  - 또는 수동 방식

성공한 것:
  - corpCode: OK
  - fnlttSinglAcntAll (주요 계정): OK
  - document (rcept_no 알 때): OK
```

### OpenDartReader
```yaml
문제:
  - finstate_all: 간헐적 오류
  - list: 900 오류
  
해결:
  - 직접 requests 사용
  - parse_sga_with_zip.py 스크립트 사용
```

---

## 💡 빠른 시작 (다음 세션)

### 즉시 실행
```bash
# 1. DART API 테스트
python3 scripts/parse_sga_with_zip.py --company "이마트" --year 2023

# 성공 시:
# → data/raw/이마트_sga_complete.yaml 생성
# → SG&A 세부 항목 자동 추출

# 2. 실패 시:
# → 사용자가 DART 웹사이트에서 수동 확인
# → SG&A 세부 항목 복사
# → 제공하면 제가 YAML 변환
```

---

## 📚 참고 문서

### 이론/개념
```yaml
- dev_docs/REALISTIC_DATA_APPROACH.md
  → 실제 데이터 접근 방법

- dev_docs/REAL_DATA_COLLECTION_PLAN.md
  → 데이터 수집 계획

- docs/guides/API_DATA_COLLECTION_GUIDE.md
  → API 사용 가이드
```

### 완성 데이터
```yaml
- data/raw/bgf_retail_FINAL_complete.yaml ⭐
  → BGF리테일 완전 벤치마크
  → 템플릿으로 사용!

- data/raw/profit_margin_benchmarks_korea_real.yaml
  → 새로운 구조 (검증 가능)
```

### 스크립트
```yaml
- scripts/parse_sga_with_zip.py ⭐
  → 최종 Robust 파서
  → ZIP 압축 해제 포함
  → 다음 세션 메인 도구!

- scripts/collect_dart_financials.py
  → 주요 계정 수집
```

---

## 🎯 다음 세션 목표

### 목표: 10-15개 완전 벤치마크

**구성:**
```yaml
완전 (SG&A 세부 포함): 10개
  - BGF리테일 ✅ (완료!)
  - 삼성전자
  - 이마트
  - GS리테일
  - 아모레퍼시픽
  - LG생활건강
  - 하이브
  - CJ ENM
  - 유한양행
  - 기타 1-2개

기본 (주요 계정만): 이미 10개 완료
```

**예상 소요:**
```yaml
방법 A (수동): 2-3시간
  - 사용자가 DART 확인
  - 복사/제공
  - 제가 YAML 변환

방법 B (자동): 1-2시간
  - DART API 재시도
  - parse_sga_with_zip.py 실행
```

---

## 🔑 API Key 상태

```yaml
.env 파일:
  ✓ DART_API_KEY: 설정됨 (40자)
  ✓ KOSIS_API_KEY: 설정됨 (따옴표 처리)

확인:
  python3 scripts/test_api_key_parsing.py
```

---

## 📊 현재 데이터 현황

### Verified (11개)
```yaml
완전 (SG&A 세부):
  1. BGF리테일 (21개 항목) ✅

기본 (주요 계정):
  2. GS리테일
  3. 이마트
  4. 삼성전자
  5. LG전자
  6. 유한양행
  7. 아모레퍼시픽
  8. LG생활건강
  9. 하이브
  10. CJ ENM

파일:
  - bgf_retail_FINAL_complete.yaml (완전)
  - dart_collected_benchmarks.yaml (기본 10개)
```

### 백업
```yaml
profit_margin_benchmarks_backup_fictional.yaml:
  - 200개 fictional 데이터
  - 참고용 보관
```

---

## 💡 Robust 파서 사용법

### parse_sga_with_zip.py

**기능:**
- ZIP 압축 해제 (.xml → ZIP)
- 숫자 무관 섹션 찾기 ("30. 판매비..." or "22. 판매비...")
- "영업비용" 패턴도 지원
- 단위 자동 감지 (백만원, 천원, 원)
- 모든 항목 자동 추출

**사용:**
```bash
python3 scripts/parse_sga_with_zip.py --company "이마트" --year 2023
python3 scripts/parse_sga_with_zip.py --company "삼성전자" --year 2023
```

**출력:**
```yaml
data/raw/{회사명}_sga_complete.yaml:
  - company: "이마트"
  - year: 2023
  - unit: "백만원"
  - sga_details_million: {급여: XXX, ...}
  - sga_count: N개
```

---

## 🎯 BGF 템플릿 활용

### 새 기업 추가 템플릿

**복사:**
```bash
cp data/raw/bgf_retail_FINAL_complete.yaml data/raw/samsung_template.yaml
```

**수정 항목:**
```yaml
company_info:
  company_name: "삼성전자"  # 변경
  industry: "전자제조"  # 변경
  ...

income_statement_2023:
  key_accounts_billion:
    revenue: XXXXX  # 업데이트
    ...

sga_details_2024:
  details_million:
    급여: XXXXX  # 업데이트
    ...
```

---

## 🚀 빠른 재개 체크리스트

### 즉시 확인
```yaml
1. ☐ API Key 상태:
   python3 scripts/test_api_key_parsing.py

2. ☐ 이전 데이터 확인:
   cat data/raw/bgf_retail_FINAL_complete.yaml

3. ☐ DART API 테스트:
   python3 scripts/parse_sga_with_zip.py --company "이마트" --year 2023

4. ☐ 성공 시 → 계속 진행
   실패 시 → 수동 방식
```

---

## 📊 목표 (다음 세션 종료 시)

```yaml
완전 벤치마크: 10개
  - BGF리테일 ✅
  - 삼성전자
  - 이마트
  - GS리테일
  - 아모레퍼시픽
  - LG생활건강
  - 하이브
  - CJ ENM
  - 유한양행
  - 기타 1개

각각:
  ✓ 주요 계정
  ✓ SG&A 세부 15-25개
  ✓ 변동비/고정비 분류
  ✓ 공헌이익 계산
```

---

## 🎊 이전 세션 총정리

```yaml
생성: ~45,000줄
시간: 1일
달성:
  ✅ Tier 1: 93%
  ✅ Gap #1, #2, #3 완료
  ✅ 실제 데이터 시스템
  ✅ BGF리테일 완전 벤치마크
  ✅ Robust 파서

품질: 실제 + 완전!
```

---

**다음 세션 시작:**
1. 이 문서 읽기
2. parse_sga_with_zip.py 실행 또는
3. DART 수동 확인

**BGF 템플릿 활용하여 빠르게 확장 가능!** 🚀




