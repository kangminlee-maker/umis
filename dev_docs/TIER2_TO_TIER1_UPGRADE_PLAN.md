# Tier 2 → Tier 1 업그레이드 계획
**작성일**: 2025-11-12
**버전**: v7.6.2 → v7.7.0 (제안)
**목적**: 의사결정 품질 향상을 위한 Tier 2 질문들의 Tier 1 승격

---

## Executive Summary

### 현재 상태
- **Tier 1 (⭐⭐⭐⭐⭐)**: 8개 질문 (53%)
- **Tier 2 (⭐⭐⭐⭐)**: 6개 질문 (40%) ← **업그레이드 대상**
- **Tier 3 (⭐⭐⭐)**: 1개 질문 (7%)

### 목표
**Tier 2 → Tier 1 승격**: 6개 질문 모두
- Q3: 시장 히스토리 (80% → 95%+)
- Q4-5: 플레이어 변화 (90% → 98%+)
- Q7: 이익 점유 추정 (90% → 95%+)
- Q11: 핵심 Dynamics (90% → 95%+)
- Q14: 공략 방법 (85% → 95%+)

### 핵심 Gap
1. ⚠️ **시계열 분석 도구 부재** (Q3, Q4-5, Q11 영향)
2. ⚠️ **비공개 데이터 추정 정확도** (Q7 영향)
3. ⚠️ **실행 전략 구체화 도구 부족** (Q14 영향)

---

## 1. 상세 Gap 분석

### Gap #1: 시계열 분석 도구 부재 (Critical!)

#### 영향받는 질문
- **Q3**: MRO 시장의 히스토리는? (80%)
- **Q4-5**: 과거/현재 주요 플레이어들의 변화는? (90%)
- **Q11**: MRO 비즈니스의 핵심 dynamics는? (90%)

#### 현재 상태 분석

**현재 가능한 것**:
```yaml
Observer (market_structure):
  - 현재 시장 구조 분석: ✅ 강력
  - 가치사슬 맵핑: ✅ 강력
  - 비효율성 발견: ✅ 강력
  
Explorer (pattern_search):
  - 역사적 패턴 매칭: ✅ 가능 (54개 사례 중 timeline 필드 존재)
  - 실패 사례 분석: ✅ 강력 (incumbent_failures, startup_failures)

Quantifier (growth_analysis):
  - CAGR 계산: ✅ 가능
  - S-Curve 분석: ✅ 가능
```

**현재 불가능한 것** (시계열 분석):
```yaml
시장 히스토리 추적:
  - ❌ 연도별 시장 규모 변화 추이
  - ❌ 주요 사건 타임라인 (M&A, 규제 변화, 기술 도입)
  - ❌ 시장 구조 진화 패턴 (독점 → 경쟁 → 재편)
  - ❌ 가치사슬 변화 추이
  
플레이어 변화 추적:
  - ❌ 플레이어별 점유율 변화 추이 (2015 → 2020 → 2025)
  - ❌ 진입/퇴출 플레이어 분석 (누가 언제 왜)
  - ❌ 주요 플레이어 전략 변화 (피봇, 포지셔닝 전환)
  - ❌ 승자/패자 패턴 분석
  
Dynamics 변화:
  - ❌ 거래 메커니즘 진화 (오프라인 → 플랫폼)
  - ❌ 수익 모델 변화 (판매 → 구독)
  - ❌ 규제 환경 변화와 영향
```

#### 근본 원인

**1. Observer Deliverable Spec 분석**:
```yaml
# market_reality_report_spec.yaml
sections:
  - value_exchange: ✅ 현재 구조
  - transaction_mechanism: ✅ 현재 메커니즘
  - market_structure: ✅ 현재 집중도
  - inefficiencies: ✅ 현재 비효율
  
  ❌ market_history: 없음!
  ❌ structural_evolution: 없음!
  ❌ player_dynamics: 없음!
```

**2. Observer RAG Collections**:
```python
# observer.py
collections:
  - market_structure_patterns (30개): 구조 패턴
  - value_chain_benchmarks (50개): 벤치마크
  
  ❌ historical_evolution_patterns: 없음!
  ❌ market_timeline_data: 없음!
```

