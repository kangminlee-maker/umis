"""
DART Robust 크롤러 v2.0 (Bot 탐지 우회)

목적:
- JavaScript 목차 데이터 파싱을 통한 정확한 섹션 추출
- Bot 탐지 우회 (User-Agent 랜덤화, Rate limiting, Session 관리)
- 높은 성공률과 안정성

핵심 발견:
- DART는 HTML에 JavaScript로 목차 데이터(treeData) 포함
- "판매비와 관리비 - 별도" 섹션 파라미터: dcmNo, eleId, offset, length
- viewer.do API로 직접 접근 가능

작성일: 2025-11-16
버전: v2.0 (Robust)
"""

import requests
from bs4 import BeautifulSoup
import re
import time
import random
import json
from typing import Dict, List, Optional
from pathlib import Path
import hashlib


class DARTCrawlerRobust:
    """
    Robust DART 크롤러 (Bot 탐지 우회)
    
    Features:
    1. JavaScript 목차 데이터 파싱
    2. Bot 탐지 우회 (User-Agent, Rate limiting, Session)
    3. 자동 재시도 (지수 백오프)
    4. 캐싱 (중복 요청 방지)
    5. OFS/CFS 자동 검증
    """
    
    # User-Agent 리스트 (실제 브라우저 모방)
    USER_AGENTS = [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0'
    ]
    
    def __init__(
        self,
        cache_dir: Optional[str] = None,
        min_delay: float = 2.0,
        max_delay: float = 5.0,
        timeout: int = 30,
        max_retries: int = 3
    ):
        """
        Args:
            cache_dir: 캐시 디렉토리 (None이면 캐싱 안 함)
            min_delay: 최소 요청 간격 (초)
            max_delay: 최대 요청 간격 (초)
            timeout: 요청 타임아웃 (초)
            max_retries: 최대 재시도 횟수
        """
        
        self.base_url = "https://dart.fss.or.kr"
        self.cache_dir = Path(cache_dir) if cache_dir else None
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Session 생성 (쿠키 유지)
        self.session = requests.Session()
        
        # 캐시 디렉토리 생성
        if self.cache_dir:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # 마지막 요청 시간
        self.last_request_time = 0
    
    def _get_headers(self) -> Dict[str, str]:
        """랜덤 헤더 생성 (실제 브라우저 모방)"""
        
        return {
            'User-Agent': random.choice(self.USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        }
    
    def _rate_limit(self):
        """Rate limiting (요청 간 랜덤 지연)"""
        
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        
        if elapsed < self.min_delay:
            delay = random.uniform(self.min_delay, self.max_delay)
            time.sleep(delay)
        
        self.last_request_time = time.time()
    
    def _get_cache_path(self, key: str) -> Optional[Path]:
        """캐시 파일 경로"""
        
        if not self.cache_dir:
            return None
        
        # MD5 해시로 파일명 생성
        hash_key = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{hash_key}.json"
    
    def _load_from_cache(self, key: str) -> Optional[Dict]:
        """캐시에서 로드"""
        
        cache_path = self._get_cache_path(key)
        
        if cache_path and cache_path.exists():
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        
        return None
    
    def _save_to_cache(self, key: str, data: Dict):
        """캐시에 저장"""
        
        cache_path = self._get_cache_path(key)
        
        if cache_path:
            try:
                with open(cache_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            except:
                pass
    
    def _request_with_retry(
        self,
        url: str,
        params: Optional[Dict] = None,
        max_retries: Optional[int] = None
    ) -> requests.Response:
        """재시도 로직을 포함한 HTTP 요청 (지수 백오프)"""
        
        if max_retries is None:
            max_retries = self.max_retries
        
        for attempt in range(max_retries):
            try:
                # Rate limiting
                self._rate_limit()
                
                # 요청
                headers = self._get_headers()
                
                # Referer 추가 (첫 요청이 아닌 경우)
                if attempt > 0 or params:
                    headers['Referer'] = self.base_url
                
                response = self.session.get(
                    url,
                    params=params,
                    headers=headers,
                    timeout=self.timeout
                )
                
                # 성공
                if response.status_code == 200:
                    return response
                
                # 429 (Too Many Requests) - 긴 지연
                if response.status_code == 429:
                    wait_time = (2 ** attempt) * 5  # 5, 10, 20초
                    print(f"  ⚠️ Rate limit (429), {wait_time}초 대기 중...")
                    time.sleep(wait_time)
                    continue
                
                # 503 (Service Unavailable) - 재시도
                if response.status_code == 503:
                    wait_time = (2 ** attempt) * 2  # 2, 4, 8초
                    print(f"  ⚠️ Service unavailable (503), {wait_time}초 대기 중...")
                    time.sleep(wait_time)
                    continue
                
                # 기타 오류
                print(f"  ❌ HTTP {response.status_code}")
                
            except requests.exceptions.Timeout:
                print(f"  ⚠️ Timeout (시도 {attempt + 1}/{max_retries})")
                time.sleep(2 ** attempt)  # 1, 2, 4초
                
            except Exception as e:
                print(f"  ⚠️ 오류: {e} (시도 {attempt + 1}/{max_retries})")
                time.sleep(2 ** attempt)
        
        raise Exception(f"최대 재시도 횟수 초과 ({max_retries}회)")
    
    def fetch_toc_data(self, rcept_no: str) -> Dict[str, List[Dict]]:
        """
        사업보고서 목차 데이터 추출
        
        Args:
            rcept_no: 사업보고서 접수번호
        
        Returns:
            {
                'all_sections': [
                    {
                        'text': '주석 - 33. 판매비와 관리비 - 별도',
                        'rcpNo': '...',
                        'dcmNo': '...',
                        'eleId': '...',
                        'offset': '...',
                        'length': '...',
                        ...
                    },
                    ...
                ]
            }
        """
        
        print(f"\n[목차 데이터 추출]")
        print("=" * 70)
        
        # 캐시 확인
        cache_key = f"toc_{rcept_no}"
        cached = self._load_from_cache(cache_key)
        
        if cached:
            print(f"  ✓ 캐시에서 로드")
            return cached
        
        # 사업보고서 메인 페이지
        url = f"{self.base_url}/dsaf001/main.do"
        params = {'rcpNo': rcept_no}
        
        print(f"  URL: {url}")
        print(f"  rcpNo: {rcept_no}")
        
        try:
            response = self._request_with_retry(url, params)
            
            print(f"  ✓ HTML 다운로드 완료 ({len(response.text):,}자)")
            
            # HTML 파싱
            html = response.text
            
            # JavaScript 목차 데이터 추출
            sections = self._parse_toc_from_html(html)
            
            result = {'all_sections': sections}
            
            # 캐시 저장
            self._save_to_cache(cache_key, result)
            
            print(f"  ✓ {len(sections)}개 섹션 추출 완료")
            
            return result
            
        except Exception as e:
            print(f"  ❌ 목차 추출 실패: {e}")
            return {'all_sections': []}
    
    def _parse_toc_from_html(self, html: str) -> List[Dict]:
        """HTML에서 JavaScript 목차 데이터 파싱 (node1, node2, node3 모두 지원)"""
        
        sections = []
        
        lines = html.split('\n')
        
        # node1, node2, node3 모두 파싱
        current_node = None
        
        for line in lines:
            line = line.strip()
            
            # 새로운 node 시작 (node1, node2, node3 모두)
            if re.match(r'var node[123] = \{\}', line):
                if current_node and current_node.get('text'):
                    # 필수 필드가 있는지 확인
                    required = ['text', 'rcpNo', 'dcmNo', 'eleId']
                    if all(current_node.get(k) for k in required):
                        sections.append(current_node)
                current_node = {}
            
            # node 속성 추출 (node1, node2, node3 모두)
            if current_node is not None:
                # node[123]['text'] = "..."
                text_match = re.search(r"node[123]\['text'\]\s*=\s*\"([^\"]+)\"", line)
                if text_match:
                    current_node['text'] = text_match.group(1)
                
                # node[123]['rcpNo'] = "..."
                rcpno_match = re.search(r"node[123]\['rcpNo'\]\s*=\s*\"([^\"]+)\"", line)
                if rcpno_match:
                    current_node['rcpNo'] = rcpno_match.group(1)
                
                # node[123]['dcmNo'] = "..."
                dcmno_match = re.search(r"node[123]\['dcmNo'\]\s*=\s*\"([^\"]+)\"", line)
                if dcmno_match:
                    current_node['dcmNo'] = dcmno_match.group(1)
                
                # node[123]['eleId'] = "..."
                eleid_match = re.search(r"node[123]\['eleId'\]\s*=\s*\"([^\"]+)\"", line)
                if eleid_match:
                    current_node['eleId'] = eleid_match.group(1)
                
                # node[123]['offset'] = "..."
                offset_match = re.search(r"node[123]\['offset'\]\s*=\s*\"([^\"]+)\"", line)
                if offset_match:
                    current_node['offset'] = offset_match.group(1)
                
                # node[123]['length'] = "..."
                length_match = re.search(r"node[123]\['length'\]\s*=\s*\"([^\"]+)\"", line)
                if length_match:
                    current_node['length'] = length_match.group(1)
                
                # node[123]['dtd'] = "..."
                dtd_match = re.search(r"node[123]\['dtd'\]\s*=\s*\"([^\"]+)\"", line)
                if dtd_match:
                    current_node['dtd'] = dtd_match.group(1)
        
        # 마지막 node 추가
        if current_node and current_node.get('text'):
            required = ['text', 'rcpNo', 'dcmNo', 'eleId']
            if all(current_node.get(k) for k in required):
                sections.append(current_node)
        
        return sections
    
    def find_sga_section(self, toc_data: Dict) -> Optional[Dict]:
        """
        판매비와 관리비 섹션 찾기 (여러 패턴 지원)
        
        Args:
            toc_data: fetch_toc_data() 결과
        
        Returns:
            섹션 정보 or None
        """
        
        sections = toc_data.get('all_sections', [])
        
        # 우선순위 1: "판매비" + "별도" 키워드 (이마트 패턴)
        for section in sections:
            text = section.get('text', '')
            
            if '판매비' in text and '별도' in text:
                # "연결" 제외
                if '연결' not in text:
                    return section
        
        # 우선순위 2: "재무제표 주석" - 별도/개별 (삼성전자 패턴)
        # 번호가 있는 "재무제표 주석" (예: "5. 재무제표 주석")
        for section in sections:
            text = section.get('text', '')
            
            # "재무제표 주석" 또는 "재무제표주석"
            if ('재무제표' in text and '주석' in text) or '재무제표주석' in text:
                # "연결" 제외
                if '연결' not in text:
                    # 섹션에 특별 플래그 추가
                    section['is_notes'] = True
                    section['needs_subsection_search'] = True  # 하위 섹션 검색 필요
                    return section
        
        # 우선순위 3: "판매비" 또는 "관리비" 키워드만 (넓게 검색)
        for section in sections:
            text = section.get('text', '')
            
            if '판매비' in text or '관리비' in text:
                if '연결' not in text:
                    return section
        
        return None
    
    def fetch_section_content(self, section: Dict) -> Optional[str]:
        """
        섹션 내용 다운로드 (viewer.do API)
        
        Args:
            section: 섹션 정보 (rcpNo, dcmNo, eleId, offset, length, dtd)
        
        Returns:
            HTML 내용 or None
        """
        
        # 필수 파라미터 확인
        required = ['rcpNo', 'dcmNo', 'eleId', 'offset', 'length', 'dtd']
        if not all(section.get(k) for k in required):
            return None
        
        # 캐시 확인
        cache_key = f"section_{section['rcpNo']}_{section['dcmNo']}_{section['eleId']}"
        cached = self._load_from_cache(cache_key)
        
        if cached:
            return cached.get('content')
        
        # viewer.do API
        url = f"{self.base_url}/report/viewer.do"
        params = {
            'rcpNo': section['rcpNo'],
            'dcmNo': section['dcmNo'],
            'eleId': section['eleId'],
            'offset': section['offset'],
            'length': section['length'],
            'dtd': section['dtd']
        }
        
        try:
            response = self._request_with_retry(url, params)
            
            content = response.text
            
            # 캐시 저장
            self._save_to_cache(cache_key, {'content': content})
            
            return content
            
        except Exception as e:
            print(f"  ❌ 섹션 다운로드 실패: {e}")
            return None
    
    def parse_sga_table(self, html: str) -> Optional[Dict]:
        """
        판관비 HTML에서 테이블 파싱 (당기 데이터만)
        
        여러 패턴 지원:
        1. 이마트 패턴: 단일 섹션, 단순 테이블
        2. 삼성전자 패턴: 재무제표 주석 내, "계정과목|당기|전기" 구조
        
        Returns:
            {
                'items': {항목명: 금액},
                'unit': '백만원' or '천원',
                'total': 41313.0 (억원)
            }
        """
        
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text()
        
        # 단위 추출
        unit_match = re.search(r'단위\s*[:：]\s*(백만원|천원|원)', text)
        unit = unit_match.group(1) if unit_match else '백만원'
        
        # 테이블 찾기
        tables = soup.find_all('table')
        
        if not tables:
            return None
        
        items = {}
        total_amount = 0
        
        # 판매비와관리비 테이블 찾기 (여러 패턴)
        target_table = None
        is_account_format = False  # "계정과목|당기|전기" 형식인지
        
        # 패턴 1: "계정과목|당기|전기" 3열 구조 + 급여 항목 (삼성전자 패턴)
        # 전체 HTML에서 이 조건을 만족하는 모든 테이블을 찾고, 가장 큰 합계 선택
        
        candidate_tables = []
        
        for table in tables:
            table_text = table.get_text()
            rows = table.find_all('tr')
            
            # 조건: 15행 이상 + "당기" + "급여"
            if len(rows) >= 15 and '당기' in table_text and '급여' in table_text:
                # 3열 구조 확인
                first_row = rows[0]
                cells = first_row.find_all(['td', 'th'])
                
                if len(cells) == 3:
                    # 헤더 확인 (공백 제거 후 비교)
                    header_texts = [c.get_text(strip=True).replace(' ', '') for c in cells]
                    has_account = any('과목' in h for h in header_texts)
                    has_current = any('당기' in h for h in header_texts)
                    
                    if has_account and has_current:
                        # 합계 계산 (두 번째 열 = 당기)
                        table_total = 0
                        
                        for row in rows:
                            row_cells = row.find_all(['td', 'th'])
                            
                            if len(row_cells) == 3:
                                item = row_cells[0].get_text(strip=True)
                                amount_str = row_cells[1].get_text(strip=True)
                                
                                if '합계' in item or '소계' in item or '총계' in item:
                                    amount_clean = re.sub(r'[^\d-]', '', amount_str)
                                    if amount_clean:
                                        try:
                                            table_total = float(amount_clean)
                                        except:
                                            pass
                        
                        if table_total > 0:
                            candidate_tables.append((table, table_total))
        
        # 합계가 가장 큰 테이블 선택 (판관비가 가장 큼)
        if candidate_tables:
            candidate_tables.sort(key=lambda x: x[1], reverse=True)
            target_table = candidate_tables[0][0]
            is_account_format = True
        
        # 패턴 2: "당기" 테이블 다음 (이마트 패턴)
        if not target_table:
            for i, table in enumerate(tables):
                table_text = table.get_text()
                
                # "당기" 헤더 테이블
                if '당기' in table_text and '단위' in table_text:
                    # 다음 테이블이 실제 데이터
                    if i + 1 < len(tables):
                        next_table = tables[i + 1]
                        next_rows = next_table.find_all('tr')
                        
                        # 10행 이상이어야
                        if len(next_rows) >= 10:
                            target_table = next_table
                            break
        
        # 패턴 3: 모든 테이블 시도
        if not target_table:
            # 가장 긴 테이블 선택
            longest_table = max(tables, key=lambda t: len(t.find_all('tr')))
            if len(longest_table.find_all('tr')) >= 10:
                target_table = longest_table
        
        if not target_table:
            return None
        
        tables_to_parse = [target_table]
        
        for table in tables_to_parse:
            rows = table.find_all('tr')
            
            # 헤더 행 분석 (어떤 형식인지 파악)
            header_row = None
            당기_col_idx = None
            
            for row_idx, row in enumerate(rows[:3]):  # 처음 3행 내에서 헤더 찾기
                cells = row.find_all(['td', 'th'])
                
                for cell_idx, cell in enumerate(cells):
                    cell_text = cell.get_text(strip=True)
                    
                    # "당기" 헤더 찾기
                    if cell_text == '당기' or cell_text.replace(' ', '') == '당기':
                        header_row = row_idx
                        당기_col_idx = cell_idx
                        break
                
                if 당기_col_idx is not None:
                    break
            
            # "계정과목|당기|전기" 형식 (삼성전자)
            if 당기_col_idx is not None:
                for row_idx, row in enumerate(rows):
                    # 헤더 행 스킵
                    if row_idx == header_row:
                        continue
                    
                    cells = row.find_all(['td', 'th'])
                    
                    if len(cells) <= 당기_col_idx:
                        continue
                    
                    # 항목명 (첫 열)
                    item_name = cells[0].get_text(strip=True)
                    
                    # 당기 금액
                    amount_str = cells[당기_col_idx].get_text(strip=True)
                    
                    # 파싱
                    if not item_name or not amount_str:
                        continue
                    
                    # 헤더 제외
                    if item_name in ['과목', '계정과목', '당기', '전기', '공시금액']:
                        continue
                    
                    # 숫자 추출
                    amount_clean = re.sub(r'[^\d-]', '', amount_str)
                    
                    if not amount_clean:
                        continue
                    
                    try:
                        amount = float(amount_clean)
                        
                        # 최소 임계값
                        min_threshold = {'백만원': 10, '천원': 10000, '원': 100000000}.get(unit, 10)
                        
                        if abs(amount) <= min_threshold:
                            continue
                        
                        # 합계 체크
                        is_total = re.match(r'^(합|총|소)\s*계$', item_name.strip())
                        is_sga_total = item_name.strip() in ['판매비와관리비', '판매비와 관리비']
                        
                        if is_total or is_sga_total:
                            total_amount = self._convert_to_eokwon(amount, unit)
                        else:
                            items[item_name] = amount
                    
                    except ValueError:
                        continue
            
            # 기존 파싱 방식 (이마트 패턴)
            else:
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    
                    if len(cells) < 2:
                        continue
                    
                    # 항목명 (첫 열)
                    item_name = cells[0].get_text(strip=True)
                    
                    # 두 번째 열 (당기 금액)
                    amount_str = cells[1].get_text(strip=True)
                    
                    # ", 판관비" 제거
                    item_name = re.sub(r',\s*판관비$', '', item_name)
                    
                    # 숫자 추출
                    amount_clean = re.sub(r'[^\d-]', '', amount_str)
                    
                    if not item_name or not amount_clean:
                        continue
                    
                    # 헤더 제외
                    if item_name in ['과목', '당기', '전기', '공시금액', '계정과목']:
                        continue
                    
                    try:
                        amount = float(amount_clean)
                        
                        # 최소 임계값
                        min_threshold = {'백만원': 10, '천원': 10000, '원': 100000000}.get(unit, 10)
                        
                        if abs(amount) <= min_threshold:
                            continue
                        
                        # 합계 항목 체크
                        is_total = re.match(r'^(합|총|소)\s*계$', item_name.strip())
                        is_sga_total = item_name.strip() in [
                            '판매비와관리비', '판매비와 관리비',
                            '판매 및 일반관리비'
                        ]
                        
                        if is_total or is_sga_total:
                            # 합계 → 억원 변환
                            total_amount = self._convert_to_eokwon(amount, unit)
                        else:
                            # 일반 항목
                            items[item_name] = amount
                    
                    except ValueError:
                        continue
        
        # 검증
        if not items:
            return None
        
        # 합계가 없으면 항목들의 합으로 계산
        if total_amount == 0:
            total_amount = sum(items.values())
            total_amount = self._convert_to_eokwon(total_amount, unit)
        
        return {
            'items': items,
            'unit': unit,
            'total': total_amount
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
    
    def crawl_sga(
        self,
        corp_name: str,
        rcept_no: str,
        verify_ofs: bool = True,
        year: int = 2024
    ) -> Dict:
        """
        판관비 크롤링 (전체 파이프라인)
        
        Args:
            corp_name: 기업명
            rcept_no: 사업보고서 접수번호
            verify_ofs: OFS 검증 여부
            year: 사업연도
        
        Returns:
            {
                'success': bool,
                'corp_name': str,
                'total': float,
                'items': {...},
                'grade': str,
                ...
            }
        """
        
        print(f"\n[DART Robust 크롤링]")
        print("=" * 70)
        print(f"기업: {corp_name}")
        print(f"접수번호: {rcept_no}")
        
        try:
            # 1. 목차 데이터 추출
            print(f"\n[1/4] 목차 데이터 추출 중...")
            toc_data = self.fetch_toc_data(rcept_no)
            
            if not toc_data['all_sections']:
                return {
                    'success': False,
                    'error': '목차 데이터를 추출할 수 없습니다',
                    'corp_name': corp_name
                }
            
            # 2. 판관비 섹션 찾기
            print(f"\n[2/4] 판관비 섹션 찾는 중...")
            sga_section = self.find_sga_section(toc_data)
            
            if not sga_section:
                return {
                    'success': False,
                    'error': '판매비와 관리비 - 별도 섹션을 찾을 수 없습니다',
                    'corp_name': corp_name
                }
            
            print(f"  ✓ 발견: {sga_section['text']}")
            print(f"  dcmNo: {sga_section['dcmNo']}")
            print(f"  eleId: {sga_section['eleId']}")
            
            # 3. 섹션 내용 다운로드
            print(f"\n[3/4] 섹션 내용 다운로드 중...")
            html_content = self.fetch_section_content(sga_section)
            
            if not html_content:
                return {
                    'success': False,
                    'error': '섹션 내용을 다운로드할 수 없습니다',
                    'corp_name': corp_name
                }
            
            print(f"  ✓ 다운로드 완료 ({len(html_content):,}자)")
            
            # 4. 테이블 파싱
            print(f"\n[4/4] 테이블 파싱 중...")
            parsed = self.parse_sga_table(html_content)
            
            if not parsed:
                return {
                    'success': False,
                    'error': '테이블 파싱 실패',
                    'corp_name': corp_name
                }
            
            print(f"  ✓ {len(parsed['items'])}개 항목 추출")
            print(f"  ✓ 합계: {parsed['total']:,.1f}억원")
            
            # 5. OFS 검증 (선택)
            grade = 'UNKNOWN'
            fs_type = 'UNKNOWN'
            dart_ofs = None
            
            if verify_ofs:
                print(f"\n[검증] OFS 검증 중...")
                
                try:
                    from umis_rag.utils.dart_api import DARTClient
                    
                    client = DARTClient()
                    dart_ofs = client.get_sga_total(corp_name, year, fs_div='OFS')
                    
                    if dart_ofs and dart_ofs > 0:
                        error_rate = abs(parsed['total'] - dart_ofs) / dart_ofs * 100
                        
                        # 등급 판정
                        if error_rate <= 5.0:
                            grade = 'A'
                        elif error_rate <= 10.0:
                            grade = 'B'
                        elif error_rate <= 20.0:
                            grade = 'C'
                        else:
                            grade = 'D'
                        
                        # FS 타입
                        if error_rate <= 1.0:
                            fs_type = 'OFS'
                        elif error_rate > 50:
                            fs_type = 'CFS'
                        else:
                            fs_type = 'UNKNOWN'
                        
                        print(f"  ✓ DART OFS: {dart_ofs:,.1f}억원")
                        print(f"  ✓ 오차율: {error_rate:.2f}%")
                        print(f"  ✓ 등급: {grade}")
                        print(f"  ✓ 재무제표: {fs_type}")
                
                except Exception as e:
                    print(f"  ⚠️ OFS 검증 실패: {e}")
            
            # 결과 반환
            return {
                'success': True,
                'source': 'dart_robust',
                'corp_name': corp_name,
                'year': year,
                'rcept_no': rcept_no,
                'items': parsed['items'],
                'total': parsed['total'],
                'unit': parsed['unit'],
                'fs_type': fs_type,
                'grade': grade,
                'dart_ofs': dart_ofs,
                'section': sga_section
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


# 편의 함수
def crawl_sga_robust(
    corp_name: str,
    rcept_no: str,
    cache_dir: Optional[str] = '/tmp/dart_cache',
    verify_ofs: bool = True
) -> Dict:
    """
    간편 크롤링 함수 (Robust)
    
    Example:
        result = crawl_sga_robust('이마트', '20250318000688')
        
        if result['success']:
            print(f"✅ {result['total']:.1f}억원 (등급: {result['grade']})")
    """
    
    crawler = DARTCrawlerRobust(cache_dir=cache_dir)
    
    return crawler.crawl_sga(
        corp_name=corp_name,
        rcept_no=rcept_no,
        verify_ofs=verify_ofs
    )

