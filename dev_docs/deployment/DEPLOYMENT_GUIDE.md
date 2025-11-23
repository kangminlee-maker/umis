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

### 방법 2: 수동 배포 (안전 로직)

```bash
# 1. Alpha 최신화
git checkout alpha
git pull origin alpha

# 2. Main 전환
git checkout main
git pull origin main

# 3. Alpha merge (커밋하지 않음)
git merge alpha --no-ff --no-commit

# 4. 제외 폴더/파일 삭제 (간단 로직 ⭐)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 4-1. Archive 전체 제거
git rm -r archive/ 2>/dev/null || true

# 4-2. 개발 문서 제거
git rm -r dev_docs/ 2>/dev/null || true

# 4-3. 프로젝트 폴더 제거
git rm -r projects/ 2>/dev/null || true

# 4-4. 개인 설정 파일 제거
git rm cursor_global_rules.txt 2>/dev/null || true
git rm .env.backup_* 2>/dev/null || true

# 4-5. .gitignore 충돌 해결 (Main 버전 유지)
# Main의 .gitignore에는 "archive/" 규칙 있음
git checkout --ours .gitignore 2>/dev/null || true
git add .gitignore
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 5. 최종 확인
git status
# 예상 결과:
# - archive/ 전체 삭제 ✅
# - dev_docs/ 삭제 ✅
# - projects/ 삭제 ✅

# 6. 커밋
git commit -m "release: vX.X.X - Production 배포

Alpha → Main merge 완료

제외된 폴더:
- archive/v1.x ~ v6.x (구 버전, 66K+ 줄)
- archive/guestimation_v1_v2 (deprecated)
- dev_docs/ (개발 문서)
- projects/ (분석 프로젝트)

유지된 폴더:
- archive/deprecated_features/ (v7.x deprecated)
- archive/v7.2.0_and_earlier/ (v7.2.0 이하)
"

# 7. Push (확인 후)
git push origin main

# 8. Tag
git tag vX.X.X -m "vX.X.X: [주요 기능]"
git push origin vX.X.X

# 9. Alpha 복귀
git checkout alpha
```

---

## 📋 제외 규칙

### Main 브랜치에서 제외

```yaml
제외 폴더:
  - projects/: 분석 프로젝트 (실험적)
  - archive/: 전체 제외 ⭐ (구 버전 + deprecated 모두)
  - dev_docs/: 설계 문서, 세션 요약

제외 파일:
  - cursor_global_rules.txt: 개인 Cursor 설정
  - .env.backup_*: 환경변수 백업 (민감 정보)

이유:
  - Main: Production 코드만 (순수 실행 가능 코드)
  - Alpha: 전체 히스토리 + 개발 문서
  - Archive는 개발 참조용 (Main 불필요)
  - 민감 정보 보호

효과:
  - Main 초간결 (실행 코드만)
  - Alpha 완전 보존 (히스토리 전체)
  - 저장소 크기 최소화
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

## 🔐 안전 로직 상세 설명

### 1. Archive 전체 제외

#### 정책
- Main: archive 폴더 전체 제외
- Alpha: archive 폴더 전체 유지
- 이유: Main은 순수 실행 코드만

#### 구현
```bash
# 간단 명령 (전체 제거)
git rm -r archive/ 2>/dev/null || true

# 안전 장치:
# - 2>/dev/null: 에러 메시지 숨김 (폴더 없을 수 있음)
# - || true: 실패해도 계속 진행
```

#### 검증
```bash
# 제거 후 확인
git status | grep "archive/"

# 예상 결과:
# deleted:    archive/deprecated_features/...
# deleted:    archive/v1.x/...
# deleted:    archive/v2.x/...
# (archive 관련 모두 삭제됨)

# 또는
ls archive/ 2>/dev/null && echo "❌ archive 아직 있음!" || echo "✅ archive 제거됨"
```

### 2. .gitignore 충돌 해결

#### 문제
- Alpha: `# archive/` (주석, 포함)
- Main: `archive/v*.x/` (활성, 제외)
- 머지 시 충돌 발생

