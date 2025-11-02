#!/usr/bin/env python3
"""
UMIS Development Watcher

YAML 파일 변경 감지 및 자동 RAG 업데이트

개념:
-----
인라인 어셈블러처럼:
  - YAML 수정 (VS Code/Cursor)
  - 저장 (Ctrl+S)
  - 2초 후 자동 반영!
  - 즉시 테스트 가능

사용:
-----
python scripts/dev_watcher.py

또는:
make dev
"""

import sys
import time
from pathlib import Path
from typing import Dict

# Watchdog for file monitoring
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except ImportError:
    print("❌ watchdog 패키지 필요: pip install watchdog")
    sys.exit(1)

from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.panel import Panel

# Project root
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.core.config import settings
from umis_rag.utils.logger import logger

console = Console()


class UMISYAMLWatcher(FileSystemEventHandler):
    """
    YAML 변경 감지 → 자동 RAG 업데이트
    
    피드백 루프:
    -----------
    1. YAML 수정 (0초)
    2. 변경 감지 (즉시)
    3. 청크 재생성 (0.5초)
    4. 벡터 업데이트 (1-2초)
    5. 완료! (총 2초)
    
    → 인라인 어셈블러 수준! ⚡
    """
    
    def __init__(self):
        self.last_modified: Dict[Path, float] = {}
        self.update_count = 0
        self.last_update_time = None
        
        # Import heavy modules only once
        logger.info("Watcher 초기화 중...")
        self._setup_processors()
    
    def _setup_processors(self):
        """프로세서 초기화 (한 번만)"""
        # Import 경로 수정 (스크립트를 모듈처럼)
        import sys
        scripts_dir = Path(__file__).parent
        if str(scripts_dir) not in sys.path:
            sys.path.insert(0, str(scripts_dir))
        
        # 동적 import
        import importlib.util
        
        # 01_convert_yaml.py
        spec1 = importlib.util.spec_from_file_location(
            "convert_yaml",
            scripts_dir / "01_convert_yaml.py"
        )
        convert_module = importlib.util.module_from_spec(spec1)
        spec1.loader.exec_module(convert_module)
        
        # 02_build_index.py  
        spec2 = importlib.util.spec_from_file_location(
            "build_index",
            scripts_dir / "02_build_index.py"
        )
        index_module = importlib.util.module_from_spec(spec2)
        spec2.loader.exec_module(index_module)
        
        self.converter = convert_module.UMISYAMLConverter(settings.data_dir)
        self.indexer = index_module.UMISIndexBuilder()
        
        logger.info("  ✅ 프로세서 준비 완료")
    
    def on_modified(self, event):
        """파일 변경 이벤트 핸들러"""
        if event.is_directory:
            return
        
        filepath = Path(event.src_path)
        
        # YAML 파일만
        if filepath.suffix not in ['.yaml', '.yml']:
            return
        
        # UMIS 파일만
        if not any(x in filepath.name for x in ['business_model', 'disruption', 'ai_guide']):
            return
        
        # 중복 이벤트 필터 (1초 내)
        now = time.time()
        if filepath in self.last_modified:
            if now - self.last_modified[filepath] < 1.0:
                return
        
        self.last_modified[filepath] = now
        
        # 업데이트 실행
        self._incremental_update(filepath)
    
    def _incremental_update(self, filepath: Path):
        """
        증분 업데이트 (빠름!)
        
        전체 재구축 (느림):
          - 모든 YAML 처리
          - 모든 청크 생성
          - 전체 인덱스 재구축
          - 5-10분
        
        증분 업데이트 (빠름):
          - 변경된 파일만
          - 해당 청크만
          - Upsert만
          - 1-2초! ⚡
        """
        
        console.print(f"\n[yellow]🔄 변경 감지: {filepath.name}[/yellow]")
        console.print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        start = time.time()
        
        try:
            # 1. 청크 재생성
            console.print("  [cyan]1/3[/cyan] 청크 재생성 중...")
            
            if "business_model" in filepath.name:
                new_chunks = self.converter.convert_business_model_patterns_for_explorer()
                source_file = "umis_business_model_patterns_v6.2.yaml"
            elif "disruption" in filepath.name:
                new_chunks = self.converter.convert_disruption_patterns_for_explorer()
                source_file = "umis_disruption_patterns_v6.2.yaml"
            else:
                console.print("  [yellow]⚠️  처리 안 함[/yellow]")
                return
            
            console.print(f"     → {len(new_chunks)}개 청크 생성")
            
            # 2. Document 변환
            console.print("  [cyan]2/3[/cyan] 벡터 임베딩 중...")
            
            from langchain_core.documents import Document
            from langchain_community.vectorstores.utils import filter_complex_metadata
            
            documents = [
                Document(
                    page_content=c["content"],
                    metadata=c["metadata"]
                )
                for c in new_chunks
            ]
            
            filtered_docs = filter_complex_metadata(documents)
            
            # 3. Upsert (기존 삭제 + 새로 추가)
            console.print("  [cyan]3/3[/cyan] 인덱스 업데이트 중...")
            
            # 기존 청크 삭제
            try:
                self.indexer.vectorstore._collection.delete(
                    where={"source_file": source_file}
                )
            except:
                pass  # 없으면 무시
            
            # 새 청크 추가
            self.indexer.vectorstore.add_documents(filtered_docs)
            
            # 완료
            elapsed = time.time() - start
            self.update_count += 1
            self.last_update_time = time.strftime("%H:%M:%S")
            
            console.print(f"\n  [green]✅ 완료! ({elapsed:.1f}초)[/green]")
            console.print(f"  [dim]💾 {len(new_chunks)}개 청크 업데이트")
            console.print(f"  [dim]🔍 다음 검색부터 반영됨[/dim]\n")
            
        except Exception as e:
            console.print(f"\n  [red]❌ 에러: {e}[/red]\n")
            logger.exception("증분 업데이트 실패")
    
    def get_stats(self) -> Table:
        """통계 테이블 생성"""
        table = Table(title="📊 Watcher 통계")
        table.add_column("항목", style="cyan")
        table.add_column("값", style="green")
        
        table.add_row("업데이트 횟수", str(self.update_count))
        table.add_row("마지막 업데이트", self.last_update_time or "-")
        table.add_row("감시 중", "✅ 활성")
        
        return table


def main():
    """메인 실행"""
    console.print("\n[bold blue]🚀 UMIS Development Watcher[/bold blue]")
    console.print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
    
    watch_dir = settings.data_dir / 'raw'
    
    console.print(Panel(
        f"""[green]✅ 준비 완료![/green]

📁 감시 디렉토리: {watch_dir}
💡 YAML 파일 수정 시 자동으로 RAG 업데이트됩니다.

[dim]피드백 루프: YAML 수정 → 2초 → 반영! ⚡[/dim]

⚠️  종료: Ctrl+C""",
        border_style="blue"
    ))
    
    # Watcher 설정
    event_handler = UMISYAMLWatcher()
    observer = Observer()
    observer.schedule(
        event_handler,
        path=str(watch_dir),
        recursive=False
    )
    
    # 시작
    observer.start()
    
    console.print()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        
        console.print("\n\n[yellow]⏸️  Watcher 중단 중...[/yellow]")
        observer.join()
        
        # 최종 통계
        console.print()
        console.print(event_handler.get_stats())
        console.print("\n[green]✅ 종료 완료[/green]\n")


if __name__ == "__main__":
    main()

