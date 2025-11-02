#!/usr/bin/env python3
"""
벡터 인덱스 구축 스크립트

청크 파일(.jsonl)을 읽어서 벡터 DB(Chroma)에 임베딩 후 저장합니다.

개념:
------
1. **Embeddings**: 텍스트를 1536차원 벡터로 변환
   - OpenAI text-embedding-3-small 사용
   - 비용 효율적 (ada-002 대비 5배 저렴)

2. **Chroma DB**: 로컬 벡터 데이터베이스
   - 프로토타입용 (무료, 로컬)
   - 프로덕션에서는 Pinecone 사용 권장

3. **Agent별 Collection**: 
   - Explorer용 컬렉션 따로 관리
   - 향후 Observer, Quantifier, Validator 컬렉션 추가

사용법:
    python scripts/02_build_index.py --agent explorer
    python scripts/02_build_index.py --agent all
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

from rich.console import Console
from rich.progress import track, Progress
from rich.table import Table

# LangChain imports
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.vectorstores.utils import filter_complex_metadata
from langchain_core.documents import Document

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.core.config import settings
from umis_rag.utils.logger import logger

console = Console()


class UMISIndexBuilder:
    """
    UMIS RAG 벡터 인덱스 구축기
    
    역할:
    ------
    1. JSON Lines 청크 파일 로드
    2. OpenAI Embeddings로 벡터화
    3. Chroma DB에 저장
    4. 에이전트별 컬렉션 관리
    
    개념:
    ------
    - **Document**: LangChain의 기본 단위
      {page_content: str, metadata: dict}
    
    - **Embeddings**: 텍스트 → 벡터 변환기
      OpenAI API 사용 (인터넷 필요)
    
    - **VectorStore**: 벡터 저장소 (Chroma)
      유사도 검색 제공
    """
    
    def __init__(self):
        self.data_dir = settings.project_root / "data"
        self.chunks_dir = self.data_dir / "chunks"
        self.chroma_dir = settings.chroma_persist_dir
        
        # OpenAI Embeddings 초기화
        logger.info(f"OpenAI Embeddings 초기화: {settings.embedding_model}")
        self.embeddings = OpenAIEmbeddings(
            model=settings.embedding_model,
            openai_api_key=settings.openai_api_key
        )
        
        logger.info(f"Chroma DB 경로: {self.chroma_dir}")
    
    def load_chunks(self, filename: str) -> List[Dict[str, Any]]:
        """
        JSON Lines 청크 파일 로드
        
        JSON Lines 형식:
        - 한 줄에 하나의 JSON 객체
        - 메모리 효율적 (한 줄씩 읽기 가능)
        """
        filepath = self.chunks_dir / filename
        logger.info(f"청크 파일 로딩: {filepath}")
        
        if not filepath.exists():
            logger.error(f"  ❌ 파일 없음: {filepath}")
            return []
        
        chunks = []
        with open(filepath, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    chunk = json.loads(line)
                    chunks.append(chunk)
                except json.JSONDecodeError as e:
                    logger.warning(f"  ⚠️  라인 {line_num} 파싱 실패: {e}")
        
        logger.info(f"  ✅ {len(chunks)}개 청크 로드 완료")
        return chunks
    
    def chunks_to_documents(self, chunks: List[Dict[str, Any]]) -> List[Document]:
        """
        청크를 LangChain Document로 변환
        
        Document 구조:
        - page_content: 실제 텍스트 내용
        - metadata: 검색 필터링용 메타데이터
        
        개념:
        ------
        LangChain의 모든 도구는 Document 객체를 사용합니다.
        우리의 청크를 이 표준 형식으로 변환해야 합니다.
        """
        logger.info(f"청크 → Document 변환 중...")
        
        documents = []
        for chunk in chunks:
            doc = Document(
                page_content=chunk["content"],
                metadata=chunk["metadata"]
            )
            documents.append(doc)
        
        logger.info(f"  ✅ {len(documents)}개 Document 생성")
        return documents
    
    def build_explorer_index(self) -> None:
        """
        Explorer 에이전트용 벡터 인덱스 구축
        
        프로세스:
        1. Business Model 청크 로드
        2. Disruption 청크 로드
        3. 합치기
        4. 벡터화 (OpenAI API 호출!)
        5. Chroma DB 저장
        
        참고:
        ------
        - API 호출 비용 발생 (54개 청크 × $0.00002 ≈ $0.001)
        - 1-2분 소요 (API 속도 의존)
        """
        console.print("\n[bold blue]📊 Explorer 인덱스 구축 시작[/bold blue]\n")
        
        # 1. 청크 로드
        console.print("[yellow]Step 1/4: 청크 파일 로딩...[/yellow]")
        bm_chunks = self.load_chunks("explorer_business_models.jsonl")
        dp_chunks = self.load_chunks("explorer_disruption_patterns.jsonl")
        all_chunks = bm_chunks + dp_chunks
        
        if not all_chunks:
            logger.error("청크가 없습니다. 먼저 01_convert_yaml.py를 실행하세요.")
            return
        
        console.print(f"  → 총 {len(all_chunks)}개 청크 로드됨\n")
        
        # 2. Document 변환
        console.print("[yellow]Step 2/4: LangChain Document 변환...[/yellow]")
        documents = self.chunks_to_documents(all_chunks)
        console.print(f"  → {len(documents)}개 Document 생성\n")
        
        # 2.5. 메타데이터 필터링 (Chroma DB 호환성)
        console.print("[yellow]Step 2.5/4: 메타데이터 필터링...[/yellow]")
        documents = filter_complex_metadata(documents)
        console.print(f"  → list/dict 타입 JSON 문자열로 변환\n")
        
        # 3. 벡터화 및 저장
        console.print("[yellow]Step 3/4: 벡터 임베딩 생성 (OpenAI API 호출)...[/yellow]")
        console.print("  ⏳ 1-2분 소요 예상... (API 속도 의존)\n")
        
        # Chroma DB 생성 (자동으로 임베딩 + 저장)
        collection_name = "explorer_knowledge_base"
        
        logger.info(f"Chroma Collection 생성: {collection_name}")
        vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            collection_name=collection_name,
            persist_directory=str(self.chroma_dir)
        )
        
        console.print(f"  ✅ 벡터 DB 저장 완료!\n")
        
        # 4. 검증
        console.print("[yellow]Step 4/4: 인덱스 검증...[/yellow]")
        self._validate_index(vectorstore, documents)
        
        # 통계 출력
        self._print_statistics(all_chunks)
        
        console.print("\n[bold green]✅ Explorer 인덱스 구축 완료![/bold green]\n")
        console.print(f"📁 저장 위치: {self.chroma_dir}")
        console.print(f"📊 Collection: {collection_name}")
        console.print(f"📝 Document 수: {len(documents)}")
        console.print("\n다음 단계:")
        console.print("  python scripts/03_test_search.py --agent explorer")
    
    def _validate_index(self, vectorstore: Chroma, documents: List[Document]) -> None:
        """
        인덱스 검증: 간단한 검색 테스트
        
        개념:
        ------
        벡터 DB가 제대로 구축되었는지 확인하기 위해
        테스트 쿼리를 실행해봅니다.
        """
        logger.info("인덱스 검증 중...")
        
        # 테스트 쿼리
        test_queries = [
            "플랫폼 비즈니스 모델",
            "구독 서비스",
            "1등 추월 전략"
        ]
        
        for query in test_queries:
            results = vectorstore.similarity_search(query, k=1)
            if results:
                logger.info(f"  ✅ '{query}' → {results[0].metadata.get('chunk_id', 'unknown')}")
            else:
                logger.warning(f"  ⚠️  '{query}' → 결과 없음")
        
        console.print("  ✅ 인덱스 검증 완료\n")
    
    def _print_statistics(self, chunks: List[Dict[str, Any]]) -> None:
        """통계 정보 출력"""
        # 청크 타입별 집계
        from collections import Counter
        
        chunk_types = Counter(c["metadata"]["chunk_type"] for c in chunks)
        pattern_types = Counter(c["metadata"]["pattern_type"] for c in chunks)
        
        # 테이블 생성
        table = Table(title="📊 Explorer 인덱스 통계")
        table.add_column("구분", style="cyan")
        table.add_column("개수", style="magenta")
        
        table.add_row("총 청크 수", str(len(chunks)))
        table.add_row("Business Model", str(sum(1 for c in chunks if c["metadata"]["pattern_type"] == "business_model")))
        table.add_row("Disruption", str(sum(1 for c in chunks if c["metadata"]["pattern_type"] == "disruption")))
        
        console.print(table)


def main():
    """메인 실행 함수"""
    parser = argparse.ArgumentParser(description="UMIS RAG 벡터 인덱스 구축")
    parser.add_argument(
        "--agent",
        choices=["explorer", "observer", "quantifier", "validator", "all"],
        default="explorer",
        help="구축할 에이전트 인덱스"
    )
    args = parser.parse_args()
    
    console.print("\n[bold blue]🚀 UMIS RAG 벡터 인덱스 구축[/bold blue]")
    console.print(f"Agent: {args.agent}\n")
    
    # 환경 변수 검증
    if not settings.openai_api_key:
        console.print("[bold red]❌ OpenAI API Key가 설정되지 않았습니다![/bold red]")
        console.print("\n.env 파일에 다음을 추가하세요:")
        console.print("  OPENAI_API_KEY=sk-your-api-key-here\n")
        sys.exit(1)
    
    # 인덱스 빌더 초기화
    builder = UMISIndexBuilder()
    
    # 에이전트별 실행
    if args.agent == "explorer":
        builder.build_explorer_index()
    elif args.agent == "all":
        builder.build_explorer_index()
        # TODO: 향후 다른 에이전트 추가
    else:
        console.print(f"[yellow]⚠️  {args.agent} 인덱스는 아직 구현되지 않았습니다.[/yellow]")
        console.print("현재 사용 가능: explorer")


if __name__ == "__main__":
    main()