**3. Quantifier의 Growth Analysis 한계**:
```python
# quantifier.py - growth_analysis
현재:
  - CAGR 계산: 단순 성장률 (점 → 점)
  - S-Curve 분석: 개념적 (실제 데이터 없음)
  
필요:
  - 연도별 시장 규모 추이 시각화
  - 변곡점 자동 감지 (inflection point)
  - 주요 사건과 성장률 상관관계
```

---

### Gap #2: 비공개 데이터 추정 정확도 (Q7)

#### 영향받는 질문
- **Q7**: 위 이익 중 누가 각각 얼마씩을 해먹고 있는걸까? (90%)

#### 현재 상태

**공개 기업**: ✅ 우수 (영업이익률 직접 확인)
**비공개 기업**: ⚠️ 추정 의존 (Estimator Phase 2-4)

**현재 Estimator 정확도** (v7.6.2):
```yaml
Phase 2 (Validator 검색):
  coverage: 85%
  accuracy: 94.7%
  confidence: 1.0
  note: "유사 기업 마진율 검색"

Phase 3 (Guestimation):
  coverage: 2-5%
  accuracy: 70-80%
  confidence: 0.60-0.80
  note: "업계 평균 추정"

Phase 4 (Fermi):
  coverage: 3%
  accuracy: 75%
  confidence: 0.60-0.80
  note: "재귀 분해 추정"
```

#### 개선 필요 사항

**문제**: 비공개 기업 이익률 추정 시 정확도 70-80%
**목표**: 90%+ 정확도

**현재 부족한 데이터**:
```yaml
Validator RAG (data_sources_registry):
  현재: 24개 데이터 소스
  부족:
    - ❌ 산업별 평균 마진율 DB (체계적)
    - ❌ 기업 규모별 마진율 패턴
    - ❌ 비즈니스 모델별 벤치마크
    - ❌ 비공개 기업 추정 사례 (학습)
```

---

### Gap #3: 실행 전략 구체화 도구 부족 (Q14)

#### 영향받는 질문
- **Q14**: 그래서 어떻게 뚫어야하는데? (85%)

#### 현재 상태

**강력한 영역**:
```yaml
Explorer (7_step_process):
  - ✅ 비효율성 발견 (Observer 연계)
  - ✅ 기회 가설 생성 (RAG 패턴 매칭)
  - ✅ 구조적 검증 (Albert)
  - ✅ 정량 검증 (Bill)

Framework (counter_positioning):
  - ✅ 1등 강점의 약점 찾기
  - ✅ 대안적 비즈니스 모델 제안
```

**부족한 영역**:
```yaml
실행 전략:
  - ⚠️ Go-to-Market 전략 (채널, 가격, 마케팅)
  - ⚠️ 제품 우선순위 (MVP, Feature Roadmap)
  - ⚠️ 실험 설계 (무엇을 검증할지)
  - ⚠️ 리스크 대응 (주요 리스크와 Mitigation)
```

**현재 부분적 지원**:
```yaml
Explorer (validation_protocol):
  - 가설 검증 단계: ✅ 있음
  - 실험 설계: △ 개념만
  - 구체적 실행 계획: ❌ 없음
```

---

## 2. 업그레이드 솔루션

### Solution #1: 시계열 분석 시스템 추가 (우선순위 1)

#### 2.1.1 Observer 도구 확장

**새로운 도구**: `tool:observer:market_timeline`

