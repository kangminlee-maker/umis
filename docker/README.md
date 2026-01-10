# UMIS Docker Guide

UMIS를 Docker 컨테이너에서 실행하는 방법입니다.

## 빠른 시작

```bash
# 1. 환경 변수 설정 (택1)
# 방법 A: 환경 변수에서 직접 설정 (권장)
export OPENAI_API_KEY=sk-...

# 방법 B: .env 파일 사용
cp env.template .env
# .env 파일에서 OPENAI_API_KEY 설정

# 2. 빌드 및 실행
./scripts/docker-build.sh
./scripts/docker-run.sh

# 3. RAG 쿼리 실행
docker-compose exec umis python scripts/query_rag.py pattern "구독 모델"
```

스크립트가 자동으로 환경 변수에서 `OPENAI_API_KEY`를 가져와 `.env` 파일을 생성합니다.

## 컨테이너 구조

```
┌────────────────────────────────────────────┐
│  Docker Compose Network (umis-network)     │
│                                            │
│  ┌─────────────┐    ┌─────────────┐        │
│  │ umis-app    │◄──►│ umis-neo4j  │        │
│  │ (UMIS +     │    │ (Neo4j 5.x) │        │
│  │  ChromaDB)  │    │             │        │
│  └─────────────┘    └─────────────┘        │
│                                            │
└────────────────────────────────────────────┘
```

## 환경 변수

셸 환경 변수 또는 `.env` 파일에서 설정:

```bash
# 셸에서 설정 (스크립트가 자동으로 .env 생성)
export OPENAI_API_KEY=sk-...
export ANTHROPIC_API_KEY=sk-ant-...  # 선택
```

| 변수 | 필수 | 기본값 | 설명 |
|------|------|--------|------|
| `OPENAI_API_KEY` | Yes | - | OpenAI API 키 |
| `ANTHROPIC_API_KEY` | No | - | Anthropic API 키 |
| `LLM_MODE` | No | `cursor` | LLM 모드 |
| `AUTO_BUILD_RAG` | No | `true` | 첫 실행 시 RAG 자동 빌드 |
| `NEO4J_PASSWORD` | No | `***REMOVED***` | Neo4j 비밀번호 |
| `WAIT_FOR_NEO4J` | No | `true` | Neo4j 대기 여부 |

## 명령어

### 기본 명령어

```bash
# 빌드
./scripts/docker-build.sh

# 실행
./scripts/docker-run.sh

# 상태 확인
./scripts/docker-run.sh --status

# 종료
./scripts/docker-run.sh --down
```

### docker-compose 직접 사용

```bash
# 빌드 및 실행
docker-compose up -d --build

# 로그 확인
docker-compose logs -f umis

# 컨테이너 접속
docker-compose exec umis bash

# 종료
docker-compose down
```

### RAG 쿼리

```bash
# 패턴 검색
docker-compose exec umis python scripts/query_rag.py "구독 모델"

# System RAG 검색
docker-compose exec umis python scripts/query_system_rag.py tool:explorer:complete
```

## 볼륨 (데이터 영속성)

| Volume | 컨테이너 경로 | 용도 |
|--------|---------------|------|
| `umis-chroma-data` | `/app/data/chroma` | ChromaDB 벡터 인덱스 |
| `umis-chunks-data` | `/app/data/chunks` | JSONL 청크 캐시 |
| `umis-logs` | `/app/logs` | 애플리케이션 로그 |
| `umis-neo4j-data` | `/data` | Neo4j 데이터 |

### 데이터 백업

```bash
# ChromaDB 백업
docker run --rm -v umis-chroma-data:/data -v $(pwd):/backup \
  alpine tar czf /backup/chroma-backup.tar.gz -C /data .

# ChromaDB 복원
docker run --rm -v umis-chroma-data:/data -v $(pwd):/backup \
  alpine tar xzf /backup/chroma-backup.tar.gz -C /data
```

### 볼륨 삭제 (초기화)

```bash
# 모든 볼륨 삭제
docker-compose down -v
```

## Neo4j

- **Browser UI**: http://localhost:7474
- **Bolt Driver**: bolt://localhost:7687
- **Username**: neo4j
- **Password**: .env의 `NEO4J_PASSWORD` (기본값: `***REMOVED***`)

## 문제 해결

### 빌드 실패

```bash
# 캐시 없이 다시 빌드
./scripts/docker-build.sh --no-cache
```

### RAG 인덱스 빌드 실패

1. `.env` 파일에 `OPENAI_API_KEY` 확인
2. 네트워크 연결 확인
3. 수동 빌드:
   ```bash
   docker-compose exec umis python scripts/02_build_index.py --agent explorer
   ```

### Neo4j 연결 실패

```bash
# Neo4j 상태 확인
docker-compose logs neo4j

# Neo4j 재시작
docker-compose restart neo4j
```

### 컨테이너 재시작

```bash
docker-compose restart umis
```

## 개발 모드

로컬 소스 코드를 마운트하여 개발:

```bash
# docker-compose.override.yml 생성
cat > docker-compose.override.yml << 'EOF'
version: '3.8'
services:
  umis:
    volumes:
      - ./umis_rag:/app/umis_rag:ro
      - ./scripts:/app/scripts:ro
EOF

# 실행
docker-compose up -d
```
