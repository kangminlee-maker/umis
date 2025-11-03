#!/usr/bin/env python3
"""
UMIS v7.0.0 Automated Setup Script
AI가 자동으로 실행 가능한 설치 스크립트

사용법:
  python setup.py              # 전체 설치
  python setup.py --minimal    # 최소 설치 (Neo4j 제외)
  python setup.py --check      # 설치 상태 확인
"""

import os
import sys
import subprocess
import platform
from pathlib import Path
from typing import Tuple, Optional

# ============================================
# 색상 출력
# ============================================

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(msg: str):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{msg:^60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

def print_step(step: int, msg: str):
    print(f"{Colors.OKCYAN}{Colors.BOLD}[Step {step}]{Colors.ENDC} {msg}")

def print_success(msg: str):
    print(f"{Colors.OKGREEN}✅ {msg}{Colors.ENDC}")

def print_warning(msg: str):
    print(f"{Colors.WARNING}⚠️  {msg}{Colors.ENDC}")

def print_error(msg: str):
    print(f"{Colors.FAIL}❌ {msg}{Colors.ENDC}")

def print_info(msg: str):
    print(f"{Colors.OKBLUE}ℹ️  {msg}{Colors.ENDC}")

# ============================================
# 유틸리티
# ============================================

def run_command(cmd: str, check: bool = True) -> Tuple[bool, str]:
    """명령 실행"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            check=check,
            capture_output=True,
            text=True
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def check_python_version() -> bool:
    """Python 버전 확인 (3.9+)"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 9:
        print_success(f"Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print_error(f"Python 3.9+ 필요 (현재: {version.major}.{version.minor})")
        return False

def check_venv() -> bool:
    """가상환경 활성화 확인"""
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print_success("가상환경 활성화됨")
        return True
    else:
        print_warning("가상환경 비활성화 (권장: venv 사용)")
        return False

def check_file_exists(path: str) -> bool:
    """파일 존재 확인"""
    return Path(path).exists()

def check_openai_key() -> bool:
    """OpenAI API 키 확인"""
    env_path = Path(".env")
    
    if not env_path.exists():
        print_warning(".env 파일 없음")
        return False
    
    with open(env_path) as f:
        content = f.read()
    
    if "your-api-key-here" in content:
        print_warning("OpenAI API 키 미설정 (.env 파일 수정 필요)")
        return False
    
    if "OPENAI_API_KEY=" in content and len(content.split("OPENAI_API_KEY=")[1].split("\n")[0].strip()) > 10:
        print_success("OpenAI API 키 설정됨")
        return True
    
    print_warning("OpenAI API 키 확인 필요")
    return False

def check_docker() -> bool:
    """Docker 실행 확인"""
    success, _ = run_command("docker ps", check=False)
    if success:
        print_success("Docker 실행 중")
        return True
    else:
        print_warning("Docker 미실행 (Neo4j 필요 시)")
        return False

def check_neo4j() -> bool:
    """Neo4j 컨테이너 확인"""
    success, output = run_command("docker ps | grep umis-neo4j", check=False)
    if success and "umis-neo4j" in output:
        print_success("Neo4j 컨테이너 실행 중")
        return True
    else:
        print_info("Neo4j 컨테이너 미실행 (선택 사항)")
        return False

def check_chromadb() -> bool:
    """ChromaDB 인덱스 확인"""
    chroma_path = Path("data/chroma")
    
    if not chroma_path.exists():
        print_warning("ChromaDB 인덱스 없음 (빌드 필요)")
        return False
    
    # chroma.sqlite3 파일 확인
    if (chroma_path / "chroma.sqlite3").exists():
        print_success("ChromaDB 인덱스 존재")
        return True
    
    print_warning("ChromaDB 인덱스 비어있음")
    return False

# ============================================
# 설치 단계
# ============================================

def step1_check_environment():
    """Step 1: 환경 확인"""
    print_step(1, "환경 확인")
    
    all_ok = True
    
    # Python 버전
    if not check_python_version():
        all_ok = False
    
    # 가상환경
    check_venv()  # 경고만
    
    # 현재 디렉토리
    if check_file_exists("umis.yaml"):
        print_success("UMIS 루트 디렉토리 확인")
    else:
        print_error("umis.yaml 없음 - UMIS 루트에서 실행하세요")
        all_ok = False
    
    return all_ok

def step2_install_dependencies():
    """Step 2: 패키지 설치"""
    print_step(2, "Python 패키지 설치")
    
    print_info("pip install -r requirements.txt 실행 중...")
    success, output = run_command("pip install -r requirements.txt")
    
    if success:
        print_success("모든 패키지 설치 완료")
        return True
    else:
        print_error("패키지 설치 실패")
        print(output)
        return False

def step3_setup_env_file():
    """Step 3: .env 파일 설정"""
    print_step(3, ".env 파일 설정")
    
    env_path = Path(".env")
    
    if env_path.exists():
        print_success(".env 파일 존재")
        check_openai_key()
    else:
        print_info("env.template → .env 복사 중...")
        success, _ = run_command("cp env.template .env")
        
        if success:
            print_success(".env 파일 생성 완료")
            print_warning("⚠️  다음 단계: .env 파일에서 OPENAI_API_KEY 설정 필요!")
            print_info("   → https://platform.openai.com/api-keys")
        else:
            print_error(".env 파일 생성 실패")
            return False
    
    return True

def step4_build_rag_index():
    """Step 4: RAG 인덱스 빌드"""
    print_step(4, "RAG 인덱스 빌드")
    
    # OpenAI 키 확인
    if not check_openai_key():
        print_error("OpenAI API 키 미설정 - RAG 인덱스 빌드 불가")
        print_info("   .env 파일에서 OPENAI_API_KEY 설정 후 다시 실행하세요")
        return False
    
    # ChromaDB 존재 확인
    if check_chromadb():
        print_info("기존 인덱스 발견 - 재빌드하시겠습니까? (y/N): ", end='')
        response = input().strip().lower()
        if response != 'y':
            print_info("인덱스 빌드 스킵")
            return True
    
    print_info("RAG 인덱스 빌드 중... (1-2분 소요)")
    print_info("비용: 약 $0.006")
    
    # YAML → JSONL 변환
    print_info("  [1/2] YAML → JSONL 변환...")
    success, output = run_command("python scripts/01_convert_yaml.py")
    
    if not success:
        print_error("YAML 변환 실패")
        print(output)
        return False
    
    # 인덱스 빌드
    print_info("  [2/2] Vector DB 빌드...")
    success, output = run_command("python scripts/02_build_index.py --agent explorer")
    
    if success:
        print_success("RAG 인덱스 빌드 완료")
        return True
    else:
        print_error("인덱스 빌드 실패")
        print(output)
        return False

def step5_setup_neo4j(skip: bool = False):
    """Step 5: Neo4j 설정 (선택 사항)"""
    print_step(5, "Neo4j 설정 (선택 사항)")
    
    if skip:
        print_info("Neo4j 설정 스킵 (--minimal 모드)")
        return True
    
    # Docker 확인
    if not check_docker():
        print_warning("Docker 미실행 - Neo4j 설정 스킵")
        print_info("   Knowledge Graph 기능 필요 시 Docker 설치 후:")
        print_info("   → docker-compose up -d")
        return True
    
    # Neo4j 확인
    if check_neo4j():
        print_success("Neo4j 이미 실행 중")
        return True
    
    # Neo4j 실행 여부 묻기
    print_info("Neo4j를 실행하시겠습니까? (y/N): ", end='')
    response = input().strip().lower()
    
    if response == 'y':
        print_info("docker-compose up -d 실행 중...")
        success, output = run_command("docker-compose up -d")
        
        if success:
            print_success("Neo4j 컨테이너 시작됨")
            print_info("   → Neo4j Browser: http://localhost:7474")
            print_info("   → User: neo4j / Password: umis_password")
            return True
        else:
            print_error("Neo4j 시작 실패")
            print(output)
            return False
    else:
        print_info("Neo4j 설정 스킵")
        return True

def check_installation():
    """설치 상태 확인"""
    print_header("UMIS v7.0.0 설치 상태 확인")
    
    status = {}
    
    print("\n1️⃣  환경")
    status['python'] = check_python_version()
    status['venv'] = check_venv()
    status['umis_root'] = check_file_exists("umis.yaml")
    
    print("\n2️⃣  필수 파일")
    status['env_file'] = check_file_exists(".env")
    status['api_key'] = check_openai_key()
    
    print("\n3️⃣  Python 패키지")
    try:
        import chromadb
        import openai
        import pydantic
        print_success("핵심 패키지 설치됨 (chromadb, openai, pydantic)")
        status['packages'] = True
    except ImportError as e:
        print_error(f"패키지 미설치: {e}")
        status['packages'] = False
    
    print("\n4️⃣  RAG 인덱스")
    status['chromadb'] = check_chromadb()
    
    print("\n5️⃣  선택 사항 (Neo4j)")
    status['docker'] = check_docker()
    status['neo4j'] = check_neo4j()
    
    # 요약
    print("\n" + "="*60)
    essential_ok = all([
        status.get('python', False),
        status.get('umis_root', False),
        status.get('env_file', False),
        status.get('packages', False),
        status.get('chromadb', False)
    ])
    
    if essential_ok:
        print_success("✅ UMIS 사용 준비 완료!")
        print_info("\n다음 단계:")
        print_info("  Cursor Composer (Cmd+I)")
        print_info('  "@Explorer, 구독 모델 패턴 찾아줘"')
    else:
        print_warning("⚠️  설치 미완료 - python setup.py 실행 필요")
    
    print("="*60 + "\n")

# ============================================
# 메인
# ============================================

def main():
    """메인 설치 프로세스"""
    
    # 인자 파싱
    args = sys.argv[1:]
    minimal_mode = '--minimal' in args
    check_mode = '--check' in args
    
    if check_mode:
        check_installation()
        return
    
    # 헤더
    print_header("UMIS v7.0.0 자동 설치")
    print_info("Universal Market Intelligence System")
    print_info("RAG-powered 5-Agent 협업 시스템\n")
    
    if minimal_mode:
        print_info("모드: 최소 설치 (Neo4j 제외)")
    else:
        print_info("모드: 전체 설치")
    
    # 설치 시작
    print("\n" + "="*60)
    
    # Step 1: 환경 확인
    if not step1_check_environment():
        print_error("\n환경 확인 실패 - 설치 중단")
        sys.exit(1)
    
    # Step 2: 패키지 설치
    if not step2_install_dependencies():
        print_error("\n패키지 설치 실패 - 설치 중단")
        sys.exit(1)
    
    # Step 3: .env 설정
    if not step3_setup_env_file():
        print_error("\n.env 설정 실패 - 설치 중단")
        sys.exit(1)
    
    # Step 4: RAG 인덱스 빌드
    if not step4_build_rag_index():
        print_warning("\nRAG 인덱스 빌드 실패")
        print_info("  → .env에서 OPENAI_API_KEY 설정 후")
        print_info("  → python scripts/02_build_index.py --agent explorer 실행")
    
    # Step 5: Neo4j 설정 (선택)
    if not minimal_mode:
        step5_setup_neo4j()
    
    # 완료
    print_header("설치 완료!")
    print_success("✅ UMIS v7.0.0 설치 성공\n")
    
    print_info("다음 단계:")
    print_info("  1. Cursor 열기")
    print_info("  2. Cmd+I (Composer)")
    print_info('  3. "@Explorer, 구독 모델 패턴 찾아줘"')
    print_info("\n또는:")
    print_info('  python scripts/query_rag.py "구독 모델"\n')
    
    print_info("문서:")
    print_info("  → UMIS_ARCHITECTURE_BLUEPRINT.md (전체 구조)")
    print_info("  → SETUP.md (상세 가이드)")
    
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_warning("\n\n설치 중단됨")
        sys.exit(1)
    except Exception as e:
        print_error(f"\n예상치 못한 오류: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

