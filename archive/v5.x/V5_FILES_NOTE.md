# v5.x 파일 구성 설명

## 🗂️ v5.0 파일들의 구성

v5.0은 파일 크기 제한으로 인해 작성 시 여러 파일로 분할되었다가 통합되었습니다:

### 📄 파일 목록

1. **`umis_guidelines_v5.0.yaml`** (93KB)
   - 완전한 통합 버전
   - 모든 내용을 포함한 최종 파일

2. **`umis_guidelines_v5.0_part1.yaml`** 
   - 시스템 개요 및 핵심 구성요소
   - 에이전트 정의 (MOwner, MAnalyst, MExplorer)

3. **`umis_guidelines_v5.0_part2.yaml`** 
   - 에이전트 정의 계속 (MQuant, MValidator, MCurator)
   - 협업 규칙

4. **`umis_guidelines_v5.0_part3.yaml`** 
   - 워크플로우 정의
   - 품질 관리 시스템

5. **`umis_guidelines_v5.0_additions.yaml`** 
   - v5.0 신규 기능
   - Adaptive Intelligence
   - Progress Guardian System
   - Data Integrity System

## 🔧 파일 생성 과정

```bash
# 토큰 제한으로 인한 분할 작성
1. part1 작성 → part2 작성 → part3 작성
2. 파일들 병합: cat part1 part2 part3 > v5.0.yaml
3. 추가 기능 작성: additions.yaml
4. 최종 통합: v5.0.yaml + additions.yaml
```

## 📌 사용 권장사항

- **일반 사용**: `umis_guidelines_v5.0.yaml` 사용
- **부분 참조**: 필요한 part 파일만 참조
- **신규 기능만**: `additions.yaml` 참조

## ⚡ v5.0 이후 버전들

### v5.1 시리즈 개요

v5.0 이후에도 단일 파일 구조를 유지하며 지속적으로 개선되었습니다:

1. **`umis_guidelines_v5.1.yaml`** (131KB)
   - Adaptive Clarification Protocol 정식 도입
   - 6단계 워크플로우 구체화
   - Progressive Narrowing 전략

2. **`umis_guidelines_v5.1.1.yaml`** (132KB)
   - 시장 기회의 두 가지 원천 명확화
   - Steve 역할 변경 (추론 → MECE 옵션)
   - 중립적 분석 프레임워크 강화

3. **`umis_guidelines_v5.1.2.yaml`** (138KB)
   - Albert가 MECE 담당으로 변경
   - Stage 간 연결성 강화
   - Albert → Steve 협업 패턴 확립

4. **`umis_guidelines_v5.1.3.yaml`** (136KB) - 현재 안정 버전
   - AI 친화적 최적화 (구조적 정리)
   - 가독성과 AI 이해도 균형
   - ChatGPT 프로젝트 활용 최적화

5. **`umis_v5.1.3_modular/`** (총 96KB) - 모듈화 버전
   - ChatGPT 최적화 모듈 구조
   - agents/ 디렉토리: 5개 에이전트 파일 (48KB)
   - workflows/ 디렉토리: 워크플로우 파일 (48KB)
   - MOwner 역할 정의 추가
   - 선택적 로딩으로 유연성 확보

## 🔧 파일 관리 전략

### 단일 파일 유지의 장점
- **통합성**: 모든 정보가 한 곳에
- **AI 친화적**: LLM이 전체 맥락 파악 용이
- **버전 관리**: 단순하고 명확한 버전 추적
- **사용 편의성**: 하나의 파일만 관리

### 크기 최적화 방법
- 중복 제거
- 구조적 정리
- 의미 유지하며 압축
- AI 이해도 손상 없이 최적화

## 📌 사용 권장사항

- **일반 사용**: 
  - 단일 파일: `umis_guidelines_v5.1.3.yaml` (전체 시스템)
  - 모듈화: `umis_v5.1.3_modular/` (선택적 로딩)
- **ChatGPT 활용**: 
  - 빠른 분석: 모듈화 버전의 최소 구성
  - 전체 분석: 단일 파일 또는 모든 모듈
- **선택 기준**:
  - 단일 파일: 전체 맥락이 중요한 경우
  - 모듈화: 효율성과 유연성이 필요한 경우

---

*UMIS는 사용 상황에 따라 단일 파일과 모듈화 버전을 모두 제공합니다.*
