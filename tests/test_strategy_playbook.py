#!/usr/bin/env python3
"""
Strategy Playbook 테스트

3개 실제 기회로 generate_strategy_playbook() 검증

테스트 케이스:
1. 피아노 구독 서비스
2. 음악 레슨 플랫폼
3. 뷰티 D2C 브랜드

v7.10.0 (Gap #3 Week 3)
"""

import unittest
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.agents.explorer import create_explorer_agent


class TestStrategyPlaybook(unittest.TestCase):
    """Strategy Playbook 기능 테스트"""
    
    @classmethod
    def setUpClass(cls):
        """테스트 setup"""
        cls.explorer = create_explorer_agent()
    
    def test_1_piano_subscription(self):
        """테스트 1: 피아노 구독 서비스"""
        
        print("\n" + "=" * 70)
        print("테스트 1: 피아노 구독 서비스")
        print("=" * 70)
        
        validated_opportunity = {
            'opportunity_id': 'OPP_PIANO_001',
            'title': '피아노 구독 서비스',
            'value_proposition': '초기 부담 없이 피아노 시작',
            'target_customer': '피아노 입문자 (20-40대)',
            'revenue_model': '월 구독',
            'core_features': [
                {'name': '사용자 가입', 'type': 'core', 'complexity': 'simple'},
                {'name': '피아노 선택/배송', 'type': 'core', 'complexity': 'medium'},
                {'name': '결제 시스템', 'type': 'core', 'complexity': 'medium'},
                {'name': '관리 대시보드', 'type': 'frequent', 'complexity': 'simple'},
                {'name': '레슨 매칭', 'type': 'frequent', 'complexity': 'medium'}
            ],
            'unit_economics': {
                'arpu': 120000,
                'cac': 180000,
                'ltv': 2400000,
                'churn': 0.05
            }
        }
        
        market_context = {
            'market_structure': '과점 (3개 업체 60%)',
            'competitors': [
                {'name': 'A사', 'price': 150000},
                {'name': 'B사', 'price': 160000},
                {'name': 'C사', 'price': 140000}
            ],
            'inefficiencies': ['높은 초기 비용', '해지 어려움', '제한적 선택']
        }
        
        quantified_market = {
            'sam': 1300,
            'target_share': 0.05
        }
        
        # Strategy Playbook 생성
        result = self.explorer.generate_strategy_playbook(
            validated_opportunity=validated_opportunity,
            market_context=market_context,
            quantified_market=quantified_market,
            project_name="piano_subscription_test"
        )
        
        # 검증
        self.assertIn('gtm_strategy', result)
        self.assertIn('product_roadmap', result)
        self.assertIn('execution_milestones', result)
        self.assertIn('risk_mitigation', result)
        self.assertIn('markdown_path', result)
        self.assertIn('excel_path', result)
        
        # GTM Strategy 검증
        gtm = result['gtm_strategy']
        self.assertIn('customer_acquisition', gtm)
        self.assertGreater(len(gtm['customer_acquisition']['channels']), 0)
        
        # Product Roadmap 검증
        roadmap = result['product_roadmap']
        self.assertEqual(len(roadmap['mvp']['features']), 3)
        self.assertGreater(roadmap['mvp']['features'][0]['rice_score'], 0)
        
        # Milestones 검증
        milestones = result['execution_milestones']
        self.assertIn('month_3', milestones)
        self.assertIn('month_6', milestones)
        self.assertIn('month_12', milestones)
        
        # Risk 검증
        risks = result['risk_mitigation']
        self.assertGreater(len(risks['key_risks']), 0)
        
        # 파일 생성 확인
        md_path = Path(result['markdown_path'])
        self.assertTrue(md_path.exists())
        
        print(f"\n✅ 테스트 1 통과!")
        print(f"  - GTM: {len(gtm['customer_acquisition']['channels'])}개 채널")
        print(f"  - Features: {len(roadmap['all_features'])}개")
        print(f"  - Risks: {len(risks['key_risks'])}개")
        print(f"  - Markdown: {md_path}")
    
    def test_2_music_lesson_platform(self):
        """테스트 2: 음악 레슨 플랫폼"""
        
        print("\n" + "=" * 70)
        print("테스트 2: 음악 레슨 플랫폼")
        print("=" * 70)
        
        validated_opportunity = {
            'opportunity_id': 'OPP_MUSIC_002',
            'title': '음악 레슨 온라인 플랫폼',
            'value_proposition': '언제 어디서나 전문가와 1:1 레슨',
            'target_customer': '성인 음악 학습자 (25-45대)',
            'revenue_model': '플랫폼 수수료 (Take Rate 25%)',
            'core_features': [
                {'name': '강사 등록/관리', 'type': 'core', 'complexity': 'medium'},
                {'name': '학생 매칭', 'type': 'core', 'complexity': 'complex'},
                {'name': '화상 레슨', 'type': 'core', 'complexity': 'complex'},
                {'name': '결제/정산', 'type': 'core', 'complexity': 'medium'},
                {'name': '예약 시스템', 'type': 'core', 'complexity': 'simple'}
            ],
            'unit_economics': {
                'arpu': 80000,
                'cac': 100000,
                'ltv': 960000,
                'churn': 0.10
            }
        }
        
        market_context = {
            'market_structure': '분산형 (개인 강사 중심)',
            'competitors': [
                {'name': '개인 강사', 'price': 100000},
                {'name': '음악 학원', 'price': 150000}
            ],
            'inefficiencies': ['시간/장소 제약', '강사 찾기 어려움']
        }
        
        quantified_market = {
            'sam': 3000,
            'target_share': 0.03
        }
        
        # Strategy Playbook 생성
        result = self.explorer.generate_strategy_playbook(
            validated_opportunity=validated_opportunity,
            market_context=market_context,
            quantified_market=quantified_market,
            project_name="music_lesson_platform_test"
        )
        
        # 검증
        self.assertIn('gtm_strategy', result)
        self.assertIn('product_roadmap', result)
        
        # Milestones 계산 확인
        milestones = result['execution_milestones']
        customers_3 = milestones['month_3']['metrics']['customers']
        self.assertGreater(customers_3, 0)
        
        print(f"\n✅ 테스트 2 통과!")
        print(f"  - Month 3 고객: {customers_3}명")
        print(f"  - SAM: {quantified_market['sam']}억")
    
    def test_3_beauty_d2c(self):
        """테스트 3: 뷰티 D2C 브랜드"""
        
        print("\n" + "=" * 70)
        print("테스트 3: 뷰티 D2C 브랜드")
        print("=" * 70)
        
        validated_opportunity = {
            'opportunity_id': 'OPP_BEAUTY_003',
            'title': '친환경 뷰티 D2C 브랜드',
            'value_proposition': '비건 천연 화장품, 직접 판매',
            'target_customer': '친환경 소비자 (20-35대 여성)',
            'revenue_model': '직접 판매',
            'core_features': [
                {'name': '커머스 사이트', 'type': 'core', 'complexity': 'medium'},
                {'name': '제품 상세', 'type': 'core', 'complexity': 'simple'},
                {'name': '장바구니/결제', 'type': 'core', 'complexity': 'medium'},
                {'name': '회원 관리', 'type': 'core', 'complexity': 'simple'},
                {'name': '리뷰 시스템', 'type': 'frequent', 'complexity': 'simple'}
            ],
            'unit_economics': {
                'arpu': 65000,  # AOV
                'cac': 45000,
                'ltv': 180000,
                'churn': 0.35  # 연간
            }
        }
        
        market_context = {
            'market_structure': '경쟁 시장',
            'competitors': [
                {'name': '올리브영', 'price': 50000},
                {'name': '기존 브랜드들', 'price': 70000}
            ],
            'inefficiencies': ['중간 유통 마진', '대량 생산']
        }
        
        quantified_market = {
            'sam': 8000,
            'target_share': 0.02
        }
        
        # Strategy Playbook 생성
        result = self.explorer.generate_strategy_playbook(
            validated_opportunity=validated_opportunity,
            market_context=market_context,
            quantified_market=quantified_market,
            project_name="beauty_d2c_test"
        )
        
        # 검증
        self.assertIn('gtm_strategy', result)
        
        # Resource Plan 검증
        resources = result['resource_plan']
        self.assertIn('team_structure', resources)
        self.assertIn('budget', resources)
        
        # Risk 검증
        risks = result['risk_mitigation']
        self.assertGreater(len(risks['key_risks']), 0)
        
        print(f"\n✅ 테스트 3 통과!")
        print(f"  - Risks: {len(risks['key_risks'])}개")
        print(f"  - Team (Month 12): {sum([t['count'] for t in resources['team_structure']['month_12']])}명")


if __name__ == '__main__':
    # 테스트 실행
    unittest.main(verbosity=2)






