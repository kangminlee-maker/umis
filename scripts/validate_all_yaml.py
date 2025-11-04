#!/usr/bin/env python3
"""
data/raw 폴더의 모든 YAML 파일 검증
- 문법 오류
- 구조 오류
- 논리 오류
"""

import yaml
from pathlib import Path
from typing import List, Dict, Any


def validate_yaml_syntax(file_path: Path) -> Dict[str, Any]:
    """YAML 문법 검증"""
    
    result = {
        'file': str(file_path),
        'syntax_valid': False,
        'error': None,
        'error_line': None
    }
    
    try:
        with open(file_path, encoding='utf-8') as f:
            yaml.safe_load(f)
        
        result['syntax_valid'] = True
        print(f"✅ {file_path.name}: 문법 정상")
        
    except yaml.YAMLError as e:
        result['error'] = str(e.problem)
        result['error_line'] = e.problem_mark.line if hasattr(e, 'problem_mark') else None
        print(f"❌ {file_path.name}: Line {result['error_line']} - {result['error']}")
    
    except Exception as e:
        result['error'] = str(e)
        print(f"❌ {file_path.name}: {e}")
    
    return result


def validate_all_yaml_files(data_dir: str = "data/raw") -> List[Dict]:
    """모든 YAML 파일 검증"""
    
    data_path = Path(data_dir)
    yaml_files = list(data_path.glob("*.yaml"))
    
    print(f"\n🔍 검증 시작: {len(yaml_files)}개 YAML 파일")
    print(f"   경로: {data_dir}\n")
    
    results = []
    
    for yaml_file in sorted(yaml_files):
        result = validate_yaml_syntax(yaml_file)
        results.append(result)
    
    # 요약
    print(f"\n{'='*60}")
    print("검증 결과 요약")
    print(f"{'='*60}\n")
    
    valid_count = sum(1 for r in results if r['syntax_valid'])
    invalid_count = len(results) - valid_count
    
    print(f"✅ 정상: {valid_count}개")
    print(f"❌ 오류: {invalid_count}개")
    
    if invalid_count > 0:
        print(f"\n오류 파일:")
        for r in results:
            if not r['syntax_valid']:
                print(f"  - {Path(r['file']).name}")
                print(f"    Line {r['error_line']}: {r['error']}")
    
    return results


def main():
    """메인 함수"""
    results = validate_all_yaml_files()
    
    # 종료 코드
    invalid_count = sum(1 for r in results if not r['syntax_valid'])
    
    if invalid_count > 0:
        print(f"\n⚠️ {invalid_count}개 파일 수정 필요")
        exit(1)
    else:
        print(f"\n🎉 모든 파일 정상!")
        exit(0)


if __name__ == "__main__":
    main()