#### 해결
```bash
# 1. Merge 충돌 발생
git merge alpha --no-ff --no-commit
# CONFLICT (content): Merge conflict in .gitignore

# 2. Main 버전 유지 (archive 제외 규칙 활성)
git checkout --ours .gitignore

# 3. 스테이징
git add .gitignore

# 4. 검증
cat .gitignore | grep "archive"
# 출력: archive/v*.x/  (활성화됨)
```

#### 이유
- Main: archive 제외 필요
- Alpha: archive 포함 필요
- 각 브랜치의 .gitignore 독립 유지

### 3. 머지 전략

#### --no-commit 사용 이유
```bash
# ❌ 바로 커밋
git merge alpha --no-ff
# → 자동 커밋, 제외 작업 불가

# ✅ 커밋 보류
git merge alpha --no-ff --no-commit
# → 수동 제외 작업 가능
# → 검증 후 커밋
```

#### 검증 단계
```bash
# 1. 머지 완료
git merge alpha --no-ff --no-commit

# 2. 제외 작업
git rm -r archive/ dev_docs/ projects/

# 3. 상태 확인
git status

# 4. Diff 확인 (중요!)
git diff --cached --stat
# archive/ 제거됨 확인
# dev_docs/ 제거됨 확인
# projects/ 제거됨 확인

# 5. 이상 없으면 커밋
git commit
```

### 4. 실패 안전 장치

```bash
# 각 명령어에 안전 장치
git rm -r archive/v1.x/ 2>/dev/null || true
#                        ^^^^^^^^^^^    ^^^^
#                        에러 숨김       실패해도 계속

# 이유:
# - 폴더가 이미 없을 수 있음
# - 한 폴더 실패해도 다른 폴더 계속 처리
# - 스크립트 중단 방지
```

### 5. 자동 검증

```bash
# 제외 후 자동 검증
echo "=== 검증 시작 ==="

# 제거되어야 할 폴더 확인
test -d archive && echo "❌ archive 아직 있음!" || echo "✅ archive 제거됨"
test -d dev_docs && echo "❌ dev_docs 아직 있음!" || echo "✅ dev_docs 제거됨"
test -d projects && echo "❌ projects 아직 있음!" || echo "✅ projects 제거됨"

# Git 상태 확인
echo ""
echo "=== Git 상태 ==="
git status --short | grep -E "(archive|dev_docs|projects)" && echo "⚠️  위 폴더들이 아직 존재" || echo "✅ 모든 제외 폴더 제거됨"

echo "=== 검증 완료 ==="
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
# - 버전 입력: v7.7.1
# - Push 확인: y
# - Tag 메시지: "v7.7.1: 문서 구조 개선"
```

### 고급 옵션 (수동 제어)

```bash
# 스크립트 없이 단계별 수동 (안전 로직 포함)
git checkout alpha
git pull origin alpha

git checkout main
git merge alpha --no-ff --no-commit

# 제외 작업 (간단 로직)
git rm -r archive/ dev_docs/ projects/ 2>/dev/null || true
git rm cursor_global_rules.txt .env.backup_* 2>/dev/null || true

# .gitignore 충돌 해결
git checkout --ours .gitignore 2>/dev/null || true
git add .gitignore

# 검증
test -d archive && echo "❌ archive 있음" || echo "✅ archive 제거"
test -d dev_docs && echo "❌ dev_docs 있음" || echo "✅ dev_docs 제거"

git commit  # 메시지 직접 작성
git push origin main

# Tag
git tag vX.X.X -m "..."
git push origin vX.X.X

git checkout alpha
```

### 완전 자동화 스크립트 (최신 ⭐)

