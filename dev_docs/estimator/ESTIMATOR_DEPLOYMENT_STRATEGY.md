# Estimator Agent 전환 배포 전략

**작성일**: 2025-11-07  
**변경 규모**: 중대 (Breaking Change 포함)  
**위험도**: 중간  
**권장 전략**: 단계적 배포 (Phased Rollout)

---

## 🎯 배포 전략 개요

### 상황 분석

```yaml
현재 상태:
  - v7.3.0: Main 배포 완료 (2025-11-07)
  - 사용자: 거의 없음 (방금 배포)
  - 테스트: 100% 통과
  - 안정성: 높음

변경 규모:
  - Breaking Change: import 경로
  - 폴더 이동: guestimation_v3/ → agents/estimator/
  - agent_view 변경: guestimation → estimator
  - 파일 수정: ~35개

위험 요소:
  ⚠️ Import 경로 변경 (Breaking)
  ⚠️ agent_view 변경 (데이터 호환성)
  ⚠️ 대규모 리팩토링
  ✅ 테스트 커버리지 높음 (26%)
  ✅ 사용자 적음 (방금 배포)
```

---

## 🚀 권장 전략: **3단계 배포 (Feature Branch)**

### 전략 개요

```yaml
Stage 1: Feature Branch (개발 및 검증)
  브랜치: feature/estimator-agent
  기간: 1일
  목표: 완전한 구현 및 테스트
  
Stage 2: Alpha 통합 (통합 테스트)
  브랜치: alpha
  기간: 0.5일
  목표: 전체 시스템 통합 검증

Stage 3: Main 배포 (v7.3.1)
  브랜치: main
  기간: 즉시
  목표: Production 배포

장점:
  ✅ 안전한 격리 (feature branch)
  ✅ 롤백 용이 (alpha로 복귀)
  ✅ 단계적 검증
  ✅ Main 안정성 유지
```

---

## 📋 상세 배포 단계

### **Stage 1: Feature Branch 개발** (1일)

#### Step 1-1: 브랜치 생성 (5분)

```bash
# 1. Alpha에서 feature 브랜치 생성
git checkout alpha
git pull origin alpha
git checkout -b feature/estimator-agent

# 2. 확인
git branch
# * feature/estimator-agent
#   alpha
#   main
```

**이유**: alpha를 건드리지 않고 안전하게 개발

#### Step 1-2: 폴더 구조 변경 (30분)

```bash
# 1. 새 폴더 생성
mkdir -p umis_rag/agents/estimator
mkdir -p umis_rag/agents/estimator/sources

# 2. 파일 git mv (이력 보존)
git mv umis_rag/guestimation_v3/tier1.py umis_rag/agents/estimator/
git mv umis_rag/guestimation_v3/tier2.py umis_rag/agents/estimator/
git mv umis_rag/guestimation_v3/learning_writer.py umis_rag/agents/estimator/
git mv umis_rag/guestimation_v3/source_collector.py umis_rag/agents/estimator/
git mv umis_rag/guestimation_v3/judgment.py umis_rag/agents/estimator/
git mv umis_rag/guestimation_v3/models.py umis_rag/agents/estimator/
git mv umis_rag/guestimation_v3/rag_searcher.py umis_rag/agents/estimator/
git mv umis_rag/guestimation_v3/sources/* umis_rag/agents/estimator/sources/

# 3. guestimation_v3 폴더 삭제
git rm -r umis_rag/guestimation_v3/

# 4. 커밋
git commit -m "refactor: 폴더 이동 guestimation_v3 → agents/estimator"
```

**검증**:
- ✅ git log --follow 로 이력 보존 확인
- ✅ 모든 파일 이동 확인

#### Step 1-3: EstimatorRAG 통합 클래스 작성 (1시간)

