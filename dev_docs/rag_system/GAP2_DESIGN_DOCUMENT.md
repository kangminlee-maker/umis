# Gap #2: 비공개 기업 이익률 추정 정확도 개선 설계
**작성일**: 2025-11-12
**버전**: v7.9.0 제안
**목적**: Q7 (이익 점유 추정) 정확도 향상

---

## 문제 정의

### 현재 상태

**Q7: 위 이익 중 누가 각각 얼마씩을 해먹고 있는걸까?**

**공개 기업**: ✅ 100% 정확 (공시 자료 직접 확인)
**비공개 기업**: ⚠️ 70-80% 정확 (±20-30% 오차)

**문제점**:
```yaml
비공개 기업 추정:
  현재 방법: Estimator Phase 2-4
  Phase 2 (Validator 검색):
    - Coverage: 85%
    - 정확도: 94.7%
    - 문제: 24개 데이터 소스만 (부족!)
  
  Phase 3-4 (Guestimation + Fermi):
    - Coverage: 15%
    - 정확도: 70-80%
    - 문제: 산업별 마진율 DB 부족

결과:
  - 경쟁사 수익성 오판 리스크
  - 시장 매력도 잘못 평가 가능
```

---

## 목표

### 정량 목표
```yaml
Phase 2 (Validator 검색):
  - Coverage: 85% → 92%+
  - 정확도: 94.7% → 96%+
  - 방법: 데이터 보강 (24개 → 200개)

Phase 3-4:
  - 정확도: 70-80% → 85%+
  - 방법: 알고리즘 개선 + 데이터

비공개 기업 전체:
  - 오차: ±20-30% → ±10% 이내
  - 신뢰도: 70-80% → 90%+
```

### 정성 목표
- 의사결정자가 비공개 경쟁사 수익성을 신뢰
- 시장 매력도 평가 정확도 향상

---

## 솔루션 설계

### Solution 2.1: Validator RAG 데이터 대폭 보강

#### 신규 데이터: profit_margin_benchmarks.yaml

