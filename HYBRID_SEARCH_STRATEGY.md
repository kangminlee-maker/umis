# Validator + Estimator 하이브리드 검색 전략 (v7.7.0+)

**날짜**: 2025-11-12  
**버전**: v7.7.0  
**목적**: AI 주도 검색(Validator) + 자동화 검색(Estimator) 최적 조합

---

## 🎯 핵심 아이디어

Validator의 **지능형 판단**과 Estimator의 **빠른 자동화**를 결합하여 **최고의 검색 품질**과 **최소의 비용/시간**을 달성합니다.

---

## 📊 현재 통합 상태 (v7.7.0)

### ✅ 이미 구현된 통합

```python
# Estimator Phase 2에서 Validator 활용 (기존)
estimator = EstimatorRAG()
result = estimator.estimate("한국 인구는?")

# Phase 0: Literal (프로젝트 데이터) → 없음
# Phase 1: Direct RAG (학습 규칙) → 없음
# ⭐ Phase 2: Validator.search_definite_data() → 찾음! (85% 커버)
#   → Validator RAG: data_sources_registry 검색
#   → 확정 데이터 있으면 즉시 반환 (추정 불필요)
# Phase 3: Guestimation → 스킵
# Phase 4: Fermi → 스킵
```

**특징**:
- Validator의 RAG (Vector Search)만 활용
- Validator의 AI 검색(Creative Sourcing)은 미활용
- 자동 실행 (사용자 개입 없음)

---

## 🚀 제안: 3-Layer 하이브리드 전략

### Layer 1: 완전 자동화 (Fast Track)
**대상**: 단순 사실 질문 (80% 커버)  
**소요**: 1-15초  
**비용**: $0-0.005

```
Phase 0 (Literal) → Phase 1 (RAG) → Phase 2 (Validator RAG) → Phase 3 (Web 자동)
                                              ↓
                                         확정 데이터 발견
                                              ↓
                                         즉시 반환 ✅
```

**예시**:
- "한국 인구는?" → Phase 2 (Validator RAG) → 51,169,148명 (1초)
- "서울 면적은?" → Phase 3 (Web Search) → 605km² (12초)

### Layer 2: AI 보조 (Smart Track)
**대상**: 복잡한 맥락 질문 (15% 커버)  
**소요**: 20-60초  
**비용**: $0.02-0.05

```
Estimator 자동 시도 (Phase 0-3)
         ↓
    실패 or 낮은 신뢰도 (<0.7)
         ↓
    Validator AI 개입
         ↓
    Creative Sourcing (12가지)
         ↓
    AI가 최적 전략 선택
         ↓
    Estimator 재시도 ✅
```

**예시**:
- "한국 B2B SaaS 평균 CAC는?"
  1. Estimator 시도 → confidence 0.6 (낮음)
  2. Validator AI 호출 → "Gartner B2B SaaS 리포트" 추천
  3. AI가 리포트 검색 → CAC 데이터 발견
  4. Estimator 재계산 → confidence 0.9 ✅

### Layer 3: 전문가 모드 (Expert Track)
**대상**: 데이터 없는 탐색적 질문 (5% 커버)  
**소요**: 60-180초  
**비용**: $0.05-0.15

```
사용자: "이 시장 데이터 어디서 구해?"
    ↓
Validator AI 주도
    ↓
12가지 Creative Sourcing 평가
    ↓
추천 전략 + 검색어 생성
    ↓
사용자/AI가 수동 검색
    ↓
데이터 발견 → Estimator로 학습 ✅
```

**예시**:
- "북한 GDP는?" (데이터 부족)
  1. Estimator 실패 (Phase 0-4 모두)
  2. Validator AI: "CIA World Factbook, 한국은행 추정치" 추천
  3. AI가 검색 → 근사값 발견
  4. Learning에 저장 → 다음부터 Phase 1에서 처리

---

## 🔧 구현 방안

### 방안 1: Estimator에 AI Fallback 추가 (권장)

```python
# umis_rag/agents/estimator/estimator.py

def estimate(self, question: str, context=None) -> EstimationResult:
    """5-Phase + AI Fallback"""
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Phase 0-4: 기존 자동화 프로세스
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    result = self._try_phases_0_to_4(question, context)
    
    if result and result.confidence >= 0.70:
        return result  # 자동 성공 ✅
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Phase 5: AI Fallback (v7.8.0+)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    if settings.umis_mode == "native":
        logger.info("[Phase 5] AI Fallback: Validator Creative Sourcing 추천")
        
        # Validator에게 소싱 전략 요청
        strategies = self.validator.recommend_sourcing_strategies(
            question=question,
            failed_phases=[0, 1, 2, 3, 4],
            context=context
        )
        
        # AI에게 전략 제공
        return {
            "phase": 5,
            "mode": "ai_assisted",
            "strategies": strategies,  # 12가지 중 추천 3-5개
            "instruction": (
                "자동 추정 실패. Validator가 추천하는 전략으로 데이터를 찾아주세요:\n\n"
                f"{strategies}\n\n"
                "데이터 발견 시 Estimator에 학습시켜주세요."
            )
        }
    
    # External 모드: AI API 호출로 자동 처리
    else:
        return self._ai_assisted_search(question, strategies)
```

