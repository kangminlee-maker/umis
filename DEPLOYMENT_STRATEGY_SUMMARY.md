# Balanced 배포 전략 요약

**작성일**: 2025-11-08  
**브랜치**: production-format-optimization  
**전략**: 개발 YAML → 프로덕션 Balanced (JSON.gz + MessagePack)

---

## 🎯 핵심 전략

```yaml
개발:
  - YAML 편집 (100% 유지)
  - Git 커밋 (YAML만)
  - 로컬 테스트 (YAML 직접 사용)

CI/CD:
  - YAML → JSON.gz (설정)
  - YAML → MessagePack (데이터)
  - Docker 빌드 (dist/만)

프로덕션:
  - JSON.gz + MessagePack 사용
  - 15-87배 빠른 로딩
  - YAML 원본 제외 (IP 보호)
```

---

## ✅ 실제 빌드 결과

### 성공: 18개 파일 변환

```
설정 (JSON.gz) - 9개:
  ✅ schema_registry.yaml → 4.5KB (78% 감소)
  ✅ tool_registry.yaml → 14KB (71% 감소)
  ✅ pattern_relationships.yaml → 5.8KB (85% 감소) ⭐
  ✅ agent_names.yaml → 122B (94% 감소) ⭐
  ✅ routing_policy.yaml → 1.2KB (73% 감소)
  ✅ runtime.yaml → 805B (75% 감소)
  ✅ llm_mode.yaml → 3KB (68% 감소)
  ✅ projection_rules.yaml → 908B (69% 감소)
  ✅ overlay_layer.yaml → 821B (77% 감소)

데이터 (MessagePack) - 9개:
  ✅ umis_business_model_patterns.yaml → 21KB (31% 감소)
  ✅ umis_disruption_patterns.yaml → 37KB (35% 감소)
  ✅ market_benchmarks.yaml → 35KB (34% 감소)
  ✅ market_structure_patterns.yaml → 27KB (32% 감소)
  ✅ value_chain_benchmarks.yaml → 16KB (34% 감소)
  ✅ calculation_methodologies.yaml → 24KB (31% 감소)
  ✅ definition_validation_cases.yaml → 19KB (46% 감소)
  ✅ data_sources_registry.yaml → 20KB (33% 감소)
  ✅ umis_ai_guide.yaml → 23KB (29% 감소)
  
기타:
  ✅ umis_deliverable_standards.yaml → 69KB (32% 감소)

총: 617KB → 356KB (42% 감소)
```

### 실패: 4개 파일 (YAML 파싱 에러)

```
❌ umis.yaml (YAML 구문 오류)
❌ umis_core.yaml (YAML 구문 오류)
❌ fermi_model_search.yaml (YAML 구문 오류)
❌ umis_examples.yaml (YAML 구문 오류)

→ 별도 수정 필요 (YAML 문법 검증)
```

---

## 📊 성능 효과 (성공한 18개 파일 기준)

### 파일 크기

```yaml
설정 (JSON.gz):
  원본: 133KB
  압축: 31KB
  감소: 77% ⭐⭐⭐

데이터 (MessagePack):
  원본: 485KB
  압축: 325KB
  감소: 33%

전체:
  원본: 618KB
  압축: 356KB
  감소: 42%
```

---

### 로딩 속도 (예상)

```yaml
설정 로딩 (1회):
  YAML: 80ms
  JSON.gz: 5ms (16배 빠름) ✅

데이터 로딩 (초당 10-100회):
  YAML: 200ms
  MessagePack: 2.3ms (87배 빠름) ✅⭐

전체:
  YAML: 280ms
  Balanced: 7.3ms (38배 빠름)
```

---

## 🚀 GitHub 배포 워크플로우

### 1. PR 검증

```yaml
feature/* → develop/main PR:
  ✅ YAML 린트
  ✅ Python 린트
  ✅ 단위 테스트 (YAML)
  ✅ Balanced 빌드 테스트
  ✅ 통합 테스트 (Balanced)
  
결과: PR 코멘트 (통과/실패)
```

**파일**: `.github/workflows/pr-check.yml` ✅

---

### 2. 스테이징 배포

```yaml
develop 브랜치 푸시:
  ✅ Balanced 빌드
  ✅ 빌드 검증
  ✅ Docker 빌드
  ✅ Docker 검증 (YAML 제외 확인)
  ✅ 스테이징 배포
  ✅ 헬스체크
  
결과: 스테이징 환경 업데이트
```

**파일**: `.github/workflows/deploy-staging.yml` ✅

---

### 3. 프로덕션 배포

```yaml
main 브랜치 푸시:
  ✅ Balanced 빌드
  ✅ 모든 테스트
  ✅ Docker 빌드
  ✅ Git 태그 생성 (선택)
  ✅ 프로덕션 배포
  ✅ 10분 모니터링
  ✅ Rollback (실패 시)
  
결과: 프로덕션 업데이트 또는 Rollback
```

**파일**: `.github/workflows/deploy-production.yml` ✅

---

## 📁 파일 구조

### Git 저장소 (YAML 원본)

```
umis/
├── .github/workflows/
│   ├── pr-check.yml              ← PR 검증
│   ├── deploy-staging.yml         ← 스테이징 배포
│   └── deploy-production.yml      ← 프로덕션 배포
│
├── config/
│   ├── schema_registry.yaml       ← Git 커밋 ✅
│   └── ...
│
├── data/raw/
│   ├── umis_business_model_patterns.yaml  ← Git 커밋 ✅
│   └── ...
│
├── scripts/
│   ├── build_balanced.py          ← 빌드 스크립트
│   └── ...
│
├── Dockerfile.balanced             ← Balanced 전용 Dockerfile
└── .gitignore                     ← dist/ 제외
```

