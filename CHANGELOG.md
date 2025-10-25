# UMIS (Universal Market Intelligence System) 변경 이력

## 개요
이 문서는 UMIS의 모든 버전 변경사항을 기록합니다.

---

## v6.0.3 (2024-10-25) - Validated Opportunity Discovery Process [CRITICAL UPDATE]

### 🎯 핵심 개선사항
**Steve 가설 검증 프로토콜**: 모든 기회는 체계적으로 검증됨
- **3개 에이전트 병렬 검증**: Albert(구조적), Bill(경제적), Rachel(데이터) 타당성 검증
- **조건부 기회 추적**: Stewart의 월별 모니터링 시스템
- **Stewart 예외 조항**: Steve 가설 검증은 반복 제한에서 제외
- **학습 기반 개선**: 실패를 통한 체계적 학습과 진화

### 🏗️ 주요 개선사항

#### 1. 가설 검증 사이클 (신규)
- 30분 가설 제출 → 2-4시간 병렬 검증 → 2시간 종합 회의
- 검증 결과: 검증됨/조건부/기각
- 최대 5회 반복을 통한 가설 정교화
- 모든 Steve 기회는 자동으로 검증 프로세스 진입

#### 2. 조건부 기회 관리 (신규)
- Stewart가 월별 조건 충족도 모니터링
- 70% 충족: 재검증 준비
- 85% 충족: 실행팀 구성
- 100% 충족: 즉시 실행

#### 3. 검증 효율성 개선
- Fast Track Mode: 긴급 시 2시간 내 Go/No-Go
- Adaptive Depth: 프로젝트 명확도에 따른 검증 깊이 조정
- 중복 검증 방지: 개별 가설과 포트폴리오 검증 분리

#### 4. Steve 프로세스 업데이트
- Phase 6: "검증 준비 및 종합"으로 변경
- Phase 8: "검증 후 처리" 신규 추가
- 검증 결과별 차별화된 후속 조치

---

## v6.0.2 (2024-10-24) - Integrated Opportunity Discovery Process [MAJOR UPDATE]

### 🎯 핵심 개선사항
**Steve의 통합 기회 발굴 프로세스**: 체계적인 7단계 프로세스 도입
- **Extended → Core**: extended_frameworks를 핵심 분석 프레임워크로 통합
- **시간 할당**: 최소 8시간 ~ 최대 3일 명시
- **품질 기준**: 완성도, 깊이, 검증, 실행 가능성 표준화
- **다차원 분석**: 6개 프레임워크 필수 적용

### 🏗️ 주요 개선사항

#### 1. 7단계 통합 프로세스
- Phase 1: 초기 기회 스캔 (2-4시간)
- Phase 2: 다차원 심층 분석 (4-8시간)
- Phase 3: 융합 기회 발굴 (2-3시간)
- Phase 4: 현실성 검증 (2-4시간)
- Phase 5: 우선순위화 (1-2시간)
- Phase 6: 전략적 종합 (2-3시간)
- Phase 7: 최종 문서화 (1-2시간)

#### 2. 6개 핵심 분석 프레임워크
- Defensive Structure Analysis
- Platform Power Interpretation
- Information Asymmetry Mapping
- Regulatory Impact Assessment
- Technology Disruption Scan
- Affinity Economy Exploration

#### 3. 품질 기준 강화
- 프레임워크 적용 완성도
- 분석의 깊이와 구체성
- 검증 프로토콜 통과율
- 실행 가능성과 구체성

#### 4. 협업 터치포인트 명확화
- 각 단계별 협업 시점과 목적 정의
- Albert, Bill, Rachel, Owner와의 상호작용 구조화

---

## v6.0.1 (2024-10-24) - Information Flow Optimization [MINOR UPDATE]

### 🎯 핵심 개선사항
**정보 흐름 최적화**: 에이전트 간 역할과 협업 구조 명확화
- **정보 흐름**: Albert → Steve → Owner의 명확한 단계별 진행
- **계층 구조**: Raw Data → Processed Data → Insights
- **해석 구분**: 구조적 해석(Albert) vs 가설적 해석(Steve)
- **Stewart 강화**: 자율 개입 트리거 구체화

### 🏗️ 주요 개선사항

#### 1. 정보 흐름 아키텍처 신규 추가
- Main Flow: 관찰 → 해석 → 결정
- Information Layers: 4계층 구조 정의
- Support Functions: Rachel/Bill 역할 명확화
- Oversight Function: Stewart 모니터링 강화

