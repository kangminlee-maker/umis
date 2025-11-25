#!/usr/bin/env python3
"""
Phase 4 응답 파싱 버그 수정 검증 테스트
v7.8.1: Structural Fix 적용

목적:
1. _parse_llm_response 메서드 테스트
2. _parse_llm_models 메서드 테스트 (JSON/YAML)
3. 실제 Phase 4 통합 테스트 (gpt-4o-mini, o1-mini)
"""

import os
import sys
from pathlib import Path

# 프로젝트 루트 경로 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# LLM_MODE 설정 (External LLM)
os.environ['LLM_MODE'] = 'gpt-4o-mini'

from dotenv import load_dotenv
load_dotenv()

from umis_rag.agents.estimator import EstimatorRAG
from umis_rag.agents.estimator.phase4_fermi import Phase4FermiDecomposition
from umis_rag.agents.estimator.models import Context

import time
from datetime import datetime


def test_parse_llm_response():
    """_parse_llm_response 메서드 단위 테스트"""
    
    print("\n" + "="*80)
    print("테스트 1: _parse_llm_response 메서드")
    print("="*80)
    
    from umis_rag.agents.estimator.phase3_guestimation import Phase3Guestimation
    
    # Phase4FermiDecomposition 인스턴스 생성
    phase3 = Phase3Guestimation()
    phase4 = Phase4FermiDecomposition(phase3_instance=phase3)
    
    # Mock 응답 객체 (Responses API)
    class MockOutputText:
        def __init__(self, text):
            self.text = text
            self.type = "text"
    
    class MockOutputMessage:
        def __init__(self, content):
            self.content = content
    
    class MockResponse:
        def __init__(self, output):
            self.output = output
    
    # 테스트 케이스 1: Responses API (리스트 구조)
    print("\n📝 테스트 1-1: Responses API (output[0].content[0].text)")
    mock_response = MockResponse(
        output=[
            MockOutputMessage(
                content=[
                    MockOutputText(text="테스트 응답 텍스트")
                ]
            )
        ]
    )
    
    result = phase4._parse_llm_response(mock_response, 'responses', depth=0)
    
    if result == "테스트 응답 텍스트":
        print("✅ 성공: 응답 파싱 정상")
    else:
        print(f"❌ 실패: {result}")
    
    # 테스트 케이스 2: Chat API
    print("\n📝 테스트 1-2: Chat API (choices[0].message.content)")
    
    class MockMessage:
        def __init__(self, content):
            self.content = content
    
    class MockChoice:
        def __init__(self, message):
            self.message = message
    
    class MockChatResponse:
        def __init__(self, choices):
            self.choices = choices
    
    mock_chat_response = MockChatResponse(
        choices=[
            MockChoice(
                message=MockMessage(content="채팅 응답 텍스트")
            )
        ]
    )
    
    result = phase4._parse_llm_response(mock_chat_response, 'chat', depth=0)
    
    if result == "채팅 응답 텍스트":
        print("✅ 성공: 채팅 응답 파싱 정상")
    else:
        print(f"❌ 실패: {result}")
    
    print("\n✅ 테스트 1 완료\n")


def test_parse_llm_models():
    """_parse_llm_models 메서드 단위 테스트 (JSON/YAML)"""
    
    print("\n" + "="*80)
    print("테스트 2: _parse_llm_models 메서드 (JSON/YAML)")
    print("="*80)
    
    from umis_rag.agents.estimator.phase3_guestimation import Phase3Guestimation
    
    phase3 = Phase3Guestimation()
    phase4 = Phase4FermiDecomposition(phase3_instance=phase3)
    
    # 테스트 케이스 1: JSON 블록
    print("\n📝 테스트 2-1: JSON 블록 파싱")
    
    json_response = """```json
{
    "models": [
        {
            "id": "TEST_001",
            "formula": "A = B * C",
            "description": "테스트 모형",
            "variables": [
                {"name": "A", "available": false},
                {"name": "B", "available": true},
                {"name": "C", "available": true}
            ]
        }
    ]
}
```"""
    
    models = phase4._parse_llm_models(json_response, depth=0)
    
    if len(models) == 1 and models[0].model_id == "TEST_001":
        print(f"✅ 성공: {len(models)}개 모형 파싱")
        print(f"   모형 ID: {models[0].model_id}")
        print(f"   공식: {models[0].formula}")
        print(f"   변수: {len(models[0].variables)}개")
    else:
        print(f"❌ 실패: {len(models)}개 모형")
    
    # 테스트 케이스 2: YAML 블록
    print("\n📝 테스트 2-2: YAML 블록 파싱")
    
    yaml_response = """```yaml
models:
  - id: TEST_002
    formula: "X = Y / Z"
    description: "YAML 테스트"
    variables:
      - name: X
        available: false
      - name: Y
        available: true
      - name: Z
        available: true
```"""
    
    models = phase4._parse_llm_models(yaml_response, depth=0)
    
    if len(models) == 1 and models[0].model_id == "TEST_002":
        print(f"✅ 성공: {len(models)}개 모형 파싱")
        print(f"   모형 ID: {models[0].model_id}")
        print(f"   공식: {models[0].formula}")
    else:
        print(f"❌ 실패: {len(models)}개 모형")
    
    print("\n✅ 테스트 2 완료\n")


