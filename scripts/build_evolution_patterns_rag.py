#!/usr/bin/env python3
"""
market_evolution_patterns.yaml → ChromaDB Collection 구축

Collection: historical_evolution_patterns
Agent: Observer
"""

import yaml
from pathlib import Path

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

import sys
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.core.config import settings


def build_evolution_patterns_collection():
    """
    historical_evolution_patterns Collection 구축
    """
    
    print("🚀 Historical Evolution Patterns Collection 구축 시작")
    print()
    
    # 1. YAML 로드
    yaml_file = project_root / 'data/raw/market_evolution_patterns.yaml'
    
    if not yaml_file.exists():
        print(f"❌ 파일 없음: {yaml_file}")
        return
    
    with open(yaml_file) as f:
        data = yaml.safe_load(f)
    
    patterns = data.get('patterns', [])
    print(f"✅ {len(patterns)}개 패턴 로드")
    print()
    
    # 2. 문서 생성
    documents = []
    metadatas = []
    ids = []
    
    for pattern in patterns:
        pattern_id = pattern.get('pattern_id', 'unknown')
        
        # Content: 전체 패턴을 검색 가능한 텍스트로
        content_parts = [
            f"# {pattern.get('pattern_name', '')}",
            f"\nPattern ID: {pattern_id}",
            f"\nType: {pattern.get('pattern_type', '')}",
            f"\nDescription: {pattern.get('description', '')}",
        ]
        
        # Phases 추가
        if 'phases' in pattern:
            content_parts.append("\n## Phases:")
            for phase in pattern['phases']:
                phase_name = phase.get('phase', '')
                chars = phase.get('characteristics', [])
                content_parts.append(f"\n### {phase_name}")
                if isinstance(chars, dict):
                    for category, items in chars.items():
                        if isinstance(items, list):
                            content_parts.append(f"\n{category}: {', '.join(str(i) for i in items)}")
                elif isinstance(chars, list):
                    content_parts.append(f"\nCharacteristics: {', '.join(str(c) for c in chars)}")
        
        # Case Studies 추가
        if 'case_studies' in pattern:
            content_parts.append("\n## Case Studies:")
            cases = pattern['case_studies']
            if isinstance(cases, list):
                if cases and isinstance(cases[0], dict):
                    for case in cases:
                        market = case.get('market', '')
                        content_parts.append(f"\n- {market}")
                else:
                    content_parts.append(f"\n{', '.join(str(c) for c in cases)}")
        
        content = '\n'.join(content_parts)
        
        # Metadata
        metadata = {
            'pattern_id': pattern_id,
            'pattern_name': pattern.get('pattern_name', ''),
            'pattern_type': pattern.get('pattern_type', ''),
            'has_case_studies': 'case_studies' in pattern
        }
        
        documents.append(content)
        metadatas.append(metadata)
        ids.append(pattern_id)
        
        print(f"  📦 {pattern_id}: {pattern.get('pattern_name', '')}")
    
    print()
    print(f"✅ {len(documents)}개 문서 생성")
    print()
    
    # 3. ChromaDB에 추가
    print("🔨 ChromaDB Collection 구축 중...")
    
    embeddings = OpenAIEmbeddings(
        model=settings.embedding_model,
        openai_api_key=settings.openai_api_key
    )
    
    # 기존 Collection 삭제 (재구축)
    try:
        import chromadb
        client = chromadb.PersistentClient(path=str(settings.chroma_persist_dir))
        client.delete_collection("historical_evolution_patterns")
        print("🗑️  기존 Collection 삭제")
    except Exception:
        pass
    
    # 새 Collection 생성
    collection = Chroma.from_texts(
        texts=documents,
        metadatas=metadatas,
        ids=ids,
        embedding=embeddings,
        collection_name="historical_evolution_patterns",
        persist_directory=str(settings.chroma_persist_dir)
    )
    
    print(f"✅ {len(documents)}개 패턴 인덱싱 완료")
    print()
    
    # 4. 검증
    print("🔍 검증 중...")
    count = collection._collection.count()
    print(f"  Collection 크기: {count}개")
    
    # 테스트 검색
    test_results = collection.similarity_search("독점에서 경쟁으로 전환", k=2)
    print(f"  테스트 검색: {len(test_results)}개 결과")
    
    if test_results:
        top_result = test_results[0]
        print(f"    Top 결과: {top_result.metadata.get('pattern_name', 'N/A')}")
    
    print()
    print("🎉 historical_evolution_patterns Collection 구축 완료!")
    print()
    print("다음 단계:")
    print("  1. Observer에서 사용: observer.evolution_store 활성화")
    print("  2. 패턴 매칭 테스트: python3 tests/test_evolution_patterns_rag.py")


if __name__ == "__main__":
    build_evolution_patterns_collection()

