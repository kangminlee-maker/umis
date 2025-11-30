# UMIS Architecture Documents

UMIS 시스템의 주요 아키텍처 재설계 문서 모음

---

## 📁 문서 목록

### 1. DATA_SOURCE_PRIORITY_REDESIGN.md
**버전**: v8.0.0 준비  
**작성일**: 2025-11-30  
**목적**: 데이터 소스 우선순위 체계 재설계

#### 주요 내용
- **문제점 분석**
  - Observer가 Validator 없이 Estimator 의존
  - 사실 확인 없는 보고 프로세스
  - 잘못된 데이터 소스 우선순위

- **해결 방안**
  - 4-Tier 데이터 획득 파이프라인
    - Tier 1: Evidence Collection (Fast Path)
    - Tier 2: Validator (Active Search)
    - Tier 3: Calculator (Formula Design)
    - Tier 4: Estimator (Pure Guessing)
  - Fact-Check Protocol 도입
  - Agent 계층화 재구성

#### 영향 범위
- Observer, Explorer, Quantifier, Validator, Estimator 전체
- umis.yaml 전체 업데이트 필요
- 워크플로우 전면 재설계

---

### 2. UMIS_v8_AGENT_ROLES_AND_WORKFLOWS.md
**버전**: v8.0.0  
**작성일**: 2025-11-30  
**목적**: v8.0.0 Agent 역할 및 워크플로우 상세 설계

#### 주요 내용
- **Agent 계층 구조**
  ```
  Business Analysis Layer
    ├─ Observer (Market Structure + Sizing)
    └─ Explorer (Opportunity Scout)
  
  Evidence Generation Layer
    ├─ Evidence Collector (Fast Path)
    ├─ Validator (Active Search)
    ├─ Calculator (Formula Design) ← NEW
    └─ Estimator (Pure Guessing)
  
  Supervision Layer
    └─ Guardian (Process Overseer)
  ```

- **Calculator 신규 도입**
  - Mode 1: Exact Calculation (정확한 공식 계산)
  - Mode 2: Multi-Formula Convergence (다공식 수렴 추정)
  - Fermi Decomposition (Estimator에서 이동)
  - 계산을 통한 증거 생성

- **Estimator 단순화**
  - 4-Stage → 2-Stage로 축소
    - Stage 1: Evidence Collection (Fast Path)
    - Stage 2: Generative Prior (최후의 찍기)
  - Fermi 제거 → Calculator로 이동
  - Fusion 제거 → Calculator Convergence로 대체

- **Observer 확장**
  - 시장 구조 + 시장 규모 통합 분석
  - Calculator 활용한 Bottom-up 계산
  - Fact-check 필수화

#### 워크플로우 상세
- 각 Agent의 단계별 프로세스
- 데이터 획득 우선순위
- Fallback 메커니즘
- 품질 보증 프로토콜

---

## 🔄 변경 이력

### v8.0.0 (설계 중)
- **2025-11-30**: 초기 설계 문서 작성
  - DATA_SOURCE_PRIORITY_REDESIGN.md
  - UMIS_v8_AGENT_ROLES_AND_WORKFLOWS.md

---

## 📌 Implementation Status

### Phase 1: 설계 (완료 ✅)
- [x] 문제점 분석
- [x] 4-Tier Pipeline 설계
- [x] Agent 역할 재정의
- [x] 워크플로우 상세 설계

### Phase 2: 구현 (대기 중)
- [ ] Calculator 도구 구현
- [ ] Estimator 단순화
- [ ] Observer 확장
- [ ] umis.yaml 업데이트

### Phase 3: 테스트 (대기 중)
- [ ] 단위 테스트
- [ ] 통합 테스트
- [ ] End-to-End 테스트

### Phase 4: 배포 (대기 중)
- [ ] Alpha 테스트
- [ ] Production 배포

---

## 📖 관련 문서

- `/docs/architecture/UMIS_ARCHITECTURE_BLUEPRINT.md`: 전체 시스템 아키텍처
- `/umis.yaml`: 현재 시스템 스펙 (v7.11.1)
- `/dev_docs/estimator/`: Estimator 관련 상세 문서
- `/dev_docs/guides/`: 개발 가이드

---

## ⚠️ 주의사항

이 폴더의 문서들은 **전체 시스템 구조의 근간을 변경**하는 중대한 재설계입니다.

- 구현 전 충분한 검토 필요
- 모든 Agent에 영향을 미침
- 하위 호환성 없음 (Breaking Changes)
- 단계적 구현 권장

---

**Last Updated**: 2025-11-30  
**Version**: v8.0.0 Design Phase
