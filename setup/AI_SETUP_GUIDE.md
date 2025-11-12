# UMIS v7.7.0 AI 자동 설치 가이드

**버전**: v7.7.0  
**업데이트**: 2025-11-12  
**신규**: Native 모드, Web Search 페이지 크롤링 (3,614% 정보 증가)  
**대상**: AI Assistant (Cursor, Claude, GPT)  
**목적**: 신규 사용자의 UMIS 설치를 AI가 자동으로 수행

---

## 🤖 AI Assistant를 위한 지침

이 문서는 **AI가 읽고 실행**하기 위한 것입니다.  
사용자가 "UMIS 설치해줘" 또는 "@setup" 명령 시 이 가이드를 따라 단계별로 실행하세요.

---

## 📋 사전 확인 사항

실행 전 **반드시 확인**:

```python
# 1. 현재 디렉토리 확인
import os
current_dir = os.getcwd()
# umis/ 루트여야 함 (umis.yaml 존재)

# 2. Python 버전 확인
import sys
python_version = sys.version_info
# Python 3.9+ 필요

# 3. 운영체제 확인
import platform
os_name = platform.system()  # Darwin(Mac), Linux, Windows
```

**확인 완료 후 진행하세요.**

---

## 🚀 자동 설치 프로세스

### 방법 1: Python 스크립트 실행 (권장)

```bash
# 전체 설치 (Neo4j 포함)
python setup.py

# 최소 설치 (Neo4j 제외)
python setup.py --minimal

# 설치 상태 확인만
python setup.py --check
```

**AI가 할 일**:
1. `run_terminal_cmd` 도구 사용
2. `python setup.py` 실행
3. 출력 확인 및 사용자에게 리포트

**주의**:
- OpenAI API 키 입력 필요 시 사용자에게 안내
- 네트워크 권한 필요 (`required_permissions: ["network"]`)

---

### 방법 2: 단계별 수동 실행

`setup.py` 실행이 불가능한 경우, 아래 단계를 순차적으로 실행:

#### Step 1: 환경 확인

```python
# AI가 실행할 코드
import sys
import os
from pathlib import Path

# Python 버전 확인
version = sys.version_info
if version.major < 3 or (version.major == 3 and version.minor < 9):
    print("❌ Python 3.9+ 필요")
    print(f"현재: Python {version.major}.{version.minor}")
    # 사용자에게 안내 후 중단
else:
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")

# umis.yaml 확인
if Path("umis.yaml").exists():
    print("✅ UMIS 루트 디렉토리 확인")
else:
    print("❌ umis.yaml 없음 - UMIS 루트에서 실행하세요")
    # 중단
```

#### Step 2: 패키지 설치

```bash
# AI가 실행할 명령
pip install -r requirements.txt
```

**예상 시간**: 30초  
**필요 권한**: `network`

**AI가 할 일**:
- `run_terminal_cmd` 사용
- 성공 메시지 확인
- 실패 시 에러 로그를 사용자에게 보고

**v7.7.0 신규 패키지**:
- `requests` - 웹 페이지 크롤링
- `beautifulsoup4` - HTML 파싱
- 이미 `requirements.txt`에 포함되어 자동 설치됨

#### Step 3: .env 파일 생성

```bash
# AI가 실행할 명령
cp env.template .env
```

**AI가 추가로 할 일**:
1. `.env` 파일이 생성되었는지 확인
2. 사용자에게 안내:
   ```
   ✅ .env 파일 생성 완료
   
   ⚠️  다음 단계: OpenAI API 키 설정 필요
   
   1. https://platform.openai.com/api-keys 방문
   2. API 키 생성
   3. .env 파일에서 OPENAI_API_KEY=your-api-key-here 수정
   ```

#### Step 4: API 키 확인

```python
# AI가 확인할 코드
from pathlib import Path

env_path = Path(".env")
if env_path.exists():
    with open(env_path) as f:
        content = f.read()
    
    if "your-api-key-here" in content:
        print("⚠️  OpenAI API 키 미설정")
        print("→ .env 파일에서 OPENAI_API_KEY 설정 필요")
        # 사용자에게 입력 요청
    elif "OPENAI_API_KEY=" in content:
        key = content.split("OPENAI_API_KEY=")[1].split("\n")[0].strip()
        if len(key) > 10:
            print("✅ OpenAI API 키 설정됨")
        else:
            print("⚠️  API 키 확인 필요")
```

