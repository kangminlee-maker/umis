"""
Rule Learner: LLM 로그에서 자동 규칙 학습

FINAL_DECISION 01_projection 스펙:
- LLM 판단 로그 분석
- 반복 패턴 발견
- 자동 규칙 생성
- config/projection_rules.yaml 업데이트

효과: LLM 10% → 1% (90% 절감)
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Tuple
from collections import defaultdict
import yaml

import sys
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.utils.logger import get_logger

logger = get_logger(__name__)


class RuleLearner:
    """
    LLM 로그에서 규칙 학습
    
    워크플로우:
    1. data/llm_projection_log.jsonl 읽기
    2. 패턴 분석 (source_id x agent → decision)
    3. 신뢰도 계산 (consistency)
    4. 규칙 생성 (>= 80% 일관성)
    5. config/projection_rules.yaml 업데이트
    """
    
    def __init__(
        self,
        log_path: str = "data/llm_projection_log.jsonl",
        consistency_threshold: float = 0.80,
        min_samples: int = 3
    ):
        """
        Args:
            log_path: LLM 로그 파일 경로
            consistency_threshold: 규칙 생성 최소 일관성 (0.80)
            min_samples: 규칙 생성 최소 샘플 수 (3개)
        """
        self.log_path = Path(log_path)
        self.consistency_threshold = consistency_threshold
        self.min_samples = min_samples
        
        logger.info(f"RuleLearner 초기화")
        logger.info(f"  로그: {log_path}")
        logger.info(f"  일관성 임계값: {consistency_threshold}")
        logger.info(f"  최소 샘플: {min_samples}")
    
    def load_logs(self) -> List[Dict[str, Any]]:
        """
        LLM 로그 로드
        
        Returns:
            로그 엔트리 리스트
        """
        if not self.log_path.exists():
            logger.warning(f"  ⚠️  로그 파일 없음: {self.log_path}")
            return []
        
        logs = []
        with open(self.log_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    logs.append(json.loads(line))
        
        logger.info(f"  ✅ {len(logs)}개 로그 로드")
        return logs
    
    def analyze_patterns(
        self,
        logs: List[Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """
        패턴 분석: source_id x agent → decision 통계
        
        Args:
            logs: LLM 로그 엔트리
        
        Returns:
            {
                "source_id": {
                    "agent": {
                        "yes_count": int,
                        "no_count": int,
                        "total": int,
                        "consistency": float,
                        "decision": bool
                    }
                }
            }
        """
        logger.info(f"  패턴 분석 중...")
        
        # source_id x agent → decision 집계
        stats = defaultdict(lambda: defaultdict(lambda: {'yes': 0, 'no': 0}))
        
        for entry in logs:
            source_id = entry.get('source_id', '')
            agent = entry.get('agent', '')
            decision = entry.get('decision', False)
            
            if decision:
                stats[source_id][agent]['yes'] += 1
            else:
                stats[source_id][agent]['no'] += 1
        
        # 일관성 계산
        patterns = {}
        
        for source_id, agents in stats.items():
            patterns[source_id] = {}
            
            for agent, counts in agents.items():
                total = counts['yes'] + counts['no']
                yes_count = counts['yes']
                no_count = counts['no']
                
                # 일관성 = max(yes, no) / total
                consistency = max(yes_count, no_count) / total if total > 0 else 0
                
                # 최종 판단 = 더 많은 쪽
                decision = yes_count > no_count
                
                patterns[source_id][agent] = {
                    'yes_count': yes_count,
                    'no_count': no_count,
                    'total': total,
                    'consistency': consistency,
                    'decision': decision
                }
        
        logger.info(f"  ✅ {len(patterns)}개 source_id 패턴 분석")
        
        return patterns
    
    def extract_rules(
        self,
        patterns: Dict[str, Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        패턴에서 규칙 추출
        
        Args:
            patterns: analyze_patterns() 결과
        
        Returns:
            학습된 규칙 리스트
        """
        logger.info(f"  규칙 추출 중...")
        
        learned_rules = []
        
        for source_id, agents in patterns.items():
            # Agent별로 일관성 체크
            high_confidence_agents = []
            
            for agent, stats in agents.items():
                # 일관성과 샘플 수 체크
                if (stats['consistency'] >= self.consistency_threshold and
                    stats['total'] >= self.min_samples and
                    stats['decision']):  # yes 판단만
                    
                    high_confidence_agents.append(agent)
            
            # 규칙 생성
            if high_confidence_agents:
                # source_id에서 키워드 추출
                # 예: "amazon_prime_success_case" → "amazon_prime"
                keywords = self._extract_keywords(source_id)
                
                rule = {
                    'source_pattern': source_id,
                    'keywords': keywords,
                    'agents': high_confidence_agents,
                    'learned_from_llm': True,
                    'confidence': min([agents[a]['consistency'] for a in high_confidence_agents]),
                    'sample_count': min([agents[a]['total'] for a in high_confidence_agents])
                }
                
                learned_rules.append(rule)
        
        logger.info(f"  ✅ {len(learned_rules)}개 규칙 추출")
        
        return learned_rules
    
    def _extract_keywords(self, source_id: str) -> List[str]:
        """
        source_id에서 키워드 추출
        
        Args:
            source_id: 소스 ID
        
        Returns:
            키워드 리스트
        """
        # 간단한 키워드 추출 (_, - 기준으로 split)
        parts = source_id.lower().replace('_', ' ').replace('-', ' ').split()
        
        # 불용어 제거
        stopwords = ['case', 'success', 'example', 'pattern', 'model', 'the', 'a', 'an']
        keywords = [p for p in parts if p not in stopwords and len(p) > 2]
        
        return keywords[:3]  # 상위 3개만
    
    def generate_yaml_rules(
        self,
        learned_rules: List[Dict[str, Any]]
    ) -> str:
        """
        학습된 규칙을 YAML 형식으로 변환
        
        Args:
            learned_rules: extract_rules() 결과
        
        Returns:
            YAML 문자열
        """
        yaml_rules = {
            '_meta': {
                'learned_from_llm': True,
                'auto_generated': True,
                'total_rules': len(learned_rules)
            },
            'learned_rules': {}
        }
        
        for rule in learned_rules:
            # 키워드 기반 룰 이름 생성
            rule_name = '_'.join(rule['keywords']) if rule['keywords'] else rule['source_pattern']
            
            yaml_rules['learned_rules'][rule_name] = {
                'agents': rule['agents'],
                'keywords': rule['keywords'],
                'confidence': round(rule['confidence'], 3),
                'sample_count': rule['sample_count'],
                'source_pattern': rule['source_pattern']
            }
        
        return yaml.dump(yaml_rules, allow_unicode=True, sort_keys=False)
    
    def learn_and_save(
        self,
        output_path: str = "learned_config/projection_rules.yaml"
    ) -> Dict[str, Any]:
        """
        전체 학습 프로세스 실행 및 저장
        
        Args:
            output_path: 저장할 파일 경로
        
        Returns:
            {
                'total_logs': int,
                'patterns_found': int,
                'rules_learned': int,
                'saved_to': str
            }
        """
        logger.info("=" * 60)
        logger.info("Learning Loop 시작")
        logger.info("=" * 60)
        
        # 1. 로그 로드
        logs = self.load_logs()
        
        if not logs:
            logger.warning("  ⚠️  로그 없음 - 학습 불가")
            return {
                'total_logs': 0,
                'patterns_found': 0,
                'rules_learned': 0,
                'saved_to': None
            }
        
        # 2. 패턴 분석
        patterns = self.analyze_patterns(logs)
        
        # 3. 규칙 추출
        rules = self.extract_rules(patterns)
        
        # 4. YAML 생성
        yaml_content = self.generate_yaml_rules(rules)
        
        # 5. 파일 저장
        output_file = Path(output_path)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(yaml_content)
        
        logger.info("=" * 60)
        logger.info("Learning Loop 완료")
        logger.info("=" * 60)
        logger.info(f"  총 로그: {len(logs)}")
        logger.info(f"  패턴: {len(patterns)}")
        logger.info(f"  학습된 규칙: {len(rules)}")
        logger.info(f"  저장: {output_file}")
        logger.info("=" * 60)
        
        # 6. 규칙 미리보기
        if rules:
            logger.info("\n학습된 규칙 미리보기:")
            for i, rule in enumerate(rules[:5], 1):
                logger.info(f"  {i}. {rule['source_pattern']}")
                logger.info(f"     Agents: {', '.join(rule['agents'])}")
                logger.info(f"     Confidence: {rule['confidence']:.3f}")
        
        return {
            'total_logs': len(logs),
            'patterns_found': len(patterns),
            'rules_learned': len(rules),
            'saved_to': str(output_file)
        }


