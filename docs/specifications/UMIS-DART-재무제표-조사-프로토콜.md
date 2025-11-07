# UMIS DART 재무제표 조사 프로토콜 v0.1

- 목적: DART(FSS) 기반 기업 재무 데이터 조사 및 활용 절차 표준화
- 적용 범위: 상장/외감 대상 법인의 정기/수시공시 재무정보 수집, 검증, 기록
- 작성일: 2025-09-16

## 1. 핵심 원칙
- 정의 우선: 연결/별도(CFS/OFS), 회계기준(K-IFRS/K-GAAP), 기간(사업/반기/분기), 통화/단위를 먼저 확정
- 출처 신뢰: DART 원문/XBRL을 1차 소스로 사용, 2차 출처는 보조
- 완전 추적성: 접수번호(rcp_no), 제출일, 보고서명, 추출 경로를 기록
- 검색 확장: 사용자 관점 키워드 확장으로 누락 방지 (예: "사업보고서", "정정공시", "XBRL", 회사명+"실적")

## 2. 절차 개요
- 웹 UI 경로: dart.fss.or.kr → 회사 검색 → 보고서 유형/필터 선택 → XBRL/본문 확인
- OpenAPI 경로: corpCode 매핑 → 공시목록(list) → 재무제표(fnlttSinglAcntAll) 수집 → 검증/기록

## 3. 웹 UI 상세 절차
1) 회사명 검색 후 기업 선택
2) 좌측 필터에서 보고서 유형 선택: 사업/반기/분기/감사/정정공시
3) 표시 확인: "연결재무제표"/"별도재무제표", XBRL 보기 존재 여부
4) 체크 포인트:
   - 정정공시 유무(최신본 우선)
   - 감사의견(적정/한정/부적정/의견거절)
   - 기준일/기간, 단위(천원/백만원)
   - 주석: 세그먼트, 범위변경(종속 편입/제외), 수익인식 변경, 환산 기준
5) 필요 표 추출: 손익계산서, 재무상태표, 현금흐름표, 자본변동표, 세그먼트

## 4. OpenAPI 상세 절차
1) 기업 고유번호 확보: corpCode.xml 다운로드 후 회사명↔corp_code 매핑
2) 공시목록 조회(list.json): rcp_no, 보고서명, 제출일, 정정여부 수집
3) 재무제표 조회(fnlttSinglAcntAll.json): 표준계정별 수치 수집
   - 파라미터: corp_code, bsns_year, reprt_code(11011 사업/11012 반기/11013 3분기/11014 1분기), fs_div(CFS/OFS), sj_div(BS/IS/CF/SCE 선택)
4) 정합성 검증 후 기록 포맷에 저장

### 4.1 샘플 요청(curl)
```bash
curl -G "https://opendart.fss.or.kr/api/fnlttSinglAcntAll.json" 
  --data-urlencode "crtfc_key=YOUR_API_KEY" 
  --data-urlencode "corp_code=00126380" 
  --data-urlencode "bsns_year=2024" 
  --data-urlencode "reprt_code=11011" 
  --data-urlencode "fs_div=CFS" | jq ".list | map(select(.account_nm=="매출액" or .account_nm=="영업이익" or .account_nm=="당기순이익"))"
```

## 5. 품질/정합성 체크리스트
- 연결 vs 별도: 기본 연결 우선, 필요 시 별도 병기
- 기간 일치: 전기/전전기 라벨, 누적/분기 구분
- 회계기준: K-IFRS 전환/정책 변경 메모
- 정정공시: 최신 정정본 반영
- 단위/통화: 천원/백만원 환산 일관성, 외화 환산 근거 기록
- 감사의견: 한정/부적정/의견거절 경고
- 수치 검증: XBRL 합계 일치, 표 간 교차확인(매출 vs 세그먼트 합)
- 메타데이터: rcp_no, 보고서명, 제출일, 페이지/표 제목, 추출일

## 6. 기록 포맷(예시)
```yaml
source: DART
company: {법인명}
corp_code: {고유번호}
report:
  name: {사업/반기/분기/감사보고서}
  rcp_no: {접수번호}
  submit_date: {YYYY-MM-DD}
accounting:
  basis: K-IFRS
  fs_div: CFS # or OFS
  unit: KRW_million
  audit_opinion: {적정/한정/부적정/의견거절}
figures:
  revenue: {값}
  operating_income: {값}
  net_income: {값}
notes:
  - {세그먼트/범위변경/정정 사유 등}
```

## 7. 검색어 확장 가이드(일반 검색 병행 시)
- 직접: 재무제표, 사업보고서, 감사보고서, 연결재무제표, 별도재무제표
- 상황: 정정공시, 회계정책 변경, 세그먼트 정보, XBRL
- 지표: 매출액, 영업이익, 당기순이익, 현금흐름
- 일상어/브랜드: 회사명+매출, 회사명+실적발표

## 8. 운영상 주의
- API 제한: 호출 제한 발생 시 지수적 백오프, 기간 분할 수집
- 비상장/외감 제외: 공시의무·범위 확인
- 구버전 공시: PDF만 있는 경우 XBRL/본문 병행 확인

## 9. 변경 이력
- v0.1 (2025-09-16): 최초 작성. 웹 UI/OpenAPI 절차, 체크리스트, 템플릿 포함

## 10. DART OpenAPI 키 관리
- 발급: `opendart.fss.or.kr` 개발자센터에서 개인 키 발급
- 보관 원칙: 코드/문서에 직접 키를 넣지 않음. 환경변수·로컬 시크릿 사용
- 운영 원칙: 키는 개인별·환경별 분리 관리, 로그/PR에 노출 금지

### 10.1 환경변수 설정(macOS/zsh)
```bash
# 1) 최초 1회: ~/.zshrc에 키 추가
echo 'export DART_API_KEY="<YOUR_KEY>"' >> ~/.zshrc
# 2) 현재 세션 반영
source ~/.zshrc
# 3) 확인
printenv DART_API_KEY
```

### 10.2 curl 사용 예시
```bash
curl -G "https://opendart.fss.or.kr/api/fnlttSinglAcntAll.json" \
  --data-urlencode crtfc_key="$DART_API_KEY" \
  --data-urlencode corp_code="00126380" \
  --data-urlencode bsns_year="2024" \
  --data-urlencode reprt_code="11011" \
  --data-urlencode fs_div="CFS" | jq .
```

### 10.3 Python 사용 예시
```python
import os, requests
API_KEY = os.getenv('DART_API_KEY')
params = {
  'crtfc_key': API_KEY,
  'corp_code': '00126380',
  'bsns_year': '2024',
  'reprt_code': '11011',
  'fs_div': 'CFS'
}
r = requests.get('https://opendart.fss.or.kr/api/fnlttSinglAcntAll.json', params=params)
print(r.json())
```

### 10.4 키 미보유/미설정 시 처리
- 실행 시 키가 없으면 사용자에게 다음 중 하나를 요청:
  - 환경변수 `DART_API_KEY` 설정 후 재실행
  - 일회성 실행을 위해 키 값을 직접 입력 제공
- 메시지 예:
  - "DART API Key가 설정되지 않았습니다. `export DART_API_KEY="<YOUR_KEY>"` 후 다시 시도하거나, 키 값을 알려주세요."

### 10.5 보안 모범사례
- 키는 저장소에 커밋 금지(.env.local, 키체인/시크릿 매니저 권장)
- 스크립트는 키 부재 시 즉시 중단하고 안내 메시지 출력
- 로그에 요청 URL/키 값 마스킹 처리

