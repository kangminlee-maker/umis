# UMIS 의존성 매트릭스
## Dependency Matrix

**생성일**: 2025-11-09 11:21:04  
**버전**: UMIS v7.5.0

---

## 📊 개요

이 문서는 UMIS 코드베이스의 의존성 관계를 자동 분석한 결과입니다.

### 분석 범위

- **Python 모듈**: 124개 파일
- **YAML 설정**: 21개 파일
- **Agent**: 5개
- **Collection**: 7개

---

## 1. Agent-Collection 매핑

각 Agent가 사용하는 RAG Collection 목록입니다.

| Agent | Collections | Count |
|-------|-------------|-------|
| **explorer** | `field:business_model`, `field:churn_rate`, `field:competitive_landscape`, `field:critical_success_factors`, `field:execution_strategy`, `field:revenue_model`, `field:trigger_observations`, `projected_index` | 8 |
| **guardian** | `field:churn_rate`, `field:critical_success_factors`, `field:data_reliability` | 3 |
| **observer** | `field:competitive_landscape`, `field:market_structure`, `field:trigger_observations`, `market_structure_patterns`, `value_chain_benchmarks` | 5 |
| **quantifier** | `calculation_methodologies`, `field:churn_rate`, `field:market_size`, `field:revenue_model`, `market_benchmarks` | 5 |
| **validator** | `data_sources_registry`, `definition_validation_cases`, `field:data_reliability`, `field:source_citations` | 4 |

---

## 2. Collection-Agent 역매핑

각 Collection을 사용하는 Agent 목록입니다.

| Collection | Agents | Count |
|------------|--------|-------|
| `calculation_methodologies` | `quantifier` | 1 |
| `data_sources_registry` | `validator` | 1 |
| `definition_validation_cases` | `validator` | 1 |
| `market_benchmarks` | `quantifier` | 1 |
| `market_structure_patterns` | `observer` | 1 |
| `projected_index` | `explorer` | 1 |
| `value_chain_benchmarks` | `observer` | 1 |

---

## 3. Python 모듈 의존성

주요 모듈 간 import 관계입니다.

### 3.1 Agent 모듈

| Agent 파일 | 의존 모듈 | Count |
|------------|-----------|-------|
| `estimator.py` | `umis_rag.core.config`<br>`umis_rag.utils.logger` | 2 |
| `judgment.py` | `umis_rag.utils.logger` | 1 |
| `rag_searcher.py` | `umis_rag.core.config`<br>`umis_rag.utils.logger` | 2 |
| `source_collector.py` | `umis_rag.utils.logger` | 1 |
| `physical.py` | `umis_rag.utils.logger` | 1 |
| `soft.py` | `umis_rag.utils.logger` | 1 |
| `value.py` | `umis_rag.agents.quantifier`<br>`umis_rag.utils.logger` | 2 |
| `tier1.py` | `umis_rag.utils.logger` | 1 |
| `tier2.py` | `umis_rag.utils.logger` | 1 |
| `tier3.py` | `umis_rag.agents.estimator.models`<br>`umis_rag.agents.estimator.tier2`<br>`umis_rag.core.config`<br>`umis_rag.utils.logger` | 4 |
| `explorer.py` | `umis_rag.core.config`<br>`umis_rag.graph.connection`<br>`umis_rag.graph.hybrid_search`<br>`umis_rag.utils.logger` | 4 |
| `observer.py` | `umis_rag.core.config`<br>`umis_rag.utils.logger` | 2 |
| `quantifier.py` | `umis_rag.agents.estimator`<br>`umis_rag.agents.estimator.models`<br>`umis_rag.core.config`<br>`umis_rag.guardian.meta_rag`<br>`umis_rag.methodologies.domain_reasoner`<br>`umis_rag.utils.logger` | 6 |
| `validator.py` | `umis_rag.agents.estimator`<br>`umis_rag.core.config`<br>`umis_rag.utils.logger` | 3 |

---

## 4. YAML 설정 참조

YAML 파일에서 참조하는 Agent 및 Collection입니다.

