#!/usr/bin/env python3
"""
Tier 3 비즈니스 지표 E2E 테스트

8개 비즈니스 지표 템플릿 검증
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.agents.estimator.tier3 import Tier3FermiPath, BUSINESS_METRIC_TEMPLATES
from umis_rag.agents.estimator.models import Context
from umis_rag.utils.logger import logger


def test_template_matching():
    """템플릿 매칭 테스트"""
    logger.info("=" * 60)
    logger.info("Test 1: 비즈니스 지표 템플릿 매칭")
    logger.info("=" * 60)
    
    tier3 = Tier3FermiPath()
    
    # 테스트 케이스 (질문 → 예상 템플릿)
    test_cases = [
        ("국내 B2B SaaS 시장은?", "market_sizing"),
        ("SaaS 고객 LTV는?", "ltv"),
        ("CAC는?", "cac"),
        ("Freemium 전환율은?", "conversion"),
        ("월간 Churn Rate는?", "churn"),
        ("SaaS ARPU는?", "arpu"),
        ("YoY 성장률은?", "growth"),
        ("LTV/CAC 비율은?", "unit_economics"),
    ]
    
    passed = 0
    for question, expected_template in test_cases:
        models = tier3._match_business_metric_template(question)
        
        if models:
            # 템플릿 이름 확인
            if models[0].name == expected_template:
                logger.info(f"  ✅ '{question}' → {expected_template} ({len(models)}개 모형)")
                passed += 1
            else:
                logger.error(f"  ❌ '{question}': {models[0].name} (예상: {expected_template})")
        else:
            logger.error(f"  ❌ '{question}': 매칭 실패 (예상: {expected_template})")
    
    logger.info(f"\n  결과: {passed}/{len(test_cases)} 통과")
    
    return passed == len(test_cases)


def test_formula_execution():
    """수식 실행 테스트"""
    logger.info("\n" + "=" * 60)
    logger.info("Test 2: 수식 파서 (안전한 계산)")
    logger.info("=" * 60)
    
    tier3 = Tier3FermiPath()
    
    # 테스트 케이스 (수식, 변수, 예상 결과)
    test_cases = [
        # 곱셈
        (
            "market = customers × arpu × 12",
            {"customers": 1000, "arpu": 50000},
            1000 * 50000 * 12
        ),
        # 나눗셈
        (
            "ltv = arpu / churn_rate",
            {"arpu": 80000, "churn_rate": 0.05},
            80000 / 0.05
        ),
        # 덧셈
        (
            "arpu = base_fee + overage_fee",
            {"base_fee": 50000, "overage_fee": 30000},
            50000 + 30000
        ),
        # 뺄셈
        (
            "growth = (current - last) / last",
            {"current": 120, "last": 100},
            (120 - 100) / 100
        ),
        # 괄호
        (
            "cac = cpc / conversion",
            {"cpc": 1000, "conversion": 0.02},
            1000 / 0.02
        ),
    ]
    
    passed = 0
    for formula, bindings, expected in test_cases:
        result = tier3._execute_formula_simple(formula, bindings)
        
        # 오차 허용 (부동소수점)
        if abs(result - expected) < 0.01:
            logger.info(f"  ✅ {formula}")
            logger.info(f"      결과: {result:.2f} (예상: {expected:.2f})")
            passed += 1
        else:
            logger.error(f"  ❌ {formula}")
            logger.error(f"      결과: {result:.2f}, 예상: {expected:.2f}")
    
    logger.info(f"\n  결과: {passed}/{len(test_cases)} 통과")
    
    return passed == len(test_cases)


def test_template_models():
    """템플릿 모형 구조 검증"""
    logger.info("\n" + "=" * 60)
    logger.info("Test 3: 템플릿 모형 구조")
    logger.info("=" * 60)
    
    total_templates = len(BUSINESS_METRIC_TEMPLATES)
    total_models = sum(len(t['models']) for t in BUSINESS_METRIC_TEMPLATES.values())
    
    logger.info(f"  템플릿: {total_templates}개")
    logger.info(f"  총 모형: {total_models}개")
    
    # 각 템플릿 검증
    passed = 0
    for name, template in BUSINESS_METRIC_TEMPLATES.items():
        try:
            # 필수 필드 확인
            assert 'keywords' in template
            assert 'models' in template
            assert len(template['models']) > 0
            
            # 각 모형 검증
            for model in template['models']:
                assert 'id' in model
                assert 'formula' in model
                assert 'description' in model
                assert 'variables' in model
            
            logger.info(f"  ✅ {name}: {len(template['models'])}개 모형")
            passed += 1
        
        except AssertionError as e:
            logger.error(f"  ❌ {name}: 구조 오류 - {e}")
    
    logger.info(f"\n  결과: {passed}/{total_templates} 템플릿 검증")
    
    return passed == total_templates


def test_variable_policy_integration():
    """변수 정책 통합 테스트"""
    logger.info("\n" + "=" * 60)
    logger.info("Test 4: 변수 정책 통합")
    logger.info("=" * 60)
    
    tier3 = Tier3FermiPath()
    
    # LTV 템플릿 (2개 변수)
    models = tier3._match_business_metric_template("LTV는?")
    
    if not models:
        logger.error("  ❌ 템플릿 매칭 실패")
        return False
    
    logger.info(f"  템플릿: LTV ({len(models)}개 모형)")
    
    # 각 모형의 변수 개수 체크
    passed = 0
    for model in models:
        var_count = model.total_variables
        allowed, warning = tier3.variable_policy.check(var_count)
        
        if allowed:
            if warning:
                logger.info(f"  ✅ {model.model_id}: {var_count}개 변수 (경고: {warning})")
            else:
                logger.info(f"  ✅ {model.model_id}: {var_count}개 변수 (정상)")
            passed += 1
        else:
            logger.error(f"  ❌ {model.model_id}: {var_count}개 변수 금지")
    
    logger.info(f"\n  결과: {passed}/{len(models)} 모형 통과")
    
    return passed == len(models)


def main():
    """전체 테스트 실행"""
    logger.info("\n")
    logger.info("╔" + "=" * 58 + "╗")
    logger.info("║" + " " * 14 + "Tier 3 Business Metrics Test" + " " * 16 + "║")
    logger.info("╚" + "=" * 58 + "╝")
    logger.info("\n")
    
    results = []
    
    # Test 1: Template Matching
    try:
        results.append(("Template Matching", test_template_matching()))
    except Exception as e:
        logger.error(f"Test 1 failed: {e}")
        results.append(("Template Matching", False))
    
    # Test 2: Formula Execution
    try:
        results.append(("Formula Execution", test_formula_execution()))
    except Exception as e:
        logger.error(f"Test 2 failed: {e}")
        results.append(("Formula Execution", False))
    
    # Test 3: Template Structure
    try:
        results.append(("Template Structure", test_template_models()))
    except Exception as e:
        logger.error(f"Test 3 failed: {e}")
        results.append(("Template Structure", False))
    
    # Test 4: Policy Integration
    try:
        results.append(("Policy Integration", test_variable_policy_integration()))
    except Exception as e:
        logger.error(f"Test 4 failed: {e}")
        results.append(("Policy Integration", False))
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("Test Summary")
    logger.info("=" * 60)
    
    for name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        logger.info(f"{name:.<40} {status}")
    
    total = len(results)
    passed_count = sum(1 for _, p in results if p)
    
    logger.info("\n" + "=" * 60)
    logger.info(f"Total: {passed_count}/{total} tests passed")
    logger.info("=" * 60 + "\n")
    
    return all(p for _, p in results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

