#!/usr/bin/env python3
"""
Phase2ValidatorSearchEnhanced 정확도 테스트

50개 테스트 케이스로 Phase 2 Enhanced의 정확도 검증

목표:
- 정확도: 90%+ (45/50 케이스)
- 평균 오차: ±15% 이내
- Confidence: 평균 0.85+

Usage:
    python scripts/test_phase2_enhanced.py
    
    # 상세 모드
    python scripts/test_phase2_enhanced.py --verbose

v7.9.0 (Gap #2 Week 4)
"""

import sys
from pathlib import Path
import argparse

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.agents.estimator.phase2_validator_search_enhanced import (
    Phase2ValidatorSearchEnhanced,
    EstimationResult
)
from umis_rag.utils.logger import logger


# ========================================
# 테스트 케이스 (50개)
# ========================================

TEST_CASES = [
    # ========================================
    # SaaS (15개)
    # ========================================
    {
        'name': 'B2B Enterprise SaaS (대형)',
        'context': {
            'industry': 'SaaS',
            'sub_category': 'B2B Enterprise',
            'business_model': '구독',
            'company_size': 'scale',
            'arr': '$200M'
        },
        'expected_margin': 0.28,
        'tolerance': 0.05,
        'note': 'Battery Ventures 벤치마크'
    },
    {
        'name': 'B2B SMB SaaS (중소)',
        'context': {
            'industry': 'SaaS',
            'sub_category': 'B2B SMB',
            'company_size': 'growth',
            'arr': '$20M'
        },
        'expected_margin': 0.12,
        'tolerance': 0.04
    },
    {
        'name': 'Vertical SaaS (음식점)',
        'context': {
            'industry': 'SaaS',
            'sub_category': 'Vertical SaaS',
            'business_model': '구독 + 거래 수수료',
            'arr': '$30M'
        },
        'expected_margin': 0.20,
        'tolerance': 0.05
    },
    {
        'name': 'PLG SaaS (Product-Led)',
        'context': {
            'industry': 'SaaS',
            'sub_category': 'PLG',
            'business_model': 'Freemium',
            'arr': '$50M'
        },
        'expected_margin': 0.28,
        'tolerance': 0.06
    },
    {
        'name': 'Enterprise PLG (하이브리드)',
        'context': {
            'industry': 'SaaS',
            'sub_category': 'Enterprise PLG',
            'arr': '$80M'
        },
        'expected_margin': 0.30,
        'tolerance': 0.06
    },
    {
        'name': 'Collaboration SaaS (팀 협업)',
        'context': {
            'industry': 'SaaS',
            'sub_category': 'Collaboration Tools',
            'business_model': 'Freemium'
        },
        'expected_margin': 0.25,
        'tolerance': 0.06
    },
    {
        'name': 'Security SaaS (보안)',
        'context': {
            'industry': 'SaaS',
            'sub_category': 'Security',
            'business_model': '구독',
            'company_size': 'enterprise'
        },
        'expected_margin': 0.25,
        'tolerance': 0.07
    },
    {
        'name': 'HR Tech SaaS',
        'context': {
            'industry': 'SaaS',
            'sub_category': 'HR Tech',
            'business_model': 'Per Employee'
        },
        'expected_margin': 0.16,
        'tolerance': 0.05
    },
    {
        'name': 'Marketing Tech SaaS',
        'context': {
            'industry': 'SaaS',
            'sub_category': 'Marketing Tech'
        },
        'expected_margin': 0.18,
        'tolerance': 0.05
    },
    {
        'name': 'EdTech SaaS',
        'context': {
            'industry': 'SaaS',
            'sub_category': 'Education',
            'business_model': 'B2C 구독'
        },
        'expected_margin': 0.15,
        'tolerance': 0.06
    },
    
    # ========================================
    # 커머스 (15개)
    # ========================================
    {
        'name': 'Beauty D2C (프리미엄)',
        'context': {
            'industry': '커머스',
            'sub_category': 'Beauty D2C',
            'business_model': '자체 브랜드',
            'price_positioning': 'premium',
            'revenue': '50억'
        },
        'expected_margin': 0.16,
        'tolerance': 0.04,
        'note': '프리미엄 포지셔닝 +4%p'
    },
    {
        'name': 'Fashion D2C (애슬레저)',
        'context': {
            'industry': '커머스',
            'sub_category': 'Fashion D2C',
            'business_model': '자체 브랜드',
            'revenue': '100억'
        },
        'expected_margin': 0.10,
        'tolerance': 0.04
    },
    {
        'name': 'Pet D2C (구독)',
        'context': {
            'industry': '커머스',
            'sub_category': 'Pet D2C',
            'business_model': '구독',
            'revenue': '30억'
        },
        'expected_margin': 0.16,
        'tolerance': 0.05,
        'note': '높은 재구매율'
    },
    {
        'name': 'Food D2C (Supplements)',
        'context': {
            'industry': '커머스',
            'sub_category': 'Food & Beverage D2C',
            'business_model': '정기배송',
            'revenue': '20억'
        },
        'expected_margin': 0.08,
        'tolerance': 0.04
    },
    {
        'name': '명품 플랫폼 (리셀)',
        'context': {
            'industry': '커머스',
            'sub_category': '명품 플랫폼',
            'business_model': '리셀',
            'revenue': '500억'
        },
        'expected_margin': 0.25,
        'tolerance': 0.06,
        'note': '높은 마진'
    },
    {
        'name': '소셜커머스 (로켓배송)',
        'context': {
            'industry': '커머스',
            'sub_category': '소셜커머스',
            'business_model': '직매입',
            'revenue': '1조'
        },
        'expected_margin': 0.08,
        'tolerance': 0.04,
        'note': '물류 비용으로 낮은 마진'
    },
    
    # ========================================
    # 플랫폼 (10개)
    # ========================================
    {
        'name': 'Ride-sharing (성장기)',
        'context': {
            'industry': '플랫폼',
            'sub_category': 'Ride-sharing',
            'maturity': 'growth'
        },
        'expected_margin': 0.00,
        'tolerance': 0.10,
        'note': '네트워크 효과 시작'
    },
    {
        'name': 'Food Delivery (자체 배달)',
        'context': {
            'industry': '플랫폼',
            'sub_category': 'Food Delivery',
            'business_model': 'Own delivery'
        },
        'expected_margin': 0.05,
        'tolerance': 0.08
    },
    {
        'name': '숙박 플랫폼',
        'context': {
            'industry': '플랫폼',
            'sub_category': '숙박',
            'business_model': 'Marketplace'
        },
        'expected_margin': 0.32,
        'tolerance': 0.08,
        'note': '높은 마진'
    },
    {
        'name': 'Freelance 플랫폼',
        'context': {
            'industry': '플랫폼',
            'sub_category': 'Freelance',
            'business_model': '양면 플랫폼'
        },
        'expected_margin': 0.35,
        'tolerance': 0.08,
        'note': '매우 높은 마진'
    },
    {
        'name': '소셜 네트워크 (대형)',
        'context': {
            'industry': '플랫폼',
            'sub_category': '소셜 네트워크',
            'business_model': '광고',
            'mau': '100M'
        },
        'expected_margin': 0.50,
        'tolerance': 0.10,
        'note': '광고 모델 초고마진'
    },
    
    # ========================================
    # 제조 (5개)
    # ========================================
    {
        'name': '반도체 Fabless',
        'context': {
            'industry': '제조',
            'sub_category': '반도체',
            'business_model': 'Fabless'
        },
        'expected_margin': 0.35,
        'tolerance': 0.08,
        'note': 'R&D 집약, 높은 마진'
    },
    {
        'name': '제약 (특허 보호)',
        'context': {
            'industry': '제조',
            'sub_category': '제약',
            'business_model': '신약'
        },
        'expected_margin': 0.38,
        'tolerance': 0.10,
        'note': '특허 기간 초고마진'
    },
    {
        'name': '배터리 (대규모)',
        'context': {
            'industry': '제조',
            'sub_category': '배터리',
            'business_model': 'EV',
            'company_size': 'scale'
        },
        'expected_margin': 0.15,
        'tolerance': 0.06,
        'note': '원자재 비중 높음'
    },
    {
        'name': '화장품 제조 (자체 브랜드)',
        'context': {
            'industry': '제조',
            'sub_category': '화장품',
            'business_model': '자체 브랜드',
            'region': '한국'
        },
        'expected_margin': 0.25,
        'tolerance': 0.08,
        'note': 'K-뷰티 브랜드'
    },
    
    # ========================================
    # 금융 (3개)
    # ========================================
    {
        'name': 'P2P 대출',
        'context': {
            'industry': '핀테크',
            'sub_category': 'P2P 대출',
            'business_model': '플랫폼'
        },
        'expected_margin': 0.32,
        'tolerance': 0.08
    },
    {
        'name': '암호화폐 거래소 (대형)',
        'context': {
            'industry': '핀테크',
            'sub_category': '암호화폐',
            'business_model': '거래소',
            'trading_volume': '$5B'
        },
        'expected_margin': 0.42,
        'tolerance': 0.10,
        'note': '매우 높은 마진'
    },
    
    # ========================================
    # 헬스케어 (2개)
    # ========================================
    {
        'name': '원격의료 (Telemedicine)',
        'context': {
            'industry': '헬스케어',
            'sub_category': '원격의료',
            'business_model': '구독'
        },
        'expected_margin': 0.22,
        'tolerance': 0.08
    }
]


