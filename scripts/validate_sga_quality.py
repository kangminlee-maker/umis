#!/usr/bin/env python3
"""
SG&A 파싱 품질 검증 시스템 v2.0

3단계 검증:
1. 계정 타입 체크 (SG&A vs 매출원가 vs 금융 등)
2. 파싱 합계 vs DART 총액 비교
3. 미상 잡비용 비율 → 신뢰도 평가

품질 기준 (v2.0):
- 오차 ±5% 이내: A등급 (신뢰도 95%, Production Ready)
- 오차 ±10% 이내: B등급 (신뢰도 80%, 참고용)
- 오차 ±20% 이내: C등급 (신뢰도 60%, 재검토)
- 오차 >20%: D등급 (신뢰도 40%, 폐기)

미상 비용 기준:
- <10%: 양호
- 10-20%: 주의
- >20%: 신뢰도 낮음 (D등급)
"""

import yaml
from pathlib import Path
from typing import Dict, Tuple
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from umis_rag.utils.dart_api import DARTClient


# 계정 타입 분류
ACCOUNT_TYPES = {
    'sga': {
        'keywords': [
            '급여', '퇴직급여', '복리후생', '여비', '접대비', '회의비', '통신비',
            '임차료', '감가상각비', '상각비', '수선비', '소모품비', '교육훈련비',
            '지급수수료', '수수료', '세금과공과', '광고', '판촉', '운반비',
            '포장비', '연구개발비', '경상연구개발비', '서비스',
        ],
        'name': 'SG&A (판매비와관리비)'
    },
    
    'cogs': {
        'keywords': [
            '매입', '원재료', '재료비', '저장품', '재공품', '제품의 변동',
            '외주가공비', '외주용역비', '제조', '생산',
        ],
        'name': '매출원가 (COGS)'
    },
    
    'financial': {
        'keywords': [
            '금융수익', '금융비용', '이자수익', '이자비용', '배당금',
            '외환', '파생상품',
        ],
        'name': '금융손익'
    },
    
    'investment': {
        'keywords': [
            '투자주식', '관계기업', '공동기업', '종속기업',
            '평가', '손상', '처분',
        ],
        'name': '투자 관련'
    },
    
    'summary': {
        'keywords': [
            '합계', '총계', '소계', '총액', 'Total',
            '순이익', '영업이익', '세전', '법인세',
        ],
        'name': '합계/요약 항목'
    }
}


def classify_account_type(item_name: str) -> str:
    """계정 항목 타입 분류"""
    
    item_lower = item_name.lower()
    
    # 우선순위: summary > cogs > financial > investment > sga
    for type_id in ['summary', 'cogs', 'financial', 'investment']:
        for keyword in ACCOUNT_TYPES[type_id]['keywords']:
            if keyword in item_name:
                return type_id
    
    # 기본: SGA
    return 'sga'


