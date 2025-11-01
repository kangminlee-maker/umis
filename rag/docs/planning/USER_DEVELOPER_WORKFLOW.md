# UMIS RAG: 사용자 vs 개발자 워크플로우

## 🎯 핵심 철학

```
사용과 개발의 경계를 최소화
피드백 루프를 최대한 짧게
배포는 간단하게
```

---

## 👨‍💻 개발자 워크플로우 (당신)

### 특징: 인라인 어셈블러 수준 피드백

```yaml
목표:
  - YAML 수정 → 즉시 반영
  - 사용 중 피드백 → 바로 개발
  - 테스트 → 수정 → 테스트 (빠른 반복)
```

### 워크플로우

```bash
# 1. 개발 모드 시작 (한 번만)
make dev

# → Watcher 실행됨
# → data/raw/ 감시 중
# → YAML 변경 자동 감지

# 2. Cursor에서 UMIS 사용
@umis_guidelines_v6.2.yaml
"피아노 구독 서비스 분석"

# 3. 사용 중 발견
"코웨이 사례에 해지율 데이터가 없네?"

# 4. 즉시 수정 (VS Code)
# data/raw/umis_business_model_patterns_v6.2.yaml 열기
코웨이 섹션에 추가:
  churn_rate: "3-5% (업계 평균)"

# Ctrl+S 저장

# 5. 자동 업데이트! (2초)
# Watcher 출력:
🔄 변경 감지: umis_business_model_patterns_v6.2.yaml
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  1/3 청크 재생성 중...
     → 31개 청크 생성
  2/3 벡터 임베딩 중...
  3/3 인덱스 업데이트 중...

  ✅ 완료! (1.8초)
  💾 31개 청크 업데이트
  🔍 다음 검색부터 반영됨

# 6. 즉시 테스트
python scripts/query_rag.py case "코웨이"

# → 해지율 데이터 포함됨! ✅

# 7. Cursor에서 계속 사용
# → 이미 반영됨!
```

### 피드백 루프 타임라인

```
0초: YAML 수정 (VS Code)
0초: 저장 (Ctrl+S)
0.1초: Watcher 감지
0.5초: 청크 재생성
1.5초: 벡터 업데이트
2초: 완료! ✅

→ 2초 만에 적용! ⚡
→ 인라인 어셈블러 수준!
```

---

## 👥 사용자 워크플로우 (다른 사람)

### 특징: 안정적 버전, 간단한 사용

```yaml
목표:
  - 복잡한 설정 없이 사용
  - 안정적인 품질
  - 간단한 업데이트
```

### Option A: Local RAG (자체 관리)

```bash
# 1. 설치 (최초 1회)
git clone https://github.com/your/umis-rag
cd umis-rag
make install

# → 자동으로:
#   - venv 생성
#   - 패키지 설치
#   - .env 설정 가이드
#   - 초기 인덱스 구축

# 2. 사용
@umis_guidelines_v6.2.yaml

# YAML만 사용 또는 RAG 추가

# 3. 업데이트 (월 1회)
git pull origin main
make rebuild

# → 최신 YAML + 인덱스 재구축
```

**장점:**
```yaml
✅ 완전한 통제
✅ 오프라인 사용
✅ 커스터마이징 가능
✅ 개인 데이터 추가 가능
```

**단점:**
```yaml
❌ 초기 설정 필요
❌ 관리 부담
❌ 디스크 공간 (1GB)
```

### Option B: Shared RAG (중앙 관리)

```bash
# 1. 설정 (최초 1회)
# .env 파일만 생성
UMIS_RAG_ENDPOINT=https://umis-rag.your-server.com
UMIS_API_KEY=your-api-key

# 2. 사용
@umis_guidelines_v6.2.yaml

# RAG는 중앙 서버 사용 (자동)

# 3. 업데이트
# 중앙에서 자동!
# 사용자는 아무것도 안 해도 됨
```

**장점:**
```yaml
✅ 설정 최소
✅ 자동 업데이트
✅ 디스크 공간 절약
✅ 항상 최신
```

**단점:**
```yaml
❌ 인터넷 필요
❌ 중앙 의존
❌ 커스터마이징 불가
❌ API 비용 가능
```

---

## 🔄 버전 관리 전략

### Git Branch 전략

```
main (stable)
  ├── develop (latest)
  │   ├── feature/knowledge-graph
  │   ├── feature/stewart-circular-detection
  │   └── feature/goal-alignment
  │
  └── releases/
      ├── v1.0.0 (2024-11-01)
      ├── v1.1.0 (2024-11-15) - planned
      └── v1.2.0 (2024-12-01) - planned

사용자는:
  - main branch clone (안정적)
  
개발자는:
  - develop branch (최신)
  - feature branches (실험)
```

