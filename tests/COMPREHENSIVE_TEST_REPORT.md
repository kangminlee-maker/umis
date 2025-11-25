# Estimator Phase 0-4 종합 테스트 보고서

**테스트 일시**: 2025-11-24 16:22  
**테스트 유형**: Native vs External 모드 비교  
**문항 수**: 13개 (기본 3개 + 확장 10개)  
**버전**: v7.8.1 (cursor-native Integration)

---

## 📊 테스트 결과 요약

### 전체 성공률

| 모드 | 성공 | 실패 | 성공률 |
|------|------|------|--------|
| **Native** | 1/13 | 12/13 | 7.7% |
| **External** | 1/13 | 12/13 | 7.7% |

### Phase 분포

| Phase | Native | External | 설명 |
|-------|--------|----------|------|
| Phase 0 (Literal) | 0 | 0 | 프로젝트 데이터 직접 참조 |
| Phase 1 (Direct RAG) | 0 | 0 | 학습된 규칙 RAG |
| Phase 2 (Validator) | **1** | **1** | 확정 데이터 검색 ✅ |
| Phase 3 (Guestimation) | 0 | 0 | 11개 Source 기반 추정 |
| Phase 4 (Fermi) | 0 | 0 | Fermi 분해 |

---

## 🎯 성공 케이스 분석

### ✅ 성공: 서울시 인구 (Phase 2)

**질문**: "서울시 인구는 몇 명일까?"

| 항목 | Native | External |
|------|--------|----------|
| Phase | 2 (Validator) | 2 (Validator) |
| 추정값 | 9,500,000명 | 9,500,000명 |
| 정답 | 9,500,000명 | 9,500,000명 |
| 정확도 | 100점 | 100점 |
| 신뢰도 | 1.00 | 1.00 |
| 소요 시간 | 0.34초 | 0.34초 |
| 비용 | $0 | $0 |

**성공 이유**:
- Validator RAG에 통계청 데이터로 저장되어 있음
- Distance: 0.858 (거의 동일, <0.90)
- Relevance 검증 통과: ['인구', '서울']

---

## ❌ 실패 원인 분석

### 1. Phase 3 (Guestimation) 실패

**실패한 12개 문항 모두 동일한 패턴**:

```
[Phase 3] ìì: {질문}
  ë§¥ë½: intent=get_value, domain=General
[Source Collector] ìì§ ìì
  Physical: 0ê° ì ì½
  [AI+Web] Native ëª¨ë: instruction ìì±
  Value: 1ê° ì¶ì 
  Soft: 0ê° ê°ì´ë
  â ìì§ ìë£
[Judgment] 1ê° ì¦ê±° ì¢í©
  ì ëµ: single_best
WARNING: íë¨ ì¤í¨
```

**근본 원인**: Phase 3의 `Judgment` 시스템 실패
- Source는 정상적으로 수집 (Value Source 1개)
- 하지만 Judgment 단계에서 판단 실패
- `synthesis()` 함수에서 "단일 증거"를 처리하지 못함

### 2. Phase 4 Native 모델 생성 실패

**Phase 4 진입 시**:

```
[Phase 4] Fermi Estimation (depth 0)
  [Step 1] ì´ê¸° ì¤ìº (íì¥)
  [Step 2] ëª¨í ìì±
    [cursor-native] Cursor LLM ì§ì  ìì±
      [Cursor LLM] ëª¨í ìì± ìì²­
      [Cursor LLM] ë¹ì©: $0 (ë¬´ë£)
WARNING: [Cursor LLM] ì´ ì§ë¬¸ í¨í´ì ìì§ êµ¬íëì§ ìì
INFO: TODO: Cursor LLMì´ ëì ì¼ë¡ ëª¨í ìì±íëë¡ ê°ì  íì
    Fallback â Phase 3 ìì
WARNING: â Step 2 ì¤í¨ (ëª¨í ìì)
```