**구조**:
```yaml
# data/raw/profit_margin_benchmarks.yaml

version: "1.0"
created: "2025-11-12"
total_benchmarks: 200  # 목표
current_count: 0  # 작성 필요

benchmarks:
  
  # === SaaS 산업 ===
  - benchmark_id: margin_saas_001
    industry: "SaaS"
    sub_category: "B2B"
    business_model: "구독"
    region: "Global"
    
    margins:
      gross_margin:
        p25: 72%
        median: 78%
        p75: 85%
        mean: 77%
        stddev: 8%
      
      operating_margin:
        p25: 8%
        median: 15%
        p75: 25%
        mean: 16%
        stddev: 12%
      
      net_margin:
        p25: 3%
        median: 8%
        p75: 15%
        mean: 9%
        stddev: 10%
    
    by_company_size:
      seed_0_10M_ARR:
        gross: 60-70%
        operating: -30% to 0%
        note: "초기 적자 일반적, R&D 투자"
      
      early_stage_10_50M:
        gross: 70-80%
        operating: -10% to 10%
        note: "Break-even 근접"
      
      growth_50_100M:
        gross: 75-85%
        operating: 10-20%
        note: "규모 효과 시작"
      
      scale_100M_plus:
        gross: 80-90%
        operating: 20-30%
        note: "규모 경제 확립"
    
    by_revenue_scale:
      under_10M_USD:
        operating_margin: -20% to 5%
      _10M_to_50M:
        operating_margin: 0% to 15%
      _50M_to_100M:
        operating_margin: 10% to 20%
      over_100M:
        operating_margin: 15% to 30%
    
    by_pricing_model:
      per_seat:
        gross: 75-85%
        operating: 15-25%
      
      usage_based:
        gross: 70-80%
        operating: 10-20%
      
      hybrid:
        gross: 75-85%
        operating: 15-25%
    
    metrics:
      rule_of_40:
        description: "Growth Rate + Profit Margin"
        good: "> 40%"
        great: "> 60%"
        elite: "> 80%"
      
      ltv_cac_ratio:
        median: 3.5
        good: "> 3.0"
        great: "> 5.0"
    
    source: "SRC_OPENVIEW_2024"
    reliability: "high"
    sample_size: 450
    year: 2024
    url: "https://openviewpartners.com/saas-benchmarks"
  
  # === 커머스 산업 ===
  - benchmark_id: margin_commerce_001
    industry: "커머스"
    sub_category: "D2C"
    business_model: "자체 브랜드"
    
    margins:
      gross_margin:
        p25: 45%
        median: 52%
        p75: 60%
      
      operating_margin:
        p25: 5%
        median: 10%
        p75: 15%
    
    by_category:
      beauty:
        gross: 50-60%
        operating: 8-12%
      
      fashion:
        gross: 40-50%
        operating: 5-10%
      
      food:
        gross: 30-40%
        operating: 3-8%
    
    source: "SRC_KPMG_COMMERCE_2024"
    year: 2024
    sample_size: 200

  # === 플랫폼 산업 ===
  - benchmark_id: margin_platform_001
    industry: "플랫폼"
    sub_category: "Marketplace"
    business_model: "중개"
    
    margins:
      gross_margin:
        p25: 60%
        median: 70%
        p75: 80%
        note: "Take Rate가 대부분 gross margin"
      
      operating_margin:
        p25: 10%
        median: 20%
        p75: 30%
    
    by_take_rate:
      low_3_5_percent:
        operating: 10-15%
        example: "배달 플랫폼"
      
      medium_10_15_percent:
        operating: 20-25%
        example: "숙박 플랫폼"
      
      high_20_plus_percent:
        operating: 30-40%
        example: "앱스토어"
    
    source: "SRC_A16Z_MARKETPLACE_2024"
    year: 2024

  # === 제조 산업 ===
  - benchmark_id: margin_manufacturing_001
    industry: "제조"
    sub_category: "소비재"
    
    margins:
      gross_margin:
        p25: 35%
        median: 42%
        p75: 50%
      
      operating_margin:
        p25: 8%
        median: 12%
        p75: 18%
    
    source: "SRC_STATISTICS_KOREA_2024"
    year: 2024

# ========================================
# 데이터 수집 계획
# ========================================

collection_plan:
  
  target: 200개 벤치마크
  
  by_industry:
    tier_1_priority:
      - SaaS (20개)
      - 커머스 (20개)
      - 플랫폼 (15개)
      - 제조 (15개)
      - 금융 (10개)
    
    tier_2:
      - 헬스케어 (10개)
      - 교육 (10개)
      - 미디어 (10개)
      - 기타 (90개)
  
  by_source:
    high_priority:
      - 공개 재무제표 (DART, SEC): 50개
      - 산업 리포트 (KPMG, Deloitte): 50개
      - 벤치마크 DB (OpenView, ChartMogul): 30개
    
    medium_priority:
      - 통계청 기업 경영 분석: 40개
      - 산업 협회 자료: 30개
  
  schedule:
    week_1: "스키마 확정, 우선순위 산업 리스트"
    week_2: "Tier 1 산업 80개 수집"
    week_3: "Tier 2 산업 120개 수집"
    week_4: "RAG Collection 구축, 검증"
```

---

## Solution 2.2: Estimator Phase 2 Enhanced

### 현재 Phase 2 (Validator 검색)

```python
# 현재 (간단)
def search_in_validator(query):
    results = validator.search_definite_data(query)
    return results
```

**문제**: 컨텍스트 활용 부족 (산업, 규모, 모델 고려 안 함)

---

### Phase 2 Enhanced (컨텍스트 기반)

