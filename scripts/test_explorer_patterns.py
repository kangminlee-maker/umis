#!/usr/bin/env python3
"""
Explorer RAG 패턴 검색 테스트 스크립트
개선사항:
1. get_pattern_details() 헬퍼 메서드 사용
2. load_dotenv()로 환경변수 로드
"""

import sys
from pathlib import Path

# 프로젝트 루트 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 환경변수 로드 (중요!)
from dotenv import load_dotenv
load_dotenv()

from umis_rag.agents.explorer import ExplorerRAG


def main():
    """Explorer RAG 패턴 검색 테스트"""
    
    print("=" * 80)
    print("Explorer RAG 패턴 검색 테스트 (개선 버전)")
    print("=" * 80)
    print()
    
    # Explorer 초기화
    print("🔧 Explorer 초기화 중...")
    explorer = ExplorerRAG()
    print("✅ Explorer 초기화 완료")
    print()
    
    # 테스트 쿼리
    queries = [
        'SaaS 구독 모델',
        '마케팅 자동화 플랫폼',
        'B2B SaaS',
        'freemium 비즈니스 모델'
    ]
    
    for query in queries:
        print(f"📌 Query: \"{query}\"")
        print("-" * 80)
        
        # 1. 패턴 검색 (tuple 반환)
        results = explorer.search_patterns(query, top_k=3)
        
        # 2. 헬퍼 메서드로 변환 (dict 반환)
        pattern_details = explorer.get_pattern_details(results)
        
        # 3. 출력
        for i, pattern in enumerate(pattern_details, 1):
            print(f"  {i}. [{pattern['pattern_id']}] {pattern['pattern_name']}")
            print(f"     카테고리: {pattern['category']}")
            print(f"     유사도: {pattern['score']:.4f}")
            print(f"     설명: {pattern['description'][:100]}...")
            print()
        
        print()


if __name__ == "__main__":
    main()


