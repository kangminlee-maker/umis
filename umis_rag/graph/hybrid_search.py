"""
Hybrid Search: Vector + Graph 통합 검색

Vector RAG (유사성) + Knowledge Graph (관계성) = 강력한 인사이트

사용 흐름:
1. Vector 검색으로 유사 패턴 찾기
2. Graph로 조합/대안 확장
3. Confidence 기반 정렬
4. 종합 결과 반환
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

from umis_rag.graph.connection import Neo4jConnection
from umis_rag.graph.confidence_calculator import ConfidenceCalculator
from umis_rag.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class PatternMatch:
    """Vector 검색 결과"""
    pattern_id: str
    content: str
    score: float  # Vector similarity
    metadata: Dict[str, Any]


@dataclass
class PatternCombination:
    """Graph 확장 결과"""
    source_pattern: str
    target_pattern: str
    relationship_type: str
    synergy: str
    confidence: Dict[str, Any]
    evidence_ids: List[str]


@dataclass
class HybridResult:
    """Hybrid 검색 최종 결과"""
    direct_matches: List[PatternMatch]
    combinations: List[PatternCombination]
    insights: List[str]


class HybridSearch:
    """
    Vector + Graph Hybrid 검색
    
    핵심 기능:
    - Vector 검색으로 직접 매칭
    - Graph 확장으로 조합 발견
    - Multi-Dimensional Confidence로 정렬
    - 인사이트 자동 생성
    """
    
    def __init__(
        self,
        graph_connection: Optional[Neo4jConnection] = None,
        min_vector_score: float = 0.7,
        min_confidence: float = 0.6
    ):
        """
        Args:
            graph_connection: Neo4j 연결 (없으면 자동 생성)
            min_vector_score: Vector 검색 최소 점수
            min_confidence: Graph 관계 최소 신뢰도
        """
        self.graph = graph_connection or Neo4jConnection()
        self.confidence_calc = ConfidenceCalculator()
        self.min_vector_score = min_vector_score
        self.min_confidence = min_confidence
        
        logger.info(f"HybridSearch initialized (vector>={min_vector_score}, confidence>={min_confidence})")
    
    def search(
        self,
        vector_results: List[Tuple[Any, float]],
        max_combinations: int = 10,
        relationship_types: Optional[List[str]] = None
    ) -> HybridResult:
        """
        Hybrid 검색 실행
        
        Args:
            vector_results: Vector 검색 결과 [(document, score), ...]
            max_combinations: 최대 조합 수
            relationship_types: 검색할 관계 유형 (None이면 전체)
        
        Returns:
            HybridResult (직접 매칭 + 조합)
        """
        logger.info(f"Starting hybrid search with {len(vector_results)} vector results")
        
        # 1. Vector 결과 파싱
        direct_matches = self._parse_vector_results(vector_results)
        logger.info(f"  Direct matches: {len(direct_matches)}")
        
        # 2. Graph 확장
        combinations = self._expand_with_graph(
            direct_matches,
            max_combinations,
            relationship_types
        )
        logger.info(f"  Combinations found: {len(combinations)}")
        
        # 3. 인사이트 생성
        insights = self._generate_insights(direct_matches, combinations)
        logger.info(f"  Insights generated: {len(insights)}")
        
        return HybridResult(
            direct_matches=direct_matches,
            combinations=combinations,
            insights=insights
        )
    
    def _parse_vector_results(
        self,
        vector_results: List[Tuple[Any, float]]
    ) -> List[PatternMatch]:
        """Vector 검색 결과를 PatternMatch로 변환"""
        matches = []
        
        for doc, score in vector_results:
            if score < self.min_vector_score:
                continue
            
            # 메타데이터에서 pattern_id 추출
            pattern_id = None
            metadata = {}
            
            if hasattr(doc, 'metadata'):
                metadata = doc.metadata
                pattern_id = metadata.get('explorer_pattern_id') or metadata.get('pattern_id')
            
            # pattern_id가 없으면 content에서 추출 시도
            if not pattern_id:
                content = doc.page_content if hasattr(doc, 'page_content') else str(doc)
                # 간단한 패턴 매칭 (개선 가능)
                if 'platform' in content.lower():
                    pattern_id = 'platform_business_model'
                elif 'subscription' in content.lower():
                    pattern_id = 'subscription_model'
                # ... 다른 패턴들
            
            if pattern_id:
                matches.append(PatternMatch(
                    pattern_id=pattern_id,
                    content=doc.page_content if hasattr(doc, 'page_content') else str(doc),
                    score=score,
                    metadata=metadata
                ))
        
        return matches
    
    def _expand_with_graph(
        self,
        direct_matches: List[PatternMatch],
        max_combinations: int,
        relationship_types: Optional[List[str]]
    ) -> List[PatternCombination]:
        """Graph로 조합 발견"""
        combinations = []
        
        # 각 직접 매칭에 대해 Graph 확장
        for match in direct_matches:
            pattern_combinations = self._find_pattern_combinations(
                match.pattern_id,
                relationship_types
            )
            combinations.extend(pattern_combinations)
        
        # Confidence로 정렬
        combinations.sort(
            key=lambda x: x.confidence.get('overall', 0),
            reverse=True
        )
        
        # 최대 개수 제한
        return combinations[:max_combinations]
    
    def _find_pattern_combinations(
        self,
        pattern_id: str,
        relationship_types: Optional[List[str]]
    ) -> List[PatternCombination]:
        """특정 패턴의 조합 찾기"""
        
        # Cypher 쿼리: 패턴의 모든 관계 찾기
        if relationship_types:
            type_filter = f"AND r.relationship_type IN {relationship_types}"
        else:
            type_filter = ""
        
        query = f"""
        MATCH (source:Pattern {{pattern_id: $pattern_id}})-[r:RELATIONSHIP]-(target:Pattern)
        WHERE 1=1 {type_filter}
        RETURN 
            source.pattern_id as source,
            target.pattern_id as target,
            r.relationship_type as rel_type,
            r.synergy as synergy,
            r.confidence as confidence,
            r.evidence_ids as evidence_ids,
            r.description as description
        ORDER BY toFloat(r.confidence) DESC
        """
        
        try:
            results = self.graph.execute_query(query, {'pattern_id': pattern_id})
            
            combinations = []
            for row in results:
                # Confidence 파싱 (문자열로 저장되어 있을 수 있음)
                confidence_str = row.get('confidence', '{}')
                try:
                    # eval은 위험하지만, 여기서는 우리가 저장한 데이터이므로 안전
                    confidence = eval(confidence_str) if isinstance(confidence_str, str) else confidence_str
                except:
                    confidence = {'overall': 0.5}
                
                # 최소 신뢰도 필터
                if confidence.get('overall', 0) < self.min_confidence:
                    continue
                
                combinations.append(PatternCombination(
                    source_pattern=row['source'],
                    target_pattern=row['target'],
                    relationship_type=row['rel_type'],
                    synergy=row.get('synergy', ''),
                    confidence=confidence,
                    evidence_ids=row.get('evidence_ids', []),
                ))
            
            return combinations
            
        except Exception as e:
            logger.error(f"Failed to find combinations for {pattern_id}: {e}")
            return []
    
    def _generate_insights(
        self,
        direct_matches: List[PatternMatch],
        combinations: List[PatternCombination]
    ) -> List[str]:
        """인사이트 자동 생성"""
        insights = []
        
        # 1. 직접 매칭 인사이트
        if direct_matches:
            top_match = direct_matches[0]
            insights.append(
                f"🎯 가장 유사한 패턴: {top_match.pattern_id} (유사도 {top_match.score:.2f})"
            )
        
        # 2. 조합 인사이트
        if combinations:
            # 가장 강력한 조합
            top_combo = combinations[0]
            insights.append(
                f"💡 최고 조합: {top_combo.source_pattern} + {top_combo.target_pattern} "
                f"({top_combo.relationship_type}, 신뢰도 {top_combo.confidence.get('overall', 0):.2f})"
            )
            
            # 관계 유형별 통계
            rel_types = {}
            for combo in combinations:
                rel_type = combo.relationship_type
                rel_types[rel_type] = rel_types.get(rel_type, 0) + 1
            
            if rel_types:
                insights.append(
                    f"📊 발견된 관계 유형: {', '.join([f'{k}({v})' for k, v in rel_types.items()])}"
                )
        
        # 3. Evidence 통계
        all_evidence = set()
        for combo in combinations:
            all_evidence.update(combo.evidence_ids)
        
        if all_evidence:
            insights.append(
                f"📚 참고 사례: {len(all_evidence)}개 (예: {', '.join(list(all_evidence)[:3])}...)"
            )
        
        return insights
    
    def search_by_pattern_id(
        self,
        pattern_id: str,
        max_combinations: int = 10
    ) -> HybridResult:
        """
        패턴 ID로 직접 검색
        
        Args:
            pattern_id: 검색할 패턴 ID
            max_combinations: 최대 조합 수
        
        Returns:
            HybridResult
        """
        logger.info(f"Searching combinations for pattern: {pattern_id}")
        
        # 직접 매칭은 해당 패턴 자체
        direct_matches = [
            PatternMatch(
                pattern_id=pattern_id,
                content=f"Pattern: {pattern_id}",
                score=1.0,
                metadata={'pattern_id': pattern_id}
            )
        ]
        
        # Graph 확장
        combinations = self._expand_with_graph(
            direct_matches,
            max_combinations,
            None
        )
        
        # 인사이트 생성
        insights = self._generate_insights(direct_matches, combinations)
        
        return HybridResult(
            direct_matches=direct_matches,
            combinations=combinations,
            insights=insights
        )
    
    def explain_combination(
        self,
        source: str,
        target: str
    ) -> Optional[Dict[str, Any]]:
        """
        특정 조합의 상세 설명
        
        Args:
            source: 소스 패턴
            target: 타겟 패턴
        
        Returns:
            관계 상세 정보
        """
        query = """
        MATCH (s:Pattern {pattern_id: $source})-[r:RELATIONSHIP]-(t:Pattern {pattern_id: $target})
        RETURN 
            r.relationship_type as rel_type,
            r.synergy as synergy,
            r.description as description,
            r.confidence as confidence,
            r.evidence_ids as evidence,
            r.provenance as provenance
        """
        
        try:
            results = self.graph.execute_query(
                query,
                {'source': source, 'target': target}
            )
            
            if results:
                row = results[0]
                confidence_str = row.get('confidence', '{}')
                confidence = eval(confidence_str) if isinstance(confidence_str, str) else confidence_str
                
                return {
                    'source': source,
                    'target': target,
                    'relationship_type': row['rel_type'],
                    'synergy': row['synergy'],
                    'description': row.get('description', ''),
                    'confidence': confidence,
                    'evidence': row.get('evidence', []),
                    'provenance': row.get('provenance', {})
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to explain combination {source}-{target}: {e}")
            return None


def print_hybrid_results(result: HybridResult):
    """Hybrid 검색 결과를 보기 좋게 출력"""
    print("\n" + "=" * 60)
    print("Hybrid Search Results")
    print("=" * 60)
    
    # Direct Matches
    print(f"\n📍 Direct Matches ({len(result.direct_matches)}):")
    for i, match in enumerate(result.direct_matches[:5], 1):
        print(f"  {i}. {match.pattern_id} (유사도: {match.score:.3f})")
    
    # Combinations
    print(f"\n🔗 Combinations ({len(result.combinations)}):")
    for i, combo in enumerate(result.combinations[:10], 1):
        conf = combo.confidence.get('overall', 0)
        print(f"  {i}. {combo.source_pattern} -[{combo.relationship_type}]-> {combo.target_pattern}")
        print(f"     시너지: {combo.synergy}")
        print(f"     신뢰도: {conf:.2f}")
        if combo.evidence_ids:
            print(f"     증거: {', '.join(combo.evidence_ids[:2])}")
        print()
    
    # Insights
    print(f"\n💡 Insights ({len(result.insights)}):")
    for insight in result.insights:
        print(f"  • {insight}")
    
    print("\n" + "=" * 60 + "\n")


# 편의 함수
def search_patterns(
    vector_results: List[Tuple[Any, float]],
    **kwargs
) -> HybridResult:
    """
    편의 함수: Vector 결과로 Hybrid 검색
    
    Args:
        vector_results: Vector 검색 결과
        **kwargs: HybridSearch 초기화 인자
    
    Returns:
        HybridResult
    """
    with Neo4jConnection() as conn:
        searcher = HybridSearch(graph_connection=conn, **kwargs)
        return searcher.search(vector_results)


def search_by_id(
    pattern_id: str,
    max_combinations: int = 10,
    min_confidence: float = 0.6
) -> HybridResult:
    """
    편의 함수: 패턴 ID로 직접 검색
    
    Args:
        pattern_id: 패턴 ID
        max_combinations: 최대 조합 수
        min_confidence: 최소 신뢰도
    
    Returns:
        HybridResult
    """
    with Neo4jConnection() as conn:
        searcher = HybridSearch(graph_connection=conn, min_confidence=min_confidence)
        return searcher.search_by_pattern_id(pattern_id, max_combinations)


# 예시 사용
if __name__ == "__main__":
    # Example: Platform 패턴의 조합 검색
    print("Example: Platform Business Model 조합 검색\n")
    
    result = search_by_id("platform_business_model", max_combinations=5)
    print_hybrid_results(result)
    
    # Example: Subscription 패턴
    print("\n" + "=" * 60)
    print("Example: Subscription Model 조합 검색\n")
    
    result2 = search_by_id("subscription_model", max_combinations=5)
    print_hybrid_results(result2)

