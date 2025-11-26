"""
Native/External 모드 테스트 스크립트

UMIS v7.7.0 신규 기능:
- Native 모드: RAG만 수행 → Cursor LLM이 처리
- External 모드: RAG + API 호출 → 완성된 결과

사용법:
------
# Native 모드 테스트
UMIS_MODE=native python scripts/test_native_mode.py

# External 모드 테스트
UMIS_MODE=external python scripts/test_native_mode.py

# 모드 비교 (둘 다 실행)
python scripts/test_native_mode.py --compare
"""

import sys
from pathlib import Path
import json

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.agents.explorer import ExplorerRAG
from umis_rag.core.config import settings
from umis_rag.core.llm_provider import LLMProvider
from umis_rag.utils.logger import logger


def test_current_mode():
    """현재 설정된 모드 테스트"""
    
    print("\n" + "="*80)
    print("UMIS Native/External 모드 테스트")
    print("="*80)
    
    # 현재 모드 확인
    mode_info = LLMProvider.get_mode_info()
    
    print(f"\n📊 현재 모드 정보:")
    print(f"  - 모드: {mode_info['mode']}")
    print(f"  - API 사용: {mode_info['uses_api']}")
    print(f"  - 비용: {mode_info['cost']}")
    print(f"  - 자동화: {mode_info['automation']}")
    print(f"  - 설명: {mode_info['description']}")
    
    # Explorer 초기화
    print(f"\n🚀 Explorer 초기화 중...")
    try:
        explorer = ExplorerRAG(use_projected=False)
        print(f"  ✅ 초기화 완료")
    except Exception as e:
        print(f"  ❌ 초기화 실패: {e}")
        return
    
    # 간단한 패턴 검색
    print(f"\n🔍 RAG 패턴 검색 테스트")
    trigger_signals = "구독 모델, 고객 유지, 정기 수익"
    
    try:
        results = explorer.search_patterns(
            trigger_signals=trigger_signals,
            top_k=3,
            use_graph=False  # Vector만 사용
        )
        
        print(f"  ✅ 검색 완료: {len(results)}개 패턴 발견")
        
        for i, (doc, score) in enumerate(results, 1):
            pattern_id = doc.metadata.get('pattern_id', 'N/A')
            print(f"    #{i} {pattern_id} (유사도: {score:.4f})")
    
    except Exception as e:
        print(f"  ❌ 검색 실패: {e}")
        return
    
    # 가설 생성 테스트
    print(f"\n💡 가설 생성 테스트")
    
    observer_observation = """
    음악 스트리밍 시장 관찰:
    - 파편화된 아티스트-청취자 연결
    - 높은 플랫폼 중개 비용
    - 구독 모델 확산
    """
    
    matched_patterns = [doc for doc, _ in results[:2]]
    success_cases = []  # 간단한 테스트이므로 생략
    
    try:
        hypothesis = explorer.generate_opportunity_hypothesis(
            observer_observation=observer_observation,
            matched_patterns=matched_patterns,
            success_cases=success_cases
        )
        
        print(f"  ✅ 가설 생성 완료")
        print(f"\n📝 결과 타입: {type(hypothesis)}")
        
        if isinstance(hypothesis, dict):
            # Native 모드 결과
            print(f"\n🎯 Native 모드 결과:")
            print(f"  - 모드: {hypothesis.get('mode')}")
            print(f"  - 매칭 패턴 수: {hypothesis.get('matched_patterns_count')}")
            print(f"  - 성공 사례 수: {hypothesis.get('success_cases_count')}")
            print(f"\n📋 Cursor LLM 지시사항:")
            print(f"{hypothesis.get('instruction')}")
            print(f"\n💬 다음 단계:")
            print(f"{hypothesis.get('next_step')}")
            
            # RAG 컨텍스트 일부 출력
            rag_context = hypothesis.get('rag_context', '')
            print(f"\n📚 RAG 컨텍스트 (처음 500자):")
            print(rag_context[:500] + "...")
        
        else:
            # External 모드 결과
            print(f"\n🌐 External 모드 결과:")
            print(hypothesis)
    
    except Exception as e:
        print(f"  ❌ 가설 생성 실패: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n" + "="*80)
    print("테스트 완료!")
    print("="*80)


def compare_modes():
    """Native/External 모드 비교"""
    
    print("\n" + "="*80)
    print("Native vs External 모드 비교")
    print("="*80)
    
    print("\n⚠️  이 기능은 .env 파일 수정이 필요합니다.")
    print("현재는 설정된 모드만 테스트됩니다.")
    print("\n비교 방법:")
    print("1. .env에서 UMIS_MODE=native 설정 → 이 스크립트 실행")
    print("2. .env에서 UMIS_MODE=external 설정 → 이 스크립트 실행")
    print("3. 결과 비교")
    
    test_current_mode()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="UMIS Native/External 모드 테스트")
    parser.add_argument(
        "--compare",
        action="store_true",
        help="Native/External 모드 비교 (안내만)"
    )
    
    args = parser.parse_args()
    
    if args.compare:
        compare_modes()
    else:
        test_current_mode()

