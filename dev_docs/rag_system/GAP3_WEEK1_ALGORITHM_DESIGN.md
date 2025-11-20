# Gap #3 Week 1: 알고리즘 설계 문서
**작성일**: 2025-11-12
**목표**: Strategy Playbook 생성 알고리즘 상세 설계
**버전**: v7.10.0

---

## 📋 전체 알고리즘 개요

### generate_strategy_playbook() 흐름
```
Input:
  - validated_opportunity (7-Step 완료)
  - market_context (Observer)
  - quantified_market (Quantifier)

Process:
  1. GTM Strategy 설계
  2. Product Roadmap (RICE)
  3. Resource Plan
  4. Milestones (3/6/12)
  5. Risk Assessment
  6. Markdown 생성
  7. Excel 생성

Output:
  - gtm_strategy (dict)
  - product_roadmap (dict)
  - resource_plan (dict)
  - milestones (dict)
  - risks (dict)
  - markdown_path (str)
  - excel_path (str)
```

---

## 🎯 Algorithm 1: GTM Strategy 설계

### _design_gtm_strategy()

**Input**:
```python
validated_opportunity: {
    'title': '피아노 구독 서비스',
    'value_proposition': '초기 부담 없이 피아노 시작',
    'target_customer': '피아노 입문자 (20-40대)',
    'revenue_model': '월 구독',
    'unit_economics': {
        'arpu': 120000,
        'cac': 180000,
        'ltv': 2400000
    }
}

market_context: {
    'market_structure': {...},
    'competitors': [...],
    'inefficiencies': [...]
}

quantified_market: {
    'sam': 1300,  # 억원
    'target_share': 0.05
}
```

**Algorithm**:
```python
def _design_gtm_strategy(opportunity, market_context, quantified):
    """
    GTM Strategy 설계 알고리즘
    """
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Step 1: Customer Acquisition
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    # 1.1 Target Segment 정의
    target_segment = opportunity['target_customer']
    
    # 1.2 Segment Size 추정
    sam = quantified['sam']  # 1300억
    target_share = quantified['target_share']  # 5%
    target_revenue = sam * target_share  # 65억
    
    # ARPU로 고객 수 역산
    arpu = opportunity['unit_economics']['arpu']  # 12만원
    target_customers = (target_revenue * 100000000) / (arpu * 12)  # 연간
    # 65억 / (12만원 * 12개월) = 약 4,500명
    
    # 1.3 Acquisition Channels 우선순위
    # Logic: CAC, 초기 vs 스케일업, 산업 특성
    
    cac = opportunity['unit_economics']['cac']  # 18만원
    ltv = opportunity['unit_economics']['ltv']  # 240만원
    ltv_cac_ratio = ltv / cac  # 13.3
    
    channels = []
    
    # 초기 단계 (Month 1-6): Direct Sales
    if ltv_cac_ratio > 3:  # LTV/CAC 건전하면
        channels.append({
            'channel': 'Direct Sales',
            'priority': 1,
            'cac_estimate': cac * 1.0,  # CAC 그대로
            'rationale': '초기 고객 밀착, 피드백 수집 필수',
            'timeline': 'Month 1-6'
        })
    
    # 확장 단계 (Month 3+): Digital Marketing
    channels.append({
        'channel': 'Digital Marketing',
        'priority': 2,
        'cac_estimate': cac * 0.7,  # 디지털은 30% 저렴
        'rationale': '스케일업 준비, 자동화 가능',
        'timeline': 'Month 3+'
    })
    
    # Partnership (산업 특성 반영)
    # 예: 피아노 = 피아노 학원 partnership
    industry_keywords = self._extract_industry_keywords(opportunity['title'])
    if any(keyword in ['피아노', '악기', '음악'] for keyword in industry_keywords):
        channels.append({
            'channel': 'Partnership (피아노 학원)',
            'priority': 3,
            'cac_estimate': cac * 0.5,  # Partnership이 가장 저렴
            'rationale': '신뢰할 수 있는 추천, 높은 전환율',
            'timeline': 'Month 6+'
        })
    
    # 1.4 Acquisition Funnel
    # Assumptions: Awareness → Consideration (30%) → Conversion (10%)
    monthly_target_customers = target_customers / 12  # 월간 목표
    
    funnel = {
        'awareness': int(monthly_target_customers / 0.03),  # 3% 전환 가정
        'consideration': int(monthly_target_customers / 0.03 * 0.30),
        'conversion': int(monthly_target_customers),
        'target_cac': cac
    }
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Step 2: Distribution
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    # Distribution channel 결정
    # Logic: 제품 특성, 배송 필요 여부
    
    requires_physical = self._requires_physical_delivery(opportunity)
    
    if requires_physical:
        primary_channel = 'Direct (온라인 주문 + 배송)'
        channel_mix = {
            'direct': '70%',
            'partnership': '30%'
        }
    else:
        primary_channel = 'Digital (앱/웹)'
        channel_mix = {
            'direct': '100%'
        }
    
    # Partnership 전략
    partnerships = []
    if 'partnership' in channel_mix:
        # 산업별 적절한 파트너 제안
        partners = self._suggest_partners(industry_keywords)
        for partner in partners:
            partnerships.append({
                'partner_type': partner['type'],
                'value': partner['value'],
                'terms': partner['suggested_terms']
            })
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Step 3: Pricing
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    pricing_model = opportunity['revenue_model']  # '월 구독'
    price_point = arpu  # 12만원
    
    # 경쟁사 비교 (market_context에서)
    competitors = market_context.get('competitors', [])
    competitor_comparison = []
    
    for comp in competitors[:3]:  # Top 3
        comp_price = comp.get('price', arpu * 1.25)  # 추정
        
        competitor_comparison.append({
            'competitor': comp.get('name', 'Competitor'),
            'price': f'월 {comp_price/10000:.0f}만원',
            'our_price': f'월 {price_point/10000:.0f}만원',
            'differential': f'{((price_point - comp_price) / comp_price):.0%}'
        })
    
    # Pricing strategy
    if price_point < (sum([c.get('price', price_point) for c in competitors]) / len(competitors)):
        pricing_strategy = 'Penetration Pricing (진입 가격)'
    else:
        pricing_strategy = 'Value-based Pricing (가치 기반)'
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Step 4: Marketing Approach
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    positioning = opportunity['value_proposition']
    
    # Content strategy (산업별)
    content_strategy = self._suggest_content_strategy(industry_keywords)
    
    # Budget allocation (표준 비율)
    total_marketing_budget = target_revenue * 0.20  # 매출의 20%
    
    budget_allocation = {
        'digital_ads': '40%',
        'content_marketing': '30%',
        'partnership': '20%',
        '기타': '10%'
    }
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Return
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    return {
        'customer_acquisition': {
            'target_segment': target_segment,
            'segment_size': target_customers,
            'channels': channels,
            'funnel': funnel
        },
        'distribution': {
            'primary_channel': primary_channel,
            'channel_mix': channel_mix,
            'partnerships': partnerships
        },
        'pricing': {
            'pricing_model': pricing_model,
            'price_point': price_point,
            'pricing_strategy': pricing_strategy,
            'competitor_comparison': competitor_comparison
        },
        'marketing_approach': {
            'positioning': positioning,
            'content_strategy': content_strategy,
            'budget_allocation': budget_allocation,
            'total_budget': total_marketing_budget
        }
    }
```

