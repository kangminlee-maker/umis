#!/usr/bin/env python3
"""
RAG 검색 테스트 스크립트

구축된 벡터 인덱스에서 실제 검색을 테스트합니다.

개념:
------
1. **Semantic Search (의미 기반 검색)**
   - 키워드 일치가 아닌 의미 유사도로 검색
   - "플랫폼" 검색 → "배달의민족", "우버" 찾음

2. **Metadata Filtering (메타데이터 필터링)**
   - agent="explorer", pattern_type="disruption"
   - 특정 조건의 청크만 검색

3. **Top-K Retrieval**
   - 가장 유사한 K개 문서 반환
   - UMIS 기본값: K=5

사용법:
    # 기본 검색
    python scripts/03_test_search.py --agent explorer --query "플랫폼 비즈니스 모델"
    
    # 필터링 검색
    python scripts/03_test_search.py --agent explorer --query "추월 전략" --filter disruption
    
    # Top-K 조정
    python scripts/03_test_search.py --agent explorer --query "구독" --top-k 3
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Any

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown

# LangChain imports
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.core.config import settings
from umis_rag.utils.logger import logger

console = Console()


class UMISSearchTester:
    """
    UMIS RAG 검색 테스터
    
    기능:
    ------
    1. 벡터 인덱스 로드
    2. 쿼리 검색
    3. 결과 분석 및 시각화
    
    검색 방식:
    ------
    - Similarity Search: 의미적 유사도 기반
    - MMR (Maximal Marginal Relevance): 다양성 고려
    - Similarity with Score: 유사도 점수 포함
    """
    
    def __init__(self, agent: str = "explorer"):
        self.agent = agent
        self.chroma_dir = settings.chroma_persist_dir
        
        # Embeddings 초기화
        logger.info(f"Embeddings 초기화: {settings.embedding_model}")
        self.embeddings = OpenAIEmbeddings(
            model=settings.embedding_model,
            openai_api_key=settings.openai_api_key
        )
        
        # 벡터 스토어 로드
        collection_name = f"{agent}_knowledge_base"
        logger.info(f"벡터 스토어 로드: {collection_name}")
        
        try:
            self.vectorstore = Chroma(
                collection_name=collection_name,
                embedding_function=self.embeddings,
                persist_directory=str(self.chroma_dir)
            )
            
            # 인덱스 정보 확인
            count = self.vectorstore._collection.count()
            logger.info(f"  ✅ {count}개 Document 로드됨")
            
        except Exception as e:
            logger.error(f"  ❌ 벡터 스토어 로드 실패: {e}")
            raise
    
    def search(
        self, 
        query: str, 
        top_k: int = 5,
        filter_dict: Dict[str, Any] | None = None
    ) -> List[tuple]:
        """
        의미 기반 검색 (유사도 점수 포함)
        
        개념:
        ------
        1. Query를 벡터로 변환 (OpenAI API)
        2. 인덱스의 모든 벡터와 유사도 계산
        3. Top-K개 반환
        
        반환값:
        ------
        List of (Document, similarity_score)
        """
        logger.info(f"검색 쿼리: {query}")
        logger.info(f"  Top-K: {top_k}, Filter: {filter_dict}")
        
        # 유사도 점수 포함 검색
        results = self.vectorstore.similarity_search_with_score(
            query,
            k=top_k,
            filter=filter_dict
        )
        
        logger.info(f"  ✅ {len(results)}개 결과 반환")
        return results
    
    def display_results(
        self, 
        query: str,
        results: List[tuple],
        show_content: bool = True
    ) -> None:
        """
        검색 결과를 예쁘게 출력
        
        개념:
        ------
        Rich 라이브러리로 터미널에 컬러풀한 출력
        - Table: 결과 요약
        - Panel: 개별 청크 내용
        """
        console.print(f"\n[bold blue]🔍 검색 쿼리: {query}[/bold blue]\n")
        
        if not results:
            console.print("[yellow]⚠️  검색 결과가 없습니다.[/yellow]")
            return
        
        # 결과 테이블
        table = Table(title=f"📊 검색 결과 (Top {len(results)})")
        table.add_column("순위", style="cyan", width=6)
        table.add_column("유사도", style="magenta", width=10)
        table.add_column("청크 ID", style="green")
        table.add_column("타입", style="yellow")
        table.add_column("패턴", style="blue")
        
        for rank, (doc, score) in enumerate(results, 1):
            emoji = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else "  "
            
            table.add_row(
                f"{emoji} {rank}",
                f"{score:.4f}",
                doc.metadata.get("chunk_id", "N/A")[:40],
                doc.metadata.get("chunk_type", "N/A"),
                doc.metadata.get("pattern_id", "N/A")[:30]
            )
        
        console.print(table)
        console.print()
        
        # 1등 문서 상세 출력
        if show_content and results:
            doc, score = results[0]
            
            panel_content = f"""
