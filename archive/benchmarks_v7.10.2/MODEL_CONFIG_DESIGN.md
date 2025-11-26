# 모델별 API 최적화 구조 설계 - 대안 분석

**Version:** v1.0  
**Date:** 2025-11-23  
**Context:** Estimator Phase 4 모델별 API 설정 구조화

---

## 📋 목차

1. [현재 구조 분석](#1-현재-구조-분석)
2. [핵심 설계 질문](#2-핵심-설계-질문)
3. [대안 비교](#3-대안-비교)
4. [추천 솔루션](#4-추천-솔루션)
5. [구현 가이드](#5-구현-가이드)
6. [마이그레이션 계획](#6-마이그레이션-계획)

---

## 1. 현재 구조 분석

### 1.1 기존 시스템

**현재 구조 (v7.7.0):**
```
.env (모델 선택)
  ↓
umis_rag/core/config.py (Settings)
  ↓
umis_rag/core/model_router.py (Phase별 모델 선택)
  ↓
umis_rag/agents/estimator/phase4_fermi.py (LLM 호출)
```

**현재 설정 방식:**
```python
# .env
LLM_MODEL_PHASE4=o1-mini
USE_PHASE_BASED_ROUTING=true

# umis_rag/core/config.py
llm_model_phase4: str = Field(default="o1-mini")
use_phase_based_routing: bool = Field(default=True)

# umis_rag/core/model_router.py
def select_model(self, phase: PhaseType) -> str:
    if phase == 4:
        return settings.llm_model_phase4  # "o1-mini"
```

**Phase 4에서 사용:**
```python
# umis_rag/agents/estimator/phase4_fermi.py
from umis_rag.core.model_router import select_model

model_name = select_model(context)  # Phase 기반 자동 선택
response = self._call_llm(prompt, model_name)  # 단순 호출
```

### 1.2 벤치마크 시스템

**벤치마크 구조:**
```python
# benchmarks/estimator/phase4/common.py

MODEL_API_CONFIGS = {
    'o1-mini': {
        'api_type': 'responses',
        'reasoning_effort_support': True,
        'reasoning_effort_levels': ['low', 'medium', 'high'],
        'max_output_tokens': 16000,
        'notes': 'STEM 최적화, 80% 저렴'
    },
    'gpt-5.1': {
        'api_type': 'responses',
        'reasoning_effort_support': True,
        'reasoning_effort_levels': ['low', 'medium', 'high'],
        'max_output_tokens': 16000,
        'notes': 'Advanced reasoning, JSON 형식 약함'
    },
    # ... 15개 모델
}

def get_model_config(model_name: str) -> dict:
    return MODEL_API_CONFIGS.get(model_name, DEFAULT_CONFIG)

def build_api_params(model_name: str, prompt: str, reasoning_effort='medium') -> dict:
    config = get_model_config(model_name)
    # config에 따라 API 파라미터 구성
    if config['api_type'] == 'responses':
        return {
            'model': model_name,
            'input': prompt,
            'reasoning': {'effort': reasoning_effort},
            'max_output_tokens': config['max_output_tokens']
        }
```

### 1.3 문제점

**현재 시스템의 한계:**
1. **모델별 최적화 부족**: Phase 4에서 모델 이름만 받아서 단순 호출
2. **API 파라미터 하드코딩**: `reasoning_effort`, `max_output_tokens` 등이 코드에 박혀있음
3. **모델 변경 시 수동 조정**: .env에서 모델 바꾸면 API 파라미터도 수동으로 맞춰야 함
4. **중복 관리**: 벤치마크와 실제 시스템에서 각각 모델 설정 관리

---

## 2. 핵심 설계 질문

### 2.1 질문 목록

**Q1: 모델 설정을 어디에 둘 것인가?**
- A안: `.env` 파일 (단순, 사용자 친화적)
- B안: `config.py` (중앙 집중, 타입 안전)
- C안: `model_configs.py` (전용 모듈, 확장성)
- D안: YAML 파일 (설정 파일, 버전 관리)

**Q2: 누가 모델 설정을 적용할 것인가?**
- A안: Phase 4가 직접 읽어서 적용
- B안: ModelRouter가 설정까지 포함하여 반환
- C안: 별도 ModelConfigManager 생성

**Q3: 설정 변경 시 어떻게 반영할 것인가?**
- A안: 재시작 필요 (정적 로딩)
- B안: 실시간 리로딩 (동적 로딩)
- C안: 하이브리드 (캐싱 + 선택적 리로딩)

**Q4: 벤치마크와 실제 시스템 설정을 어떻게 통합할 것인가?**
- A안: 벤치마크 설정을 실제 시스템으로 이동
- B안: 공통 모듈 생성 (양쪽에서 import)
- C안: 설정 파일로 통합 (YAML/JSON)

---

## 3. 대안 비교

### 3.1 대안 1: 최소 변경 (Phase 4 직접 읽기)

**구조:**
```
.env (모델 이름만)
  ↓
config.py (모델 이름 로딩)
  ↓
model_router.py (모델 이름 선택)
  ↓
phase4_fermi.py (모델 설정 직접 관리) ← 🆕 MODEL_API_CONFIGS 포함
```

**장점:**
- ✅ 구현 간단 (2시간)
- ✅ 기존 구조 최소 변경
- ✅ Phase 4에서 완전한 제어

**단점:**
- ❌ Phase 4에만 적용 (다른 Phase는 별도 작업)
- ❌ 설정 중복 (벤치마크 vs 실제)
- ❌ 확장성 낮음

**코드 예시:**
```python
# umis_rag/agents/estimator/phase4_fermi.py

MODEL_API_CONFIGS = {
    'o1-mini': {...},
    'gpt-5.1': {...},
    # ...
}

class Phase4FermiDecomposition:
    def _call_llm(self, prompt: str, model_name: str) -> str:
        config = MODEL_API_CONFIGS.get(model_name, DEFAULT_CONFIG)
        
        # config 기반 API 호출
        if config['api_type'] == 'responses':
            params = {
                'model': model_name,
                'input': prompt,
                'reasoning': {'effort': 'medium'},
                'max_output_tokens': config['max_output_tokens']
            }
            response = self.client.responses.create(**params)
```

**평가:**
- 적합성: ⭐⭐ (단기 해결책)
- 확장성: ⭐ (낮음)
- 유지보수: ⭐⭐ (보통)

---

### 3.2 대안 2: ModelRouter 확장 (설정 포함 반환) ⭐ 추천

**구조:**
```
config/model_configs.yaml (모델별 API 설정) 🆕
  ↓
umis_rag/core/model_configs.py (설정 로딩) 🆕
  ↓
umis_rag/core/model_router.py (모델 + 설정 반환) 🔧
  ↓
umis_rag/agents/estimator/phase4_fermi.py (설정 사용) 🔧
```

**장점:**
- ✅ 중앙 집중 관리
- ✅ 모든 Phase에 적용 가능
- ✅ 벤치마크와 설정 통합 가능
- ✅ YAML로 버전 관리 용이
- ✅ 확장성 높음

**단점:**
- ❌ 구현 복잡 (4-6시간)
- ❌ 새로운 모듈 추가
- ❌ 기존 코드 수정 필요

**코드 예시:**

**1. 설정 파일:**
```yaml
# config/model_configs.yaml

models:
  o1-mini:
    api_type: responses
    reasoning_effort:
      support: true
      levels: [low, medium, high]
      default: medium
    max_output_tokens: 16000
    temperature_support: false
    notes: "STEM 최적화, 80% 저렴"
  
  gpt-5.1:
    api_type: responses
    reasoning_effort:
      support: true
      levels: [low, medium, high]
      default: high
    max_output_tokens: 16000
    temperature_support: false
    notes: "Advanced reasoning, JSON 형식 약함"
  
  gpt-4.1-nano:
    api_type: chat
    reasoning_effort:
      support: false
    max_output_tokens: 4096
    temperature_support: true
    temperature_default: 0.7
    notes: "Phase 0-2 최적화"

defaults:
  api_type: chat
  max_output_tokens: 4096
  temperature: 0.7
```

**2. 설정 로더:**
```python
# umis_rag/core/model_configs.py

from typing import Dict, Any, Optional
from pathlib import Path
import yaml
from dataclasses import dataclass

@dataclass
class ModelConfig:
    """모델별 API 설정"""
    model_name: str
    api_type: str  # 'responses' or 'chat'
    reasoning_effort_support: bool
    reasoning_effort_levels: list[str]
    reasoning_effort_default: str
    max_output_tokens: int
    temperature_support: bool
    temperature_default: float
    notes: str
    
    def build_api_params(
        self, 
        prompt: str, 
        reasoning_effort: Optional[str] = None,
        temperature: Optional[float] = None
    ) -> Dict[str, Any]:
        """API 파라미터 구성"""
        
        if self.api_type == 'responses':
            params = {
                'model': self.model_name,
                'input': prompt,
                'max_output_tokens': self.max_output_tokens
            }
            
            # reasoning_effort 적용
            if self.reasoning_effort_support:
                effort = reasoning_effort or self.reasoning_effort_default
                if effort in self.reasoning_effort_levels:
                    params['reasoning'] = {'effort': effort}
            
            return params
        
        else:  # chat
            params = {
                'model': self.model_name,
                'messages': [{'role': 'user', 'content': prompt}],
                'max_tokens': self.max_output_tokens
            }
            
            # temperature 적용
            if self.temperature_support:
                temp = temperature or self.temperature_default
                params['temperature'] = temp
            
            return params


class ModelConfigManager:
    """모델 설정 관리자"""
    
    _instance = None
    _configs: Dict[str, ModelConfig] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_configs()
        return cls._instance
    
    def _load_configs(self):
        """YAML에서 설정 로드"""
        config_path = Path(__file__).parent.parent.parent / "config" / "model_configs.yaml"
        
        with open(config_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        defaults = data.get('defaults', {})
        
        for model_name, config in data.get('models', {}).items():
            self._configs[model_name] = ModelConfig(
                model_name=model_name,
                api_type=config.get('api_type', defaults.get('api_type', 'chat')),
                reasoning_effort_support=config.get('reasoning_effort', {}).get('support', False),
                reasoning_effort_levels=config.get('reasoning_effort', {}).get('levels', []),
                reasoning_effort_default=config.get('reasoning_effort', {}).get('default', 'medium'),
                max_output_tokens=config.get('max_output_tokens', defaults.get('max_output_tokens', 4096)),
                temperature_support=config.get('temperature_support', defaults.get('temperature_support', True)),
                temperature_default=config.get('temperature_default', defaults.get('temperature', 0.7)),
                notes=config.get('notes', '')
            )
    
    def get_config(self, model_name: str) -> ModelConfig:
        """모델 설정 조회"""
        return self._configs.get(model_name, self._get_default_config(model_name))
    
    def _get_default_config(self, model_name: str) -> ModelConfig:
        """기본 설정 반환"""
        return ModelConfig(
            model_name=model_name,
            api_type='chat',
            reasoning_effort_support=False,
            reasoning_effort_levels=[],
            reasoning_effort_default='medium',
            max_output_tokens=4096,
            temperature_support=True,
            temperature_default=0.7,
            notes='Default config'
        )
    
    def list_models(self) -> list[str]:
        """지원 모델 목록"""
        return list(self._configs.keys())


# Singleton instance
model_config_manager = ModelConfigManager()
```

**3. ModelRouter 확장:**
```python
# umis_rag/core/model_router.py

from umis_rag.core.model_configs import model_config_manager, ModelConfig
from typing import Tuple

class ModelRouter:
    
    def select_model_with_config(self, phase: PhaseType) -> Tuple[str, ModelConfig]:
        """
        Phase에 맞는 최적 모델과 설정 반환 (v7.8.0)
        
        Returns:
            (model_name, model_config)
        """
        model_name = self.select_model(phase)  # 기존 로직
        config = model_config_manager.get_config(model_name)
        
        return model_name, config
```

**4. Phase 4에서 사용:**
```python
# umis_rag/agents/estimator/phase4_fermi.py

from umis_rag.core.model_router import ModelRouter
from umis_rag.core.model_configs import ModelConfig

class Phase4FermiDecomposition:
    
    def __init__(self):
        self.router = ModelRouter()
        # ...
    
    def estimate(self, query: str, context: Context) -> EstimationResult:
        """Phase 4 추정 실행"""
        
        # 1. 모델 + 설정 선택
        model_name, model_config = self.router.select_model_with_config(phase=4)
        
        # 2. 프롬프트 생성 (Fast Mode 고려)
        prompt = self._build_fermi_prompt(context, model_name)
        
        # 3. API 파라미터 구성
        api_params = model_config.build_api_params(
            prompt=prompt,
            reasoning_effort='medium'  # 또는 context에서 가져오기
        )
        
        # 4. LLM 호출
        if model_config.api_type == 'responses':
            response = self.client.responses.create(**api_params)
            raw_response = response.output
        else:
            response = self.client.chat.completions.create(**api_params)
            raw_response = response.choices[0].message.content
        
        # ... 나머지 로직
```

**평가:**
- 적합성: ⭐⭐⭐⭐⭐ (최적)
- 확장성: ⭐⭐⭐⭐⭐ (매우 높음)
- 유지보수: ⭐⭐⭐⭐ (우수)

---

### 3.3 대안 3: ModelConfigManager 독립 모듈

**구조:**
```
config/model_configs.yaml 🆕
  ↓
umis_rag/core/model_config_manager.py (전용 매니저) 🆕
  ↓
umis_rag/core/model_router.py (모델 선택만) 
  ↓
umis_rag/agents/estimator/phase4_fermi.py (매니저 직접 사용) 🔧
```

**장점:**
- ✅ 책임 분리 명확
- ✅ ModelRouter는 단순 유지
- ✅ 설정 관리 전문화

**단점:**
- ❌ 모듈 간 결합도 증가
- ❌ Phase 4에서 두 개 모듈 import

**코드 예시:**
```python
# umis_rag/agents/estimator/phase4_fermi.py

from umis_rag.core.model_router import ModelRouter
from umis_rag.core.model_config_manager import ModelConfigManager

class Phase4FermiDecomposition:
    
    def __init__(self):
        self.router = ModelRouter()
        self.config_manager = ModelConfigManager()
    
    def estimate(self, query: str, context: Context) -> EstimationResult:
        # 모델 선택
        model_name = self.router.select_model(phase=4)
        
        # 설정 조회
        config = self.config_manager.get_config(model_name)
        
        # API 호출
        api_params = config.build_api_params(prompt)
        # ...
```

**평가:**
- 적합성: ⭐⭐⭐⭐ (좋음)
- 확장성: ⭐⭐⭐⭐ (높음)
- 유지보수: ⭐⭐⭐ (좋음)

---

### 3.4 대안 4: .env 확장 (파라미터 포함)

**구조:**
```
.env (모델 + 파라미터)
  ↓
config.py (모델별 설정 로딩) 🔧
  ↓
model_router.py (설정 포함 반환) 🔧
  ↓
phase4_fermi.py (설정 사용) 🔧
```

**장점:**
- ✅ 설정 파일 추가 불필요
- ✅ 사용자가 .env만 수정

**단점:**
- ❌ .env 복잡도 급증
- ❌ 15개 모델 × 5개 파라미터 = 75개 환경변수
- ❌ 타입 안전성 낮음
- ❌ 유지보수 어려움

**코드 예시:**
```bash
# .env (복잡도 폭발)

LLM_MODEL_PHASE4=o1-mini
LLM_MODEL_PHASE4_API_TYPE=responses
LLM_MODEL_PHASE4_REASONING_EFFORT_SUPPORT=true
LLM_MODEL_PHASE4_REASONING_EFFORT_LEVELS=low,medium,high
LLM_MODEL_PHASE4_MAX_OUTPUT_TOKENS=16000

# gpt-5.1로 변경하면?
LLM_MODEL_PHASE4=gpt-5.1
LLM_MODEL_PHASE4_API_TYPE=responses  # 다시 설정해야 함
LLM_MODEL_PHASE4_REASONING_EFFORT_SUPPORT=true  # 다시 설정해야 함
# ...
```

**평가:**
- 적합성: ⭐ (비추천)
- 확장성: ⭐ (매우 낮음)
- 유지보수: ⭐ (매우 어려움)

---

## 4. 추천 솔루션

### 4.1 최종 추천: 대안 2 (ModelRouter 확장) ⭐⭐⭐⭐⭐

**선정 이유:**

**1. 중앙 집중 관리**
- 모든 모델 설정을 한 곳에서 관리
- 벤치마크와 실제 시스템 통합 가능
- 일관성 보장

**2. 확장성**
- 새 모델 추가: YAML에 항목만 추가
- 새 Phase 추가: 기존 구조 그대로 활용
- 새 파라미터 추가: YAML 스키마만 확장

**3. 사용자 친화성**
- `.env`에서는 모델 이름만 선택 (단순)
- 상세 설정은 YAML로 관리 (전문가)
- 기본값 제공으로 대부분 수정 불필요

**4. 버전 관리**
- YAML 파일을 Git으로 관리
- 모델 설정 변경 이력 추적
- 팀 협업 용이

**5. 타입 안전성**
- `ModelConfig` dataclass로 타입 체크
- IDE 자동완성 지원
- 런타임 오류 감소

### 4.2 구현 우선순위

**Phase 1 (즉시):**
1. `config/model_configs.yaml` 생성
2. `umis_rag/core/model_configs.py` 구현
3. 기존 Phase 4에서 사용

**Phase 2 (단계적):**
4. `ModelRouter.select_model_with_config()` 추가
5. 다른 Phase (0-3)에도 적용

**Phase 3 (최적화):**
6. 벤치마크 설정 통합
7. 동적 리로딩 지원

---

## 5. 구현 가이드

### 5.1 Step-by-Step

**Step 1: 설정 파일 생성 (30분)**
```bash
# config/model_configs.yaml 생성
mkdir -p config
touch config/model_configs.yaml
```

**Step 2: 모델 설정 모듈 구현 (2시간)**
```bash
# umis_rag/core/model_configs.py 구현
# - ModelConfig dataclass
# - ModelConfigManager singleton
# - YAML 로딩 로직
```

**Step 3: Phase 4 통합 (1.5시간)**
```bash
# umis_rag/agents/estimator/phase4_fermi.py 수정
# - model_configs import
# - _call_llm() 메서드 수정
# - API 파라미터 동적 구성
```

**Step 4: 테스트 (1시간)**
```bash
# 테스트 케이스 작성
python -m pytest tests/test_model_configs.py
python -m pytest tests/test_estimator_phase4.py
```

**Step 5: 문서화 (30분)**
```bash
# README 업데이트
# config/model_configs.yaml 주석 추가
# 마이그레이션 가이드 작성
```

**총 소요 시간: 5.5시간**

### 5.2 테스트 케이스

```python
# tests/test_model_configs.py

import pytest
from umis_rag.core.model_configs import ModelConfigManager, ModelConfig

def test_model_config_loading():
    """YAML 로딩 테스트"""
    manager = ModelConfigManager()
    
    # o1-mini 설정 확인
    config = manager.get_config('o1-mini')
    assert config.api_type == 'responses'
    assert config.reasoning_effort_support == True
    assert config.max_output_tokens == 16000

def test_api_params_building():
    """API 파라미터 구성 테스트"""
    manager = ModelConfigManager()
    config = manager.get_config('o1-mini')
    
    params = config.build_api_params(
        prompt="Test prompt",
        reasoning_effort='medium'
    )
    
    assert params['model'] == 'o1-mini'
    assert params['input'] == "Test prompt"
    assert params['reasoning']['effort'] == 'medium'
    assert params['max_output_tokens'] == 16000

def test_unsupported_model():
    """미지원 모델 기본값 테스트"""
    manager = ModelConfigManager()
    config = manager.get_config('unknown-model')
    
    assert config.api_type == 'chat'  # 기본값
    assert config.max_output_tokens == 4096  # 기본값
```

### 5.3 마이그레이션 체크리스트

**코드 변경:**
- [ ] `config/model_configs.yaml` 생성 및 15개 모델 정의
- [ ] `umis_rag/core/model_configs.py` 구현
- [ ] `umis_rag/agents/estimator/phase4_fermi.py` 수정
- [ ] 테스트 케이스 작성 및 실행

**문서 업데이트:**
- [ ] README에 모델 설정 추가 방법 설명
- [ ] `model_configs.yaml` 주석 및 예시
- [ ] 마이그레이션 가이드 작성

**검증:**
- [ ] 기존 테스트 통과
- [ ] 모델 변경 시 자동 설정 적용 확인
- [ ] 새 모델 추가 테스트 (YAML만 수정)

---

## 6. 마이그레이션 계획

### 6.1 단계별 계획

**Week 1: Phase 4 적용**
- Day 1: `model_configs.yaml` 및 `model_configs.py` 구현
- Day 2: Phase 4 통합 및 테스트
- Day 3: 문서화 및 검증

**Week 2: 전체 확장**
- Day 1-2: `ModelRouter.select_model_with_config()` 구현
- Day 3-4: Phase 0-3 적용
- Day 5: 통합 테스트

**Week 3: 벤치마크 통합**
- Day 1-2: 벤치마크 `MODEL_API_CONFIGS` → YAML 이동
- Day 3-4: 벤치마크 테스트 스크립트 수정
- Day 5: 전체 검증

### 6.2 롤백 계획

**문제 발생 시:**
1. Git으로 이전 버전 복구
2. Feature flag로 기능 비활성화
3. `.env`에서 `USE_MODEL_CONFIGS=false` 설정

---

## 7. FAQ

**Q1: .env에서 모델만 바꾸면 자동으로 설정이 적용되나요?**
A1: 네! `LLM_MODEL_PHASE4=gpt-5.1`로 바꾸면 `model_configs.yaml`의 gpt-5.1 설정이 자동 적용됩니다.

**Q2: 새 모델을 추가하려면?**
A2: `config/model_configs.yaml`에 항목만 추가하면 됩니다. 코드 수정 불필요.

**Q3: 벤치마크와 실제 시스템이 같은 설정을 사용하나요?**
A3: 네! YAML을 공유하므로 벤치마크에서 검증된 설정이 그대로 실제 시스템에 적용됩니다.

**Q4: 성능 영향은?**
A4: YAML 로딩은 최초 1회만 (singleton). 실행 중에는 메모리 캐시 사용하므로 오버헤드 거의 없음.

**Q5: 기존 코드와 호환되나요?**
A5: 네! 기존 `select_model(phase)` 메서드는 그대로 유지. 새로운 `select_model_with_config(phase)` 추가.

---

## 8. 참고 자료

### 8.1 관련 파일

**기존 시스템:**
- `umis_rag/core/config.py` - Settings 클래스
- `umis_rag/core/model_router.py` - Phase별 모델 선택
- `umis_rag/agents/estimator/phase4_fermi.py` - Phase 4 구현

**벤치마크:**
- `benchmarks/estimator/phase4/common.py` - MODEL_API_CONFIGS
- `benchmarks/estimator/phase4/tests/` - 테스트 스크립트

### 8.2 문서

- `benchmarks/estimator/PHASE4_IMPROVEMENT_PLAN.md` - 개선 계획
- `docs/architecture/UMIS_ARCHITECTURE_BLUEPRINT.md` - 전체 구조

---

**문서 작성:** AI Assistant  
**날짜:** 2025-11-23  
**버전:** v1.0

