# 버전 업데이트 체크리스트

**목적**: 버전 업데이트 시 수정해야 할 모든 파일 및 문서 간 역할 정의  
**최종 업데이트**: 2025-11-03 (v7.0.0)

---

## 📚 핵심 문서 역할 (4개)

### 목적 및 업데이트 방식

| 문서 | 목적 | 대상 | 업데이트 시점 | 업데이트 내용 |
|------|------|------|-------------|--------------|
| **README.md** | 프로젝트 관문 (100줄) | 신규 방문자 | 메이저 변경 시 | 버전 번호, 주요 기능, 링크 |
| **UMIS_ARCHITECTURE_BLUEPRINT.md** | 전체 아키텍처 (Comprehensive) | 개발자/기여자 | 구조 변경 시 | 아키텍처, 개념, 설계, 마일스톤 |
| **CURRENT_STATUS.md** | 현재 상태 (200줄) | 개발자/테스터 | 기능 완성 시 | 완성 기능, 통계, 사용법 |
| **CHANGELOG.md** | 버전 이력 (1,000줄+) | 모든 사용자 | 모든 릴리즈 | 변경 사항, Breaking Changes |

### 각 문서의 고유 역할

#### README.md (프로젝트 관문)
- ✅ GitHub 첫 페이지
- ✅ 3분 내 UMIS 파악
- ✅ 빠른 시작 링크
- ❌ 상세 아키텍처 (→ BLUEPRINT)
- ❌ 버전 변경 이력 (→ CHANGELOG)

#### UMIS_ARCHITECTURE_BLUEPRINT.md (기술 설계도)
- ✅ 시스템 전체 구조 이해
- ✅ **Comprehensive** (최대한 상세)
- ✅ 3-Layer Architecture
- ✅ 5-Agent, 5-Layer RAG 상세
- ✅ Data Flow, Configuration
- ✅ Best Practices
- ❌ 설치 상세 (→ INSTALL.md)
- ❌ 버전 이력 상세 (→ CHANGELOG)

#### CURRENT_STATUS.md (현재 상태)
- ✅ 지금 뭐가 작동하는지
- ✅ 통계 및 테스트 결과
- ✅ 사용 방법 (코드 예시)
- ✅ 다음 단계 계획
- ❌ 아키텍처 설명 (→ BLUEPRINT)
- ❌ 과거 버전 (→ CHANGELOG)

#### CHANGELOG.md (버전 이력)
- ✅ 모든 버전 변경 사항
- ✅ Breaking Changes
- ✅ 날짜 및 상태
- ❌ 아키텍처 상세 (→ BLUEPRINT)
- ❌ 현재 상태 (→ CURRENT_STATUS)

---

## 📋 버전 업데이트 체크리스트

### Phase 1: 버전 번호 업데이트

#### 1.1 VERSION.txt
```bash
[ ] VERSION.txt
    현재: 7.0.0
    변경: 새 버전으로 (예: 7.1.0)
```

#### 1.2 핵심 YAML (6개) - 첫 줄 Compatible 명시
```bash
[ ] umis.yaml
    첫 줄: # UMIS guidelines - Compatible with v7.1.0

[ ] data/raw/umis_business_model_patterns.yaml
    첫 줄: # UMIS business_model_patterns - Compatible with v7.1.0

[ ] data/raw/umis_disruption_patterns.yaml
    첫 줄: # UMIS disruption_patterns - Compatible with v7.1.0

[ ] data/raw/umis_ai_guide.yaml
    첫 줄: # UMIS ai_guide - Compatible with v7.1.0

[ ] umis_deliverable_standards.yaml
    첫 줄: # UMIS deliverable_standards - Compatible with v7.1.0

[ ] umis_examples.yaml
    첫 줄: # UMIS examples - Compatible with v7.1.0
```

#### 1.3 Config YAML (5개)
```bash
[ ] config/schema_registry.yaml
    _meta.umis_version: "7.1.0"

[ ] config/overlay_layer.yaml
    _meta.version: (필요시)

[ ] config/routing_policy.yaml
    _meta.version: (필요시)

[ ] config/runtime.yaml
    version: (필요시)

[ ] config/projection_rules.yaml
    _meta.version: (필요시)
```

#### 1.4 Cursor Rules
```bash
[ ] .cursorrules
    Line 3: # v7.1.0 | Non-coder | Cursor-only
    Line 10: version: 7.1.0
```

---

### Phase 2: 문서 업데이트

