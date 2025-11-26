# Config 파일 변경점 설계 (v7.11.0)

**날짜:** 2025-11-26  
**Task:** Phase 1.4 - Config 파일 변경점 설계  
**목적:** Phase 3-4 Config를 Stage 2-3 기반으로 리팩터링

---

## 📊 전체 요약

### Config 파일 현황
- **`model_configs.yaml`:** 279줄, Phase 3-4 timeout 및 모델 설정
- **`fermi_model_search.yaml`:** 1,543줄, Phase 4 Fermi 설계 문서
- **`tool_registry.yaml`:** Phase 3-4 언급 (319줄)

---

## 🎯 Config 1: `model_configs.yaml` (최우선)

### 현재 구조 (Lines 1-46)
```yaml
# UMIS Model API Configurations
# Phase 4 Fermi Decomposition 벤치마크 기반 (v7.8.0)

phase_timeouts:
  phase_3:
    default: 45  # Guestimation (6-35초)
    models:
      gpt-4o-mini: 15
      gpt-5.1: 45
      o1-mini: 45
  
  phase_4:
    default: 60  # Fermi Decomposition (11-60초)
    models:
      gpt-4o-mini: 20
      gpt-5.1: 60
      o1-mini: 60
      o1: 90
      o1-pro: 120
      gpt-5-pro: 180

models:
  o1-mini:
    notes: "STEM 최적화, 80% 저렴, Phase 4 기본 모델"
  # ... (기타 모델들)
```

---

### v7.11.0 변경 사항

#### 1. Phase → Stage 리네이밍

**변경 전:**
```yaml
phase_timeouts:
  phase_3:
    default: 45
  phase_4:
    default: 60
```

**변경 후:**
```yaml
stage_timeouts:
  stage_2_generative_prior:  # 구 Phase 3
    default: 45
    legacy_alias: phase_3    # 하위 호환성
    models:
      gpt-4o-mini: 15
      gpt-5.1: 45
      o1-mini: 45
  
  stage_3_fermi:  # 구 Phase 4
    default: 60
    legacy_alias: phase_4    # 하위 호환성
    models:
      gpt-4o-mini: 20
      gpt-5.1: 60
      o1-mini: 60
      o1: 90
      o1-pro: 120
      gpt-5-pro: 180
  
  # 신규 Stage 1, 4는 timeout 불필요
  # Stage 1: Evidence Collection (LLM 사용 안 함)
  # Stage 4: Fusion (계산만, LLM 사용 안 함)
```

---

#### 2. 환경변수 매핑 (하위 호환성)

**코드 변경 필요 (umis_rag/core/model_router.py 등):**
```python
# 환경변수 매핑
LEGACY_ENV_MAPPING = {
    'LLM_MODEL_PHASE3': 'stage_2_generative_prior',
    'LLM_MODEL_PHASE4': 'stage_3_fermi',
    'PHASE3_TIMEOUT': 'STAGE2_TIMEOUT',
    'PHASE4_TIMEOUT': 'STAGE3_TIMEOUT',
}

def get_stage_config(stage_name: str) -> dict:
    """Stage Config 가져오기 (레거시 환경변수 지원)"""
    # 환경변수 확인 (레거시 우선)
    if stage_name == 'stage_2_generative_prior':
        model = os.getenv('LLM_MODEL_PHASE3') or os.getenv('LLM_MODEL_STAGE2')
    elif stage_name == 'stage_3_fermi':
        model = os.getenv('LLM_MODEL_PHASE4') or os.getenv('LLM_MODEL_STAGE3')
    
    return model_configs[stage_name]
```

**결과:** 기존 `.env` 설정 계속 동작 ✅
```bash
# .env (기존 방식, 계속 동작)
LLM_MODEL_PHASE3=gpt-4o-mini  # → Stage 2로 자동 매핑
LLM_MODEL_PHASE4=o1-mini      # → Stage 3으로 자동 매핑

# .env (신규 방식, 권장)
LLM_MODEL_STAGE2=gpt-4o-mini
LLM_MODEL_STAGE3=o1-mini
```

---

#### 3. 주석 및 Notes 업데이트

**변경 전:**
```yaml
models:
  o1-mini:
    notes: "STEM 최적화, 80% 저렴, Phase 4 기본 모델"
```

**변경 후:**
```yaml
models:
  o1-mini:
    notes: "STEM 최적화, 80% 저렴, Stage 3 Fermi 기본 모델 (구 Phase 4)"
  
  gpt-4o-mini:
    notes: "빠르고 저렴, Stage 2 Generative Prior 최적 (구 Phase 3)"
```

---

### 최종 `model_configs.yaml` 구조 (v7.11.0)

