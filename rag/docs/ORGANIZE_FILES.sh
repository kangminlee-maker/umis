#!/bin/bash
# RAG 파일 정리 스크립트

echo "📁 UMIS RAG 파일 정리"
echo "═══════════════════════════════════════════════════════════════════════"

# 디렉토리 생성
mkdir -p rag_project/{architecture,planning,guides,analysis}

echo ""
echo "1️⃣ 아키텍처 문서 이동..."
mv umis_rag_architecture_v1.0.yaml rag_project/architecture/ 2>/dev/null
mv umis_rag_architecture_v1.1_enhanced.yaml rag_project/architecture/ 2>/dev/null
mv COMPLETE_RAG_ARCHITECTURE.md rag_project/architecture/ 2>/dev/null
mv umis_guidelines_v6.2_rag_enabled.yaml rag_project/architecture/ 2>/dev/null
echo "  ✅ 아키텍처 문서"

echo ""
echo "2️⃣ 구현 계획 이동..."
mv DETAILED_TASK_LIST.md rag_project/planning/ 2>/dev/null
mv IMPLEMENTATION_PLAN.md rag_project/planning/ 2>/dev/null
mv IMPLEMENTATION_ROADMAP.md rag_project/planning/ 2>/dev/null
echo "  ✅ 계획 문서"

echo ""
echo "3️⃣ 사용 가이드 이동..."
mv START_HERE.md rag_project/guides/ 2>/dev/null
mv CURSOR_QUICK_START.md rag_project/guides/ 2>/dev/null
mv SIMPLEST_WORKFLOW.md rag_project/guides/ 2>/dev/null
mv USAGE_COMPARISON.md rag_project/guides/ 2>/dev/null
mv SETUP_GUIDE.md rag_project/guides/ 2>/dev/null
echo "  ✅ 가이드 문서"

echo ""
echo "4️⃣ 분석 문서 이동..."
mv SPEC_REVIEW.md rag_project/analysis/ 2>/dev/null
mv MEMORY_AUGMENTED_RAG_ANALYSIS.md rag_project/analysis/ 2>/dev/null
mv ADVANCED_RAG_CHALLENGES.md rag_project/analysis/ 2>/dev/null
mv RAG_INTEGRATION_OPTIONS.md rag_project/analysis/ 2>/dev/null
echo "  ✅ 분석 문서"

echo ""
echo "5️⃣ 개발/배포 문서 이동..."
mv DEPLOYMENT_STRATEGY.md rag_project/planning/ 2>/dev/null
mv USER_DEVELOPER_WORKFLOW.md rag_project/planning/ 2>/dev/null
mv DEVELOPMENT_WORKFLOW.md rag_project/planning/ 2>/dev/null
echo "  ✅ 개발 문서"

echo ""
echo "6️⃣ 요약 문서 이동..."
mv PROJECT_SUMMARY.md rag_project/ 2>/dev/null
mv SESSION_SUMMARY.md rag_project/ 2>/dev/null
mv FINAL_SUMMARY.md rag_project/ 2>/dev/null
mv FINAL_STATUS_AND_NEXT_STEPS.md rag_project/ 2>/dev/null
mv CLEANUP_PLAN.md rag_project/ 2>/dev/null
echo "  ✅ 요약 문서"

echo ""
echo "7️⃣ README 업데이트..."
mv README_RAG.md rag_project/guides/ 2>/dev/null
echo "  ✅ README"

echo ""
echo "═══════════════════════════════════════════════════════════════════════"
echo "✅ 정리 완료!"
echo ""
echo "📁 정리된 구조:"
tree -L 2 rag_project/ 2>/dev/null || ls -R rag_project/
echo ""
