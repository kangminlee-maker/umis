# 🦄 유니콘 데이터 → RAG Canonical Index 변환 계획

**작성일:** 2025-11-04  
**목적:** 유니콘 기업 데이터를 UMIS RAG 시스템의 비즈니스 사례 데이터로 활용

---

## 📊 현황 분석

### 1️⃣ 현재 유니콘 데이터 구조

```json
{
  "company": "Bytedance",
  "valuation": {
    "amount_billion": "$140.00",
    "date_added": "2017.4.7"
  },
  "location": {
    "country": "China"
  },
  "category": "Artificial intelligence",
  "select_investors": [...],
  "funding_history": [...],
  "business": {
    "summary": "숏폼 비디오 콘텐츠 SNS 틱톡 운영사",
    "details": []
  }
}
```

**보유 정보:**
- ✅ 회사명, 카테고리, 위치
- ✅ 밸류에이션 (금액, 날짜)
- ✅ 투자자 목록
- ✅ 펀딩 히스토리 (날짜, 금액, 투자자)
- ✅ 비즈니스 요약
- ⚠️ 세부 비즈니스 정보 부족

---

### 2️⃣ Canonical Index 요구 구조

```yaml
canonical_chunk:
  # === Core Fields (Required) ===
  source_id: "bytedance_case"
  canonical_chunk_id: "CAN-byteda01"
  domain: "case_study"
  content_type: "normalized_full"
  version: "7.0.0"
  
  # === Lineage (Required) ===
  lineage:
    from: "CAN-byteda01"
    created_by:
      agent: "Explorer"
      overlay_layer: "core"
  
  # === Content Sections (Required) ===
  sections:
    - agent_view: "explorer"
      anchor_path: "bytedance_case.opportunity_structure"
      content_hash: "sha256:..."
  
  # === Timestamps (Required) ===
  created_at: "2025-11-04T00:00:00Z"
  updated_at: "2025-11-04T00:00:00Z"
  
  # === Metadata ===
  total_tokens: 1500
  quality_grade: "B"
  validation_status: "pending"
```

---

### 3️⃣ 기존 UMIS Case Study 구조 (참고)

```yaml
# 코웨이 사례 예시
코웨이:
  market: "정수기/공기청정기 렌탈"
  launched: "1998년"
  
  breakthrough_insight:
    problem: "정수기 초기 구매 부담 (100만원+)"
    solution: "월 3만원 렌탈 + 정기 관리"
  
  business_structure:
    revenue: "월 구독료"
    service: "2개월 필터 교체"
    retention: "정기 방문"
  
  scale_achieved:
    domestic: "655만 계정"
    global: "405만 계정"
  
  economics:
    arpu: "월 ~3만원"
    annual_revenue: "연 ~2.4조원"
    churn_rate: "3-5%"
  
  critical_success_factors:
    - "정기 방문으로 Lock-in"
    - "위생 관리 = 지속 가치"
```

---

## 🎯 변환 전략

### Phase 1: 데이터 구조 확장 ⭐

현재 유니콘 데이터에 **RAG 호환 필드** 추가:

```json
{
  "company": "Bytedance",
  
  // === RAG Core Fields 추가 ===
  "rag_metadata": {
    "source_id": "bytedance_case",
    "canonical_chunk_id": "CAN-byteda01",
    "domain": "case_study",
    "version": "7.0.0",
    "created_at": "2025-11-04T00:00:00Z",
    "updated_at": "2025-11-04T00:00:00Z",
    "quality_grade": "B",
    "validation_status": "pending",
    
    "lineage": {
      "from": "CAN-byteda01",
      "created_by": {
        "agent": "Explorer",
        "overlay_layer": "core"
      },
      "evidence_ids": []
    },
    
    "sections": [
      {
        "agent_view": "explorer",
        "anchor_path": "bytedance_case.business_model",
        "content_hash": "sha256:...",
        "span_hint": {
          "tokens": 500
        }
      }
    ],
    
    "total_tokens": 1500
  },
  
  // === 기존 필드 유지 ===
  "valuation": {...},
  "location": {...},
  "category": "Artificial intelligence",
  "select_investors": [...],
  "funding_history": [...],
  
  // === 비즈니스 정보 확장 ===
  "business": {
    "summary": "숏폼 비디오 콘텐츠 SNS 틱톡 운영사",
    "details": [],
    
    // 🆕 추가 필드 (리서치 필요)
    "business_model": {
      "pattern_type": "platform",  // 또는 subscription, marketplace 등
      "pattern_id": "platform_model",
      "revenue_model": [
        {
          "type": "advertising",
          "description": "광고 수익"
        },
        {
          "type": "in_app_purchase",
          "description": "인앱 구매"
        }
      ]
    },
    
    "problem_solution": {
      "problem": "짧은 시간에 소비할 수 있는 엔터테인먼트 콘텐츠 부족",
      "solution": "AI 추천 기반 숏폼 비디오 플랫폼",
      "unique_value": "중독성 있는 알고리즘 추천"
    },
    
    "unit_economics": {
      "arpu": null,  // 리서치 필요
      "cac": null,   // 리서치 필요
      "ltv": null,   // 리서치 필요
      "churn_rate": null,
      "gross_margin": null
    },
    
    "market_dynamics": {
      "market_size": null,  // 리서치 필요
      "market_growth": null,
      "target_segment": "Z세대, 밀레니얼",
      "geographic_focus": ["China", "Global"]
    },
    
    "competitive_advantage": [
      "강력한 AI 추천 알고리즘",
      "글로벌 확장 성공 (틱톡)",
      "콘텐츠 크리에이터 생태계"
    ],
    
    "key_metrics": {
      "mau": null,  // 리서치 필요
      "dau": null,
      "engagement_rate": null,
      "content_created_daily": null
    },
    
    "critical_success_factors": [
      "AI 기반 개인화 추천",
      "짧은 콘텐츠 형식 (60초)",
      "크리에이터 수익화 모델"
    ],
    
    "growth_trajectory": {
      "launch_date": "2012",
      "unicorn_date": "2017.4.7",
      "major_milestones": []  // 리서치 필요
    }
  }
}
```

---

## 📋 필요한 변경 사항

### A. `unicorn_companies_structured.json` 변경

#### ✅ 즉시 추가 가능한 필드 (현재 데이터 활용)

1. **`rag_metadata`** (자동 생성 가능)
   - `source_id`: `{company_name}_case` (자동)
   - `canonical_chunk_id`: `CAN-{hash}` (자동)
   - `created_at/updated_at`: 현재 시각
   - `lineage`: 기본값
   - `sections`: 자동 생성

2. **`business.business_model.pattern_type`** (카테고리 기반 추론)
   - Fintech → payment/lending/marketplace
   - E-commerce → marketplace/d2c
   - SaaS → subscription
   - AI → platform/tool

3. **`business.growth_trajectory`**
   - `launch_date`: 추정 (unicorn_date - 5년)
   - `unicorn_date`: `valuation.date_added`

4. **`business.market_dynamics.target_segment`**
   - Category 기반 추정

#### ⚠️ 리서치가 필요한 필드

**각 800개 기업마다 조사 필요:**

1. **비즈니스 모델 상세**
   - `business_model.revenue_model[]`
   - `problem_solution.{problem, solution, unique_value}`

2. **Unit Economics**
   - `arpu`, `cac`, `ltv`, `churn_rate`, `gross_margin`
   - ⚠️ 대부분 비공개 정보

3. **핵심 지표**
   - `key_metrics.{mau, dau, engagement_rate}`
   - ⚠️ 상장 기업만 일부 공개

4. **경쟁 우위**
   - `competitive_advantage[]`
   - 정성적 분석 필요

5. **성공 요인**
   - `critical_success_factors[]`
   - 케이스 스터디 분석 필요

**리서치 소스:**
- Crunchbase, PitchBook (유료)
- 기업 공식 발표
- Tech 미디어 (TechCrunch, The Information)
- 상장 기업 IR 자료
- 업계 리포트

---

### B. `schema_registry.yaml` 변경

#### 필요 없음! ✅

현재 스키마는 **이미 case_study를 지원**합니다:
- `domain: case_study` (line 148)
- Canonical Index 구조 완비
- Lineage, Evidence 지원

**단, 추가 고려사항:**