---

## 🎯 Algorithm 2: Product Roadmap (RICE)

### _prioritize_features()

**RICE Framework**:
```
RICE Score = (Reach × Impact × Confidence) / Effort

Reach: 월간 영향 받는 고객 수
Impact: Massive(3), High(2), Medium(1), Low(0.5)
Confidence: 0-100% (확신도)
Effort: person-months
```

**Algorithm**:
```python
def _prioritize_features(opportunity, market_context):
    """
    Feature 우선순위 결정 (RICE)
    """
    
    features = opportunity.get('core_features', [])
    
    if not features:
        # core_features 없으면 기본 구조 제안
        features = self._suggest_basic_features(opportunity)
    
    prioritized = []
    
    for feature in features:
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # RICE 점수 계산
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        
        # 1. Reach (월간 사용 고객 수)
        # Logic: Feature type에 따라 다름
        feature_type = feature.get('type', 'core')
        
        total_monthly_users = quantified['target_share'] * sam / arpu / 12
        
        if feature_type == 'core':
            reach = total_monthly_users * 1.0  # 100%
        elif feature_type == 'frequent':
            reach = total_monthly_users * 0.70  # 70%
        elif feature_type == 'occasional':
            reach = total_monthly_users * 0.30  # 30%
        else:
            reach = total_monthly_users * 0.50  # Default 50%
        
        # 2. Impact (고객 가치)
        # Logic: Value proposition 연관도
        impact_score = self._calculate_impact(
            feature=feature,
            value_proposition=opportunity['value_proposition']
        )
        # Returns: 3 (Massive), 2 (High), 1 (Medium), 0.5 (Low)
        
        # 3. Confidence (확신도 %)
        # Logic: 검증 완료 여부, 경쟁사 유무
        confidence = self._estimate_confidence(feature, market_context)
        # Returns: 50-100%
        
        # 4. Effort (개발 공수)
        # Logic: 복잡도 추정
        effort = self._estimate_effort(feature)
        # Returns: 0.5-6.0 person-months
        
        # 5. RICE Score 계산
        rice_score = (reach * impact_score * (confidence / 100)) / effort
        
        prioritized.append({
            'feature': feature.get('name'),
            'description': feature.get('description'),
            'reach': reach,
            'impact': impact_score,
            'confidence': confidence,
            'effort': effort,
            'rice_score': rice_score,
            'priority': 0  # 나중에 설정
        })
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 점수순 정렬
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    prioritized.sort(key=lambda x: x['rice_score'], reverse=True)
    
    # Priority 번호 부여
    for idx, item in enumerate(prioritized, 1):
        item['priority'] = idx
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # MVP, Phase 2, Phase 3 분류
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    mvp_features = prioritized[:3]  # Top 3
    phase2_features = prioritized[3:7]  # Next 4
    phase3_features = prioritized[7:]  # Rest
    
    return {
        'mvp': {
            'features': mvp_features,
            'timeline': '3개월',
            'total_effort': sum([f['effort'] for f in mvp_features]),
            'description': 'Must-have 핵심 기능'
        },
        'phase_2': {
            'features': phase2_features,
            'timeline': '6개월',
            'total_effort': sum([f['effort'] for f in phase2_features]),
            'description': '확장 기능'
        },
        'phase_3': {
            'features': phase3_features,
            'timeline': '12개월',
            'total_effort': sum([f['effort'] for f in phase3_features]),
            'description': '성숙 기능'
        },
        'all_features': prioritized
    }
```

