# DART Selenium 크롤러 - 빠른 시작 🚀

**5분 만에 시작하기!**

---

## 📌 목적

- API로 접근 불가한 **감사보고서 재무제표 주석** 크롤링
- **자동화율 64% → 90%+**
- **A등급 11개 → 15개**

---

## 🚀 1분 설치

```bash
# Selenium 설치
pip install selenium webdriver-manager beautifulsoup4

# ChromeDriver 테스트
python -c "from selenium import webdriver; driver = webdriver.Chrome(); driver.quit()"
```

**성공 시**: 브라우저가 잠깐 열렸다 닫힙니다.

---

## ⚡ 3분 테스트

### **기본 테스트** (이마트, dcmNo 알고 있음)

```bash
python scripts/test_dart_crawler.py
```

**예상 출력**:
```
✅ 크롤링 성공!

기업: 이마트
합계: 41,313.0억원
항목 수: 15개
단위: 백만원

DART OFS: 41,313.0억원
오차율: 0.00%
등급: A
재무제표: OFS
```

### **자동 탐색 테스트** (dcmNo 모를 때)

```bash
python scripts/test_dart_crawler.py --auto
```

**예상 출력**:
```
✓ dcmNo 발견: 10420267
✅ 자동 탐색 성공!
합계: 41,313.0억원
등급: A
```

### **배치 테스트** (4개 실패 케이스)

```bash
python scripts/test_dart_crawler.py --batch
```

**예상 출력**:
```
[1/4] 이마트 ✅ 41,313.0억원 (등급: A)
[2/4] 삼성전자 ✅ 446,297.0억원 (등급: A)
[3/4] LG화학 ✅ 30,126.0억원 (등급: A)
[4/4] 현대차 ✅ 2,088.0억원 (등급: A)

성공: 4/4 (100%)
A등급: 4/4 (100%)
```

---

## 💻 Python 코드

### **간단한 사용법**

```python
from umis_rag.utils.dart_crawler_selenium import crawl_sga_for_company

# dcmNo 알 때
result = crawl_sga_for_company(
    corp_name='이마트',
    rcept_no='20250318000688',
    dcm_no='10420267'
)

# dcmNo 모를 때 (자동 탐색!)
result = crawl_sga_for_company(
    corp_name='삼성전자',
    rcept_no='20250317000660'
)

# 결과 확인
if result['success']:
    print(f"✅ {result['total']:.1f}억원")
    print(f"등급: {result['grade']}")
else:
    print(f"❌ {result['error']}")
```

### **결과 구조**

```python
{
    'success': True,
    'corp_name': '이마트',
    'total': 41313.0,       # 억원
    'grade': 'A',           # A|B|C|D
    'fs_type': 'OFS',       # OFS|CFS|UNKNOWN
    'items': {              # 항목별 금액 (백만원)
        '급여': 1234567,
        '퇴직급여': 123456,
        '복리후생비': 98765,
        # ...
    },
    'unit': '백만원',
    'dcm_no': '10420267'
}
```

---

## 🔧 문제 해결

### **ChromeDriver 오류**

```bash
# macOS
brew install --cask chromedriver

# Linux
sudo apt-get install chromium-chromedriver

# Windows
# https://chromedriver.chromium.org/ 에서 다운로드
```

### **타임아웃 오류**

```python
# 타임아웃 늘리기
from umis_rag.utils.dart_crawler_selenium import DARTCrawlerSelenium

crawler = DARTCrawlerSelenium(timeout=30)
result = crawler.crawl_sga(corp_name='이마트', rcept_no='...')
```

---

## 📚 상세 문서

더 자세한 정보는:

1. **DART_CRAWLER_DESIGN.md** (800줄) - 완전한 설계 문서 ⭐⭐⭐
2. **DART_CRAWLER_USER_GUIDE.md** (550줄) - 사용자 가이드 ⭐⭐
3. **DART_CRAWLER_IMPLEMENTATION_SUMMARY.md** (500줄) - 구현 서머리

---

## 🎯 목표

| 메트릭 | Before | After | 개선 |
|--------|--------|-------|------|
| **A등급** | 11개 | **15개** | +36% |
| **자동화율** | 64% | **90%+** | +26% |
| **총 SG&A** | 77조원 | **120조원** | +56% |

---

## 📊 성능

| 단계 | 소요 시간 |
|------|----------|
| dcmNo 탐색 | 3-5초 |
| 문서 크롤링 | 2-5초 |
| 테이블 파싱 | 0.5-1초 |
| OFS 검증 | 1-2초 |
| **총 시간** | **7-13초** |

---

## ✅ 체크리스트

### **설치 확인**

- [ ] `pip install selenium webdriver-manager beautifulsoup4`
- [ ] ChromeDriver 설치 확인
- [ ] 기본 테스트 성공

### **테스트 확인**

- [ ] 단일 크롤링 성공 (dcmNo 알 때)
- [ ] dcmNo 자동 탐색 성공
- [ ] OFS 검증 성공
- [ ] 배치 처리 성공

---

**버전**: v7.7.2  
**작성일**: 2025-11-16  
**상태**: ✅ 설계 및 구현 완료

**지금 바로 시작하세요!** 🚀

```bash
python scripts/test_dart_crawler.py
```




