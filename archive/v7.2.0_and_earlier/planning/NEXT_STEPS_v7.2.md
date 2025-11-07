# Hybrid Guestimation 다음 작업 리스트
**날짜**: 2025-11-05  
**현재 상태**: Step 1-5 완료 (MVP)  
**버전**: v7.2.0-dev

---

## 📊 현재 완료 상태

### ✅ 완료된 작업 (Step 1-5)

| Step | 작업 | 상태 | 커밋 |
|------|------|------|------|
| Step 1 | Tool Registry 확장 | ✅ | `b323fdc` |
| Step 2 | Guardian 자동 전환 | ✅ | `3c78bcd` |
| Step 3 | Should/Will 분석 | ✅ | `e69c532` |
| Step 4 | KPI Library (MVP) | ✅ | `97f4742` |
| Step 5 | Cursor 통합 & 가이드 | ✅ | `c754a35` |

**총 변경사항**: 19 files, +8,263 insertions

**기능 완성도**:
- Guardian 자동 전환: 100% ✅
- Should/Will 분석: 100% ✅
- Excel 통합: 80% ✅ (Should_vs_Will 시트 추가)
- KPI Library: 10% ✅ (10/100개)
- Domain Reasoner: 30% ⚠️ (s4만 완성, s1-s3, s5-s10 stub)

---

## 🎯 다음 작업 (우선순위)

### 📌 Phase A: 핵심 완성 (즉시 - 2주)

#### A1. Domain Reasoner 엔진 완성 (1주) ⭐⭐⭐⭐⭐

**목표**: 10개 신호 모두 구현 (현재 s4만 완성)

**작업 내용**:

```yaml
현재:
  ✅ s4_behavioral_econ: 완성 (Should/Will)
  ⚠️  s1-s3, s5-s10: Stub (TODO)

구현 필요:
  
  s1_llm_guess:
    파일: "umis_rag/methodologies/domain_reasoner.py"
    메서드: "Signal1_LLMGuess.process()"
    기능: "LLM으로 초안 생성 (빠른 범위 설정)"
    난이도: "⭐ (쉬움)"
    시간: "1시간"
  
  s2_rag_consensus:
    파일: "umis_rag/methodologies/domain_reasoner.py"
    메서드: "Signal2_RAGConsensus.process()"
    기능: |
      UMIS RAG 검색 → 합의 범위 추출
      - explorer_knowledge_base
      - market_benchmarks
      - definition_validation_cases
    연동: "UMIS RAG v3.0 (기존)"
    난이도: "⭐⭐⭐ (중간)"
    시간: "4-6시간"
  
  s3_laws_ethics_physics:
    파일: "umis_rag/methodologies/domain_reasoner.py"
    메서드: "Signal3_Laws.check()"
    기능: "규제/물리/윤리 제약 확인"
    난이도: "⭐⭐⭐⭐ (어려움, 도메인 지식)"
    시간: "6-8시간"
  
  s5_stat_patterns:
    기능: "통계 패턴 (80-20, S-Curve, Elasticity)"
    난이도: "⭐⭐ (쉬움)"
    시간: "2시간"
  
  s6_math_relations:
    기능: "차원 분석, 보존 법칙, Bounds 계산"
    난이도: "⭐⭐⭐ (중간)"
    시간: "3-4시간"
  
  s7_rules_of_thumb:
    기능: "UMIS RAG Rule of Thumb 활용"
    연동: "market_benchmarks, business_model_patterns"
    난이도: "⭐⭐ (쉬움)"
    시간: "2시간"
  
  s8_time_space_bounds:
    기능: "시공간 제약 (개발 기간, 지리, 용량)"
    난이도: "⭐⭐ (쉬움)"
    시간: "2시간"
  
  s9_case_analogies:
    기능: |
      유사 사례 전이 보정
      - success_case_library 검색
      - 6가지 특징 유사도
      - 4가지 조정 계수
    난이도: "⭐⭐⭐⭐ (어려움)"
    시간: "6-8시간"
  
  s10_industry_kpi:
    기능: "KPI 라이브러리 활용 (이미 Rachel에 구현됨)"
    연동: "Validator.validate_kpi_definition()"
    난이도: "⭐ (매우 쉬움, 연동만)"
    시간: "1시간"
```

**예상 시간**: 27-36시간 (1주)

**우선순위**:
1. **s2 (RAG Consensus)**: 가장 중요 (weight 0.9)
2. **s10 (KPI Library)**: Rachel 연동만 (쉬움)
3. **s9 (Case Analogies)**: 신규 시장 필수 (weight 0.85)
4. **s3 (Laws)**: 규제 산업 필수 (weight 1.0)
5. 나머지: s1, s5, s6, s7, s8

