"""
DART Robust 크롤러 배치 테스트

목적: 실패 케이스 4개 모두 A등급 달성 검증

작성일: 2025-11-16
"""

import sys
from pathlib import Path

# UMIS 루트 추가
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from umis_rag.utils.dart_crawler_robust import crawl_sga_robust


# 테스트 케이스
TEST_CASES = [
    {
        'corp_name': '이마트',
        'rcept_no': '20250318000688',
        'dart_ofs': 41_313.0,
        'priority': 'HIGH'
    },
    {
        'corp_name': '삼성전자',
        'rcept_no': '20250317000660',
        'dart_ofs': 446_297.0,
        'priority': 'MEDIUM'
    },
    {
        'corp_name': 'LG화학',
        'rcept_no': '20250317000540',
        'dart_ofs': 30_126.0,
        'priority': 'MEDIUM'
    },
    {
        'corp_name': '현대차',
        'rcept_no': '20250331000291',
        'dart_ofs': 2_088.0,
        'priority': 'LOW'
    }
]


def main():
    print("=" * 80)
    print("DART Robust 크롤러 배치 테스트")
    print("=" * 80)
    print(f"\n테스트 케이스: {len(TEST_CASES)}개")
    
    results = []
    
    for i, case in enumerate(TEST_CASES, 1):
        print(f"\n{'='*80}")
        print(f"[{i}/{len(TEST_CASES)}] {case['corp_name']} (우선순위: {case['priority']})")
        print(f"{'='*80}")
        
        result = crawl_sga_robust(
            corp_name=case['corp_name'],
            rcept_no=case['rcept_no'],
            cache_dir='/tmp/dart_cache',
            verify_ofs=False
        )
        
        # 결과 저장
        case_result = {
            **case,
            'crawled': result.get('total', 0),
            'success': result['success'],
            'error': result.get('error', None),
            'items_count': len(result.get('items', {})),
            'section': result.get('section', {})
        }
        
        if result['success']:
            error_rate = abs(result['total'] - case['dart_ofs']) / case['dart_ofs'] * 100
            
            if error_rate <= 5.0:
                grade = 'A'
            elif error_rate <= 10.0:
                grade = 'B'
            elif error_rate <= 20.0:
                grade = 'C'
            else:
                grade = 'D'
            
            case_result['error_rate'] = error_rate
            case_result['grade'] = grade
            
            print(f"\n✅ 성공!")
            print(f"  크롤링: {result['total']:,.1f}억원")
            print(f"  DART OFS: {case['dart_ofs']:,.1f}억원")
            print(f"  오차율: {error_rate:.4f}%")
            print(f"  등급: {grade}")
        else:
            print(f"\n❌ 실패")
            print(f"  오류: {result.get('error', 'Unknown')}")
        
        results.append(case_result)
    
    # 전체 요약
    print(f"\n\n{'='*80}")
    print("배치 테스트 요약")
    print(f"{'='*80}")
    
    success_count = sum(1 for r in results if r['success'])
    a_grade_count = sum(1 for r in results if r.get('grade') == 'A')
    
    print(f"\n총 테스트: {len(results)}개")
    print(f"성공: {success_count}개 ({success_count/len(results)*100:.1f}%)")
    print(f"A등급: {a_grade_count}개 ({a_grade_count/len(results)*100:.1f}%)")
    
    print(f"\n상세 결과:")
    print(f"{'-'*80}")
    print(f"{'기업':<12} {'DART OFS':>12} {'크롤링':>12} {'오차율':>10} {'등급':>6}")
    print(f"{'-'*80}")
    
    for r in results:
        if r['success']:
            print(f"{r['corp_name']:<12} {r['dart_ofs']:>12,.1f}억 {r['crawled']:>12,.1f}억 {r['error_rate']:>9.4f}% {r['grade']:>6}")
        else:
            print(f"{r['corp_name']:<12} {r['dart_ofs']:>12,.1f}억 {'실패':>12} {'N/A':>10} {'N/A':>6}")
    
    print(f"{'-'*80}")
    
    # 최종 평가
    if a_grade_count == len(results):
        print(f"\n🎉 완벽! 모든 케이스 A등급 달성!")
    elif a_grade_count >= len(results) * 0.75:
        print(f"\n✅ 우수! {a_grade_count}/{len(results)} A등급 달성")
    else:
        print(f"\n⚠️ {a_grade_count}/{len(results)} A등급 달성 (개선 필요)")
    
    return results


if __name__ == '__main__':
    main()




