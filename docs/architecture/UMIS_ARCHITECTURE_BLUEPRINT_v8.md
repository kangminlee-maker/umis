# UMIS v8 Architecture Blueprint

Universal Market Intelligence System – v8 아키텍처 설계서

본 문서는 v8 기준으로 시스템을 재구현할 수 있을 정도의 완결성을 목표로 한다. v7 문서와의 차이를 명확히 하고, 실제 구성 파일(`umis_v8.yaml`)과 1:1로 매핑되는 구조를 제공한다.

---

## 1. System Philosophy (v8)

- Agent 중심 구조 유지: 동일 Agent로 다양한 Workflow를 조합해 여러 시스템을 구성 가능
- Truth Factory: Validator–Calculator–Estimator 3 Agent가 Business Layer가 사용할 단일 진실(SSoT)을 생산
- Value Store(VAL-*): Business Layer는 항상 VAL-*만 참조
- Clean Architecture: Estimator Fusion을 도메인 순수 함수(FusionPolicy)로 격리, LLM 추상화 완전 캡슐화
- RAG 4-Layer 유지: Canonical / Projected / Knowledge Graph / Memory

---

## 2. What’s New in v8 (vs v7)

- Quantifier → Calculator: 계산/공식/분해/수렴 허브로 재정의(Agent 유지, 내부 엔진은 Tool)
- Estimator 재정의: Generative Prior 전담(Last Resort), 재귀 없음
- Truth Factory 도입: EvidenceCollector → Validator → Calculator → Estimator → Fusion
- Value Store(VAL-*) 도입: 최종 참조 레코드, Business Layer는 VAL-*만 직접 사용
- 용어 분리: source_tier(데이터 세계) vs origin_level(계산 파이프라인 내부 원천 레벨)
- curated internal(KG/패턴 YAML) 공식에 준하는 1b 등급으로 승격

---

## 3. Core Terms (Aligned with `umis_v8.yaml`)

- agent_tier
  - tier_1_business_analysis: `observer`, `explorer`
  - tier_2_evidence_generation: `evidence_collector`, `validator`, `calculator`, `estimator`
  - tier_3_supervision: `guardian`
- source_tier(데이터 우선순위)
  - 1: official, 1b: curated_internal, 2: commercial, 3: structured_estimation, 4: llm_baseline
- origin_level(계산 파이프라인 내부 레벨)
  - level_1_official, level_1b_curated, level_2_validated, level_3_calculated, level_4_prior

---

## 4. High-level Architecture

```
[Layer 1: Business]
  Observer(구조/리포트)  Explorer(기회)
        │                     │
        └─────── value_service.get(metric, context, policy) ───────┐
                                                                   ▼
[Truth Factory]
  EvidenceCollector → Validator → Calculator → Estimator → FusionPolicy
                                                                   ▼
[Value Store]
  VAL-* (canonical values, lineage, certainty)
                                                                   ▼
[Consumers]
  모든 Business Layer Agent는 VAL-*만 참조
```

---

## 5. Agents (v8 정의)

- Observer (Albert)
  - 역할: 시장 구조/가치사슬 관찰, 계산/추정은 Truth Factory 호출로 위임
  - 산출물: `market_reality_report.md`
  - 규칙: 보고 전 Fact-check Gate(Validator 승인) 필수
- Explorer (Steve)
  - 역할: 패턴/사례 탐색(RAG+Graph), 기회 포트폴리오 작성
  - 규칙: 빠른 prior는 Estimator 직접 호출 허용(draft), 보고 전 Truth Factory 재계산
- Calculator (Bill)
  - 역할: 공식/분해/수렴 허브, tracks(deterministic/scenario/exploratory)
  - 출력: TruthCandidateList, VAL 승격 후보 생성
- Validator (Rachel)
  - 역할: 공식/상업 데이터 수집·정의·신뢰도, EvidenceBundle 강화
- Estimator (Fermi)
  - 역할: Generative Prior(Last Resort), 재귀 금지, hard_bounds 준수
  - 출력: EstimationEvent(EST-*) – 최종 VAL은 아님
- Guardian (Stewart)
  - 역할: 정책/품질/메모리/런타임 감독, Fact-check Gate, Circuit Breaker
- EvidenceCollector (Infra)
  - 역할: <1s Fast Path(Literal/RAG/KG/Cache) EvidenceBundle 구성

---

## 6. Truth Factory

- 목적: Business Layer가 사용할 단일 진실을 규정된 순서와 정책으로 생산
- 단계
  1) EvidenceCollector: Literal/RAG/KG/Memory로 EvidenceBundle 생성
  2) Validator: Active Search로 공식/상업 데이터 보강
  3) Calculator: 공식 적용, Fermi 분해, 다중 방법론 수렴(Convergence)
  4) Estimator: 부족 변수 Prior 생성(Last Resort)
  5) FusionPolicy: Evidence/Calculated/Prior를 정책 가중으로 최종 합성
- FusionPolicy(도메인 순수 함수)
  - 입력: Stage 결과들의 리스트(Stage, value, confidence, bounds 등)
  - 규칙: Evidence 우선, hard_bounds, 일관성 검증, early_return 허용
  - 구성: domain/fusion_policy.py + config adapter(runtime.yaml)
