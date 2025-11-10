"""
Value Sources

구체적 값 제시
- 확정 데이터
- LLM 추정
- 웹 검색
- RAG 벤치마크
- 통계 패턴 값
"""

from typing import Optional, List, Dict, Any
import os

from umis_rag.utils.logger import logger
from ..models import ValueEstimate, SourceType, Context, DistributionType, SoftGuide


class ValueSourceBase:
    """Value Source Base Class"""
    
    def collect(self, question: str, context: Optional[Context] = None) -> List[ValueEstimate]:
        """값 수집"""
        raise NotImplementedError


class DefiniteDataSource(ValueSourceBase):
    """
    확정 데이터
    
    역할:
    -----
    - 프로젝트 데이터에서 확정값
    - confidence 0.95-1.0
    """
    
    def collect(self, question: str, context: Optional[Context] = None) -> List[ValueEstimate]:
        """확정 데이터 수집"""
        
        if not context or not context.project_data:
            return []
        
        estimates = []
        
        # 키워드 매칭 (간단히)
        keywords = self._extract_keywords(question)
        
        for key, value in context.project_data.items():
            # 키 매칭
            if any(kw in key.lower() for kw in keywords):
                estimate = ValueEstimate(
                    source_type=SourceType.DEFINITE_DATA,
                    value=float(value) if isinstance(value, (int, float)) else 0.0,
                    confidence=0.98,  # 완전 확정은 드묾
                    reasoning=f"프로젝트 확정 데이터: {key}",
                    source_detail=f"project_data.{key}",
                    raw_data=value
                )
                
                estimates.append(estimate)
        
        return estimates
    
    def _extract_keywords(self, question: str) -> List[str]:
        """키워드 추출 (간단히)"""
        # 불용어 제거
        stopwords = {'은', '는', '이', '가', '를', '의', '에', '와'}
        words = question.split()
        keywords = [w.lower() for w in words if w not in stopwords and len(w) >= 2]
        return keywords


class LLMEstimationSource(ValueSourceBase):
    """
    LLM 추정
    
    역할:
    -----
    - LLM에게 직접 질문
    - Native Mode (Cursor) or External (API)
    - confidence 0.60-0.90
    """
    
    def __init__(self, llm_mode: str = "native"):
        self.llm_mode = llm_mode
    
    def collect(self, question: str, context: Optional[Context] = None) -> List[ValueEstimate]:
        """LLM 추정"""
        
        if self.llm_mode == "skip":
            return []
        
        # 간단한 사실 질문만 (복잡한 건 Tier 2에서)
        if not self._is_simple_factual(question):
            return []
        
        # TODO: 실제 LLM 호출
        # 현재는 스킵
        logger.info(f"  [LLM] 스킵 (Native Mode는 interactive 필요)")
        
        return []
    
    def _is_simple_factual(self, question: str) -> bool:
        """간단한 사실 질문인가?"""
        factual_keywords = ['인구', '면적', 'gdp', '수도']
        return any(kw in question.lower() for kw in factual_keywords)


