#!/usr/bin/env python3
"""
RAG 롤백 스크립트
마지막 정상 상태로 복원

사용법:
    python3 scripts/rollback_rag.py
    python3 scripts/rollback_rag.py --list  # 백업 목록만 표시
"""

import shutil
import subprocess
from pathlib import Path
from datetime import datetime


def list_backups():
    """백업 목록 표시"""
    backup_dir = Path('config/backups')
    
    if not backup_dir.exists():
        print("❌ 백업 디렉토리 없음")
        return
    
    backups = sorted(backup_dir.glob('tool_registry_*.yaml'), reverse=True)
    
    if not backups:
        print("❌ 백업 파일 없음")
        return
    
    print("📂 백업 목록:")
    print()
    
    for i, backup in enumerate(backups[:10], 1):  # 최근 10개만
        stat = backup.stat()
        size = stat.st_size
        mtime = datetime.fromtimestamp(stat.st_mtime)
        
        print(f"{i}. {backup.name}")
        print(f"   - 크기: {size:,} bytes")
        print(f"   - 날짜: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
        print()


def rollback():
    """최근 백업으로 롤백"""
    
    print("🔄 RAG 롤백 시작")
    print()
    
    backup_dir = Path('config/backups')
    
    if not backup_dir.exists():
        print("❌ 백업 디렉토리 없음")
        return
    
    # 최근 백업 찾기
    backups = sorted(backup_dir.glob('tool_registry_*.yaml'), reverse=True)
    
    if not backups:
        print("❌ 백업 파일 없음")
        return
    
    latest = backups[0]
    print(f"📂 최근 백업: {latest.name}")
    
    # 백업 정보
    stat = latest.stat()
    mtime = datetime.fromtimestamp(stat.st_mtime)
    print(f"   - 크기: {stat.st_size:,} bytes")
    print(f"   - 날짜: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 복원 확인
    response = input("복원하시겠습니까? (y/N): ")
    if response.lower() != 'y':
        print("취소됨")
        return
    
    print()
    
    # 복원
    shutil.copy(latest, 'config/tool_registry.yaml')
    print(f"✅ tool_registry.yaml 복원 완료")
    print()
    
    # RAG 재구축
    print("🔨 RAG 재구축 중...")
    result = subprocess.run(
        ['python3', 'scripts/build_system_knowledge.py'],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"❌ RAG 재구축 실패:\n{result.stderr}")
        return
    
    print("   ✅ RAG 재구축 완료")
    print()
    print("✅ 롤백 완료!")


def main():
    import sys
    
    if '--list' in sys.argv:
        list_backups()
    else:
        rollback()


if __name__ == "__main__":
    main()





