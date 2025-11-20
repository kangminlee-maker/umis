# Validator 과거 데이터 수집 프로토콜
**목적**: 시계열 분석용 과거 데이터 탐색 및 검증
**Agent**: Validator (Rachel)
**버전**: v7.8.0

---

## 🎯 Validator 역할 (명확화)

### Observer Timeline 분석 시

**Validator (Rachel) 역할**:
```yaml
1. 과거 데이터 탐색 및 수집 ⭐
   - 연도별 시장 규모
   - 플레이어별 점유율 (과거)
   - 주요 사건 (뉴스, 리포트)
   
2. 데이터 출처 검증
   - SRC_ID 부여
   - 신뢰도 평가 (연도별)
   
3. 데이터 Gap 식별
   - 누락 연도 파악
   - Estimator에게 추정 요청
```

**Estimator (Fermi) 역할**:
```yaml
1. 누락 데이터 추정
   - 연도별 시장 규모 (데이터 없을 때)
   - 비공개 플레이어 점유율
   
2. 보간 (Interpolation)
   - 2015, 2020 데이터만 있으면
   - 2017, 2018, 2019 추정
```

**Observer (Albert) 역할**:
```yaml
1. 수집된 데이터로 패턴 분석
   - 사건 분류
   - 타임라인 구성
   
2. RAG 패턴 매칭
   - HHI 추이 → evolution 패턴
```

**Quantifier (Bill) 역할**:
```yaml
1. 수학적 분석
   - CAGR, YoY 계산
   - 변곡점 감지 (2차 미분)
   - 추세 분해
```

---

## 📋 Validator 데이터 수집 메서드

### 신규 메서드: search_historical_data()

```python
# umis_rag/agents/validator.py

class ValidatorRAG:
    
    def search_historical_data(
        self,
        market: str,
        years: range
    ) -> Dict[str, Any]:
        """
        과거 데이터 탐색 및 수집
        
        Args:
            market: 시장 이름 (예: "음악 스트리밍")
            years: range(2015, 2026) → 2015-2025
        
        Returns:
            {
                'market_size_by_year': {
                    2015: {'value': 500, 'source': 'SRC_XXX', 'reliability': 'high'},
                    2020: {'value': 1200, 'source': 'SRC_YYY', 'reliability': 'high'},
                    2025: {'value': 2500, 'source': 'SRC_ZZZ', 'reliability': 'medium'}
                },
                'players_by_year': {
                    2015: {
                        'Spotify': {'share': 40, 'source': 'SRC_AAA'},
                        'Apple': {'share': 30, 'source': 'SRC_BBB'}
                    }
                },
                'events': [
                    {
                        'year': 2018,
                        'event': '규제 완화',
                        'source': 'SRC_CCC',
                        'category': 'regulation'
                    }
                ],
                'data_gaps': {
                    'missing_years': [2016, 2017, 2019],  # Estimator 추정 필요
                    'missing_players': ['Player C'],
                    'confidence': 'medium'
                }
            }
        """
        
        result = {
            'market_size_by_year': {},
            'players_by_year': {},
            'events': [],
            'data_gaps': {'missing_years': [], 'missing_players': []}
        }
        
        # 1. 공식 통계 검색 (우선)
        official_data = self._search_official_statistics(market, years)
        
        # 2. 산업 리포트 검색
        industry_reports = self._search_industry_reports(market, years)
        
        # 3. 공시 데이터 (상장사)
        public_filings = self._search_public_filings(market, years)
        
        # 4. 뉴스/언론 (사건)
        news_events = self._search_news_events(market, years)
        
        # 5. 데이터 통합
        result = self._integrate_data_sources(
            official_data,
            industry_reports,
            public_filings,
            news_events
        )
        
        # 6. Gap 식별
        result['data_gaps'] = self._identify_data_gaps(result, years)
        
        # 7. SRC_ID 부여
        result = self._assign_src_ids(result)
        
        return result
```

---

