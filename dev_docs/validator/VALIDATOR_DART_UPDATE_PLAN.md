# Validator DART 통합 업데이트 계획

## 🎯 목표

Validator가 DART API를 범용적으로 사용할 수 있도록 업데이트

**핵심:**
- ❌ SG&A 파싱 메서드 추가 (필요 없음)
- ✅ DART API 범용 유틸리티 제공

---

## 📋 업데이트 대상

### 1. DART 유틸리티 모듈 (신규 생성)

**파일**: `umis_rag/utils/dart_api.py`

**기능:**
```python
class DARTClient:
    """범용 DART API 클라이언트"""
    
    def __init__(self, api_key):
        self.api_key = api_key
    
    # 핵심 기능들 (SG&A 파서에서 검증됨)
    def get_corp_code(company_name: str) -> str:
        """기업 코드 조회 (상장사 우선)"""
    
    def get_report_list(corp_code, year, report_type='A') -> list:
        """공시 목록 조회 (900 오류 재시도 포함)"""
    
    def download_document(rcept_no, reprt_code='11011') -> str:
        """원문 다운로드 (ZIP 압축 해제)"""
    
    def get_financials(corp_code, year, fs_div='OFS') -> dict:
        """재무제표 조회"""
```

**출처**: `parse_sga_with_zip.py`의 검증된 로직 추출

---

### 2. Validator 메서드 업데이트

**파일**: `umis_rag/agents/validator.py`

**수정할 메서드:**
```python
def search_dart_company_financials(
    self,
    company_name: str,
    year: int = 2024,
    data_type: str = 'financials'  # 또는 'sga', 'all'
) -> Optional[Dict]:
    """
    DART API로 상장사 데이터 검색
    
    기존:
      - company.json API (구식)
      - CFS만 조회
    
    개선:
      - corpCode.xml (최신, 검증됨)
      - OFS 우선 (개별재무제표)
      - DARTClient 사용
    """
    
    from umis_rag.utils.dart_api import DARTClient
    
    client = DARTClient(self.dart_api_key)
    
    # 기업 코드
    corp_code = client.get_corp_code(company_name)
    
    # 재무제표 조회
    if data_type == 'financials':
        return client.get_financials(corp_code, year, fs_div='OFS')
    
    # 또는 원문 다운로드
    elif data_type == 'document':
        reports = client.get_report_list(corp_code, year)
        rcept_no = reports[0]['rcept_no']
        return client.download_document(rcept_no)
```

---

### 3. Data Sources Registry 업데이트

**파일**: `data/raw/data_sources_registry.yaml`

**업데이트:**
```yaml
api_sources:
  dart_api:
    version: "2.0"  # 업데이트!
    description: "DART 전자공시 API (검증됨, v1.0.0)"
    updates:
      - "corpCode.xml 사용 (상장사 우선)"
      - "OFS 우선 (개별재무제표)"
      - "900 오류 재시도 로직"
      - "ZIP 압축 해제"
      - "reprt_code 필수"
    
    endpoints:
      corp_code: "corpCode.xml"
      financials: "fnlttSinglAcntAll.json"
      report_list: "list.json"
      document: "document.xml"
    
    usage:
      method: "ValidatorRAG.search_dart_company_financials()"
      utility: "umis_rag.utils.dart_api.DARTClient"
```

---

### 4. 문서화

**파일**: `docs/guides/VALIDATOR_DART_USAGE.md` (신규)

**내용:**
- Validator가 DART를 사용하는 방법
- 예시 코드
- 주의사항 (900 오류, OFS vs CFS 등)

---

## 📊 업데이트 순서

1. ✅ **DART 유틸리티 생성** (`umis_rag/utils/dart_api.py`)
   - parse_sga_with_zip.py에서 검증된 로직 추출
   - 범용 클래스로 재구성

2. ✅ **Validator 메서드 개선** (`umis_rag/agents/validator.py`)
   - search_dart_company_financials() 업데이트
   - DARTClient 사용하도록 수정

3. ✅ **Data Registry 업데이트** (`data/raw/data_sources_registry.yaml`)
   - DART 정보 업데이트
   - 검증된 방법 명시

4. ✅ **문서 작성** (선택)
   - Validator DART 사용 가이드

---

## 💡 핵심 원칙

**Validator는:**
- ✅ DART API로 **모든** 데이터 조회 가능
- ✅ 회사 검색, 재무제표, 원문, 공시목록 등
- ❌ SG&A 특화 파싱은 불필요 (별도 스크립트)

**SG&A 파서는:**
- ✅ 독립 스크립트로 유지 (`parse_sga_final.py`)
- ✅ Validator와 같은 DART 유틸리티 공유
- ✅ 프로젝트별 사용 (일상적인 Validator 작업과 분리)

---

## 🚀 작업 시작할까요?

제안:
1. `umis_rag/utils/dart_api.py` 생성 (검증된 로직)
2. `validator.py` 업데이트 (DARTClient 사용)
3. `data_sources_registry.yaml` 업데이트

시작할까요?




