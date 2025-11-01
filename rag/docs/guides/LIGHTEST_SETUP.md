#!/usr/bin/env python3
"""
UMIS RAG - Ultra Simple Version

하나의 파일로 모든 것!
- YAML 읽기, 청킹, 인덱싱, 검색

사용:
    python umis_rag_simple.py

그게 끝!
"""

import yaml
from pathlib import Path
from typing import List, Dict
import os

# 환경 변수 로드
from dotenv import load_dotenv
load_dotenv()

# LangChain (최소한만)
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

print("🚀 UMIS RAG Simple")
print("="*70)

# ========================================
# 1. YAML 로드 및 청킹 (자동!)
# ========================================

def load_and_chunk():
    """YAML 파일을 자동으로 청킹"""
    print("\n📖 YAML 로딩 및 청킹...")
    
    chunks = []
    
    # Business Model Patterns
    with open('umis_business_model_patterns_v6.2.yaml', 'r', encoding='utf-8') as f:
        bm_data = yaml.safe_load(f)
    
    for pattern_id in ['platform_business_model', 'subscription_model', 
                       'franchise_model', 'direct_to_consumer_model']:
        if pattern_id in bm_data:
            pattern = bm_data[pattern_id]
            
            # 간단한 청크
            chunks.append(Document(
                page_content=f"{pattern.get('concept', {}).get('name', pattern_id)}\n\n{yaml.dump(pattern, allow_unicode=True)[:500]}",
                metadata={
                    'pattern_id': pattern_id,
                    'type': 'business_model',
                    'agent_view': 'steve'
                }
            ))
    
    print(f"  ✅ {len(chunks)}개 청크 생성")
    return chunks

# ========================================
# 2. 인덱스 구축 (자동!)
# ========================================

def build_index(chunks):
    """벡터 인덱스 구축"""
    print("\n🔍 벡터 인덱스 구축...")
    
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-large",
        openai_api_key=os.getenv('OPENAI_API_KEY')
    )
    
    # 메모리에만 (디스크 안 씀!)
    vectorstore = Chroma.from_documents(
        chunks,
        embeddings,
        collection_name="umis_simple"
    )
    
    print(f"  ✅ {len(chunks)}개 인덱싱 완료")
    return vectorstore

# ========================================
# 3. REPL (대화형!)
# ========================================

def search_repl(vectorstore):
    """대화형 검색"""
    print("\n" + "="*70)
    print("💬 UMIS RAG 검색 (종료: 'q')")
    print("="*70)
    
    while True:
        query = input("\n🔍 검색: ")
        
        if query.lower() in ['q', 'quit', 'exit']:
            break
        
        if not query.strip():
            continue
        
        # 검색!
        results = vectorstore.similarity_search(query, k=3)
        
        print(f"\n📊 결과 ({len(results)}개):")
        print("-"*70)
        
        for i, doc in enumerate(results, 1):
            print(f"\n{i}. {doc.metadata.get('pattern_id', 'N/A')}")
            print(f"   {doc.page_content[:200]}...")
        
        print("-"*70)

# ========================================
# 메인
# ========================================

if __name__ == "__main__":
    # 1. 청킹
    chunks = load_and_chunk()
    
    # 2. 인덱싱
    vectorstore = build_index(chunks)
    
    # 3. 검색 REPL
    search_repl(vectorstore)
    
    print("\n✅ 종료!\n")

