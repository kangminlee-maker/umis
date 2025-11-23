#!/usr/bin/env python3
"""
UMIS External LLM 모드 무결성 테스트
v7.7.0

목적:
----
UMIS 전체 시스템에서 External LLM 모드가 제대로 작동하는지 검증

테스트 범위:
----------
1. 설정 로딩 및 유효성 검증
2. LLMProvider 동작 검증 (Native vs External)
3. 6-Agent 시스템 External 모드 호환성
4. Estimator 5-Phase External 모드 동작
5. Model Router Phase별 자동 선택
6. API 호출 및 재시도 로직
7. 비용/성능 모니터링

사용법:
------
# 전체 테스트
UMIS_MODE=external python scripts/test_external_llm_integrity.py

# 특정 카테고리만
python scripts/test_external_llm_integrity.py --category config
python scripts/test_external_llm_integrity.py --category agents
python scripts/test_external_llm_integrity.py --category estimator

# 상세 로그
python scripts/test_external_llm_integrity.py --verbose
"""

import sys
import os
from pathlib import Path
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
import time
import json

# 프로젝트 루트 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.core.config import settings
from umis_rag.core.llm_provider import LLMProvider
from umis_rag.core.model_router import ModelRouter, select_model
from umis_rag.utils.logger import logger


@dataclass
class TestResult:
    """테스트 결과"""
    category: str
    test_name: str
    passed: bool
    message: str
    details: Dict[str, Any] = None
    duration_ms: float = 0.0


