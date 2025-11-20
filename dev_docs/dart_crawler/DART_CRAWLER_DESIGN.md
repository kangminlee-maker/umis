# DART 크롤링 기능 설계 문서

**작성일**: 2025-11-16  
**버전**: v1.0  
**목적**: 실패 케이스 자동화를 위한 Selenium 기반 크롤링 시스템 설계

---

## 📊 현황 분석

### **현재 성과** (SESSION_SUMMARY_20251116_FINAL.md)

| 항목 | 값 |
|------|-----|
| **A등급** | 11개 (목표 157% ✅) |
| **총 SG&A** | 77조원 |
| **자동 파싱** | 7개 (64%) |
| **수동 입력** | 4개 (36%) |
| **평균 오차** | 1.77% |

### **실패 케이스** (수동 입력 4개)

| 기업 | DART OFS | 실패 원인 | 우선순위 |
|-----|----------|----------|---------|
| **이마트** | 41,313억 | XML 섹션35 = CFS (117% 차이) | ⭐⭐⭐ |
| **삼성전자** | 446,297억 | XML에 OFS 주석 없음 | ⭐⭐ |
| **LG화학** | 30,126억 | XML에 OFS 주석 없음 | ⭐⭐ |
| **현대차** | 2,088억 | XML에 OFS 주석 없음 | ⭐ |

**공통점**: 
- DART API `document.xml`에 **별도재무제표 주석이 없음**
- 웹사이트에는 존재 (감사보고서 dcmNo 별도 문서)
- API는 사업보고서 본문만 제공

---

## 🎯 크롤링 목표

### **단기 목표** (1주일)
1. ✅ 이마트 자동 파싱 (섹션 33, dcmNo=10420267)
2. ✅ Selenium 기반 크롤러 완성
3. ✅ OFS/CFS 자동 감지

### **중기 목표** (1개월)
1. 4개 실패 케이스 모두 자동화
2. 자동화율 90%+ (11개 → 15개)
3. 품질 검증 시스템 통합

### **장기 목표** (3개월)
1. 20개 기업 A등급
2. 산업별 3개 이상
3. Quantifier RAG 완전 구축

---

## 🏗️ 시스템 아키텍처

### **3-Layer 구조**

```
┌─────────────────────────────────────────────────────┐
│ Layer 1: API 우선 시도 (parse_sga_optimized.py)   │
│ - DART API document.xml                             │
│ - OFS 섹션 검증 (±1% 일치)                         │
│ - 성공률: 64%                                       │
└─────────────┬───────────────────────────────────────┘
              │ 실패 (OFS 불일치 또는 섹션 없음)
              ↓
┌─────────────────────────────────────────────────────┐
│ Layer 2: Hybrid 파서 (parse_sga_hybrid.py)         │
│ - 복잡 구조 대응 (규칙 + LLM)                      │
│ - 성공률: 9% (1/11)                                 │
└─────────────┬───────────────────────────────────────┘
              │ 실패 (구조 너무 복잡 또는 섹션 없음)
              ↓
┌─────────────────────────────────────────────────────┐
│ Layer 3: 웹 크롤링 (dart_crawler_selenium.py) ⭐   │
│ - Selenium 기반                                     │
│ - 감사보고서 직접 추출                              │
│ - dcmNo 자동 탐색                                   │
│ - 성공률 목표: 90%+                                 │
└─────────────────────────────────────────────────────┘
```

### **워크플로우**

```python
def parse_sga_auto(corp_name: str, rcept_no: str) -> Dict:
    """
    3-Layer 자동 파싱 파이프라인
    """
    
    # Layer 1: API 우선 시도
    result = parse_sga_optimized(corp_name, rcept_no)
    
    if result['grade'] == 'A':
        return result
    
    # Layer 2: Hybrid 파서
    result = parse_sga_hybrid(corp_name, rcept_no)
    
    if result['grade'] == 'A':
        return result
    
    # Layer 3: 웹 크롤링 (신규!)
    result = crawl_sga_selenium(corp_name, rcept_no)
    
    return result
```

---

## 🔧 Selenium 크롤러 설계

### **1. 기술 스택**

```yaml
selenium: 4.15.0+  # 웹 브라우저 자동화
webdriver-manager: 4.0.0+  # ChromeDriver 자동 설치
beautifulsoup4: 4.12.0+  # HTML 파싱
pandas: 2.1.0+  # 테이블 파싱
```

### **2. 크롤링 전략**

