# Week 4-6 남은 작업
**기간**: Week 4-6 (3주)
**목표**: 실제 데이터 수집 + RAG 구축 + 통합 테스트
**상태**: 코드 프레임워크 완성, 데이터 작업 대기

---

## 현재 상태

### ✅ 완료 (Week 1-3)
- Deliverable Spec
- 30개 패턴 skeleton
- Observer 코드 (~560줄)
- Validator 코드 (~190줄)
- Quantifier 코드 (~200줄)

**총 코드**: ~950줄 추가

### ⏳ 남은 작업 (Week 4-6)

---

## Week 4: 단위 테스트 + 알고리즘 개선

### 작업 내용

**1. 단위 테스트 작성**
```python
# tests/test_observer_timeline.py

def test_analyze_market_timeline():
    """Timeline 분석 기본 동작 테스트"""
    observer = ObserverRAG()
    
    # Mock 데이터
    result = observer.analyze_market_timeline(
        market="테스트 시장",
        start_year=2015,
        end_year=2020
    )
    
    assert 'events' in result
    assert 'market_size_trend' in result
    assert 'inflection_points' in result

def test_event_classification():
    """사건 분류 테스트"""
    # ...

def test_hhi_pattern_matching():
    """HHI 패턴 매칭 테스트"""
    # ...
```

**2. Validator 실제 구현 시작**
```python
# umis_rag/agents/validator.py

def _search_official_statistics(self, market, years):
    """
    통계청 API 연동 (실제 구현)
    
    TODO:
    - KOSIS API 키 설정
    - 시장명 → KSIC 코드 매핑
    - API 호출 및 파싱
    """
    # 구현 시작
```

**3. 변곡점 감지 정확도 개선**
```python
# Quantifier 알고리즘 튜닝
# - 임계값 조정 (30% → 25%?)
# - 이상치 제거
# - 신뢰도 계산 개선
```

**예상 시간**: 5일

---

## Week 5: RAG 데이터 작성 + Collection 구축

### 작업 1: 30개 패턴 상세 작성

**P0 패턴 (5개) - 최우선**:
```yaml
evolution_001-005:
  - phases 상세 작성 (metrics, indicators)
  - case_studies 2-3개씩
  - trigger_events 구체화
  - 참고 자료 추가
```

**P1 패턴 (10개)**:
```yaml
evolution_006-015:
  - 기본 phases
  - case_studies 1-2개
  - skeleton 완성
```

**P2 패턴 (15개)**:
```yaml
evolution_016-030:
  - skeleton만 (향후 보완)
```

**예상 시간**: 3일

---

### 작업 2: RAG Collection 구축

**스크립트 작성**: `scripts/build_evolution_patterns_rag.py`

```python
#!/usr/bin/env python3
"""
market_evolution_patterns.yaml → ChromaDB Collection
"""

import yaml
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

def build_evolution_patterns_collection():
    """
    historical_evolution_patterns Collection 구축
    """
    
    # 1. YAML 로드
    with open('data/raw/market_evolution_patterns.yaml') as f:
        data = yaml.safe_load(f)
    
    patterns = data['patterns']
    
    # 2. 문서 생성
    documents = []
    metadatas = []
    
    for pattern in patterns:
        # Content: 전체 패턴 텍스트
        content = f"""
{pattern['pattern_name']}

{pattern['description']}

Phases:
{yaml.dump(pattern.get('phases', []))}

Case Studies:
{yaml.dump(pattern.get('case_studies', []))}
"""
        
        documents.append(content)
        metadatas.append({
            'pattern_id': pattern['pattern_id'],
            'pattern_name': pattern['pattern_name'],
            'pattern_type': pattern['pattern_type']
        })
    
    # 3. ChromaDB에 추가
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
    
    collection = Chroma.from_texts(
        texts=documents,
        metadatas=metadatas,
        embedding=embeddings,
        collection_name="historical_evolution_patterns",
        persist_directory="data/chroma"
    )
    
    print(f"✅ {len(documents)}개 패턴 인덱싱 완료")

if __name__ == "__main__":
    build_evolution_patterns_collection()
```

**실행**:
```bash
python3 scripts/build_evolution_patterns_rag.py
```

**예상 시간**: 1일

---

### 작업 3: Observer에 RAG 연동

```python
# umis_rag/agents/observer.py

class ObserverRAG:
    def __init__(self):
        # 기존 Collections
        self.structure_store = ...
        self.chain_store = ...
        
        # 신규 Collection
        try:
            self.evolution_store = Chroma(
                collection_name="historical_evolution_patterns",
                embedding_function=self.embeddings,
                persist_directory=str(settings.chroma_persist_dir)
            )
            logger.info(f"  ✅ 진화 패턴: {self.evolution_store._collection.count()}개")
        except Exception as e:
            logger.warning(f"  ⚠️ 진화 패턴 Collection 없음: {e}")
            self.evolution_store = None
```

**예상 시간**: 1일

---

## Week 6: 통합 테스트

### 테스트 시나리오

**시나리오 1: 음악 스트리밍 (데이터 풍부)**
```python
# 실제 실행
observer = ObserverRAG()
result = observer.analyze_market_timeline(
    market="음악 스트리밍",
    start_year=2015,
    end_year=2025
)

# 검증
assert len(result['events']) >= 5  # 주요 사건 5개 이상
assert len(result['inflection_points']) >= 1  # 변곡점 최소 1개
assert result['structural_evolution']['pattern']  # 패턴 매칭됨
assert result['data_quality']['grade'] in ['A', 'B']  # 품질 양호

# Deliverable 확인
assert os.path.exists(result['deliverable_path'])
```

