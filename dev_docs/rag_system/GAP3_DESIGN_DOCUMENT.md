# Gap #3: 실행 전략 구체화 도구 설계
**작성일**: 2025-11-12
**버전**: v7.10.0 제안
**목적**: Q14, Q15 (공략 방법 + 실행 계획) 구체화

---

## 문제 정의

### 현재 상태

**Q14: 그래서 어떻게 뚫어야하는데?** (85%)
**Q15: 그러기 위해선 뭘 해야하는데?** (60%)

**강력한 것**:
```yaml
Explorer:
  - ✅ 비효율성 발견 (Observer 연계)
  - ✅ 기회 가설 생성 (RAG 패턴 매칭)
  - ✅ 구조적 검증 (7-Step)
  - ✅ Counter-Positioning 전략
```

**부족한 것**:
```yaml
실행 계획:
  - ⚠️ Go-to-Market 전략 (채널, 가격, 마케팅)
  - ⚠️ 제품 우선순위 (MVP, Feature Roadmap)
  - ⚠️ 실험 설계 (무엇을 검증할지)
  - ⚠️ 3/6/12개월 Milestone
  - ⚠️ 리스크 대응 계획
```

**영향**:
- 전략 → 실행 변환에 추가 시간
- 팀 공유 어려움 (추상적)
- 실행 지연

---

## 목표

### 정량 목표
```yaml
Q14 (공략 방법):
  - Coverage: 85% → 95%+
  - 구체성: 중 → 높음

Q15 (실행 계획):
  - Coverage: 60% → 80%+
  - 실행 가능성: 낮음 → 높음
```

### 정성 목표
- 팀에 즉시 공유 가능한 구체적 계획
- 3/6/12개월 Milestone 명확
- 실행 리드타임 -50%

---

## 솔루션 설계

### Solution 3.1: Explorer 도구 추가

**새 도구**: `tool:explorer:strategy_playbook`

#### 메서드 설계

```python
# umis_rag/agents/explorer.py

class ExplorerRAG:
    
    def generate_strategy_playbook(
        self,
        validated_opportunity: Dict,
        market_context: Dict,
        quantified_market: Dict
    ) -> Dict[str, Any]:
        """
        검증된 기회 → 실행 가능한 전략 Playbook 생성
        
        Args:
            validated_opportunity: 7-Step 완료된 기회
                {
                    'opportunity_id': 'OPP_XXX',
                    'title': '구독 모델 피아노 서비스',
                    'value_proposition': '...',
                    'target_customer': '...',
                    'core_features': [...],
                    'unit_economics': {...}
                }
            
            market_context: Observer 구조 분석
                {
                    'market_structure': {...},
                    'inefficiencies': [...],
                    'competitors': [...]
                }
            
            quantified_market: Quantifier SAM 계산
                {
                    'sam': 1300억,
                    'target_share': 5%,
                    'unit_economics': {...}
                }
        
        Returns:
            {
                'gtm_strategy': {...},
                'product_roadmap': {...},
                'resource_plan': {...},
                'execution_milestones': {...},
                'risk_mitigation': {...},
                'excel_path': 'strategy_playbook.xlsx'
            }
        """
        
        logger.info(f"[Explorer] Strategy Playbook 생성: {validated_opportunity['title']}")
        
        # 1. GTM Strategy
        logger.info("  Step 1: GTM Strategy")
        gtm = self._design_gtm_strategy(
            validated_opportunity, market_context, quantified_market
        )
        
        # 2. Product Roadmap
        logger.info("  Step 2: Product Roadmap")
        roadmap = self._prioritize_features(
            validated_opportunity, market_context
        )
        
        # 3. Resource Plan
        logger.info("  Step 3: Resource Plan")
        resources = self._plan_resources(
            quantified_market, validated_opportunity
        )
        
        # 4. Execution Milestones
        logger.info("  Step 4: Execution Milestones")
        milestones = self._set_milestones(
            roadmap, resources, quantified_market
        )
        
        # 5. Risk Mitigation
        logger.info("  Step 5: Risk Mitigation")
        risks = self._assess_and_mitigate_risks(
            validated_opportunity, market_context
        )
        
        # 6. Excel 자동 생성
        logger.info("  Step 6: Excel 생성")
        excel_path = self._generate_playbook_excel(
            gtm, roadmap, resources, milestones, risks
        )
        
        logger.info(f"  ✅ Strategy Playbook 완료: {excel_path}")
        
        return {
            'gtm_strategy': gtm,
            'product_roadmap': roadmap,
            'resource_plan': resources,
            'execution_milestones': milestones,
            'risk_mitigation': risks,
            'excel_path': excel_path
        }
```

