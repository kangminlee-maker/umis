# umis.yaml 수동 정리 가이드

**작성일**: 2025-11-10  
**버전**: v7.5.0  
**필수성**: 선택 (코드는 이미 정리됨)  

---

## 📋 정리 대상

### Line 6048~6293: guestimation 섹션 (약 245줄)

**제거 대상**:
```yaml
      guestimation:
        name: "Guestimation (Fermi Estimation)"
        version: '3.0'
        category: "범용 추정 방법론 → v7.3.2: Estimator Agent로 통합"
        
        # 8개 출처 세부 설명 (source_1~source_8)
        # 4대 비교 기준
        # 8단계 프로세스
        # 예시 4개
        # Agent별 사용 가이드
        # ... 약 245줄
```

### Line 6294~6513: domain_reasoner 섹션 (약 219줄)

**제거 대상**:
```yaml
      # domain_reasoner - REMOVED (v7.5.0)
      # ... 주석 ...
        
        definition:
          core: "10가지 신호 우선순위..."
        
        # 10개 신호 세부 (s1~s10)
        # 6단계 파이프라인
        # Should vs Will
        # Agent별 사용 가이드
        # ... 약 219줄
```

### Line 6514~6664: hybrid_strategy 섹션 (약 150줄)

**제거 대상**:
```yaml
      hybrid_strategy:
        name: "Hybrid 2-Phase Approach"
        
        # Phase 1: Guestimation
        # Guardian 평가
        # Phase 2: Domain Reasoner
        # 5개 시나리오
        # Cursor 명령어 (@guestimate, @reasoner)
        # 비교 매트릭스
        # ... 약 150줄
```

**총 제거**: 약 614줄

---

## ✅ 대체 내용 (간결)

### 새로운 내용 (~70줄)

```yaml
    methodologies:
      # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
      # Estimation Methodologies - CONSOLIDATED (v7.5.0)
      # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
      # 
      # v7.2.0: guestimation + domain_reasoner (독립 방법론)
      # v7.5.0: Estimator Agent로 통합 (3-Tier)
      # 
      # Archive (614줄 제거):
      #   - guestimation 섹션 (245줄)
      #   - domain_reasoner 섹션 (219줄)
      #   - hybrid_strategy 섹션 (150줄)
      # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
      
      estimator_agent:
        name: "Estimator (Fermi) Agent"
        version: "v7.5.0"
        tool_key: "tool:estimator:estimate"
        category: "값 추정 (Single Source of Truth)"
        status: "✅ 완성 (3-Tier, 100% 커버리지)"
        
        role:
          what: "데이터 없을 때 값을 창의적으로 추정"
          not_what: "계산 (Quantifier), 검증 (Validator)"
          mece: "Estimator = 추정, Quantifier = 계산"
        
        three_tier_architecture:
          tier_1:
            method: "Built-in + 학습 규칙"
            threshold: "유사도 0.95+ (v7.5.0 강화)"
            speed: "<0.5초"
          
          tier_2:
            method: "11 Sources 판단"
            threshold: "confidence 0.80+ (v7.5.0 강화)"
            speed: "3-8초"
            sources: "Physical(3) + Soft(3) + Value(5)"
          
          tier_3:
            method: "일반 Fermi 분해 (재귀)"
            speed: "10-30초"
            examples: ["음식점 수", "탁구공 개수", "커피 시장"]
        
        usage:
          python: "estimator.estimate(question, domain, region)"
          cursor: "@Fermi, B2B SaaS 한국 ARPU는?"
        
        collaboration:
          quantifier: "★★★★★ 계산 시 값 요청"
          explorer: "★★★★ 기회 크기"
          observer: "★★★ 비율 추정"
          validator: "★★★ 교차 검증"
          guardian: "★ 리소스 추정"
        
        deprecated:
          tools:
            - "tool:universal:guestimation → tool:estimator:estimate"
            - "tool:universal:domain_reasoner → Estimator Tier 2"
          
          methods:
            - "Quantifier.calculate_sam_with_hybrid()"
            - "Guardian.recommend_methodology() (Deprecated)"
          
          methodologies:
            - "Guestimation 8개 출처 → Estimator Tier 2 (11 Sources)"
            - "Domain Reasoner 10개 신호 → Estimator Tier 2"
            - "Hybrid 2-Phase → Estimator 3-Tier"
          
          archive: "archive/v7.2.0_and_earlier/"
  
  # 7. 측정과 개선 (MEASURE)
  measurement_and_improvement:
```

---

## 🔧 수동 정리 방법

### Option 1: 직접 편집 (권장)

1. **umis.yaml 열기**
2. **Line 6048 찾기**: `methodologies:`
3. **Line 6048~6664 선택** (약 617줄)
4. **삭제**
5. **위의 "대체 내용" 붙여넣기** (~70줄)
6. **저장**

### Option 2: v8.0에서 처리

- 현재 상태 유지 (참고 문서로)
- 다음 메이저 버전에서 정리

---

## ⚠️ 중요

**코드 레벨에서는 이미 완료됨**:
- Estimator/Quantifier 코드 분리 ✅
- Domain Reasoner 제거 ✅
- Tool Registry 정리 ✅

**umis.yaml은 문서성 내용**:
- 동작에 영향 없음
- 참고용 문서
- 수동 정리 권장

---

## 📊 정리 효과

```
Before: 6,790줄
After:  6,176줄
감소:   614줄 (9.0% 축소)

더 간결하고 명확한 문서!
```

---

**END**