## 📊 데이터 소스 우선순위

### Tier S: 공식 통계 (신뢰도 95%+)
```yaml
sources:
  - 통계청 (KOSIS)
  - 한국은행
  - 산업통상자원부
  - 금융감독원

적용:
  - 시장 규모 (산업별)
  - 기업 수, 매출
```

### Tier A: 산업 리포트 (신뢰도 85-95%)
```yaml
sources:
  - Gartner, IDC, Statista
  - McKinsey, BCG, Bain
  - 산업 협회 리포트

적용:
  - 시장 규모 (글로벌, 산업별)
  - 성장률, 트렌드
  - 플레이어 점유율 (추정)
```

### Tier B: 공시 자료 (신뢰도 85-95%)
```yaml
sources:
  - DART (한국)
  - SEC (미국)
  - IR 자료

적용:
  - 상장사 재무 데이터
  - 매출, 이익
  - 사업 부문별 분해
```

### Tier C: 뉴스/언론 (신뢰도 70-85%)
```yaml
sources:
  - Bloomberg, WSJ
  - 한경, 매경
  - 산업 전문지

적용:
  - 주요 사건 (M&A, 규제)
  - 플레이어 동향
  - 시장 변화
```

### Tier D: 추정 (신뢰도 60-80%)
```yaml
source:
  - Estimator (Phase 2-4)

적용:
  - 누락 연도 데이터
  - 비공개 기업
  - 보간 (Interpolation)
```

---

## 🔍 데이터 수집 프로세스

### Step 1: 공식 통계 검색

```python
def _search_official_statistics(self, market, years):
    """
    통계청, 한국은행 등 공식 통계
    
    검색 키워드:
    - "{market} 시장 규모"
    - "{market} 산업 통계"
    - KSIC 코드 기반
    
    Returns:
        {
            year: {
                'value': float,
                'source': 'SRC_KOSIS_2024_001',
                'reliability': 'high'
            }
        }
    """
    
    # KOSIS API 또는 웹 검색
    # ...
    
    return official_data
```

---

### Step 2: 산업 리포트 검색

```python
def _search_industry_reports(self, market, years):
    """
    Gartner, Statista 등 산업 리포트
    
    검색 전략:
    1. RAG: data_sources_registry 검색 (50개)
    2. Web Search: "{market} market size {year}"
    3. 수동 수집: 주요 리포트 구매
    
    Returns:
        연도별 데이터 + 출처
    """
    
    # RAG 우선
    rag_sources = self.source_store.similarity_search(
        f"{market} market size historical data"
    )
    
    # Web Search 보조
    # ...
    
    return industry_data
```

---

### Step 3: 공시 데이터 검색

```python
def _search_public_filings(self, market, years):
    """
    상장사 공시 자료 (DART, SEC)
    
    프로세스:
    1. 주요 플레이어 식별 (상장사)
    2. 연도별 재무제표 수집
    3. 매출 추출 (사업 부문별)
    
    Returns:
        플레이어별 연도별 데이터
    """
    
    # DART API 활용 (구현 필요)
    # 또는 수동 수집
    
    return public_data
```

---

### Step 4: 뉴스/사건 검색

```python
def _search_news_events(self, market, years):
    """
    주요 사건 추출
    
    검색:
    - "{market} M&A {year}"
    - "{market} 규제 {year}"
    - "{market} 진입 {year}"
    
    Returns:
        [
            {
                'year': 2018,
                'event': '규제 완화',
                'source': 'SRC_NEWS_001',
                'impact': 'high'
            }
        ]
    """
    
    # 키워드 기반 뉴스 검색
    # ...
    
    return events
```

---

### Step 5: 데이터 Gap 식별