#### **전략 A: iframe 직접 접근** (권장 ⭐)

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def crawl_audit_report_direct(rcept_no: str, dcm_no: str) -> Dict:
    """
    감사보고서 iframe 직접 접근
    
    장점: 빠름 (5-10초)
    단점: dcmNo 필요
    """
    
    driver = webdriver.Chrome()
    
    try:
        # 1. 감사보고서 페이지 로드
        url = f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={rcept_no}&dcmNo={dcm_no}"
        driver.get(url)
        
        # 2. iframe 대기 및 전환
        wait = WebDriverWait(driver, 10)
        iframe = wait.until(
            EC.presence_of_element_located((By.TAG_NAME, "iframe"))
        )
        driver.switch_to.frame(iframe)
        
        # 3. "판매비와 관리비" 테이블 찾기
        # 방법 1: XPath (정확)
        table = driver.find_element(
            By.XPATH, 
            "//table[contains(., '급여') and contains(., '판관비')]"
        )
        
        # 또는 방법 2: CSS Selector (유연)
        tables = driver.find_elements(By.TAG_NAME, "table")
        for table in tables:
            if "급여" in table.text and "판관비" in table.text:
                break
        
        # 4. 테이블 HTML 추출
        table_html = table.get_attribute('outerHTML')
        
        # 5. BeautifulSoup으로 파싱
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(table_html, 'html.parser')
        items = parse_sga_table(soup)
        
        return {
            'source': 'selenium_direct',
            'dcm_no': dcm_no,
            'items': items,
            'success': True
        }
        
    finally:
        driver.quit()
```

#### **전략 B: dcmNo 자동 탐색** (완전 자동화 ⭐⭐⭐)

```python
def find_audit_report_dcmno(driver, rcept_no: str) -> Optional[str]:
    """
    사업보고서에서 감사보고서 dcmNo 자동 탐색
    
    장점: 완전 자동화
    단점: 느림 (15-20초)
    """
    
    # 1. 사업보고서 메인 페이지
    url = f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={rcept_no}"
    driver.get(url)
    
    # 2. 좌측 목차에서 "감사보고서" 링크 찾기
    wait = WebDriverWait(driver, 10)
    
    # 방법 1: 정확한 텍스트 매칭
    audit_link = wait.until(
        EC.presence_of_element_located((
            By.XPATH, 
            "//a[contains(text(), '감사보고서') and not(contains(text(), '연결'))]"
        ))
    )
    
    # 3. dcmNo 추출
    href = audit_link.get_attribute('href')
    dcm_match = re.search(r'dcmNo=(\d+)', href)
    
    if dcm_match:
        dcm_no = dcm_match.group(1)
        print(f"  ✓ 감사보고서 dcmNo 발견: {dcm_no}")
        return dcm_no
    
    return None


def crawl_sga_auto(corp_name: str, rcept_no: str) -> Dict:
    """
    완전 자동 크롤링 (dcmNo 탐색 → 크롤링)
    """
    
    driver = webdriver.Chrome()
    
    try:
        # 1. dcmNo 자동 탐색
        dcm_no = find_audit_report_dcmno(driver, rcept_no)
        
        if not dcm_no:
            return {'success': False, 'error': 'dcmNo not found'}
        
        # 2. 감사보고서 크롤링
        result = crawl_audit_report_direct(rcept_no, dcm_no)
        
        return result
        
    finally:
        driver.quit()
```

### **3. 테이블 파싱 로직**

```python
def parse_sga_table(soup: BeautifulSoup) -> Dict:
    """
    판관비 테이블 파싱 (기존 로직 재사용)
    
    입력: BeautifulSoup 테이블
    출력: {
        'items': {항목명: 금액},
        'unit': '백만원',
        'total': 41_313.0,
        'year': 2024
    }
    """
    
    # 1. 단위 추출
    table_text = soup.get_text()
    unit_match = re.search(r'단위\s*[:：]\s*(백만원|천원|원)', table_text)
    unit = unit_match.group(1) if unit_match else '백만원'
    
    # 2. 행 파싱
    rows = soup.find_all('tr')
    items = {}
    total_amount = 0
    
    for row in rows:
        cells = row.find_all(['td', 'th'])
        
        if len(cells) >= 2:
            # 항목명
            item_name = cells[0].get_text(strip=True)
            # 당기 금액 (두 번째 열)
            amount_str = cells[1].get_text(strip=True)
            
            # 숫자 추출
            amount_clean = re.sub(r'[^\d-]', '', amount_str)
            
            if item_name and amount_clean:
                try:
                    amount = float(amount_clean)
                    
                    # 합계 항목 체크
                    if re.match(r'^(합|총|소)\s*계$', item_name):
                        # 억원 변환
                        total_amount = convert_to_eokwon(amount, unit)
                    
                    # SG&A 합계
                    elif item_name in ['판매비와관리비', '판매비와 관리비']:
                        total_amount = convert_to_eokwon(amount, unit)
                    
                    # 일반 항목
                    else:
                        items[item_name] = amount
                        
                except ValueError:
                    continue
    
    # 3. 검증
    if not items:
        raise ValueError("테이블 파싱 실패: 항목 없음")
    
    if total_amount == 0:
        total_amount = sum(items.values()) / (100 if unit == '백만원' else 100_000)
    
    return {
        'items': items,
        'unit': unit,
        'total': total_amount
    }


