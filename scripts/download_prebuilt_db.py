#!/usr/bin/env python3
"""
사전 빌드 ChromaDB 다운로드
Google Drive에서 자동 다운로드 및 압축 해제
"""

import os
import sys
import subprocess
from pathlib import Path
import urllib.request
import shutil


# ========================================
# TODO: Google Drive 업로드 후 파일 ID 업데이트
# ========================================
# 
# 업로드 방법:
# 1. chroma-db-v7.1.0-dev2.tar.gz를 Google Drive에 업로드
# 2. 공유 설정: "링크가 있는 모든 사용자"
# 3. 링크에서 파일 ID 추출
#    예: https://drive.google.com/file/d/1ABC123XYZ/view
#        → 파일 ID: 1ABC123XYZ
# 4. 아래 GDRIVE_FILE_ID에 붙여넣기
# 
# ========================================

GDRIVE_FILE_ID = "1EKHFfT5XnI_0St38-kq_4GnorZssd9q_"  # TODO: 업로드 후 파일 ID 입력

# 버전별 다운로드 URL
DOWNLOAD_URLS = {
    "v7.1.0-dev2": {
        "gdrive_id": GDRIVE_FILE_ID,
        "size": "16MB (압축)",
        "original_size": "51MB",
        "collections": 13,
        "documents": 826,
        "file": "chroma-db-v7.1.0-dev2.tar.gz"
    }
}


def download_from_gdrive(file_id: str, output_path: Path) -> bool:
    """
    Google Drive에서 파일 다운로드
    
    Args:
        file_id: Google Drive 파일 ID
        output_path: 저장 경로
    
    Returns:
        성공 여부
    """
    
    print(f"📥 다운로드 시작...")
    print(f"   파일 ID: {file_id}")
    print(f"   저장 위치: {output_path}")
    
    # Google Drive Direct Download URL
    url = f"https://drive.google.com/uc?export=download&id={file_id}"
    
    try:
        # gdown 사용 (더 안정적)
        try:
            import gdown
            gdown.download(url, str(output_path), quiet=False)
        except ImportError:
            print("\n⚠️ gdown 모듈이 없습니다. 설치 중...")
            subprocess.run([sys.executable, "-m", "pip", "install", "gdown"], check=True)
            import gdown
            gdown.download(url, str(output_path), quiet=False)
        
        print(f"✅ 다운로드 완료: {output_path}")
        return True
        
    except Exception as e:
        print(f"❌ 다운로드 실패: {e}")
        print(f"\n수동 다운로드:")
        print(f"  1. 브라우저에서 열기: https://drive.google.com/file/d/{file_id}")
        print(f"  2. 다운로드")
        print(f"  3. {output_path}에 저장")
        return False


def extract_db(tar_file: Path, extract_to: Path) -> bool:
    """
    압축 파일 해제
    
    Args:
        tar_file: .tar.gz 파일
        extract_to: 압축 해제 위치 (프로젝트 루트)
    
    Returns:
        성공 여부
    """
    
    print(f"\n📦 압축 해제 중...")
    print(f"   파일: {tar_file}")
    print(f"   위치: {extract_to}")
    
    try:
        import tarfile
        
        with tarfile.open(tar_file, 'r:gz') as tar:
            tar.extractall(path=extract_to)
        
        print(f"✅ 압축 해제 완료")
        return True
        
    except Exception as e:
        print(f"❌ 압축 해제 실패: {e}")
        return False


