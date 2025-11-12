# Observer.analyze_market_timeline() 메서드 설계
**목적**: 시장 시계열 분석 핵심 메서드
**버전**: v7.8.0
**파일**: umis_rag/agents/observer.py

---

## 메서드 시그니처

```python
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
        
        Args:
            market: 시장 이름 (예: "음악 스트리밍")
            start_year: 분석 시작 연도 (예: 2015)
            end_year: 분석 종료 연도 (예: 2025)
            focus_areas: 집중 영역 (선택)
                ['market_size', 'players', 'structure', 'technology']
        
        Returns:
            {
                'events': List[Event],
                'market_size_trend': List[Tuple[int, float]],
                'player_share_evolution': Dict[str, List[Tuple[int, float]]],
                'inflection_points': List[InflectionPoint],
                'structural_evolution': Dict,
                'mermaid_charts': Dict[str, str]
            }
        """
```

---

## 구현 로직

### Step 1: 데이터 수집 (Validator 협업)

```python
def _collect_historical_data(
    self,
    market: str,
    start_year: int,
    end_year: int
) -> Dict[str, Any]:
    """
    과거 데이터 수집
    
    데이터 소스 우선순위:
    1. Quantifier: 연도별 SAM 데이터 (있으면)
    2. Validator: 산업 리포트, 통계 자료
    3. Web Search: 뉴스, 기사 (보조)
    4. Estimator: 누락 연도 추정
    
    Returns:
        {
            'market_size_by_year': {year: size, ...},
            'players_by_year': {year: {player: share, ...}, ...},
            'events': [Event, ...],
            'sources': [SRC_ID, ...]
        }
    """
    
    # Validator에게 과거 데이터 요청
    from umis_rag.agents.validator import ValidatorRAG
    validator = ValidatorRAG()
    
    historical_sources = validator.search_historical_data(
        market=market,
        years=range(start_year, end_year + 1)
    )
    
    # Quantifier에게 과거 SAM 요청 (계산된 것 있으면)
    # ...
    
    # 데이터 통합
    # ...
    
    return collected_data
```

---

### Step 2: 사건 추출 및 분류

```python
def _extract_and_classify_events(
    self,
    raw_data: Dict,
    start_year: int,
    end_year: int
) -> List[Dict]:
    """
    텍스트에서 주요 사건 추출 및 분류
    
    분류 카테고리:
    - player: 플레이어 진입/퇴출/M&A
    - regulation: 규제 변화
    - technology: 기술 도입/성숙
    - ma: M&A
    - economic: 경제 환경 (COVID, 경기 침체 등)
    
    방법:
    1. 키워드 기반 추출 (규칙)
    2. LLM 분류 (애매한 경우)
    
    Returns:
        [
            {
                'year': 2018,
                'month': 3,
                'event': '저작권법 개정',
                'category': 'regulation',
                'impact': 'high',
                'description': '...',
                'source': 'SRC_XXX'
            },
            ...
        ]
    """
    
    events = []
    
    # 1. 키워드 기반 추출
    keywords = {
        'player': ['진입', '퇴출', '설립', '파산'],
        'regulation': ['규제', '법안', '개정', '제재'],
        'technology': ['도입', '상용화', '특허', '혁신'],
        'ma': ['인수', '합병', 'M&A', '투자']
    }
    
    # 2. LLM 분류 (애매한 경우)
    # ...
    
    return events
```

---

### Step 3: 시계열 추세 분석 (Quantifier 협업)

```python
def _analyze_trends(
    self,
    market_size_data: Dict[int, float],
    player_share_data: Dict[int, Dict[str, float]]
) -> Dict[str, Any]:
    """
    시계열 추세 분석
    
    Quantifier 협업:
    - CAGR 계산
    - YoY 성장률
    - 변곡점 감지 (2차 미분)
    
    Returns:
        {
            'market_size': {
                'trend': [(year, size), ...],
                'cagr': float,
                'yoy': [(year, rate), ...]
            },
            'players': {
                player_name: {
                    'trend': [(year, share), ...],
                    'growth': 'increasing/decreasing/stable'
                }
            }
        }
    """
    
    # Quantifier에게 분석 요청
    from umis_rag.agents.quantifier import QuantifierRAG
    quantifier = QuantifierRAG()
    
    growth_analysis = quantifier.analyze_growth_with_timeline(
        market=self.current_market,
        historical_data=list(market_size_data.items())
    )
    
    return {
        'market_size': growth_analysis,
        'players': self._analyze_player_trends(player_share_data)
    }
```

---

### Step 4: 변곡점 자동 감지

```python
def _detect_inflection_points(
    self,
    trend_data: List[Tuple[int, float]],
    events: List[Dict]
) -> List[Dict]:
    """
    변곡점 자동 감지
    
    방법:
    1. 성장률 급변 감지 (±30% 이상)
    2. 2차 미분 (Quantifier)
    3. 주요 사건과 상관관계
    
    Returns:
        [
            {
                'year': 2018,
                'type': 'acceleration',
                'growth_before': 15%,
                'growth_after': 35%,
                'trigger_event': '규제 완화',
                'impact': 'high',
                'confidence': 0.9
            },
            ...
        ]
    """
    
    inflection_points = []
    
    # Quantifier의 변곡점 감지 활용
    # ...
    
    # 주요 사건과 매칭
    for point in detected_points:
        # 해당 연도 ±1년 내 주요 사건 찾기
        related_events = [
            e for e in events 
            if abs(e['year'] - point['year']) <= 1 and e['impact'] == 'high'
        ]
        
        if related_events:
            point['trigger_event'] = related_events[0]['event']
            point['confidence'] = 0.9
        else:
            point['trigger_event'] = 'Unknown'
            point['confidence'] = 0.6
        
        inflection_points.append(point)
    
    return inflection_points
```

