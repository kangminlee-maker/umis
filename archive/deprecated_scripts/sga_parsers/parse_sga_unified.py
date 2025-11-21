"""
통합 SG&A 파싱 파이프라인

4-Layer 자동 파이프라인:
  Layer 1: Robust 크롤러 (이마트 패턴) - 웹 크롤링
  Layer 2: Optimized 파서 (일반 기업) - document.xml
  Layer 3: Hybrid 파서 (복잡 구조) - document.xml + LLM
  Layer 4: Manual fallback

목표:
- 최대 성공률 (70-90%)
- 완전 자동화
- Production 품질

사용법:
    python scripts/parse_sga_unified.py --corp 이마트 --rcept 20250318000688
    
    # 배치 처리
    python scripts/parse_sga_unified.py --batch --file corps.txt

작성일: 2025-11-16
버전: v1.0
"""

import sys
import argparse
from pathlib import Path
from typing import Dict, List, Optional
import yaml
import os

# UMIS 루트 추가
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from umis_rag.utils.dart_crawler_robust import crawl_sga_robust
from umis_rag.utils.dart_api import DARTClient


def parse_sga_unified(
    corp_name: str,
    rcept_no: str,
    year: int = 2024,
    save_yaml: bool = True,
    cache_dir: str = '/tmp/dart_unified_cache'
) -> Dict:
    """
    통합 SG&A 파싱 파이프라인 (4-Layer)
    
    Args:
        corp_name: 기업명
        rcept_no: 사업보고서 접수번호
        year: 사업연도
        save_yaml: YAML 자동 저장 여부
        cache_dir: 캐시 디렉토리
    
    Returns:
        {
            'success': bool,
            'corp_name': str,
            'total': float (억원),
            'items': {...},
            'grade': 'A'|'B'|'C'|'D',
            'method': 'robust_crawler'|'optimized'|'hybrid'|'manual',
            'layer': 1|2|3|4
        }
    """
    
    print(f"\n{'='*80}")
    print(f"통합 SG&A 파싱 파이프라인")
    print(f"{'='*80}")
    print(f"기업: {corp_name}")
    print(f"접수번호: {rcept_no}")
    print(f"사업연도: {year}")
    
    # DART API로 정확한 OFS 확인
    print(f"\n[사전 검증] DART API OFS 조회...")
    
    try:
        client = DARTClient()
        corp_code = client.get_corp_code(corp_name)
        
        if corp_code:
            financials = client.get_financials(corp_code=corp_code, year=year, fs_div='OFS')
            
            if financials and not (isinstance(financials, dict) and 'error' in financials):
                # 판매비와관리비 찾기
                for item in financials:
                    account_nm = item.get('account_nm', '')
                    
                    if '판매비' in account_nm and '관리비' in account_nm:
                        amount_str = item.get('thstrm_amount', '0')
                        amount_won = int(amount_str.replace(',', ''))
                        dart_ofs = amount_won / 100_000_000  # 원 → 억원
                        
                        print(f"  ✓ DART OFS: {dart_ofs:,.1f}억원")
                        break
                else:
                    dart_ofs = None
            else:
                dart_ofs = None
        else:
            dart_ofs = None
    except Exception as e:
        print(f"  ⚠️ DART API 조회 실패: {e}")
        dart_ofs = None
    
    # Layer 1: Robust 크롤러
    print(f"\n{'='*80}")
    print(f"[Layer 1] Robust 크롤러 시도")
    print(f"{'='*80}")
    
    try:
        result = crawl_sga_robust(
            corp_name=corp_name,
            rcept_no=rcept_no,
            cache_dir=cache_dir,
            verify_ofs=False
        )
        
        if result['success']:
            # OFS 검증
            if dart_ofs:
                error_rate = abs(result['total'] - dart_ofs) / dart_ofs * 100
                
                if error_rate <= 5.0:
                    grade = 'A'
                elif error_rate <= 10.0:
                    grade = 'B'
                elif error_rate <= 20.0:
                    grade = 'C'
                else:
                    grade = 'D'
                
                result['grade'] = grade
                result['error_rate'] = error_rate
                result['dart_ofs'] = dart_ofs
                
                print(f"\n✅ Layer 1 성공!")
                print(f"  크롤링: {result['total']:,.1f}억원")
                print(f"  DART OFS: {dart_ofs:,.1f}억원")
                print(f"  오차: {error_rate:.2f}%")
                print(f"  등급: {grade}")
                
                if grade == 'A':
                    result['method'] = 'robust_crawler'
                    result['layer'] = 1
                    
                    # YAML 저장
                    if save_yaml:
                        save_to_yaml_file(result)
                    
                    return result
            else:
                # OFS 없어도 일단 성공으로 처리
                result['method'] = 'robust_crawler'
                result['layer'] = 1
                result['grade'] = 'UNKNOWN'
                
                print(f"\n✅ Layer 1 성공 (OFS 검증 없음)")
                print(f"  크롤링: {result['total']:,.1f}억원")
                
                if save_yaml:
                    save_to_yaml_file(result)
                
                return result
        
        print(f"\n⚠️ Layer 1 실패: {result.get('error', 'Unknown')}")
        
    except Exception as e:
        print(f"\n⚠️ Layer 1 예외: {e}")
    
    # Layer 2: Optimized 파서
    print(f"\n{'='*80}")
    print(f"[Layer 2] XML 파서 - Optimized 시도")
    print(f"{'='*80}")
    
    try:
        # parse_company_optimized 직접 호출
        sys.path.insert(0, str(Path(__file__).parent))
        from parse_sga_optimized import parse_company_optimized
        
        result = parse_company_optimized(corp_name, rcept_no)
        
        if result.get('success') and result.get('grade') == 'A':
            # OFS 업데이트
            if dart_ofs:
                result['dart_ofs'] = dart_ofs
                result['error_rate'] = abs(result['total'] - dart_ofs) / dart_ofs * 100
            
            result['layer'] = 2
            
            print(f"\n✅ Layer 2 성공!")
            print(f"  크롤링: {result['total']:,.1f}억원")
            
            if dart_ofs:
                print(f"  DART OFS: {dart_ofs:,.1f}억원")
                print(f"  오차: {result['error_rate']:.2f}%")
            
            print(f"  등급: {result['grade']}")
            
            # YAML 저장
            if save_yaml:
                save_to_yaml_file(result)
            
            return result
        
        print(f"\n⚠️ Layer 2 실패: {result.get('error', 'Unknown')} (등급: {result.get('grade', 'N/A')})")
        
    except ImportError as e:
        print(f"\n⚠️ Layer 2 Import 오류: {e}")
    except Exception as e:
        print(f"\n⚠️ Layer 2 예외: {e}")
    
    # Layer 3: Hybrid 파서
    print(f"\n{'='*80}")
    print(f"[Layer 3] XML 파서 - Hybrid 시도")
    print(f"{'='*80}")
    
    try:
        # parse_company_hybrid 직접 호출
        from parse_sga_hybrid import parse_company_hybrid
        
        result = parse_company_hybrid(corp_name, rcept_no)
        
        if result.get('success') and result.get('grade') == 'A':
            # OFS 업데이트
            if dart_ofs:
                result['dart_ofs'] = dart_ofs
                result['error_rate'] = abs(result['total'] - dart_ofs) / dart_ofs * 100
            
            result['layer'] = 3
            
            print(f"\n✅ Layer 3 성공!")
            print(f"  크롤링: {result['total']:,.1f}억원")
            
            if dart_ofs:
                print(f"  DART OFS: {dart_ofs:,.1f}억원")
                print(f"  오차: {result['error_rate']:.2f}%")
            
            print(f"  등급: {result['grade']}")
            print(f"  비용: ~${result.get('llm_cost', 0.005)}")
            
            # YAML 저장
            if save_yaml:
                save_to_yaml_file(result)
            
            return result
        
        print(f"\n⚠️ Layer 3 실패: {result.get('error', 'Unknown')} (등급: {result.get('grade', 'N/A')})")
        
    except ImportError as e:
        print(f"\n⚠️ Layer 3 Import 오류: {e}")
    except Exception as e:
        print(f"\n⚠️ Layer 3 예외: {e}")
    
    # Layer 4: Manual fallback
    print(f"\n{'='*80}")
    print(f"[Layer 4] Manual fallback")
    print(f"{'='*80}")
    
    print(f"\n❌ 모든 자동 방법 실패")
    print(f"\n수동 입력이 필요합니다:")
    print(f"  1. DART 웹사이트에서 확인")
    print(f"     https://dart.fss.or.kr/dsaf001/main.do?rcpNo={rcept_no}")
    print(f"  2. 판매비와관리비 세부 항목 확인")
    print(f"  3. YAML 파일 수동 작성")
    
    return {
        'success': False,
        'corp_name': corp_name,
        'needs_manual': True,
        'method': 'manual',
        'layer': 4,
        'dart_ofs': dart_ofs
    }