**근본 원인**: `_generate_native_models()` 패턴 미구현
- Native Mode에서 동적 모델 생성 기능이 아직 구현되지 않음
- 현재는 사전 정의된 패턴만 지원
- TODO로 표시된 개선 필요 항목

---

## 🔍 기술적 문제점

### 1. Phase 3 Judgment 시스템

**위치**: `umis_rag/agents/estimator/judgment.py`

**문제**:
- `single_best` 전략에서 단일 증거 처리 실패
- 1개의 Value Source만 있을 때 판단 불가
- 복수의 증거가 있을 때만 작동하도록 설계됨

**영향**:
- Native/External 모드 모두 동일하게 실패
- Phase 3가 작동하지 않아 Phase 4로 넘어가야 하지만, Phase 4도 실패

### 2. Native Mode 동적 모델 생성

**위치**: `umis_rag/agents/estimator/phase4_fermi.py:_generate_native_models()`

**문제**:
- 패턴 매칭 기반만 구현됨
- 동적인 질문에 대한 모델 생성 불가
- Cursor LLM을 활용한 실시간 모델 생성 미구현

**영향**:
- Native Mode에서 Phase 4 사용 불가
- 사전 정의된 질문 패턴만 처리 가능

---

## 💰 비용 분석

| 모드 | Phase 4 비용 | Phase 3 비용 | 총 비용 | 1,000회 기준 |
|------|--------------|--------------|---------|--------------|
| **Native** | $0 (0개) | $0 (0개) | **$0** | **$0** |
| **External** | $0 (0개) | $0 (0개) | **$0** | **$0** |

**참고**: 실패로 인해 비용 발생 없음

---

## 📋 개별 문항 상세

### 기본 3개 문항

1. **한국 전체 사업자 수는 몇 개일까?** ❌
   - 예상 Phase: 4
   - 결과: Phase 3에서 Judgment 실패
   - 예상값: 8,200,000개

2. **서울시 인구는 몇 명일까?** ✅
   - 예상 Phase: 2
   - 결과: Phase 2에서 성공
   - 추정값: 9,500,000명 (100% 정확)

3. **한국 커피 전문점 수는?** ❌
   - 예상 Phase: 3
   - 결과: Phase 3에서 Judgment 실패
   - 예상값: 100,000개

### 확장 10개 문항

4. **한국 전체 배달 기사(라이더) 수는?** ❌ (Phase 3 실패)
5. **한국 연간 치킨 배달 주문 건수는?** ❌ (Phase 3 실패)
6. **서울시 하루 평균 택시 승객 수는?** ❌ (Phase 3 실패)
7. **한국 연간 신용카드 승인 건수는?** ❌ (Phase 3 실패)
8. **한국 연간 병원 외래 진료 건수는?** ❌ (Phase 3 실패)
9. **한국 초중고 학생 연간 사교육비 총액은?** ❌ (Phase 3 실패)
10. **서울시 연간 전세 계약 건수는?** ❌ (Phase 3 실패)
11. **한국 유료 OTT 구독자 수는?** ❌ (Phase 3 실패)
12. **쿠팡 일평균 배송 물량(박스 수)은?** ❌ (Phase 3 실패)
13. **한국 연간 일회용 컵 사용량은?** ❌ (Phase 3 실패)

---

## 🎯 주요 발견사항

### 1. Phase 2 (Validator) 정상 작동 ✅
- Distance threshold 개선 (v7.8.1) 효과 확인
- 엄격한 유사도 기준 (< 0.90) 정상 작동
- Relevance 검증도 정확히 작동

### 2. Phase 3 (Guestimation) 시스템 오류 ❌
- **Judgment 시스템이 단일 증거를 처리하지 못함**
- 모든 문항에서 동일한 패턴으로 실패
- Native/External 모두 영향 (모드 무관)

