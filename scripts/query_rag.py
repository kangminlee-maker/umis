#!/usr/bin/env python3
"""
UMIS RAG Quick Query Script

Cursor에서 UMIS 분석 중 RAG 검색이 필요할 때 간단히 사용하는 스크립트입니다.

사용법:
    # 패턴 검색
    python scripts/query_rag.py pattern "높은 초기 비용, 정기 사용"
    
    # 사례 검색
    python scripts/query_rag.py case "음악 스트리밍" --pattern subscription_model
    
    # 데이터 검증
    python scripts/query_rag.py verify "학습자 수 50만명"
"""

import sys
import argparse
from pathlib import Path

# Project root
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.agents.steve import create_steve_agent
from rich.console import Console
from rich.panel import Panel

console = Console()


def search_patterns(query: str, top_k: int = 2):
    """패턴 검색"""
    console.print(f"\n[yellow]🔍 패턴 검색: {query}[/yellow]\n")
    
    steve = create_steve_agent()
    results = steve.search_patterns(query, top_k=top_k)
    
    console.print(f"[green]✅ {len(results)}개 패턴 발견[/green]\n")
    
    for rank, (doc, score) in enumerate(results, 1):
        pattern_id = doc.metadata.get("pattern_id", "N/A")
        pattern_type = doc.metadata.get("pattern_type", "N/A")
        
        emoji = "🥇" if rank == 1 else "🥈"
        console.print(f"{emoji} [bold]{rank}. {pattern_id}[/bold] ({pattern_type})")
        console.print(f"   유사도: {score:.4f}\n")
        
        # 간단한 내용
        console.print(Panel(
            doc.page_content[:300] + "...",
            title=f"{pattern_id}",
            border_style="cyan"
        ))
        console.print()


def search_cases(query: str, pattern_id: str = None, top_k: int = 3):
    """사례 검색"""
    console.print(f"\n[yellow]🔍 사례 검색: {query}[/yellow]")
    if pattern_id:
        console.print(f"[dim]패턴 필터: {pattern_id}[/dim]\n")
    
    steve = create_steve_agent()
    results = steve.search_cases(query, pattern_id=pattern_id, top_k=top_k)
    
    console.print(f"[green]✅ {len(results)}개 사례 발견[/green]\n")
    
    for rank, (doc, score) in enumerate(results, 1):
        company = doc.metadata.get("company", "N/A")
        market = doc.metadata.get("industry", "N/A")
        
        emoji = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉"
        console.print(f"{emoji} [bold]{rank}. {company}[/bold] ({market})")
        console.print(f"   유사도: {score:.4f}\n")


def verify_data(data_point: str):
    """데이터 검증 (향후 구현)"""
    console.print(f"\n[yellow]🔍 데이터 검증: {data_point}[/yellow]\n")
    console.print("[dim]Rachel retriever는 향후 구현 예정입니다.[/dim]\n")
    console.print("현재는 Steve retriever로 관련 정보 검색:\n")
    
    steve = create_steve_agent()
    results = steve.vectorstore.similarity_search(data_point, k=2)
    
    for i, doc in enumerate(results, 1):
        console.print(f"{i}. {doc.metadata.get('chunk_id', 'N/A')}")
        console.print(f"   {doc.page_content[:150]}...\n")


def main():
    parser = argparse.ArgumentParser(
        description="UMIS RAG Quick Query - Cursor 분석 중 RAG 검색"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="명령어")
    
    # pattern 명령
    pattern_parser = subparsers.add_parser("pattern", help="패턴 검색")
    pattern_parser.add_argument("query", help="검색 쿼리 (트리거 시그널)")
    pattern_parser.add_argument("--top-k", type=int, default=2, help="결과 수")
    
    # case 명령
    case_parser = subparsers.add_parser("case", help="사례 검색")
    case_parser.add_argument("query", help="검색 쿼리 (산업/구조)")
    case_parser.add_argument("--pattern", help="패턴 ID 필터")
    case_parser.add_argument("--top-k", type=int, default=3, help="결과 수")
    
    # verify 명령
    verify_parser = subparsers.add_parser("verify", help="데이터 검증")
    verify_parser.add_argument("data_point", help="검증할 데이터")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == "pattern":
            search_patterns(args.query, args.top_k)
        
        elif args.command == "case":
            search_cases(args.query, args.pattern, args.top_k)
        
        elif args.command == "verify":
            verify_data(args.data_point)
        
        console.print("\n[green]✅ 검색 완료![/green]")
        console.print("\n[dim]💡 위 결과를 Cursor 채팅에 붙여넣으세요.[/dim]\n")
    
    except Exception as e:
        console.print(f"\n[red]❌ 에러: {e}[/red]\n")
        console.print("[dim]RAG 인덱스가 구축되어 있는지 확인하세요:[/dim]")
        console.print("[dim]  python scripts/02_build_index.py --agent steve[/dim]\n")


if __name__ == "__main__":
    main()

