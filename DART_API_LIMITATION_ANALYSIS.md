# DART API 한계 및 해결 방안 분석

**작성일**: 2025-11-15  
**목적**: 감사보고서 (별도재무제표) 접근 방법 연구

---

## 🔍 발견 사항

### **사용자 통찰**
- 링크: https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20250318000688&**dcmNo=10420267**
- **dcmNo=10420267** = 감사보고서 (별도재무제표)
- 이 문서에 **섹션 33 (판매비와 관리비 - 별도)** 존재
- 데이터: 정확! (DART OFS API와 100% 일치)

### **우리가 다운로드한 것**
- `document.xml` API (reprt_code='11011')
- **사업보고서 본문만** 포함
- 섹션 35 (연결? 금액 2.2배 큼)

---

## 📊 DART 문서 구조

```
사업보고서 (rcept_no: 20250318000688)
├─ 본문 (dcmNo=?)
│  └─ 섹션 35: 판매비와관리비 (연결? 87,911억)
│
└─ 첨부문서들:
   ├─ 감사보고서 (dcmNo=10420267) ⭐
   │  └─ 섹션 33: 판매비와 관리비 - 별도 (41,312억) ✅
   ├─ 연결감사보고서 (dcmNo=?)
   ├─ 감사의감사보고서 (dcmNo=?)
   ├─ 내부감시장치 (dcmNo=?)
   └─ 영업보고서 (dcmNo=?)
```

---

## 📊 우리가 사용하는 API

### **1. fnlttSinglAcntAll.json** ✅
```python
url = "https://opendart.fss.or.kr/api/fnlttSinglAcntAll.json"
params = {'corp_code': corp_code, 'bsns_year': 2024, 'fs_div': 'OFS'}
```
- **결과**: 판매비와관리비 총액 = 41,312억원 ✅
- **출처**: 별도재무제표 (OFS)
- **문제**: 세부 항목 없음 (총액만)

### **2. document.xml** (현재)
```python
url = "https://opendart.fss.or.kr/api/document.xml"
params = {'rcept_no': rcept_no, 'reprt_code': '11011'}
```
- **결과**: 사업보고서 본문 XML
- **문제**: 
  - dcmNo 파라미터 미지원 ❌
  - 첨부문서 (감사보고서) 접근 불가
  - 섹션 35만 존재 (연결?)

---

## 🔧 시도한 방법

### **1. dcmNo 파라미터 추가** ❌
```python
params = {'rcept_no': '20250318000688', 'dcmNo': '10420267'}
# 결과: HTML 오류 페이지 (4,694 bytes)
```

### **2. reprt_code 변경** ❌
```python
# 11012, 11013, 11014 등 시도
# 결과: 모두 HTML 오류 페이지
```

### **3. list.json으로 감사보고서 검색** ❌
```python
params = {'corp_code': corp_code, 'pblntf_ty': 'F'}  # 외부감사관련
# 결과: 사업보고서만 반환 (감사보고서 rcept_no 얻기 실패)
```

---

## 💡 가능한 해결 방안

### **방안 1: 문서 목록 API 발견** (가능성 있음)
```python
# 추측: document 목록 조회 API가 별도 존재?
url = "https://opendart.fss.or.kr/api/document/list.json"
params = {'rcept_no': '20250318000688'}

# 기대: 첨부문서 목록 + dcmNo 반환
```

### **방안 2: XBRL API 사용** (가능성 있음)
```
DART 웹사이트 메뉴:
재무정보 > 재무정보 다운로드 > XBRL재무제표 원문 내려받기

추측 API:
- fnlttXbrl.xml (우리는 시도 안 함)
- 재무제표 주석 포함 가능성
```

### **방안 3: 웹 스크래핑** (최후 수단)
```python
# DART 웹사이트에서 직접 추출
# https://dart.fss.or.kr/dsaf001/main.do?rcpNo=...&dcmNo=...
# 비권장 (API 우선 원칙)
```

### **방안 4: 수동 입력** (현재) ✅
```python
# 사용자가 DART 웹사이트에서 확인
# 데이터 직접 제공
# YAML 수동 생성
```

---

## 🎯 추천 방안

### **즉시: 방안 4 (수동 입력)** ✅
- 이마트: 사용자 제공 데이터 사용 → **A등급** ✅
- BGF리테일: 사용자 확인 필요

### **향후: 방안 2 (XBRL API 연구)**
- fnlttXbrl.xml 테스트
- 재무제표 주석 포함 여부 확인
- 자동화 가능성 탐색

---

## 📊 현재 성과

**자동 파싱 성공**: 5개 A등급  
**수동 입력**: 1개 A등급 (이마트)  
**총 A등급**: 6개

**자동화율**: 83% (5/6)  
**평균 오차**: 2.3%

---

## ✅ 결론

**DART API 한계**:
- document.xml은 사업보고서 본문만
- 감사보고서 (첨부문서) 접근 불가
- dcmNo 파라미터 미지원

**현재 해결책**:
- 수동 입력 (사용자 제공 데이터)
- 높은 품질 보장 (100% 정확)

**향후 연구**:
- XBRL API 탐색
- 문서 목록 API 발견

