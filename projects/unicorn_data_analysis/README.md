# 🦄 유니콘 기업 데이터 분석 프로젝트

**프로젝트 일자:** 2025-11-04  
**데이터 소스:** CB Insights Unicorn List  
**총 기업 수:** 800개  
**목표:** UMIS RAG 시스템의 비즈니스 사례 데이터로 활용

---

## 📁 파일 구조

### 원본 데이터
- `Unicorn Club_FV - 시트1.csv` - 원본 CSV 파일

### 정리된 데이터
- `unicorn_companies_structured.json` - 구조화된 데이터 (v2.0)
- **`unicorn_companies_rag_enhanced.json`** - RAG 호환 데이터 (v3.0) ⭐
- `unicorn_companies.json` - 기본 JSON 변환 (v1.0)
- `unicorn_companies_structured_backup_*.json` - 백업 파일

### 파일럿 데이터
- **`pilot_companies.json`** - 파일럿 10개 유니콘 선정 결과

### 문서
- `UNICORN_DATA_README.md` - 프로젝트 전체 가이드 ⭐
- `unicorn_companies_summary.md` - Markdown 요약본
- `unicorn_companies_comparison.md` - 데이터 구조 변경 전후 비교
- `unicorn_types.ts` - TypeScript 타입 정의

### 투자자 데이터 정리
- `INVESTOR_CLEANUP_FINAL_REPORT.md` - 최종 정리 보고서 ⭐
- `INVESTOR_DUPLICATES_REVIEW.md` - 중복 분석 상세
- `investor_safe_duplicates.json` - 중복 원시 데이터
- `investor_duplicates_report.json` - 중복 리포트 데이터

---

## 🚀 빠른 시작

### Python
```python
import json

with open('unicorn_companies_structured.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 800개 유니콘 기업 데이터 분석
for company in data['companies']:
    print(f"{company['company']}: {company['valuation']['amount_billion']}")
```

### TypeScript
```typescript
import data from './unicorn_companies_structured.json';
import type { UnicornDatabase } from './unicorn_types';

const db: UnicornDatabase = data;
console.log(`Total companies: ${db.metadata.total_companies}`);
```

---

## 📊 주요 통계

- **총 기업:** 800개
- **총 국가:** 41개
- **총 카테고리:** 17개
- **고유 투자자:** 1,668개 (정리 후)
- **총 펀딩 라운드:** 2,709회

### 국가별 Top 3
1. 🇺🇸 미국: 402개 (50.3%)
2. 🇨🇳 중국: 158개 (19.8%)
3. 🇮🇳 인도: 40개 (5.0%)

### 투자자 Top 3
1. Tiger Global Management: 146회
2. Accel: 113회
3. Sequoia Capital: 91회

---

## ✅ 데이터 품질

### 정리 작업 완료
- ✅ 311건의 투자자 이름 중복/오타 수정
- ✅ 대소문자, 띄어쓰기, 특수문자 통일
- ✅ Business/History 필드 구조화
- ✅ 투자자 목록 배열화

### 검증 완료
- ✅ 다른 투자자 구분 유지 (예: SoftBank ≠ SoftBank Group)
- ✅ 지역별 분사 구분 유지 (예: Sequoia Capital ≠ Sequoia Capital China)
- ✅ 원본 백업 완료

---

### 자동화 스크립트
- **`scripts/01_add_rag_metadata.py`** - RAG 메타데이터 자동 추가 ⭐
- **`scripts/02_select_pilot_companies.py`** - 파일럿 10개 선정
- **`scripts/03_research_template.md`** - 리서치 템플릿

---

## 🚀 빠른 시작

### 1. RAG 호환 데이터 사용

```python
import json

# RAG 호환 데이터 로드
with open('unicorn_companies_rag_enhanced.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 첫 번째 기업의 RAG 메타데이터 확인
company = data['companies'][0]
print(f"Source ID: {company['rag_metadata']['source_id']}")
print(f"Canonical ID: {company['rag_metadata']['canonical_chunk_id']}")
print(f"Pattern Type: {company['business']['business_model']['pattern_type']}")
```

### 2. 파일럿 데이터 확인

```python
# 파일럿 10개 기업 로드
with open('pilot_companies.json', 'r', encoding='utf-8') as f:
    pilot = json.load(f)

for company in pilot['pilot_companies']:
    print(f"{company['company']}: {company['valuation']['amount_billion']}")
```

