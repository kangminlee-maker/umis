#!/usr/bin/env python3
"""
Observer Timeline 분석 단위 테스트
"""

import pytest
from typing import Dict, List
import sys
from pathlib import Path

# 프로젝트 루트 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.agents.observer import ObserverRAG, get_observer_rag


class TestObserverTimeline:
    """Observer Timeline 분석 테스트"""
    
    @pytest.fixture
    def observer(self):
        """Observer 인스턴스"""
        return get_observer_rag()
    
    @pytest.fixture
    def mock_historical_data(self):
        """Mock 과거 데이터"""
        return {
            'market_size_by_year': {
                2015: {'value': 500, 'source': 'SRC_TEST_001', 'reliability': 'high'},
                2018: {'value': 1200, 'source': 'SRC_TEST_002', 'reliability': 'high'},
                2020: {'value': 1800, 'source': 'SRC_TEST_003', 'reliability': 'high'},
                2025: {'value': 2500, 'source': 'SRC_TEST_004', 'reliability': 'medium'}
            },
            'players_by_year': {
                2015: {
                    'Player A': {'share': 40, 'source': 'SRC_TEST_005'},
                    'Player B': {'share': 30, 'source': 'SRC_TEST_006'}
                },
                2020: {
                    'Player A': {'share': 35, 'source': 'SRC_TEST_007'},
                    'Player B': {'share': 35, 'source': 'SRC_TEST_008'},
                    'Player C': {'share': 20, 'source': 'SRC_TEST_009'}
                },
                2025: {
                    'Player A': {'share': 28, 'source': 'SRC_TEST_010'},
                    'Player B': {'share': 42, 'source': 'SRC_TEST_011'},
                    'Player C': {'share': 22, 'source': 'SRC_TEST_012'}
                }
            },
            'events': [
                {'year': 2018, 'event': '규제 완화', 'impact': 'high'},
                {'year': 2020, 'event': 'COVID-19', 'impact': 'high'},
                {'year': 2022, 'event': 'M&A 활발', 'impact': 'medium'}
            ],
            'hhi_by_year': {
                2015: 8000,
                2020: 3000,
                2025: 4500
            },
            'player_count_by_year': {
                2015: 2,
                2020: 15,
                2025: 8
            }
        }
    
    def test_analyze_market_timeline_basic(self, observer):
        """기본 동작 테스트"""
        # 실행
        result = observer.analyze_market_timeline(
            market="테스트 시장",
            start_year=2015,
            end_year=2020
        )
        
        # 검증
        assert isinstance(result, dict)
        assert 'events' in result
        assert 'market_size_trend' in result
        assert 'inflection_points' in result
        assert 'structural_evolution' in result
        assert 'mermaid_charts' in result
        assert 'deliverable_path' in result
    
    def test_event_classification(self, observer):
        """사건 분류 테스트"""
        raw_events = [
            {'year': 2018, 'event': 'Spotify 한국 진입'},
            {'year': 2020, 'event': '저작권법 개정'},
            {'year': 2022, 'event': 'AI 추천 알고리즘 도입'}
        ]
        
        classified = observer._extract_and_classify_events(raw_events, 2015, 2025)
        
        # 검증
        assert len(classified) == 3
        assert classified[0]['category'] == 'player'  # 진입
        assert classified[1]['category'] == 'regulation'  # 법안
        assert classified[2]['category'] == 'technology'  # 기술
    
    def test_hhi_pattern_description(self, observer):
        """HHI 패턴 설명 테스트"""
        # 독점 → 경쟁
        hhi_trend_1 = [(2015, 8000), (2020, 2500)]
        desc_1 = observer._describe_hhi_evolution(hhi_trend_1)
        assert "독점에서 경쟁" in desc_1
        
        # 경쟁 → 독점
        hhi_trend_2 = [(2015, 2000), (2020, 6000)]
        desc_2 = observer._describe_hhi_evolution(hhi_trend_2)
        assert "경쟁에서 독점" in desc_2
        
        # 고도 집중 유지
        hhi_trend_3 = [(2015, 7000), (2020, 6500)]
        desc_3 = observer._describe_hhi_evolution(hhi_trend_3)
        assert "고도 집중 유지" in desc_3
    
    def test_player_trends_analysis(self, observer, mock_historical_data):
        """플레이어 추세 분석 테스트"""
        players = mock_historical_data['players_by_year']
        
        trends = observer._analyze_player_trends(players)
        
        # 검증
        assert 'Player A' in trends
        assert 'Player B' in trends
        assert 'Player C' in trends
        
        # Player A: 40% → 28% (감소)
        assert trends['Player A']['direction'] == 'decreasing'
        assert trends['Player A']['change'] < 0
        
        # Player B: 30% → 42% (증가)
        assert trends['Player B']['direction'] == 'increasing'
        assert trends['Player B']['change'] > 0
    
    def test_gantt_chart_generation(self, observer, mock_historical_data):
        """Gantt 차트 생성 테스트"""
        events = mock_historical_data['events']
        
        # 카테고리 추가
        for event in events:
            event['category'] = observer._classify_event_category(event['event'])
        
        gantt = observer._generate_gantt_chart("테스트 시장", events)
        
        # 검증
        assert '```mermaid' in gantt
        assert 'gantt' in gantt
        assert 'section' in gantt
        assert '규제 완화' in gantt
    
    def test_market_size_table(self, observer):
        """시장 규모 테이블 생성 테스트"""
        trend_data = [
            (2015, 500),
            (2020, 1200),
            (2025, 2500)
        ]
        
        table = observer._generate_size_table(trend_data)
        
        # 검증
        assert '| 연도 | 시장 규모 | YoY |' in table
        assert '| 2015 | 500억 | - |' in table
        assert '2020' in table
        assert '2025' in table
    
    def test_hhi_table_generation(self, observer):
        """HHI 테이블 생성 테스트"""
        hhi_trend = [
            (2015, 8000),
            (2020, 1200),  # 경쟁 (< 1500)
            (2025, 4500)
        ]
        
        table = observer._generate_hhi_table(hhi_trend)
        
        # 검증
        assert '| 연도 | HHI | 시장 구조 |' in table
        assert '고도 집중' in table
        assert '경쟁' in table
        assert '중간 집중' in table


