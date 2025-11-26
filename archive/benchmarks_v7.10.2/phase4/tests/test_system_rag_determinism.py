#!/usr/bin/env python3
"""
System RAG 결정성 테스트
같은 키 → 항상 같은 결과 (100회 반복)
"""

import time
from statistics import mean, stdev
from typing import List, Dict, Any
from query_system_rag import SystemRAG


def test_system_rag_determinism(iterations: int = 100) -> bool:
    """
    100회 반복해도 동일한 결과
    
    Args:
        iterations: 반복 횟수
        
    Returns:
        테스트 통과 여부
    """
    
    print("🧪 System RAG 결정성 테스트 시작")
    print(f"   반복 횟수: {iterations}회")
    
    system_rag = SystemRAG()
    
    # 테스트 키 (실제로는 Registry에 있어야 함)
    test_keys = system_rag.get_available_keys()
    
    if not test_keys:
        print("❌ 테스트할 키가 없습니다.")
        print("   먼저 scripts/build_system_knowledge.py를 실행하세요.")
        return False
    
    # 최대 5개만 테스트
    test_keys = test_keys[:5]
    
    print(f"\n테스트 키: {len(test_keys)}개")
    for key in test_keys:
        print(f"  - {key}")
    
    all_passed = True
    
    for key in test_keys:
        print(f"\n{'='*60}")
        print(f"테스트: {key}")
        print(f"{'='*60}")
        
        results = []
        latencies = []
        match_types = []
        
        for i in range(iterations):
            try:
                start = time.time()
                result = system_rag.search_tool_by_key(key, verbose=False)
                latency = (time.time() - start) * 1000
                
                results.append(result['tool_id'])
                latencies.append(latency)
                match_types.append(result['match_type'])
                
            except Exception as e:
                print(f"❌ 반복 {i+1} 실패: {e}")
                all_passed = False
                break
        
        if not results:
            continue
        
        # 검증 1: 결과 일관성
        unique_results = set(results)
        if len(unique_results) != 1:
            print(f"❌ 결과 불일치!")
            print(f"   서로 다른 결과: {unique_results}")
            all_passed = False
        else:
            print(f"✅ 결과 일관성: {results[0]}")
        
        # 검증 2: 비결정적 여부
        if not all(r == results[0] for r in results):
            print(f"❌ 비결정적!")
            all_passed = False
        else:
            print(f"✅ 결정성: 100% 동일")
        
        # 검증 3: Match Type 일관성
        unique_match_types = set(match_types)
        if len(unique_match_types) != 1:
            print(f"⚠️ Match Type 불일치: {unique_match_types}")
        else:
            print(f"✅ Match Type: {match_types[0]}")
        
        # 통계
        avg_latency = mean(latencies)
        std_latency = stdev(latencies) if len(latencies) > 1 else 0
        min_latency = min(latencies)
        max_latency = max(latencies)
        
        print(f"\n📊 지연시간 통계:")
        print(f"   평균: {avg_latency:.2f}ms")
        print(f"   표준편차: {std_latency:.2f}ms")
        print(f"   최소: {min_latency:.2f}ms")
        print(f"   최대: {max_latency:.2f}ms")
        
        # 성능 검증
        if match_types[0] == 'exact_key':
            if avg_latency > 1.0:
                print(f"⚠️ KeyDirectory 지연시간 > 1ms (목표: < 1ms)")
            else:
                print(f"✅ 성능 목표 달성 (< 1ms)")
        else:
            if avg_latency > 20.0:
                print(f"⚠️ Vector 폴백 지연시간 > 20ms (목표: < 20ms)")
            else:
                print(f"✅ 성능 목표 달성 (< 20ms)")
    
    print(f"\n{'='*60}")
    if all_passed:
        print("🎉 모든 테스트 통과!")
        return True
    else:
        print("❌ 일부 테스트 실패")
        return False


def test_system_rag_stats():
    """System RAG 통계 테스트"""
    
    print("\n🧪 System RAG 통계 테스트")
    
    system_rag = SystemRAG()
    stats = system_rag.stats()
    
    print(f"\n📊 통계:")
    print(f"   총 도구: {stats['total_tools']}개")
    print(f"\n   Agent별:")
    for agent, count in stats['agents'].items():
        print(f"     - {agent}: {count}개")
    
    print(f"\n   Category별:")
    for category, count in stats['categories'].items():
        print(f"     - {category}: {count}개")
    
    print(f"\n   Priority별:")
    for priority, count in stats['priorities'].items():
        print(f"     - {priority}: {count}개")


def main():
    """메인 함수"""
    import sys
    
    if '--stats' in sys.argv:
        test_system_rag_stats()
        return
    
    # 반복 횟수
    iterations = 100
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        iterations = int(sys.argv[1])
    
    # 결정성 테스트
    passed = test_system_rag_determinism(iterations)
    
    # 통계 테스트
    test_system_rag_stats()
    
    # 종료 코드
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()

