# Schema-Registry 최종 결정

**날짜:** 2025-11-02  
**결론:** Schema Registry + Contract Tests (2-Layer 방어)

---

## 🎯 최종 아키텍처

### 2-Layer 방어 시스템

```yaml
Layer 1: Schema Registry (설계 + 실행)
  파일: schema_registry.yaml
  
  역할:
    • 모든 필드 중앙 정의
    • Layer 간 필드 매핑
    • 타입 검증
    • 버전 호환성 관리
  
  예시:
    source_id:
      type: string
      required: true
      used_by: [layer1, layer2, layer3, layer4]
    
    explorer_pattern_id:
      type: string
      alias: [pattern_id]
      layer1: explorer_pattern_id
      layer3: pattern_id  # ← 매핑!

Layer 2: Contract Tests (검증)
  파일: tests/test_schema_contract.py
  
  역할:
    • Layer 간 호환성 실제 검증
    • 필드 손실 방지
    • 회귀 테스트
    • CI/CD 통합
  
  예시:
    def test_layer1_to_layer3():
        chunk = create_layer1_chunk()
        assert can_use_in_layer3(chunk)
```

### Pydantic 제외 결정

```yaml
제외 이유:
  1. 사용자 = Cursor 중심
     • Python 코드 직접 작성 안 함
     • Pydantic 타입 체크 불필요
  
  2. Schema Registry로 충분
     • 타입 검증: validate_field()
     • 필드 매핑: map_field()
     • alias: registry에서
  
  3. 단순성 우선
     • 2-Layer vs 3-Layer
     • YAML 중심 vs Python 중심
  
  판단:
    Pydantic 추가 가치 < 복잡도
    → 제외! ✅

metadata_schema.py:
  • 참조용으로 유지
  • 실제 사용 안 함
  • 향후 필요 시 활성화
```

---

## 🔧 구현 계획

### Phase 1: Schema Registry (1주)

```yaml
Day 1-2: schema_registry.yaml 작성
  • 모든 필드 정의 (core + layer별)
  • Layer 간 매핑 규칙
  • 타입 정의

Day 3-4: Registry 로직 구현
  • load_registry()
  • validate_field()
  • map_field()
  • check_compatibility()

Day 5: 통합
  • scripts/01_convert_yaml.py 통합
  • 자동 검증 추가

Day 6-7: 테스트
  • 모든 필드 검증
  • 매핑 테스트
```

### Phase 2: Contract Tests (3일)

```yaml
Day 1: 테스트 작성
  • Layer 1 ↔ Layer 3 호환성
  • Canonical ↔ Projected 손실 없음
  • 스키마 버전 호환성

Day 2-3: CI/CD 통합
  • GitHub Actions
  • 자동 실행
  • 회귀 방지
```

---

## 💡 실제 사용 예시

### 필드 추가 시

```yaml
사용자 작업:
  1. Cursor: "confidence_score 필드 추가해줘"

AI 자동 처리:
  1. schema_registry.yaml 수정:
     + confidence_score:
     +   type: float
     +   range: [0, 1]
     +   used_by: [layer1, layer2]
  
  2. validation 로직 자동 업데이트
  
  3. Contract Test 자동 실행
     → 호환성 확인
  
  4. 통과 → 사용 가능
     실패 → 수정 필요

사용자:
  대화만! 복잡도 0!
```

### 스키마 변경 시

```yaml
변경:
  "explorer_csf → explorer_success_factors"

Schema Registry:
  1. Deprecation 표시:
     explorer_csf:
       deprecated: true
       replaced_by: explorer_success_factors
  
  2. 양쪽 모두 지원 (전환 기간)
  
  3. Contract Test:
     • 기존 청크 (explorer_csf) → 작동 확인
     • 새 청크 (explorer_success_factors) → 작동 확인
  
  4. 점진적 마이그레이션

→ 안전한 변경! ✅
```

---

## 🎯 최종 판단

**당신의 제안이 정확합니다!**

```yaml
채택:
  ✅ Schema Registry (YAML)
  ✅ Contract Tests (pytest)

제외:
  ❌ Pydantic

이유:
  1. UMIS = Cursor 중심
     • 사용자: Python 안 씀
     • 개발자: Cursor가 대신
  
  2. Schema Registry로 충분
     • 타입 검증: validate()
     • 필드 매핑: map()
     • alias: registry
  
  3. 단순성
     • 2-Layer > 3-Layer
     • YAML 중심
     • 직관적

결론:
  당신이 맞음! ✅
  Pydantic은 오버엔지니어링!
```

**metadata_schema.py:**
```yaml
처리:
  • 참조용 유지
  • 주석 추가: "참조용, 미사용"
  • 향후 필요 시 활성화
```

---

## 📋 구현 우선순위

```yaml
2번 최종:
  🔴 P0: Schema Registry (1주)
  🟡 P1: Contract Tests (1주, 배포 시)

구현:
  즉시: schema_registry.yaml
  배포: Contract Tests
```

---

**다음:** 3번 (Routing YAML) 검토

**관련 문서:**
- 02_schema_registry/REVIEW.md
- 02_schema_registry/PYDANTIC_NECESSITY.md
- 이 파일 (FINAL_DECISION.md)

