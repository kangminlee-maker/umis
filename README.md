# UMIS Monolithic Guidelines

## 📚 개요

이 폴더는 UMIS (Universal Market Intelligence System)의 단일 파일(monolithic) 형태로 작성된 가이드라인입니다.

v1.2부터 현재 v6.0.1까지의 진화 과정을 담고 있으며, 지속적으로 단일 파일 형태로 유지·발전되고 있습니다.

**📝 v5.2부터 버전 히스토리는 별도 파일로 관리됩니다: [CHANGELOG.md](./CHANGELOG.md)**

## 📁 파일 구조

```
umis-monolithic-guidelines/
├── umis_guidelines_v1.2.yaml   # 초기 버전
├── umis_guidelines_v1.3.yaml   # 에이전트 역할 확장
├── umis_guidelines_v1.4.yaml   # 협업 규칙 추가
├── umis_guidelines_v1.5.yaml   # 데이터 관리 강화
├── umis_guidelines_v1.6.yaml   # 품질 검증 추가
├── umis_guidelines_v1.7.yaml   # 워크플로우 개선
├── umis_guidelines_v1.8.yaml   # 세부 프로세스 강화
├── umis_guidelines_v2.0.yaml   # 메이저 업데이트
├── umis_guidelines_v2.1.yaml   # 버그 수정 및 개선
├── umis_guidelines_v3.0.yaml   # 새로운 에이전트 추가
├── umis_guidelines_v4.0.yaml   # 대규모 확장 (86KB)
├── umis_guidelines_v5.0*.yaml  # 적응형 인텔리전스 도입
├── umis_guidelines_v5.1.yaml   # Adaptive Clarification Protocol
├── umis_guidelines_v5.1.1.yaml # 시장 기회 원천 명확화
├── umis_guidelines_v5.1.2.yaml # Albert-Steve 협업 패턴 확립
├── umis_guidelines_v5.1.3.yaml # AI 친화적 최적화
├── umis_guidelines_v5.2.yaml   # Creative Boost 통합
├── umis_guidelines_v5.2.1.yaml # Classic 제거, 단순화
├── umis_guidelines_v5.2.2.yaml # Market Definition 개선
├── umis_guidelines_v5.3.yaml   # 7 Powers 통합
├── umis_guidelines_v6.0.yaml   # Progressive Intelligence Edition (169KB)
├── umis_guidelines_v6.0.1.yaml # Information Flow Optimization (현재 버전, 177KB)
├── adaptive_workflow_examples.yaml # Adaptive workflow 실행 예시
├── CHANGELOG.md                # 상세 버전 히스토리
├── VERSION.txt                 # 현재 버전 정보
├── umis_v5.1.3_modular/        # 모듈러 v5.1.3
└── umis_v5.3_modular/          # 모듈러 v5.3 (7 Powers 통합)
    ├── agents/
    │   ├── manalyst_albert_v5.3.yaml
    │   ├── mexplorer_steve_v5.3.yaml  # + 방어 구조 분석
    │   ├── mquant_bill_v5.3.yaml      # + 시간 가치 정량화
    │   ├── mvalidator_rachel_v5.3.yaml
    │   └── mcurator_stewart_v5.3.yaml
    ├── workflows/
    │   └── adaptive_workflow_v5.3.yaml  # + 기회 평가 프레임워크
    ├── custom_instructions_v5.3.txt
    ├── example_usage_v5.3.md
    └── UMIS_ChatGPT_Guide_v5.3.md
```

## 🔄 버전별 주요 변경사항

### v1.x 시리즈
- **v1.2**: 기본 구조 정립, 4개 에이전트
- **v1.3-1.4**: 에이전트 역할 세분화
- **v1.5-1.6**: 데이터 관리 및 품질 검증
- **v1.7-1.8**: 워크플로우 최적화

### v2.x 시리즈
- **v2.0**: 대규모 리팩토링
- **v2.1**: 안정성 개선

### v3.0
- 새로운 에이전트 추가
- 협업 메커니즘 강화

### v4.0
- 6개 에이전트 체제 확립
- MECE 원칙 적용
- 대규모 확장 (파일 크기 3배 증가)

### v5.0
- **Adaptive Intelligence** 도입
- Progress Guardian (Stewart) 시스템
- 3단계 데이터 무결성 시스템
- 6단계 Adaptive Clarification Protocol 초안

### v5.1 시리즈
- **v5.1**: Adaptive Clarification Protocol 정식 도입
  - 6단계 적응형 워크플로우
  - Progressive Narrowing 전략
  - 명시적 Depth 선택 메커니즘
  
- **v5.1.1**: 시장 기회 원천 체계화
  - 두 가지 기회 원천 명확화: ①비효율성 해소 ②환경 변화 활용
  - Steve의 역할 재정의 (추론 → MECE 옵션 제시)
  - 투자자 중심 편향 제거
  
- **v5.1.2**: 에이전트 협업 최적화
  - Stage 2 MECE 담당을 Albert로 변경
  - 모든 Stage에 두 가지 기회 원천 반영
  - Stage 간 입력/출력 관계 명확화
  - Albert → Steve 협업 패턴 확립
  
