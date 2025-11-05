# 📊 데이터 구조 개선 보고서

**작업 일시:** 2025-11-04  
**버전:** v3.0 → v3.1  
**목적:** 현실적이고 리서치 가능한 지표 구조로 개선

---

## 🎯 개선 배경

### 문제점
- **unit_economics**와 **key_metrics**가 독립 섹션으로 존재
- 대부분 비공개 정보로 리서치 불가능
- 추정값 사용시 신뢰도 저하 우려

### 해결 방안
- **Performance Metrics** 통합 구조로 재설계
- 재무 실적 중심 (상장사 IR 자료 활용 가능)
- 확인 가능한 지표만 선택적으로 기재

---

## 📋 변경 사항

### ❌ 제거된 섹션

```json
// BEFORE (v3.0)
{
  "business": {
    "unit_economics": {
      "arpu": null,
      "cac": null,
      "ltv": null,
      "churn_rate": null,
      "gross_margin": null
    },
    
    "key_metrics": {
      "mau": null,
      "dau": null,
      "engagement_rate": null,
      "gmv": null,
      "arr": null
    }
  }
}
```

**제거 이유:**
- 800개 기업 중 대부분 비공개 정보
- 리서치 불가능 → 빈 값으로 남음
- 추정시 신뢰도 문제

---

### ✅ 추가된 섹션

```json
// AFTER (v3.1)
{
  "business": {
    "performance_metrics": {
      "_note": "확인 가능한 재무/운영 지표만 기재",
      
      // A. Financial Metrics (재무 지표)
      "financial": {
        "revenue": {
          "year_1": {"year": 2023, "amount_usd_million": 1500, "source": "IR"},
          "year_2": {"year": 2022, "amount_usd_million": 1200, "source": "IR"},
          "year_3": {"year": 2021, "amount_usd_million": 900, "source": "IR"}
        },
        "operating_profit": {
          "year_1": {"year": 2023, "amount_usd_million": 200, "source": "IR"},
          "year_2": {"year": 2022, "amount_usd_million": 150, "source": "IR"},
          "year_3": {"year": 2021, "amount_usd_million": 100, "source": "IR"}
        },
        "gross_margin": 65.5,
        "ebitda": 250,
        "_note": "최근 3개년 데이터 우선"
      },
      
      // B. Operational Metrics (운영 지표)
      "operational": {
        "users": 500000000,
        "mau": 300000000,
        "dau": 150000000,
        "transactions": null,
        "gmv_usd_million": 5000,
        "arr_usd_million": 1200,
        "subscribers": 50000000,
        "_note": "확인 가능한 지표만 선택적으로 기재"
      },
      
      // C. Unit Economics (선택 - 공개된 경우만)
      "unit_economics": {
        "arpu_usd": 5.0,
        "cac_usd": null,
        "ltv_usd": null,
        "ltv_cac_ratio": null,
        "churn_rate_percent": 2.5,
        "payback_period_months": null,
        "_note": "공개된 경우에만 기재"
      }
    }
  }
}
```

**추가 이유:**
- 상장사 IR 자료에서 확인 가능한 재무 지표
- 연도별 추적 가능 (year, amount, source)
- 선택적 기재로 유연성 확보

---

## 🎨 새로운 구조의 특징

### 1. Financial Metrics (재무 지표)

**최근 3개년 데이터 중심:**
- ✅ Revenue (매출)
- ✅ Operating Profit (영업이익)
- ✅ Gross Margin (선택)
- ✅ EBITDA (선택)

**각 연도별 추적:**
```json
{
  "year": 2023,
  "amount_usd_million": 1500,
  "source": "10-K Filing"
}
```

**리서치 소스:**
- 상장사: SEC Filings (10-K, S-1)
- 비상장: IR 자료, 언론 보도
- 신뢰도: 소스 명시로 검증 가능

---

### 2. Operational Metrics (운영 지표)

**확인 가능한 것만 선택적으로:**
- Users / MAU / DAU
- GMV (Gross Merchandise Value)
- ARR (Annual Recurring Revenue)
- Subscribers
- Transactions

**특징:**
- 필수 아님 (확인 불가시 null)
- 공개된 지표만 기재
- 추정 금지

---

### 3. Unit Economics (선택)

**공개된 경우에만:**
- ARPU, CAC, LTV
- LTV/CAC Ratio
- Churn Rate
- Payback Period

**특징:**
- 대부분 비공개 → null
- 상장사 인터뷰, IR 자료에서 확인시만 기재
- 추정 금지 원칙

---

## 📊 비교표

| 항목 | v3.0 (이전) | v3.1 (개선) |
|------|------------|------------|
| **구조** | unit_economics + key_metrics 독립 | performance_metrics 통합 |
| **재무 데이터** | ❌ 없음 | ✅ 최근 3개년 매출/영업이익 |
| **데이터 소스** | ❌ 추적 불가 | ✅ source 필드로 추적 |
| **리서치 가능성** | ⚠️ 대부분 비공개 | ✅ 상장사는 가능 |
| **추정값 사용** | ⚠️ 불명확 | ✅ 금지 명시 |
| **유연성** | ❌ 고정 필드 | ✅ 선택적 기재 |

---

## 💡 리서치 가이드

### 우선순위 1: Financial Metrics ⭐⭐⭐⭐⭐

**상장사 (약 50-100개):**
- SEC Filings (10-K, S-1)
- IR 자료
- Earnings Call

