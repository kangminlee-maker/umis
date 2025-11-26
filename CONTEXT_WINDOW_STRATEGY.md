# Context Window 전략 (v7.11.1)

## 📊 Complete vs Task 도구 사용 전략

### 모델별 권장 사항

#### 1️⃣ **128K-200K 모델** (gpt-4o-mini, claude-sonnet-3.5)
```yaml
상황: 가장 일반적인 사용 케이스
문제: Medium 이상 작업 시 컨텍스트 부족
권장: Task 도구 필수 ⭐⭐⭐

사용 전략:
  - 단일 작업: Task 도구 우선
  - 2+ Agent 협업: Task 도구 필수
  - Discovery Sprint: Task 도구 없으면 불가능
  
절약 효과:
  - Light 작업: 37% 절약 (32K → 20K)
  - Medium 작업: 23% 절약 (52K → 40K)
  - Heavy 작업: 12% 절약 (102K → 90K)
```

#### 2️⃣ **272K-400K 모델** (gemini-1.5-pro, gpt-4.1)
```yaml
상황: 엔터프라이즈 사용
문제: Heavy 작업 시 컨텍스트 압박
권장: Task 도구 권장 ⭐⭐

사용 전략:
  - 단일 작업: Complete 가능
  - 3+ Agent 협업: Task 권장
  - Discovery Sprint: Task 사용 시 안정적
  
절약 효과:
  - 4-6% 절약으로 추가 파일 2-3개 로드 가능
  - 복잡한 Excel 생성 시 안전 마진 확보
```

#### 3️⃣ **1M 모델** (claude-opus-3.5)
```yaml
상황: 최고급 모델
문제: 컨텍스트 문제 없음
권장: 선택적 사용 ⭐

사용 전략:
  - Complete 도구로도 충분
  - Task 도구는 API 비용 절감 목적으로만
  
절약 효과:
  - 토큰 절약보다는 명확성/속도 중시
  - Complete 도구의 포괄성이 더 유리
```

---

## 🎯 시나리오별 전략

### Scenario 1: 빠른 단일 작업
```python
예시: "@Explorer, 구독 모델 패턴만 찾아줘"

Complete 도구:
  - explorer:complete (482줄, 3,536 토큰)
  - 총 컨텍스트: ~20K 토큰
  - 모든 모델에서 안전 ✅

Task 도구:
  - explorer:pattern_search (133줄, 627 토큰)
  - 총 컨텍스트: ~16K 토큰
  - 82% 토큰 절약 ⭐

권장: Task 도구 (빠르고 집중적)
```

### Scenario 2: 일반 협업 (2-3 Agents)
```python
예시: "음악 스트리밍 시장 분석"
Agent: Observer → Explorer → Quantifier

Complete 도구:
  - 3개 Agent: 8,165 토큰
  - Medium 작업: ~43K 토큰
  - 200K 모델: 22% 사용 ✅
  - 128K 모델: 34% 사용 🟡

Task 도구:
  - 3개 Agent: 2,449 토큰
  - Medium 작업: ~37K 토큰
  - 200K 모델: 19% 사용 ✅
  - 128K 모델: 29% 사용 ✅

권장:
  - 200K+: Complete 가능
  - 128K: Task 권장
```

### Scenario 3: Discovery Sprint (6 Agents)
```python
예시: "피아노 구독 서비스 시장 (목표 불명확)"
Agent: 전체 6개 병렬

Complete 도구:
  - 6개 Agent: 16,912 토큰
  - Heavy 작업: ~102K 토큰
  - 200K 모델: 51% 사용 🔴
  - 400K 모델: 26% 사용 🟢

Task 도구:
  - 6개 Agent: 5,073 토큰
  - Heavy 작업: ~90K 토큰
  - 200K 모델: 45% 사용 🟡
  - 400K 모델: 23% 사용 🟢

권장:
  - 200K: Task 필수 ⚠️
  - 400K+: Task 권장
```

---

## 🔧 구현 권장사항

### 1. **Dynamic Tool Selection** (자동 선택)

```python
def select_tool_type(
    model_context_window: int,
    num_agents: int,
    work_complexity: str
) -> str:
    """
    모델 컨텍스트와 작업 복잡도에 따라 자동 선택
    """
    # 예상 컨텍스트 사용량 계산
    estimated_usage = calculate_usage(num_agents, work_complexity)
    usage_ratio = estimated_usage / model_context_window
    
    # 128K-200K 모델
    if model_context_window <= 200_000:
        if num_agents >= 2 or work_complexity == 'medium':
            return 'task'
        if num_agents >= 4 or work_complexity == 'heavy':
            return 'task'  # 필수
    
    # 272K-400K 모델
    elif model_context_window <= 400_000:
        if num_agents >= 4 and work_complexity == 'heavy':
            return 'task'  # 권장
    
    # 1M 모델
    else:
        # Complete 기본, 사용자 선택 가능
        return 'complete'
    
    return 'complete'
```

### 2. **Hybrid Approach** (혼합 전략) ⭐ 최적

```python
def hybrid_tool_selection(agents: list, task_type: str):
    """
    Agent와 작업 타입에 따라 Complete/Task 혼합 사용
    """
    tool_map = {}
    
    for agent in agents:
        # 특정 작업만 필요한 경우
        if task_type == 'pattern_search' and agent == 'explorer':
            tool_map[agent] = 'task:explorer:pattern_search'
        
        elif task_type == 'sam_calculation' and agent == 'quantifier':
            tool_map[agent] = 'task:quantifier:sam_4methods'
        
        # 전체 컨텍스트 필요한 경우
        else:
            tool_map[agent] = f'complete:{agent}'
    
    return tool_map

# 예시: SAM 계산만 필요
tools = hybrid_tool_selection(
    agents=['observer', 'quantifier', 'validator'],
    task_type='sam_calculation'
)
# → observer:complete (267줄)
# → quantifier:sam_4methods (256줄) ← Task!
# → validator:complete (444줄)
# 총합: 967줄 vs 1,101줄 (Complete 사용 시)
```