**설계**:
```python
# umis_rag/agents/estimator/phase2_validator_search_enhanced.py

class Phase2ValidatorSearchEnhanced:
    """
    컨텍스트 기반 Validator 검색 (강화 버전)
    
    개선 사항:
    1. Industry-specific search
    2. Company size adjustment
    3. Business model matching
    4. Confidence scoring
    """
    
    def search_with_context(
        self,
        query: str,
        context: Dict[str, Any]
    ) -> EstimationResult:
        """
        Args:
            query: "뷰티 D2C 기업 영업이익률은?"
            context: {
                'industry': '뷰티 커머스',
                'sub_category': 'D2C',
                'business_model': '자체 브랜드',
                'company_size': 'scaleup',
                'revenue': '50억',
                'region': '한국'
            }
        
        Returns:
            EstimationResult(
                value=0.10,  # 10%
                confidence=0.92,
                phase='phase_2_enhanced',
                reasoning_detail={
                    'base_industry': {
                        'industry': '커머스 D2C',
                        'median': 0.10,
                        'range': [0.05, 0.15]
                    },
                    'size_adjustment': {
                        'company_size': 'scaleup',
                        'adjustment': '+0%',
                        'rationale': 'scaleup은 median 적용'
                    },
                    'category_adjustment': {
                        'category': 'beauty',
                        'adjustment': '+1%',
                        'rationale': '뷰티는 평균보다 1%p 높음'
                    },
                    'final': 0.11,
                    'confidence_factors': {
                        'data_quality': 0.95,
                        'sample_size': 200,
                        'recency': 2024
                    }
                }
            )
        """
        
        # Step 1: Industry-specific 벤치마크 검색
        industry_benchmarks = self._search_industry_benchmarks(
            industry=context.get('industry'),
            sub_category=context.get('sub_category'),
            business_model=context.get('business_model')
        )
        
        if not industry_benchmarks:
            return None  # Phase 3로
        
        # Step 2: Base margin 추출
        base_margin = industry_benchmarks['margins']['operating_margin']['median']
        
        # Step 3: Company size adjustment
        size_adjusted = self._adjust_by_company_size(
            base_margin=base_margin,
            company_size=context.get('company_size'),
            size_patterns=industry_benchmarks.get('by_company_size')
        )
        
        # Step 4: Revenue scale adjustment
        revenue_adjusted = self._adjust_by_revenue(
            margin=size_adjusted,
            revenue=context.get('revenue'),
            revenue_patterns=industry_benchmarks.get('by_revenue_scale')
        )
        
        # Step 5: Category/Model adjustment
        final_margin = self._adjust_by_subcategory(
            margin=revenue_adjusted,
            sub_category=context.get('sub_category'),
            category_patterns=industry_benchmarks.get('by_category')
        )
        
        # Step 6: Confidence 계산
        confidence = self._calculate_confidence(
            data_quality=industry_benchmarks.get('reliability'),
            sample_size=industry_benchmarks.get('sample_size'),
            recency=industry_benchmarks.get('year'),
            context_match_score=self._calculate_context_match(context, industry_benchmarks)
        )
        
        return EstimationResult(
            value=final_margin,
            confidence=confidence,
            phase='phase_2_enhanced',
            reasoning_detail={...}
        )
    
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
        
        # RAG 검색
        search_queries = []
        
        # Query 1: 정확 매칭
        if industry and sub_category and business_model:
            search_queries.append(f"{industry} {sub_category} {business_model} margin")
        
        # Query 2: Industry + sub
        if industry and sub_category:
            search_queries.append(f"{industry} {sub_category} margin")
        
        # Query 3: Industry only
        if industry:
            search_queries.append(f"{industry} operating margin benchmark")
        
        # RAG 검색 실행
        for query in search_queries:
            results = self.validator.benchmark_store.similarity_search(query, k=1)
            
            if results and results[0].metadata.get('reliability') in ['high', 'medium']:
                return self._parse_benchmark_data(results[0])
        
        return None
    
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
        - growth: Base (평균)
        - scale: Base + 5%p (규모 경제)
        """
        
        if not company_size or not size_patterns:
            return base_margin
        
        adjustments = {
            'seed': -0.10,
            'early_stage': -0.05,
            'growth': 0.00,
            'scaleup': 0.00,
            'scale': +0.05,
            'enterprise': +0.08
        }
        
        adjustment = adjustments.get(company_size, 0.00)
        
        return base_margin + adjustment
    
    def _adjust_by_revenue(
        self,
        margin: float,
        revenue: str,
        revenue_patterns: Dict
    ) -> float:
        """
        매출 규모에 따른 조정
        
        매출 파싱:
        "50억" → 5000000000
        "$10M" → 10000000 USD
        """
        
        if not revenue or not revenue_patterns:
            return margin
        
        # 매출 파싱 (간단 버전)
        revenue_value = self._parse_revenue(revenue)
        
        # Range 찾기
        for range_name, margin_range in revenue_patterns.items():
            if self._in_revenue_range(revenue_value, range_name):
                # Range median 사용
                range_median = (margin_range.get('min', 0) + margin_range.get('max', 0)) / 2
                return range_median
        
        return margin
    
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
        current_year = 2025  # TODO: datetime.now().year
        years_old = current_year - recency
        
        if years_old <= 1:
            recency_score = 1.0
        elif years_old <= 3:
            recency_score = 0.9
        elif years_old <= 5:
            recency_score = 0.7
        else:
            recency_score = 0.5
        
        # 4. 컨텍스트 매칭 점수 (이미 계산됨)
        
        # 가중 평균
        confidence = (
            quality_score * 0.3 +
            size_score * 0.3 +
            recency_score * 0.2 +
            context_match_score * 0.2
        )
        
        return confidence
```

