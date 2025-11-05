#!/usr/bin/env python3
"""
유니콘 데이터에 RAG Canonical Index 메타데이터 자동 추가

작성일: 2025-11-04
목적: unicorn_companies_structured.json을 UMIS RAG 호환 형식으로 변환
"""

import json
import hashlib
from datetime import datetime
from typing import Dict, List, Any
import re


# ========================================
# Category → Pattern Type 매핑
# ========================================

CATEGORY_TO_PATTERN = {
    # Fintech
    "Fintech": "fintech_platform",
    
    # E-commerce & Marketplace
    "E-commerce & direct-to-consumer": "marketplace",
    "Supply chain, logistics, & delivery": "marketplace",
    
    # SaaS & Software
    "Internet software & services": "saas_platform",
    "Data management & analytics": "saas_tool",
    "Cybersecurity": "saas_security",
    
    # Platform Models
    "Artificial intelligence": "ai_platform",
    "Mobile & telecommunications": "platform",
    
    # Subscription/Service
    "Health": "healthcare_service",
    "Edtech": "education_service",
    "Travel": "travel_service",
    
    # Hardware/Manufacturing
    "Auto & transportation": "hardware_mobility",
    "Hardware": "hardware",
    "Consumer & retail": "retail",
    
    # Other
    "Other": "other",
}


# ========================================
# Helper Functions
# ========================================

def generate_canonical_id(company_name: str) -> str:
    """
    회사명으로 Canonical ID 생성
    
    Format: CAN-{hash8}
    Example: CAN-byteda01
    """
    # 회사명을 소문자 알파벳+숫자만 남김
    clean_name = re.sub(r'[^a-z0-9]', '', company_name.lower())
    
    # 앞 6자 + 01 (버전)
    if len(clean_name) >= 6:
        base = clean_name[:6]
    else:
        base = clean_name.ljust(6, '0')
    
    return f"CAN-{base}01"


def generate_source_id(company_name: str) -> str:
    """
    Source ID 생성
    
    Format: {company_name}_case
    Example: bytedance_case
    """
    clean_name = re.sub(r'[^a-z0-9]', '_', company_name.lower())
    clean_name = re.sub(r'_+', '_', clean_name)  # 연속 언더스코어 제거
    clean_name = clean_name.strip('_')
    
    return f"{clean_name}_case"


def generate_content_hash(content: str) -> str:
    """
    컨텐츠 SHA-256 해시 생성
    
    Returns: sha256:{hash}
    """
    hash_obj = hashlib.sha256(content.encode('utf-8'))
    return f"sha256:{hash_obj.hexdigest()}"


def estimate_tokens(text: str) -> int:
    """
    토큰 수 추정 (간단한 방식: 단어 수 * 1.3)
    """
    words = len(text.split())
    return int(words * 1.3)


def get_pattern_type(category: str) -> str:
    """
    카테고리로 패턴 타입 추론
    """
    return CATEGORY_TO_PATTERN.get(category, "platform")


def estimate_launch_year(unicorn_date: str, company_name: str) -> str:
    """
    유니콘 등재일로 창업 연도 추정
    
    Strategy: 유니콘 - 7년 (평균)
    """
    try:
        # "2017.4.7" → 2017
        year = int(unicorn_date.split('.')[0])
        launch_year = year - 7  # 평균 7년
        
        # 2000년 이전은 2000으로 설정
        if launch_year < 2000:
            launch_year = 2000
            
        return str(launch_year)
    except:
        return "2010"  # 기본값


def calculate_funding_total(funding_history: List[Dict]) -> float:
    """
    총 펀딩 금액 계산 (백만 달러 단위)
    """
    total = 0.0
    for round in funding_history:
        amount_str = round.get('amount', '')
        if 'M' in amount_str:
            value = float(amount_str.replace('M', '').replace(',', ''))
            total += value
        elif 'B' in amount_str:
            value = float(amount_str.replace('B', '').replace(',', ''))
            total += value * 1000
    
    return total


def extract_funding_rounds(funding_history: List[Dict]) -> List[str]:
    """
    펀딩 라운드 날짜 추출
    """
    dates = []
    for round in funding_history:
        date = round.get('date', '')
        if date:
            dates.append(date)
    return dates


# ========================================
# Main Transformation Function
# ========================================

