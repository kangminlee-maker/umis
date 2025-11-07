"""
Hybrid Projector

Canonical → Projected 변환
- 90% config/projection_rules.yaml
- 10% LLM 판단
- LLM 로그 저장
"""

import yaml
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
from langchain_openai import ChatOpenAI

from umis_rag.core.schema import generate_id
from umis_rag.core.config import settings
from umis_rag.utils.logger import logger


class HybridProjector:
    """
    Hybrid Projection: 규칙 90% + LLM 10%
    """
    
    def __init__(self, rules_path: str = "config/projection_rules.yaml"):
        self.rules = self._load_rules(rules_path)
        self.llm = ChatOpenAI(
            model=settings.llm_model,
            temperature=settings.llm_temperature,
            openai_api_key=settings.openai_api_key
        )
        self.log_path = Path(self.rules.get('llm_log_path', 'data/llm_projection_log.jsonl'))
        
        logger.info("HybridProjector 초기화")
    
    def _load_rules(self, path: str) -> Dict:
        """config/projection_rules.yaml 로드"""
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def project(self, canonical_chunk: Dict) -> List[Dict]:
        """
        Canonical → Projected (Agent별)
        
        Args:
            canonical_chunk: Canonical 청크
        
        Returns:
            Projected 청크 리스트 (Agent별)
        """
        projected_chunks = []
        
        # Step 0: Chunk Type 체크 (v7.3.0+)
        chunk_type = canonical_chunk.get('metadata', {}).get('chunk_type') or canonical_chunk.get('chunk_type')
        
        # Chunk Type별 규칙 (learned_rule 등)
        if chunk_type:
            type_projections = self._apply_chunk_type_rules(canonical_chunk, chunk_type)
            if type_projections:
                projected_chunks.extend(type_projections)
                return projected_chunks  # Chunk Type 규칙이 있으면 종료
        
        # 기본 Agent 목록
        agents = ['observer', 'explorer', 'quantifier', 'validator', 'guardian']
        
        for agent in agents:
            # Step 1: 규칙 기반 (90%)
            should_project = self._apply_rules(canonical_chunk, agent)
            
            if should_project is None:
                # Step 2: LLM 판단 (10%)
                should_project = self._llm_decide(canonical_chunk, agent)
                
                # 로그 저장
                self._log_llm_decision(canonical_chunk, agent, should_project)
            
            # Step 3: Projected 생성
            if should_project:
                projected = self._create_projected(canonical_chunk, agent)
                projected_chunks.append(projected)
        
        return projected_chunks
    
    def _apply_chunk_type_rules(self, canonical: Dict, chunk_type: str) -> List[Dict]:
        """
        Chunk Type별 규칙 적용 (v7.3.0+)
        
        Args:
            canonical: Canonical 청크
            chunk_type: 청크 타입 (learned_rule 등)
        
        Returns:
            Projected 청크 리스트 (없으면 빈 리스트)
        """
        chunk_type_rules = self.rules.get('chunk_type_rules', {})
        
        if chunk_type not in chunk_type_rules:
            return []
        
        rule = chunk_type_rules[chunk_type]
        target_agents = rule.get('target_agents', [])
        
        if not target_agents:
            return []
        
        # Projected 청크 생성
        projected_chunks = []
        
        for agent in target_agents:
            projected = self._create_projected_with_mapping(
                canonical=canonical,
                agent=agent,
                rule=rule
            )
            projected_chunks.append(projected)
        
        logger.info(f"Chunk Type 규칙 적용: {chunk_type} → {target_agents}")
        
        return projected_chunks
    
    def _apply_rules(self, canonical: Dict, agent: str) -> bool:
        """
        규칙 기반 투영 판단
        
        Returns:
            True: 투영해야 함
            False: 투영 안 함
            None: 규칙 없음 (LLM 판단 필요)
        """
        field_rules = self.rules.get('field_rules', {})
        pattern_id = canonical.get('source_id', '')
        
        # 필드 규칙 확인
        for field_name, rule in field_rules.items():
            if field_name in pattern_id.lower() or field_name in str(canonical.get('content', '')).lower():
                agents = rule.get('agents', [])
                if agent in agents:
                    return True
        
        # 패턴별 기본 매핑
        pattern_defaults = self.rules.get('pattern_defaults', {})
        for pattern_key, pattern_rule in pattern_defaults.items():
            if pattern_key in pattern_id.lower():
                priority_agents = pattern_rule.get('priority_agents', [])
                if agent in priority_agents:
                    return True
        
        # 규칙 없음 → LLM
        return None
    
    def _llm_decide(self, canonical: Dict, agent: str) -> bool:
        """
        LLM으로 투영 판단
        """
        prompt = f"""
다음 사례/패턴을 {agent} Agent가 사용해야 하는지 판단하세요.

사례: {canonical.get('source_id')}
내용 (요약): {canonical.get('content', '')[:500]}

Agent 역할:
- observer: 시장 구조 관찰
- explorer: 기회 발굴
- quantifier: 정량 분석
- validator: 데이터 검증
- guardian: 품질 관리

이 사례가 {agent}에게 유용한가요?
응답: yes/no만
"""
        
        try:
            response = self.llm.invoke(prompt)
            decision = 'yes' in response.content.lower()
            return decision
        except Exception as e:
            logger.error(f"LLM 판단 실패: {e}")
            return False
    
    def _log_llm_decision(self, canonical: Dict, agent: str, decision: bool):
        """LLM 판단 로그"""
        log_entry = {
            'source_id': canonical.get('source_id'),
            'agent': agent,
            'decision': decision,
            'timestamp': datetime.now().isoformat()
        }
        
        # Append to log
        with open(self.log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
    
    def _create_projected(self, canonical: Dict, agent: str) -> Dict:
        """
        Projected 청크 생성 (schema 준수!)
        """
        projected_id = generate_id("PRJ", f"{canonical['source_id']}-{agent}")
        
        # Agent별 섹션 추출
        section_content = self._extract_agent_section(canonical, agent)
        
        return {
            'projected_chunk_id': projected_id,
            'source_id': canonical['source_id'],
            'agent_view': agent,
            'canonical_chunk_id': canonical['canonical_chunk_id'],
            'projection_method': 'rule',  # or 'llm'
            'domain': canonical['domain'],
            'version': canonical['version'],
            
            # TTL (v3.0)
            'materialization': {
                'strategy': 'on_demand',
                'cache_ttl_hours': 24,
                'persist_profile': None,
                'last_materialized_at': datetime.now().isoformat(),
                'access_count': 0
            },
            
            # Lineage (v3.0)
            'lineage': {
                'from': canonical['canonical_chunk_id'],
                'via': [
                    {
                        'step': 1,
                        'action': 'projection',
                        'rule_id': 'auto',
                        'chunk_id': projected_id
                    }
                ],
                'evidence_ids': [canonical['canonical_chunk_id']],
                'created_by': {
                    'agent': 'system',
                    'overlay_layer': 'core',
                    'tenant_id': None
                }
            },
            
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'content': section_content
        }
    
    def _extract_agent_section(self, canonical: Dict, agent: str) -> str:
        """
        Canonical에서 Agent별 섹션 추출
        
        anchor_path로 위치 찾기
        """
        sections = canonical.get('sections', [])
        
        # sections가 JSON 문자열이면 파싱
        if isinstance(sections, str):
            try:
                sections = json.loads(sections)
            except:
                sections = []
        
        for section in sections:
            if isinstance(section, dict) and section.get('agent_view') == agent:
                anchor = section.get('anchor_path')
                # 실제로는 anchor로 YAML 경로 파싱
                # 여기서는 간단히 전체 내용 반환
                return canonical.get('content', '')
        
        # 섹션 없으면 전체 반환
        return canonical.get('content', '')
    
    def _create_projected_with_mapping(
        self,
        canonical: Dict,
        agent: str,
        rule: Dict
    ) -> Dict:
        """
        Chunk Type 규칙 기반 Projected 생성 (v7.3.0+)
        
        metadata_mapping 적용
        """
        projected_id = generate_id("PRJ", f"{canonical.get('canonical_chunk_id', 'unknown')}-{agent}")
        
        # Metadata 매핑 적용
        metadata_mapping = rule.get('metadata_mapping', {})
        projected_metadata = {}
        
        canonical_metadata = canonical.get('metadata', {})
        
        for source_key, target_key in metadata_mapping.items():
            if source_key in canonical_metadata:
                projected_metadata[target_key] = canonical_metadata[source_key]
        
        # 기본 필드
        projected_metadata.update({
            'canonical_chunk_id': canonical.get('canonical_chunk_id'),
            'agent_view': agent,
            'projection_method': 'chunk_type_rule',
            'chunk_type': canonical_metadata.get('chunk_type')
        })
        
        # TTL 설정
        ttl = rule.get('ttl', 'on_demand')
        
        if ttl == 'persistent':
            materialization = {
                'strategy': 'persistent',
                'cache_ttl_hours': None,
                'persist_profile': 'always',
                'last_materialized_at': datetime.now().isoformat(),
                'access_count': 0
            }
        else:
            materialization = {
                'strategy': 'on_demand',
                'cache_ttl_hours': 24,
                'persist_profile': None,
                'last_materialized_at': datetime.now().isoformat(),
                'access_count': 0
            }
        
        return {
            'projected_chunk_id': projected_id,
            'agent_view': agent,
            'canonical_chunk_id': canonical.get('canonical_chunk_id'),
            'projection_method': 'chunk_type_rule',
            
            # Content
            'content': canonical.get('content', ''),
            
            # Metadata (매핑 적용)
            'metadata': projected_metadata,
            
            # TTL
            'materialization': materialization,
            
            # Lineage
            'lineage': {
                'from': canonical.get('canonical_chunk_id'),
                'via': [
                    {
                        'step': 1,
                        'action': 'projection',
                        'rule_id': f"chunk_type:{canonical_metadata.get('chunk_type')}",
                        'chunk_id': projected_id
                    }
                ],
                'evidence_ids': [canonical.get('canonical_chunk_id')],
                'created_by': {
                    'agent': 'system',
                    'overlay_layer': 'core',
                    'tenant_id': None
                }
            },
            
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }

