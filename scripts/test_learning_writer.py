"""
Learning Writer 기본 테스트
Phase 5: Step 1 검증
"""

import sys
from pathlib import Path

# UMIS 경로 추가
umis_root = Path(__file__).parent.parent
sys.path.insert(0, str(umis_root))

from umis_rag.guestimation_v3.learning_writer import LearningWriter, UserContribution
from umis_rag.guestimation_v3.models import (
    EstimationResult,
    Context,
    ValueEstimate,
    SoftGuide,
    Boundary,
    SourceType
)


def test_learning_writer_basic():
    """기본 Learning Writer 테스트 (Canonical 연결 전)"""
    
    print("=" * 60)
    print("Test 1: Learning Writer 기본 동작")
    print("=" * 60)
    
    # Mock Canonical Collection
    class MockCanonical:
        def __init__(self):
            self.stored = []
        
        def add(self, ids, documents, metadatas):
            self.stored.append({
                'ids': ids,
                'documents': documents,
                'metadatas': metadatas
            })
            print(f"✅ Canonical 저장 완료: {ids[0]}")
    
    # Learning Writer 초기화
    mock_canonical = MockCanonical()
    writer = LearningWriter(canonical_collection=mock_canonical)
    
    print("\n✅ LearningWriter 초기화 성공")
    
    # Test Case 1: SaaS Churn Rate
    print("\n" + "-" * 60)
    print("Test Case 1: SaaS Churn Rate")
    print("-" * 60)
    
    question = "B2B SaaS Churn Rate는?"
    
    result = EstimationResult(
        question=question,
        value=0.06,
        unit="percentage",
        value_range=(0.05, 0.07),
        confidence=0.85,
        value_estimates=[
            ValueEstimate(
                source_type=SourceType.STATISTICAL_VALUE,
                value=0.06,
                confidence=0.80,
                reasoning="정규분포 mean=6%"
            ),
            ValueEstimate(
                source_type=SourceType.RAG_BENCHMARK,
                value=0.06,
                confidence=0.75,
                reasoning="3개 벤치마크 평균"
            ),
            ValueEstimate(
                source_type=SourceType.STATISTICAL,
                value=0.06,
                confidence=0.70,
                reasoning="범위 [5%, 7%]"
            )
        ],
        soft_guides=[
            SoftGuide(
                source_type=SourceType.STATISTICAL,
                suggested_range=(0.05, 0.07),
                insight="정규분포 [5%, 7%]"
            )
        ],
        boundaries=[
            Boundary(
                source_type=SourceType.MATHEMATICAL,
                min_value=0.0,
                max_value=1.0,
                reasoning="백분율은 [0, 100%]"
            )
        ],
        conflicts_detected=[],
        conflicts_resolved=True,
        judgment_strategy="weighted_average"
    )
    
    context = Context(
        domain="B2B_SaaS",
        region=None,
        time_period="2024"
    )
    
    # 학습 가치 판단
    should_learn = writer.should_learn(result)
    print(f"\n학습 가치: {should_learn}")
    print(f"  - Confidence: {result.confidence:.2f} (>= 0.80)")
    print(f"  - Evidence: {len(result.value_estimates)}개 (>= 2)")
    print(f"  - 충돌: {len(result.conflicts_detected)}개")
    
    assert should_learn, "❌ 학습 가치 판단 실패"
    print("✅ 학습 조건 통과!")
    
    # Rule ID 생성
    rule_id = writer._generate_rule_id(question, context)
    print(f"\n생성된 Rule ID: {rule_id}")
    assert rule_id.startswith("RULE-B2B_SAAS-"), "❌ Rule ID 형식 오류"
    print("✅ Rule ID 형식 정확")
    
    # Content 생성
    content = writer._format_content(question, result, context)
    print(f"\n생성된 Content (샘플):")
    print("-" * 40)
    print(content[:300] + "...")
    print("-" * 40)
    assert "질문:" in content, "❌ Content에 질문 없음"
    assert "6%" in content or "0.06" in content, "❌ Content에 값 없음"
    print("✅ Content 형식 정확")
    
    # Metadata 생성
    metadata = writer._create_metadata(rule_id, result, context, None)
    print(f"\n생성된 Metadata:")
    for key in ['chunk_type', 'rule_id', 'domain', 'confidence', 'evidence_count']:
        print(f"  - {key}: {metadata.get(key)}")
    
    assert metadata['chunk_type'] == 'learned_rule', "❌ chunk_type 오류"
    assert metadata['domain'] == 'B2B_SaaS', "❌ domain 오류"
    assert metadata['confidence'] == 0.85, "❌ confidence 오류"
    print("✅ Metadata 형식 정확")
    
    # 실제 저장 (Mock)
    saved_rule_id = writer.save_learned_rule(question, result, context)
    print(f"\n저장 완료: {saved_rule_id}")
    
    assert saved_rule_id == rule_id, "❌ 저장된 Rule ID 불일치"
    assert len(mock_canonical.stored) == 1, "❌ Canonical 저장 실패"
    
    stored = mock_canonical.stored[0]
    print(f"\nCanonical에 저장된 데이터:")
    print(f"  - ID: {stored['ids'][0]}")
    print(f"  - Content 길이: {len(stored['documents'][0])}자")
    print(f"  - Metadata 키: {len(stored['metadatas'][0])}개")
    
    print("\n✅ Test Case 1 완료!")
    
    # Test Case 2: 학습하면 안 되는 경우
    print("\n" + "-" * 60)
    print("Test Case 2: 학습 조건 미달 (낮은 confidence)")
    print("-" * 60)
    
    low_confidence_result = EstimationResult(
        question="테스트",
        value=100,
        confidence=0.50,  # 낮음!
        value_estimates=[
            ValueEstimate(
                source_type=SourceType.LLM_ESTIMATION,
                value=100,
                confidence=0.50
            )
        ],
        judgment_strategy="fallback"
    )
    
    should_learn_low = writer.should_learn(low_confidence_result)
    print(f"학습 가치: {should_learn_low}")
    print(f"  - Confidence: {low_confidence_result.confidence:.2f} (< 0.80)")
    
    assert not should_learn_low, "❌ 낮은 confidence 케이스 실패"
    print("✅ 낮은 confidence는 학습 안 함 (정상)")
    
    # Test Case 3: 학습하면 안 되는 경우 (증거 부족)
    print("\n" + "-" * 60)
    print("Test Case 3: 학습 조건 미달 (증거 부족)")
    print("-" * 60)
    
    few_evidence_result = EstimationResult(
        question="테스트",
        value=100,
        confidence=0.90,  # 높지만
        value_estimates=[
            ValueEstimate(
                source_type=SourceType.DEFINITE_DATA,
                value=100,
                confidence=0.90
            )
        ],  # 증거 1개만!
        judgment_strategy="single_source"
    )
    
    should_learn_few = writer.should_learn(few_evidence_result)
    print(f"학습 가치: {should_learn_few}")
    print(f"  - Evidence: {len(few_evidence_result.value_estimates)}개 (< 2)")
    
    assert not should_learn_few, "❌ 증거 부족 케이스 실패"
    print("✅ 증거 부족은 학습 안 함 (정상)")
    
    print("\n" + "=" * 60)
    print("✅ 모든 테스트 통과!")
    print("=" * 60)


