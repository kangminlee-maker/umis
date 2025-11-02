"""
UMIS Multi-Agent RAG 메타데이터 스키마

개념:
-----
**Single Source of Truth with Multi-View**

같은 "배달의민족" 사례가 여러 agent용 청크로 저장되지만,
공통 메타데이터로 연결되어 일관성 유지.

구조:
-----
1. **Core Metadata**: 모든 agent가 공유
2. **Agent-Specific Metadata**: agent별 관점
3. **Cross-Reference**: agent간 참조 가능
"""

from typing import Literal, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


# ========================================
# Core Metadata (모든 청크 공통)
# ========================================

class CoreMetadata(BaseModel):
    """
    모든 agent가 공유하는 핵심 메타데이터
    
    목적:
    -----
    - 데이터 일관성 보장
    - Cross-agent 참조 가능
    - 중복 제거
    """
    
    # 식별자
    source_id: str = Field(
        description="원본 데이터 식별자 (예: 'baemin_case')"
    )
    source_file: str = Field(
        description="원본 파일명"
    )
    
    # 분류
    domain: Literal[
        "business_model",      # 사업모델 패턴
        "disruption",          # 파괴 패턴
        "case_study",          # 성공/실패 사례
        "framework",           # 검증/분석 프레임워크
        "market_data"          # 시장 데이터
    ]
    
    category: Optional[str] = Field(
        default=None,
        description="세부 카테고리 (예: 'platform', 'subscription')"
    )
    
    # 메타 정보
    created_at: datetime = Field(
        default_factory=datetime.now
    )
    version: str = "6.2"
    language: str = "ko"
    
    # 품질
    validation_status: Literal[
        "verified",      # Validator 검증 완료
        "estimated",     # 추정치 포함
        "unverified"     # 미검증
    ] = "unverified"
    
    quality_grade: Optional[Literal["A", "B", "C", "D"]] = None


# ========================================
# Agent-Specific Metadata
# ========================================

class ObserverMetadata(BaseModel):
    """
    Observer (Observer) 관점 메타데이터
    
    관심사:
    -------
    - 시장 구조
    - 경쟁 역학
    - 트렌드 패턴
    """
    
    agent_view: Literal["observer"] = "observer"
    view_type: Literal[
        "structural",        # 구조 분석
        "competitive",       # 경쟁 구도
        "trend",            # 트렌드
        "dynamics"          # 시장 역학
    ]
    
    # Observer 특화 필드
    structural_patterns: List[str] = Field(
        default_factory=list,
        description="발견된 구조 패턴 (예: ['중개_플랫폼', '3면_시장'])"
    )
    
    market_dynamics: List[str] = Field(
        default_factory=list,
        description="시장 역학 (예: ['파편화→집중화', 'power_shift'])"
    )
    
    time_dimension: Optional[str] = Field(
        default=None,
        description="시간 차원 (예: '10년_변화', '급성장기')"
    )
    
    chunking_level: Literal["macro", "meso", "micro"] = Field(
        default="meso",
        description="청킹 레벨: macro(시장 전체), meso(구조 요소), micro(세부 패턴)"
    )


class ExplorerMetadata(BaseModel):
    """
    Explorer (Explorer) 관점 메타데이터
    
    관심사:
    -------
    - 기회 패턴
    - 실행 전략
    - 성공 요인
    """
    
    agent_view: Literal["explorer"] = "explorer"
    view_type: Literal[
        "opportunity",       # 기회 발견
        "strategy",          # 전략 실행
        "validation",        # 검증 방법
        "case_learning"      # 사례 학습
    ]
    
    # Explorer 특화 필드
    pattern_id: str = Field(
        description="적용 패턴 ID (예: 'platform_business_model')"
    )
    
    pattern_type: Literal["business_model", "disruption"]
    
    triggers: str = Field(  # JSON string (Chroma DB 호환)
        default="[]",
        description="트리거 시그널 리스트 (JSON)"
    )
    
    critical_success_factors: str = Field(
        default="[]",
        description="핵심 성공 요인 (JSON)"
    )
    
    # 적용성
    applicability: str = Field(
        default="[]",
        description="적용 가능 산업/상황 (JSON)"
    )
    
    difficulty: Literal["low", "medium", "high"] = "medium"
    capital_requirement: Literal["low", "medium", "high"] = "medium"
    timeframe: Optional[str] = None
    
    chunking_level: Literal["pattern", "section", "case"] = Field(
        default="section",
        description="청킹 레벨: pattern(전체), section(섹션), case(사례)"
    )


