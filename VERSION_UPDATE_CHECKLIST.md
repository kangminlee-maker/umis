# 버전 업데이트 체크리스트

**목적:** 버전 업데이트 시 수정해야 할 모든 파일 목록

---

## 📋 필수 업데이트 파일

### 1. 버전 파일

```
[ ] VERSION.txt
    현재: 7.0.0
    변경: 새 버전으로
```

### 2. YAML 파일 첫 줄 (6개)

```
[ ] umis_guidelines.yaml
    첫 줄: # UMIS guidelines - Compatible with v7.0.0
    
[ ] umis_business_model_patterns.yaml
    첫 줄: # UMIS business_model_patterns - Compatible with v7.0.0
    
[ ] umis_disruption_patterns.yaml
    첫 줄: # UMIS disruption_patterns - Compatible with v7.0.0
    
[ ] umis_ai_guide.yaml
    첫 줄: # UMIS ai_guide - Compatible with v7.0.0
    
[ ] umis_deliverable_standards.yaml
    첫 줄: # UMIS deliverable_standards - Compatible with v7.0.0
    
[ ] umis_examples.yaml
    첫 줄: # UMIS examples - Compatible with v7.0.0
```

### 3. 문서 파일

```
[ ] README.md
    **버전:** 7.0.0
    
[ ] rag/README.md
    **버전:** 7.0.0
    
[ ] CHANGELOG.md
    새 섹션 추가: ## vX.X.X (YYYY-MM-DD)
```

### 4. data/raw/ (YAML 복사본)

```
[ ] data/raw/umis_guidelines.yaml (첫 줄)
[ ] data/raw/umis_business_model_patterns.yaml (첫 줄)
[ ] data/raw/umis_disruption_patterns.yaml (첫 줄)
```

---

## 🔄 자동 스크립트

```bash
#!/bin/bash
# update_version.sh NEW_VERSION

NEW_VERSION=$1

if [ -z "$NEW_VERSION" ]; then
  echo "사용법: ./update_version.sh 6.3.1"
  exit 1
fi

echo "버전 $NEW_VERSION 으로 업데이트 중..."

# VERSION.txt
echo "$NEW_VERSION" > VERSION.txt

# YAML 파일들
for file in umis_*.yaml; do
  sed -i '' "1s/v[0-9.]*-*[a-z]*/v$NEW_VERSION/" "$file"
done

# data/raw/
if [ -d "data/raw" ]; then
  cd data/raw
  for file in umis_*.yaml; do
    sed -i '' "1s/v[0-9.]*-*[a-z]*/v$NEW_VERSION/" "$file"
  done
  cd ../..
fi

# README 파일들
sed -i '' "s/\*\*버전:\*\* [0-9.]*-*[a-z]*/\*\*버전:\*\* $NEW_VERSION/" README.md
sed -i '' "s/\*\*버전:\*\* [0-9.]*-*[a-z]*/\*\*버전:\*\* $NEW_VERSION/" rag/README.md

echo "✅ 완료!"
echo ""
echo "다음 단계:"
echo "  1. CHANGELOG.md에 새 섹션 추가"
echo "  2. git commit"
echo "  3. git tag v$NEW_VERSION"
```

---

## 📝 수동 확인 사항

```
[ ] CHANGELOG.md 새 섹션 작성
[ ] 주요 변경사항 기록
[ ] Breaking Changes 표시
[ ] 테스트 실행
[ ] Git tag 생성
```

---

## 🎯 버전 업데이트 프로세스

1. **새 파일 확인**
   - 이번 버전에 추가된 YAML 파일?
   - 이 리스트에 추가!

2. **자동 스크립트 실행**
   ```bash
   ./update_version.sh 6.3.1
   ```

3. **수동 작업**
   - CHANGELOG.md 작성
   - 테스트

4. **배포**
   ```bash
   git commit -am "release: v6.3.1"
   git tag v6.3.1
   git push origin alpha --tags
   ```

---

**이 파일 자체도 버전 업데이트 시 확인하세요!**

