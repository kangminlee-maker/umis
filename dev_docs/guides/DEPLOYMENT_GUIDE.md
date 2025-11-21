# UMIS 배포 가이드 (v7.8.0 업데이트)

**목적**: Alpha → Main 단방향 배포 (독립 운영)  
**대상 폴더**: projects/, archive/, dev_docs/  
**업데이트**: 2025-11-12 (v7.8.0 배포 전략 명확화)

---

## 🎯 **브랜치 전략 (v7.8.0)**

### **핵심 원칙**

```yaml
Alpha 브랜치 (개발):
  역할: 모든 개발 작업 및 히스토리 보관
  포함:
    - 코드 (umis_rag/, scripts/, config/)
    - 문서 (docs/, setup/)
    - 개발 문서 (dev_docs/ 52개 파일)
    - 아카이브 (archive/ 전체)
    - 프로젝트 (projects/)
  
  Main 연동: 단방향 (Alpha → Main만)
  Main에서 가져오기: ❌ 절대 안 함 (역류 시 문서 삭제)

Main 브랜치 (배포):
  역할: Production 코드만
  포함:
    - 코드 (umis_rag/, scripts/, config/)
    - 문서 (docs/, setup/)
  
  제외:
    - dev_docs/ (개발 문서)
    - archive/ (deprecated)
    - projects/ (실험)
  
  Alpha 연동: 단방향 (Alpha에서만 받음)
  Alpha로 보내기: ❌ 절대 안 함 (정리 내용이 역류)
```

### **⚠️ 중요: Main → Alpha 머지 금지**

```bash
# ❌ 절대 실행 금지!
git checkout alpha
git merge origin/main  # 이렇게 하면 dev_docs/ 등이 삭제됨!

# 실제 발생한 문제:
# - Main에 없는 dev_docs/ 152개 파일 삭제
# - archive/ 폴더 완전 삭제
# - 80,484줄 손실
```

**복구 방법** (이미 실행한 경우):
```bash
# 머지 이전으로 되돌리기
git reset --hard HEAD~1  # 또는 커밋 ID
git push origin alpha --force-with-lease
```

---

## 🚀 **배포 방법 (v7.8.0)**

### **방법 1: Cherry-pick 배포 (권장 ⭐)**

Alpha의 특정 커밋만 Main에 선택적으로 적용:

```bash
# 1. Alpha에서 배포할 커밋 확인
git checkout alpha
git log --oneline -10

# 예: 60866c7 feat(estimator): Phase 3 Source 재설계

# 2. Main으로 전환
git checkout main
git pull origin main

# 3. 특정 커밋만 cherry-pick
git cherry-pick 60866c7

# 이때 자동으로 필터링:
# - 코드 변경만 적용
# - dev_docs/, archive/ 변경은 자동 스킵 (Main에 없으므로)

# 4. 확인
git status
git diff --stat HEAD~1

# 5. Push
git push origin main

# 6. Tag
git tag v7.8.0 -m "v7.8.0: Phase 3 Source 재설계"
git push origin v7.8.0

# 7. Alpha 복귀
git checkout alpha
```

**장점**:
- ✅ 정확한 제어 (원하는 커밋만)
- ✅ dev_docs/ 자동 스킵 (Main에 없으므로)
- ✅ 안전 (역류 없음)

---

### **방법 2: 전체 Merge + 수동 정리 (신중)**

```bash
# ⚠️ 주의: dev_docs/ 등이 이미 Main에서 삭제된 경우만 사용

# 1. Main에서
git checkout main
git pull origin main

# 2. Alpha 전체 merge
git merge alpha --no-ff --no-commit

# 3. 혹시 모를 개발 문서 제거
git rm -r projects/ 2>/dev/null || true
git rm -r archive/ 2>/dev/null || true
git rm -r dev_docs/v7.5.0_development/ 2>/dev/null || true
git rm -r dev_docs/v7.6.2_development/ 2>/dev/null || true
git rm -r dev_docs/guestimation_v3/ 2>/dev/null || true

# 4. 확인
git status

# 5. 커밋
git commit -m "release: v7.8.0 - Phase 3 Source 재설계 및 Web 크롤링"

# 6. Push
git push origin main

# 7. Tag
git tag v7.8.0
git push origin v7.8.0

# 8. Alpha 복귀
git checkout alpha
```

