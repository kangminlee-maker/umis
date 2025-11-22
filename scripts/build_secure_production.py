#!/usr/bin/env python3
"""
UMIS 보안 프로덕션 빌드 스크립트
v7.5.0 - 성능 + IP 보호

보안 레벨:
  - level1: MessagePack + 압축 (기본, 무료)
  - level2: AES-256 암호화 (B2B)
  - level3: PyArmor + 암호화 (엔터프라이즈)
"""

import sys
import yaml
import json
import msgpack
import zstandard as zstd
from pathlib import Path
from typing import Dict, Any, Optional
import shutil
import subprocess
import hashlib
import os

# 프로젝트 루트
ROOT = Path(__file__).parent.parent
DIST = ROOT / 'dist'
DIST.mkdir(exist_ok=True)


class SecureBuilder:
    """보안 빌드 엔진"""
    
    def __init__(self, security_level: int = 1, license_key: Optional[str] = None):
        """
        Args:
            security_level: 1 (기본), 2 (암호화), 3 (PyArmor)
            license_key: Level 2+ 필요
        """
        self.security_level = security_level
        self.license_key = license_key
        
        # Level 2+ 검증
        if security_level >= 2:
            if not license_key:
                raise ValueError("Security level 2+ requires license_key")
            
            # 암호화 키 생성 (라이선스 키 기반)
            from cryptography.fernet import Fernet
            key_material = hashlib.pbkdf2_hmac(
                'sha256',
                license_key.encode(),
                b'umis_v7.5.0_salt',
                100000,
                dklen=32
            )
            import base64
            self.encryption_key = base64.urlsafe_b64encode(key_material)
            self.cipher = Fernet(self.encryption_key)
        
        print(f"🔒 보안 레벨: {security_level}")
        print(f"📦 출력 디렉토리: {DIST}")
    
    # =========================================
    # Level 1: MessagePack + 압축
    # =========================================
    
    def pack_and_compress(self, data: Dict[str, Any]) -> bytes:
        """MessagePack + zstd 압축"""
        packed = msgpack.packb(data, use_bin_type=True)
        compressed = zstd.compress(packed, level=22)  # 최대 압축
        return compressed
    
    def build_level1_config(self):
        """설정 파일: YAML → MessagePack + zstd"""
        print("\n[1/6] 설정 파일 변환 중...")
        
        config_files = [
            'config/agent_names.yaml',
            'config/schema_registry.yaml',
            'config/routing_policy.yaml',
        ]
        
        for yaml_path in config_files:
            source = ROOT / yaml_path
            if not source.exists():
                print(f"  ⚠️  {yaml_path} 없음, 스킵")
                continue
            
            # YAML 로드
            with open(source) as f:
                data = yaml.safe_load(f)
            
            # 압축
            compressed = self.pack_and_compress(data)
            
            # 저장
            output = DIST / f"{source.stem}.bin"
            with open(output, 'wb') as f:
                f.write(compressed)
            
            # 통계
            original_size = source.stat().st_size
            compressed_size = len(compressed)
            ratio = (1 - compressed_size / original_size) * 100
            
            print(f"  ✅ {source.name}: {original_size} → {compressed_size} bytes ({ratio:.1f}% 감소)")
    
    def build_level1_patterns(self):
        """패턴 라이브러리: YAML → MessagePack + zstd"""
        print("\n[2/6] 패턴 라이브러리 변환 중...")
        
        pattern_files = [
            'data/raw/umis_business_model_patterns.yaml',
            'data/raw/umis_disruption_patterns.yaml',
        ]
        
        for yaml_path in pattern_files:
            source = ROOT / yaml_path
            if not source.exists():
                print(f"  ⚠️  {yaml_path} 없음, 스킵")
                continue
            
            with open(source) as f:
                data = yaml.safe_load(f)
            
            compressed = self.pack_and_compress(data)
            
            output = DIST / f"{source.stem}.bin"
            with open(output, 'wb') as f:
                f.write(compressed)
            
            original_size = source.stat().st_size
            compressed_size = len(compressed)
            ratio = (1 - compressed_size / original_size) * 100
            
            print(f"  ✅ {source.name}: {original_size} → {compressed_size} bytes ({ratio:.1f}% 감소)")
    
    def build_level1_prompts(self):
        """프롬프트: umis_core.yaml → MessagePack + zstd"""
        print("\n[3/6] 프롬프트 변환 중...")
        
        source = ROOT / 'umis_core.yaml'
        if not source.exists():
            print("  ⚠️  umis_core.yaml 없음, umis.yaml 사용")
            source = ROOT / 'umis.yaml'
        
        with open(source) as f:
            data = yaml.safe_load(f)
        
        compressed = self.pack_and_compress(data)
        
        output = DIST / 'prompts.bin'
        with open(output, 'wb') as f:
            f.write(compressed)
        
        original_size = source.stat().st_size
        compressed_size = len(compressed)
        ratio = (1 - compressed_size / original_size) * 100
        
        print(f"  ✅ {source.name}: {original_size} → {compressed_size} bytes ({ratio:.1f}% 감소)")
    
    # =========================================
    # Level 2: AES-256 암호화
    # =========================================
    
    def encrypt_data(self, data: bytes) -> bytes:
        """AES-256 암호화"""
        if self.security_level < 2:
            return data
        return self.cipher.encrypt(data)
    
    def build_level2_config(self):
        """Level 2: 암호화 추가"""
        print("\n[1/6] 설정 파일 암호화 중...")
        
        config_files = list((ROOT / 'config').glob('*.yaml'))
        
        for source in config_files:
            with open(source) as f:
                data = yaml.safe_load(f)
            
            # MessagePack + 압축
            compressed = self.pack_and_compress(data)
            
            # 암호화
            encrypted = self.encrypt_data(compressed)
            
            # 저장
            output = DIST / f"{source.stem}.enc"
            with open(output, 'wb') as f:
                f.write(encrypted)
            
            original_size = source.stat().st_size
            encrypted_size = len(encrypted)
            
            print(f"  🔐 {source.name}: {original_size} → {encrypted_size} bytes (암호화됨)")
    
    def build_level2_patterns(self):
        """Level 2: 패턴 암호화"""
        print("\n[2/6] 패턴 라이브러리 암호화 중...")
        
        pattern_files = [
            'data/raw/umis_business_model_patterns.yaml',
            'data/raw/umis_disruption_patterns.yaml',
        ]
        
        for yaml_path in pattern_files:
            source = ROOT / yaml_path
            if not source.exists():
                continue
            
            with open(source) as f:
                data = yaml.safe_load(f)
            
            compressed = self.pack_and_compress(data)
            encrypted = self.encrypt_data(compressed)
            
            output = DIST / f"{source.stem}.enc"
            with open(output, 'wb') as f:
                f.write(encrypted)
            
            print(f"  🔐 {source.name}: 암호화 완료")
    
    def build_level2_prompts(self):
        """Level 2: 프롬프트 암호화"""
        print("\n[3/6] 프롬프트 암호화 중...")
        
        source = ROOT / 'umis_core.yaml'
        if not source.exists():
            source = ROOT / 'umis.yaml'
        
        with open(source) as f:
            data = yaml.safe_load(f)
        
        compressed = self.pack_and_compress(data)
        encrypted = self.encrypt_data(compressed)
        
        output = DIST / 'prompts.enc'
        with open(output, 'wb') as f:
            f.write(encrypted)
        
        print(f"  🔐 {source.name}: 암호화 완료")
    
    # =========================================
    # Python 코드 보호
    # =========================================
    
    def build_pyc(self):
        """Python → .pyc (bytecode)"""
        print("\n[4/6] Python 코드 컴파일 중...")
        
        # 컴파일
        result = subprocess.run(
            ['python3', '-m', 'compileall', 'umis_rag'],
            cwd=ROOT,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("  ✅ .pyc 컴파일 완료")
        else:
            print(f"  ⚠️  컴파일 경고:\n{result.stderr}")
        
        # .py 파일 제거 (선택)
        if self.security_level >= 2:
            print("  🗑️  .py 파일 제거 중...")
            py_files = list(Path(ROOT / 'umis_rag').rglob('*.py'))
            for py_file in py_files:
                # __init__.py는 유지 (import 위해)
                if py_file.name != '__init__.py':
                    py_file.unlink()
            print(f"  ✅ {len(py_files)} 개 .py 파일 제거")
    
    def build_pyarmor(self):
        """Level 3: PyArmor 난독화"""
        if self.security_level < 3:
            return
        
        print("\n[5/6] PyArmor 난독화 중...")
        
        # PyArmor 설치 확인
        try:
            subprocess.run(['pyarmor', '--version'], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("  ⚠️  PyArmor 미설치: pip install pyarmor")
            print("  ⚠️  PyArmor 스킵, .pyc만 사용")
            return
        
        # 난독화
        cmd = [
            'pyarmor',
            'gen',
            '--output', str(DIST / 'umis_rag_protected'),
            '--pack', 'dist',
            '--obf-code', '2',
            '--obf-module', '1',
            'umis_rag/'
        ]
        
        result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("  ✅ PyArmor 난독화 완료")
        else:
            print(f"  ❌ PyArmor 실패:\n{result.stderr}")
    
    # =========================================
    # 런타임 로더 생성
    # =========================================
    
    def generate_loader(self):
        """런타임 로더 코드 생성"""
        print("\n[6/6] 런타임 로더 생성 중...")
        
        if self.security_level == 1:
            loader_code = self._generate_loader_level1()
        elif self.security_level == 2:
            loader_code = self._generate_loader_level2()
        else:
            loader_code = self._generate_loader_level3()
        
        output = DIST / 'config_loader.py'
        with open(output, 'w') as f:
            f.write(loader_code)
        
        print(f"  ✅ {output} 생성 완료")
        print(f"  💡 사용법: from dist.config_loader import load_config")
    
    def _generate_loader_level1(self) -> str:
        """Level 1 로더 코드"""
        return '''"""
UMIS 프로덕션 설정 로더 (Level 1)
MessagePack + zstd 압축
"""

import msgpack
import zstandard as zstd
from pathlib import Path

DIST = Path(__file__).parent

def load_config(name: str):
    """설정 로드
    
    Args:
        name: 파일명 (확장자 제외)
        예: 'schema_registry', 'agent_names'
    
    Returns:
        dict: 설정 데이터
    """
    filepath = DIST / f"{name}.bin"
    
    with open(filepath, 'rb') as f:
        compressed = f.read()
    
    # 압축 해제
    decompressed = zstd.decompress(compressed)
    
    # MessagePack 디코딩
    data = msgpack.unpackb(decompressed, raw=False)
    
    return data

def load_prompts():
    """프롬프트 로드"""
    return load_config('prompts')

def load_patterns(name: str):
    """패턴 로드
    
    Args:
        name: 'umis_business_model_patterns' 또는 'umis_disruption_patterns'
    """
    return load_config(name)

# 사용 예시
if __name__ == '__main__':
    config = load_config('schema_registry')
    print(f"✅ Config loaded: {len(config)} keys")
    
    prompts = load_prompts()
    print(f"✅ Prompts loaded: {len(prompts)} keys")
'''
    
    def _generate_loader_level2(self) -> str:
        """Level 2 로더 코드 (암호화)"""
        return f'''"""
UMIS 프로덕션 설정 로더 (Level 2)
AES-256 암호화 + MessagePack + zstd
"""

import msgpack
import zstandard as zstd
from pathlib import Path
from cryptography.fernet import Fernet
import hashlib
import base64
import os

DIST = Path(__file__).parent

class SecureConfigLoader:
    """암호화된 설정 로더"""
    
    def __init__(self, license_key: str = None):
        """
        Args:
            license_key: 라이선스 키 (또는 환경변수 UMIS_LICENSE_KEY)
        """
        if not license_key:
            license_key = os.getenv('UMIS_LICENSE_KEY')
        
        if not license_key:
            raise ValueError("License key required. Set UMIS_LICENSE_KEY env var.")
        
        # 암호화 키 생성
        key_material = hashlib.pbkdf2_hmac(
            'sha256',
            license_key.encode(),
            b'umis_v7.5.0_salt',
            100000,
            dklen=32
        )
        encryption_key = base64.urlsafe_b64encode(key_material)
        self.cipher = Fernet(encryption_key)
    
    def load(self, name: str):
        """설정 로드 및 복호화"""
        filepath = DIST / f"{{name}}.enc"
        
        with open(filepath, 'rb') as f:
            encrypted = f.read()
        
        # 복호화
        try:
            decrypted = self.cipher.decrypt(encrypted)
        except Exception as e:
            raise ValueError(f"Invalid license key: {{e}}")
        
        # 압축 해제
        decompressed = zstd.decompress(decrypted)
        
        # MessagePack 디코딩
        data = msgpack.unpackb(decompressed, raw=False)
        
        return data
    
    def load_prompts(self):
        return self.load('prompts')
    
    def load_patterns(self, name: str):
        return self.load(name)

# 전역 로더
_loader = None

def get_loader():
    global _loader
    if _loader is None:
        _loader = SecureConfigLoader()
    return _loader

def load_config(name: str):
    return get_loader().load(name)

def load_prompts():
    return get_loader().load_prompts()

def load_patterns(name: str):
    return get_loader().load_patterns(name)

# 사용 예시
if __name__ == '__main__':
    # 환경변수 설정: export UMIS_LICENSE_KEY="your-key-here"
    loader = SecureConfigLoader()
    
    config = loader.load('schema_registry')
    print(f"✅ Config loaded: {{len(config)}} keys")
'''
    
    def _generate_loader_level3(self) -> str:
        """Level 3 로더 코드 (PyArmor + 암호화)"""
        return self._generate_loader_level2()  # PyArmor는 코드 보호만
    
    # =========================================
    # 빌드 실행
    # =========================================
    
    def build(self):
        """전체 빌드"""
        print("\n" + "="*60)
        print("UMIS 보안 프로덕션 빌드")
        print("="*60)
        
        # dist 초기화
        if DIST.exists():
            shutil.rmtree(DIST)
        DIST.mkdir()
        
        # 레벨별 빌드
        if self.security_level == 1:
            self.build_level1_config()
            self.build_level1_patterns()
            self.build_level1_prompts()
        else:
            self.build_level2_config()
            self.build_level2_patterns()
            self.build_level2_prompts()
        
        # Python 코드
        self.build_pyc()
        self.build_pyarmor()
        
        # 로더
        self.generate_loader()
        
        # 요약
        self.print_summary()
    
    def print_summary(self):
        """빌드 요약"""
        print("\n" + "="*60)
        print("빌드 완료!")
        print("="*60)
        
        # 파일 목록
        files = sorted(DIST.glob('**/*'))
        total_size = sum(f.stat().st_size for f in files if f.is_file())
        
        print(f"\n📦 출력 파일: {len([f for f in files if f.is_file()])}개")
        print(f"💾 총 크기: {total_size:,} bytes ({total_size/1024:.1f} KB)")
        
        print("\n파일 목록:")
        for f in files:
            if f.is_file():
                size = f.stat().st_size
                print(f"  - {f.name}: {size:,} bytes")
        
        # 다음 단계
        print("\n" + "="*60)
        print("다음 단계:")
        print("="*60)
        
        if self.security_level == 1:
            print("1. dist/ 폴더를 프로덕션 환경에 복사")
            print("2. 사용:")
            print("   from dist.config_loader import load_config")
            print("   config = load_config('schema_registry')")
        else:
            print("1. 라이선스 키 설정:")
            print(f"   export UMIS_LICENSE_KEY='{self.license_key}'")
            print("2. dist/ 폴더를 프로덕션 환경에 복사")
            print("3. 사용:")
            print("   from dist.config_loader import load_config")
            print("   config = load_config('schema_registry')")


def main():
    """CLI 실행"""
    import argparse
    
    parser = argparse.ArgumentParser(description='UMIS 보안 프로덕션 빌드')
    parser.add_argument(
        '--level',
        type=int,
        choices=[1, 2, 3],
        default=1,
        help='보안 레벨: 1 (압축), 2 (암호화), 3 (PyArmor)'
    )
    parser.add_argument(
        '--license-key',
        type=str,
        help='라이선스 키 (Level 2+ 필수)'
    )
    
    args = parser.parse_args()
    
    # Level 2+ 검증
    if args.level >= 2:
        if not args.license_key:
            # 환경변수 확인
            args.license_key = os.getenv('UMIS_BUILD_LICENSE_KEY')
            if not args.license_key:
                print("❌ Error: --license-key required for security level 2+")
                print("   또는 환경변수 설정: export UMIS_BUILD_LICENSE_KEY='your-key'")
                sys.exit(1)
    
    # 빌드
    try:
        builder = SecureBuilder(
            security_level=args.level,
            license_key=args.license_key
        )
        builder.build()
    except Exception as e:
        print(f"\n❌ 빌드 실패: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