```python
# umis_rag/agents/estimator/estimator.py (신규)

"""
Estimator (Fermi) RAG Agent

6번째 Agent - 값 추정 및 지능적 판단 전문가
"""

from typing import Optional, Dict, Any
from pathlib import Path

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

from umis_rag.core.config import settings
from umis_rag.utils.logger import logger

from .tier1 import Tier1FastPath
from .tier2 import Tier2JudgmentPath
from .learning_writer import LearningWriter
from .models import Context, EstimationResult


class EstimatorRAG:
    """
    Estimator (Fermi) RAG Agent
    
    역할:
    -----
    - 값 추정 및 지능적 판단
    - 11개 Source 통합 (Physical, Soft, Value)
    - 학습하는 시스템 (사용할수록 6-16배 빨라짐)
    
    3-Tier 아키텍처:
    ---------------
    - Tier 1: Built-in + 학습 규칙 (<0.5초)
    - Tier 2: 11개 Source 수집 + 종합 판단 (3-8초)
    - Tier 3: Fermi Decomposition (미래)
    
    협업:
    -----
    - Observer: 비율 추정
    - Explorer: 시장 크기 감 잡기
    - Quantifier: 데이터 부족 시
    - Validator: 추정치 검증
    
    Usage:
        >>> estimator = EstimatorRAG()
        >>> result = estimator.estimate("B2B SaaS Churn Rate는?")
        >>> print(f"{result.value} (Tier {result.tier})")
    """
    
    def __init__(self):
        """초기화"""
        logger.info("[Estimator] Fermi Agent 초기화")
        
        # Tier 1: Fast Path
        self.tier1 = Tier1FastPath()
        logger.info("  ✅ Tier 1 (Built-in + 학습)")
        
        # Tier 2: Judgment Path (Lazy)
        self.tier2 = None
        self.learning_writer = None
        
        # Tier 3: Fermi (미래)
        self.tier3 = None
        
        # RAG Collections (Lazy)
        self.canonical_store = None
        self.projected_store = None
        
        logger.info("  ✅ Estimator Agent 준비 완료")
    
    def estimate(
        self,
        question: str,
        context: Optional[Context] = None,
        domain: Optional[str] = None,
        region: Optional[str] = None,
        time_period: Optional[str] = None
    ) -> Optional[EstimationResult]:
        """
        통합 추정 메서드
        
        자동으로 Tier 1 → 2 → 3 시도
        """
        # Context 생성
        if context is None:
            context = Context(
                domain=domain or "General",
                region=region,
                time_period=time_period or "2024"
            )
        
        logger.info(f"[Estimator] 추정: {question}")
        
        # Tier 1 시도
        result = self.tier1.estimate(question, context)
        if result:
            logger.info(f"  ⚡ Tier 1: {result.value} ({result.execution_time:.2f}초)")
            return result
        
        # Tier 2 실행
        self._ensure_tier2()
        result = self.tier2.estimate(question, context)
        
        if result:
            logger.info(f"  🧠 Tier 2: {result.value} ({result.execution_time:.2f}초)")
            return result
        
        # Tier 3 (미래)
        
        logger.warning("  ❌ 추정 실패")
        return None
    
    def _ensure_tier2(self):
        """Tier 2 Lazy 초기화"""
        if self.tier2 is None:
            # Learning Writer
            if self.learning_writer is None:
                # Canonical Collection 로드 (Lazy)
                # TODO: 실제 ChromaDB 연결
                pass
            
            self.tier2 = Tier2JudgmentPath(
                learning_writer=self.learning_writer
            )
            logger.info("  ✅ Tier 2 초기화")

# 싱글톤
_estimator_rag_instance = None

def get_estimator_rag() -> EstimatorRAG:
    """Estimator RAG 싱글톤 인스턴스"""
    global _estimator_rag_instance
    if _estimator_rag_instance is None:
        _estimator_rag_instance = EstimatorRAG()
    return _estimator_rag_instance
```

**커밋**: `feat: EstimatorRAG 통합 클래스 추가`

**검증**:
- ✅ EstimatorRAG 클래스 완성
- ✅ Tier 1→2 자동 전환
- ✅ 싱글톤 패턴