def validate_sga_parsing(
    company_name: str,
    parsed_sga: Dict[str, float],
    dart_sga_total: float,
    unit: str = '백만원'
) -> Dict:
    """
    SG&A 파싱 품질 검증
    
    Args:
        company_name: 회사명
        parsed_sga: 파싱된 SG&A {항목명: 금액}
        dart_sga_total: DART 재무제표 SG&A 총액
        unit: 단위
    
    Returns:
        {
            'quality_grade': 'A/B/C',
            'confidence': 0.95,
            'issues': [...],
            'recommendations': [...],
            'clean_sga': {...},
            'removed_items': {...},
            'unknown_amount': float
        }
    """
    
    print(f"\n{'='*70}")
    print(f"📋 {company_name} 품질 검증")
    print(f"{'='*70}")
    
    # Step 1: 계정 타입 분류
    print(f"\n[Step 1] 계정 타입 분류")
    print("-"*70)
    
    categorized = {
        'sga': {},
        'cogs': {},
        'financial': {},
        'investment': {},
        'summary': {}
    }
    
    for item, amount in parsed_sga.items():
        type_id = classify_account_type(item)
        categorized[type_id][item] = amount
    
    print(f"  SG&A: {len(categorized['sga'])}개")
    print(f"  매출원가: {len(categorized['cogs'])}개")
    print(f"  금융: {len(categorized['financial'])}개")
    print(f"  투자: {len(categorized['investment'])}개")
    print(f"  합계: {len(categorized['summary'])}개")
    
    if categorized['cogs']:
        print(f"\n  ⚠️ 매출원가 항목 발견:")
        for item in list(categorized['cogs'].keys())[:3]:
            print(f"    - {item}")
    
    if categorized['summary']:
        print(f"\n  ⚠️ 합계 항목 발견:")
        for item in list(categorized['summary'].keys())[:3]:
            print(f"    - {item}")
    
    # Step 2: SG&A만 추출 및 합계 비교
    print(f"\n[Step 2] 합계 검증")
    print("-"*70)
    
    clean_sga = categorized['sga']
    
    # 단위 변환 (억원)
    if unit == '백만원':
        parsed_total = sum(clean_sga.values()) / 100
    elif unit == '천원':
        parsed_total = sum(clean_sga.values()) / 100_000
    elif unit == '원':
        parsed_total = sum(clean_sga.values()) / 100_000_000
    else:
        parsed_total = sum(clean_sga.values())
    
    print(f"  DART SG&A 총액: {dart_sga_total:>12,.1f}억원")
    print(f"  파싱 SG&A 합계: {parsed_total:>12,.1f}억원")
    
    diff = parsed_total - dart_sga_total
    diff_ratio = diff / dart_sga_total if dart_sga_total > 0 else 0
    
    print(f"  차이:          {diff:>12,.1f}억원 ({diff_ratio:>6.1%})")
    
    # Step 3: 미상 비용 및 신뢰도 평가
    print(f"\n[Step 3] 신뢰도 평가")
    print("-"*70)
    
    issues = []
    recommendations = []
    
    # 오차 평가 (A/B/C/D)
    if abs(diff_ratio) <= 0.05:
        accuracy_grade = 'A'
        print(f"  ✅ 오차 {abs(diff_ratio):.1%} (±5% 이내) - Production Ready")
    elif abs(diff_ratio) <= 0.10:
        accuracy_grade = 'B'
        print(f"  ✅ 오차 {abs(diff_ratio):.1%} (±10% 이내) - 참고용")
    elif abs(diff_ratio) <= 0.20:
        accuracy_grade = 'C'
        print(f"  ⚠️ 오차 {abs(diff_ratio):.1%} (±20% 이내) - 재검토 필요")
        issues.append(f"오차 {abs(diff_ratio):.1%} (±20% 이내)")
    else:
        accuracy_grade = 'D'
        print(f"  ❌ 오차 {abs(diff_ratio):.1%} (>20%) - 폐기")
        issues.append(f"오차 {abs(diff_ratio):.1%} (>20%)")
        recommendations.append("다시 파싱 필요 (다른 섹션 시도)")
    
    # 미상 비용 계산
    if diff < 0:  # 파싱 < DART (빠진 항목 있음)
        unknown_amount = abs(diff)
        unknown_ratio = unknown_amount / dart_sga_total
        
        print(f"\n  ⚠️ 빠진 항목: {unknown_amount:,.1f}억원 ({unknown_ratio:.1%})")
        
        if unknown_ratio > 0.20:
            unknown_grade = 'D'
            print(f"  ❌ 미상 비용 {unknown_ratio:.1%} (>20%) - 폐기")
            issues.append(f"미상 비용 {unknown_ratio:.1%} (>20%)")
            recommendations.append("재파싱 필수 (LLM 검증 또는 다른 섹션 시도)")
        elif unknown_ratio > 0.10:
            unknown_grade = 'C'
            print(f"  ⚠️ 미상 비용 {unknown_ratio:.1%} (10-20%) - 재검토")
            recommendations.append("LLM 검증 권장")
        else:
            unknown_grade = 'A'
            print(f"  ✅ 미상 비용 {unknown_ratio:.1%} (<10%) - 양호")
            recommendations.append("미상 잡비용으로 표기 가능")
    
    elif diff > 0:  # 파싱 > DART (잘못된 항목 포함)
        unknown_amount = 0
        over_ratio = diff / dart_sga_total
        
        if over_ratio > 1.0:  # 100% 이상 과다
            unknown_grade = 'D'
            print(f"\n  ❌ 과다 파싱: {diff:,.1f}억원 ({diff_ratio:.1%}) - 폐기")
            print(f"  원인: 완전히 잘못된 섹션 파싱")
            issues.append(f"과다 파싱 {diff_ratio:.1%} (>100%)")
            recommendations.append("섹션 재선택 필수")
        elif over_ratio > 0.30:  # 30% 이상 과다
            unknown_grade = 'D'
            print(f"\n  ❌ 과다 파싱: {diff:,.1f}억원 ({diff_ratio:.1%}) - 폐기")
            print(f"  원인: 매출원가/금융/합계 항목 대량 포함 의심")
            issues.append(f"과다 파싱 {diff_ratio:.1%} (>30%)")
            recommendations.append("LLM 검증 후 재파싱")
        else:
            unknown_grade = 'C'
            print(f"\n  ⚠️ 과다 파싱: {diff:,.1f}억원 ({diff_ratio:.1%})")
            print(f"  원인: 일부 잘못된 항목 포함 가능")
            issues.append(f"과다 파싱 {diff_ratio:.1%}")
            recommendations.append("계정 타입 재분류 검토")
    
    else:  # 정확히 일치
        unknown_amount = 0
        unknown_grade = 'A'
        print(f"\n  ✅ 완벽 일치!")
    
    # 제거된 항목 집계
    removed_items = {}
    for type_id in ['cogs', 'financial', 'investment', 'summary']:
        removed_items.update(categorized[type_id])
    
    # 최종 등급 (더 낮은 등급 선택)
    grade_priority = {'D': 0, 'C': 1, 'B': 2, 'A': 3}
    
    final_grade = accuracy_grade if grade_priority[accuracy_grade] <= grade_priority[unknown_grade] else unknown_grade
    
    grade_info = {
        'A': (0.95, 'Production Ready'),
        'B': (0.80, '참고용'),
        'C': (0.60, '재검토 필요'),
        'D': (0.40, '폐기 (재파싱)')
    }
    
    quality_grade = final_grade
    confidence, status = grade_info[quality_grade]
    
    print(f"\n{'='*70}")
    print(f"최종 품질 등급: {quality_grade} (신뢰도: {confidence:.0%})")
    print(f"{'='*70}")
    
    if issues:
        print(f"\n⚠️ 발견된 이슈:")
        for issue in issues:
            print(f"  - {issue}")
    
    if recommendations:
        print(f"\n💡 권장사항:")
        for rec in recommendations:
            print(f"  - {rec}")
    
    return {
        'quality_grade': quality_grade,
        'confidence': confidence,
        'accuracy_grade': accuracy_grade,
        'unknown_grade': unknown_grade,
        'issues': issues,
        'recommendations': recommendations,
        'clean_sga': clean_sga,
        'removed_items': removed_items,
        'unknown_amount_billion': unknown_amount if 'unknown_amount' in locals() else 0,
        'unknown_ratio': unknown_ratio if 'unknown_ratio' in locals() else 0,
        'dart_total': dart_sga_total,
        'parsed_total': parsed_total,
        'difference': diff,
        'difference_ratio': diff_ratio
    }


