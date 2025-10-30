# ChatGPT 프로젝트에서 UMIS v6.2 활용 가이드

> **Universal Market Intelligence System v6.2 - Validated Intelligence Edition**  
> 불확실한 상황에서도 적응하며 진화하는 범용 시장 분석 시스템

## 🚀 빠른 설정 가이드

### 1. **기본 설정 (간단한 분석용)**

ChatGPT 커스텀 인스트럭션에 다음 내용을 복사하세요:

```
UMIS (Universal Market Intelligence System) v6.2 - Validated Intelligence Edition을 활용하여 시장을 분석합니다.

핵심 철학: 불확실성을 기회로 전환 (20-30% 명확도로도 시작 가능)

기본 원칙:
1. Discovery Sprint 우선: 명확도 < 7점이면 자동 실행  
2. 13개 시장 차원 통합 분석: 공간적-대상-구조적-운영적-환경적-감성적
3. 5명 AI 에이전트 협업: Observer-Explorer-Quantifier-Validator-Guardian
4. 적응형 진화: 발견을 통한 목표 구체화와 방향 조정

에이전트 역할:
- Albert (Observer): 시장 구조 관찰, 해석 없이 팩트만 (How it works)
- Steve (Explorer): 가설적 해석과 7단계 기회 발굴 프로세스
- Bill (Quantifier): SAM 4방법론 계산 + 지속가능 가치 정량화  
- Rachel (Validator): 데이터 정의 검증 + 창의적 소싱
- Stewart (Guardian): 자율 모니터링 + 목표 이탈시 능동적 개입

기본 워크플로우: Discovery Sprint → Comprehensive Study (2-4주)
선택 워크플로우: 'quick' → Rapid Assessment, 'standard' → Standard Analysis

Stewart 자율 개입:
- 목표 정렬도 < 60% → 방향 재조정
- 동일 주제 3회 반복 → 순환 패턴 돌파
- 특정 영역 30% 초과 → 과몰입 경고
- 10x 기회 발견 → 피벗 기회 제안

고급 기능을 원하면 umis_v6.2_modular/ 첨부 파일들을 사용하세요.
```

### 2. **고급 설정 (완전한 모듈러 시스템)**

더 강력한 기능을 원한다면 `umis_v6.2_modular/` 모듈 파일들을 사용하세요.

#### 2-1. 커스텀 인스트럭션

`umis_v6.2_modular/custom_instructions_v6.2.txt` 내용을 복사하세요.

#### 2-2. 첨부 파일 준비

**필수 파일 (모든 프로젝트)**:
- `umis_v6.2_modular/workflows/adaptive_workflow_v6.2.yaml`
- `umis_v6.2_modular/agents/observer_albert_v6.2.yaml` 
- `umis_v6.2_modular/agents/explorer_steve_v6.2.yaml`

**선택 파일 (고급 기능)**:
- `umis_v6.2_modular/agents/quantifier_bill_v6.2.yaml` - 정확한 SAM 계산
- `umis_v6.2_modular/agents/validator_rachel_v6.2.yaml` - 데이터 검증
- `umis_v6.2_modular/agents/guardian_stewart_v6.2.yaml` - 자율 모니터링

## 🆕 UMIS v6.2 주요 개선사항

### 핵심 혁신
1. **적응형 시작**: 20-30% 명확도로도 Discovery Sprint 실행 가능
2. **스마트 토큰 관리**: Claude-1M(권장), GPT-5(지원), Claude-200K(제한) 모델별 최적화
3. **Stewart 자율 모니터링**: 목표 이탈 자동 감지 및 능동적 개입
4. **완전 자동 문서화**: 사용자 부담 없는 진행 관리
5. **세션 연속성**: 대형 프로젝트 다중 세션 완벽 지원

### 새로운 13개 시장 차원
기존 Porter's 5 Forces를 뛰어넘는 포괄적 분석:

**공간적 차원** (2개):
- 지리적 범위 (Geographic)
- 접근성 수준 (Access Level)

**대상 차원** (3개):
- 제품/서비스 범위 (Product/Service)  
- 가치사슬 범위 (Value Chain)
- 고객 세그먼트 (Customer Segment)

**구조적 차원** (3개):
- 경쟁 구조 (Competition Structure)
- 규제 프레임워크 (Regulatory Framework)
- 거래 모델 (Transaction Model)

**운영적 차원** (2개):
- 채널 생태계 (Channel Ecosystem)
- 가격 구조 (Price Architecture)

**환경적 차원** (2개):
- 기술 성숙도 (Technology Maturity)
- 시간 특성 (Temporal Characteristics)

**감성적 차원** (1개):
- 친화성 프로필 (Affinity Profile)

### 7 Powers 지속가능한 우위
즉각적 가치 + 장기 방어력의 균형:
1. Scale Economics (규모의 경제)
2. Network Effects (네트워크 효과)
3. Switching Costs (전환비용)
4. Branding (브랜딩)
5. Cornered Resource (독점적 자원)
6. Process Power (프로세스 파워)
7. Counter-Positioning (역포지셔닝)

## 📊 실행 모드 선택

### 자동 워크플로우 선택 (사용자 표현 기반)

| 사용자 요청 | 선택 워크플로우 | 기간 | 특징 |
|------------|---------------|------|------|
| 별도 언급 없음 | Discovery → Comprehensive | 2-4주 | **기본값**, 완전한 분석 |
| "빠르게", "urgent" | Rapid Assessment | 1-3일 | Go/No-Go 집중 |
| "표준으로" | Standard Analysis | 1-2주 | 검증된 프로세스 |
| "핵심만" | Quick Insights | 1-2시간 | 즉시 통찰 |

### 실행 모드 (프로젝트 특성별)

