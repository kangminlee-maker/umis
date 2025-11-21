#!/usr/bin/env python3
"""
벤치마크 데이터 검증 스크립트
다중 출처 교차 검증
"""

import yaml
from pathlib import Path
from typing import Dict, List, Any


class BenchmarkValidator:
    """벤치마크 데이터 검증"""
    
    def __init__(self):
        self.validation_sources = self._load_validation_sources()
    
    def _load_validation_sources(self) -> Dict[str, Any]:
        """
        검증 출처 정의
        
        Returns:
            출처별 신뢰도 및 접근 방법
        """
        return {
            # Tier 1: 최고 신뢰도 (공식 통계, 업계 표준)
            'tier_1': {
                'statista': {
                    'reliability': 'A',
                    'url': 'https://www.statista.com',
                    'coverage': '글로벌 + 국가별',
                    'access': 'Freemium',
                    'validation_method': '원출처 확인 필요'
                },
                'gartner': {
                    'reliability': 'A+',
                    'coverage': 'IT/SaaS 중심',
                    'access': '유료',
                    'validation_method': '업계 표준'
                },
                'emarketer': {
                    'reliability': 'A',
                    'coverage': '이커머스, 디지털',
                    'access': '유료',
                    'validation_method': '정기 업데이트'
                }
            },
            
            # Tier 2: 높은 신뢰도 (산업 리포트, 컨설팅)
            'tier_2': {
                'mckinsey': {
                    'reliability': 'A+',
                    'type': '전략 컨설팅',
                    'access': '일부 무료'
                },
                'bcg': {
                    'reliability': 'A+',
                    'type': '전략 컨설팅',
                    'access': '일부 무료'
                },
                'forrester': {
                    'reliability': 'A',
                    'coverage': '기술, CX',
                    'access': '유료'
                }
            },
            
            # Tier 3: 중간 신뢰도 (업계 블로그, 조사)
            'tier_3': {
                'baymard': {
                    'name': 'Baymard Institute',
                    'reliability': 'B+',
                    'specialization': 'UX/전환율 연구',
                    'note': '48,000개 이커머스 사이트 분석',
                    'url': 'https://baymard.com/lists/cart-abandonment-rate'
                },
                'littledata': {
                    'reliability': 'B+',
                    'specialization': '이커머스 벤치마크',
                    'note': '실제 Shopify 데이터'
                },
                'profitwell': {
                    'reliability': 'A',
                    'specialization': 'SaaS 메트릭',
                    'note': '수천 개 SaaS 데이터'
                }
            }
        }
    
    def validate_metric(
        self, 
        metric_name: str, 
        claimed_value: str,
        country: str = 'global'
    ) -> Dict[str, Any]:
        """
        특정 메트릭의 벤치마크 검증
        
        Args:
            metric_name: 메트릭 이름 (예: "Conversion Rate")
            claimed_value: 주장하는 값 (예: "3.5-4.5%")
            country: 국가 (korea, japan, us, global)
        
        Returns:
            검증 결과
        """
        
        print(f"\n🔍 검증 중: {metric_name} ({country})")
        print(f"   주장 값: {claimed_value}")
        print(f"\n검증 방법:")
        
        # 1. 알려진 출처 목록
        known_sources = self._get_known_sources_for_metric(metric_name, country)
        
        print(f"\n✅ 참조할 신뢰 가능 출처:")
        for source in known_sources:
            print(f"   - {source['name']}: {source['url']}")
            print(f"     신뢰도: {source['reliability']}")
            print(f"     범위: {source.get('typical_range', 'N/A')}")
        
        # 2. 교차 검증 체크리스트
        checklist = self._get_validation_checklist(metric_name)
        
        print(f"\n📋 검증 체크리스트:")
        for item in checklist:
            print(f"   □ {item}")
        
        # 3. 의심 신호
        warnings = self._check_suspicious_values(metric_name, claimed_value)
        
        if warnings:
            print(f"\n⚠️ 주의사항:")
            for warning in warnings:
                print(f"   - {warning}")
        
        return {
            'metric': metric_name,
            'claimed_value': claimed_value,
            'country': country,
            'sources_to_check': known_sources,
            'validation_checklist': checklist,
            'warnings': warnings
        }
    
    def _get_known_sources_for_metric(
        self, 
        metric_name: str, 
        country: str
    ) -> List[Dict[str, str]]:
        """메트릭별 알려진 출처"""
        
        sources = []
        
        if 'conversion' in metric_name.lower():
            sources = [
                {
                    'name': 'Baymard Institute',
                    'url': 'https://baymard.com/lists/cart-abandonment-rate',
                    'reliability': 'B+',
                    'note': '48,000개 사이트 분석',
                    'typical_range': 'Global 2.5-3%'
                },
                {
                    'name': 'Littledata Benchmarks',
                    'url': 'https://www.littledata.io/benchmarks',
                    'reliability': 'B+',
                    'note': 'Shopify 실제 데이터',
                    'typical_range': '1.5-3%'
                },
                {
                    'name': 'Statista E-commerce',
                    'url': 'https://www.statista.com',
                    'reliability': 'A',
                    'typical_range': 'Country-specific'
                }
            ]
            
            if country == 'korea':
                sources.append({
                    'name': '통계청 전자상거래 동향',
                    'url': 'https://kostat.go.kr',
                    'reliability': 'A+',
                    'note': '한국 공식 통계'
                })
        
        elif 'churn' in metric_name.lower():
            sources = [
                {
                    'name': 'ProfitWell SaaS Report',
                    'url': 'https://www.profitwell.com/recur/all/retention-benchmarks',
                    'reliability': 'A',
                    'typical_range': 'B2B: <2%, B2C: 3-7%'
                },
                {
                    'name': 'ChartMogul Benchmarks',
                    'url': 'https://chartmogul.com/benchmarks',
                    'reliability': 'A',
                    'note': 'SaaS 특화'
                }
            ]
        
        return sources
    
    def _get_validation_checklist(self, metric_name: str) -> List[str]:
        """메트릭별 검증 체크리스트"""
        
        checklist = [
            "여러 출처에서 동일한 범위 확인 (최소 3개)",
            "출처의 데이터 수집 년도 확인 (2023-2024)",
            "출처의 샘플 크기 확인 (n > 100)",
            "정의 일치 확인 (동일한 계산 방법)"
        ]
        
        if 'conversion' in metric_name.lower():
            checklist.extend([
                "디바이스 구분 확인 (모바일 vs 데스크톱)",
                "산업 구분 확인 (패션 vs 전자제품 등)",
                "측정 방법 확인 (GA vs 자체 트래킹)"
            ])
        
        if any(country in metric_name.lower() for country in ['korea', 'japan']):
            checklist.extend([
                "국가 특화 출처 확인",
                "현지 플랫폼 데이터 참조",
                "문화적 요인 고려"
            ])
        
        return checklist
    
    def _check_suspicious_values(
        self, 
        metric_name: str, 
        value: str
    ) -> List[str]:
        """의심스러운 값 감지"""
        
        warnings = []
        
        # 전환율 관련 체크
        if 'conversion' in metric_name.lower():
            # 한국 전환율이 글로벌의 2배 이상이면 의심
            if 'korea' in value.lower() and any(x in value for x in ['5-6%', '6-7%', '7%+']):
                warnings.append(
                    "한국 전환율이 매우 높음 (글로벌 2배+). "
                    "출처 재확인 필요. 쿠팡/네이버 공시자료 참조."
                )
            
            # 일본이 한국보다 높으면 의심
            if 'japan' in metric_name.lower() and '4-5%' in value:
                warnings.append(
                    "일본 전환율이 비정상적으로 높음. "
                    "일본은 일반적으로 글로벌 평균보다 낮음."
                )
        
        # Churn 관련 체크
        if 'churn' in metric_name.lower():
            if 'korea' in value.lower() and '< 2%' in value and 'b2c' in value.lower():
                warnings.append(
                    "한국 B2C Churn이 너무 낮음. "
                    "한국은 경쟁 심화로 Churn이 글로벌보다 높은 경향."
                )
        
        return warnings
    
    def generate_validation_report(
        self, 
        collection_file: str
    ) -> Dict[str, Any]:
        """
        Collection 전체 검증 리포트
        
        Args:
            collection_file: YAML 파일 경로
        
        Returns:
            검증 리포트
        """
        
        with open(collection_file) as f:
            data = yaml.safe_load(f)
        
        report = {
            'file': collection_file,
            'total_items': 0,
            'items_needing_validation': [],
            'high_confidence': [],
            'medium_confidence': [],
            'needs_verification': []
        }
        
        # 각 벤치마크 검증
        # (구현 로직...)
        
        return report