```yaml
# UMIS Model API Configurations (v7.11.0)
# 
# Stage 2-3 기반 (4-Stage Fusion Architecture)
#
# 사용법:
#   .env에서 LLM_MODEL_STAGE3=o1-mini 설정하면
#   자동으로 해당 모델의 API 설정 적용
#
# 하위 호환성:
#   LLM_MODEL_PHASE3, LLM_MODEL_PHASE4도 계속 동작

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 기본값
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
defaults:
  api_type: chat
  max_output_tokens: 4096
  temperature: 0.7
  timeout_seconds: 30

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Stage별 Timeout 설정 (v7.11.0)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Stage 2: Generative Prior (구 Phase 3 Guestimation)
# Stage 3: Structural Explanation (구 Phase 4 Fermi, 재귀 제거)
stage_timeouts:
  stage_2_generative_prior:  # 구 Phase 3
    description: "LLM 직접 값 요청 (단일 호출)"
    default: 45
    legacy_alias: phase_3    # LLM_MODEL_PHASE3 지원
    models:
      gpt-4o-mini: 15      # 빠름 (2-6초)
      gpt-4.1-nano: 10     # 매우 빠름
      gpt-5.1: 45          # reasoning
      o1-mini: 45

  stage_3_fermi:  # 구 Phase 4 (재귀 제거)
    description: "구조적 설명 (Fermi 분해, 재귀 없음, max_depth=2)"
    default: 60
    legacy_alias: phase_4    # LLM_MODEL_PHASE4 지원
    models:
      gpt-4o-mini: 20      # 빠름 (5-15초)
      gpt-5.1: 60          # reasoning high
      o1-mini: 60          # reasoning
      o1: 90               # 대형 reasoning
      o1-pro: 120          # Pro 모델 (30-70초)
      gpt-5-pro: 180       # Pro 모델 (73초)
  
  # Stage 1: Evidence Collection (LLM 사용 안 함, timeout 불필요)
  # Stage 4: Fusion & Validation (계산만, LLM 사용 안 함)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 모델별 설정
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
models:
  o1-mini:
    api_type: responses
    max_output_tokens: 16000
    reasoning_effort:
      support: true
      levels: [low, medium, high]
      default: medium
    temperature_support: false
    context_window: 128000
    notes: "STEM 최적화, Stage 3 Fermi 기본 (구 Phase 4)"
  
  gpt-4o-mini:
    api_type: chat
    max_output_tokens: 4096
    temperature: 1.0
    context_window: 128000
    notes: "빠르고 저렴, Stage 2 Generative Prior 최적 (구 Phase 3)"
  
  # ... (기타 모델들)
```

---

## 🎯 Config 2: `fermi_model_search.yaml` (Archive)

### 현재 상황
- **파일:** 1,543줄 대형 파일
- **내용:** Phase 4 Fermi Decomposition 설계 문서
- **상태:** "100% 구현 완료 (v7.7.0)", Phase 4 재귀 로직 설명

### 문제점
1. **레거시 재귀 로직:** v7.11.0에서 재귀 완전 제거
2. **Phase 4 Step 1-4:** 더 이상 사용하지 않음
3. **파일 크기:** 1,543줄 (너무 큼)

### 결정: Archive 이동

**이유:**
- v7.11.0 Stage 3 (Fermi)는 단순화됨
  - 재귀 없음
  - max_depth=2
  - Budget 기반
- 이 파일은 역사적 가치만 있음 (참고용)

**Archive 위치:**
```bash
archive/phase3_4_legacy_v7.10.2/fermi_model_search.yaml
```

**README 작성:**
```markdown
# fermi_model_search.yaml (레거시)

**원본:** config/fermi_model_search.yaml  
**이동일:** 2025-11-26  
**버전:** v7.7.0 (Phase 4 Fermi Decomposition 설계)

## Archive 이유

v7.11.0에서 Fermi 아키텍처 완전 재설계:
- 재귀 완전 제거
- max_depth=2 강제
- Budget 기반 탐색
- 1,543줄 → 단순화

이 파일은 Phase 4 재귀 로직 역사적 기록으로만 유효합니다.

## 신규 아키텍처

v7.11.0 Stage 3 (Fermi):
- `umis_rag/agents/estimator/fermi_estimator.py`
- 재귀 금지 원칙
- PriorEstimator 주입 (의존성 역전)
```

---

## 🎯 Config 3: `tool_registry.yaml` (부분 업데이트)

### Phase 3-4 언급 위치
- Lines 1060-1710: Estimator 섹션 (319줄)

### 변경 방안

**Option 1: 최소 변경 (권장)**
- Estimator 섹션만 수정
- Phase 3-4 → Stage 2-3
- 주석 추가 (구 Phase N)

**Option 2: 전체 재작성**
- umis.yaml Estimator 섹션 참조
- 4-Stage Fusion Architecture 전체 반영
- 시간 소요 큼 (3-4시간)

**결정:** Option 1 (최소 변경)

