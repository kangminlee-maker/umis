# v7.6.2 배포 변경사항 요약

**버전**: v7.6.0 → v7.6.2  
**날짜**: 2025-11-10

---

## 📋 주요 변경사항

### **1. Estimator 완전 재설계 (v7.6.0)**

- ❌ Built-in Rules 제거 (tier1_rules/builtin.yaml)
- ⭐ Validator 우선 검색 추가 (Phase 2)
- ✅ 4-Phase → 5-Phase 프로세스
- ✅ data_sources_registry 구축 (24개)

### **2. Validator 완벽화 (v7.6.1)**

- ✅ 단위 자동 변환 (갑/년 → 갑/일)
- ✅ Relevance 검증 (GDP 오류 방지)
- ✅ search_definite_data() 메서드 추가

### **3. Tier 3 개선 (v7.6.2)**

- ✅ 하드코딩 완전 제거 (adoption_rate, arpu 등)
- ✅ 개념 기반 동적 Boundary 추론
- ✅ LLM 기반 비정형 사고 (BoundaryValidator)
- ✅ Fallback 체계 (confidence 0.5)

### **4. Web Search 구현 (v7.6.2)**

- ✅ DuckDuckGo (기본, 무료)
- ✅ Google Custom Search (선택, 유료)
- ✅ .env 기반 동적 엔진 선택
- ✅ Consensus 알고리즘

---

## 📝 신규 파일

1. `data/raw/data_sources_registry.yaml` - Validator 데이터 (20개)
2. `scripts/build_data_sources_registry.py` - 구축 스크립트
3. `umis_rag/agents/estimator/boundary_validator.py` - Boundary 검증
4. `config/web_search.env.template` - Web Search 설정

---

## 🔧 수정 파일

1. `umis_rag/agents/validator.py` - search_definite_data() 등
2. `umis_rag/agents/estimator/estimator.py` - Phase 0/2 추가
3. `umis_rag/agents/estimator/tier1.py` - Built-in 제거
4. `umis_rag/agents/estimator/tier3.py` - 하드코딩 제거, Boundary
5. `umis_rag/agents/estimator/sources/value.py` - Web Search
6. `umis_rag/agents/estimator/learning_writer.py` - metadata 수정
7. `umis_rag/core/config.py` - Web Search 설정

---

## 📊 성과

- Validator 정확도: 100% (0% 오차)
- Tier 3 정확도: 75% (25% 오차, 3배 개선)
- E2E 성공률: 95%
- Validator 커버리지: 94.7%

---

## 🎯 버전 업데이트

- v7.5.0 → v7.6.0 (재설계)
- v7.6.0 → v7.6.1 (Validator 완벽화)
- v7.6.1 → v7.6.2 (Tier 3 개선 + Web Search)