def add_rag_metadata(company: Dict[str, Any]) -> Dict[str, Any]:
    """
    개별 회사 데이터에 RAG 메타데이터 추가
    """
    company_name = company.get('company', 'unknown')
    category = company.get('category', 'Other')
    
    # === 1. RAG Core Metadata ===
    canonical_id = generate_canonical_id(company_name)
    source_id = generate_source_id(company_name)
    
    # === 2. Content for hashing ===
    content_parts = [
        company_name,
        company.get('business', {}).get('summary', ''),
        category,
        str(company.get('valuation', {})),
    ]
    content_text = ' '.join(filter(None, content_parts))
    content_hash = generate_content_hash(content_text)
    
    # === 3. Timestamps ===
    now = datetime.utcnow().isoformat() + 'Z'
    
    # === 4. Pattern Type ===
    pattern_type = get_pattern_type(category)
    
    # === 5. Growth Info ===
    unicorn_date = company.get('valuation', {}).get('date_added', '2020.1.1')
    launch_year = estimate_launch_year(unicorn_date, company_name)
    
    # === 6. Funding Info ===
    funding_history = company.get('funding_history', [])
    total_funding = calculate_funding_total(funding_history)
    funding_rounds = extract_funding_rounds(funding_history)
    
    # === 7. Token Count ===
    total_tokens = estimate_tokens(content_text)
    
    # === RAG Metadata Structure ===
    rag_metadata = {
        # Core Identity
        "source_id": source_id,
        "canonical_chunk_id": canonical_id,
        "domain": "case_study",
        "content_type": "normalized_full",
        "version": "7.0.0",
        
        # Lineage
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
        
        # Content Sections
        "sections": [
            {
                "agent_view": "explorer",
                "anchor_path": f"{source_id}.business_model",
                "content_hash": content_hash,
                "span_hint": {
                    "tokens": total_tokens
                }
            }
        ],
        
        # Metadata
        "total_tokens": total_tokens,
        "quality_grade": "B",  # 기본값, 추후 검증 필요
        "validation_status": "pending",
        
        # Timestamps
        "created_at": now,
        "updated_at": now,
        
        # Embedding (선택)
        "embedding": {
            "model": "text-embedding-3-large",
            "dimension": 3072,
            "space": "cosine"
        }
    }
    
    # === Business Model Enhancement ===
    business_enhancement = {
        "business_model": {
            "pattern_type": pattern_type,
            "pattern_id": f"{pattern_type}_pattern",
            "revenue_model": []  # 리서치 필요
        },
        
        "problem_solution": {
            "problem": None,  # 리서치 필요
            "solution": company.get('business', {}).get('summary', ''),
            "unique_value": None  # 리서치 필요
        },
        
        "performance_metrics": {
            "_note": "확인 가능한 재무/운영 지표만 기재 (상장사, IR 자료 등)",
            
            "financial": {
                "revenue": {
                    "year_1": {"year": None, "amount_usd_million": None, "source": None},
                    "year_2": {"year": None, "amount_usd_million": None, "source": None},
                    "year_3": {"year": None, "amount_usd_million": None, "source": None}
                },
                "operating_profit": {
                    "year_1": {"year": None, "amount_usd_million": None, "source": None},
                    "year_2": {"year": None, "amount_usd_million": None, "source": None},
                    "year_3": {"year": None, "amount_usd_million": None, "source": None}
                },
                "gross_margin": None,
                "ebitda": None,
                "_note": "최근 3개년 데이터 우선"
            },
            
            "operational": {
                "users": None,
                "mau": None,
                "dau": None,
                "transactions": None,
                "gmv_usd_million": None,
                "arr_usd_million": None,
                "subscribers": None,
                "_note": "확인 가능한 지표만 선택적으로 기재"
            },
            
            "unit_economics": {
                "arpu_usd": None,
                "cac_usd": None,
                "ltv_usd": None,
                "ltv_cac_ratio": None,
                "churn_rate_percent": None,
                "payback_period_months": None,
                "_note": "공개된 경우에만 기재 (상장사, 인터뷰 등)"
            }
        },
        
        "market_dynamics": {
            "market_size": None,
            "market_growth": None,
            "target_segment": None,
            "geographic_focus": [company.get('location', {}).get('country', 'Unknown')]
        },
        
        "competitive_advantage": [],  # 리서치 필요
        
        "critical_success_factors": [],  # 리서치 필요
        
        "growth_trajectory": {
            "launch_date": launch_year,
            "unicorn_date": unicorn_date,
            "total_funding_usd_million": total_funding,
            "funding_rounds": len(funding_rounds),
            "major_milestones": []  # 리서치 필요
        }
    }
    
    # === 기존 데이터에 추가 ===
    enhanced_company = company.copy()
    enhanced_company['rag_metadata'] = rag_metadata
    
    # business 필드 확장
    if 'business' in enhanced_company:
        enhanced_company['business'].update(business_enhancement)
    else:
        enhanced_company['business'] = {
            'summary': '',
            'details': [],
            **business_enhancement
        }
    
    return enhanced_company


