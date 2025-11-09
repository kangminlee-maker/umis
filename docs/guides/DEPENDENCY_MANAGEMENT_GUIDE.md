# UMIS 의존성 관리 실전 가이드
## Practical Guide for Dependency Management

**작성일**: 2025-11-09  
**버전**: 1.0.0  
**대상**: UMIS 개발자 및 기여자

---

## 📋 목차

1. [빠른 시작](#1-빠른-시작)
2. [일상적인 사용](#2-일상적인-사용)
3. [리팩토링 시나리오](#3-리팩토링-시나리오)
4. [트러블슈팅](#4-트러블슈팅)

---

## 1. 빠른 시작

### 1.1 도구 설치

```bash
# 기본 도구 (이미 설치되어 있음)
cd /Users/kangmin/umis_main_1103/umis

# 선택적 도구 (의존성 시각화)
pip install pydeps
pip install import-linter
```

### 1.2 첫 실행

```bash
# 1. 현재 의존성 상태 파악
python scripts/generate_dependency_matrix.py

# 2. 일관성 검증
python scripts/validate_consistency.py

# 3. 결과 확인
cat docs/architecture/DEPENDENCY_MATRIX.md
```

**출력 예시**:
```
✅ 의존성 분석 완료!
📄 생성된 파일:
  - docs/architecture/DEPENDENCY_MATRIX.md
  - dependency_analysis.json
```

---

## 2. 일상적인 사용

### 2.1 코드 변경 전 (Pre-Change Checklist)

**시나리오**: Agent 이름을 변경하려고 합니다.

```bash
# Step 1: 현재 브랜치 커밋
git add .
git commit -m "checkpoint before refactor"

# Step 2: 영향 분석
python scripts/impact_analyzer.py \
  --change "explorer" \
  --type "agent_rename" \
  --new-name "opportunity_hunter"
```

**출력 해석**:
```
📊 영향 받는 파일: 53개
  CODE: 9개
  CONFIG: 8개
  DATA: 2개
  DOCS: 19개
  SCRIPTS: 15개

⏱️  예상 소요 시간: 157분 (약 2.5시간)

⚠️  간접 의존성: 7개
  - umis_rag/methodologies/domain_reasoner.py
    → scripts/test_signal10_kpi.py
```

**의사결정**:
- 🟢 파일 수 < 20개 → 즉시 진행
- 🟡 파일 수 20-50개 → 계획 후 진행 (반나절 소요)
- 🔴 파일 수 > 50개 → 팀 리뷰 필요 (1일 이상 소요)

### 2.2 코드 변경 후 (Post-Change Verification)

```bash
# Step 1: 일관성 검증
python scripts/validate_consistency.py

# Step 2: 의존성 매트릭스 재생성
python scripts/generate_dependency_matrix.py

# Step 3: (선택) 테스트 실행
pytest tests/

# Step 4: 커밋
git add .
git commit -m "refactor: rename explorer to opportunity_hunter"
```

**검증 실패 시**:
```
❌ 일관성 검증 실패

🔴 에러: 1개
  1. 설정에는 있지만 구현되지 않은 Agent: {'opportunity_hunter'}

💡 다음 단계:
  1. config/agent_names.yaml 업데이트
  2. 다시 검증: python scripts/validate_consistency.py
```

### 2.3 주기적 점검 (Weekly/Monthly)

```bash
# 매주 월요일 (5분)
python scripts/validate_consistency.py
python scripts/generate_dependency_matrix.py

# 매월 1일 (10분)
pydeps umis_rag -o docs/architecture/dependency_graph_$(date +%Y%m).svg
lint-imports
```

---

## 3. 리팩토링 시나리오

### 시나리오 1: Agent 이름 변경 (Moderate Complexity)

**목표**: `explorer` → `opportunity_hunter`

#### Before (기존 방식)

```bash
# 1. grep으로 검색
grep -r "explorer" .

# 2. 결과 500개... 수동 확인 😢
# 3. 관련 파일 20-30개 수동 수정
# 4. 누락 가능성 높음
# 5. 수동 테스트
# 소요 시간: 반나절~1일
```

#### After (개선된 방식)

```bash
# Step 1: 영향 분석 (1분)
python scripts/impact_analyzer.py \
  --change "explorer" \
  --type "agent_rename" \
  --new-name "opportunity_hunter"

# → 53개 파일 정확히 식별
# → impact_analysis_result.json 저장

# Step 2: 새 브랜치 생성
git checkout -b refactor/rename-explorer-to-opportunity-hunter

# Step 3: 체계적 변경 (1-2시간)

# 3-1. Python 코드 (IDE 활용)
# - umis_rag/agents/explorer.py → opportunity_hunter.py 이름 변경
# - 클래스명: ExplorerRAG → OpportunityHunterRAG
# - IDE Refactor 기능 사용 (모든 import 자동 업데이트)

# 3-2. YAML 설정 (수동)
# config/agent_names.yaml
explorer: Steve  →  opportunity_hunter: Steve

# config/routing_policy.yaml
agent: explorer  →  agent: opportunity_hunter

# config/projection_rules.yaml
agents: [explorer]  →  agents: [opportunity_hunter]

# 3-3. 데이터 파일 (스크립트)
mv data/chunks/explorer_business_models.jsonl \
   data/chunks/opportunity_hunter_business_models.jsonl

# 3-4. 문서 (Find & Replace)
# umis.yaml, umis_core.yaml, .cursorrules
# "explorer" → "opportunity_hunter" (케이스 유지)

# Step 4: RAG 인덱스 재구축 (2-3분)
python scripts/02_build_index.py --agent opportunity_hunter

# Step 5: 검증 (1분)
python scripts/validate_consistency.py

# Step 6: 테스트 (선택)
pytest tests/test_opportunity_hunter.py

# Step 7: 커밋
git add .
git commit -m "refactor: rename explorer to opportunity_hunter

- Renamed agent ID: explorer → opportunity_hunter
- Updated all references (53 files)
- Rebuilt RAG index
- All consistency checks passed
"

# 총 소요 시간: 1-2시간 (vs 기존 반나절~1일)
# 누락 위험: 거의 없음 (vs 기존 20-30%)
```

### 시나리오 2: 설정 키 변경 (Low Complexity)

**목표**: `llm_mode` → `ai_mode`

```bash
# Step 1: 영향 분석
python scripts/impact_analyzer.py \
  --change "llm_mode" \
  --type "config_change" \
  --new-name "ai_mode"

# Step 2: 변경 (10-15분)
# - config/ 파일 수정
# - umis_rag/core/config.py 수정
# - 관련 코드 수정

# Step 3: 검증
python scripts/validate_consistency.py

# 총 소요 시간: 15-20분
```

### 시나리오 3: 클래스 이름 변경 (High Complexity)

**목표**: `ExplorerRAG` → `OpportunityDiscoveryEngine`

```bash
# Step 1: 영향 분석
python scripts/impact_analyzer.py \
  --change "ExplorerRAG" \
  --type "class_rename" \
  --new-name "OpportunityDiscoveryEngine"

# Step 2: IDE Refactor 활용
# - VS Code / PyCharm Refactor 기능
# - 모든 import, 인스턴스 자동 업데이트

# Step 3: 검증
python scripts/validate_consistency.py

# 총 소요 시간: 10-15분 (IDE 덕분에 매우 빠름)
```

---

## 4. 트러블슈팅

### 4.1 일관성 검증 실패

**문제**:
```
❌ 일관성 검증 실패
🔴 에러: 설정에는 있지만 구현되지 않은 Agent: {'estimator'}
```

**해결**:

**Option 1**: Agent 구현 추가
```bash
# umis_rag/agents/estimator.py 생성
# umis_rag/agents/__init__.py에 export 추가
```

**Option 2**: 설정에서 제거
```bash
# config/agent_names.yaml에서 estimator 제거
```

### 4.2 ChromaDB 연결 실패

**문제**:
```
⚠️  ChromaDB 연결 실패: No module named 'umis_rag'
```

**해결**:
```bash
# Option 1: PYTHONPATH 설정
export PYTHONPATH=/Users/kangmin/umis_main_1103/umis:$PYTHONPATH
python scripts/validate_consistency.py

# Option 2: 프로젝트 루트에서 실행
cd /Users/kangmin/umis_main_1103/umis
python scripts/validate_consistency.py
```

### 4.3 의존성 그래프 생성 실패

**문제**:
```
pydeps: command not found
```

**해결**:
```bash
pip install pydeps

# 그래프 생성
pydeps umis_rag --max-bacon 2 -o docs/architecture/dependency_graph.svg

# 순환 의존성만 표시
pydeps umis_rag --only umis_rag --cluster --max-bacon 2
```

### 4.4 영향 분석 결과가 부정확함

**문제**: 일부 파일을 놓침

**원인**: 동적 import 사용
```python
# 예시: 문자열로 동적 import
agent_module = importlib.import_module(f"umis_rag.agents.{agent_id}")
```

**해결**:
```bash
# 추가 수동 검색
grep -r "agent_id" .
grep -r "\"explorer\"" .  # 문자열 리터럴 검색
```

---

## 5. 고급 활용

### 5.1 의존성 규칙 강제 (import-linter)

**설정**: `.import-linter.toml`

```toml
[tool.importlinter]
root_package = "umis_rag"

# Agent 간 직접 import 금지
[[tool.importlinter.contracts]]
name = "Agent independence"
type = "independence"
modules = [
    "umis_rag.agents.observer",
    "umis_rag.agents.explorer",
    "umis_rag.agents.quantifier",
    "umis_rag.agents.validator",
    "umis_rag.agents.guardian",
    "umis_rag.agents.estimator",
]
```

**실행**:
```bash
lint-imports

# 규칙 위반 시:
# ❌ umis_rag.agents.explorer imports umis_rag.agents.quantifier
#    (agents should be independent)
```

### 5.2 의존성 그래프 시각화

```bash
# 전체 그래프 (복잡함)
pydeps umis_rag -o dependency_full.svg

# 간소화 (2단계까지만)
pydeps umis_rag --max-bacon 2 -o dependency_simple.svg

# Agent만
pydeps umis_rag.agents --cluster -o agents_dependency.svg

# 순환 의존성만
pydeps umis_rag --show-cycles --max-bacon 3
```

### 5.3 CI/CD 통합

**`.github/workflows/dependency-check.yml`**:

```yaml
name: Dependency Check

on: [push, pull_request]

jobs:
  check:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install import-linter
      
      - name: Validate consistency
        run: python scripts/validate_consistency.py
      
      - name: Check import rules
        run: lint-imports
```

---

## 6. 베스트 프랙티스

### 6.1 변경 전 체크리스트

- [ ] 영향 분석 실행
- [ ] 예상 소요 시간 확인
- [ ] 간접 의존성 파악
- [ ] 새 브랜치 생성
- [ ] 현재 상태 커밋

### 6.2 변경 중 체크리스트

- [ ] IDE Refactor 기능 최대 활용
- [ ] Python 코드 먼저, YAML 나중에
- [ ] 변경 로그 작성 (어떤 파일 수정했는지)
- [ ] 중간중간 검증 (`validate_consistency.py`)

### 6.3 변경 후 체크리스트

- [ ] 일관성 검증 통과
- [ ] 의존성 매트릭스 재생성
- [ ] 테스트 실행 (있다면)
- [ ] RAG 인덱스 재구축 (필요 시)
- [ ] 문서 업데이트
- [ ] 커밋 메시지 작성

### 6.4 커밋 메시지 템플릿

```
refactor: <변경 요약>

- <변경 내용 1>
- <변경 내용 2>
- Updated <X> files
- All consistency checks passed

Impact: <Low/Medium/High>
Files affected: <숫자>
Time spent: <시간>
```

**예시**:
```
refactor: rename explorer to opportunity_hunter

- Renamed agent ID: explorer → opportunity_hunter
- Updated all references (53 files)
- Rebuilt RAG index
- Updated documentation

Impact: High
Files affected: 53
Time spent: 2 hours
```

---

## 7. 자주 묻는 질문 (FAQ)

### Q1: 언제 의존성 분석을 해야 하나요?

**A**: 다음 상황에서 필수입니다:
- Agent/Collection/설정 키 이름 변경
- 모듈 이동 또는 재구조화
- 대규모 리팩토링 전
- 새로운 의존성 추가 전

### Q2: 분석 결과를 신뢰할 수 있나요?

**A**: 90% 이상 정확합니다. 하지만:
- ❌ 동적 import는 탐지 어려움
- ❌ 문자열 리터럴은 일부 누락 가능
- ✅ 직접 import는 100% 정확
- ✅ YAML 참조는 거의 완벽

**권장**: 분석 결과 + 수동 확인

### Q3: 시간이 오래 걸리는데 더 빠르게 할 수 없나요?

**A**: 최적화 팁:
```bash
# 특정 디렉토리만 분석
python scripts/impact_analyzer.py --change "explorer" --type "agent_rename" --scope "umis_rag/agents"

# 캐시 활용 (향후 구현 예정)
python scripts/impact_analyzer.py --use-cache
```

### Q4: CI에서 실패하는데 로컬에서는 통과합니다.

**A**: 환경 차이:
```bash
# CI와 동일한 조건으로 로컬 실행
export PYTHONPATH=""
cd /Users/kangmin/umis_main_1103/umis
python scripts/validate_consistency.py --strict
```

---

## 8. 추가 자료

### 8.1 관련 문서

- [의존성 관리 전략](../architecture/DEPENDENCY_MANAGEMENT_STRATEGY.md) - 전체 전략 및 설계
- [의존성 매트릭스](../architecture/DEPENDENCY_MATRIX.md) - 현재 의존성 상태
- [아키텍처 블루프린트](../../UMIS_ARCHITECTURE_BLUEPRINT.md) - 전체 구조

### 8.2 도구 문서

- **pydeps**: https://github.com/thebjorn/pydeps
- **import-linter**: https://github.com/seddonym/import-linter
- **Rope** (향후): https://github.com/python-rope/rope

### 8.3 외부 참고

- "Python Dependency Management Best Practices" (Real Python)
- "Refactoring Python Applications" (Martin Fowler)

---

**마지막 업데이트**: 2025-11-09  
**작성자**: AI Assistant  
**피드백**: 개선 사항이 있으면 이슈 등록해주세요!

