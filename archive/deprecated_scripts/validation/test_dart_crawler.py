"""
DART Selenium 크롤러 테스트 스크립트

사용법:
    # 1. 기본 테스트 (이마트, dcmNo 알고 있음)
    python scripts/test_dart_crawler.py

    # 2. dcmNo 자동 탐색
    python scripts/test_dart_crawler.py --auto

    # 3. 특정 기업
    python scripts/test_dart_crawler.py --corp 삼성전자 --rcept 20250317000660

    # 4. 배치 테스트 (수동 입력 4개)
    python scripts/test_dart_crawler.py --batch

작성일: 2025-11-16
버전: v1.0
"""

import sys
import argparse
from pathlib import Path

# UMIS 루트 추가
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from umis_rag.utils.dart_crawler_selenium import DARTCrawlerSelenium, crawl_sga_for_company


# 테스트 케이스 (수동 입력 4개)
TEST_CASES = [
    {
        'corp_name': '이마트',
        'rcept_no': '20250318000688',
        'dcm_no': '10420267',  # 알려진 dcmNo
        'dart_ofs': 41_313.0,
        'priority': 'HIGH'
    },
    {
        'corp_name': '삼성전자',
        'rcept_no': '20250317000660',
        'dcm_no': None,  # 탐색 필요
        'dart_ofs': 446_297.0,
        'priority': 'MEDIUM'
    },
    {
        'corp_name': 'LG화학',
        'rcept_no': '20250317000540',
        'dcm_no': None,
        'dart_ofs': 30_126.0,
        'priority': 'MEDIUM'
    },
    {
        'corp_name': '현대차',
        'rcept_no': '20250331000291',
        'dcm_no': None,
        'dart_ofs': 2_088.0,
        'priority': 'LOW'
    }
]


def test_single(corp_name: str, rcept_no: str, dcm_no: str = None, headless: bool = True):
    """단일 기업 테스트"""

    print("\n" + "=" * 80)
    print(f"🧪 테스트: {corp_name}")
    print("=" * 80)

    result = crawl_sga_for_company(
        corp_name=corp_name,
        rcept_no=rcept_no,
        dcm_no=dcm_no,
        headless=headless
    )

    # 결과 출력
    print("\n" + "=" * 80)
    print("📊 결과")
    print("=" * 80)

    if result['success']:
        print(f"✅ 크롤링 성공!")
        print(f"\n기업: {result['corp_name']}")
        print(f"접수번호: {result['rcept_no']}")
        print(f"dcmNo: {result['dcm_no']}")
        print(f"\n합계: {result['total']:,.1f}억원")
        print(f"항목 수: {len(result['items'])}개")
        print(f"단위: {result['unit']}")

        if 'dart_ofs' in result and result['dart_ofs']:
            print(f"\nDART OFS: {result['dart_ofs']:,.1f}억원")
            print(f"오차율: {abs(result['total'] - result['dart_ofs']) / result['dart_ofs'] * 100:.2f}%")
            print(f"등급: {result['grade']}")
            print(f"재무제표: {result['fs_type']}")

        print(f"\n상위 5개 항목:")
        sorted_items = sorted(
            result['items'].items(),
            key=lambda x: abs(x[1]),
            reverse=True
        )[:5]

        for item, amount in sorted_items:
            if result['unit'] == '백만원':
                print(f"  - {item}: {amount:,.0f}백만원 ({amount/100:,.1f}억원)")
            else:
                print(f"  - {item}: {amount:,.0f}{result['unit']}")

    else:
        print(f"❌ 크롤링 실패")
        print(f"오류: {result.get('error', 'Unknown')}")

    return result


