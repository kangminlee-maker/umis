# UMIS 포맷 전략 제안

## 🎯 핵심 추천: YAML + 보조 포맷

### 1. **메인: YAML (현재 유지)**
- **이유**: AI 모델과 사람 모두에게 최적
- **용도**: 
  - 시스템 정의와 구조
  - 에이전트 역할과 워크플로우
  - 설정과 메타데이터

### 2. **보조: JSON (API/통신용)**
```python
# YAML → JSON 변환 자동화
import yaml
import json

with open('umis_guidelines.yaml', 'r') as f:
    config = yaml.safe_load(f)
    
# API 응답용 JSON
api_response = json.dumps(config['agents'], ensure_ascii=False)
```

### 3. **하이브리드 접근법**

#### A. 구조별 최적 포맷
```yaml
# umis_main.yaml - 핵심 정의
system:
  name: "UMIS"
  agents: !include agents/  # 별도 파일로 분리

# agents/albert.yaml - 에이전트별 파일
id: MAnalyst
name: Albert
competencies: [...]

# workflows/adaptive.py - 동적 로직
class AdaptiveWorkflow:
    def __init__(self, config):
        self.config = yaml.load(config)
    
    def execute(self):
        # Python으로 복잡한 로직 구현
```

#### B. 용도별 포맷 분리
- **정적 설정**: YAML
- **동적 로직**: Python
- **API 통신**: JSON
- **검증 스키마**: JSON Schema

### 4. **마이그레이션 전략**

1. **단계적 분리**
   - Phase 1: 현재 YAML 유지
   - Phase 2: 큰 섹션을 별도 파일로
   - Phase 3: 동적 부분 Python으로

2. **도구 체인 구축**
   ```bash
   # 변환 도구
   umis-convert --from yaml --to json
   umis-validate --schema umis.schema.json
   umis-merge --files "*.yaml" --output combined.yaml
   ```

### 5. **AI 모델 최적화 전략**

```python
class UMISLoader:
    """AI 모델에 최적화된 로더"""
    
    def load_for_ai(self, path):
        # 1. 핵심 구조만 로드
        core = self.load_core_structure(path)
        
        # 2. 필요시 상세 정보 동적 로드
        if self.needs_details:
            core.update(self.load_details())
            
        # 3. AI 친화적 포맷으로 변환
        return self.format_for_ai(core)
```

## 📋 결론

1. **현재 YAML 유지**: AI와 사람 모두에게 최적
2. **점진적 개선**: 필요한 부분만 분리/변환
3. **하이브리드 활용**: 각 용도에 맞는 포맷 선택
4. **도구 지원**: 자동 변환/검증 도구 구축

이 접근법은 현재의 장점을 유지하면서 확장성과 성능을 개선합니다.