#### Step 1-4: agent_view 일괄 변경 (1시간)

```bash
# 1. learning_writer.py
sed -i '' "s/'agent_view': 'guestimation'/'agent_view': 'estimator'/g" umis_rag/agents/estimator/learning_writer.py

# 2. rag_searcher.py
sed -i '' 's/agent_view="guestimation"/agent_view="estimator"/g' umis_rag/agents/estimator/rag_searcher.py
sed -i '' 's/guestimation_/estimator_/g' umis_rag/agents/estimator/rag_searcher.py

# 3. projection_rules.yaml
# 수동 편집 (신중하게)

# 4. 검증
grep -r "guestimation" umis_rag/agents/estimator/ --exclude-dir=__pycache__
# → 의도적 유지만 남아야 함
```

**커밋**: `refactor: agent_view "guestimation" → "estimator"`

**검증**:
- ✅ agent_view 모두 변경
- ✅ metadata 필드명 변경 (19개)
- ✅ grep 검증

#### Step 1-5: 테스트 실행 (30분)

```bash
# Feature branch에서 모든 테스트 실행
python3 scripts/test_learning_writer.py
python3 scripts/test_learning_e2e.py
python3 scripts/test_tier1_guestimation.py  # import 경로 수정 필요
python3 scripts/test_tier2_guestimation.py  # import 경로 수정 필요
python3 scripts/test_estimator_agent.py  # 신규

# 모두 통과 확인
```

**검증**:
- ✅ 모든 테스트 100% 통과
- ✅ Import 오류 없음

#### Step 1-6: Feature Branch 커밋 (10분)

```bash
# 모든 변경사항 커밋
git add -A
git commit -m "feat: Estimator (Fermi) Agent 전환 완료 (v7.3.1)

- 폴더 이동: guestimation_v3 → agents/estimator
- EstimatorRAG 통합 클래스
- agent_view: guestimation → estimator
- Agent 등록: estimator (Fermi)
- 6-Agent 시스템 완성

Breaking Change:
- import 경로 변경
- Migration Guide 포함

테스트: 100% 통과"

# Feature branch push
git push origin feature/estimator-agent
```

---

### **Stage 2: Alpha 통합** (0.5일)

#### Step 2-1: Alpha에 Merge (10분)

```bash
# 1. Alpha로 전환
git checkout alpha
git pull origin alpha

# 2. Feature branch merge
git merge feature/estimator-agent --no-ff

# 충돌 해결 (있다면)
# 일반적으로 충돌 없음 (새 기능)

# 3. Alpha push
git push origin alpha
```

**검증**:
- ✅ Merge 성공
- ✅ 충돌 없음 또는 해결

#### Step 2-2: Alpha 통합 테스트 (1-2시간)

```bash
# Alpha 브랜치에서 전체 테스트

# 1. Import 검증
python3 -c "
from umis_rag.agents.estimator import EstimatorRAG
from umis_rag.agents.quantifier import QuantifierRAG
print('✅ Import 성공')
"

# 2. 기능 테스트
python3 scripts/test_estimator_agent.py
python3 scripts/test_quantifier_v3.py  # Quantifier 통합

# 3. E2E 테스트
python3 scripts/test_learning_e2e.py

# 4. 전체 Agent 테스트
python3 scripts/test_explorer_patterns.py
python3 scripts/test_agent_rag.py

# 모두 통과 확인!
```

**검증**:
- ✅ 모든 테스트 통과
- ✅ Agent 간 협업 정상
- ✅ 성능 저하 없음

#### Step 2-3: Alpha 안정화 (필요 시)

```bash
# 문제 발견 시
git commit -m "fix: [문제 설명]"
git push origin alpha

# 재테스트
# 완전히 안정화될 때까지 반복
```

**기준**:
- ✅ 모든 테스트 100% 통과
- ✅ Import 무결성
- ✅ 성능 기준 충족

---

### **Stage 3: Main 배포** (v7.3.1)

#### Step 3-1: Main Merge 준비 (10분)