---

#### A2. Quantifier 통합 (3일) ⭐⭐⭐⭐

**목표**: Bill이 Hybrid 모드로 SAM 계산

**작업 내용**:

```python
# umis_rag/agents/quantifier.py

def calculate_sam_with_hybrid(
    self,
    market_definition: dict,
    method: str = 'auto'  # 'auto', 'guestimation', 'domain_reasoner'
) -> dict:
    """
    SAM 계산 (하이브리드 모드)
    
    Returns:
        {
            'phase_1': {...},  # Guestimation 결과
            'recommendation': {...},  # Guardian 평가
            'phase_2': {...},  # Domain Reasoner 결과 (if triggered)
            'final_result': {...}
        }
    """
```

**파일**:
- `umis_rag/agents/quantifier.py` (수정)
- `scripts/test_quantifier_hybrid.py` (신규, 테스트)

**난이도**: ⭐⭐⭐ (중간)  
**시간**: 8-12시간 (3일)

---

#### A3. 증거표 자동 생성 (2일) ⭐⭐⭐

**목표**: Domain Reasoner 결과 → 증거표 자동 포맷팅

**작업 내용**:

```python
# umis_rag/methodologies/evidence_table_builder.py (신규)

class EvidenceTableBuilder:
    """증거표 자동 생성"""
    
    def build_table(self, signal_results: dict) -> list:
        """
        신호 결과 → 증거표
        
        Columns:
          - ID (SRC_xxx)
          - 출처
          - 정의
          - 값
          - 지리
          - 기간
          - 방법론
          - 가중치
          - 모순 여부
        """
```

**파일**:
- `umis_rag/methodologies/evidence_table_builder.py` (신규)
- Excel 연동 (Markdown 또는 별도 시트)

**난이도**: ⭐⭐ (쉬움)  
**시간**: 4-6시간 (2일)

---

### 📌 Phase B: 확장 (2-3주)

#### B1. KPI 라이브러리 확장 (1주) ⭐⭐⭐

**목표**: 10개 → 100개 확대

**카테고리별 목표**:

| 카테고리 | 현재 | 목표 | 우선순위 |
|---------|------|------|----------|
| Platform | 2개 | 20개 | ⭐⭐⭐⭐⭐ |
| Subscription | 2개 | 15개 | ⭐⭐⭐⭐⭐ |
| SaaS | 1개 | 15개 | ⭐⭐⭐⭐ |
| E-commerce | 1개 | 15개 | ⭐⭐⭐⭐ |
| Marketplace | 1개 | 10개 | ⭐⭐⭐ |
| Finance | 1개 | 10개 | ⭐⭐⭐ |
| Marketing | 1개 | 10개 | ⭐⭐⭐ |
| General | 1개 | 5개 | ⭐⭐ |

**작업 방법**:
1. `scripts/build_kpi_library.py` 확장
2. UMIS RAG `market_benchmarks.yaml` 참조
3. 산업 표준 문서 참조

**난이도**: ⭐⭐ (반복 작업)  
**시간**: 20-30시간 (1주)

---

#### B2. Verification Log 자동화 (3일) ⭐⭐⭐

**목표**: 검증 로그 자동 생성 및 Excel 통합

**체크리스트**:
- [ ] 단위·차원 일관성 (s6)
- [ ] 규제 준수 (s3)
- [ ] 비교사례 합의 (s2)
- [ ] Should/Will 분리 (s4)

**파일**:
- `umis_rag/methodologies/verification_logger.py` (신규)
- Excel "Verification_Log" 시트 확장

**난이도**: ⭐⭐ (쉬움)  
**시간**: 6-8시간 (3일)

---

#### B3. 민감도 분석 자동화 (3일) ⭐⭐⭐⭐

**목표**: Excel Data Table 활용 민감도 매트릭스

**기능**:
- 변수: 채택률, 단가, 성장률
- 출력: 2D/3D 민감도 표
- 차트: 토네이도 차트

**파일**:
- `umis_rag/deliverables/excel/sensitivity_builder.py` (확장)
- Excel "Sensitivity" 시트 추가

**난이도**: ⭐⭐⭐⭐ (Excel 고급 기능)  
**시간**: 8-10시간 (3일)

---

### 📌 Phase C: 최적화 (2-3주)

#### C1. RAG 검색 최적화 (1주) ⭐⭐⭐⭐

**목표**: Domain Reasoner 속도 개선 (4시간 → 2시간)