### 3. **User Preference Override**

```yaml
# config/context_strategy.yaml
context_strategy:
  auto_select: true
  
  user_preference:
    default_tool_type: 'auto'  # 'auto', 'complete', 'task'
    
  model_thresholds:
    128k_200k:
      single_agent_light: 'complete'  # 충분히 안전
      multi_agent_medium: 'task'      # 필수
      discovery_sprint: 'task'        # 필수
    
    272k_400k:
      single_agent: 'complete'
      multi_agent: 'complete'
      discovery_sprint_heavy: 'task'  # 권장
    
    1m:
      all: 'complete'  # 항상 Complete
```

---

## 📈 비용 분석

### API 비용 절감 효과

```python
# Claude Sonnet 3.5 (200K) 기준
# Input: $3 / 1M tokens

시나리오: Discovery Sprint (월 100회)

Complete 도구 사용:
  - 평균 토큰: 51,912 / 요청
  - 월 총 토큰: 5,191,200 토큰
  - 월 비용: $15.57

Task 도구 사용:
  - 평균 토큰: 40,073 / 요청
  - 월 총 토큰: 4,007,300 토큰
  - 월 비용: $12.02
  
절약: $3.55/월 (23% 절감) ✅

연간 절약: $42.6
엔터프라이즈 (1,000회/월): $426/년
```

---

## ✅ 최종 권장사항

### **Task 도구 재생성 필수** ⭐⭐⭐

**근거:**
1. **128K-200K 모델 (주요 타겟)**: 실질적 문제 발생
   - Discovery Sprint 51% → 45% (컨텍스트 절약)
   - Multi-agent 협업 시 필수

2. **272K-400K 모델**: Heavy 작업 시 안정성 확보
   - 추가 파일 로드 여유 확보
   - 복잡한 산출물 생성 시 안전 마진

3. **API 비용**: 23% 절감 (엔터프라이즈에서 연간 수백 달러)

4. **사용자 경험**: 빠른 단일 작업 시 응답 속도 향상

### 구현 방법

**Option A: 백업 복원** (빠름, 1시간)
```bash
# 백업 파일에서 Task 도구 추출
python3 scripts/restore_task_tools.py
```

**Option B: 자동 생성** (안정적, 4시간)
```bash
# sync_umis_to_rag.py 확장
python3 scripts/sync_umis_to_rag.py --include-task-tools
```

**Option C: Hybrid** (권장, 2시간)
```bash
# 백업 복원 + 자동 생성 파이프라인 구축
1. 백업에서 Task 도구 추출
2. umis.yaml 기반 자동 업데이트 로직 추가
3. 향후 유지보수 자동화
```

---

## 📝 다음 단계

1. Task 도구 재생성 방법 선택
2. System RAG 재구축
3. `umis_core.yaml` 업데이트 (44개 도구 유지)
4. Dynamic Tool Selection 구현 (선택적)

**어떤 방법으로 진행할까요?**

---

## ✅ 최종 결정 (v7.11.1)

**Decision: Option 1 - Complete 도구만 사용**

### 결정 근거

1. **유지보수 단순성 최우선**
   - 15개 도구 vs 44개 도구 (2.9배 차이)
   - umis.yaml 업데이트 시 관리 복잡도 2.9배 감소

2. **현재 시스템 실제 동작**
   - Task 도구 쿼리 → Complete로 Vector Fallback
   - Task 없어도 시스템 정상 작동
   - 의도적으로 Task 제거한 것으로 추정 (365KB > 113KB)

3. **ROI 분석**
   - 개인/스타트업: ROI 마이너스
   - 기업: ROI 중립~플러스
   - 엔터프라이즈만 명확한 이득

4. **실제 사용 패턴**
   - 모호한 요청: Complete가 필수
   - 복잡한 협업: Complete가 더 효율적
   - 작업 범위 확장 시: Task는 여러 번 RAG 호출 필요

5. **컨텍스트 윈도우 충분**
   - 200K+ 모델 사용 시 Complete로 충분
   - Discovery Sprint (6 Agents): 51% 사용 (안정적)

### 구현 사항

- [x] `umis_core.yaml` 업데이트: 44개 → 15개 도구
- [x] Task 도구 제거 근거 주석 추가
- [x] 대안 옵션 2, 3 주석으로 문서화
- [x] Discovery Sprint 패턴 추가 (200K 모델 권장)

### 대안 옵션 (재고려 가능)

**Option 2: Hybrid 접근**
- 조건: 128K 모델 + 6 Agent Discovery Sprint
- 구현: 특정 시나리오만 Task 도구 선택적 사용
- 적합: 컨텍스트 제약이 실제 문제가 되는 경우

**Option 3: Task 전체 재생성**
- 조건: 엔터프라이즈 규모 (2000+회/월)
- 구현: 백업 복원 또는 자동 생성 로직
- 적합: API 비용 절감이 우선 순위인 경우

### 권장 모델 전략

```yaml
일반 작업:
  모델: claude-sonnet-3.5 (200K)
  Complete 도구: 충분한 컨텍스트
  
Discovery Sprint:
  모델: gemini-1.5-pro (272K) 또는 gpt-4.1 (400K)
  Complete 도구: 안정적 동작
  
예산 최우선:
  모델: gpt-4o-mini (128K)
  전략: 작업 분할 또는 Option 2 고려
```

---

**문서 작성일**: 2025-11-26  
**결정**: Option 1 (Complete만 사용)  
**버전**: v7.11.1
