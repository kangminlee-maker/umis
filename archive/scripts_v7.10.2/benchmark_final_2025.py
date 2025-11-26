#!/usr/bin/env python3
"""
LLM 종합 벤치마크 (2025-11-21 최종)
- OpenAI 전체 라인업 (nano/mini/standard/codex/thinking/pro)
- Claude 접근 가능 모델 (Opus 4, Sonnet 4, Haiku 3.5)
- UMIS 5-Phase 추론 평가
- 품질/가격/속도 종합 분석
"""

import os
import json
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
from openai import OpenAI
import anthropic

from dotenv import load_dotenv
load_dotenv()


class LLMBenchmark2025Final:
    """LLM 종합 벤치마크"""
    
    def __init__(self):
        self.openai_client = OpenAI()
        self.anthropic_client = anthropic.Anthropic()
        
        # 테스트할 모델 (접근 가능 + Deprecated 제외)
        self.models = {
            'openai_nano': ['gpt-4.1-nano', 'gpt-5-nano'],
            'openai_mini': ['gpt-4o-mini', 'gpt-4.1-mini', 'gpt-5-mini'],
            'openai_standard': ['gpt-4o', 'gpt-4.1', 'gpt-5', 'gpt-5.1'],
            'openai_codex': ['gpt-5-codex', 'gpt-5.1-codex'],
            'openai_pro': ['gpt-5-pro'],
            'openai_thinking': ['o1', 'o3', 'o3-mini', 'o4-mini'],
            'openai_thinking_pro': ['o1-pro'],
            'claude_models': ['claude-haiku-3.5', 'claude-sonnet-4', 'claude-opus-4']
        }
        
        # 가격 ($/1M) - 2025-11-21
        self.pricing = {
            'gpt-4.1-nano': {'input': 0.10, 'output': 0.40},
            'gpt-5-nano': {'input': 0.05, 'output': 0.40},
            'gpt-4o-mini': {'input': 0.15, 'output': 0.60},
            'gpt-4.1-mini': {'input': 0.40, 'output': 1.60},
            'gpt-5-mini': {'input': 0.25, 'output': 2.00},
            'gpt-4o': {'input': 2.50, 'output': 10.00},
            'gpt-4.1': {'input': 2.00, 'output': 8.00},
            'gpt-5': {'input': 1.25, 'output': 10.00},
            'gpt-5.1': {'input': 1.25, 'output': 10.00},
            'gpt-5-codex': {'input': 1.25, 'output': 10.00},
            'gpt-5.1-codex': {'input': 1.25, 'output': 10.00},
            'gpt-5-pro': {'input': 15.00, 'output': 120.00},
            'o1': {'input': 15.00, 'output': 60.00},
            'o3': {'input': 2.00, 'output': 8.00},
            'o3-mini': {'input': 1.10, 'output': 4.40},
            'o4-mini': {'input': 1.10, 'output': 4.40},
            'o1-pro': {'input': 150.00, 'output': 600.00},
            'claude-haiku-3.5': {'input': 0.80, 'output': 4.00},
            'claude-sonnet-4': {'input': 3.00, 'output': 15.00},
            'claude-opus-4': {'input': 15.00, 'output': 75.00}
        }
        
        # Claude API 이름
        # Claude API 이름 매핑 (2025-11-21 업데이트)
        self.claude_api_names = {
            'claude-haiku-3.5': 'claude-3-5-haiku-20241022',
            'claude-sonnet-4': 'claude-sonnet-4-20250514',
            'claude-sonnet-4.5': 'claude-sonnet-4-5-20250929',
            'claude-haiku-4.5': 'claude-haiku-4-5-20251001',
            'claude-opus-4': 'claude-opus-4-20250514',
            'claude-opus-4.1': 'claude-opus-4-1-20250805'
        }
        
        self.results = []
    
    def get_test_scenarios(self) -> List[Dict]:
        """UMIS 5-Phase 테스트"""
        return [
            {
                'id': 'phase0',
                'name': 'Phase 0: Literal',
                'phase': 0,
                'prompt': '''데이터에서 "한국 B2B SaaS ARPU" 찾기:

- 한국 B2B SaaS ARPU: 200,000원
- 한국 B2C ARPU: 70,000원

JSON: {"value": 200000, "unit": "원", "confidence": 1.0}''',
                'expected': {'value': 200000, 'confidence': 1.0}
            },
            {
                'id': 'phase1',
                'name': 'Phase 1: RAG',
                'phase': 1,
                'prompt': '''RAG 결과에서 코웨이 ARPU 추출:

코웨이 렌탈:
- 월 렌탈료: 33,000원

JSON: {"value": 33000, "unit": "원", "confidence": 1.0}''',
                'expected': {'value': 33000}
            },
            {
                'id': 'phase2',
                'name': 'Phase 2: 계산',
                'phase': 2,
                'prompt': '''LTV = ARPU / Churn

ARPU=80,000원, Churn=0.05

JSON: {"value": 1600000, "unit": "원", "confidence": 1.0}''',
                'expected': {'value': 1600000}
            },
            {
                'id': 'phase3_template',
                'name': 'Phase 3: 템플릿O',
                'phase': 3,
                'prompt': '''B2B SaaS 한국 ARPU 추정 (템플릿):

글로벌 $100 × 한국비율 0.6 = $60 → 78,000원

비슷하게 추정.

JSON: {"value": 숫자, "unit": "원", "confidence": 0-1, "reasoning": "한줄"}''',
                'expected': {'value_range': [50000, 150000], 'confidence_min': 0.7}
            },
            {
                'id': 'phase3_no_template',
                'name': 'Phase 3: 템플릿X',
                'phase': 3,
                'prompt': '''온라인 성인 취미교육 월 구독료 추정:

타겟: 30-40대 직장인
경쟁사: 클래스101, 탈잉

JSON: {"value": 숫자, "unit": "원", "confidence": 0-1, "reasoning": "한줄"}''',
                'expected': {'value_range': [10000, 50000], 'confidence_min': 0.6}
            },
            {
                'id': 'phase4_simple',
                'name': 'Phase 4: Fermi 단순',
                'phase': 4,
                'prompt': '''서울 피아노 학원 수 Fermi 추정:

필요 변수 → 추정 → 계산

JSON: {"value": 숫자, "unit": "개", "confidence": 0-1, "decomposition": {}, "reasoning": "요약"}''',
                'expected': {'value_range': [1500, 4000], 'confidence_min': 0.6}
            },
            {
                'id': 'phase4_complex',
                'name': 'Phase 4: Fermi 복잡',
                'phase': 4,
                'prompt': '''한국 성인 피아노 학습 연간 총 지출 추정:

학습자수/학원비/교재비/악기/기타

여러 모형 시도.

JSON: {"value": 숫자, "unit": "원", "confidence": 0-1, "models": [], "reasoning": "상세"}''',
                'expected': {'value_range': [50000000000, 500000000000], 'confidence_min': 0.5}
            }
        ]
    
    def test_openai(self, model: str, scenario: Dict) -> Dict:
        """OpenAI 테스트"""
        start = time.time()
        try:
            # 모델 타입 구분
            is_o_series = model.startswith(('o1', 'o3', 'o4'))
            is_gpt5 = model.startswith('gpt-5')
            is_reasoning = is_o_series or is_gpt5
            
            msgs = [{"role": "user", "content": scenario['prompt']}]
            if not is_reasoning:
                msgs.insert(0, {"role": "system", "content": "시장 분석 전문가. JSON만."})
            
            # API 파라미터 구성
            api_params = {"model": model, "messages": msgs}
            if is_reasoning:
                if is_o_series:
                    api_params["reasoning_effort"] = "medium"
                else:  # gpt-5
                    api_params["reasoning_effort"] = "low"
            else:
                api_params["temperature"] = 0.2
                api_params["response_format"] = {"type": "json_object"}
            
            resp = self.openai_client.chat.completions.create(**api_params)
            
            elapsed = time.time() - start
            content = resp.choices[0].message.content
            
            # JSON 추출
            try:
                if '```json' in content:
                    json_start = content.find('```json') + 7
                    json_end = content.find('```', json_start)
                    content = content[json_start:json_end].strip()
                elif '```' in content:
                    json_start = content.find('```') + 3
                    json_end = content.find('```', json_start)
                    content = content[json_start:json_end].strip()
                parsed = json.loads(content)
            except:
                parsed = {'raw': content, 'parse_error': True}
            
            cost = self._calc_cost(model, resp.usage.prompt_tokens, resp.usage.completion_tokens)
            quality = self._eval_quality(parsed, scenario.get('expected', {}))
            
            return {
                'provider': 'openai',
                'model': model,
                'scenario': scenario['name'],
                'phase': scenario['phase'],
                'response': parsed,
                'quality': quality,
                'tokens': {'in': resp.usage.prompt_tokens, 'out': resp.usage.completion_tokens, 'total': resp.usage.total_tokens},
                'cost': cost,
                'time': round(elapsed, 2),
                'success': True
            }
        except Exception as e:
            return {'provider': 'openai', 'model': model, 'scenario': scenario['name'], 'error': str(e), 'success': False}
    
    def test_claude(self, model: str, scenario: Dict) -> Dict:
        """Claude 테스트"""
        start = time.time()
        try:
            api_model = self.claude_api_names.get(model, model)
            
            resp = self.anthropic_client.messages.create(
                model=api_model,
                max_tokens=2048,
                temperature=0.2,  # temperature만 사용 (top_p와 동시 사용 불가)
                system="시장 분석 전문가. JSON만.",
                messages=[{"role": "user", "content": scenario['prompt']}]
            )
            
            elapsed = time.time() - start
            
            # refusal 처리
            if resp.stop_reason == "refusal":
                return {'provider': 'claude', 'model': model, 'scenario': scenario['name'], 'error': 'refusal', 'success': False}
            
            content = resp.content[0].text
            
            # JSON 추출
            try:
                if '```json' in content:
                    json_start = content.find('```json') + 7
                    json_end = content.find('```', json_start)
                    content = content[json_start:json_end].strip()
                elif '```' in content:
                    json_start = content.find('```') + 3
                    json_end = content.find('```', json_start)
                    content = content[json_start:json_end].strip()
                parsed = json.loads(content)
            except:
                parsed = {'raw': content, 'parse_error': True}
            
            cost = self._calc_cost(model, resp.usage.input_tokens, resp.usage.output_tokens)
            quality = self._eval_quality(parsed, scenario.get('expected', {}))
            
            return {
                'provider': 'claude',
                'model': model,
                'scenario': scenario['name'],
                'phase': scenario['phase'],
                'response': parsed,
                'quality': quality,
                'tokens': {'in': resp.usage.input_tokens, 'out': resp.usage.output_tokens, 'total': resp.usage.input_tokens + resp.usage.output_tokens},
                'cost': cost,
                'time': round(elapsed, 2),
                'success': True
            }
        except Exception as e:
            return {'provider': 'claude', 'model': model, 'scenario': scenario['name'], 'error': str(e), 'success': False}
    
    def _calc_cost(self, model: str, in_tok: int, out_tok: int) -> float:
        """비용"""
        if model not in self.pricing:
            return 0.0
        p = self.pricing[model]
        return round((in_tok / 1_000_000 * p['input'] + out_tok / 1_000_000 * p['output']), 6)
    
    def _eval_quality(self, resp: Dict, exp: Dict) -> Dict:
        """품질 (0-100)"""
        s = {
            'has_value': 'value' in resp,
            'has_confidence': 'confidence' in resp,
            'has_reasoning': 'reasoning' in resp,
            'json_valid': 'parse_error' not in resp,
            'value_ok': False,
            'confidence_ok': False
        }
        
        if s['has_value'] and 'value_range' in exp:
            v = resp.get('value')
            if isinstance(v, (int, float)):
                mn, mx = exp['value_range']
                s['value_ok'] = mn <= v <= mx
        elif s['has_value'] and 'value' in exp:
            s['value_ok'] = resp.get('value') == exp['value']
        
        if s['has_confidence'] and 'confidence_min' in exp:
            s['confidence_ok'] = resp.get('confidence', 0) >= exp['confidence_min']
        
        total = 0
        if s['json_valid']: total += 20
        if s['has_value']: total += 20
        if s['has_confidence']: total += 15
        if s['has_reasoning']: total += 15
        if s['value_ok']: total += 20
        if s['confidence_ok']: total += 10
        
        s['total'] = total
        return s
    
    def run(self, categories: Optional[List[str]] = None):
        """벤치마크 실행"""
        scenarios = self.get_test_scenarios()
        cats = categories or list(self.models.keys())
        total = sum(len(self.models[c]) for c in cats if c in self.models)
        
        print(f"\n🚀 LLM 벤치마크 시작 (2025-11-21)")
        print(f"   시나리오: {len(scenarios)}개 | 모델: {total}개\n")
        
        for sidx, scenario in enumerate(scenarios, 1):
            print(f"\n{'='*100}")
            print(f"[{sidx}/{len(scenarios)}] {scenario['name']}")
            print(f"{'='*100}")
            
            for cat in cats:
                if cat not in self.models:
                    continue
                
                for model in self.models[cat]:
                    try:
                        if 'claude' in model:
                            result = self.test_claude(model, scenario)
                        else:
                            result = self.test_openai(model, scenario)
                        
                        self.results.append(result)
                        self._print(result)
                        time.sleep(1)
                    except Exception as e:
                        print(f"   ❌ {model}: {str(e)[:80]}")
                        self.results.append({'model': model, 'scenario': scenario['name'], 'error': str(e), 'success': False})
        
        # 저장 & 리포트
        fname = f"benchmark_final_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self._save(fname)
        self._report()
    
    def _print(self, r: Dict):
        """출력"""
        if not r['success']:
            print(f"   ❌ {r['model']}: {r.get('error', '')[:70]}")
            return
        
        emoji = '🔵' if r['provider'] == 'openai' else '🟣'
        q = r['quality']['total']
        print(f"   {emoji} {r['model']:25s} | ${r['cost']:.6f} | {r['time']:4.1f}초 | {q:3d}/100")
        
        if 'value' in r['response']:
            print(f"        → {r['response'].get('value')} {r['response'].get('unit', '')}")
    
    def _save(self, fname: str):
        """저장"""
        with open(fname, 'w', encoding='utf-8') as f:
            json.dump({
                'meta': {'timestamp': datetime.now().isoformat(), 'total': len(self.results), 
                        'success': sum(1 for r in self.results if r['success'])},
                'results': self.results
            }, f, ensure_ascii=False, indent=2)
        print(f"\n✅ 저장: {fname}")
    
    def _report(self):
        """리포트"""
        success = [r for r in self.results if r['success']]
        
        print(f"\n{'='*100}")
        print(f"📊 벤치마크 리포트")
        print(f"{'='*100}")
        print(f"\n총: {len(self.results)}개 | 성공: {len(success)}개 ({len(success)/len(self.results)*100:.1f}%)")
        
        # 모델별 평균
        from collections import defaultdict
        stats = defaultdict(lambda: {'costs': [], 'quality': [], 'times': []})
        
        for r in success:
            stats[r['model']]['costs'].append(r['cost'])
            stats[r['model']]['quality'].append(r['quality']['total'])
            stats[r['model']]['times'].append(r['time'])
        
        avgs = []
        for m, d in stats.items():
            if not d['costs']:
                continue
            ac = sum(d['costs']) / len(d['costs'])
            aq = sum(d['quality']) / len(d['quality'])
            at = sum(d['times']) / len(d['times'])
            eff = aq / (ac * 1000) if ac > 0 else 0
            provider = 'openai' if any(x in m for x in ['gpt', 'o1', 'o3', 'o4']) else 'claude'
            avgs.append({'model': m, 'provider': provider, 'cost': ac, 'quality': aq, 'time': at, 'eff': eff, 'cnt': len(d['costs'])})
        
        # 가성비 순
        avgs.sort(key=lambda x: x['eff'], reverse=True)
        
        print(f"\n🏆 최고 가성비 TOP 10:")
        print(f"{'='*100}")
        for i, a in enumerate(avgs[:10], 1):
            emoji = '🔵' if a['provider'] == 'openai' else '🟣'
            print(f"  {i:2d}. {emoji} {a['model']:25s} | 가성비: {a['eff']:7.1f} | 품질: {a['quality']:5.1f}/100 | 비용: ${a['cost']:.6f} | {a['time']:4.1f}초")
        
        # Phase별
        print(f"\n📋 Phase별 최적 모델:")
        print(f"{'='*100}")
        
        phases = defaultdict(list)
        for r in success:
            phases[r['phase']].append(r)
        
        for phase in sorted(phases.keys()):
            rs = phases[phase]
            print(f"\nPhase {phase}:")
            
            # 가성비 (품질/비용)
            rs_scored = [(r, r['quality']['total'] / (r['cost'] * 1000) if r['cost'] > 0 else 0) for r in rs]
            rs_scored.sort(key=lambda x: x[1], reverse=True)
            
            print("  가성비 TOP 3:")
            for i, (r, eff) in enumerate(rs_scored[:3], 1):
                emoji = '🔵' if r['provider'] == 'openai' else '🟣'
                print(f"    {i}. {emoji} {r['model']:25s} 가성비:{eff:7.1f} | 품질:{r['quality']['total']:3d}/100 | ${r['cost']:.6f} | {r['time']:4.1f}초")
        
        # 최저 비용 TOP 5
        print(f"\n💰 최저 비용 TOP 5:")
        print(f"{'='*100}")
        avgs_cost = sorted(avgs, key=lambda x: x['cost'])
        for i, a in enumerate(avgs_cost[:5], 1):
            emoji = '🔵' if a['provider'] == 'openai' else '🟣'
            print(f"  {i}. {emoji} {a['model']:25s} ${a['cost']:.6f}/작업 | 품질: {a['quality']:5.1f}/100")
        
        # 최고 품질 TOP 5
        print(f"\n🎯 최고 품질 TOP 5:")
        print(f"{'='*100}")
        avgs_quality = sorted(avgs, key=lambda x: x['quality'], reverse=True)
        for i, a in enumerate(avgs_quality[:5], 1):
            emoji = '🔵' if a['provider'] == 'openai' else '🟣'
            print(f"  {i}. {emoji} {a['model']:25s} {a['quality']:.1f}/100 | ${a['cost']:.6f}/작업")