def test_phase4_integration():
    """Phase 4 통합 테스트 (실제 API 호출)"""
    
    print("\n" + "="*80)
    print("테스트 3: Phase 4 통합 테스트 (실제 API)")
    print("="*80)
    
    # 현재 LLM_MODE 확인
    from umis_rag.core.config import settings
    print(f"\n📌 현재 LLM Mode: {settings.llm_mode}")
    
    # Estimator 생성
    estimator = EstimatorRAG()
    
    # 테스트 질문 (간단한 Phase 4 질문)
    questions = [
        "서울시 피아노 학원 수는?",
        "한국 성인 피아노 학습자는 몇 명?"
    ]
    
    results = []
    
    for idx, question in enumerate(questions, 1):
        print(f"\n{'='*80}")
        print(f"질문 {idx}/{len(questions)}: {question}")
        print(f"{'='*80}")
        
        start_time = time.time()
        
        try:
            result = estimator.estimate(question)
            elapsed = time.time() - start_time
            
            if result:
                print(f"\n✅ 성공 (Phase {result.phase})")
                print(f"   추정값: {result.value:,.0f} {result.unit}")
                print(f"   신뢰도: {result.confidence:.2f}")
                print(f"   소요시간: {elapsed:.1f}초")
                
                results.append({
                    'question': question,
                    'success': True,
                    'phase': result.phase,
                    'value': result.value,
                    'confidence': result.confidence,
                    'time': elapsed
                })
            else:
                print(f"\n❌ 실패: 결과 없음")
                results.append({
                    'question': question,
                    'success': False,
                    'time': elapsed
                })
        
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"\n❌ 오류: {e}")
            results.append({
                'question': question,
                'success': False,
                'error': str(e),
                'time': elapsed
            })
        
        # Rate limiting
        if idx < len(questions):
            time.sleep(2)
    
    # 결과 요약
    print("\n" + "="*80)
    print("테스트 3 결과 요약")
    print("="*80)
    
    success_count = sum(1 for r in results if r['success'])
    total_time = sum(r['time'] for r in results)
    
    print(f"\n총 테스트: {len(results)}개")
    print(f"성공: {success_count}개")
    print(f"실패: {len(results) - success_count}개")
    print(f"총 소요시간: {total_time:.1f}초")
    
    # Phase별 분포
    phase_counts = {}
    for r in results:
        if r['success']:
            phase = r['phase']
            phase_counts[phase] = phase_counts.get(phase, 0) + 1
    
    if phase_counts:
        print(f"\nPhase별 분포:")
        for phase in sorted(phase_counts.keys()):
            print(f"  Phase {phase}: {phase_counts[phase]}개")
    
    print("\n✅ 테스트 3 완료\n")
    
    return results


def main():
    """메인 실행"""
    
    print("\n" + "="*80)
    print("Phase 4 응답 파싱 버그 수정 검증 테스트")
    print("v7.8.1: Structural Fix")
    print("="*80)
    print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    start_time = time.time()
    
    # 테스트 1: _parse_llm_response
    try:
        test_parse_llm_response()
    except Exception as e:
        print(f"\n❌ 테스트 1 실패: {e}\n")
    
    # 테스트 2: _parse_llm_models
    try:
        test_parse_llm_models()
    except Exception as e:
        print(f"\n❌ 테스트 2 실패: {e}\n")
    
    # 테스트 3: Phase 4 통합 (실제 API)
    try:
        results = test_phase4_integration()
    except Exception as e:
        print(f"\n❌ 테스트 3 실패: {e}\n")
        results = []
    
    elapsed = time.time() - start_time
    
    print("\n" + "="*80)
    print("전체 테스트 완료")
    print("="*80)
    print(f"총 소요시간: {elapsed:.1f}초")
    print(f"종료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 최종 결론
    if results:
        success_rate = sum(1 for r in results if r['success']) / len(results) * 100
        print(f"\n🎯 Phase 4 성공률: {success_rate:.0f}%")
        
        if success_rate >= 80:
            print("✅ Structural Fix 성공! 응답 파싱 문제 해결됨")
        elif success_rate >= 50:
            print("⚠️  부분 개선, 추가 디버깅 필요")
        else:
            print("❌ 문제 지속, 추가 분석 필요")
    
    print("\n")


if __name__ == '__main__':
    main()