```yaml
tool:observer:market_timeline:
  purpose: "시장의 역사적 변화를 시계열로 추적 및 분석"
  
  inputs:
    - market_definition: "시장 정의"
    - time_range: "분석 기간 (예: 2015-2025)"
    - focus_areas: ["market_size", "players", "structure", "technology"]
  
  outputs:
    market_evolution_report:
      - timeline_visualization: "Mermaid Gantt Chart"
      - key_events: "주요 사건 리스트 (시간순)"
      - inflection_points: "변곡점 분석"
      - pattern_classification: "진화 패턴 분류"
  
  analysis_dimensions:
    1_market_size_evolution:
      - yearly_size: "연도별 시장 규모 (Quantifier 연계)"
      - growth_phases: "성장 단계 (도입/성장/성숙/쇠퇴)"
      - inflection_points: "변곡점 (성장률 급변)"
      
    2_player_dynamics:
      - entry_exit_timeline: "진입/퇴출 플레이어"
      - market_share_evolution: "점유율 변화 (Top 5)"
      - strategy_shifts: "주요 전략 변화"
      - m_and_a_activity: "M&A 활동"
      
    3_structural_evolution:
      - value_chain_changes: "가치사슬 구조 변화"
      - business_model_shifts: "수익 모델 변화"
      - concentration_trend: "시장 집중도 추이 (HHI)"
      
    4_technology_adoption:
      - tech_milestones: "기술 도입 시점"
      - adoption_curve: "보급률 변화"
      - disruption_events: "파괴적 혁신 사건"
      
    5_regulatory_changes:
      - regulation_timeline: "규제 변경 사항"
      - impact_assessment: "규제 영향 분석"
  
  data_collection_strategy:
    primary_sources:
      - validator_registry: "검증된 데이터 소스"
      - quantifier_historical: "과거 SAM 데이터"
      - explorer_patterns: "역사적 패턴 (RAG)"
    
    automation:
      - year_detection: "텍스트에서 연도 자동 추출"
      - event_classification: "사건 자동 분류 (LLM)"
      - timeline_generation: "타임라인 자동 생성"
  
  deliverable:
    filename: "market_timeline_analysis.md"
    sections:
      - executive_summary: "3줄 요약"
      - timeline_chart: "Mermaid Gantt"
      - detailed_analysis: "기간별 상세 분석"
      - pattern_insights: "패턴 인사이트"
      - future_implications: "미래 시사점"
  
  integration:
    from_quantifier:
      - historical_sam: "과거 시장 규모 데이터"
      - growth_rates: "연도별 성장률"
    
    from_explorer:
      - pattern_timeline: "패턴 발생 시점 (RAG)"
      - case_studies: "유사 사례 타임라인"
    
    from_validator:
      - historical_data: "과거 데이터 검증"
      - source_reliability: "연도별 신뢰도"
```

**구현 방법**:
```python
# umis_rag/agents/observer.py

class ObserverRAG:
    def analyze_market_timeline(
        self,
        market: str,
        start_year: int,
        end_year: int,
        focus_areas: List[str] = None
    ) -> Dict[str, Any]:
        """
        시장 시계열 분석
        
        Returns:
            timeline_data: {
                'events': [
                    {
                        'year': 2015,
                        'event': 'Uber 한국 진입',
                        'category': 'player_entry',
                        'impact': 'high',
                        'source': 'SRC_XXX'
                    },
                    ...
                ],
                'market_size_trend': [(2015, 500), (2016, 650), ...],
                'player_share_evolution': {
                    'player_A': [(2015, 40%), (2016, 35%), ...],
                    'player_B': [(2015, 30%), (2016, 35%), ...]
                },
                'inflection_points': [
                    {
                        'year': 2018,
                        'type': 'regulatory_change',
                        'description': '플랫폼 규제 강화',
                        'impact': '성장률 15% → 5%'
                    }
                ],
                'mermaid_chart': "gantt\n  title Market Timeline\n  ..."
            }
        """
        pass
```

#### 2.1.2 Quantifier 도구 강화

**강화**: `tool:quantifier:growth_analysis`

```yaml
tool:quantifier:growth_analysis:
  current_capabilities:
    - CAGR 계산: ✅
    - S-Curve 분석: ✅ (개념)
  
  new_capabilities:
    
    1_timeseries_visualization:
      - yearly_data_table: "연도별 시장 규모 테이블"
      - growth_rate_chart: "성장률 변화 그래프 (Mermaid)"
      - comparison_chart: "복수 플레이어 비교"
    
    2_inflection_point_detection:
      - algorithm: "2차 미분 기반 변곡점 자동 감지"
      - threshold: "성장률 변화 ±30%"
      - event_correlation: "주요 사건과 연계 (Observer 연계)"
    
    3_trend_decomposition:
      - trend: "장기 추세 (5년 이동평균)"
      - seasonality: "계절성 (해당 시)"
      - anomaly: "이상치 감지 (2σ 이상)"
    
    4_cohort_analysis:
      - player_cohorts: "진입 연도별 그룹 (2010-2015, 2016-2020)"
      - survival_rate: "생존율 분석"
      - growth_pattern: "코호트별 성장 패턴"
  
  excel_output:
    new_sheets:
      - "Historical Trend" (연도별 데이터)
      - "Growth Rate Analysis" (성장률 분해)
      - "Player Evolution" (플레이어 점유율 변화)
      - "Inflection Points" (변곡점 리스트)
```