---

### **방법 3: 자동 스크립트 (TODO)**

```bash
# 향후 구현 예정
./scripts/deploy_to_main.sh
```

---

## 📋 제외 규칙

### Main 브랜치에서 제외

```yaml
제외 폴더:
  - projects/: 분석 프로젝트 (실험적)
  - archive/: deprecated 코드/문서
  - dev_docs/: 설계 문서, 세션 요약

이유:
  - Main: Production 코드만
  - Alpha: 전체 히스토리

효과:
  - Main 초간결
  - Alpha 완전 보존
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

## ⚠️ **주의사항 (v7.8.0 중요!)**

### **1. Main → Alpha 머지 절대 금지** ⚠️⚠️⚠️

```bash
# ❌ 절대 실행 금지!
git checkout alpha
git merge origin/main
# 또는
git rebase origin/main

# 결과:
# → dev_docs/ 152개 파일 삭제 (80,484줄 손실)
# → archive/ 폴더 완전 삭제
# → projects/ 삭제
```

**이유**:
- Main은 이미 정리됨 (dev_docs/ 등 삭제)
- Alpha로 Main 머지 시 → Main의 "삭제" 내용이 Alpha에 적용
- 개발 히스토리 손실

**만약 실수로 실행했다면**:
```bash
# 즉시 복구
git reflog
git reset --hard HEAD@{1}  # 머지 이전으로
git push origin alpha --force-with-lease
```

### **2. 단방향 워크플로우 준수**

```yaml
올바른 흐름:
  Alpha (개발) → Main (배포) ✅
  
금지:
  Main → Alpha ❌
  
이유:
  - Alpha: 모든 것 보관 (개발 문서 포함)
  - Main: Production만 (정리된 상태)
  - Main → Alpha 시 정리 내용이 역류
```

### **3. Cherry-pick vs Merge**

```yaml
Cherry-pick (권장):
  - 특정 커밋만 선택
  - 개발 문서 자동 스킵
  - 안전함

Merge:
  - 전체 머지
  - 수동 정리 필요
  - 주의 필요
```

### **4. 커밋 메시지**

```yaml
형식:
  release: vX.X.X - [주요 기능]
  
  Alpha → Main cherry-pick
  
  Commits:
  - 60866c7: Phase 3 Source 재설계
  
  제외 (자동):
  - dev_docs/ (Main에 없음)
  - archive/ (Main에 없음)

예:
  release: v7.8.0 - Phase 3 Source 재설계 및 Web 크롤링
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

## 📚 **FAQ (v7.8.0 업데이트)**

### **Q: Alpha와 Main이 54개 커밋 차이나는데 괜찮나?**

```
A: 완전히 정상입니다! ✅

이유:
- Main의 54개 커밋 = 대부분 "Merge alpha" 머지 커밋
- 실제 코드는 Alpha에 이미 있음
- Alpha는 개발 브랜치 (Main 머지 필요 없음)

결론:
- Alpha를 Main에 동기화하면 안 됨 (문서 삭제됨)
- 독립 운영이 정상
```

### **Q: 왜 Main → Alpha 머지 금지?**

```
A: 개발 문서 손실 방지

Main 상태:
- dev_docs/ 삭제됨 (21개만 유지)
- archive/ 삭제됨
- projects/ 삭제됨

Alpha로 Main 머지 시:
→ Main의 "삭제" 내용이 Alpha에 적용
→ dev_docs/ 152개 파일 손실 (80,484줄)
→ 개발 히스토리 영구 손실 ⚠️

해결책:
- Alpha는 Main과 독립
- Alpha → Main만 (단방향)
```

### **Q: 왜 projects/를 제외?**

```
A: 실험적 분석 프로젝트
   - 개발 중이거나 완료되지 않은 프로젝트
   - Main은 안정된 코드만
```