---

## Solution 2.3: 데이터 수집 전략

### 자동 수집 (50개)

**DART API 연동**:
```python
# scripts/collect_profit_margins_dart.py

import requests

def collect_from_dart(industry_list):
    """
    DART API로 상장사 재무제표 수집
    
    Process:
    1. 산업별 상장사 리스트
    2. 최근 5년 재무제표 조회
    3. 영업이익률 계산
    4. 산업별 통계 (p25, median, p75)
    """
    
    API_KEY = "YOUR_DART_API_KEY"
    
    for industry in industry_list:
        # 1. 해당 산업 상장사 검색
        companies = search_companies_by_industry(industry)
        
        # 2. 재무 데이터 수집
        margins = []
        for company in companies:
            financials = get_financials(company['corp_code'])
            margin = calculate_operating_margin(financials)
            margins.append(margin)
        
        # 3. 통계 계산
        benchmark = {
            'industry': industry,
            'margins': calculate_statistics(margins),
            'source': 'DART',
            'sample_size': len(margins)
        }
        
        yield benchmark
```

---

### 수동 수집 (150개)

**출처 목록**:
```yaml
Tier S (신뢰도 95%+):
  - KPMG, Deloitte, PwC 산업 리포트 (50개)
  - OpenView SaaS Benchmarks (10개)
  - ChartMogul SaaS Metrics (10개)

Tier A (신뢰도 85-95%):
  - Gartner, IDC 산업 분석 (30개)
  - 산업 협회 리포트 (20개)
  
Tier B (신뢰도 70-85%):
  - 통계청 기업 경영 분석 (30개)
  - 학술 논문 (10개)
```

**수집 템플릿**:
```yaml
industry: "{산업명}"
sub_category: "{세부 카테고리}"
business_model: "{비즈니스 모델}"

margins:
  gross_margin:
    p25: X%
    median: Y%
    p75: Z%
  
  operating_margin:
    p25: A%
    median: B%
    p75: C%

by_company_size:
  startup: "Range"
  scaleup: "Range"
  enterprise: "Range"

source: "SRC_XXX"
year: 2024
sample_size: N
```

---

## Solution 2.4: RAG Collection 구축

**Collection**: `profit_margin_benchmarks`

**스크립트**: `scripts/build_margin_benchmarks_rag.py`

