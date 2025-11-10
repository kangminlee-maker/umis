"""
Data Sources Registry 구축 스크립트

Validator가 확정 데이터 검색에 사용할 data_sources_registry 구축
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import yaml
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

from umis_rag.core.config import settings
from umis_rag.utils.logger import logger


def load_yaml_data(yaml_path: Path) -> dict:
    """YAML 파일 로드"""
    with open(yaml_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def create_documents(data: dict) -> list[Document]:
    """
    YAML 데이터를 Chroma Document로 변환
    
    각 데이터 소스를:
    - content: 설명 텍스트 (검색용)
    - metadata: 값, 출처, 정의 등 (추출용)
    """
    documents = []
    
    # 카테고리별 처리
    categories = [
        'official_statistics',
        'industry_benchmarks',
        'market_data',
        'constants'
    ]
    
    for category in categories:
        if category not in data:
            continue
        
        category_data = data[category]
        
        for key, source_info in category_data.items():
            # Content 생성 (검색용 텍스트)
            content_parts = []
            
            # 데이터 포인트
            data_point = source_info.get('data_point', key)
            content_parts.append(f"데이터: {data_point}")
            
            # 출처
            source_name = source_info.get('source_name', 'Unknown')
            content_parts.append(f"출처: {source_name}")
            
            # 카테고리
            cat = source_info.get('category', category)
            content_parts.append(f"분류: {cat}")
            
            # 정의
            if 'definition' in source_info:
                content_parts.append(f"정의: {source_info['definition']}")
            
            # 관련 질문들 (중요!)
            if 'related_queries' in source_info:
                queries = ", ".join(source_info['related_queries'])
                content_parts.append(f"관련 질문: {queries}")
            
            # 노트
            if 'notes' in source_info:
                notes = ", ".join(source_info['notes'])
                content_parts.append(f"참고: {notes}")
            
            content = "\n".join(content_parts)
            
            # Metadata 생성 (값 추출용)
            metadata = {
                'source_id': source_info.get('source_id', f"{category.upper()}-{key}"),
                'source_name': source_name,
                'category': cat,
                'data_point': data_point,
                
                # 값 (핵심!)
                'value': source_info.get('value'),
                'unit': source_info.get('unit', ''),
                'definition': source_info.get('definition', ''),
                
                # 메타 정보
                'year': source_info.get('metadata', {}).get('year', ''),
                'reliability': source_info.get('metadata', {}).get('reliability', 'medium'),
                'access_method': source_info.get('metadata', {}).get('access_method', ''),
            }
            
            # Derived 값 (일일 판매량 등)
            if 'derived' in source_info:
                for derived_key, derived_val in source_info['derived'].items():
                    # Derived 값을 별도 Document로 (검색 강화)
                    derived_content_parts = [
                        f"파생 데이터: {derived_key}",
                        f"원본: {data_point}",
                        f"출처: {source_name}",
                        f"계산: {derived_val.get('formula', '')}",
                        f"값: {derived_val.get('value')} {derived_val.get('unit', '')}"
                    ]
                    
                    # 원본 related_queries도 포함 (검색 강화!)
                    if 'related_queries' in source_info:
                        derived_content_parts.append(f"관련 질문: {', '.join(source_info['related_queries'])}")
                    
                    derived_content = "\n".join(derived_content_parts)
                    
                    derived_metadata = metadata.copy()
                    derived_metadata['source_id'] = f"{metadata['source_id']}_derived_{derived_key}"
                    derived_metadata['value'] = derived_val.get('value')
                    derived_metadata['unit'] = derived_val.get('unit', '')
                    derived_metadata['formula'] = derived_val.get('formula', '')
                    derived_metadata['is_derived'] = True
                    derived_metadata['data_point'] = f"{data_point} ({derived_key})"
                    
                    documents.append(Document(
                        page_content=derived_content,
                        metadata=derived_metadata
                    ))
            
            # Distribution 추가 (범위 정보)
            if 'distribution' in source_info:
                metadata['has_distribution'] = True
                dist = source_info['distribution']
                for k, v in dist.items():
                    metadata[f'dist_{k}'] = v
            
            # Range 추가
            if 'range' in source_info:
                range_val = source_info['range']
                if isinstance(range_val, dict):
                    for k, v in range_val.items():
                        metadata[f'range_{k}'] = v
            
            # None 값 제거 (Chroma 요구사항)
            metadata = {k: v for k, v in metadata.items() if v is not None}
            
            # Document 생성
            documents.append(Document(
                page_content=content,
                metadata=metadata
            ))
    
    return documents


def build_index(yaml_path: Path, collection_name: str = "data_sources_registry"):
    """
    Data Sources Registry 인덱스 구축
    
    Args:
        yaml_path: YAML 파일 경로
        collection_name: Chroma collection 이름
    """
    logger.info(f"[Build] {collection_name} 구축 시작")
    logger.info(f"  YAML: {yaml_path}")
    
    # 1. YAML 로드
    data = load_yaml_data(yaml_path)
    logger.info(f"  ✅ YAML 로드 완료")
    
    # 2. Documents 생성
    documents = create_documents(data)
    logger.info(f"  ✅ {len(documents)}개 Document 생성")
    
    # 3. Embeddings 초기화
    embeddings = OpenAIEmbeddings(
        model=settings.embedding_model,
        openai_api_key=settings.openai_api_key
    )
    logger.info(f"  ✅ Embeddings 준비")
    
    # 4. Chroma 초기화 (기존 삭제 후 재구축)
    try:
        import chromadb
        
        client = chromadb.PersistentClient(
            path=str(settings.chroma_persist_dir)
        )
        
        # 기존 collection 삭제
        try:
            client.delete_collection(collection_name)
            logger.info(f"  ✅ 기존 collection 삭제")
        except Exception:
            pass
        
        # 새 collection 생성
        vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=embeddings,
            collection_name=collection_name,
            persist_directory=str(settings.chroma_persist_dir)
        )
        
        logger.info(f"  ✅ Chroma Collection 생성")
        logger.info(f"  ✅ {len(documents)}개 청크 색인화")
        
    except Exception as e:
        logger.error(f"  ❌ Chroma 구축 실패: {e}")
        raise
    
    # 5. 검증
    collection = vectorstore._collection
    count = collection.count()
    
    logger.info(f"\n✅ 구축 완료!")
    logger.info(f"  Collection: {collection_name}")
    logger.info(f"  총 청크: {count}개")
    
    # 샘플 검색 테스트
    logger.info(f"\n🔍 검색 테스트:")
    
    test_queries = [
        "한국 인구는?",
        "담배 판매량은?",
        "SaaS 이탈률은?"
    ]
    
    for query in test_queries:
        results = vectorstore.similarity_search_with_score(query, k=1)
        
        if results:
            doc, score = results[0]
            source = doc.metadata.get('source_name', 'Unknown')
            value = doc.metadata.get('value', 'N/A')
            
            logger.info(f"  '{query}'")
            logger.info(f"    → {source}: {value} (유사도: {score:.3f})")
        else:
            logger.info(f"  '{query}' → 결과 없음")
    
    return vectorstore


def main():
    """메인 실행"""
    print("=" * 80)
    print("Data Sources Registry 구축")
    print("=" * 80)
    print()
    
    # YAML 경로
    yaml_path = project_root / "data" / "raw" / "data_sources_registry.yaml"
    
    if not yaml_path.exists():
        print(f"❌ YAML 파일 없음: {yaml_path}")
        sys.exit(1)
    
    # 구축
    try:
        vectorstore = build_index(yaml_path)
        
        print()
        print("=" * 80)
        print("✅ 구축 완료!")
        print("=" * 80)
        print()
        print("사용 예시:")
        print("  from umis_rag.agents.validator import get_validator_rag")
        print("  validator = get_validator_rag()")
        print("  result = validator.search_definite_data('한국 인구는?')")
        print()
        
    except Exception as e:
        print(f"❌ 구축 실패: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