---

### Step 5: 구조 진화 패턴 분석 (RAG)

```python
def _analyze_structural_evolution(
    self,
    hhi_trend: List[Tuple[int, int]],
    player_count: List[Tuple[int, int]],
    events: List[Dict]
) -> Dict[str, Any]:
    """
    구조 진화 패턴 분석 및 RAG 매칭
    
    Returns:
        {
            'hhi_trend': [(year, hhi), ...],
            'pattern': {
                'matched_pattern_id': 'evolution_001',
                'pattern_name': '독점 → 경쟁 → 재편',
                'similarity': 0.92,
                'current_phase': '재편기',
                'reference_case': '통신 시장'
            },
            'evolution_summary': '독점 → 경쟁 → 재편 사이클'
        }
    """
    
    # RAG 검색으로 유사 패턴 찾기
    if hasattr(self, 'evolution_store'):
        # HHI 추이 패턴을 텍스트로
        pattern_description = self._describe_hhi_pattern(hhi_trend)
        
        matched_patterns = self.evolution_store.similarity_search(
            pattern_description,
            k=3
        )
        
        best_match = matched_patterns[0] if matched_patterns else None
    else:
        best_match = None
    
    return {
        'hhi_trend': hhi_trend,
        'pattern': best_match,
        'evolution_summary': self._summarize_evolution(hhi_trend)
    }
```

---

### Step 6: 타임라인 시각화

```python
def _generate_timeline_visualizations(
    self,
    events: List[Dict],
    market_size_trend: List[Tuple[int, float]],
    player_share: Dict
) -> Dict[str, str]:
    """
    Mermaid 차트 자동 생성
    
    Returns:
        {
            'gantt_timeline': mermaid_gantt_code,
            'market_size_chart': mermaid_line_chart,
            'player_share_table': markdown_table
        }
    """
    
    # Template 활용
    from dev_docs.MERMAID_TIMELINE_TEMPLATES import (
        generate_gantt_timeline,
        generate_market_size_chart,
        generate_player_share_table
    )
    
    return {
        'gantt_timeline': generate_gantt_timeline(events),
        'market_size_chart': generate_market_size_chart(
            market_name=self.current_market,
            trend_data=market_size_trend
        ),
        'player_share_table': generate_player_share_table(player_share)
    }
```

---

## 전체 메서드 흐름

```python
def analyze_market_timeline(self, market, start_year, end_year, focus_areas=None):
    """전체 프로세스"""
    
    # Step 1: 데이터 수집 (Validator)
    historical_data = self._collect_historical_data(market, start_year, end_year)
    
    # Step 2: 사건 추출 및 분류
    events = self._extract_and_classify_events(historical_data, start_year, end_year)
    
    # Step 3: 추세 분석 (Quantifier)
    trends = self._analyze_trends(
        historical_data['market_size_by_year'],
        historical_data['players_by_year']
    )
    
    # Step 4: 변곡점 감지
    inflections = self._detect_inflection_points(trends['market_size']['trend'], events)
    
    # Step 5: 구조 진화 패턴 (RAG)
    evolution = self._analyze_structural_evolution(
        hhi_trend=historical_data['hhi_by_year'],
        player_count=historical_data['player_count'],
        events=events
    )
    
    # Step 6: 시각화
    charts = self._generate_timeline_visualizations(
        events, trends['market_size']['trend'], trends['players']
    )
    
    # Step 7: Deliverable 생성
    deliverable = self._generate_timeline_deliverable(
        market, start_year, end_year,
        events, trends, inflections, evolution, charts
    )
    
    return {
        'events': events,
        'market_size_trend': trends['market_size']['trend'],
        'player_share_evolution': trends['players'],
        'inflection_points': inflections,
        'structural_evolution': evolution,
        'mermaid_charts': charts,
        'deliverable_path': deliverable['file_path']
    }
```

---

## 구현 위치

**파일**: `umis_rag/agents/observer.py`
**클래스**: `ObserverRAG`
**추가 줄 수**: ~300-400줄

**의존성**:
- Validator (과거 데이터 수집)
- Quantifier (추세 분석, 변곡점 감지)
- RAG Collection: historical_evolution_patterns
- Mermaid 템플릿 함수

---

## 테스트 케이스

### 케이스 1: 음악 스트리밍
```python
result = observer.analyze_market_timeline(
    market="음악 스트리밍",
    start_year=2015,
    end_year=2025,
    focus_areas=['market_size', 'players', 'technology']
)

# 예상 결과:
# - 8개 주요 사건
# - 2개 변곡점 (2018, 2022)
# - 패턴 매칭: evolution_001
# - Deliverable: market_timeline_analysis.md 생성
```

### 케이스 2: 배달 시장
```python
result = observer.analyze_market_timeline(
    market="배달",
    start_year=2010,
    end_year=2025,
    focus_areas=['players', 'regulation']
)

# 예상 결과:
# - 플랫폼 전환 패턴 매칭
# - 규제 변화 타임라인
```

---

**Week 3 구현 시작 예정**

문서 끝