def save_to_yaml_file(result: Dict):
    """결과를 YAML 파일로 저장"""
    
    corp_name = result['corp_name']
    year = result.get('year', 2024)
    
    # YAML 경로
    yaml_path = ROOT / 'data' / 'raw' / f'{corp_name}_sga_unified.yaml'
    
    # YAML 데이터 구성
    yaml_data = {
        'company': corp_name,
        'year': year,
        'source': result.get('method', 'unified'),
        'layer': result.get('layer', 0),
        'crawling_date': '2025-11-16',
        
        'sga_total': {
            'amount_eokwon': result['total'],
            'unit': result.get('unit', '백만원'),
            'grade': result.get('grade', 'UNKNOWN')
        },
        
        'dart_verification': {
            'ofs': result.get('dart_ofs'),
            'error_rate': result.get('error_rate', 0),
            'fs_type': result.get('fs_type', 'OFS')
        },
        
        'items': result.get('items', {}),
        
        'metadata': {
            'rcept_no': result.get('rcept_no'),
            'dcm_no': result.get('section', {}).get('dcmNo') if 'section' in result else None,
            'ele_id': result.get('section', {}).get('eleId') if 'section' in result else None
        }
    }
    
    # YAML 저장
    with open(yaml_path, 'w', encoding='utf-8') as f:
        yaml.dump(yaml_data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    
    print(f"\n✅ YAML 저장 완료: {yaml_path}")


def batch_process(corps_file: str, cache_dir: str = '/tmp/dart_unified_cache'):
    """배치 처리"""
    
    print(f"\n{'='*80}")
    print(f"배치 SG&A 파싱")
    print(f"{'='*80}")
    
    # 파일에서 기업 목록 로드
    with open(corps_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    companies = []
    
    for line in lines:
        line = line.strip()
        
        if line and not line.startswith('#'):
            # 형식: 기업명,rcept_no
            parts = line.split(',')
            
            if len(parts) >= 2:
                companies.append({
                    'name': parts[0].strip(),
                    'rcept': parts[1].strip()
                })
    
    print(f"\n총 {len(companies)}개 기업")
    
    results = []
    
    for i, company in enumerate(companies, 1):
        print(f"\n{'='*80}")
        print(f"[{i}/{len(companies)}] {company['name']}")
        print(f"{'='*80}")
        
        result = parse_sga_unified(
            corp_name=company['name'],
            rcept_no=company['rcept'],
            cache_dir=cache_dir
        )
        
        results.append(result)
    
    # 요약
    print(f"\n\n{'='*80}")
    print(f"배치 처리 요약")
    print(f"{'='*80}")
    
    success_count = sum(1 for r in results if r['success'])
    a_grade_count = sum(1 for r in results if r.get('grade') == 'A')
    
    print(f"\n총 처리: {len(results)}개")
    print(f"성공: {success_count}개 ({success_count/len(results)*100:.1f}%)")
    print(f"A등급: {a_grade_count}개 ({a_grade_count/len(results)*100:.1f}%)")
    
    # Layer별 성공률
    layer_counts = {}
    
    for r in results:
        layer = r.get('layer', 4)
        
        if layer not in layer_counts:
            layer_counts[layer] = 0
        
        layer_counts[layer] += 1
    
    print(f"\nLayer별 성공:")
    for layer in sorted(layer_counts.keys()):
        count = layer_counts[layer]
        layer_name = {
            1: 'Robust 크롤러',
            2: 'XML Optimized',
            3: 'XML Hybrid',
            4: 'Manual 필요'
        }.get(layer, f'Layer {layer}')
        
        print(f"  Layer {layer} ({layer_name}): {count}개")
    
    # 상세 결과
    print(f"\n상세 결과:")
    print(f"{'-'*80}")
    print(f"{'기업':<15} {'금액':>12} {'등급':>6} {'방법':>15} {'Layer':>7}")
    print(f"{'-'*80}")
    
    for r in results:
        if r['success']:
            print(f"{r['corp_name']:<15} {r['total']:>12,.1f}억 {r.get('grade', 'N/A'):>6} {r.get('method', 'N/A'):>15} {r.get('layer', 0):>7}")
        else:
            print(f"{r['corp_name']:<15} {'실패':>12} {'N/A':>6} {'Manual':>15} {4:>7}")
    
    print(f"{'-'*80}")
    
    return results


def main():
    parser = argparse.ArgumentParser(
        description="통합 SG&A 파싱 파이프라인 (4-Layer)"
    )
    
    parser.add_argument(
        '--corp',
        type=str,
        help='기업명'
    )
    
    parser.add_argument(
        '--rcept',
        type=str,
        help='사업보고서 접수번호'
    )
    
    parser.add_argument(
        '--year',
        type=int,
        default=2024,
        help='사업연도 (기본: 2024)'
    )
    
    parser.add_argument(
        '--batch',
        action='store_true',
        help='배치 처리 모드'
    )
    
    parser.add_argument(
        '--file',
        type=str,
        default='data/corps_list.txt',
        help='배치 파일 (기업명,rcept_no 형식)'
    )
    
    parser.add_argument(
        '--no-save',
        action='store_true',
        help='YAML 저장 안 함'
    )
    
    parser.add_argument(
        '--cache-dir',
        type=str,
        default='/tmp/dart_unified_cache',
        help='캐시 디렉토리'
    )
    
    args = parser.parse_args()
    
    # 배치 처리
    if args.batch:
        batch_process(args.file, args.cache_dir)
    
    # 단일 처리
    elif args.corp and args.rcept:
        result = parse_sga_unified(
            corp_name=args.corp,
            rcept_no=args.rcept,
            year=args.year,
            save_yaml=not args.no_save,
            cache_dir=args.cache_dir
        )
        
        # 최종 결과 출력
        print(f"\n\n{'='*80}")
        print(f"최종 결과")
        print(f"{'='*80}")
        
        if result['success']:
            print(f"\n✅ 성공!")
            print(f"  기업: {result['corp_name']}")
            print(f"  금액: {result['total']:,.1f}억원")
            print(f"  등급: {result.get('grade', 'UNKNOWN')}")
            print(f"  방법: {result.get('method', 'N/A')}")
            print(f"  Layer: {result.get('layer', 0)}")
        else:
            print(f"\n❌ 실패")
            print(f"  수동 입력 필요")
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()

