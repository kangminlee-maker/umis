#!/usr/bin/env python3
"""
한국 실무교육시장 규모 추정 (Guestimation)
날짜: 2025-11-05
방법론: UMIS Guestimation Framework
"""

import sys
from pathlib import Path

# Add project root
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.deliverables.excel.market_sizing_generator import MarketSizingWorkbookGenerator


def estimate_korean_practical_education_market():
    """
    한국 실무교육시장 규모 추정
    
    시장 정의:
    - 대상: 성인 직장인 대상 실무교육 (온/오프라인)
    - 포함: 직무교육, 자격증, IT/디지털 스킬, 외국어, 비즈니스 스킬
    - 제외: 학위과정, K-12, 취미/여가 교육
    
    추정 방법:
    - Method 1: Top-Down (교육시장 → 성인교육 → 실무교육)
    - Method 2: Bottom-Up (타겟 세그먼트별 합산)
    - Method 3: Proxy (기업 교육훈련비 데이터)
    - Method 4: Competitor Revenue (주요 플레이어 역산)
    """
    
    print("\n" + "="*70)
    print("📊 한국 실무교육시장 규모 추정 (UMIS Guestimation)")
    print("="*70 + "\n")
    
    print("🎯 시장 정의:")
    print("   대상: 성인 직장인 (20-59세)")
    print("   범위: 직무교육, IT/디지털, 외국어, 자격증")
    print("   기간: 2025년 기준\n")
    
    generator = MarketSizingWorkbookGenerator()
    
    # 추정 데이터 (Guestimation 기반)
    data = {
        'market_name': 'korean_adult_education_2025',
        
        # Assumptions (15개 가정)
        'assumptions': [
            # ===== TAM (전체 교육시장) =====
            {'id': 'TAM_VALUE', 'category': 'TAM', 'description': '한국 교육시장 전체',
             'value': 100_000_000_000_000, 'unit': '원', 'data_type': '추정치',
             'source': 'EST_TAM_001', 'confidence': 'Medium',
             'notes': '사교육비 + 공교육 + 성인교육 포함 (약 100조 추정)'},
            
            # ===== Top-Down Narrowing =====
            {'id': 'FILTER_ADULT', 'category': '연령', 'description': '성인교육 비중',
             'value': 0.15, 'unit': '%', 'data_type': '추정치',
             'source': 'EST_001', 'confidence': 'Medium',
             'notes': '전체 교육시장 중 성인(20-59세) 대상 비중 약 15%'},
            
            {'id': 'FILTER_PRACTICAL', 'category': '목적', 'description': '실무교육 비중',
             'value': 0.60, 'unit': '%', 'data_type': '추정치',
             'source': 'EST_002', 'confidence': 'Medium',
             'notes': '성인교육 중 실무/직무교육 비중 (학위과정 제외)'},
            
            # ===== Bottom-Up Segment 1: 직장인 자기계발 =====
            {'id': 'SEG1_POPULATION', 'category': '세그먼트1', 'description': '경제활동인구',
             'value': 28_000_000, 'unit': '명', 'data_type': '직접데이터',
             'source': 'SRC_001', 'confidence': 'High',
             'notes': '통계청 2025년 경제활동인구 약 2,800만명'},
            
            {'id': 'SEG1_RATE', 'category': '세그먼트1', 'description': '연간 교육 참여율',
             'value': 0.35, 'unit': '%', 'data_type': '추정치',
             'source': 'EST_003', 'confidence': 'Medium',
             'notes': '직장인 중 연간 1회 이상 실무교육 참여 비율 약 35%'},
            
            {'id': 'SEG1_AOV', 'category': '세그먼트1', 'description': '1인당 연간 교육비',
             'value': 800_000, 'unit': '원', 'data_type': '추정치',
             'source': 'EST_004', 'confidence': 'Medium',
             'notes': '온/오프라인 강의, 자격증 등 포함 평균 80만원'},
            
            {'id': 'SEG1_FREQ', 'category': '세그먼트1', 'description': '연간 구매 횟수',
             'value': 1, 'unit': '회', 'data_type': '직접데이터',
             'source': 'SRC_002', 'confidence': 'High',
             'notes': '1인당 연간 평균 1회 (이미 AOV에 연간 총액 반영)'},
            
            # ===== Bottom-Up Segment 2: 기업 교육훈련 =====
            {'id': 'SEG2_COMPANIES', 'category': '세그먼트2', 'description': '기업 수 (100인 이상)',
             'value': 15_000, 'unit': '개', 'data_type': '직접데이터',
             'source': 'SRC_003', 'confidence': 'High',
             'notes': '통계청 기업체수 중 100인 이상 약 15,000개'},
            
            {'id': 'SEG2_RATE', 'category': '세그먼트2', 'description': '교육훈련 실시율',
             'value': 0.70, 'unit': '%', 'data_type': '추정치',
             'source': 'EST_005', 'confidence': 'Medium',
             'notes': '100인 이상 기업 중 체계적 교육훈련 실시 비율'},
            
            {'id': 'SEG2_AOV', 'category': '세그먼트2', 'description': '기업당 연간 교육비',
             'value': 50_000_000, 'unit': '원', 'data_type': '추정치',
             'source': 'EST_006', 'confidence': 'Medium',
             'notes': '외부 교육기관 지출 (내부 인건비 제외)'},
            
            {'id': 'SEG2_FREQ', 'category': '세그먼트2', 'description': '연간 계약',
             'value': 1, 'unit': '회', 'data_type': '직접데이터',
             'source': 'SRC_004', 'confidence': 'High',
             'notes': '연간 총액 기준'},
            
            # ===== Proxy Data (고용보험 직업능력개발 사업) =====
            {'id': 'PROXY_SIZE', 'category': 'Proxy', 'description': '고용보험 지원금 총액',
             'value': 2_000_000_000_000, 'unit': '원', 'data_type': '추정치',
             'source': 'EST_007', 'confidence': 'Medium',
             'notes': '연간 직업능력개발 지원금 약 2조원 (추정)'},
            
            {'id': 'PROXY_CORR', 'category': 'Proxy', 'description': '상관계수',
             'value': 0.80, 'unit': '%', 'data_type': '추정치',
             'source': 'EST_008', 'confidence': 'Medium',
             'notes': '고용보험 지원 교육과 민간 실무교육의 상관성'},
            
            {'id': 'PROXY_APP', 'category': 'Proxy', 'description': '적용 비율',
             'value': 5.0, 'unit': '배', 'data_type': '추정치',
             'source': 'EST_009', 'confidence': 'Low',
             'notes': '정부 지원금 1원당 민간 총 시장 약 5배 (지원금 + 자비 지출)'},
            
            # ===== Competitor Data (패스트캠퍼스 등 주요 플레이어) =====
            {'id': 'COMP_TOTAL_REV', 'category': '경쟁사', 'description': '상위 10개사 매출 합계',
             'value': 500_000_000_000, 'unit': '원', 'data_type': '추정치',
             'source': 'EST_010', 'confidence': 'Low',
             'notes': '패스트캠퍼스, 코드스테이츠, 인프런 등 합산 약 5,000억 추정'},
            
            {'id': 'COMP_SHARE', 'category': '경쟁사', 'description': '상위 10개사 시장점유율',
             'value': 0.08, 'unit': '%', 'data_type': '추정치',
             'source': 'EST_011', 'confidence': 'Low',
             'notes': '전체 시장 중 상위 플레이어 점유율 약 8% (매우 파편화)'},
        ],
        
        # TAM Definition
        'tam': {
            'value': 100_000_000_000_000,  # 100조
            'definition': '한국 교육시장 전체 (2025)',
            'source': 'TAM_VALUE',
            'narrowing_steps': [
                {'dimension': '연령', 'ratio_source': 'FILTER_ADULT', 
                 'description': '성인(20-59세) 교육 15% → 15조'},
                {'dimension': '목적', 'ratio_source': 'FILTER_PRACTICAL', 
                 'description': '실무/직무교육 60% → 9조'},
            ]
        },
        
        # Bottom-Up Segments
        'segments': [
            {
                'name': '직장인 자기계발',
                'target_customers': 'SEG1_POPULATION',
                'purchase_rate': 'SEG1_RATE',
                'aov': 'SEG1_AOV',
                'frequency': 'SEG1_FREQ'
            },
            {
                'name': '기업 교육훈련 (B2B)',
                'target_customers': 'SEG2_COMPANIES',
                'purchase_rate': 'SEG2_RATE',
                'aov': 'SEG2_AOV',
                'frequency': 'SEG2_FREQ'
            }
        ],
        
        # Proxy Data
        'proxy_data': {
            'proxy_market': 'PROXY_SIZE',
            'correlation': 'PROXY_CORR',
            'application_rate': 'PROXY_APP'
        },
        
        # Competitors
        'competitors': [
            {
                'company': '상위 10개 플레이어',
                'revenue': 'COMP_TOTAL_REV',
                'market_share': 'COMP_SHARE'
            }
        ],
        
        # 출력 디렉토리
        'output_dir': project_root / 'test_output'
    }
    
    print("🔢 핵심 가정:")
    print(f"   TAM: 한국 교육시장 100조원")
    print(f"   성인교육 비중: 15% → 15조원")
    print(f"   실무교육 비중: 60% → 9조원")
    print(f"   경제활동인구: 2,800만명")
    print(f"   연간 교육 참여율: 35%")
    print(f"   1인당 연간 교육비: 80만원\n")
    
    print("🚀 Market Sizing Excel 생성 중...\n")
    
    try:
        filepath = generator.generate(**data)
        
        print("\n" + "="*70)
        print("✅ 시장 규모 추정 완료!")
        print("="*70 + "\n")
        
        if filepath.exists():
            size_kb = filepath.stat().st_size / 1024
            
            print(f"📁 파일: {filepath.name}")
            print(f"📏 크기: {size_kb:.1f} KB\n")
            
            # 예상 SAM 계산 (Quick Preview)
            tam = 100_000_000_000_000
            sam_topdown = tam * 0.15 * 0.60  # 9조
            
            seg1_size = 28_000_000 * 0.35 * 800_000 * 1  # 7.84조
            seg2_size = 15_000 * 0.70 * 50_000_000 * 1  # 5,250억
            sam_bottomup = seg1_size + seg2_size  # 약 8.365조
            
            proxy_sam = 2_000_000_000_000 * 4.0  # 8조
            
            comp_sam = 500_000_000_000 / 0.08  # 6.25조
            
            print("📊 추정 결과 (SAM - Serviceable Available Market):")
            print(f"   Method 1 (Top-Down):    {sam_topdown/1_000_000_000_000:.1f}조원")
            print(f"   Method 2 (Bottom-Up):   {sam_bottomup/1_000_000_000_000:.1f}조원")
            print(f"   Method 3 (Proxy):       {proxy_sam/1_000_000_000_000:.1f}조원")
            print(f"   Method 4 (Competitor):  {comp_sam/1_000_000_000_000:.1f}조원\n")
            
            avg_sam = (sam_topdown + sam_bottomup + proxy_sam + comp_sam) / 4
            print(f"   ⭐ 평균 (4-Method):     {avg_sam/1_000_000_000_000:.1f}조원")
            print(f"   📐 범위:                6.3 ~ 9.0조원\n")
            
            print("📋 포함 내용:")
            print("   ✅ Summary Dashboard")
            print("   ✅ Assumptions (15개 가정)")
            print("   ✅ Estimation Details")
            print("   ✅ Method 1: Top-Down (100조 → 9조)")
            print("   ✅ Method 2: Bottom-Up (2개 세그먼트)")
            print("   ✅ Method 3: Proxy (고용보험 x4)")
            print("   ✅ Method 4: Competitor Revenue")
            print("   ✅ Convergence Analysis")
            print("   ✅ Scenarios (Best/Base/Worst)\n")
            
            print("💡 다음 단계:")
            print("   1. Excel 파일에서 상세 계산 확인")
            print("   2. Assumptions 시트에서 가정 조정")
            print("   3. Convergence 시트에서 ±30% 수렴 확인")
            print("   4. 신뢰도 < 50% 시 Domain Reasoner 고려\n")
            
            print("📈 해석:")
            print("   - 한국 실무교육시장 규모: 약 7~9조원 (2025)")
            print("   - B2C (자기계발): ~7.8조원 (주도)")
            print("   - B2B (기업교육): ~0.5조원")
            print("   - 신뢰도: Medium (±30-50%)")
            print("   - 오차 원인: TAM 추정치, 참여율 불확실성\n")
            
        return filepath
        
    except Exception as e:
        print(f"\n❌ 생성 실패: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    print("\n" + "="*70)
    print("🎓 한국 실무교육시장 규모 추정 (UMIS Guestimation)")
    print("="*70)
    
    filepath = estimate_korean_practical_education_market()
    
    if filepath:
        print("\n" + "="*70)
        print("🎉 분석 완료!")
        print(f"📁 파일: {filepath}")
        print("="*70 + "\n")
        sys.exit(0)
    else:
        print("\n❌ 분석 실패")
        sys.exit(1)

