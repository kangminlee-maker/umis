# v5.0 파일 구성 설명

## 🗂️ v5.0 파일들의 구성

v5.0은 파일 크기 제한으로 인해 여러 파일로 분할되었습니다:

### 📄 파일 목록

1. **`umis_guidelines_v5.0.yaml`** (36KB)
   - 완전한 통합 버전
   - 모든 내용을 포함한 최종 파일

2. **`umis_guidelines_v5.0_part1.yaml`** (14KB)
   - 시스템 개요 및 핵심 구성요소
   - 에이전트 정의 (MOwner, MAnalyst, MExplorer)

3. **`umis_guidelines_v5.0_part2.yaml`** (11KB)
   - 에이전트 정의 계속 (MQuant, MValidator, MCurator)
   - 협업 규칙

4. **`umis_guidelines_v5.0_part3.yaml`** (9KB)
   - 워크플로우 정의
   - 품질 관리 시스템

5. **`umis_guidelines_v5.0_additions.yaml`** (6KB)
   - v5.0 신규 기능
   - Adaptive Intelligence
   - Progress Guardian System
   - Data Integrity System

## 🔧 파일 생성 과정

```bash
# 토큰 제한으로 인한 분할 작성
1. part1 작성 → part2 작성 → part3 작성
2. 파일들 병합: cat part1 part2 part3 > v5.0.yaml
3. 추가 기능 작성: additions.yaml
4. 최종 통합: v5.0.yaml + additions.yaml
```

## 📌 사용 권장사항

- **일반 사용**: `umis_guidelines_v5.0.yaml` 사용
- **부분 참조**: 필요한 part 파일만 참조
- **신규 기능만**: `additions.yaml` 참조

## ⚡ v5.0 이후

v5.0부터는 모듈형 구조로 전환되어 더 이상 단일 파일이 아닙니다:
- 위치: `../UMIS-framework/`
- 구조: 기능별 폴더 및 파일 분리
- 장점: 유지보수 용이, 버전 관리 개선

---

*이 설명은 v5.0 파일 구조를 이해하는 데 도움을 드리기 위해 작성되었습니다.*