# 편의 함수
def learn_from_logs(
    log_path: str = "data/llm_projection_log.jsonl",
    output_path: str = "learned_config/projection_rules.yaml"
) -> Dict[str, Any]:
    """
    편의 함수: 로그에서 규칙 학습
    
    Args:
        log_path: LLM 로그 파일
        output_path: 출력 YAML 파일
    
    Returns:
        학습 결과
    """
    learner = RuleLearner(log_path=log_path)
    return learner.learn_and_save(output_path)


# 예시 사용
if __name__ == "__main__":
    # 테스트 로그 생성
    print("=" * 60)
    print("Learning Loop 테스트")
    print("=" * 60)
    
    # 1. 샘플 로그 생성 (테스트용)
    sample_logs = [
        # churn_rate는 항상 explorer, quantifier
        {"source_id": "churn_rate_analysis", "agent": "explorer", "decision": True, "timestamp": "2025-11-03T01:00:00Z"},
        {"source_id": "churn_rate_analysis", "agent": "explorer", "decision": True, "timestamp": "2025-11-03T02:00:00Z"},
        {"source_id": "churn_rate_analysis", "agent": "explorer", "decision": True, "timestamp": "2025-11-03T03:00:00Z"},
        {"source_id": "churn_rate_analysis", "agent": "quantifier", "decision": True, "timestamp": "2025-11-03T01:00:00Z"},
        {"source_id": "churn_rate_analysis", "agent": "quantifier", "decision": True, "timestamp": "2025-11-03T02:00:00Z"},
        {"source_id": "churn_rate_analysis", "agent": "quantifier", "decision": True, "timestamp": "2025-11-03T03:00:00Z"},
        {"source_id": "churn_rate_analysis", "agent": "observer", "decision": False, "timestamp": "2025-11-03T01:00:00Z"},
        
        # platform_case는 항상 explorer, observer
        {"source_id": "platform_business_model_case", "agent": "explorer", "decision": True, "timestamp": "2025-11-03T01:00:00Z"},
        {"source_id": "platform_business_model_case", "agent": "explorer", "decision": True, "timestamp": "2025-11-03T02:00:00Z"},
        {"source_id": "platform_business_model_case", "agent": "explorer", "decision": True, "timestamp": "2025-11-03T03:00:00Z"},
        {"source_id": "platform_business_model_case", "agent": "observer", "decision": True, "timestamp": "2025-11-03T01:00:00Z"},
        {"source_id": "platform_business_model_case", "agent": "observer", "decision": True, "timestamp": "2025-11-03T02:00:00Z"},
        {"source_id": "platform_business_model_case", "agent": "observer", "decision": True, "timestamp": "2025-11-03T03:00:00Z"},
    ]
    
    # 샘플 로그 저장
    log_file = Path("test_data/llm_projection_log.jsonl")
    with open(log_file, 'w', encoding='utf-8') as f:
        for log in sample_logs:
            f.write(json.dumps(log, ensure_ascii=False) + '\n')
    
    print(f"\n✅ 샘플 로그 생성: {len(sample_logs)}개")
    
    # 2. 학습 실행
    print("\n학습 시작...")
    result = learn_from_logs(
        log_path=str(log_file),
        output_path="test_learned_rules.yaml"
    )
    
    # 3. 결과 확인
    print(f"\n결과:")
    print(f"  총 로그: {result['total_logs']}")
    print(f"  패턴: {result['patterns_found']}")
    print(f"  학습된 규칙: {result['rules_learned']}")
    print(f"  저장: {result['saved_to']}")
    
    # 4. 학습된 규칙 확인
    if result['saved_to']:
        print(f"\n학습된 규칙 내용:")
        with open(result['saved_to'], 'r', encoding='utf-8') as f:
            print(f.read())
    
    # 5. 정리
    log_file.unlink()
    if Path(result['saved_to']).exists():
        Path(result['saved_to']).unlink()
    
    print("\n✅ 테스트 완료 (임시 파일 삭제됨)")