### 지원 메서드 알고리즘

#### _calculate_impact()
```python
def _calculate_impact(feature, value_proposition):
    """
    Feature가 가치 제안에 얼마나 기여하는지
    
    Returns: 3 (Massive), 2 (High), 1 (Medium), 0.5 (Low)
    """
    
    feature_desc = feature.get('description', '').lower()
    value_prop = value_proposition.lower()
    
    # 키워드 매칭으로 연관도 계산
    keywords = self._extract_keywords(value_prop)
    
    match_count = sum(1 for kw in keywords if kw in feature_desc)
    
    if match_count >= 3:
        return 3  # Massive
    elif match_count >= 2:
        return 2  # High
    elif match_count >= 1:
        return 1  # Medium
    else:
        # Feature type으로 판단
        if feature.get('type') == 'core':
            return 2  # Core는 High
        else:
            return 0.5  # Low
```

#### _estimate_confidence()
```python
def _estimate_confidence(feature, market_context):
    """
    Feature 구현 확신도 (%)
    
    Returns: 50-100%
    """
    
    confidence = 70  # Base
    
    # 1. 검증 완료 여부
    if feature.get('validated', False):
        confidence += 20
    
    # 2. 경쟁사에 유사 기능 존재
    competitors = market_context.get('competitors', [])
    feature_name = feature.get('name', '').lower()
    
    for comp in competitors:
        comp_features = comp.get('features', [])
        if any(feature_name in f.lower() for f in comp_features):
            confidence += 10
            break
    
    # 3. 기술적 복잡도
    complexity = feature.get('complexity', 'medium')
    if complexity == 'simple':
        confidence += 10
    elif complexity == 'complex':
        confidence -= 10
    
    return min(max(confidence, 50), 100)
```

#### _estimate_effort()
```python
def _estimate_effort(feature):
    """
    개발 공수 추정 (person-months)
    
    Returns: 0.5-6.0
    """
    
    complexity = feature.get('complexity', 'medium')
    
    # 복잡도별 기본 공수
    base_effort = {
        'simple': 0.5,
        'medium': 1.5,
        'complex': 3.0,
        'very_complex': 6.0
    }.get(complexity, 1.5)
    
    # Dependencies 고려
    dependencies = feature.get('dependencies', [])
    if dependencies:
        base_effort *= (1 + len(dependencies) * 0.2)
    
    # Third-party integration
    if feature.get('requires_integration', False):
        base_effort *= 1.3
    
    return round(base_effort, 1)
```

---

## 🎯 Algorithm 3: Resource Plan

### _plan_resources()

