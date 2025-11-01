# UMIS Multi-Agent RAG System

Universal Market Intelligence System의 지식 베이스를 위한 Multi-Agent RAG 시스템입니다.

## 🎯 개요

5명의 전문 에이전트가 각자의 관점으로 시장 정보를 분석하고 협업합니다:

- **Albert** (Observer): 시장 구조 관찰
- **Steve** (Explorer): 기회 발굴
- **Bill** (Quantifier): 정량 분석
- **Rachel** (Validator): 데이터 검증
- **Stewart** (Guardian): 프로세스 관리

## 📁 프로젝트 구조

```
umis-main/
├── umis_rag/                 # 메인 패키지
│   ├── agents/               # 에이전트별 RAG 모듈
│   │   ├── albert.py
│   │   ├── steve.py
│   │   ├── bill.py
│   │   ├── rachel.py
│   │   └── stewart.py
│   ├── core/                 # 핵심 RAG 기능
│   │   ├── chunking.py       # 청킹 전략
│   │   ├── embeddings.py     # 임베딩 관리
│   │   └── vectorstore.py    # 벡터 DB 관리
│   ├── loaders/              # 데이터 로더
│   │   ├── yaml_loader.py    # YAML 파싱
│   │   └── converter.py      # 청크 변환
│   └── utils/                # 유틸리티
│       ├── config.py
│       └── logger.py
├── scripts/                  # 실행 스크립트
│   ├── 01_convert_yaml.py    # YAML → 청크 변환
│   ├── 02_build_index.py     # 인덱스 구축
│   └── 03_test_search.py     # 검색 테스트
├── notebooks/                # Jupyter 노트북
│   └── prototype.ipynb       # 프로토타입
├── tests/                    # 테스트
│   ├── test_chunking.py
│   └── test_agents.py
├── data/                     # 데이터 디렉토리
│   ├── raw/                  # 원본 YAML
│   ├── chunks/               # 생성된 청크
│   └── chroma/               # Chroma DB
└── docs/                     # 문서
    └── architecture.md
```

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# Python 3.11+ 확인
python --version

# 가상환경 생성
python -m venv venv

# 가상환경 활성화
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# 패키지 설치
pip install -r requirements.txt

# 개발 패키지 설치 (선택)
pip install -r requirements-dev.txt
```

### 2. 환경 변수 설정

```bash
# .env 파일 생성
cp .env.example .env

# .env 파일 편집 (API 키 입력)
nano .env
```

### 3. YAML 데이터 변환

```bash
# YAML 파일을 RAG용 청크로 변환
python scripts/01_convert_yaml.py
```

### 4. 벡터 인덱스 구축

```bash
# 에이전트별 인덱스 생성
python scripts/02_build_index.py --agents all
```

### 5. 검색 테스트

```bash
# Steve 에이전트 검색 테스트
python scripts/03_test_search.py --agent steve --query "플랫폼 비즈니스 모델"
```

## 🔧 개발 모드

### Jupyter 노트북으로 프로토타입

```bash
jupyter notebook notebooks/prototype.ipynb
```

### 대화형 테스트 (IPython)

```bash
ipython

>>> from umis_rag.agents.steve import SteveRAG
>>> steve = SteveRAG()
>>> results = steve.search_patterns("구독 서비스")
>>> print(results)
```

## 📊 Phase별 개발 계획

### Phase 1: MVP (현재)
- [x] 환경 설정
- [ ] YAML → 청크 변환기
- [ ] Steve 인덱스 구축
- [ ] 기본 검색 테스트

### Phase 2: Multi-Agent
- [ ] 5개 에이전트 인덱스
- [ ] 에이전트별 청킹 전략
- [ ] 협업 로직 (Steve ↔ Bill/Rachel)

### Phase 3: Agentic RAG
- [ ] LangChain Agent 통합
- [ ] 자율 실행 워크플로우
- [ ] Stewart 자동 검증

## 🧪 테스트

```bash
# 전체 테스트 실행
pytest

# 커버리지 리포트
pytest --cov=umis_rag --cov-report=html

# 특정 테스트만
pytest tests/test_chunking.py -v
```

## 📝 코드 품질

```bash
# Linting & Formatting (Ruff)
ruff check .
ruff format .

# Type Checking (MyPy)
mypy umis_rag/

# Pre-commit hooks (선택)
pre-commit install
pre-commit run --all-files
```

## 📚 문서

- [아키텍처 설계](docs/architecture.md)
- [에이전트 가이드](docs/agents.md)
- [API 레퍼런스](docs/api.md)

## 🤝 기여

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 라이선스

MIT License

## 🙋 문의

UMIS 팀

