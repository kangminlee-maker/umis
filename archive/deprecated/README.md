# Deprecated Files

**목적**: 루트 폴더와 동일한 구조로 deprecated 파일 보관  
**업데이트**: 2025-11-03

---

## 📁 구조

```
deprecated/
├── docs/           # deprecated된 docs 문서들
├── setup/          # deprecated된 setup 파일들 (향후)
├── scripts/        # deprecated된 scripts (향후)
└── README.md       # 이 파일
```

**원칙**: 루트 디렉토리와 **동일한 구조**를 유지

---

## 📝 파일 추가 규칙

파일이 deprecated될 때:

```bash
# 예시 1: docs 파일
umis/docs/old_protocol.md
  → archive/deprecated/docs/old_protocol_v6.2.md

# 예시 2: setup 파일 (향후)
umis/setup/old_setup.py
  → archive/deprecated/setup/old_setup_v6.2.py

# 예시 3: scripts 파일 (향후)
umis/scripts/old_script.py
  → archive/deprecated/scripts/old_script_v6.2.py
```

**권장**: 파일명에 버전 정보 추가

---

## 📄 현재 내용

### docs/
- `UMIS_v6.2_Complete_Guide.md` - v6.2 전체 가이드
- `UMIS v6.2 Executive Summary` - v6.2 요약
- `umis_format_comparison.md` - 포맷 비교

---

**Deprecated 날짜**: 2025-11-03  
**이유**: v7.0.0 릴리즈로 대체됨
