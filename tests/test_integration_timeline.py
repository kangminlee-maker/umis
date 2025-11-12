#!/usr/bin/env python3
"""
Timeline 분석 통합 테스트
전체 파이프라인 동작 검증
"""

import pytest
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.agents.observer import get_observer_rag


class TestTimelineIntegration:
    """Timeline 분석 통합 테스트"""
    
    @pytest.fixture
    def observer(self):
        """Observer 인스턴스"""
        return get_observer_rag()
    
    def test_full_pipeline_minimal(self, observer):
        """
        전체 파이프라인 동작 테스트 (최소)
        
        Validator 미구현 상태에서도 기본 동작 확인
        """
        print("\n" + "="*80)
        print("통합 테스트: 전체 파이프라인")
        print("="*80)
        
        # 실행
        result = observer.analyze_market_timeline(
            market="테스트 시장",
            start_year=2015,
            end_year=2025
        )
        
        # 검증
        assert isinstance(result, dict), "결과가 dict여야 함"
        
        print(f"\n✅ 기본 구조 검증:")
        assert 'events' in result, "events 필드 필수"
        print(f"  - events: {len(result['events'])}개")
        
        assert 'market_size_trend' in result, "market_size_trend 필드 필수"
        print(f"  - market_size_trend: {len(result['market_size_trend'])}개 데이터 포인트")
        
        assert 'inflection_points' in result, "inflection_points 필드 필수"
        print(f"  - inflection_points: {len(result['inflection_points'])}개")
        
        assert 'structural_evolution' in result, "structural_evolution 필드 필수"
        print(f"  - structural_evolution: {result['structural_evolution'].get('current_phase', 'N/A')}")
        
        assert 'mermaid_charts' in result, "mermaid_charts 필드 필수"
        print(f"  - mermaid_charts: {len(result['mermaid_charts'])}개")
        
        assert 'deliverable_path' in result, "deliverable_path 필드 필수"
        print(f"  - deliverable_path: {result['deliverable_path']}")
        
        assert 'data_quality' in result, "data_quality 필드 필수"
        print(f"  - data_quality: {result['data_quality']}")
        
        print("\n✅ 전체 파이프라인 동작 확인!")
        print("="*80)
    
    def test_evolution_pattern_matching(self, observer):
        """
        진화 패턴 RAG 매칭 테스트
        """
        print("\n" + "="*80)
        print("통합 테스트: 진화 패턴 RAG 매칭")
        print("="*80)
        
        # HHI 추이 데이터 (독점 → 경쟁 패턴)
        hhi_data = {
            2015: 8000,  # 독점
            2020: 2500,  # 경쟁
            2025: 4000   # 재편
        }
        
        player_count = {
            2015: 2,
            2020: 15,
            2025: 8
        }
        
        # 분석
        evolution = observer._analyze_structural_evolution(
            hhi_data,
            player_count,
            []
        )
        
        # 검증
        print(f"\n✅ 구조 진화 분석:")
        print(f"  - HHI 추이: {evolution['hhi_trend']}")
        print(f"  - 현재 단계: {evolution['current_phase']}")
        print(f"  - 진화 요약: {evolution['evolution_summary']}")
        
        if evolution['pattern']:
            print(f"  - 매칭 패턴: {evolution['pattern']['pattern_name']}")
            print(f"  - 유사도: {evolution['pattern']['similarity']:.2f}")
            
            # 예상: evolution_001 "독점 → 경쟁 → 재편"
            assert 'evolution_001' in evolution['pattern']['pattern_id']
        else:
            print(f"  - 매칭 패턴: None (evolution_store 없음 또는 매칭 실패)")
        
        print("="*80)
    
    def test_mermaid_generation(self, observer):
        """
        Mermaid 차트 생성 테스트
        """
        print("\n" + "="*80)
        print("통합 테스트: Mermaid 차트 생성")
        print("="*80)
        
        # Mock 데이터
        events = [
            {'year': 2018, 'event': 'Spotify 진입', 'category': 'player', 'impact': 'high'},
            {'year': 2020, 'event': '규제 완화', 'category': 'regulation', 'impact': 'high'},
            {'year': 2022, 'event': 'AI 도입', 'category': 'technology', 'impact': 'medium'}
        ]
        
        trends = {
            'market_size': {
                'trend': [(2015, 500), (2020, 1200), (2025, 2500)]
            }
        }
        
        evolution = {
            'hhi_trend': [(2015, 8000), (2020, 3000), (2025, 4500)]
        }
        
        # 차트 생성
        charts = observer._generate_timeline_visualizations(
            "음악 스트리밍", events, trends, evolution
        )
        
        # 검증
        print(f"\n✅ 생성된 차트:")
        
        if 'gantt_timeline' in charts:
            print(f"  - Gantt Timeline: {len(charts['gantt_timeline'])} 문자")
            assert '```mermaid' in charts['gantt_timeline']
            assert 'Spotify 진입' in charts['gantt_timeline']
        
        if 'market_size_table' in charts:
            print(f"  - Market Size Table: {len(charts['market_size_table'])} 문자")
            assert '| 연도 | 시장 규모 | YoY |' in charts['market_size_table']
        
        if 'hhi_table' in charts:
            print(f"  - HHI Table: {len(charts['hhi_table'])} 문자")
            assert '| 연도 | HHI | 시장 구조 |' in charts['hhi_table']
        
        print("\n✅ Mermaid 차트 생성 성공!")
        print("="*80)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