**최적화 항목**:
1. **캐싱**: 동일 쿼리 재사용
2. **병렬 처리**: 신호별 독립 실행
3. **k 조정**: k=30 → 적정값 (15-20)
4. **하이브리드 검색**: BM25 + Dense 최적 비율

**파일**:
- `umis_rag/methodologies/domain_reasoner.py` (최적화)
- `umis_rag/core/cache_manager.py` (신규)

**난이도**: ⭐⭐⭐⭐ (성능 튜닝)  
**시간**: 15-20시간 (1주)

---

#### C2. Guardian 품질 평가 강화 (3일) ⭐⭐⭐

**목표**: 신호 다양성, 증거표 완성도 자동 평가

**추가 기준**:
```python
def evaluate_domain_reasoner_quality(result):
    """
    Domain Reasoner 결과 품질 평가
    
    기준:
    - 신호 다양성 (10개 중 몇 개?)
    - 증거표 완성도 (독립 출처 ≥2?)
    - Should/Will 분리 여부
    - 검증 로그 체크리스트 통과율
    
    Returns:
        신뢰도: Low/Medium/High
    """
```

**파일**:
- `umis_rag/guardian/meta_rag.py` (확장)
- `umis_rag/guardian/quality_scorer.py` (신규)

**난이도**: ⭐⭐⭐ (중간)  
**시간**: 6-8시간 (3일)

---

#### C3. Cursor @ 명령어 공식 지원 (2일) ⭐⭐

**목표**: .cursorrules 업데이트

**추가 섹션**:
```yaml
# ========================================
# PART 8: Guestimation Commands
# ========================================

guestimation_commands:
  
  "@auto [질문]":
    description: "Guardian 자동 판단 → 최적 방법론"
    example: "@auto 국내 OTT 시장 규모"
  
  "@guestimate [질문]":
    description: "빠른 추정 (5-30분, ±50%)"
    example: "@guestimate 음악 스트리밍 시장"
  
  "@reasoner [질문]":
    description: "정밀 분석 (1-4시간, ±30%)"
    example: "@reasoner 시니어 케어 로봇 시장"
  
  "@Explorer guestimate [질문]":
    description: "Agent + 방법론 조합"
  
  "@Quantifier reasoner [질문]":
    description: "정밀 SAM 계산"
```

**파일**:
- `.cursorrules` (cursor_global_rules.txt 또는 별도)

**난이도**: ⭐⭐ (문서화)  
**시간**: 4-6시간 (2일)

---

### 📌 Phase D: 고도화 (3-4주)

#### D1. 실제 프로젝트 테스트 (1주) ⭐⭐⭐⭐⭐

**목표**: 3개 실제 시장 분석 수행

**테스트 프로젝트**:

1. **성숙 시장**: 국내 이커머스 시장 규모
   - 방법론: Guestimation (예상)
   - 목표: Phase 1만으로 충분 확인

2. **신규 시장**: K-로봇 수술 시스템 시장
   - 방법론: Hybrid (Phase 1→2)
   - 목표: Case Analogies (s9) 검증

3. **규제 산업**: 디지털 헬스케어 원격 진료
   - 방법론: Domain Reasoner (필수)
   - 목표: s3 Laws 검증

**출력**:
- `projects/hybrid_test/`
  - `ecommerce_analysis.md`
  - `robot_surgery_analysis.md`
  - `telehealth_analysis.md`

**난이도**: ⭐⭐⭐⭐⭐ (실전)  
**시간**: 15-25시간 (1주, 프로젝트당 5-8시간)

---

#### D2. 성능 벤치마크 (2일) ⭐⭐⭐

**목표**: 속도/정확도 측정 및 개선

**측정 항목**:
- Guestimation 평균 속도: 목표 < 30분
- Domain Reasoner 평균 속도: 목표 < 3시간
- Guardian 전환 정확도: 목표 > 85%
- Should/Will Gap 타당성: 전문가 리뷰

**파일**:
- `scripts/benchmark_hybrid.py` (신규)
- `docs/PERFORMANCE_REPORT.md` (결과)

**난이도**: ⭐⭐⭐ (측정 + 분석)  
**시간**: 6-8시간 (2일)

---

#### D3. 사용자 피드백 수집 (1주) ⭐⭐⭐⭐

**목표**: 실제 사용자 테스트 및 개선

**활동**:
1. 내부 테스트 (3명, 각 3개 프로젝트)
2. 피드백 수집 (설문 + 인터뷰)
3. 개선 사항 도출
4. 우선순위 정리

**예상 피드백**:
- "Domain Reasoner 너무 느려요" → 최적화
- "KPI 정의 더 필요해요" → 확장
- "@ 명령어 직관적이에요" → 유지