**AI가 할 일**:
- API 키가 없으면 사용자에게 입력 요청
- 사용자가 제공한 키를 `.env` 파일에 안전하게 저장

#### Step 5: RAG 인덱스 빌드

```bash
# AI가 실행할 명령 (순차)

# 1. YAML → JSONL 변환
python scripts/01_convert_yaml.py

# 2. Vector DB 빌드
python scripts/02_build_index.py --agent explorer
```

**예상 시간**: 1-2분  
**예상 비용**: $0.006 (OpenAI API)  
**필요 권한**: `network`

**AI가 할 일**:
1. 사용자에게 비용 안내 및 동의 확인
2. 명령 실행
3. 진행 상황 모니터링
4. 완료 메시지 확인:
   ```
   ✅ 54 documents processed
   ✅ Collection 'explorer_knowledge_base' created
   ```

#### Step 6: Neo4j 설정 (선택 사항)

```bash
# Docker 확인
docker ps

# Neo4j 실행
docker-compose up -d
```

**AI가 할 일**:
1. 사용자에게 Neo4j 필요 여부 확인
2. Docker 실행 여부 확인
3. 필요 시 docker-compose 실행
4. Neo4j Browser 접속 안내:
   ```
   ✅ Neo4j 실행 완료
   → Browser: http://localhost:7474
   → User: neo4j / Password: umis_password
   ```

---

## ✅ 설치 완료 확인

```python
# AI가 실행하여 확인할 체크리스트
import os
from pathlib import Path

checklist = {
    "Python 3.9+": sys.version_info >= (3, 9),
    ".env 파일": Path(".env").exists(),
    "ChromaDB 인덱스": Path("data/chroma/chroma.sqlite3").exists(),
    "핵심 패키지": all([
        __import__('chromadb'),
        __import__('openai'),
        __import__('pydantic'),
        __import__('requests'),
        __import__('bs4')  # beautifulsoup4
    ])
}

all_ok = all(checklist.values())

# 사용자에게 리포트
if all_ok:
    print("✅ UMIS v7.7.0 설치 완료!")
    print("🆕 Web Search 페이지 크롤링 활성화")
else:
    print("⚠️  일부 항목 미완료:")
    for item, status in checklist.items():
        print(f"  {'✅' if status else '❌'} {item}")
```

---

## 🎯 사용자에게 최종 안내

설치 완료 후 사용자에게 다음을 안내하세요:

```markdown
✅ UMIS v7.7.0 설치 완료!

🆕 신규 기능:
- Web Search 페이지 크롤링 (정보량 37배 증가)
- Native 모드 (비용 $0)
- Estimator 5-Phase 완성

🚀 다음 단계:

1. Cursor Composer 열기 (Cmd+I)
2. umis.yaml 파일 첨부
3. 다음 명령 시도:
   "@Explorer, 구독 모델 패턴 찾아줘"
   "@Fermi, 한국 인구는?"  (Web 크롤링 자동!)

또는 터미널에서:
   python scripts/query_rag.py "구독 모델"
   python scripts/test_web_search_crawling.py --mode url

📚 도움말:
- docs/guides/WEB_SEARCH_CRAWLING_GUIDE.md (크롤링 가이드)
- UMIS_ARCHITECTURE_BLUEPRINT.md (전체 구조)
- SETUP.md (상세 가이드)
- umis.yaml (Cursor Rules)
```

---

## 🔧 문제 해결

AI가 다음 오류 발생 시 대처 방법:

### 오류 1: pip install 실패

```
ERROR: Could not find a version that satisfies...
```

**대처**:
```bash
# pip 업그레이드
pip install --upgrade pip

# 재시도
pip install -r requirements.txt
```

### 오류 2: OpenAI API 키 오류

```
openai.AuthenticationError
```

**대처**:
1. `.env` 파일 확인
2. API 키 형식 확인 (sk-...)
3. https://platform.openai.com/account/api-keys 에서 키 활성화 확인

### 오류 3: ChromaDB 빌드 실패

```
Error: Embedding failed
```

**대처**:
1. OpenAI API 키 확인
2. 네트워크 연결 확인
3. 재시도: `python scripts/02_build_index.py --agent explorer`

### 오류 4: 권한 오류

```
PermissionError: [Errno 13]
```

**대처**:
```bash
# 가상환경 사용 권장
python -m venv venv
source venv/bin/activate  # Mac/Linux
# 또는
venv\Scripts\activate  # Windows

# 재시도
pip install -r requirements.txt
```

