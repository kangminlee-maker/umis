# UMIS Monolithic Guidelines

## 📚 개요

이 폴더는 UMIS (Universal Market Intelligence System)의 단일 파일(monolithic) 형태로 작성된 가이드라인입니다.

v1.2부터 현재 v5.1.3까지의 진화 과정을 담고 있으며, 지속적으로 단일 파일 형태로 유지·발전되고 있습니다.

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
└── umis_guidelines_v5.1.3.yaml # AI 친화적 최적화 (현재 버전)
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
  
- **v5.1.3**: AI 친화적 최적화
  - 1단계 최적화로 7.7% 크기 절감
  - AI 이해도 유지하면서 토큰 사용량 감소
  - ChatGPT 프로젝트 활용 가이드 포함
  
- **v5.1.4**: ChatGPT 최적화 모듈화 (현재)
  - 적절한 수준의 모듈화로 유연성 확보
  - 에이전트별 파일 분리 (5개, 48KB)
  - 워크플로우 단일 파일 (48KB)
  - MOwner 역할 정의 포함
  - 총 96KB (단일 파일 대비 29% 절감)

## 💡 사용 권장사항

- **최신 버전 선택**:
  - 단일 파일: `umis_guidelines_v5.1.3.yaml` (136KB) - 전체 시스템 한 번에 로드
  - 모듈화: `umis_v5.1.4_modular/` (총 96KB) - 선택적 로드로 유연성 확보
- **ChatGPT 프로젝트**: Custom Instructions와 함께 활용
- **용도별 선택**:
  - 빠른 탐색: 모듈화 버전의 최소 구성 (workflow + albert + steve)
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
```

## 🚀 빠른 시작

최신 버전으로 시작하려면:

```bash
# 1. 최신 파일 사용
umis_guidelines_v5.1.3.yaml

# 2. ChatGPT 프로젝트 설정
chatgpt_custom_instructions.txt 내용 복사
umis_guidelines_v5.1.3.yaml 파일 첨부

# 3. 테스트 프롬프트
"[시장명]을 UMIS로 분석해주세요"
```

## 📈 발전 방향

- **단일 파일 유지**: 모듈화 대신 최적화를 통한 효율성 추구
- **AI 친화적**: LLM이 이해하고 활용하기 쉬운 구조
- **지속적 개선**: 사용자 피드백 기반 업데이트

---

*UMIS는 지속적으로 진화하고 있습니다. 최신 버전을 사용하여 더 나은 시장 분석을 경험하세요.*
