#!/usr/bin/env python3
"""
Agent RAG Collections 구축
6개 신규 Collection → ChromaDB 인덱싱

Collection 매핑:
  Quantifier:
    - calculation_methodologies (30개)
    - market_benchmarks (100개)
  
  Validator:
    - data_sources_registry (50개)
    - definition_validation_cases (100개)
  
  Observer:
    - market_structure_patterns (30개)
    - value_chain_benchmarks (50개)

사용법:
    python scripts/build_agent_rag_collections.py --agent quantifier
    python scripts/build_agent_rag_collections.py --agent all
"""

import argparse
import json
import yaml
import sys
import os
from pathlib import Path
from typing import Any, Dict, List

from rich.console import Console
from rich.progress import track, Progress
from rich.table import Table

# .env 파일 로드
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv 없으면 수동으로 로드
    env_file = Path(__file__).parent.parent / '.env'
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

# LangChain imports
try:
    from langchain_openai import OpenAIEmbeddings
    from langchain_community.vectorstores import Chroma
    from langchain_core.documents import Document
except ImportError:
    print("❌ LangChain 모듈이 설치되지 않았습니다.")
    print("   설치: pip install langchain langchain-openai langchain-community")
    sys.exit(1)

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.core.config import settings

console = Console()


# ========================================
# Agent별 Collection 정의
# ========================================

AGENT_COLLECTIONS = {
    'quantifier': {
        'collections': [
            {
                'name': 'calculation_methodologies',
                'file': 'data/raw/calculation_methodologies.yaml',
                'key_field': 'method_id',
                'content_fields': ['method_name', 'concept', 'formula', 'example'],
                'description': 'Quantifier - 계산 방법론'
            },
            {
                'name': 'market_benchmarks',
                'file': 'data/raw/market_benchmarks.yaml',
                'key_field': 'benchmark_id',
                'content_fields': ['metric', 'industry', 'benchmarks'],
                'description': 'Quantifier - 시장 벤치마크'
            }
        ]
    },
    'validator': {
        'collections': [
            {
                'name': 'data_sources_registry',
                'file': 'data/raw/data_sources_registry.yaml',
                'key_field': 'source_id',
                'content_fields': ['source_name', 'organization', 'data_types'],
                'description': 'Validator - 데이터 소스'
            },
            {
                'name': 'definition_validation_cases',
                'file': 'data/raw/definition_validation_cases.yaml',
                'key_field': 'metric_id',
                'content_fields': ['metric_name', 'standard_definition', 'formula'],
                'description': 'Validator - 정의 검증 사례'
            }
        ]
    },
    'observer': {
        'collections': [
            {
                'name': 'market_structure_patterns',
                'file': 'data/raw/market_structure_patterns.yaml',
                'key_field': 'pattern_id',
                'content_fields': ['pattern_name', 'characteristics', 'examples'],
                'description': 'Observer - 시장 구조 패턴'
            },
            {
                'name': 'value_chain_benchmarks',
                'file': 'data/raw/value_chain_benchmarks.yaml',
                'key_field': 'benchmark_id',
                'content_fields': ['industry', 'value_chain_stages'],
                'description': 'Observer - 가치사슬 벤치마크'
            }
        ]
    }
}


def load_yaml_data(yaml_file: Path) -> Dict:
    """YAML 파일 로드"""
    with open(yaml_file, encoding='utf-8') as f:
        return yaml.safe_load(f)


def extract_items_from_yaml(data: Dict) -> List[Dict]:
    """YAML에서 항목 추출 (중첩 구조 처리)"""
    
    items = []
    
    # _meta 제외
    for key, value in data.items():
        if key.startswith('_'):
            continue
        
        if isinstance(value, list):
            # 리스트 형태 (대부분의 경우)
            items.extend(value)
        elif isinstance(value, dict):
            # 중첩된 딕셔너리 (market_benchmarks의 카테고리별)
            for subkey, subvalue in value.items():
                if isinstance(subvalue, list):
                    items.extend(subvalue)
    
    return items