---

## 📊 설치 진행 상황 리포트 템플릿

AI가 사용자에게 보고할 때 사용할 템플릿:

```markdown
🔄 UMIS v7.7.0 설치 진행 중...

[단계 1/5] 환경 확인
  ✅ Python 3.11.5
  ✅ UMIS 루트 디렉토리

[단계 2/5] 패키지 설치
  🔄 pip install 실행 중... (30초 예상)
  ✅ 30개 패키지 설치 완료
  ✅ 신규: requests, beautifulsoup4 (웹 크롤링용)

[단계 3/5] .env 파일 생성
  ✅ .env 파일 생성
  ⚠️  OpenAI API 키 입력 필요
  ✅ Web Search 크롤링 설정 (기본 활성화)

[단계 4/5] RAG 인덱스 빌드
  🔄 YAML → JSONL 변환 중...
  ✅ 54개 문서 변환 완료
  🔄 Vector DB 빌드 중... (1분 예상, 비용 $0.006)
  ✅ ChromaDB 인덱스 생성 완료

[단계 5/5] Neo4j 설정 (선택)
  ⏭️  스킵 (Docker 미실행)

✅ 설치 완료! (총 소요: 2분 30초)

🆕 v7.7.0 신규 기능:
  ✅ Web Search 페이지 크롤링 (정보량 37배 증가)
  ✅ Native 모드 (비용 $0)
  ✅ Estimator 5-Phase 완성
```

---

## 🤖 AI 실행 예시

### 예시 1: 전체 자동 설치

```python
# AI가 실행할 코드 시퀀스

# 1. 사전 확인
import os, sys
from pathlib import Path

if not Path("umis.yaml").exists():
    print("❌ UMIS 루트에서 실행하세요")
    exit(1)

# 2. 사용자에게 안내
print("""
🚀 UMIS v7.6.2 자동 설치를 시작합니다.

소요 시간: 약 3분
필요 항목:
  - OpenAI API 키 (없으면 생성 안내)
  - 인터넷 연결
  - 약 100MB 디스크 공간

계속하시겠습니까? (y/N)
""")

# 3. run_terminal_cmd 실행
run_terminal_cmd(
    command="python setup.py",
    is_background=False,
    required_permissions=["network"]
)

# 4. 결과 확인 및 리포트
```

### 예시 2: 최소 설치 (Neo4j 제외)

```python
run_terminal_cmd(
    command="python setup.py --minimal",
    is_background=False,
    required_permissions=["network"]
)
```

### 예시 3: 설치 상태만 확인

```python
run_terminal_cmd(
    command="python setup.py --check",
    is_background=False
)
```

---

## 📝 AI가 기억해야 할 핵심 사항

1. **항상 사전 확인**
   - Python 버전 (3.9+)
   - umis.yaml 존재 (루트 디렉토리)
   - 인터넷 연결

2. **OpenAI API 키 처리**
   - 절대 키를 로그에 출력하지 말 것
   - `.env` 파일에 안전하게 저장
   - 사용자에게만 보이도록

3. **네트워크 권한 요청**
   - pip install, RAG 빌드 시 필요
   - `required_permissions: ["network"]`

4. **진행 상황 실시간 리포트**
   - 각 단계마다 상태 업데이트
   - 예상 시간 안내
   - 실패 시 명확한 오류 메시지

5. **완료 후 Next Steps 안내**
   - Cursor에서 사용 방법
   - 터미널 사용 방법
   - 문서 참조

---

## 🎓 FAQ (AI용)

**Q: 사용자가 Python이 없다고 하면?**  
A: Python 3.9+ 설치 안내 (https://python.org/downloads)

**Q: Docker 없이도 UMIS 사용 가능한가?**  
A: 네! Neo4j는 선택 사항. `--minimal` 모드 권장.

**Q: ChromaDB 빌드 중 오류 발생 시?**  
A: OpenAI API 키 확인 → 네트워크 확인 → 재시도

**Q: 설치 후 테스트 방법은?**  
A: `python scripts/query_rag.py "구독 모델"`

**Q: 기존 설치 덮어쓰기 가능한가?**  
A: 네. `setup.py`는 기존 설치 확인 후 필요한 부분만 업데이트.

---

**문서 버전**: v7.0.0  
**최종 업데이트**: 2025-11-03  
**유지 관리**: 버전 업데이트 시 함께 갱신

