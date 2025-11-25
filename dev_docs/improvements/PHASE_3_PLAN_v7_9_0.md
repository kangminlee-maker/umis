# Phase 3: 프로덕션 배포 준비 계획 (v7.9.0)

**작성일**: 2025-11-25  
**버전**: v7.9.0  
**목표**: 프로덕션 환경에서 안정적으로 운영 가능한 시스템 구축

---

## 📋 목차

1. [개요](#개요)
2. [우선순위 작업](#우선순위-작업)
3. [Task 상세](#task-상세)
4. [타임라인](#타임라인)

---

## 개요

**Phase 2 완료 현황**:
- ✅ 81개 테스트 (100% 통과)
- ✅ 버그 수정 완료
- ✅ 성능 목표 달성
- ✅ 프로덕션급 안정성 확보

**Phase 3 목표**:
- 📚 완전한 문서화
- 📊 운영 모니터링 체계 구축
- ⚡ 성능 최적화
- 🔒 보안 강화
- 🚀 배포 자동화

---

## 우선순위 작업

### 우선순위 1: 문서화 (필수, 1-2일)

**목표**: 개발자와 사용자가 시스템을 쉽게 이해하고 사용할 수 있도록

#### Task 1.1: CHANGELOG 작성 ✅ (즉시 시작)
- **파일**: `CHANGELOG.md` (최상위)
- **내용**:
  - v7.9.0 변경사항
  - Phase 0-2 완료 내역
  - 버그 수정
  - Breaking Changes
  - Migration Guide

#### Task 1.2: API 문서 업데이트
- **대상**:
  - `EstimatorRAG.estimate()` (v7.9.0 변경사항)
  - `Phase3Guestimation.estimate()`
  - `Phase4FermiDecomposition.estimate()`
  - `ValidatorRAG.search_definite_data()`
- **내용**:
  - 파라미터 설명
  - 반환값 (항상 EstimationResult)
  - 사용 예시
  - 성능 특성

#### Task 1.3: 사용자 가이드 업데이트
- **파일**: `docs/guides/ESTIMATOR_USER_GUIDE.md` (신규 또는 업데이트)
- **내용**:
  - Quick Start
  - Phase별 동작 방식
  - LLM Mode 선택 가이드
  - Cursor vs API Mode
  - 성능 최적화 팁
  - 트러블슈팅

#### Task 1.4: 아키텍처 문서 업데이트
- **파일**: `docs/architecture/UMIS_ARCHITECTURE_BLUEPRINT.md`
- **업데이트**:
  - v7.9.0 변경사항 반영
  - Phase 0-4 흐름 다이어그램
  - LLM Mode 동적 전환
  - Cursor Fallback 메커니즘

---

### 우선순위 2: 모니터링 (중요, 2-3일)

**목표**: 프로덕션 환경에서 시스템 상태를 실시간으로 파악

#### Task 2.1: 구조화된 로깅
- **현재**: 단순 print/logger 사용
- **개선**:
  - JSON 로그 포맷
  - 로그 레벨 표준화 (DEBUG/INFO/WARNING/ERROR)
  - 상관관계 ID (correlation_id) 추가
  - 성능 메트릭 자동 기록

**예시**:
```python
{
  "timestamp": "2025-11-25T14:00:00Z",
  "level": "INFO",
  "correlation_id": "req-12345",
  "phase": 3,
  "question": "B2B SaaS ARPU는?",
  "execution_time": 2.5,
  "confidence": 0.8,
  "llm_mode": "gpt-4o-mini"
}
```

#### Task 2.2: 메트릭 수집
- **도구**: Python `logging` + 파일 또는 Prometheus (선택적)
- **메트릭**:
  - Phase별 사용률 (Phase 0/1/2/3/4 비율)
  - Phase별 평균 실행 시간
  - 성공률 / 실패율
  - LLM Mode 사용 분포
  - API 호출 비용 (Phase 3-4)

#### Task 2.3: 알람 설정 (선택적)
- **조건**:
  - 실패율 > 10%
  - Phase 3 응답 시간 > 10초
  - Phase 4 응답 시간 > 20초
- **방법**: 로그 파일 모니터링 또는 이메일 알림

---

### 우선순위 3: 최적화 (선택적, 3-5일)

**목표**: 응답 속도 개선 및 비용 절감

#### Task 3.1: Phase 2 Validator 데이터베이스 재구축
- **현재 문제**:
  - 질문 원본 그대로 저장 ("B2B SaaS의 평균 ARPU는?")
  - 정규화 없이 검색 → 유사도 불안정
  
- **개선**:
  - 질문 정규화 적용 (`_normalize_question()`)
  - 데이터베이스 재구축 (24개 데이터 소스)
  - 유사도 정확도 향상

**예상 효과**:
- Phase 2 활성화율 ↑ (현재 낮음 → 20-30%)
- Phase 3-4 부하 ↓ (비용 절감)

#### Task 3.2: Phase 3-4 LLM 프롬프트 최적화
- **현재**:
  - 프롬프트 길이 최적화 필요
  - 토큰 소비 많음
  
- **개선**:
  - 프롬프트 압축
  - Few-shot 예시 최적화
  - 시스템 메시지 간결화

**예상 효과**:
- 토큰 소비 -20%
- 응답 속도 +10%
- API 비용 절감

#### Task 3.3: 캐싱 전략 (선택적)
- **대상**:
  - Phase 1 (Direct RAG) 결과
  - Phase 2 (Validator) 검색 결과
  
- **방법**:
  - 메모리 캐시 (LRU Cache)
  - 또는 Redis (선택적)

**예상 효과**:
- 반복 질문 응답 속도 ×10
- API 비용 절감

---

### 우선순위 4: 보안 강화 (선택적, 1-2일)

#### Task 4.1: API 키 관리
- **현재**: `.env` 파일
- **개선**:
  - 환경 변수 검증
  - 키 로테이션 가이드
  - 민감 정보 로그 제외

#### Task 4.2: 입력 검증
- **개선**:
  - 질문 길이 제한 (예: 1000자)
  - SQL Injection 방지 (이미 안전)
  - Rate Limiting (선택적)

---

### 우선순위 5: 배포 자동화 (선택적, 1-2일)

#### Task 5.1: CI/CD 파이프라인
- **도구**: GitHub Actions (또는 GitLab CI)
- **단계**:
  1. 테스트 자동 실행 (pytest)
  2. 코드 품질 검사 (flake8, mypy)
  3. 문서 생성 (Sphinx)
  4. 배포 (Docker 또는 pip)

#### Task 5.2: Docker 컨테이너화 (선택적)
- **파일**: `Dockerfile`
- **내용**:
  - Python 3.13 base
  - 의존성 설치
  - 환경 변수 설정

---

## Task 상세

### Task 1.1: CHANGELOG 작성 (즉시 시작) ✅

**구조**:
```markdown
# Changelog

## [7.9.0] - 2025-11-25

### Added
- None 반환 제거: 항상 EstimationResult 반환
- Cursor Auto Fallback (Phase 3-4)
- 81개 테스트 (단위/통합/엣지/성능)

### Changed
- LLM Mode 동적 전환 (Property 패턴)
- Phase 2 유사도 임계값 강화 (0.95 → 0.85)

### Fixed
- ZeroDivisionError in judgment.py (0으로 나누기)

### Breaking Changes
- `EstimatorRAG.estimate()` 항상 EstimationResult 반환 (None 불가)

### Migration Guide
- Before: `if result is None: ...`
- After: `if not result.is_successful(): ...`
```

---

## 타임라인

### Week 1 (우선순위 1-2)
- Day 1-2: 문서화 (CHANGELOG, API 문서, 사용자 가이드)
- Day 3-4: 모니터링 (로깅 개선, 메트릭 수집)
- Day 5: 통합 테스트

### Week 2 (우선순위 3-5, 선택적)
- Day 1-3: 최적화 (Validator DB, 프롬프트, 캐싱)
- Day 4: 보안 강화
- Day 5: 배포 자동화

---

## 즉시 시작할 작업

**Task 1.1: CHANGELOG 작성** (5분)

이 작업을 먼저 시작하시겠습니까?

---

**작성자**: AI Assistant  
**검토자**: [TBD]  
**승인일**: 2025-11-25

---

**END OF PLAN**

