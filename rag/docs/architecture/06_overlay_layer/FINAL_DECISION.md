# Overlay 레이어 최종 결정

**날짜:** 2025-11-02  
**결론:** 설계만 (구현은 향후)

---

## 🎯 최종 아키텍처 (설계)

### 3-Layer Overlay

```yaml
구조:
  umis-main/
  ├── core/  # Core Layer (공식)
  │   ├── umis_guidelines.yaml
  │   ├── umis_business_model_patterns.yaml
  │   ├── umis_disruption_patterns.yaml
  │   └── ... (검증된 것만)
  │
  ├── team/  # Team Layer (팀 표준)
  │   ├── team_patterns.yaml
  │   ├── team_cases.yaml
  │   └── README.md
  │
  └── personal/  # Personal Layer (개인 실험)
      ├── {user_name}/
      │   ├── experiments.yaml
      │   └── draft_ideas.yaml
      └── README.md

우선순위:
  검색 시: Personal > Team > Core
  
  이유:
    개인 실험이 최우선 (덮어쓰기)
    팀 표준이 그 다음
    Core는 Fallback
```

### 승격 경로

```yaml
흐름:
  Personal (실험)
    ↓ 검증됨
  Team (공유)
    ↓ 팀 승인
  Core (공식)
    ↓ Guardian 검증

예시:
  1. Personal: "피아노 구독" 실험
  2. Team: 성공! 팀 공유
  3. Core: Guardian 검증 → 공식 등재
```

### 설정 파일

```yaml
# layer_config.yaml (설계)

layers:
  core:
    path: "core/"
    priority: 3
    write_access: "admin_only"
    validation: "guardian_required"
  
  team:
    path: "team/"
    priority: 2
    write_access: "team_members"
    validation: "team_lead_approval"
  
  personal:
    path: "personal/{user_name}/"
    priority: 1
    write_access: "owner_only"
    validation: "none"

search_order: [personal, team, core]

promotion_workflow:
  personal_to_team:
    - validation: "team_review"
    - approval: "team_lead"
  
  team_to_core:
    - validation: "guardian"
    - approval: "core_maintainer"
```

---

## 🎯 현재 vs 향후

### 현재 (v6.3.0-alpha)

```yaml
구현:
  ❌ 3-Layer 구현 안 함

설계:
  ✅ 문서화 (이 파일)
  ✅ 폴더 구조 정의
  ✅ 우선순위 로직

상태:
  Core만 사용 (단순)
```

### 향후 (팀 확장 시)

```yaml
트리거:
  • 사용자 3명 이상
  • 팀 공유 필요
  • 개인 실험 보호 필요

구현:
  1. team/ 폴더 생성
  2. personal/ 폴더 생성
  3. layer_config.yaml 작성
  4. 검색 로직 구현 (우선순위)
  
  소요: 2일

활성화:
  layer_config.yaml:
    enabled: true
```

---

## 📋 6번 최종 결정

**설계만 (구현 향후)**

```yaml
현재:
  • 설계 문서: ✅
  • 폴더 구조: ✅
  • 구현: ❌

향후:
  • 팀 확장 시 활성화
  • 2일 구현

우선순위:
  설계: P0 (지금)
  구현: P2 (향후)

장점:
  ✅ 지금: 단순 (Core만)
  ✅ 향후: 준비됨 (설계 있음)
  ✅ 점진적: 필요 시 활성화

→ 실용적 접근! ✨
```

---

**관련 문서:**
- 06_overlay_layer/REVIEW.md
- 이 파일 (FINAL_DECISION.md)

**상태:** ✅ 검토 완료, 설계만

**다음:** 7번 (Fail-Safe 런타임 모드)

