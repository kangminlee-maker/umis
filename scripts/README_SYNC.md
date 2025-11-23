# umis.yaml → RAG 동기화 스크립트

## 🎯 목적

umis.yaml을 수정하면 **자동으로** System RAG에 반영되도록 하는 파이프라인

---

## 🚀 빠른 시작

### 기본 사용
```bash
# umis.yaml 수정 후
python3 scripts/sync_umis_to_rag.py

# 완료! (10초)
```

### 또는 배치 스크립트
```bash
./scripts/quick_sync.sh
```

---

## 📋 스크립트 목록

| 스크립트 | 목적 | 사용 시점 |
|---------|------|----------|
| **sync_umis_to_rag.py** | 메인 동기화 | umis.yaml 수정 후 (필수) |
| **rollback_rag.py** | 롤백 | 문제 발생 시 |
| **quick_sync.sh** | 간단 배치 | 빠른 실행 |
| migrate_umis_to_rag.py | 변환 로직 | (내부 사용) |
| extract_agent_sections.py | Agent 추출 | (내부 사용) |

---

## 🔄 워크플로우

```
umis.yaml 수정
    ↓
sync_umis_to_rag.py
    ↓ (자동)
백업 생성
    ↓
tool_registry.yaml 생성
    ↓
검증
    ↓
System RAG 재구축
    ↓
최종 검증
    ↓
✅ 완료 또는 ❌ 롤백
```

---

## 📚 상세 가이드

- **개발자 가이드**: `docs/guides/UMIS_YAML_DEVELOPMENT_GUIDE.md`
- **파이프라인 설계**: `dev_docs/UMIS_YAML_TO_RAG_PIPELINE.md`
- **변환 규칙**: `config/migration_rules.yaml`

---

## ⚠️ 중요

**편집 금지**:
- ❌ `config/tool_registry.yaml` (자동 생성)
- ❌ `data/chroma/*` (자동 구축)

**편집 가능**:
- ✅ `umis.yaml` (Source of Truth)
- ✅ `config/migration_rules.yaml` (설정)

---

**문서 끝**