### 3. 자동화 스크립트 실행

```bash
# RAG 메타데이터 추가 (이미 실행됨)
python3 scripts/01_add_rag_metadata.py

# 파일럿 선정 (이미 실행됨)
python3 scripts/02_select_pilot_companies.py
```

---

## 📊 데이터 버전 히스토리

| 버전 | 파일 | 설명 | 상태 |
|------|------|------|------|
| v1.0 | `unicorn_companies.json` | CSV → JSON 기본 변환 | ✅ 완료 |
| v2.0 | `unicorn_companies_structured.json` | 구조화 (funding_history, business 객체화) | ✅ 완료 |
| v3.0 | `unicorn_companies_rag_enhanced.json` | RAG 메타데이터 추가 | ✅ 완료 |
| v3.1 | `unicorn_companies_rag_enhanced.json` | Performance Metrics 구조 개선 | ✅ 완료 |

---

## 🎯 현재 진행 상황

### ✅ 완료된 작업

1. **데이터 정리** (v1.0 → v2.0)
   - CSV → JSON 변환
   - Business/History 필드 구조화
   - 투자자 이름 중복 제거 (311건)

2. **RAG 호환 변환** (v2.0 → v3.0)
   - Canonical Index 메타데이터 자동 추가
   - Category → Pattern Type 매핑
   - Growth Trajectory 추출
   - Business Model 필드 구조 확장

3. **파일럿 선정**
   - Top 10 유니콘 선정 완료
   - 산업/국가 다양성 확보
   - Data Richness Score 계산

### 🔄 진행 중

- **파일럿 리서치** (0/10 완료)
  - Stripe, SpaceX, Klarna, Instacart, Bytedance
  - Databricks, Rivian, Fanatics, BYJU's, DJI

### 📋 계획

1. **Phase 1: 파일럿 완료** (1-2주)
   - 10개 기업 상세 리서치
   - 템플릿 검증 및 개선

2. **Phase 2: Tier 1 확장** (4-6주)
   - Top 100 기업 기본 정보 추가

3. **Phase 3: RAG 통합** (1주)
   - Canonical Index 생성
   - UMIS Explorer RAG 연동

---

## 📖 상세 문서

### 프로젝트 문서
- **`TRANSFORMATION_PLAN.md`** - 전체 변환 계획 ⭐
- **`STRUCTURE_UPDATE_REPORT.md`** - 구조 개선 보고서 (v3.1) ⭐
- **`AUTOMATION_COMPLETE_REPORT.md`** - 자동화 완료 보고서
- **`UNICORN_DATA_README.md`** - 데이터 가이드
- **`unicorn_companies_comparison.md`** - 구조 비교

### 투자자 정리
- **`INVESTOR_CLEANUP_FINAL_REPORT.md`** - 정리 보고서
- **`INVESTOR_DUPLICATES_REVIEW.md`** - 중복 분석

### TypeScript 지원
- **`unicorn_types.ts`** - 타입 정의

---

## 📊 통계

- **총 기업:** 800개
- **고유 투자자:** 1,668개 (정리 후)
- **총 펀딩 라운드:** 2,709회
- **총 펀딩 금액:** $XXX,XXXM
- **국가:** 41개
- **카테고리:** 17개

### Pattern Type 분포
- Fintech Platform: 152개 (19.0%)
- SaaS Platform: 132개 (16.5%)
- Marketplace: 130개 (16.2%)
- AI Platform: 64개 (8.0%)
- Healthcare Service: 57개 (7.1%)
- *[전체 14개 패턴]*

---

## 🛠️ 기술 스택

- **데이터 처리:** Python 3.x
- **데이터 형식:** JSON
- **스키마:** UMIS RAG Schema v7.0.0
- **타입 정의:** TypeScript

---

## 💡 사용 사례

### 1. Explorer RAG 강화
800개 실제 비즈니스 사례를 통한 패턴 매칭 정확도 향상

### 2. 투자자 네트워크 분석
1,668개 투자자 × 5,738건 투자 관계 분석

### 3. 산업 벤치마크
17개 카테고리 × 41개 국가 벤치마크 데이터

### 4. 시계열 분석
2010-2025 펀딩 트렌드 및 밸류에이션 추이

---

**생성:** UMIS v7.0.0  
**최종 업데이트:** 2025-11-04  
**다음 단계:** 파일럿 10개 리서치 시작
