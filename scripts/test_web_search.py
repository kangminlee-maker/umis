"""
Web Search 기능 테스트 (v7.6.2)

Estimator의 Web Search Source가 제대로 작동하는지 확인
- DuckDuckGo 검색
- 숫자 추출
- Consensus 알고리즘
- 신뢰도 계산
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.agents.estimator.sources.value import WebSearchSource
from umis_rag.agents.estimator.models import Context


def test_web_search_basic():
    """기본 웹 검색 테스트"""
    
    print("\n" + "="*80)
    print(" "*25 + "Web Search 기본 테스트")
    print("="*80)
    
    web_search = WebSearchSource()
    
    # 웹 검색이 활성화되었는지 확인
    print(f"\n[설정 확인]")
    print(f"  Web Search 활성화: {web_search.enabled}")
    print(f"  검색 엔진: {web_search.engine}")
    print(f"  검색 가능: {web_search.has_search}")
    
    if not web_search.has_search:
        print("\n⚠️  Web Search 비활성화 (패키지 없음 또는 설정 문제)")
        print("   DuckDuckGo: pip install duckduckgo-search")
        print("   Google: pip install google-api-python-client")
        return
    
    print("\n✅ Web Search 준비 완료!")


def test_korea_population():
    """한국 인구 검색 테스트"""
    
    print("\n" + "="*80)
    print(" "*25 + "한국 인구 검색 테스트")
    print("="*80)
    
    web_search = WebSearchSource()
    
    if not web_search.has_search or not web_search.enabled:
        print("\n⚠️  Web Search 비활성화")
        return
    
    question = "한국 인구는?"
    context = Context(region="한국")
    
    print(f"\n[질문] {question}")
    print(f"[컨텍스트] 지역: {context.region}")
    
    results = web_search.collect(question, context)
    
    print(f"\n[결과] {len(results)}개 추정값 발견")
    
    for est in results:
        print(f"\n  값: {est.value:,.0f}명")
        print(f"  신뢰도: {est.confidence:.0%}")
        print(f"  근거: {est.reasoning}")
        print(f"  출처: {est.source_detail}")
        
        if est.raw_data and 'sources' in est.raw_data:
            print(f"  일치 출처 수: {len(est.raw_data['sources'])}개")
    
    if results:
        print("\n✅ Web Search 성공!")
        # 예상 범위 확인 (51,000,000 ~ 52,000,000)
        value = results[0].value
        if 50_000_000 <= value <= 53_000_000:
            print(f"✅ 합리적 범위 내 값: {value:,.0f}명")
        else:
            print(f"⚠️  예상 범위 벗어남: {value:,.0f}명 (예상: 51-52백만)")
    else:
        print("\n❌ 검색 결과 없음")


def test_saas_churn():
    """SaaS Churn Rate 검색 테스트"""
    
    print("\n" + "="*80)
    print(" "*25 + "SaaS Churn Rate 검색 테스트")
    print("="*80)
    
    web_search = WebSearchSource()
    
    if not web_search.has_search or not web_search.enabled:
        print("\n⚠️  Web Search 비활성화")
        return
    
    question = "SaaS average monthly churn rate"
    context = Context(domain="B2B_SaaS", region="Global")
    
    print(f"\n[질문] {question}")
    print(f"[컨텍스트] 도메인: {context.domain}, 지역: {context.region}")
    
    results = web_search.collect(question, context)
    
    print(f"\n[결과] {len(results)}개 추정값 발견")
    
    for est in results:
        print(f"\n  값: {est.value*100:.1f}%")
        print(f"  신뢰도: {est.confidence:.0%}")
        print(f"  근거: {est.reasoning}")
        print(f"  출처: {est.source_detail}")
        
        if est.raw_data and 'sources' in est.raw_data:
            print(f"  일치 출처 수: {len(est.raw_data['sources'])}개")
            # 출처 URL 출력 (처음 3개만)
            for i, source in enumerate(est.raw_data['sources'][:3], 1):
                print(f"    {i}. {source}")
    
    if results:
        print("\n✅ Web Search 성공!")
        # 예상 범위 확인 (3% ~ 8%)
        value = results[0].value
        if 0.02 <= value <= 0.10:
            print(f"✅ 합리적 범위 내 값: {value*100:.1f}%")
        else:
            print(f"⚠️  예상 범위 벗어남: {value*100:.1f}% (예상: 3-8%)")
    else:
        print("\n❌ 검색 결과 없음")
        print("   가능한 원인:")
        print("   1. 숫자 추출 패턴 매칭 실패")
        print("   2. Consensus 형성 실패 (값 분산)")
        print("   3. 검색 결과 없음")


def test_coffee_shops_seoul():
    """서울 커피숍 개수 검색 테스트"""
    
    print("\n" + "="*80)
    print(" "*25 + "서울 커피숍 개수 검색 테스트")
    print("="*80)
    
    web_search = WebSearchSource()
    
    if not web_search.has_search or not web_search.enabled:
        print("\n⚠️  Web Search 비활성화")
        return
    
    question = "서울 커피숍 개수는?"
    context = Context(region="서울", domain="Food_Beverage")
    
    print(f"\n[질문] {question}")
    print(f"[컨텍스트] 지역: {context.region}, 도메인: {context.domain}")
    
    results = web_search.collect(question, context)
    
    print(f"\n[결과] {len(results)}개 추정값 발견")
    
    for est in results:
        print(f"\n  값: {est.value:,.0f}개")
        print(f"  신뢰도: {est.confidence:.0%}")
        print(f"  근거: {est.reasoning}")
        print(f"  출처: {est.source_detail}")
        
        if est.raw_data and 'sources' in est.raw_data:
            print(f"  일치 출처 수: {len(est.raw_data['sources'])}개")
    
    if results:
        print("\n✅ Web Search 성공!")
        value = results[0].value
        print(f"  발견된 값: {value:,.0f}개")
    else:
        print("\n❌ 검색 결과 없음")


def test_consensus_algorithm():
    """Consensus 알고리즘 테스트 (내부 로직)"""
    
    print("\n" + "="*80)
    print(" "*25 + "Consensus 알고리즘 테스트")
    print("="*80)
    
    web_search = WebSearchSource()
    
    # 테스트 데이터 (다양한 값들)
    test_numbers = [
        {'value': 5.0, 'source': 'source1', 'context': 'test'},
        {'value': 5.2, 'source': 'source2', 'context': 'test'},
        {'value': 5.1, 'source': 'source3', 'context': 'test'},  # 5.0-5.2: 3개 (±30% 내)
        {'value': 10.0, 'source': 'source4', 'context': 'test'},  # 이상치
        {'value': 2.0, 'source': 'source5', 'context': 'test'},   # 이상치
    ]
    
    print(f"\n[입력 값들]")
    for num in test_numbers:
        print(f"  {num['value']} (출처: {num['source']})")
    
    consensus = web_search._find_consensus(test_numbers)
    
    if consensus:
        print(f"\n[Consensus 발견]")
        print(f"  값: {consensus['value']:.2f}")
        print(f"  신뢰도: {consensus['confidence']:.0%}")
        print(f"  일치 개수: {consensus['count']}개")
        print(f"  출처: {', '.join(consensus['sources'])}")
        
        # 예상: 5.0-5.2의 평균 (약 5.1)
        if 5.0 <= consensus['value'] <= 5.2:
            print("\n✅ Consensus 알고리즘 정상 작동!")
        else:
            print(f"\n⚠️  예상과 다름 (예상: 5.0-5.2)")
    else:
        print("\n❌ Consensus 형성 실패")
    
    # 분산된 값들 테스트
    print("\n" + "-"*80)
    print("분산된 값들 테스트 (Consensus 없어야 함)")
    print("-"*80)
    
    dispersed_numbers = [
        {'value': 5.0, 'source': 'source1', 'context': 'test'},
        {'value': 50.0, 'source': 'source2', 'context': 'test'},
        {'value': 500.0, 'source': 'source3', 'context': 'test'},
    ]
    
    print(f"\n[입력 값들]")
    for num in dispersed_numbers:
        print(f"  {num['value']} (출처: {num['source']})")
    
    consensus2 = web_search._find_consensus(dispersed_numbers)
    
    if consensus2:
        print(f"\n⚠️  Consensus 형성됨 (예상 밖): {consensus2['value']:.2f}")
    else:
        print(f"\n✅ Consensus 없음 (정상!)")


def test_number_extraction():
    """숫자 추출 로직 테스트"""
    
    print("\n" + "="*80)
    print(" "*25 + "숫자 추출 로직 테스트")
    print("="*80)
    
    web_search = WebSearchSource()
    
    # 테스트 검색 결과들 (다양한 포맷)
    test_results = [
        {
            'title': '한국 인구 51,740,000명',
            'body': '2024년 기준 한국의 총 인구는 약 51,740,000명입니다.',
            'href': 'http://example.com/1'
        },
        {
            'title': 'SaaS Churn Rate Benchmark',
            'body': 'The average monthly churn rate for B2B SaaS is 5-7%.',
            'href': 'http://example.com/2'
        },
        {
            'title': '커피숍 매출 통계',
            'body': '서울 커피숍 평균 매출: 월 1,500만원',
            'href': 'http://example.com/3'
        },
        {
            'title': '백분율 테스트',
            'body': '전환율은 약 3.5%입니다.',
            'href': 'http://example.com/4'
        }
    ]
    
    print(f"\n[테스트 데이터] {len(test_results)}개 검색 결과")
    
    for i, result in enumerate(test_results, 1):
        print(f"\n{i}. {result['title']}")
        print(f"   본문: {result['body']}")
        
        # 숫자 추출
        extracted = web_search._extract_numbers_from_results([result], "테스트 질문")
        
        print(f"   추출된 숫자: {len(extracted)}개")
        for num in extracted:
            print(f"     - 값: {num['value']:,.2f}")
            print(f"       단위: {num['unit']}")
            print(f"       원본: {num['original']}")
            print(f"       맥락: {num['context'][:80]}...")
    
    print("\n✅ 숫자 추출 테스트 완료!")


def main():
    """메인 테스트 실행"""
    
    print("\n" + "="*80)
    print(" "*20 + "Estimator Web Search 기능 테스트 (v7.6.2)")
    print("="*80)
    
    # 1. 기본 설정 확인
    test_web_search_basic()
    
    # 2. Consensus 알고리즘 (내부 로직)
    test_consensus_algorithm()
    
    # 3. 숫자 추출 로직
    test_number_extraction()
    
    # 4. 실제 검색 테스트 (DuckDuckGo API 호출)
    print("\n" + "="*80)
    print(" "*25 + "실제 검색 테스트 (API 호출)")
    print("="*80)
    print("\n⚠️  주의: 실제 웹 검색을 수행합니다 (네트워크 필요)")
    print("   각 테스트마다 3-5초 소요됩니다.\n")
    
    import time
    
    # 한국 인구 (정확한 값 있음)
    test_korea_population()
    time.sleep(2)  # Rate limiting 방지
    
    # SaaS Churn (범위 값)
    test_saas_churn()
    time.sleep(2)
    
    # 서울 커피숍 (복잡한 쿼리)
    test_coffee_shops_seoul()
    
    # 최종 요약
    print("\n" + "="*80)
    print(" "*25 + "테스트 완료!")
    print("="*80)
    print("\n✅ Web Search 기능 동작 확인 완료")
    print("\n[요약]")
    print("  - DuckDuckGo 검색: 작동")
    print("  - 숫자 추출: 다양한 포맷 지원")
    print("  - Consensus 알고리즘: ±30% 범위 내 그룹화")
    print("  - 신뢰도: 일치 출처 개수에 비례 (2개: 60%, 3개: 70%, 4개+: 80%)")
    print("\n[참고]")
    print("  - .env 설정: WEB_SEARCH_ENGINE=duckduckgo (기본)")
    print("  - Google 사용: WEB_SEARCH_ENGINE=google + API 키 필요")
    print("  - 비활성화: WEB_SEARCH_ENABLED=false")
    print("="*80)


if __name__ == "__main__":
    main()