def main():
    """메인"""
    print("="*100)
    print("LLM 종합 벤치마크 (2025-11-21 최종)")
    print("="*100)
    
    if not os.getenv('OPENAI_API_KEY'):
        print("\n❌ OPENAI_API_KEY 없음")
        return
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("\n❌ ANTHROPIC_API_KEY 없음")
        return
    
    print("\n✅ API 키 확인 완료\n")
    print("테스트 옵션:")
    print("  1. 전체 모델 (~30분, $10-20)")
    print("  2. 핵심 모델 (~15분, $3-7) ⭐")
    print("  3. nano/mini만 (~5분, $0.50)")
    print("  4. thinking만 (~10분, $5-10)")
    print("  5. Claude만 (~3분, $1-2)")
    
    choice = input("\n선택 (1-5): ").strip()
    
    bm = LLMBenchmark2025Final()
    
    if choice == '2':
        cats = ['openai_mini', 'openai_standard', 'openai_thinking', 'claude_models']
    elif choice == '3':
        cats = ['openai_nano', 'openai_mini']
    elif choice == '4':
        cats = ['openai_thinking', 'openai_thinking_pro']
    elif choice == '5':
        cats = ['claude_models']
    else:
        cats = None
    
    try:
        bm.run(categories=cats)
    except KeyboardInterrupt:
        print("\n\n⚠️ 중단")
        if bm.results:
            bm._save('benchmark_partial.json')
    
    print("\n🎉 완료!")


if __name__ == "__main__":
    main()