def yaml_to_document(
    item: Dict, 
    item_id: str,
    collection_name: str
) -> Document:
    """
    YAML 항목을 LangChain Document로 변환
    
    Args:
        item: YAML 항목 (dict)
        item_id: 항목 ID
        collection_name: Collection 이름
    
    Returns:
        Document 객체
    """
    
    # Content 구성 (재귀적으로 모든 필드 포함)
    def dict_to_text(d: Dict, indent: int = 0) -> str:
        """딕셔너리를 텍스트로 변환"""
        lines = []
        prefix = "  " * indent
        
        for k, v in d.items():
            if isinstance(v, dict):
                lines.append(f"{prefix}{k}:")
                lines.append(dict_to_text(v, indent + 1))
            elif isinstance(v, list):
                lines.append(f"{prefix}{k}:")
                for item in v:
                    if isinstance(item, dict):
                        lines.append(dict_to_text(item, indent + 1))
                    else:
                        lines.append(f"{prefix}  - {item}")
            else:
                lines.append(f"{prefix}{k}: {v}")
        
        return "\n".join(lines)
    
    content = dict_to_text(item)
    
    # Metadata (검색 필터용)
    metadata = {
        'id': item_id,
        'collection': collection_name,
        'type': item.get('category', 'general')
    }
    
    # 추가 메타데이터
    if 'agent' in item:
        metadata['agent'] = item['agent']
    if 'year' in item:
        metadata['year'] = item['year']
    if 'industry' in item:
        metadata['industry'] = item['industry']
    
    return Document(
        page_content=content,
        metadata=metadata
    )


def build_collection(
    collection_config: Dict,
    chroma_path: str = "data/chroma",
    force_rebuild: bool = False
) -> int:
    """
    단일 Collection 구축
    
    Args:
        collection_config: Collection 설정
        chroma_path: ChromaDB 경로
        force_rebuild: 기존 Collection 삭제 후 재구축
    
    Returns:
        인덱싱된 항목 수
    """
    
    collection_name = collection_config['name']
    yaml_file = Path(collection_config['file'])
    
    console.print(f"\n[bold cyan]📦 Collection: {collection_name}[/bold cyan]")
    console.print(f"   파일: {yaml_file}")
    
    # 1. YAML 로드
    if not yaml_file.exists():
        console.print(f"[red]❌ 파일 없음: {yaml_file}[/red]")
        return 0
    
    data = load_yaml_data(yaml_file)
    items = extract_items_from_yaml(data)
    
    console.print(f"   항목 수: {len(items)}개")
    
    if not items:
        console.print(f"[yellow]⚠️ 항목이 없습니다.[/yellow]")
        return 0
    
    # 2. Document 변환
    key_field = collection_config['key_field']
    documents = []
    
    for item in items:
        item_id = item.get(key_field)
        if not item_id:
            console.print(f"[yellow]⚠️ {key_field} 없음, 건너뜀[/yellow]")
            continue
        
        doc = yaml_to_document(item, item_id, collection_name)
        documents.append(doc)
    
    console.print(f"   Documents: {len(documents)}개 생성")
    
    # 3. ChromaDB 인덱싱
    console.print(f"   임베딩 중... ({settings.embedding_model})")
    
    # Embeddings (settings에서 가져오기 - Agent와 일관성)
    embeddings = OpenAIEmbeddings(
        model=settings.embedding_model,
        dimensions=settings.embedding_dimension
    )
    
    # ChromaDB
    import chromadb
    client = chromadb.PersistentClient(path=chroma_path)
    
    # 기존 Collection 삭제 (재구축)
    if force_rebuild:
        try:
            client.delete_collection(collection_name)
            console.print(f"   🗑️  기존 Collection 삭제")
        except Exception:
            pass
    
    # Vector Store 생성
    vectorstore = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=chroma_path,
        collection_metadata={"description": collection_config['description']}
    )
    
    # 배치 인덱싱
    batch_size = 50
    total_indexed = 0
    
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i+batch_size]
        
        vectorstore.add_documents(batch)
        total_indexed += len(batch)
        
        console.print(f"   📦 배치 {i//batch_size + 1}: {len(batch)}개 인덱싱")
    
    console.print(f"[green]✅ {collection_name}: {total_indexed}개 인덱싱 완료[/green]")
    
    return total_indexed


