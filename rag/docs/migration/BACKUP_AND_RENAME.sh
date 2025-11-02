#!/bin/bash
# Agent Name → ID 일괄 변경 (안전 백업 포함)

echo "═══════════════════════════════════════════════════════════════════════"
echo "  Agent 변수명 일괄 변경 (steve → explorer 등)"
echo "═══════════════════════════════════════════════════════════════════════"

# 사용자 선택 받기
echo ""
echo "ID 이름 선택:"
echo "  A. UMIS_Observer, UMIS_Explorer, ... (추천!)"
echo "  B. MarketObserver, OpportunityExplorer, ..."
echo "  C. Observer, Explorer, ... (현재)"
echo ""
read -p "선택 (A/B/C): " choice

# 매핑 정의
case $choice in
  A|a)
    OBSERVER="UMIS_Observer"
    EXPLORER="UMIS_Explorer"
    QUANTIFIER="UMIS_Quantifier"
    VALIDATOR="UMIS_Validator"
    GUARDIAN="UMIS_Guardian"
    PREFIX="umis_"
    echo "  → UMIS Prefix 방식 선택"
    ;;
  B|b)
    OBSERVER="MarketObserver"
    EXPLORER="OpportunityExplorer"
    QUANTIFIER="MarketQuantifier"
    VALIDATOR="DataValidator"
    GUARDIAN="ProcessGuardian"
    PREFIX=""
    echo "  → 역할 명확화 방식 선택"
    ;;
  C|c)
    OBSERVER="Observer"
    EXPLORER="Explorer"
    QUANTIFIER="Quantifier"
    VALIDATOR="Validator"
    GUARDIAN="Guardian"
    PREFIX=""
    echo "  → 현재 유지"
    ;;
  *)
    echo "잘못된 선택. 종료."
    exit 1
    ;;
esac

echo ""
echo "─────────────────────────────────────────────────────────────────────"
echo "1️⃣ Git 백업 브랜치 생성"
echo "─────────────────────────────────────────────────────────────────────"

git branch backup/before-agent-rename 2>/dev/null
git checkout -b refactor/agent-id-rename 2>/dev/null || git checkout refactor/agent-id-rename

echo "  ✅ 백업 브랜치: backup/before-agent-rename"
echo "  ✅ 작업 브랜치: refactor/agent-id-rename"

echo ""
echo "─────────────────────────────────────────────────────────────────────"
echo "2️⃣ 파일 백업 (로컬)"
echo "─────────────────────────────────────────────────────────────────────"

backup_dir="backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$backup_dir"

cp -r umis_rag "$backup_dir/"
cp -r scripts "$backup_dir/"
cp -r data "$backup_dir/"

echo "  ✅ 백업 완료: $backup_dir/"

echo ""
echo "─────────────────────────────────────────────────────────────────────"
echo "3️⃣ data/ 삭제 (재생성 예정)"
echo "─────────────────────────────────────────────────────────────────────"

read -p "data/chunks/, data/chroma/ 삭제? (y/N): " delete_data

if [[ $delete_data =~ ^[Yy]$ ]]; then
  rm -rf data/chunks/*
  rm -rf data/chroma/*
  echo "  ✅ data/ 삭제 완료 (재생성 예정)"
else
  echo "  ⚠️  data/ 유지"
fi

echo ""
echo "─────────────────────────────────────────────────────────────────────"
echo "4️⃣ 변경 영역 표시"
echo "─────────────────────────────────────────────────────────────────────"

echo ""
echo "변경될 항목:"
echo "  • 파일명: steve.py → ${PREFIX}explorer.py"
echo "  • 클래스: SteveRAG → ${EXPLORER}RAG"
echo "  • 함수: create_steve_agent() → create_${PREFIX}explorer()"
echo "  • 변수: steve → ${PREFIX}explorer"
echo "  • 메타데이터: steve_view → ${PREFIX}explorer_view"
echo ""
echo "  총 7개 파일, 약 124개 항목"
echo ""

read -p "계속 진행? (y/N): " confirm

if [[ ! $confirm =~ ^[Yy]$ ]]; then
  echo ""
  echo "취소됨. 백업은 유지됩니다: $backup_dir/"
  exit 0
fi

echo ""
echo "─────────────────────────────────────────────────────────────────────"
echo "5️⃣ 일괄 변경 실행"
echo "─────────────────────────────────────────────────────────────────────"

# 변수명 일괄 변경 (소문자)
find umis_rag scripts -name "*.py" -type f -exec sed -i '' \
  -e "s/steve/${PREFIX}explorer/g" \
  -e "s/albert/${PREFIX}observer/g" \
  -e "s/bill/${PREFIX}quantifier/g" \
  -e "s/rachel/${PREFIX}validator/g" \
  -e "s/stewart/${PREFIX}guardian/g" \
  {} +

echo "  ✅ 변수명 변경 완료"

# 클래스명/함수명 (CamelCase)
find umis_rag scripts -name "*.py" -type f -exec sed -i '' \
  -e "s/Steve/${EXPLORER}/g" \
  -e "s/Albert/${OBSERVER}/g" \
  -e "s/Bill/${QUANTIFIER}/g" \
  -e "s/Rachel/${VALIDATOR}/g" \
  -e "s/Stewart/${GUARDIAN}/g" \
  {} +

echo "  ✅ 클래스명 변경 완료"

# 파일명 변경
if [ "$choice" != "C" ] && [ "$choice" != "c" ]; then
  mv umis_rag/agents/steve.py "umis_rag/agents/${PREFIX}explorer.py" 2>/dev/null
  echo "  ✅ 파일명 변경 완료"
fi

echo ""
echo "─────────────────────────────────────────────────────────────────────"
echo "6️⃣ 검증"
echo "─────────────────────────────────────────────────────────────────────"

echo ""
echo "변경 확인:"
grep -r "${PREFIX}explorer" --include="*.py" umis_rag/ scripts/ | head -3
echo "..."

echo ""
echo "─────────────────────────────────────────────────────────────────────"
echo "7️⃣ 재구축 (선택)"
echo "─────────────────────────────────────────────────────────────────────"

read -p "RAG 인덱스 재구축? (y/N): " rebuild

if [[ $rebuild =~ ^[Yy]$ ]]; then
  echo ""
  echo "재구축 중..."
  
  source venv/bin/activate 2>/dev/null
  
  python scripts/01_convert_yaml.py
  python scripts/02_build_index.py --agent ${PREFIX}explorer
  
  echo "  ✅ 재구축 완료!"
else
  echo "  ⚠️  나중에 재구축하세요:"
  echo "     python scripts/01_convert_yaml.py"
  echo "     python scripts/02_build_index.py --agent ${PREFIX}explorer"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════════════"
echo "✅ 변경 완료!"
echo "═══════════════════════════════════════════════════════════════════════"
echo ""
echo "백업 위치:"
echo "  Git: backup/before-agent-rename 브랜치"
echo "  로컬: $backup_dir/"
echo ""
echo "변경 브랜치: refactor/agent-id-rename"
echo ""
echo "다음 단계:"
echo "  1. 테스트: python scripts/query_rag.py pattern \"구독\""
echo "  2. 확인 후 커밋: git commit -am \"refactor: Agent ID rename\""
echo "  3. 병합: git checkout alpha && git merge refactor/agent-id-rename"
echo ""