def convert_to_eokwon(amount: float, unit: str) -> float:
    """단위 변환"""
    conversion = {
        '백만원': 100,
        '천원': 100_000,
        '원': 100_000_000
    }
    return amount / conversion[unit]
```

### **4. OFS/CFS 자동 감지**

```python
def detect_fs_type(soup: BeautifulSoup, dart_ofs: float) -> str:
    """
    크롤링한 테이블이 OFS인지 CFS인지 자동 감지
    
    방법:
    1. 테이블 제목에 "별도" → OFS
    2. 테이블 제목에 "연결" → CFS
    3. 합계 금액 vs DART OFS ±1% 일치 → OFS
    """
    
    # 방법 1: 제목 기반
    table_text = soup.get_text()
    
    if '별도재무제표' in table_text or '별도 재무제표' in table_text:
        return 'OFS'
    
    if '연결재무제표' in table_text or '연결 재무제표' in table_text:
        return 'CFS'
    
    # 방법 2: 금액 검증
    parsed = parse_sga_table(soup)
    table_total = parsed['total']
    
    error_rate = abs(table_total - dart_ofs) / dart_ofs * 100
    
    if error_rate <= 1.0:
        return 'OFS'
    elif error_rate > 50:
        return 'CFS'  # 크게 차이나면 CFS
    else:
        return 'UNKNOWN'
```

---

## 📦 파일 구조

### **신규 파일**

```
umis_rag/utils/
├── dart_crawler.py               (기존, requests 기반 - deprecated)
└── dart_crawler_selenium.py      ✨ (신규, Selenium 기반)

scripts/
└── crawl_sga_batch.py            ✨ (배치 크롤링 스크립트)

tests/
└── test_dart_crawler.py          ✨ (단위 테스트)

docs/
└── DART_CRAWLER_USER_GUIDE.md    ✨ (사용자 가이드)
```

### **dart_crawler_selenium.py 구조**

```python
"""
DART Selenium 크롤러 v1.0

목적:
- API로 접근 불가한 감사보고서 재무제표 주석 크롤링
- 완전 자동화 (dcmNo 탐색 → 크롤링 → 파싱)

의존성:
- selenium >= 4.15.0
- webdriver-manager >= 4.0.0
- beautifulsoup4 >= 4.12.0

사용법:
    crawler = DARTCrawlerSelenium()
    result = crawler.crawl_sga(corp_name='이마트', rcept_no='20250318000688')
"""

class DARTCrawlerSelenium:
    """Selenium 기반 DART 크롤러"""
    
    def __init__(self, headless: bool = True):
        """
        Args:
            headless: 브라우저 숨김 모드 (기본 True)
        """
        pass
    
    def crawl_sga(
        self,
        corp_name: str,
        rcept_no: str,
        dcm_no: Optional[str] = None,
        verify_ofs: bool = True
    ) -> Dict:
        """
        판관비 크롤링 (전체 파이프라인)
        
        Args:
            corp_name: 기업명
            rcept_no: 사업보고서 접수번호
            dcm_no: 감사보고서 dcmNo (없으면 자동 탐색)
            verify_ofs: OFS 검증 여부
        
        Returns:
            {
                'success': bool,
                'source': 'selenium',
                'dcm_no': str,
                'items': {항목: 금액},
                'total': float,
                'unit': str,
                'fs_type': 'OFS',
                'grade': 'A'
            }
        """
        pass
    
    def find_dcmno(self, rcept_no: str) -> Optional[str]:
        """감사보고서 dcmNo 자동 탐색"""
        pass
    
    def crawl_audit_report(self, rcept_no: str, dcm_no: str) -> BeautifulSoup:
        """감사보고서 테이블 크롤링"""
        pass
    
    def parse_sga_table(self, soup: BeautifulSoup) -> Dict:
        """테이블 파싱"""
        pass
    
    def verify_ofs(self, table_total: float, corp_name: str) -> bool:
        """OFS 검증 (DART API 조회)"""
        pass
