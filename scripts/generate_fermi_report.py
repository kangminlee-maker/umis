#!/usr/bin/env python3
"""
Fermi 평가 결과로부터 상세 보고서 생성
"""

import json
import sys
from datetime import datetime

# JSON 파일 읽기
json_file = sys.argv[1] if len(sys.argv) > 1 else 'fermi_comprehensive_evaluation_20251121_161120.json'

with open(json_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

# 보고서 생성
report_file = f"docs/FERMI_TEST_DETAILED_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

with open(report_file, 'w', encoding='utf-8') as f:
    f.write("# Fermi 추정 종합 평가 - 상세 보고서\n\n")
    f.write(f"**작성일**: {data['metadata']['timestamp']}\n\n")
    f.write("---\n\n")
    
    # 개요
    f.write("## 📋 테스트 개요\n\n")
    f.write(f"- **평가 방식**: AI 기준선 비교\n")
    f.write(f"- **테스트 모델**: {data['metadata']['models_tested']}개\n")
    f.write(f"- **문제 수**: {len(data['metadata']['problems'])}개\n\n")
    
    f.write("### 평가 기준\n\n")
    for criterion, desc in data['metadata']['evaluation_criteria'].items():
        f.write(f"- **{criterion}**: {desc}\n")
    
    f.write("\n---\n\n")
    
    # 최종 순위
    f.write("## 🏆 최종 종합 순위 (3개 문제 평균)\n\n")
    f.write("| 순위 | 모델 | 평균 점수 | 정확도 | 분해 | 논리 |\n")
    f.write("|------|------|----------|--------|------|------|\n")
    
    for i, m in enumerate(data['summary']['by_model'], 1):
        marker = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else ""
        f.write(f"| {marker}{i} | {m['model']} | {m['avg_total']:.1f}/100 | {m['avg_accuracy']:.1f}/40 | {m['avg_decomp']:.1f}/30 | {m['avg_logic']:.1f}/30 |\n")
    
    f.write("\n")
    
    # 주요 발견
    f.write("## 💡 주요 발견\n\n")
    
    top_model = data['summary']['by_model'][0]
    f.write(f"### 🥇 1위: {top_model['model']}\n\n")
    f.write(f"- **평균 점수**: {top_model['avg_total']:.1f}/100\n")
    f.write(f"- **정확도**: {top_model['avg_accuracy']:.1f}/40\n")
    f.write(f"- **분해 품질**: {top_model['avg_decomp']:.1f}/30\n")
    f.write(f"- **논리 일관성**: {top_model['avg_logic']:.1f}/30\n\n")
    
    # 문제별 상세
    for problem_id in data['metadata']['problems']:
        problem_def = data['problems'][problem_id]
        f.write(f"\n---\n\n")
        f.write(f"## 🎯 문제: {problem_def['name']}\n\n")
        f.write(f"**정답**: {problem_def['ground_truth']:,} {problem_def['unit']}\n\n")
        
        # AI 기준선
        ai = problem_def['ai_baseline']
        f.write(f"### AI 기준선 (Assistant)\n\n")
        f.write(f"- **추정값**: {ai['estimate']:,} {problem_def['unit']}\n")
        f.write(f"- **오차율**: {ai['error_rate']*100:.1f}%\n\n")
        
        f.write("**분해 과정**:\n\n")
        for i, step in enumerate(ai['decomposition'], 1):
            f.write(f"{i}. **{step['step']}**: {step['value']:,}\n")
            f.write(f"   - 가정: {step['assumption']}\n")
        
        f.write("\n**장점**:\n")
        for strength in ai['strengths']:
            f.write(f"- {strength}\n")
        
        f.write("\n**약점**:\n")
        for weakness in ai['weaknesses']:
            f.write(f"- {weakness}\n")
        
        f.write("\n")
        
        # 모델별 결과
        problem_results = [r for r in data['results'] if r['problem'] == problem_def['name']]
        problem_results.sort(key=lambda x: x['total_score'], reverse=True)
        
        f.write(f"### 모델 평가 결과\n\n")
        f.write(f"| 순위 | 모델 | 추정값 | 오차 | 총점 | 정확도 | 분해 | 논리 |\n")
        f.write(f"|------|------|--------|------|------|--------|------|------|\n")
        
        for i, r in enumerate(problem_results, 1):
            if r['accuracy']['score'] > 0 and 'model_error_pct' in r['accuracy']:
                error_pct = r['accuracy']['model_error_pct']
            else:
                error_pct = 999
            
            marker = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else ""
            f.write(f"| {marker}{i} | {r['model']} | {r['value']:,} | {error_pct:.1f}% | {r['total_score']}/100 | {r['accuracy']['score']}/40 | {r['decomposition_quality']['score']}/30 | {r['logic_coherence']['score']}/30 |\n")
        
        f.write("\n")
        
        # 상세 분석
        f.write(f"### 상세 분석\n\n")
        
        for r in problem_results[:3]:  # 상위 3개만
            f.write(f"#### {r['model']}\n\n")
            f.write(f"**추정값**: {r['value']:,} {r['unit']}\n\n")
            f.write(f"**총점**: {r['total_score']}/100\n\n")
            
            # 정확도
            acc = r['accuracy']
            f.write(f"**정확도** ({acc['score']}/40):\n")
            if acc['score'] > 0:
                f.write(f"- 오차: {acc.get('model_error_pct', 0):.1f}% (AI: {acc.get('ai_error_pct', 0):.1f}%)\n")
                f.write(f"- AI 대비: {acc.get('vs_ai', 'N/A')}\n")
            else:
                f.write("- 유효한 값 없음\n")
            f.write("\n")
            
            # 분해
            decomp = r['decomposition_quality']
            f.write(f"**분해 합리성** ({decomp['score']}/30):\n")
            for detail in decomp.get('details', []):
                f.write(f"- {detail}\n")
            f.write("\n")
            
            # 논리
            logic = r['logic_coherence']
            f.write(f"**논리 일관성** ({logic['score']}/30):\n")
            for detail in logic.get('details', []):
                f.write(f"- {detail}\n")
            f.write("\n")
            
            # 실제 분해
            if 'raw_response' in r and 'decomposition' in r['raw_response']:
                decomp_list = r['raw_response']['decomposition']
                if isinstance(decomp_list, list) and len(decomp_list) > 0:
                    f.write("**모델의 분해 과정**:\n\n")
                    for i, step in enumerate(decomp_list[:4], 1):
                        f.write(f"{i}. {step.get('step', 'N/A')}\n")
                        if 'value' in step:
                            f.write(f"   - 값: {step['value']:,}\n")
                        if 'assumption' in step:
                            assumption = step['assumption'][:150]
                            if len(step['assumption']) > 150:
                                assumption += "..."
                            f.write(f"   - 가정: {assumption}\n")
                    f.write("\n")
            
            f.write("---\n\n")
    
    # 결론
    f.write("\n## 📊 결론\n\n")
    f.write("### 평가 방법의 의의\n\n")
    f.write("이 평가는 AI(Assistant)가 직접 작성한 Fermi 분해를 기준선으로 사용했습니다.\n\n")
    f.write("**장점**:\n")
    f.write("- 투명한 평가 기준 (AI의 분해 과정 공개)\n")
    f.write("- 상대적 비교 가능 (AI 대비 더 나은지 평가)\n")
    f.write("- 실제 데이터 기반 (통계청 등 공식 데이터)\n\n")
    
    f.write("**한계**:\n")
    f.write("- AI 기준선도 완벽하지 않음 (10-23% 오차)\n")
    f.write("- 더 나은 Fermi 분해 방법이 있을 수 있음\n")
    f.write("- 일부 모델이 0점을 받음 (JSON 파싱 실패 등)\n\n")
    
    f.write("### 권장사항\n\n")
    f.write(f"**Fermi 추정 작업에 가장 적합한 모델**: {top_model['model']}\n\n")
    f.write("- 정확도와 논리 일관성 모두 우수\n")
    f.write("- 실제 데이터에 가까운 추정\n")
    f.write("- 체계적인 분해 과정\n")

print(f"✅ 상세 보고서 생성: {report_file}")