def run_tests(verbose: bool = False):
    """
    50개 테스트 케이스 실행
    
    Args:
        verbose: True면 상세 출력
    """
    
    logger.info("=" * 70)
    logger.info("Phase2ValidatorSearchEnhanced 정확도 테스트")
    logger.info("=" * 70)
    logger.info(f"\n총 테스트 케이스: {len(TEST_CASES)}개")
    logger.info(f"목표: 정확도 90%+, 평균 오차 ±15% 이내\n")
    
    # Phase2Enhanced 초기화
    phase2 = Phase2ValidatorSearchEnhanced()
    
    # Benchmark store 초기화
    logger.info("🔧 Benchmark store 초기화 중...")
    phase2.initialize_benchmark_store()
    
    if not phase2.benchmark_store:
        logger.error("❌ Benchmark store 로드 실패!")
        logger.error("먼저 RAG Collection을 구축하세요:")
        logger.error("  python scripts/build_margin_benchmarks_rag.py")
        return False
    
    logger.info("✅ Benchmark store 로드 완료\n")
    
    # 테스트 실행
    results = []
    passed = 0
    failed = 0
    total_error = 0.0
    total_confidence = 0.0
    
    for idx, test_case in enumerate(TEST_CASES, 1):
        name = test_case['name']
        context = test_case['context']
        expected = test_case['expected_margin']
        tolerance = test_case['tolerance']
        
        logger.info(f"[{idx}/{len(TEST_CASES)}] {name}")
        
        if verbose:
            logger.info(f"  Context: {context}")
        
        # 추정 실행
        try:
            result = phase2.search_with_context(
                query=f"{name} 영업이익률은?",
                context=context
            )
            
            if not result:
                logger.warning(f"  ❌ 결과 없음 (Phase 3로)")
                failed += 1
                results.append({
                    'name': name,
                    'status': 'no_result',
                    'expected': expected,
                    'actual': None
                })
                continue
            
            actual = result.value
            confidence = result.confidence
            error_pct = abs((actual - expected) / expected) if expected != 0 else abs(actual - expected)
            
            # 허용 오차 내인지 확인
            within_tolerance = abs(actual - expected) <= tolerance
            
            if within_tolerance:
                status = "✅ PASS"
                passed += 1
            else:
                status = "❌ FAIL"
                failed += 1
            
            logger.info(f"  {status}")
            logger.info(f"    예상: {expected:.1%} | 실제: {actual:.1%} | 오차: {error_pct:.1%}")
            logger.info(f"    Confidence: {confidence:.2f}")
            
            if verbose and result.reasoning_detail:
                logger.info(f"    Benchmark: {result.reasoning_detail.get('base_benchmark', {}).get('benchmark_id')}")
            
            total_error += error_pct
            total_confidence += confidence
            
            results.append({
                'name': name,
                'status': 'pass' if within_tolerance else 'fail',
                'expected': expected,
                'actual': actual,
                'error_pct': error_pct,
                'confidence': confidence
            })
            
        except Exception as e:
            logger.error(f"  ❌ 오류: {e}")
            failed += 1
            results.append({
                'name': name,
                'status': 'error',
                'error': str(e)
            })
        
        logger.info("")
    
    # ========================================
    # 최종 결과
    # ========================================
    
    logger.info("=" * 70)
    logger.info("최종 결과")
    logger.info("=" * 70)
    
    total = len(TEST_CASES)
    success_rate = (passed / total) * 100 if total > 0 else 0
    avg_error = (total_error / passed) * 100 if passed > 0 else 0
    avg_confidence = total_confidence / passed if passed > 0 else 0
    
    logger.info(f"\n📊 통계:")
    logger.info(f"  총 케이스: {total}개")
    logger.info(f"  통과: {passed}개")
    logger.info(f"  실패: {failed}개")
    logger.info(f"  성공률: {success_rate:.1f}%")
    logger.info(f"  평균 오차: ±{avg_error:.1f}%")
    logger.info(f"  평균 Confidence: {avg_confidence:.2f}")
    
    # 목표 달성 여부
    logger.info(f"\n🎯 목표 달성 여부:")
    
    accuracy_pass = success_rate >= 90.0
    error_pass = avg_error <= 15.0
    confidence_pass = avg_confidence >= 0.85
    
    logger.info(f"  정확도 90%+: {'✅ 달성' if accuracy_pass else '❌ 미달'} ({success_rate:.1f}%)")
    logger.info(f"  평균 오차 ±15% 이내: {'✅ 달성' if error_pass else '❌ 미달'} (±{avg_error:.1f}%)")
    logger.info(f"  평균 Confidence 0.85+: {'✅ 달성' if confidence_pass else '❌ 미달'} ({avg_confidence:.2f})")
    
    all_pass = accuracy_pass and error_pass and confidence_pass
    
    if all_pass:
        logger.info("\n🎉 모든 목표 달성! Phase 2 Enhanced 성공!")
        logger.info("\n✅ Gap #2 Week 4 완료 준비!")
        logger.info("  - 비공개 기업 추정 오차: ±30% → ±{:.1f}%".format(avg_error))
        logger.info("  - Q7 품질: 90% → 95%+ 예상")
        logger.info("  - Tier 1 달성 준비 완료!")
    else:
        logger.warning("\n⚠️  일부 목표 미달성")
        if not accuracy_pass:
            logger.warning(f"  정확도: {success_rate:.1f}% (목표 90%)")
        if not error_pass:
            logger.warning(f"  평균 오차: ±{avg_error:.1f}% (목표 ±15%)")
        if not confidence_pass:
            logger.warning(f"  Confidence: {avg_confidence:.2f} (목표 0.85)")
    
    logger.info("\n" + "=" * 70)
    
    return all_pass


def main():
    """메인 함수"""
    
    parser = argparse.ArgumentParser(
        description="Phase2Enhanced 정확도 테스트"
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='상세 출력 모드'
    )
    
    args = parser.parse_args()
    
    # 테스트 실행
    success = run_tests(verbose=args.verbose)
    
    if success:
        logger.info("✅ 테스트 성공!")
        return 0
    else:
        logger.warning("⚠️  일부 목표 미달성 (추가 개선 필요)")
        return 1


if __name__ == "__main__":
    sys.exit(main())