**Algorithm**:
```python
def _plan_resources(quantified, opportunity):
    """
    Resource Plan 생성
    """
    
    target_revenue = quantified['sam'] * quantified['target_share']  # 65억
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Step 1: Team Structure (3/6/12개월)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    # Month 3 (MVP)
    team_month_3 = [
        {'role': 'CEO/Founder', 'count': 1, 'salary': 0, 'note': '창업자'},
        {'role': '개발', 'count': 2, 'salary': 6000000, 'note': 'Fullstack'},
        {'role': '디자인', 'count': 1, 'salary': 5000000, 'note': 'UI/UX'},
        {'role': '마케팅', 'count': 1, 'salary': 5500000, 'note': 'Growth'}
    ]
    team_size_3 = sum([t['count'] for t in team_month_3])  # 5명
    
    # Month 6 (PMF)
    # Logic: MVP 대비 2배 성장
    team_month_6 = [
        {'role': 'CEO/Founder', 'count': 1},
        {'role': '개발', 'count': 4, 'note': '+2명 (백엔드, 프론트)'},
        {'role': '디자인', 'count': 1},
        {'role': '마케팅/영업', 'count': 3, 'note': '+2명 (영업 2)'},
        {'role': 'CS', 'count': 1, 'note': '+1명 (고객 지원)'}
    ]
    team_size_6 = 9
    
    # Month 12 (Scale)
    # Logic: PMF 대비 2배 성장
    team_month_12 = [
        {'role': 'Executive', 'count': 2, 'note': 'CEO + CTO'},
        {'role': '개발', 'count': 8, 'note': '팀 확장'},
        {'role': '마케팅/영업', 'count': 6},
        {'role': 'CS/운영', 'count': 3},
        {'role': '데이터/분석', 'count': 2, 'note': '의사결정 지원'}
    ]
    team_size_12 = 20
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Step 2: Budget (인건비 + 운영비)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    # 월 인건비 계산
    salary_3 = sum([t['count'] * t.get('salary', 5500000) for t in team_month_3])
    salary_6 = salary_3 * (team_size_6 / team_size_3)
    salary_12 = salary_3 * (team_size_12 / team_size_3)
    
    # 운영비 = 인건비의 50% (사무실, 인프라, 마케팅 등)
    opex_3 = salary_3 * 0.50
    opex_6 = salary_6 * 0.50
    opex_12 = salary_12 * 0.50
    
    # 총 월 예산
    budget_3 = salary_3 + opex_3
    budget_6 = salary_6 + opex_6
    budget_12 = salary_12 + opex_12
    
    # 누적 투자 (Burn)
    burn_to_3 = budget_3 * 3
    burn_to_6 = burn_to_3 + budget_6 * 3
    burn_to_12 = burn_to_6 + budget_12 * 6
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Step 3: Key Hires
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    key_hires = [
        {'role': 'CTO/Tech Lead', 'priority': 1, 'timing': 'Month 1', 'jd': 'Fullstack, 스타트업 경험'},
        {'role': 'Product Manager', 'priority': 2, 'timing': 'Month 3', 'jd': 'B2C 제품 경험'},
        {'role': 'Sales Lead', 'priority': 3, 'timing': 'Month 6', 'jd': 'Enterprise 영업'},
        {'role': 'Marketing Lead', 'priority': 4, 'timing': 'Month 6', 'jd': 'Growth Hacking'},
        {'role': 'CS Lead', 'priority': 5, 'timing': 'Month 9', 'jd': '고객 성공 경험'}
    ]
    
    return {
        'team_structure': {
            'month_3': team_month_3,
            'month_6': team_month_6,
            'month_12': team_month_12
        },
        'budget': {
            'month_3': {
                'salary': salary_3,
                'opex': opex_3,
                'total': budget_3
            },
            'month_6': {
                'salary': salary_6,
                'opex': opex_6,
                'total': budget_6
            },
            'month_12': {
                'salary': salary_12,
                'opex': opex_12,
                'total': budget_12
            },
            'cumulative_burn': {
                'to_month_3': burn_to_3,
                'to_month_6': burn_to_6,
                'to_month_12': burn_to_12
            }
        },
        'key_hires': key_hires
    }
```

---

## 🎯 Algorithm 4: Milestones (3/6/12개월)

### _set_milestones()

