"""
Google Custom Search API 테스트

실제 Google 검색을 통해 Web Search 기능 검증
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.agents.estimator.sources.value import WebSearchSource
from umis_rag.agents.estimator.models import Context


def test_google_search_simple():
    """간단한 Google 검색 테스트"""
    
    print("\n" + "="*80)
    print(" "*25 + "Google Search 테스트")
    print("="*80)
    
    web_search = WebSearchSource()
    
    print(f"\n[설정 확인]")
    print(f"  엔진: {web_search.engine}")
    print(f"  활성화: {web_search.has_search}")
    
    if not web_search.has_search:
        print("\n❌ Google Search 비활성화 (API 키 또는 패키지 문제)")
        return
    
    print("\n✅ Google Search 준비 완료!")
    
    # 테스트 쿼리들
    test_cases = [
        {
            'question': 'South Korea population 2024',
            'context': Context(region="South Korea"),
            'expected_range': (50_000_000, 53_000_000),
            'description': '한국 인구 (명확한 통계)'
        },
        {
            'question': 'average SaaS monthly churn rate',
            'context': Context(domain="B2B_SaaS"),
            'expected_range': (0.02, 0.10),  # 2-10%
            'description': 'SaaS Churn Rate (범위 값)'
        },
        {
            'question': 'United States population 2024',
            'context': Context(region="USA"),
            'expected_range': (330_000_000, 340_000_000),
            'description': '미국 인구 (대규모 통계)'
        },
    ]
    
    results_summary = []
    
    for i, test in enumerate(test_cases, 1):
        print("\n" + "-"*80)
        print(f"테스트 {i}/{len(test_cases)}: {test['description']}")
        print("-"*80)
        
        print(f"\n[질문] {test['question']}")
        
        # 검색 실행
        estimates = web_search.collect(test['question'], test['context'])
        
        if estimates:
            est = estimates[0]
            print(f"\n✅ 검색 성공!")
            print(f"  값: {est.value:,.2f}")
            print(f"  신뢰도: {est.confidence:.0%}")
            print(f"  근거: {est.reasoning}")
            
            # 범위 확인
            expected_min, expected_max = test['expected_range']
            if expected_min <= est.value <= expected_max:
                print(f"  ✅ 합리적 범위 내 ({expected_min:,.0f} ~ {expected_max:,.0f})")
                results_summary.append((test['description'], '✅ 성공', est.value))
            else:
                print(f"  ⚠️  범위 벗어남 (예상: {expected_min:,.0f} ~ {expected_max:,.0f})")
                results_summary.append((test['description'], '⚠️ 범위 벗어남', est.value))
            
            # 출처 정보
            if est.raw_data and 'sources' in est.raw_data:
                print(f"  일치 출처: {len(est.raw_data['sources'])}개")
                for j, source in enumerate(est.raw_data['sources'][:3], 1):
                    print(f"    {j}. {source}")
        else:
            print(f"\n❌ 검색 실패")
            print(f"  가능한 원인:")
            print(f"    - 숫자 추출 패턴 매칭 실패")
            print(f"    - Consensus 형성 실패 (값 분산)")
            print(f"    - Google API 할당량 초과")
            results_summary.append((test['description'], '❌ 실패', None))
    
    # 최종 요약
    print("\n" + "="*80)
    print(" "*30 + "테스트 요약")
    print("="*80)
    
    for desc, status, value in results_summary:
        value_str = f"{value:,.2f}" if value else "N/A"
        print(f"{status} {desc}: {value_str}")
    
    success_count = sum(1 for _, status, _ in results_summary if status == '✅ 성공')
    print(f"\n성공률: {success_count}/{len(test_cases)} ({success_count/len(test_cases)*100:.0f}%)")
    
    print("\n" + "="*80)


def test_google_vs_duckduckgo():
    """Google vs DuckDuckGo 품질 비교 (선택적)"""
    
    print("\n" + "="*80)
    print(" "*20 + "Google vs DuckDuckGo 품질 비교")
    print("="*80)
    
    print("\n⚠️  이 테스트는 .env에서 엔진을 수동으로 변경해야 합니다.")
    print("   1. WEB_SEARCH_ENGINE=google → 테스트")
    print("   2. WEB_SEARCH_ENGINE=duckduckgo → 테스트")
    print("   3. 결과 비교")
    print("\n현재는 Google만 테스트합니다.")


def main():
    """메인 테스트"""
    
    print("\n" + "="*80)
    print(" "*20 + "Estimator Google Web Search 테스트")
    print("="*80)
    
    # Google 검색 테스트
    test_google_search_simple()
    
    # 비교 테스트 (선택적)
    # test_google_vs_duckduckgo()
    
    print("\n" + "="*80)
    print(" "*30 + "완료!")
    print("="*80)
    
    print("\n[참고]")
    print("  - Google API 할당량: 무료 100쿼리/일")
    print("  - 초과 시 비용: $5/1000쿼리")
    print("  - 현재 사용량 확인: https://console.cloud.google.com/apis/dashboard")


if __name__ == "__main__":
    main()