def create_validation_guide():
    """검증 가이드 생성"""
    
    guide = """
# 벤치마크 데이터 검증 가이드

## 1. 신뢰도 등급별 출처

### S급 (공식 통계)
- 통계청, 한국은행, World Bank
- 정부 공시자료 (DART)
- 사용: 무조건 우선

### A급 (업계 표준)
- Gartner, IDC, Forrester
- McKinsey, BCG
- 사용: 신뢰 가능, 원출처 확인

### B급 (전문 조사)
- Baymard Institute (UX/전환율)
- ProfitWell (SaaS)
- Littledata (이커머스)
- 사용: 샘플 크기 확인 후 사용

### C급 (일반 블로그, 언론)
- 사용: 보조 참고만

## 2. 검증 프로세스 (3단계)

### Step 1: 출처 확인
- [ ] 최소 3개 출처에서 유사한 값?
- [ ] 출처의 신뢰도 등급?
- [ ] 데이터 수집 년도 (2023-2024)?

### Step 2: 정의 일치 확인
- [ ] 계산 방법 동일?
- [ ] 모집단 동일? (B2B vs B2C)
- [ ] 측정 기간 동일? (월간 vs 연간)

### Step 3: 논리적 검증
- [ ] 상식적으로 타당?
- [ ] 국가 간 차이 설명 가능?
- [ ] 산업 특성과 일치?

## 3. 국가별 검증 전략

### 한국
**주요 출처**:
1. 통계청 (kostat.go.kr)
   - 온라인쇼핑 동향조사
   - 월간, 무료
   
2. 기업 공시 (DART)
   - 쿠팡, 네이버, 카카오 실적
   - 분기별
   
3. 산업 협회
   - 한국콘텐츠진흥원
   - 전자상거래협회

**검증 팁**:
- 네이버, 쿠팡 IR 자료 참조
- "한국 전환율 높음" → 간편결제, 빠른 배송 근거
- 모바일 비중 80%+ → 과학기술정보통신부 통계

### 일본
**주요 출처**:
1. Ministry of Economy (METI)
2. 일본 전자상거래협회
3. Rakuten, Yahoo Japan 공시

**검증 팁**:
- "일본 전환율 낮음" → 현금 문화, 신중한 구매
- "일본 충성도 높음" → 문화적 요인

### 미국
**주요 출처**:
1. US Census Bureau (이커머스 통계)
2. eMarketer (디지털 마케팅)
3. 상장사 공시 (SEC EDGAR)

## 4. 의심 신호 (Red Flags)

⚠️ 다음 경우 재검증:
- 출처가 1개뿐
- 출처가 3년 이상 된 데이터
- 국가 간 차이가 5배 이상
- "업계 평균"이라고만 하고 출처 없음
- 블로그/언론 인용이 출처
- 너무 정확한 값 (예: "3.247%")

## 5. 실전 검증 예시

### 예시 1: 한국 이커머스 전환율

**주장**: "3.5-4.5%"

**검증**:
1. 통계청 전자상거래 동향
   → 거래액은 있지만 전환율 직접 발표 X
   
2. 쿠팡 IR (2023)
   → Active customers, 주문 수 공개
   → 역산 가능
   
3. Statista Korea E-commerce
   → "한국 모바일 전환율 글로벌 대비 높음" (정성적)
   
4. Baymard Institute
   → 글로벌 평균 2.5-3%
   → 한국이 1.5배 높다면 3.75-4.5%
   
**결론**: 합리적 범위 ✅

### 예시 2: 일본 Churn 낮음

**주장**: "0.8-1.5% (B2B SaaS)"

**검증**:
1. ProfitWell Global
   → B2B 평균 1-2%
   
2. 문화적 요인
   → 일본 고객 충성도 높음 (일반적 인식)
   
3. 일본 SaaS 기업 공시
   → Sansan, Freee 등 확인 가능
   
**결론**: 문화적으로 타당, 실제 데이터로 검증 필요 ⚠️

## 6. 자동화 가능 검증

```python
def quick_sanity_check(metric, value, country):
    '''빠른 상식 체크'''
    
    # 전환율은 0-100% 범위
    if 'conversion' in metric and extract_percent(value) > 50:
        return "ERROR: 전환율 > 50%는 비정상"
    
    # Churn은 0-100% 범위
    if 'churn' in metric and extract_percent(value) > 50:
        return "WARNING: Churn > 50%는 매우 높음"
    
    # 국가 간 차이가 10배 이상이면 의심
    if check_country_variance(metric) > 10:
        return "WARNING: 국가 간 차이 과다"
    
    return "PASS"
```

## 7. 권장 검증 프로세스

### 우선순위 1: 공식 통계 (있으면 사용)
→ 통계청, 한국은행, DART

### 우선순위 2: 업계 표준 리포트
→ Gartner, Statista (유료지만 신뢰)

### 우선순위 3: 전문 조사기관
→ Baymard, ProfitWell (특화 분야)

### 우선순위 4: 역산
→ 상장사 공시에서 역산
   예: MAU, Revenue → ARPU 계산

### 우선순위 5: 전문가 판단
→ 출처 없으면 "추정" 명시
   3개 이상 출처에서 범위 확인될 때까지

## 8. 메타데이터 추가 권장

각 벤치마크에 추가:
```yaml
- benchmark_id: "BMK_EC_001"
  metric: "Conversion Rate"
  value: "3.5-4.5%"
  
  validation:  # 추가!
    sources:
      - name: "Baymard Institute"
        year: 2024
        url: "..."
        value: "2.5-3% (글로벌)"
      
      - name: "통계청"
        year: 2023
        note: "역산 (거래액/방문자)"
        value: "3.8% 추정"
    
    confidence: "Medium"  # High/Medium/Low
    last_verified: "2025-11-03"
    notes: "한국 특화 간편결제 고려"
```

## 9. 즉시 검증 가능한 메트릭

### 웹에서 무료 확인 가능:
- Cart Abandonment: Baymard Institute
- SaaS Churn: ProfitWell
- 이커머스 전환율: Littledata
- Mobile vs Desktop: StatCounter

### 공시자료 역산 가능:
- ARPU: 매출 / MAU
- CAC: S&M Spend / New Customers
- LTV: ARPU × Lifetime

### 추정 필요 (출처 부족):
- 국가별 세부 차이
- 신생 산업 메트릭

## 10. 검증 우선순위

**즉시 검증 필요**:
1. 투자 의사결정에 사용
2. 고객에게 제시
3. 공개 발표

**나중 검증 가능**:
1. 내부 참고용
2. 대략적 추정
3. 방향성 파악

---

**원칙**: "출처 불명 > 추정 명시 > 나중에 검증"
        "확실하지 않으면 범위 넓게 + 출처 명시"
"""
    
    return guide


def main():
    """메인 함수"""
    
    validator = BenchmarkValidator()
    
    # 예시: 한국 이커머스 전환율 검증
    result = validator.validate_metric(
        metric_name="E-commerce Conversion Rate",
        claimed_value="3.5-4.5%",
        country="korea"
    )
    
    print("\n" + "="*60)
    print("검증 결과 요약")
    print("="*60)
    
    if not result['warnings']:
        print("✅ 특별한 의심 신호 없음")
    
    print("\n📄 검증 가이드 생성 중...")
    guide = create_validation_guide()
    
    # 가이드 저장
    output_path = Path("docs/BENCHMARK_VALIDATION_GUIDE.md")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(guide)
    
    print(f"✅ 검증 가이드 생성: {output_path}")
    print("\n다음 단계:")
    print("  1. 가이드 참조하여 수동 검증")
    print("  2. 주요 메트릭부터 우선 검증")
    print("  3. 검증 완료 시 메타데이터 추가")


if __name__ == "__main__":
    main()