**Algorithm**:
```python
def _set_milestones(roadmap, resources, quantified):
    """
    3/6/12개월 Milestone 자동 설정
    """
    
    sam = quantified['sam']
    target_share = quantified['target_share']
    target_revenue_annual = sam * target_share  # 65억
    arpu = quantified.get('arpu', 120000)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Month 3: MVP 런칭
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    # Logic: 목표 매출의 1% (초기 저조한 전환)
    customers_3 = int((target_revenue_annual * 0.01 * 100000000) / (arpu * 12))
    # 65억 * 1% / (12만원 * 12개월) = 약 45명 → 100명으로 반올림
    customers_3 = max(100, customers_3)
    
    mrr_3 = customers_3 * arpu
    
    milestone_3 = {
        'milestone': 'MVP 런칭',
        'metrics': {
            'customers': customers_3,
            'mrr': mrr_3,
            'churn': '< 10%'
        },
        'key_activities': [
            'MVP 개발 완료',
            f'Beta 테스트 ({customers_3 // 2}명)',
            f'첫 {customers_3}명 고객 확보'
        ],
        'success_criteria': [
            'Product-Market Fit 초기 검증',
            'Churn < 10%',
            'NPS > 40'
        ]
    }
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Month 6: PMF 검증
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    # Logic: Month 3 대비 5배 성장
    customers_6 = customers_3 * 5  # 500명
    mrr_6 = customers_6 * arpu
    
    milestone_6 = {
        'milestone': 'PMF 검증',
        'metrics': {
            'customers': customers_6,
            'mrr': mrr_6,
            'churn': '< 7%'
        },
        'key_activities': [
            'Phase 2 기능 출시',
            '파트너십 3개 확보',
            f'{customers_6}명 돌파'
        ],
        'success_criteria': [
            'PMF 확정 (재구매 > 60%)',
            'LTV/CAC > 2.0',
            'Churn < 7%'
        ]
    }
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Month 12: 스케일업
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    # Logic: Month 6 대비 6배 성장
    customers_12 = customers_6 * 6  # 3,000명
    arr_12 = customers_12 * arpu * 12
    
    # Target revenue의 30% 달성 목표
    target_arr_12 = target_revenue_annual * 0.30
    
    milestone_12 = {
        'milestone': '스케일업 준비',
        'metrics': {
            'customers': customers_12,
            'arr': int(target_arr_12),
            'churn': '< 5%'
        },
        'key_activities': [
            'Phase 3 기능 출시',
            '시리즈 A 투자 유치',
            '팀 확장 (20명)'
        ],
        'success_criteria': [
            f'ARR {target_arr_12:.0f}억 달성',
            'Rule of 40 > 40%',
            '시장 점유율 1%'
        ]
    }
    
    return {
        'month_3': milestone_3,
        'month_6': milestone_6,
        'month_12': milestone_12
    }
```

---

## 🎯 Algorithm 5: Risk Assessment

### _assess_and_mitigate_risks()

**Algorithm**:
```python
def _assess_and_mitigate_risks(opportunity, market_context):
    """
    리스크 식별, 평가, 대응 계획
    """
    
    risks = []
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Step 1: 리스크 식별
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    # 1.1 시장 리스크
    competitors = market_context.get('competitors', [])
    
    if len(competitors) >= 3:
        risks.append({
            'risk_id': 'RISK_MARKET_001',
            'category': 'market',
            'risk': '경쟁사 가격 인하',
            'probability': 'high',
            'impact': 'high',
            'severity': 'critical',
            'mitigation': [
                '차별화 강화 (서비스 품질)',
                '전환 비용 구축 (데이터, 기록)',
                '브랜드 구축 (커뮤니티)'
            ],
            'contingency': '가격 10% 추가 인하 가능 (마진 확보 시)'
        })
    
    # 1.2 실행 리스크 (Churn)
    target_churn = opportunity['unit_economics'].get('churn', 0.05)
    
    if target_churn <= 0.05:  # 야심찬 목표
        risks.append({
            'risk_id': 'RISK_EXEC_001',
            'category': 'execution',
            'risk': 'Churn Rate 목표 미달성',
            'probability': 'medium',
            'impact': 'high',
            'severity': 'high',
            'mitigation': [
                '온보딩 강화 (첫 달 집중)',
                '고객 성공 팀 (CS)',
                '정기 피드백 수집'
            ],
            'contingency': 'Churn 10% 초과 시 기능 개선 집중'
        })
    
    # 1.3 재무 리스크
    ltv_cac = opportunity['unit_economics']['ltv'] / opportunity['unit_economics']['cac']
    
    if ltv_cac < 3:  # LTV/CAC 낮으면
        risks.append({
            'risk_id': 'RISK_FIN_001',
            'category': 'financial',
            'risk': 'Unit Economics 악화',
            'probability': 'medium',
            'impact': 'critical',
            'severity': 'critical',
            'mitigation': [
                'CAC 최적화 (채널 분석)',
                'LTV 증대 (Churn 개선)',
                '가격 조정 검토'
            ],
            'contingency': 'Burn rate 감소 (팀 규모 조정)'
        })
    
    # 1.4 파트너십 리스크
    if 'partnership' in str(opportunity):  # Partnership 의존 시
        risks.append({
            'risk_id': 'RISK_PART_001',
            'category': 'partnership',
            'risk': '파트너십 확보 지연',
            'probability': 'medium',
            'impact': 'medium',
            'severity': 'medium',
            'mitigation': [
                '다수 파트너 후보 확보 (10+)',
                'Win-win 조건 제시',
                '파일럿 프로그램'
            ],
            'contingency': 'Direct 채널 강화'
        })
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Step 2: Critical Assumptions 식별
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    assumptions = []
    
    # 2.1 Churn Rate 가정
    assumptions.append({
        'assumption_id': 'ASM_001',
        'assumption': f'Churn Rate {target_churn:.0%} 유지',
        'basis': 'Validator 벤치마크 (유사 서비스)',
        'test_method': '첫 3개월 Beta 모니터링',
        'success_criteria': f'Beta Churn < {target_churn * 1.4:.0%}'
    })
    
    # 2.2 가격 수용성
    price = opportunity['unit_economics']['arpu']
    assumptions.append({
        'assumption_id': 'ASM_002',
        'assumption': f'월 {price/10000:.0f}만원 가격 수용',
        'basis': '경쟁사 대비 할인, 가치 제안',
        'test_method': '50명 Beta 가격 테스트',
        'success_criteria': '전환율 > 10%'
    })
    
    # 2.3 채널 전환율
    assumptions.append({
        'assumption_id': 'ASM_003',
        'assumption': '획득 채널 전환율 3%',
        'basis': '산업 벤치마크',
        'test_method': '3개월 채널별 A/B 테스트',
        'success_criteria': '실제 전환율 > 2%'
    })
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Step 3: Severity 계산 및 정렬
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    severity_order = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}
    risks.sort(key=lambda r: severity_order.get(r['severity'], 0), reverse=True)
    
    return {
        'key_risks': risks,
        'critical_assumptions': assumptions,
        'risk_matrix': self._generate_risk_matrix(risks),
        'assumption_tests': assumptions
    }
```