### **Q: archive/는?**

```
A: Deprecated 코드/문서
   - v1.0, v2.1 등 과거 버전
   - Main에 불필요
   - Alpha에서 히스토리 보존
```

### **Q: dev_docs/는?**

```
A: 개발 문서 (52개 파일)
   - Alpha: 52개 (전체 히스토리)
   - Main: 21개 (최신 필수만)
   
   Alpha 전용 (31개):
   - v7.5.0_development/ (25개)
   - v7.6.2_development/ (29개)
   - guestimation_v3/ (20개)
   - analysis/, reports/, fermi/
```

### **Q: Cherry-pick이 안전한 이유?**

```
A: Main에 없는 파일은 자동 스킵

Cherry-pick 동작:
1. Alpha 커밋 가져오기
2. Main에 적용 시도
3. Main에 없는 파일 (dev_docs/) → 무시
4. Main에 있는 파일만 적용

결과:
- 코드만 깔끔하게 적용
- 개발 문서 충돌 없음
```

---

## 🛠️ **현재 상태 (v7.8.0)**

### **브랜치 현황**

```bash
Alpha (origin/alpha):
  커밋: 60866c7
  상태: 개발 문서 전체 보존 ✅
  파일: dev_docs/ 52개, archive/ 전체

Main (origin/main):
  커밋: 69d5321
  상태: Production 정리 완료 ✅
  파일: dev_docs/ 21개 (최신만)

차이: 54개 커밋 (정상, 머지 커밋들)
```

### **v7.8.0 배포 예정**

```bash
# 현재 Alpha에만 있는 커밋
60866c7 feat(estimator): Phase 3 Source 재설계 및 Web 크롤링 (v7.8.0)

# Main에 배포할 내용:
- AIAugmentedEstimationSource (LLM + Web 통합)
- Web 크롤링 기능
- Physical/Soft Constraints 재설계
- Soft 경고 시스템

# 제외할 내용:
- dev_docs/ 신규 3개 (Alpha만 보관)
- archive/ (이미 Main에 없음)
```

---

## 📋 **배포 체크리스트 (v7.8.0)**

### **배포 전 확인**

```yaml
✅ Alpha 테스트 완료
   - test_source_consolidation.py 통과
   - AIAugmented instruction 생성 확인
   - Physical/Soft 제약 작동 확인

✅ 문서 업데이트
   - CHANGELOG.md (v7.8.0)
   - setup/ 파일들 (v7.8.0)
   - 가이드 문서 추가

✅ Alpha 커밋 정리
   - 60866c7: 최종 커밋
   - 테스트 통과
```

### **배포 실행 (Cherry-pick 권장)**

```bash
# 1. Main 전환
git checkout main
git pull origin main

# 2. Alpha 커밋 적용
git cherry-pick 60866c7

# 3. 확인 (dev_docs/ 변경 제외되었는지)
git status
git diff --stat HEAD~1

# 4. Push
git push origin main

# 5. Tag
git tag v7.8.0 -m "v7.8.0: Phase 3 Source 재설계 및 Web 크롤링"
git push origin v7.8.0

# 6. Alpha 복귀
git checkout alpha
```

### **배포 후 확인**

```yaml
✅ Main push 성공
✅ Tag 생성 확인
✅ GitHub에서 코드 확인
✅ Alpha 개발 문서 보존 확인
   - dev_docs/ 52개 유지
   - archive/ 유지
```

---

## 🎯 **핵심 원칙 (다시 한 번)**

```yaml
절대 원칙:
  1. Alpha → Main ✅ (단방향)
  2. Main → Alpha ❌ (절대 금지)
  3. Cherry-pick 권장 (안전)
  4. Alpha 독립 운영 (개발 문서 보관)

브랜치 역할:
  Alpha: 모든 개발 작업 + 히스토리
  Main: Production 코드만

배포 방법:
  Cherry-pick (특정 커밋만)
```

---

**배포 스크립트**: TODO (향후 구현)  
**현재 방법**: Cherry-pick 수동 배포  
**업데이트**: 2025-11-12 (v7.8.0)

