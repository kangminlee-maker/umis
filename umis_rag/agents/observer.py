"""
Observer RAG Agent Module

Observer (Albert) 에이전트의 RAG 기반 시장 구조 분석 시스템입니다.

핵심 개념:
-----------
1. **Structure Pattern Matching**: 관찰 → 구조 패턴 매칭
2. **Value Chain Benchmarks**: 유사 산업 가치사슬 참조
3. **Transaction Pattern Recognition**: 거래 패턴 인식
4. **Market Structure Comparison**: 시장 구조 비교

Observer의 핵심 역할:
--------------------
1. 시장 구조 관찰 및 해석
2. 가치사슬 맵핑
3. 거래 패턴 분석
4. 비효율성 발견

RAG Collections:
----------------
- market_structure_patterns: 시장 구조 패턴 (30개)
- value_chain_benchmarks: 가치사슬 벤치마크 (50개)
"""

from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

import sys
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.core.config import settings
from umis_rag.utils.logger import logger


class ObserverRAG:
    """
    Observer (Albert) RAG Agent
    
    역할:
    -----
    - 시장 구조 분석
    - 가치사슬 맵핑
    - 거래 패턴 인식
    - 비효율성 발견
    
    핵심 메서드:
    -----------
    - search_structure_pattern(): 구조 패턴 검색
    - search_value_chain(): 가치사슬 벤치마크 검색
    - search_inefficiency(): 비효율성 패턴 검색
    
    협업:
    -----
    - Validator: 관찰 데이터 검증
    - Quantifier: 구조 정량화
    """
    
    def __init__(self):
        """Observer RAG 에이전트 초기화"""
        logger.info("Observer RAG 에이전트 초기화")
        
        # Embeddings
        self.embeddings = OpenAIEmbeddings(
            model=settings.embedding_model,
            openai_api_key=settings.openai_api_key
        )
        
        # Vector Stores
        try:
            # 1. 시장 구조 패턴
            self.structure_store = Chroma(
                collection_name="market_structure_patterns",
                embedding_function=self.embeddings,
                persist_directory=str(settings.chroma_persist_dir)
            )
            logger.info(f"  ✅ 구조 패턴: {self.structure_store._collection.count()}개")
        except Exception as e:
            logger.warning(f"  ⚠️  구조 패턴 Collection 없음 (구축 필요): {e}")
            self.structure_store = None
        
        try:
            # 2. 가치사슬 벤치마크
            self.chain_store = Chroma(
                collection_name="value_chain_benchmarks",
                embedding_function=self.embeddings,
                persist_directory=str(settings.chroma_persist_dir)
            )
            logger.info(f"  ✅ 가치사슬: {self.chain_store._collection.count()}개")
        except Exception as e:
            logger.warning(f"  ⚠️  가치사슬 Collection 없음 (구축 필요): {e}")
            self.chain_store = None
        
        try:
            # 3. 진화 패턴 (v7.8.0 신규)
            self.evolution_store = Chroma(
                collection_name="historical_evolution_patterns",
                embedding_function=self.embeddings,
                persist_directory=str(settings.chroma_persist_dir)
            )
            logger.info(f"  ✅ 진화 패턴: {self.evolution_store._collection.count()}개")
        except Exception as e:
            logger.warning(f"  ⚠️  진화 패턴 Collection 없음 (구축 필요): {e}")
            self.evolution_store = None
    
    def search_structure_pattern(
        self,
        observations: str,
        top_k: int = 3
    ) -> List[tuple[Document, float]]:
        """
        시장 구조 패턴 검색
        
        사용 시점:
        ----------
        시장을 관찰하고 유사한 구조 패턴을 찾을 때
        
        예시:
        -----
        Input: "공급자-중개-수요자 3단계, 중개 수수료 20%"
        Output: [플랫폼 양면시장, 다단계 유통, ...]
        
        Parameters:
        -----------
        observations: 관찰 내용
        top_k: 반환할 패턴 수
        
        Returns:
        --------
        List of (Document, similarity_score)
        """
        if not self.structure_store:
            logger.warning("  ⚠️  구조 패턴 RAG 미구축")
            return []
        
        logger.info(f"[Observer] 구조 패턴 검색")
        logger.info(f"  관찰: {observations[:100]}...")
        
        results = self.structure_store.similarity_search_with_score(
            observations,
            k=top_k
        )
        
        logger.info(f"  ✅ {len(results)}개 패턴 발견")
        for doc, score in results:
            pattern_name = doc.metadata.get('structure_type', 'Unknown')
            logger.info(f"    - {pattern_name} (유사도: {score:.2f})")
        
        return results
    
    def search_value_chain(
        self,
        industry: str,
        top_k: int = 3
    ) -> List[tuple[Document, float]]:
        """
        가치사슬 벤치마크 검색
        
        사용 시점:
        ----------
        산업의 가치사슬을 파악할 때, 유사 산업 참조
        
        예시:
        -----
        Input: "음악 산업"
        Output: [아티스트→레이블→플랫폼→청취자 (마진 40%/20%/15%), ...]
        
        Parameters:
        -----------
        industry: 산업 이름
        top_k: 반환할 벤치마크 수
        
        Returns:
        --------
        List of (Document, similarity_score)
        """
        if not self.chain_store:
            logger.warning("  ⚠️  가치사슬 RAG 미구축")
            return []
        
        logger.info(f"[Observer] 가치사슬 검색")
        logger.info(f"  산업: {industry}")
        
        results = self.chain_store.similarity_search_with_score(
            industry,
            k=top_k
        )
        
        logger.info(f"  ✅ {len(results)}개 벤치마크 발견")
        for doc, score in results:
            industry_name = doc.metadata.get('industry', 'Unknown')
            logger.info(f"    - {industry_name} (유사도: {score:.2f})")
        
        return results
    
    def search_inefficiency(
        self,
        structure_description: str,
        top_k: int = 3
    ) -> List[tuple[Document, float]]:
        """
        비효율성 패턴 검색
        
        사용 시점:
        ----------
        관찰한 구조에서 비효율성을 찾을 때
        
        예시:
        -----
        Input: "3단계 유통, 각 20% 마진"
        Output: [중개 비효율 패턴, D2C 기회, ...]
        """
        if not self.structure_store:
            return []
        
        logger.info(f"[Observer] 비효율성 패턴 검색")
        
        results = self.structure_store.similarity_search_with_score(
            structure_description,
            k=top_k,
            filter={"type": "inefficiency"}
        )
        
        return results
    
    def analyze_structure_with_rag(
        self,
        observations: str,
        industry: str
    ) -> Dict[str, Any]:
        """
        RAG 기반 구조 분석
        
        프로세스:
        ---------
        1. 구조 패턴 검색 → 유사 구조 파악
        2. 가치사슬 검색 → 벤치마크 참조
        3. 비효율성 검색 → 기회 영역
        
        Returns:
        --------
        구조 분석 결과 + 패턴 매칭 + 벤치마크
        """
        logger.info(f"[Observer] RAG 기반 구조 분석")
        
        result = {
            'structure_patterns': [],
            'value_chain_benchmarks': [],
            'inefficiencies': []
        }
        
        # 1. 구조 패턴
        patterns = self.search_structure_pattern(observations, top_k=2)
        if patterns:
            result['structure_patterns'] = [
                {
                    'pattern': doc.metadata.get('structure_type'),
                    'description': doc.page_content[:200],
                    'confidence': score
                }
                for doc, score in patterns
            ]
        
        # 2. 가치사슬
        chains = self.search_value_chain(industry, top_k=2)
        if chains:
            result['value_chain_benchmarks'] = [
                {
                    'industry': doc.metadata.get('industry'),
                    'chain': doc.metadata.get('chain_structure'),
                    'margins': doc.metadata.get('margins'),
                    'confidence': score
                }
                for doc, score in chains
            ]
        
        # 3. 비효율성
        inefficiencies = self.search_inefficiency(observations, top_k=2)
        if inefficiencies:
            result['inefficiencies'] = [
                {
                    'pattern': doc.metadata.get('inefficiency_type'),
                    'opportunity': doc.page_content[:150],
                    'confidence': score
                }
                for doc, score in inefficiencies
            ]
        
        logger.info("  ✅ RAG 기반 분석 완료")
        return result
    
    def analyze_market_timeline(
        self,
        market: str,
        start_year: int,
        end_year: int,
        focus_areas: List[str] = None
    ) -> Dict[str, Any]:
        """
        시장 시계열 분석 (v7.8.0 신규)
        
        프로세스:
        ---------
        1. Validator: 과거 데이터 수집
        2. Estimator: 누락 데이터 추정
        3. Observer: 사건 분류 및 패턴 분석
        4. Quantifier: 변곡점 감지 및 추세 분석
        
        Args:
            market: 시장 이름
            start_year: 분석 시작 연도
            end_year: 분석 종료 연도
            focus_areas: ['market_size', 'players', 'structure', 'technology']
        
        Returns:
            {
                'events': List[Event],
                'market_size_trend': List[Tuple[int, float]],
                'player_share_evolution': Dict,
                'inflection_points': List[Dict],
                'structural_evolution': Dict,
                'mermaid_charts': Dict[str, str],
                'deliverable_path': str
            }
        """
        logger.info(f"[Observer] 시장 타임라인 분석: {market} ({start_year}-{end_year})")
        
        # Step 1: Validator 협업 - 과거 데이터 수집
        logger.info("  Step 1: Validator 과거 데이터 수집")
        historical_data = self._collect_historical_data_via_validator(
            market, start_year, end_year
        )
        
        # Step 2: 사건 추출 및 분류
        logger.info("  Step 2: 주요 사건 추출")
        events = self._extract_and_classify_events(
            historical_data.get('events', []),
            start_year,
            end_year
        )
        
        # Step 3: Quantifier 협업 - 추세 분석
        logger.info("  Step 3: Quantifier 추세 분석")
        trends = self._analyze_trends_via_quantifier(
            historical_data.get('market_size_by_year', {}),
            historical_data.get('players_by_year', {})
        )
        
        # Step 4: 변곡점 감지
        logger.info("  Step 4: 변곡점 감지")
        inflection_points = self._detect_inflection_points(
            trends.get('market_size', {}).get('yoy', []),
            events
        )
        
        # Step 5: 구조 진화 패턴 분석 (RAG)
        logger.info("  Step 5: 구조 진화 패턴 분석")
        evolution = self._analyze_structural_evolution(
            historical_data.get('hhi_by_year', {}),
            historical_data.get('player_count_by_year', {}),
            events
        )
        
        # Step 6: 시각화
        logger.info("  Step 6: Mermaid 차트 생성")
        charts = self._generate_timeline_visualizations(
            market, events, trends, evolution
        )
        
        # Step 7: Deliverable 생성
        logger.info("  Step 7: Deliverable 생성")
        deliverable_path = self._generate_timeline_deliverable(
            market, start_year, end_year,
            historical_data, events, trends, inflection_points, evolution, charts
        )
        
        logger.info(f"  ✅ 타임라인 분석 완료: {deliverable_path}")
        
        return {
            'events': events,
            'market_size_trend': trends.get('market_size', {}).get('trend', []),
            'player_share_evolution': trends.get('players', {}),
            'inflection_points': inflection_points,
            'structural_evolution': evolution,
            'mermaid_charts': charts,
            'deliverable_path': deliverable_path,
            'data_quality': historical_data.get('data_quality', {})
        }
    
    def _collect_historical_data_via_validator(
        self,
        market: str,
        start_year: int,
        end_year: int
    ) -> Dict[str, Any]:
        """
        Validator 협업: 과거 데이터 수집
        
        Returns:
            {
                'market_size_by_year': {year: {value, source, reliability}, ...},
                'players_by_year': {year: {player: {share, source}, ...}, ...},
                'events': [Event, ...],
                'hhi_by_year': {year: hhi, ...},
                'player_count_by_year': {year: count, ...},
                'data_quality': {...}
            }
        """
        logger.info("    Validator에게 과거 데이터 요청")
        
        # Validator import (필요 시 동적)
        try:
            from umis_rag.agents.validator import get_validator_rag
            validator = get_validator_rag()
            
            # Validator의 search_historical_data() 호출
            if hasattr(validator, 'search_historical_data'):
                data = validator.search_historical_data(
                    market=market,
                    years=range(start_year, end_year + 1)
                )
                logger.info(f"    ✅ Validator 데이터 수집 완료")
                return data
            else:
                logger.warning("    ⚠️ Validator.search_historical_data() 미구현")
                return self._collect_minimal_data(market, start_year, end_year)
        
        except Exception as e:
            logger.warning(f"    ⚠️ Validator 협업 실패: {e}")
            return self._collect_minimal_data(market, start_year, end_year)
    
    def _collect_minimal_data(self, market, start_year, end_year):
        """최소 데이터 (Fallback)"""
        return {
            'market_size_by_year': {},
            'players_by_year': {},
            'events': [],
            'hhi_by_year': {},
            'player_count_by_year': {},
            'data_quality': {'note': 'Minimal data - Validator 미구현'}
        }
    
    def _extract_and_classify_events(
        self,
        raw_events: List[Dict],
        start_year: int,
        end_year: int
    ) -> List[Dict]:
        """
        사건 추출 및 분류
        
        Categories:
        - player: 진입/퇴출/M&A
        - regulation: 규제 변화
        - technology: 기술 도입
        - economic: 경제 환경
        """
        classified_events = []
        
        for event in raw_events:
            year = event.get('year')
            if start_year <= year <= end_year:
                # 카테고리 분류 (키워드 기반)
                event['category'] = self._classify_event_category(event['event'])
                classified_events.append(event)
        
        # 연도순 정렬
        classified_events.sort(key=lambda x: x['year'])
        
        logger.info(f"    ✅ {len(classified_events)}개 사건 분류 완료")
        return classified_events
    
    def _classify_event_category(self, event_text: str) -> str:
        """사건 카테고리 분류 (키워드 기반)"""
        keywords = {
            'player': ['진입', '퇴출', '설립', '파산', '인수', '합병', 'M&A'],
            'regulation': ['규제', '법안', '개정', '제재', '허용'],
            'technology': ['도입', '상용화', '특허', '혁신', '기술'],
            'economic': ['경기', 'COVID', '불황', '호황']
        }
        
        for category, words in keywords.items():
            if any(word in event_text for word in words):
                return category
        
        return 'other'
    
    def _analyze_trends_via_quantifier(
        self,
        market_size_by_year: Dict,
        players_by_year: Dict
    ) -> Dict[str, Any]:
        """
        Quantifier 협업: 추세 분석
        """
        logger.info("    Quantifier에게 추세 분석 요청")
        
        # Quantifier import
        try:
            from umis_rag.agents.quantifier import get_quantifier_rag
            quantifier = get_quantifier_rag()
            
            # 시장 규모 추세 분석
            if hasattr(quantifier, 'analyze_growth_with_timeline'):
                size_trend_data = [(year, data['value']) 
                                   for year, data in sorted(market_size_by_year.items())]
                
                market_analysis = quantifier.analyze_growth_with_timeline(
                    market=self.current_market,
                    historical_data=size_trend_data
                )
                
                logger.info(f"    ✅ Quantifier 분석 완료")
                
                return {
                    'market_size': market_analysis,
                    'players': self._analyze_player_trends(players_by_year)
                }
        
        except Exception as e:
            logger.warning(f"    ⚠️ Quantifier 협업 실패: {e}")
        
        # Fallback: 간단한 분석
        return {'market_size': {}, 'players': {}}
    
    def _analyze_player_trends(self, players_by_year: Dict) -> Dict:
        """플레이어별 추세 분석 (간단 버전)"""
        player_trends = {}
        
        # 각 플레이어별로
        all_players = set()
        for year_data in players_by_year.values():
            all_players.update(year_data.keys())
        
        for player in all_players:
            trend = []
            for year in sorted(players_by_year.keys()):
                if player in players_by_year[year]:
                    share = players_by_year[year][player].get('share', 0)
                    trend.append((year, share))
            
            if len(trend) >= 2:
                # 증가/감소/안정 판단
                first_share = trend[0][1]
                last_share = trend[-1][1]
                change = last_share - first_share
                
                if change > 5:
                    direction = 'increasing'
                elif change < -5:
                    direction = 'decreasing'
                else:
                    direction = 'stable'
                
                player_trends[player] = {
                    'trend': trend,
                    'direction': direction,
                    'change': change
                }
        
        return player_trends
    
    def _detect_inflection_points(
        self,
        yoy_data: List[Tuple[int, float]],
        events: List[Dict]
    ) -> List[Dict]:
        """
        변곡점 감지 (성장률 급변 + 주요 사건 매칭)
        
        기준: YoY 변화율 ±30% 이상
        """
        inflection_points = []
        
        if len(yoy_data) < 2:
            return inflection_points
        
        # YoY 변화율 계산
        for i in range(1, len(yoy_data)):
            prev_year, prev_rate = yoy_data[i-1]
            curr_year, curr_rate = yoy_data[i]
            
            # 성장률 변화
            rate_change = abs(curr_rate - prev_rate)
            
            # 30% 이상 변화 → 변곡점
            if rate_change >= 0.30:
                # 주요 사건 찾기 (±1년)
                related_events = [
                    e for e in events
                    if abs(e['year'] - curr_year) <= 1 and e.get('impact') == 'high'
                ]
                
                inflection_point = {
                    'year': curr_year,
                    'type': 'acceleration' if curr_rate > prev_rate else 'deceleration',
                    'growth_before': prev_rate,
                    'growth_after': curr_rate,
                    'change': rate_change,
                    'trigger_event': related_events[0]['event'] if related_events else 'Unknown',
                    'confidence': 0.9 if related_events else 0.6
                }
                
                inflection_points.append(inflection_point)
        
        logger.info(f"    ✅ {len(inflection_points)}개 변곡점 발견")
        return inflection_points
    
    def _analyze_structural_evolution(
        self,
        hhi_by_year: Dict,
        player_count_by_year: Dict,
        events: List[Dict]
    ) -> Dict[str, Any]:
        """
        구조 진화 패턴 분석 (RAG 매칭)
        
        Returns:
            {
                'hhi_trend': [(year, hhi), ...],
                'player_count_trend': [(year, count), ...],
                'pattern': {matched_pattern_id, name, similarity},
                'current_phase': str,
                'evolution_summary': str
            }
        """
        hhi_trend = sorted(hhi_by_year.items())
        player_trend = sorted(player_count_by_year.items())
        
        # RAG 패턴 매칭 (evolution_store가 있으면)
        evolution_pattern = None
        
        # HHI 패턴 설명
        if len(hhi_trend) >= 3:
            pattern_desc = self._describe_hhi_evolution(hhi_trend)
            logger.info(f"    HHI 패턴: {pattern_desc}")
            
            # RAG 검색 (historical_evolution_patterns Collection)
            if self.evolution_store:
                matches = self.evolution_store.similarity_search_with_score(
                    pattern_desc,
                    k=1
                )
                
                if matches:
                    doc, score = matches[0]
                    evolution_pattern = {
                        'pattern_id': doc.metadata.get('pattern_id'),
                        'pattern_name': doc.metadata.get('pattern_name'),
                        'similarity': 1.0 - score,  # ChromaDB는 distance 반환
                        'description': doc.page_content[:200]
                    }
                    logger.info(f"    ✅ 패턴 매칭: {evolution_pattern['pattern_name']} (유사도 {evolution_pattern['similarity']:.2f})")
        
        # 현재 단계 판단
        current_phase = "Unknown"
        if hhi_trend:
            latest_hhi = hhi_trend[-1][1]
            if latest_hhi > 5000:
                current_phase = "독점기"
            elif latest_hhi > 2500:
                current_phase = "재편기"
            else:
                current_phase = "경쟁기"
        
        evolution_summary = self._summarize_evolution(hhi_trend, player_trend)
        
        return {
            'hhi_trend': hhi_trend,
            'player_count_trend': player_trend,
            'pattern': evolution_pattern,
            'current_phase': current_phase,
            'evolution_summary': evolution_summary
        }
    
    def _describe_hhi_evolution(self, hhi_trend: List[Tuple[int, int]]) -> str:
        """HHI 추이를 텍스트로 설명"""
        if len(hhi_trend) < 2:
            return "데이터 부족"
        
        first_hhi = hhi_trend[0][1]
        last_hhi = hhi_trend[-1][1]
        
        if first_hhi > 5000 and last_hhi < 3000:
            return "독점에서 경쟁으로 전환"
        elif first_hhi < 3000 and last_hhi > 5000:
            return "경쟁에서 독점으로 재집중"
        elif first_hhi > 5000 and last_hhi > 4000:
            return "고도 집중 유지"
        else:
            return "경쟁 시장 유지"
    
    def _summarize_evolution(self, hhi_trend, player_trend) -> str:
        """진화 요약"""
        if not hhi_trend or len(hhi_trend) < 2:
            return "진화 패턴 분석 불가 (데이터 부족)"
        
        desc = self._describe_hhi_evolution(hhi_trend)
        
        # 플레이어 수 변화
        if player_trend and len(player_trend) >= 2:
            player_change = player_trend[-1][1] - player_trend[0][1]
            if player_change > 5:
                desc += ", 플레이어 급증"
            elif player_change < -5:
                desc += ", 플레이어 감소"
        
        return desc
    
    def _generate_timeline_visualizations(
        self,
        market: str,
        events: List[Dict],
        trends: Dict,
        evolution: Dict
    ) -> Dict[str, str]:
        """
        Mermaid 차트 생성
        
        Returns:
            {
                'gantt_timeline': str,
                'market_size_chart': str,
                'hhi_table': str
            }
        """
        charts = {}
        
        # 1. Gantt Timeline (주요 사건)
        if events:
            charts['gantt_timeline'] = self._generate_gantt_chart(market, events)
        
        # 2. 시장 규모 차트 (간단 테이블)
        if trends.get('market_size', {}).get('trend'):
            charts['market_size_table'] = self._generate_size_table(
                trends['market_size']['trend']
            )
        
        # 3. HHI 테이블
        if evolution.get('hhi_trend'):
            charts['hhi_table'] = self._generate_hhi_table(
                evolution['hhi_trend']
            )
        
        return charts
    
    def _generate_gantt_chart(self, market: str, events: List[Dict]) -> str:
        """Mermaid Gantt Chart 생성"""
        # 카테고리별 분류
        by_category = {}
        for event in events:
            cat = event.get('category', 'other')
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(event)
        
        # Mermaid 코드
        lines = [
            "```mermaid",
            "gantt",
            f"    title {market} 시장 주요 사건",
            "    dateFormat YYYY-MM",
            ""
        ]
        
        category_names = {
            'player': '플레이어',
            'regulation': '규제',
            'technology': '기술',
            'ma': 'M&A',
            'economic': '경제'
        }
        
        for cat, cat_events in by_category.items():
            if cat_events:
                lines.append(f"    section {category_names.get(cat, cat)}")
                
                for evt in cat_events[:10]:  # 최대 10개
                    year = evt['year']
                    name = evt['event'][:30]
                    impact = evt.get('impact', 'normal')
                    marker = "crit, " if impact == 'high' else ""
                    
                    lines.append(f"    {name:<30} :{marker}{year}-01, {year}-01")
                
                lines.append("")
        
        lines.append("```")
        return "\n".join(lines)
    
    def _generate_size_table(self, trend_data: List[Tuple[int, float]]) -> str:
        """시장 규모 테이블 생성"""
        lines = [
            "| 연도 | 시장 규모 | YoY |",
            "|------|----------|-----|"
        ]
        
        for i, (year, size) in enumerate(trend_data):
            if i == 0:
                yoy = "-"
            else:
                prev_size = trend_data[i-1][1]
                yoy_rate = (size - prev_size) / prev_size
                yoy = f"{yoy_rate:+.1%}"
            
            lines.append(f"| {year} | {size:.0f}억 | {yoy} |")
        
        return "\n".join(lines)
    
    def _generate_hhi_table(self, hhi_trend: List[Tuple[int, int]]) -> str:
        """HHI 테이블 생성"""
        lines = [
            "| 연도 | HHI | 시장 구조 |",
            "|------|-----|-----------|"
        ]
        
        for year, hhi in hhi_trend:
            if hhi > 5000:
                structure = "고도 집중"
            elif hhi > 2500:
                structure = "중간 집중"
            else:
                structure = "경쟁"
            
            lines.append(f"| {year} | {hhi:,} | {structure} |")
        
        return "\n".join(lines)
    
    def _generate_timeline_deliverable(
        self,
        market: str,
        start_year: int,
        end_year: int,
        historical_data: Dict,
        events: List[Dict],
        trends: Dict,
        inflection_points: List[Dict],
        evolution: Dict,
        charts: Dict
    ) -> str:
        """
        Deliverable 생성: market_timeline_analysis.md
        
        Returns:
            deliverable_path: str
        """
        from datetime import datetime
        import os
        
        # 경로 설정
        output_dir = Path("projects/market_analysis")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        deliverable_path = output_dir / f"{market}_timeline_analysis.md"
        
        logger.info(f"    Deliverable 생성: {deliverable_path}")
        
        # Markdown 내용 생성
        content_parts = []
        
        # YAML Frontmatter
        content_parts.append("---")
        content_parts.append("type: market_timeline_analysis")
        content_parts.append(f"market: {market}")
        content_parts.append(f"analysis_period:")
        content_parts.append(f"  start_year: {start_year}")
        content_parts.append(f"  end_year: {end_year}")
        content_parts.append(f"  duration_years: {end_year - start_year}")
        content_parts.append(f"analysis_date: {datetime.now().strftime('%Y-%m-%d')}")
        content_parts.append(f"author: observer")
        content_parts.append(f"status: draft")
        content_parts.append("---")
        content_parts.append("")
        
        # Title
        content_parts.append(f"# {market} 시장 타임라인 분석")
        content_parts.append("")
        
        # 1. Executive Summary
        content_parts.append("## Executive Summary")
        content_parts.append("")
        duration = end_year - start_year
        content_parts.append(f"{start_year}-{end_year}년 {duration}년간 시장 분석 결과.")
        content_parts.append(f"변곡점 {len(inflection_points)}개 발견, 진화 패턴: {evolution.get('evolution_summary', 'N/A')}")
        content_parts.append("")
        
        # 2. Market Size Evolution
        content_parts.append("## Market Size Evolution")
        content_parts.append("")
        
        if charts.get('market_size_table'):
            content_parts.append(charts['market_size_table'])
            content_parts.append("")
        
        # 변곡점
        if inflection_points:
            content_parts.append("### 변곡점 분석")
            content_parts.append("")
            for i, point in enumerate(inflection_points, 1):
                content_parts.append(f"{i}. **{point['year']}년 ({point['type']})**")
                content_parts.append(f"   - 성장률: {point['growth_before']:.1%} → {point['growth_after']:.1%}")
                content_parts.append(f"   - 촉발 사건: {point.get('trigger_event', 'Unknown')}")
                content_parts.append("")
        
        # 3. Player Dynamics
        if trends.get('players'):
            content_parts.append("## Player Dynamics")
            content_parts.append("")
            
            for player, data in trends['players'].items():
                direction_emoji = "↑" if data['direction'] == 'increasing' else "↓" if data['direction'] == 'decreasing' else "→"
                content_parts.append(f"- **{player}**: {direction_emoji} {data['direction']} ({data['change']:+.0f}%p)")
            content_parts.append("")
        
        # 4. Structural Evolution
        content_parts.append("## Structural Evolution")
        content_parts.append("")
        
        if charts.get('hhi_table'):
            content_parts.append(charts['hhi_table'])
            content_parts.append("")
        
        content_parts.append(f"**현재 단계**: {evolution.get('current_phase', 'Unknown')}")
        content_parts.append(f"**진화 요약**: {evolution.get('evolution_summary', 'N/A')}")
        content_parts.append("")
        
        # 패턴 매칭
        if evolution.get('pattern'):
            pattern = evolution['pattern']
            content_parts.append(f"**매칭 패턴**: {pattern.get('pattern_name', 'N/A')} (유사도 {pattern.get('similarity', 0):.2f})")
            content_parts.append("")
        
        # 5. Key Events Timeline
        if charts.get('gantt_timeline'):
            content_parts.append("## Key Events Timeline")
            content_parts.append("")
            content_parts.append(charts['gantt_timeline'])
            content_parts.append("")
        
        # 6. Future Implications
        if trends.get('market_size', {}).get('forecast'):
            content_parts.append("## Future Implications")
            content_parts.append("")
            forecast = trends['market_size']['forecast']
            
            for key, data in forecast.items():
                content_parts.append(f"- **{data['year']}년**: {data['size']:.0f}억 (신뢰도 {data['confidence']:.0%})")
            content_parts.append("")
        
        # 파일 저장
        content = "\n".join(content_parts)
        
        with open(deliverable_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"    ✅ Deliverable 파일 생성: {deliverable_path}")
        
        return str(deliverable_path)


# Observer RAG 인스턴스 (싱글톤)
_observer_rag_instance = None

def get_observer_rag() -> ObserverRAG:
    """Observer RAG 싱글톤 인스턴스 반환"""
    global _observer_rag_instance
    if _observer_rag_instance is None:
        _observer_rag_instance = ObserverRAG()
    return _observer_rag_instance

