#!/usr/bin/env python3
"""
UMIS 프로덕션 포맷 벤치마크

다양한 직렬화 포맷의 성능 비교:
- YAML (baseline)
- JSON
- MessagePack
- Protobuf (TODO)
- Parquet
"""

import sys
import time
import json
import yaml
from pathlib import Path
from typing import Dict, Any, List
import tempfile

# 벤치마크 결과 저장
results = {}

def measure_time(func):
    """실행 시간 측정 데코레이터"""
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = (time.perf_counter() - start) * 1000  # ms
        return result, elapsed
    return wrapper


class FormatBenchmark:
    """포맷별 성능 테스트"""
    
    def __init__(self, test_data: Dict[str, Any]):
        self.test_data = test_data
        self.results = {}
        
    def run_all(self) -> Dict[str, Dict[str, float]]:
        """모든 포맷 테스트 실행"""
        print("=" * 60)
        print("UMIS 포맷 벤치마크 시작")
        print("=" * 60)
        
        # 1. YAML (baseline)
        print("\n[1/5] YAML 테스트...")
        self.test_yaml()
        
        # 2. JSON
        print("[2/5] JSON 테스트...")
        self.test_json()
        
        # 3. MessagePack
        print("[3/5] MessagePack 테스트...")
        try:
            import msgpack
            self.test_msgpack()
        except ImportError:
            print("  ⚠️  msgpack 미설치 (pip install msgpack)")
            self.results['msgpack'] = None
        
        # 4. Parquet
        print("[4/5] Parquet 테스트...")
        try:
            import pandas as pd
            self.test_parquet()
        except ImportError:
            print("  ⚠️  pandas 미설치 (pip install pandas pyarrow)")
            self.results['parquet'] = None
        
        # 5. CBOR
        print("[5/5] CBOR 테스트...")
        try:
            import cbor2
            self.test_cbor()
        except ImportError:
            print("  ⚠️  cbor2 미설치 (pip install cbor2)")
            self.results['cbor'] = None
        
        return self.results
    
    @measure_time
    def _write_yaml(self, filepath):
        """YAML 쓰기"""
        with open(filepath, 'w', encoding='utf-8') as f:
            yaml.dump(self.test_data, f, default_flow_style=False)
    
    @measure_time
    def _read_yaml(self, filepath):
        """YAML 읽기"""
        with open(filepath, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def test_yaml(self):
        """YAML 성능 측정"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            # Write
            _, write_time = self._write_yaml(tmp_path)
            file_size = Path(tmp_path).stat().st_size
            
            # Read
            _, read_time = self._read_yaml(tmp_path)
            
            self.results['yaml'] = {
                'write_ms': write_time,
                'read_ms': read_time,
                'size_bytes': file_size,
                'size_kb': file_size / 1024
            }
            
            print(f"  ✅ Write: {write_time:.2f}ms | Read: {read_time:.2f}ms | Size: {file_size/1024:.2f}KB")
        finally:
            Path(tmp_path).unlink(missing_ok=True)
    
    @measure_time
    def _write_json(self, filepath):
        """JSON 쓰기"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.test_data, f, separators=(',', ':'))
    
    @measure_time
    def _read_json(self, filepath):
        """JSON 읽기"""
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def test_json(self):
        """JSON 성능 측정"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            # Write
            _, write_time = self._write_json(tmp_path)
            file_size = Path(tmp_path).stat().st_size
            
            # Read
            _, read_time = self._read_json(tmp_path)
            
            self.results['json'] = {
                'write_ms': write_time,
                'read_ms': read_time,
                'size_bytes': file_size,
                'size_kb': file_size / 1024
            }
            
            print(f"  ✅ Write: {write_time:.2f}ms | Read: {read_time:.2f}ms | Size: {file_size/1024:.2f}KB")
        finally:
            Path(tmp_path).unlink(missing_ok=True)
    
    @measure_time
    def _write_msgpack(self, filepath):
        """MessagePack 쓰기"""
        import msgpack
        with open(filepath, 'wb') as f:
            msgpack.pack(self.test_data, f)
    
    @measure_time
    def _read_msgpack(self, filepath):
        """MessagePack 읽기"""
        import msgpack
        with open(filepath, 'rb') as f:
            return msgpack.unpack(f, raw=False)
    
    def test_msgpack(self):
        """MessagePack 성능 측정"""
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.msgpack', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            # Write
            _, write_time = self._write_msgpack(tmp_path)
            file_size = Path(tmp_path).stat().st_size
            
            # Read
            _, read_time = self._read_msgpack(tmp_path)
            
            self.results['msgpack'] = {
                'write_ms': write_time,
                'read_ms': read_time,
                'size_bytes': file_size,
                'size_kb': file_size / 1024
            }
            
            print(f"  ✅ Write: {write_time:.2f}ms | Read: {read_time:.2f}ms | Size: {file_size/1024:.2f}KB")
        finally:
            Path(tmp_path).unlink(missing_ok=True)
    
    @measure_time
    def _write_parquet(self, filepath, df):
        """Parquet 쓰기"""
        df.to_parquet(filepath, compression='zstd', index=False)
    
    @measure_time
    def _read_parquet(self, filepath):
        """Parquet 읽기"""
        import pandas as pd
        return pd.read_parquet(filepath)
    
    def test_parquet(self):
        """Parquet 성능 측정 (테이블 데이터만)"""
        import pandas as pd
        
        # test_data가 리스트 형태여야 함
        if not isinstance(self.test_data, list):
            # Dict를 리스트로 변환 시도
            if 'patterns' in self.test_data and isinstance(self.test_data['patterns'], list):
                table_data = self.test_data['patterns']
            else:
                print("  ⚠️  Parquet는 테이블 데이터만 지원 (스킵)")
                self.results['parquet'] = None
                return
        else:
            table_data = self.test_data
        
        df = pd.DataFrame(table_data)
        
        with tempfile.NamedTemporaryFile(suffix='.parquet', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            # Write
            _, write_time = self._write_parquet(tmp_path, df)
            file_size = Path(tmp_path).stat().st_size
            
            # Read
            _, read_time = self._read_parquet(tmp_path)
            
            self.results['parquet'] = {
                'write_ms': write_time,
                'read_ms': read_time,
                'size_bytes': file_size,
                'size_kb': file_size / 1024
            }
            
            print(f"  ✅ Write: {write_time:.2f}ms | Read: {read_time:.2f}ms | Size: {file_size/1024:.2f}KB")
        finally:
            Path(tmp_path).unlink(missing_ok=True)
    
    @measure_time
    def _write_cbor(self, filepath):
        """CBOR 쓰기"""
        import cbor2
        with open(filepath, 'wb') as f:
            cbor2.dump(self.test_data, f)
    
    @measure_time
    def _read_cbor(self, filepath):
        """CBOR 읽기"""
        import cbor2
        with open(filepath, 'rb') as f:
            return cbor2.load(f)
    
    def test_cbor(self):
        """CBOR 성능 측정"""
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.cbor', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            # Write
            _, write_time = self._write_cbor(tmp_path)
            file_size = Path(tmp_path).stat().st_size
            
            # Read
            _, read_time = self._read_cbor(tmp_path)
            
            self.results['cbor'] = {
                'write_ms': write_time,
                'read_ms': read_time,
                'size_bytes': file_size,
                'size_kb': file_size / 1024
            }
            
            print(f"  ✅ Write: {write_time:.2f}ms | Read: {read_time:.2f}ms | Size: {file_size/1024:.2f}KB")
        finally:
            Path(tmp_path).unlink(missing_ok=True)


def generate_test_data(size='small') -> Dict[str, Any]:
    """테스트 데이터 생성
    
    Args:
        size: 'small', 'medium', 'large'
    """
    if size == 'small':
        # 1개 패턴 (실제 UMIS 패턴 구조)
        return {
            'patterns': [{
                'id': 'BM001',
                'name': 'Subscription Model',
                'category': 'Revenue Model',
                'description': '정기 구독을 통한 반복 수익 모델',
                'triggers': [
                    'High churn in traditional sales',
                    'Customer wants predictable costs',
                    'Product has ongoing value'
                ],
                'examples': [
                    {'company': 'Netflix', 'industry': 'Entertainment'},
                    {'company': 'Spotify', 'industry': 'Music'},
                    {'company': 'Adobe', 'industry': 'Software'}
                ],
                'metrics': {
                    'MRR': 'Monthly Recurring Revenue',
                    'Churn_Rate': 'Customer attrition rate',
                    'LTV': 'Lifetime Value'
                }
            }]
        }
    
    elif size == 'medium':
        # 10개 패턴
        pattern = generate_test_data('small')['patterns'][0]
        return {
            'patterns': [
                {**pattern, 'id': f'BM{i:03d}', 'name': f'Pattern {i}'}
                for i in range(1, 11)
            ]
        }
    
    else:  # large
        # 54개 패턴 (실제 UMIS Explorer 규모)
        pattern = generate_test_data('small')['patterns'][0]
        return {
            'patterns': [
                {**pattern, 'id': f'BM{i:03d}', 'name': f'Pattern {i}'}
                for i in range(1, 55)
            ]
        }


def print_comparison_table(results: Dict[str, Dict[str, float]]):
    """결과 비교 테이블 출력"""
    print("\n" + "=" * 60)
    print("벤치마크 결과 비교")
    print("=" * 60)
    
    # YAML을 기준으로 상대 성능 계산
    yaml_results = results.get('yaml')
    if not yaml_results:
        print("⚠️  YAML 결과 없음")
        return
    
    print(f"\n{'Format':<12} {'Size (KB)':<12} {'Write (ms)':<12} {'Read (ms)':<12} {'Total (ms)':<12}")
    print("-" * 60)
    
    for format_name in ['yaml', 'json', 'msgpack', 'cbor', 'parquet']:
        if format_name not in results or results[format_name] is None:
            continue
        
        r = results[format_name]
        size_kb = r['size_kb']
        write_ms = r['write_ms']
        read_ms = r['read_ms']
        total_ms = write_ms + read_ms
        
        print(f"{format_name.upper():<12} {size_kb:<12.2f} {write_ms:<12.2f} {read_ms:<12.2f} {total_ms:<12.2f}")
    
    # 상대 비교
    print("\n" + "=" * 60)
    print("YAML 대비 성능 (낮을수록 좋음)")
    print("=" * 60)
    print(f"\n{'Format':<12} {'Size':<12} {'Write':<12} {'Read':<12} {'Total':<12}")
    print("-" * 60)
    
    yaml_size = yaml_results['size_kb']
    yaml_write = yaml_results['write_ms']
    yaml_read = yaml_results['read_ms']
    yaml_total = yaml_write + yaml_read
    
    for format_name in ['yaml', 'json', 'msgpack', 'cbor', 'parquet']:
        if format_name not in results or results[format_name] is None:
            continue
        
        r = results[format_name]
        
        size_ratio = r['size_kb'] / yaml_size
        write_ratio = r['write_ms'] / yaml_write if yaml_write > 0 else 0
        read_ratio = r['read_ms'] / yaml_read if yaml_read > 0 else 0
        total_ratio = (r['write_ms'] + r['read_ms']) / yaml_total if yaml_total > 0 else 0
        
        print(f"{format_name.upper():<12} {size_ratio:<12.2f} {write_ratio:<12.2f} {read_ratio:<12.2f} {total_ratio:<12.2f}")
    
    # 권장사항
    print("\n" + "=" * 60)
    print("권장사항")
    print("=" * 60)
    
    # 가장 작은 크기
    smallest = min(
        [(k, v['size_kb']) for k, v in results.items() if v is not None],
        key=lambda x: x[1]
    )
    print(f"📦 최소 크기: {smallest[0].upper()} ({smallest[1]:.2f}KB)")
    
    # 가장 빠른 읽기
    fastest_read = min(
        [(k, v['read_ms']) for k, v in results.items() if v is not None],
        key=lambda x: x[1]
    )
    print(f"⚡ 최고 읽기 속도: {fastest_read[0].upper()} ({fastest_read[1]:.2f}ms)")
    
    # 가장 빠른 전체
    fastest_total = min(
        [(k, v['write_ms'] + v['read_ms']) for k, v in results.items() if v is not None],
        key=lambda x: x[1]
    )
    print(f"🚀 최고 전체 속도: {fastest_total[0].upper()} ({fastest_total[1]:.2f}ms)")


def main():
    """메인 실행"""
    import argparse
    
    parser = argparse.ArgumentParser(description='UMIS 포맷 벤치마크')
    parser.add_argument(
        '--size',
        choices=['small', 'medium', 'large'],
        default='medium',
        help='테스트 데이터 크기 (default: medium)'
    )
    parser.add_argument(
        '--iterations',
        type=int,
        default=1,
        help='반복 횟수 (평균 계산용, default: 1)'
    )
    
    args = parser.parse_args()
    
    print(f"\n테스트 설정:")
    print(f"  - 데이터 크기: {args.size}")
    print(f"  - 반복 횟수: {args.iterations}")
    
    # 테스트 데이터 생성
    test_data = generate_test_data(args.size)
    
    if args.iterations == 1:
        # 단일 실행
        benchmark = FormatBenchmark(test_data)
        results = benchmark.run_all()
        print_comparison_table(results)
    else:
        # 여러 번 실행 후 평균
        print(f"\n{args.iterations}회 반복 실행 중...\n")
        
        all_results = []
        for i in range(args.iterations):
            print(f"[반복 {i+1}/{args.iterations}]")
            benchmark = FormatBenchmark(test_data)
            results = benchmark.run_all()
            all_results.append(results)
        
        # 평균 계산
        avg_results = {}
        for format_name in all_results[0].keys():
            if all_results[0][format_name] is None:
                avg_results[format_name] = None
                continue
            
            avg_results[format_name] = {
                'write_ms': sum(r[format_name]['write_ms'] for r in all_results) / args.iterations,
                'read_ms': sum(r[format_name]['read_ms'] for r in all_results) / args.iterations,
                'size_bytes': all_results[0][format_name]['size_bytes'],  # 크기는 동일
                'size_kb': all_results[0][format_name]['size_kb']
            }
        
        print(f"\n평균 결과 ({args.iterations}회):")
        print_comparison_table(avg_results)


if __name__ == '__main__':
    main()

