# 파일명 버전 관리 전략

**질문:** 매번 버전 올릴 때마다 파일명 변경?

---

## 🔍 현재 문제

### v7.0.0인데 파일명은 v6.2

```yaml
현재:
  umis_guidelines.yaml
  umis_business_model_patterns.yaml
  umis_disruption_patterns.yaml
  ...

버전:
  VERSION.txt: 7.0.0
  
  → 불일치! ⚠️
```

---

## 💡 3가지 옵션

### Option 1: 매번 파일명 변경

```yaml
v6.2 → v7.0.0로 변경:
  umis_guidelines.yaml
  → umis_guidelines_v7.0.0.yaml

v7.0.0 → v6.3.0로 변경:
  umis_guidelines_v7.0.0.yaml
  → umis_guidelines_v6.3.0.yaml

v6.3.0 → v6.3.1로 변경:
  ...
```

**장점:**
```yaml
✅ 명확: 파일명만 보고 버전 알 수 있음
✅ 이력: 여러 버전 파일 공존 가능
```

**단점:**
```yaml
❌ 참조 깨짐: 모든 import, @umis... 변경
❌ 혼란: "어느 버전 써야 하나?"
❌ 유지보수: 매번 rename + 참조 수정
❌ 비효율: 마이너 변경에도 대공사
```

---

### Option 2: 파일명 고정

```yaml
파일명:
  umis_guidelines.yaml (버전 없음)
  umis_business_model_patterns.yaml
  ...

버전 표시:
  VERSION.txt: 7.0.0
  
  파일 내부:
    _meta:
      version: "7.0.0"
```

**장점:**
```yaml
✅ 안정: 참조 절대 안 깨짐
✅ 간단: rename 불필요
✅ 일관: 항상 같은 파일명
```

**단점:**
```yaml
❌ 모호: 파일명만 보고 버전 모름
❌ 이력: 여러 버전 공존 불가
```

---

### Option 3: 메이저만 파일명에 (추천!) ⭐

```yaml
파일명:
  umis_guidelines_v6.yaml (메이저만)
  umis_business_model_patterns_v6.yaml
  ...

버전 표시:
  VERSION.txt: 7.0.0
  
  파일 내부:
    _meta:
      version: "7.0.0"

변경 시점:
  v6.x → v7.0: 파일명 변경 (Breaking Change)
  v6.2 → v6.3: 파일명 유지 (내부만)
```

**장점:**
```yaml
✅ 안정: 마이너 변경 시 참조 유지
✅ 명확: 메이저 버전은 파일명으로
✅ 유연: 마이너는 내부 meta로
✅ 효율: 대부분의 경우 rename 불필요
```

**단점:**
```yaml
⚠️ 마이너: 파일명에 안 보임
   → 하지만 VERSION.txt와 _meta로 확인 가능
```

---

## 🎯 최종 추천: Option 3

### 전략

```yaml
파일명 구조:
  umis_guidelines_v{major}.yaml
  
  예:
    • v6.0, v6.1, v6.2, v6.3 → umis_guidelines_v6.yaml
    • v7.0 → umis_guidelines_v7.yaml (Breaking)

버전 관리:
  1. VERSION.txt (루트)
     7.0.0
  
  2. 파일 내부 _meta
     version: "7.0.0"
  
  3. CHANGELOG.md
     ## v7.0.0 ...

파일명 변경:
  Breaking Change 시에만 (v6 → v7)
```

---

## 🔄 현재 적용

### v7.0.0 적용 방안

```yaml
Option A: v6.2 유지 (추천!)
  파일명: v6.2 그대로
  이유: 
    • v6.x 시리즈
    • Breaking Change 아님
    • 참조 유지
  
  버전 표시:
    VERSION.txt: 7.0.0
    _meta: 7.0.0
    
  → 안정적! ✅

Option B: v7.0.0로 변경
  파일명: 모두 v7.0.0로
  이유:
    • 명확성
  
  작업:
    • 6개 YAML 파일명 변경
    • .cursorrules 참조 변경
    • 모든 문서 참조 변경
    
  → 번거로움! ❌
```

---

## 💡 제 강력한 추천

### v6.2 파일명 유지!

**이유:**

```yaml
1. v6 시리즈:
   • v6.0, v6.1, v6.2, v6.3 모두 v6
   • Breaking Change 아님
   • 호환성 유지

2. 안정성:
   • 참조 깨지지 않음
   • .cursorrules 변경 불필요
   • Cursor 사용자 혼란 없음

3. 효율성:
   • 파일명 변경 불필요
   • 대규모 수정 불필요

4. 버전 추적:
   • VERSION.txt: 7.0.0
   • CHANGELOG.md: 모든 변경
   • _meta: 파일 내부 버전
   
   → 충분히 명확!
```

**v7.0 나올 때:**
```yaml
그때 파일명 변경:
  umis_guidelines_v6.yaml
  → umis_guidelines_v7.yaml

이유: Breaking Change
```

---

## 🎯 결론

**v6.2 파일명 유지 권장!**

```yaml
현재:
  umis_guidelines.yaml ✅
  VERSION.txt: 7.0.0 ✅
  
  → 이대로 유지!

향후:
  v6.3.1, v6.4 → 파일명 유지
  v7.0 → 파일명 변경

이유:
  안정성 > 명확성
  효율성 > 완벽성
```

**어떻게 하시겠어요?**

A. v6.2 유지 (추천!) ✅  
B. v7.0.0로 변경  
C. 다른 방식?

