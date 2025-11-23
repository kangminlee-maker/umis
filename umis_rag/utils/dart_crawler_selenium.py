"""
DART Selenium 크롤러 v1.0

목적:
- API로 접근 불가한 감사보고서 재무제표 주석 크롤링
- 완전 자동화 (dcmNo 탐색 → 크롤링 → 파싱 → 검증)

의존성:
- selenium >= 4.15.0
- webdriver-manager >= 4.0.0
- beautifulsoup4 >= 4.12.0

사용법:
    from umis_rag.utils.dart_crawler_selenium import DARTCrawlerSelenium

    crawler = DARTCrawlerSelenium(headless=True)
    result = crawler.crawl_sga(
        corp_name='이마트',
        rcept_no='20250318000688'
    )

    if result['success']:
        print(f"✅ {result['total']:.1f}억원")
        print(f"등급: {result['grade']}")

작성일: 2025-11-16
버전: v1.0
"""

import re
import time
from typing import Dict, List, Optional
from bs4 import BeautifulSoup

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False


class DARTCrawlerSelenium:
    """
    Selenium 기반 DART 크롤러

    Features:
    1. 감사보고서 dcmNo 자동 탐색
    2. iframe 기반 문서 크롤링
    3. 판관비 테이블 파싱
    4. OFS/CFS 자동 검증
    5. 등급 자동 판정
    """

    def __init__(self, headless: bool = True, timeout: int = 20):
        """
        Args:
            headless: 브라우저 숨김 모드 (기본 True)
            timeout: 페이지 로드 타임아웃 (초)
        """

        if not SELENIUM_AVAILABLE:
            raise ImportError(
                "Selenium이 설치되지 않았습니다.\n"
                "설치: pip install selenium webdriver-manager"
            )

        self.base_url = "https://dart.fss.or.kr"
        self.headless = headless
        self.timeout = timeout
        self.driver = None

    def _init_driver(self):
        """Chrome 드라이버 초기화"""

        if self.driver:
            return

        options = Options()

        if self.headless:
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')

        # 기본 설정
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')
        options.add_argument(
            'user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
            'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )

        try:
            # webdriver-manager 사용 (자동 설치)
            from webdriver_manager.chrome import ChromeDriverManager
            from selenium.webdriver.chrome.service import Service

            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)

        except ImportError:
            # webdriver-manager 없으면 기본 설치 시도
            self.driver = webdriver.Chrome(options=options)

        self.driver.set_page_load_timeout(self.timeout)

    def _close_driver(self):
        """드라이버 종료"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None

    def crawl_sga(
        self,
        corp_name: str,
        rcept_no: str,
        dcm_no: Optional[str] = None,
        verify_ofs: bool = True,
        year: int = 2024
    ) -> Dict:
        """
        판관비 크롤링 (전체 파이프라인)

        Args:
            corp_name: 기업명
            rcept_no: 사업보고서 접수번호
            dcm_no: 감사보고서 dcmNo (없으면 자동 탐색)
            verify_ofs: OFS 검증 여부
            year: 사업연도

        Returns:
            {
                'success': bool,
                'source': 'selenium',
                'dcm_no': str,
                'items': {항목: 금액},
                'total': float,
                'unit': str,
                'fs_type': 'OFS'|'CFS'|'UNKNOWN',
                'grade': 'A'|'B'|'C'|'D',
                'error': str (실패 시)
            }
        """

        print(f"\n[DART Selenium 크롤링]")
        print("=" * 70)
        print(f"기업: {corp_name}")
        print(f"접수번호: {rcept_no}")

        try:
            # 1. 드라이버 초기화
            self._init_driver()

            # 2. dcmNo 자동 탐색 (필요 시)
            if not dcm_no:
                print(f"\n[1/4] 감사보고서 dcmNo 탐색 중...")
                dcm_no = self.find_dcmno(rcept_no)

                if not dcm_no:
                    return {
                        'success': False,
                        'error': 'dcmNo를 찾을 수 없습니다',
                        'corp_name': corp_name
                    }

                print(f"  ✓ dcmNo 발견: {dcm_no}")
            else:
                print(f"  ✓ dcmNo 제공됨: {dcm_no}")

            # 3. 감사보고서 크롤링
            print(f"\n[2/4] 감사보고서 크롤링 중...")
            table_soup = self.crawl_audit_report(rcept_no, dcm_no)

            if not table_soup:
                return {
                    'success': False,
                    'error': '판관비 테이블을 찾을 수 없습니다',
                    'dcm_no': dcm_no
                }

            print(f"  ✓ 테이블 추출 완료")

            # 4. 테이블 파싱
            print(f"\n[3/4] 테이블 파싱 중...")
            parsed = self.parse_sga_table(table_soup)

            if not parsed:
                return {
                    'success': False,
                    'error': '테이블 파싱 실패',
                    'dcm_no': dcm_no
                }

            print(f"  ✓ {len(parsed['items'])}개 항목 추출")
            print(f"  ✓ 합계: {parsed['total']:,.1f}억원")
            print(f"  ✓ 단위: {parsed['unit']}")

            # 5. OFS 검증 (선택)
            grade = 'UNKNOWN'
            fs_type = 'UNKNOWN'
            dart_ofs = None

            if verify_ofs:
                print(f"\n[4/4] OFS 검증 중...")
                verification = self.verify_ofs(
                    parsed['total'],
                    corp_name,
                    year
                )

                grade = verification['grade']
                fs_type = verification['fs_type']
                dart_ofs = verification['dart_ofs']

                print(f"  ✓ DART OFS: {dart_ofs:,.1f}억원")
                print(f"  ✓ 오차율: {verification['error_rate']:.2f}%")
                print(f"  ✓ 등급: {grade}")
                print(f"  ✓ 재무제표: {fs_type}")

            # 6. 결과 반환
            return {
                'success': True,
                'source': 'selenium',
                'corp_name': corp_name,
                'year': year,
                'rcept_no': rcept_no,
                'dcm_no': dcm_no,
                'items': parsed['items'],
                'total': parsed['total'],
                'unit': parsed['unit'],
                'fs_type': fs_type,
                'grade': grade,
                'dart_ofs': dart_ofs
            }

        except Exception as e:
            print(f"\n  ❌ 크롤링 실패: {e}")
            import traceback
            traceback.print_exc()

            return {
                'success': False,
                'error': str(e),
                'corp_name': corp_name
            }

        finally:
            # 드라이버 종료
            self._close_driver()

    def find_dcmno(self, rcept_no: str) -> Optional[str]:
        """
        사업보고서에서 감사보고서 dcmNo 자동 탐색

        Args:
            rcept_no: 사업보고서 접수번호

        Returns:
            감사보고서 dcmNo or None
        """

        url = f"{self.base_url}/dsaf001/main.do?rcpNo={rcept_no}"

        try:
            self.driver.get(url)
            time.sleep(2)  # 페이지 로드 대기

            # 좌측 목차에서 "감사보고서" 링크 찾기
            # 패턴: "감사보고서" (연결 제외)

            # 방법 1: XPath (정확)
            try:
                audit_link = self.driver.find_element(
                    By.XPATH,
                    "//a[contains(text(), '감사보고서') and not(contains(text(), '연결'))]"
                )
            except NoSuchElementException:
                # 방법 2: 모든 링크 검색
                links = self.driver.find_elements(By.TAG_NAME, 'a')

                audit_link = None
                for link in links:
                    text = link.text.strip()
                    if '감사보고서' in text and '연결' not in text:
                        audit_link = link
                        break

                if not audit_link:
                    return None

            # dcmNo 추출
            href = audit_link.get_attribute('href')

            if not href:
                return None

            dcm_match = re.search(r'dcmNo=(\d+)', href)

            if dcm_match:
                return dcm_match.group(1)

            return None

        except TimeoutException:
            print(f"  ❌ 페이지 로드 타임아웃")
            return None

        except Exception as e:
            print(f"  ❌ dcmNo 탐색 실패: {e}")
            return None

    def crawl_audit_report(self, rcept_no: str, dcm_no: str) -> Optional[BeautifulSoup]:
        """
        감사보고서에서 판관비 테이블 크롤링

        Args:
            rcept_no: 사업보고서 접수번호
            dcm_no: 감사보고서 dcmNo

        Returns:
            BeautifulSoup 테이블 or None
        """

        url = f"{self.base_url}/dsaf001/main.do?rcpNo={rcept_no}&dcmNo={dcm_no}"

        try:
            self.driver.get(url)
            time.sleep(2)  # 페이지 로드 대기

            # iframe 찾기 및 전환
            wait = WebDriverWait(self.driver, self.timeout)

            iframe = wait.until(
                EC.presence_of_element_located((By.TAG_NAME, "iframe"))
            )

            self.driver.switch_to.frame(iframe)
            time.sleep(1)

            # "판매비와 관리비" 또는 "급여, 판관비" 테이블 찾기
            tables = self.driver.find_elements(By.TAG_NAME, "table")

            target_table = None

            for table in tables:
                table_text = table.text

                # 패턴 1: "급여, 판관비" 또는 "급여,판관비"
                if ('급여' in table_text and '판관비' in table_text):
                    target_table = table
                    break

                # 패턴 2: "판매비와관리비"
                if '판매비와관리비' in table_text or '판매비와 관리비' in table_text:
                    target_table = table
                    break

            if not target_table:
                return None

            # 테이블 HTML 추출
            table_html = target_table.get_attribute('outerHTML')

            # BeautifulSoup 파싱
            soup = BeautifulSoup(table_html, 'html.parser')

            return soup

        except TimeoutException:
            print(f"  ❌ iframe 로드 타임아웃")
            return None

        except Exception as e:
            print(f"  ❌ 테이블 크롤링 실패: {e}")
            return None

    def parse_sga_table(self, soup: BeautifulSoup) -> Optional[Dict]:
        """
        판관비 테이블 파싱

        Args:
            soup: BeautifulSoup 테이블

        Returns:
            {
                'items': {항목명: 금액(백만원)},
                'unit': '백만원',
                'total': 41313.0 (억원),
                'item_count': 10
            }
            or None
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

            if len(cells) < 2:
                continue

            # 항목명 (첫 열)
            item_name = cells[0].get_text(strip=True)

            # 당기 금액 (두 번째 열)
            amount_str = cells[1].get_text(strip=True)

            # ", 판관비" 제거
            item_name = re.sub(r',\s*판관비$', '', item_name)

            # 숫자 추출
            amount_clean = re.sub(r'[^\d-]', '', amount_str)

            if not item_name or not amount_clean:
                continue

            # 헤더 제외
            if item_name in ['과목', '당기', '전기', '공시금액', '계정과목', '항목']:
                continue

            # 길이 체크 (너무 짧은 항목 제외)
            if len(item_name) < 2:
                continue

            try:
                amount = float(amount_clean)

                # 최소 임계값
                min_threshold = {
                    '백만원': 10,
                    '천원': 10_000,
                    '원': 100_000_000
                }.get(unit, 10)

                if abs(amount) <= min_threshold:
                    continue

                # 합계 항목 체크
                is_total = re.match(r'^(합|총|소)\s*계$', item_name.strip())
                is_sga_total = item_name.strip() in [
                    '판매비와관리비', '판매비와 관리비',
                    '판매 및 일반관리비', '판매비 및 일반관리비'
                ]

                if is_total or is_sga_total:
                    # 합계 → 억원 변환
                    total_amount = self._convert_to_eokwon(amount, unit)
                else:
                    # 일반 항목 → 원래 단위 유지
                    items[item_name] = amount

            except ValueError:
                continue

        # 3. 검증
        if not items:
            return None

        # 합계가 없으면 항목들의 합으로 계산
        if total_amount == 0:
            total_amount = sum(items.values())
            total_amount = self._convert_to_eokwon(total_amount, unit)

        return {
            'items': items,
            'unit': unit,
            'total': total_amount,
            'item_count': len(items)
        }

    def verify_ofs(self, crawled_total: float, corp_name: str, year: int = 2024) -> Dict:
        """
        크롤링한 금액 vs DART API OFS 검증

        Args:
            crawled_total: 크롤링한 합계 (억원)
            corp_name: 기업명
            year: 사업연도

        Returns:
            {
                'match': bool,
                'crawled': 41313.0,
                'dart_ofs': 41313.0,
                'error_rate': 0.00,
                'grade': 'A',
                'fs_type': 'OFS'|'CFS'|'UNKNOWN'
            }
        """

        try:
            from umis_rag.utils.dart_api import DARTClient

            client = DARTClient()

            # DART API OFS 조회
            dart_ofs = client.get_sga_total(corp_name, year, fs_div='OFS')

            if not dart_ofs or dart_ofs <= 0:
                return {
                    'match': False,
                    'crawled': crawled_total,
                    'dart_ofs': None,
                    'error_rate': 999.0,
                    'grade': 'UNKNOWN',
                    'fs_type': 'UNKNOWN'
                }

            # 오차율 계산
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

            # FS 타입 판정
            if error_rate <= 1.0:
                fs_type = 'OFS'
            elif error_rate > 50:
                fs_type = 'CFS'  # 크게 차이나면 CFS
            else:
                fs_type = 'UNKNOWN'

            return {
                'match': error_rate <= 1.0,
                'crawled': crawled_total,
                'dart_ofs': dart_ofs,
                'error_rate': error_rate,
                'grade': grade,
                'fs_type': fs_type
            }

        except Exception as e:
            print(f"  ⚠️ OFS 검증 실패: {e}")

            return {
                'match': False,
                'crawled': crawled_total,
                'dart_ofs': None,
                'error_rate': 999.0,
                'grade': 'UNKNOWN',
                'fs_type': 'UNKNOWN'
            }

    @staticmethod
    def _convert_to_eokwon(amount: float, unit: str) -> float:
        """단위 → 억원 변환"""
        conversion = {
            '백만원': 100,
            '천원': 100_000,
            '원': 100_000_000
        }
        return amount / conversion.get(unit, 100)


# 편의 함수
def crawl_sga_for_company(
    corp_name: str,
    rcept_no: str,
    dcm_no: Optional[str] = None,
    headless: bool = True
) -> Dict:
    """
    간편 크롤링 함수

    Args:
        corp_name: 기업명
        rcept_no: 사업보고서 접수번호
        dcm_no: 감사보고서 dcmNo (선택)
        headless: 브라우저 숨김 모드

    Returns:
        판관비 데이터 딕셔너리

    Example:
        result = crawl_sga_for_company('이마트', '20250318000688')

        if result['success']:
            print(f"✅ {result['total']:.1f}억원 (등급: {result['grade']})")
        else:
            print(f"❌ {result['error']}")
    """

    crawler = DARTCrawlerSelenium(headless=headless)

    return crawler.crawl_sga(
        corp_name=corp_name,
        rcept_no=rcept_no,
        dcm_no=dcm_no,
        verify_ofs=True
    )





