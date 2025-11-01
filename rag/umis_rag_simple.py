#!/usr/bin/env python3
"""
UMIS RAG - Ultra Simple Single File Version

가장 가볍고 간단한 UMIS RAG!

사용법:
    # 1회 실행 (인덱스 구축)
    python umis_rag_simple.py --build
    
    # 대화형 검색
    python umis_rag_simple.py
    
    # YAML 수정 후 재실행 → 자동 반영!
"""

import os
import sys
import yaml
import argparse
from pathlib import Path
from typing import List

# 환경 변수
from dotenv import load_dotenv
load_dotenv()

# LangChain (최소한)
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document


class SimpleUMISRAG:
    """
    단일 파일 UMIS RAG
    
    특징:
    -----
    - 설정 최소
    - 파일 하나
    - 즉시 사용
    - YAML 수정 → 재실행 → 반영!
    """
    
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-large",
            openai_api_key=os.getenv('OPENAI_API_KEY')
        )
        
        # 메모리 인덱스 (빠름!)
        self.vectorstore = None
    
    def load_yaml_and_chunk(self) -> List[Document]:
        """YAML 로드 및 간단한 청킹"""
        chunks = []
        
        # Business Model Patterns
        try:
            with open('umis_business_model_patterns_v6.2.yaml', 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            for key in data.keys():
                if key.startswith('_'):
                    continue
                
                pattern = data[key]
                if isinstance(pattern, dict) and 'concept' in pattern:
                    content = yaml.dump(pattern, allow_unicode=True)
                    
                    chunks.append(Document(
                        page_content=content[:1000],  # 간단히
                        metadata={
                            'pattern_id': key,
                            'type': 'business_model'
                        }
                    ))
        except Exception as e:
            print(f"  ⚠️  Business Model 로드 실패: {e}")
        
        # Disruption Patterns
        try:
            with open('umis_disruption_patterns_v6.2.yaml', 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            for key in data.keys():
                if key.startswith('_'):
                    continue
                
                pattern = data[key]
                if isinstance(pattern, dict) and 'concept' in pattern:
                    content = yaml.dump(pattern, allow_unicode=True)
                    
                    chunks.append(Document(
                        page_content=content[:1000],
                        metadata={
                            'pattern_id': key,
                            'type': 'disruption'
                        }
                    ))
        except Exception as e:
            print(f"  ⚠️  Disruption 로드 실패: {e}")
        
        return chunks
    
    def build(self):
        """인덱스 구축"""
        print("📖 YAML 로딩 및 청킹...")
        chunks = self.load_yaml_and_chunk()
        print(f"  ✅ {len(chunks)}개 청크 생성")
        
        print("\n🔍 벡터 인덱스 구축...")
        self.vectorstore = Chroma.from_documents(
            chunks,
            self.embeddings,
            collection_name="umis_simple"
        )
        print(f"  ✅ 완료!")
        
        return self.vectorstore
    
    def search(self, query: str, k: int = 3):
        """검색"""
        if not self.vectorstore:
            print("❌ 인덱스 없음. --build로 먼저 구축하세요.")
            return []
        
        results = self.vectorstore.similarity_search(query, k=k)
        return results
    
    def repl(self):
        """대화형 검색"""
        print("\n" + "="*70)
        print("💬 UMIS RAG 검색 REPL")
        print("="*70)
        print("\n명령어:")
        print("  검색어 입력 → 검색")
        print("  'reload' → YAML 재로드")
        print("  'q' → 종료")
        print()
        
        while True:
            try:
                query = input("🔍 ").strip()
                
                if not query:
                    continue
                
                if query.lower() in ['q', 'quit', 'exit']:
                    break
                
                if query.lower() == 'reload':
                    print("\n🔄 YAML 재로드 중...")
                    self.build()
                    print("  ✅ 완료! 다시 검색하세요.\n")
                    continue
                
                # 검색
                results = self.search(query)
                
                if not results:
                    print("  ⚠️  결과 없음\n")
                    continue
                
                print(f"\n📊 {len(results)}개 결과:")
                print("-"*70)
                
                for i, doc in enumerate(results, 1):
                    print(f"\n{i}. {doc.metadata.get('pattern_id', 'N/A')}")
                    print(f"   타입: {doc.metadata.get('type', 'N/A')}")
                    print(f"   {doc.page_content[:150]}...")
                
                print("-"*70 + "\n")
            
            except KeyboardInterrupt:
                print("\n\n종료...\n")
                break
            except Exception as e:
                print(f"\n❌ 에러: {e}\n")


def main():
    parser = argparse.ArgumentParser(description="UMIS RAG Simple")
    parser.add_argument('--build', action='store_true', help='인덱스 구축')
    parser.add_argument('--query', type=str, help='검색 쿼리')
    
    args = parser.parse_args()
    
    rag = SimpleUMISRAG()
    
    if args.build:
        rag.build()
        print("\n✅ 인덱스 구축 완료!")
        print("이제: python umis_rag_simple.py\n")
    
    elif args.query:
        rag.build()  # 빠르게 구축
        results = rag.search(args.query)
        
        for i, doc in enumerate(results, 1):
            print(f"{i}. {doc.metadata['pattern_id']}")
    
    else:
        # REPL 모드
        if not rag.vectorstore:
            print("📦 초기 인덱스 구축 중...")
            rag.build()
        
        rag.repl()


if __name__ == "__main__":
    main()

