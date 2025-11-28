# DART 웹 크롤링 TODO

**작성일**: 2025-11-16  
**목적**: 재무제표 주석 크롤링 (향후 개발)

---

## 🎯 크롤링 필요성

### **케이스**:
- 이마트: OFS 섹션 33이 XML에 없음
- BGF리테일: OFS 섹션이 XML에 없음

### **현재 해결**:
- 사용자 수동 입력 (YAML 생성)
- A등급 달성 ✅

### **향후 자동화**:
- DART 웹 크롤링
- 감사보고서 재무제표 주석 추출

---

## 🔧 기술적 도전 과제

### **1. iframe 구조**
```
DART 웹사이트:
├─ 목차 페이지 (main.do)
└─ iframe으로 실제 문서 로드
    └─ 별도 URL (찾아야 함)
```

### **2. JavaScript 동적 로드**
- 정적 HTML 크롤링 불가
- Selenium 또는 Playwright 필요

### **3. dcmNo 자동 탐색**
- 사업보고서 → 감사보고서 dcmNo 찾기
- 문서 목록 API 미지원

---

## 📊 해결 방안

### **방안 1: Selenium 사용** (권장)
```python
from selenium import webdriver

driver = webdriver.Chrome()
driver.get(f'https://dart.fss.or.kr/dsaf001/main.do?rcpNo={rcept_no}&dcmNo={dcm_no}')

# iframe 전환
iframe = driver.find_element(By.TAG_NAME, 'iframe')
driver.switch_to.frame(iframe)

# 테이블 추출
table = driver.find_element(By.XPATH, "//table[contains(., '급여, 판관비')]")
```

### **방안 2: iframe src 직접 추출**
```python
# main.do HTML에서 iframe src 찾기
# iframe URL 직접 요청
```

### **방안 3: DART API 개선 요청**
- 금융감독원에 재무제표 주석 API 요청
- 또는 dcmNo 파라미터 지원 요청

---

## ✅ 현재 상태

**자동 파싱**: 7개 A등급 (64%)  
**수동 입력**: 4개 A등급 (36%)  
**총 A등급**: 11개

**크롤링 없이도 충분한 성과!** ✅

---

## 🚀 다음 단계

**당장 필요**:
- 없음 (11개 A등급 충분)

**향후 개선**:
- Selenium 크롤링 개발
- 자동화율 90%+ 목표

---

**현재는 수동 입력으로 충분합니다!** 🎯