def validate_all_companies():
    """전체 기업 검증"""
    
    print("="*70)
    print("전체 SG&A 파싱 품질 검증")
    print("="*70)
    
    from dotenv import load_dotenv
    import os
    load_dotenv()
    
    client = DARTClient(os.getenv('DART_API_KEY'))
    
    sga_files = list(Path('data/raw').glob('*_sga_complete.yaml'))
    
    results = []
    
    for filepath in sorted(sga_files):
        with open(filepath, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        company = data.get('company', filepath.stem)
        year = data.get('year', 2023)
        sga_items = data.get('sga_details_million', {})
        unit = data.get('unit', '백만원')
        
        # DART 총액 조회
        corp_code = client.get_corp_code(company)
        
        if not corp_code:
            print(f"\n⚠️ {company}: corp_code 없음")
            continue
        
        financials = client.get_financials(corp_code, year, fs_div='OFS')
        
        if not financials:
            print(f"\n⚠️ {company}: 재무제표 없음")
            continue
        
        # SG&A 총액 추출
        dart_sga = 0
        for item in financials:
            account = item.get('account_nm', '')
            if '판매비' in account or '관리비' in account:
                amount_str = item.get('thstrm_amount', '0')
                try:
                    dart_sga = float(amount_str.replace(',', '')) / 100_000_000  # 억원
                    break
                except:
                    pass
        
        if dart_sga == 0:
            print(f"\n⚠️ {company}: DART SG&A 총액 없음")
            continue
        
        # 검증
        validation = validate_sga_parsing(company, sga_items, dart_sga, unit)
        
        results.append({
            'company': company,
            **validation
        })
    
    # 전체 요약
    print(f"\n\n{'='*70}")
    print(f"전체 품질 요약")
    print(f"{'='*70}")
    
    print(f"\n{'회사':<15} {'등급':<6} {'신뢰도':<8} {'오차':<10} {'미상비용':<10}")
    print("-"*60)
    
    for r in results:
        print(f"{r['company']:<15} {r['quality_grade']:<6} {r['confidence']:<8.0%} {r['difference_ratio']:>8.1%} {r['unknown_ratio']:>8.1%}")
    
    # 등급별 집계
    grades = {}
    for r in results:
        grade = r['quality_grade']
        grades[grade] = grades.get(grade, 0) + 1
    
    print(f"\n등급별 분포:")
    for grade in ['A', 'B', 'C']:
        count = grades.get(grade, 0)
        if count > 0:
            print(f"  {grade}등급: {count}개")
    
    print(f"\n총 {len(results)}개 기업 검증 완료")
    
    return results


def main():
    results = validate_all_companies()
    
    # 결과 저장
    output = {
        'validation_date': '2025-11-13',
        'total_companies': len(results),
        'results': results
    }
    
    with open('data/raw/sga_quality_validation.yaml', 'w', encoding='utf-8') as f:
        yaml.dump(output, f, allow_unicode=True, default_flow_style=False)
    
    print(f"\n✅ 검증 결과 저장: data/raw/sga_quality_validation.yaml")
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())

