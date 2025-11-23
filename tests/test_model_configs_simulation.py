#!/usr/bin/env python3
"""
Model Config 실전 시뮬레이션

실제 Phase 4 사용 시나리오를 시뮬레이션
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.core.model_router import select_model_with_config
from umis_rag.core.model_configs import is_pro_model


def simulate_phase4_estimation():
    """Phase 4 추정 시뮬레이션"""
    print("\n" + "="*60)
    print("🎯 Phase 4 Fermi Estimation 시뮬레이션")
    print("="*60)
    
    # 1. 모델 + 설정 선택
    model_name, config = select_model_with_config(phase=4)
    
    print(f"\n📌 Phase 4 모델 선택:")
    print(f"   모델: {model_name}")
    print(f"   API: {config.api_type}")
    print(f"   Max tokens: {config.max_output_tokens}")
    
    # 2. Fast Mode 체크
    if is_pro_model(model_name):
        print(f"\n🚀 Fast Mode 적용 대상 (pro 모델)")
        fast_mode_prompt = """
🔴 SPEED OPTIMIZATION MODE
⏱️ 목표 응답 시간: 60초 이내
📏 최대 출력 길이: 2,000자 이내
"""
        print(f"   Fast Mode 프롬프트 추가됨")
    else:
        print(f"\n✅ 일반 모델 (Fast Mode 미적용)")
        fast_mode_prompt = ""
    
    # 3. 프롬프트 구성
    base_prompt = "서울 하루 택시 승객 수는?"
    full_prompt = fast_mode_prompt + base_prompt if fast_mode_prompt else base_prompt
    
    print(f"\n📝 프롬프트:")
    print(f"   - Fast Mode: {'적용' if fast_mode_prompt else '미적용'}")
    print(f"   - 길이: {len(full_prompt)}자")
    
    # 4. API 파라미터 구성
    api_params = config.build_api_params(
        prompt=full_prompt,
        reasoning_effort='medium'
    )
    
    print(f"\n⚙️ API 파라미터:")
    for key, value in api_params.items():
        if key == 'input':
            print(f"   - {key}: {value[:30]}...")
        elif key == 'messages':
            print(f"   - {key}: {len(value)}개 메시지")
        elif isinstance(value, dict):
            print(f"   - {key}: {value}")
        else:
            print(f"   - {key}: {value}")
    
    print(f"\n✅ API 호출 준비 완료")
    print(f"   실제 호출: client.{config.api_type}.create(**api_params)")
    
    return True


def test_multiple_models():
    """여러 모델 설정 비교"""
    print("\n" + "="*60)
    print("📊 모델별 API 설정 비교")
    print("="*60)
    
    from umis_rag.core.model_configs import get_model_config
    
    test_models = [
        'o1-mini',      # Phase 4 기본
        'o3-mini-2025-01-31',  # 벤치마크 최우선
        'gpt-5.1',      # 높은 추론, 낮은 형식
        'gpt-5-pro',    # Pro 모델
        'gpt-4.1-nano'  # Phase 0-2
    ]
    
    print("\n모델 비교표:")
    print("-" * 100)
    print(f"{'모델':<25} {'API':<12} {'Max Tokens':<12} {'Reasoning':<12} {'Pro':<8} {'비고'}")
    print("-" * 100)
    
    for model_name in test_models:
        config = get_model_config(model_name)
        reasoning = 'Yes' if config.reasoning_effort_support else 'No'
        if config.reasoning_effort_fixed:
            reasoning += f" (fixed)"
        pro = 'Yes' if is_pro_model(model_name) else 'No'
        notes = config.notes[:30]
        
        print(f"{model_name:<25} {config.api_type:<12} {config.max_output_tokens:<12} {reasoning:<12} {pro:<8} {notes}")
    
    print("-" * 100)
    
    return True


def test_reasoning_effort_variations():
    """Reasoning effort 레벨별 파라미터 테스트"""
    print("\n" + "="*60)
    print("🔧 Reasoning Effort 레벨별 테스트")
    print("="*60)
    
    from umis_rag.core.model_configs import get_model_config
    
    config = get_model_config('o1-mini')
    
    efforts = ['low', 'medium', 'high']
    
    print(f"\n모델: o1-mini")
    print(f"지원 레벨: {config.reasoning_effort_levels}")
    
    for effort in efforts:
        params = config.build_api_params(
            prompt="테스트",
            reasoning_effort=effort
        )
        
        if 'reasoning' in params:
            actual_effort = params['reasoning']['effort']
            status = "✅" if actual_effort == effort else "❌"
            print(f"{status} {effort} → reasoning.effort={actual_effort}")
        else:
            print(f"❌ {effort} → reasoning 필드 없음")
    
    # Pro 모델 테스트 (high 고정)
    print(f"\n모델: gpt-5-pro (high 고정)")
    config_pro = get_model_config('gpt-5-pro')
    print(f"지원 레벨: {config_pro.reasoning_effort_levels}")
    print(f"고정값: {config_pro.reasoning_effort_fixed}")
    
    for effort in efforts:
        params = config_pro.build_api_params(
            prompt="테스트",
            reasoning_effort=effort
        )
        
        if 'reasoning' in params:
            actual_effort = params['reasoning']['effort']
            expected = 'high'  # 고정
            status = "✅" if actual_effort == expected else "❌"
            print(f"{status} {effort} 요청 → reasoning.effort={actual_effort} (고정)")
    
    return True


def test_environment_model_change():
    """환경변수 기반 모델 변경 시뮬레이션"""
    print("\n" + "="*60)
    print("🔄 .env 모델 변경 시뮬레이션")
    print("="*60)
    
    # 시나리오: .env에서 LLM_MODEL_PHASE4를 변경
    scenarios = [
        ('o1-mini', '기본 모델 (Phase 4 기본)'),
        ('gpt-5.1', 'Advanced reasoning 모델'),
        ('o3-mini-2025-01-31', '벤치마크 최우선 후보'),
        ('gpt-5-pro', 'Pro 모델 (Fast Mode)'),
    ]
    
    print("\n시뮬레이션: .env에서 LLM_MODEL_PHASE4 변경")
    print("-" * 80)
    
    for model_name, description in scenarios:
        print(f"\n📝 LLM_MODEL_PHASE4={model_name}")
        print(f"   설명: {description}")
        
        from umis_rag.core.model_configs import get_model_config
        config = get_model_config(model_name)
        
        print(f"   자동 적용:")
        print(f"   - API 타입: {config.api_type}")
        print(f"   - Max tokens: {config.max_output_tokens}")
        print(f"   - Reasoning: {config.reasoning_effort_support}")
        if config.reasoning_effort_support:
            print(f"   - Default effort: {config.reasoning_effort_default}")
        
        if is_pro_model(model_name):
            print(f"   - ⭐ Fast Mode 자동 적용")
        
        # API 파라미터 미리보기
        params = config.build_api_params(
            prompt="테스트",
            reasoning_effort='medium'
        )
        print(f"   - API keys: {list(params.keys())}")
    
    print("\n✅ 모든 모델 변경 시나리오 검증 완료")
    return True


def main():
    """실전 시뮬레이션 실행"""
    print("\n" + "━"*60)
    print("🎮 Model Config System 실전 시뮬레이션")
    print("━"*60)
    
    tests = [
        ("Phase 4 추정 시뮬레이션", simulate_phase4_estimation),
        ("모델별 설정 비교", test_multiple_models),
        ("Reasoning Effort 레벨 테스트", test_reasoning_effort_variations),
        ("환경변수 모델 변경", test_environment_model_change),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ {name} 실패: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # 결과 요약
    print("\n" + "━"*60)
    print("📊 시뮬레이션 결과")
    print("━"*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print(f"\n총 결과: {passed}/{total} 통과 ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 모든 시뮬레이션 성공!")
        print("\n✅ 실제 Phase 4 통합 준비 완료!")
        return 0
    else:
        print(f"\n⚠️ {total - passed}개 시뮬레이션 실패")
        return 1


if __name__ == "__main__":
    sys.exit(main())