```

---

## 🔍 품질 검증

### **1. OFS 검증 (필수)**

```python
def verify_ofs_match(crawled_total: float, corp_name: str, year: int = 2024) -> Dict:
    """
    크롤링한 금액 vs DART API OFS 검증
    
    Returns:
        {
            'match': bool,
            'crawled': 41_313.0,
            'dart_ofs': 41_313.0,
            'error_rate': 0.00,
            'grade': 'A'
        }
    """
    
    from umis_rag.utils.dart_api import DARTClient
    
    # DART API OFS 조회
    client = DARTClient()
    dart_ofs = client.get_sga_total(corp_name, year, fs_div='OFS')
    
    # ±1% 검증
    error_rate = abs(crawled_total - dart_ofs) / dart_ofs * 100
    
    # 등급 판정
    if error_rate <= 5.0:
        grade = 'A'
    elif error_rate <= 10.0:
        grade = 'B'
    elif error_rate <= 20.0:
        grade = 'C'
    else:
        grade = 'D'
    
    return {
        'match': error_rate <= 1.0,
        'crawled': crawled_total,
        'dart_ofs': dart_ofs,
        'error_rate': error_rate,
        'grade': grade
    }
```

### **2. 구조 검증**

```python
def validate_crawled_data(data: Dict) -> Dict:
    """
    크롤링 데이터 구조 검증
    
    체크 항목:
    1. 항목 수 >= 5
    2. 합계 > 0
    3. 합계 항목 제외됨
    4. 단위 명시
    """
    
    warnings = []
    
    # 1. 항목 수
    if len(data['items']) < 5:
        warnings.append(f"항목 수 부족: {len(data['items'])}개")
    
    # 2. 합계
    if data['total'] <= 0:
        warnings.append("합계 금액 없음")
    
    # 3. 합계 항목 체크
    for item in data['items']:
        if re.match(r'^(합|총|소)\s*계$', item):
            warnings.append(f"합계 항목 포함: {item}")
    
    # 4. 단위
    if 'unit' not in data:
        warnings.append("단위 없음")
    
    return {
        'valid': len(warnings) == 0,
        'warnings': warnings
    }
```

---

## 🚀 구현 단계

### **Phase 1: 기본 크롤러** (3일)

**목표**: 이마트 1개 성공

```bash
# 1일차: 환경 설정
pip install selenium webdriver-manager
python -c "from selenium import webdriver; driver = webdriver.Chrome(); driver.quit()"

# 2일차: dcmNo 알고 있을 때 크롤링
python scripts/test_crawler.py --corp 이마트 --rcept 20250318000688 --dcm 10420267

