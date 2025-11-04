#!/usr/bin/env python3
"""
System RAG Index 구축
Tool Registry → ChromaDB (system_knowledge Collection)
"""

import yaml
from pathlib import Path
from typing import List, Dict, Any

# Lazy import (샘플 생성 시 chromadb 불필요)
chromadb = None


def build_system_knowledge_index(
    registry_path: str = "config/tool_registry.yaml",
    chroma_path: str = "data/chroma"
) -> None:
    """
    Tool Registry → System RAG
    
    Args:
        registry_path: tool_registry.yaml 경로
        chroma_path: ChromaDB 저장 경로
    """
    
    # chromadb import
    global chromadb
    if chromadb is None:
        import chromadb as _chromadb
        chromadb = _chromadb
    
    print("🚀 System RAG Index 구축 시작")
    print(f"   Registry: {registry_path}")
    print(f"   ChromaDB: {chroma_path}")
    
    # 1. Tool Registry 로드
    registry_file = Path(registry_path)
    
    if not registry_file.exists():
        print(f"❌ {registry_path} 파일이 없습니다.")
        print(f"   먼저 Tool Registry를 작성하세요.")
        return
    
    with open(registry_file) as f:
        registry = yaml.safe_load(f)
    
    print(f"✅ Registry 로드: {len(registry.get('tools', []))}개 도구")
    
    # 2. 청크 생성 (tool_key를 메타데이터에 포함!)
    chunks = []
    for tool in registry.get('tools', []):
        chunk = {
            'id': tool['tool_id'],
            'key': tool['tool_key'],  # 정확 매칭 키
            'content': tool['content'],
            'metadata': {
                **tool.get('metadata', {}),
                'tool_key': tool['tool_key']  # ✅ 메타데이터에 추가!
            }
        }
        chunks.append(chunk)
    
    print(f"✅ 청크 생성: {len(chunks)}개")
    
    # 3. ChromaDB 저장
    client = chromadb.PersistentClient(path=chroma_path)
    
    # 기존 Collection 삭제 (재구축)
    try:
        client.delete_collection("system_knowledge")
        print("🗑️  기존 system_knowledge Collection 삭제")
    except Exception:
        pass
    
    collection = client.get_or_create_collection(
        "system_knowledge",
        metadata={"description": "UMIS 도구 검색 (Key-based)"}
    )
    
    # 배치 추가
    batch_size = 100
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i+batch_size]
        
        collection.add(
            ids=[c['id'] for c in batch],
            documents=[c['content'] for c in batch],
            metadatas=[c['metadata'] for c in batch]
        )
        
        print(f"📦 배치 {i//batch_size + 1}: {len(batch)}개 추가")
    
    print(f"\n✅ {len(chunks)}개 도구 인덱싱 완료!")
    
    # 4. 검증
    print("\n🔍 검증 중...")
    
    all_data = collection.get()
    print(f"   총 문서: {len(all_data['ids'])}개")
    
    # tool_key 메타데이터 확인
    keys_with_tool_key = sum(
        1 for meta in all_data['metadatas'] 
        if meta.get('tool_key')
    )
    print(f"   tool_key 메타데이터: {keys_with_tool_key}개")
    
    if keys_with_tool_key == len(chunks):
        print("   ✅ 모든 도구에 tool_key 메타데이터 포함")
    else:
        print(f"   ⚠️ tool_key 누락: {len(chunks) - keys_with_tool_key}개")
    
    # Agent별 통계
    agents = {}
    for meta in all_data['metadatas']:
        agent = meta.get('agent', 'unknown')
        agents[agent] = agents.get(agent, 0) + 1
    
    print(f"\n📊 Agent별 도구 수:")
    for agent, count in sorted(agents.items()):
        print(f"   - {agent}: {count}개")
    
    print("\n🎉 System RAG Index 구축 완료!")
    print("\n다음 단계:")
    print("  1. python scripts/query_system_rag.py --list")
    print("  2. python scripts/query_system_rag.py tool:explorer:pattern_search")


def create_sample_registry():
    """샘플 Tool Registry 생성 (개발용)"""
    
    sample_registry = {
        'version': '7.1.0',
        'created': '2025-11-03',
        'tools': [
            {
                'tool_id': 'explorer:pattern_search',
                'tool_key': 'tool:explorer:pattern_search',
                'metadata': {
                    'agent': 'explorer',
                    'category': 'rag_search',
                    'complexity': 'low',
                    'context_size': 200,
                    'priority': 'high'
                },
                'when_to_use': {
                    'keywords': ['패턴', '모델', '사례'],
                    'conditions': [
                        "agent == 'explorer'",
                        "task_type in ['pattern_discovery', 'model_matching']"
                    ]
                },
                'content': """
# Explorer: RAG 패턴 검색

## 목적
31개 비즈니스 모델 + 23개 Disruption 패턴에서 관련 패턴 자동 검색

## 사용 예시
```python
from umis_rag.agents.explorer import ExplorerRAG

explorer = ExplorerRAG()
patterns = explorer.search_patterns("구독 모델")
```

(샘플 - 실제로는 더 상세한 내용)
"""
            }
        ]
    }
    
    # 저장
    output_path = Path("config/tool_registry_sample.yaml")
    with open(output_path, 'w', encoding='utf-8') as f:
        yaml.dump(sample_registry, f, allow_unicode=True, sort_keys=False)
    
    print(f"✅ 샘플 Registry 생성: {output_path}")


def main():
    """CLI 인터페이스"""
    import sys
    
    if '--sample' in sys.argv:
        create_sample_registry()
        return
    
    # Registry 경로 확인
    registry_path = "config/tool_registry.yaml"
    if not Path(registry_path).exists():
        print(f"⚠️ {registry_path} 파일이 없습니다.")
        print("\n다음 중 하나를 선택하세요:")
        print("  1. Tool Registry 직접 작성")
        print("  2. python scripts/build_system_knowledge.py --sample (샘플 생성)")
        return
    
    build_system_knowledge_index()


if __name__ == "__main__":
    main()

