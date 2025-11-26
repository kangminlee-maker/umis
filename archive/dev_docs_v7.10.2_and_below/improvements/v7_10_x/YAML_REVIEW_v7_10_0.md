# umis.yaml Work Domain 검토 결과 (v7.10.0)

**작성일**: 2025-11-23
**검토 대상**: Estimator Work Domain YAML
**결과**: ✅ **승인 (일부 개선 반영)**

---

## 📝 전체 평가

### ✅ 장점

1. **구조 명확**: 3-Stage Pipeline이 잘 정리됨
2. **상세성**: 각 Phase 역할/동작이 구체적
3. **실용성**: 코드 구현 가능
4. **피드백 반영**: Hard/Soft 분리, Phase 3 Range 엔진 명시

### 🔧 개선 사항 (5가지 반영)

---

## 🔧 개선 사항 상세

### 1. **Phase 3 역할 명확화** ⭐⭐⭐⭐⭐

**원본**:
```yaml
phase_3_guestimation_range:
  output:
    value_range: "최소/최대 값"
    confidence: "0.70-0.90"
```

**개선**:
```yaml
phase_3_guardrail_range_engine:
  redesign_v7_10_0: "순수 Range 엔진으로 재정의"
  output:
    value: "None (부수적) 또는 Range 중앙값"
    value_range: "[min, max] (핵심 출력)"
    confidence: "0.90-0.95 (Hard Guardrail 기반)"
  
  constraints_usage:
    hard_only: "논리적 100% 제약만 Range 생성에 사용"
    soft_context_only: "reasoning에만 사용, Range 제한 안 함"
```

**효과**: Phase 3 = **"Hard Guardrail Range 엔진"** 명확화

---

### 2. **Hard/Soft Guardrail 명시적 분리** ⭐⭐⭐⭐⭐

**원본**:
```yaml
guardrails:
  types: ["upper_bound", "lower_bound", "exact", "ratio"]
```

**개선**:
```yaml
guardrails:
  types:
    hard:
      - "hard_upper: 논리적 상한 (음식점 < 사업자)"
      - "hard_lower: 논리적 하한 (자영업자 > 0)"
      - "logical: 물리적/수학적 제약 (value >= 0)"
    soft:
      - "soft_upper: 경험적 상한 (통계적)"
      - "soft_lower: 경험적 하한"
      - "expected_range: 일반 범위"

application_points:
  phase_3:
    usage: "Hard guardrails만 사용하여 Range 생성"
  phase_4:
    usage: "Hard/Soft 모두 참고"
  synthesis:
    usage: "Hard 위반 시 값 조정, Soft 위반 시 경고"
```

**효과**: 역할 명확, 안정성 향상

---

### 3. **Synthesis 위상 명확화** ⭐⭐⭐⭐

**원본**:
```yaml
stage_3_synthesis:
  phase_number_in_result: "5 (Synthesis, 내부 phase 표기용)"
```

**개선**:
```yaml
stage_3_synthesis:
  phase_number:
    external_api: "4 (API 호환성 유지)"
    internal_log: "5 또는 'Synthesis' (로그 명확화)"
```

**효과**: API 안정성 + 내부 명확성

---

### 4. **실행 가능성 가이드 추가** ⭐⭐⭐⭐

**추가**:
```yaml
implementation_guidance:
  code_structure:
    functions:
      stage_1:
        - "_stage1_collect()"
        - "_check_project_data_sync()"
        - "asyncio.gather(phase1, phase2)"
      
      stage_2:
        - "_stage2_estimate()"
        - "asyncio.gather(phase3, phase4)"
      
      stage_3:
        - "_stage3_synthesis()"
        - "_cross_validate()"
        - "_weighted_fusion()"
        - "_guardrail_validate()"

migration_path:
  from: "v7.9.0 Sequential"
  to: "v7.10.0 Hybrid"
  steps: ["Week 1-5 로드맵"]
```

**효과**: 구현 방향 명확

---