- 산출
  - EstimationResult(최종 값/범위/확신도/lineage)
  - Value Store(VAL-*)로 승격되어 Business Layer에 제공

---

## 7. Value Store (VAL-*)

- 목적: Business Layer가 직접 참조하는 단일 진실 레이어
- ValueRecord 필드(예시)
  - metric_id, value, unit, period
  - source_mix(literal/calculated/estimated 비중)
  - lineage([SRC-*, EST-*, ASM-*, OPP-*])
  - certainty(high/medium/low), policy_tag(official/scenario/experimental)
- 규칙
  - Business Layer는 VAL-*만 직접 사용
  - Truth Factory 출력(EstimationResult)을 검증 통과 시 VAL로 승격

---

## 8. Data Source Priority & Fact-check Gate

- 우선순위
  1. source_tier_1_official
  1b. source_tier_1b_curated_internal(KG/패턴 YAML)
  2. source_tier_2_commercial
  3. source_tier_3_structured_estimation(구조적 계산)
  4. source_tier_4_llm_baseline(Prior)
- Fact-check Gate
  - 보고 전 Validator 승인 필수(의사결정/대외 산출물)
  - Guardian가 정책/품질 로그 관리

---

## 9. RAG & Knowledge Graph Integration

- Canonical Index(CAN-*)
  - 정규화 원본 청크, anchor_path + content_hash, 업데이트 친화
- Projected Index(PRJ-*)
  - Agent별 검색 뷰, projection_rules 90% + 10% LLM 학습
- Knowledge Graph(GND-*, GED-*)
  - 패턴/관계/조합, curated internal YAML 온보딩, evidence_high로 취급
- Memory(MEM-*, RAE-*)
  - Query/Goal/RAE, 순환 감지/목표 정렬/평가 재사용

---

## 10. Runtime & LLM Abstraction

- LLMProvider 인터페이스 유지, TaskType 기반 라우팅
  - prior_estimation, fermi_decomposition, fusion_validation
- 모드
  - yaml_only / hybrid / rag_full
  - Circuit Breaker 및 Fail-safe 정책(runtime.yaml)
- Fusion 모드 플래그
  - full / selector_only / disabled
  - 데이터 기반으로 운영 후 점진적 단순화 가능

---

## 11. Business Workflows (Agent Recipes)

- Observer Default
  - 구조/참여자/거래 관찰 → 핵심 지표 Truth Factory 요청 → Calculator 수렴 → Fact-check → 보고
- Explorer Default
  - 패턴/사례 검색(CAN/PRJ/KG) → OPP 후보 → Rough sizing Truth Factory → 검증 → 포트폴리오 확정
- 공통 규칙
  - Business Layer는 보고 수치에 대해 VAL-*만 사용
  - Draft 단계 prior는 Explorer에서 제한적으로 허용(명시적 태깅)

---

## 12. Migration from v7

- Agent
  - quantifier → calculator(Agent 유지, 내부 도구화)
  - estimator: Stage3/4 기능은 Calculator로 이동, Prior 전담
- 호출 매핑(가이드)
  - 순수 계산 → calculator.deterministic
  - 다중 방법론 사이징 → calculator.convergence
  - 구조 분해 필요 → calculator.fermi
  - 순수 추정 → estimator.prior
- ID 네임스페이스
  - VAL-* 도입(최종 참조), EST-*는 추정 이벤트(메모리/학습)로 축소

---

## 13. Quality & Validation

- Policy 기반 품질 관리(Guardian)
  - min_literal_ratio, min_convergence_methods, max_spread_ratio
- 평가 지표(검증 시)
  - 수치 오차(가능한 경우), certainty calibration, 다운스트림 영향(LTV, Payback 등)
- Fusion 검증
  - full vs selector_only vs disabled A/B, evidence-sparse + high-variance 구간 집중 분석

---

## 14. File & Config Map

- `umis_v8.yaml`
  - agents, truth_factory, value_store, data_source_priority, workflows, rag_and_kg, runtime, migration
- `config/schema_registry.yaml`
  - EvidenceBundle, TruthCandidate, EstimationResult, ValueRecord 스키마
- `config/runtime.yaml`
  - 모드/Fail-safe/Policies/Fusion 설정
- `config/projection_rules.yaml`
  - Canonical → Projected 규칙, curated_internal 반영

---

## 15. Appendix: ID Namespace

| Prefix | 의미 | 소유 |
|--------|------|------|
| SRC- | 원천 데이터 | Validator |
| EST- | Estimator 추정 이벤트 | Estimator |
| VAL- | Value Store Canonical Value | Truth Factory/Guardian |
| ASM- | Assumption | Calculator/Guardian |
| OPP- | 기회 가설 | Explorer |
| DEL- | 산출물 | Guardian |
| CAN-/PRJ- | RAG 청크 | RAG System |
| GND-/GED- | KG 노드/간선 | Neo4j |
| MEM-/RAE- | 메모리/평가 | Guardian |

---

본 문서는 v8 기준의 단일 진실 생산 공정을 중심으로 Agent 역할과 RAG 통합을 재정의한다. 세부 스키마/정책은 `umis_v8.yaml` 및 `config/*.yaml`에 위임하며, 해당 파일들만으로 실행 구성이 가능하도록 일관성을 유지한다.
