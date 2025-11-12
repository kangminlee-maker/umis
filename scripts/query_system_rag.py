#!/usr/bin/env python3
"""
System RAG: Key-based 정확 검색
Key-first · Vector-fallback 2단계 검색
"""

import time
from typing import Dict, Any, Optional
from pathlib import Path

try:
    import chromadb
except ImportError:
    print("❌ chromadb 모듈이 없습니다.")
    print("   설치: pip install chromadb")
    raise


class SystemRAG:
    """Key-first · Vector-fallback 2단계 검색"""
    
    def __init__(self, chroma_path: str = "data/chroma"):
        """
        Args:
            chroma_path: ChromaDB 경로
        """
        self.client = chromadb.PersistentClient(path=chroma_path)
        
        try:
            self.collection = self.client.get_collection("system_knowledge")
        except Exception as e:
            print(f"⚠️ system_knowledge Collection이 아직 없습니다.")
            print(f"   먼저 scripts/build_system_knowledge.py를 실행하세요.")
            raise e
        
        # KeyDirectory (메모리 상주) - O(1) 정확 매칭
        print("🔧 KeyDirectory 구축 중...")
        self.key_directory = self._build_key_directory()
        print(f"✅ KeyDirectory 구축 완료: {len(self.key_directory)}개 키")
    
    def _build_key_directory(self) -> Dict[str, Dict[str, Any]]:
        """
        모든 도구 키 → ID 매핑 (메모리)
        
        Returns:
            {
                "tool:explorer:pattern_search": {
                    "id": "explorer:pattern_search",
                    "agent": "explorer",
                    "context_size": 200
                },
                ...
            }
        """
        # Collection의 모든 메타데이터 로드
        all_data = self.collection.get()
        
        key_dir = {}
        for idx, metadata in enumerate(all_data['metadatas']):
            tool_key = metadata.get('tool_key')
            if tool_key:
                key_dir[tool_key] = {
                    'id': all_data['ids'][idx],
                    'agent': metadata.get('agent'),
                    'category': metadata.get('category'),
                    'context_size': metadata.get('context_size', 200),
                    'priority': metadata.get('priority', 'normal')
                }
        
        return key_dir
    
    def search_tool_by_key(
        self, 
        tool_key: str,
        verbose: bool = True
    ) -> Dict[str, Any]:
        """
        Key로 도구 검색 (2단계)
        
        Args:
            tool_key: "tool:agent:task" 형식 키
            verbose: 로그 출력 여부
        
        Returns:
            {
                'tool_id': str,
                'content': str,
                'metadata': dict,
                'match_type': 'exact_key' | 'vector_fallback',
                'latency_ms': float,
                'similarity': float (vector_fallback만)
            }
        """
        start = time.time()
        
        # Step 1: KeyDirectory 정확 매칭 (O(1), 무료, 확실)
        if tool_key in self.key_directory:
            tool_info = self.key_directory[tool_key]
            
            # ID로 직접 조회 (벡터 검색 불필요!)
            result = self.collection.get(ids=[tool_info['id']])
            
            latency_ms = (time.time() - start) * 1000
            
            if verbose:
                print(f"✅ Key 정확 매칭: {tool_key}")
                print(f"   ID: {tool_info['id']}")
                print(f"   Agent: {tool_info['agent']}")
                print(f"   지연시간: {latency_ms:.2f}ms")
            
            return {
                'tool_id': tool_info['id'],
                'content': result['documents'][0],
                'metadata': result['metadatas'][0],
                'match_type': 'exact_key',  # ✅ 정확 매칭
                'latency_ms': latency_ms
            }
        
        # Step 2: Vector Fallback (오타/동의어 허용)
        if verbose:
            print(f"⚠️ Key '{tool_key}' 없음 → Vector 폴백 검색")
        
        results = self.collection.query(
            query_texts=[tool_key],
            n_results=1
        )
        
        latency_ms = (time.time() - start) * 1000
        
        if not results['documents'] or not results['documents'][0]:
            raise ValueError(f"도구 없음: {tool_key}")
        
        similarity = 1.0 - results['distances'][0][0]  # ChromaDB는 distance 반환
        
        if verbose:
            print(f"🔍 Vector 폴백 매칭")
            print(f"   ID: {results['ids'][0][0]}")
            print(f"   유사도: {similarity:.3f}")
            print(f"   지연시간: {latency_ms:.2f}ms")
        
        return {
            'tool_id': results['ids'][0][0],
            'content': results['documents'][0][0],
            'metadata': results['metadatas'][0][0],
            'match_type': 'vector_fallback',  # ✅ 유사도 검색
            'similarity': similarity,
            'latency_ms': latency_ms
        }
    
    def get_available_keys(self) -> list[str]:
        """사용 가능한 모든 키 반환"""
        return sorted(self.key_directory.keys())
    
    def get_keys_by_agent(self, agent: str) -> list[str]:
        """특정 Agent의 키 반환"""
        return [
            key for key, info in self.key_directory.items()
            if info['agent'] == agent
        ]
    
    def stats(self) -> Dict[str, Any]:
        """통계 반환"""
        agents = {}
        categories = {}
        priorities = {}
        
        for key, info in self.key_directory.items():
            # Agent별
            agent = info['agent']
            agents[agent] = agents.get(agent, 0) + 1
            
            # Category별
            category = info['category']
            categories[category] = categories.get(category, 0) + 1
            
            # Priority별
            priority = info['priority']
            priorities[priority] = priorities.get(priority, 0) + 1
        
        return {
            'total_tools': len(self.key_directory),
            'agents': agents,
            'categories': categories,
            'priorities': priorities
        }


def main():
    """CLI 인터페이스"""
    import sys
    
    if len(sys.argv) < 2:
        print("사용법: python query_system_rag.py <tool_key>")
        print("\n예시:")
        print("  python query_system_rag.py tool:explorer:pattern_search")
        print("  python query_system_rag.py --list")
        print("  python query_system_rag.py --stats")
        sys.exit(1)
    
    system_rag = SystemRAG()
    
    if sys.argv[1] == '--list':
        print("\n📋 사용 가능한 도구 키:")
        for key in system_rag.get_available_keys():
            print(f"  - {key}")
        return
    
    if sys.argv[1] == '--stats':
        stats = system_rag.stats()
        print("\n📊 System RAG 통계:")
        print(f"  총 도구 수: {stats['total_tools']}개")
        print(f"\n  Agent별:")
        for agent, count in stats['agents'].items():
            print(f"    - {agent}: {count}개")
        print(f"\n  Category별:")
        for category, count in stats['categories'].items():
            print(f"    - {category}: {count}개")
        return
    
    tool_key = sys.argv[1]
    result = system_rag.search_tool_by_key(tool_key)
    
    print("\n📄 검색 결과:")
    print(f"  Match Type: {result['match_type']}")
    print(f"  Tool ID: {result['tool_id']}")
    print(f"  Latency: {result['latency_ms']:.2f}ms")
    if 'similarity' in result:
        print(f"  Similarity: {result['similarity']:.3f}")
    
    # 전체 content 출력 (제한 없음)
    content_lines = result['content'].split('\n')
    print(f"\n📝 Content ({len(content_lines)} 줄, {len(result['content'])} 문자):")
    print("=" * 80)
    print(result['content'])
    print("=" * 80)


if __name__ == "__main__":
    main()

