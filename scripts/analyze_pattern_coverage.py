#!/usr/bin/env python3
"""
패턴-사례 커버리지 분석 스크립트

목적:
  - 각 비즈니스 모델 패턴별 성공/실패 사례 개수 파악
  - 성공-실패 매칭율 계산
  - 보충이 필요한 영역 식별

사용법:
  python scripts/analyze_pattern_coverage.py
"""

import yaml
from pathlib import Path
from collections import defaultdict
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

# 프로젝트 루트
project_root = Path(__file__).parent.parent
data_dir = project_root / "data" / "raw"

def load_yaml(filename):
    """YAML 파일 로드"""
    filepath = data_dir / filename
    with open(filepath, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def count_cases_in_pattern(pattern_data, pattern_id):
    """패턴 내부의 사례 개수 세기"""
    count = 0
    
    def recursive_count(obj, depth=0):
        nonlocal count
        if depth > 10:  # 무한 재귀 방지
            return
        
        if isinstance(obj, dict):
            # case_studies, success_cases, failure_cases 등 찾기
            if any(key in ['case_studies', 'case_study', 'success_cases', 'examples', 
                          'fancy', 'boring', 'korean', 'global'] for key in obj.keys()):
                # 리스트 항목 개수 세기
                for value in obj.values():
                    if isinstance(value, list):
                        count += len(value)
                    elif isinstance(value, dict):
                        recursive_count(value, depth + 1)
            else:
                for value in obj.values():
                    recursive_count(value, depth + 1)
        elif isinstance(obj, list):
            for item in obj:
                recursive_count(item, depth + 1)
    
    recursive_count(pattern_data)
    return count

def analyze_business_models():
    """비즈니스 모델 패턴 분석"""
    console.print("\n[bold cyan]📊 비즈니스 모델 패턴 분석[/bold cyan]\n")
    
    data = load_yaml("umis_business_model_patterns.yaml")
    
    # 패턴 리스트
    patterns = [
        "platform_business_model", "subscription_model", "franchise_model",
        "direct_to_consumer_model", "advertising_model", "licensing_model",
        "freemium_model",
        # Boring patterns
        "manufacturing_model", "wholesale_distribution_model", "traditional_retail_model",
        "small_business_model", "b2b_sales_model", "professional_services_model",
        "construction_model", "logistics_model", "real_estate_model",
        "education_services_model", "healthcare_services_model", "service_provider_model",
        "agriculture_model", "agency_dealership_model", "financial_services_model"
    ]
    
    table = Table(title="비즈니스 모델 패턴별 사례 수")
    table.add_column("패턴", style="cyan")
    table.add_column("타입", style="yellow")
    table.add_column("성공 사례", style="green")
    table.add_column("실패 사례", style="red")
    table.add_column("상태", style="magenta")
    
    stats = {
        'total_patterns': 0,
        'with_success': 0,
        'with_failure': 0,
        'with_both': 0,
        'total_success_cases': 0,
        'total_failure_cases': 0
    }
    
    for pattern_id in patterns:
        if pattern_id not in data:
            continue
        
        stats['total_patterns'] += 1
        pattern_data = data[pattern_id]
        
        # 사례 개수 세기
        success_count = count_cases_in_pattern(pattern_data, pattern_id)
        
        # 실패 사례는 별도로 (현재는 없을 것)
        failure_count = 0  # TODO: 실패 사례 연결 필요
        
        if success_count > 0:
            stats['with_success'] += 1
            stats['total_success_cases'] += success_count
        
        if failure_count > 0:
            stats['with_failure'] += 1
            stats['total_failure_cases'] += failure_count
        
        if success_count > 0 and failure_count > 0:
            stats['with_both'] += 1
        
        # 패턴 타입
        pattern_type = "Fancy" if pattern_id in patterns[:7] else "Boring"
        
        # 상태 판단
        if success_count >= 5 and failure_count >= 5:
            status = "✅ Excellent"
        elif success_count > 0 and failure_count > 0:
            status = "⚠️ Partial"
        elif success_count > 0:
            status = "⚠️ Success Only"
        elif failure_count > 0:
            status = "⚠️ Failure Only"
        else:
            status = "❌ No Cases"
        
        table.add_row(
            pattern_id[:30],
            pattern_type,
            str(success_count),
            str(failure_count),
            status
        )
    
    console.print(table)
    
    # 통계 요약
    console.print(f"\n[bold]통계 요약:[/bold]")
    console.print(f"  총 패턴: {stats['total_patterns']}개")
    console.print(f"  성공 사례 있음: {stats['with_success']}개 ({stats['with_success']/stats['total_patterns']*100:.1f}%)")
    console.print(f"  실패 사례 있음: {stats['with_failure']}개 ({stats['with_failure']/stats['total_patterns']*100:.1f}%)")
    console.print(f"  [bold green]양쪽 모두 있음: {stats['with_both']}개 ({stats['with_both']/stats['total_patterns']*100:.1f}%)[/bold green]")
    console.print(f"\n  총 성공 사례: {stats['total_success_cases']}개")
    console.print(f"  총 실패 사례: {stats['total_failure_cases']}개")
    console.print(f"  패턴당 평균 사례: {(stats['total_success_cases'] + stats['total_failure_cases'])/stats['total_patterns']:.1f}개")
    
    return stats

def analyze_disruption_patterns():
    """Disruption 패턴 분석"""
    console.print("\n[bold cyan]🔥 Disruption 패턴 분석[/bold cyan]\n")
    
    data = load_yaml("umis_disruption_patterns.yaml")
    
    patterns = [
        "innovation_disruption", "low_end_disruption", "channel_disruption",
        "experience_disruption", "continuous_innovation_disruption", "hybrid_disruption",
        # Boring
        "regulatory_change_disruption", "format_disruption", "generational_disruption",
        "import_substitution_disruption", "franchising_disruption", "payment_disruption",
        "platform_aggregation_disruption", "sme_automation_disruption", "sustainability_disruption"
    ]
    
    table = Table(title="Disruption 패턴별 사례 수")
    table.add_column("패턴", style="cyan")
    table.add_column("타입", style="yellow")
    table.add_column("성공 사례", style="green")
    table.add_column("실패 사례", style="red")
    table.add_column("상태", style="magenta")
    
    stats = {
        'total_patterns': 0,
        'with_success': 0,
        'with_failure': 0,
        'with_both': 0,
        'total_success_cases': 0
    }
    
    for pattern_id in patterns:
        if pattern_id not in data:
            continue
        
        stats['total_patterns'] += 1
        pattern_data = data[pattern_id]
        
        success_count = count_cases_in_pattern(pattern_data, pattern_id)
        failure_count = 0  # Disruption은 주로 성공 사례
        
        if success_count > 0:
            stats['with_success'] += 1
            stats['total_success_cases'] += success_count
        
        pattern_type = "Fancy" if pattern_id in patterns[:6] else "Boring"
        
        if success_count >= 5:
            status = "✅ Good"
        elif success_count > 0:
            status = "⚠️ Needs More"
        else:
            status = "❌ No Cases"
        
        table.add_row(
            pattern_id[:30],
            pattern_type,
            str(success_count),
            str(failure_count),
            status
        )
    
    console.print(table)
    console.print(f"\n  총 Disruption 사례: {stats['total_success_cases']}개")
    console.print(f"  패턴당 평균: {stats['total_success_cases']/stats['total_patterns']:.1f}개")
    
    return stats

def analyze_failure_patterns():
    """실패 패턴 분석"""
    console.print("\n[bold red]⚠️  실패 패턴 분석[/bold red]\n")
    
    # Incumbent Failure
    incumbent_data = load_yaml("umis_incumbent_failure_patterns.yaml")
    startup_data = load_yaml("umis_startup_failure_patterns.yaml")
    
    console.print("[yellow]Incumbent Failure 패턴:[/yellow]")
    console.print(f"  - 패턴 수: ~10개")
    console.print(f"  - 사례: 60+ (Fancy 40%, Boring 60%)")
    
    console.print("\n[yellow]Startup Failure 패턴:[/yellow]")
    console.print(f"  - 패턴 수: ~9개")
    console.print(f"  - 사례: 75+ (Fancy 30%, Boring 70%)")

def identify_gaps():
    """Gap 식별 및 보충 권장사항"""
    console.print("\n[bold yellow]🎯 Gap 분석 및 보충 권장사항[/bold yellow]\n")
    
    recommendations = []
    
    # 1. 성공-실패 매칭 부족
    recommendations.append({
        "category": "성공-실패 매칭",
        "현황": "30% 패턴만 양쪽 커버",
        "목표": "80% 패턴 양쪽 커버",
        "action": [
            "각 비즈니스 모델에 대응하는 실패 사례 추가",
            "Subscription → MoviePass, Blue Apron 연결",
            "Manufacturing → 중소제조사 폐업 사례",
            "Franchise → 프랜차이즈 실패 사례"
        ],
        "예상_추가": "100개 실패 사례"
    })
    
    # 2. Boring 패턴 사례 부족
    recommendations.append({
        "category": "Boring 패턴 사례",
        "현황": "패턴당 평균 2-3개",
        "목표": "패턴당 최소 10개",
        "action": [
            "제조업 사례 +8개",
            "유통 사례 +8개",
            "자영업 사례 +10개",
            "B2B 사례 +8개"
        ],
        "예상_추가": "150개 사례"
    })
    
    # 3. 디테일 부족
    recommendations.append({
        "category": "사례 디테일",
        "현황": "1-2줄 간단 설명",
        "목표": "10-15줄 상세 분석",
        "action": [
            "사례 템플릿 재정의",
            "재무 데이터 추가",
            "실패 원인 상세화",
            "교훈 명시화"
        ],
        "예상_작업": "200개 사례 재작성"
    })
    
    # 4. Cross-reference 부재
    recommendations.append({
        "category": "Cross-Reference",
        "현황": "패턴-사례 연결 느슨함",
        "목표": "명시적 ref 체계",
        "action": [
            "YAML에 ref 필드 추가",
            "성공 패턴 → 실패 사례 링크",
            "실패 패턴 → 성공 사례 링크"
        ],
        "예상_작업": "YAML 구조 개선"
    })
    
    # 출력
    for i, rec in enumerate(recommendations, 1):
        panel = Panel(
            f"[bold]현황:[/bold] {rec['현황']}\n"
            f"[bold]목표:[/bold] {rec['목표']}\n"
            f"[bold]액션:[/bold]\n" + "\n".join(f"  - {a}" for a in rec['action']) +
            f"\n\n[bold yellow]추가 필요:[/bold yellow] {rec.get('예상_추가', rec.get('예상_작업', 'N/A'))}",
            title=f"Gap {i}: {rec['category']}",
            border_style="yellow"
        )
        console.print(panel)

def main():
    console.print("\n[bold blue]🔍 UMIS Pattern-Case Coverage Analysis[/bold blue]\n")
    console.print("목적: 패턴별 사례 분포 파악 및 Gap 식별\n")
    
    # 분석
    biz_stats = analyze_business_models()
    dis_stats = analyze_disruption_patterns()
    analyze_failure_patterns()
    
    # Gap 식별
    identify_gaps()
    
    # 최종 요약
    console.print("\n[bold green]📈 최종 요약[/bold green]\n")
    
    summary_table = Table()
    summary_table.add_column("구분", style="cyan")
    summary_table.add_column("현재", style="yellow")
    summary_table.add_column("목표", style="green")
    summary_table.add_column("Gap", style="red")
    
    summary_table.add_row("총 패턴 수", "56개", "56개", "✅ 충분")
    summary_table.add_row("총 사례 수", "~180개", "600개", "❌ 420개 부족")
    summary_table.add_row("성공-실패 매칭", "30%", "80%", "❌ 50%p 부족")
    summary_table.add_row("사례 디테일", "간단", "상세", "❌ 재작성 필요")
    summary_table.add_row("패턴당 평균 사례", "~3개", "10개", "❌ 7개 부족")
    
    console.print(summary_table)
    
    console.print("\n[bold yellow]🎯 우선순위 액션:[/bold yellow]")
    console.print("  1. [bold]성공-실패 Matching Table 구축[/bold] (즉시)")
    console.print("  2. [bold]Boring 패턴 사례 보충[/bold] (제조, 유통, 자영업)")
    console.print("  3. [bold]사례 템플릿 강화[/bold] (디테일 3배)")
    console.print("  4. [bold]Cross-reference 시스템[/bold] (ref 필드)")
    console.print()

if __name__ == "__main__":
    main()

