# Main 브랜치 설정 가이드

**목적**: alpha → main 병합 시 개발 파일 제외  
**대상**: 릴리즈 담당자

---

## 🎯 개요

UMIS는 **두 가지 브랜치 전략**을 사용합니다:

### alpha 브랜치 (개발)
- ✅ 모든 파일 포함 (개발 히스토리 보존)
- ✅ `archive/` 포함 (버전 히스토리)
- ✅ `dev_docs/` 포함 (RAG 개발 문서)
- ✅ `projects/` 전체 포함 (분석 예시)

### main 브랜치 (릴리즈)
- ✅ 핵심 코드 및 문서만
- 🚫 `archive/` 제외 (전체)
- 🚫 `dev_docs/` 제외 (전체)
- ⚠️ `projects/` 폴더 유지, 내용만 제외
  - `projects/README.md` ✅ 포함
  - `projects/*` 🚫 제외

---

## 📝 main 브랜치 .gitignore 설정

### 1. main 브랜치로 체크아웃

```bash
git checkout main
```

### 2. .gitignore 수정

```bash
# .gitignore 파일에 추가
echo "" >> .gitignore
echo "# Development files (main branch only)" >> .gitignore
echo "archive/" >> .gitignore
echo "dev_docs/" >> .gitignore
echo "" >> .gitignore
echo "# Project files (keep folder structure, exclude contents)" >> .gitignore
echo "projects/*" >> .gitignore
echo "!projects/README.md" >> .gitignore
```

**설명**:
- `archive/`: 전체 폴더 제외
- `dev_docs/`: 전체 폴더 제외
- `projects/*`: 폴더 내 모든 내용 제외
- `!projects/README.md`: README.md만 예외로 포함 (사용자 안내용)

### 3. 기존 추적 파일 제거

```bash
# Git 추적에서만 제거 (로컬 파일은 유지)
git rm -r --cached archive/
git rm -r --cached dev_docs/
git rm -r --cached projects/*

# projects/README.md는 다시 추가
git add -f projects/README.md

# 커밋
git add .gitignore
git commit -m "main: exclude development files and project contents"
```

### 4. 확인

```bash
# 제외된 파일들 확인
git status

# 예상 출력:
# On branch main
# Untracked files:
#   archive/
#   dev_docs/
#   projects/market_analysis/

# projects/ 폴더 구조 확인
ls projects/
# 예상 출력:
#   README.md  (포함됨 ✅)
#   market_analysis/  (제외됨)

# Git 추적 확인
git ls-files | grep projects
# 예상 출력:
#   projects/README.md  (이것만 추적됨)
```

### 5. projects/ 폴더 구조 유지 확인

```bash
# projects/ 폴더가 비어있지 않은지 확인
ls projects/

# 예상 출력:
#   README.md

# 이렇게 되면 성공:
# - projects/ 폴더 존재 ✅
# - projects/README.md 추적됨 ✅
# - projects/market_analysis/ 제외됨 ✅
```

### 6. Push

```bash
git push origin main
```

---

## 🔄 alpha → main 병합 시

### 일반적인 병합 (개발 파일 제외)

```bash
# 1. main으로 이동
git checkout main

# 2. alpha에서 선택적 병합
git checkout alpha -- umis_rag/
git checkout alpha -- scripts/
git checkout alpha -- config/schema_registry.yaml
git checkout alpha -- umis.yaml
# ... (필요한 파일들만)

# 3. 커밋
git add .
git commit -m "Release v7.1.0: merge from alpha"

# 4. Push
git push origin main
```

### 또는 병합 후 제거

```bash
# 1. 전체 병합
git checkout main
git merge alpha

# 2. 개발 파일 제거
git rm -r archive/ dev_docs/
git commit -m "Remove dev files for release"

# 3. Push
git push origin main
```

---

## ✅ 검증

main 브랜치에서 확인:

```bash
# main 브랜치
git checkout main

# 제외되어야 함 (untracked)
ls archive/      # 존재하지만 Git 추적 안 함
ls dev_docs/     # 존재하지만 Git 추적 안 함
git ls-files | grep archive    # 출력 없음
git ls-files | grep dev_docs   # 출력 없음

# projects/ 특별 케이스
ls projects/     # README.md만 (내용 제외됨)
git ls-files | grep projects
# 출력: projects/README.md (이것만 추적)

# 포함되어야 함
ls umis_rag/     # 정상 출력
ls scripts/      # 정상 출력
ls docs/         # 정상 출력 (활성 프로토콜)
ls setup/        # 정상 출력
```

---

## 📋 릴리즈 체크리스트

main 브랜치 push 전:

- [ ] VERSION.txt 업데이트
- [ ] CHANGELOG.md 업데이트
- [ ] UMIS_ARCHITECTURE_BLUEPRINT.md 검토
- [ ] archive/, dev_docs/ 제외 확인
- [ ] 핵심 파일들 존재 확인:
  - [ ] umis.yaml
  - [ ] umis_rag/
  - [ ] scripts/
  - [ ] docs/ (활성 프로토콜만)
  - [ ] setup/
  - [ ] config/schema_registry.yaml
  - [ ] requirements.txt
- [ ] 폴더 구조 확인:
  - [ ] projects/README.md 존재 (폴더 유지)
  - [ ] projects/market_analysis/ 제외됨

---

## 🎯 브랜치별 용도

### alpha (개발)
- 모든 개발 히스토리
- 아키텍처 문서
- 실험적 기능
- Deprecated 파일 보존

### main (릴리즈)
- 안정화된 코드만
- 사용자 필수 문서만
- 깔끔한 구조
- 프로덕션 준비

---

## 🔧 현재 상태 (alpha 브랜치)

**현재 브랜치**: alpha  
**상태**: 개발 진행 중

**main 브랜치 .gitignore 설정**은:
- main 브랜치로 전환 후 설정
- 또는 릴리즈 시점에 설정

**지금은**: alpha 브랜치에서 개발 계속
- archive/ 포함
- dev_docs/ 포함

---

**작성일**: 2025-11-03  
**버전**: v7.0.0

