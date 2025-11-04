#!/usr/bin/env python3
"""
Agent RAG 검색 테스트
6개 신규 Collection 검색 테스트
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.agents.quantifier import QuantifierRAG
from umis_rag.agents.validator import ValidatorRAG
from umis_rag.agents.observer import ObserverRAG


def test_quantifier_rag():
    """Quantifier RAG 테스트"""
    
    print("\n" + "="*60)
    print("🧪 Quantifier RAG 테스트")
    print("="*60)
    
    quantifier = QuantifierRAG()
    
    # Test 1: 계산 방법론 검색
    print("\n[Test 1] SAM 계산 방법론 검색")
    print("-" * 60)
    
    results = quantifier.search_methodology("SAM 계산", top_k=3)
    
    print(f"검색 결과: {len(results)}개")
    for i, (doc, score) in enumerate(results, 1):
        metadata = doc.metadata
        print(f"\n{i}. ID: {metadata.get('id', 'N/A')}")
        print(f"   유사도: {score:.3f}")
        print(f"   내용 (처음 100자): {doc.page_content[:100]}...")
    
    # Test 2: 벤치마크 검색
    print("\n[Test 2] SaaS 벤치마크 검색")
    print("-" * 60)
    
    results = quantifier.search_benchmark("SaaS churn rate", top_k=3)
    
    print(f"검색 결과: {len(results)}개")
    for i, (doc, score) in enumerate(results, 1):
        metadata = doc.metadata
        print(f"\n{i}. ID: {metadata.get('id', 'N/A')}")
        print(f"   유사도: {score:.3f}")
        print(f"   내용 (처음 100자): {doc.page_content[:100]}...")


def test_validator_rag():
    """Validator RAG 테스트"""
    
    print("\n" + "="*60)
    print("🧪 Validator RAG 테스트")
    print("="*60)
    
    validator = ValidatorRAG()
    
    # Test 1: 데이터 소스 검색
    print("\n[Test 1] 한국 통계 소스 검색")
    print("-" * 60)
    
    results = validator.search_data_source("한국 통계청", top_k=3)
    
    print(f"검색 결과: {len(results)}개")
    for i, (doc, score) in enumerate(results, 1):
        metadata = doc.metadata
        print(f"\n{i}. ID: {metadata.get('id', 'N/A')}")
        print(f"   유사도: {score:.3f}")
        print(f"   내용 (처음 100자): {doc.page_content[:100]}...")
    
    # Test 2: 정의 검증 사례 검색
    print("\n[Test 2] MAU 정의 검색")
    print("-" * 60)
    
    results = validator.search_definition_case("MAU 정의", top_k=3)
    
    print(f"검색 결과: {len(results)}개")
    for i, (doc, score) in enumerate(results, 1):
        metadata = doc.metadata
        print(f"\n{i}. ID: {metadata.get('id', 'N/A')}")
        print(f"   유사도: {score:.3f}")
        print(f"   내용 (처음 100자): {doc.page_content[:100]}...")


def test_observer_rag():
    """Observer RAG 테스트"""
    
    print("\n" + "="*60)
    print("🧪 Observer RAG 테스트")
    print("="*60)
    
    observer = ObserverRAG()
    
    # Test 1: 시장 구조 패턴 검색
    print("\n[Test 1] 독과점 시장 구조 검색")
    print("-" * 60)
    
    results = observer.search_structure_pattern("독과점 시장", top_k=3)
    
    print(f"검색 결과: {len(results)}개")
    for i, (doc, score) in enumerate(results, 1):
        metadata = doc.metadata
        print(f"\n{i}. ID: {metadata.get('id', 'N/A')}")
        print(f"   유사도: {score:.3f}")
        print(f"   내용 (처음 100자): {doc.page_content[:100]}...")
    
    # Test 2: 가치사슬 벤치마크 검색
    print("\n[Test 2] 이커머스 가치사슬 검색")
    print("-" * 60)
    
    results = observer.search_value_chain("이커머스 물류", top_k=3)
    
    print(f"검색 결과: {len(results)}개")
    for i, (doc, score) in enumerate(results, 1):
        metadata = doc.metadata
        print(f"\n{i}. ID: {metadata.get('id', 'N/A')}")
        print(f"   유사도: {score:.3f}")
        print(f"   내용 (처음 100자): {doc.page_content[:100]}...")


def main():
    """메인 함수"""
    
    print("\n" + "="*60)
    print("🚀 Agent RAG 검색 테스트 시작")
    print("="*60)
    
    try:
        # Quantifier
        test_quantifier_rag()
        
        # Validator
        test_validator_rag()
        
        # Observer
        test_observer_rag()
        
        print("\n" + "="*60)
        print("🎉 모든 테스트 완료!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        exit(1)


if __name__ == "__main__":
    main()

