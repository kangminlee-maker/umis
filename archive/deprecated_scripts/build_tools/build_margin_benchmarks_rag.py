#!/usr/bin/env python3
"""
profit_margin_benchmarks RAG Collection 구축

100개 벤치마크 데이터를 ChromaDB Collection으로 인덱싱

Input:
- data/raw/profit_margin_benchmarks.yaml (7,510줄, 100개 벤치마크)

Output:
- ChromaDB Collection: profit_margin_benchmarks
- 100개 document 인덱싱
- Metadata: benchmark_id, industry, sub_category, margins, etc.

Usage:
    python scripts/build_margin_benchmarks_rag.py
    
    # 재구축
    python scripts/build_margin_benchmarks_rag.py --rebuild

v7.9.0 (Gap #2 Week 4)
"""

import yaml
from pathlib import Path
import sys
import argparse

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

from umis_rag.core.config import settings
from umis_rag.utils.logger import logger


def build_margin_benchmarks_collection(rebuild: bool = False):
    """
    profit_margin_benchmarks Collection 구축
    
    Args:
        rebuild: True면 기존 Collection 삭제 후 재구축
    """
    
    logger.info("=" * 60)
    logger.info("Profit Margin Benchmarks RAG Collection 구축 시작")
    logger.info("=" * 60)
    
    # 1. YAML 로드
    yaml_path = project_root / "data" / "raw" / "profit_margin_benchmarks.yaml"
    
    if not yaml_path.exists():
        logger.error(f"❌ 파일 없음: {yaml_path}")
        return False
    
    logger.info(f"📂 YAML 로드: {yaml_path}")
    
    with open(yaml_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    benchmarks = data.get('benchmarks', [])
    logger.info(f"  총 {len(benchmarks)}개 벤치마크 발견")
    
    if not benchmarks:
        logger.error("❌ 벤치마크 데이터 없음")
        return False
    
    # 2. 문서 생성
    logger.info("📝 문서 생성 중...")
    
    documents = []
    metadatas = []
    ids = []
    
    for idx, bm in enumerate(benchmarks):
        benchmark_id = bm.get('benchmark_id')
        
        if not benchmark_id:
            logger.warning(f"  ⚠️  Benchmark {idx+1}: ID 없음, 스킵")
            continue
        
        # 검색 가능한 텍스트 생성
        content_parts = [
            f"Industry: {bm.get('industry', 'N/A')}",
            f"Sub-category: {bm.get('sub_category', 'N/A')}",
            f"Business Model: {bm.get('business_model', 'N/A')}",
            f"Region: {bm.get('region', 'Global')}",
            ""
        ]
        
        # Margins 정보
        margins = bm.get('margins', {})
        if margins:
            content_parts.append("Margins:")
            
            # Operating Margin
            op_margin = margins.get('operating_margin', {})
            if op_margin:
                content_parts.append(f"  Operating Margin:")
                content_parts.append(f"    Median: {op_margin.get('median', 'N/A')}")
                content_parts.append(f"    P25: {op_margin.get('p25', 'N/A')}")
                content_parts.append(f"    P75: {op_margin.get('p75', 'N/A')}")
            
            # Gross Margin
            gross_margin = margins.get('gross_margin', {})
            if gross_margin:
                content_parts.append(f"  Gross Margin:")
                content_parts.append(f"    Median: {gross_margin.get('median', 'N/A')}")
            
            content_parts.append("")
        
        # Company size patterns
        by_company_size = bm.get('by_company_size', {})
        if by_company_size:
            content_parts.append("By Company Size:")
            for size_key, size_data in by_company_size.items():
                content_parts.append(f"  {size_key}: {size_data}")
            content_parts.append("")
        
        # Revenue scale patterns
        by_revenue_scale = bm.get('by_revenue_scale', {})
        if by_revenue_scale:
            content_parts.append("By Revenue Scale:")
            for rev_key, rev_data in by_revenue_scale.items():
                content_parts.append(f"  {rev_key}: {rev_data}")
            content_parts.append("")
        
        # Category patterns
        by_category = bm.get('by_category', {})
        if by_category:
            content_parts.append("By Category:")
            for cat_key, cat_data in by_category.items():
                content_parts.append(f"  {cat_key}: {cat_data}")
            content_parts.append("")
        
        # Notes
        notes = bm.get('notes', '')
        if notes:
            content_parts.append("Notes:")
            content_parts.append(notes)
        
        content = "\n".join(content_parts)
        
        # Metadata 생성
        metadata = {
            'benchmark_id': benchmark_id,
            'industry': bm.get('industry', ''),
            'sub_category': bm.get('sub_category', ''),
            'business_model': bm.get('business_model', ''),
            'region': bm.get('region', 'Global'),
            'reliability': bm.get('reliability', 'medium'),
            'sample_size': bm.get('sample_size', 0),
            'year': bm.get('year', 2024),
            'source': bm.get('source', ''),
            'source_name': bm.get('source_name', ''),
            # Margins를 문자열로 저장 (ChromaDB metadata 제약)
            'margins_json': str(margins),
            'by_company_size_json': str(by_company_size),
            'by_revenue_scale_json': str(by_revenue_scale),
            'by_category_json': str(by_category)
        }
        
        documents.append(content)
        metadatas.append(metadata)
        ids.append(benchmark_id)
    
    logger.info(f"  ✅ {len(documents)}개 문서 생성 완료")
    
    # 3. ChromaDB Collection 생성
    logger.info("🔨 ChromaDB Collection 구축 중...")
    
    try:
        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-large",
            openai_api_key=settings.OPENAI_API_KEY
        )
        
        persist_directory = str(project_root / "data" / "chroma")
        
        # Rebuild 옵션
        if rebuild:
            logger.info("  🔄 기존 Collection 삭제 후 재구축...")
            import shutil
            collection_path = Path(persist_directory) / "profit_margin_benchmarks"
            if collection_path.exists():
                shutil.rmtree(collection_path)
                logger.info("  ✓ 기존 Collection 삭제")
        
        # Collection 생성
        collection = Chroma.from_texts(
            texts=documents,
            metadatas=metadatas,
            ids=ids,
            embedding=embeddings,
            collection_name="profit_margin_benchmarks",
            persist_directory=persist_directory
        )
        
        logger.info(f"  ✅ ChromaDB Collection 생성 완료")
        logger.info(f"  Collection: profit_margin_benchmarks")
        logger.info(f"  Documents: {len(documents)}개")
        logger.info(f"  저장 위치: {persist_directory}")
        
        # 4. 검증: 테스트 검색
        logger.info("\n🧪 테스트 검색 중...")
        
        test_queries = [
            "SaaS B2B Enterprise operating margin",
            "커머스 Beauty D2C margin",
            "플랫폼 Food Delivery operating margin",
            "제조 반도체 Fabless margin",
            "핀테크 P2P 대출 margin"
        ]
        
        for query in test_queries:
            results = collection.similarity_search(query, k=1)
            if results:
                result = results[0]
                logger.info(f"  ✓ '{query}'")
                logger.info(f"    → {result.metadata.get('benchmark_id')}: {result.metadata.get('industry')} - {result.metadata.get('sub_category')}")
            else:
                logger.warning(f"  ✗ '{query}' - 결과 없음")
        
        logger.info("\n" + "=" * 60)
        logger.info("✅ Profit Margin Benchmarks RAG Collection 구축 완료!")
        logger.info("=" * 60)
        
        # 통계
        logger.info("\n📊 통계:")
        logger.info(f"  총 벤치마크: {len(benchmarks)}개")
        logger.info(f"  인덱싱: {len(documents)}개")
        logger.info(f"  데이터 소스: {len(data.get('data_sources', {}))}개")
        logger.info(f"  산업 커버: 7개 (SaaS, 커머스, 플랫폼, 제조, 금융, 헬스케어, 교육)")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Collection 구축 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """메인 함수"""
    
    parser = argparse.ArgumentParser(
        description="Profit Margin Benchmarks RAG Collection 구축"
    )
    parser.add_argument(
        '--rebuild',
        action='store_true',
        help='기존 Collection 삭제 후 재구축'
    )
    
    args = parser.parse_args()
    
    # Collection 구축
    success = build_margin_benchmarks_collection(rebuild=args.rebuild)
    
    if success:
        logger.info("\n✅ 성공!")
        logger.info("\n다음 단계:")
        logger.info("  1. Phase2Enhanced에서 사용:")
        logger.info("     estimator.phase2_enhanced.initialize_benchmark_store(...)")
        logger.info("  2. 정확도 테스트:")
        logger.info("     python scripts/test_phase2_enhanced.py")
        return 0
    else:
        logger.error("\n❌ 실패!")
        return 1


if __name__ == "__main__":
    sys.exit(main())