class WebSearchSource(ValueSourceBase):
    """
    웹 검색 (v7.6.2)
    
    역할:
    -----
    - 웹에서 최신 데이터 검색
    - 여러 결과에서 숫자 추출
    - consensus 알고리즘 (다수 일치)
    - confidence 0.60-0.80
    
    구현:
    -----
    - DuckDuckGo (무료, API 키 불필요)
    - 숫자 추출 + 단위 파싱
    - 3-5개 결과 조합
    """
    
    def __init__(self):
        """
        초기화 (v7.6.2 - 동적 엔진 선택)
        
        .env 설정:
          WEB_SEARCH_ENGINE=duckduckgo (기본, 무료)
          또는
          WEB_SEARCH_ENGINE=google
          GOOGLE_API_KEY=your-key
          GOOGLE_SEARCH_ENGINE_ID=your-id
        """
        from umis_rag.core.config import settings
        
        self.enabled = settings.web_search_enabled
        self.engine = settings.web_search_engine.lower()
        
        # 검색 엔진별 초기화
        if self.engine == "google":
            self._init_google()
        else:  # duckduckgo (기본)
            self._init_duckduckgo()
    
    def _init_duckduckgo(self):
        """DuckDuckGo 초기화"""
        try:
            from duckduckgo_search import DDGS
            self.ddgs = DDGS()
            self.has_search = True
            logger.info("  [Web] DuckDuckGo 준비 (무료)")
        except ImportError:
            logger.warning("  [Web] duckduckgo-search 패키지 없음 (pip install ddgs)")
            self.has_search = False
    
    def _init_google(self):
        """Google Custom Search 초기화"""
        from umis_rag.core.config import settings
        
        try:
            from googleapiclient.discovery import build
            
            if not settings.google_api_key or not settings.google_search_engine_id:
                logger.warning("  [Web] Google API 키 또는 Search Engine ID 없음")
                logger.warning("  [Web] .env에 GOOGLE_API_KEY, GOOGLE_SEARCH_ENGINE_ID 설정 필요")
                self.has_search = False
                return
            
            self.google_service = build(
                "customsearch",
                "v1",
                developerKey=settings.google_api_key
            )
            self.google_engine_id = settings.google_search_engine_id
            self.has_search = True
            
            logger.info("  [Web] Google Custom Search 준비 (유료, 고품질)")
        
        except ImportError:
            logger.warning("  [Web] google-api-python-client 패키지 없음")
            logger.warning("  [Web] pip install google-api-python-client")
            self.has_search = False
        
        except Exception as e:
            logger.warning(f"  [Web] Google 초기화 실패: {e}")
            self.has_search = False
    
    def collect(self, question: str, context: Optional[Context] = None) -> List[ValueEstimate]:
        """
        웹 검색
        
        프로세스:
        1. 검색 쿼리 구성
        2. DuckDuckGo 검색 (top 5)
        3. 결과에서 숫자 추출
        4. consensus 확인 (여러 출처 일치)
        5. ValueEstimate 반환
        """
        if not self.has_search or not self.enabled:
            logger.info(f"  [Web] 비활성화")
            return []
        
        # 사실 질문만 (수치 질문)
        if not self._is_numerical_question(question):
            logger.info(f"  [Web] 수치 질문 아님 → 스킵")
            return []
        
        logger.info(f"  [Web] 검색 시작 (엔진: {self.engine})")
        
        try:
            # 검색 쿼리 구성
            search_query = self._build_search_query(question, context)
            logger.info(f"    쿼리: {search_query}")
            
            # 엔진별 검색 실행
            if self.engine == "google":
                results = self._search_google(search_query)
            else:  # duckduckgo
                results = self._search_duckduckgo(search_query)
            
            if not results:
                logger.info(f"    검색 결과 없음")
                return []
            
            logger.info(f"    {len(results)}개 결과 발견")
            
            # 숫자 추출
            extracted_numbers = self._extract_numbers_from_results(
                results, question
            )
            
            if not extracted_numbers:
                logger.info(f"    숫자 추출 실패 (패턴 매칭 안됨)")
                # 디버깅: 결과 샘플 출력
                if results:
                    sample = results[0]
                    logger.info(f"    샘플: {sample.get('title', '')[:50]}...")
                return []
            
            logger.info(f"    {len(extracted_numbers)}개 숫자 추출됨")
            
            # Consensus 확인 (여러 출처에서 유사한 값)
            consensus = self._find_consensus(extracted_numbers)
            
            if consensus:
                logger.info(f"    Consensus: {consensus['value']} (신뢰도: {consensus['confidence']:.2f})")
                
                return [ValueEstimate(
                    source_type=SourceType.WEB_SEARCH,
                    value=consensus['value'],
                    confidence=consensus['confidence'],
                    reasoning=f"웹 검색 consensus ({consensus['count']}개 출처 일치)",
                    source_detail=f"DuckDuckGo: {search_query}",
                    raw_data={'sources': consensus['sources']}
                )]
            else:
                logger.info(f"    Consensus 없음 (값 분산)")
                return []
        
        except Exception as e:
            logger.warning(f"  [Web] 검색 실패: {e}")
            return []
    
    def _search_duckduckgo(self, query: str) -> list:
        """
        DuckDuckGo 검색 실행
        
        Returns:
            [{'title': str, 'body': str, 'href': str}, ...]
        """
        try:
            results = self.ddgs.text(
                keywords=query,
                max_results=5
            )
            return results if results else []
        
        except Exception as e:
            logger.warning(f"    DuckDuckGo 검색 실패: {e}")
            return []
    
    def _search_google(self, query: str) -> list:
        """
        Google Custom Search 실행
        
        Returns:
            [{'title': str, 'body': str, 'href': str}, ...]
            (DuckDuckGo와 동일한 형식으로 변환)
        """
        try:
            response = self.google_service.cse().list(
                q=query,
                cx=self.google_engine_id,
                num=5
            ).execute()
            
            items = response.get('items', [])
            
            # DuckDuckGo 형식으로 변환
            results = []
            for item in items:
                results.append({
                    'title': item.get('title', ''),
                    'body': item.get('snippet', ''),
                    'href': item.get('link', '')
                })
            
            return results
        
        except Exception as e:
            logger.warning(f"    Google 검색 실패: {e}")
            return []
    
    def _is_numerical_question(self, question: str) -> bool:
        """수치 질문인지 확인"""
        numerical_keywords = [
            '수', '개수', '몇', '얼마', '평균', '비율', '률', '규모', '인구',
            'count', 'how many', 'average', 'rate', 'size', 'population'
        ]
        
        # "얼마인가", "몇인가" 등 질문 형태도 포함
        if '?' in question or '인가' in question:
            return True
        
        return any(kw in question.lower() for kw in numerical_keywords)
    
    def _build_search_query(
        self,
        question: str,
        context: Optional[Context]
    ) -> str:
        """검색 쿼리 구성"""
        
        # Context 추가
        if context:
            parts = []
            
            if context.region:
                parts.append(context.region)
            
            if context.domain and context.domain != "General":
                parts.append(context.domain.replace('_', ' '))
            
            parts.append(question)
            
            query = " ".join(parts)
        else:
            query = question
        
        # "통계" 또는 "데이터" 추가 (정확도 향상)
        if '통계' not in query and 'statistics' not in query.lower():
            query += " 통계"
        
        return query
    
    def _extract_numbers_from_results(
        self,
        results: list,
        question: str
    ) -> list:
        """
        검색 결과에서 숫자 추출 (개선)
        
        Returns:
            [{'value': float, 'source': str, 'context': str}, ...]
        """
        import re
        
        extracted = []
        
        for result in results:
            title = result.get('title', '')
            body = result.get('body', '')
            text = f"{title} {body}"
            source = result.get('href', 'unknown')
            
            # 숫자 패턴 (개선 - 더 유연하게)
            patterns = [
                # 한국어 큰 숫자 (51,740,000명)
                (r'(\d{1,3}(?:,\d{3})+)', r'([조억만천백십]?[원명개갑점호대%]|명|개|원|조|억|만)'),
                
                # 일반 숫자 + 단위
                (r'(\d+(?:\.\d+)?)', r'\s*([조억만천]?[원명개갑점호대%]|%)'),
                
                # 백분율
                (r'(\d+(?:\.\d+)?)', r'%'),
            ]
            
            for num_pattern, unit_pattern in patterns:
                # 숫자와 단위를 함께 찾기
                combined_pattern = num_pattern + r'\s*' + unit_pattern
                matches = re.findall(combined_pattern, text)
                
                for match in matches:
                    if isinstance(match, tuple) and len(match) >= 2:
                        num_str = match[0]
                        unit = match[1] if len(match) > 1 else ""
                    else:
                        num_str = str(match)
                        unit = ""
                    
                    try:
                        # 쉼표 제거
                        num_str = num_str.replace(',', '')
                        
                        # 숫자 변환
                        value = float(num_str)
                        
                        # 한국어 단위 변환
                        if '조' in unit and '억' not in unit:  # 조 단독
                            value *= 1_000_000_000_000
                        elif '억' in unit and '조' not in unit:  # 억 단독
                            value *= 100_000_000
                        elif '만' in unit and '억' not in unit:  # 만 단독
                            value *= 10_000
                        
                        # 백분율 → 비율
                        if '%' in unit or '%' in text[text.find(num_str):text.find(num_str)+20]:
                            if value > 1:  # 백분율 형태
                                value = value / 100
                        
                        # 너무 작거나 너무 큰 값 필터링
                        if value <= 0 or value > 1e18:
                            continue
                        
                        # 맥락 추출
                        num_pos = text.find(num_str)
                        if num_pos >= 0:
                            context_start = max(0, num_pos - 50)
                            context_end = min(len(text), num_pos + 100)
                            context_text = text[context_start:context_end]
                        else:
                            context_text = title[:100] if title else body[:100]
                        
                        extracted.append({
                            'value': value,
                            'unit': unit,
                            'source': source,
                            'context': context_text,
                            'original': f"{num_str} {unit}"
                        })
                    
                    except Exception as e:
                        # 숫자 변환 실패는 무시
                        continue
        
        # 중복 제거 (같은 값)
        unique = []
        seen_values = set()
        
        for item in extracted:
            val = item['value']
            # ±5% 범위로 중복 체크
            is_duplicate = any(abs(val - seen) / max(seen, val) < 0.05 for seen in seen_values)
            
            if not is_duplicate:
                unique.append(item)
                seen_values.add(val)
        
        return unique
    
    def _find_consensus(self, extracted_numbers: list) -> Optional[Dict]:
        """
        Consensus 찾기 (여러 출처에서 유사한 값)
        
        Args:
            extracted_numbers: [{'value': ..., 'source': ...}, ...]
        
        Returns:
            {
                'value': float,
                'confidence': float,
                'count': int,
                'sources': [...]
            } or None
        """
        if len(extracted_numbers) < 2:
            return None
        
        # 값들을 그룹화 (±30% 범위 내면 같은 그룹)
        groups = []
        
        for item in extracted_numbers:
            value = item['value']
            
            # 기존 그룹에 속하는지 확인
            found_group = False
            
            for group in groups:
                group_avg = sum(g['value'] for g in group) / len(group)
                
                # ±30% 범위 내
                if abs(value - group_avg) / group_avg < 0.30:
                    group.append(item)
                    found_group = True
                    break
            
            if not found_group:
                groups.append([item])
        
        # 가장 큰 그룹 찾기
        if not groups:
            return None
        
        largest_group = max(groups, key=len)
        
        # 2개 이상 일치해야 consensus
        if len(largest_group) < 2:
            return None
        
        # 평균 계산
        avg_value = sum(item['value'] for item in largest_group) / len(largest_group)
        
        # Confidence: 일치하는 출처 개수에 비례
        # 2개: 0.60, 3개: 0.70, 4개+: 0.80
        confidence_map = {2: 0.60, 3: 0.70, 4: 0.80, 5: 0.85}
        confidence = confidence_map.get(len(largest_group), 0.85)
        
        return {
            'value': avg_value,
            'confidence': confidence,
            'count': len(largest_group),
            'sources': [item['source'] for item in largest_group]
        }