### 방안 2: Validator에 Estimator 연동 추가

```python
# umis_rag/agents/validator.py

def find_and_estimate(
    self, 
    question: str,
    context: Optional[Context] = None
) -> Dict[str, Any]:
    """
    통합 검색: 출처 찾기 + 값 추정
    
    Process:
    1. Creative Sourcing (AI 주도)
    2. 데이터 발견 시 Estimator로 값 추정
    3. 결과 통합 반환
    """
    
    # Step 1: AI가 소싱 전략 선택
    strategies = self._select_sourcing_strategies(question)
    
    # Step 2: AI가 데이터 검색
    sources = self._ai_search_with_strategies(question, strategies)
    
    # Step 3: Estimator로 값 추정
    if sources:
        # Estimator에게 값 추정 요청
        estimator = get_estimator_rag()
        result = estimator.estimate(
            question=question,
            context=context,
            discovered_sources=sources  # 신규 파라미터
        )
        
        return {
            "sources": sources,
            "estimate": result,
            "hybrid": True,
            "workflow": "Validator AI → Estimator Auto"
        }
    
    return {"sources": [], "estimate": None}
```

### 방안 3: 지능형 라우팅 (가장 정교)

```python
# umis_rag/agents/hybrid_router.py (신규)

class HybridSearchRouter:
    """
    질문 복잡도를 분석하여 최적 경로 선택
    """
    
    def route(self, question: str) -> str:
        """
        질문 분석 → 경로 결정
        
        Returns:
            "fast_track"    - Estimator 자동 (Phase 0-4)
            "smart_track"   - Estimator → Validator AI
            "expert_track"  - Validator AI 주도
        """
        
        complexity = self._analyze_complexity(question)
        
        if complexity < 0.3:
            return "fast_track"  # 단순 사실
        elif complexity < 0.7:
            return "smart_track"  # 복잡한 맥락
        else:
            return "expert_track"  # 탐색적
    
    def _analyze_complexity(self, question: str) -> float:
        """
        복잡도 점수 계산 (0.0-1.0)
        
        낮음 (0.0-0.3): "한국 인구는?"
        중간 (0.3-0.7): "한국 B2B SaaS 평균 CAC는?"
        높음 (0.7-1.0): "북한 GDP는?"
        """
        
        score = 0.0
        
        # 1. 키워드 분석
        if any(kw in question for kw in ["인구", "면적", "GDP", "수도"]):
            score += 0.1  # 단순 사실
        
        if any(kw in question for kw in ["평균", "CAC", "LTV", "Churn"]):
            score += 0.3  # 비즈니스 지표
        
        if any(kw in question for kw in ["B2B", "SaaS", "특정 산업"]):
            score += 0.2  # 도메인 특화
        
        # 2. 데이터 가용성 예측
        availability = self._check_data_availability(question)
        if availability < 0.5:
            score += 0.4  # 데이터 부족 예상
        
        return min(score, 1.0)
```

---

## 📈 예상 효과

### 성능 비교 (100개 질문 기준)

| 메트릭 | 현재 (Estimator만) | 제안 (하이브리드) | 개선율 |
|--------|-------------------|-----------------|--------|
| **평균 응답 시간** | 15초 | 12초 | **20% ↓** |
| **성공률** | 95% | 98% | **3%p ↑** |
| **평균 신뢰도** | 0.82 | 0.88 | **7% ↑** |
| **평균 비용** | $0.50 | $0.80 | 60% ↑ |

**트레이드오프**:
- 성공률 +3%p (95% → 98%)
- 신뢰도 +7% (0.82 → 0.88)
- 비용 +60% ($0.50 → $0.80)
- **ROI**: 품질 향상 대비 비용 증가 합리적

### 질문 유형별 경로 분포 (예상)

```
Fast Track (80%): Estimator 자동
  - 소요: 1-15초
  - 비용: $0-0.005
  - 예: "한국 인구", "서울 면적"

Smart Track (15%): Estimator → Validator AI
  - 소요: 20-60초
  - 비용: $0.02-0.05
  - 예: "B2B SaaS CAC", "음식 배달 시장 규모"

Expert Track (5%): Validator AI 주도
  - 소요: 60-180초
  - 비용: $0.05-0.15
  - 예: "북한 GDP", "특수 산업 지표"
```