#### 2.1 README.md (프로젝트 관문)
```bash
[ ] 버전 배지
    Line 4: [![Version](https://img.shields.io/badge/version-7.1.0-green)]

[ ] 버전 정보
    Line 7: **버전:** 7.1.0

[ ] 주요 기능 (메이저 변경 시만)
    v7.0.0 주요 기능 → v7.1.0 주요 기능
```

**업데이트 빈도**: 메이저/마이너 릴리즈 시

#### 2.2 UMIS_ARCHITECTURE_BLUEPRINT.md (Comprehensive 아키텍처)
```bash
[ ] Version Info 테이블
    Line 10: | **UMIS Version** | v7.1.0 |
    Line 13: | **Last Updated** | YYYY-MM-DD |

[ ] Version History 섹션
    주요 마일스톤 업데이트:
    - v7.1.0: (새 기능 요약)
    - v7.0.0: RAG v3.0 완전 통합, ...

[ ] System Architecture (구조 변경 시만)
    다이어그램, 레이어, 플로우 업데이트

[ ] Core Concepts (새 개념 추가 시만)
    새 Agent, Layer, ID Prefix 등

[ ] Component Map (폴더/파일 변경 시만)
    폴더 구조, 파일 경로 업데이트

[ ] Configuration (설정 변경 시만)
    runtime_config, routing_policy 등

[ ] Maintenance
    Line: Next Review: v7.2.0 예상
```

**업데이트 빈도**: 모든 릴리즈 (구조 변경 시 상세 업데이트)

#### 2.3 CURRENT_STATUS.md (현재 상태)
```bash
[ ] 버전 및 날짜
    Line 3: **버전**: v7.1.0
    Line 4: **마지막 업데이트**: YYYY-MM-DD

[ ] 완성된 기능 (기능 추가 시)
    새 기능 추가, 상태 업데이트

[ ] 현재 통계 (주기적)
    파일 수, 데이터 수, 테스트 결과

[ ] 다음 단계 (항상)
    v7.2.0 계획 업데이트
```

**업데이트 빈도**: 모든 릴리즈 (기능 완성/통계 변경 시)

#### 2.4 CHANGELOG.md (버전 이력)
```bash
[ ] 새 버전 섹션 추가 (최상단)
    ## v7.1.0 (YYYY-MM-DD) - [Release Name]
    
    ### 주요 기능 추가
    - ...
    
    ### 변경사항
    - ...
    
    ### Breaking Changes (있는 경우)
    - ...
```

**업데이트 빈도**: 모든 릴리즈 (필수!)

#### 2.5 INSTALL.md
```bash
[ ] 버전 번호 (필요 시)
    설치 명령어 변경 시만
```

**업데이트 빈도**: 설치 프로세스 변경 시만

#### 2.6 FOLDER_STRUCTURE.md
```bash
[ ] 폴더 구조 (폴더 변경 시만)
    새 폴더 추가/제거/이동 반영

[ ] 정리 히스토리
    주요 구조 변경 기록
```

**업데이트 빈도**: 폴더 구조 변경 시만

---

### Phase 3: Setup 파일

#### 3.1 setup/setup.py
```bash
[ ] 버전 확인 로직 (필요 시)
    print_header("UMIS v7.1.0 자동 설치")
```

#### 3.2 setup/ 문서들
```bash
[ ] setup/SETUP.md
    **버전**: v7.1.0 (필요 시)

[ ] setup/START_HERE.md
    **버전**: v7.1.0 (필요 시)

[ ] setup/AI_SETUP_GUIDE.md
    UMIS v7.1.0 표기 (필요 시)
```

**업데이트 빈도**: 설치 프로세스 변경 시만

---

### Phase 4: 스키마 및 설정 (선택적)

#### 4.1 config/schema_registry.yaml
```bash
[ ] _meta 섹션
    umis_version: "7.1.0"
    last_updated: "YYYY-MM-DD"
```

**업데이트 빈도**: 스키마 변경 시만

#### 4.2 config 파일들
```bash
[ ] config/overlay_layer.yaml (_meta.version)
[ ] config/routing_policy.yaml (_meta.version)
[ ] config/runtime.yaml (version)
[ ] config/projection_rules.yaml (_meta.version)
```

**업데이트 빈도**: 설정 변경 시만

---

## 🔄 버전별 업데이트 범위

### Patch (v7.0.1)
**범위**: 버그 수정, 작은 개선

**필수 업데이트**:
- [ ] VERSION.txt
- [ ] CHANGELOG.md (Patch 섹션 추가)

