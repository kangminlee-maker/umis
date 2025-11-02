#!/usr/bin/env python3
"""
개발 버전 → 배포 패키지 변환

사용:
    python scripts/build_release.py --version 1.1.0

생성:
    releases/umis-rag-v1.1.0.zip
"""

import shutil
import zipfile
from pathlib import Path
from datetime import datetime
import argparse


def build_release(version: str, include_index: bool = None):
    """배포 패키지 생성"""
    
    release_dir = Path("releases") / f"umis-rag-v{version}"
    release_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"📦 배포 패키지 생성: v{version}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    # 1. 필수 파일 복사
    print("\n1️⃣ 필수 파일 복사...")
    
    files_to_copy = [
        "umis_guidelines_v6.2.yaml",
        "umis_business_model_patterns_v6.2.yaml",
        "umis_disruption_patterns_v6.2.yaml",
        "requirements.txt",
        "requirements-dev.txt",
        "README_RAG.md",
        "CURSOR_QUICK_START.md",
        "env.template",
        "Makefile",
    ]
    
    for f in files_to_copy:
        if Path(f).exists():
            shutil.copy(f, release_dir / f)
            print(f"  ✅ {f}")
    
    # 2. 패키지 복사
    print("\n2️⃣ Python 패키지 복사...")
    
    if (Path("umis_rag")).exists():
        shutil.copytree("umis_rag", release_dir / "umis_rag", dirs_exist_ok=True)
        print("  ✅ umis_rag/")
    
    if (Path("scripts")).exists():
        shutil.copytree("scripts", release_dir / "scripts", dirs_exist_ok=True)
        print("  ✅ scripts/")
    
    # 3. 인덱스 포함 여부
    print("\n3️⃣ RAG 인덱스...")
    
    if include_index is None:
        include_index = input("사전 구축 인덱스 포함? (y/N): ").lower() == 'y'
    
    if include_index:
        if Path("data/chroma").exists():
            shutil.copytree("data/chroma", release_dir / "data" / "chroma", dirs_exist_ok=True)
            print("  ✅ data/chroma/ (벡터 인덱스)")
        
        if Path("data/chunks").exists():
            shutil.copytree("data/chunks", release_dir / "data" / "chunks", dirs_exist_ok=True)
            print("  ✅ data/chunks/ (청크)")
        
        index_size = sum(f.stat().st_size for f in (release_dir / "data").rglob('*') if f.is_file())
        print(f"  📊 인덱스 크기: {index_size / (1024*1024):.1f} MB")
    else:
        (release_dir / "data" / "chroma").mkdir(parents=True, exist_ok=True)
        (release_dir / "data" / "chunks").mkdir(parents=True, exist_ok=True)
        (release_dir / "data" / "raw").mkdir(parents=True, exist_ok=True)
        print("  ⚠️  인덱스 미포함 (사용자가 직접 구축)")
    
    # 4. Manifest 생성
    print("\n4️⃣ Manifest 생성...")
    
    manifest = {
        "version": version,
        "release_date": datetime.now().isoformat(),
        "umis_version": "6.2",
        "rag_architecture": "v1.0",
        "includes_index": include_index,
        "embedding_model": "text-embedding-3-large",
        "chunks": 54 if include_index else 0,
        "install_command": "./setup.sh" if not include_index else "즉시 사용 가능",
    }
    
    import yaml
    with open(release_dir / "manifest.yaml", 'w') as f:
        yaml.dump(manifest, f, allow_unicode=True)
    
    print("  ✅ manifest.yaml")
    
    # 5. 배포 노트
    print("\n5️⃣ 배포 노트...")
    
    with open(release_dir / "RELEASE_NOTES.md", 'w') as f:
        f.write(f"""# UMIS RAG v{version}

## 📅 배포 날짜
{datetime.now().strftime('%Y년 %m월 %d일')}

## 📦 포함 내용
- ✅ UMIS Guidelines v6.2
- ✅ Explorer RAG 에이전트
- ✅ 54개 패턴/사례 청크
{f'- ✅ 사전 구축 벡터 인덱스 ({index_size / (1024*1024):.1f} MB)' if include_index else '- ⚠️ 인덱스 미포함 (직접 구축 필요)'}

## 🚀 빠른 시작

### 설치

```bash
# 압축 해제
unzip umis-rag-v{version}.zip
cd umis-rag-v{version}/

{'# 즉시 사용 가능!' if include_index else '# 초기 설정'}
{'source venv/bin/activate' if include_index else './setup.sh'}
```

### 사용

**Cursor에서:**
```
@umis_guidelines_v6.2.yaml

"피아노 구독 서비스 기회 분석"
```

**필요 시 RAG 검색:**
```bash
python scripts/query_rag.py pattern "구독 서비스"
```

## 📖 문서
- CURSOR_QUICK_START.md - Cursor 사용 가이드
- README_RAG.md - 전체 개요

## ⚙️ 요구사항
- Python 3.11+
- OpenAI API Key

## 🆕 변경사항
- Vector RAG 프로토타입
- text-embedding-3-large (고품질)
- 54개 검증된 패턴/사례

## 🔄 업데이트 방법

### Local RAG (자체 관리)
```bash
git pull origin main
make rebuild
```

### Shared RAG (중앙 서버)
- 자동 업데이트 (별도 작업 불필요)
""")
    
    print("  ✅ RELEASE_NOTES.md")
    
    # 6. ZIP 압축
    print("\n6️⃣ ZIP 압축...")
    
    zip_path = Path("releases") / f"umis-rag-v{version}.zip"
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file in release_dir.rglob('*'):
            if file.is_file():
                arcname = file.relative_to(release_dir.parent)
                zf.write(file, arcname)
    
    zip_size = zip_path.stat().st_size / (1024 * 1024)
    
    print(f"  ✅ {zip_path.name} ({zip_size:.1f} MB)")
    
    # 완료
    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("✅ 배포 패키지 생성 완료!")
    print()
    print(f"📦 파일: {zip_path}")
    print(f"📊 크기: {zip_size:.1f} MB")
    print()
    print("GitHub Release:")
    print("  1. https://github.com/your/umis-rag/releases/new")
    print(f"  2. Tag: v{version}")
    print(f"  3. Upload: {zip_path.name}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UMIS RAG 배포 패키지 생성")
    parser.add_argument("--version", required=True, help="배포 버전 (예: 1.1.0)")
    parser.add_argument("--include-index", action="store_true", help="인덱스 포함")
    parser.add_argument("--no-index", action="store_true", help="인덱스 제외")
    
    args = parser.parse_args()
    
    include = None
    if args.include_index:
        include = True
    elif args.no_index:
        include = False
    
    build_release(args.version, include)