---

#### 1. GTM Strategy 설계

```python
def _design_gtm_strategy(self, opportunity, market_context, quantified):
    """
    Go-to-Market 전략 설계
    
    Returns:
        {
            'customer_acquisition': {...},
            'distribution': {...},
            'pricing': {...},
            'marketing_approach': {...}
        }
    """
    
    return {
        'customer_acquisition': {
            'target_segment': opportunity['target_customer'],
            'segment_size': self._calculate_segment_size(market_context),
            'channels': [
                {
                    'channel': 'Direct Sales',
                    'priority': 1,
                    'cac_estimate': self._estimate_cac_by_channel('direct'),
                    'rationale': '초기 고객 밀착 필요'
                },
                {
                    'channel': 'Digital Marketing',
                    'priority': 2,
                    'cac_estimate': self._estimate_cac_by_channel('digital'),
                    'rationale': '스케일업 준비'
                }
            ],
            'acquisition_funnel': {
                'awareness': '1,000명',
                'consideration': '300명 (30%)',
                'conversion': '30명 (10%)',
                'target_cac': quantified['unit_economics'].get('target_cac', 'N/A')
            }
        },
        
        'distribution': {
            'primary_channel': 'Direct (온라인)',
            'channel_mix': {
                'direct': '70%',
                'partnership': '30%'
            },
            'partnership_strategy': [
                {
                    'partner_type': '피아노 학원',
                    'value': '고객 접점',
                    'terms': 'Revenue share 20%'
                }
            ]
        },
        
        'pricing': {
            'pricing_model': opportunity.get('revenue_model', '구독'),
            'price_point': self._determine_price_point(market_context, quantified),
            'pricing_strategy': 'Value-based',
            'competitors_comparison': [
                {
                    'competitor': 'A사',
                    'price': '월 15만원',
                    'our_price': '월 12만원',
                    'differential': '-20% (진입 가격)'
                }
            ]
        },
        
        'marketing_approach': {
            'positioning': opportunity['value_proposition'],
            'key_message': '초기 부담 없이 피아노 시작',
            'content_strategy': [
                'YouTube: 피아노 레슨 콘텐츠',
                'Blog: 피아노 선택 가이드',
                'SNS: 고객 후기'
            ],
            'budget_allocation': {
                'digital_ads': '40%',
                'content_marketing': '30%',
                'partnership': '20%',
                '기타': '10%'
            }
        }
    }
```

---

#### 2. Product Roadmap

```python
def _prioritize_features(self, opportunity, market_context):
    """
    Feature 우선순위 (RICE Framework)
    
    RICE:
    - Reach: 영향 받는 고객 수
    - Impact: 고객 가치 (Massive/High/Medium/Low)
    - Confidence: 확신도 (%)
    - Effort: 개발 공수 (person-months)
    
    Score = (Reach × Impact × Confidence) / Effort
    """
    
    features = opportunity.get('core_features', [])
    
    prioritized = []
    
    for feature in features:
        # RICE 점수 계산
        rice_score = self._calculate_rice(feature, market_context)
        
        prioritized.append({
            'feature': feature['name'],
            'description': feature['description'],
            'rice_score': rice_score,
            'reach': rice_score['reach'],
            'impact': rice_score['impact'],
            'confidence': rice_score['confidence'],
            'effort': rice_score['effort'],
            'priority': rice_score['final_score']
        })
    
    # 점수순 정렬
    prioritized.sort(key=lambda x: x['priority'], reverse=True)
    
    # MVP, Phase 2, Phase 3 분류
    mvp_features = prioritized[:3]  # Top 3
    phase2_features = prioritized[3:7]  # Next 4
    phase3_features = prioritized[7:]  # Rest
    
    return {
        'mvp': {
            'features': mvp_features,
            'timeline': '3개월',
            'description': 'Must-have 핵심 기능'
        },
        'phase_2': {
            'features': phase2_features,
            'timeline': '6개월',
            'description': '확장 기능'
        },
        'phase_3': {
            'features': phase3_features,
            'timeline': '12개월',
            'description': '성숙 기능'
        }
    }
```

---

#### 3. Execution Milestones

