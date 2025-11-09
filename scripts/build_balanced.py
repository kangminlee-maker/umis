#!/usr/bin/env python3
"""
UMIS Balanced 프로덕션 빌드 스크립트
설정: YAML → JSON.gz
데이터: YAML → MessagePack

사용법:
    python scripts/build_balanced.py
"""

import yaml
import json
import msgpack
import gzip
import sys
from pathlib import Path
from typing import Dict, Any

class BalancedBuilder:
    """Balanced 빌드 엔진"""
    
    def __init__(self):
        self.root = Path(__file__).parent.parent
        self.dist = self.root / 'dist'
        self.stats = {
            'json_gz': {'count': 0, 'original': 0, 'compressed': 0},
            'msgpack': {'count': 0, 'original': 0, 'compressed': 0},
            'errors': []
        }
    
    def build(self):
        """전체 빌드"""
        print("=" * 60)
        print("UMIS Balanced 빌드")
        print("설정 → JSON.gz, 데이터 → MessagePack")
        print("=" * 60)
        
        # dist 초기화
        if self.dist.exists():
            import shutil
            shutil.rmtree(self.dist)
        self.dist.mkdir()
        
        # 1. 설정 → JSON.gz
        print("\n[1/3] 설정 파일 → JSON.gz...")
        self.convert_configs_to_json()
        
        # 2. 데이터 → MessagePack
        print("\n[2/3] 데이터 파일 → MessagePack...")
        self.convert_data_to_msgpack()
        
        # 3. 통계
        print("\n[3/3] 빌드 완료 통계...")
        self.print_stats()
        
        # 에러 확인
        if self.stats['errors']:
            print("\n⚠️  경고: 일부 파일 변환 실패")
            for error in self.stats['errors']:
                print(f"  - {error}")
            return 1
        
        return 0
    
    def convert_to_json_gz(self, src_path: Path, dst_path: Path):
        """YAML → JSON.gz 변환"""
        try:
            # YAML 로드
            with open(src_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            # 데이터 검증
            if data is None:
                raise ValueError(f"YAML 파싱 결과가 None입니다 (빈 파일이거나 주석만 있음)")
            
            # JSON 직렬화 (최소 크기)
            json_str = json.dumps(
                data,
                separators=(',', ':'),
                ensure_ascii=False
            )
            
            # gzip 압축
            compressed = gzip.compress(
                json_str.encode('utf-8'),
                compresslevel=9
            )
            
            # 저장
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            dst_path.write_bytes(compressed)
            
            # 통계
            original_size = src_path.stat().st_size
            compressed_size = len(compressed)
            ratio = (1 - compressed_size / original_size) * 100
            
            print(f"  ✅ {src_path.name}")
            print(f"     {original_size:,} → {compressed_size:,} bytes ({ratio:.1f}% 감소)")
            
            self.stats['json_gz']['count'] += 1
            self.stats['json_gz']['original'] += original_size
            self.stats['json_gz']['compressed'] += compressed_size
            
        except Exception as e:
            error_msg = f"{src_path.name} (JSON.gz): {str(e)}"
            print(f"  ❌ {error_msg}")
            self.stats['errors'].append(error_msg)
    
    def convert_to_msgpack(self, src_path: Path, dst_path: Path):
        """YAML → MessagePack 변환"""
        try:
            # YAML 로드
            with open(src_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            # 데이터 검증
            if data is None:
                raise ValueError(f"YAML 파싱 결과가 None입니다 (빈 파일이거나 주석만 있음)")
            
            # MessagePack 직렬화
            packed = msgpack.packb(data, use_bin_type=True)
            
            # 저장
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            dst_path.write_bytes(packed)
            
            # 통계
            original_size = src_path.stat().st_size
            packed_size = len(packed)
            ratio = (1 - packed_size / original_size) * 100
            
            print(f"  ✅ {src_path.name}")
            print(f"     {original_size:,} → {packed_size:,} bytes ({ratio:.1f}% 감소)")
            
            self.stats['msgpack']['count'] += 1
            self.stats['msgpack']['original'] += original_size
            self.stats['msgpack']['compressed'] += packed_size
            
        except Exception as e:
            error_msg = f"{src_path.name} (MessagePack): {str(e)}"
            print(f"  ❌ {error_msg}")
            self.stats['errors'].append(error_msg)
    
    def convert_configs_to_json(self):
        """설정 파일 → JSON.gz"""
        
        # 메인 설정
        main_configs = [
            ('umis.yaml', 'umis.json.gz'),
            ('umis_core.yaml', 'umis_core.json.gz'),
        ]
        
        for src, dst in main_configs:
            src_path = self.root / src
            dst_path = self.dist / dst
            if src_path.exists():
                self.convert_to_json_gz(src_path, dst_path)
        
        # Config 디렉토리
        config_files = [
            'schema_registry.yaml',
            'tool_registry.yaml',
            'fermi_model_search.yaml',
            'pattern_relationships.yaml',
            'agent_names.yaml',
            'routing_policy.yaml',
            'runtime.yaml',
            'llm_mode.yaml',
            'projection_rules.yaml',
            'overlay_layer.yaml',
        ]
        
        config_dir = self.root / 'config'
        for config_file in config_files:
            src_path = config_dir / config_file
            dst_path = self.dist / 'config' / config_file.replace('.yaml', '.json.gz')
            if src_path.exists():
                self.convert_to_json_gz(src_path, dst_path)
    
    def convert_data_to_msgpack(self):
        """데이터 파일 → MessagePack"""
        
        data_dir = self.root / 'data' / 'raw'
        
        # 필수 데이터 파일들
        data_files = [
            'umis_business_model_patterns.yaml',
            'umis_disruption_patterns.yaml',
            'market_benchmarks.yaml',
            'market_structure_patterns.yaml',
            'value_chain_benchmarks.yaml',
            'calculation_methodologies.yaml',
            'definition_validation_cases.yaml',
            'data_sources_registry.yaml',
            'umis_ai_guide.yaml',
            'umis_domain_reasoner_methodology.yaml',
            'kpi_definitions.yaml',
        ]
        
        for data_file in data_files:
            src_path = data_dir / data_file
            dst_path = self.dist / 'data' / data_file.replace('.yaml', '.msgpack')
            if src_path.exists():
                self.convert_to_msgpack(src_path, dst_path)
        
        # Tier1 규칙
        tier1_path = self.root / 'data' / 'tier1_rules' / 'builtin.yaml'
        if tier1_path.exists():
            dst_path = self.dist / 'data' / 'tier1_rules' / 'builtin.msgpack'
            self.convert_to_msgpack(tier1_path, dst_path)
        
        # 선택 파일들
        optional_files = [
            ('umis_examples.yaml', 'umis_examples.msgpack'),
            ('umis_deliverable_standards.yaml', 'umis_deliverable_standards.msgpack'),
        ]
        
        for src, dst in optional_files:
            src_path = self.root / src
            dst_path = self.dist / dst
            if src_path.exists():
                self.convert_to_msgpack(src_path, dst_path)
    
    def print_stats(self):
        """통계 출력"""
        print("\n" + "=" * 60)
        print("빌드 완료!")
        print("=" * 60)
        
        # JSON.gz 통계
        json_stats = self.stats['json_gz']
        if json_stats['count'] > 0:
            json_ratio = (1 - json_stats['compressed'] / json_stats['original']) * 100
            print(f"\n📄 JSON.gz (설정 파일):")
            print(f"  파일 수: {json_stats['count']}개")
            print(f"  원본: {json_stats['original'] / 1024:.1f} KB")
            print(f"  압축: {json_stats['compressed'] / 1024:.1f} KB")
            print(f"  압축률: {json_ratio:.1f}% 감소")
        
        # MessagePack 통계
        msgpack_stats = self.stats['msgpack']
        if msgpack_stats['count'] > 0:
            msgpack_ratio = (1 - msgpack_stats['compressed'] / msgpack_stats['original']) * 100
            print(f"\n📦 MessagePack (데이터 파일):")
            print(f"  파일 수: {msgpack_stats['count']}개")
            print(f"  원본: {msgpack_stats['original'] / 1024:.1f} KB")
            print(f"  압축: {msgpack_stats['compressed'] / 1024:.1f} KB")
            print(f"  압축률: {msgpack_ratio:.1f}% 감소")
        
        # 전체 통계
        total_original = json_stats['original'] + msgpack_stats['original']
        total_compressed = json_stats['compressed'] + msgpack_stats['compressed']
        total_count = json_stats['count'] + msgpack_stats['count']
        
        if total_count > 0:
            total_ratio = (1 - total_compressed / total_original) * 100
            print(f"\n🎯 전체:")
            print(f"  파일 수: {total_count}개")
            print(f"  원본: {total_original / 1024:.1f} KB ({total_original / 1024 / 1024:.2f} MB)")
            print(f"  압축: {total_compressed / 1024:.1f} KB ({total_compressed / 1024 / 1024:.2f} MB)")
            print(f"  압축률: {total_ratio:.1f}% 감소")
        
        # 다음 단계
        print("\n" + "=" * 60)
        print("다음 단계:")
        print("=" * 60)
        print("1. 빌드 검증:")
        print("   python -c \"import gzip,json; print(json.load(gzip.open('dist/umis.json.gz')))\"")
        print("\n2. 프로덕션 테스트:")
        print("   UMIS_ENV=production pytest tests/")
        print("\n3. Docker 빌드:")
        print("   docker build -t umis:latest .")
        print("\n4. 배포:")
        print("   docker push umis:latest")


def main():
    """메인 실행"""
    try:
        builder = BalancedBuilder()
        exit_code = builder.build()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n중단됨.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 빌드 실패: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