### YAML 버전 관리

```yaml
umis-main/
├── umis_guidelines_v6.2.yaml          (stable)
├── umis_business_model_patterns_v6.2.yaml
├── umis_disruption_patterns_v6.2.yaml
│
└── dev/                                (개발용)
    ├── umis_guidelines_v6.3_dev.yaml
    ├── new_patterns.yaml
    └── experimental/
```

### RAG 인덱스 버전 관리

```yaml
data/
├── chroma/                  (현재 활성)
│   └── steve_knowledge_base
│
└── versions/                (버전별 스냅샷)
    ├── v1.0.0/
    │   ├── chroma/
    │   ├── chunks/
    │   └── manifest.yaml
    │
    └── v1.1.0/
        └── ...

배포 시:
  1. 현재 인덱스를 versions/v1.1.0/로 복사
  2. manifest.yaml 생성 (메타데이터)
  3. ZIP 압축
  4. GitHub Release 업로드
```

---

## 🚀 개발 → 배포 파이프라인

### 자동화 스크립트

```python
# scripts/build_release.py

"""
개발 버전 → 배포 패키지 변환

사용:
    python scripts/build_release.py --version 1.1.0

생성:
    releases/umis-rag-v1.1.0.zip
    ├── umis_guidelines_v6.2.yaml
    ├── umis_rag/
    ├── data/chroma/  (사전 구축 인덱스)
    ├── scripts/
    ├── requirements.txt
    ├── .env.example
    └── README.md
"""

import shutil
import zipfile
from pathlib import Path
from datetime import datetime

def build_release(version: str):
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
        ".env.example",
    ]
    
    for f in files_to_copy:
        shutil.copy(f, release_dir / f)
        print(f"  ✅ {f}")
    
    # 2. 패키지 복사
    print("\n2️⃣ Python 패키지 복사...")
    shutil.copytree("umis_rag", release_dir / "umis_rag")
    shutil.copytree("scripts", release_dir / "scripts")
    print("  ✅ umis_rag/")
    print("  ✅ scripts/")
    
    # 3. 사전 구축 인덱스 복사 (선택)
    print("\n3️⃣ 인덱스 복사 (선택)...")
    
    include_index = input("사전 구축 인덱스 포함? (y/N): ")
    
    if include_index.lower() == 'y':
        shutil.copytree("data/chroma", release_dir / "data" / "chroma")
        shutil.copytree("data/chunks", release_dir / "data" / "chunks")
        print("  ✅ data/chroma/ (벡터 인덱스)")
        print("  ✅ data/chunks/ (청크)")
    else:
        (release_dir / "data" / "chroma").mkdir(parents=True)
        (release_dir / "data" / "chunks").mkdir(parents=True)
        print("  ⚠️  인덱스 미포함 (사용자가 직접 구축)")
    
    # 4. 배포 노트 생성
    print("\n4️⃣ 배포 노트 생성...")
    
    with open(release_dir / "RELEASE_NOTES.md", 'w') as f:
        f.write(f"""# UMIS RAG v{version} Release Notes

## 배포 날짜
{datetime.now().strftime('%Y-%m-%d')}

## 포함 내용
- UMIS Guidelines v6.2
- Steve RAG 에이전트
- 54개 사전 청크
{'- 사전 구축 벡터 인덱스' if include_index.lower() == 'y' else ''}

## 설치 방법
1. 압축 해제
2. `./setup.sh` 실행
3. `.env` 파일에 OpenAI API 키 입력
{'4. 사용 시작 (인덱스 이미 구축됨!)' if include_index.lower() == 'y' else '4. `make rebuild` 실행 (인덱스 구축)'}

## 사용 방법
- 📖 CURSOR_QUICK_START.md 참조

## 버전 정보
- Vector RAG: v1.0
- Embeddings: text-embedding-3-large
- Documents: 54 chunks
""")
    
    print("  ✅ RELEASE_NOTES.md")
    
    # 5. ZIP 압축
    print("\n5️⃣ ZIP 압축...")
    
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
    print("다음 단계:")
    print("  1. GitHub Release 생성")
    print(f"  2. {zip_path.name} 업로드")
    print("  3. RELEASE_NOTES.md 내용 복사")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", required=True, help="배포 버전 (예: 1.1.0)")
    args = parser.parse_args()
    
    build_release(args.version)