### _generate_risk_matrix()
```python
def _generate_risk_matrix(risks):
    """
    리스크 매트릭스 생성 (2x2)
    
    Returns:
        {
            'high_prob_high_impact': [risks],
            'high_prob_low_impact': [risks],
            'low_prob_high_impact': [risks],
            'low_prob_low_impact': [risks]
        }
    """
    
    matrix = {
        'critical': [],  # High prob, High impact
        'high': [],
        'medium': [],
        'low': []
    }
    
    for risk in risks:
        prob = risk['probability']
        impact = risk['impact']
        
        # Severity 자동 계산
        if prob == 'high' and impact == 'high':
            category = 'critical'
        elif prob == 'high' or impact == 'high':
            category = 'high'
        elif prob == 'medium' or impact == 'medium':
            category = 'medium'
        else:
            category = 'low'
        
        matrix[category].append(risk)
    
    return matrix
```

---

## 🎯 Algorithm 6: Excel 생성

### _generate_playbook_excel()

**Algorithm**:
```python
def _generate_playbook_excel(gtm, roadmap, resources, milestones, risks):
    """
    Excel 파일 자동 생성 (openpyxl)
    """
    
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
    
    wb = Workbook()
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Sheet 1: Executive Summary
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    ws1 = wb.active
    ws1.title = "Executive Summary"
    
    # Headers
    ws1['A1'] = '항목'
    ws1['B1'] = '내용'
    
    # 기회 개요
    ws1['A2'] = '기회 제목'
    ws1['B2'] = opportunity['title']
    ws1['A3'] = '가치 제안'
    ws1['B3'] = opportunity['value_proposition']
    # ... (더 추가)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Sheet 2: GTM Strategy
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    ws2 = wb.create_sheet("GTM Strategy")
    
    headers = ['영역', '전략', '세부 내용', '담당', '예산', '타이밍']
    for col, header in enumerate(headers, 1):
        ws2.cell(1, col, header)
    
    # Customer Acquisition
    row = 2
    for channel in gtm['customer_acquisition']['channels']:
        ws2.cell(row, 1, '고객 획득')
        ws2.cell(row, 2, channel['channel'])
        ws2.cell(row, 3, channel['rationale'])
        ws2.cell(row, 4, '-')  # 담당 (나중에 채움)
        ws2.cell(row, 5, f"{channel['cac_estimate']/10000:.0f}만원")
        ws2.cell(row, 6, channel['timeline'])
        row += 1
    
    # Distribution, Pricing, Marketing도 동일하게
    # ...
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Sheet 3: Product Roadmap (RICE)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    ws3 = wb.create_sheet("Product Roadmap")
    
    headers = ['Feature', 'Description', 'Reach', 'Impact', 'Confidence', 
               'Effort', 'RICE Score', 'Priority', 'Timeline']
    
    for col, header in enumerate(headers, 1):
        ws3.cell(1, col, header)
    
    row = 2
    for feature in roadmap['all_features']:
        ws3.cell(row, 1, feature['feature'])
        ws3.cell(row, 2, feature['description'])
        ws3.cell(row, 3, feature['reach'])
        ws3.cell(row, 4, feature['impact'])
        ws3.cell(row, 5, f"{feature['confidence']}%")
        ws3.cell(row, 6, feature['effort'])
        ws3.cell(row, 7, round(feature['rice_score'], 1))
        ws3.cell(row, 8, feature['priority'])
        
        # Timeline (MVP/Phase2/Phase3)
        if feature['priority'] <= 3:
            timeline = 'MVP (3개월)'
        elif feature['priority'] <= 7:
            timeline = 'Phase 2 (6개월)'
        else:
            timeline = 'Phase 3 (12개월)'
        ws3.cell(row, 9, timeline)
        
        row += 1
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Sheet 4: Resource Plan
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    ws4 = wb.create_sheet("Resource Plan")
    
    # Team Structure 섹션
    ws4['A1'] = '팀 구조'
    headers = ['역할', 'Month 3', 'Month 6', 'Month 12', '월 급여', '비고']
    for col, header in enumerate(headers, 1):
        ws4.cell(2, col, header)
    
    row = 3
    for team_3 in resources['team_structure']['month_3']:
        role = team_3['role']
        
        # Month 6, 12에서 같은 role 찾기
        count_6 = next((t['count'] for t in resources['team_structure']['month_6'] if t['role'] == role), 0)
        count_12 = next((t['count'] for t in resources['team_structure']['month_12'] if t.get('role') == role), 0)
        
        ws4.cell(row, 1, role)
        ws4.cell(row, 2, f"{team_3['count']}명")
        ws4.cell(row, 3, f"{count_6}명" if count_6 else '-')
        ws4.cell(row, 4, f"{count_12}명" if count_12 else '-')
        ws4.cell(row, 5, f"{team_3.get('salary', 0)/10000:.0f}만원")
        ws4.cell(row, 6, team_3.get('note', ''))
        row += 1
    
    # Budget 섹션 (아래에)
    # ...
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Sheet 5: Milestones
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    ws5 = wb.create_sheet("Milestones")
    
    headers = ['Milestone', '타이밍', 'Metric', '목표값', 
               'Key Activities', 'Success Criteria', 'Status']
    
    for col, header in enumerate(headers, 1):
        ws5.cell(1, col, header)
    
    # Month 3, 6, 12 데이터
    milestones_list = [
        ('month_3', 'Month 3'),
        ('month_6', 'Month 6'),
        ('month_12', 'Month 12')
    ]
    
    row = 2
    for key, timing in milestones_list:
        ms = milestones[key]
        
        ws5.cell(row, 1, ms['milestone'])
        ws5.cell(row, 2, timing)
        
        # Metrics (멀티라인)
        metrics_text = '\n'.join([
            f"{k}: {v}" for k, v in ms['metrics'].items()
        ])
        ws5.cell(row, 3, 'Multiple')
        ws5.cell(row, 4, metrics_text)
        
        # Key Activities
        activities_text = '\n'.join(ms['key_activities'])
        ws5.cell(row, 5, activities_text)
        
        # Success Criteria
        criteria_text = '\n'.join(ms['success_criteria'])
        ws5.cell(row, 6, criteria_text)
        
        # Status
        if key == 'month_3':
            status = 'In Progress'
        else:
            status = 'Planned'
        ws5.cell(row, 7, status)
        
        row += 1
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Sheet 6: Risk Register
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    ws6 = wb.create_sheet("Risk Register")
    
    headers = ['Risk ID', 'Risk', 'Probability', 'Impact', 'Severity',
               'Mitigation', 'Contingency', 'Owner', 'Status']
    
    for col, header in enumerate(headers, 1):
        ws6.cell(1, col, header)
    
    row = 2
    for risk in risks['key_risks']:
        ws6.cell(row, 1, risk['risk_id'])
        ws6.cell(row, 2, risk['risk'])
        ws6.cell(row, 3, risk['probability'].title())
        ws6.cell(row, 4, risk['impact'].title())
        ws6.cell(row, 5, risk['severity'].title())
        ws6.cell(row, 6, '\n'.join(risk['mitigation']))
        ws6.cell(row, 7, risk['contingency'])
        ws6.cell(row, 8, 'CEO')  # Default owner
        ws6.cell(row, 9, 'Active')
        row += 1
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 스타일링
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Header 스타일 (모든 시트)
    header_fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
    header_font = Font(bold=True, color='FFFFFF')
    
    for ws in wb.worksheets:
        for cell in ws[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center', vertical='center')
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 저장
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    excel_path = f"projects/{project_name}/02_analysis/explorer/strategy_playbook.xlsx"
    wb.save(excel_path)
    
    logger.info(f"  ✅ Excel 생성: {excel_path}")
    
    return excel_path
```