#### 2.1.3 Explorer RAG 데이터 보강

**새로운 RAG Collection**: `historical_evolution_patterns`

```yaml
collection: historical_evolution_patterns
size: 50개 패턴 (목표)

pattern_schema:
  pattern_id: "market_evolution_001"
  pattern_name: "독점 → 경쟁 → 재편 사이클"
  
  timeline:
    - phase: "독점기 (2000-2005)"
      characteristics: ["1-2개 지배 기업", "높은 마진", "낮은 혁신"]
    - phase: "경쟁기 (2006-2015)"
      characteristics: ["신규 진입 급증", "가격 경쟁", "혁신 가속"]
    - phase: "재편기 (2016-현재)"
      characteristics: ["M&A 활발", "시장 집중도 재상승"]
  
  trigger_events:
    - "규제 완화 (2005)"
    - "기술 보편화 (2010)"
  
  case_studies:
    - market: "통신 시장"
      timeline: "독점(KT) → 경쟁(SKT, LG) → 3강 체제"
    - market: "항공 시장"
      timeline: "독점(KAL) → 경쟁(AAR, 저가항공) → 재편"
  
  indicators:
    - hhi_trend: [8000, 3000, 4500]  # 독점 → 경쟁 → 재집중
    - player_count: [2, 15, 8]  # 진입 → 퇴출
```

**데이터 수집 계획**:
```yaml
sources:
  - incumbent_failures.yaml: ✅ 이미 timeline 필드 존재
  - disruption_patterns.yaml: ✅ 이미 timeline 필드 존재
  
  new:
    - market_evolution_patterns.yaml (신규 작성)
    - industry_lifecycle_cases.yaml (신규 작성)
```

---

### Solution #2: 비공개 데이터 추정 정확도 향상 (우선순위 2)

#### 2.2.1 Validator RAG 보강

**강화**: `tool:validator:data_definition`

```yaml
new_data:
  
  profit_margin_benchmarks:
    category: "산업별 평균 마진율"
    size: 200개 데이터 포인트 (목표)
    
    schema:
      industry: "뷰티 커머스"
      sub_category: "MRO"
      business_model: "D2C"
      
      margins:
        gross_margin: 45-55%
        operating_margin: 8-12%
        net_margin: 3-7%
      
      by_company_size:
        startup_0_50_employees:
          gross: 35-45%
          operating: -10-5%
        scaleup_50_500:
          gross: 45-55%
          operating: 5-12%
        enterprise_500_plus:
          gross: 50-60%
          operating: 10-15%
      
      by_revenue_scale:
        under_10B_KRW:
          operating_margin: 0-5%
        _10_100B:
          operating_margin: 5-10%
        over_100B:
          operating_margin: 8-15%
      
      source: "SRC_XXX"
      reliability: "high"
      year: 2024
  
  private_company_estimation_cases:
    category: "비공개 기업 추정 사례 (학습용)"
    size: 100개 사례
    
    schema:
      company_profile:
        industry: "SaaS"
        revenue_est: "50억"
        employees: 80
        founded: 2018
      
      estimation_process:
        method: "유사 기업 비교"
        comparable_companies: ["CompanyA", "CompanyB"]
        adjustments: ["규모 조정 -2%", "성장 단계 +1%"]
      
      estimated_margin:
        operating_margin: 12%
        confidence: 0.75
      
      actual_margin_if_known:
        operating_margin: 14%
        estimation_error: -2% (양호)
      
      learnings: "SaaS 초기 스케일업은 규모 효과 빠름"
```

**수집 방법**:
```yaml
automated:
  - web_scraping: "공개 재무제표 (금융감독원)"
  - api_integration: "통계청, 산업 리포트 API"

manual:
  - industry_reports: "산업 보고서 정리 (McKinsey, BCG)"
  - case_studies: "기업 사례 수집"

crowdsourced:
  - user_contribution: "Estimator.contribute() 기능 활용"
  - validation: "3명 이상 검증 시 추가"
```

#### 2.2.2 Estimator Phase 2 강화

**현재 Phase 2**:
```python
# phase2_validator_search.py
def search_in_validator(query):
    # data_sources_registry (24개) 검색
    # 정확도 94.7%
```

