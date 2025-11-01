# ========================================
# UMIS RAG Makefile
# ========================================

.PHONY: help dev dev-stop rebuild test query stats clean release

help:
	@echo "📚 UMIS RAG 명령어"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo ""
	@echo "개발:"
	@echo "  make dev          - 개발 모드 (YAML 자동 반영)"
	@echo "  make dev-stop     - 개발 모드 중단"
	@echo "  make rebuild      - 전체 재구축"
	@echo ""
	@echo "테스트:"
	@echo "  make test         - 검색 테스트"
	@echo "  make query QUERY='플랫폼' - 빠른 검색"
	@echo "  make stats        - 인덱스 통계"
	@echo ""
	@echo "배포:"
	@echo "  make release      - 배포 패키지"
	@echo ""
	@echo "관리:"
	@echo "  make clean        - 청크 삭제"
	@echo ""

dev:
	@echo "🚀 개발 모드 시작"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo ""
	@echo "💡 YAML 수정 → 2초 → 자동 반영!"
	@echo "⚠️  종료: Ctrl+C"
	@echo ""
	@source venv/bin/activate && python scripts/dev_watcher.py

dev-stop:
	@pkill -f dev_watcher.py || echo "✅ 중단됨"

rebuild:
	@echo "🔄 전체 재구축..."
	@source venv/bin/activate && \
		python scripts/01_convert_yaml.py && \
		python scripts/02_build_index.py --agent steve
	@echo "✅ 완료!"

test:
	@source venv/bin/activate && python scripts/03_test_search.py --agent steve

query:
	@source venv/bin/activate && python scripts/query_rag.py pattern "$(QUERY)"

stats:
	@source venv/bin/activate && python -c "import chromadb; client = chromadb.PersistentClient(path='data/chroma'); cols = client.list_collections(); print('📊 RAG 통계:'); [print(f'  {col.name}: {col.count()} docs') for col in cols]"

clean:
	@rm -rf data/chunks/* data/chroma/*
	@echo "✅ 정리 완료"

release:
	@echo "📦 배포 패키지 생성..."
	@python scripts/build_release.py

