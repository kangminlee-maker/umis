# Estimator 개발 문서

Fermi Estimator 및 벤치마크 시스템 관련 개발 문서입니다.

## 주요 문서

### 벤치마크 및 평가
- `BENCHMARK_RESULTS_ANALYSIS.md`: 벤치마크 결과 분석
- `PHASE3_MODEL_ANALYSIS.md`: Phase 3 모델 분석
- `C_GRADE_ANALYSIS.md`: C등급 케이스 분석
- `CD_GRADE_IMPROVEMENT_REPORT.md`: C/D등급 개선 보고서
- `UNIT_ECONOMICS_BENCHMARK.md`: 단위경제학 벤치마크
- `UNIT_ECONOMICS_FINAL.md`: 단위경제학 최종 보고서

### 설계 및 전략
- `ESTIMATOR_AGENT_DESIGN.md`: Estimator Agent 설계
- `ESTIMATOR_DEPLOYMENT_STRATEGY.md`: 배포 전략
- `ESTIMATOR_SINGLE_SOURCE_DESIGN.md`: Single Source 설계
- `ESTIMATOR_QUANTIFIER_SEPARATION_V7.5.0.md`: Quantifier 분리 (v7.5.0)
- `ESTIMATION_POLICY_CLARIFICATION.md`: 추정 정책 명확화

### 기능 가이드
- `SOFT_CONSTRAINT_WARNING_GUIDE.md`: Soft Constraint 경고 시스템 (v7.8.0)
- `FAILURE_PATTERN_INTEGRATION_V7_8_0.md`: 실패 패턴 통합 (v7.8.0)

## 주요 기능

- 5-Phase Estimation Architecture
- Native Mode + Fermi Mode
- 12개 비즈니스 지표 추정
- 품질 자동 평가 (A-F 등급)
- 학습 시스템 (Learned Rules)

## 벤치마크 데이터

- `benchmark_*.json`: 벤치마크 결과 데이터

## 관련 코드

- `umis_rag/agents/estimator/`
- `scripts/benchmark_*.py`

