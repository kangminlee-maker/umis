# UMIS RAG 환경 설정 가이드

## 📋 사전 요구사항

- Python 3.11 이상
- OpenAI API Key
- 10GB 이상 디스크 여유 공간

## 🚀 설정 단계

### 방법 1: 자동 설정 스크립트 (권장)

```bash
# 1. setup.sh 실행
./setup.sh

# 2. .env 파일 편집 (API 키 입력)
nano .env

# 3. 가상환경 활성화
source venv/bin/activate
```

### 방법 2: 수동 설정

#### Step 1: 가상환경 생성

```bash
# Python 버전 확인
python3 --version  # 3.11 이상 확인

# 가상환경 생성
python3 -m venv venv

# 가상환경 활성화
source venv/bin/activate  # macOS/Linux
# Windows: venv\Scripts\activate
```

#### Step 2: 패키지 설치

```bash
# pip 업그레이드
pip install --upgrade pip

# 기본 패키지 설치
pip install -r requirements.txt

# 개발 패키지 설치 (선택)
pip install -r requirements-dev.txt
```

#### Step 3: 환경 변수 설정

```bash
# .env 파일 생성
cp env.template .env

# .env 파일 편집
nano .env
```

**필수 설정:**
```bash
OPENAI_API_KEY=sk-your-api-key-here
```

**선택 설정:**
```bash
# Pinecone 사용 시
VECTOR_DB=pinecone
PINECONE_API_KEY=your-pinecone-key
PINECONE_ENVIRONMENT=us-east-1

# LangSmith 모니터링 (선택)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your-langsmith-key
```

#### Step 4: 디렉토리 구조 확인

```bash
# 디렉토리 생성 (이미 생성되어 있을 수 있음)
mkdir -p data/{raw,chunks,chroma}
mkdir -p logs
mkdir -p notebooks
mkdir -p tests
```

#### Step 5: YAML 파일 준비

```bash
# YAML 파일을 data/raw로 복사
cp umis_business_model_patterns_v6.2.yaml data/raw/
cp umis_disruption_patterns_v6.2.yaml data/raw/
cp umis_ai_guide_v6.2.yaml data/raw/
```

## ✅ 설정 검증

### 1. Python 환경 확인

```bash
python --version
# Python 3.11.6 (또는 그 이상)

which python
# /Users/kangmin/Documents/AI_dev/umis-main/venv/bin/python
```

### 2. 패키지 설치 확인

```bash
pip list | grep -E "langchain|openai|chromadb"
```

예상 출력:
```
chromadb              0.4.22
langchain             0.1.0
langchain-community   0.0.20
langchain-openai      0.0.5
openai                1.10.0
```

### 3. 설정 파일 확인

```bash
# .env 파일 존재 확인
ls -la .env

# YAML 파일 확인
ls -la data/raw/
```

### 4. Python 임포트 테스트

```bash
python -c "from umis_rag import settings; print(f'✅ Config loaded: {settings.openai_model}')"
```

## 🐛 문제 해결

### Q: "No module named 'umis_rag'"

```bash
# 현재 디렉토리 확인
pwd
# /Users/kangmin/Documents/AI_dev/umis-main

# 가상환경 활성화 확인
which python
# venv/bin/python이어야 함

# 패키지 재설치
pip install -e .
```

### Q: "OPENAI_API_KEY validation error"

```bash
# .env 파일 확인
cat .env | grep OPENAI_API_KEY

# API 키가 설정되어 있는지 확인
# sk-로 시작해야 함
```

### Q: Chroma DB 권한 오류

```bash
# Chroma 디렉토리 권한 확인
ls -ld data/chroma/

# 권한 수정
chmod 755 data/chroma/
```

### Q: M1/M2 Mac에서 chromadb 설치 오류

```bash
# Rosetta 없이 Native ARM 설치
arch -arm64 pip install chromadb
```

## 📦 선택적 설정

### Jupyter 노트북 설정

```bash
# Jupyter kernel 등록
python -m ipykernel install --user --name=umis-rag --display-name="UMIS RAG"

# Jupyter 실행
jupyter notebook
```

### Pre-commit Hooks (코드 품질)

```bash
# pre-commit 설치 (requirements-dev.txt에 포함)
pre-commit install

# 모든 파일에 실행
pre-commit run --all-files
```

### VS Code 설정

`.vscode/settings.json`:
```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.ruffEnabled": true,
    "python.formatting.provider": "ruff",
    "editor.formatOnSave": true,
    "[python]": {
        "editor.defaultFormatter": "charliermarsh.ruff"
    }
}
```

## 🎯 다음 단계

환경 설정이 완료되면:

1. **[README_RAG.md](README_RAG.md)** - 프로젝트 개요 읽기
2. **notebooks/prototype.ipynb** - 프로토타입 노트북 실행
3. **scripts/** - 데이터 변환 및 인덱스 구축

## 💡 도움말

### 가상환경 비활성화
```bash
deactivate
```

### 가상환경 재활성화
```bash
source venv/bin/activate
```

### 패키지 업데이트
```bash
pip install --upgrade -r requirements.txt
```

### 전체 재설정
```bash
# 가상환경 삭제
rm -rf venv/

# 데이터 삭제 (주의!)
rm -rf data/chroma/

# 처음부터 다시
./setup.sh
```

## 📞 문의

문제가 계속되면 다음을 확인하세요:
- Python 버전: `python --version`
- pip 버전: `pip --version`
- OS 정보: `uname -a`
- 에러 로그: `logs/umis_rag.log`