| YAML 파일 | Agents | Collections |
|-----------|--------|-------------|
| `agent_names.yaml` | `estimator`, `explorer`, `guardian`, `observer`, `quantifier`, `validator` | - |
| `llm_mode.yaml` | `explorer`, `observer` | - |
| `overlay_layer.yaml` | `guardian` | - |
| `pattern_relationships.yaml` | `validator` | - |
| `projection_rules.yaml` | `estimator`, `explorer`, `guardian`, `observer`, `quantifier`, `validator` | - |
| `routing_policy.yaml` | `estimator`, `explorer`, `observer`, `quantifier`, `validator` | - |
| `runtime.yaml` | `estimator` | - |
| `schema_registry.yaml` | `estimator`, `explorer`, `guardian`, `observer`, `quantifier`, `validator` | `canonical_index`, `goal_memory`, `projected_index`, `query_memory`, `rae_index` |
| `tool_registry.yaml` | `estimator`, `explorer`, `guardian`, `observer`, `quantifier`, `validator` | - |
| `tool_registry_sample.yaml` | `explorer` | - |
| `calculation_methodologies.yaml` | `quantifier` | - |
| `data_sources_registry.yaml` | `validator` | - |
| `definition_validation_cases.yaml` | `validator` | - |
| `kpi_definitions.yaml` | `validator` | - |
| `market_benchmarks.yaml` | `quantifier` | - |
| `market_structure_patterns.yaml` | `observer` | - |
| `umis_ai_guide.yaml` | `explorer`, `guardian`, `observer`, `quantifier`, `validator` | - |
| `umis_business_model_patterns.yaml` | `explorer` | - |
| `umis_disruption_patterns.yaml` | `explorer` | - |
| `umis_domain_reasoner_methodology.yaml` | `explorer`, `guardian`, `observer`, `quantifier`, `validator` | - |
| `value_chain_benchmarks.yaml` | `observer` | - |

---

## 5. 고위험 의존성 (High-Risk Dependencies)

변경 시 영향 범위가 큰 모듈들입니다.

| 모듈 | 참조 횟수 | 위험도 |
|------|-----------|--------|
| `sys` | 94 | 🔴 High |
| `umis_rag.utils.logger` | 46 | 🔴 High |
| `yaml` | 28 | 🔴 High |
| `traceback` | 24 | 🔴 High |
| `umis_rag.core.config` | 23 | 🔴 High |
| `json` | 18 | 🔴 High |
| `re` | 15 | 🔴 High |
| `umis_rag.agents.estimator.models` | 10 | 🔴 High |
| `chromadb` | 10 | 🔴 High |
| `time` | 9 | 🔴 High |

---

## 6. 변경 영향 가이드

### 6.1 Agent 이름 변경 시

영향 받는 곳:
- ✅ Python 코드 (import, 인스턴스 생성)
- ✅ YAML 설정 (agent_names.yaml, routing_policy.yaml 등)
- ✅ RAG 인덱스 메타데이터
- ✅ 문서 (umis.yaml, umis_core.yaml, .cursorrules)
- ✅ 스크립트 파일명 및 내용

권장 도구:
```bash
python scripts/impact_analyzer.py --change "agent_id" --type "agent_rename"
```

### 6.2 Collection 이름 변경 시

영향 받는 곳:
- ✅ Agent 코드 (collection_name 파라미터)
- ✅ ChromaDB 인덱스 (재구축 필요)
- ✅ 설정 파일 (projection_rules.yaml 등)
- ✅ 빌드 스크립트 (02_build_index.py)

권장 도구:
```bash
python scripts/impact_analyzer.py --change "collection_name" --type "collection_rename"
```

### 6.3 설정 키 변경 시

영향 받는 곳:
- ✅ 설정 로드 코드 (config.py, Settings 클래스)
- ✅ 다른 YAML 파일 (참조하는 경우)
- ✅ 문서

권장 도구:
```bash
python scripts/validate_consistency.py
```

---

## 7. 다음 단계

### 7.1 즉시 실행 가능

1. **의존성 그래프 시각화**
```bash
pip install pydeps
pydeps umis_rag -o docs/architecture/dependency_graph.svg
```

2. **순환 의존성 체크**
```bash
pip install import-linter
lint-imports
```

### 7.2 점진적 개선

1. Pydantic 스키마 추가 (타입 안정성)
2. 영향 분석 스크립트 작성
3. CI/CD 자동 검증 통합

---

**참고**: 이 매트릭스는 자동 생성됩니다. 정기적으로 재생성하세요.

```bash
python scripts/generate_dependency_matrix.py
```
