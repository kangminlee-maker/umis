# UMIS RAG Scripts

실행 스크립트 모음입니다.

## 실행 순서

1. **01_convert_yaml.py** - YAML 파일을 RAG용 청크로 변환
2. **02_build_index.py** - 에이전트별 벡터 인덱스 구축
3. **03_test_search.py** - 검색 기능 테스트

## 사용법

```bash
# 1. YAML 변환
python scripts/01_convert_yaml.py

# 2. 인덱스 구축
python scripts/02_build_index.py --agents all

# 3. 검색 테스트
python scripts/03_test_search.py --agent steve --query "플랫폼 비즈니스"
```

## 스크립트 상세

### 01_convert_yaml.py
- 입력: `data/raw/*.yaml`
- 출력: `data/chunks/*.jsonl`
- 기능: 에이전트별 청킹 전략 적용

### 02_build_index.py
- 입력: `data/chunks/*.jsonl`
- 출력: `data/chroma/` (벡터 DB)
- 기능: 임베딩 생성 및 인덱스 구축

### 03_test_search.py
- 입력: 검색 쿼리
- 출력: 검색 결과
- 기능: RAG 시스템 동작 확인

