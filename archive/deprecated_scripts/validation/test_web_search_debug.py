"""
Web Search 디버깅 테스트

실제 검색 결과를 상세히 출력하여 문제 진단
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.agents.estimator.sources.value import WebSearchSource
from umis_rag.agents.estimator.models import Context


def debug_search_with_details(question: str, context: Context = None):
    """검색 결과 상세 출력"""
    
    print("\n" + "="*80)
    print(f"질문: {question}")
    if context:
        print(f"컨텍스트: region={context.region}, domain={context.domain}")
    print("="*80)
    
    web_search = WebSearchSource()
    
    # 검색 쿼리 구성
    search_query = web_search._build_search_query(question, context)
    print(f"\n[검색 쿼리] {search_query}")
    
    # DuckDuckGo 검색
    print("\n[검색 중...]")
    results = web_search._search_duckduckgo(search_query)
    
    print(f"\n[검색 결과] {len(results)}개")
    
    # 각 결과 출력
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result.get('title', 'No Title')}")
        print(f"   URL: {result.get('href', 'No URL')}")
        print(f"   본문: {result.get('body', 'No Body')[:200]}...")
    
    # 숫자 추출
    print("\n" + "-"*80)
    print("[숫자 추출]")
    print("-"*80)
    
    extracted = web_search._extract_numbers_from_results(results, question)
    
    if extracted:
        print(f"\n추출된 숫자: {len(extracted)}개\n")
        for i, num in enumerate(extracted, 1):
            print(f"{i}. 값: {num['value']:,.2f}")
            print(f"   단위: {num['unit']}")
            print(f"   원본: {num['original']}")
            print(f"   출처: {num['source']}")
            print(f"   맥락: {num['context'][:100]}...")
            print()
    else:
        print("\n❌ 숫자 추출 실패!")
        print("   검색 결과에서 숫자 패턴을 찾을 수 없습니다.")
    
    # Consensus 확인
    if extracted:
        print("-"*80)
        print("[Consensus 알고리즘]")
        print("-"*80)
        
        consensus = web_search._find_consensus(extracted)
        
        if consensus:
            print(f"\n✅ Consensus 형성!")
            print(f"   값: {consensus['value']:,.2f}")
            print(f"   신뢰도: {consensus['confidence']:.0%}")
            print(f"   일치 개수: {consensus['count']}개")
            print(f"   출처:")
            for j, source in enumerate(consensus['sources'], 1):
                print(f"     {j}. {source}")
        else:
            print("\n❌ Consensus 형성 실패!")
            print("   값들이 너무 분산되어 있습니다 (±30% 범위 내 2개 이상 필요)")
            print("\n   추출된 값 분포:")
            for num in extracted:
                print(f"     - {num['value']:,.2f}")


def main():
    """메인 테스트"""
    
    print("\n" + "="*80)
    print(" "*20 + "Web Search 디버깅 테스트")
    print("="*80)
    
    # 테스트 1: 한국 인구 (실패했던 케이스)
    debug_search_with_details(
        "한국 인구는?",
        Context(region="한국")
    )
    
    # 테스트 2: 한국 인구 (영어로)
    debug_search_with_details(
        "South Korea population",
        Context(region="South Korea")
    )
    
    # 테스트 3: SaaS Churn Rate (실패했던 케이스)
    debug_search_with_details(
        "SaaS average monthly churn rate",
        Context(domain="B2B_SaaS", region="Global")
    )
    
    # 테스트 4: 간단한 수치 질문
    debug_search_with_details(
        "미국 인구",
        Context(region="미국")
    )
    
    print("\n" + "="*80)
    print(" "*25 + "디버깅 완료!")
    print("="*80)


if __name__ == "__main__":
    main()