class ExternalLLMIntegrityTester:
    """External LLM 모드 무결성 테스트"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results: List[TestResult] = []
        self.start_time = time.time()
        
        print("\n" + "=" * 80)
        print("UMIS External LLM 모드 무결성 테스트 v7.7.0")
        print("=" * 80)
        print()
    
    def run_all_tests(self):
        """모든 테스트 실행"""
        print("🚀 전체 테스트 시작...\n")
        
        # 1. 설정 테스트
        self.test_configuration()
        
        # 2. LLMProvider 테스트
        self.test_llm_provider()
        
        # 3. Model Router 테스트
        self.test_model_router()
        
        # 4. Explorer Agent 테스트
        self.test_explorer_agent()
        
        # 5. Estimator Agent 테스트
        self.test_estimator_agent()
        
        # 6. 기타 Agent 테스트
        self.test_other_agents()
        
        # 7. API 연결 테스트
        self.test_api_connection()
        
        # 결과 출력
        self.print_summary()
    
    def run_category(self, category: str):
        """특정 카테고리만 테스트"""
        category_map = {
            'config': self.test_configuration,
            'provider': self.test_llm_provider,
            'router': self.test_model_router,
            'explorer': self.test_explorer_agent,
            'estimator': self.test_estimator_agent,
            'agents': self.test_other_agents,
            'api': self.test_api_connection
        }
        
        if category not in category_map:
            print(f"❌ 알 수 없는 카테고리: {category}")
            print(f"사용 가능: {', '.join(category_map.keys())}")
            return
        
        print(f"🎯 카테고리 테스트: {category}\n")
        category_map[category]()
        self.print_summary()
    
    # ========================================
    # 1. 설정 테스트
    # ========================================
    
    def test_configuration(self):
        """설정 로딩 및 유효성 검증"""
        print("📋 [1/7] 설정 테스트")
        print("-" * 40)
        
        # Test 1.1: .env 파일 존재
        self._test("config", "env_file_exists", self._check_env_file)
        
        # Test 1.2: UMIS_MODE 설정
        self._test("config", "umis_mode_set", self._check_umis_mode)
        
        # Test 1.3: OpenAI API Key
        self._test("config", "openai_api_key", self._check_api_key)
        
        # Test 1.4: LLM 모델 설정
        self._test("config", "llm_models", self._check_llm_models)
        
        # Test 1.5: Phase 기반 라우팅 설정
        self._test("config", "phase_routing", self._check_phase_routing)
        
        print()
    
    def _check_env_file(self) -> Tuple[bool, str, Dict]:
        """.env 파일 존재 확인"""
        env_path = project_root / ".env"
        if not env_path.exists():
            return False, ".env 파일이 없습니다", {}
        return True, f".env 파일 존재: {env_path}", {}
    
    def _check_umis_mode(self) -> Tuple[bool, str, Dict]:
        """UMIS_MODE 설정 확인"""
        mode = settings.umis_mode.lower()
        
        if mode not in ['native', 'external']:
            return False, f"잘못된 UMIS_MODE: {mode}", {'mode': mode}
        
        if mode != 'external':
            return False, f"External 모드가 아닙니다: {mode}", {'mode': mode}
        
        return True, f"External 모드 설정됨", {'mode': mode}
    
    def _check_api_key(self) -> Tuple[bool, str, Dict]:
        """OpenAI API Key 확인"""
        api_key = settings.openai_api_key
        
        if not api_key:
            return False, "OpenAI API Key가 설정되지 않았습니다", {}
        
        if not api_key.startswith('sk-'):
            return False, f"잘못된 API Key 형식: {api_key[:10]}...", {}
        
        return True, f"API Key 설정됨: {api_key[:10]}...", {'key_length': len(api_key)}
    
    def _check_llm_models(self) -> Tuple[bool, str, Dict]:
        """LLM 모델 설정 확인"""
        models = {
            'default': settings.llm_model,
            'phase0_2': getattr(settings, 'llm_model_phase0_2', None),
            'phase3': getattr(settings, 'llm_model_phase3', None),
            'phase4': getattr(settings, 'llm_model_phase4', None)
        }
        
        missing = [k for k, v in models.items() if not v]
        
        if missing:
            return False, f"모델 설정 누락: {', '.join(missing)}", models
        
        return True, "모든 Phase 모델 설정됨", models
    
    def _check_phase_routing(self) -> Tuple[bool, str, Dict]:
        """Phase 기반 라우팅 설정 확인"""
        enabled = getattr(settings, 'use_phase_based_routing', False)
        
        return True, f"Phase 라우팅: {'활성화' if enabled else '비활성화'}", {
            'enabled': enabled
        }
    
    # ========================================
    # 2. LLMProvider 테스트
    # ========================================
    
    def test_llm_provider(self):
        """LLMProvider 동작 검증"""
        print("🤖 [2/7] LLMProvider 테스트")
        print("-" * 40)
        
        # Test 2.1: LLMProvider.create_llm() - External 모드
        self._test("provider", "create_llm_external", self._check_create_llm_external)
        
        # Test 2.2: 모드 확인 메서드
        self._test("provider", "mode_detection", self._check_mode_detection)
        
        # Test 2.3: 모드 정보 반환
        self._test("provider", "mode_info", self._check_mode_info)
        
        print()
    
    def _check_create_llm_external(self) -> Tuple[bool, str, Dict]:
        """External 모드에서 LLM 객체 생성 확인"""
        try:
            llm = LLMProvider.create_llm()
            
            if llm is None:
                return False, "External 모드인데 LLM이 None입니다", {}
            
            # ChatOpenAI 인스턴스 확인
            from langchain_core.language_models.chat_models import BaseChatModel
            
            if not isinstance(llm, BaseChatModel):
                return False, f"잘못된 LLM 타입: {type(llm)}", {'type': str(type(llm))}
            
            return True, f"LLM 객체 생성 성공: {type(llm).__name__}", {
                'type': type(llm).__name__
            }
        
        except Exception as e:
            return False, f"LLM 생성 실패: {str(e)}", {'error': str(e)}
    
    def _check_mode_detection(self) -> Tuple[bool, str, Dict]:
        """모드 확인 메서드 검증"""
        is_native = LLMProvider.is_native_mode()
        is_external = LLMProvider.is_external_mode()
        
        if is_native:
            return False, "is_native_mode()가 True를 반환합니다", {
                'is_native': is_native,
                'is_external': is_external
            }
        
        if not is_external:
            return False, "is_external_mode()가 False를 반환합니다", {
                'is_native': is_native,
                'is_external': is_external
            }
        
        return True, "모드 감지 정상", {
            'is_native': is_native,
            'is_external': is_external
        }
    
    def _check_mode_info(self) -> Tuple[bool, str, Dict]:
        """모드 정보 반환 검증"""
        info = LLMProvider.get_mode_info()
        
        required_keys = ['mode', 'uses_api', 'cost', 'automation', 'description']
        missing = [k for k in required_keys if k not in info]
        
        if missing:
            return False, f"모드 정보 누락: {', '.join(missing)}", info
        
        if info['mode'] != 'external':
            return False, f"잘못된 모드 정보: {info['mode']}", info
        
        if not info['uses_api']:
            return False, "uses_api가 False입니다", info
        
        return True, "모드 정보 정상", info
    
    # ========================================
    # 3. Model Router 테스트
    # ========================================
    
    def test_model_router(self):
        """Model Router Phase별 자동 선택 검증"""
        print("🚦 [3/7] Model Router 테스트")
        print("-" * 40)
        
        # Test 3.1: Router 초기화
        self._test("router", "initialization", self._check_router_init)
        
        # Test 3.2: Phase별 모델 선택
        self._test("router", "phase_selection", self._check_phase_selection)
        
        # Test 3.3: 비용 추정
        self._test("router", "cost_estimation", self._check_cost_estimation)
        
        print()
    
    def _check_router_init(self) -> Tuple[bool, str, Dict]:
        """Router 초기화 확인"""
        try:
            router = ModelRouter()
            return True, "ModelRouter 초기화 성공", {
                'routing_enabled': router.routing_enabled
            }
        except Exception as e:
            return False, f"초기화 실패: {str(e)}", {'error': str(e)}
    
    def _check_phase_selection(self) -> Tuple[bool, str, Dict]:
        """Phase별 모델 선택 확인"""
        try:
            selections = {}
            for phase in [0, 1, 2, 3, 4]:
                model = select_model(phase)
                selections[f'phase_{phase}'] = model
            
            # Phase 0-2는 같은 모델
            if not (selections['phase_0'] == selections['phase_1'] == selections['phase_2']):
                return False, "Phase 0-2 모델이 다릅니다", selections
            
            return True, "Phase별 모델 선택 정상", selections
        
        except Exception as e:
            return False, f"모델 선택 실패: {str(e)}", {'error': str(e)}
    
    def _check_cost_estimation(self) -> Tuple[bool, str, Dict]:
        """비용 추정 확인"""
        try:
            from umis_rag.core.model_router import estimate_cost
            
            cost_info = estimate_cost()
            
            required_keys = ['avg_cost_per_task', 'cost_per_1000', 'savings_vs_baseline']
            missing = [k for k in required_keys if k not in cost_info]
            
            if missing:
                return False, f"비용 정보 누락: {', '.join(missing)}", cost_info
            
            # 합리적인 비용 범위 확인
            avg_cost = cost_info['avg_cost_per_task']
            if not (0.0001 < avg_cost < 0.01):
                return False, f"비정상적인 평균 비용: ${avg_cost}", cost_info
            
            return True, f"비용 추정 정상: ${avg_cost:.6f}/작업", cost_info
        
        except Exception as e:
            return False, f"비용 추정 실패: {str(e)}", {'error': str(e)}
    
    # ========================================
    # 4. Explorer Agent 테스트
    # ========================================
    
    def test_explorer_agent(self):
        """Explorer Agent External 모드 검증"""
        print("🔍 [4/7] Explorer Agent 테스트")
        print("-" * 40)
        
        # Test 4.1: Explorer 초기화
        self._test("explorer", "initialization", self._check_explorer_init)
        
        # Test 4.2: LLM 모드 설정
        self._test("explorer", "llm_mode", self._check_explorer_llm_mode)
        
        # Test 4.3: 패턴 검색 (RAG만)
        self._test("explorer", "pattern_search", self._check_explorer_search)
        
        print()
    
    def _check_explorer_init(self) -> Tuple[bool, str, Dict]:
        """Explorer 초기화 확인"""
        try:
            from umis_rag.agents.explorer import ExplorerRAG
            
            explorer = ExplorerRAG(use_projected=False)
            
            return True, "Explorer 초기화 성공", {
                'mode': explorer.mode,
                'llm_type': type(explorer.llm).__name__ if explorer.llm else 'None'
            }
        
        except Exception as e:
            return False, f"초기화 실패: {str(e)}", {'error': str(e)}
    
    def _check_explorer_llm_mode(self) -> Tuple[bool, str, Dict]:
        """Explorer LLM 모드 확인"""
        try:
            from umis_rag.agents.explorer import ExplorerRAG
            
            explorer = ExplorerRAG(use_projected=False)
            
            if explorer.mode != 'external':
                return False, f"잘못된 모드: {explorer.mode}", {'mode': explorer.mode}
            
            if explorer.llm is None:
                return False, "External 모드인데 LLM이 None입니다", {}
            
            return True, f"External 모드 설정 확인", {
                'mode': explorer.mode,
                'llm': type(explorer.llm).__name__
            }
        
        except Exception as e:
            return False, f"모드 확인 실패: {str(e)}", {'error': str(e)}
    
    def _check_explorer_search(self) -> Tuple[bool, str, Dict]:
        """Explorer 패턴 검색 확인 (RAG만)"""
        try:
            from umis_rag.agents.explorer import ExplorerRAG
            
            explorer = ExplorerRAG(use_projected=False)
            
            results = explorer.search_patterns(
                trigger_signals="구독 모델",
                top_k=3,
                use_graph=False
            )
            
            if not results:
                return False, "검색 결과가 없습니다", {}
            
            return True, f"패턴 검색 성공: {len(results)}개 발견", {
                'count': len(results),
                'patterns': [doc.metadata.get('pattern_id') for doc, _ in results[:3]]
            }
        
        except Exception as e:
            return False, f"검색 실패: {str(e)}", {'error': str(e)}
    
    # ========================================
    # 5. Estimator Agent 테스트
    # ========================================
    
    def test_estimator_agent(self):
        """Estimator Agent 5-Phase External 모드 검증"""
        print("📊 [5/7] Estimator Agent 테스트")
        print("-" * 40)
        
        # Test 5.1: Estimator 초기화
        self._test("estimator", "initialization", self._check_estimator_init)
        
        # Test 5.2: Phase 4 (Fermi) LLM 사용
        self._test("estimator", "phase4_llm", self._check_phase4_llm)
        
        print()
    
    def _check_estimator_init(self) -> Tuple[bool, str, Dict]:
        """Estimator 초기화 확인"""
        try:
            from umis_rag.agents.estimator import EstimatorRAG
            
            estimator = EstimatorRAG()
            
            return True, "Estimator 초기화 성공", {}
        
        except Exception as e:
            return False, f"초기화 실패: {str(e)}", {'error': str(e)}
    
    def _check_phase4_llm(self) -> Tuple[bool, str, Dict]:
        """Phase 4 LLM 사용 확인"""
        try:
            # Phase 4 모듈 import
            from umis_rag.agents.estimator.phase4_fermi import Phase4FermiDecomposition
            
            # OpenAI 클라이언트 확인
            try:
                from openai import OpenAI
                has_openai = True
            except ImportError:
                has_openai = False
            
            if not has_openai:
                return False, "OpenAI 패키지가 설치되지 않았습니다", {}
            
            return True, "Phase 4 LLM 준비 완료", {
                'has_openai': has_openai
            }
        
        except Exception as e:
            return False, f"Phase 4 확인 실패: {str(e)}", {'error': str(e)}
    
    # ========================================
    # 6. 기타 Agent 테스트
    # ========================================
    
    def test_other_agents(self):
        """기타 Agent LLM 사용 확인"""
        print("👥 [6/7] 기타 Agent 테스트")
        print("-" * 40)
        
        # Test 6.1: Guardian (3-Stage Evaluator)
        self._test("agents", "guardian_evaluator", self._check_guardian_evaluator)
        
        # Test 6.2: Hybrid Projector
        self._test("agents", "hybrid_projector", self._check_hybrid_projector)
        
        print()
    
    def _check_guardian_evaluator(self) -> Tuple[bool, str, Dict]:
        """Guardian 3-Stage Evaluator LLM 확인"""
        try:
            from umis_rag.guardian.three_stage_evaluator import ThreeStageEvaluator
            
            evaluator = ThreeStageEvaluator()
            
            if evaluator.llm is None:
                return False, "Evaluator LLM이 None입니다", {}
            
            return True, "Guardian Evaluator LLM 설정 확인", {
                'llm_type': type(evaluator.llm).__name__
            }
        
        except Exception as e:
            return False, f"Evaluator 확인 실패: {str(e)}", {'error': str(e)}
    
    def _check_hybrid_projector(self) -> Tuple[bool, str, Dict]:
        """Hybrid Projector LLM 확인"""
        try:
            from umis_rag.projection.hybrid_projector import HybridProjector
            
            projector = HybridProjector()
            
            if projector.llm is None:
                return False, "Projector LLM이 None입니다", {}
            
            return True, "Hybrid Projector LLM 설정 확인", {
                'llm_type': type(projector.llm).__name__
            }
        
        except Exception as e:
            return False, f"Projector 확인 실패: {str(e)}", {'error': str(e)}
    
    # ========================================
    # 7. API 연결 테스트
    # ========================================
    
    def test_api_connection(self):
        """실제 API 호출 테스트"""
        print("🌐 [7/7] API 연결 테스트")
        print("-" * 40)
        
        # Test 7.1: OpenAI API 연결
        self._test("api", "openai_connection", self._check_openai_connection)
        
        # Test 7.2: 간단한 완성 테스트
        self._test("api", "simple_completion", self._check_simple_completion)
        
        print()
    
    def _check_openai_connection(self) -> Tuple[bool, str, Dict]:
        """OpenAI API 연결 확인"""
        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=settings.openai_api_key)
            
            # 모델 목록 조회 (가벼운 API 호출)
            models = client.models.list()
            
            return True, f"OpenAI API 연결 성공", {
                'model_count': len(models.data) if hasattr(models, 'data') else 0
            }
        
        except Exception as e:
            return False, f"API 연결 실패: {str(e)}", {'error': str(e)}
    
    def _check_simple_completion(self) -> Tuple[bool, str, Dict]:
        """간단한 완성 테스트"""
        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=settings.openai_api_key)
            
            # 가장 저렴한 모델로 간단한 테스트
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "user", "content": "1+1은?"}
                ],
                max_tokens=10,
                temperature=0
            )
            
            answer = response.choices[0].message.content.strip()
            
            # 비용 계산
            usage = response.usage
            cost = (usage.prompt_tokens * 0.00015 + usage.completion_tokens * 0.0006) / 1000
            
            return True, f"완성 테스트 성공: '{answer}'", {
                'answer': answer,
                'tokens': usage.total_tokens,
                'cost': f"${cost:.6f}"
            }
        
        except Exception as e:
            return False, f"완성 테스트 실패: {str(e)}", {'error': str(e)}
    
    # ========================================
    # 유틸리티
    # ========================================
    
    def _test(self, category: str, test_name: str, test_func):
        """개별 테스트 실행"""
        start = time.time()
        
        try:
            passed, message, details = test_func()
            duration = (time.time() - start) * 1000
            
            result = TestResult(
                category=category,
                test_name=test_name,
                passed=passed,
                message=message,
                details=details,
                duration_ms=duration
            )
            
            self.results.append(result)
            
            status = "✅" if passed else "❌"
            print(f"  {status} {test_name}: {message} ({duration:.0f}ms)")
            
            if self.verbose and details:
                print(f"     상세: {json.dumps(details, ensure_ascii=False, indent=6)}")
        
        except Exception as e:
            duration = (time.time() - start) * 1000
            
            result = TestResult(
                category=category,
                test_name=test_name,
                passed=False,
                message=f"예외 발생: {str(e)}",
                details={'error': str(e)},
                duration_ms=duration
            )
            
            self.results.append(result)
            
            print(f"  ❌ {test_name}: 예외 발생 ({duration:.0f}ms)")
            if self.verbose:
                import traceback
                traceback.print_exc()
    
    def print_summary(self):
        """결과 요약 출력"""
        total_duration = time.time() - self.start_time
        
        print("\n" + "=" * 80)
        print("테스트 결과 요약")
        print("=" * 80)
        
        # 카테고리별 집계
        categories = {}
        for result in self.results:
            cat = result.category
            if cat not in categories:
                categories[cat] = {'passed': 0, 'failed': 0, 'total': 0}
            
            categories[cat]['total'] += 1
            if result.passed:
                categories[cat]['passed'] += 1
            else:
                categories[cat]['failed'] += 1
        
        # 카테고리별 출력
        print("\n📊 카테고리별 결과:")
        for cat, stats in categories.items():
            pass_rate = (stats['passed'] / stats['total'] * 100) if stats['total'] > 0 else 0
            status = "✅" if stats['failed'] == 0 else "⚠️"
            print(f"  {status} {cat}: {stats['passed']}/{stats['total']} 통과 ({pass_rate:.0f}%)")
        
        # 전체 통계
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        failed = total - passed
        pass_rate = (passed / total * 100) if total > 0 else 0
        
        print("\n📈 전체 통계:")
        print(f"  총 테스트: {total}개")
        print(f"  통과: {passed}개")
        print(f"  실패: {failed}개")
        print(f"  통과율: {pass_rate:.1f}%")
        print(f"  소요 시간: {total_duration:.2f}초")
        
        # 실패한 테스트 상세
        if failed > 0:
            print("\n❌ 실패한 테스트:")
            for result in self.results:
                if not result.passed:
                    print(f"  - [{result.category}] {result.test_name}")
                    print(f"    {result.message}")
                    if result.details:
                        print(f"    상세: {json.dumps(result.details, ensure_ascii=False)}")
        
        # 최종 상태
        print("\n" + "=" * 80)
        if failed == 0:
            print("🎉 모든 테스트 통과! External LLM 모드가 정상 작동합니다.")
        else:
            print(f"⚠️  {failed}개 테스트 실패. 위 내용을 확인하세요.")
        print("=" * 80)


def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="UMIS External LLM 모드 무결성 테스트"
    )
    parser.add_argument(
        '--category',
        choices=['config', 'provider', 'router', 'explorer', 'estimator', 'agents', 'api'],
        help="특정 카테고리만 테스트"
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help="상세 로그 출력"
    )
    
    args = parser.parse_args()
    
    tester = ExternalLLMIntegrityTester(verbose=args.verbose)
    
    if args.category:
        tester.run_category(args.category)
    else:
        tester.run_all_tests()


if __name__ == "__main__":
    main()