```yaml
# schema_registry.yaml - Business Case 전용 확장 (선택)

layer_1_canonical:
  
  # 기존 필드 유지...
  
  # Business Case 전용 필드 (선택적 추가)
  business_case_fields:
    company_name:
      type: string
      required: true  # case_study일 때만
    
    industry:
      type: string
      required: true
    
    business_model_pattern:
      type: string
      mapping_to: "pattern_id"
      examples: ["platform", "subscription", "marketplace"]
    
    unit_economics:
      type: object
      required: false
      properties:
        arpu: float
        cac: float
        ltv: float
        churn_rate: float
        payback_period_months: int
    
    key_metrics:
      type: object
      required: false
      properties:
        users: int
        mau: int
        dau: int
        gmv: float
        arr: float
    
    competitive_moat:
      type: array
      items: string
      description: "경쟁 우위 요소"
```

---

## 🚀 실행 계획

### Step 1: 파일럿 변환 (Top 10 유니콘)

**선정 기준:**
- 밸류에이션 Top 10
- 정보가 풍부한 기업 (상장사 우선)

**작업:**
1. ✅ RAG 메타데이터 자동 생성
2. 🔍 비즈니스 모델 패턴 분류 (자동 + 수동)
3. 🔍 리서치를 통한 추가 정보 수집:
   - Problem/Solution
   - Revenue Model
   - Unit Economics (가능한 것만)
   - Critical Success Factors

**예상 시간:** 기업당 30-60분 × 10 = **5-10시간**

---

### Step 2: 스키마 최종화

**파일럿 결과 기반으로:**
1. 필수 필드 vs 선택 필드 구분
2. 리서치 가능 필드 vs 불가능 필드 파악
3. 자동화 가능 항목 스크립트화

---

### Step 3: 단계적 확장

**우선순위:**
1. **Tier 1** (Top 100): 상세 정보 수집
2. **Tier 2** (101-300): 중급 정보
3. **Tier 3** (301-800): 기본 정보만

**자동화:**
- Category → Pattern Type 매핑
- Funding History → Growth Trajectory
- Investors → Network Analysis

---

## 📊 ROI 분석

### 투입

| 작업 | 시간 | 비고 |
|------|------|------|
| 파일럿 10개 | 10시간 | 수동 리서치 |
| Tier 1 (90개) | 90시간 | 일부 자동화 |
| Tier 2 (200개) | 100시간 | 자동화 증가 |
| Tier 3 (500개) | 50시간 | 기본 정보만 |
| **합계** | **250시간** | |

### 효과

1. **800개 실제 비즈니스 사례**
   - Explorer RAG 강화
   - 패턴 매칭 정확도 향상

2. **투자자 네트워크 분석**
   - 1,668개 투자자
   - 5,738건 투자 관계

3. **산업별 벤치마크**
   - 17개 카테고리
   - 41개 국가

4. **시계열 분석**
   - 2010-2025 펀딩 트렌드
   - 밸류에이션 추이

---

## 💡 권장 사항

### Option A: 점진적 접근 (추천) ⭐

1. **Week 1**: 파일럿 10개 완료
2. **Week 2-3**: Tier 1 (100개) 기본 정보
3. **Week 4+**: 자동화 도구 개발
4. **이후**: 점진적 보완

**장점:**
- 빠른 시작 가능
- 파일럿으로 검증
- 점진적 ROI

### Option B: 자동화 우선

1. Category → Pattern 매핑 AI
2. 공개 데이터 크롤링 (Crunchbase API)
3. 기본 정보 일괄 추가

**장점:**
- 빠른 전체 커버리지
- 균일한 품질

**단점:**
- 초기 개발 시간
- 자동화 한계

### Option C: 하이브리드 (최적) ✨

1. 자동화 가능 항목 먼저 (pattern_type, growth_trajectory)
2. Top 50 수동 리서치 (고품질)
3. 나머지는 기본 정보 + 점진적 보완

---

## 🎯 다음 단계

### 즉시 실행 가능

1. **스키마 확장 스크립트 작성**
   - RAG metadata 자동 생성
   - Category → Pattern Type 매핑
   - Canonical ID 생성

2. **파일럿 10개 선정**
   - Bytedance, Stripe, SpaceX, Klarna, Instacart
   - Revolut, Nubank, Epic Games, Databricks, Rivian

3. **리서치 템플릿 작성**
   - 필수 정보 체크리스트
   - 소스 기록 양식

### 의사결정 필요

1. **리서치 범위**: Top 100? Top 50?
2. **품질 기준**: 어느 수준까지?
3. **자동화 우선순위**: 어떤 필드부터?

---

**생성:** UMIS v7.0.0  
**다음:** 파일럿 실행 or 스키마 확장 스크립트 작성