#### 2. 에이전트 역할 명확화
- **Albert**: "How" - 구조적 해석 전문
- **Steve**: "Why & What if" - 가설적 해석 전문
- 해석의 명확한 구분으로 중복 제거

#### 3. 협업 프로토콜 개선
- Albert-Bill 병렬 분석 동기화 강화
- 2시간 단위 체크포인트 명시
- 구조-정량 통합 리포트 표준화

#### 4. Stewart 자율 개입 확대
- 4가지 개입 트리거 정의
- 임계값 기반 자동 개입
- 구체적 액션 가이드라인

---

## v6.1a (2024-10-24) - Modular Architecture Edition [ARCHITECTURE UPDATE]

### 🎯 핵심 변경사항
**아키텍처 업데이트**: BMAD-METHOD 분석을 통한 모듈화 구조 도입
- **파일 크기**: 177KB → 16KB (90% 감소)
- **토큰 효율성**: 70% 개선
- **선택적 로딩**: 필요한 모듈만 로드

### 🏗️ 주요 개선사항

#### 1. 모듈화 아키텍처
- **Core Module**: 핵심 에이전트와 워크플로우 유지
- **Meta Workflow**: 지능형 진입점 도입
- **Data Management**: 1차/2차 데이터 분리
- **Lifecycle Management**: 30일 규칙 적용

#### 2. 데이터 관리 체계
- **자동 분류 시스템**: 가치 기반 자동 분류
- **데이터 계보 추적**: 모든 2차 데이터의 출처 추적
- **Working Directory**: 프로젝트 진행 중 데이터 실시간 저장

#### 3. 성능 최적화
- **캐싱 전략**: Hot/Cold 캐시 구분
- **지연 로딩**: 필요시에만 모듈 로드
- **배치 처리**: 일일/주간/월간 자동화

#### 4. 프로젝트 구조 정리
- **core 폴더 제거**: 중복 제거 및 구조 단순화
- **VERSION.txt**: 프로젝트 루트로 이동
- **문서 업데이트**: 모든 참조 경로 수정

### 📁 간소화된 구조
```
umis-monolithic-guidelines/
├── umis_guidelines_v6.0.yaml   # 기준 버전
├── umis_guidelines_v6.1a.yaml  # 모듈화 버전
├── VERSION.txt                 # 현재 버전
└── [기타 폴더들]
```

---

## v6.0 (2024-10-22) - Progressive Intelligence Edition [MAJOR UPDATE]

### 🎯 핵심 철학 변화
**메이저 업데이트 핵심**: 실행력과 현실성 대폭 강화
- **명확도 프레임워크**: "뭔가 기회가 있을 것 같아"(20-30%)도 시작 가능
- **병렬 분석 구조**: 현실(Albert)과 기회(Steve)의 균형
- **검증된 의사결정**: 상상이 아닌 데이터 기반 판단

### 🚀 v5.x → v6.0 업그레이드 이유
1. **시스템 전반 재구조화**: 9개 섹션 전체 재정의
2. **핵심 개념 진화**: 적응형 → 점진적 지능
3. **실행 메커니즘 혁신**: 추상적 → 구체적 가이드
4. **에이전트 역할 재정립**: 표준화 + 협업 강화
5. **사용자 경험 혁신**: 진입 장벽 대폭 낮춤

### 🏗️ 1. 시스템 구조 재편

#### 전체 구조 개선
- **9개 섹션 체제**로 재구성 (기존 11개 → 9개)
- **Section 통합/분리**:
  - Section 2: Adaptive Intelligence System으로 통합 (기존 Section 8 흡수)
  - Section 4: COLLABORATION PROTOCOLS 독립 (기존 Section 3에서 분리)
  - Section 10, 11 제거 (불필요한 과거 참조 정리)

#### Market Analysis Framework 체계화
- **3단계 구조의 완성도 향상**:
  - Step 1: Purpose Alignment (WHY) - 12개 관점 (창업자/기업/투자자)
  - Step 2: Market Boundary (WHAT×WHERE×WHO) - 13개 차원
  - Step 3: Market Dynamics (HOW×WHEN×WHY) - 3-part 구조

#### 파일 최적화
- **크기 감소**: 176KB → 169KB (4.0%)
- **실행 예시 분리**: adaptive_workflow_examples.yaml

### 🧠 2. 개념적 강화

#### 이론적 기반 확장
- **immediate_value** (6개 영역): problem_solution_fit, value_proposition_design, customer_discovery, time_to_value, innovation_patterns, lean_validation
- **sustainable_value** (7 Powers 완전 포함): scale/network/switching/brand/resource/process/counter-positioning dynamics