---

## 📊 알고리즘 복잡도

### 계산 복잡도
```yaml
GTM Strategy:
  - O(n) where n = competitors 수
  - 예상: O(5) = 매우 빠름

Product Roadmap (RICE):
  - O(n log n) where n = features 수
  - Sorting 포함
  - 예상: O(10 log 10) = 매우 빠름

Resource Plan:
  - O(1) - 고정 계산
  - 예상: O(1) = 즉시

Milestones:
  - O(1) - 3개 고정
  - 예상: O(1) = 즉시

Risk Assessment:
  - O(n) where n = risks 수
  - 예상: O(10) = 매우 빠름

Excel 생성:
  - O(n) where n = total rows
  - 예상: O(50) = 매우 빠름

전체: O(n log n) = 1-2초 예상
```

---

## 🎯 데이터 흐름

### 입력 → 출력 맵핑
```yaml
validated_opportunity:
  - title → Executive Summary, 모든 파일명
  - value_proposition → GTM (Positioning)
  - target_customer → GTM (Target Segment)
  - core_features → Product Roadmap (RICE)
  - revenue_model → GTM (Pricing Model)
  - unit_economics → Milestones 계산

market_context:
  - competitors → GTM (Competitor Comparison)
  - inefficiencies → Risk (기회 검증)
  - market_structure → Risk (경쟁 강도)

quantified_market:
  - sam → Milestones (목표 계산)
  - target_share → Resource Plan (예산)
  - unit_economics → Risk (LTV/CAC 검증)
```