def build_agent_collections(
    agent: str,
    chroma_path: str = "data/chroma",
    force_rebuild: bool = False
) -> Dict[str, int]:
    """
    Agent별 Collection 구축
    
    Args:
        agent: Agent 이름 (quantifier, validator, observer, all)
        chroma_path: ChromaDB 경로
        force_rebuild: 기존 삭제 후 재구축
    
    Returns:
        Collection별 인덱싱 수
    """
    
    console.print(f"\n[bold green]🚀 Agent RAG Collections 구축[/bold green]")
    console.print(f"   Agent: {agent}")
    console.print(f"   ChromaDB: {chroma_path}")
    
    results = {}
    
    if agent == 'all':
        agents_to_build = ['quantifier', 'validator', 'observer']
    else:
        agents_to_build = [agent]
    
    total_collections = 0
    total_items = 0
    
    for agent_name in agents_to_build:
        if agent_name not in AGENT_COLLECTIONS:
            console.print(f"[red]❌ Unknown agent: {agent_name}[/red]")
            continue
        
        console.print(f"\n[bold yellow]{'='*60}[/bold yellow]")
        console.print(f"[bold yellow]Agent: {agent_name.upper()}[/bold yellow]")
        console.print(f"[bold yellow]{'='*60}[/bold yellow]")
        
        agent_config = AGENT_COLLECTIONS[agent_name]
        
        for collection_config in agent_config['collections']:
            count = build_collection(
                collection_config,
                chroma_path=chroma_path,
                force_rebuild=force_rebuild
            )
            
            results[collection_config['name']] = count
            total_collections += 1
            total_items += count
    
    # 결과 요약
    console.print(f"\n[bold green]{'='*60}[/bold green]")
    console.print(f"[bold green]🎉 구축 완료![/bold green]")
    console.print(f"[bold green]{'='*60}[/bold green]")
    
    table = Table(title="인덱싱 결과")
    table.add_column("Collection", style="cyan")
    table.add_column("항목 수", justify="right", style="green")
    
    for collection_name, count in results.items():
        table.add_row(collection_name, str(count))
    
    table.add_row("─" * 30, "─" * 10, style="dim")
    table.add_row("[bold]총계[/bold]", f"[bold]{total_items}개[/bold]")
    
    console.print(table)
    
    console.print(f"\n📊 통계:")
    console.print(f"   Collections: {total_collections}개")
    console.print(f"   총 항목: {total_items}개")
    console.print(f"   ChromaDB: {chroma_path}")
    
    return results


def verify_collections(chroma_path: str = "data/chroma"):
    """구축된 Collection 검증"""
    
    console.print(f"\n[bold cyan]🔍 Collection 검증[/bold cyan]")
    
    import chromadb
    client = chromadb.PersistentClient(path=chroma_path)
    
    # 모든 Collection 목록
    collections = client.list_collections()
    
    console.print(f"\n총 {len(collections)}개 Collection:")
    
    table = Table(title="ChromaDB Collections")
    table.add_column("Collection", style="cyan")
    table.add_column("항목 수", justify="right", style="green")
    table.add_column("설명", style="dim")
    
    for collection in collections:
        count = collection.count()
        metadata = collection.metadata or {}
        description = metadata.get('description', 'N/A') if metadata else 'N/A'
        
        table.add_row(
            collection.name,
            str(count),
            description
        )
    
    console.print(table)


def main():
    """메인 함수"""
    
    parser = argparse.ArgumentParser(
        description='Agent RAG Collections 구축'
    )
    
    parser.add_argument(
        '--agent',
        type=str,
        choices=['quantifier', 'validator', 'observer', 'all'],
        default='all',
        help='Agent 선택 (기본값: all)'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='기존 Collection 삭제 후 재구축'
    )
    
    parser.add_argument(
        '--verify',
        action='store_true',
        help='구축된 Collection 검증만'
    )
    
    parser.add_argument(
        '--chroma-path',
        type=str,
        default='data/chroma',
        help='ChromaDB 경로'
    )
    
    args = parser.parse_args()
    
    # 검증만
    if args.verify:
        verify_collections(args.chroma_path)
        return
    
    # OpenAI API Key 확인
    import os
    if not os.getenv('OPENAI_API_KEY'):
        console.print("[red]❌ OPENAI_API_KEY 환경변수가 설정되지 않았습니다.[/red]")
        console.print("   .env 파일에 OPENAI_API_KEY=your-key 추가")
        sys.exit(1)
    
    # Collection 구축
    results = build_agent_collections(
        agent=args.agent,
        chroma_path=args.chroma_path,
        force_rebuild=args.force
    )
    
    # 검증
    if results:
        verify_collections(args.chroma_path)
    
    console.print(f"\n[bold green]✅ 완료![/bold green]")
    console.print(f"\n다음 단계:")
    console.print(f"  1. Agent RAG 검색 테스트:")
    console.print(f"     python scripts/test_agent_rag.py")
    console.print(f"  2. Quantifier 검색:")
    console.print(f"     python -c \"from umis_rag.agents.quantifier import QuantifierRAG; q=QuantifierRAG(); print(q.search_methodologies('SAM 계산'))\"")


if __name__ == "__main__":
    main()

