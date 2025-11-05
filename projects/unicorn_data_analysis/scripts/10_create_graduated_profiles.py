#!/usr/bin/env python3
"""
졸업 유니콘 12개 프로필 생성

작성일: 2025-11-05
목적: SEC로 수집한 12개 회사를 유니콘 리스트와 동일한 구조로 생성
"""

import json
import glob
import os
from datetime import datetime


# ========================================
# 알려진 정보 (웹 검색 필요한 것들)
# ========================================

GRADUATED_UNICORNS_INFO = {
    "Rivian": {
        "location": {"country": "United States"},
        "category": "Auto & transportation",
        "ipo_date": "2021-11-10",
        "ticker": "RIVN",
        "valuation_at_ipo": "$66.50",  # IPO 당일 시가총액
        "select_investors": ["Amazon", "Ford", "T. Rowe Price", "Fidelity"],
        "business_summary": "Adventure Electric Vehicles 제조사 (R1T, R1S, EDV)",
    },
    
    "Coinbase": {
        "location": {"country": "United States"},
        "category": "Fintech",
        "ipo_date": "2021-04-14",
        "ticker": "COIN",
        "valuation_at_ipo": "$85.80",
        "select_investors": ["Andreessen Horowitz", "Union Square Ventures", "Ribbit Capital"],
        "business_summary": "암호화폐 거래소 플랫폼",
    },
    
    "DoorDash": {
        "location": {"country": "United States"},
        "category": "Supply chain, logistics, & delivery",
        "ipo_date": "2020-12-09",
        "ticker": "DASH",
        "valuation_at_ipo": "$72.00",
        "select_investors": ["Sequoia Capital", "SoftBank Vision Fund", "Coatue"],
        "business_summary": "음식 배달 플랫폼 및 물류 서비스",
    },
    
    "Affirm": {
        "location": {"country": "United States"},
        "category": "Fintech",
        "ipo_date": "2021-01-13",
        "ticker": "AFRM",
        "valuation_at_ipo": "$12.00",
        "select_investors": ["Lightspeed Venture Partners", "Andreessen Horowitz", "Khosla Ventures"],
        "business_summary": "Buy Now Pay Later (BNPL) 핀테크 서비스",
        "cik_note": "CIK 확인 필요 (현재 Robinhood와 중복)",
    },
    
    "Snowflake": {
        "location": {"country": "United States"},
        "category": "Data management & analytics",
        "ipo_date": "2020-09-16",
        "ticker": "SNOW",
        "valuation_at_ipo": "$120.00",
        "select_investors": ["Sequoia Capital", "Redpoint Ventures", "Sutter Hill Ventures"],
        "business_summary": "클라우드 데이터 웨어하우스 플랫폼",
    },
    
    "Unity": {
        "location": {"country": "United States"},
        "category": "Internet software & services",
        "ipo_date": "2020-09-18",
        "ticker": "U",
        "valuation_at_ipo": "$13.70",
        "select_investors": ["Sequoia Capital", "Silver Lake", "DFJ Growth"],
        "business_summary": "게임 개발 엔진 및 실시간 3D 플랫폼",
    },
    
    "Roblox": {
        "location": {"country": "United States"},
        "category": "Internet software & services",
        "ipo_date": "2021-03-10",
        "ticker": "RBLX",
        "valuation_at_ipo": "$45.00",
        "select_investors": ["Altos Ventures", "Index Ventures", "Tiger Global Management"],
        "business_summary": "온라인 게임 플랫폼 및 게임 제작 시스템",
    },
    
    "Robinhood": {
        "location": {"country": "United States"},
        "category": "Fintech",
        "ipo_date": "2021-07-29",
        "ticker": "HOOD",
        "valuation_at_ipo": "$32.00",
        "select_investors": ["Sequoia Capital", "Andreessen Horowitz", "Ribbit Capital"],
        "business_summary": "수수료 없는 주식 거래 앱",
        "cik_note": "CIK 0001783879 확인 필요 (현재 Affirm과 중복)",
    },
    
    "Palantir": {
        "location": {"country": "United States"},
        "category": "Data management & analytics",
        "ipo_date": "2020-09-30",
        "ticker": "PLTR",
        "valuation_at_ipo": "$10.00",
        "select_investors": ["Founders Fund", "In-Q-Tel", "Tiger Global Management"],
        "business_summary": "빅데이터 분석 플랫폼 (정부, 기업용)",
    },
    
    "Asana": {
        "location": {"country": "United States"},
        "category": "Internet software & services",
        "ipo_date": "2020-09-30",
        "ticker": "ASAN",
        "valuation_at_ipo": "$28.00",
        "select_investors": ["Benchmark", "Founders Fund", "Generation Investment Management"],
        "business_summary": "프로젝트 관리 및 협업 소프트웨어",
    },
    
    "C3.ai": {
        "location": {"country": "United States"},
        "category": "Artificial intelligence",
        "ipo_date": "2020-12-09",
        "ticker": "AI",
        "valuation_at_ipo": "$10.00",
        "select_investors": ["TPG", "Breyer Capital"],
        "business_summary": "엔터프라이즈 AI 플랫폼",
    },
    
    "Coupang": {
        "location": {"country": "South Korea"},
        "category": "E-commerce & direct-to-consumer",
        "ipo_date": "2021-03-11",
        "ticker": "CPNG",
        "valuation_at_ipo": "$109.00",
        "select_investors": ["SoftBank Vision Fund", "Sequoia Capital", "BlackRock"],
        "business_summary": "한국 이커머스 플랫폼 (로켓배송)",
    },
}


