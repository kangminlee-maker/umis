# Cursor Composer 명령어 가이드

**UMIS v7.2.0** | Cursor Composer에서 사용 가능한 모든 명령어

---

## 📋 목차

1. [Agent 멘션 명령](#agent-멘션-명령)
2. [추정 방법론 명령](#추정-방법론-명령)
3. [복합 워크플로우](#복합-워크플로우)
4. [실제 사용 예시](#실제-사용-예시)

---

## 1. Agent 멘션 명령

### 1.1 기본 형식

```
@[Agent이름] [작업 내용]
```

**Agent 이름 (기본값):**
- `@Albert` 또는 `@Observer` - 시장 구조 분석
- `@Steve` 또는 `@Explorer` - 기회 발굴 (RAG 활용)
- `@Bill` 또는 `@Quantifier` - 정량 분석
- `@Rachel` 또는 `@Validator` - 데이터 검증
- `@Stewart` 또는 `@Guardian` - 품질 관리

**커스터마이징:** `config/agent_names.yaml` 파일에서 이름 변경 가능

---

### 1.2 Observer (Albert) 명령

**역할:** 시장 구조 분석, 가치사슬 매핑, 비효율성 발견

**명령 예시:**
```
@Observer, 음악 스트리밍 시장 구조 분석해줘
@Albert, 가치사슬 매핑해줘
@Observer, 비효율성 찾아봐
@Albert, 경쟁 구조 파악해줘
```

**주요 기능:**
- 시장 구조 관찰 (`tool:observer:market_structure`)
- 가치사슬 분석 (`tool:observer:value_chain`)
- 비효율성 감지 (`tool:observer:inefficiency_detection`)
- 파괴 기회 발견 (`tool:observer:disruption_opportunity`)

**산출물:**
- `market_reality_report.md`

---

### 1.3 Explorer (Steve) 명령

**역할:** 기회 발굴, 패턴 매칭, 가설 생성 (RAG 활용!)

**명령 예시:**
```
@Explorer, 구독 모델 패턴 찾아줘
@Steve, 음악 스트리밍 기회 분석해줘
@Explorer, 플랫폼 비즈니스 사례 찾아줘
@Steve, 패턴 조합 가능한 것 찾아봐
```

**주요 기능:**
- 패턴 검색 (`tool:explorer:pattern_search`) - RAG 자동 검색
- 7단계 기회 발굴 (`tool:explorer:7_step_process`)
- 가설 생성 (`tool:explorer:hypothesis_generation`)
- 검증 프로토콜 (`tool:explorer:validation_protocol`)

**RAG 활용:**
- 31개 비즈니스 모델 패턴 자동 검색
- 23개 Disruption 패턴 자동 검색
- Knowledge Graph로 패턴 조합 발견

**산출물:**
- `OPP_*.md` (기회 가설)
- `opportunity_portfolio.md`

---

### 1.4 Quantifier (Bill) 명령

**역할:** 시장 규모 계산, 성장률 분석, Excel 생성

**명령 예시:**
```
@Quantifier, 음악 스트리밍 SAM 계산해줘
@Bill, 시장 규모 추정해줘
@Quantifier, 성장률 분석해줘
@Bill, 벤치마크 비교해줘
```

**주요 기능:**
- SAM 4가지 방법 계산 (`tool:quantifier:sam_4methods`)
  - Method 1: Top-Down (TAM → SAM)
  - Method 2: Bottom-Up (세그먼트 합산)
  - Method 3: Proxy (벤치마크 조정)
  - Method 4: Competitor Revenue (경쟁사 역산)
- 성장률 분석 (`tool:quantifier:growth_analysis`)
- 시나리오 계획 (`tool:quantifier:scenario_planning`)
- 벤치마크 분석 (`tool:quantifier:benchmark_analysis`)

**Excel 자동 생성:**
- `market_sizing.xlsx` (9개 시트)
- `unit_economics.xlsx`
- `financial_projection.xlsx`

**산출물:**
- `market_sizing.xlsx`
- `growth_forecast.md`

---

### 1.5 Validator (Rachel) 명령

**역할:** 데이터 검증, 출처 확인, 정의 검증

**명령 예시:**
```
@Validator, MAU 정의 확인해줘
@Rachel, 데이터 출처 검증해줘
@Validator, Gap 분석해줘
@Rachel, 창의적 소싱 방법 알려줘
```

**주요 기능:**
- 데이터 정의 검증 (`tool:validator:data_definition`) - RAG 활용
- 출처 검증 (`tool:validator:source_verification`)
- Gap 분석 (`tool:validator:gap_analysis`)
- 창의적 소싱 (`tool:validator:creative_sourcing`) - 12가지 방법

**산출물:**
- `data_validation_report.md`
- `source_registry.md`

---

### 1.6 Guardian (Stewart) 명령

**역할:** 프로세스 모니터링, 품질 평가, 최종 승인

**명령 예시:**
```
@Guardian, 프로젝트 진행 상황 확인해줘
@Stewart, 산출물 품질 평가해줘
@Guardian, 목표 정렬 확인해줘
```

**주요 기능:**
- 진행 모니터링 (`tool:guardian:progress_monitoring`)
  - 순환 감지 (같은 주제 3회 반복)
  - 목표 정렬 확인
- 품질 평가 (`tool:guardian:quality_evaluation`)
  - 3단계 평가 (규칙 → 임계값 → LLM)
  - RAE Memory (평가 일관성)

**Meta-RAG:**
- Query Memory: 순환 패턴 감지
- Goal Memory: 목표 이탈 감지
- RAE Memory: 평가 일관성 유지

**산출물:**
- `quality_report.md`
- `project_log.md`

---

## 2. 추정 방법론 명령

### 2.1 @auto 명령 (Hybrid Strategy)

**설명:** Guardian이 자동으로 최적 방법론 선택

**형식:**
```
@auto [질문]
```

**예시:**
```
@auto 국내 OTT 시장 규모
@auto 피아노 구독 서비스 시장 크기
```

**동작:**
1. Phase 1: Guestimation (5-30분) 실행
2. Guardian 평가
3. 조건 충족 시 → Phase 2: Domain Reasoner (1-4시간)

**전환 트리거:**
- 신뢰도 < 50% → Domain Reasoner
- 범위 폭 > ±75% → Domain Reasoner
- 기회 > 1,000억 → Domain Reasoner
- 규제 산업 → Domain Reasoner (필수)
- 신규 시장 → Domain Reasoner

---

### 2.2 @guestimate 명령 (빠른 추정)

**설명:** UMIS Guestimation (빠른 추정, ±50% 정확도)

**형식:**
```
@guestimate [질문]
또는
@[Agent] guestimate [질문]
```

**예시:**
```
@guestimate 구독 모델 시장 규모
@Explorer guestimate 기회 크기
@Quantifier guestimate B2B SaaS Churn Rate
```

**특징:**
- ⚡ 속도: 5-30분
- 정확도: ±50% (자릿수)
- 적합: 초기 탐색, 기회 우선순위

**Fermi 4원칙:**
- 모형 (시장 = 고객 × 구매액)
- 분해 (1인당 = 교통 + 식비 + 숙박)
- 제약 (하루 24h, 1끼 30분)
- 자릿수 (500억? 5000억?)

**8가지 데이터 출처:**
1. 프로젝트 데이터
2. LLM 직접 ('한국 인구?')
3. 검색 공통 맥락 (웹)
4. 법칙 (물리/법률)
5. 행동경제학 (Loss Aversion)
6. 통계 패턴 (80-20)
7. Rule of Thumb (RAG)
8. 시공간 제약 (24h)

---

### 2.3 @reasoner 명령 (정밀 분석)

**설명:** Domain-Centric Reasoner (정밀 분석, ±30% 정확도)

**형식:**
```
@reasoner [질문]
또는
@[Agent] reasoner [질문]
```

**예시:**
```
@reasoner 시니어 케어 로봇 시장 규모
@Quantifier reasoner 시장 규모
@Validator reasoner KPI 정의
```

**특징:**
- 🔬 속도: 1-4시간
- 정확도: ±30% (수렴)
- 적합: 정밀 분석, 투자 심사, 규제 산업

**10가지 신호 우선순위:**
- s3 → s8 → s6 → s10 → s2 → ...
- s2: RAG Consensus (0.9 가중치)
- s9: Case Analogies (RAG)
- s10: Industry KPI (RAG)

**Should vs Will 분리:**
- 행동경제학 기반
- 증거표 + 검증 로그

---

## 3. 복합 워크플로우

### 3.1 시장 분석 (전체)

**명령:**
```
시장 분석해줘
음악 스트리밍 시장 분석해줘
```

**자동 실행:**
1. Observer → 시장 구조 관찰
2. Explorer → 기회 발굴 (RAG)
3. Quantifier → SAM 계산

**도구 로드:**
- `tool:observer:market_structure`
- `tool:explorer:pattern_search`
- `tool:quantifier:sam_4methods`

---

### 3.2 기회 검증

**명령:**
```
기회 검증해줘
구독 모델 기회 검증해줘
```

**자동 실행:**
1. Explorer → 기회 발굴
2. Validator → 데이터 검증
3. Quantifier → 규모 계산

---

### 3.3 Discovery Sprint

**조건:** 명확도 < 7 (목표 불명확)

**명령:**
```
Discovery Sprint 시작해줘
피아노 구독 서비스 Discovery Sprint
```

**자동 실행:**
- 5개 Agent 병렬 탐색
- 목표 구체화
- 다음 단계 결정

**도구 로드:**
- `tool:framework:discovery_sprint`
- 모든 Agent 도구

---

## 4. 실제 사용 예시

### 4.1 빠른 시작 예시

```
Cursor Composer (Cmd+I):
umis.yaml 첨부

"@Explorer, 구독 모델 패턴 찾아줘"
```

**결과:**
- Explorer가 RAG로 패턴 자동 검색
- `subscription_model` 발견
- Spotify, Netflix 사례 검색
- 패턴 조합 발견 (Graph)
- 가설 생성

---

### 4.2 시장 규모 계산 예시

```
"@Quantifier, 음악 스트리밍 SAM 계산해줘"
```

**결과:**
1. Validator가 데이터 정의 검증
2. Quantifier가 4가지 방법 계산
3. Convergence ±30% 확인
4. Excel 자동 생성 (`market_sizing.xlsx`)

---

### 4.3 Hybrid 추정 예시

```
"@auto 국내 OTT 시장 규모"
```

**결과:**
1. Phase 1: Guestimation (5-30분)
   - 빠른 추정 수행
2. Guardian 평가
   - 신뢰도 < 50% 감지
3. Phase 2: Domain Reasoner (1-4시간)
   - 정밀 분석 자동 실행
4. 최종 결과: ±30% 정확도

---

### 4.4 Agent 커스터마이징 예시

**설정:** `config/agent_names.yaml`
```yaml
explorer: Alex
quantifier: Mike
```

**사용:**
```
"@Alex, 기회 찾아봐"
"@Mike, 시장 규모 계산해줘"
```

**양방향 매핑:**
- 입력: `@Alex` → Explorer 실행
- 출력: Explorer → "Alex" 표시

---

## 5. 명령어 요약표

| 명령 형식 | 설명 | 예시 |
|---------|------|------|
| `@[Agent] [작업]` | Agent 멘션 | `@Explorer, 패턴 찾아줘` |
| `@auto [질문]` | 자동 방법론 선택 | `@auto 시장 규모` |
| `@guestimate [질문]` | 빠른 추정 | `@guestimate Churn Rate` |
| `@reasoner [질문]` | 정밀 분석 | `@reasoner 시장 규모` |
| `@[Agent] guestimate` | Agent + 빠른 추정 | `@Explorer guestimate 기회` |
| `@[Agent] reasoner` | Agent + 정밀 분석 | `@Quantifier reasoner SAM` |

---

## 6. 참고 문서

- **umis.yaml** - 메인 가이드라인 (Cursor 첨부용)
- **umis_core.yaml** - System RAG INDEX
- **umis_examples.yaml** - 실제 사용 예시
- **config/agent_names.yaml** - Agent 이름 커스터마이징
- **README.md** - 프로젝트 개요

---

**UMIS v7.2.0 • 2025**

