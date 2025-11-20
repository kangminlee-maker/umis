# RAG System 개발 문서

UMIS RAG 시스템 관련 개발 문서입니다.

## 주요 문서

- `HYBRID_SEARCH_STRATEGY.md`: 하이브리드 검색 전략
- `LAYER_2_3_INTEGRATION_COMPLETE.md`: Layer 2-3 통합 완료
- `INTEGRATED_PIPELINE_FINAL_SUMMARY.md`: 통합 파이프라인 요약
- `UNIFIED_PIPELINE_COMPLETE.md`: 통합 파이프라인 완료

## RAG Architecture v3.0

### 4-Layer Architecture

1. **Layer 1: Canonical Store**
   - 정규화된 원본 데이터
   - 단일 진실 원천 (Single Source of Truth)

2. **Layer 2: Projected Views**
   - Agent별 검색용 뷰
   - 6개 Agent (Observer, Explorer, Quantifier, Validator, Guardian, Estimator)

3. **Layer 3: Graph Store**
   - Neo4j 기반 관계형 데이터
   - 13개 노드 타입, 45개 관계 타입

4. **Layer 4: Memory Store**
   - Query Memory (순환 감지)
   - Goal Memory (목표 정렬)
   - RAE Index (평가 일관성)

## 관련 코드

- `umis_rag/core/`
- `scripts/build_index.py`
- `scripts/query_rag.py`

