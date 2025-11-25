"""
v7.8.0 Model Config 시스템 Phase 4 테스트
- Phase 4 Fermi Decomposition 도달 테스트
- Model Config 시스템 작동 확인
"""

import os
import sys
import json
from datetime import datetime

sys.path.insert(0, os.path.abspath('.'))

from umis_rag.agents.estimator import EstimatorRAG

def test_phase4_model(model_name: str):
    """Phase 4 도달 테스트"""
    
    # Phase 4에 도달할 가능성이 높은 질문
    question = "서울시에 피아노 조율사는 몇 명이나 있을까?"
    
    print(f"\n{'='*70}")
    print(f"🧪 테스트: {model_name}")
    print(f"{'='*70}")
    print(f"질문: {question}")
    print()
    
    # .env 임시 변경
    original_model = os.environ.get('LLM_MODEL_PHASE4')
    os.environ['LLM_MODEL_PHASE4'] = model_name
    
    try:
        estimator = EstimatorRAG()
        
        print(f"⏳ {model_name} 추정 시작...")
        print(f"   (Validator에 데이터가 없으면 Phase 4로 진행됩니다)")
        start_time = datetime.now()
        
        result = estimator.estimate(question)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"\n✅ 추정 완료 (소요 시간: {duration:.2f}초)")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        if result:
            print(f"Phase: {result.phase}")
            print(f"값: {result.value}")
            print(f"단위: {result.unit}")
            
            if result.phase == 4:
                print(f"\n🎉 Phase 4 Fermi Decomposition 도달!")
                print(f"   → Model Config 시스템이 {model_name}을(를) 성공적으로 사용했습니다")
                
                if result.decomposition:
                    decomp = result.decomposition
                    print(f"\n분해 정보:")
                    print(f"  - 변수 수: {len(decomp.get('variables', []))}")
                    print(f"  - 모형 수: {len(decomp.get('models', []))}")
                    
                    if decomp.get('variables'):
                        print(f"\n변수들:")
                        for var in decomp['variables']:
                            print(f"    • {var.get('name', 'N/A')}: {var.get('value', 'N/A')} {var.get('unit', '')}")
                    
                    if decomp.get('models'):
                        print(f"\n모형들:")
                        for model in decomp['models']:
                            print(f"    • {model.get('formula', 'N/A')}")
            else:
                print(f"\n⚠️  Phase {result.phase}에서 완료 (Phase 4 미도달)")
                print(f"   → Validator나 다른 Phase에서 데이터를 찾았습니다")
        else:
            print("❌ 추정 실패")
        
        return {
            'model': model_name,
            'question': question,
            'success': result is not None,
            'phase': result.phase if result else None,
            'reached_phase4': result.phase == 4 if result else False,
            'value': result.value if result else None,
            'unit': result.unit if result else None,
            'duration': duration
        }
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return {
            'model': model_name,
            'question': question,
            'success': False,
            'error': str(e)
        }
    finally:
        if original_model:
            os.environ['LLM_MODEL_PHASE4'] = original_model

def main():
    print("\n" + "━"*70)
    print("🚀 v7.8.0 Model Config Phase 4 테스트")
    print("━"*70)
    
    # 테스트할 모델들
    test_models = [
        "o1-mini",      # Phase 4 기본 모델
        "gpt-5.1",      # 현재 .env 설정
    ]
    
    results = []
    
    for model_name in test_models:
        result = test_phase4_model(model_name)
        results.append(result)
        print("\n" + "-"*70)
    
    # 최종 요약
    print(f"\n\n{'='*70}")
    print("📊 Model Config 시스템 테스트 결과")
    print(f"{'='*70}\n")
    
    for result in results:
        model = result['model']
        success = "✅" if result['success'] else "❌"
        phase = result.get('phase', 'N/A')
        phase4 = "🎉 Phase 4!" if result.get('reached_phase4') else ""
        duration = result.get('duration', 0)
        
        print(f"{success} {model:15} | Phase: {phase:2} {phase4:15} | {duration:6.2f}초")
    
    # JSON 저장
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"test_phase4_model_config_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n💾 결과 저장: {filename}")
    
    # Phase 4 도달률
    phase4_count = sum(1 for r in results if r.get('reached_phase4'))
    total_count = len(results)
    
    print(f"\n🎯 Phase 4 도달률: {phase4_count}/{total_count}")
    
    if phase4_count > 0:
        print(f"✅ Model Config 시스템이 Phase 4에서 정상 작동합니다!")
    else:
        print(f"ℹ️  Phase 4에 도달하지 못했습니다 (Validator가 데이터를 찾았을 가능성)")
    
    return results

if __name__ == "__main__":
    main()




