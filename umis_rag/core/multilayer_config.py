"""
Multi-Layer Guestimation 설정 로더
v2.1 - 2025-11-05

config/multilayer_config.yaml에서 Guestimation 전용 설정을 로드

참고:
- UMIS_MODE (LLM 제공자): .env에서 관리 (umis_rag.UMIS_MODE)
- web_search_mode, interactive_mode: 이 파일에서 관리 (Guestimation 전용)
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class GuestimationConfig:
    """Guestimation 전용 설정"""
    web_search_mode: str = "native"  # native, api, scraping, skip
    interactive_mode: bool = False


@dataclass
class LayerConfig:
    """레이어별 설정"""
    enabled: bool = True
    confidence_threshold: float = 0.5


class MultiLayerConfigLoader:
    """
    Multi-Layer Guestimation 설정 로더
    
    config/multilayer_config.yaml에서 Guestimation 전용 설정 로드
    (UMIS_MODE는 .env에서 별도 관리)
    """
    
    _instance = None
    _config = None
    
    def __new__(cls):
        """싱글톤 패턴"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """초기화 (최초 1회만)"""
        if self._config is None:
            self._load_config()
    
    def _load_config(self):
        """설정 파일 로드"""
        # 설정 파일 경로
        config_path = Path(__file__).parent.parent.parent / "config" / "multilayer_config.yaml"
        
        if not config_path.exists():
            # 기본 설정 사용
            self._config = self._get_default_config()
            return
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self._config = yaml.safe_load(f)
        except Exception as e:
            print(f"⚠️ 설정 파일 로드 실패: {e}")
            self._config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """기본 설정 (Guestimation 전용)"""
        return {
            # Guestimation 전용 설정
            'web_search_mode': 'native',
            'interactive_mode': False,
            
            'layer_2_llm': {
                'native': {'enabled': True, 'confidence': 0.7},
                'external': {'enabled': False, 'model': 'gpt-4o-mini'},
            },
            'layer_3_web_search': {
                'native': {'enabled': True, 'use_cursor_tool': True},
                'api': {'enabled': False, 'results_count': 20},
                'scraping': {'enabled': False},
                'consensus_extraction': {
                    'similarity_based': {'threshold': 0.7},
                    'outlier_removal': {'threshold': 1.5},
                    'clustering': {'min_cluster_size': 3}
                }
            },
            'confidence_thresholds': {
                'layer_2_llm': 0.7,
                'layer_3_web': 0.75,
                'layer_5_behavioral': 0.6,
                'layer_6_statistical': 0.5,
                'layer_7_rag': 0.5,
                'layer_8_constraint': 0.4
            }
        }
    
    # =========================================
    # Getter 메서드들 (Guestimation 전용)
    # =========================================
    
    def get_guestimation_config(self) -> GuestimationConfig:
        """Guestimation 설정 반환"""
        return GuestimationConfig(
            web_search_mode=self._config.get('web_search_mode', 'native'),
            interactive_mode=self._config.get('interactive_mode', False)
        )
    
    def get_web_search_mode(self) -> str:
        """웹 검색 모드 반환 (native, api, scraping, skip)"""
        return self._config.get('web_search_mode', 'native')
    
    def is_interactive_mode(self) -> bool:
        """Interactive 모드 여부"""
        return self._config.get('interactive_mode', False)
    
    def get_layer_config(self, layer_name: str) -> Dict[str, Any]:
        """특정 레이어 설정 반환"""
        layer_configs = {
            'layer_2': self._config.get('layer_2_llm', {}),
            'layer_3': self._config.get('layer_3_web_search', {}),
        }
        return layer_configs.get(layer_name, {})
    
    def get_confidence_threshold(self, layer_name: str) -> float:
        """레이어별 신뢰도 임계값"""
        thresholds = self._config.get('confidence_thresholds', {})
        return thresholds.get(layer_name, 0.5)
    
    def get_llm_config(self, mode: str = None) -> Dict[str, Any]:
        """LLM 설정 반환"""
        if mode is None:
            mode = self.get_llm_mode()
        
        layer_2 = self._config.get('layer_2_llm', {})
        return layer_2.get(mode, {})
    
    def get_web_search_config(self, mode: str = None) -> Dict[str, Any]:
        """웹 검색 설정 반환"""
        if mode is None:
            mode = self.get_web_search_mode()
        
        layer_3 = self._config.get('layer_3_web_search', {})
        return layer_3.get(mode, {})
    
    def get_consensus_config(self) -> Dict[str, Any]:
        """공통값 추출 설정 반환 (Layer 3용)"""
        layer_3 = self._config.get('layer_3_web_search', {})
        return layer_3.get('consensus_extraction', {})
    
    def get_number_extraction_patterns(self) -> list:
        """숫자 추출 패턴 반환 (Layer 2용)"""
        layer_2 = self._config.get('layer_2_llm', {})
        return layer_2.get('number_extraction', {}).get('patterns', [])


# =========================================
# 전역 싱글톤 인스턴스
# =========================================

_config_loader = None

def get_multilayer_config() -> MultiLayerConfigLoader:
    """글로벌 설정 로더 반환 (싱글톤)"""
    global _config_loader
    if _config_loader is None:
        _config_loader = MultiLayerConfigLoader()
    return _config_loader


# =========================================
# 편의 함수들 (Guestimation 전용)
# =========================================

def get_web_search_mode() -> str:
    """현재 웹 검색 모드 반환 (Guestimation Layer 3)"""
    return get_multilayer_config().get_web_search_mode()


def is_interactive() -> bool:
    """Interactive 모드 여부 (Guestimation Layer 2, 3)"""
    return get_multilayer_config().is_interactive_mode()


def get_guestimation_config() -> GuestimationConfig:
    """Guestimation 전용 설정 전체 반환"""
    return get_multilayer_config().get_guestimation_config()

