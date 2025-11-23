#!/usr/bin/env python3
"""
모델 라우터 테스트 스크립트

Phase별 최적 모델 선택 및 비용 추정 검증
"""

import sys
from pathlib import Path

# 프로젝트 루트 경로 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.core.model_router import (
    get_model_router, select_model, get_model_info, estimate_cost
)
import json


def print_section(title: str):
    """섹션 헤더 출력"""
    print()
    print("=" * 70)
    print(f"  {title}")
    print("=" * 70)
    print()


def test_model_selection():
    """Phase별 모델 선택 테스트"""
    print_section("Phase별 모델 선택 테스트")
    
    router = get_model_router()
    
    for phase in [0, 1, 2, 3, 4]:
        model = router.select_model(phase)
        info = router.get_model_info(phase)
        
        print(f"📌 Phase {phase} ({info['phase_name']})")
        print(f"   모델: {model}")
        print(f"   비용: ${info['cost_per_task']:.6f}/작업")
        print(f"   속도: {info['avg_time_sec']:.2f}초")
        print(f"   정확도: {info['accuracy']}%")
        print(f"   테스트: {'✅ 완료' if info['tested'] else '⚠️ 미완료'}")
        print(f"   작업: {', '.join(info['tasks'][:2])}")
        if 'note' in info:
            print(f"   참고: {info['note']}")
        print()


def test_cost_estimation():
    """비용 추정 테스트"""
    print_section("비용 추정 (실측 분포 기반)")
    
    router = get_model_router()
    cost_info = router.estimate_cost()
    
    print("📊 Phase별 작업 분포:")
    for phase, ratio in cost_info['phase_distribution'].items():
        print(f"   Phase {phase}: {ratio*100:.0f}%")
    print()
    
    print("💰 비용 분석:")
    print(f"   평균 비용: ${cost_info['avg_cost_per_task']:.6f}/작업")
    print(f"   100회: ${cost_info['avg_cost_per_task'] * 100:.4f}")
    print(f"   1,000회: ${cost_info['cost_per_1000']:.2f}")
    print(f"   10,000회: ${cost_info['cost_per_10000']:.2f}")
    print(f"   100,000회: ${cost_info['cost_per_100000']:.2f}")
    print()
    
    savings = cost_info['savings_vs_baseline']
    print("📉 비용 절감:")
    print(f"   기존: ${savings['baseline_cost_per_1000']:.2f}/1,000회")
    print(f"   최적화: ${savings['optimized_cost_per_1000']:.2f}/1,000회")
    print(f"   절감: {savings['savings_percent']:.1f}% ⭐")
    print()


def test_custom_distribution():
    """커스텀 분포 테스트"""
    print_section("커스텀 작업 분포 시나리오")
    
    scenarios = {
        "단순 작업 위주 (Phase 0-2 60%)": {
            0: 0.20, 1: 0.20, 2: 0.20,
            3: 0.35, 4: 0.05
        },
        "복잡 작업 위주 (Phase 3-4 60%)": {
            0: 0.15, 1: 0.15, 2: 0.10,
            3: 0.40, 4: 0.20
        },
        "균등 분포": {
            0: 0.20, 1: 0.20, 2: 0.20,
            3: 0.20, 4: 0.20
        }
    }
    
    router = get_model_router()
    
    for scenario_name, distribution in scenarios.items():
        cost_info = router.estimate_cost(distribution)
        
        print(f"📋 {scenario_name}")
        print(f"   평균 비용: ${cost_info['avg_cost_per_task']:.6f}/작업")
        print(f"   1,000회: ${cost_info['cost_per_1000']:.2f}")
        print(f"   절감: {cost_info['savings_vs_baseline']['savings_percent']:.1f}%")
        print()


def test_convenience_functions():
    """편의 함수 테스트"""
    print_section("편의 함수 테스트")
    
    print("🔧 select_model() 함수:")
    for phase in [0, 2, 3, 4]:
        model = select_model(phase)
        print(f"   select_model({phase}) → {model}")
    print()
    
    print("📋 get_model_info() 함수:")
    info = get_model_info(3)
    print(f"   Phase 3 정보:")
    print(f"   - 모델: {info['current_model']}")
    print(f"   - 비용: ${info['cost_per_task']:.6f}")
    print()
    
    print("💰 estimate_cost() 함수:")
    cost = estimate_cost()
    print(f"   평균 비용: ${cost['avg_cost_per_task']:.6f}/작업")
    print(f"   1,000회: ${cost['cost_per_1000']:.2f}")


def test_json_export():
    """JSON 내보내기 테스트"""
    print_section("JSON 형식 출력")
    
    router = get_model_router()
    
    # 모든 Phase 정보
    all_phases = {}
    for phase in [0, 1, 2, 3, 4]:
        all_phases[f"phase_{phase}"] = router.get_model_info(phase)
    
    # 비용 정보
    cost_info = router.estimate_cost()
    
    result = {
        "phases": all_phases,
        "cost_estimation": cost_info,
        "summary": {
            "total_phases": 5,
            "routing_enabled": router.routing_enabled,
            "avg_cost_per_task": cost_info['avg_cost_per_task'],
            "cost_per_1000": cost_info['cost_per_1000'],
            "savings_percent": cost_info['savings_vs_baseline']['savings_percent']
        }
    }
    
    print(json.dumps(result, indent=2, ensure_ascii=False))


def main():
    """메인 테스트 실행"""
    print()
    print("🚀 UMIS 모델 라우터 테스트")
    print("=" * 70)
    print()
    print("목표: Phase별 최적 모델 자동 선택으로 98% 비용 절감")
    print("기반: UMIS_LLM_OPTIMIZATION_FINAL.md")
    
    # 테스트 실행
    test_model_selection()
    test_cost_estimation()
    test_custom_distribution()
    test_convenience_functions()
    
    # JSON 출력 (선택)
    import os
    if os.getenv("EXPORT_JSON"):
        test_json_export()
    
    print_section("테스트 완료 ✅")
    print("다음 단계:")
    print("  1. .env에서 USE_PHASE_BASED_ROUTING=true 확인")
    print("  2. Estimator 실제 작업 수행 및 비용 측정")
    print("  3. 모니터링 대시보드 구축")
    print()


if __name__ == "__main__":
    main()