class QuantifierMetadata(BaseModel):
    """
    Quantifier (Quantifier) 관점 메타데이터
    
    관심사:
    -------
    - 정량 데이터
    - 계산식
    - 메트릭
    """
    
    agent_view: Literal["quantifier"] = "quantifier"
    view_type: Literal[
        "quantitative",      # 정량 데이터
        "calculation",       # 계산식
        "benchmark",         # 벤치마크
        "forecast"           # 예측
    ]
    
    # Quantifier 특화 필드
    metrics: str = Field(  # JSON string
        default="[]",
        description="포함된 메트릭 (예: [{name: 'MAU', value: 10M}])"
    )
    
    formulas: str = Field(  # JSON string
        default="[]",
        description="계산식 리스트"
    )
    
    data_quality: Literal[
        "verified",      # 검증된 실제 데이터
        "estimated",     # 추정치
        "calculated"     # 계산 결과
    ] = "verified"
    
    calculation_basis: Optional[str] = None
    
    has_numbers: bool = Field(
        default=True,
        description="숫자 데이터 포함 여부 (빠른 필터링용)"
    )
    
    chunking_level: Literal["metric", "calculation", "report"] = Field(
        default="calculation",
        description="청킹 레벨: metric(개별 지표), calculation(계산 블록), report(전체)"
    )


class ValidatorMetadata(BaseModel):
    """
    Validator (Validator) 관점 메타데이터
    
    관심사:
    -------
    - 데이터 출처
    - 신뢰도
    - 검증 상태
    """
    
    agent_view: Literal["validator"] = "validator"
    view_type: Literal[
        "source",            # 출처 정보
        "verification",      # 검증 리포트
        "gap_analysis",      # 데이터 Gap
        "reliability"        # 신뢰도 평가
    ]
    
    # Validator 특화 필드
    sources: str = Field(  # JSON string
        default="[]",
        description="출처 리스트 (예: [{src_id: 'SRC_001', type: 'official'}])"
    )
    
    data_gaps: str = Field(  # JSON string
        default="[]",
        description="부족한 데이터 리스트"
    )
    
    reliability: Literal["high", "medium", "low"] = "medium"
    
    verification_date: Optional[datetime] = None
    
    chunking_level: Literal["source", "verification", "full_report"] = Field(
        default="source",
        description="청킹 레벨: source(출처별), verification(검증 항목별), full_report(전체)"
    )


class GuardianMetadata(BaseModel):
    """
    Guardian (Guardian) 관점 메타데이터
    
    관심사:
    -------
    - 검증 상태
    - 품질 관리
    - 프로세스 준수
    """
    
    agent_view: Literal["guardian"] = "guardian"
    view_type: Literal[
        "governance",        # 거버넌스
        "quality",          # 품질 평가
        "process",          # 프로세스
        "approval"          # 승인 상태
    ]
    
    # Guardian 특화 필드
    quality_grade: Literal["A", "B", "C", "D"]
    
    validation_complete: bool = False
    
    checked_by: str = Field(  # JSON string
        default="[]",
        description="검증한 agent 리스트"
    )
    
    approved_phases: str = Field(  # JSON string
        default="[]",
        description="승인된 사용 단계"
    )
    
    warnings: str = Field(  # JSON string
        default="[]",
        description="주의사항 리스트"
    )
    
    usage_count: int = 0
    last_used: Optional[datetime] = None
    
    chunking_level: Literal["summary", "detail"] = Field(
        default="summary",
        description="청킹 레벨: summary(요약), detail(상세)"
    )


# ========================================
# Unified Metadata Schema
# ========================================

