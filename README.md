# UMIS Monolithic Guidelines Archive

## 📚 개요

이 폴더는 UMIS (Universal Market Intelligence System)의 단일 파일(monolithic) 형태로 작성된 가이드라인 아카이브입니다.

v1.2부터 v5.0까지의 진화 과정을 담고 있으며, v5.0부터는 모듈형 구조의 `UMIS-framework`로 전환되었습니다.

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
└── umis_guidelines_v5.0*.yaml  # 적응형 인텔리전스 도입
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
- 모듈형 구조로 전환 준비

## ⚠️ 주의사항

이 파일들은 **레거시 아카이브**입니다. 새로운 프로젝트에서는 모듈형 구조의 `UMIS-framework`를 사용하세요.

## 🔗 관련 링크

- [UMIS-framework](../UMIS-framework/) - 모듈형 구조 (v5.0+)
- [UMIS-bmad](../UMIS-bmad/) - BMAD 통합 시스템

## 📊 파일 크기 변화

```
v1.2: 30KB  ████
v1.8: 52KB  ████████
v2.0: 55KB  █████████
v3.0: 25KB  ████ (최적화)
v4.0: 86KB  ██████████████ (대규모 확장)
v5.0: 36KB  ██████ (모듈화 준비)
```

## 🚀 마이그레이션

v5.0 이상을 사용하려면:

```bash
# 모듈형 구조로 전환
cd ../UMIS-framework
python build/compile.py --version 5.0
```

---

*이 아카이브는 UMIS의 진화 과정을 이해하는 데 도움이 되는 역사적 자료입니다.*