```bash
#!/bin/bash
# scripts/deploy_to_main.sh

set -e  # 에러 시 중단

echo "=== UMIS Alpha → Main 배포 (안전 로직) ==="

# 1. Alpha 최신화
echo "1. Alpha 최신화..."
git checkout alpha
git pull origin alpha

# 2. Main 전환
echo "2. Main 전환..."
git checkout main
git pull origin main

# 3. 버전 입력
echo -n "배포 버전 (예: v7.7.1): "
read VERSION

# 4. Alpha merge (커밋 안 함)
echo "4. Alpha merge (--no-commit)..."
git merge alpha --no-ff --no-commit

# 5. 제외 작업 (간단 로직)
echo "5. 제외 작업..."

# 5-1. Archive 전체 제거
echo "  - archive 전체 제거..."
git rm -r archive/ 2>/dev/null || true

# 5-2. 개발 문서 제거
echo "  - dev_docs 제거..."
git rm -r dev_docs/ 2>/dev/null || true

# 5-3. 프로젝트 폴더 제거
echo "  - projects 제거..."
git rm -r projects/ 2>/dev/null || true

# 5-4. 개인 설정 제거
echo "  - 개인 설정 파일 제거..."
git rm cursor_global_rules.txt 2>/dev/null || true
git rm .env.backup_* 2>/dev/null || true

# 5-5. .gitignore 충돌 해결
echo "  - .gitignore 충돌 해결 (Main 버전 유지)..."
git checkout --ours .gitignore 2>/dev/null || true
git add .gitignore 2>/dev/null || true

# 6. 검증
echo "6. 검증..."
echo "=== 제거되어야 할 폴더 확인 ==="
test -d archive && echo "  ❌ archive 아직 있음!" || echo "  ✅ archive 제거됨"
test -d dev_docs && echo "  ❌ dev_docs 아직 있음!" || echo "  ✅ dev_docs 제거됨"
test -d projects && echo "  ❌ projects 아직 있음!" || echo "  ✅ projects 제거됨"

# 7. 상태 확인
echo ""
echo "=== Git 상태 ==="
git status --short | head -20

# 8. 커밋 확인
echo ""
echo -n "커밋하시겠습니까? (y/N): "
read CONFIRM
if [ "$CONFIRM" != "y" ]; then
    echo "배포 취소. (git merge --abort로 되돌리기)"
    exit 1
fi

# 9. 커밋
echo "9. 커밋..."
git commit -m "release: ${VERSION} - Production 배포

Alpha → Main merge 완료

제외된 폴더:
- archive/ (전체, 히스토리 보존용)
- dev_docs/ (개발 문서)
- projects/ (분석 프로젝트)

Main 브랜치: 순수 실행 코드만 포함
Alpha 브랜치: 전체 히스토리 보존
"

# 10. Push 확인
echo ""
echo -n "Main에 push하시겠습니까? (y/N): "
read PUSH_CONFIRM
if [ "$PUSH_CONFIRM" = "y" ]; then
    echo "10. Push..."
    git push origin main
    
    # 11. Tag
    echo -n "Tag 메시지: "
    read TAG_MSG
    git tag ${VERSION} -m "${TAG_MSG}"
    git push origin ${VERSION}
    
    echo "✅ 배포 완료!"
else
    echo "Push 보류됨. 수동으로: git push origin main"
fi

# 12. Alpha 복귀
echo "12. Alpha 복귀..."
git checkout alpha

echo ""
echo "=== 배포 완료 ==="
echo "Main: ${VERSION} 배포됨"
echo "Alpha: 작업 브랜치로 복귀"
```

**사용법**:
```bash
chmod +x scripts/deploy_to_main.sh
./scripts/deploy_to_main.sh
```

---

## 🎓 Best Practices

### 1. 항상 --no-commit 사용
```bash
# 이유: 수동 제외 작업 필요
git merge alpha --no-ff --no-commit
```

### 2. 검증 후 커밋
```bash
# 자동 커밋 ❌
git merge alpha

# 검증 후 커밋 ✅
git merge alpha --no-commit
# ... 제외 작업 ...
git status  # 확인
git commit  # 수동 커밋
```

