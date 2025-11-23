#!/usr/bin/env python3
"""
Model Config System 테스트

config/model_configs.yaml 및 model_configs.py, model_router.py 검증
"""

import sys
from pathlib import Path

# 프로젝트 루트 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.core.model_configs import (
    model_config_manager,
    get_model_config,
    list_supported_models,
    is_pro_model
)
from umis_rag.core.model_router import select_model_with_config


def test_yaml_loading():
    """YAML 로딩 테스트"""
    print("\n" + "="*60)
    print("TEST 1: YAML 로딩")
    print("="*60)
    
    try:
        models = list_supported_models()
        print(f"✅ 로드된 모델 수: {len(models)}개")
        print(f"   모델 목록: {', '.join(models[:8])}...")
        return True
    except Exception as e:
        print(f"❌ 실패: {e}")
        return False


def test_model_config_query():
    """모델 설정 조회 테스트"""
    print("\n" + "="*60)
    print("TEST 2: 모델 설정 조회")
    print("="*60)
    
    test_models = ['o1-mini', 'gpt-5.1', 'gpt-5-pro', 'gpt-4.1-nano']
    success_count = 0
    
    for model_name in test_models:
        try:
            config = get_model_config(model_name)
            print(f"\n✅ {model_name}:")
            print(f"   - API 타입: {config.api_type}")
            print(f"   - Max tokens: {config.max_output_tokens}")
            print(f"   - Reasoning effort: {config.reasoning_effort_support}")
            if config.reasoning_effort_support:
                print(f"     - Levels: {config.reasoning_effort_levels}")
                print(f"     - Default: {config.reasoning_effort_default}")
                if config.reasoning_effort_fixed:
                    print(f"     - Fixed: {config.reasoning_effort_fixed}")
            print(f"   - Temperature: {config.temperature_support}")
            print(f"   - Notes: {config.notes[:50]}...")
            success_count += 1
        except Exception as e:
            print(f"❌ {model_name} 실패: {e}")
    
    print(f"\n결과: {success_count}/{len(test_models)} 성공")
    return success_count == len(test_models)


def test_api_params_building():
    """API 파라미터 구성 테스트"""
    print("\n" + "="*60)
    print("TEST 3: API 파라미터 자동 구성")
    print("="*60)
    
    test_cases = [
        {
            'model': 'o1-mini',
            'reasoning_effort': 'medium',
            'expected_api': 'responses'
        },
        {
            'model': 'gpt-5.1',
            'reasoning_effort': 'high',
            'expected_api': 'responses'
        },
        {
            'model': 'gpt-4.1-nano',
            'reasoning_effort': None,
            'expected_api': 'chat'
        }
    ]
    
    success_count = 0
    
    for test in test_cases:
        try:
            config = get_model_config(test['model'])
            params = config.build_api_params(
                prompt="테스트 프롬프트",
                reasoning_effort=test['reasoning_effort']
            )
            
            print(f"\n✅ {test['model']}:")
            print(f"   - API 타입: {config.api_type}")
            print(f"   - model: {params.get('model')}")
            
            if config.api_type == 'responses':
                print(f"   - input: {params.get('input')[:30]}...")
                print(f"   - max_output_tokens: {params.get('max_output_tokens')}")
                if 'reasoning' in params:
                    print(f"   - reasoning.effort: {params['reasoning']['effort']}")
            else:
                print(f"   - messages: {len(params.get('messages', []))}개")
                print(f"   - max_tokens: {params.get('max_tokens')}")
                if 'temperature' in params:
                    print(f"   - temperature: {params['temperature']}")
            
            # 검증
            assert config.api_type == test['expected_api'], f"API 타입 불일치"
            assert params.get('model') == test['model'], f"모델 이름 불일치"
            
            success_count += 1
        except Exception as e:
            print(f"❌ {test['model']} 실패: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n결과: {success_count}/{len(test_cases)} 성공")
    return success_count == len(test_cases)