```python
def _set_milestones(self, roadmap, resources, quantified):
    """
    3/6/12개월 Milestone 설정
    
    Returns:
        {
            'month_3': {...},
            'month_6': {...},
            'month_12': {...}
        }
    """
    
    sam = quantified['sam']
    target_share = quantified.get('target_share', 0.05)
    target_revenue = sam * target_share
    
    return {
        'month_3': {
            'milestone': 'MVP 런칭',
            'metrics': {
                'customers': 100,
                'mrr': '1,000만원',
                'churn': '< 10%'
            },
            'key_activities': [
                'MVP 개발 완료',
                'Beta 테스트 (50명)',
                '첫 100명 고객 확보'
            ],
            'success_criteria': [
                'Product-Market Fit 초기 검증',
                'Churn < 10%',
                'NPS > 40'
            ]
        },
        
        'month_6': {
            'milestone': 'PMF 검증',
            'metrics': {
                'customers': 500,
                'mrr': '5,000만원',
                'churn': '< 7%'
            },
            'key_activities': [
                'Phase 2 기능 출시',
                '파트너십 3개 확보',
                '500명 돌파'
            ],
            'success_criteria': [
                'PMF 확정 (재구매 > 60%)',
                'LTV/CAC > 2.0',
                'Churn < 7%'
            ]
        },
        
        'month_12': {
            'milestone': '스케일업 준비',
            'metrics': {
                'customers': 3000,
                'arr': f'{target_revenue * 0.3:.0f}억',
                'churn': '< 5%'
            },
            'key_activities': [
                'Phase 3 기능 출시',
                '시리즈 A 투자 유치',
                '팀 확장 (20명)'
            ],
            'success_criteria': [
                f'ARR {target_revenue * 0.3:.0f}억 달성',
                'Rule of 40 > 40%',
                '시장 점유율 1%'
            ]
        }
    }
```

---

#### 4. Risk Mitigation

```python
def _assess_and_mitigate_risks(self, opportunity, market_context):
    """
    리스크 평가 및 대응 계획
    
    Returns:
        {
            'key_risks': [...],
            'critical_assumptions': [...],
            'contingency_plans': {...}
        }
    """
    
    # 주요 리스크 식별
    risks = [
        {
            'risk_id': 'RISK_001',
            'risk': '경쟁사 가격 인하',
            'probability': 'high',
            'impact': 'high',
            'severity': 'critical',
            'mitigation': [
                '차별화 강화 (서비스 품질)',
                '전환 비용 구축 (데이터, 레슨 기록)',
                '브랜드 구축 (커뮤니티)'
            ],
            'contingency': '가격 10% 추가 인하 가능 (마진 확보 시)'
        },
        {
            'risk_id': 'RISK_002',
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
        }
    ]
    
    # Critical Assumptions
    assumptions = [
        {
            'assumption_id': 'ASM_001',
            'assumption': 'Churn Rate 5% 유지',
            'basis': 'Validator 벤치마크 (유사 서비스 3-7%)',
            'test_method': '첫 3개월 Beta 모니터링',
            'success_criteria': 'Beta Churn < 7%'
        },
        {
            'assumption_id': 'ASM_002',
            'assumption': '월 12만원 가격 수용',
            'basis': '경쟁사 대비 20% 저렴, 설문 조사',
            'test_method': '50명 Beta 가격 테스트',
            'success_criteria': '전환율 > 10%'
        }
    ]
    
    return {
        'key_risks': risks,
        'critical_assumptions': assumptions,
        'risk_matrix': self._generate_risk_matrix(risks),
        'assumption_tests': self._design_assumption_tests(assumptions)
    }
```

---

### Solution 3.2: Excel 자동 생성

**Deliverable**: `strategy_playbook.xlsx`

**5개 시트**:

#### Sheet 1: GTM Strategy
```
Columns:
- 영역 (고객 획득, 유통, 가격, 마케팅)
- 전략
- 세부 내용
- 담당
- 예산
```

#### Sheet 2: Product Roadmap
```
Columns:
- Feature
- Description
- RICE Score
- Priority
- Timeline (MVP/Phase2/Phase3)
- 개발 공수
```

#### Sheet 3: Resource Plan
```
Sections:
- Team Structure (역할, 인원, 타이밍)
- Budget (항목별)
- Key Hires (우선순위, JD)
```

#### Sheet 4: Milestone Tracker
```
Columns:
- Milestone (3/6/12개월)
- Metrics (고객 수, MRR/ARR, Churn)
- Key Activities
- Success Criteria
- Status
```

#### Sheet 5: Risk Register
```
Columns:
- Risk ID
- Risk Description
- Probability (High/Medium/Low)
- Impact (High/Medium/Low)
- Severity (Critical/High/Medium/Low)
- Mitigation Plan
- Contingency Plan
- Owner
- Status
```

---

### Solution 3.3: Deliverable Spec

**파일**: `deliverable_specs/explorer/strategy_playbook_spec.yaml`