### 3. 선택적 제거 (전체 제거 금지)
```bash
# 전체 제거 ❌
git rm -r archive/

# 선택적 제거 ✅
git rm -r archive/v1.x/ archive/v2.x/ ...
```

### 4. .gitignore 충돌 해결
```bash
# Main 버전 유지
git checkout --ours .gitignore
git add .gitignore
```

### 5. 자동 검증 추가
```bash
# 스크립트에 검증 로직 포함
test -d archive/deprecated_features || echo "ERROR!"
```

---

## 📊 브랜치별 Archive 구조

### Alpha 브랜치
```
archive/
├── deprecated_features/     # ⭐ Alpha만
│   ├── domain_reasoner/     # v7.5.0 제거
│   ├── tier_system/         # v7.7.0 제거
│   └── v7.4_and_earlier/
├── v7.2.0_and_earlier/      # ⭐ Alpha만
├── v1.x/                    # ⭐ Alpha만
├── v2.x/                    # ⭐ Alpha만
├── v3.x/                    # ⭐ Alpha만
├── v4.x/                    # ⭐ Alpha만
├── v5.x/                    # ⭐ Alpha만
├── v6.x/                    # ⭐ Alpha만
└── guestimation_v1_v2/      # ⭐ Alpha만
```

### Main 브랜치
```
# archive/ 폴더 없음 (전체 제외됨)
```

**차이점:**
- Alpha: 전체 히스토리 보존 (개발 참조용)
- Main: 순수 실행 코드만 (Production용)

---

## 🚨 트러블슈팅

### 문제 1: .gitignore 충돌

**증상**:
```
CONFLICT (content): Merge conflict in .gitignore
```

**해결**:
```bash
# Main 버전 선택 (archive 제외 규칙 유지)
git checkout --ours .gitignore
git add .gitignore
git commit
```

### 문제 2: Archive가 남아있음

**원인**:
```bash
# 명령 실패 또는 에러 무시
git rm -r archive/  # 실패했는데 눈치 못챔
```

**해결**:
```bash
# 수동 삭제 후 스테이징
rm -rf archive/
git add -A

# 또는 강제 제거
git rm -rf archive/
```

### 문제 3: 머지 후 커밋됨 (제외 불가)

**원인**:
```bash
# --no-commit 빠뜨림
git merge alpha --no-ff
```

**해결**:
```bash
# 마지막 커밋 취소
git reset --soft HEAD^

# 제외 작업 수행
git rm -r archive/v1.x/ ...

# 다시 커밋
git commit
```

### 문제 4: 스크립트 권한 오류

**증상**:
```
Permission denied: ./scripts/deploy_to_main.sh
```

**해결**:
```bash
chmod +x scripts/deploy_to_main.sh
```

---

## 📝 체크리스트

### 배포 전 (Alpha)
- [ ] 모든 테스트 통과
- [ ] CHANGELOG.md 업데이트
- [ ] VERSION.txt 확인
- [ ] Alpha push 완료

### 배포 중 (Main)
- [ ] `--no-commit`으로 merge
- [ ] **archive/ 전체 제거** ⭐
- [ ] dev_docs/ 제거
- [ ] projects/ 제거
- [ ] .gitignore 충돌 해결
- [ ] **archive 없는지 확인** ⭐ (`test -d archive`)
- [ ] git status 확인
- [ ] git diff --cached 확인

### 배포 후
- [ ] Main push 완료
- [ ] Tag 생성 및 push
- [ ] GitHub에서 확인
- [ ] Alpha 브랜치로 복귀
- [ ] 배포 노트 작성

---

**스크립트 위치**: `scripts/deploy_to_main.sh`  
**권한**: `chmod +x scripts/deploy_to_main.sh`  
**사용**: `./scripts/deploy_to_main.sh`  
**문의**: 문제 발생 시 이 가이드 참조

**마지막 업데이트**: 2024-11-20 (v7.7.1 archive 로직 추가)