**난이도**: ⭐⭐⭐⭐ (조직)  
**시간**: 20-30시간 (1주, 대부분 사용자 시간)

---

### 📌 Phase E: 배포 (1주)

#### E1. v7.2.0 릴리스 준비 (3일) ⭐⭐⭐

**체크리스트**:
- [ ] 모든 테스트 통과 (25개 + 추가)
- [ ] 문서 최종 검토
- [ ] CHANGELOG.md 작성
- [ ] RELEASE_NOTES_v7.2.0.md 작성
- [ ] 버전 번호 업데이트
  - `VERSION.txt`: 7.2.0
  - `umis.yaml`: v7.2.0
  - `config/tool_registry.yaml`: v7.2.0

**난이도**: ⭐⭐ (문서 작업)  
**시간**: 6-8시간 (3일)

---

#### E2. Main 브랜치 병합 (1일) ⭐⭐

**절차**:
1. Alpha 브랜치 최종 검증
2. Main 브랜치와 Conflict 확인
3. 병합 (Merge alpha → main)
4. Tag 생성 (v7.2.0)
5. Release Notes 게시

**난이도**: ⭐⭐ (Git 작업)  
**시간**: 2-4시간 (1일)

---

## 🗓️ 타임라인

### 즉시 시작 가능 (Phase A)

**Week 1**: Domain Reasoner 엔진 완성
- Day 1-2: s2 (RAG Consensus) ⭐⭐⭐
- Day 3: s10 (KPI Library 연동) ⭐
- Day 4-5: s9 (Case Analogies) ⭐⭐⭐⭐
- Day 6-7: s3 (Laws) ⭐⭐⭐⭐

**Week 2**: Quantifier 통합 + 증거표
- Day 1-3: Quantifier hybrid 모드
- Day 4-5: 증거표 자동 생성

### 확장 (Phase B)

**Week 3-4**: KPI 확장 + 검증 로그
- KPI 라이브러리 10→100개
- Verification Log 자동화

### 고도화 (Phase C-D)

**Week 5-7**: 최적화 + 실전 테스트
- 성능 최적화
- 실제 프로젝트 3개
- 사용자 피드백

### 배포 (Phase E)

**Week 8**: 릴리스
- 문서 정리
- Main 병합
- v7.2.0 Release

**총 예상 기간**: 8주 (2개월)

---

## 📋 현실적 단계별 계획

### 🎯 Milestone 1: 동작하는 엔진 (2주)

**목표**: Domain Reasoner 엔드투엔드 작동

**완료 조건**:
- [ ] 10개 신호 모두 구현
- [ ] Quantifier 통합
- [ ] 증거표 생성
- [ ] 1개 실제 프로젝트 완수

**우선순위**: ⭐⭐⭐⭐⭐ (가장 중요!)

---

### 🎯 Milestone 2: 실용화 (1개월)

**목표**: 실제 사용 가능한 수준

**완료 조건**:
- [ ] KPI 50개 이상
- [ ] 3개 실제 프로젝트 완수
- [ ] 성능 < 3시간 (Domain Reasoner)
- [ ] Guardian 전환 정확도 > 80%

**우선순위**: ⭐⭐⭐⭐

---

### 🎯 Milestone 3: 안정화 (2개월)

**목표**: v7.2.0 공식 릴리스

**완료 조건**:
- [ ] KPI 100개
- [ ] 사용자 피드백 반영
- [ ] 문서화 완료
- [ ] Main 브랜치 병합

**우선순위**: ⭐⭐⭐

---

## 🚀 즉시 시작할 작업 (우선순위 Top 3)

### 1. s2_rag_consensus 구현 (최우선!) ⭐⭐⭐⭐⭐

**이유**: 
- 가장 중요한 신호 (weight 0.9)
- UMIS RAG 활용 핵심
- 독립 출처 합의 범위

**예상 시간**: 4-6시간

**파일**: `umis_rag/methodologies/domain_reasoner.py`

**구현 내용**:
```python
class Signal2_RAGConsensus(BaseSignal):
    def process(self, definition, context):
        # 1. UMIS RAG 검색 (explorer, quantifier, validator)
        # 2. 독립성 확인 (≥2 출처)
        # 3. 합의 범위 추출 (IQR, trimmed mean)
        # 4. SRC_xxx ID 부여
```

---

### 2. s10_industry_kpi 연동 (쉬움!) ⭐⭐⭐⭐⭐

**이유**:
- 이미 Rachel에 구현됨
- 연동만 하면 됨
- KPI 표준화 핵심

**예상 시간**: 1시간