#### Market Dynamics 3-Part 구조
- **Part A**: 경계의 진화 패턴 (13개 차원별)
- **Part B**: 시장 작동 메커니즘 (value/force/lifecycle)
- **Part C**: 통합적 시장 역학 (상호작용/패턴/신호)

### 🤝 3. 협업 메커니즘 강화

#### Albert-Bill 병렬 분석 구조
- **실시간 동기화**: 2시간마다 중간 결과 공유
- **통합 리포트**: Steve에게 구조-정량 통합 데이터 제공
- **예상 효과**: 재작업 빈도 60% → 15% 감소

#### 의사결정 검증 체계 (4단계)
1. Albert, Steve, Bill: 최종 산출물 제출
2. Rachel: 근거 신뢰도 평가 (Evidence Reliability Matrix)
3. Stewart: 논리적 건전성 검증 (Decision Readiness Assessment)
4. Owner + 전체: 최종 의사결정 회의

### 🎯 4. 실행력 강화

#### 명확도 프레임워크 구체화
- **3개 핵심 차원**: 의도 명확도(40%), 도메인 지식(35%), 시급성(25%)
- **Sprint Customization Matrix**: 의도×지식 조합별 4가지 접근법
- **예상 효과**: 프로젝트 시작 시간 -50%, 방향 전환 빈도 -40%

#### Adaptive Safeguards
- **3회 순환 차단**: 동일 주제 3회 반복 시 Stewart 자동 개입
- **예외 처리**: 10x 기회, 블랙스완 이벤트는 제한 없음

### 🔍 5. 모니터링 개선

#### Proactive Monitoring 재구성
**목표 정렬 중심의 4가지 문제 유형**:
- **A. 목표 자체**: obsolete goal, superior opportunity, goal conflict
- **B. 실행 과정**: micro obsession, scope inflation, analysis paralysis
- **C. 방향성**: goal drift, wrong vector, circular motion
- **D. 리소스**: resource drain, capability mismatch

### 📉 6. 대폭 간소화된 섹션들

- **DATA INTEGRITY SYSTEM**: 620줄 → 152줄 (75% 감소)
- **CREATIVE BOOST MODULE**: 800줄 → 120줄 (85% 감소)

### 🎁 7. 에이전트/오너 표준화

- **Agent 4-섹션 구조**: IDENTITY, CAPABILITIES, WORK DOMAIN, BOUNDARIES & INTERFACES
- **Extended Frameworks**: 모든 에이전트에 새로운 시장 차원 대응 능력 추가

### 📊 예상 효과 요약

| 영역 | 개선 효과 |
|------|-----------|
| 프로젝트 시작 시간 | -50% |
| 방향 전환 빈도 | -40% |
| 재작업 빈도 | -45% |
| 의사결정 신뢰도 | +50% |
| 현실성 | +40% |
| 논리 오류 | -60% |

---

## v6.1a (2024-10-23) - [DEPRECATED - Replaced by v6.1a Modular Architecture]

*Note: 이 버전은 2024-10-24 모듈화 아키텍처 버전으로 대체되었습니다.*

원래 v6.1a는 사용자 접근성 강화를 위해 Brownfield Intelligence System과 Activation System을 추가했으나, 
모듈화 아키텍처가 더 효율적인 솔루션을 제공하므로 대체되었습니다.

### 주요 변경사항 (참고용)
- Brownfield Intelligence System 추가 (Section 13)
- Activation Code System 추가 (umis_activation_system.yaml, umis_activation_prompt.md)
- 사용자 친화적 인터페이스 강화

---

## v5.3 (2024-10-21) - Sustainable Advantage Edition
### 추가
- **7 Powers Framework 통합**
  - Market Dynamics에 sustainable_value 개념 통합
  - 지속 가능한 경쟁 우위 메커니즘 분석
- **Agent 역할 강화**
  - Steve: 지속가능성 평가 추가 (step_3_sustainability_assessment)
  - Steve: 방어 구조 분석 추가 (defensive_structure_analysis) 
  - Bill: 시간 가치 정량화 추가 (sustainable_value_quantification)
- **Owner 평가 프레임워크**
  - opportunity_evaluation_framework 추가
  - 즉각적 가치와 지속가능한 가치 균형 평가
  - 2x2 의사결정 매트릭스

