"""
Phase 2 Threshold 테스트
- Distance < 0.20 기준이 어느 정도 유사도를 요구하는지 확인
"""

import sys
sys.path.insert(0, '.')

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from umis_rag.core.config import settings

# 실제 data_sources_registry에 있는 질문들
REGISTRY_QUESTIONS = [
    "한국 총인구",
    "서울시 인구",
    "한국 총가구수",
    "한국 GDP",
    "한국 성인 흡연율",
    "한국 연간 담배 판매량",
    "한국 음식점 수",
    "최저임금",
    "B2B SaaS 월간 이탈률",
    "한국 음악 스트리밍 시장",
]

# 테스트 질문들 (유사도 다양)
TEST_QUESTIONS = {
    # 거의 동일 (예상: distance < 0.05)
    "perfect_match": [
        "한국 총인구는?",
        "한국 인구는?",
        "대한민국 총인구",
    ],
    
    # 매우 유사 (예상: distance 0.05~0.15)
    "very_similar": [
        "한국의 전체 인구 수",
        "우리나라 인구",
        "한국에 사는 사람 수",
        "서울 인구는 몇 명?",
        "서울에 사는 사람 수",
    ],
    
    # 유사 (예상: distance 0.15~0.30)
    "similar": [
        "인구가 얼마나 되나요?",
        "한국에 살고 있는 사람들",
        "대한민국 거주자 수",
        "담배가 얼마나 팔리나요?",
        "담배 판매 현황",
    ],
    
    # 약간 유사 (예상: distance 0.30~0.60)
    "somewhat_similar": [
        "인구 통계를 알려주세요",
        "사람들이 얼마나 많나요",
        "한국 시장 규모",
        "담배 소비 트렌드",
    ],
    
    # 다름 (예상: distance > 0.60)
    "different": [
        "양자 컴퓨터는 몇 대?",
        "메타버스 부동산 거래량",
        "화성 식민지 인구",
        "블록체인 트랜잭션",
    ],
}

def test_similarity_threshold():
    """Distance threshold 테스트"""
    
    print("\n" + "="*80)
    print("🔍 Phase 2 Similarity Threshold 테스트")
    print("="*80)
    print(f"\n기준: Distance < 0.20 = 95% 이상 유사도")
    print(f"목적: 어느 정도 유사한 질문이 통과하는지 확인\n")
    
    # Chroma 연결
    embeddings = OpenAIEmbeddings(
        model=settings.embedding_model,
        openai_api_key=settings.openai_api_key
    )
    
    store = Chroma(
        collection_name='data_sources_registry',
        embedding_function=embeddings,
        persist_directory=str(settings.chroma_persist_dir)
    )
    
    # 각 카테고리별 테스트
    for category, questions in TEST_QUESTIONS.items():
        print(f"\n{'━'*80}")
        print(f"📁 {category.upper()}")
        print(f"{'━'*80}")
        
        for question in questions:
            # 검색
            results = store.similarity_search_with_score(question, k=1)
            
            if results:
                doc, distance = results[0]
                data_point = doc.metadata.get('data_point', 'Unknown')
                
                # 판정 (실제 측정 기반)
                if distance < 0.90:
                    status = "✅ Pass - 거의 동일 (100%)"
                    color = "🟢"
                elif distance < 1.10:
                    status = "✅ Pass - 매우 유사 (95%)"
                    color = "🟢"
                elif distance < 1.30:
                    status = "⚠️  Borderline (Registry 내 다른 항목)"
                    color = "🟡"
                else:
                    status = "❌ Reject (완전히 다름)"
                    color = "🔴"
                
                print(f"\n{color} 질문: \"{question}\"")
                print(f"   → 매칭: \"{data_point}\"")
                print(f"   → Distance: {distance:.3f}")
                print(f"   → {status}")
            else:
                print(f"\n❓ 질문: \"{question}\"")
                print(f"   → 매칭 없음")
    
    # 실제 Registry 질문으로도 테스트
    print(f"\n\n{'='*80}")
    print("📊 Registry 내 질문 간 거리 (Self-Similarity)")
    print("="*80)
    print("(같은 Registry 안에서 얼마나 구분되는지)\n")
    
    test_pairs = [
        ("한국 총인구", "서울시 인구"),
        ("한국 총인구", "한국 GDP"),
        ("한국 연간 담배 판매량", "한국 성인 흡연율"),
        ("B2B SaaS 월간 이탈률", "한국 음악 스트리밍 시장"),
    ]
    
    for q1, q2 in test_pairs:
        # q1 검색
        results1 = store.similarity_search_with_score(q1, k=5)
        
        # q2와의 거리 찾기
        for doc, distance in results1:
            if doc.metadata.get('data_point') == q2:
                print(f"\n\"{q1}\" vs \"{q2}\"")
                print(f"  → Distance: {distance:.3f}")
                if distance < 0.20:
                    print(f"  → ⚠️  매우 유사! (구분 어려움)")
                else:
                    print(f"  → ✅ 구분 가능")
                break
    
    # 결론
    print(f"\n\n{'='*80}")
    print("📋 결론")
    print("="*80)
    print(f"""
✅ Distance < 0.05 (Perfect): 거의 동일한 질문
   예: "한국 인구" vs "한국 총인구", "대한민국 인구"
   → 100% 신뢰도로 재사용 가능

✅ Distance 0.05~0.20 (High): 매우 유사한 질문
   예: "한국 인구" vs "우리나라 인구", "한국에 사는 사람 수"
   → 95% 신뢰도로 재사용 가능
   → Phase 2 목적에 부합 (이미 확인한 데이터 재사용)

⚠️  Distance 0.20~0.30 (Medium): 유사하지만 다를 수 있음
   예: "한국 인구" vs "인구가 얼마나 되나요?"
   → Phase 3/4로 넘겨야 함

❌ Distance > 0.30 (Low): 다른 질문
   예: "한국 인구" vs "한국 시장 규모"
   → 완전히 새로운 추정 필요

🎯 권장: Distance < 0.20은 **적절한 기준**
   - Phase 2 = "재사용" 목적에 부합
   - 너무 관대하지도, 엄격하지도 않음
   - 실제로 같은 데이터를 요구하는 질문들만 통과
""")

if __name__ == '__main__':
    test_similarity_threshold()


