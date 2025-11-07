#!/usr/bin/env python3
"""
SEC 수집 데이터를 메인 JSON에 자동 반영

작성일: 2025-11-05
목적: SEC_*_final.json 데이터를 unicorn_companies_rag_enhanced.json에 업데이트
"""

import json
import os
import glob
from datetime import datetime


def update_company_performance(main_data: dict, sec_data: dict) -> bool:
    """
    SEC 데이터로 메인 JSON의 Performance Metrics 업데이트
    """
    company_name = sec_data['company']
    
    # 해당 기업 찾기
    company = None
    for comp in main_data['companies']:
        if comp['company'] == company_name:
            company = comp
            break
    
    if not company:
        print(f"  ⚠️ {company_name}를 메인 JSON에서 찾을 수 없습니다.")
        return False
    
    # Performance Metrics 업데이트
    sec_metrics = sec_data['performance_metrics']['financial']
    
    company['business']['performance_metrics']['financial'] = {
        'revenue': sec_metrics.get('revenue', {}),
        'operating_profit': sec_metrics.get('operating_profit', {}),
        'gross_profit': sec_metrics.get('gross_profit', {}),
        'net_income': sec_metrics.get('net_income', {}),
        'gross_margin': sec_metrics.get('gross_margin'),
        'operating_margin': sec_metrics.get('operating_margin'),
        'net_margin': sec_metrics.get('net_margin'),
        'ebitda': sec_metrics.get('ebitda'),
        '_note': '최근 3개년 데이터 우선'
    }
    
    # Cash 업데이트
    if sec_metrics.get('cash_and_equivalents'):
        company['business']['performance_metrics']['financial']['cash_and_equivalents'] = sec_metrics['cash_and_equivalents']
    
    # RAG 메타데이터 업데이트
    company['rag_metadata']['updated_at'] = datetime.utcnow().isoformat() + 'Z'
    company['rag_metadata']['quality_grade'] = 'A'  # SEC 데이터는 A등급
    company['rag_metadata']['validation_status'] = 'verified'
    
    return True


def main():
    print("="*80)
    print("📊 SEC 데이터 → 메인 JSON 자동 반영")
    print("="*80)
    print()
    
    # 경로 설정
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    
    # 메인 JSON 로드
    main_file = os.path.join(project_dir, 'unicorn_companies_rag_enhanced.json')
    print(f"📂 메인 파일: unicorn_companies_rag_enhanced.json")
    
    with open(main_file, 'r', encoding='utf-8') as f:
        main_data = json.load(f)
    
    print(f"   총 기업: {len(main_data['companies'])}개")
    print()
    
    # SEC 데이터 파일 찾기
    sec_files = glob.glob(os.path.join(project_dir, 'research', 'SEC_*_final.json'))
    print(f"🔍 SEC 데이터 파일: {len(sec_files)}개")
    print()
    
    # 각 SEC 파일 처리
    updated_count = 0
    failed_count = 0
    
    for sec_file in sorted(sec_files):
        company_name = os.path.basename(sec_file).replace('SEC_', '').replace('_final.json', '')
        
        print(f"📊 {company_name}...")
        
        # SEC 데이터 로드
        with open(sec_file, 'r', encoding='utf-8') as f:
            sec_data = json.load(f)
        
        # 업데이트
        success = update_company_performance(main_data, sec_data)
        
        if success:
            updated_count += 1
            print(f"   ✅ 업데이트 완료")
            
            # 간단히 확인
            for comp in main_data['companies']:
                if comp['company'] == sec_data['company']:
                    rev = comp['business']['performance_metrics']['financial']['revenue']
                    if 'year_1' in rev:
                        y1 = rev['year_1']
                        print(f"   → {y1['year']}: ${y1['amount_usd_million']}M")
                    break
        else:
            failed_count += 1
    
    print()
    print("="*80)
    print("💾 메인 JSON 저장 중...")
    print("="*80)
    
    # 백업 생성
    backup_file = os.path.join(
        project_dir,
        f"unicorn_companies_rag_enhanced_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    
    with open(main_file, 'r', encoding='utf-8') as f:
        backup_data = f.read()
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(backup_data)
    
    print(f"✅ 백업 생성: {os.path.basename(backup_file)}")
    
    # 메인 파일 업데이트
    with open(main_file, 'w', encoding='utf-8') as f:
        json.dump(main_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 메인 파일 업데이트 완료")
    print()
    
    # 요약
    print("="*80)
    print("📊 업데이트 요약")
    print("="*80)
    print()
    print(f"  총 처리: {len(sec_files)}개")
    print(f"  성공: {updated_count}개")
    print(f"  실패: {failed_count}개")
    print()
    
    # 업데이트된 기업 리스트
    print("✅ 업데이트된 기업:")
    updated_companies = []
    for comp in main_data['companies']:
        if comp['rag_metadata'].get('quality_grade') == 'A' and comp['rag_metadata'].get('validation_status') == 'verified':
            rev = comp['business']['performance_metrics']['financial']['revenue']
            if rev and 'year_1' in rev:
                y1 = rev['year_1']
                updated_companies.append({
                    'name': comp['company'],
                    'year': y1['year'],
                    'revenue': y1['amount_usd_million']
                })
    
    for i, comp in enumerate(sorted(updated_companies, key=lambda x: x['revenue'], reverse=True), 1):
        print(f"  {i:2d}. {comp['name']:15s} - {comp['year']}: ${comp['revenue']:>8,.0f}M")
    
    print()
    print("="*80)
    print("✅ 작업 완료!")
    print("="*80)
    print()
    print("📁 파일 위치:")
    print(f"  - 메인: unicorn_companies_rag_enhanced.json (업데이트됨)")
    print(f"  - 백업: {os.path.basename(backup_file)}")
    print()
    print("🎯 다음 단계:")
    print("  1. 메인 JSON 확인")
    print("  2. 실패 5개 CIK 재확인")
    print("  3. 파일럿 나머지 8개 진행")


if __name__ == "__main__":
    main()



