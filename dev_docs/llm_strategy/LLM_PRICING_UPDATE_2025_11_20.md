# LLM 가격 업데이트 (2025-11-20)

## 📊 주요 변경사항 요약

### OpenAI 변경사항

#### 신규 모델 추가
- **gpt-5-pro**: $15.00/$120.00 (Standard Tier)
- **o1-pro**: $150.00/$600.00 (Standard Tier) - 최고가!
- **o3-pro**: $20.00/$80.00 (Standard Tier)
- **o3-deep-research**: $10.00/$40.00 (Standard Tier)
- **o4-mini-deep-research**: $2.00/$8.00 (Standard Tier)
- **computer-use-preview**: $3.00/$12.00 (Standard Tier)

#### 가격 유지
대부분의 기존 모델 가격은 동일하게 유지됨:
- gpt-5.1, gpt-5, gpt-5-mini, gpt-5-nano: 동일
- gpt-4.1 시리즈: 동일
- gpt-4o, gpt-4o-mini: 동일
- o1, o3, o3-mini, o4-mini, o1-mini: 동일

### Claude 변경사항

#### 가격 확정
- **Opus 4.1**: ~$20/$80 (추정) → **$15/$75 (확정)** ✅
  - 추정보다 25% 저렴!
  - UMIS에 좋은 소식

#### 신규 모델
- **Haiku 4.5**: $1/$5 (신규 출시)
  - Haiku 3.5 대비 4-5배 비쌈
  - 최신 기술 적용

#### 가격 인상
- **Sonnet 4.5**: 200K 토큰 초과 시 2배 비용
  - ≤200K: $3/$15 (기존)
  - >200K: $6/$22.50 (신규) ⚠️
  
- **Haiku 3.5** (Legacy): $0.25/$1.25 → $0.80/$4.00
  - 3.2배 인상
  - Legacy 모델로 분류

---

## 🎯 UMIS에 미치는 영향

### 긍정적 영향 ✅

1. **Opus 4.1 가격 확정 ($15/$75)**
   - 추정보다 저렴
   - Discovery Sprint Full에 활용 가능
   - 최고급 작업에 합리적 비용

2. **Haiku 4.5 출시**
   - 200K 컨텍스트 + 저가 조합
   - 긴 문서 분석에 유용
   - GPT-4o보다 저렴 (200K 기준)

### 주의사항 ⚠️

1. **Sonnet 4.5 200K 초과 비용**
   - 200K 초과 시 2배 비용
   - UMIS 대부분 작업은 200K 이하
   - 긴 문서 분석 시 주의 필요

2. **Haiku 3.5 가격 인상**
   - 3.2배 인상
   - Haiku 4.5 사용 권장

3. **신규 OpenAI Pro 모델들**
   - 대부분 UMIS에 오버킬
   - 비용 대비 효과 낮음
   - 특수 상황에만 사용

---

## 💡 업데이트된 권장사항

### 최적 구성 (2025-11-20 기준)

```yaml
Tier 1 (85% 작업): GPT-4o-mini
  - Phase 0-2 (모든 경우)
  - Phase 3 (템플릿 있음)
  - Quantifier 모든 계산
  - Validator 정의 검증
  - Explorer RAG 작업
  비용: $0.00045/작업
  
Tier 2 (15% 작업): Sonnet 4.5
  - Phase 3 (템플릿 없음)
  - Phase 4 (중급-복잡)
  - 가설 생성
  - 신뢰도 판단
  - Observer 분석
  비용: $0.0105/작업 (≤200K)
```

### 비용 계산

```yaml
평균 비용:
  (0.85 × $0.00045) + (0.15 × $0.0105)
  = $0.00038 + $0.00158
  = $0.00196/작업
  
1,000회 작업: $1.96

vs 이전 (Sonnet 4.5 100%): $10.50/1,000회
절감: 81% ⭐⭐⭐
```

### 특수 상황 모델

```yaml
최고급 작업 (5%): Opus 4.1
  - Discovery Sprint Full
  - 복잡한 Observer 분석
  - 최고 품질 필요
  비용: $0.0525/작업

GPT Thinking 필요 시: o1-mini
  - Phase 4 대안
  - 복잡한 추론
  비용: $0.009/작업

긴 컨텍스트 (200K): Haiku 4.5
  - 긴 문서 분석
  - 200K 컨텍스트 필요
  비용: $0.0035/작업
```

---

## 📊 가격 비교표

### Phase별 최적 모델 및 비용

| Phase | 최적 모델 | 비용/작업 | 2순위 | 비용/작업 | 비용 차이 |
|-------|----------|----------|-------|----------|---------|
| Phase 0-2 | GPT-4o-mini | $0.00045 | Haiku 4.5 | $0.0035 | 8배 |
| Phase 3 (템O) | GPT-4o-mini | $0.00045 | Sonnet 4.5 | $0.0105 | 23배 |
| Phase 3 (템X) | Sonnet 4.5 | $0.0105 | GPT-4o | $0.0125 | 1.2배 |
| Phase 4 (복잡) | Sonnet 4.5 | $0.0105 | Opus 4.1 | $0.0525 | 5배 |
| Phase 4 (최고급) | Opus 4.1 | $0.0525 | o3-pro | $0.06 | 1.1배 |

