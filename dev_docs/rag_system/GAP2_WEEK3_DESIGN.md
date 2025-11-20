# Gap #2 Week 3: Phase2ValidatorSearchEnhanced 설계
**작성일**: 2025-11-12
**목표**: 컨텍스트 기반 Validator 검색으로 정확도 향상
**예상 코드**: ~500줄

---

## 📋 구현 목표

### 현재 Phase 2 (Simple)
```python
# 현재 (기본 검색)
def search_in_validator(query):
    results = validator.search_definite_data(query)
    return results

문제:
  - 컨텍스트 활용 부족
  - 산업/규모/모델 고려 안 함
  - Confidence 계산 없음
```

### 개선된 Phase 2 (Enhanced)
```python
# 개선 (컨텍스트 기반)
def search_with_context(query, context):
    # 1. 산업별 벤치마크 검색
    # 2. 기업 규모 조정
    # 3. 매출 규모 조정
    # 4. 세부 카테고리 조정
    # 5. Confidence 계산
    return EstimationResult(
        value=adjusted_margin,
        confidence=confidence_score,
        phase='phase_2_enhanced',
        reasoning_detail={...}
    )

효과:
  - 정확도: ±30% → ±10-15%
  - Confidence: 명확한 점수
  - 추적 가능성: 조정 과정 투명
```

---

## 🎯 클래스 구조

### Phase2ValidatorSearchEnhanced
```python
class Phase2ValidatorSearchEnhanced:
    """
    컨텍스트 기반 Validator 검색 (강화 버전)
    
    개선 사항:
    1. Industry-specific search (산업별 검색)
    2. Company size adjustment (규모 조정)
    3. Revenue scale adjustment (매출 조정)
    4. Business model matching (모델 매칭)
    5. Confidence scoring (신뢰도 계산)
    
    데이터 소스:
    - profit_margin_benchmarks Collection (100개)
    - 83개 신뢰할 수 있는 출처
    """
    
    def __init__(self, validator_rag):
        self.validator = validator_rag
        self.benchmark_store = None  # ChromaDB collection
        
    def search_with_context(
        self,
        query: str,
        context: Dict[str, Any]
    ) -> Optional[EstimationResult]:
        """
        컨텍스트 기반 마진 검색
        
        Args:
            query: "뷰티 D2C 기업 영업이익률은?"
            context: {
                'industry': '커머스',
                'sub_category': 'Beauty D2C',
                'business_model': '자체 브랜드',
                'company_size': 'scaleup',
                'revenue': '50억',
                'price_positioning': 'premium',
                'region': '한국'
            }
        
        Returns:
            EstimationResult or None (Phase 3로)
        """
        
    def _search_industry_benchmarks(self, industry, sub_category, business_model):
        """산업별 벤치마크 검색 (우선순위 매칭)"""
        
    def _adjust_by_company_size(self, base_margin, company_size, size_patterns):
        """기업 규모별 마진 조정"""
        
    def _adjust_by_revenue(self, margin, revenue, revenue_patterns):
        """매출 규모별 마진 조정"""
        
    def _adjust_by_subcategory(self, margin, sub_category, category_patterns):
        """세부 카테고리별 마진 조정"""
        
    def _calculate_confidence(self, data_quality, sample_size, recency, context_match):
        """신뢰도 점수 계산"""
        
    def _calculate_context_match(self, context, benchmark):
        """컨텍스트 매칭 점수 계산"""
        
    def _parse_revenue(self, revenue_string):
        """매출 문자열 파싱 ("50억" → 5000000000)"""
```

---

## 🔍 주요 메서드 설계