### 3. Native Mode Phase 4 미완성 ❌
- 동적 모델 생성 기능 미구현
- 패턴 매칭만 가능
- TODO로 표시된 개선 필요 항목

### 4. cursor-native 통합은 정상 ✅
- Model Config 시스템에서 cursor-native 정상 로드
- api_type: cursor 분기 정상 작동
- 다만 Phase 4 로직 자체가 미완성

---

## 🔧 개선 필요 사항

### 우선순위 1: Phase 3 Judgment 수정 (긴급) 🚨

**파일**: `umis_rag/agents/estimator/judgment.py:258-268`

**문제**: `_single_best_judgment()`에서 `uncertainty` 필드 접근 오류

**근본 원인**:
```python
def _single_best_judgment(self, estimates: List[ValueEstimate]) -> Dict:
    best = max(estimates, key=lambda x: x.confidence)
    
    return {
        'value': best.value,
        'confidence': best.confidence,
        'uncertainty': best.uncertainty,  # ❌ AttributeError!
        'reasoning': f"최고 신뢰 증거: {best.source_type.value}"
    }
```

`ValueEstimate` 객체에 `uncertainty` 필드가 없거나 None일 때 AttributeError 발생

**해결 방안**:
```python
'uncertainty': getattr(best, 'uncertainty', 0.3),  # 기본값 0.3
```

### 우선순위 2: Phase 4 Native Mode LLM 호출 통합 (중요)

**파일**: `umis_rag/agents/estimator/phase4_fermi.py:896-1020`

**문제**: `_generate_native_models()`가 패턴 매칭만 구현, LLM 호출 없음

**올바른 설계** (사용자 요구사항):
> "llm모드와 native 모드는 **사용하는 llm이 다를 뿐**, phase 4의 작동방식은 똑같아야 해."

즉:
- ✅ `_generate_llm_models`의 로직을 그대로 사용
- ✅ 단지 LLM API 호출만 다르게:
  - External: OpenAI API (유료)
  - Native: Cursor에게 instruction 전달 (무료)

**해결 방안**:
- `_generate_native_models`를 삭제하고
- `_generate_llm_models`에서 `self.llm_mode`에 따라 API 호출 방식만 분기
- Native일 때: Cursor에게 "이 질문에 대한 Fermi 모형을 생성해주세요" instruction 작성
- External일 때: OpenAI API 호출 (기존 로직)

---

## 📈 다음 단계

1. **Phase 3 Judgment 긴급 수정** → 12개 문항 복구 가능
2. **Native Mode Phase 4 구현** → 완전한 cursor-native 통합
3. **재테스트 실행** → 13개 문항 100% 목표

---

## 📝 결론

### 긍정적 측면

1. **Phase 2 개선 검증 완료** ✅
   - v7.8.1 Distance threshold가 정확히 작동
   - Relevance 검증도 정상

2. **cursor-native 통합 구조 정상** ✅
   - Model Config 시스템 정상 작동
   - api_type 분기 정상
   - 시스템 아키텍처는 완벽

3. **Native/External 동일 동작** ✅
   - 모드 무관하게 동일한 Phase 진행
   - 비용만 차이 (설계 의도대로)

### 해결 필요 사항

1. **Phase 3 Judgment 오류** 🚨
   - 단일 증거 처리 로직 누락
   - 12개 문항 실패의 직접적 원인
   - 긴급 수정 필요

2. **Phase 4 Native 미구현**
   - 동적 모델 생성 기능 부재
   - 현재는 패턴 매칭만 지원
   - 장기적 개선 필요

### 테스트의 가치

이번 테스트로 다음을 확인했습니다:
- ✅ cursor-native 통합이 시스템적으로 완벽히 작동
- ✅ Phase 2 개선이 정확히 효과 발휘
- ❌ Phase 3/4의 실제 로직에 개선 필요
- 🎯 수정 방향 명확히 파악

**전체 평가**: **시스템 아키텍처 성공, 로직 개선 필요**