- **v5.1.3**: AI 친화적 최적화 및 모듈화
  - 1단계 최적화로 7.7% 크기 절감
  - AI 이해도 유지하면서 토큰 사용량 감소
  - ChatGPT 프로젝트 활용 가이드 포함
  - 적절한 수준의 모듈화로 유연성 확보
  - 에이전트별 파일 분리 (5개, 48KB)
  - 워크플로우 단일 파일 (48KB)
  - MOwner 역할 정의 포함
  - 모듈 총 96KB (단일 파일 대비 29% 절감)

### v5.2 - Creative Boost Edition
- **AI Brainstorming Framework 통합**
  - 10개의 브레인스토밍 모듈 (M1~M10)
  - 선택적 활성화 방식 (명시적 요청 필요)
  - [BRAINSTORM] 태그로 결과물 구분
  - 기존 UMIS 워크플로우 완전 보존
- **버전 관리 개선**
  - CHANGELOG.md로 버전 히스토리 분리
  - VERSION.txt 파일 추가
  - 메인 파일 간소화

### v5.2.1 - Simplified Edition
- **Classic Workflow v4 제거**
  - 단일 Adaptive workflow로 통합
  - 모든 명확도 수준(1-9) 대응 가능
  - Stewart의 실시간 품질 모니터링
- **파일 크기 최적화**
  - 약 5.5% 감소 (174KB → 164KB)
  - 불필요한 중복 제거
  - 더 깔끔한 구조
- **Migration Guide 제거**
  - 더 이상 필요하지 않음
  - 단일 워크플로우로 단순화

### v5.2.2 - Enhanced Market Definition
- **Universal Market Definition 개선**
  - 2단계 계층구조 도입 (Core + Contextual)
  - Market Boundary: 4개 → 10개 차원
  - Market Dynamics: 4개 → 10개 역학
- **Core 차원 강화**
  - technology_maturity와 temporal_dynamics 추가
  - technology_evolution과 information_asymmetry 추가
- **유연성 증대**
  - 상황별 선택적 차원 활용 가능
  - 시장 특성에 맞춤형 분석

### v5.3 - Sustainable Advantage Edition
- **7 Powers Framework 통합**
  - value_creation을 immediate_value와 sustainable_value로 구분
  - 4가지 지속가능성 다이나믹스 정의 (scale/network/lock-in/uniqueness)
- **Agent 역할 강화**
  - Steve: 지속가능성 평가 추가 (step_3_sustainability_assessment)
  - Steve: 방어 구조 분석 추가 (defensive_structure_analysis)
  - Bill: 시간 가치 정량화 추가 (sustainable_value_quantification)
- **Owner 평가 프레임워크**
  - opportunity_evaluation_framework 도입
  - 즉각적 가치와 지속가능한 가치 균형 평가
  - 2x2 의사결정 매트릭스 추가
- **진정한 경쟁 우위 구축**
  - 단순 기회 발견을 넘어 지속 가능한 해자(moat) 구축
  - 시간이 지날수록 강해지는 사업 모델 설계

### v6.0 - Progressive Intelligence Edition
- **System Definition 전면 재구성**
  - MECE 원칙에 따른 개념 구조 개선
  - 중복 제거 및 누락 요소 보완
  - 정적/동적 요소의 명확한 분리
- **시장 분석 프레임워크 체계화**
  - Step 1: Purpose Alignment - 창업자/기업/투자자 12개 관점
  - Step 2: Market Boundary - 13개 차원의 정적 구조
  - Step 3: Market Dynamics - 3-part 동적 분석
- **이론적 기반 강화**
  - immediate_value: Lean Startup, JTBD, Value Proposition Canvas 통합
  - sustainable_value: 7 Powers 완전 포함
  - 경영학 이론들의 체계적 매핑
- **Adaptive Intelligence System 통합 (Section 2)**
  - 기존 Adaptive Framework와 Workflow를 통합
  - Philosophy, Framework, Methodology, Workflow, Application 5개 하위섹션
  - What, Why, How, When, Where 완전한 구조화
- **Section 구조 개선**
  - Section 3 (PROACTIVE MONITORING): 목표 정렬 중심으로 재구성
  - 새로운 Section 4 (COLLABORATION PROTOCOLS) 생성
  - 총 11개 섹션으로 재구성 (기존 10개에서 확장)
- **실무 활용성 개선**
  - adaptive_workflow_examples.yaml로 실행 예시 분리
  - 각 Step별 integrated_approach 명시
  - 정보 손실 없는 효율적 구조

## 📌 UMIS Core Structure (v6.0)