**강화된 Phase 2**:
```python
def search_in_validator_enhanced(query, context):
    """
    Enhanced Validator Search with Industry Context
    
    Improvements:
    1. Industry-specific margin search
    2. Company size adjustment
    3. Business model matching
    4. Confidence scoring
    """
    
    # 1. 산업별 마진 검색
    industry_margins = search_industry_margins(
        industry=context.get('industry'),
        sub_category=context.get('sub_category'),
        business_model=context.get('business_model')
    )
    
    # 2. 기업 규모 조정
    if context.get('company_size'):
        margin_adjusted = adjust_by_company_size(
            base_margin=industry_margins,
            size=context.get('company_size')
        )
    
    # 3. 유사 기업 비교
    comparable_cases = search_comparable_cases(
        revenue=context.get('revenue'),
        employees=context.get('employees'),
        founded_year=context.get('founded_year')
    )
    
    # 4. Confidence 계산
    confidence = calculate_confidence(
        industry_data_quality=industry_margins.reliability,
        comparable_count=len(comparable_cases),
        recency=industry_margins.year
    )
    
    return EstimationResult(
        value=margin_adjusted,
        confidence=confidence,
        reasoning="..."
    )
```

**목표 정확도**:
```yaml
current:
  Phase 2 accuracy: 94.7%
  Phase 3-4 accuracy: 70-80%

target:
  Phase 2 accuracy: 96%+  (데이터 보강)
  Phase 3-4 accuracy: 85%+  (알고리즘 개선)

overall_impact:
  Q7 (이익 점유 추정): 90% → 95%+
```

---

### Solution #3: 실행 전략 구체화 도구 (우선순위 3)

#### 2.3.1 Explorer 도구 추가

**새로운 도구**: `tool:explorer:strategy_playbook`

```yaml
tool:explorer:strategy_playbook:
  purpose: "검증된 기회를 실행 가능한 전략으로 구체화"
  
  prerequisites:
    - validated_opportunity: "Explorer 7-Step 완료"
    - market_context: "Observer 구조 분석"
    - quantified_market: "Quantifier SAM 계산"
  
  outputs:
    strategy_playbook:
      - go_to_market: "시장 진입 전략"
      - product_strategy: "제품/서비스 전략"
      - competitive_positioning: "경쟁 포지셔닝"
      - execution_roadmap: "실행 로드맵"
      - risk_mitigation: "리스크 대응"
  
  analysis_framework:
    
    1_go_to_market_strategy:
      customer_acquisition:
        - target_segment: "우선 타겟 (Observer 세그먼트)"
        - channel_strategy: "채널 선택 및 우선순위"
        - messaging: "핵심 메시지 (가치 제안)"
        - pricing_strategy: "가격 전략 (Quantifier 연계)"
        - launch_approach: "런칭 방식 (Soft/Hard/Stealth)"
      
      distribution:
        - primary_channel: "주 유통 채널"
        - partnership_strategy: "파트너십 전략"
        - direct_vs_indirect: "직판 vs 간접"
      
      marketing_approach:
        - awareness: "인지도 확보 방법"
        - acquisition_tactics: "고객 획득 전술"
        - conversion_optimization: "전환 최적화"
    
    2_product_strategy:
      mvp_definition:
        - core_features: "핵심 기능 (Must-have)"
        - nice_to_have: "부가 기능"
        - excluded: "제외 기능 (명시적)"
      
      feature_prioritization:
        - framework: "RICE or Kano Model"
        - priority_list: "우선순위 리스트"
        - rationale: "우선순위 근거"
      
      development_roadmap:
        - phase_1: "MVP (3개월)"
        - phase_2: "확장 (6개월)"
        - phase_3: "성숙 (12개월)"
    
    3_competitive_positioning:
      positioning_statement:
        - target: "누구를 위한"
        - need: "어떤 니즈"
        - category: "무엇 (카테고리)"
        - differentiation: "차별점"
      
      competitive_moat:
        - 7_powers_application: "7 Powers 중 활용 가능"
        - defensibility: "방어 가능성"
        - sustainability: "지속 가능성"
    
    4_execution_roadmap:
      milestones:
        - 3_month: "MVP 런칭, 첫 100명 고객"
        - 6_month: "제품-시장 적합성 검증, 500명"
        - 12_month: "스케일업 준비, 5,000명"
      
      resource_requirements:
        - team: "필요 인력 (역할별)"
        - budget: "예산 (Quantifier 추정)"
        - partnerships: "핵심 파트너십"
      
      success_metrics:
        - north_star: "핵심 지표"
        - leading_indicators: "선행 지표"
        - lagging_indicators: "후행 지표"
    
    5_risk_mitigation:
      key_risks:
        - risk_1:
            description: "리스크 설명"
            probability: "high/medium/low"
            impact: "high/medium/low"
            mitigation: "대응 방안"
            contingency: "비상 계획"
      
      assumption_testing:
        - critical_assumptions: "검증 필요 가정"
        - test_design: "검증 실험 설계"
        - success_criteria: "성공 기준"
  
  deliverable:
    filename: "strategy_playbook.md"
    excel: "strategy_playbook.xlsx"
    
    excel_sheets:
      - "GTM Strategy"
      - "Product Roadmap"
      - "Resource Plan"
      - "Milestone Tracker"
      - "Risk Register"
  
  integration:
    from_explorer:
      - validated_opportunity: "검증 완료 기회"
      - hypothesis: "핵심 가설"
    
    from_observer:
      - market_structure: "시장 구조 제약"
      - inefficiencies: "공략 포인트"
    
    from_quantifier:
      - market_size: "기회 규모"
      - unit_economics: "단위 경제성"
    
    from_validator:
      - assumptions: "검증 필요 가정"
```