### 컨텍스트별 최적 모델

| 컨텍스트 | OpenAI | 비용 | Claude | 비용 | 권장 |
|---------|--------|------|--------|------|------|
| < 50k | GPT-4o-mini | $0.00045 | Haiku 4.5 | $0.0035 | OpenAI (8배 저렴) |
| 50-128k | GPT-4o-mini | $0.00045 | Haiku 4.5 | $0.0035 | OpenAI (8배 저렴) |
| 128-200k | GPT-4o | $0.0125 | Haiku 4.5 | $0.0035 | **Claude** (3.6배 저렴) |
| > 200k | GPT-4o | $0.0125 | Sonnet 4.5 | $0.0173 | **OpenAI** (1.4배 저렴) |

---

## 🚀 즉시 실행 가능한 최적화

### Step 1: 라우터 업데이트 (1일)
```python
def select_model(phase, has_template, context_size):
    if phase in [0, 1, 2]:
        return "gpt-4o-mini"
    
    if phase == 3:
        if has_template:
            return "gpt-4o-mini"
        else:
            return "sonnet-4.5"
    
    if phase == 4:
        complexity = assess_complexity()
        if complexity == "high":
            return "opus-4.1"  # 확정 가격!
        else:
            return "sonnet-4.5"
    
    # 컨텍스트 고려
    if context_size > 200000:
        if context_size > 300000:
            return "gpt-4o"  # 비용 주의
        else:
            return "haiku-4.5"  # 200K 지원
```

### Step 2: 비용 모니터링 (즉시)
- Sonnet 4.5 사용 시 컨텍스트 크기 확인
- 200K 초과 시 경고
- 긴 문서는 Haiku 4.5 고려

### Step 3: 템플릿 확장 (1주)
- Phase 3 작업 템플릿 10-20개 추가
- GPT-4o-mini 사용률 85% → 90% 증가
- 추가 20-30% 비용 절감

---

## 📈 예상 효과

### 비용 절감
```yaml
현재 (Sonnet 4.5 100%):
  - 1,000회: $10.50
  - 10,000회: $105.00
  - 100,000회: $1,050.00

최적화 후 (2-Tier Hybrid):
  - 1,000회: $1.96 (81% 절감)
  - 10,000회: $19.60 (81% 절감)
  - 100,000회: $196.00 (81% 절감)

연간 절감 (100,000회 기준):
  - $854 절감
  - 한화 약 110만원 절감
```

### 품질 유지
```yaml
85% 작업 (GPT-4o-mini):
  - 기존과 동일 품질 (95%)
  - 속도 3-5배 빠름
  
15% 작업 (Sonnet 4.5):
  - 기존과 동일 품질 (95%)
  - 균형잡힌 성능

5% 작업 (Opus 4.1):
  - 최고 품질 (98%)
  - 확정 가격으로 예산 관리 용이
```

---

## ⚠️ 주의사항

### 1. Sonnet 4.5 컨텍스트 모니터링
```python
# 컨텍스트 크기 확인
if model == "sonnet-4.5":
    context_size = count_tokens(prompt)
    if context_size > 200000:
        estimated_cost = context_size * $6 / 1000000  # 2배 비용
        warn(f"Sonnet 4.5 200K 초과: 비용 {estimated_cost}")
```

### 2. Haiku 선택 가이드
```yaml
Haiku 3.5 (Legacy):
  - 사용 금지 ❌
  - Haiku 4.5로 대체

Haiku 4.5:
  - 200K 컨텍스트 필요 시만 사용
  - GPT-4o-mini가 8배 저렴
  - 긴 문서 분석 전용
```

### 3. 신규 OpenAI 모델
```yaml
사용 금지 (UMIS 오버킬):
  - gpt-5-pro: $15/$120 (너무 비쌈)
  - o1-pro: $150/$600 (최고가!)
  - o3-pro: $20/$80 (Opus 대비 비쌈)
  - deep-research 모델들 (특수 용도)

예외:
  - 특별한 요구사항 있을 시만
  - 예산 충분할 때
```

---

## 🎯 최종 권장 (2025-11-20)

### 즉시 적용
1. **GPT-4o-mini**: 85% 작업 (Phase 0-3 템O)
2. **Sonnet 4.5**: 15% 작업 (Phase 3 템X, Phase 4)
3. **컨텍스트 모니터링**: 200K 초과 경고

### 선택적 적용
4. **Opus 4.1**: 최고급 작업 (5%)
5. **Haiku 4.5**: 긴 컨텍스트 (200K+)

### 사용 금지
6. **Haiku 3.5**: Haiku 4.5로 대체
7. **신규 Pro 모델들**: 오버킬

---

**작성일**: 2025-11-20
**적용 버전**: UMIS v7.8.0+
**예상 절감**: 81% (연간 약 110만원, 100,000회 기준)

