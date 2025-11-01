# ========================================
# UMIS RAG Makefile
# ========================================
# 
# 간단한 명령어로 모든 작업 수행
#
# 사용법:
#   make dev          - 개발 모드 (Hot-Reload)
#   make rebuild      - 전체 재구축
#   make test         - 검색 테스트
#   make release      - 배포 패키지
#
# ========================================

.PHONY: help dev dev-stop rebuild test query stats clean release install

# 기본 명령 (help)
help:
	@echo "📚 UMIS RAG 명령어"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo ""
	@echo "개발:"
	@echo "  make dev          - 개발 모드 시작 (YAML 자동 반영)"
	@echo "  make dev-stop     - 개발 모드 중단"
	@echo "  make rebuild      - 전체 재구축"
	@echo ""
	@echo "테스트:"
	@echo "  make test         - 검색 테스트"
	@echo "  make query QUERY='플랫폼' - 빠른 검색"
	@echo "  make stats        - 인덱스 통계"
	@echo ""
	@echo "배포:"
	@echo "  make release VERSION=1.1.2 - 배포 패키지 생성"
	@echo ""
	@echo "관리:"
	@echo "  make clean        - 청크 및 인덱스 삭제"
	@echo ""

# 개발 모드
dev:
	@echo "🚀 UMIS 개발 모드 시작"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo ""
	@echo "💡 YAML 파일 수정 시 자동으로 RAG 업데이트됩니다."
	@echo "📁 감시 디렉토리: data/raw/"
	@echo "⚠️  종료: make dev-stop"
	@echo ""
	@source venv/bin/activate && python scripts/dev_watcher.py

dev-stop:
	@pkill -f dev_watcher.py || true
	@echo "✅ 개발 모드 중단"

# 전체 재구축
rebuild:
	@echo "🔄 YAML → 청크 변환..."
	@source venv/bin/activate && python scripts/01_convert_yaml.py
	@echo ""
	@echo "🔄 벡터 인덱스 구축..."
	@source venv/bin/activate && python scripts/02_build_index.py --agent steve
	@echo ""
	@echo "✅ 전체 재구축 완료!"

# 테스트
test:
	@echo "🧪 검색 테스트 실행..."
	@source venv/bin/activate && python scripts/03_test_search.py --agent steve

# 빠른 검색 (예: make query QUERY="플랫폼")
query:
	@source venv/bin/activate && python scripts/query_rag.py pattern "$(QUERY)"

# 통계
stats:
	@echo "📊 UMIS RAG 통계"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@source venv/bin/activate && python -c "\
	import chromadb;\
	from pathlib import Path;\
	client = chromadb.PersistentClient(path='data/chroma');\
	cols = client.list_collections();\
	print(f'\\n  Collections: {len(cols)}');\
	for col in cols:\
	    print(f'    • {col.name}: {col.count()} documents');\
	print()"

# 정리
clean:
	@echo "🗑️  청크 및 인덱스 삭제 중..."
	@rm -rf data/chunks/*
	@rm -rf data/chroma/*
	@echo "✅ 정리 완료!"
	@echo "⚠️  다시 사용하려면: make rebuild"

# 배포 패키지 생성
release:
	@echo "📦 배포 패키지 생성 (v$(VERSION))"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo ""
	@echo "⚠️  build_release.py 스크립트가 필요합니다."
	@echo "    (향후 구현 예정)"
	@echo ""
	@echo "수동 패키징:"
	@echo "  1. git tag v$(VERSION)"
	@echo "  2. 필요 파일 복사"
	@echo "  3. ZIP 생성"

# 설치 (새 사용자용)
install:
	@echo "🔧 UMIS RAG 설치"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@./setup.sh