**선택 업데이트**:
- [ ] CURRENT_STATUS.md (버그 수정 반영)

### Minor (v7.1.0)
**범위**: 새 기능 추가, 중요한 개선

**필수 업데이트**:
- [ ] VERSION.txt
- [ ] 모든 YAML 첫 줄 (6개)
- [ ] .cursorrules (버전)
- [ ] README.md (버전 배지, 주요 기능)
- [ ] UMIS_ARCHITECTURE_BLUEPRINT.md (Version Info, 마일스톤)
- [ ] CURRENT_STATUS.md (완성 기능, 다음 단계)
- [ ] CHANGELOG.md (Minor 섹션 상세)

**선택 업데이트**:
- [ ] config/schema_registry.yaml (_meta)
- [ ] config 파일들 (_meta)
- [ ] Component Map (기능 추가 시)

### Major (v8.0.0)
**범위**: 구조적 변경, 철학적 전환, Breaking Changes

**필수 업데이트**:
- [ ] 모든 Phase 1-2 항목
- [ ] UMIS_ARCHITECTURE_BLUEPRINT.md
  - System Architecture (다이어그램)
  - Core Concepts (새 개념)
  - Component Map (구조 변경)
  - Configuration (설정 변경)
- [ ] FOLDER_STRUCTURE.md (구조 변경 시)
- [ ] MAIN_BRANCH_SETUP.md (브랜치 정책 변경 시)
- [ ] config/schema_registry.yaml (스키마 변경)
- [ ] 모든 config 파일 (정책 변경)

**선택 업데이트**:
- [ ] deliverable_specs/ (산출물 변경 시)
- [ ] umis_deliverable_standards.yaml (표준 변경 시)

---

## 🤖 자동화 스크립트

### update_version.sh

```bash
#!/bin/bash
# 버전 자동 업데이트 스크립트
# 사용법: ./update_version.sh 7.1.0

NEW_VERSION=$1

if [ -z "$NEW_VERSION" ]; then
  echo "❌ 사용법: ./update_version.sh 7.1.0"
  exit 1
fi

echo "🔄 버전 v$NEW_VERSION 으로 업데이트 중..."
echo ""

# 1. VERSION.txt
echo "$NEW_VERSION" > VERSION.txt
echo "✅ VERSION.txt → $NEW_VERSION"

# 2. 핵심 YAML (6개)
for file in umis.yaml umis_deliverable_standards.yaml umis_examples.yaml; do
  if [ -f "$file" ]; then
    sed -i '' "1s/Compatible with v[0-9.]*-*[a-z]*/Compatible with v$NEW_VERSION/" "$file"
    echo "✅ $file (첫 줄)"
  fi
done

# 3. data/raw/ YAML
for file in data/raw/umis_*.yaml; do
  if [ -f "$file" ]; then
    sed -i '' "1s/Compatible with v[0-9.]*-*[a-z]*/Compatible with v$NEW_VERSION/" "$file"
    echo "✅ $file (첫 줄)"
  fi
done

# 4. .cursorrules
sed -i '' "3s/# v[0-9.]*-*[a-z]*/# v$NEW_VERSION/" .cursorrules
sed -i '' "10s/version: [0-9.]*-*[a-z]*/version: $NEW_VERSION/" .cursorrules
echo "✅ .cursorrules"

# 5. README.md
sed -i '' "s/version-[0-9.]*-*[a-z]*-/version-$NEW_VERSION-/" README.md
sed -i '' "s/\*\*버전:\*\* [0-9.]*-*[a-z]*/\*\*버전:\*\* $NEW_VERSION/" README.md
echo "✅ README.md"

# 6. UMIS_ARCHITECTURE_BLUEPRINT.md
sed -i '' "s/| \*\*UMIS Version\*\* | v[0-9.]*-*[a-z]* |/| **UMIS Version** | v$NEW_VERSION |/" UMIS_ARCHITECTURE_BLUEPRINT.md
sed -i '' "s/| \*\*Last Updated\*\* | [0-9-]* |/| **Last Updated** | $(date +%Y-%m-%d) |/" UMIS_ARCHITECTURE_BLUEPRINT.md
echo "✅ UMIS_ARCHITECTURE_BLUEPRINT.md"

# 7. CURRENT_STATUS.md
sed -i '' "s/\*\*버전\*\*: v[0-9.]*-*[a-z]*/\*\*버전\*\*: v$NEW_VERSION/" CURRENT_STATUS.md
sed -i '' "s/\*\*마지막 업데이트\*\*: [0-9-]*/\*\*마지막 업데이트\*\*: $(date +%Y-%m-%d)/" CURRENT_STATUS.md
echo "✅ CURRENT_STATUS.md"

# 8. config/schema_registry.yaml
sed -i '' "s/umis_version: \"[0-9.]*-*[a-z]*\"/umis_version: \"$NEW_VERSION\"/" config/schema_registry.yaml
echo "✅ config/schema_registry.yaml"

echo ""
echo "✅ 자동 업데이트 완료!"
echo ""
echo "📝 다음 단계 (수동):"
echo "  1. CHANGELOG.md 새 섹션 추가"
echo "  2. UMIS_ARCHITECTURE_BLUEPRINT.md 마일스톤 업데이트"
echo "  3. CURRENT_STATUS.md 완성 기능/다음 단계 업데이트"
echo "  4. 테스트 실행"
echo "  5. git commit & tag"
echo ""
echo "📋 체크리스트:"
echo "  python scripts/02_build_index.py --agent explorer  # RAG 작동 확인"
echo "  python tests/test_schema_contract.py              # 스키마 확인"
echo "  git commit -am 'release: v$NEW_VERSION'"
echo "  git tag v$NEW_VERSION"
echo "  git push origin alpha --tags"
```