**비상장사:**
- 언론 보도 (공식 발표)
- 업계 리포트
- 인터뷰 기사

**소요 시간:** 기업당 10-20분

---

### 우선순위 2: Operational Metrics ⭐⭐⭐⭐

**공개 정보:**
- 공식 블로그
- 보도자료
- Tech 미디어 (TechCrunch 등)

**확인 가능 지표:**
- Users, MAU (자주 공개)
- GMV (커머스 기업)
- ARR (SaaS 기업)

**소요 시간:** 기업당 5-10분

---

### 우선순위 3: Unit Economics ⭐⭐

**매우 제한적:**
- 상장사 IR 자료
- 경영진 인터뷰
- 업계 분석 리포트

**확인 어려움:**
- CAC, LTV (거의 비공개)
- Churn Rate (일부만 공개)
- ARPU (일부 공개)

**소요 시간:** 기업당 10-30분 (찾아도 없을 가능성 높음)

---

## ✅ 개선 효과

### 1. 리서치 가능성 향상

| 지표 유형 | 이전 (v3.0) | 개선 (v3.1) |
|----------|------------|------------|
| **상장사 재무** | 구조 없음 | ✅ 구조화됨 |
| **운영 지표** | 필수 → 빈 값 | 선택 → 있는 것만 |
| **Unit Economics** | 필수 → 빈 값 | 선택 → 공개시만 |

**예상 완성도:**
- Financial: 상장사 80%, 비상장 30%
- Operational: 전체 50%
- Unit Economics: 전체 10%

---

### 2. 데이터 품질 향상

**이전 (v3.0):**
- 추정값 사용 유혹
- 신뢰도 검증 어려움
- 빈 값 대량 발생

**개선 (v3.1):**
- ✅ 소스 추적 가능
- ✅ 확인된 정보만 기재
- ✅ null = 정보 없음 (명확)

---

### 3. RAG 활용성 향상

**재무 실적 기반 분석 가능:**
```
Query: "연매출 1,000억 이상 SaaS 유니콘 사례"
→ financial.revenue 기반 필터링

Query: "영업이익 흑자 전환 사례"
→ operating_profit 추이 분석

Query: "MAU 1억 이상 소셜 플랫폼"
→ operational.mau 기반 검색
```

---

## 📁 영향받는 파일

### 자동 업데이트됨 ✅

1. **`unicorn_companies_rag_enhanced.json`**
   - 800개 기업 모두 새 구조 적용
   - 파일 크기: 2.81 MB → 3.1 MB (약간 증가)

2. **`scripts/01_add_rag_metadata.py`**
   - business_enhancement 로직 업데이트
   - performance_metrics 생성 로직 추가

3. **`scripts/03_research_template.md`**
   - Section 3 완전히 재구성
   - Financial/Operational/Unit Economics 구분

### 수동 업데이트 필요 📝

1. **`TRANSFORMATION_PLAN.md`**
   - 구조 설명 업데이트 필요

2. **`AUTOMATION_COMPLETE_REPORT.md`**
   - 통계 업데이트 필요

---

## 🎯 파일럿 리서치 전략

### Top 10 우선순위

**재무 데이터 확보 가능 (상장 준비/완료):**
1. ✅ **Stripe** - IR 자료 풍부
2. ✅ **Databricks** - 상장 준비, 언론 보도
3. ✅ **Rivian** - 상장사 (RIVN)
4. ⚠️ **SpaceX** - 비상장, 제한적
5. ⚠️ **Klarna** - 비상장, 일부 공개
6. ⚠️ **Instacart** - 상장 준비
7. ⚠️ **Bytedance** - 비상장, 중국
8. ⚠️ **Fanatics** - 비상장
9. ⚠️ **BYJU's** - 비상장, 인도
10. ⚠️ **DJI** - 비상장, 중국

**전략:**
- 상장사 우선 완성 (Rivian)
- 상장 준비사 언론 보도 활용
- 비상장사는 공개 정보 범위 내

---

## 📝 다음 단계

### Immediate (즉시)

1. ✅ 데이터 구조 업데이트 완료
2. ✅ 리서치 템플릿 업데이트 완료
3. ✅ 스크립트 재실행 완료

### Next (파일럿 리서치)

4. **상장사 우선 리서치:**
   - Rivian (RIVN)
   - Databricks (언론 보도)
   - Stripe (IR 자료)

5. **템플릿 검증:**
   - 3개 기업 완료 후 템플릿 개선
   - 리서치 시간 측정

6. **확장:**
   - 나머지 7개 파일럿 완료
   - Tier 1 (Top 100) 계획 수립

---

## 🎉 요약

### 개선 사항

✅ **현실적인 구조**
- 리서치 가능한 지표 중심
- 상장사 IR 자료 활용 가능

✅ **데이터 품질 향상**
- 소스 추적 (year, source)
- 추정 금지 원칙
- 선택적 기재

✅ **RAG 활용성**
- 재무 실적 기반 검색
- 시계열 분석 가능
- 신뢰도 높은 데이터

### 변경 요약

- ❌ unit_economics (독립) → ✅ performance_metrics.unit_economics (선택)
- ❌ key_metrics (독립) → ✅ performance_metrics.operational (선택)
- ✅ performance_metrics.financial 신규 추가 (최근 3개년)

---

**작업 완료:** 2025-11-04  
**버전:** v3.1  
**다음:** 파일럿 10개 리서치 시작

