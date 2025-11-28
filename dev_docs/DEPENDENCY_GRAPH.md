# UMIS Dependency Graph Analysis

**목적**: 세션 완료 시 의존성 변경을 자동으로 감지하고 검증

---

## 📊 시스템 개요

### 전체 통계
- **총 파일 수**: 107개 Python 파일
- **총 의존성**: 108개 (내부 import)
- **외부 라이브러리**: 140개
- **총 코드 라인**: 35,780줄

### 분석 날짜
- **최초 분석**: 2025-11-28
- **스크립트**: `scripts/analyze_dependencies.py`
- **결과 파일**: `dev_docs/dependency_analysis.json`

---

## ⭐ Critical Nodes (상위 15개)

**정의**: 다른 파일들이 많이 의존하는 핵심 파일

| Rank | Module | Depends On | Imported By | Score |
|------|--------|------------|-------------|-------|
| 1 | `utils.logger` | 1 | **38** | 77 |
| 2 | `core.config` | 0 | **25** | 50 |
| 3 | `core.llm_interface` | 0 | **8** | 16 |
| 4 | `core.llm_provider_factory` | 4 | **5** | 14 |
| 5 | `core.model_router` | 2 | **3** | 8 |
| 6 | `agents.quantifier` | 4 | **2** | 8 |
| 7 | `graph.connection` | 1 | **3** | 7 |
| 8 | `core.model_configs` | 0 | **3** | 6 |
| 9 | `agents.validator` | 4 | **1** | 6 |
| 10 | `utils.dart_api` | 0 | **3** | 6 |
| 11 | `core.llm_external` | 3 | **1** | 5 |
| 12 | `graph.hybrid_search` | 3 | **1** | 5 |
| 13 | `agents.explorer` | 5 | 0 | 5 |
| 14 | `guardian.memory` | 3 | **1** | 5 |
| 15 | `guardian.three_stage_evaluator` | 3 | **1** | 5 |

**Score 계산**: `depends_on + (imported_by × 2)`  
→ 다른 파일이 의존하는 것을 더 중요하게 평가

### 🚨 주의사항

#### 1. `utils.logger` (Score: 77)
- **38개 파일이 의존**
- 변경 시 **전체 시스템에 영향**
- 로깅 인터페이스 변경 금지
- 하위 호환성 필수

#### 2. `core.config` (Score: 50)
- **25개 파일이 의존**
- 설정 구조 변경 시 전체 검증 필요
- 환경 변수 키 변경 금지

#### 3. `core.llm_interface` (Score: 16)
- **8개 파일이 의존**
- LLM 추상화 계층
- TaskType, BaseLLM 인터페이스 안정성 중요

---

## 🔄 순환 의존성

### 현재 상태
✅ **순환 의존성 없음** (2025-11-28 기준)

### 검증 방법
```bash
python3 scripts/analyze_dependencies.py --check-circular
```

### 과거 이슈
- 없음 (깨끗한 의존성 그래프)

---

## 🚪 진입점 (Entry Points)

**정의**: 다른 프로젝트 파일에 의존하지 않는 파일 (외부 라이브러리만 사용)

### Core 진입점 (6개)
```
umis_rag.core.metadata_schema
umis_rag.core.config
umis_rag.core.llm_interface
umis_rag.core.model_configs
umis_rag.core.schema
```

### Agent 진입점 (1개)
```
umis_rag.agents.estimator
```

### Utils 진입점 (3개)
```
umis_rag.utils.dart_crawler
umis_rag.utils.dart_api
umis_rag.utils.dart_validator
```

### Excel 진입점 (34개)
- Excel 빌더 파일들은 대부분 독립적
- 각 시트별 빌더가 개별 진입점
- 재사용성 높은 구조

**총 44개 진입점**: 전체 107개 중 41%

---

## 🍃 리프 노드 (Leaf Nodes)

**정의**: 다른 파일이 의존하지 않는 파일 (최종 산출물)

### 주요 리프 노드
```
umis_rag.agents.observer
umis_rag.agents.explorer
umis_rag.guardian.meta_rag
umis_rag.core.circuit_breaker
umis_rag.core.workflow_executor
```

**총 69개 리프 노드**: 전체 107개 중 64%

**의미**: 시스템의 대부분이 최종 산출물 또는 독립 모듈

---

## 📦 외부 라이브러리 의존성