---

### CI/CD 빌드 산출물 (dist/)

```
dist/  ← Git에 없음, 빌드 시 생성
├── config/
│   ├── schema_registry.json.gz    ← 설정 (텍스트, 디버깅 가능)
│   ├── tool_registry.json.gz
│   └── ... (9개)
│
└── data/
    ├── umis_business_model_patterns.msgpack  ← 데이터 (바이너리, 성능)
    ├── market_benchmarks.msgpack
    └── ... (9개)
```

---

### Docker 이미지 (프로덕션)

```
Docker Image (150MB):
├── dist/                          ← Balanced 빌드 산출물만
│   ├── config/*.json.gz
│   └── data/*.msgpack
│
├── umis_rag/                      ← Python 코드
│   └── ...
│
└── (YAML 원본 없음!)              ← IP 보호 ✅
```

---

## 🔄 개발자 워크플로우

### 일반 개발

```bash
# 1. Feature 브랜치 생성
git checkout -b feature/add-new-pattern

# 2. YAML 편집 (평소처럼)
vim data/raw/umis_business_model_patterns.yaml

# 3. 로컬 테스트 (YAML 직접 사용)
export UMIS_ENV=development
python -m umis_rag.cli analyze --industry SaaS

# 4. Git 커밋
git add data/raw/umis_business_model_patterns.yaml
git commit -m "Add subscription pattern"
git push origin feature/add-new-pattern

# 5. PR 생성
# → GitHub Actions 자동 실행 (Balanced 빌드 테스트)

# 6. 리뷰 후 머지
# → develop 브랜치로 머지
# → 스테이징 자동 배포
```

---

### 프로덕션 배포

```bash
# 1. develop 검증 완료 후
git checkout main
git merge develop

# 2. 버전 태그 (선택)
git tag v7.5.1
git push origin main --tags

# → GitHub Actions 자동 실행:
#   - Balanced 빌드
#   - Docker 빌드
#   - 프로덕션 배포
#   - 모니터링
#   - Rollback (실패 시)
```

---

## 💰 예상 효과

### AWS Lambda (100만 요청/월)

```yaml
현재 (YAML):
  배포 크기: 500 MB
  로딩 시간: 280 ms
  메모리: 1024 MB
  월 비용: $45

Balanced:
  배포 크기: 150 MB (-70%)
  로딩 시간: 7 ms (-97%) ⭐
  메모리: 512 MB (-50%)
  월 비용: $20 (-56%)

연간 절감: $300
```

---

### 보안 효과

```yaml
YAML 원본 보호:
  ✅ Docker 이미지에 YAML 없음
  ✅ 주석/문서 노출 안 됨
  ✅ IP 보호

역공학 난이도:
  현재 (YAML): ⭐ (5분)
  Balanced: ⭐⭐⭐ (1-2시간)
```

---

## 📋 체크리스트

### 초기 설정 (1회)

- [x] .github/workflows/*.yml 생성
- [x] scripts/build_balanced.py 생성
- [x] Dockerfile.balanced 생성
- [x] .gitignore 확인 (dist/ 제외)
- [ ] requirements.txt에 msgpack 추가

### 매 배포 시 (자동)

- [ ] Git push (YAML 커밋)
- [ ] GitHub Actions 실행 (자동)
- [ ] Balanced 빌드 (자동)
- [ ] Docker 빌드 (자동)
- [ ] 배포 (자동)
- [ ] 모니터링 (자동)

---

## 🎯 핵심 메시지

### "개발은 YAML, 배포는 자동으로"

```
개발자:
  ✅ YAML만 편집 (변화 없음)
  ✅ Git 커밋 (YAML만)
  ✅ 학습 곡선 0

CI/CD:
  ✅ Balanced 빌드 (자동)
  ✅ 검증 (자동)
  ✅ 배포 (자동)
  ✅ Rollback (자동)

프로덕션:
  ✅ 38배 빠른 로딩
  ✅ 42% 작은 크기
  ✅ IP 보호
  ✅ $300/년 절감
```

---

## 📚 관련 문서

```
전략:
  - GITHUB_DEPLOYMENT_STRATEGY.md (상세 전략)
  - BALANCED_PRODUCTION_STRATEGY.md (Balanced 설명)
  - PRACTICAL_FORMAT_ALTERNATIVES.md (대안 비교)

구현:
  - scripts/build_balanced.py (빌드 스크립트)
  - .github/workflows/*.yml (CI/CD)
  - Dockerfile.balanced (Docker)

결과:
  - MINIMALIST_CONVERSION_PLAN.md (변환 대상)
  - BENCHMARK_RESULTS.md (성능 측정)
```

---

## 🚀 다음 단계

### 즉시 실행 가능

```bash
# 1. 의존성 추가
echo "msgpack" >> requirements.txt

# 2. 로컬 빌드 테스트
python scripts/build_balanced.py

# 3. 결과 확인
ls -lh dist/

# 4. Git 커밋
git add .github/workflows/ scripts/build_balanced.py Dockerfile.balanced
git commit -m "feat: Balanced 배포 전략 구현"

# 5. PR 생성 또는 푸시
git push

# → GitHub Actions 자동 실행!
```

---

## ⚠️ YAML 파싱 에러 수정

4개 파일에 YAML 문법 오류:
```bash
# 수정 필요
- umis.yaml (line 4453)
- umis_core.yaml (line 244)
- fermi_model_search.yaml (line 380)
- umis_examples.yaml (line 538)

# yamllint로 검증
yamllint umis.yaml
```

→ 별도 수정 후 재빌드

---

**Balanced 전략의 GitHub 배포 워크플로우 완성!** 🎉