### UMIS v6.0 전체 구조 (9개 섹션):
1. **SYSTEM DEFINITION** - 시스템 정의와 핵심 역량
2. **ADAPTIVE INTELLIGENCE SYSTEM** - 점진적 지능 통합 시스템
3. **PROACTIVE MONITORING** - 목표 정렬 모니터링
4. **COLLABORATION PROTOCOLS** - 에이전트 간 협업 규칙
5. **DATA INTEGRITY SYSTEM** - 데이터 라이프사이클 관리
6. **AGENTS** - 5개 전문 에이전트 (Albert, Steve, Bill, Rachel, Stewart)
7. **ROLES** - Owner 역할과 책임
8. **CREATIVE BOOST MODULE** - 선택적 창의성 증강
9. **IMPLEMENTATION GUIDE** - 실행 가이드

### Market Analysis Framework:
```yaml
Step 1: Purpose Alignment (WHY)
  └─ 창업자/기업/투자자 관점의 12가지 분석 목적

Step 2: Market Boundary Definition (WHAT × WHERE × WHO)
  └─ 13개 차원의 정적 시장 구조 정의

Step 3: Market Dynamics Framework (HOW × WHEN × WHY)
  ├─ Part A: 경계의 진화 패턴
  ├─ Part B: 시장 작동 메커니즘
  └─ Part C: 통합적 시장 역학
```

### v6.0.1 - Information Flow Optimization (현재)
- **정보 흐름 아키텍처 추가**
  - Main Flow: 관찰(Albert) → 해석(Steve) → 결정(Owner)
  - Information Layers: Raw Data → Processed Data → Insights
  - Support/Oversight 기능 명확화
- **에이전트 역할 명확화**
  - Albert: 구조적 해석 (How it works)
  - Steve: 가설적 해석 (Why & What if)
  - 해석의 명확한 구분으로 중복 제거
- **협업 프로토콜 개선**
  - Albert-Bill 병렬 분석 동기화 강화
  - 2시간 단위 체크포인트 명시
  - 구조-정량 통합 리포트 표준화
- **Stewart 자율 개입 확대**
  - 4가지 개입 트리거 정의 (순환/목표이탈/정체/비효율)
  - 임계값 기반 자동 개입
  - 구체적 액션 가이드라인

## 💡 사용 권장사항

- **최신 버전 선택**:
  - 단일 파일: `umis_guidelines_v6.0.1.yaml` (177KB) - Information Flow Optimization
  - 모듈러 최신: `umis_v5.3_modular/` (총 144KB) - 7 Powers 통합, 선택적 로드
  - 모듈러 안정: `umis_v5.1.3_modular/` (총 96KB) - 검증된 모듈러 구조
- **ChatGPT 프로젝트**: Custom Instructions와 함께 활용
- **용도별 선택**:
  - 빠른 탐색: 모듈화 버전의 최소 구성 (adaptive_workflow_v5.3.yaml + manalyst_albert_v5.3.yaml + mexplorer_steve_v5.3.yaml)
  - 전체 분석: 단일 파일 또는 모듈 전체

## 🔗 관련 링크

- [chatgpt_project_setup.md](./chatgpt_project_setup.md) - ChatGPT 활용 가이드
- [umis_format_comparison.md](./umis_format_comparison.md) - 포맷 비교 분석

## 📊 파일 크기 변화

```
v1.2: 30KB   ████
v1.8: 52KB   ████████
v2.0: 55KB   █████████
v3.0: 25KB   ████ (최적화)
v4.0: 86KB   ██████████████ (대규모 확장)
v5.0: 93KB   ███████████████ (Adaptive Intelligence)
v5.1: 131KB  █████████████████████ (Adaptive Protocol)
v5.1.1: 132KB █████████████████████
v5.1.2: 138KB ██████████████████████ (협업 패턴 확립)
v5.1.3: 136KB ██████████████████████ (AI 친화적 정리)
v5.2: 174KB  ████████████████████████████ (Creative Boost)
v5.2.1: 164KB  ██████████████████████████ (Simplified)
v5.2.2: 167KB  ███████████████████████████ (Enhanced Definition)
v5.3: 176KB    █████████████████████████████ (Sustainable Advantage)
v6.0: 169KB    ████████████████████████ (Progressive Intelligence)
v6.0.1: 177KB  █████████████████████████████ (Information Flow)
```

## 🚀 빠른 시작

최신 버전으로 시작하려면:

```bash
# 1. 최신 파일 사용
umis_guidelines_v6.0.yaml

# 2. ChatGPT 프로젝트 설정
chatgpt_custom_instructions.txt 내용 복사
umis_guidelines_v6.0.yaml 파일 첨부

# 3. 테스트 프롬프트
"[시장명]을 UMIS로 분석해주세요"

# 4. Creative Boost 활용 (선택사항)
"[시장명]을 UMIS로 분석하되, Creative Boost를 활용해주세요"
```

## 📈 발전 방향

- **단일 파일 유지**: 모듈화 대신 최적화를 통한 효율성 추구
- **AI 친화적**: LLM이 이해하고 활용하기 쉬운 구조
- **지속적 개선**: 사용자 피드백 기반 업데이트

---

*UMIS는 지속적으로 진화하고 있습니다. 최신 버전을 사용하여 더 나은 시장 분석을 경험하세요.*
