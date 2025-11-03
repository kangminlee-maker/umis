# 즉시 실행 항목 재정의

**날짜:** 2025-11-02  
**전제:** umis_guidelines.yaml 모듈화 보류

---

## 📋 실행 항목

### ✅ 1. umis_guidelines_v6.2_rag_enabled.yaml 처리

**현재 위치:**
```
rag/docs/architecture/umis_guidelines_v6.2_rag_enabled.yaml (138줄)
```

**분석:**
```yaml
역할:
  RAG 통합 버전 가이드
  
내용:
  • _rag_integration 섹션
  • RAG 함수 설명
  • 사용 가이드
  • 실제 guidelines는 참조만

v7.0.0:
  .cursorrules로 대체됨!
  
  .cursorrules:
    • RAG 자동화 규칙
    • 훨씬 실용적
  
  결론: 불필요! ❌
```

**처리:**
```yaml
채택: 삭제

이유:
  • .cursorrules가 완전 대체
  • RAG 통합은 자동화됨
  • 중복 문서
  • rag/docs/architecture/ 정리

실행:
  rm rag/docs/architecture/umis_guidelines_v6.2_rag_enabled.yaml
```

---

### ✅ 2. patterns → data/raw/ 이동

**현재 상태:**
```
루트:
  • umis_business_model_patterns.yaml
  • umis_disruption_patterns.yaml

data/raw/:
  • umis_business_model_patterns.yaml (복사본)
  • umis_disruption_patterns.yaml (복사본)

→ 중복!
```

**실행:**
```bash
# 루트에서 제거
rm umis_business_model_patterns.yaml
rm umis_disruption_patterns.yaml

# data/raw/만 유지 ✅
```

**영향:**
```yaml
사용자: 변화 없음 (Cursor 자동 찾기)
scripts/: 이미 data/raw/ 참조
결과: 루트 깔끔!
```

**우선순위:** P0

---

### ✅ 3. umis_ai_guide.yaml 백업

**재정의:**
```yaml
채택: data/raw/ 이동

실행:
  mv umis_ai_guide.yaml data/raw/

이유:
  • 참조용 백업
  • RAG 소스 가능 (향후)
  • 루트 깔끔
  • 안전
```

**우선순위:** P0

---

### ✅ 4. umis_guidelines.yaml → umis.yaml

**재정의:**
```yaml
채택: umis.yaml

실행:
  mv umis_guidelines.yaml umis.yaml

이유:
  • 간결 (Cursor: @umis.yaml)
  • "guidelines" 레거시 제거
  • 모듈화 준비 (향후)

참조 업데이트:
  • .cursorrules
  • README.md
  • START_HERE.md
  • SETUP.md
  • rag/docs/
```

**우선순위:** P0

---

### ✅ 5. .cursorrules 최적화

**실행:**
```bash
mv .cursorrules_new .cursorrules
```

**내용:**
```yaml
Before: 243줄
After: 145줄 (현재 _new)

개선:
  • Agent ID 사용
  • Part 1: UMIS 개념 (최우선!)
  • Part 2: 자동화
  • Part 3: 경로
  • Part 4: 메시지

압축: 40%
```

**추가 필요:**
```yaml
umis.yaml 참조 규칙:
  
  When user asks market analysis:
    Before starting:
      1. Read @umis.yaml (system definition)
      2. Extract workflow
      3. Generate roadmap
      4. Present & approve
      5. Execute
```

**우선순위:** P0

---

## 🎯 실행 순서

```yaml
Step 1: rag_enabled 삭제
  rm rag/docs/architecture/umis_guidelines_v6.2_rag_enabled.yaml

Step 2: patterns 이동 (실제로는 삭제, data/raw/ 유지)
  rm umis_business_model_patterns.yaml
  rm umis_disruption_patterns.yaml

Step 3: ai_guide 백업
  mv umis_ai_guide.yaml data/raw/

Step 4: guidelines → umis
  mv umis_guidelines.yaml umis.yaml
  
  참조 업데이트:
    sed -i '' 's/umis_guidelines\.yaml/umis.yaml/g' .cursorrules
    sed -i '' 's/@umis_guidelines\.yaml/@umis.yaml/g' README.md START_HERE.md

Step 5: .cursorrules 최적화
  # .cursorrules_new 수정 (umis.yaml 참조 규칙 추가)
  # 적용
  mv .cursorrules_new .cursorrules

Step 6: 커밋 & 푸시
```

---

## 📊 최종 구조

### 루트 YAML (7개 → 4개)

```yaml
Before:
  • umis_guidelines.yaml (5,428줄)
  • umis_business_model_patterns.yaml
  • umis_disruption_patterns.yaml
  • umis_ai_guide.yaml
  • umis_deliverable_standards.yaml
  • umis_examples.yaml
  • agent_names.yaml

After:
  • umis.yaml (5,428줄) ⭐
  • umis_deliverable_standards.yaml
  • umis_examples.yaml
  • agent_names.yaml
```

### data/raw/

```yaml
Before:
  • umis_business_model_patterns.yaml (복사본)
  • umis_disruption_patterns.yaml (복사본)

After:
  • umis_business_model_patterns.yaml ✅
  • umis_disruption_patterns.yaml ✅
  • umis_ai_guide.yaml ⭐ 백업
```

### 삭제

```yaml
❌ rag/docs/architecture/umis_guidelines_v6.2_rag_enabled.yaml
   이유: .cursorrules로 대체
```

---

**실행 준비 완료!** 🚀
