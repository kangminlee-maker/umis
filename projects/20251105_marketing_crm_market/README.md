# 국내 마케팅 CRM 툴 시장 분석

**프로젝트 ID**: `20251105_marketing_crm_market`  
**생성일**: 2025-11-05  
**상태**: 진행 중 (Discovery Sprint)  
**UMIS 버전**: v7.0.0

---

## 📌 프로젝트 개요

이 프로젝트는 **국내 마케팅 CRM 툴 시장**의 현황과 기회 요인을 UMIS v7.0.0 시스템으로 분석합니다.

### 핵심 질문
- 국내 마케팅 CRM 시장의 구조는?
- 주요 플레이어와 경쟁 구도는?
- 시장 규모와 성장률은?
- 실행 가능한 기회 요인은?

### 분석 범위
- **제품**: 마케팅 CRM 툴 (이메일, 소셜, 캠페인, 고객 데이터 관리)
- **지역**: 대한민국
- **고객**: 기업 (B2B)
- **기간**: 2025년 현재 + 향후 3-5년 전망

---

## 🗂️ 프로젝트 구조

```
20251105_marketing_crm_market/
├── 00_overview/              # 프로젝트 개요
│   ├── project_charter.md    # 프로젝트 헌장
│   ├── progress_tracker.md   # 진행 추적
│   └── README.md             # 이 파일
├── 01_discovery/             # Discovery Sprint
│   ├── parallel_discoveries/ # 에이전트별 발견
│   └── checkpoints/          # 체크포인트
├── 02_analysis/              # 본격 분석
│   ├── validator/            # Rachel 데이터 검증
│   ├── quantifier/           # Bill 시장 규모
│   ├── observer/             # Albert 구조 분석
│   └── explorer/             # Steve 기회 발굴
├── 03_insights/              # 핵심 발견
│   └── supporting_data/      # 근거 자료
└── 99_decisions/             # 의사결정 기록
    └── rationale/            # 결정 근거
```

---

## 👥 참여 에이전트

| Agent | 역할 | 담당 영역 |
|-------|------|-----------|
| **Albert** (Observer) | 시장 구조 관찰 | 거래 패턴, 경쟁 구조, 가치사슬 |
| **Steve** (Explorer) | 기회 발굴 | RAG 기반 패턴 검색, 기회 가설 |
| **Bill** (Quantifier) | 시장 규모 계산 | SAM 4가지 방법, 성장률 분석 |
| **Rachel** (Validator) | 데이터 검증 | 출처 검증, 신뢰도 평가 |
| **Stewart** (Guardian) | 프로세스 감독 | 진행 모니터링, 품질 보증 |

---

## 🎯 현재 상태

### Phase 0: Discovery Sprint (진행 중)

**목표**: 사용자와의 대화를 통해 프로젝트 목표와 범위 명확화

**진행률**: 10%

**다음 단계**:
1. 초기 질문 세션 (목적, 세그먼트, 시한 확인)
2. 5-Agent 병렬 탐색 (시장 초기 스캔)
3. 발견사항 수렴 및 방향 확정

---

## 📊 주요 산출물 (예정)

### Discovery Sprint
- [ ] 초기 시장 스캔 보고서
- [ ] 명확도 진화 로그
- [ ] 방향성 수렴 보고서

### Phase 1: Market Mapping
- [ ] Market Reality Report (Albert)
- [ ] 시장 구조 매트릭스
- [ ] 경쟁 지형도

### Phase 2: Dimensional Analysis
- [ ] 13개 차원 심층 분석
- [ ] 차원 간 상호작용 맵
- [ ] SAM 계산서 (Bill)

### Phase 3: Dynamic Patterns
- [ ] 기회 포트폴리오 (Steve)
- [ ] 시나리오 플래닝
- [ ] 기술/규제 영향 분석

### Phase 4: Strategy Synthesis
- [ ] 최종 전략 보고서
- [ ] 실행 로드맵
- [ ] 리스크 매트릭스

---

## 🔍 UMIS 핵심 원칙 적용

### 완전한 추적성 (Traceability)
- 모든 결론 → 원본 데이터 역추적 가능
- source_id (SRC_YYYYMMDD_NNN) 부여
- 추정치 논리 투명 문서화 (EST_NNN)

### 재검증 가능성 (Reproducibility)
- Excel 함수 100% (하드코딩 금지)
- 4가지 방법 ±30% 수렴
- 검증 체인 완결

### 적응형 접근 (Adaptive)
- 낮은 명확도(45%)로 시작
- Discovery를 통한 목표 진화
- 발견에 따른 피벗 허용

---

## 📅 타임라인

| Phase | 기간 | 예상 완료일 |
|-------|------|-------------|
| Discovery Sprint | 1-3일 | 2025-11-08 |
| Phase 1 | 5일 | 2025-11-13 |
| Phase 2 | 5일 | 2025-11-18 |
| Phase 3 | 5일 | 2025-11-23 |
| Phase 4 | 5일 | 2025-11-28 |

**전체 예상 기간**: 3-4주

---

## 📖 참고 문서

- **UMIS 가이드라인**: `/umis.yaml`
- **시스템 아키텍처**: `/UMIS_ARCHITECTURE_BLUEPRINT.md`
- **사용 예시**: `/umis_examples.yaml`
- **패턴 DB**: `/data/raw/umis_business_model_patterns.yaml`
- **추정 방법론**: `/docs/GUESTIMATION_FRAMEWORK.md`

---

## 🔄 최종 업데이트

**날짜**: 2025-11-05  
**업데이트**: Stewart (Guardian)  
**변경 사항**: 프로젝트 초기화 완료, Discovery Sprint 시작

---

**Note**: 이 프로젝트는 UMIS v7.0.0의 모든 표준과 프로토콜을 준수하며, 완전한 추적성과 재검증 가능성을 보장합니다.