### 1. search_with_context()
```python
def search_with_context(self, query: str, context: Dict) -> Optional[EstimationResult]:
    # Step 1: Industry-specific 벤치마크 검색
    benchmark = self._search_industry_benchmarks(
        industry=context.get('industry'),
        sub_category=context.get('sub_category'),
        business_model=context.get('business_model')
    )
    
    if not benchmark:
        return None  # Phase 3로
    
    # Step 2: Base margin 추출
    base_margin = benchmark['margins']['operating_margin']['median']
    
    # Step 3: Company size adjustment
    size_adjusted = self._adjust_by_company_size(
        base_margin=base_margin,
        company_size=context.get('company_size'),
        size_patterns=benchmark.get('by_company_size')
    )
    
    # Step 4: Revenue scale adjustment
    revenue_adjusted = self._adjust_by_revenue(
        margin=size_adjusted,
        revenue=context.get('revenue'),
        revenue_patterns=benchmark.get('by_revenue_scale')
    )
    
    # Step 5: Subcategory adjustment
    final_margin = self._adjust_by_subcategory(
        margin=revenue_adjusted,
        sub_category=context.get('sub_category'),
        category_patterns=benchmark.get('by_category')
    )
    
    # Step 6: Confidence 계산
    confidence = self._calculate_confidence(
        data_quality=benchmark.get('reliability'),
        sample_size=benchmark.get('sample_size'),
        recency=benchmark.get('year'),
        context_match_score=self._calculate_context_match(context, benchmark)
    )
    
    return EstimationResult(
        value=final_margin,
        confidence=confidence,
        phase='phase_2_enhanced',
        reasoning_detail={...}
    )
```

---

### 2. _search_industry_benchmarks()
```python
def _search_industry_benchmarks(
    self,
    industry: str,
    sub_category: str = None,
    business_model: str = None
) -> Optional[Dict]:
    """
    산업별 마진율 벤치마크 검색
    
    검색 우선순위:
    1. Exact match (industry + sub_category + model)
    2. Industry + sub_category
    3. Industry only
    
    Returns:
        benchmark data or None
    """
    
    # RAG 검색 쿼리 생성
    search_queries = []
    
    # Query 1: 정확 매칭
    if industry and sub_category and business_model:
        search_queries.append(
            f"{industry} {sub_category} {business_model} operating margin"
        )
    
    # Query 2: Industry + sub
    if industry and sub_category:
        search_queries.append(
            f"{industry} {sub_category} margin"
        )
    
    # Query 3: Industry only
    if industry:
        search_queries.append(
            f"{industry} operating margin benchmark"
        )
    
    # RAG 검색 실행
    for query in search_queries:
        results = self.benchmark_store.similarity_search(
            query, k=3
        )
        
        for result in results:
            reliability = result.metadata.get('reliability')
            if reliability in ['high', 'medium']:
                return self._parse_benchmark_data(result)
    
    return None
```

---

### 3. _adjust_by_company_size()
```python
def _adjust_by_company_size(
    self,
    base_margin: float,
    company_size: str,
    size_patterns: Dict
) -> float:
    """
    기업 규모에 따른 마진 조정
    
    Logic:
    - seed/early: Base - 10%p (초기 적자)
    - growth: Base - 5%p
    - scaleup: Base (평균)
    - scale: Base + 5%p (규모 경제)
    - enterprise: Base + 8%p
    """
    
    if not company_size or not size_patterns:
        return base_margin
    
    # 표준 조정값
    adjustments = {
        'seed': -0.10,
        'startup': -0.08,
        'early_stage': -0.05,
        'growth': -0.03,
        'scaleup': 0.00,
        'scale': +0.05,
        'enterprise': +0.08,
        'large_enterprise': +0.10
    }
    
    # 벤치마크에 size_patterns가 있으면 우선 사용
    if size_patterns and company_size in size_patterns:
        pattern = size_patterns[company_size]
        if isinstance(pattern, dict) and 'operating_margin' in pattern:
            return pattern['operating_margin']
    
    # 없으면 표준 조정값 사용
    adjustment = adjustments.get(company_size, 0.00)
    
    return base_margin + adjustment
```

---

