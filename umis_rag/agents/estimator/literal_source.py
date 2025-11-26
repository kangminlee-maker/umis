"""
Literal Source - 프로젝트 확정 데이터 (v7.11.1)

역할:
- 프로젝트별로 저장된 확정 데이터 탐색
- 즉시 반환 (<0.1초)
- Confidence = 1.0 (확정 값)

데이터 구조:
- JSON 기반 키-값 저장
- 프로젝트별 네임스페이스
- 타임스탬프 관리

사용 예시:
    project_data = {
        'B2B_SaaS_Korea_2024': {
            'churn_rate': 0.05,
            'arpu': 80000,
            'ltv': 1600000
        }
    }
"""

from typing import Optional, Dict, Any
import json
from pathlib import Path

from umis_rag.utils.logger import logger
from umis_rag.core.config import settings

from .models import Context, EstimationResult


class LiteralSource:
    """
    Literal Source - 프로젝트 확정 데이터 (v7.11.1)
    
    역할:
    -----
    - 프로젝트별 확정 데이터 저장/조회
    - 즉시 반환 (<0.1초)
    - Confidence = 1.0
    
    데이터 위치:
    -----------
    - projects/{project_id}/data.json
    - 또는 메모리 (runtime)
    
    구조:
    -----
    {
        "project_id": "B2B_SaaS_Korea_2024",
        "data": {
            "churn_rate": 0.05,
            "arpu": 80000,
            "ltv": 1600000
        },
        "metadata": {
            "created_at": "2024-11-26",
            "source": "프로젝트 정의"
        }
    }
    """
    
    def __init__(self, project_id: Optional[str] = None):
        """
        초기화
        
        Args:
            project_id: 프로젝트 ID (None이면 기본값)
        """
        self.project_id = project_id or "default"
        self.data: Dict[str, Any] = {}
        
        logger.info(f"[Phase 0] Literal 초기화 (project_id={self.project_id})")
        
        # 프로젝트 데이터 로드
        self._load_project_data()
    
    def _load_project_data(self):
        """프로젝트 데이터 로드"""
        try:
            # 프로젝트 폴더 경로
            project_root = Path(__file__).parent.parent.parent.parent
            project_dir = project_root / "projects" / self.project_id
            data_file = project_dir / "data.json"
            
            if data_file.exists():
                with open(data_file, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
                
                logger.info(f"  ✅ 프로젝트 데이터 로드: {len(self.data)}개 항목")
            else:
                logger.info(f"  ℹ️  프로젝트 데이터 파일 없음: {data_file}")
                self.data = {}
        
        except Exception as e:
            logger.warning(f"  프로젝트 데이터 로드 실패: {e}")
            self.data = {}
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 메인 인터페이스
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def get(
        self,
        question: str,
        context: Optional[Context] = None
    ) -> Optional[EstimationResult]:
        """
        프로젝트 데이터 조회
        
        Args:
            question: 질문
            context: 맥락
        
        Returns:
            EstimationResult or None
        """
        logger.info(f"[Phase 0] 조회: {question}")
        
        # 질문에서 변수명 추출
        variable_name = self._extract_variable_name(question)
        
        if not variable_name:
            logger.info("  변수명 추출 실패")
            return None
        
        # 데이터 조회
        value = self._lookup_value(variable_name, context)
        
        if value is None:
            logger.info(f"  데이터 없음: {variable_name}")
            return None
        
        # 결과 생성
        result = EstimationResult(
            question=question,
            phase=0,
            value=value,
            confidence=1.0,  # 확정 값
            uncertainty=0.0,
            context=context,
            reasoning=f"프로젝트 데이터 (확정): {variable_name} = {value}",
            execution_time=0.0
        )
        
        logger.info(f"  ✅ 발견: {variable_name} = {value}")
        
        return result
    
    def set(
        self,
        variable_name: str,
        value: float,
        metadata: Optional[Dict] = None
    ):
        """
        프로젝트 데이터 저장
        
        Args:
            variable_name: 변수명
            value: 값
            metadata: 메타데이터
        """
        self.data[variable_name] = {
            'value': value,
            'metadata': metadata or {}
        }
        
        logger.info(f"[Phase 0] 저장: {variable_name} = {value}")
        
        # 파일 저장
        self._save_project_data()
    
    def _save_project_data(self):
        """프로젝트 데이터 저장"""
        try:
            project_root = Path(__file__).parent.parent.parent.parent
            project_dir = project_root / "projects" / self.project_id
            project_dir.mkdir(parents=True, exist_ok=True)
            
            data_file = project_dir / "data.json"
            
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"  ✅ 저장 완료: {data_file}")
        
        except Exception as e:
            logger.error(f"  저장 실패: {e}")
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Private Methods
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def _extract_variable_name(self, question: str) -> Optional[str]:
        """
        질문에서 변수명 추출
        
        Args:
            question: "B2B SaaS Churn Rate는?"
        
        Returns:
            변수명: "churn_rate" 또는 None
        """
        # 간단한 키워드 매칭
        mappings = {
            'churn': 'churn_rate',
            '해지율': 'churn_rate',
            'arpu': 'arpu',
            'ltv': 'ltv',
            'cac': 'cac',
            '고객획득': 'cac',
            '도입률': 'adoption_rate',
            '전환율': 'conversion_rate',
            '성장률': 'growth_rate'
        }
        
        question_lower = question.lower()
        
        for keyword, var_name in mappings.items():
            if keyword in question_lower:
                return var_name
        
        return None
    
    def _lookup_value(
        self,
        variable_name: str,
        context: Optional[Context]
    ) -> Optional[float]:
        """
        변수 값 조회 (Context 고려)
        
        Args:
            variable_name: 변수명
            context: 맥락
        
        Returns:
            값 or None
        """
        # 1. Context 기반 조회 (우선)
        if context:
            # Context 형식 처리: 객체 또는 딕셔너리
            domain = None
            region = None
            
            if isinstance(context, dict):
                domain = context.get('domain')
                region = context.get('region')
            elif hasattr(context, 'domain'):
                domain = context.domain
                region = context.region
            
            # Context 키 생성: domain_region_variable
            if domain and region:
                context_key = f"{domain}_{region}_{variable_name}"
                
                if context_key in self.data:
                    return self.data[context_key].get('value')
            
            # domain만 매칭
            if domain:
                domain_key = f"{domain}_{variable_name}"
                if domain_key in self.data:
                    return self.data[domain_key].get('value')
        
        # 2. 변수명 직접 조회
        if variable_name in self.data:
            return self.data[variable_name].get('value')
        
        return None
