# RAG Database 설정 가이드

**작성일**: 2025-11-25 (v7.11.1 업데이트)
**대상**: UMIS v7.11.1+  
**ChromaDB 크기**: ~50-100MB (향후 증가 예상)

---

## 📊 문제: ChromaDB가 Git에 너무 큼

### 현재 상황
```
ChromaDB 크기: ~50MB (현재)
예상 크기: 100-200MB (데이터 추가 시)

GitHub 제한:
  - 파일당 100MB: 하드 리밋
  - 파일당 50MB: 경고
  
→ Git에 포함하기 어려움!
```

---

## ✅ 해결 방법: 3가지 옵션

### **Option 1: 자동 재생성 (권장) ⭐**

#### 장점
- ✅ Git에 DB 안 올림 (깔끔)
- ✅ 항상 최신 상태
- ✅ 사용자가 직접 생성 (신뢰)

#### 단점
- ⚠️ OpenAI API Key 필요
- ⚠️ 초기 설정 시간 (~5분)
- ⚠️ API 비용 발생 (~$1-2)

#### 사용 방법

**방법 1: setup.py 자동 설치**
```bash
python setup/setup.py

# 자동으로:
# 1. 패키지 설치
# 2. .env 생성
# 3. RAG Collections 구축 ← 자동!
# 4. 테스트
```

**방법 2: 수동 구축**
```bash
# 1. API Key 설정
cp env.template .env
# .env에 OPENAI_API_KEY=your-key 입력

# 2. RAG Collections 구축
python scripts/build_agent_rag_collections.py --agent all

# 소요 시간: ~5분
# 비용: ~$1-2
```

**생성되는 Collections** (v7.11.1 기준):

**Agent Collections (6개)**:
- `explorer_knowledge_base` (54개 패턴: 31 Business Models + 23 Disruption)
- `calculation_methodologies` (30개, Quantifier)
- `market_benchmarks` (100개, Quantifier)
- `data_sources_registry` (50개, Validator)
- `definition_validation_cases` (84개, Validator)
- `market_structure_patterns` (30개, Observer)
- `value_chain_benchmarks` (50개, Observer)

**Estimator Collections (3개)**:
- `canonical_store` (정규화된 학습 데이터)
- `estimator` (Agent별 View, 0→2,000개 진화)
- `learned_rules` (학습된 규칙, Estimator 자동 학습)

**System Collections (2개)**:
- `system_knowledge` (44개 도구: System 9, Complete 6, Task 29)
- `goal_memory`, `query_memory`, `rae_index` (Guardian Meta-RAG)

**총 Collections**: 11-14개 (Agent + Estimator + System + Guardian)

---

### **Option 2: 사전 빌드 DB 다운로드 (빠름)**

#### 장점
- ✅ 즉시 사용 가능 (30초)
- ✅ API Key 불필요
- ✅ 비용 없음

#### 단점
- ⚠️ 수동 다운로드
- ⚠️ 업데이트 시 재다운로드
- ⚠️ 외부 저장소 필요

#### 사용 방법

**GitHub Releases 활용**:
```bash
# 1. 사전 빌드 DB 다운로드
wget https://github.com/kangminlee-maker/umis/releases/download/v7.1.0/chroma-db.tar.gz

# 2. 압축 해제
tar -xzf chroma-db.tar.gz -C data/

# 3. 즉시 사용!
python scripts/test_agent_rag.py
```

**제공 방식**:
- setup.py 자동 빌드 (권장)

---

### **Option 3: Git LFS (추천하지 않음)**

#### 장점
- Git으로 관리

#### 단점
- ❌ GitHub LFS 제한 (1GB/month 무료)
- ❌ 100MB+ → 금방 초과
- ❌ 비용 증가 ($5/50GB)
- ❌ 설정 복잡

**비추천 이유**: 비용 대비 효율 낮음

---

### **Option 4: 클라우드 Vector DB**

#### Pinecone, Weaviate Cloud 등

#### 장점
- 중앙 관리
- 모든 사용자 공유
- 확장성

#### 단점
- ❌ 월 비용 ($70-100+)
- ❌ 개인 프로젝트에 부담
- ❌ 인터넷 필수

**비추천 이유**: UMIS는 오픈소스/개인 프로젝트

---

## 🎯 UMIS 권장 전략

### **기본: Option 1 (재생성)**

```yaml
사용자 경험:
  
  1. Git clone
  2. python setup/setup.py
  3. API Key 입력
  4. 5분 대기 (자동 구축)
  5. 완료!

장점:
  - 간단
  - 최신 상태
  - Git 깔끔
```

### **백업: Option 2 (사전 빌드)**

```yaml
API Key 없는 사용자용:
  
  README에 다운로드 링크:
    - GitHub Release
    - Google Drive
  
  "API Key 없으면 사전 빌드 DB 다운로드"
```

---

## 📝 구현 계획

### 1. setup.py 업데이트 ✅ (방금 수정)
- RAG Collection 자동 구축 추가

### 2. README.md 업데이트
```markdown
## ChromaDB 설정

### Option A: 자동 재생성 (권장)
python setup/setup.py

### Option B: 사전 빌드 다운로드 (빠름)
wget https://github.com/.../chroma-db.tar.gz
tar -xzf chroma-db.tar.gz -C data/
```

### 3. GitHub Release
- v7.1.0 릴리즈 시
- chroma-db.tar.gz 첨부
- 주기적 업데이트

### 4. .gitignore 확인 ✅ (이미 설정됨)
```gitignore
data/chroma/**/*.bin
data/chroma/**/*.sqlite3
```

---

## 💰 비용 분석

### Option 1 (재생성)
```
API 호출:
  - 360개 항목 × 임베딩
  - text-embedding-3-large
  - 비용: ~$1-2 (1회)

사용자당: $1-2 (최초 1회)
```

### Option 2 (사전 빌드)
```
저장 비용:
  - GitHub Releases: 무료 (GB 단위)
  - Google Drive: 무료 (15GB)
  - S3: $0.023/GB/month = $0.02/month

관리자: $0.02/month
사용자: $0 (무료 다운로드)
```

---

## 🎯 최종 권장

**Hybrid 전략**:

1. **기본**: 재생성 스크립트 (setup.py 자동화)
2. **백업**: 사전 빌드 DB (GitHub Release)
3. **문서**: README에 양쪽 모두 안내

**이유**:
- 사용자 선택권
- API Key 없어도 사용 가능
- Git 깔끔 유지
- 비용 최소화

---

이 전략으로 진행할까요? 지금 바로 README와 setup.py를 업데이트할 수 있습니다!