# 3일차: OFS 검증 + YAML 저장
python scripts/crawl_sga.py --corp 이마트 --auto
```

**완료 기준**:
- ✅ 이마트 A등급 (오차 < 5%)
- ✅ YAML 자동 생성
- ✅ 로그 완벽

### **Phase 2: dcmNo 자동 탐색** (2일)

**목표**: 완전 자동화

```bash
# dcmNo 없이 실행
python scripts/crawl_sga.py --corp 이마트
```

**완료 기준**:
- ✅ dcmNo 자동 발견
- ✅ 성공률 90%+

### **Phase 3: 배치 처리** (2일)

**목표**: 4개 실패 케이스 모두 처리

```bash
python scripts/crawl_sga_batch.py --corps 이마트,삼성전자,LG화학,현대차
```

**완료 기준**:
- ✅ 4개 중 3개 이상 A등급
- ✅ 자동화율 90%+

### **Phase 4: 통합 & 최적화** (2일)

**목표**: parse_sga_auto.py 통합

```python
# 3-Layer 자동 파이프라인
result = parse_sga_auto('이마트', '20250318000688')
# → Layer 1 실패 → Layer 2 실패 → Layer 3 성공!
```

**완료 기준**:
- ✅ 통합 스크립트 완성
- ✅ 에러 핸들링 완벽
- ✅ 문서화 완료

---

## 💰 비용 & 성능

### **예상 비용**

| 항목 | 비용 |
|------|------|
| **Selenium** | $0 (무료) |
| **ChromeDriver** | $0 (무료) |
| **LLM** | $0 (규칙 기반) |
| **총 비용** | **$0/기업** |

### **예상 성능**

| 메트릭 | 값 |
|--------|-----|
| **dcmNo 알 때** | 5-10초 |
| **dcmNo 탐색** | 15-20초 |
| **성공률** | 90%+ |
| **오차율** | < 5% (A등급) |

---

## ⚠️ 리스크 & 대응

### **리스크 1: DART 웹사이트 구조 변경**

**확률**: 중 (10%)  
**영향**: 크롤링 전면 실패

**대응**:
1. 테스트 케이스 자동 실행 (매주)
2. 실패 시 알림
3. 빠른 수정 (1-2일)

### **리스크 2: iframe src 동적 변경**

**확률**: 낮 (5%)  
**영향**: iframe 접근 실패

**대응**:
1. 여러 방법 준비 (XPath, CSS Selector)
2. Fallback 전략

### **리스크 3: 봇 감지 & 차단**

**확률**: 낮 (5%)  
**영향**: 접근 차단

**대응**:
1. User-Agent 설정
2. 랜덤 딜레이 (3-5초)
3. 세션 관리

### **리스크 4: 성능 저하 (느림)**

**확률**: 중 (20%)  
**영향**: 15-20초 소요

**대응**:
1. Headless 모드 (기본)
2. 캐싱 (dcmNo 저장)
3. 배치 처리 최적화

---

## 📊 성공 지표

### **Phase 1 (기본 크롤러)**
- ✅ 이마트 A등급
- ✅ 오차 < 5%
- ✅ 소요 시간 < 20초

### **Phase 2 (자동 탐색)**
- ✅ dcmNo 발견율 90%+
- ✅ 완전 자동화

### **Phase 3 (배치)**
- ✅ 4개 중 3개 A등급
- ✅ 자동화율 90%+

### **Phase 4 (통합)**
- ✅ 통합 파이프라인 완성
- ✅ 문서화 100%

---

## 🎯 최종 목표

### **정량적**
- ✅ A등급 15개 (현재 11개 → 4개 추가)
- ✅ 자동화율 90%+ (현재 64%)
- ✅ 평균 오차 < 3%
- ✅ 비용 $0

### **정성적**
- ✅ 완전 자동화 파이프라인
- ✅ 환각 방지 (규칙 기반)
- ✅ Production 품질

---

## 📁 관련 파일

### **기존 시스템**
- `scripts/parse_sga_optimized.py` - Layer 1 (API)
- `scripts/parse_sga_hybrid.py` - Layer 2 (Hybrid)
- `umis_rag/utils/dart_api.py` - DART API 클라이언트
- `umis_rag/utils/dart_validator.py` - OFS/CFS 검증

### **신규 파일** (구현 예정)
- `umis_rag/utils/dart_crawler_selenium.py` ⭐ Layer 3
- `scripts/crawl_sga_batch.py` - 배치 크롤링
- `scripts/parse_sga_auto.py` - 통합 파이프라인
- `tests/test_dart_crawler.py` - 단위 테스트

---

## 📚 참고 문서

1. **SESSION_SUMMARY_20251116_FINAL.md** - 현황 분석
2. **DART_API_LIMITATION_ANALYSIS.md** - API 한계
3. **CRAWLING_TODO.md** - 크롤링 계획
4. **SGA_PARSER_FINAL_GUIDE.md** - 파서 가이드
5. **LEARNING_CLASSIFICATION.md** - 규칙 vs LLM

---

## ✅ 다음 액션

### **즉시 시작 가능**

```bash
# 1. Selenium 설치
pip install selenium webdriver-manager beautifulsoup4

# 2. ChromeDriver 테스트
python -c "from selenium import webdriver; driver = webdriver.Chrome(); driver.quit()"

# 3. 이마트 수동 테스트 (dcmNo 알고 있음)
python scripts/test_crawler_manual.py
```

### **1주일 계획**
- **Day 1-3**: Phase 1 (기본 크롤러)
- **Day 4-5**: Phase 2 (dcmNo 자동 탐색)
- **Day 6-7**: Phase 3 (배치 처리)

---

**작성자**: AI (Cursor)  
**검토자**: 사용자  
**상태**: 설계 완료, 구현 대기  
**우선순위**: 중 (11개 A등급 이미 달성, 향후 개선 항목)

**"완전 자동화로 자동화율 90%+를 달성하자!"** 🚀