```python
#!/usr/bin/env python3
"""
profit_margin_benchmarks.yaml → ChromaDB Collection
"""

import yaml
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

def build_margin_benchmarks_collection():
    """
    profit_margin_benchmarks Collection 구축
    """
    
    # 1. YAML 로드
    with open('data/raw/profit_margin_benchmarks.yaml') as f:
        data = yaml.safe_load(f)
    
    benchmarks = data['benchmarks']
    
    # 2. 문서 생성
    documents = []
    metadatas = []
    
    for bm in benchmarks:
        # 검색 가능한 텍스트
        content = f"""
{bm['industry']} - {bm.get('sub_category', '')}
Business Model: {bm.get('business_model', '')}

Operating Margin:
- Median: {bm['margins']['operating_margin']['median']}
- Range: {bm['margins']['operating_margin'].get('p25')} - {bm['margins']['operating_margin'].get('p75')}

Company Size Patterns:
{yaml.dump(bm.get('by_company_size', {}))}

Sample Size: {bm.get('sample_size')}
Year: {bm.get('year')}
"""
        
        documents.append(content)
        metadatas.append({
            'benchmark_id': bm['benchmark_id'],
            'industry': bm['industry'],
            'sub_category': bm.get('sub_category'),
            'business_model': bm.get('business_model'),
            'sample_size': bm.get('sample_size'),
            'year': bm.get('year')
        })
    
    # 3. ChromaDB
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
    
    collection = Chroma.from_texts(
        texts=documents,
        metadatas=metadatas,
        embedding=embeddings,
        collection_name="profit_margin_benchmarks",
        persist_directory="data/chroma"
    )
    
    print(f"✅ {len(documents)}개 벤치마크 인덱싱 완료")

if __name__ == "__main__":
    build_margin_benchmarks_collection()
```

---

## 📋 구현 로드맵 (4주)

### Week 1: 데이터 스키마 + 수집 시작
```yaml
Day 1-2:
  - profit_margin_benchmarks.yaml 스키마 확정
  - 우선순위 산업 20개 리스트
  - 데이터 소스 확보 (KPMG, OpenView 등)

Day 3-4:
  - Tier 1 산업 40개 수집 (SaaS 20, 커머스 20)
  - YAML 작성

Day 5:
  - 주간 리뷰
  - Week 2 계획
```

---

### Week 2: 데이터 수집 완료
```yaml
Day 1-3:
  - Tier 1 나머지 40개 (플랫폼, 제조, 금융)
  - 총 80개 완성

Day 4-5:
  - Tier 2 산업 시작 (헬스케어, 교육)
  - 추가 50개
  - 총 130개
```

---

### Week 3: Phase 2 Enhanced 구현
```python
작업:
  - Phase2ValidatorSearchEnhanced 클래스 구현
  - _search_industry_benchmarks()
  - _adjust_by_company_size()
  - _adjust_by_revenue()
  - _calculate_confidence()

테스트:
  - 50개 테스트 케이스
  - 정확도 측정
```

---

### Week 4: RAG 구축 + 검증
```yaml
Day 1-2:
  - profit_margin_benchmarks Collection 구축
  - Estimator 연동

Day 3-4:
  - 정확도 테스트 (100개 케이스)
  - 목표: 90%+ 달성

Day 5:
  - 문서화
  - v7.9.0 배포 준비
```

---

## 🎯 예상 효과

### 정확도 향상
```yaml
Before:
  Phase 2: 94.7% (Coverage 85%)
  Phase 3-4: 70-80%
  비공개 기업: ±30% 오차

After:
  Phase 2: 96%+ (Coverage 92%)
  Phase 3-4: 85%+
  비공개 기업: ±10% 이내
```

### Q7 품질
```
Before: 90% (⭐⭐⭐⭐)
After: 95%+ (⭐⭐⭐⭐⭐)

→ Tier 1 달성!
```

---

**문서 끝**