### 5. **검증 케이스 명시** ⭐⭐⭐⭐

**추가**:
```yaml
testing_strategy:
  validation_cases:
    - "'자영업자 수' → '개인사업자', '경제활동인구' 가드레일"
    - "'음식점 수' → '사업자 수' 상한선"
    - "Phase 3 [20만, 40만] + Phase 4 30만 → Agreement"
```

**효과**: 테스트 시나리오 명확

---

## 📊 최종 YAML 구조

```yaml
hybrid_architecture_v7_10_0:
  version: "v7.10.0"
  status: "🚧 설계 완료, 구현 대기"
  
  stage_overview:
    stage_1_tiered_collection:
      outputs: [definite_values, guardrails (hard/soft)]
    
    stage_2_parallel_estimation:
      phase_3: Range Engine (Hard 기반)
      phase_4: Point Estimator (Fermi)
    
    stage_3_synthesis:
      steps:
        1. definite_values 우선
        2. Cross-Validation (Range ∋ Point)
        3. Weighted Fusion (신뢰도/불확실성)
        4. Guardrail Validation (Hard/Soft)
        5. Result Construction
  
  information_flow:
    pattern: "Unidirectional + Shared Collector"
    fast_path: "Phase 0-2 확정값 → 즉시 반환"
    no_early_return: "그 외 → Synthesis"
  
  phase_definitions:
    phase_0: Literal (프로젝트 데이터)
    phase_1: Direct RAG (학습 규칙)
    phase_2: Validator (검증 데이터)
    phase_3: Guardrail Range Engine (Hard 제약)
    phase_4: Fermi Decomposition (Point)
  
  guardrail_system:
    collector: [definite_values, hard_guards, soft_guards]
    priority: [Validator > Project > RAG > Soft]
    application: [Phase3=Hard, Phase4=All, Synthesis=Validate]
  
  implementation_guidance:
    code: [Stage1-3 함수 구조]
    testing: [Unit + Integration + Validation]
    migration: [Week 1-5]
  
  expected_improvements:
    speed: 100배 (Phase 0)
    confidence: +15-20%
    information: 손실 제거
    parallelism: 23% 단축
```

---

## ✅ 승인 사항

1. **전체 구조**: 3-Stage Pipeline ✅
2. **Phase 정의**: 0-4 역할 명확 ✅
3. **Guardrail System**: Hard/Soft 분리 ✅
4. **Synthesis 로직**: 5-Step 명확 ✅
5. **구현 가이드**: 코드 구조 제시 ✅

---

## 📅 다음 단계

### 1. umis.yaml 반영
```bash
# 위치
umis.yaml의 Estimator 섹션
"# ===== 3. WORK DOMAIN =====" 부분

# 파일
estimator_work_domain_v7_10_0.yaml 내용 복사
```

### 2. 구현 착수 (Week 1)
- GuardrailType (HARD/SOFT)
- GuardrailCollector
- Phase 3 → Phase3GuardrailRangeEngine

### 3. 테스트 케이스 작성
- 자영업자 수 (구조적 제약)
- 음식점 수 (상한선)
- Agreement 시나리오

---

## 🎯 핵심 요약

### 작성된 YAML의 강점

- ✅ **명확성**: Stage/Phase/Guardrail 역할 분명
- ✅ **상세성**: 각 단계별 동작 구체적
- ✅ **실용성**: 코드 구현 가능
- ✅ **검증성**: 테스트 케이스 명시

### 개선 사항 (모두 반영)

- ✅ Phase 3: 순수 Range 엔진
- ✅ Hard/Soft: 명시적 분리
- ✅ Synthesis: API 호환 + 로그 명확
- ✅ 구현 가이드: 함수 구조
- ✅ 테스트: 검증 케이스

---

**결론**: **승인 + 개선 반영 완료** ✅

**위치**: `/Users/kangmin/umis_main_1103/umis/estimator_work_domain_v7_10_0.yaml`

**다음**: umis.yaml에 반영 → Week 1 구현 착수

---

**END**