---

## 🎯 단계별 구현 로드맵

### Phase 1: 기초 통합 (v7.8.0, 1-2주)

1. **Estimator에 AI Fallback 추가**
   ```python
   # Phase 5: AI Fallback
   if result.confidence < 0.70:
       return self._request_ai_assistance(question)
   ```

2. **Validator에 recommend_sourcing_strategies() 추가**
   ```python
   def recommend_sourcing_strategies(self, question, failed_phases):
       # 12가지 중 적합한 3-5개 추천
       return strategies
   ```

3. **테스트 및 검증**
   - 100개 질문으로 A/B 테스트
   - 성공률, 신뢰도, 비용 측정

### Phase 2: 지능형 라우팅 (v7.9.0, 2-3주)

1. **HybridSearchRouter 구현**
   - 복잡도 분석 알고리즘
   - 경로 결정 로직

2. **Estimator와 Validator 통합**
   - 양방향 통신
   - 데이터 공유

3. **성능 최적화**
   - 캐싱
   - 병렬 처리

### Phase 3: 학습 시스템 (v8.0.0, 1개월)

1. **AI 검색 결과 자동 학습**
   - Validator AI가 찾은 데이터 → Estimator Phase 1에 저장
   - 다음부터 자동 처리

2. **피드백 루프**
   - 사용자 확인 → 신뢰도 업데이트
   - 실패 패턴 분석 → 전략 개선

3. **성능 모니터링**
   - 대시보드
   - 자동 리포트

---

## 💡 사용 예시

### 예시 1: Fast Track (자동 성공)

```python
from umis_rag.agents import EstimatorRAG

estimator = EstimatorRAG()
result = estimator.estimate("한국 인구는?")

# Phase 2: Validator RAG → 51,169,148명
# 소요: 1초
# 비용: $0
# 신뢰도: 1.0
```

### 예시 2: Smart Track (AI 보조)

```python
result = estimator.estimate("한국 B2B SaaS 평균 CAC는?")

# Phase 0-3 시도 → confidence 0.6 (낮음)
# Phase 5: AI Fallback
#   → Validator AI: "Gartner SaaS 리포트" 추천
#   → AI가 검색 → 데이터 발견
#   → Estimator 재계산 → confidence 0.9
# 소요: 35초
# 비용: $0.03
# 신뢰도: 0.9
```

### 예시 3: Expert Track (AI 주도)

```python
from umis_rag.agents import ValidatorRAG

validator = ValidatorRAG()
result = validator.find_and_estimate("북한 GDP는?")

# Validator AI 주도:
#   1. Creative Sourcing: "CIA World Factbook" 추천
#   2. AI 검색 → 근사값 발견
#   3. Estimator 학습 → 다음부터 자동
# 소요: 90초
# 비용: $0.08
# 신뢰도: 0.7 (추정치)
```

---

## 🔍 장단점 요약

### 하이브리드 전략의 장점

1. ✅ **최고의 성공률** (98%)
   - Estimator 자동 (95%) + Validator AI (3%)

2. ✅ **최적의 비용/성능**
   - Fast Track 80% → $0 (자동)
   - Smart Track 15% → $0.03 (AI 보조)
   - Expert Track 5% → $0.08 (AI 주도)

3. ✅ **학습하는 시스템**
   - AI가 찾은 데이터 → Estimator 학습
   - 다음부터 자동 처리 (Fast Track으로 이동)

4. ✅ **사용자 경험 개선**
   - 80%는 즉시 답변 (1-15초)
   - 20%만 약간 느림 (20-180초)
   - 실패율 2% (vs 5%)

### 하이브리드 전략의 단점

1. ⚠️ **복잡도 증가**
   - 경로 결정 로직 필요
   - Phase 5 추가 구현

2. ⚠️ **비용 증가**
   - $0.50 → $0.80 (60% ↑)
   - 단, 품질 대비 합리적

3. ⚠️ **응답 시간 편차**
   - Fast: 1-15초
   - Smart: 20-60초
   - Expert: 60-180초

---

## 📝 결론

**권장 전략**: Phase 1 (기초 통합)부터 시작

1. **즉시 구현 가능** (1-2주)
2. **점진적 개선** (Phase 2, 3)
3. **학습 효과** (사용할수록 Fast Track 증가)

**기대 효과**:
- 성공률: 95% → 98% (+3%p)
- 신뢰도: 0.82 → 0.88 (+7%)
- 비용: $0.50 → $0.80 (+60%, but 합리적)

**ROI**: 품질 향상이 비용 증가보다 크므로 **도입 권장** ✅

---

**작성자**: UMIS Team  
**버전**: v7.7.0  
**다음**: v7.8.0 (Phase 1 구현)

