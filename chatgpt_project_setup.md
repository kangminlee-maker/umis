# ChatGPT 프로젝트에서 UMIS v5.1.3 활용 가이드

## 🚀 빠른 설정 가이드

### 1. **프로젝트 지침 (Custom Instructions)**

다음 내용을 ChatGPT 프로젝트의 "Instructions"에 복사하세요:

```
나는 UMIS (Universal Market Intelligence System) v5.1.3을 활용하여 시장을 분석합니다.

핵심 원칙:
1. 두 가지 기회 원천 추적: ①비효율성 해소 ②환경 변화 활용
2. 6단계 적응형 워크플로우 수행
3. 5명의 전문 에이전트 협업 시뮬레이션

에이전트 역할:
- Albert (MAnalyst): 관찰과 분류 전담, 해석 없이 팩트만
- Steve (MExplorer): Albert의 관찰 기반 기회 해석
- Bill (MQuant): 4가지 방법으로 시장 규모 계산
- Rachel (MValidator): 데이터 정의와 신뢰성 검증
- Stewart (MCurator): 자율 모니터링과 지식 관리

워크플로우:
Stage 1: Progressive Narrowing (점진적 구체화)
Stage 2: Interactive Discovery (대화형 탐색) 
Stage 3: Smart Default (명시적 깊이 선택)
Stage 4: Context-Aware Suggestions (맥락 기반 제안)
Stage 5: Visual Synthesis (시각적 종합)
Stage 6: Pattern Library (패턴 축적)

상세 구현은 첨부된 umis_guidelines_v5.1.3.yaml 참조.
```

### 2. **첨부 파일 전략**

#### A. 단일 파일 접근법 (권장)
```
📎 umis_guidelines_v5.1.3.yaml (97KB)
   → 전체 시스템 정의 포함
   → ChatGPT가 필요한 부분을 자동으로 참조
```

#### B. 모듈화 접근법 (고급)
```
📎 umis_core.yaml (10KB) - 시스템 정의와 원칙
📎 umis_agents.yaml (25KB) - 에이전트 상세 정의
📎 umis_workflow.yaml (25KB) - 워크플로우 상세
📎 umis_examples.yaml (15KB) - 예시와 패턴
```

### 3. **파일 분할 스크립트**

```python
# split_umis.py - UMIS를 모듈로 분할
import yaml

with open('umis_guidelines_v5.1.3.yaml', 'r', encoding='utf-8') as f:
    data = yaml.safe_load(f)

# 1. Core 파일
core = {
    'system': data['system'],
    'adaptive_framework': data.get('adaptive_framework', {}),
    'core_principles': data.get('core_principles', [])
}
with open('umis_core.yaml', 'w', encoding='utf-8') as f:
    yaml.dump(core, f, allow_unicode=True, sort_keys=False)

# 2. Agents 파일  
agents = {
    'agents': data['agents'],
    'collaboration_triggers': data.get('collaboration_triggers', {})
}
with open('umis_agents.yaml', 'w', encoding='utf-8') as f:
    yaml.dump(agents, f, allow_unicode=True, sort_keys=False)

# 3. Workflow 파일
workflow = {
    'adaptive_workflow': data['adaptive_workflow'],
    'workflow_modes': data.get('workflow_modes', {})
}
with open('umis_workflow.yaml', 'w', encoding='utf-8') as f:
    yaml.dump(workflow, f, allow_unicode=True, sort_keys=False)
```

## 💡 활용 예시

### 1. **시장 분석 시작**
```
"골프 시장을 UMIS로 분석해줘"
→ ChatGPT가 자동으로 6단계 워크플로우 적용
```

### 2. **특정 에이전트 활용**
```
"Albert의 관점에서 이 시장의 거래 패턴을 분류해줘"
→ 첨부 파일에서 Albert의 정의를 참조하여 분석
```

### 3. **깊이 조절**
```
"Stage 3의 Level 2 (Structured Insights) 수준으로 분석해줘"
→ 명시적 깊이 선택 메커니즘 활용
```

## 🎯 최적화 팁

### 1. **프롬프트 템플릿**
```
[시장명]을 UMIS로 분석하고 싶습니다.
- 초기 명확도: [1-10]
- 주요 관심사: [투자/사업/연구/정책]
- 원하는 깊이: [Quick/Structured/Comprehensive/Custom]

Stage 1부터 시작해주세요.
```

### 2. **대화 이어가기**
```
"Stage 2의 Albert가 제시한 MECE 옵션 중 3번을 선택합니다"
"Steve의 해석을 듣고 싶습니다"
"다음 Stage로 진행해주세요"
```

### 3. **결과물 요청**
```
"지금까지의 분석을 Stage 5 형식으로 시각화해주세요"
"발견된 패턴을 Stage 6 라이브러리에 추가할 형식으로 정리해주세요"
```

## ⚡ 성능 최적화

### 1. **컨텍스트 관리**
- 긴 대화 시 중간 요약 요청
- 필요한 Stage만 참조하도록 명시

### 2. **명확한 지시**
- "UMIS의 [특정 섹션]을 참조하여..."
- "첨부 파일의 [특정 부분]에 따라..."

### 3. **반복 활용**
- 자주 사용하는 분석은 별도 프로젝트로
- 산업별 커스텀 프로젝트 생성

## 📋 체크리스트

- [ ] Custom Instructions 설정 (1,500자 이내)
- [ ] umis_guidelines_v5.1.3.yaml 파일 첨부
- [ ] 프로젝트 이름 설정 (예: "UMIS 시장분석")
- [ ] 테스트 프롬프트 실행
- [ ] 필요시 추가 파일 첨부