class RAGBenchmarkSource(ValueSourceBase):
    """
    RAG 벤치마크
    
    역할:
    -----
    - Quantifier.market_benchmarks 활용
    - 도메인 지표 검색
    - confidence 0.50-0.80
    """
    
    def __init__(self):
        """초기화 (Lazy)"""
        self.quantifier = None
        self._initialized = False
    
    def _initialize(self):
        """Lazy 초기화"""
        if self._initialized:
            return
        
        try:
            from umis_rag.agents.quantifier import QuantifierRAG
            self.quantifier = QuantifierRAG()
            logger.info(f"  [RAG] QuantifierRAG 연결 완료")
            self._initialized = True
        except Exception as e:
            logger.warning(f"  [RAG] QuantifierRAG 로드 실패: {e}")
            self._initialized = True
    
    def collect(self, question: str, context: Optional[Context] = None) -> List[ValueEstimate]:
        """RAG 벤치마크 검색"""
        
        self._initialize()
        
        if not self.quantifier:
            return []
        
        # 도메인 지표 질문만
        if not self._is_domain_metric(question):
            return []
        
        logger.info(f"  [RAG] Quantifier 벤치마크 검색")
        
        try:
            # Quantifier.search_benchmark() 호출
            results = self.quantifier.search_benchmark(
                market=question,
                top_k=3
            )
            
            if not results:
                return []
            
            estimates = []
            
            for doc, score in results:
                # 메타데이터에서 값 추출 (다양한 필드 시도)
                value = self._extract_value_from_metadata(doc.metadata, doc.page_content)
                
                if value:
                    estimate = ValueEstimate(
                        source_type=SourceType.RAG_BENCHMARK,
                        value=value,
                        confidence=score * 0.8,  # 유사도 기반, 약간 할인
                        reasoning=f"RAG 벤치마크 (유사도 {score:.2f})",
                        source_detail=doc.metadata.get('metric', 'market_benchmarks'),
                        raw_data=doc.metadata
                    )
                    
                    estimates.append(estimate)
            
            logger.info(f"  [RAG] {len(estimates)}개 벤치마크 발견")
            return estimates
            
        except Exception as e:
            logger.error(f"  [RAG] 검색 실패: {e}")
            return []
    
    def _is_domain_metric(self, question: str) -> bool:
        """도메인 지표 질문인가?"""
        # SaaS, 비즈니스 지표 키워드
        domain_metrics = [
            'churn', 'ltv', 'cac', 'arpu', 'mrr', 'arr',
            '해지율', '이탈률', '전환율', 'conversion',
            '점유율', '성장률', '마진'
        ]
        
        question_lower = question.lower()
        return any(metric in question_lower for metric in domain_metrics)
    
    def _extract_value_from_metadata(self, metadata: Dict, content: str) -> Optional[float]:
        """메타데이터에서 값 추출"""
        
        # 시도 1: global_benchmark.median
        if 'global_benchmark' in metadata:
            global_bench = metadata['global_benchmark']
            if isinstance(global_bench, dict):
                median = global_bench.get('median')
                if median:
                    return self._parse_value(median)
        
        # 시도 2: value 필드
        if 'value' in metadata:
            return self._parse_value(metadata['value'])
        
        # 시도 3: content에서 추출 (간단히)
        # "5-7%" 같은 패턴
        import re
        patterns = [
            r'(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)\s*%',  # "5-7%"
            r'(\d+(?:\.\d+)?)\s*%',  # "6%"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                if len(match.groups()) == 2:  # range
                    min_val = float(match.group(1))
                    max_val = float(match.group(2))
                    return (min_val + max_val) / 2 / 100  # % → 소수
                else:  # single value
                    return float(match.group(1)) / 100
        
        return None
    
    def _parse_value(self, value_raw) -> Optional[float]:
        """값 파싱"""
        # 숫자면 그대로
        if isinstance(value_raw, (int, float)):
            return float(value_raw)
        
        # 문자열이면 파싱 시도
        if isinstance(value_raw, str):
            # "5-7%" → 중앙값 6
            if '-' in value_raw:
                parts = value_raw.replace('%', '').split('-')
                try:
                    min_val = float(parts[0])
                    max_val = float(parts[1])
                    return (min_val + max_val) / 2 / 100  # % → 소수
                except:
                    pass
            
            # "6%" → 0.06
            try:
                val_str = value_raw.replace('%', '').replace(',', '').strip()
                val = float(val_str)
                # % 형태면 100으로 나누기
                if '%' in value_raw:
                    return val / 100
                return val
            except:
                pass
        
        return None


class StatisticalValueSource(ValueSourceBase):
    """
    통계 패턴 값
    
    역할:
    -----
    - 통계 패턴의 대표값 (median or mean)
    - 다른 Value 없을 때만 사용
    - confidence 0.50-0.65
    """
    
    def collect(
        self,
        question: str,
        context: Optional[Context] = None,
        statistical_guide: Optional['SoftGuide'] = None
    ) -> List[ValueEstimate]:
        """통계값 추출"""
        
        if not statistical_guide or not statistical_guide.distribution:
            return []
        
        estimates = []
        
        dist = statistical_guide.distribution
        
        # 분포 타입별 대표값 선택
        if dist.distribution_type == DistributionType.NORMAL:
            # 정규분포 → mean
            if dist.mean:
                estimate = ValueEstimate(
                    source_type=SourceType.STATISTICAL_VALUE,
                    value=dist.mean,
                    confidence=0.70 if (dist.cv and dist.cv < 0.20) else 0.60,
                    reasoning="정규분포 평균값"
                )
                estimates.append(estimate)
        
        elif dist.distribution_type == DistributionType.POWER_LAW:
            # Power Law → median (평균 금지!)
            if dist.percentiles and 'p50' in dist.percentiles:
                estimate = ValueEstimate(
                    source_type=SourceType.STATISTICAL_VALUE,
                    value=dist.percentiles['p50'],
                    confidence=0.60,
                    reasoning="Power Law 중앙값 (평균 사용 금지)"
                )
                estimates.append(estimate)
        
        elif dist.distribution_type == DistributionType.EXPONENTIAL:
            # 지수분포 → median
            if dist.percentiles and 'p50' in dist.percentiles:
                estimate = ValueEstimate(
                    source_type=SourceType.STATISTICAL_VALUE,
                    value=dist.percentiles['p50'],
                    confidence=0.65,
                    reasoning="지수분포 중앙값"
                )
                estimates.append(estimate)
        
        elif dist.distribution_type == DistributionType.BIMODAL:
            # 이봉분포 → 값 제시 못함
            logger.info("  [통계값] 이봉분포 → 세분화 필요")
            return []
        
        return estimates