**수정 범위:**
```yaml
# tool_registry.yaml Lines 1060-1710

# 변경 전
estimator:
  five_phase_architecture:
    phase_3:
      name: Guestimation
    phase_4:
      name: Fermi Decomposition

# 변경 후
estimator:
  four_stage_fusion_architecture:  # v7.11.0
    stage_2_generative_prior:
      name: Generative Prior
      legacy: "구 Phase 3 Guestimation"
    stage_3_fermi:
      name: Structural Explanation (Fermi)
      legacy: "구 Phase 4 Fermi Decomposition (재귀 제거)"
```

---

## 📋 구현 순서

### Step 1: model_configs.yaml 백업
```bash
cp config/model_configs.yaml config/backups/model_configs_$(date +%Y%m%d_%H%M%S).yaml
```

### Step 2: model_configs.yaml 수정
1. `phase_timeouts` → `stage_timeouts`
2. `phase_3` → `stage_2_generative_prior`
3. `phase_4` → `stage_3_fermi`
4. `legacy_alias` 추가
5. Notes 업데이트

### Step 3: 코드 변경 (model_router.py)
```python
# umis_rag/core/model_router.py

LEGACY_ENV_MAPPING = {
    'LLM_MODEL_PHASE3': 'stage_2_generative_prior',
    'LLM_MODEL_PHASE4': 'stage_3_fermi',
}

def get_stage_timeout(stage_name: str, model_name: str) -> int:
    """Stage별 timeout 가져오기 (레거시 지원)"""
    config = yaml.safe_load(open('config/model_configs.yaml'))
    
    stage_config = config['stage_timeouts'].get(stage_name)
    if not stage_config:
        # 레거시 매핑 시도
        for legacy_key, new_key in LEGACY_ENV_MAPPING.items():
            if new_key == stage_name:
                # phase_3 → stage_2 매핑 시도
                legacy_name = f"phase_{stage_name.split('_')[1]}"
                stage_config = config['stage_timeouts'].get(legacy_name)
                break
    
    if stage_config:
        return stage_config['models'].get(model_name, stage_config['default'])
    
    return config['defaults']['timeout_seconds']
```

### Step 4: fermi_model_search.yaml Archive
```bash
mkdir -p archive/phase3_4_legacy_v7.10.2/
mv config/fermi_model_search.yaml archive/phase3_4_legacy_v7.10.2/
echo "# fermi_model_search.yaml moved to archive/" > config/fermi_model_search.yaml.moved
```

### Step 5: tool_registry.yaml 수정
- Estimator 섹션 (Lines 1060-1710) 수정
- Phase 3-4 → Stage 2-3
- Legacy 주석 추가

### Step 6: 테스트
```python
# 환경변수 테스트
import os
os.environ['LLM_MODEL_PHASE3'] = 'gpt-4o-mini'  # 레거시
os.environ['LLM_MODEL_PHASE4'] = 'o1-mini'      # 레거시

from umis_rag.core.model_router import get_stage_timeout

# Stage 2 timeout (구 Phase 3)
timeout = get_stage_timeout('stage_2_generative_prior', 'gpt-4o-mini')
assert timeout == 15

# Stage 3 timeout (구 Phase 4)
timeout = get_stage_timeout('stage_3_fermi', 'o1-mini')
assert timeout == 60
```

---

## 📊 작업 통계

| Config | 변경 범위 | 예상 시간 | 우선순위 |
|--------|----------|----------|---------|
| `model_configs.yaml` | 전체 (279줄) | 1-2시간 | ★★★★★ |
| `fermi_model_search.yaml` | Archive 이동 | 30분 | ★★★☆☆ |
| `tool_registry.yaml` | Estimator 섹션 (319줄) | 1-2시간 | ★★★☆☆ |
| `model_router.py` (코드) | 환경변수 매핑 | 1시간 | ★★★★☆ |
| **총계** | | **3.5-5.5시간** | |

---

## ✅ 성공 기준

### Must Have
- ✅ `model_configs.yaml` Stage 기반 리팩터링
- ✅ 환경변수 하위 호환성 유지
- ✅ 기존 `.env` 설정 계속 동작

### Should Have
- 🎯 `fermi_model_search.yaml` Archive
- 🎯 `tool_registry.yaml` 최소 업데이트
- 🎯 코드 테스트 통과

### Nice to Have
- 🎯 모델별 Notes 업데이트
- 🎯 README 작성

---

## 🚨 리스크

### High Risk
**환경변수 매핑 실패**
- **문제:** 기존 `.env` 설정 동작 안 함
- **대응:** 철저한 테스트, Fallback 로직

### Medium Risk
**Timeout 불일치**
- **문제:** Stage 2-3 timeout이 Phase 3-4와 다름
- **대응:** timeout 값 유지 (45초, 60초)

### Low Risk
**tool_registry.yaml 업데이트 누락**
- **문제:** 문서 불일치
- **영향:** 낮음 (참고용)

---

## 🎯 다음 단계

**Phase 2.1: Phase 3-4 파일 Archive 이동**

---

**작성자:** AI Assistant  
**작성일:** 2025-11-26  
**Task:** Phase 1.4 완료 ✅

**끝.**

