# Google Drive ChromaDB 업로드 가이드

**대상**: UMIS 관리자  
**목적**: ChromaDB 사전 빌드 파일을 Google Drive에 업로드하여 사용자에게 제공

---

## 📦 업로드할 파일

```
파일명: chroma-db-v7.1.0-dev2.tar.gz
위치: /Users/kangmin/umis_main_1103/umis/
크기: 16MB (압축), 51MB (원본)
포함: 13개 Collection, 826개 문서
```

---

## 🚀 Google Drive 업로드 단계

### Step 1: Google Drive 접속
1. https://drive.google.com 접속
2. 로그인

### Step 2: 파일 업로드
1. "새로 만들기" 또는 "파일 업로드"
2. `chroma-db-v7.1.0-dev2.tar.gz` 선택
3. 업로드 완료 대기

### Step 3: 공유 설정
1. 업로드된 파일 우클릭 → "공유"
2. "일반 액세스" 클릭
3. **"링크가 있는 모든 사용자"** 선택
4. 권한: **"뷰어"** (다운로드만 가능)
5. "완료"

### Step 4: 공유 링크 복사
1. "링크 복사" 클릭
2. 링크 예시:
   ```
   https://drive.google.com/file/d/1ABC123XYZ_aBcDeF-GhIjKl/view?usp=sharing
   ```

### Step 5: 파일 ID 추출
```
전체 링크:
https://drive.google.com/file/d/1ABC123XYZ_aBcDeF-GhIjKl/view?usp=sharing

파일 ID (중간 부분):
1ABC123XYZ_aBcDeF-GhIjKl
```

---

## 🔧 코드 업데이트

### 파일 1: `scripts/download_prebuilt_db.py`

**Line 29 수정**:
```python
# Before
GDRIVE_FILE_ID = "YOUR_FILE_ID_HERE"

# After
GDRIVE_FILE_ID = "1ABC123XYZ_aBcDeF-GhIjKl"  # 여기에 파일 ID 붙여넣기
```

### 파일 2: `README.md`

**Line 64-66 수정**:
```markdown
<!-- Before -->
# TODO: Google Drive 링크 추가 예정
# wget [다운로드 링크]

<!-- After -->
wget "https://drive.google.com/uc?export=download&id=1ABC123XYZ_aBcDeF-GhIjKl" -O chroma-db.tar.gz
```

또는 직접 링크:
```markdown
**다운로드**: [Google Drive](https://drive.google.com/file/d/1ABC123XYZ_aBcDeF-GhIjKl/view?usp=sharing)
```

---

## 📋 업데이트 후 작업

### 1. 코드 수정
```bash
# 1. download_prebuilt_db.py 파일 ID 업데이트
# 2. README.md 링크 추가
```

### 2. 커밋
```bash
git add -A
git commit -m "chore: add Google Drive download link for ChromaDB

- download_prebuilt_db.py 파일 ID 업데이트
- README.md 다운로드 링크 추가
- 사용자가 Option B (사전 빌드) 사용 가능
"
git push origin alpha
```

### 3. 테스트
```bash
# 다운로드 테스트
python scripts/download_prebuilt_db.py

# 또는 수동
wget "https://drive.google.com/uc?export=download&id=YOUR_FILE_ID" -O test.tar.gz
tar -xzf test.tar.gz
```

---

## 🔄 업데이트 주기

**언제 새 파일 업로드?**
- 데이터 대폭 업데이트 시
- Collection 추가 시
- 버전 업그레이드 시 (v7.1.0, v7.2.0 등)

**권장**: 월 1회 또는 Major 업데이트 시

---

## ⚠️ 주의사항

1. **파일 크기**
   - 현재: 16MB
   - Google Drive 무료: 15GB
   - 여유 충분

2. **공유 설정**
   - 반드시 "링크가 있는 모든 사용자"
   - 권한: "뷰어" (편집 불가)

3. **파일 이름**
   - 버전 포함 (chroma-db-v7.1.0-dev2.tar.gz)
   - 나중에 여러 버전 관리 가능

4. **다운로드 제한**
   - Google Drive는 다운로드 횟수 제한 있음
   - 하루 수백-수천 다운로드 후 일시 차단 가능
   - 대안: GitHub Release (무제한)

---

## 📝 체크리스트

업로드 완료 후:
- [ ] 파일 ID 복사 완료
- [ ] download_prebuilt_db.py 업데이트
- [ ] README.md 링크 추가
- [ ] 다운로드 테스트 (wget 또는 스크립트)
- [ ] Git 커밋 & 푸시
- [ ] 다른 사람이 다운로드 테스트

---

**준비 완료!**
파일 업로드 후 파일 ID만 알려주시면 자동으로 코드 업데이트하겠습니다.

