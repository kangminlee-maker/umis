# 🦄 유니콘 기업 데이터 분석 프로젝트

**프로젝트 일자:** 2025-11-04  
**데이터 소스:** CB Insights Unicorn List  
**총 기업 수:** 800개

---

## 📁 파일 구조

### 원본 데이터
- `Unicorn Club_FV - 시트1.csv` - 원본 CSV 파일

### 정리된 데이터 ⭐
- **`unicorn_companies_structured.json`** - 구조화된 최신 데이터 (사용 권장)
- `unicorn_companies.json` - 기본 JSON 변환 (v1.0)
- `unicorn_companies_structured_backup_*.json` - 백업 파일

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

## 📖 상세 문서

- **전체 가이드:** `UNICORN_DATA_README.md`
- **정리 보고서:** `INVESTOR_CLEANUP_FINAL_REPORT.md`
- **데이터 구조:** `unicorn_companies_comparison.md`

---

**생성:** UMIS v7.0.0  
**최종 업데이트:** 2025-11-04