class TestQuantifierTimeline:
    """Quantifier Timeline 분석 테스트"""
    
    @pytest.fixture
    def quantifier(self):
        """Quantifier 인스턴스"""
        from umis_rag.agents.quantifier import get_quantifier_rag
        return get_quantifier_rag()
    
    def test_cagr_calculation(self, quantifier):
        """CAGR 계산 테스트"""
        data = [(2015, 500), (2025, 2500)]
        
        cagr = quantifier._calculate_cagr_from_timeline(data)
        
        # 10년간 5배 = CAGR ~17.5%
        assert 0.17 < cagr < 0.18
    
    def test_yoy_calculation(self, quantifier):
        """YoY 계산 테스트"""
        data = [
            (2015, 500),
            (2020, 1200),
            (2025, 2500)
        ]
        
        yoy = quantifier._calculate_yoy_rates(data)
        
        # 검증
        assert len(yoy) == 2
        assert yoy[0][0] == 2020  # 연도
        assert abs(yoy[0][1] - 1.4) < 0.01  # 140% 증가
    
    def test_inflection_point_detection(self, quantifier):
        """변곡점 감지 테스트"""
        yoy_data = [
            (2016, 0.10),  # 10% 성장
            (2018, 0.45),  # 45% 성장 (급증! +35%p)
            (2020, 0.20),  # 20% 성장
            (2022, -0.15)  # -15% 성장 (급락! -35%p)
        ]
        
        inflections = quantifier._detect_inflection_points_math(yoy_data)
        
        # 검증
        assert len(inflections) == 2  # 2개 변곡점
        
        # 첫 번째: 가속 (2018년)
        assert inflections[0]['year'] == 2018
        assert inflections[0]['type'] == 'acceleration'
        
        # 두 번째: 감속 (2022년)
        assert inflections[1]['year'] == 2022
        assert inflections[1]['type'] == 'deceleration'
    
    def test_forecast_simple(self, quantifier):
        """미래 예측 테스트"""
        data = [(2020, 1000), (2025, 2000)]
        cagr = quantifier._calculate_cagr_from_timeline(data)
        
        forecast = quantifier._forecast_simple(data, cagr)
        
        # 검증
        assert 'year_1' in forecast
        assert 'year_3' in forecast
        assert 'year_5' in forecast
        
        # 신뢰도: 멀수록 낮음
        assert forecast['year_1']['confidence'] > forecast['year_3']['confidence']
        assert forecast['year_3']['confidence'] > forecast['year_5']['confidence']
    
    def test_full_timeline_analysis(self, quantifier):
        """전체 Timeline 분석 테스트"""
        historical_data = [
            (2015, 500),
            (2018, 1200),
            (2020, 1800),
            (2022, 2200),
            (2025, 2500)
        ]
        
        result = quantifier.analyze_growth_with_timeline(
            market="테스트 시장",
            historical_data=historical_data
        )
        
        # 검증
        assert 'cagr' in result
        assert 'yoy' in result
        assert 'inflection_points' in result
        assert 'forecast' in result
        
        assert len(result['yoy']) == 4  # 4개 YoY
        assert result['cagr'] > 0  # 양수 성장


class TestValidatorHistoricalData:
    """Validator 과거 데이터 수집 테스트"""
    
    @pytest.fixture
    def validator(self):
        """Validator 인스턴스"""
        from umis_rag.agents.validator import get_validator_rag
        return get_validator_rag()
    
    def test_search_historical_data_basic(self, validator):
        """기본 동작 테스트"""
        result = validator.search_historical_data(
            market="테스트 시장",
            years=range(2015, 2021)
        )
        
        # 검증
        assert isinstance(result, dict)
        assert 'market_size_by_year' in result
        assert 'players_by_year' in result
        assert 'events' in result
        assert 'data_quality' in result
    
    def test_data_gap_identification(self, validator):
        """Gap 식별 테스트"""
        collected = {
            'market_size_by_year': {
                2015: {'value': 500},
                2020: {'value': 1200}
                # 2016-2019 누락!
            }
        }
        
        gaps = validator._identify_data_gaps(collected, range(2015, 2021))
        
        # 검증
        assert len(gaps['missing_years']) == 4  # 2016-2019
        assert 2016 in gaps['missing_years']
        assert 2019 in gaps['missing_years']
        assert len(gaps['estimator_requests']) == 4
    
    def test_data_quality_assessment(self, validator):
        """데이터 품질 평가 테스트"""
        data = {
            'market_size_by_year': {
                2015: {'reliability': 'high'},
                2016: {'reliability': 'estimated'},
                2017: {'reliability': 'estimated'},
                2018: {'reliability': 'high'},
                2019: {'reliability': 'estimated'},
                2020: {'reliability': 'high'}
            }
        }
        
        quality = validator._assess_data_quality(data, range(2015, 2021))
        
        # 검증
        assert quality['total_years'] == 6
        assert quality['verified_years'] == 3
        assert quality['estimated_years'] == 3
        assert quality['verified_ratio'] == 0.5
        assert quality['grade'] == 'A (High)'  # >= 0.5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

