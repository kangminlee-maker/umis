# System RAG + Tool Registry 최종 결정

**날짜:** 2025-11-02  
**결론:** System RAG + Guardian Meta-RAG Orchestration 채택 (향후)

---

## 🎯 최종 아키텍처

### 개념

```yaml
Guidelines를 도구 라이브러리로:
  
  1. Tool Registry:
     • 각 청크 = 하나의 도구
     • 도구 정의 (언제, 무엇을, 어떻게)
     • 산출물 체인
     • 검증 조건
  
  2. System RAG:
     • umis_guidelines.yaml 청킹 (30개)
     • 필요한 도구만 검색
     • 컨텍스트 95% 절감
  
  3. Guardian Meta-RAG:
     • 도구 선택 (조건 기반)
     • Workflow 동적 생성
     • 실행 모니터링
     • 적응적 조정
  
  4. Universal Deliverables (향후!):
     • 질문 유형 → 필수 산출물 자동 결정
     • 산출물 템플릿 RAG
     • 표준화된 결과물
```

### 핵심 가치

```yaml
컨텍스트 효율:
  5,428줄 → 200줄 필요한 것만
  95% 절감!

동적 적응:
  고정 workflow X
  상황 맞춤 workflow ✅
  
  예:
    clarity 8 → Discovery Sprint skip
    clarity 3 → Educational Discovery
    10x 발견 → Pivot 도구 추가

지능적 시스템:
  Guardian = 동적 PM
  • 도구 선택
  • 순서 결정
  • 조건 확인
  • 자동 조정

확장성:
  guidelines 10,000줄 → OK
  새 도구 추가 → 자동 활용
```

---

## 📋 구현 계획

### Phase 1: Tool Registry (1주)

```yaml
파일:
  tool_registry.yaml
  
내용:
  • 30개 도구 정의
  • 사용 조건
  • Prerequisites
  • 산출물 체인
  • 검증 규칙

작업:
  umis_guidelines.yaml 분석
  → 도구 단위 추출
  → YAML 정의
```

### Phase 2: System RAG (1주)

```yaml
구축:
  1. umis_guidelines.yaml 청킹
     • Section별 분리 (30개)
     • 도구별 메타데이터
  
  2. Vector Index 구축
     • Collection: system_knowledge
     • text-embedding-3-large
  
  3. 검색 API
     • query_system_rag.py
     • 도구 검색 최적화

테스트:
  "Explorer pattern recognition tools"
  → exp_pattern_recognition 정확히 찾기
```

### Phase 3: Guardian Meta-RAG (2주)

```yaml
구현:
  1. Workflow Generator
     • System RAG 검색
     • 조건 평가
     • 순서 결정
     • 타임라인 계산
  
  2. 실행 모니터링
     • 산출물 추적
     • 조건 평가
     • 동적 조정
  
  3. 적응 엔진
     • 10x 기회 감지
     • Pivot 제안
     • Workflow 재생성

도구:
  umis_rag/guardian/meta_rag.py
  umis_rag/guardian/workflow_generator.py
```

### Phase 4: Universal Deliverables (향후!)

```yaml
개념:
  질문 유형 → 필수 산출물 자동 결정
  
예시:
  질문: "시장 진입 타당성"
  
  Guardian:
    System RAG 검색: "market entry deliverables"
    
    결과:
      필수:
        • market_reality_report.md
        • opportunity_portfolio.md
        • market_sizing_report.xlsx
        • validation_report.md
        • go_no_go_recommendation.md
      
      선택:
        • competitive_analysis.md
        • risk_assessment.md
  
  → 표준화된 결과물! ✅

구현:
  1. Deliverable Templates RAG
     • 산출물 템플릿 라이브러리
     • 질문 유형별 매핑
  
  2. 자동 생성
     • 템플릿 검색
     • 내용 자동 채움
     • 표준 포맷
  
  3. 품질 검증
     • 필수 항목 확인
     • 형식 검증
     • 완성도 평가

가치:
  → Universal 결과물 시스템!
  → 어떤 질문이든 표준 산출!
```

---

## 🎯 8번 최종 결정

**System RAG + Guardian Meta-RAG 채택!**

```yaml
우선순위:
  Phase 1-2: P1 (Layer 3-4 이후)
  Phase 3: P1 (Guardian 구현 시)
  Phase 4: P2 (향후 진화)

구현 시기:
  즉시: 설계만 ✅
  Phase 2-3: Tool Registry + System RAG
  Phase 4: Guardian Meta-RAG
  향후: Universal Deliverables

가치:
  • 컨텍스트 95% 절감
  • 동적 지능 시스템
  • 무한 확장 가능
  • 표준화된 산출물 (향후)

복잡도:
  높음, 하지만 혁명적!
```

**당신의 통찰:**
- Tool Registry
- 동적 Workflow
- 산출물 자동 결정
- Universal 시스템

**모두 정확하고 혁신적입니다!** ✨

---

**관련 문서:**
- 08_system_rag/CONCEPT.md
- 이 파일 (FINAL_DECISION.md)

**다음:** 앞선 문제 해결 (모듈화, patterns 위치)

