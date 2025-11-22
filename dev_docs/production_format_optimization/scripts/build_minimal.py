#!/usr/bin/env python3
"""
UMIS Minimalist 빌드 스크립트
YAML → JSON.gz 변환 (단순화된 프로덕션 빌드)

사용법:
    python scripts/build_minimal.py
"""

import yaml
import json
import gzip
import sys
from pathlib import Path
from typing import Dict, Any

class MinimalistBuilder:
    """Minimalist 빌드 엔진 (YAML → JSON.gz)"""
    
    def __init__(self):
        self.root = Path(__file__).parent.parent
        self.dist = self.root / 'dist'
        self.stats = {
            'total_files': 0,
            'total_original': 0,
            'total_compressed': 0,
            'errors': []
        }
    
    def build(self):
        """전체 빌드"""
        print("=" * 60)
        print("UMIS Minimalist 빌드 (YAML → JSON.gz)")
        print("=" * 60)
        
        # dist 초기화
        if self.dist.exists():
            import shutil
            shutil.rmtree(self.dist)
        self.dist.mkdir()
        
        # 1. 핵심 설정
        print("\n[1/4] 핵심 설정 변환 중...")
        self.convert_core_configs()
        
        # 2. Config 파일들
        print("\n[2/4] Config 파일 변환 중...")
        self.convert_configs()
        
        # 3. 데이터 파일들
        print("\n[3/4] 데이터 파일 변환 중...")
        self.convert_data_files()
        
        # 4. 선택 파일들
        print("\n[4/4] 선택 파일 변환 중...")
        self.convert_optional_files()
        
        # 통계
        self.print_stats()
        
        # 에러 확인
        if self.stats['errors']:
            print("\n⚠️  경고: 일부 파일 변환 실패")
            for error in self.stats['errors']:
                print(f"  - {error}")
            return 1
        
        return 0
    
    def convert_file(self, yaml_path: Path, output_path: Path):
        """단일 파일 변환
        
        Args:
            yaml_path: YAML 원본 파일
            output_path: JSON.gz 출력 파일
        """
        try:
            # YAML 로드
            with open(yaml_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            # JSON 직렬화 (최소 크기)
            json_str = json.dumps(
                data,
                separators=(',', ':'),
                ensure_ascii=False
            )
            
            # gzip 압축 (최대 압축)
            compressed = gzip.compress(
                json_str.encode('utf-8'),
                compresslevel=9
            )
            
            # 저장
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_bytes(compressed)
            
            # 통계
            original_size = yaml_path.stat().st_size
            compressed_size = len(compressed)
            ratio = (1 - compressed_size / original_size) * 100
            
            print(f"  ✅ {yaml_path.name}")
            print(f"     {original_size:,} → {compressed_size:,} bytes ({ratio:.1f}% 감소)")
            
            self.stats['total_files'] += 1
            self.stats['total_original'] += original_size
            self.stats['total_compressed'] += compressed_size
            
        except Exception as e:
            error_msg = f"{yaml_path.name}: {str(e)}"
            print(f"  ❌ {error_msg}")
            self.stats['errors'].append(error_msg)
    
    def convert_core_configs(self):
        """핵심 설정 변환"""
        files = [
            ('umis.yaml', 'umis.json.gz'),
            ('umis_core.yaml', 'umis_core.json.gz'),
        ]
        
        for src, dst in files:
            src_path = self.root / src
            dst_path = self.dist / dst
            if src_path.exists():
                self.convert_file(src_path, dst_path)
            else:
                print(f"  ⚠️  {src} 없음 (스킵)")
    
    def convert_configs(self):
        """Config 파일들 변환"""
        config_dir = self.root / 'config'
        
        # 필수 설정 파일들
        required_configs = [
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
        
        for config_file in required_configs:
            src_path = config_dir / config_file
            dst_path = self.dist / 'config' / config_file.replace('.yaml', '.json.gz')
            if src_path.exists():
                self.convert_file(src_path, dst_path)
            else:
                print(f"  ⚠️  {config_file} 없음 (스킵)")
    
    def convert_data_files(self):
        """데이터 파일들 변환"""
        data_dir = self.root / 'data' / 'raw'
        
        # 필수 데이터 파일들
        required_data = [
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
        ]
        
        for data_file in required_data:
            src_path = data_dir / data_file
            dst_path = self.dist / 'data' / data_file.replace('.yaml', '.json.gz')
            if src_path.exists():
                self.convert_file(src_path, dst_path)
            else:
                print(f"  ⚠️  {data_file} 없음 (스킵)")
        
        # Tier1 규칙
        tier1_path = self.root / 'data' / 'tier1_rules' / 'builtin.yaml'
        if tier1_path.exists():
            dst_path = self.dist / 'data' / 'tier1_rules' / 'builtin.json.gz'
            self.convert_file(tier1_path, dst_path)
    
    def convert_optional_files(self):
        """선택 파일들 변환"""
        optional_files = [
            ('umis_examples.yaml', 'umis_examples.json.gz'),
            ('umis_deliverable_standards.yaml', 'umis_deliverable_standards.json.gz'),
        ]
        
        for src, dst in optional_files:
            src_path = self.root / src
            dst_path = self.dist / dst
            if src_path.exists():
                self.convert_file(src_path, dst_path)
        
        # KPI 정의
        kpi_path = self.root / 'data' / 'raw' / 'kpi_definitions.yaml'
        if kpi_path.exists():
            dst_path = self.dist / 'data' / 'kpi_definitions.json.gz'
            self.convert_file(kpi_path, dst_path)
    
    def print_stats(self):
        """통계 출력"""
        print("\n" + "=" * 60)
        print("빌드 완료!")
        print("=" * 60)
        
        if self.stats['total_files'] == 0:
            print("\n⚠️  변환된 파일이 없습니다.")
            return
        
        total_original_mb = self.stats['total_original'] / 1024 / 1024
        total_compressed_mb = self.stats['total_compressed'] / 1024 / 1024
        total_ratio = (1 - self.stats['total_compressed'] / self.stats['total_original']) * 100
        
        print(f"\n📦 변환된 파일: {self.stats['total_files']}개")
        print(f"📊 원본 크기: {total_original_mb:.2f} MB")
        print(f"📉 압축 크기: {total_compressed_mb:.2f} MB")
        print(f"🎯 압축률: {total_ratio:.1f}% 감소")
        
        print("\n다음 단계:")
        print("1. dist/ 폴더 확인")
        print(f"   ls -lh {self.dist}")
        print("2. 테스트 (Python)")
        print("   python -c \"import gzip, json; print(json.load(gzip.open('dist/umis.json.gz')))\"")
        print("3. 배포")
        print("   프로덕션 환경에 dist/ 폴더 복사")


def main():
    """메인 실행"""
    try:
        builder = MinimalistBuilder()
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

