"""
DART 웹사이트 크롤링 모듈

목적:
- API로 접근 불가한 재무제표 주석 크롤링
- 감사보고서의 "판매비와 관리비" 세부 항목 추출

케이스:
- 이마트: 섹션 33 (별도재무제표)
- BGF리테일: 섹션 28 (별도재무제표)
"""

import requests
from bs4 import BeautifulSoup
import re
from typing import Dict, List, Optional
import time


class DARTCrawler:
    """
    DART 웹사이트 크롤러
    
    참고 URL:
    https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20250318000688&dcmNo=10420267
    """
    
    def __init__(self):
        self.base_url = "https://dart.fss.or.kr"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
    
    def find_audit_report_dcmno(self, rcept_no: str) -> Optional[str]:
        """
        사업보고서에서 감사보고서 dcmNo 찾기
        
        Args:
            rcept_no: 사업보고서 접수번호
        
        Returns:
            감사보고서 dcmNo or None
        """
        
        # 사업보고서 메인 페이지
        url = f"{self.base_url}/dsaf001/main.do"
        params = {'rcpNo': rcept_no}
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            
            if response.status_code != 200:
                return None
            
            # HTML 파싱
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 감사보고서 링크 찾기
            # 패턴: "감사보고서" (연결 아님)
            links = soup.find_all('a', href=True)
            
            for link in links:
                text = link.get_text(strip=True)
                href = link['href']
                
                # "감사보고서" (연결 제외)
                if '감사보고서' in text and '연결' not in text:
                    # dcmNo 추출
                    dcm_match = re.search(r'dcmNo=(\d+)', href)
                    if dcm_match:
                        dcm_no = dcm_match.group(1)
                        print(f"  ✓ 감사보고서 dcmNo: {dcm_no}")
                        return dcm_no
            
            return None
            
        except Exception as e:
            print(f"  ❌ 오류: {e}")
            return None
    
    def crawl_sga_from_audit_report(
        self,
        rcept_no: str,
        dcm_no: Optional[str] = None,
        section_keyword: str = "판매비"
    ) -> Optional[Dict]:
        """
        감사보고서에서 판관비 세부 항목 크롤링
        
        Args:
            rcept_no: 사업보고서 접수번호
            dcm_no: 감사보고서 dcmNo (없으면 자동 탐색)
            section_keyword: 섹션 검색 키워드
        
        Returns:
            {
                'company': str,
                'year': int,
                'items': {항목명: 금액},
                'unit': str,
                'total': float,
                'dcm_no': str
            }
            or None
        """
        
        print(f"\n[DART 웹 크롤링]")
        print("="*70)
        
        # dcmNo 자동 탐색
        if not dcm_no:
            print(f"감사보고서 dcmNo 찾는 중...")
            dcm_no = self.find_audit_report_dcmno(rcept_no)
            
            if not dcm_no:
                print(f"  ❌ 감사보고서를 찾을 수 없습니다")
                return None
        
        print(f"  rcpNo: {rcept_no}")
        print(f"  dcmNo: {dcm_no}")
        
        # 감사보고서 페이지 로드
        url = f"{self.base_url}/dsaf001/main.do"
        params = {
            'rcpNo': rcept_no,
            'dcmNo': dcm_no
        }
        
        try:
            print(f"\n감사보고서 다운로드 중...")
            response = self.session.get(url, params=params, timeout=60)
            
            if response.status_code != 200:
                print(f"  ❌ HTTP {response.status_code}")
                return None
            
            print(f"  ✓ 다운로드 완료 ({len(response.text):,}자)")
            
            # HTML 파싱
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # "판매비와 관리비" 섹션 찾기
            print(f"\n'{section_keyword}' 섹션 찾는 중...")
            
            # 방법 1: 테이블 직접 찾기
            tables = soup.find_all('table')
            print(f"  ✓ {len(tables)}개 테이블 발견")
            
            # "급여, 판관비" 패턴이 있는 테이블 찾기
            target_table = None
            for table in tables:
                table_text = table.get_text()
                if '급여, 판관비' in table_text or '급여,판관비' in table_text:
                    target_table = table
                    print(f"  ✓ 판관비 테이블 발견!")
                    break
            
            if not target_table:
                print(f"  ❌ 판관비 테이블을 찾을 수 없습니다")
                return None
            
            # 테이블 파싱
            print(f"\n테이블 파싱 중...")
            items = self._parse_sga_table(target_table)
            
            if items:
                print(f"  ✓ {len(items['items'])}개 항목 추출")
                print(f"  ✓ 합계: {items['total']:,.1f}억원")
                return items
            else:
                print(f"  ❌ 파싱 실패")
                return None
                
        except Exception as e:
            print(f"  ❌ 크롤링 오류: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _parse_sga_table(self, table) -> Optional[Dict]:
        """
        판관비 테이블 파싱
        
        Returns:
            {'items': {name: amount}, 'unit': str, 'total': float}
        """
        
        rows = table.find_all('tr')
        
        # 단위 찾기
        unit = '백만원'
        table_text = table.get_text()
        unit_match = re.search(r'단위\s*[:：]\s*(백만원|천원|원)', table_text)
        if unit_match:
            unit = unit_match.group(1)
        
        items = {}
        total_amount = 0
        
        for row in rows:
            cells = row.find_all(['td', 'th'])
            
            if len(cells) >= 2:
                # 첫 열: 항목명
                item_name = cells[0].get_text(strip=True)
                # 두 번째 열: 당기 금액
                amount_str = cells[1].get_text(strip=True)
                
                # ", 판관비" 제거
                item_name = re.sub(r',\s*판관비$', '', item_name)
                
                # 숫자 추출
                amount_clean = re.sub(r'[^\d-]', '', amount_str)
                
                if item_name and amount_clean and len(item_name) > 1:
                    # 헤더 제외
                    if item_name in ['과목', '당기', '전기', '공시금액', '계정과목']:
                        continue
                    
                    try:
                        amount = float(amount_clean)
                        
                        # 최소 임계값
                        min_threshold = {'백만원': 10, '천원': 10000, '원': 100000000}.get(unit, 10)
                        
                        if abs(amount) > min_threshold:
                            # 합계 항목 체크
                            is_total = re.match(r'^(합|총|소)\s*계$', item_name.strip())
                            is_sga_total = item_name.strip() in ['판매비와관리비', '판매비와 관리비', '판매 및 일반관리비']
                            
                            if is_total or is_sga_total:
                                # 억원 변환
                                if unit == '백만원':
                                    total_amount = amount / 100
                                elif unit == '천원':
                                    total_amount = amount / 100_000
                                else:
                                    total_amount = amount / 100_000_000
                            else:
                                items[item_name] = amount
                    except:
                        pass
        
        if items:
            return {
                'items': items,
                'unit': unit,
                'total': total_amount if total_amount > 0 else sum(items.values()) / 100
            }
        
        return None


# 편의 함수
def crawl_sga_for_company(rcept_no: str, dcm_no: Optional[str] = None) -> Optional[Dict]:
    """
    간편 크롤링 함수
    
    Args:
        rcept_no: 사업보고서 접수번호
        dcm_no: 감사보고서 dcmNo (선택)
    
    Returns:
        판관비 데이터 or None
    """
    crawler = DARTCrawler()
    return crawler.crawl_sga_from_audit_report(rcept_no, dcm_no)





