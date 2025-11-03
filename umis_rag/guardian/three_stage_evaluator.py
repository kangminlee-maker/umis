"""
Three-Stage Evaluator: Guardian Meta-RAG

3단계 평가 시스템:
- Stage 1: Weighted Scoring (빠름, 80%)
- Stage 2: Cross-Encoder (정밀, 15%)
- Stage 3: LLM + RAE (최종, 5%)
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.utils.logger import get_logger
from umis_rag.guardian.rae_memory import RAEMemory
from langchain_openai import ChatOpenAI
from umis_rag.core.config import settings

logger = get_logger(__name__)


@dataclass
class EvaluationResult:
    """평가 결과"""
    grade: str  # A/B/C/D
    score: float  # 0-1
    rationale: str
    evidence_ids: List[str]
    stage: str  # stage_1 / stage_2 / stage_3
    confidence: float  # 0-1


class ThreeStageEvaluator:
    """
    3-Stage 평가 시스템
    
    Stage 1 (빠름, 80%):
      자동 점수 계산으로 빠른 필터링
      
    Stage 2 (정밀, 15%):
      Cross-Encoder로 정밀 재평가
      
    Stage 3 (최종, 5%):
      LLM + RAE Index로 최종 판단
    
    사용:
    -----
    evaluator = ThreeStageEvaluator()
    
    result = evaluator.evaluate(deliverable)
    # → Stage 1로 대부분 처리
    # → 애매한 경우만 Stage 2, 3
    """
    
    def __init__(self):
        """초기화"""
        self.rae_memory = RAEMemory()
        self.llm = ChatOpenAI(
            model=settings.llm_model,
            temperature=0.3,  # 낮은 temperature (일관성)
            openai_api_key=settings.openai_api_key
        )
        
        logger.info("ThreeStageEvaluator 초기화")
        logger.info("  Stage 1: Weighted Scoring (자동)")
        logger.info("  Stage 2: Cross-Encoder (정밀)")
        logger.info("  Stage 3: LLM + RAE (최종)")
    
    def evaluate(
        self,
        deliverable: Dict[str, Any],
        force_stage: Optional[int] = None
    ) -> EvaluationResult:
        """
        3-Stage 평가 실행
        
        Args:
            deliverable: 평가 대상 산출물
            force_stage: 강제 Stage (테스트용)
        
        Returns:
            EvaluationResult
        """
        deliverable_id = deliverable.get('id', 'unknown')
        deliverable_content = deliverable.get('content', '')
        
        logger.info(f"[Guardian] 3-Stage 평가 시작: {deliverable_id}")
        
        # Stage 1: Weighted Scoring (빠름)
        if force_stage is None or force_stage == 1:
            stage1_result = self._stage1_weighted_scoring(deliverable)
            
            # 명확한 케이스면 Stage 1에서 종료 (80%)
            if stage1_result.confidence >= 0.90:
                logger.info(f"  ✅ Stage 1 확정: {stage1_result.grade} (신뢰도 {stage1_result.confidence:.2f})")
                return stage1_result
        
        # Stage 2: Cross-Encoder (정밀) - 15%
        if force_stage is None or force_stage == 2:
            stage2_result = self._stage2_cross_encoder(deliverable, stage1_result if force_stage is None else None)
            
            # 명확해지면 Stage 2에서 종료
            if stage2_result.confidence >= 0.85:
                logger.info(f"  ✅ Stage 2 확정: {stage2_result.grade} (신뢰도 {stage2_result.confidence:.2f})")
                return stage2_result
        
        # Stage 3: LLM + RAE (최종) - 5%
        logger.info(f"  🔄 Stage 3 (LLM + RAE) 필요 - 애매한 케이스")
        stage3_result = self._stage3_llm_rae(deliverable)
        logger.info(f"  ✅ Stage 3 최종: {stage3_result.grade} (신뢰도 {stage3_result.confidence:.2f})")
        
        return stage3_result
    
    def _stage1_weighted_scoring(self, deliverable: Dict[str, Any]) -> EvaluationResult:
        """
        Stage 1: Weighted Scoring (자동)
        
        체크리스트 기반 자동 점수 계산:
        - 명확성 (Clarity): 30%
        - 실행가능성 (Feasibility): 30%
        - 근거 (Evidence): 25%
        - 정량화 (Quantification): 15%
        """
        logger.info("  [Stage 1] Weighted Scoring 시작")
        
        content = deliverable.get('content', '')
        metadata = deliverable.get('metadata', {})
        
        scores = {}
        
        # 1. 명확성 (30%)
        clarity_score = 0.0
        if len(content) > 100:  # 충분한 설명
            clarity_score += 0.3
        if '목표' in content or 'target' in content.lower():  # 목표 명확
            clarity_score += 0.4
        if '전략' in content or 'strategy' in content.lower():  # 전략 있음
            clarity_score += 0.3
        
        scores['clarity'] = min(clarity_score, 1.0)
        
        # 2. 실행가능성 (30%)
        feasibility_score = 0.0
        if '시장' in content or 'market' in content.lower():  # 시장 언급
            feasibility_score += 0.3
        if '사례' in content or 'case' in content.lower():  # 사례 있음
            feasibility_score += 0.4
        if metadata.get('has_examples'):  # 메타데이터에 사례
            feasibility_score += 0.3
        
        scores['feasibility'] = min(feasibility_score, 1.0)
        
        # 3. 근거 (25%)
        evidence_score = 0.0
        evidence_ids = metadata.get('evidence_ids', [])
        if evidence_ids:
            evidence_score = min(len(evidence_ids) * 0.3, 1.0)
        
        scores['evidence'] = evidence_score
        
        # 4. 정량화 (15%)
        quant_score = 0.0
        if any(char.isdigit() for char in content):  # 숫자 있음
            quant_score += 0.5
        if '$' in content or '원' in content or 'SAM' in content:  # 금액/시장 크기
            quant_score += 0.5
        
        scores['quant'] = min(quant_score, 1.0)
        
        # 가중 평균
        total_score = (
            scores['clarity'] * 0.30 +
            scores['feasibility'] * 0.30 +
            scores['evidence'] * 0.25 +
            scores['quant'] * 0.15
        )
        
        # 등급 결정
        if total_score >= 0.85:
            grade = 'A'
            confidence = 0.95
        elif total_score >= 0.70:
            grade = 'B'
            confidence = 0.92
        elif total_score >= 0.50:
            grade = 'C'
            confidence = 0.88
        else:
            grade = 'D'
            confidence = 0.85
        
        # Rationale 생성
        rationale_parts = []
        if scores['clarity'] >= 0.7:
            rationale_parts.append("명확한 목표와 전략")
        if scores['feasibility'] >= 0.7:
            rationale_parts.append("실행 가능성 높음")
        if scores['evidence'] >= 0.5:
            rationale_parts.append(f"{len(evidence_ids)}개 근거 사례")
        if scores['quant'] >= 0.5:
            rationale_parts.append("정량화됨")
        
        rationale = ", ".join(rationale_parts) if rationale_parts else f"점수 {total_score:.2f}"
        
        logger.info(f"    점수: {total_score:.3f}, 등급: {grade}, 신뢰도: {confidence:.2f}")
        
        return EvaluationResult(
            grade=grade,
            score=total_score,
            rationale=rationale,
            evidence_ids=evidence_ids,
            stage='stage_1',
            confidence=confidence
        )
    
    def _stage2_cross_encoder(
        self,
        deliverable: Dict[str, Any],
        stage1_result: Optional[EvaluationResult]
    ) -> EvaluationResult:
        """
        Stage 2: Cross-Encoder (정밀 재평가)
        
        현재: 간소화 버전 (실제 Cross-Encoder는 별도 모델 필요)
        """
        logger.info("  [Stage 2] Cross-Encoder 정밀 평가")
        
        # Stage 1 결과 기반으로 재평가
        if stage1_result:
            # Stage 1 점수 조정 (더 엄격하게)
            adjusted_score = stage1_result.score * 0.95
            
            # 재등급화
            if adjusted_score >= 0.80:
                grade = 'A'
                confidence = 0.90
            elif adjusted_score >= 0.65:
                grade = 'B'
                confidence = 0.87
            elif adjusted_score >= 0.45:
                grade = 'C'
                confidence = 0.83
            else:
                grade = 'D'
                confidence = 0.80
            
            logger.info(f"    조정 점수: {adjusted_score:.3f}, 등급: {grade}")
            
            return EvaluationResult(
                grade=grade,
                score=adjusted_score,
                rationale=f"Stage 2 재평가: {stage1_result.rationale}",
                evidence_ids=stage1_result.evidence_ids,
                stage='stage_2',
                confidence=confidence
            )
        
        # Stage 1 없이 직접 실행 시
        return self._stage1_weighted_scoring(deliverable)
    
    def _stage3_llm_rae(self, deliverable: Dict[str, Any]) -> EvaluationResult:
        """
        Stage 3: LLM + RAE (최종 판단)
        
        - RAE Index에서 유사 평가 검색
        - LLM으로 최종 판단
        - 가장 신뢰도 높음
        """
        logger.info("  [Stage 3] LLM + RAE 최종 판단")
        
        deliverable_id = deliverable.get('id', 'unknown')
        deliverable_content = deliverable.get('content', '')
        
        # 1. RAE Index에서 유사 평가 검색
        similar_evals = self.rae_memory.find_similar_evaluations(deliverable_content)
        
        # 2. LLM 프롬프트 구성
        prompt = f"""
다음 기회 가설을 평가하세요.

가설:
{deliverable_content[:500]}

평가 기준:
1. 명확성: 목표와 전략이 명확한가?
2. 실행가능성: 실제로 실행 가능한가?
3. 근거: 충분한 근거가 있는가?
4. 정량화: 시장 크기 등이 정량화되었는가?

"""
        
        # 유사 평가가 있으면 참고
        if similar_evals:
            prompt += "\n과거 유사 평가:\n"
            for eval_data in similar_evals[:2]:
                prompt += f"- {eval_data['deliverable_id']}: {eval_data['grade']} ({eval_data['rationale'][:50]}...)\n"
            prompt += "\n위 평가와 일관성 있게 평가하세요.\n"
        
        prompt += """
응답 형식 (JSON):
{
  "grade": "A/B/C/D",
  "score": 0.0-1.0,
  "rationale": "평가 사유 (한 문장)"
}
"""
        
        # 3. LLM 평가
        try:
            response = self.llm.invoke(prompt)
            
            # JSON 파싱 (간단히)
            import json
            import re
            
            # JSON 블록 추출
            json_match = re.search(r'\{[^}]+\}', response.content, re.DOTALL)
            if json_match:
                result_data = json.loads(json_match.group())
                
                logger.info(f"    LLM 평가: {result_data.get('grade')} ({result_data.get('score', 0):.2f})")
                
                return EvaluationResult(
                    grade=result_data.get('grade', 'C'),
                    score=result_data.get('score', 0.5),
                    rationale=result_data.get('rationale', 'LLM 평가'),
                    evidence_ids=deliverable.get('metadata', {}).get('evidence_ids', []),
                    stage='stage_3',
                    confidence=0.98  # LLM + RAE = 최고 신뢰도
                )
        
        except Exception as e:
            logger.error(f"    ❌ LLM 평가 실패: {e}")
        
        # Fallback: Stage 1
        logger.warning("    ⚠️  Stage 3 실패 → Stage 1 Fallback")
        return self._stage1_weighted_scoring(deliverable)


# 예시 사용
if __name__ == "__main__":
    print("=" * 60)
    print("Three-Stage Evaluator 테스트")
    print("=" * 60)
    
    evaluator = ThreeStageEvaluator()
    
    # 테스트 가설
    test_deliverable = {
        'id': 'OPP-TEST-001',
        'content': '''
음악 스트리밍 시장에서 Freemium + 광고 모델 기회

목표: Spotify와 유사한 구독 + 광고 이중 수익화 모델
전략: 무료 사용자는 광고, 프리미엄은 구독으로 전환
시장 규모: 연 $10B
근거: Spotify 사례, YouTube Music 성공

실행 계획:
1. 무료 버전 출시
2. 광고 파트너 확보
3. 프리미엄 전환 유도
        ''',
        'metadata': {
            'evidence_ids': ['CAN-spotify-001', 'CAN-youtube-002'],
            'has_examples': True
        }
    }
    
    # 각 Stage 테스트
    print("\n[1] Stage 1: Weighted Scoring")
    result1 = evaluator.evaluate(test_deliverable, force_stage=1)
    print(f"  등급: {result1.grade}")
    print(f"  점수: {result1.score:.3f}")
    print(f"  신뢰도: {result1.confidence:.2f}")
    print(f"  사유: {result1.rationale}")
    
    print("\n[2] Stage 2: Cross-Encoder")
    result2 = evaluator.evaluate(test_deliverable, force_stage=2)
    print(f"  등급: {result2.grade}")
    print(f"  점수: {result2.score:.3f}")
    print(f"  신뢰도: {result2.confidence:.2f}")
    
    print("\n[3] Stage 3: LLM + RAE (실제 LLM 호출)")
    result3 = evaluator.evaluate(test_deliverable, force_stage=3)
    print(f"  등급: {result3.grade}")
    print(f"  점수: {result3.score:.3f}")
    print(f"  신뢰도: {result3.confidence:.2f}")
    print(f"  사유: {result3.rationale}")
    
    print("\n[4] 자동 Stage 선택")
    result_auto = evaluator.evaluate(test_deliverable)
    print(f"  선택된 Stage: {result_auto.stage}")
    print(f"  최종 등급: {result_auto.grade}")
    
    print("\n✅ Three-Stage Evaluator 작동 확인")