---

## 🧪 테스트 시나리오

### Scenario 1: 피아노 구독 서비스
```yaml
Input:
  - SAM: 1,300억
  - Target Share: 5%
  - ARPU: 12만원
  - CAC: 18만원
  - Churn: 5%

Expected Output:
  GTM:
    - Channels: Direct, Digital, Partnership
    - Price: 12만원 (-20% vs 경쟁사)
  
  Roadmap:
    - MVP: 3개 (가입, 피아노 선택, 배송)
    - RICE Top 1: 사용자 가입 (Score: 6000)
  
  Milestones:
    - Month 3: 100명, MRR 1,000만원
    - Month 6: 500명, MRR 5,000만원
    - Month 12: 3,000명, ARR 30억
  
  Risks:
    - RISK_001: 경쟁사 가격 인하 (Critical)
    - RISK_002: Churn 목표 미달 (High)
```

### Scenario 2: B2B SaaS
```yaml
Input:
  - SAM: 5,000억
  - Target Share: 3%
  - ARPU: 50만원 (월)
  - CAC: 300만원

Expected Output:
  GTM:
    - Channels: Enterprise Sales, Digital (PLG)
    - Price: 50만원/seat
  
  Milestones:
    - Month 12: ARR 45억 (목표 150억의 30%)
  
  Risks:
    - Sales cycle 길어질 리스크
    - Enterprise 전환 지연
```

---

## 📋 구현 체크리스트

### Week 1 완료 항목
```yaml
✅ Day 1-2: Spec 작성
  - strategy_playbook_spec.yaml: 500줄
  - 7개 섹션 상세 정의
  - Excel 6개 시트 구조

✅ Day 3-4: 알고리즘 설계 (현재 문서)
  - GTM Strategy 로직
  - RICE Framework
  - Milestone 자동 생성
  - Risk Assessment
  - Excel 생성

☐ Day 5: Week 1 완료 문서
  - 설계 검토
  - Week 2 계획
```

---

## 🚀 Week 2 준비

### 구현 예상 (Week 2)
```yaml
explorer.py: ~550줄 추가
  - generate_strategy_playbook(): 80줄
  - _design_gtm_strategy(): 100줄
  - _prioritize_features(): 120줄
  - _plan_resources(): 80줄
  - _set_milestones(): 80줄
  - _assess_and_mitigate_risks(): 90줄
  - 지원 메서드 (10개): 100줄
  - _generate_playbook_excel(): 200줄 (openpyxl)
  - _generate_playbook_markdown(): 100줄

총: ~950줄 예상
```

---

**Week 1 알고리즘 설계 완료!** ✅

다음: Week 1 완료 문서 → Week 2 구현 시작!





