# Overlay 레이어 (Core/Team/Personal) 검토

**제안:** 개인 실험과 팀 표준을 한 시스템에서

---

## 🔍 문제 상황

### 브라운필드 충돌

```yaml
시나리오:
  Core (공식):
    umis_business_model_patterns.yaml
    • subscription_model (공식)
    • 코웨이 사례 (검증됨)
  
  Personal (개인 실험):
    사용자 A: "피아노 구독 추가 (실험)"
    
    umis_business_model_patterns.yaml에 직접 추가?
    → Core 오염! 🚨
  
  Team (팀 표준):
    팀: "음악 산업 패턴 (팀 전용)"
    
    어디에 추가?
    → Core? Personal?
    → 혼란! 🚨

문제:
  • 개인 실험이 Core 섞임
  • 검증 안 된 것이 팀 전파
  • 충돌, 덮어쓰기 위험
  
  → 관리 불가능! ❌
```

---

## 💡 제안: 3-Layer Overlay

### 계층 구조

```yaml
1. Core (공식, 읽기 전용):
   umis_business_model_patterns.yaml
   
   내용:
     • 검증된 패턴 (7개)
     • 검증된 사례 (30개)
     • Guardian 승인
   
   변경:
     • Pull Request만
     • 리뷰 필수
     • 공식 릴리즈

2. Team (팀 표준):
   team/team_patterns.yaml
   
   내용:
     • 팀 전용 패턴
     • 팀 사례
     • 팀장 승인
   
   변경:
     • 팀원 누구나
     • 팀 내 공유
     • Core 제안 가능

3. Personal (개인 실험):
   personal/{user_name}/my_patterns.yaml
   
   내용:
     • 개인 실험
     • 아이디어
     • 초안
   
   변경:
     • 자유롭게
     • Team 제안 가능
```

### 우선순위 (Overlay)

```python
def search_pattern(query):
    """
    3-Layer 순서로 검색
    """
    
    # 1. Personal (최우선!)
    result = search_in('personal/{user}/my_patterns.yaml', query)
    if result:
        return result
    
    # 2. Team
    result = search_in('team/team_patterns.yaml', query)
    if result:
        return result
    
    # 3. Core (마지막)
    result = search_in('umis_business_model_patterns.yaml', query)
    return result
```

**효과:**
```yaml
개인 실험:
  personal/에서 자유롭게
  → Core 영향 없음! ✅

팀 표준:
  team/에서 공유
  → 개인 실험 오염 없음! ✅

Core 보호:
  공식만
  → 품질 유지! ✅

승격 경로:
  Personal → Team → Core
  → 검증 단계! ✅
```

---

## 🔧 구조 예시

```
umis-main/
├── core/  # Core Layer
│   ├── umis_guidelines.yaml
│   ├── umis_business_model_patterns.yaml
│   └── umis_disruption_patterns.yaml
│
├── team/  # Team Layer
│   ├── team_patterns.yaml
│   ├── team_cases.yaml
│   └── README.md
│
├── personal/  # Personal Layer
│   ├── user_a/
│   │   ├── my_experiments.yaml
│   │   └── draft_patterns.yaml
│   └── user_b/
│       └── my_ideas.yaml
│
└── config/
    └── layer_priority.yaml  # Personal > Team > Core
```

---

## 📊 장단점

### 장점

```yaml
✅ 격리:
   • 개인/팀/Core 분리
   • 충돌 없음

✅ 안전:
   • Core 보호
   • 실험 자유

✅ 승격:
   • Personal → Team → Core
   • 검증 단계

✅ 협업:
   • 팀 공유 쉬움
   • 개인 보호됨
```

### 단점

```yaml
❌ 복잡도:
   • 3개 레이어 관리
   • 우선순위 로직
   • 병합 충돌?

❌ 초기 설정:
   • 폴더 구조
   • layer_priority.yaml
   • 검색 로직

❌ 혼란:
   • "어디에 추가?"
   • Personal? Team?
   • 판단 필요
```

---

## 🎯 필요성 검증

### UMIS 사용 패턴

```yaml
현재 (v7.0.0):
  사용자: 1명 (당신)
  
  필요:
    Personal: 불필요 (혼자)
    Team: 불필요 (팀 없음)
    Core: 충분!

6개월 후:
  사용자: 3-5명 (팀)
  
  필요:
    Team: 필요! (팀 공유)
    Personal: 선택 (실험)

1년 후:
  사용자: 10+명
  
  필요:
    3-Layer: 필수! (충돌 방지)
```

### 현 단계 판단

```yaml
지금 (1명):
  Core만으로 충분
  → 3-Layer 불필요

향후 (팀):
  Team 레이어 추가
  → 그때 구현!

문제:
  미리 구현 vs 필요 시 구현?
  
  미리:
    • 설계 명확
    • 나중에 쉬움
  
  필요 시:
    • 지금 단순
    • 오버헤드 없음
```

---

## 💡 절충안: 설계만 (구현 나중에)

```yaml
지금:
  • 3-Layer 설계 문서화
  • 폴더 구조 정의
  • 우선순위 로직 설계

나중에 (팀 생길 때):
  • team/ 폴더 생성
  • layer_priority.yaml 추가
  • 검색 로직 구현

장점:
  ✅ 지금: 단순 (구현 안 함)
  ✅ 향후: 준비됨 (설계 있음)
  ✅ 점진적: 필요 시 활성화
```

---

## 🎯 6번 최종 추천

**설계만 + 구현은 향후**

```yaml
지금 (v7.0.0):
  • 설계 문서화 ✅
  • 폴더 구조 정의 ✅
  • 구현: 안 함 ❌

향후 (팀 확장 시):
  • team/ 폴더 생성
  • 검색 로직 구현
  • 활성화

우선순위:
  설계: P0 (지금)
  구현: P2 (향후)

→ 점진적 접근! ✨
```

**당신의 의견은?**

A. 지금 구현 (미리 준비)  
B. 설계만 (필요 시 구현) ⭐ 제 추천  
C. 완전 제외

선택해주세요! 🚀