def verify_db(chroma_path: Path) -> bool:
    """
    ChromaDB 검증
    
    Args:
        chroma_path: data/chroma 경로
    
    Returns:
        유효 여부
    """
    
    print(f"\n🔍 ChromaDB 검증 중...")
    
    # 1. 폴더 존재
    if not chroma_path.exists():
        print(f"❌ 폴더 없음: {chroma_path}")
        return False
    
    # 2. chroma.sqlite3 존재
    sqlite_file = chroma_path / 'chroma.sqlite3'
    if not sqlite_file.exists():
        print(f"❌ chroma.sqlite3 없음")
        return False
    
    print(f"✅ chroma.sqlite3 발견 ({sqlite_file.stat().st_size / 1024 / 1024:.1f}MB)")
    
    # 3. ChromaDB로 Collection 확인
    try:
        import chromadb
        
        client = chromadb.PersistentClient(path=str(chroma_path))
        collections = client.list_collections()
        
        print(f"✅ {len(collections)}개 Collection 발견:")
        for col in collections[:5]:  # 처음 5개만
            print(f"   - {col.name}: {col.count()}개")
        
        if len(collections) > 5:
            print(f"   ... 외 {len(collections) - 5}개")
        
        return True
        
    except Exception as e:
        print(f"⚠️ Collection 검증 실패: {e}")
        print(f"   (ChromaDB는 있지만 접근 오류)")
        return False


def main():
    """메인 함수"""
    
    print("\n" + "="*60)
    print("🚀 UMIS ChromaDB 사전 빌드 다운로드")
    print("="*60)
    
    # 프로젝트 루트 확인
    project_root = Path.cwd()
    chroma_path = project_root / 'data' / 'chroma'
    
    print(f"\n현재 위치: {project_root}")
    
    # 기존 DB 확인
    if chroma_path.exists():
        print(f"\n⚠️ ChromaDB가 이미 존재합니다: {chroma_path}")
        
        choice = input("덮어쓰기? (y/N): ")
        if choice.lower() != 'y':
            print("❌ 취소됨")
            return
        
        # 백업
        backup_path = project_root / 'data' / 'chroma_backup'
        print(f"📦 기존 DB 백업 중: {backup_path}")
        shutil.move(str(chroma_path), str(backup_path))
    
    # 다운로드
    tar_file = project_root / 'chroma-db.tar.gz'
    
    # Google Drive 파일 ID 확인
    if GDRIVE_FILE_ID == "YOUR_FILE_ID_HERE":
        print("\n❌ Google Drive 파일 ID가 설정되지 않았습니다.")
        print("\n수동 다운로드:")
        print("  1. README.md의 다운로드 링크에서 파일 다운로드")
        print("  2. chroma-db.tar.gz를 프로젝트 루트에 저장")
        print("  3. 다시 실행: python scripts/download_prebuilt_db.py --extract")
        return
    
    success = download_from_gdrive(GDRIVE_FILE_ID, tar_file)
    
    if not success:
        return
    
    # 압축 해제
    success = extract_db(tar_file, project_root)
    
    if not success:
        return
    
    # 검증
    success = verify_db(chroma_path)
    
    if not success:
        print("\n⚠️ 검증 실패. 재생성 권장:")
        print("  python scripts/build_agent_rag_collections.py --agent all")
        return
    
    # 정리
    print(f"\n🗑️  임시 파일 삭제...")
    tar_file.unlink()
    
    print("\n" + "="*60)
    print("🎉 ChromaDB 설치 완료!")
    print("="*60)
    
    print("\n다음 단계:")
    print("  python scripts/test_agent_rag.py")
    print("  또는")
    print("  python -c \"from umis_rag.agents.quantifier import QuantifierRAG; q=QuantifierRAG(); print('✅ OK')\"")


if __name__ == "__main__":
    
    # --extract 플래그 (tar 파일이 이미 있는 경우)
    if len(sys.argv) > 1 and sys.argv[1] == '--extract':
        project_root = Path.cwd()
        tar_file = project_root / 'chroma-db.tar.gz'
        
        if not tar_file.exists():
            print(f"❌ {tar_file} 파일이 없습니다.")
            sys.exit(1)
        
        extract_db(tar_file, project_root)
        verify_db(project_root / 'data' / 'chroma')
    else:
        main()