### 4. _calculate_confidence()
```python
def _calculate_confidence(
    self,
    data_quality: str,
    sample_size: int,
    recency: int,
    context_match_score: float
) -> float:
    """
    신뢰도 점수 계산
    
    Factors:
    - 데이터 품질 (0.3)
    - 샘플 크기 (0.3)
    - 최신성 (0.2)
    - 컨텍스트 매칭 (0.2)
    
    Returns:
        0.0-1.0 점수
    """
    
    # 1. 데이터 품질 점수
    quality_score = {
        'high': 1.0,
        'medium': 0.8,
        'low': 0.5
    }.get(data_quality, 0.5)
    
    # 2. 샘플 크기 점수
    if sample_size >= 100:
        size_score = 1.0
    elif sample_size >= 50:
        size_score = 0.8
    elif sample_size >= 20:
        size_score = 0.6
    else:
        size_score = 0.4
    
    # 3. 최신성 점수
    current_year = 2025
    years_old = current_year - recency
    
    if years_old <= 1:
        recency_score = 1.0
    elif years_old <= 3:
        recency_score = 0.9
    elif years_old <= 5:
        recency_score = 0.7
    else:
        recency_score = 0.5
    
    # 4. 가중 평균
    confidence = (
        quality_score * 0.3 +
        size_score * 0.3 +
        recency_score * 0.2 +
        context_match_score * 0.2
    )
    
    return confidence
```

---

### 5. _calculate_context_match()
```python
def _calculate_context_match(
    self,
    context: Dict,
    benchmark: Dict
) -> float:
    """
    컨텍스트 매칭 점수 계산
    
    매칭 조건:
    - Industry exact match: +0.4
    - Sub-category match: +0.3
    - Business model match: +0.2
    - Region match: +0.1
    
    Returns:
        0.0-1.0 점수
    """
    
    score = 0.0
    
    # Industry 매칭
    if context.get('industry') == benchmark.get('industry'):
        score += 0.4
    
    # Sub-category 매칭
    if context.get('sub_category') == benchmark.get('sub_category'):
        score += 0.3
    elif context.get('sub_category') and benchmark.get('sub_category'):
        # 유사도 체크 (간단 버전)
        if self._is_similar(context.get('sub_category'), benchmark.get('sub_category')):
            score += 0.15
    
    # Business model 매칭
    if context.get('business_model') == benchmark.get('business_model'):
        score += 0.2
    
    # Region 매칭
    context_region = context.get('region', 'Global')
    benchmark_region = benchmark.get('region', 'Global')
    
    if context_region == benchmark_region:
        score += 0.1
    elif 'Global' in [context_region, benchmark_region]:
        score += 0.05  # Global은 부분 매칭
    
    return min(score, 1.0)
```

---

## 📂 파일 구조

### 신규 파일
```
umis_rag/agents/estimator/
  - phase2_validator_search_enhanced.py (신규, ~500줄)
  - __init__.py (업데이트)

tests/
  - test_phase2_enhanced.py (신규, ~300줄)
```

### 기존 파일 수정
```
umis_rag/agents/estimator/estimator_rag.py:
  - Phase2ValidatorSearchEnhanced 임포트
  - estimate() 메서드에서 사용
  - ~30줄 수정
```

---

## 🔧 구현 계획 (Week 3)

### Day 1-2: 핵심 메서드 구현
```yaml
작업:
  - Phase2ValidatorSearchEnhanced 클래스 생성
  - search_with_context() 구현
  - _search_industry_benchmarks() 구현
  - _parse_benchmark_data() 구현

예상: ~200줄
```

### Day 3: 조정 로직 구현
```yaml
작업:
  - _adjust_by_company_size() 구현
  - _adjust_by_revenue() 구현
  - _adjust_by_subcategory() 구현
  - _parse_revenue() 유틸리티

예상: ~150줄
```

### Day 4: Confidence 계산
```yaml
작업:
  - _calculate_confidence() 구현
  - _calculate_context_match() 구현
  - _is_similar() 유틸리티

예상: ~100줄
```

### Day 5: 통합 + 테스트
```yaml
작업:
  - Estimator 통합
  - 50개 테스트 케이스 작성
  - 정확도 측정
  - 문서화

예상: ~50줄 + 테스트 300줄
```