### 핵심 라이브러리 (15개)
```
chromadb           # Vector DB
neo4j              # Knowledge Graph
openai             # LLM API
langchain_*        # LangChain 생태계
openpyxl           # Excel 생성
pydantic           # 데이터 검증
requests           # HTTP
selenium           # Web Crawling
bs4                # HTML Parsing
duckduckgo_search  # Web Search
numpy              # 수치 계산
loguru             # 로깅
dotenv             # 환경 변수
yaml               # 설정 파일
```

### 총 외부 라이브러리
- **총 140개** (중복 제거 후)
- `requirements.txt`와 동기화 필요

---

## 🔧 세션 완료 시 체크리스트

### 1. 의존성 분석 실행
```bash
cd /path/to/umis
python3 scripts/analyze_dependencies.py
```

### 2. 순환 의존성 체크
```bash
python3 scripts/analyze_dependencies.py --check-circular
```
- ✅ 순환 없음 → 계속 진행
- ❌ 순환 발견 → **즉시 수정 필요**

### 3. Critical Node 변경 확인
```bash
# 이전 결과와 비교
diff dev_docs/dependency_analysis.json dev_docs/dependency_analysis_prev.json
```

**Critical Node 변경 시**:
- `utils.logger` 변경 → 전체 시스템 회귀 테스트
- `core.config` 변경 → 환경 설정 검증
- `core.llm_interface` 변경 → LLM 통합 테스트

### 4. 새 외부 라이브러리 추가 확인
```bash
# external_imports 섹션 확인
jq '.external_imports' dev_docs/dependency_analysis.json
```

**새 라이브러리 추가 시**:
- `requirements.txt` 업데이트
- 라이선스 확인
- 설치 가이드 업데이트

### 5. 진입점/리프 노드 변화
- 진입점 감소 → 의존성 증가 (주의)
- 리프 노드 감소 → 재사용성 증가 (긍정적)

---

## 📈 의존성 시각화

### 그래프 생성
```bash
# networkx 설치 필요
pip install networkx matplotlib

# 시각화 생성
python3 scripts/analyze_dependencies.py --visualize --max-nodes 50
```

**출력**: `dev_docs/dependency_graph.png`

### GraphML 내보내기
```bash
python3 scripts/analyze_dependencies.py --save-graph
```

**출력**: `dev_docs/dependency_graph.graphml`  
**활용**: Gephi, Cytoscape 등에서 열기 가능

---

## 🚨 경고 신호

### 1. 순환 의존성 발견
**증상**: `--check-circular`에서 경고
**원인**: 잘못된 import 구조
**해결**:
- 추상화 계층 도입
- 인터페이스 분리
- 의존성 방향 재설계

### 2. Critical Node 점수 급증
**증상**: 특정 파일의 imported_by가 급증
**원인**: 유틸리티 함수가 너무 많은 곳에서 사용
**해결**:
- 모듈 분리
- 더 구체적인 유틸리티 작성
- 중복 코드 제거

### 3. 진입점 감소
**증상**: 이전 분석 대비 진입점 수 감소
**원인**: 새로운 의존성 추가
**해결**:
- 의존성 필요성 재검토
- 선택적 import 고려

---

## 📝 히스토리

### 2025-11-28 (v7.11.1)
- **최초 분석**: 107 파일, 108 의존성
- **순환 의존성**: 없음 ✅
- **Critical Nodes**: utils.logger (38 deps), core.config (25 deps)
- **외부 라이브러리**: 140개

---

## 🔗 관련 문서

- `scripts/analyze_dependencies.py`: 분석 스크립트
- `dev_docs/dependency_analysis.json`: 분석 결과
- `SESSION_CLOSURE_PROTOCOL.yaml`: 세션 마무리 프로토콜
- `UMIS_ARCHITECTURE_BLUEPRINT.md`: 전체 아키텍처

---

## 💡 Best Practices

### 1. 새 파일 추가 시
- 의존성을 최소화
- 순환 참조 방지
- Critical Node에 불필요한 의존 금지

### 2. 기존 파일 수정 시
- Critical Node 변경 전 영향 범위 확인
- 하위 호환성 유지
- 변경 후 의존성 재분석

### 3. 리팩토링 시
- 의존성 방향 단순화
- 진입점 수 유지 또는 증가
- 순환 의존성 절대 도입 금지

---

**마지막 업데이트**: 2025-11-28  
**담당자**: Dependency Analyzer  
**버전**: v1.0