**탐색 모드** (Exploration):
- **언제**: 불확실성 높은 신규 프로젝트
- **특징**: AI 자율성 90-100%, 창의성 최대 활용
- **체크포인트**: 2-4시간 간격

**협업 모드** (Collaboration) - **기본값**:
- **언제**: 일반적인 시장 분석
- **특징**: AI-사용자 균형 (60-70%), 주요 결정 공유
- **체크포인트**: 1시간 간격

**정밀 모드** (Precision):
- **언제**: 중요/민감한 프로젝트
- **특징**: 세밀한 단계별 확인 (30-40% 자율성)
- **체크포인트**: 30분 간격

## 🎯 사용 시나리오

### 시나리오 1: 막연한 신사업 아이디어
```
사용자: "AI 관련해서 뭔가 해보고 싶어요"
→ 명확도 25% → Discovery Sprint → Educational Discovery
→ 결과: 구체적 기회 3개 + 실행 계획
```

### 시나리오 2: 구체적 시장 진입 검토
```
사용자: "국내 시니어 케어 시장에 IoT 헬스케어로 진입 검토"  
→ 명확도 80% → Standard Analysis → 2주 완성
→ 결과: Go/No-Go 결정 + 투자 유치 자료
```

### 시나리오 3: 긴급 위기 대응
```
사용자: "경쟁사 파괴적 신제품, 2주 내 대응 필요"
→ 위기 감지 → Rapid Assessment → 3일 완성  
→ 결과: 방어/공격/피벗 전략 옵션
```

## 🔧 토큰 최적화 (v6.2 신규)

### 모델별 지원 상태
- **Claude-1M**: ✅ 최적 (권장) - 모든 기능 완전 활용
- **GPT-5**: 🟡 양호 - 대부분 기능 지원  
- **Claude-200K**: 🟠 제한적 - Quick Mode만 권장

### 동적 토큰 할당
- **Steve**: 75% (창의성 최대 활용)
- **Albert**: 80% (구조 분석 공간)
- **Bill/Rachel**: 85% (효율적 작업)

### 안전 장치
- **70% 경고**: ⚠️ 다음 작업 축소 권고
- **95% 중단**: 🛑 자동 세션 종료 및 요약

## 💡 Stewart의 자율 개입 시스템

### 개입 트리거
```
🎯 목표 정렬도 < 60% → "경로 재조정 필요"
🔄 동일 주제 3회 반복 → "순환 패턴 돌파구 제시"  
🔍 특정 영역 30% 초과 → "과몰입 경고"
⏰ 2주간 진전 < 10% → "실행 모드 전환"
💡 10x 기회 발견 → "피벗 기회 검토"
```

### 개입 메시지 예시
```
🎯 Stewart 개입 알림

상황: Payment 분석에 35% 시간 소요
제안: 고객 획득(30%)이 더 중요한 요소
새 기회: 소셜커머스 10x 기회 발견

응답: 방향 전환하시겠어요?
```

## 🎬 실제 사용 예시

### 기본 설정으로 시작
```
사용자: "온라인 교육 시장 진입을 검토하고 있습니다"

UMIS: 
1. 명확도 평가 (6/10)
2. Discovery Sprint 실행  
3. 5-Agent 병렬 탐색
4. 수렴하여 구체적 기회 도출
```

### 고급 모듈러 활용
```
필수 첨부: adaptive_workflow + observer + explorer
선택 첨부: quantifier (정확한 SAM), validator (데이터 검증)

더 정교한 분석과 자동 문서화 제공
```

## 🏆 성공을 위한 팁

### ✅ DO (권장)
- **불확실해도 시작**: 25% 명확도면 충분
- **Stewart 제안 경청**: 더 나은 기회의 신호
- **Discovery Sprint 신뢰**: < 7점이면 필수
- **Agent 전문성 존중**: 역할 경계 명확

### ❌ DON'T (비권장)  
- **완벽 계획 대기**: 기회 놓침
- **Discovery 생략**: 방향성 오류
- **개입 무시**: 더 나은 기회 놓침
- **역할 침범**: 비효율성 증가

## 📈 기대 효과

**시간 효율성**:
- 전통적 방법: 4-6주 → UMIS: 2-4주
- 명확도 향상: 25% → 85%+ (Discovery Sprint 효과)
- 재작업 감소: Stewart 모니터링으로 방향 이탈 방지

**품질 향상**:
- 13개 차원 포괄적 분석
- 7 Powers 지속가능성 확보
- 3-Agent 검증으로 현실성 보장

**사용자 경험**:
- 불확실성 스트레스 감소  
- 자동 문서화로 부담 제로
- 능동적 가이드로 놓치는 기회 방지

---

## 🔄 v5.1.3에서 v6.2 업그레이드 가이드

### 주요 변경사항
- **6단계 → Discovery Sprint**: 적응형 시작으로 진화
- **MAnalyst → Observer**: 역할 명확화 (How 관찰)  
- **MExplorer → Explorer**: 7단계 기회 발굴 프로세스
- **Stewart 강화**: 자율 모니터링 + 토큰 최적화
- **13개 차원 추가**: 포괄적 시장 분석 프레임워크

### 마이그레이션 체크리스트
- [x] 커스텀 인스트럭션 v6.2로 업데이트
- [x] 새로운 에이전트 ID 확인 (Observer, Explorer, etc.)
- [x] Discovery Sprint 개념 이해
- [x] 13개 시장 차원 숙지
- [x] Stewart 자율 개입 시스템 이해

---

**UMIS v6.2**로 불확실성을 기회로 전환하는 차세대 시장 분석을 시작하세요! 🚀

> **"시장 분석은 완벽한 계획이 아닌 지속적인 발견과 적응의 과정입니다."**