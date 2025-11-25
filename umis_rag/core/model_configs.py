"""
Model API Configuration Manager

모델별 API 설정을 YAML에서 로드하고 관리
Phase 4 Fermi Decomposition 벤치마크 기반 (v7.8.0)

Usage:
    from umis_rag.core.model_configs import model_config_manager
    
    config = model_config_manager.get_config('o1-mini')
    api_params = config.build_api_params(prompt="Test", reasoning_effort='medium')
"""

from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass, field
import yaml
import logging

logger = logging.getLogger(__name__)


@dataclass
class ModelConfig:
    """모델별 API 설정
    
    Attributes:
        model_name: 모델 이름 (e.g., 'o1-mini', 'gpt-5.1', 'cursor-native')
        api_type: API 타입 ('responses', 'chat', 'cursor')
        max_output_tokens: 최대 출력 토큰 수
        reasoning_effort_support: reasoning effort 지원 여부
        reasoning_effort_levels: 지원하는 effort 레벨 목록
        reasoning_effort_fixed: 고정된 effort (pro 모델)
        reasoning_effort_default: 기본 effort
        temperature_support: temperature 지원 여부
        temperature_condition: temperature 지원 조건
        temperature_default: 기본 temperature
        context_window: 컨텍스트 윈도우 크기
        notes: 모델 설명
    """
    model_name: str
    api_type: str
    max_output_tokens: int
    reasoning_effort_support: bool = False
    reasoning_effort_levels: List[str] = field(default_factory=list)
    reasoning_effort_fixed: Optional[str] = None
    reasoning_effort_default: str = 'medium'
    temperature_support: bool = False
    temperature_condition: Optional[str] = None
    temperature_default: float = 0.7
    context_window: Optional[int] = None
    notes: str = ''
    
    def build_api_params(
        self, 
        prompt: str, 
        reasoning_effort: Optional[str] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """API 파라미터 구성
        
        Args:
            prompt: 프롬프트 텍스트
            reasoning_effort: reasoning effort 레벨 (선택)
            temperature: temperature 값 (선택)
            **kwargs: 추가 파라미터
        
        Returns:
            API 호출용 파라미터 dict
        
        Example:
            >>> config = ModelConfig(...)
            >>> params = config.build_api_params(
            ...     prompt="Test",
            ...     reasoning_effort='medium'
            ... )
            >>> # Responses API
            >>> {'model': 'o1-mini', 'input': 'Test', 'reasoning': {'effort': 'medium'}, ...}
            >>> # Chat API
            >>> {'model': 'gpt-4o-mini', 'messages': [...], 'temperature': 0.7, ...}
            >>> # Cursor API
            >>> {'mode': 'cursor', 'prompt': 'Test'}
        """
        
        # Cursor Native: API 호출 불필요, 패턴 매칭만 수행
        if self.api_type == 'cursor':
            return {
                'mode': 'cursor',
                'prompt': prompt
            }
        
        elif self.api_type == 'responses':
            params = {
                'model': self.model_name,
                'input': prompt,
                'max_output_tokens': self.max_output_tokens
            }
            
            # reasoning_effort 적용
            if self.reasoning_effort_support:
                # 고정 effort (pro 모델)
                if self.reasoning_effort_fixed:
                    effort = self.reasoning_effort_fixed
                else:
                    effort = reasoning_effort or self.reasoning_effort_default
                
                # 지원하는 레벨인지 확인
                if effort in self.reasoning_effort_levels:
                    params['reasoning'] = {'effort': effort}
                    logger.debug(f"[{self.model_name}] reasoning.effort={effort}")
            
            # temperature (gpt-5.1 등 일부 모델만 지원)
            if self.temperature_support:
                if self.temperature_condition == 'reasoning_effort_none':
                    # reasoning.effort=none일 때만 temperature 지원
                    if reasoning_effort == 'none':
                        temp = temperature or self.temperature_default
                        params['temperature'] = temp
                        logger.debug(f"[{self.model_name}] temperature={temp}")
                else:
                    # 무조건 temperature 지원
                    temp = temperature or self.temperature_default
                    params['temperature'] = temp
            
            return params
        
        else:  # chat
            params = {
                'model': self.model_name,
                'messages': [{'role': 'user', 'content': prompt}],
                'max_tokens': self.max_output_tokens
            }
            
            # temperature 적용
            if self.temperature_support:
                temp = temperature or self.temperature_default
                params['temperature'] = temp
                logger.debug(f"[{self.model_name}] temperature={temp}")
            
            return params
    
    def is_pro_model(self, pro_models: List[str]) -> bool:
        """Pro 모델 여부 확인 (Fast Mode 대상)"""
        return self.model_name in pro_models


class ModelConfigManager:
    """모델 설정 관리자 (Singleton)
    
    config/model_configs.yaml에서 설정을 로드하고 캐싱
    
    Example:
        >>> manager = ModelConfigManager()
        >>> config = manager.get_config('o1-mini')
        >>> config.model_name
        'o1-mini'
        >>> config.api_type
        'responses'
    """
    
    _instance = None
    _configs: Dict[str, ModelConfig] = {}
    _pro_models: List[str] = []
    _defaults: Dict[str, Any] = {}
    _phase_timeouts: Dict[str, Any] = {}  # v7.10.0: Phase별 timeout 설정
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_configs()
        return cls._instance
    
    def _load_configs(self):
        """YAML에서 설정 로드"""
        config_path = Path(__file__).parent.parent.parent / "config" / "model_configs.yaml"
        
        if not config_path.exists():
            logger.error(f"model_configs.yaml not found: {config_path}")
            raise FileNotFoundError(f"model_configs.yaml not found: {config_path}")
        
        logger.info(f"Loading model configs from: {config_path}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        # 기본값 저장
        self._defaults = data.get('defaults', {})
        
        # Pro 모델 목록 저장
        self._pro_models = data.get('pro_models', [])

        # v7.10.0: Phase별 timeout 설정 저장
        self._phase_timeouts = data.get('phase_timeouts', {})
        
        # 모델별 설정 로드
        for model_name, config in data.get('models', {}).items():
            reasoning_effort = config.get('reasoning_effort', {})
            
            self._configs[model_name] = ModelConfig(
                model_name=model_name,
                api_type=config.get('api_type', self._defaults.get('api_type', 'chat')),
                max_output_tokens=config.get('max_output_tokens', self._defaults.get('max_output_tokens', 4096)),
                reasoning_effort_support=reasoning_effort.get('support', False),
                reasoning_effort_levels=reasoning_effort.get('levels', []),
                reasoning_effort_fixed=reasoning_effort.get('fixed'),
                reasoning_effort_default=reasoning_effort.get('default', 'medium'),
                temperature_support=config.get('temperature_support', self._defaults.get('temperature_support', True)),
                temperature_condition=config.get('temperature_condition'),
                temperature_default=config.get('temperature', self._defaults.get('temperature', 0.7)),
                context_window=config.get('context_window'),
                notes=config.get('notes', '')
            )
        
        logger.info(f"✅ Loaded {len(self._configs)} model configurations")
        logger.debug(f"Supported models: {list(self._configs.keys())}")
        logger.debug(f"Pro models: {self._pro_models}")
    
    def get_config(self, model_name: str) -> ModelConfig:
        """모델 설정 조회
        
        Args:
            model_name: 모델 이름
        
        Returns:
            ModelConfig 객체
        
        Note:
            정확한 이름이 없으면 prefix 기반 폴백 시도
            그래도 없으면 기본 설정 반환
        """
        # 정확한 매칭
        if model_name in self._configs:
            logger.debug(f"Model config found: {model_name}")
            return self._configs[model_name]
        
        # Prefix 기반 폴백 (새로운 버전 모델 대비)
        logger.warning(f"Exact model config not found: {model_name}, trying prefix match")
        
        prefix_map = {
            'cursor': 'cursor-native',
            'o1-pro': 'o1-pro',
            'o1-mini': 'o1-mini',
            'o1': 'o1',
            'o3-mini': 'o3-mini',
            'o3': 'o3',
            'o4-mini': 'o4-mini',
            'gpt-5.1': 'gpt-5.1',
            'gpt-5-pro': 'gpt-5-pro',
            'gpt-4.1-mini': 'gpt-4.1-mini',
            'gpt-4.1': 'gpt-4.1',
            'gpt-4.1-nano': 'gpt-4.1-nano',
            'gpt-4o-mini': 'gpt-4o-mini'
        }
        
        for prefix, base_model in prefix_map.items():
            if model_name.startswith(prefix) and base_model in self._configs:
                logger.info(f"Using fallback config: {model_name} → {base_model}")
                return self._configs[base_model]
        
        # 기본 설정 반환
        logger.warning(f"No config found for {model_name}, using default")
        return self._get_default_config(model_name)
    
    def _get_default_config(self, model_name: str) -> ModelConfig:
        """기본 설정 반환 (미지원 모델용)"""
        return ModelConfig(
            model_name=model_name,
            api_type=self._defaults.get('api_type', 'chat'),
            max_output_tokens=self._defaults.get('max_output_tokens', 4096),
            reasoning_effort_support=False,
            reasoning_effort_levels=[],
            reasoning_effort_default='medium',
            temperature_support=True,
            temperature_default=self._defaults.get('temperature', 0.7),
            notes='Default config for unknown model'
        )
    
    def list_models(self) -> List[str]:
        """지원 모델 목록 반환"""
        return list(self._configs.keys())
    
    def get_pro_models(self) -> List[str]:
        """Pro 모델 목록 반환 (Fast Mode 대상)"""
        return self._pro_models
    
    def is_pro_model(self, model_name: str) -> bool:
        """Pro 모델 여부 확인"""
        return model_name in self._pro_models

    def get_phase_timeout(self, phase: int, model_name: Optional[str] = None) -> float:
        """
        Phase별 timeout 조회 (v7.10.0)

        Args:
            phase: Phase 번호 (3 또는 4)
            model_name: 모델 이름 (선택, 모델별 timeout 적용)

        Returns:
            timeout 초 (float)

        Example:
            >>> manager = ModelConfigManager()
            >>> manager.get_phase_timeout(4, 'gpt-5.1')
            60.0
            >>> manager.get_phase_timeout(3)  # 기본값
            45.0
        """
        phase_key = f"phase_{phase}"
        phase_config = self._phase_timeouts.get(phase_key, {})

        # 기본 timeout
        default_timeout = phase_config.get('default', self._defaults.get('timeout_seconds', 30))

        if model_name:
            # 모델별 timeout
            models_timeout = phase_config.get('models', {})
            if model_name in models_timeout:
                return float(models_timeout[model_name])

            # Prefix 매칭 시도
            for prefix, timeout in models_timeout.items():
                if model_name.startswith(prefix):
                    return float(timeout)

        return float(default_timeout)


# Singleton instance
model_config_manager = ModelConfigManager()


# Convenience functions
def get_model_config(model_name: str) -> ModelConfig:
    """모델 설정 조회 (편의 함수)"""
    return model_config_manager.get_config(model_name)


def list_supported_models() -> List[str]:
    """지원 모델 목록 (편의 함수)"""
    return model_config_manager.list_models()


def is_pro_model(model_name: str) -> bool:
    """Pro 모델 여부 (편의 함수)"""
    return model_config_manager.is_pro_model(model_name)


def get_phase_timeout(phase: int, model_name: Optional[str] = None) -> float:
    """Phase별 timeout 조회 (편의 함수, v7.10.0)"""
    return model_config_manager.get_phase_timeout(phase, model_name)