### 개선
- value_creation을 immediate_value와 sustainable_value로 구분
- 4가지 지속가능성 다이나믹스 정의
  - scale_dynamics (규모의 경제)
  - network_dynamics (네트워크 효과)
  - lock_in_dynamics (전환 비용)
  - uniqueness_dynamics (독점적 차별화)
- Albert-Steve 협업 강화: 시간 경과 관찰 데이터 전달

---

## v5.2.2 - Enhanced Market Definition (2024-10-21)
### 주요 변경사항
- **Universal Market Definition 개선**: 2단계 계층구조로 확장
- **Market Boundary Dimensions**: 4개 → 10개 (6 core + 4 contextual)
- **Market Dynamics Framework**: 4개 → 10개 (6 core + 4 contextual)
- **파일 크기**: 164KB → 167KB (약 2% 증가)

### 개선된 Core 차원들
#### Boundary Dimensions (6개)
- 기존 4개 유지 (geographic, product_service, value_chain, customer_type)
- 신규 2개 추가 (technology_maturity, temporal_dynamics)

#### Market Dynamics (6개)
- 기존 4개 유지 (value_creation, competitive_forces, market_evolution, regulatory_impact)
- 신규 2개 추가 (technology_evolution, information_asymmetry)

### Contextual 차원들
- 선택적으로 추가 가능한 보조 차원
- Boundary: transaction_model, access_level, price_positioning, channel_structure
- Dynamics: market_signals, cultural_momentum, ecosystem_health, sustainability_factors

---

## v5.2.1 - Simplified Edition (2024-10-21)
### 추가 단순화 (같은 날 업데이트)
- **Section 7 (Workflow Management) 제거**: 단일 워크플로우만 있으므로 불필요
- **UMIS_MODE 환경변수 제거**: 선택지가 없으므로 무의미
- **파일 크기 추가 감소**: 4,116줄 → 4,096줄
- **UMIS_CREATIVE만 유지**: Creative Boost on/off 제어용

---

## v5.2.1 - Simplified Edition (2024-10-21)
### 주요 변경사항
- **Classic Workflow v4 제거**: 단일 Adaptive workflow로 통합
- **Migration Guide 제거**: 더 이상 필요하지 않음
- **파일 크기 최적화**: 약 8% 감소 (4,473줄 → 4,116줄)
- **단순화된 워크플로우 관리**: 모든 명확도 수준을 하나의 워크플로우로 처리

### 제거된 섹션
- Classic Workflow v4 전체 섹션
- Migration from v4 가이드
- Classic 관련 모든 Appendix (6개)
- workflow_modes의 classic 옵션

### 개선사항
- 품질 관리: Stewart의 실시간 모니터링으로 Classic의 정적 게이트보다 우수
- 유연성: 명확도 1-9 모두 대응 가능
- 일관성: 단일 워크플로우로 혼란 제거

---

## v5.2 - Creative Boost Edition (2024-10-21)
### 주요 변경사항
- **AI Brainstorming Framework 통합**: 선택적 Creative Boost 모듈로 통합
- **창의성 증강 도구**: 필요시에만 활용하는 명시적 창의성 도구 추가
- **기존 워크플로우 유지**: 보조 도구로서의 역할 명확화
- **[BRAINSTORM] 태그**: 창의적 프로세스 결과물 명시적 표시

### 새로운 기능
- 10개의 브레인스토밍 모듈 (M1~M10)
- 4개의 Creative Workflows
- 5개의 실행 패턴
- 모듈 간 관계 정의

### 통합 원칙
- 명시적 요청 시에만 활용
- 기존 UMIS 프로세스와 명확히 구분
- 모든 결과물에 [BRAINSTORM] 태그 필수

---

## v5.1.3 - Optimization Update (2024-10-21)
### 최적화
- **구조 최적화**: 중복 주석 통합, 구조적 빈 줄 제거
- **크기 절감**: 7.7% 파일 크기 감소
- **AI 이해도 유지**: 토큰 사용량 최적화하면서 가독성 보존

---

## v5.1.2 - Collaboration Enhancement (2024-10-19)
### 주요 변경사항
- **Albert 역할 확장**: Stage 2의 MECE 기반 사용자 의도 파악 담당
- **Steve 역할 재정의**: 사용자 선택 후 기회 해석으로 변경
- **표현 개선**: Albert의 해석적 표현 제거 ("이유" → 관찰 가능한 표현)
- **기회 원천 통합**: 모든 Stage에 두 가지 기회 원천 반영
  - 비효율성 해소
  - 환경 변화 활용
- **협업 패턴 강화**: Albert → Steve 협업을 핵심 원칙으로 명시

