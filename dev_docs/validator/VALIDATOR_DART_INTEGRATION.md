# Validator DART 통합 계획
**작성일**: 2025-11-13  
**목적**: Validator가 DART API를 범용으로 사용할 수 있도록 통합

---

## 🎯 목표

**Validator:**
- ✅ DART API로 범용 데이터 조회
- ✅ 상장사 재무제표, 공시문서, 기업정보 등
- ❌ SG&A 특화 파싱 불필요 (별도 스크립트)

---

## 📋 올바른 업데이트 순서

사용자 지적대로, **umis.yaml 업데이트가 먼저**입니다!

### 순서

```
1️⃣ umis.yaml (또는 umis_core.yaml) 업데이트
   ↓
   Validator 섹션에 DART API 기능 추가
   
2️⃣ System RAG 재구축
   ↓
   python scripts/sync_umis_to_rag.py
   python scripts/build_system_knowledge.py
   
3️⃣ 실제 코드 구현
   ↓
   umis_rag/utils/dart_api.py 생성
   umis_rag/agents/validator.py 개선
   
4️⃣ Data Sources Registry 업데이트
   ↓
   data/raw/data_sources_registry.yaml
```

---

## 📝 업데이트 내용

### 1. umis.yaml (또는 umis_core.yaml)

**Validator 섹션에 추가:**
```yaml
validator:
  name: Rachel
  role: data_verification
  
  # 기존 기능
  core_capabilities:
    - 데이터 정의 검증
    - 출처 신뢰도 평가
    - Gap 분석
    - 확정 데이터 검색
  
  # ⭐ 신규 추가
  api_integrations:
    dart_api:
      description: "DART 전자공시 API 범용 접근"
      version: "1.0.0"
      verified: true
      verification_date: "2025-11-13"
      
      capabilities:
        - get_corp_code: "기업 코드 조회 (상장사 우선)"
        - get_financials: "재무제표 조회 (OFS 우선)"
        - get_report_list: "공시 목록 조회 (재시도 포함)"
        - download_document: "원문 다운로드 (ZIP 해제)"
      
      improvements:
        - "900 오류 재시도 (3회)"
        - "개별재무제표(OFS) 우선"
        - "상장사 우선 매칭"
        - "reprt_code 필수 파라미터"
        - "ZIP 압축 자동 해제"
      
      utility_module: "umis_rag.utils.dart_api.DARTClient"
      
      usage_example: |
        from umis_rag.utils.dart_api import DARTClient
        
        client = DARTClient(api_key)
        corp_code = client.get_corp_code("삼성전자")
        financials = client.get_financials(corp_code, 2023, fs_div='OFS')
```

### 2. System RAG 재구축

```bash
# umis.yaml 업데이트 후
python scripts/sync_umis_to_rag.py
python scripts/build_system_knowledge.py

# 결과:
# - tool:validator:dart_api (신규 도구)
# - Validator Complete 업데이트
```

### 3. 코드 구현 (그 다음)

**umis_rag/utils/dart_api.py** (신규):
- parse_sga_with_zip.py에서 검증된 로직 추출
- DARTClient 클래스

**umis_rag/agents/validator.py** (개선):
- DARTClient 사용
- search_dart_company_financials() 개선

### 4. Data Sources Registry 업데이트

**data/raw/data_sources_registry.yaml**:
- DART API 정보 업데이트
- 검증된 방법 반영

---

## 💡 핵심 원칙

**1. umis.yaml이 Source of Truth**
- 모든 Agent 기능은 umis.yaml에 명시
- System RAG는 umis.yaml의 반영
- 코드는 umis.yaml 기반으로 구현

**2. Validator는 범용 접근만**
- DART API 전체 기능 사용 가능
- SG&A 특화는 불필요
- 재무제표, 공시, 원문 등 모두 접근

**3. SG&A 파서는 독립**
- 별도 스크립트 유지
- Validator와 같은 유틸리티 공유
- 프로젝트별 사용

---

## 🚀 다음 단계

### 현재 세션은 여기서 마무리하고

**이번 세션 완료:**
- ✅ 11개 기업 SG&A 파싱
- ✅ 진화형 파서 시스템
- ✅ 정리 완료

**다음 세션에서:**
1. umis.yaml (또는 umis_core.yaml) 업데이트
2. System RAG 재구축
3. Validator DART 통합
4. 변동비/고정비 분류

---

**정리:**
- 사용자 지적 ✅: umis.yaml 업데이트 → System RAG → 코드
- 현재: SG&A 파싱 완료 + 정리 완료
- 다음: Validator DART 통합 (새 세션)

---

이번 세션은 여기서 마무리할까요? 🎊