```bash
# 1. Main 전환 및 업데이트
git checkout main
git pull origin main

# 2. Main 상태 확인
git log -1
# v7.3.0이어야 함

# 3. Alpha merge (dry-run)
git merge alpha --no-commit --no-ff

# 충돌 확인
git status
```

**검증**:
- ✅ Main 최신 상태
- ✅ 충돌 확인 (일반적으로 없음)

#### Step 3-2: dev_docs 제거 (Alpha 변경사항) (10분)

```bash
# Main에서 dev_docs, archive 제거
git rm -r dev_docs/ archive/

# Feature branch 문서는 유지
# (이미 dev_docs/ESTIMATOR_AGENT_DESIGN.md에 있음)

# 커밋
git commit -m "release: v7.3.1 - Estimator (Fermi) Agent

6-Agent 시스템 완성:
- Estimator (Fermi) Agent 추가
- 아키텍처 일관성 (모든 Agent가 agents/)
- 협업 파트너 역할

Breaking Change:
- import 경로 변경
- Migration Guide: docs/release_notes/RELEASE_NOTES_v7.3.1.md

Status: Production Ready"
```

#### Step 3-3: Main Push (5분)

```bash
# Main에 push
git push origin main

# Tag 생성 (선택)
git tag v7.3.1
git push origin v7.3.1
```

---

## 🛡️ 안전 장치 (Safety Nets)

### 1. 롤백 전략

```yaml
Stage 1 문제 (Feature):
  조치: Feature branch 수정
  영향: 없음 (격리됨)
  비용: 낮음

Stage 2 문제 (Alpha):
  조치: Alpha를 이전 커밋으로 revert
  영향: Alpha 사용자만 (내부)
  비용: 낮음
  
  명령:
    git checkout alpha
    git revert HEAD  # 또는
    git reset --hard <이전 커밋>
    git push -f origin alpha

Stage 3 문제 (Main):
  조치: Main revert 또는 hotfix
  영향: 외부 사용자
  비용: 높음
  
  예방: Stage 1-2에서 철저히 검증!
```

### 2. 하위 호환성 유지 (선택)

```yaml
옵션: 과도기 하위 호환 (v7.3.1 → v7.4.0)

방법:
  # umis_rag/guestimation_v3/__init__.py (Wrapper 생성)
  
  import warnings
  from umis_rag.agents.estimator import EstimatorRAG
  
  def deprecated_warning():
      warnings.warn(
          "guestimation_v3 is deprecated. Use umis_rag.agents.estimator instead.",
          DeprecationWarning,
          stacklevel=2
      )
  
  class Tier1FastPath:
      def __init__(self):
          deprecated_warning()
          from umis_rag.agents.estimator import Tier1FastPath as T1
          self._impl = T1()
      
      def estimate(self, *args, **kwargs):
          return self._impl.estimate(*args, **kwargs)

장점:
  ✅ 기존 코드 즉시 동작
  ✅ 경고 메시지로 migration 유도
  ✅ 충분한 전환 시간

단점:
  ⚠️ 코드 복잡도 증가
  ⚠️ 유지보수 부담
  ⚠️ v7.4.0에서 완전 제거 필요

권장:
  현재는 Skip (사용자 거의 없음)
  필요 시 추가 가능
```

### 3. 단계별 검증 게이트

```yaml
Stage 1 → Stage 2:
  게이트:
    ✅ 모든 테스트 100% 통과
    ✅ Import 무결성 검증
    ✅ 성능 기준 충족 (Tier 1 <0.5초, Tier 2 <8초)
  
  통과 못하면: Stage 1 재작업

Stage 2 → Stage 3:
  게이트:
    ✅ Alpha 통합 테스트 100%
    ✅ Agent 간 협업 검증
    ✅ 문서 완전성
    ✅ 24시간 Alpha 안정화 (선택)
  
  통과 못하면: Alpha 수정 또는 Stage 1 재작업
```

---

## 🔍 테스트 전략