# ========================================
# Main Execution
# ========================================

def main():
    """
    메인 실행 함수
    """
    import os
    
    # 파일 경로
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    
    input_file = os.path.join(project_dir, 'unicorn_companies_structured.json')
    output_file = os.path.join(project_dir, 'unicorn_companies_rag_enhanced.json')
    
    print("="*80)
    print("🦄 유니콘 데이터 RAG 메타데이터 자동 추가")
    print("="*80)
    print()
    
    # 데이터 로드
    print(f"📂 입력 파일: {os.path.basename(input_file)}")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    companies = data.get('companies', [])
    print(f"📊 총 기업 수: {len(companies)}개")
    print()
    
    # 변환 실행
    print("🔄 RAG 메타데이터 추가 중...")
    enhanced_companies = []
    
    for i, company in enumerate(companies, 1):
        enhanced = add_rag_metadata(company)
        enhanced_companies.append(enhanced)
        
        if i % 100 == 0:
            print(f"   진행: {i}/{len(companies)} ({i/len(companies)*100:.1f}%)")
    
    print(f"✅ 변환 완료: {len(enhanced_companies)}개")
    print()
    
    # 결과 저장
    output_data = {
        "metadata": {
            "total_companies": len(enhanced_companies),
            "data_version": "3.0",  # RAG 호환 버전
            "last_updated": datetime.utcnow().isoformat() + 'Z',
            "rag_schema_version": "7.0.0",
            "structure": {
                "rag_metadata": "UMIS Canonical Index 호환 메타데이터",
                "business": "확장된 비즈니스 정보 (일부 리서치 필요)",
                "valuation": "밸류에이션 정보",
                "funding_history": "펀딩 히스토리",
                "location": "위치 정보"
            },
            "notes": [
                "RAG 메타데이터는 자동 생성됨",
                "business_model, problem_solution 등은 일부 리서치 필요",
                "unit_economics, key_metrics는 대부분 비공개 정보"
            ]
        },
        "companies": enhanced_companies
    }
    
    print(f"💾 저장 중: {os.path.basename(output_file)}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print("✅ 저장 완료!")
    print()
    
    # 통계 출력
    print("="*80)
    print("📊 변환 통계")
    print("="*80)
    print()
    
    # Pattern Type 분포
    pattern_counts = {}
    for company in enhanced_companies:
        pattern = company['business']['business_model']['pattern_type']
        pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
    
    print("Pattern Type 분포:")
    for pattern, count in sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {pattern}: {count}개 ({count/len(enhanced_companies)*100:.1f}%)")
    
    print()
    
    # 샘플 출력
    print("="*80)
    print("📝 샘플 출력 (첫 번째 기업)")
    print("="*80)
    print()
    
    sample = enhanced_companies[0]
    print(f"회사: {sample['company']}")
    print(f"Canonical ID: {sample['rag_metadata']['canonical_chunk_id']}")
    print(f"Source ID: {sample['rag_metadata']['source_id']}")
    print(f"Pattern Type: {sample['business']['business_model']['pattern_type']}")
    print(f"Total Tokens: {sample['rag_metadata']['total_tokens']}")
    print()
    
    print("="*80)
    print("✅ 작업 완료!")
    print("="*80)
    print()
    print(f"출력 파일: {output_file}")
    print()
    print("다음 단계:")
    print("  1. unicorn_companies_rag_enhanced.json 확인")
    print("  2. 파일럿 10개 기업 선정")
    print("  3. 리서치를 통한 상세 정보 보완")


if __name__ == "__main__":
    main()