**구현 우선순위**:
```yaml
Phase 1 (필수):
  - GTM Strategy (고객 획득, 채널, 가격)
  - MVP Definition (핵심 기능)
  - 3/6/12개월 Milestone

Phase 2 (권장):
  - Resource Plan (팀, 예산)
  - Risk Register (리스크 관리)
  - Success Metrics (KPI)

Phase 3 (선택):
  - 상세 Roadmap (주차별)
  - 실험 설계 템플릿
```

---

## 3. 구현 로드맵

### Phase 1: 시계열 분석 시스템 (4-6주)

**Week 1-2: 기반 구축**
```yaml
tasks:
  - Observer 도구 설계:
      - tool:observer:market_timeline 상세 설계
      - Deliverable spec 업데이트
  
  - Quantifier 강화 설계:
      - growth_analysis 확장 기능 설계
      - Excel 템플릿 설계
  
  - 데이터 스키마:
      - market_evolution_patterns.yaml 스키마 정의
      - historical_data 수집 계획
```

**Week 3-4: 핵심 구현**
```yaml
tasks:
  - Observer 구현:
      - analyze_market_timeline() 메서드
      - Mermaid Timeline 자동 생성
      - 변곡점 감지 알고리즘
  
  - Quantifier 구현:
      - 시계열 시각화 (Mermaid)
      - 변곡점 자동 감지 (2차 미분)
      - Excel 시트 추가
  
  - Explorer RAG:
      - historical_evolution_patterns Collection 구축
      - 초기 50개 패턴 데이터 작성
```

**Week 5-6: 통합 및 테스트**
```yaml
tasks:
  - 통합 테스트:
      - Observer → Quantifier → Explorer 연계
      - 실제 시장 사례 분석 (3개)
  
  - Deliverable 검증:
      - market_timeline_analysis.md 자동 생성
      - Excel Historical Trend 시트 검증
  
  - 문서화:
      - 사용 가이드 작성
      - umis_core.yaml 업데이트
```

**달성 목표**:
```yaml
Q3 (시장 히스토리): 80% → 95%+
Q4-5 (플레이어 변화): 90% → 98%+
Q11 (핵심 Dynamics): 90% → 95%+
```

---

### Phase 2: 비공개 데이터 추정 강화 (3-4주)

**Week 1-2: 데이터 수집**
```yaml
tasks:
  - Validator RAG 데이터:
      - profit_margin_benchmarks (100개)
      - private_company_estimation_cases (50개)
  
  - 자동화 구축:
      - 금융감독원 API 연동
      - 산업 리포트 파싱
  
  - 스키마 정의:
      - 마진율 데이터 스키마
      - 추정 사례 스키마
```

**Week 3-4: Estimator 강화**
```yaml
tasks:
  - Phase 2 알고리즘:
      - Industry-specific search
      - Company size adjustment
      - Confidence scoring
  
  - Phase 3-4 개선:
      - Comparable 매칭 정확도 향상
      - Fermi 분해 휴리스틱 추가
  
  - 검증:
      - 100개 테스트 케이스
      - 정확도 측정 (목표 85%+)
```

