"""
v7.8.0 Model Config 시스템 실전 테스트
- 실제 Fermi Decomposition 실행
- 여러 모델 비교 (gpt-5.1, o1-mini, gpt-4o-mini)
"""

import os
import sys
import json
from datetime import datetime

# UMIS 경로 추가
sys.path.insert(0, os.path.abspath('.'))

from umis_rag.agents.estimator import EstimatorRAG

def test_fermi_with_model(question: str, model_name: str):
    """특정 모델로 Fermi 추정 테스트"""
    
    print(f"\n{'='*70}")
    print(f"🧪 테스트: {model_name}")
    print(f"{'='*70}")
    print(f"질문: {question}")
    print()
    
    # .env 임시 변경
    original_model = os.environ.get('LLM_MODEL_PHASE4')
    os.environ['LLM_MODEL_PHASE4'] = model_name
    
    try:
        # EstimatorRAG 인스턴스 생성
        estimator = EstimatorRAG()
        
        # 추정 실행
        print(f"⏳ {model_name} 추정 시작...")
        start_time = datetime.now()
        
        result = estimator.estimate(question)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # 결과 출력
        print(f"\n✅ 추정 완료 (소요 시간: {duration:.2f}초)")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        if result:
            # dataclass 속성으로 접근
            print(f"Phase: {result.phase}")
            print(f"값: {result.value}")
            print(f"단위: {result.unit}")
            
            if result.phase == 4 and result.decomposition:
                decomp = result.decomposition
                print(f"\n분해 정보:")
                print(f"  - 변수 수: {len(decomp.get('variables', []))}")
                print(f"  - 모형 수: {len(decomp.get('models', []))}")
                print(f"  - 사용된 변수: {len(decomp.get('used_variables', []))}")
                
                # 변수 출력
                if decomp.get('variables'):
                    print(f"\n주요 변수:")
                    for var in decomp['variables'][:3]:  # 처음 3개만
                        print(f"    • {var.get('name', 'N/A')}: {var.get('value', 'N/A')} {var.get('unit', '')}")
                
                # 모형 출력
                if decomp.get('models'):
                    print(f"\n수학 모형:")
                    for model in decomp['models'][:2]:  # 처음 2개만
                        print(f"    • {model.get('formula', 'N/A')}")
        else:
            print("❌ 추정 실패")
        
        return {
            'model': model_name,
            'success': result is not None,
            'phase': result.phase if result else None,
            'value': result.value if result else None,
            'unit': result.unit if result else None,
            'duration': duration,
            'result': str(result) if result else None  # dataclass를 문자열로 변환
        }
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return {
            'model': model_name,
            'success': False,
            'error': str(e),
            'duration': 0
        }
    finally:
        # .env 복원
        if original_model:
            os.environ['LLM_MODEL_PHASE4'] = original_model
        else:
            os.environ.pop('LLM_MODEL_PHASE4', None)

def main():
    """메인 테스트 실행"""
    
    print("\n" + "━"*70)
    print("🚀 v7.8.0 Model Config 시스템 실전 테스트")
    print("━"*70)
    
    # 테스트 질문
    question = "한국에서 연간 소비되는 샴푸 양은?"
    
    # 테스트할 모델들
    test_models = [
        ("gpt-4o-mini", "빠른 테스트 (Phase 4 도달 가능성 낮음)"),
        ("o1-mini", "Phase 4 기본 모델"),
        ("gpt-5.1", "Phase 4 현재 설정 (.env)"),
    ]
    
    results = []
    
    for model_name, description in test_models:
        print(f"\n\n{'#'*70}")
        print(f"# {description}")
        print(f"{'#'*70}")
        
        result = test_fermi_with_model(question, model_name)
        results.append(result)
    
    # 최종 요약
    print(f"\n\n{'='*70}")
    print("📊 테스트 결과 요약")
    print(f"{'='*70}\n")
    
    for result in results:
        model = result['model']
        success = "✅" if result['success'] else "❌"
        phase = result.get('phase', 'N/A')
        duration = result.get('duration', 0)
        
        print(f"{success} {model:20} | Phase: {phase:10} | 시간: {duration:6.2f}초")
    
    # JSON 저장
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"test_model_config_live_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n💾 결과 저장: {filename}")
    
    # 성공률 계산
    success_count = sum(1 for r in results if r['success'])
    total_count = len(results)
    success_rate = (success_count / total_count * 100) if total_count > 0 else 0
    
    print(f"\n✅ 성공률: {success_count}/{total_count} ({success_rate:.1f}%)")
    
    return results

if __name__ == "__main__":
    main()




