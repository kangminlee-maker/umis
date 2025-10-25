# UMIS Guidelines v6.2

## 📚 개요

UMIS (Universal Market Intelligence System)는 AI 에이전트 협업을 통한 범용 시장 정보 분석 시스템입니다.

v1.2부터 현재 v6.2까지 진화해왔으며, v6.2부터는 메인 시스템과 AI 가이드를 분리하여 관리합니다.

**📝 v5.2부터 버전 히스토리는 별도 파일로 관리됩니다: [CHANGELOG.md](./CHANGELOG.md)**

## 📁 파일 구조

```
umis-main/
├── umis_guidelines_v6.2.yaml    # 메인 시스템 정의 (4,747줄)
├── umis_ai_guide_v6.2.yaml     # AI 사용 가이드 (656줄)
├── VERSION.txt                  # 현재 버전 정보
├── CHANGELOG.md                 # 변경사항 기록
├── README.md                    # 이 파일
├── umis_examples_v6.2.yaml      # 실제 사용 예시
└── archive/                     # 이전 버전들
    ├── v1.x/                   # v1.2 - v1.8
    ├── v2.x/                   # v2.0 - v2.1  
    ├── v3.x/                   # v3.0
    ├── v4.x/                   # v4.0
    ├── v5.x/                   # v5.0 - v5.2.2
    └── v6.x/                   # v6.0 - v6.1
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
  - umis_examples_v6.2.yaml로 실행 예시 분리
  - 각 Step별 integrated_approach 명시
  - 정보 손실 없는 효율적 구조

### v6.1 - AI-Optimized Edition
- **UMIS 실행 프로토콜**
  - 모든 프로젝트는 작업리스트로 시작 (예외 없음)
  - 각 작업은 가용 토큰의 50% 이하로 설계
  - 90% 도달 시 긴급 중단 프로토콜
  - 작업별 재평가 포인트 설정
- **AI 가독성 대폭 향상**
  - 명확한 AI GUIDE 섹션 추가 (Line 24-435)

### v6.2 - Autonomous Intelligence Edition
- **동적 토큰 관리** (v6.2.1 신규) 🆕
  - 에이전트별 차등 계수 (Steve: 0.75, Albert: 0.80, Bill/Rachel: 0.85)
  - 3단계 안전장치 (70% 경고, 95% 차단, 98% 긴급)
  - 모델별 최적화: Claude 1M (권장), GPT-5 (지원), Claude 200K (제한)
- **병렬 탐색 프로토콜**
  - 2-4시간 자율 탐색으로 AI 창의성 극대화
  - 스마트 체크포인트로 필요시에만 개입
  - AI 자율성 지표 기반 동적 관리
- **3가지 실행 모드**
  - Exploration Mode: AI 자율성 90-100%
  - Collaboration Mode: AI 자율성 60-70% (기본값)
  - Precision Mode: AI 자율성 30-40%
  - 프로젝트 진행에 따른 동적 전환
- **Stewart 문서 완전 자동화**
  - 모든 작업 실시간 문서화
  - 중요도 기반 자동 분류 및 요약
  - 사용자 부담 제로
- **Data Integrity System 강화**
  - 4-5 depth 세분화된 프로젝트 구조
  - 자동 파일 생성 및 메타데이터 관리
  - 스마트 압축 및 아카이빙
  - 섹션별 검색 가이드 제공
  - 주요 기능 인덱스 구성
  - 라인 번호 참조 정확성 개선
- **동적 토큰 관리 시스템** (v6.2.1 신규) 🆕
  - 에이전트별 차등 계수 (0.75-0.85) - 작업 특성 반영
  - 3단계 안전장치 (70% 경고, 95% 예측 차단, 98% 긴급)
  - 모델별 자동 최적화 및 지원 명시
  - 세션 간 컨텍스트 보존 강화
- **Stewart 모니터링 강화**
  - 작업리스트 관리 모니터링 추가
  - 토큰 사용량 실시간 추적
  - 적응적 개입 프로토콜
  - 재평가 트리거 자동화

## 📌 UMIS Core Structure (v6.2)

### 파일 구조 (v6.2부터 분리):
- **메인 시스템**: `umis_guidelines_v6.2.yaml` (4,747줄) - 시스템 정의 및 구현
- **AI 가이드**: `umis_ai_guide_v6.2.yaml` (656줄) - AI 사용 가이드

### UMIS v6.2 - Autonomous Intelligence Edition:
- **병렬 탐색 프로토콜** - AI 자율성 극대화
- **3가지 실행 모드** - Exploration / Collaboration / Precision
- **Stewart 완전 자동 문서 관리** - 100% 자동화
- **4-5 depth 작업리스트** - 세분화된 실행 계획
- **스마트 체크포인트** - AI 지표 기반 개입

### v6.1 - AI-Optimized Edition:
- **UMIS 실행 프로토콜** - 작업리스트 기반 실행 필수화
- **토큰 관리 강화** - 50% 제한, 90% 긴급 중단
- **적응형 실행** - 각 작업 후 재평가 및 조정
- **세션 연속성** - 컨텍스트 보존 메커니즘

### v6.0.3 - Validation Excellence:
- **Steve 검증 프로토콜** - 3단계 가설 검증 체계
- **병렬 검증 시스템** - 3명 에이전트 동시 검증
- **구조화된 기회 등급** - A/B/C 3등급 분류

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

### 에이전트 역할 (v6.2 역할 기반 이름):
- **Observer (Albert)**: 시장 구조 관찰자
- **Explorer (Steve)**: 시장 기회 탐색가
- **Quantifier (Bill)**: 시장 규모 수치화 전문가
- **Validator (Rachel)**: 데이터 검증 전문가
- **Guardian (Stewart)**: 프로젝트 수호자

## 💡 사용 권장사항

- **권장 AI 모델** (v6.2.1):
  - **최적**: Claude-4-sonnet-1m (1M) ✅ 모든 모드 지원, 세션당 3-5개 쿼리
  - **양호**: GPT-5 (272K) ⭐ Standard/Quick 권장, 세션당 1-2개 쿼리
  - **제한**: Claude-4.5-sonnet / Claude-4.1-opus (200K) ⚠️ Quick Mode만

- **최신 버전 선택**:
  - 메인 시스템: `umis_guidelines_v6.2.yaml` + `umis_ai_guide_v6.2.yaml`
  - 첫 사용자: AI 가이드 먼저 읽기
  - 숙련자: 메인 시스템 파일로 바로 작업

- **ChatGPT/Claude 활용**:
  - 두 파일을 함께 첨부하여 시작
  - AI 가이드의 Quick Start 참조
  - 동적 토큰 관리 프로토콜 자동 적용

- **프로젝트 유형별**:
  - 탐색적 프로젝트: Exploration Mode 활용
  - 일반 프로젝트: Collaboration Mode (기본값)
  - 중요 프로젝트: Precision Mode 적용

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
v6.0.3: 182KB  ██████████████████████████████ (Validation Excellence)
v6.1: 187KB    ███████████████████████████████ (AI-Optimized)
v6.2: 195KB    ████████████████████████████████ (Autonomous Intelligence)
v6.2-split: 147KB+15KB ████████████████████████ (분리된 구조)
```

## 🚀 빠른 시작

최신 버전으로 시작하려면:

```bash
# 1. 두 파일 준비
umis_guidelines_v6.2.yaml  # 메인 시스템
umis_ai_guide_v6.2.yaml    # AI 가이드

# 2. AI에 파일 첨부
- 첫 사용: 두 파일 모두 첨부
- AI 가이드의 Quick Start 섹션 참조

# 3. 프로젝트 시작
"[프로젝트 목표]를 위한 UMIS 분석을 시작합니다"

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
