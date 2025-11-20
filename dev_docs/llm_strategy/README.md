# LLM 전략 및 비용 최적화 문서

UMIS에서 사용하는 LLM 모델 선택, 비용 최적화, 전략 수립 관련 개발 문서입니다.

## 주요 문서

### 전략 및 아키텍처
- `ARCHITECTURE_LLM_STRATEGY.md`: UMIS LLM 전략 개요
  - Native LLM (Cursor) vs External LLM API
  - 3가지 아키텍처 옵션 분석
  - 하이브리드 모드 구현 가이드

### 모델 비교 및 선택
- `COMPLETE_LLM_MODEL_COMPARISON.md`: 완전한 LLM 모델 비교
  - GPT vs Claude 전체 라인업
  - UMIS 작업별 최적 모델 매칭
  - 4-Tier Hybrid 전략 (85% 비용 절감)

- `GPT_MODEL_SELECTION_GUIDE.md`: GPT 모델 선택 가이드
  - GPT-4o, GPT-4o-mini, o1-mini 비교
  - UMIS 작업별 최적 모델
  - 3-Tier 시스템 (83% 절감)

- `SINGLE_PROVIDER_STRATEGY.md`: 단일 Provider 전략
  - OpenAI 전용 vs Claude 전용
  - Provider별 장단점 비교
  - 시나리오별 권장 구성

### 마이그레이션 및 최적화
- `CLAUDE_TO_GPT_MIGRATION_GUIDE.md`: Claude → GPT-4o 마이그레이션
  - Thinking 모델 품질을 일반 LLM으로 재현
  - 4단계 전략 (Level 1~4)
  - CoT 프롬프트, Few-shot, 템플릿 구현

- `NON_THINKING_MODEL_OPTIMIZATION.md`: 비-Thinking 모델 최적화
  - 일반 LLM(GPT-4o, Claude Sonnet) 효과적 사용
  - 의사결정 트리, 룰 기반 시스템
  - 5가지 개선 전략 (87% 비용 절감)

### 가격 및 비용
- `UPDATED_LLM_PRICING_2025.md`: OpenAI 최신 가격 (2025)
  - GPT-4o: 40% 인하! ($5 → $2.50/1M)
  - o1-mini: 63% 인하! ($3 → $1.10/1M)
  - gpt-5-nano 신규 ($0.05/1M, 최저가!)
  - 5-Tier Hybrid (93% 절감)

### 시스템 최적화
- `SYSTEM_RAG_ALTERNATIVES_ANALYSIS.md`: System RAG 대안 분석
  - ChromaDB vs 단순 파일 vs SQLite
  - 컨텍스트 크기별 권장 (1M / 200k / 32k)
  - System RAG 제거 vs 유지 분석

## 핵심 인사이트

### 비용 최적화 전략

```yaml
현재 (Sonnet 4.5 Thinking 100%):
  비용: $15/1,000회
  품질: 98%

최적화 후 (5-Tier Hybrid):
  구성:
    - 70%: gpt-5-nano ($0.00025)
    - 15%: GPT-4o-mini ($0.00045)
    - 8%: GPT-4o ($0.0075)
    - 5%: Sonnet 4.5 (Thinking) ($0.015)
    - 2%: o1-mini ($0.0033)
  
  비용: $1.31/1,000회
  품질: 90-92%
  절감: 91%
```

### 작업별 최적 모델

| 작업 | 최적 모델 | 비용/작업 | 비율 |
|------|----------|----------|------|
| Phase 0-2 | gpt-5-nano | $0.00025 | 70% |
| Phase 3 (템플릿 O) | GPT-4o-mini | $0.00045 | 15% |
| Phase 3 (템플릿 X) | GPT-4o | $0.0075 | 8% |
| Phase 4 (복잡) | Sonnet (Think) | $0.015 | 5% |
| Phase 4 (중간) | o1-mini | $0.0033 | 2% |

### 최신 가격 변동 (2025)

```yaml
주요 변경:
  - GPT-4o: -40% ($5 → $2.50/1M)
  - o1-mini: -63% ($3 → $1.10/1M)
  - gpt-5-nano: 신규 ($0.05/1M, GPT-4o-mini 대비 1.8배 저렴!)
  - gpt-4.1-nano: 신규 ($0.10/1M)

영향:
  - Phase 3-4 비용 대폭 감소
  - OpenAI가 Claude 대비 압도적 가성비
  - 추가 절감 가능성 확대
```

## 실행 가이드

### 즉시 실행 (검증된 모델)

```yaml
Week 1: OpenAI 전용 구성
  - 85%: GPT-4o-mini
  - 8%: GPT-4o (40% 인하!)
  - 7%: o1-mini (63% 인하!)
  
  비용: $1.21/1,000회
  절감: 92%
  품질: 90%
  
  구현: 2-3일
```

### 1개월 후 (nano 검증 완료 시)

```yaml
5-Tier Hybrid 구성
  - 70%: gpt-5-nano (검증 필요)
  - 나머지 동일
  
  비용: $1.07-1.31/1,000회
  절감: 91-93%
  품질: 88-92%
```

## 주요 전략

### 1. 모델 선택 전략
- **85% 작업**: 초저가 모델 (nano/mini)
- **10% 작업**: 중급 모델 (GPT-4o)
- **5% 작업**: 고급 모델 (Thinking)

### 2. 품질 유지 방법
- Few-shot 예시 강화
- 의사결정 트리 (20-30개 템플릿)
- 룰 기반 시스템 (공식, 단위 변환)
- Multi-pass 전략

### 3. 비용 최적화 기법
- 작업별 모델 선택 (70-83% 절감)
- 템플릿 구축 (+10-15% 절감)
- 캐싱 (+30-40% 절감)
- 총 절감 가능성: 90%+

## 관련 코드

- `umis_rag/core/llm_router.py`: 모델 라우터
- `umis_rag/agents/estimator/gpt4o_adapter.py`: GPT-4o 어댑터
- `umis_rag/core/rules_engine.py`: 룰 기반 엔진
- `umis_rag/agents/estimator/decision_tree.py`: 의사결정 트리

## 참고

이 문서들은 UMIS v7.7.0~v7.8.0 기준으로 작성되었으며, 2025년 최신 OpenAI 가격을 반영하고 있습니다.

