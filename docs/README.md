# UMIS Documentation

UMIS 프로젝트의 문서를 관리하는 폴더입니다.

## 📁 폴더 구조

### `/market_analysis/` (Git 제외)
시장 분석 및 비즈니스 인사이트 문서들이 저장됩니다.
- 민감한 비즈니스 정보 포함
- `.gitignore`에 의해 Git 추적 제외

### `/v[version]/`
각 버전별 기술 문서 및 릴리즈 정보
- `release_notes.md` - 버전 릴리즈 노트
- `integration_plan.md` - 통합 계획서
- `conflict_analysis.md` - 충돌 분석 및 해결
- 기타 버전별 기술 문서

### 기타 문서
- `umis_format_comparison.md` - UMIS 포맷 비교
- `UMIS-DART-재무제표-조사-프로토콜.md` - 재무 분석 프로토콜

## 📝 문서 작성 가이드

### 버전 문서
새로운 버전 출시 시:
1. `/v[version]/` 폴더 생성
2. 필수 문서:
   - `release_notes.md`
   - `changelog.md` (상세 변경사항)
   - `migration_guide.md` (필요시)

### 시장 분석 문서
- `/market_analysis/` 폴더에 저장
- 민감 정보는 반드시 이 폴더에만 저장
- 파일명에 날짜 포함 권장: `korea_si_market_analysis_2025.md`

## 🔒 보안 주의사항

- `/market_analysis/` 폴더의 내용은 Git에 커밋되지 않습니다
- 민감한 비즈니스 정보는 반드시 이 폴더에만 저장하세요
- 공개 가능한 기술 문서만 버전 폴더에 저장하세요

## 📚 버전 히스토리

- `v6.0.3/` - Validated Opportunity Discovery Process
- `v6.0.2/` - Integrated Opportunity Discovery Process (archive에 저장)
- `v6.0.1/` - Information Flow Optimization (archive에 저장)

자세한 버전 정보는 프로젝트 루트의 `CHANGELOG.md`를 참조하세요.