```python
def _identify_data_gaps(self, collected_data, years):
    """
    누락 데이터 파악 → Estimator 요청 리스트
    
    Returns:
        {
            'missing_years': [2016, 2017, 2019],
            'missing_players': ['Player C (비공개)'],
            'confidence': 'medium',
            'estimator_requests': [
                {
                    'type': 'market_size',
                    'year': 2017,
                    'context': {'neighbors': [(2015, 500), (2020, 1200)]}
                },
                {
                    'type': 'player_share',
                    'player': 'Player C',
                    'year': 2020,
                    'context': {'industry': 'music_streaming'}
                }
            ]
        }
    """
    
    gaps = {'missing_years': [], 'estimator_requests': []}
    
    # 누락 연도 파악
    for year in years:
        if year not in collected_data['market_size_by_year']:
            gaps['missing_years'].append(year)
            
            # Estimator 요청 생성
            gaps['estimator_requests'].append({
                'type': 'market_size',
                'year': year,
                'context': self._get_neighbor_years(collected_data, year)
            })
    
    return gaps
```

---

### Step 6: Estimator 협업 (Gap 채우기)

```python
def fill_data_gaps_with_estimator(self, collected_data, gaps):
    """
    Estimator 협업으로 누락 데이터 채우기
    
    Process:
    1. Validator가 Gap 식별
    2. Estimator에게 추정 요청
    3. Estimator 결과 받아서 통합
    4. 신뢰도 표시 (추정치임을 명시)
    """
    
    from umis_rag.agents.estimator import EstimatorRAG
    estimator = EstimatorRAG()
    
    for request in gaps['estimator_requests']:
        if request['type'] == 'market_size':
            # 보간 추정
            result = estimator.estimate(
                question=f"{market} {request['year']}년 시장 규모는?",
                context=request['context']
            )
            
            # 결과 통합 (추정치 표시)
            collected_data['market_size_by_year'][request['year']] = {
                'value': result.value,
                'source': f'EST_{result.estimation_id}',
                'reliability': 'estimated',
                'confidence': result.confidence,
                'method': result.phase
            }
    
    return collected_data
```

---

## 📋 데이터 수집 계획 (우선순위 산업)

### P0-1: 음악 스트리밍 (2015-2025)

**Validator 작업**:
```yaml
Day 1-2: 시장 규모 데이터
  sources:
    - Statista: Global Streaming Market
    - KOCCA: 한국 음악 산업 백서
    - Gartner: Music Streaming Forecast
  
  목표:
    - 연도별 시장 규모 (11년치)
    - 글로벌 + 한국

Day 3: 플레이어 데이터
  sources:
    - Spotify IR (상장사, 공개)
    - Apple IR (Services 부문)
    - YouTube Music (추정 필요 → Estimator)
  
  목표:
    - Top 3 점유율 (연도별)

Day 4: 주요 사건
  sources:
    - 뉴스 아카이브 (한경, 매경)
    - 업계 리포트
  
  목표:
    - 주요 사건 10개 이상

Day 5: 데이터 통합 및 Gap 식별
  - Estimator에게 요청 리스트 작성
  - SRC_ID 부여
```

**Estimator 작업** (Validator 요청 시):
```yaml
추정 항목:
  - YouTube Music 점유율 (2020-2025)
  - 누락 연도 시장 규모 (보간)
  - 기타 플레이어 (합계)

방법:
  - Phase 2: Validator 기존 데이터로 보간
  - Phase 3: 글로벌 데이터 조정
```

**예상 결과**:
```yaml
market_size_by_year:
  2015: {value: 500, source: SRC_KOCCA_2016, reliability: high}
  2016: {value: 650, source: EST_001, reliability: estimated, confidence: 0.85}
  2017: {value: 800, source: EST_002, reliability: estimated, confidence: 0.85}
  2018: {value: 1200, source: SRC_STATISTA_2019, reliability: high}
  2020: {value: 1800, source: SRC_KOCCA_2021, reliability: high}
  2025: {value: 2500, source: SRC_GARTNER_2025, reliability: medium}

data_quality:
  total_years: 11
  verified_years: 4 (36%)
  estimated_years: 7 (64%)
  avg_confidence: 0.82
```

---

