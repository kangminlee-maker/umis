"""
Workflow Executor

routing_policy.yaml 기반 워크플로우 실행

FINAL_DECISION 03_routing_yaml 스펙:
- YAML에서 워크플로우 로드
- 조건부 실행 (when)
- Layer toggle 지원
- Fallback 정책
"""

import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional

import sys
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.utils.logger import get_logger
from umis_rag.core.condition_parser import ConditionParser

logger = get_logger(__name__)


class WorkflowExecutor:
    """
    YAML 기반 워크플로우 실행기
    
    사용:
    -----
    executor = WorkflowExecutor('routing_policy.yaml')
    
    result = executor.execute('explorer_workflow', {
        'triggers': "음악 스트리밍 구독"
    })
    """
    
    def __init__(self, policy_path: str = "routing_policy.yaml"):
        """
        Args:
            policy_path: routing_policy.yaml 경로
        """
        self.policy_path = Path(policy_path)
        self.policy = self._load_policy()
        self.condition_parser = ConditionParser()  # Phase 2: 고급 조건 파서
        
        logger.info(f"WorkflowExecutor 초기화: {policy_path}")
        logger.info(f"  Workflows: {list(self.policy.keys() if self.policy else [])}")
        logger.info(f"  ✅ Phase 2: 고급 조건 파서 활성화")
    
    def _load_policy(self) -> Dict[str, Any]:
        """routing_policy.yaml 로드"""
        if not self.policy_path.exists():
            logger.warning(f"  ⚠️  Policy 파일 없음: {self.policy_path}")
            return {}
        
        with open(self.policy_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def execute(
        self,
        workflow_name: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        워크플로우 실행
        
        Args:
            workflow_name: 워크플로우 이름 (explorer_workflow 등)
            context: 초기 컨텍스트 (triggers 등)
        
        Returns:
            실행 결과
        """
        if workflow_name not in self.policy:
            logger.error(f"  ❌ Workflow '{workflow_name}' 없음")
            return {}
        
        workflow = self.policy[workflow_name]
        logger.info(f"[Workflow] {workflow.get('name', workflow_name)} 시작")
        
        results = context.copy()
        
        # Steps 실행
        for step in workflow.get('steps', []):
            step_id = step['id']
            
            # 조건 체크
            if not self._should_run(step.get('when', 'always'), results):
                logger.info(f"  ⏭️  Step '{step_id}' 스킵 (조건 불충족)")
                continue
            
            logger.info(f"  🔄 Step '{step_id}': {step.get('name', step_id)}")
            
            # Step 실행
            try:
                result = self._run_step(step, results)
                results[step_id] = result
                logger.info(f"  ✅ Step '{step_id}' 완료")
            except Exception as e:
                if step.get('required', False):
                    logger.error(f"  ❌ Step '{step_id}' 실패 (필수): {e}")
                    raise
                else:
                    logger.warning(f"  ⚠️  Step '{step_id}' 실패 (선택): {e}")
                    results[step_id] = None
        
        logger.info(f"[Workflow] {workflow.get('name', workflow_name)} 완료")
        
        return results
    
    def _should_run(self, condition: str, context: Dict[str, Any]) -> bool:
        """
        실행 조건 평가 (Phase 2: 고급 조건 지원)
        
        Args:
            condition: 조건 문자열
                - Simple: "always", "never"
                - Comparison: "count > 5", "confidence >= 0.7"
                - Logical: "A AND B", "A OR B", "NOT A"
                - Deep ref: "patterns[0].metadata.confidence >= 0.8"
            context: 현재 컨텍스트
        
        Returns:
            실행 여부
        """
        try:
            # Named condition (routing_policy.yaml의 conditions 섹션)
            if condition in self.policy.get('conditions', {}):
                cond_def = self.policy['conditions'][condition]
                # check 필드가 있으면 재귀 평가
                if 'check' in cond_def:
                    return self.condition_parser.evaluate(cond_def['check'], context)
                # 없으면 default
                return cond_def.get('default', False)
            
            # ConditionParser로 평가 (Phase 2)
            return self.condition_parser.evaluate(condition, context)
            
        except Exception as e:
            logger.warning(f"  ⚠️  조건 평가 실패: {condition} - {e}")
            # Phase 2: 에러 시 기본값 (안전)
            return self.policy.get('execution', {}).get('error_default', False)
    
    def _run_step(
        self,
        step: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Any:
        """
        Step 실행 (실제 로직은 외부 함수 호출)
        
        Args:
            step: Step 정의
            context: 현재 컨텍스트
        
        Returns:
            Step 결과
        """
        # 실제로는 여기서 Agent 메서드를 호출
        # 지금은 간단히 시뮬레이션
        
        method = step.get('method')
        step_input = step.get('input')
        
        # Input 파싱
        input_value = self._parse_input(step_input, context)
        
        # 실제 메서드 호출은 여기서
        # 예: explorer.search_patterns(input_value)
        
        # 지금은 시뮬레이션 결과 반환
        return {
            'method': method,
            'input': input_value,
            'simulated': True
        }
    
    def _parse_input(
        self,
        input_def: Any,
        context: Dict[str, Any]
    ) -> Any:
        """
        Input 정의를 실제 값으로 변환
        
        Args:
            input_def: Input 정의 (triggers, patterns[0].id 등)
            context: 컨텍스트
        
        Returns:
            실제 값
        """
        if isinstance(input_def, str):
            # 단순 변수 참조
            if '[' not in input_def and '.' not in input_def:
                return context.get(input_def)
            
            # patterns[0].id 같은 경로
            # 간단히 처리
            return input_def
        
        elif isinstance(input_def, list):
            # 여러 변수
            return [context.get(var, None) for var in input_def]
        
        return input_def
    
    def get_layer_config(self) -> Dict[str, bool]:
        """
        Layer 활성화 설정 조회
        
        Returns:
            Layer별 활성화 상태
        """
        return self.policy.get('layer_toggle', {})
    
    def get_fallback_policy(self, layer: str) -> Dict[str, str]:
        """
        특정 Layer의 Fallback 정책 조회
        
        Args:
            layer: Layer 이름 (vector, graph, memory)
        
        Returns:
            Fallback 정책
        """
        fallback = self.policy.get('fallback', {})
        key = f"{layer}_fail"
        
        if key in fallback:
            return {
                'action': fallback[key].get('action'),
                'message': fallback[key].get('message')
            }
        
        return {'action': 'skip', 'message': f'{layer} 실패 - 계속 진행'}


# 예시 사용
if __name__ == "__main__":
    print("=" * 60)
    print("WorkflowExecutor 테스트")
    print("=" * 60)
    
    executor = WorkflowExecutor('routing_policy.yaml')
    
    # Layer 설정 확인
    print("\n[1] Layer 설정")
    layers = executor.get_layer_config()
    for layer, enabled in layers.items():
        status = "✅ ON" if enabled else "❌ OFF"
        print(f"  {layer}: {status}")
    
    # Fallback 정책 확인
    print("\n[2] Fallback 정책")
    for layer in ['vector', 'graph', 'memory']:
        policy = executor.get_fallback_policy(layer)
        print(f"  {layer} 실패 시: {policy['action']}")
    
    # Workflow 실행 (시뮬레이션)
    print("\n[3] Explorer Workflow 실행 (시뮬레이션)")
    
    result = executor.execute('explorer_workflow', {
        'triggers': "음악 스트리밍 구독 시장",
        'patterns': [
            {'id': 'subscription_model', 'count': 1}
        ]
    })
    
    print(f"\n실행 완료:")
    for step_id, step_result in result.items():
        if isinstance(step_result, dict) and step_result.get('simulated'):
            print(f"  {step_id}: {step_result.get('method')} (시뮬레이션)")
    
    print("\n✅ WorkflowExecutor 작동 확인")

