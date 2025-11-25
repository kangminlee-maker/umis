# Estimator 사용자 가이드 (v7.9.0)

**대상**: 비개발자 포함 모든 사용자  
**버전**: v7.9.0  
**최종 업데이트**: 2025-11-25

---

## 📋 목차

1. [Quick Start](#quick-start)
2. [핵심 개념](#핵심-개념)
3. [Phase별 가이드](#phase별-가이드)
4. [LLM Mode 선택](#llm-mode-선택)
5. [성능 최적화](#성능-최적화)
6. [트러블슈팅](#트러블슈팅)
7. [FAQ](#faq)

---

## Quick Start

### 1단계: 설치 (이미 완료됨)

```bash
# UMIS 설치 확인
python setup/setup.py --check
```

### 2단계: 간단한 추정

```python
from umis_rag.agents.estimator import EstimatorRAG

# Estimator 생성
estimator = EstimatorRAG()

# 질문하기
result = estimator.estimate("B2B SaaS의 평균 ARPU는?")

# 결과 확인
if result.is_successful():
    print(f"추정값: {result.value}")
    print(f"신뢰도: {result.confidence:.0%}")
    print(f"사용된 Phase: {result.phase}")
else:
    print(f"실패: {result.error}")
```

**출력 예시**:
```
추정값: 50000.0
신뢰도: 80%
사용된 Phase: 3
```

---

## 핵심 개념

### 5-Phase Architecture

Estimator는 5단계로 값을 추정합니다:

| Phase | 이름 | 설명 | 속도 | 정확도 |
|-------|------|------|------|--------|
| **0** | Literal | 프로젝트 데이터 확인 | ⚡ 즉시 | ⭐⭐⭐⭐⭐ 100% |
| **1** | Direct RAG | 학습된 규칙 검색 | ⚡ <0.5s | ⭐⭐⭐⭐ 90% |
| **2** | Validator | 확정 데이터 검색 | ⚡ <1s | ⭐⭐⭐⭐⭐ 100% |
| **3** | Guestimation | LLM + 웹 검색 | 🕐 ~3s | ⭐⭐⭐ 70-80% |
| **4** | Fermi Decomposition | 재귀 분해 추정 | 🕐🕐 ~10s | ⭐⭐⭐ 60-70% |

**자동 진행**:
- Phase 0부터 순서대로 시도
- 실패하면 다음 Phase로 자동 진행
- 성공하면 즉시 반환

**예시**:
```
질문: "우리 회사 직원 수는?"
project_data = {'employees': 150}

Phase 0 시도 → 성공! (0.01초, 100% 신뢰도)
```

```
질문: "B2B SaaS ARPU는?"

Phase 0 시도 → 실패 (프로젝트 데이터 없음)
Phase 1 시도 → 실패 (학습 규칙 없음)
Phase 2 시도 → 실패 (확정 데이터 없음)
Phase 3 시도 → 성공! (2.5초, 80% 신뢰도)
```

### EstimationResult (결과 객체)

모든 추정은 `EstimationResult` 객체를 반환합니다 (v7.9.0: 항상 반환, None 불가).

**주요 필드**:
```python
result.value           # 추정값 (예: 50000.0)
result.unit            # 단위 (예: "원")
result.phase           # 사용된 Phase (0-4, 또는 -1: 실패)
result.confidence      # 신뢰도 (0.0-1.0)
result.error           # 실패 시 에러 메시지
result.is_successful() # 성공 여부 (True/False)
```

---

## Phase별 가이드

### Phase 0: Literal (프로젝트 데이터)

**언제 사용**:
- 프로젝트에서 이미 알고 있는 값
- 100% 정확한 데이터

**사용법**:
```python
result = estimator.estimate(
    question="churn_rate",  # 또는 "이탈률은?"
    project_data={'churn_rate': 0.05}
)
```

**키워드 매칭**:
```python
# Estimator는 자동으로 키워드를 매칭합니다
키워드 → project_data 키
"churn", "이탈", "해지" → churn_rate
"arpu", "평균매출" → arpu
"ltv" → ltv
"cac" → cac
```

**팁**:
- 질문에 project_data의 키 또는 키워드가 포함되어야 함
- 정확한 키를 사용하면 더 빠름 (예: "churn_rate")

---

### Phase 1: Direct RAG (학습 규칙)

**언제 사용**:
- 이전에 같은 질문을 한 적이 있음
- 시스템이 학습한 규칙이 있음

**특징**:
- 자동으로 학습 (학습 규칙이 쌓임)
- 초기에는 비어 있음 (0개)
- 사용할수록 빨라짐

**예시**:
```python
# 첫 번째 질문 (Phase 3 사용, 3초)
result1 = estimator.estimate("B2B SaaS ARPU?")
# → Phase 3 (3초)

# 같은 질문 반복 (Phase 1 사용, 0.5초)
result2 = estimator.estimate("B2B SaaS ARPU?")
# → Phase 1 (0.5초) ⚡
```

---

### Phase 2: Validator (확정 데이터)

**언제 사용**:
- 공개된 확정 데이터가 있음 (예: 통계청, 벤치마크)
- "거의 완벽한 매칭"만 사용 (v7.9.0: 임계값 강화)

**데이터 소스** (24개):
- 통계청, 한국은행, DART
- SaaS Capital, OpenView, ProfitWell
- 등...

**사용법**:
```python
from umis_rag.agents.estimator.models import Context

result = estimator.estimate(
    question="B2B SaaS의 평균 churn rate는?",
    context=Context(domain='B2B_SaaS', region='미국')
)
```

**v7.9.0 변경사항**:
- **임계값 강화**: 유사도 <0.85만 매칭 (이전: <1.10)
- **효과**: "거의 완벽한 매칭"만 Phase 2 사용
- **장점**: 잘못된 매칭 방지 (예: "B2B SaaS ARPU" ≠ "한국 B2B SaaS")

---

### Phase 3: Guestimation (LLM + 웹)

**언제 사용**:
- Phase 0-2 모두 실패
- LLM 지식 + 웹 검색 필요

**특징**:
- 평균 2-3초
- 신뢰도 70-80%
- 구글 검색 통합 (선택적)

**사용법**:
```python
result = estimator.estimate(
    question="2025년 AI 챗봇 서비스 평균 ARPU는?",
    context=Context(
        domain='AI_Chatbot',
        region='한국',
        time_period='2025'
    )
)
```

**Context 활용**:
```python
Context(
    domain='B2B_SaaS',      # 도메인 (예: B2B_SaaS, E-commerce)
    region='한국',           # 지역 (예: 한국, 서울, 글로벌)
    time_period='2025'      # 시간 (예: 2025, 2023Q4)
)
```

**팁**:
- Context를 자세히 제공할수록 정확도 ↑
- domain, region, time_period 모두 사용 권장

---

### Phase 4: Fermi Decomposition (재귀 분해)

**언제 사용**:
- Phase 3도 실패하거나 신뢰도 낮음
- 복잡한 추정 (예: "서울 음식점 수는?")

**특징**:
- 문제를 작은 단위로 분해
- 재귀적으로 추정
- 평균 5-10초 (복잡하면 20-30초)

**예시**:
```
질문: "서울 음식점 수는?"

LLM이 모형 생성:
음식점 수 = 서울 인구 × 1인당 외식 횟수/월 × 음식점당 평균 고객 수

재귀 추정:
- 서울 인구 → Phase 2 (확정 데이터: 1000만명)
- 1인당 외식 횟수 → Phase 3 (Guestimation: 4회/월)
- 음식점당 고객 → Phase 3 (Guestimation: 100명)

최종 계산:
1000만 × 4 × 100 = 4000만 / 100 = 40만 개
```

**사용법**:
```python
result = estimator.estimate(
    question="서울 음식점 수는?",
    context=Context(region='서울')
)

if result.phase == 4:
    print(f"Fermi 모형: {result.fermi_model}")
    print(f"하위 변수: {result.variable_results}")
```

---

## LLM Mode 선택

### 3가지 Mode

| Mode | 설명 | 속도 | 비용 | 사용 시기 |
|------|------|------|------|-----------|
| **cursor** | Cursor AI (대화형) | 빠름 | 무료 | 개발 중, 대화 |
| **gpt-4o-mini** | OpenAI GPT-4o Mini | 빠름 | 저렴 | 프로덕션 (권장) |
| **gpt-4o** | OpenAI GPT-4o | 느림 | 비쌈 | 정확도 최우선 |

### Mode 설정

**방법 1: 환경 변수** (권장)
```.env
# .env 파일
LLM_MODE=gpt-4o-mini
```

**방법 2: 코드에서 변경**
```python
from umis_rag.core.config import settings

settings.llm_mode = 'gpt-4o-mini'
```

### Cursor Auto Fallback (v7.9.0)

**자동 전환**:
- Cursor 모드에서 Phase 3-4 필요 시
- 자동으로 `gpt-4o-mini`로 전환
- 작업 완료 후 원래 모드 복원

**예시**:
```python
settings.llm_mode = 'cursor'

# Phase 3 필요한 질문
result = estimator.estimate("AI 챗봇 ARPU?")
# → 자동으로 gpt-4o-mini 사용
# → Phase 3 성공
# → cursor 모드 복원
```

**로그**:
```
[INFO] 🔄 Cursor 모드 → API 모드 자동 Fallback
[INFO] Phase 3-4는 LLM API 필요 → gpt-4o-mini 사용
[INFO] 🧠 Phase 3 완료: 50000.0
[DEBUG] Cursor 모드 복원: cursor
```

---

## 성능 최적화

### 1. Phase 0 최대한 활용

**권장**:
```python
# 프로젝트 데이터를 최대한 제공
project_data = {
    'churn_rate': 0.05,
    'arpu': 50000,
    'ltv': 1000000,
    'cac': 200000,
    'total_users': 10000
}

result = estimator.estimate("churn_rate", project_data=project_data)
# → Phase 0 (0.01초) ⚡
```

### 2. Context 명확히 제공

**권장**:
```python
# Context를 자세히
context = Context(
    domain='B2B_SaaS',
    region='한국',
    time_period='2025'
)
```

**비권장**:
```python
# Context 없음 (느림)
context = None
```

### 3. 반복 질문 활용 (Phase 1)

**첫 질문**: Phase 3 (3초)  
**같은 질문 반복**: Phase 1 (0.5초) ⚡

### 4. 배치 추정

```python
questions = [
    "churn_rate",
    "arpu",
    "ltv"
]

for q in questions:
    result = estimator.estimate(q, project_data=project_data)
    print(f"{q}: {result.value}")
```

---

## 트러블슈팅

### 문제 1: "모든 Phase에서 실패"

**증상**:
```python
result = estimator.estimate("알 수 없는 질문?")
# phase=-1, error="모든 Phase(0-4)에서 추정 실패"
```

**원인**:
- 질문이 너무 모호
- Context 부족
- project_data 없음

**해결**:
1. 질문을 구체적으로
2. Context 추가
3. project_data 제공

```python
# Before
result = estimator.estimate("값은?")

# After
result = estimator.estimate(
    question="B2B SaaS의 평균 ARPU는?",
    context=Context(domain='B2B_SaaS', region='한국')
)
```

### 문제 2: Phase 3/4 느림 (>10초)

**원인**:
- LLM API 호출 비용
- 네트워크 지연

**해결**:
1. project_data 최대한 활용 (Phase 0)
2. 반복 질문 활용 (Phase 1)
3. LLM Mode를 `gpt-4o-mini`로 (빠름)

### 문제 3: 신뢰도 낮음 (<50%)

**원인**:
- 질문이 모호
- Context 부족
- 데이터 부족

**해결**:
1. 질문을 구체적으로
2. Context 추가 (domain, region, time_period)
3. project_data 제공

### 문제 4: "Connection error" (API 호출 실패)

**원인**:
- OpenAI API 키 없음
- 네트워크 연결 문제

**해결**:
1. .env 파일 확인
   ```env
   OPENAI_API_KEY=your-key-here
   ```
2. API 키 발급: https://platform.openai.com/api-keys
3. 네트워크 연결 확인

---

## FAQ

### Q1: Phase 0-2를 건너뛰고 바로 Phase 3 사용 가능?

**A**: 예, `force_phase` 파라미터 사용 (테스트용)
```python
result = estimator.estimate("질문?", force_phase=3)
```

### Q2: 여러 질문을 한 번에 추정 가능?

**A**: 예, 반복문 사용
```python
questions = ["질문1", "질문2", "질문3"]
results = [estimator.estimate(q) for q in questions]
```

### Q3: Phase별 성공률은?

**A**:
- Phase 0: 100% (프로젝트 데이터 있으면)
- Phase 1: 90% (학습 규칙 있으면)
- Phase 2: 100% (확정 데이터 있으면)
- Phase 3: 70-80% (일반적)
- Phase 4: 60-70% (복잡한 문제)

### Q4: Cursor 모드와 API 모드 차이는?

**A**:
| 특징 | Cursor | API (gpt-4o-mini) |
|------|--------|-------------------|
| 속도 | 빠름 | 빠름 |
| 비용 | 무료 | 저렴 ($0.15/1M tokens) |
| 사용 | 개발 중 | 프로덕션 |
| Phase 3-4 | 자동 Fallback ✅ | 직접 사용 ✅ |

### Q5: v7.9.0 주요 변경사항은?

**A**:
1. ✅ None 반환 제거 (항상 EstimationResult)
2. ✅ Cursor Auto Fallback
3. ✅ Phase 2 임계값 강화 (0.95 → 0.85)
4. ✅ LLM Mode 동적 전환
5. ✅ 81개 테스트 (100% 통과)

---

## 참고 자료

- **API 문서**: `docs/api/ESTIMATOR_API_v7_9_0.md`
- **CHANGELOG**: `CHANGELOG.md`
- **아키텍처**: `docs/architecture/UMIS_ARCHITECTURE_BLUEPRINT.md`
- **Production Roadmap**: `dev_docs/improvements/PRODUCTION_QUALITY_ROADMAP_COMPLETE_v7_9_0.md`

---

**작성일**: 2025-11-25  
**버전**: v7.9.0  
**작성자**: AI Assistant  
**대상**: 모든 사용자 (비개발자 포함)

---

**END OF USER GUIDE**