### P0-2: 배달 앱 (2010-2025)

**Validator 작업**:
```yaml
Day 1-2: 시장 규모
  sources:
    - 통계청: 음식 배달 산업
    - 배달 플랫폼 공시 (상장 시)
    - 산업 리포트

Day 3: 플레이어
  sources:
    - 배달의민족: 언론 자료
    - 쿠팡이츠: 공시 자료
    - 요기요: 합병 전 데이터

Day 4: 규제 변화 사건
  sources:
    - 국회 입법 자료
    - 공정위 자료
  
  목표:
    - 규제 변화 타임라인
```

---

## 🔗 Agent 협업 프로토콜

### Validator → Estimator

**요청 형식**:
```python
estimator_request = {
    'type': 'interpolation',  # or 'estimation'
    'question': '음악 스트리밍 2017년 시장 규모는?',
    'context': {
        'market': '음악 스트리밍',
        'year': 2017,
        'known_data': {
            2015: 500,
            2020: 1200
        },
        'cagr_hint': 0.15  # 참고용
    }
}

# Estimator 호출
result = estimator.estimate(**estimator_request)

# 결과:
# {
#     'value': 800,
#     'confidence': 0.85,
#     'method': 'linear_interpolation with CAGR adjustment',
#     'estimation_id': 'EST_001'
# }
```

### Validator → Observer

**전달 형식**:
```python
validated_historical_data = {
    'market': '음악 스트리밍',
    'period': (2015, 2025),
    'market_size_by_year': {...},  # 완성 (검증 + 추정)
    'players_by_year': {...},
    'events': [...],
    'data_quality': {
        'verified_ratio': 0.36,
        'estimated_ratio': 0.64,
        'avg_confidence': 0.82,
        'reliability': 'medium-high'
    }
}

# Observer에게 전달
observer.analyze_market_timeline_from_validated_data(validated_historical_data)
```

---

## ⚠️ 데이터 품질 기준

### 최소 요구사항

**시장 규모**:
- 최소 5년치 데이터
- 검증된 데이터 30% 이상
- 평균 신뢰도 > 0.7

**플레이어**:
- Top 3 플레이어 연도별 추적
- 주요 진입/퇴출 파악

**사건**:
- 주요 사건 최소 5개
- 변곡점 관련 사건 필수

**품질 등급**:
```yaml
High (A):
  - 검증 데이터 50%+
  - 평균 신뢰도 > 0.8

Medium (B):
  - 검증 데이터 30-50%
  - 평균 신뢰도 0.7-0.8

Low (C):
  - 검증 데이터 < 30%
  - 평균 신뢰도 < 0.7
  - 주의: 결과 신뢰도 낮음 명시
```

---

## 📚 산출물

**Validator 산출물**: `historical_data_collection_report.md`

```markdown
# 음악 스트리밍 시장 과거 데이터 수집 보고서

## 데이터 품질 요약
- 기간: 2015-2025 (11년)
- 검증 데이터: 4년 (36%)
- 추정 데이터: 7년 (64%)
- 평균 신뢰도: 0.82 (Medium-High)

## 시장 규모 데이터
[연도별 테이블 + SRC_ID]

## 플레이어 데이터
[플레이어별 점유율 + SRC_ID]

## 주요 사건
[사건 리스트 + SRC_ID]

## 데이터 Gap 및 추정
[Estimator 요청 내역 + 결과]

## 신뢰도 평가
- 시장 규모: High
- 플레이어 점유율: Medium
- 사건 타임라인: High
```

---

## 🎯 Week 2 완료 기준

### Validator 작업
- [ ] 음악 스트리밍 데이터 수집 완료
- [ ] 배달 앱 데이터 수집 완료
- [ ] historical_data_collection_report.md (2개)

### Estimator 작업
- [ ] 누락 데이터 추정 (요청 시)
- [ ] 보간 알고리즘 구현

**다음**: Week 3 코드 구현 착수

---

**문서 끝**