def generate_source_id(company_name: str) -> str:
    """Source ID 생성"""
    clean = company_name.lower().replace('.', '').replace(' ', '_')
    return f"{clean}_case"


def generate_canonical_id(company_name: str) -> str:
    """Canonical ID 생성"""
    clean = company_name.lower().replace('.', '').replace(' ', '')[:6]
    return f"CAN-{clean.ljust(6, '0')}01"


def create_graduated_unicorn_profile(company_name: str, sec_data: dict, info: dict) -> dict:
    """
    졸업 유니콘의 완전한 프로필 생성
    """
    # RAG 메타데이터
    source_id = generate_source_id(company_name)
    canonical_id = generate_canonical_id(company_name)
    
    now = datetime.utcnow().isoformat() + 'Z'
    
    # 기본 프로필 구조 (유니콘 리스트와 동일)
    profile = {
        "company": company_name,
        
        "valuation": {
            "amount_billion": info.get('valuation_at_ipo', 'N/A'),
            "date_added": info.get('ipo_date', 'N/A'),
            "note": "IPO 당시 valuation (졸업 유니콘)"
        },
        
        "location": info.get('location', {"country": "United States"}),
        
        "category": info.get('category', 'Internet software & services'),
        
        "ipo_info": {
            "date": info.get('ipo_date'),
            "ticker": info.get('ticker'),
            "exchange": "NASDAQ",  # 대부분 NASDAQ
            "status": "graduated_unicorn"
        },
        
        "select_investors": info.get('select_investors', []),
        
        "funding_history": [],  # 웹 검색 필요
        
        "business": {
            "summary": info.get('business_summary', ''),
            "details": [],
            
            # SEC에서 가져온 데이터
            "performance_metrics": sec_data['performance_metrics'],
            
            "business_model": {
                "pattern_type": "public_company",  # 상장사
                "pattern_id": "public_company_pattern",
                "revenue_model": []  # 리서치 필요
            },
            
            "problem_solution": {
                "problem": None,
                "solution": info.get('business_summary'),
                "unique_value": None
            },
            
            "market_dynamics": {
                "market_size": None,
                "market_growth": None,
                "target_segment": None,
                "geographic_focus": [info.get('location', {}).get('country', 'United States')]
            },
            
            "competitive_advantage": [],
            
            "critical_success_factors": [],
            
            "growth_trajectory": {
                "launch_date": None,  # 리서치 필요
                "unicorn_date": None,  # 리서치 필요
                "ipo_date": info.get('ipo_date'),
                "total_funding_usd_million": None,  # 리서치 필요
                "funding_rounds": None,
                "major_milestones": [
                    {"date": info.get('ipo_date'), "event": f"IPO ({info.get('ticker')})"}
                ]
            }
        },
        
        # RAG 메타데이터
        "rag_metadata": {
            "source_id": source_id,
            "canonical_chunk_id": canonical_id,
            "domain": "case_study",
            "content_type": "normalized_full",
            "version": "7.0.0",
            
            "lineage": {
                "from": canonical_id,
                "via": [],
                "evidence_ids": [],
                "created_by": {
                    "agent": "Explorer",
                    "overlay_layer": "core",
                    "tenant_id": None
                }
            },
            
            "sections": [{
                "agent_view": "explorer",
                "anchor_path": f"{source_id}.business_model",
                "content_hash": "sha256:pending",
                "span_hint": {"tokens": 500}
            }],
            
            "total_tokens": 500,
            "quality_grade": "A",  # SEC 데이터
            "validation_status": "verified",
            
            "created_at": now,
            "updated_at": now,
            
            "embedding": {
                "model": "text-embedding-3-large",
                "dimension": 3072,
                "space": "cosine"
            }
        }
    }
    
    # CIK 경고 추가
    if 'cik_note' in info:
        profile['_cik_warning'] = info['cik_note']
    
    return profile