def test_pro_model_detection():
    """Pro 모델 감지 테스트"""
    print("\n" + "="*60)
    print("TEST 4: Pro 모델 감지")
    print("="*60)
    
    pro_models = ['gpt-5-pro', 'o1-pro', 'o1-pro-2025-03-19']
    non_pro_models = ['o1-mini', 'gpt-5.1', 'gpt-4.1-nano']
    
    success_count = 0
    total = len(pro_models) + len(non_pro_models)
    
    print("\nPro 모델 (Fast Mode 대상):")
    for model in pro_models:
        result = is_pro_model(model)
        print(f"  {model}: {result}")
        if result:
            success_count += 1
        else:
            print(f"    ❌ Pro 모델이지만 False 반환")
    
    print("\n일반 모델:")
    for model in non_pro_models:
        result = is_pro_model(model)
        print(f"  {model}: {result}")
        if not result:
            success_count += 1
        else:
            print(f"    ❌ 일반 모델이지만 True 반환")
    
    print(f"\n결과: {success_count}/{total} 성공")
    return success_count == total


def test_model_router_integration():
    """ModelRouter 통합 테스트"""
    print("\n" + "="*60)
    print("TEST 5: ModelRouter select_model_with_config()")
    print("="*60)
    
    test_phases = [0, 1, 2, 3, 4]
    success_count = 0
    
    for phase in test_phases:
        try:
            model_name, config = select_model_with_config(phase)
            
            print(f"\n✅ Phase {phase}:")
            print(f"   - 선택된 모델: {model_name}")
            print(f"   - API 타입: {config.api_type}")
            print(f"   - Max tokens: {config.max_output_tokens}")
            print(f"   - Reasoning effort: {config.reasoning_effort_support}")
            
            # API 파라미터 구성 테스트
            api_params = config.build_api_params(
                prompt=f"Phase {phase} 테스트",
                reasoning_effort='medium'
            )
            print(f"   - API params keys: {list(api_params.keys())}")
            
            success_count += 1
        except Exception as e:
            print(f"❌ Phase {phase} 실패: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n결과: {success_count}/{len(test_phases)} 성공")
    return success_count == len(test_phases)


def test_prefix_fallback():
    """Prefix 기반 폴백 테스트"""
    print("\n" + "="*60)
    print("TEST 6: Prefix 기반 폴백")
    print("="*60)
    
    test_cases = [
        ('o1-mini-2025-12-31', 'o1-mini'),  # 새 버전 → 기본 버전
        ('o3-mini-2025-99-99', 'o3-mini'),
        ('gpt-5.1-turbo', 'gpt-5.1'),
        ('unknown-model', 'default'),  # 완전 미지원
    ]
    
    success_count = 0
    
    for model_input, expected_base in test_cases:
        try:
            config = get_model_config(model_input)
            
            if expected_base == 'default':
                # 기본 설정 사용
                assert config.api_type == 'chat', "기본 설정 api_type은 chat"
                print(f"✅ {model_input} → default config")
            else:
                # 예상 베이스 모델 설정 사용
                base_config = get_model_config(expected_base)
                assert config.api_type == base_config.api_type
                print(f"✅ {model_input} → {expected_base} (fallback)")
            
            success_count += 1
        except Exception as e:
            print(f"❌ {model_input} 실패: {e}")
    
    print(f"\n결과: {success_count}/{len(test_cases)} 성공")
    return success_count == len(test_cases)


def main():
    """전체 테스트 실행"""
    print("\n" + "━"*60)
    print("🧪 Model Config System 통합 테스트")
    print("━"*60)
    
    tests = [
        ("YAML 로딩", test_yaml_loading),
        ("모델 설정 조회", test_model_config_query),
        ("API 파라미터 구성", test_api_params_building),
        ("Pro 모델 감지", test_pro_model_detection),
        ("ModelRouter 통합", test_model_router_integration),
        ("Prefix 폴백", test_prefix_fallback),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ {name} 테스트 실패: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # 결과 요약
    print("\n" + "━"*60)
    print("📊 테스트 결과 요약")
    print("━"*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print(f"\n총 결과: {passed}/{total} 통과 ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 모든 테스트 통과!")
        return 0
    else:
        print(f"\n⚠️ {total - passed}개 테스트 실패")
        return 1


if __name__ == "__main__":
    sys.exit(main())