**청크 ID**: {doc.metadata.get('chunk_id', 'N/A')}
**유사도**: {score:.4f}
**패턴**: {doc.metadata.get('pattern_id', 'N/A')}
**타입**: {doc.metadata.get('chunk_type', 'N/A')}
**토큰**: {doc.metadata.get('token_count', 'N/A')}

**내용**:
```
{doc.page_content[:500]}...
```
"""
            
            console.print(Panel(
                panel_content,
                title="🥇 1등 문서 상세",
                border_style="green"
            ))
    
    def test_scenarios(self) -> None:
        """
        다양한 검색 시나리오 테스트
        
        UMIS 실제 사용 케이스:
        1. 패턴 매칭: Observer 관찰 → Explorer 패턴 찾기
        2. 사례 검색: 유사 산업 성공 사례
        3. 검증 방법: 특정 패턴의 검증 프레임워크
        """
        console.print("\n[bold blue]🧪 UMIS 검색 시나리오 테스트[/bold blue]\n")
        
        scenarios = [
            {
                "name": "시나리오 1: 트리거 시그널 → 패턴 매칭",
                "query": "파편화된 공급자와 수요자, 높은 중개 비용",
                "filter": {"chunk_type": "pattern_overview"},
                "description": "Observer가 발견한 시장 구조 → Explorer가 어떤 패턴을 찾을까?"
            },
            {
                "name": "시나리오 2: 산업 유사성 → 사례 검색",
                "query": "음악 구독 스트리밍 서비스",
                "filter": {"chunk_type": "success_case"},
                "description": "음악 산업 → 유사한 성공 사례?"
            },
            {
                "name": "시나리오 3: Disruption 전략 검색",
                "query": "1등 기업이 못 따라올 전략",
                "filter": {"pattern_type": "disruption"},
                "description": "Counter-Positioning 패턴 찾기"
            },
            {
                "name": "시나리오 4: 검증 프레임워크",
                "query": "Quantifier에게 물어봐야 할 정량 지표",
                "filter": {"chunk_type": "validation_framework"},
                "description": "특정 패턴의 검증 방법 찾기"
            },
        ]
        
        for scenario in scenarios:
            console.print(f"[bold cyan]{scenario['name']}[/bold cyan]")
            console.print(f"[dim]{scenario['description']}[/dim]")
            
            # 검색 실행
            results = self.search(
                query=scenario["query"],
                top_k=3,
                filter_dict=scenario.get("filter")
            )
            
            # 결과 출력 (내용은 생략)
            self.display_results(
                scenario["query"],
                results,
                show_content=False
            )
            
            console.print()


def main():
    """메인 실행 함수"""
    parser = argparse.ArgumentParser(description="UMIS RAG 검색 테스트")
    parser.add_argument(
        "--agent",
        choices=["explorer", "observer", "quantifier", "validator"],
        default="explorer",
        help="검색할 에이전트 인덱스"
    )
    parser.add_argument(
        "--query",
        type=str,
        help="검색 쿼리 (미지정 시 테스트 시나리오 실행)"
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=5,
        help="반환할 결과 수 (기본값: 5)"
    )
    parser.add_argument(
        "--filter",
        choices=["business_model", "disruption", "pattern", "case"],
        help="필터링 타입"
    )
    parser.add_argument(
        "--no-content",
        action="store_true",
        help="1등 문서 내용 생략"
    )
    
    args = parser.parse_args()
    
    console.print("\n[bold blue]🔍 UMIS RAG 검색 테스트[/bold blue]")
    console.print(f"Agent: {args.agent}")
    console.print(f"Model: {settings.embedding_model} (차원: {settings.embedding_dimension})\n")
    
    try:
        # 테스터 초기화
        tester = UMISSearchTester(agent=args.agent)
        
        if args.query:
            # 단일 쿼리 실행
            filter_dict = None
            if args.filter:
                if args.filter in ["business_model", "disruption"]:
                    filter_dict = {"pattern_type": args.filter}
                elif args.filter == "pattern":
                    filter_dict = {"chunk_type": "pattern_overview"}
                elif args.filter == "case":
                    filter_dict = {"chunk_type": "success_case"}
            
            results = tester.search(
                query=args.query,
                top_k=args.top_k,
                filter_dict=filter_dict
            )
            
            tester.display_results(
                args.query,
                results,
                show_content=not args.no_content
            )
        else:
            # 테스트 시나리오 실행
            tester.test_scenarios()
        
        console.print("\n[bold green]✅ 테스트 완료![/bold green]\n")
        
    except Exception as e:
        console.print(f"\n[bold red]❌ 에러 발생: {e}[/bold red]\n")
        logger.exception("검색 테스트 실패")
        sys.exit(1)


if __name__ == "__main__":
    main()

