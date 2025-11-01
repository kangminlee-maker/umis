#!/bin/bash
# 최종 정리 스크립트

echo "🧹 최종 파일 정리"
echo "═══════════════════════════════════════════════════════════════════════"

# RAG 관련 파일들을 rag_project로
echo ""
echo "1️⃣ RAG 가이드 이동..."
mv LIGHTEST_SETUP.md rag_project/guides/ 2>/dev/null && echo "  ✅ LIGHTEST_SETUP.md"
mv QUICK_START.md rag_project/guides/ 2>/dev/null && echo "  ✅ QUICK_START.md"

# 스크립트 확인
echo ""
echo "2️⃣ 스크립트 정리..."
mv ORGANIZE_FILES.sh rag_project/ 2>/dev/null && echo "  ✅ ORGANIZE_FILES.sh (보관)"

# 루트 정리
echo ""
echo "3️⃣ 루트 폴더 최종 상태:"
echo ""
echo "  유지할 파일:"
echo "    ✅ START_HERE.md (RAG 시작점)"
echo "    ✅ README.md (프로젝트 메인)"
echo "    ✅ CHANGELOG.md (UMIS 버전 이력)"
echo "    ✅ IMPLEMENTATION_SUMMARY.md (UMIS v6.2)"
echo ""
echo "  스크립트/설정:"
echo "    ✅ quick_umis.sh (빠른 시작)"
echo "    ✅ setup.sh (초기 설정)"
echo "    ✅ Makefile (명령어)"
echo "    ✅ umis_rag_simple.py (단일 파일)"
echo ""
echo "  YAML 파일:"
echo "    ✅ umis_guidelines_v6.2.yaml"
echo "    ✅ umis_business_model_patterns_v6.2.yaml"
echo "    ✅ umis_disruption_patterns_v6.2.yaml"
echo "    ✅ umis_ai_guide_v6.2.yaml"
echo "    ✅ umis_deliverable_standards_v6.2.yaml"
echo "    ✅ umis_examples_v6.2.yaml"

echo ""
echo "═══════════════════════════════════════════════════════════════════════"
echo "✅ 정리 완료!"
echo ""
echo "📁 최종 구조:"
echo "  루트: 핵심 파일만 (START_HERE, README, 스크립트, YAML)"
echo "  rag_project/: 모든 RAG 문서 (26개)"
echo ""