**작업**:
```python
# Domain Reasoner에서 Rachel 호출
from umis_rag.agents.validator import ValidatorRAG

rachel = ValidatorRAG()
kpi_result = rachel.validate_kpi_definition(metric_name, definition)
```

---

### 3. Quantifier 통합 (실전 필요!) ⭐⭐⭐⭐⭐

**이유**:
- Bill이 실제로 사용해야 의미 있음
- SAM 계산과 결합
- 하이브리드 전략 완성

**예상 시간**: 8-12시간 (3일)

**작업**:
- `calculate_sam_with_hybrid()` 구현
- Phase 1/2 결과 통합
- Excel 자동 연동

---

## 📝 작업 선택 가이드

### 🔥 지금 당장 (Hot)

**목표**: 동작하는 시스템

1. **s2 + s10 구현** (5-7시간)
   - 가장 중요한 2개 신호
   - RAG + KPI 검증
   
2. **Quantifier 통합** (8-12시간)
   - 실제 사용 가능
   - SAM 계산 연동

**예상**: 2-3일 작업 → **동작하는 Hybrid 시스템 완성!**

---

### 🌡️ 다음 단계 (Warm)

**목표**: 완성도 향상

1. **나머지 신호 구현** (s1, s3, s5-s9)
2. **증거표 자동 생성**
3. **검증 로그 자동화**

**예상**: 1-2주 → **완전한 Domain Reasoner 엔진**

---

### ❄️ 장기 과제 (Cool)

**목표**: 최적화 및 확장

1. KPI 100개 확장
2. 성능 최적화
3. 실전 프로젝트 3개
4. 사용자 피드백

**예상**: 1-2개월 → **v7.2.0 공식 릴리스**

---

## 🎯 권장 순서

### 시나리오 A: 빠른 완성 (2주)

**"일단 동작하게 만들기"**

```
Week 1:
  Day 1-2: s2 (RAG Consensus) 구현 ⭐⭐⭐
  Day 3: s10 (KPI 연동) ⭐
  Day 4-5: Quantifier 통합 ⭐⭐⭐

Week 2:
  Day 1-2: s1, s5-s8 구현 (쉬운 것들) ⭐⭐
  Day 3-4: 증거표 + 검증 로그 ⭐⭐
  Day 5: 통합 테스트 ⭐

결과: 동작하는 Hybrid 시스템 (80% 완성)
```

---

### 시나리오 B: 완벽한 완성 (1개월)

**"제대로 만들기"**

```
Week 1-2: 엔진 완성 (A1-A3)
Week 3: 확장 (B1-B2)
Week 4: 실전 테스트 (D1)

결과: 실전 투입 가능 (95% 완성)
```

---

### 시나리오 C: 점진적 확장 (2개월)

**"안정적으로 성장"**

```
Week 1-2: MVP 완성 (s2, s10, Quantifier)
Week 3-4: 실전 테스트 1개 (피드백)
Week 5-6: 개선 + 나머지 신호
Week 7-8: KPI 확장 + 최적화

결과: v7.2.0 공식 릴리스 (100%)
```

---

## 💡 추천

**즉시 시작**: **시나리오 A** (2주)

**이유**:
1. ✅ 빠르게 동작하는 시스템
2. ✅ 핵심 기능 (s2, s10, Quantifier)
3. ✅ 실전 테스트 가능
4. ✅ 피드백 조기 확보

**첫 작업**:
```
1. s2_rag_consensus 구현 (4-6시간) ← 지금!
2. s10 연동 (1시간)
3. Quantifier 통합 (8-12시간)
```

**3일 안에** → 동작하는 Hybrid 시스템! 🚀

---

## 📁 작업 파일 체크리스트

### 즉시 착수 (s2 구현)

**파일**: `umis_rag/methodologies/domain_reasoner.py`

**작업**:
```python
class Signal2_RAGConsensus(BaseSignal):
    def __init__(self, weight=0.9):
        super().__init__(weight)
        # UMIS RAG 로드
        from umis_rag.agents.explorer import ExplorerRAG
        from umis_rag.agents.quantifier import get_quantifier_rag
        
        self.explorer_rag = ExplorerRAG()
        self.quantifier_rag = get_quantifier_rag()
    
    def process(self, definition, context):
        # 1. Vector 검색
        # 2. 독립성 확인
        # 3. 합의 범위 (IQR)
        # 4. SRC_ID 생성
        pass
```

**테스트**: `scripts/test_signal2_rag.py`

---

**작성**: 2025-11-05  
**현재 진행률**: Step 1-5 완료 (MVP)  
**다음**: Domain Reasoner 엔진 완성 (Phase A)