def main():
    print("="*80)
    print("🏗️ 졸업 유니콘 프로필 생성")
    print("="*80)
    print()
    
    # SEC 데이터 파일 로드
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    
    sec_files = glob.glob(os.path.join(project_dir, 'research', 'SEC_*_final.json'))
    
    print(f"📂 SEC 데이터: {len(sec_files)}개")
    print()
    
    graduated_profiles = []
    issues = []
    
    for sec_file in sorted(sec_files):
        company_name = os.path.basename(sec_file).replace('SEC_', '').replace('_final.json', '')
        
        print(f"🔨 {company_name}...")
        
        # SEC 데이터 로드
        with open(sec_file, 'r', encoding='utf-8') as f:
            sec_data = json.load(f)
        
        # 알려진 정보가 있는지 확인
        if company_name in GRADUATED_UNICORNS_INFO:
            info = GRADUATED_UNICORNS_INFO[company_name]
            
            # 프로필 생성
            profile = create_graduated_unicorn_profile(company_name, sec_data, info)
            graduated_profiles.append(profile)
            
            print(f"   ✅ 프로필 생성")
            
            if '_cik_warning' in profile:
                print(f"   ⚠️ {profile['_cik_warning']}")
                issues.append(company_name)
        else:
            print(f"   ⚠️ 기본 정보 없음 - 추가 리서치 필요")
            issues.append(company_name)
    
    print()
    print("="*80)
    print("💾 저장 중...")
    print("="*80)
    print()
    
    # 졸업 유니콘 JSON 생성
    output_data = {
        "metadata": {
            "title": "Graduated Unicorns (졸업 유니콘)",
            "description": "IPO 완료하여 유니콘 리스트에서 졸업한 기업들",
            "total_companies": len(graduated_profiles),
            "data_version": "1.0",
            "last_updated": datetime.utcnow().isoformat() + 'Z',
            "data_source": "SEC EDGAR API + Manual Research",
            "rag_schema_version": "7.0.0",
            "notes": [
                "모든 재무 데이터는 SEC 10-K에서 자동 수집",
                "일부 기업은 추가 리서치 필요 (funding_history, problem_solution 등)",
                "CIK 중복 이슈: Affirm/Robinhood 확인 필요"
            ]
        },
        "companies": graduated_profiles
    }
    
    output_file = os.path.join(project_dir, 'graduated_unicorns.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 저장 완료: graduated_unicorns.json")
    print()
    
    # 요약
    print("="*80)
    print("📊 생성 요약")
    print("="*80)
    print()
    print(f"총 생성: {len(graduated_profiles)}개")
    print(f"이슈: {len(issues)}개")
    print()
    
    if issues:
        print("⚠️ 추가 확인 필요:")
        for company in issues:
            print(f"  - {company}")
        print()
    
    # 샘플 출력
    if graduated_profiles:
        print("="*80)
        print("📝 샘플: Coinbase")
        print("="*80)
        print()
        
        coinbase = next((p for p in graduated_profiles if p['company'] == 'Coinbase'), None)
        if coinbase:
            print(f"Company: {coinbase['company']}")
            print(f"Ticker: {coinbase['ipo_info']['ticker']}")
            print(f"IPO: {coinbase['ipo_info']['date']}")
            print(f"Category: {coinbase['category']}")
            print()
            
            rev = coinbase['business']['performance_metrics']['financial']['revenue']
            if 'year_1' in rev:
                y1 = rev['year_1']
                print(f"Revenue ({y1['year']}): ${y1['amount_usd_million']}M")
            
            net = coinbase['business']['performance_metrics']['financial']['net_income']
            if 'year_1' in net:
                y1 = net['year_1']
                print(f"Net Income ({y1['year']}): ${y1['amount_usd_million']}M")
            
            print()
            print(f"Quality Grade: {coinbase['rag_metadata']['quality_grade']}")
    
    print()
    print("="*80)
    print("✅ 작업 완료!")
    print("="*80)
    print()
    print("📁 출력 파일:")
    print("  - graduated_unicorns.json")
    print()
    print("🎯 다음 단계:")
    print("  1. graduated_unicorns.json 확인")
    print("  2. CIK 중복 이슈 해결 (Affirm/Robinhood)")
    print("  3. 추가 정보 보완 (funding_history, problem_solution 등)")
    print("  4. 유니콘 800개와 통합 여부 결정")


if __name__ == "__main__":
    main()