**시나리오 2: 배달 앱 (플랫폼 전환)**
```python
result = observer.analyze_market_timeline(
    market="배달",
    start_year=2010,
    end_year=2025
)

# 예상 패턴
assert result['structural_evolution']['pattern']['pattern_id'] == 'evolution_002'  # 플랫폼 전환
```

**시나리오 3: B2B SaaS (구독 전환)**
```python
result = observer.analyze_market_timeline(
    market="B2B SaaS",
    start_year=2010,
    end_year=2025
)

# 예상 패턴
assert result['structural_evolution']['pattern']['pattern_id'] == 'evolution_004'  # 구독 전환
```

---

### 검증 기준

**필수 통과**:
- [ ] 3개 시나리오 모두 실행 완료
- [ ] Deliverable 자동 생성
- [ ] Mermaid 차트 포함
- [ ] 변곡점 1개 이상 감지
- [ ] 데이터 품질 B급 이상

**품질 기준**:
- [ ] 패턴 매칭 정확도 > 80%
- [ ] 변곡점 감지 정확도 > 70%
- [ ] 데이터 수집 성공률 > 60%

---

## ⚠️ 실제 데이터 수집 (Week 5 병행)

### 필요한 작업

**1. 통계청 API 연동** (선택):
```python
# Validator에 KOSIS API 연동
# - API 키 발급
# - 시장명 → KSIC 코드 매핑
# - 데이터 파싱
```

**난이도**: 중  
**우선순위**: P1 (없어도 진행 가능, 수동 수집)

---

**2. 수동 데이터 수집** (필수):
```yaml
음악 스트리밍:
  - Statista: 글로벌 시장 규모 (2015-2025)
  - KOCCA: 한국 음악 산업 백서
  - Spotify IR: 플레이어 데이터
  
  → data/manual/music_streaming_historical.yaml 작성

배달 앱:
  - 통계청: 음식 배달 산업
  - 배민/쿠팡 IR: 플레이어 데이터
  - 뉴스 아카이브: 주요 사건
  
  → data/manual/delivery_historical.yaml 작성
```

**난이도**: 중  
**우선순위**: P0 (필수)  
**예상 시간**: 2-3일

---

**3. Validator 로딩 로직**:
```python
def _search_manual_data(self, market, years):
    """
    수동 수집 데이터 로딩
    
    파일 구조:
    data/manual/{market}_historical.yaml
    """
    
    file_path = f"data/manual/{market}_historical.yaml"
    
    if os.path.exists(file_path):
        with open(file_path) as f:
            data = yaml.safe_load(f)
        return data
    
    return {}
```

---

## 📊 Week 4-6 요약

| Week | 작업 | 산출물 | 시간 |
|------|------|--------|------|
| Week 4 | 단위 테스트 + 알고리즘 개선 | 테스트 코드, 버그 수정 | 5일 |
| Week 5 | P0 패턴 상세 + RAG 구축 + 수동 데이터 | 5개 패턴, Collection, 2개 데이터 | 5일 |
| Week 6 | 통합 테스트 + 문서화 | 3개 시장 분석, 문서 | 5일 |

**총**: 15일 (3주)

---

## 🎯 Gap #1 완료 기준

### 기능적 완성
- [x] Observer.analyze_market_timeline() 구현
- [x] Validator.search_historical_data() 구현
- [x] Quantifier.analyze_growth_with_timeline() 구현
- [ ] RAG Collection 구축 (Week 5)
- [ ] 통합 테스트 (Week 6)

### 품질 기준
- [ ] 3개 실제 시장 분석 성공
- [ ] 변곡점 감지 정확도 > 70%
- [ ] Deliverable 자동 생성
- [ ] 데이터 품질 B급 이상

---

## 💡 간소화 옵션 (빠른 완료)

### 최소 구현 (Week 5-6 압축)

**수동 데이터만 사용**:
```yaml
Week 5:
  - P0 패턴 5개만 상세 작성
  - 음악 스트리밍 수동 데이터만
  - RAG Collection (5개 패턴)

Week 6:
  - 음악 스트리밍 1개 시장만 테스트
  - 기본 Deliverable 생성
```

**효과**:
- Gap #1 기본 기능 완성
- Q3, Q4-5, Q11 → 80-90% 달성 (Tier 1 미달성이지만 개선)
- 향후 점진적 보완 가능

**기간**: 2주 (Week 5-6 압축)

---

## 🚀 권장 진행 방안

### 옵션 A: 완전 구현 (원래 계획)
- Week 4-6 전체 진행
- 3개 시장 테스트
- 품질 Tier 1 달성

**기간**: 3주  
**효과**: 완전한 기능

---

### 옵션 B: 최소 구현 (빠른 완료)
- Week 5-6만 (압축)
- 1개 시장 테스트
- 기본 기능만

**기간**: 2주  
**효과**: 기본 동작, 향후 보완

---

## 📋 즉시 결정 필요

**선택**:
- [ ] 옵션 A: 완전 구현 (3주)
- [ ] 옵션 B: 최소 구현 (2주)

**리소스**:
- 계속 진행? (Week 4-6)
- 일단 중단? (Gap #2, #3 우선)

---

**문서 끝**