def test_user_contribution():
    """사용자 기여 파이프라인 테스트"""
    
    print("\n" + "=" * 60)
    print("Test 2: User Contribution")
    print("=" * 60)
    
    # Mock Canonical
    class MockCanonical:
        def __init__(self):
            self.stored = []
        
        def add(self, ids, documents, metadatas):
            self.stored.append({
                'ids': ids,
                'documents': documents,
                'metadatas': metadatas
            })
    
    mock_canonical = MockCanonical()
    writer = LearningWriter(canonical_collection=mock_canonical)
    contribution = UserContribution(learning_writer=writer)
    
    # Test Case 1: 확정 사실
    print("\nTest Case 1: 확정 사실 추가")
    print("-" * 40)
    
    rule_id = contribution.add_definite_fact(
        question="우리 회사 직원 수는?",
        value=150,
        unit="명",
        source="HR 시스템"
    )
    
    print(f"저장된 Rule ID: {rule_id}")
    assert rule_id is not None, "❌ 확정 사실 저장 실패"
    
    # Metadata 확인
    stored = mock_canonical.stored[-1]
    metadata = stored['metadatas'][0]
    print(f"  - Confidence: {metadata['confidence']}")
    print(f"  - Source Type: {metadata.get('source_type')}")
    
    assert metadata['confidence'] == 1.0, "❌ 확정 사실 confidence != 1.0"
    assert metadata['source_type'] == 'definite_fact', "❌ source_type 오류"
    
    print("✅ 확정 사실 저장 성공 (confidence=1.0)")
    
    # Test Case 2: 업계 상식
    print("\nTest Case 2: 업계 상식 추가")
    print("-" * 40)
    
    rule_id2 = contribution.add_domain_knowledge(
        question="한국 편의점 하루 매출은?",
        value=1_500_000,
        context=Context(domain="Retail_ConvenienceStore", region="한국"),
        source="업계 전문가"
    )
    
    print(f"저장된 Rule ID: {rule_id2}")
    assert rule_id2 is not None, "❌ 업계 상식 저장 실패"
    
    stored2 = mock_canonical.stored[-1]
    metadata2 = stored2['metadatas'][0]
    print(f"  - Confidence: {metadata2['confidence']} (검증 대기)")
    print(f"  - Verified: {metadata2.get('verified')}")
    
    assert metadata2['confidence'] == 0.80, "❌ 업계 상식 confidence 오류"
    assert metadata2['verified'] == False, "❌ verified 플래그 오류"
    
    print("✅ 업계 상식 저장 성공 (검증 대기)")
    
    print("\n" + "=" * 60)
    print("✅ User Contribution 테스트 통과!")
    print("=" * 60)


if __name__ == "__main__":
    
    print("\n" + "=" * 60)
    print("Phase 5: Learning Writer 테스트")
    print("=" * 60)
    
    try:
        # Test 1: Learning Writer 기본
        test_learning_writer_basic()
        
        # Test 2: User Contribution
        test_user_contribution()
        
        print("\n" + "=" * 60)
        print("🎉 모든 테스트 성공!")
        print("=" * 60)
        
        print("\n다음 단계:")
        print("  1. ✅ Learning Writer 구현 완료")
        print("  2. ⏳ Projection Generator 수정 (Step 2)")
        print("  3. ⏳ Tier 1-2 연결 (Step 3-4)")
        
    except AssertionError as e:
        print(f"\n❌ 테스트 실패: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 예외 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