**달성 목표**:
```yaml
Q7 (이익 점유 추정): 90% → 95%+
Phase 2-4 정확도: 70-80% → 85%+
```

---

### Phase 3: 실행 전략 도구 (2-3주)

**Week 1: 설계**
```yaml
tasks:
  - tool:explorer:strategy_playbook 상세 설계
  - Excel 템플릿 설계 (5개 시트)
  - Deliverable spec 작성
```

**Week 2: 구현**
```yaml
tasks:
  - GTM Strategy 생성 (LLM + 템플릿)
  - MVP Definition (우선순위 로직)
  - Milestone 자동 생성
```

**Week 3: 테스트 및 문서화**
```yaml
tasks:
  - 실제 기회 3개 테스트
  - Excel 자동 생성 검증
  - 사용 가이드 작성
```

**달성 목표**:
```yaml
Q14 (공략 방법): 85% → 95%+
Q15 (실행 계획): 60% → 80%+
```

---

## 4. 성공 지표

### 정량 지표

**Coverage** (목표):
```yaml
before:
  Tier 1: 8개 (53%)
  Tier 2: 6개 (40%)
  Tier 3: 1개 (7%)

after:
  Tier 1: 13-14개 (87-93%)
  Tier 2: 1-2개 (7-13%)
  Tier 3: 1개 (7%)
```

**질문별 목표**:
```yaml
Q3 (시장 히스토리):
  before: 80% → after: 95%+
  
Q4-5 (플레이어 변화):
  before: 90% → after: 98%+
  
Q7 (이익 점유):
  before: 90% → after: 95%+
  
Q11 (Dynamics):
  before: 90% → after: 95%+
  
Q14 (공략 방법):
  before: 85% → after: 95%+
```

**Estimator 정확도**:
```yaml
Phase 2-4 전체:
  before: 70-80%
  after: 85%+
  
비공개 기업 이익률:
  before: 70-80%
  after: 90%+
```

---

### 정성 지표

**의사결정 품질**:
```yaml
판단 기준:
  - 시장 히스토리 이해도: 패턴 인식 가능 여부
  - 플레이어 전략 예측: 과거 → 미래 연결 가능
  - 재무 추정 신뢰도: 비공개 기업 마진 ±10% 이내
  - 실행 계획 구체성: 실무자가 바로 실행 가능
```

**사용자 피드백**:
```yaml
목표:
  - "시장 변화 추이가 명확해서 전략 방향을 잡기 쉬웠다"
  - "비공개 경쟁사 수익성 추정이 생각보다 정확했다"
  - "실행 계획이 구체적이어서 팀에게 바로 공유했다"
```

---

## 5. 리스크 및 대응

### 리스크 #1: 데이터 수집 난이도

**문제**:
- 시계열 데이터 수집 어려움 (특히 과거 데이터)
- 비공개 기업 마진율 데이터 부족

**대응**:
```yaml
Plan A (이상):
  - 자동화 (API, Scraping)
  - 100개+ 데이터 포인트

Plan B (현실):
  - 수동 수집 (산업 리포트)
  - 30-50개 핵심 데이터

Plan C (최소):
  - LLM 보조 + 사용자 검증
  - 10-20개 고품질 데이터
```

---

### 리스크 #2: 개발 리소스

**문제**:
- Phase 1-3 총 9-13주 소요
- 1인 개발 시 부담

**대응**:
```yaml
우선순위 조정:
  P0 (필수): Phase 1 (시계열 분석)
    → Q3, Q4-5, Q11 해결 (3개 질문)
  
  P1 (권장): Phase 2 (추정 정확도)
    → Q7 해결 (1개 질문)
  
  P2 (선택): Phase 3 (실행 전략)
    → Q14 해결 (1개 질문)

단계적 출시:
  v7.7.0: Phase 1만 (6주)
  v7.8.0: Phase 2 추가 (4주)
  v7.9.0: Phase 3 추가 (3주)
```

---

### 리스크 #3: 복잡도 증가

**문제**:
- 도구 추가로 시스템 복잡도 증가
- 사용자 학습 곡선 상승

**대응**:
```yaml
자동화 우선:
  - 시계열 분석: 자동 생성 (사용자 입력 최소)
  - Excel 출력: 기존 패턴 유지
  
문서화:
  - Quick Start 가이드 업데이트
  - 예시 3개 추가
  
점진적 노출:
  - 기본: 기존 도구만
  - 고급: 시계열 분석 옵션
```

