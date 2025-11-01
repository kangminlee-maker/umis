#!/bin/bash
# UMIS RAG Quick Start

cd ~/Documents/AI_dev/umis-main
source venv/bin/activate

# IPython 실행
ipython -i -c "
print('✅ UMIS RAG 환경')
print('='*70)
print()
print('빠른 시작:')
print('  from umis_rag.agents.steve import create_steve_agent')
print('  steve = create_steve_agent()')
print('  steve.search_patterns(\"구독 서비스\")')
print()
print('자동 리로드: YAML/코드 수정 → 즉시 반영!')
print('='*70)
print()

# 자동 리로드 활성화
%load_ext autoreload
%autoreload 2
"