class UnifiedChunkMetadata(BaseModel):
    """
    통합 청크 메타데이터
    
    구조:
    -----
    Core (공통) + Agent-Specific (개별)
    
    저장:
    -----
    Chroma DB에는 flatten된 dict로 저장
    (pydantic은 내부 관리용)
    
    예시:
    -----
    {
        # Core
        "source_id": "baemin_case",
        "domain": "case_study",
        
        # Explorer-specific
        "agent_view": "explorer",
        "pattern_id": "platform_business_model",
        
        # Cross-reference
        "related_chunks": ["observer_baemin_structure", "quantifier_baemin_metrics"]
    }
    """
    
    # Unique ID
    chunk_id: str = Field(
        description="청크 고유 ID (agent_view + source_id + section)"
    )
    
    # Core metadata
    core: CoreMetadata
    
    # Agent view (하나만 선택)
    agent_view: Literal["observer", "explorer", "quantifier", "validator", "guardian"]
    
    # Agent-specific (선택적으로 하나만 존재)
    observer: Optional[ObserverMetadata] = None
    explorer: Optional[ExplorerMetadata] = None
    quantifier: Optional[QuantifierMetadata] = None
    validator: Optional[ValidatorMetadata] = None
    guardian: Optional[GuardianMetadata] = None
    
    # Cross-reference (agent간 참조)
    related_chunks: List[str] = Field(
        default_factory=list,
        description="관련 청크 ID 리스트 (다른 agent view)"
    )
    
    # 기타
    token_count: int
    
    def to_chroma_metadata(self) -> dict:
        """
        Chroma DB 호환 flat dict로 변환
        
        Chroma 제약:
        - 중첩 dict 불가
        - list는 JSON string으로
        """
        flat = {
            "chunk_id": self.chunk_id,
            "source_id": self.core.source_id,
            "source_file": self.core.source_file,
            "domain": self.core.domain,
            "category": self.core.category or "",
            "version": self.core.version,
            "language": self.core.language,
            "validation_status": self.core.validation_status,
            "quality_grade": self.core.quality_grade or "",
            
            "agent_view": self.agent_view,
            "token_count": self.token_count,
            "related_chunks": str(self.related_chunks),  # JSON string
        }
        
        # Agent-specific 추가
        if self.explorer:
            flat.update({
                "explorer_view_type": self.explorer.view_type,
                "explorer_pattern_id": self.explorer.pattern_id,
                "explorer_pattern_type": self.explorer.pattern_type,
                "explorer_triggers": self.explorer.triggers,
                "explorer_csf": self.explorer.critical_success_factors,
                "explorer_difficulty": self.explorer.difficulty,
                "explorer_chunking_level": self.explorer.chunking_level,
            })
        
        if self.observer:
            flat.update({
                "observer_view_type": self.observer.view_type,
                "observer_patterns": str(self.observer.structural_patterns),
                "observer_dynamics": str(self.observer.market_dynamics),
                "observer_chunking_level": self.observer.chunking_level,
            })
        
        if self.quantifier:
            flat.update({
                "quantifier_view_type": self.quantifier.view_type,
                "quantifier_metrics": self.quantifier.metrics,
                "quantifier_formulas": self.quantifier.formulas,
                "quantifier_data_quality": self.quantifier.data_quality,
                "quantifier_has_numbers": self.quantifier.has_numbers,
                "quantifier_chunking_level": self.quantifier.chunking_level,
            })
        
        if self.validator:
            flat.update({
                "validator_view_type": self.validator.view_type,
                "validator_sources": self.validator.sources,
                "validator_reliability": self.validator.reliability,
                "validator_chunking_level": self.validator.chunking_level,
            })
        
        if self.guardian:
            flat.update({
                "guardian_view_type": self.guardian.view_type,
                "guardian_quality": self.guardian.quality_grade,
                "guardian_validated": self.guardian.validation_complete,
                "guardian_checked_by": self.guardian.checked_by,
                "guardian_chunking_level": self.guardian.chunking_level,
            })
        
        return flat


# ========================================
# Chunking Level Guidelines
# ========================================