```yaml
spec_meta:
  spec_version: "1.0"
  agent_id: "explorer"
  agent_role: "Explorer"
  deliverable_type: "strategy_playbook"
  created: "2025-11-12"
  version: "7.10.0"

output_files:
  markdown:
    filename: "strategy_playbook.md"
    location: "02_analysis/explorer/"
  
  excel:
    filename: "strategy_playbook.xlsx"
    location: "02_analysis/explorer/"
    sheets: 5

sections:
  1_executive_summary:
    - 기회 요약
    - 전략 개요
    - 핵심 Milestone

  2_gtm_strategy:
    - 고객 획득
    - 유통 전략
    - 가격 전략
    - 마케팅

  3_product_roadmap:
    - MVP (3개월)
    - Phase 2 (6개월)
    - Phase 3 (12개월)
    - RICE 우선순위

  4_resource_plan:
    - Team Structure
    - Budget
    - Key Hires

  5_milestones:
    - 3개월
    - 6개월
    - 12개월

  6_risk_mitigation:
    - Key Risks
    - Critical Assumptions
    - Contingency Plans
```

---

## 📋 구현 로드맵 (3주)

### Week 1: 설계

**Day 1-2: Spec 작성**
```yaml
작업:
  - strategy_playbook_spec.yaml (상세)
  - Excel 템플릿 설계 (5개 시트)
  - 데이터 구조 정의
```

**Day 3-4: 알고리즘 설계**
```python
작업:
  - GTM Strategy 로직
  - RICE Framework 구현
  - Milestone 자동 생성 로직
```

**Day 5: 주간 리뷰**

---

### Week 2: 구현

**Day 1-3: 메서드 구현**
```python
작업:
  - generate_strategy_playbook()
  - _design_gtm_strategy()
  - _prioritize_features()
  - _plan_resources()
  - _set_milestones()
  - _assess_and_mitigate_risks()

예상: ~350줄
```

**Day 4-5: Excel 생성**
```python
작업:
  - _generate_playbook_excel()
  - 5개 시트 생성
  - openpyxl 활용

예상: ~200줄
```

---

### Week 3: 테스트 + 문서화

**Day 1-3: 테스트**
```yaml
작업:
  - 실제 기회 3개 테스트
  - Excel 검증
  - 사용자 시나리오 검증

케이스:
  1. 피아노 구독 서비스
  2. 음악 레슨 플랫폼
  3. 뷰티 D2C 브랜드
```

**Day 4-5: 문서화**
```yaml
작업:
  - 사용 가이드
  - 예시 3개
  - umis_core.yaml 업데이트
```

---

## 🎯 예상 효과

### Q14: 공략 방법
```
Before (85%):
  - 방향성 명확
  - 실행 계획 부족

After (95%+):
  - ✅ 방향성 명확
  - ✅ GTM Strategy 구체적
  - ✅ 채널, 가격, 마케팅 모두 포함
  - ✅ Excel로 즉시 공유 가능
```

### Q15: 실행 계획
```
Before (60%):
  - 개념적 단계만
  - 구체성 부족

After (80%+):
  - ✅ 3/6/12개월 Milestone
  - ✅ Resource Plan (팀, 예산)
  - ✅ Risk Register
  - ✅ 실행 가능한 수준
```

---

## 📊 산출물

### 코드
```
explorer.py: +550줄
  - generate_strategy_playbook()
  - 6개 지원 메서드
  - Excel 생성 로직
```

### 문서
```
strategy_playbook_spec.yaml: ~300줄
Excel 템플릿: 5개 시트
사용 가이드: ~200줄
```

### 테스트
```
test_strategy_playbook.py: 10개 테스트
통합 테스트: 3개 실제 기회
```

---

## 🔗 Agent 협업

### Input (필수)
```
From Explorer:
  - validated_opportunity (7-Step 완료)

From Observer:
  - market_context (구조 분석)
  - competitors (경쟁 분석)

From Quantifier:
  - quantified_market (SAM, Unit Economics)
  
From Estimator:
  - 핵심 지표 (LTV, CAC, Churn)
```

### Output
```
To Team:
  - strategy_playbook.xlsx (즉시 공유)
  - strategy_playbook.md (상세)

To Guardian:
  - 품질 검증 요청
```

---

## ⚠️ 주의사항

### 1. 과도한 구체화 지양
- 전략은 방향성 + 원칙
- 지나치게 상세한 실행은 경직성

### 2. 가정 명시
- 모든 계획은 가정 기반
- Critical Assumptions 명확히

### 3. 유연성 유지
- Contingency Plans 필수
- 조정 가능성 열어두기

---

**Gap #2, #3 설계 완료!** 구현 준비 완료!