---

## 6. 기대 효과

### 의사결정 품질 향상

**Before (Tier 2)**:
```yaml
Q3 (시장 히스토리):
  결과: "현재 구조는 이해했지만, 어떻게 여기까지 왔는지 모호"
  영향: "미래 예측 어려움"

Q7 (이익 점유):
  결과: "공개 기업만 정확, 비공개는 ±30% 오차"
  영향: "경쟁사 수익성 오판 리스크"

Q14 (공략 방법):
  결과: "방향성은 명확하나, 구체적 실행 계획 부족"
  영향: "전략 실행 지연"
```

**After (Tier 1)**:
```yaml
Q3 (시장 히스토리):
  결과: "2015-2025 변화 추이 명확, 변곡점 3개 식별"
  영향: "미래 패턴 예측 가능, 전략 타이밍 최적화"

Q7 (이익 점유):
  결과: "비공개 기업 ±10% 이내 정확도"
  영향: "경쟁사 수익성 정확 파악, 전략 정교화"

Q14 (공략 방법):
  결과: "3/6/12개월 Milestone, 실행 Playbook 제공"
  영향: "팀에게 즉시 공유 가능, 실행 속도 향상"
```

---

### 차별화된 가치

**기존 컨설팅**:
```yaml
시장 분석:
  - 현재 스냅샷: ✅
  - 시계열 분석: △ (수동 작업)
  - 자동화: ❌

재무 추정:
  - 공개 기업: ✅
  - 비공개 기업: △ (주먹구구)
  - 벤치마크 DB: ❌

실행 계획:
  - 전략 방향: ✅
  - 구체적 Playbook: △ (별도 프로젝트)
```

**UMIS (Tier 1 달성 후)**:
```yaml
시장 분석:
  - 현재 스냅샷: ✅ 자동화
  - 시계열 분석: ✅ 자동화 (변곡점 감지)
  - 자동화: ✅ Mermaid Timeline

재무 추정:
  - 공개 기업: ✅ 자동화
  - 비공개 기업: ✅ 85%+ 정확도 (DB 기반)
  - 벤치마크 DB: ✅ 200+ 데이터 포인트

실행 계획:
  - 전략 방향: ✅ 자동화
  - 구체적 Playbook: ✅ 자동화 (Excel 포함)
```

---

## 7. 결론

### 핵심 요약

**현재 Gap**:
1. 시계열 분석 도구 부재 (Q3, Q4-5, Q11 영향)
2. 비공개 데이터 추정 정확도 (Q7 영향)
3. 실행 전략 구체화 부족 (Q14 영향)

**솔루션**:
1. `tool:observer:market_timeline` + `growth_analysis` 강화
2. Validator RAG 보강 (200개 마진율 DB) + Estimator Phase 2-4 개선
3. `tool:explorer:strategy_playbook` 추가

**개발 기간**:
- Phase 1 (시계열): 4-6주
- Phase 2 (추정 정확도): 3-4주
- Phase 3 (실행 전략): 2-3주
- **총 9-13주**

**달성 결과**:
- **Tier 1**: 8개 → 13-14개 (87-93%)
- **평균 품질**: ⭐⭐⭐⭐ (4.0) → ⭐⭐⭐⭐⭐ (4.7)
- **의사결정 품질**: 대폭 향상

---

### 권장 사항

**단계적 접근** (권장):
```yaml
v7.7.0 (P0):
  - Phase 1: 시계열 분석 시스템
  - 기간: 6주
  - 효과: 3개 질문 Tier 1 승격 (Q3, Q4-5, Q11)

v7.8.0 (P1):
  - Phase 2: 추정 정확도 향상
  - 기간: 4주
  - 효과: 1개 질문 Tier 1 승격 (Q7)

v7.9.0 (P2):
  - Phase 3: 실행 전략 도구
  - 기간: 3주
  - 효과: 1개 질문 Tier 1 승격 (Q14)
```

**일괄 접근** (공격적):
```yaml
v7.7.0 (All-in):
  - Phase 1-3 모두
  - 기간: 10-13주 (병렬 작업)
  - 효과: 5개 질문 Tier 1 승격
```

---

**문서 끝**

