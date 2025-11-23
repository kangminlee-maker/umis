#!/bin/bash
# ========================================
# umis.yaml → RAG 빠른 동기화
# ========================================

echo "🚀 umis.yaml → RAG 동기화 시작"
echo ""

# 1. 현재 디렉토리 확인
if [ ! -f "umis.yaml" ]; then
    echo "❌ umis.yaml이 없습니다."
    echo "   프로젝트 루트에서 실행하세요."
    exit 1
fi

# 2. 백업
echo "💾 백업 중..."
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
mkdir -p config/backups
if [ -f "config/tool_registry.yaml" ]; then
    cp config/tool_registry.yaml "config/backups/tool_registry_${TIMESTAMP}.yaml"
    echo "   ✅ config/backups/tool_registry_${TIMESTAMP}.yaml"
fi
echo ""

# 3. 변환
echo "🔧 umis.yaml → tool_registry.yaml 변환 중..."
python3 scripts/migrate_umis_to_rag.py

if [ $? -ne 0 ]; then
    echo "❌ 변환 실패"
    exit 1
fi

# 4. RAG 재구축
echo ""
echo "🔨 System RAG 재구축 중..."
python3 scripts/build_system_knowledge.py

if [ $? -ne 0 ]; then
    echo "❌ RAG 재구축 실패"
    echo ""
    echo "롤백:"
    echo "  python3 scripts/rollback_rag.py"
    exit 1
fi

# 5. 검증
echo ""
echo "🧪 검증 중..."
python3 scripts/query_system_rag.py --stats > /dev/null 2>&1

if [ $? -ne 0 ]; then
    echo "❌ RAG 검증 실패"
    exit 1
fi
echo "   ✅ 검색 테스트 통과"

echo ""
echo "=" 
echo "✅ 동기화 완료!"
echo "="
echo ""
echo "다음 단계:"
echo "  python3 scripts/query_system_rag.py tool:observer:complete"
echo ""