CHUNKING_GUIDELINES = {
    "observer": {
        "macro": {
            "size": "1500-2000 tokens",
            "scope": "전체 시장 구조",
            "example": "한국 음식 배달 시장 전체 구조 변화 (2010-2025)",
            "when": "시장 전체 조망 필요"
        },
        "meso": {
            "size": "500-800 tokens",
            "scope": "구조 요소별",
            "example": "플랫폼 삽입으로 인한 가치사슬 재편",
            "when": "특정 구조 패턴 분석 (기본값)"
        },
        "micro": {
            "size": "200-400 tokens",
            "scope": "세부 패턴",
            "example": "네트워크 효과 메커니즘",
            "when": "특정 개념 정밀 검색"
        }
    },
    
    "explorer": {
        "pattern": {
            "size": "800-1200 tokens",
            "scope": "패턴 전체",
            "example": "플랫폼 비즈니스 모델 (concept + triggers + structure)",
            "when": "패턴 전체 맥락 필요"
        },
        "section": {
            "size": "300-600 tokens",
            "scope": "섹션별",
            "example": "플랫폼 비즈니스 > 기회 구조",
            "when": "특정 섹션만 필요 (기본값, 추천)"
        },
        "case": {
            "size": "400-800 tokens",
            "scope": "사례별",
            "example": "배달의민족 성공 사례",
            "when": "개별 사례 학습"
        }
    },
    
    "quantifier": {
        "report": {
            "size": "1000-1500 tokens",
            "scope": "전체 정량 리포트",
            "example": "배달의민족 성장 지표 (2010-2020)",
            "when": "종합 정량 분석"
        },
        "calculation": {
            "size": "300-500 tokens",
            "scope": "계산 블록",
            "example": "GMV = MAU × 빈도 × 객단가 (계산 과정)",
            "when": "특정 계산식 찾기 (기본값)"
        },
        "metric": {
            "size": "100-200 tokens",
            "scope": "개별 지표",
            "example": "MAU: 1,000만 (2020년)",
            "when": "특정 숫자만 빠르게"
        }
    },
    
    "validator": {
        "full_report": {
            "size": "800-1200 tokens",
            "scope": "전체 검증 리포트",
            "example": "배달의민족 데이터 출처 및 신뢰도 종합",
            "when": "전체 검증 상태 확인"
        },
        "source": {
            "size": "200-400 tokens",
            "scope": "출처별",
            "example": "SRC_001: Wikipedia - 신뢰도 Medium",
            "when": "특정 출처 확인 (기본값)"
        },
        "verification": {
            "size": "300-500 tokens",
            "scope": "검증 항목별",
            "example": "MAU 데이터 검증 (공식 발표 vs 추정)",
            "when": "특정 데이터 포인트 검증"
        }
    },
    
    "guardian": {
        "summary": {
            "size": "300-500 tokens",
            "scope": "검증 상태 요약",
            "example": "배달의민족 사례 - 등급 A, 4명 검증 완료",
            "when": "빠른 품질 확인 (기본값)"
        },
        "detail": {
            "size": "600-1000 tokens",
            "scope": "상세 검증 내역",
            "example": "검증 체크리스트 + 주의사항 + 사용 이력",
            "when": "상세 검증 필요"
        }
    }
}


# ========================================
# Storage Strategy
# ========================================

STORAGE_STRATEGY = """
저장 전략: Single Collection with Multi-View Chunks
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Collection: umis_knowledge_base (단일!)

같은 "배달의민족 사례"를 여러 관점으로 청킹:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Observer View (구조 중심):
   chunk_id: observer_baemin_market_structure
   agent_view: observer
   content: "시장 구조 변화 (파편화 → 집중화)..."
   chunking_level: meso

2. Explorer View (기회 중심):
   chunk_id: explorer_baemin_platform_opportunity
   agent_view: explorer
   content: "플랫폼 비즈니스 모델 실행 사례..."
   chunking_level: case

3. Quantifier View (정량 중심):
   chunk_id: quantifier_baemin_growth_metrics
   agent_view: quantifier
   content: "MAU: 1,000만, 점유율: 60%, GMV: 6조..."
   chunking_level: calculation

4. Validator View (출처 중심):
   chunk_id: validator_baemin_sources
   agent_view: validator
   content: "SRC_001: Wikipedia, SRC_002: 공식 발표..."
   chunking_level: source

5. Guardian View (검증 중심):
   chunk_id: guardian_baemin_validation_status
   agent_view: guardian
   content: "등급 A, 검증 완료, 주의사항..."
   chunking_level: summary

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

장점:
✅ 같은 source_id로 모든 view 연결
✅ Cross-agent 협업 쉬움
✅ 메타데이터 일관성
✅ 중복 최소화 (공통 정보는 core에)

검색:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Filter: agent_view="explorer"
→ Explorer가 볼 청크만 검색

Filter: source_id="baemin_case"
→ 배달의민족의 모든 관점 청크 검색

Filter: agent_view="explorer" AND pattern_type="disruption"
→ Explorer의 Disruption 청크만
"""