### 1. Unit 테스트 (각 단계마다)

```python
테스트 목록:
  1. test_estimator_agent.py (신규)
     - EstimatorRAG 직접 호출
     - Tier 1/2 전환
     - 사용자 기여
  
  2. test_tier1_estimator.py (이름 변경)
     - Built-in 규칙
     - RAG 검색
  
  3. test_tier2_estimator.py (이름 변경)
     - Source 수집
     - 판단 전략
  
  4. test_learning_writer.py (경로 수정)
     - 학습 로직
     - Confidence 유연화
  
  5. test_learning_e2e.py (경로 수정)
     - E2E 플로우
     - Projection 검증

통과 기준: 100% (하나라도 실패 시 진행 중단)
```

### 2. 통합 테스트 (Stage 2)

```python
테스트 시나리오:
  1. Estimator 단독 실행
     estimator = EstimatorRAG()
     result = estimator.estimate(...)
  
  2. Quantifier 협업
     quantifier = QuantifierRAG()
     result = quantifier.estimate(...)  # 내부에서 Estimator 호출
  
  3. Agent 간 협업
     observer → estimator (비율 추정)
     explorer → estimator (시장 크기)
  
  4. 학습 시스템
     첫 실행 → 학습 → 재실행 (빠름) 검증

통과 기준: 모든 시나리오 성공
```

### 3. 성능 테스트

```yaml
기준:
  - Tier 1: <0.5초 ✅
  - Tier 2: <8초 ✅
  - 학습 저장: <0.1초 ✅
  - 재실행 개선: 6-16배 ✅

회귀 테스트:
  - v7.3.0 성능과 비교
  - 저하 없음 확인
```

---

## 📊 위험 관리

### 고위험 항목

```yaml
1. agent_view 변경:
   위험: projected_index 불일치
   완화: 재구축 또는 하위 호환
   검증: RAG 검색 테스트

2. Import Breaking Change:
   위험: 기존 코드 깨짐
   완화: Migration Guide
   검증: 모든 테스트 경로 변경

3. 대규모 리팩토링:
   위험: 예상치 못한 버그
   완화: 단계적 배포, 철저한 테스트
   검증: 100% 테스트 통과
```

### 중위험 항목

```yaml
1. Quantifier 통합 변경:
   위험: Quantifier 기능 영향
   완화: 기존 메서드 유지, 신규 추가
   검증: test_quantifier_v3.py

2. 문서 업데이트:
   위험: 불일치, 오래된 정보
   완화: 체계적 업데이트 (6개 문서)
   검증: 리뷰
```

### 저위험 항목

```yaml
1. 폴더 이동:
   위험: 낮음 (git mv로 이력 보존)
   검증: git log --follow

2. 클래스 추가:
   위험: 낮음 (기존 기능 유지)
   검증: 테스트
```

---

## 🎯 권장 배포 전략 (최종)

### **전략: Phased Rollout with Feature Branch**

```yaml
타임라인:
  Day 1 Morning (2시간):
    - Feature branch 생성
    - 폴더 구조 변경
    - EstimatorRAG 클래스
    - agent_view 변경
    
  Day 1 Afternoon (2시간):
    - 테스트 업데이트
    - 모든 테스트 통과
    - Feature branch 완성
  
  Day 2 Morning (1시간):
    - Alpha merge
    - 통합 테스트
    - 안정화
  
  Day 2 Afternoon (30분):
    - Main merge
    - dev_docs/archive 제거
    - v7.3.1 배포
    
  총: 1.5일

브랜치 전략:
  feature/estimator-agent → alpha → main
  
  장점:
    ✅ 안전한 격리
    ✅ 단계적 검증
    ✅ 롤백 용이
    ✅ Main 안정성 유지

게이트:
  ✅ Feature → Alpha: 모든 테스트 100%
  ✅ Alpha → Main: 통합 테스트 + 24시간 안정화 (선택)
```

### 대안 전략

#### **전략 B: Direct Alpha (빠름, 약간 위험)**

