#!/bin/bash
# UMIS Alpha → Main 배포 스크립트
# 자동으로 projects/, archive/, dev_docs/ 제외

set -e  # 에러 시 중단

echo "======================================"
echo "UMIS Alpha → Main 배포 스크립트"
echo "======================================"
echo ""

# 현재 브랜치 확인
CURRENT_BRANCH=$(git branch --show-current)
echo "현재 브랜치: $CURRENT_BRANCH"

if [ "$CURRENT_BRANCH" != "alpha" ]; then
    echo "❌ 오류: alpha 브랜치에서 실행해야 합니다."
    echo "   현재: $CURRENT_BRANCH"
    exit 1
fi

echo ""
echo "Step 1: Alpha 최신 상태 확인"
git pull origin alpha
echo "✅ Alpha 업데이트 완료"

echo ""
echo "Step 2: Main 브랜치로 전환"
git checkout main
git pull origin main
echo "✅ Main 업데이트 완료"

echo ""
echo "Step 3: Alpha merge"
# merge만 하고 커밋은 아직 안 함
git merge alpha --no-ff --no-commit
echo "✅ Merge 완료 (커밋 전)"

echo ""
echo "Step 4: 제외 폴더/파일 삭제"
echo "  - projects/"
echo "  - archive/"
echo "  - dev_docs/"
echo "  - cursor_global_rules.txt"
echo "  - .env.backup_*"

# 존재하는 폴더만 삭제
if [ -d "projects" ]; then
    git rm -r projects/ 2>/dev/null || true
    echo "  ✅ projects/ 제거"
fi

if [ -d "archive" ]; then
    git rm -r archive/ 2>/dev/null || true
    echo "  ✅ archive/ 제거"
fi

if [ -d "dev_docs" ]; then
    git rm -r dev_docs/ 2>/dev/null || true
    echo "  ✅ dev_docs/ 제거"
fi

# 개인 설정 파일 제거
if [ -f "cursor_global_rules.txt" ]; then
    git rm cursor_global_rules.txt 2>/dev/null || true
    echo "  ✅ cursor_global_rules.txt 제거"
fi

# 환경변수 백업 파일 제거
git rm .env.backup_* 2>/dev/null || true
echo "  ✅ .env.backup_* 제거 (있다면)"

echo ""
echo "Step 5: 커밋 메시지 입력"
echo "버전을 입력하세요 (예: v7.3.2):"
read VERSION

if [ -z "$VERSION" ]; then
    echo "❌ 버전을 입력해야 합니다."
    git merge --abort
    git checkout alpha
    exit 1
fi

# 커밋
git commit -m "release: $VERSION - Production 배포

Alpha → Main merge 완료

제외:
- projects/ (Alpha only)
- archive/ (Alpha only)
- dev_docs/ (Alpha only)
- cursor_global_rules.txt (개인 설정)
- .env.backup_* (환경변수 백업)

Main: Production 코드만
Release Notes: docs/release_notes/RELEASE_NOTES_$VERSION.md"

echo "✅ 커밋 완료"

echo ""
echo "Step 6: Main push (확인 필요)"
echo "Main에 push하시겠습니까? (y/n):"
read CONFIRM

if [ "$CONFIRM" = "y" ] || [ "$CONFIRM" = "Y" ]; then
    git push origin main
    echo "✅ Main push 완료"
    
    # Tag 생성
    echo ""
    echo "Step 7: Tag 생성"
    echo "Tag 메시지:"
    read TAG_MSG
    
    git tag $VERSION -m "$TAG_MSG"
    git push origin $VERSION
    echo "✅ Tag $VERSION 생성 완료"
else
    echo "⚠️  Push 취소"
    echo "   수동으로 push: git push origin main"
fi

echo ""
echo "Step 8: Alpha로 복귀"
git checkout alpha
echo "✅ Alpha 브랜치로 복귀"

echo ""
echo "======================================"
echo "✅ 배포 완료!"
echo "======================================"
echo ""
echo "Main: $VERSION"
echo "Alpha: $(git rev-parse --short HEAD)"
echo ""
echo "확인: https://github.com/kangminlee-maker/umis"

