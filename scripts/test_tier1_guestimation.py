"""
Tier 1 Guestimation 테스트

Built-in 규칙 + RAG 검색 동작 확인
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.guestimation_v3.tier1 import Tier1FastPath
from umis_rag.guestimation_v3.models import Context, Intent


def test_builtin_rules():
    """Built-in 규칙 테스트"""
    
    print("\n" + "="*60)
    print("Built-in 규칙 테스트")
    print("="*60)
    
    tier1 = Tier1FastPath()
    
    test_cases = [
        # 공식 통계
        {
            'question': "한국 인구는?",
            'expected': True,
            'expected_value': 51740000
        },
        {
            'question': "서울 인구는?",
            'expected': True,
            'expected_value': 9500000
        },
        
        # 물리 상수
        {
            'question': "하루는 몇 시간?",
            'expected': True,
            'expected_value': 24
        },
        {
            'question': "일주일은 몇 일?",
            'expected': True,
            'expected_value': 7
        },
        
        # 법률 상수
        {
            'question': "2024년 최저임금은?",
            'expected': True,
            'expected_value': 9860
        },
        {
            'question': "법정근로시간은?",
            'expected': True,
            'expected_value': 52
        },
        
        # 제외 패턴 (미래 예측)
        {
            'question': "미래 한국 인구는?",
            'expected': False,  # 제외 키워드 "미래"
            'reason': "예측은 Tier 2"
        },
        
        # 명백하지 않은 것
        {
            'question': "한국 음식점 월매출은?",
            'expected': False,
            'reason': "Built-in 규칙 없음"
        }
    ]
    
    passed = 0
    failed = 0
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n[테스트 {i}] {case['question']}")
        
        result = tier1.estimate(case['question'])
        
        if case['expected']:
            # 성공 예상
            if result and result.tier == 1:
                print(f"  ✅ Tier 1 처리")
                print(f"     값: {result.get_display_value()}")
                print(f"     신뢰도: {result.confidence:.0%}")
                print(f"     근거: {result.reasoning}")
                
                if 'expected_value' in case and result.value:
                    if abs(result.value - case['expected_value']) < 0.01:
                        print(f"  ✅ 값 일치!")
                        passed += 1
                    else:
                        print(f"  ❌ 값 불일치 (예상: {case['expected_value']}, 실제: {result.value})")
                        failed += 1
                else:
                    passed += 1
            else:
                print(f"  ❌ 실패 (Tier 1 처리 예상)")
                print(f"     결과: {result}")
                failed += 1
        else:
            # 실패 예상 (Tier 2로)
            if result is None or result.tier != 1:
                print(f"  ✅ Tier 2로 넘김 (예상대로)")
                print(f"     이유: {case.get('reason', 'Unknown')}")
                passed += 1
            else:
                print(f"  ❌ 예상 밖 성공 (Tier 2로 넘길 것으로 예상)")
                failed += 1
    
    print(f"\n" + "="*60)
    print(f"결과: {passed}개 통과, {failed}개 실패")
    print("="*60)
    
    return passed, failed


def test_rag_search():
    """RAG 검색 테스트 (현재는 데이터 없음)"""
    
    print("\n" + "="*60)
    print("RAG 검색 테스트")
    print("="*60)
    
    tier1 = Tier1FastPath()
    
    # 현재는 학습된 규칙이 없으므로
    print("\nℹ️  학습된 규칙이 아직 없습니다.")
    print("   Tier 2/3 사용 후 자동으로 학습됩니다.")
    print("   학습되면 이 테스트가 통과할 것입니다.")
    
    # 샘플 검색 (실패 예상)
    context = Context(
        domain="Food_Service",
        region="한국"
    )
    
    result = tier1.estimate("한국 음식점 월매출은?", context)
    
    if result:
        print(f"\n  예상 밖 성공: {result.reasoning}")
    else:
        print(f"\n  ✅ 예상대로 None (학습 데이터 없음)")


def main():
    """메인 테스트"""
    
    print("\n" + "="*80)
    print(" "*20 + "Tier 1 Guestimation 테스트")
    print("="*80)
    
    # Built-in 규칙 테스트
    passed, failed = test_builtin_rules()
    
    # RAG 검색 테스트
    test_rag_search()
    
    print("\n" + "="*80)
    if failed == 0:
        print("  ✅ 모든 테스트 통과!")
    else:
        print(f"  ⚠️  {failed}개 테스트 실패")
    print("="*80)


if __name__ == "__main__":
    main()

