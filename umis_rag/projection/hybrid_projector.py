"""
Hybrid Projector

Canonical → Projected 변환
- 90% projection_rules.yaml
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
from umis_rag.utils.logger import logger


class HybridProjector:
    """
    Hybrid Projection: 규칙 90% + LLM 10%
    """
    
    def __init__(self, rules_path: str = "projection_rules.yaml"):
        self.rules = self._load_rules(rules_path)
        self.llm = ChatOpenAI(model="gpt-4-turbo-preview", temperature=0.7)
        self.log_path = Path(self.rules.get('llm_log_path', 'llm_projection_log.jsonl'))
        
        logger.info("HybridProjector 초기화")
    
    def _load_rules(self, path: str) -> Dict:
        """projection_rules.yaml 로드"""
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def project(self, canonical_chunk: Dict) -> List[Dict]:
        """
        Canonical → Projected (6개 Agent)
        
        Args:
            canonical_chunk: Canonical 청크
        
        Returns:
            Projected 청크 리스트 (Agent별)
        """
        projected_chunks = []
        
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
        
        for section in sections:
            if section.get('agent_view') == agent:
                anchor = section.get('anchor_path')
                # 실제로는 anchor로 YAML 경로 파싱
                # 여기서는 간단히 전체 내용 반환
                return canonical.get('content', '')
        
        # 섹션 없으면 전체 반환
        return canonical.get('content', '')

