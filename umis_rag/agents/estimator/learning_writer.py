"""
Guestimation v3.0 - Learning Writer
Phase 3/4 결과를 Canonical Index에 저장하여 학습하는 시스템 구현
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
import hashlib
import json

from .models import (
    EstimationResult,
    Context,
    LearnedRule,
    ValueEstimate,
    SoftGuide,
    SourceType
)


class LearningWriter:
    """
    학습된 규칙을 Canonical Index에 저장
    
    역할:
    1. Phase 3/4 결과 → LearnedRule 변환
    2. Canonical Index에 저장 (chunk_type="learned_rule")
    3. Projection 트리거 (자동)
    
    학습 조건:
    - confidence >= 0.80
    - evidence_count >= 2
    - 충돌 없음
    """
    
    def __init__(
        self,
        canonical_collection,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Args:
            canonical_collection: ChromaDB Canonical Collection
            config: 학습 설정 (threshold 등)
        """
        self.canonical = canonical_collection
        self.config = config or self._default_config()
    
    def _default_config(self) -> Dict[str, Any]:
        """기본 설정"""
        return {
            'min_confidence': 0.80,
            'min_evidence_count': 2,  # 일반 케이스
            'min_evidence_high_confidence': 1,  # confidence >= 0.90
            'high_confidence_threshold': 0.90,
            'enable_learning': True,
            'auto_projection': True
        }
    
    def save_learned_rule(
        self,
        question: str,
        result: EstimationResult,
        context: Context,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        학습된 규칙을 Canonical에 저장
        
        Args:
            question: 원본 질문
            result: Phase 3/4 판단 결과
            context: 맥락 (domain, region, time 등)
            metadata: 추가 메타데이터
        
        Returns:
            rule_id: "RULE-{DOMAIN}-{HASH}" 형식
            
        Example:
            >>> writer = LearningWriter(canonical_collection)
            >>> rule_id = writer.save_learned_rule(
            ...     question="SaaS Churn Rate는?",
            ...     result=estimation_result,
            ...     context=Context(domain="B2B_SaaS")
            ... )
            >>> print(rule_id)
            "RULE-B2B_SAAS-abc123"
        """
        
        # 1. 학습 가치 판단
        if not self.should_learn(result):
            return None
        
        # 2. Rule ID 생성
        rule_id = self._generate_rule_id(question, context)
        
        # 3. Canonical Chunk 생성
        canonical_chunk = self._create_canonical_chunk(
            rule_id=rule_id,
            question=question,
            result=result,
            context=context,
            metadata=metadata
        )
        
        # 4. Canonical에 저장
        self.canonical.add(
            ids=[canonical_chunk['id']],
            documents=[canonical_chunk['content']],
            metadatas=[canonical_chunk['metadata']]
        )
        
        return rule_id
    
    def should_learn(self, result: EstimationResult) -> bool:
        """
        학습 가치 판단 (Confidence 기반 유연화)
        
        조건:
        1. confidence >= 0.80
        2. evidence_count:
           - confidence >= 0.90: 1개 OK (매우 높은 신뢰도)
           - confidence >= 0.80: 2개 필요 (일반)
        3. 충돌 없음
        
        Args:
            result: 판단 결과
        
        Returns:
            bool: 학습할 가치가 있으면 True
        """
        
        if not self.config['enable_learning']:
            return False
        
        # Confidence 체크
        if result.confidence < self.config['min_confidence']:
            return False
        
        # Evidence 개수 체크 (Confidence 기반 유연화)
        if result.confidence >= self.config['high_confidence_threshold']:
            # 매우 높은 신뢰도 (>= 0.90): 증거 1개도 OK
            min_evidence = self.config['min_evidence_high_confidence']
        else:
            # 일반 신뢰도 (0.80~0.89): 증거 2개 필요
            min_evidence = self.config['min_evidence_count']
        
        if len(result.value_estimates) < min_evidence:
            return False
        
        # 충돌 체크 (있으면 학습 안 함)
        if result.conflicts_detected and not result.conflicts_resolved:
            return False
        
        return True
    
    def _generate_rule_id(self, question: str, context: Context) -> str:
        """
        Rule ID 생성
        
        형식: "RULE-{DOMAIN}-{HASH}"
        
        Example:
            "RULE-B2B_SAAS-a1b2c3"
            "RULE-FOOD_SERVICE-d4e5f6"
        """
        
        # Domain 정규화
        domain = context.domain or "GENERAL"
        domain_clean = domain.upper().replace(" ", "_")
        
        # Hash 생성 (질문 + 맥락)
        hash_input = f"{question}:{context.domain}:{context.region}:{context.time_period}"
        hash_value = hashlib.sha256(hash_input.encode()).hexdigest()[:6]
        
        return f"RULE-{domain_clean}-{hash_value}"
    
    def _create_canonical_chunk(
        self,
        rule_id: str,
        question: str,
        result: EstimationResult,
        context: Context,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Canonical Chunk 생성
        
        Returns:
            {
                'id': "CAN-rule-...",
                'content': "질문:\n값:\n증거:...",
                'metadata': {...}
            }
        """
        
        # Canonical ID
        canonical_id = f"CAN-rule-{rule_id.lower()}"
        
        # Content 생성 (자연어)
        content = self._format_content(question, result, context)
        
        # Metadata 생성
        chunk_metadata = self._create_metadata(
            rule_id=rule_id,
            result=result,
            context=context,
            user_metadata=metadata
        )
        
        return {
            'id': canonical_id,
            'content': content,
            'metadata': chunk_metadata
        }
    
    def _format_content(
        self,
        question: str,
        result: EstimationResult,
        context: Context
    ) -> str:
        """
        자연어 Content 생성
        
        Example:
            질문: "B2B SaaS Churn Rate는?"
            값: 6%
            범위: 5-7%
            신뢰도: 0.85
            
            맥락:
              - domain: B2B_SaaS
              - time_period: 2024
            
            증거:
              1. 통계 패턴: 정규분포 [5%, 7%], mean=6%
              2. RAG 벤치마크: "5-7%" (3개)
              3. Physical: 백분율 [0, 100]
            
            판단 전략: weighted_average
        """
        
        lines = []
        
        # 질문
        lines.append(f"질문: \"{question}\"")
        
        # 값
        if result.value:
            lines.append(f"값: {result.value}")
        
        if result.value_range:
            min_val, max_val = result.value_range
            lines.append(f"범위: {min_val}-{max_val}")
        
        # 신뢰도
        lines.append(f"신뢰도: {result.confidence:.2f}")
        
        # 맥락
        if context.domain or context.region or context.time_period:
            lines.append("\n맥락:")
            if context.domain:
                lines.append(f"  - domain: {context.domain}")
            if context.region:
                lines.append(f"  - region: {context.region}")
            if context.time_period:
                lines.append(f"  - time_period: {context.time_period}")
        
        # 증거
        if result.value_estimates:
            lines.append("\n증거:")
            for i, estimate in enumerate(result.value_estimates, 1):
                lines.append(f"  {i}. {estimate.source_type.value}: {estimate.value}")
                if estimate.reasoning:
                    lines.append(f"     ({estimate.reasoning})")
        
        # Soft Guides
        if result.soft_guides:
            lines.append("\nSoft Constraints:")
            for guide in result.soft_guides:
                guide_desc = guide.insight or str(guide.suggested_range) or ""
                lines.append(f"  - {guide.source_type.value}: {guide_desc}")
        
        # 판단 전략
        if result.judgment_strategy:
            lines.append(f"\n판단 전략: {result.judgment_strategy}")
        
        return "\n".join(lines)
    
    def _create_metadata(
        self,
        rule_id: str,
        result: EstimationResult,
        context: Context,
        user_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Metadata 생성 (검색용 + Projection용)
        
        Returns:
            {
                # 타입
                'chunk_type': 'learned_rule',
                'rule_type': 'learned',
                
                # 값
                'value': 0.06,
                'unit': 'percentage',
                'confidence': 0.85,
                
                # 맥락
                'domain': 'B2B_SaaS',
                'region': null,
                'time_period': '2024',
                
                # 증거
                'evidence_sources': ['statistical', 'rag', ...],
                'evidence_count': 5,
                'judgment_strategy': 'weighted_average',
                
                # 통계
                'usage_count': 1,
                'created_at': '2024-11-07T10:30:00',
                'last_used': '2024-11-07T10:30:00',
                
                # Projection
                'sections': [...],
                
                # 사용자 추가
                ...user_metadata
            }
        """
        
        now = datetime.now().isoformat()
        
        metadata = {
            # 타입
            'chunk_type': 'learned_rule',
            'rule_type': 'learned',
            'rule_id': rule_id,
            
            # 값
            'value': result.value if result.value else None,
            'unit': result.unit if hasattr(result, 'unit') else None,
            'confidence': result.confidence,
            
            # 맥락
            'domain': context.domain,
            'region': context.region,
            'time_period': context.time_period,
            
            # 증거 (Chroma는 metadata에 list 불가 → JSON string)
            'evidence_sources': json.dumps([est.source_type.value for est in result.value_estimates]),
            'evidence_count': len(result.value_estimates),
            'judgment_strategy': result.judgment_strategy,
            
            # 통계
            'usage_count': 1,
            'created_at': now,
            'last_used': now,
            'last_verified': datetime.now().date().isoformat(),
            
            # Projection용 sections
            'sections': json.dumps([{
                'agent_view': 'estimator',
                'anchor_path': f'learned_rules.{rule_id.lower()}',
                'content_hash': self._content_hash(result)
            }])
        }
        
        # 범위
        if result.value_range:
            metadata['range_min'] = result.value_range[0]
            metadata['range_max'] = result.value_range[1]
        
        # 사용자 메타데이터 병합
        if user_metadata:
            metadata.update(user_metadata)
        
        # Chroma는 metadata에 None 허용 안함 → 제거
        metadata = {k: v for k, v in metadata.items() if v is not None}
        
        return metadata
    
    def _content_hash(self, result: EstimationResult) -> str:
        """Content Hash 생성"""
        content_str = f"{result.value}:{result.confidence}"
        return f"sha256:{hashlib.sha256(content_str.encode()).hexdigest()[:16]}"
    
    def update_usage(self, rule_id: str):
        """
        사용 통계 업데이트
        
        Args:
            rule_id: 규칙 ID
        """
        
        # TODO: Canonical에서 규칙 찾아서 usage_count 증가
        # ChromaDB update() 사용
        
        pass
    
    def get_learning_stats(self) -> Dict[str, Any]:
        """
        학습 통계 조회
        
        Returns:
            {
                'total_rules': 150,
                'by_domain': {'B2B_SaaS': 45, 'Food_Service': 30, ...},
                'avg_confidence': 0.87,
                'recent_learned': [...]
            }
        """
        
        # TODO: Canonical에서 learned_rule 타입 통계
        
        return {
            'total_rules': 0,
            'by_domain': {},
            'avg_confidence': 0.0
        }


class UserContribution:
    """
    사용자 기여 파이프라인
    
    3가지 타입:
    1. 확정 사실: 즉시 저장 (confidence=1.0)
    2. 업계 상식: 임시 저장 → 검증 후 확정
    3. 개인 경험: 참고용 (낮은 confidence)
    """
    
    def __init__(self, learning_writer: LearningWriter):
        self.learning_writer = learning_writer
    
    def add_definite_fact(
        self,
        question: str,
        value: float,
        unit: str,
        context: Optional[Context] = None,
        source: str = "user_confirmed"
    ) -> str:
        """
        확정 사실 즉시 저장
        
        Example:
            >>> contribution.add_definite_fact(
            ...     question="우리 회사 직원 수는?",
            ...     value=150,
            ...     unit="명",
            ...     source="HR 시스템"
            ... )
        """
        
        # EstimationResult 생성 (confidence=1.0)
        result = EstimationResult(
            question=question,
            value=value,
            unit=unit,
            confidence=1.0,
            value_estimates=[
                ValueEstimate(
                    source_type=SourceType.DEFINITE_DATA,
                    value=value,
                    confidence=1.0,
                    reasoning="사용자 확정 사실",
                    source_detail=source
                )
            ],
            judgment_strategy="user_definite_fact"
        )
        
        # 맥락 생성
        if context is None:
            context = Context(domain="user_specific")
        
        # 저장
        rule_id = self.learning_writer.save_learned_rule(
            question=question,
            result=result,
            context=context,
            metadata={'source_type': 'definite_fact'}
        )
        
        return rule_id
    
    def add_domain_knowledge(
        self,
        question: str,
        value: float,
        context: Context,
        source: str = "domain_expert"
    ) -> str:
        """
        업계 상식 저장 (검증 대기)
        
        TODO: 검증 로직 (3회 일치 → 확정)
        """
        
        # 검증 대기 (confidence 0.90 → 증거 1개로 학습 가능)
        result = EstimationResult(
            question=question,
            value=value,
            confidence=0.90,  # 높은 신뢰도 (증거 1개 OK)
            value_estimates=[
                ValueEstimate(
                    source_type=SourceType.DEFINITE_DATA,
                    value=value,
                    confidence=0.90,
                    source_detail=source,
                    reasoning="업계 상식 (검증 대기)"
                )
            ],
            judgment_strategy="domain_knowledge_pending"
        )
        
        rule_id = self.learning_writer.save_learned_rule(
            question=question,
            result=result,
            context=context,
            metadata={'source_type': 'domain_knowledge', 'verified': False}
        )
        
        return rule_id
    
    def add_personal_experience(
        self,
        question: str,
        value: float,
        context_description: str
    ) -> str:
        """
        개인 경험 저장 (참고용)
        
        낮은 confidence, 검색 시 참고만
        """
        
        result = EstimationResult(
            question=question,
            value=value,
            confidence=0.40,  # 낮음
            value_estimates=[
                ValueEstimate(
                    source_type=SourceType.DEFINITE_DATA,
                    value=value,
                    confidence=0.40,
                    reasoning=context_description
                )
            ],
            judgment_strategy="personal_reference"
        )
        
        context = Context(domain="personal")
        
        rule_id = self.learning_writer.save_learned_rule(
            question=question,
            result=result,
            context=context,
            metadata={'source_type': 'personal_experience'}
        )
        
        return rule_id

