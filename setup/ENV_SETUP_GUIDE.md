# UMIS v7.7.0 환경변수 설정 가이드

**버전**: v7.7.0  
**업데이트**: 2025-11-12

---

## 🎯 Overview

UMIS v7.2.0부터 **환경변수가 자동으로 로드**됩니다!

```python
# 이제 이렇게만 하면 됩니다!
from umis_rag.agents.explorer import ExplorerRAG

explorer = ExplorerRAG()  # ✅ 자동으로 .env 로드!
```

**이전 (수동 로드 필요):**
```python
from dotenv import load_dotenv  # ❌ 이제 필요 없음!
load_dotenv()

from umis_rag.agents.explorer import ExplorerRAG
```

---

## 📋 필수 환경변수

### OPENAI_API_KEY (필수)

**목적:** GPT-4 및 임베딩 모델 사용

**받는 곳:** https://platform.openai.com/api-keys

**설정 방법:**

1. `.env` 파일 생성 (UMIS 루트 디렉토리)
   ```bash
   cd /path/to/umis
   touch .env
   ```

2. `.env` 파일 편집
   ```bash
   OPENAI_API_KEY=sk-proj-your-actual-api-key-here
   ```

3. 저장 후 테스트
   ```bash
   python3 -c "import umis_rag; print('✅ 환경변수 로드:', umis_rag._env_loaded)"
   ```

---

## 🔍 자동 로드 메커니즘

### 검색 순서

UMIS는 다음 순서로 `.env` 파일을 검색합니다:

1. **현재 작업 디렉토리** (`os.getcwd()`)
   - `./env`
   
2. **UMIS 프로젝트 루트**
   - `/path/to/umis/.env`
   
3. **사용자 홈 디렉토리**
   - `~/.env`

**첫 번째로 발견된 `.env` 파일을 로드**하고 검색을 중단합니다.

### 우선순위

- **기존 환경변수 우선**: 이미 설정된 환경변수는 `.env` 파일로 덮어쓰지 않습니다
- **명시적 설정 우선**: `export OPENAI_API_KEY=...`로 설정한 값이 `.env`보다 우선

---

## ⚠️ 문제 해결

### 문제 1: "OPENAI_API_KEY가 설정되지 않았습니다" 경고

**증상:**
```
UserWarning: ⚠️  .env 파일이 로드되었지만 OPENAI_API_KEY가 설정되지 않았습니다.
```

**해결:**
1. `.env` 파일 확인
   ```bash
   cat .env
   ```
   
2. `OPENAI_API_KEY=...` 줄이 있는지 확인

3. 오타 확인 (대소문자 구분)
   - ✅ `OPENAI_API_KEY`
   - ❌ `OPENAI_API_key`
   - ❌ `openai_api_key`

4. 앞뒤 공백 제거
   ```bash
   # ❌ 잘못된 예
   OPENAI_API_KEY = sk-proj-...
   
   # ✅ 올바른 예
   OPENAI_API_KEY=sk-proj-...
   ```

---

### 문제 2: "python-dotenv가 설치되지 않았습니다" 경고

**증상:**
```
UserWarning: ⚠️  python-dotenv가 설치되지 않았습니다.
```

**해결:**
```bash
pip install python-dotenv
```

---

### 문제 3: `.env` 파일이 없습니다

**증상:**
환경변수가 로드되지 않고 경고도 없음

**해결:**
1. `.env` 파일 생성
   ```bash
   cd /path/to/umis
   echo "OPENAI_API_KEY=your-api-key-here" > .env
   ```

2. 권한 확인
   ```bash
   chmod 600 .env  # 본인만 읽기/쓰기
   ```

3. `.gitignore` 확인 (`.env`가 포함되어야 함)
   ```bash
   cat .gitignore | grep ".env"
   # 출력: .env  ← 있어야 함!
   ```

---

## 🔐 보안 Best Practices

### 1. `.env` 파일 절대 커밋하지 마세요!

```bash
# .gitignore에 추가 (이미 추가되어 있음)
.env
.env.*
```

### 2. API 키 권한 최소화

OpenAI 대시보드에서:
- 사용량 제한 설정 (예: 월 $100)
- 특정 프로젝트에만 사용
- 정기적으로 키 회전 (rotate)

### 3. 프로덕션 환경

프로덕션에서는 `.env` 파일 대신 **환경변수 직접 설정**:

```bash
# Linux/Mac
export OPENAI_API_KEY=sk-proj-...

# Docker
docker run -e OPENAI_API_KEY=sk-proj-... ...

# Kubernetes
# secrets.yaml에 저장
```

---

## 🧪 테스트

### 환경변수 로드 확인

```python
import umis_rag

# 로드 상태 확인
print(f"환경변수 로드: {umis_rag._env_loaded}")

# API 키 확인
import os
api_key = os.getenv('OPENAI_API_KEY')
print(f"API 키 설정: {'✅' if api_key else '❌'}")
```

### Explorer 초기화 테스트

```python
from umis_rag.agents.explorer import ExplorerRAG

try:
    explorer = ExplorerRAG()
    print("✅ Explorer 초기화 성공!")
except Exception as e:
    print(f"❌ 초기화 실패: {e}")
```

---

## 📚 추가 환경변수 (선택)

### NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD

**목적:** Knowledge Graph (Neo4j) 연결 (기본값 사용 가능)

**기본값:**
```bash
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
```

**커스텀 설정 (필요 시):**
```bash
# .env 파일에 추가
NEO4J_URI=bolt://your-server:7687
NEO4J_USER=your-username
NEO4J_PASSWORD=your-password
```

### Web Search 크롤링 설정 (v7.7.0+)

**목적:** Google/DuckDuckGo 검색 결과의 전체 페이지 크롤링

**기본값:**
```bash
# 페이지 크롤링 활성화 (권장)
WEB_SEARCH_FETCH_FULL_PAGE=true

# 페이지당 최대 추출 문자 수
WEB_SEARCH_MAX_CHARS=5000

# 크롤링 타임아웃 (초)
WEB_SEARCH_TIMEOUT=10
```

**성능:**
- Snippet 모드: ~111자/페이지
- 크롤링 모드: ~4,108자/페이지 (37배 증가)
- 숫자 추출: 4개 → 41개 (10배 증가)

**설정 예시:**
```bash
# .env 파일에 추가

# 크롤링 비활성화 (빠른 응답 필요 시)
WEB_SEARCH_FETCH_FULL_PAGE=false

# 더 많은 정보 필요 시
WEB_SEARCH_MAX_CHARS=10000

# 느린 네트워크 환경
WEB_SEARCH_TIMEOUT=15
```

**자세한 가이드:** `docs/guides/WEB_SEARCH_CRAWLING_GUIDE.md`

---

## 🔄 환경변수 변경 시

### 변경 사항 반영

1. **Python 프로세스 재시작**
   - Jupyter Notebook: 커널 재시작
   - Script: 다시 실행

2. **또는 수동으로 다시 로드**
   ```python
   from dotenv import load_dotenv
   load_dotenv(override=True)  # 기존 값 덮어쓰기
   ```

---

## 📞 문제가 계속되면?

1. **로그 확인**
   ```bash
   cat logs/umis_rag.log | grep -i "api_key"
   ```

2. **디버그 모드**
   ```python
   import os
   os.environ['UMIS_DEBUG'] = '1'
   import umis_rag
   ```

3. **GitHub 이슈 제기**
   - Repo: https://github.com/your-org/umis
   - 이슈 템플릿: "환경변수 문제"

---

**마지막 업데이트:** 2025-11-05  
**담당:** UMIS Dev Team