**실행**:
```bash
chmod +x update_version.sh
./update_version.sh 7.1.0
```

---

## 📝 수동 업데이트 (중요!)

### 1. CHANGELOG.md (필수!)

최상단에 새 섹션 추가:

```markdown
## v7.1.0 (YYYY-MM-DD) - [Release Name]

### 🚀 주요 기능 추가
- Meta-RAG 구현
- System Knowledge RAG
- ...

### 🔄 변경사항
- ...

### ⚠️ Breaking Changes (있는 경우)
- ...

### 📊 통계
- 코드: +XXX줄
- 파일: 신규 XX개
```

---

### 2. UMIS_ARCHITECTURE_BLUEPRINT.md

#### Version History 섹션
```markdown
**현재 버전**: v7.1.0 (YYYY-MM-DD) - Stable Release

**주요 마일스톤**:
- v7.1.0: Meta-RAG 구현, System Knowledge
- v7.0.0: RAG v3.0 완전 통합, 5-Agent 안정화
- ...
```

#### 구조 변경 시
- [ ] System Architecture 다이어그램
- [ ] Core Concepts (새 Agent, Layer, ID Prefix)
- [ ] Component Map (폴더/파일 변경)
- [ ] Configuration (설정 변경)

---

### 3. CURRENT_STATUS.md

#### 완성된 기능
```markdown
### X. 새 기능 이름

상태: ✅ 완전 작동
...
```

#### 다음 단계
```markdown
### vX.X.0 계획

Meta-RAG 구현 완료 → 다음 목표로 변경
```

---

## 🎯 버전 릴리즈 프로세스 (전체)

### Step 1: 개발 완료 확인
```bash
# 테스트 전체 통과
python tests/test_schema_contract.py
python scripts/03_test_search.py

# Linter 확인
# 기능 확인
```

### Step 2: 자동 스크립트 실행
```bash
./update_version.sh 7.1.0
```

### Step 3: 수동 문서 작성
```bash
# CHANGELOG.md 작성
# BLUEPRINT 마일스톤 추가
# CURRENT_STATUS 업데이트
```

### Step 4: 최종 확인
```bash
# 버전 번호 일관성
grep -r "7.0.0" . --include="*.md" --include="*.yaml" --include="*.txt"

# config 파일 확인
cat VERSION.txt
head -1 umis.yaml
grep umis_version config/schema_registry.yaml
```

### Step 5: Git 커밋 & 태그
```bash
git add .
git commit -m "release: v7.1.0 - [Release Name]"
git tag v7.1.0
git push origin alpha --tags
```

### Step 6: GitHub Release
```
- Tag: v7.1.0
- Title: UMIS v7.1.0 - [Release Name]
- Description: CHANGELOG.md에서 복사
```

---

## 📋 릴리즈 체크리스트 (최종)

### Before Release
- [ ] 모든 테스트 통과
- [ ] Linter 에러 0개
- [ ] VERSION.txt 업데이트
- [ ] 모든 YAML 호환 버전 업데이트
- [ ] .cursorrules 업데이트
- [ ] 3개 핵심 문서 업데이트 (README, BLUEPRINT, CURRENT_STATUS)
- [ ] CHANGELOG.md 작성
- [ ] Breaking Changes 명시
- [ ] Migration Guide (필요 시)