```yaml
타임라인: 0.5-1일

방법:
  1. Alpha에서 직접 작업
  2. 작은 커밋들 (10개)
  3. 각 커밋마다 테스트
  4. 완료 후 Main merge

장점:
  ✅ 빠름 (브랜치 관리 없음)
  ✅ 간단함

단점:
  ⚠️ Alpha 불안정 기간 존재
  ⚠️ 롤백 복잡 (여러 커밋 revert)

권장: 작업 자신 있으면 OK
```

#### **전략 C: Version Branch (v7.3.1) (가장 안전)**

```yaml
타임라인: 2일

방법:
  1. v7.3.1 브랜치 생성 (release branch)
  2. 모든 작업 완료
  3. 철저한 테스트 (며칠)
  4. Alpha merge
  5. Main merge

장점:
  ✅ 매우 안전
  ✅ 명확한 버전 관리
  ✅ 병렬 개발 가능

단점:
  ⚠️ 느림
  ⚠️ 브랜치 관리 복잡

권장: 대규모 팀이나 중요한 변경
```

---

## 💡 최종 권장

### **전략: Phased Rollout (Feature Branch)** ⭐

**이유**:

```yaml
1. 적절한 안전성:
   ✅ Feature branch 격리
   ✅ Alpha 통합 테스트
   ✅ Main 안정성 유지

2. 적절한 속도:
   ✅ 1.5일 (빠름)
   ✅ 과도한 브랜치 관리 없음

3. 롤백 용이:
   ✅ Feature branch 폐기 가능
   ✅ Alpha revert 간단
   ✅ Main 영향 최소

4. 현재 상황 적합:
   ✅ v7.3.0 방금 배포 (사용자 적음)
   ✅ Breaking Change 있음 (신중 필요)
   ✅ 대규모 리팩토링 (검증 필요)
```

---

## 📋 체크리스트 (실행 전 확인)

### 사전 준비

```yaml
✅ v7.3.0 안정성 확인
  - Main 브랜치 정상
  - 알려진 버그 없음
  - 테스트 100% 통과

✅ 백업
  - Alpha 브랜치 최신 상태 확인
  - 로컬 백업 (선택)

✅ 작업 시간 확보
  - 연속 3-4시간 (Day 1)
  - 검증 1시간 (Day 2)

✅ 문서 준비
  - ESTIMATOR_AGENT_DESIGN.md 리뷰
  - 작업 단계 숙지
```

### 각 Stage 게이트

```yaml
Feature Branch → Alpha:
  ✅ 모든 테스트 100% 통과
  ✅ Import 무결성
  ✅ agent_view 완전 변경
  ✅ 문서 업데이트 (6개)

Alpha → Main:
  ✅ 통합 테스트 통과
  ✅ Agent 협업 검증
  ✅ 성능 기준 충족
  ✅ Release Notes 완성

Main Push 후:
  ✅ GitHub 확인
  ✅ Main 브랜치 정상
  ✅ CI/CD 통과 (있다면)
```

---

## 🎊 최종 추천 전략

```yaml
전략: Phased Rollout (Feature Branch)

단계:
  1. feature/estimator-agent 생성 ✅
  2. 모든 작업 완료 (3-4시간)
  3. 테스트 100% 통과
  4. Alpha merge
  5. 통합 테스트 (1시간)
  6. Main merge + v7.3.1 배포

타임라인:
  Day 1: Feature branch 완성
  Day 2: Alpha 통합 → Main 배포

안전 장치:
  - Feature branch 격리
  - 단계적 검증
  - 롤백 용이

이유:
  ✅ 안전 + 속도 균형
  ✅ 현재 상황 최적
  ✅ Breaking Change 대응 적절
```

---

**설계 완료!** ✅

**문서 위치**: `dev_docs/ESTIMATOR_AGENT_DESIGN.md`

**다음**: "진행" 말씀하시면 Feature Branch 생성부터 시작하겠습니다! 🚀

진행하시겠습니까?
