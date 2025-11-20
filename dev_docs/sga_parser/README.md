# SGA Parser 개발 문서

판매비와관리비(SGA) 파싱 시스템 관련 개발 문서입니다.

## 주요 문서

- `SGA_PARSER_FINAL_GUIDE.md`: 파서 사용 가이드
- `SGA_QUALITY_SYSTEM.md`: 품질 보증 시스템
- `README_SGA_PARSER.md`: 파서 개요
- `BATCH_PARSING_FINAL_REPORT.md`: 배치 파싱 결과
- `OPTIMIZED_PARSER_SUMMARY.md`: 최적화 요약
- `SECTION_SELECTION_LOGIC.md`: 섹션 선택 로직
- `GS리테일_파싱_실수_분석.md`: 파싱 에러 케이스 분석

## 주요 기능

- LLM 기반 SGA 항목 추출
- 다단계 파싱 파이프라인 (Phase 0-4)
- 품질 자동 평가 (A-F 등급)
- 배치 처리 및 재시도 로직

## 하위 시스템

### Learning System (`learning_system/`)
SGA 파싱 과정에서 발전된 학습 시스템

- Learned Rules (학습된 규칙)
- Pattern Recognition
- Quality Feedback Loop
- Continuous Improvement

## 관련 코드

- `umis_rag/parsers/sga/`
- `umis_rag/learning/`
- `scripts/parse_*.py`
- `config/learned_sga_patterns.yaml`