### Release
- [ ] Git commit
- [ ] Git tag vX.X.X
- [ ] Push to origin (alpha)
- [ ] GitHub Release 생성
- [ ] Release Notes 작성

### After Release
- [ ] main 브랜치 업데이트 (릴리즈 시)
  - .gitignore 추가 (archive/, dev_docs/)
  - 선택적 병합
- [ ] 문서 사이트 업데이트 (향후)
- [ ] 사용자 공지

---

## 🗂️ 폴더별 업데이트 정책

| 폴더 | 버전 업데이트 | 비고 |
|------|-------------|------|
| `setup/` | 설치 변경 시만 | |
| `umis_rag/` | 코드 변경 시 | 버전 번호 불필요 |
| `scripts/` | 스크립트 변경 시 | 버전 번호 불필요 |
| `data/raw/` | YAML 첫 줄 | 자동 스크립트 |
| `docs/` | 프로토콜 변경 시만 | |
| `dev_docs/` | 개발 문서 (독립적) | 날짜만 포함 |
| `projects/` | Git 제외 | 버전 무관 |
| `deliverable_specs/` | 스펙 변경 시만 | |
| `archive/` | 추가만 (수정 없음) | |

---

## 📌 특별 고려사항

### Config 파일 리네이밍 (v7.1.0 예정)
```bash
# 계획
config/overlay_layer.yaml → config/overlay_layer.yaml
config/routing_policy.yaml → config/routing_policy.yaml
config/runtime.yaml → config/runtime.yaml
config/projection_rules.yaml → config/projection_rules.yaml
config/schema_registry.yaml → config_config/schema_registry.yaml

# 하위 호환 (심볼릭 링크)
ln -s config/overlay_layer.yaml config/overlay_layer.yaml
...

# 이 체크리스트도 업데이트 필요!
```

### 문서 간 일관성

**단일 진실 원천**:
- VERSION.txt: 버전 번호
- CHANGELOG.md: 변경 이력
- BLUEPRINT: 아키텍처
- CURRENT_STATUS: 현재 상태

**파생 정보**:
- README.md: VERSION.txt 참조
- setup/: VERSION.txt 참조
- 기타 문서: 해당 원천 참조

---

## 🎓 Best Practices

### 1. 버전 번호 일관성
```bash
# 릴리즈 전 확인
./check_version_consistency.sh

# 또는 수동
grep -r "v7.0.0" . --include="*.md" --include="*.yaml"
```

### 2. Breaking Changes 명시
```markdown
CHANGELOG.md:
  ### ⚠️ Breaking Changes
  - API 변경 사항
  - 스키마 변경 사항
  - Migration 방법
```

### 3. 문서 간 링크 확인
```bash
# Markdown 링크 체크
find . -name "*.md" -exec grep -l "\[.*\](.*/.*)" {} \;
```

### 4. 테스트 자동화
```bash
# 릴리즈 전 필수 테스트
python scripts/02_build_index.py --agent explorer
python tests/test_schema_contract.py
python scripts/03_test_search.py
```

---

## 🔧 도구

### check_version_consistency.sh (향후 작성)
```bash
#!/bin/bash
# 모든 파일의 버전 번호 일관성 확인

VERSION=$(cat VERSION.txt)
echo "✅ VERSION.txt: $VERSION"

# 각 파일 확인 및 불일치 리포트
...
```

### update_all_docs.sh (향후 작성)
```bash
#!/bin/bash
# 버전 업데이트 후 모든 문서 자동 업데이트

# CHANGELOG.md 템플릿 생성
# BLUEPRINT 마일스톤 추가
# CURRENT_STATUS 다음 단계 업데이트
...
```

---

## 📖 참고 문서

- **[UMIS_ARCHITECTURE_BLUEPRINT.md](UMIS_ARCHITECTURE_BLUEPRINT.md)** - Maintenance 섹션
- **[DOCUMENT_CONSOLIDATION_PLAN.md](DOCUMENT_CONSOLIDATION_PLAN.md)** - 문서 역할 정의
- **[FOLDER_STRUCTURE.md](FOLDER_STRUCTURE.md)** - 폴더 구조 및 정책

---

**이 문서 자체도 버전 업데이트 시 확인하세요!**  
**마지막 업데이트**: 2025-11-03 (v7.0.0)
