# UMIS 배포 가이드

**목적**: Alpha → Main 배포 시 자동으로 특정 폴더 제외  
**대상 폴더**: projects/, archive/, dev_docs/

---

## 🚀 배포 방법

### 방법 1: 자동 스크립트 (권장 ⭐)

```bash
# Alpha 브랜치에서 실행
./scripts/deploy_to_main.sh

# 자동 처리:
# 1. Alpha 업데이트
# 2. Main 전환
# 3. Alpha merge
# 4. projects/, archive/, dev_docs/ 자동 제거
# 5. 커밋 (버전 입력)
# 6. Main push (확인 후)
# 7. Tag 생성
# 8. Alpha 복귀
```

**장점**:
- ✅ 실수 방지
- ✅ 일관된 프로세스
- ✅ 자동 정리

---

### 방법 2: 수동 배포

```bash
# 1. Alpha 최신화
git checkout alpha
git pull origin alpha

# 2. Main 전환
git checkout main
git pull origin main

# 3. Alpha merge
git merge alpha --no-ff --no-commit

# 4. 제외 폴더/파일 삭제
git rm -r projects/ archive/ dev_docs/ 2>/dev/null || true
git rm cursor_global_rules.txt 2>/dev/null || true
git rm .env.backup_* 2>/dev/null || true

# 5. 커밋
git commit -m "release: vX.X.X - Production 배포"

# 6. Push
git push origin main

# 7. Tag
git tag vX.X.X -m "vX.X.X: ..."
git push origin vX.X.X

# 8. Alpha 복귀
git checkout alpha
```

---

## 📋 제외 규칙

### Main 브랜치에서 제외

```yaml
제외 폴더:
  - projects/: 분석 프로젝트 (실험적)
  - archive/: deprecated 코드/문서
  - dev_docs/: 설계 문서, 세션 요약

제외 파일:
  - cursor_global_rules.txt: 개인 Cursor 설정
  - .env.backup_*: 환경변수 백업 (민감 정보)

이유:
  - Main: Production 코드만
  - Alpha: 전체 히스토리 + 개인 설정
  - 민감 정보 보호

효과:
  - Main 초간결
  - Alpha 완전 보존
  - 보안 강화
```

### Alpha 브랜치에서 유지

```yaml
유지:
  ✅ projects/: 모든 분석 프로젝트
  ✅ archive/: deprecated 코드/문서
  ✅ dev_docs/: 설계 문서 (10개+)

이유:
  - 개발 히스토리
  - 의사결정 추적
  - 학습 자료
```

---

## 🔍 Git Attributes 설명

### .gitattributes 파일

```
# Export-ignore: git archive 명령어 시 제외
dev_docs/ export-ignore
archive/ export-ignore
projects/ export-ignore

# 주의: git merge 시에는 적용 안 됨!
# → 스크립트 사용 필요
```

**한계**:
- `git archive` 명령어 시에만 작동
- `git merge` 시에는 적용 안 됨
- 따라서 배포 스크립트 필요

---

## ⚠️ 주의사항

### 1. Merge 전략

```yaml
사용: --no-ff (Fast-forward 금지)
이유: Merge 이력 보존

명령:
  git merge alpha --no-ff
```

### 2. 제외 폴더 존재 확인

```bash
# 폴더가 없을 수 있음 (이미 제거된 경우)
git rm -r dev_docs/ 2>/dev/null || true

# 2>/dev/null: 에러 숨김
# || true: 실패해도 계속
```

### 3. 커밋 메시지

```yaml
형식:
  release: vX.X.X - [주요 기능]
  
  Alpha → Main merge 완료
  
  제외:
  - projects/
  - archive/
  - dev_docs/

예:
  release: v7.3.2 - Single Source of Truth
```

---

## 🎯 배포 체크리스트

### 배포 전

```yaml
✅ Alpha 테스트 100% 통과
✅ Release Notes 작성
✅ CHANGELOG 업데이트
✅ CURRENT_STATUS.md 버전 확인
```

### 배포 중

```yaml
✅ Alpha 최신 상태
✅ Main merge
✅ projects/, archive/, dev_docs/ 제거
✅ 커밋 메시지 작성
```

### 배포 후

```yaml
✅ Main push
✅ Tag 생성
✅ GitHub 확인
✅ Alpha 복귀
```

---

## 📚 FAQ

### Q: 왜 projects/를 제외?

```
A: 실험적 분석 프로젝트
   - 개발 중이거나 완료되지 않은 프로젝트
   - Main은 안정된 코드만
```

### Q: archive/는?

```
A: Deprecated 코드/문서
   - v1.0, v2.1 등 과거 버전
   - Main에 불필요
   - Alpha에서 히스토리 보존
```

### Q: dev_docs/는?

```
A: 개발 문서
   - 설계 문서 (45,000줄+)
   - 세션 요약
   - 분석 보고서
   - Alpha에서만 필요
```

### Q: 수동으로 해도 되나?

```
A: 가능하지만 스크립트 권장
   - 실수 방지
   - 일관성
   - 빠름
```

---

## 🛠️ 스크립트 사용법

### 기본 사용

```bash
# 1. Alpha 브랜치에서
git checkout alpha

# 2. 스크립트 실행
./scripts/deploy_to_main.sh

# 3. 프롬프트 따라 진행
# - 버전 입력: v7.3.3
# - Push 확인: y
# - Tag 메시지: "v7.3.3: ..."
```

### 고급 옵션 (수동 제어)

```bash
# 스크립트 없이 단계별 수동
git checkout alpha
git pull origin alpha

git checkout main
git merge alpha --no-ff --no-commit

# 제외할 폴더만 삭제
git rm -r projects/ archive/ dev_docs/ 2>/dev/null || true

git commit  # 메시지 직접 작성
git push origin main

# Tag
git tag vX.X.X -m "..."
git push origin vX.X.X

git checkout alpha
```

---

**스크립트 위치**: `scripts/deploy_to_main.sh`  
**권한**: 실행 가능 (chmod +x)  
**사용**: `./scripts/deploy_to_main.sh`

저장하시겠습니까? 🎯