---

## 📊 예상 성능

### 정확도 개선
```yaml
Before (현재 Phase 2):
  - Coverage: 10-15%
  - 정확도: 94.7%
  - 컨텍스트 활용: 없음

After (Phase 2 Enhanced):
  - Coverage: 70-80% (100개 벤치마크)
  - 정확도: 96-97% 예상
  - 컨텍스트 활용: 5단계 조정

개선:
  - Coverage: +60%p (6배!)
  - 정확도: +1.5-2.5%p
```

### 비공개 기업 추정
```yaml
Before:
  - 오차: ±20-30%
  - 신뢰도: 70-80%

After:
  - 오차: ±10-15% 예상
  - 신뢰도: 90%+ 예상

Q7 품질: 90% → 95%+ (Tier 1 달성!)
```

---

## 🧪 테스트 계획

### 테스트 케이스 (50개)

**SaaS (15개)**:
```yaml
1. B2B Enterprise SaaS, ARR $200M → 예상 28%
2. B2C SaaS Freemium, MAU 5M → 예상 12%
3. Vertical SaaS (Restaurant), ARR $30M → 예상 20%
... (15개)
```

**커머스 (15개)**:
```yaml
1. Beauty D2C Premium, 매출 50억 → 예상 16%
2. Fashion D2C Fast Fashion, 매출 100억 → 예상 10%
3. Pet D2C 구독, 매출 30억 → 예상 16%
... (15개)
```

**플랫폼 (10개)**:
```yaml
1. Food Delivery, GMV 1조 → 예상 5%
2. 숙박 플랫폼, GMV 5000억 → 예상 32%
... (10개)
```

**제조/금융/헬스케어 (10개)**:
```yaml
1. 반도체 Fabless → 예상 30-45%
2. P2P 대출 → 예상 32%
3. 원격의료 → 예상 22%
... (10개)
```

### 성공 기준
```yaml
정확도: 90%+ (45/50 케이스)
평균 오차: ±15% 이내
Confidence: 평균 0.85+
```

---

## 🔗 Estimator 통합

### estimator_rag.py 수정
```python
# umis_rag/agents/estimator/estimator_rag.py

from .phase2_validator_search_enhanced import Phase2ValidatorSearchEnhanced

class EstimatorRAG:
    def __init__(self):
        # ... 기존 코드 ...
        
        # Phase 2 Enhanced 초기화
        self.phase2_enhanced = Phase2ValidatorSearchEnhanced(
            validator_rag=self.validator
        )
    
    def estimate(self, query: str, context: Dict = None) -> EstimationResult:
        # ... Phase 0, 1 ...
        
        # Phase 2 Enhanced (컨텍스트 기반)
        if context:
            result = self.phase2_enhanced.search_with_context(query, context)
            if result and result.confidence >= 0.75:
                return result
        
        # Phase 2 Basic (기존)
        result = self.validator.search_definite_data(query)
        
        # ... Phase 3, 4 ...
```

---

## 📋 구현 체크리스트

### 코드 구현
- [ ] Phase2ValidatorSearchEnhanced 클래스 생성
- [ ] search_with_context() 메서드
- [ ] _search_industry_benchmarks() 메서드
- [ ] _adjust_by_company_size() 메서드
- [ ] _adjust_by_revenue() 메서드
- [ ] _adjust_by_subcategory() 메서드
- [ ] _calculate_confidence() 메서드
- [ ] _calculate_context_match() 메서드
- [ ] 유틸리티 함수들

### 통합
- [ ] Estimator에 통합
- [ ] 기존 Phase 2와 호환성 유지

### 테스트
- [ ] 50개 테스트 케이스
- [ ] 정확도 측정
- [ ] Confidence 검증

### 문서
- [ ] 사용 가이드
- [ ] 예시 3개
- [ ] Week 3 완료 보고서

---

**Week 3 설계 완료!** 구현 준비 완료! 🚀