### 연결성 강화
- Stage 간 입력/출력 관계 명확화
- 워크플로우 연결성 개선

---

## v5.1.1 - Market Opportunity Clarification (2024-10-19)
### 주요 변경사항
- **시장 기회 원천 명확화**:
  1. 비효율성 해소
  2. 환경 변화 활용
- **Progressive Narrowing 개선**: 다차원적 관점과 Bottom-up 접근법 추가
- **Steve 역할 변경**: 추론에서 MECE 옵션 제시로 전환
- **Smart Default 강화**: 명시적 Depth 선택 메커니즘 추가
- **편향 제거**: 투자자 중심 편향 제거, 중립적 분석 프레임워크 강화

---

## v5.1 - Enhanced Adaptive Intelligence (2024-10-19)
### 개선사항
- Discovery Sprint 프로세스 정교화
- Stewart의 자율적 모니터링 기능 상세화
- 적응형 워크플로우 단계별 가이드 강화

---

## v5.0 - Adaptive Intelligence Edition (2024-09-16)
### 혁신적 변경
- **적응형 프레임워크 도입**: 20-30% 명확도로도 시작 가능 (기존 80-90%)
- **Discovery Sprint**: 1-2일 빠른 탐색으로 방향 설정
- **Stewart 역할 확장**: Progress Guardian으로 능동적 개입
- **실시간 피벗**: 발견에 따른 유연한 방향 전환
- **자동 데이터 보호**: 2시간마다 체크포인트, 5분 내 복구
- **목표 진화 추적**: 명확도 점수(1-10) 관리

### 새로운 철학
- "Know → Plan → Execute" (v4.0)에서
- "Explore → Discover → Adapt → Succeed" (v5.0)로 전환

### 주요 시스템
1. **Adaptive Framework**: 불확실성 수용과 발견 기반 진화
2. **Proactive Monitoring**: Stewart의 자율적 프로젝트 모니터링
3. **Data Integrity System**: 3단계 데이터 보호 체계
4. **Goal Evolution Tracking**: 목표의 적응적 진화 추적

---

## v4.0 - MECE Framework (2024-09-07)
### 핵심 변경
- **MECE 원칙 전면 도입**: 상호배타적이며 전체를 포괄하는 분석
- **체계적 워크플로우**: Phase 기반 구조화된 프로세스
- **품질 게이트**: 각 Phase 종료 시 검증 체크포인트
- **명확한 역할 분담**: 에이전트별 독립적 책임 영역

### 워크플로우
1. Project Initiation
2. Market Structure Analysis
3. Opportunity Exploration
4. Market Quantification
5. Synthesis & Decision
6. Knowledge Preservation

---

## v3.0 - Simplified Architecture (2024-09-07)
### 주요 변경
- 복잡도 대폭 감소
- 핵심 기능에 집중
- 사용성 개선

---

## v2.0 - Enhanced Collaboration (2024-09-07)
### 개선사항
- 에이전트 간 협업 프로토콜 강화
- 정보 흐름 최적화
- 실시간 협업 지원

---

## v1.x Series - Foundation Building
### v1.8 (2024-09-07)
- 추가 기능 통합
- 안정성 개선

### v1.7 (2024-09-07)
- 성능 최적화
- 버그 수정

### v1.6 (2024-09-03)
- 사용자 피드백 반영
- 인터페이스 개선

### v1.5 (2024-09-03)
- 새로운 분석 도구 추가
- 문서화 강화

### v1.4 (2024-09-03)
- 시장 정의 프레임워크 개선
- 에이전트 역할 명확화

### v1.3 (2024-09-03)
- 첫 안정화 버전
- 기본 기능 완성

### v1.2 (2024-09-03)
- 초기 프로토타입
- 기본 구조 확립

---

## 버전 관리 원칙

### Semantic Versioning
- **Major (X.0.0)**: 큰 구조적 변경, 철학적 전환
- **Minor (x.X.0)**: 새로운 기능 추가, 중요한 개선
- **Patch (x.x.X)**: 버그 수정, 작은 개선, 최적화

### 호환성
- v5.x는 v4.0과 하위 호환 (classic mode 지원)
- v4.0은 v3.0과 비호환 (완전히 새로운 구조)

### 마이그레이션
- 각 Major 버전 업그레이드 시 마이그레이션 가이드 제공
- 점진적 전환 지원

---

*이 문서는 UMIS의 공식 변경 이력입니다. 각 버전의 상세한 변경사항은 해당 버전의 가이드라인 파일을 참조하세요.*