def test_batch(headless: bool = True):
    """배치 테스트 (4개 수동 입력 케이스)"""

    print("\n" + "=" * 80)
    print("🧪 배치 테스트: 수동 입력 4개 케이스")
    print("=" * 80)

    results = []

    for i, case in enumerate(TEST_CASES, 1):
        print(f"\n[{i}/4] {case['corp_name']} (우선순위: {case['priority']})")

        result = crawl_sga_for_company(
            corp_name=case['corp_name'],
            rcept_no=case['rcept_no'],
            dcm_no=case['dcm_no'],
            headless=headless
        )

        results.append({
            **case,
            'result': result
        })

        # 간단한 결과
        if result['success']:
            print(f"  ✅ {result['total']:,.1f}억원 (등급: {result.get('grade', 'N/A')})")
        else:
            print(f"  ❌ {result.get('error', 'Unknown')}")

        print()

    # 전체 요약
    print("\n" + "=" * 80)
    print("📊 배치 테스트 요약")
    print("=" * 80)

    success_count = sum(1 for r in results if r['result']['success'])
    a_grade_count = sum(1 for r in results if r['result'].get('grade') == 'A')

    print(f"\n총 테스트: {len(results)}개")
    print(f"성공: {success_count}개 ({success_count/len(results)*100:.1f}%)")
    print(f"A등급: {a_grade_count}개 ({a_grade_count/len(results)*100:.1f}%)")

    print(f"\n상세 결과:")

    for r in results:
        result = r['result']

        if result['success']:
            print(f"  ✅ {r['corp_name']}: {result['total']:,.1f}억원 (등급: {result.get('grade', 'N/A')})")
        else:
            print(f"  ❌ {r['corp_name']}: {result.get('error', 'Unknown')}")

    return results


def test_auto_dcmno(corp_name: str, rcept_no: str, headless: bool = True):
    """dcmNo 자동 탐색 테스트"""

    print("\n" + "=" * 80)
    print(f"🧪 dcmNo 자동 탐색 테스트: {corp_name}")
    print("=" * 80)

    # dcmNo 없이 실행
    result = crawl_sga_for_company(
        corp_name=corp_name,
        rcept_no=rcept_no,
        dcm_no=None,  # 자동 탐색!
        headless=headless
    )

    # 결과
    if result['success']:
        print(f"\n✅ 자동 탐색 성공!")
        print(f"dcmNo: {result['dcm_no']}")
        print(f"합계: {result['total']:,.1f}억원")
        print(f"등급: {result.get('grade', 'N/A')}")
    else:
        print(f"\n❌ 자동 탐색 실패")
        print(f"오류: {result.get('error', 'Unknown')}")

    return result


def main():
    parser = argparse.ArgumentParser(
        description="DART Selenium 크롤러 테스트"
    )

    parser.add_argument(
        '--corp',
        type=str,
        default='이마트',
        help='기업명 (기본: 이마트)'
    )

    parser.add_argument(
        '--rcept',
        type=str,
        default='20250318000688',
        help='사업보고서 접수번호'
    )

    parser.add_argument(
        '--dcm',
        type=str,
        default='10420267',
        help='감사보고서 dcmNo (없으면 자동 탐색)'
    )

    parser.add_argument(
        '--auto',
        action='store_true',
        help='dcmNo 자동 탐색 모드'
    )

    parser.add_argument(
        '--batch',
        action='store_true',
        help='배치 테스트 (4개 수동 입력 케이스)'
    )

    parser.add_argument(
        '--no-headless',
        action='store_true',
        help='브라우저 표시 (디버깅용)'
    )

    args = parser.parse_args()

    headless = not args.no_headless

    # 배치 테스트
    if args.batch:
        test_batch(headless=headless)

    # dcmNo 자동 탐색 테스트
    elif args.auto:
        test_auto_dcmno(
            corp_name=args.corp,
            rcept_no=args.rcept,
            headless=headless
        )

    # 단일 테스트
    else:
        test_single(
            corp_name=args.corp,
            rcept_no=args.rcept,
            dcm_no=args.dcm if args.dcm else None,
            headless=headless
        )


if __name__ == '__main__':
    main()




