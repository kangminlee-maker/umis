"""
Layer Manager: Overlay Layer 관리

FINAL_DECISION 06_overlay_layer 스펙:
- Core / Team / Personal 3-Layer
- 우선순위 검색 (Personal > Team > Core)
- Merge 전략 (append / replace / patch)
"""

import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional

import sys
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.utils.logger import get_logger

logger = get_logger(__name__)


class LayerManager:
    """
    Overlay Layer 관리자
    
    기능:
    - 3-Layer 데이터 로드 (Core / Team / Personal)
    - 우선순위 기반 검색
    - Merge 전략 적용
    
    사용:
    -----
    manager = LayerManager('layer_config.yaml')
    
    # Personal > Team > Core 순서로 검색
    data = manager.load_with_overlay('patterns.yaml')
    """
    
    def __init__(self, config_path: str = "layer_config.yaml"):
        """
        Args:
            config_path: layer_config.yaml 경로
        """
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.enabled = self.config.get('enabled', False)
        
        logger.info(f"LayerManager 초기화")
        logger.info(f"  Overlay 활성화: {self.enabled}")
        
        if self.enabled:
            logger.info(f"  검색 순서: {self.config.get('search_order', [])}")
    
    def _load_config(self) -> Dict[str, Any]:
        """layer_config.yaml 로드"""
        if not self.config_path.exists():
            logger.warning(f"  ⚠️  Layer config 없음: {self.config_path}")
            return {'enabled': False}
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def load_with_overlay(
        self,
        file_name: str,
        user_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Overlay Layer를 고려하여 파일 로드
        
        Args:
            file_name: 파일명 (patterns.yaml 등)
            user_name: 사용자명 (Personal Layer용)
        
        Returns:
            Merged 데이터
        """
        # Overlay 비활성화 시 Core만
        if not self.enabled:
            return self._load_core_only(file_name)
        
        logger.info(f"[LayerManager] Overlay 로드: {file_name}")
        
        # 검색 순서대로 로드
        search_order = self.config.get('search_order', ['core'])
        layers_data = {}
        
        for layer_name in search_order:
            data = self._load_layer(layer_name, file_name, user_name)
            if data:
                layers_data[layer_name] = data
                logger.info(f"  ✅ {layer_name} Layer 로드됨")
        
        # Merge
        if layers_data:
            merged = self._merge_layers(layers_data, file_name)
            logger.info(f"  ✅ {len(layers_data)}개 Layer 병합 완료")
            return merged
        
        logger.warning(f"  ⚠️  모든 Layer에서 {file_name} 없음")
        return {}
    
    def _load_core_only(self, file_name: str) -> Dict[str, Any]:
        """Core Layer만 로드 (Overlay 비활성)"""
        core_layer = self.config.get('layers', {}).get('core', {})
        core_path = Path(core_layer.get('path', 'data/raw/'))
        
        file_path = core_path / file_name
        
        if not file_path.exists():
            # 현재 data/raw에 있을 수도 있음
            file_path = Path('data/raw') / file_name
        
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        
        return {}
    
    def _load_layer(
        self,
        layer_name: str,
        file_name: str,
        user_name: Optional[str]
    ) -> Optional[Dict[str, Any]]:
        """특정 Layer에서 파일 로드"""
        layer_config = self.config.get('layers', {}).get(layer_name)
        
        if not layer_config:
            return None
        
        # 경로 구성
        layer_path = layer_config['path']
        
        # Personal Layer는 user_name 필요
        if layer_name == 'personal':
            if not user_name:
                user_name = self.config.get('current_user', {}).get('name', 'default')
            layer_path = layer_path.replace('{user_name}', user_name)
        
        file_path = Path(layer_path) / file_name
        
        # 파일 로드
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        
        return None
    
    def _merge_layers(
        self,
        layers_data: Dict[str, Dict[str, Any]],
        file_name: str
    ) -> Dict[str, Any]:
        """
        여러 Layer 데이터를 Merge
        
        Args:
            layers_data: {layer_name: data}
            file_name: 파일명 (merge 전략 결정용)
        
        Returns:
            Merged 데이터
        """
        # Merge 전략 결정
        strategy = self._get_merge_strategy(file_name)
        
        # 검색 순서 (Personal > Team > Core)
        search_order = self.config.get('search_order', ['core'])
        
        # Base: 가장 낮은 우선순위 (Core)
        merged = layers_data.get(search_order[-1], {}).copy()
        
        # 우선순위 순서로 Merge
        for layer_name in reversed(search_order[:-1]):
            if layer_name in layers_data:
                layer_data = layers_data[layer_name]
                merged = self._apply_merge_strategy(merged, layer_data, strategy)
        
        return merged
    
    def _get_merge_strategy(self, file_name: str) -> str:
        """파일명 기반 Merge 전략 결정"""
        merge_config = self.config.get('merge_strategy', {})
        
        # 파일 타입별 전략
        if 'pattern' in file_name.lower():
            return merge_config.get('by_type', {}).get('patterns', 'append')
        elif 'case' in file_name.lower():
            return merge_config.get('by_type', {}).get('cases', 'append')
        elif 'config' in file_name.lower():
            return merge_config.get('by_type', {}).get('config', 'replace')
        
        # 기본값
        return merge_config.get('default', 'replace')
    
    def _apply_merge_strategy(
        self,
        base: Dict[str, Any],
        overlay: Dict[str, Any],
        strategy: str
    ) -> Dict[str, Any]:
        """
        Merge 전략 적용
        
        Args:
            base: 베이스 데이터 (Core)
            overlay: 덮어쓸 데이터 (Team/Personal)
            strategy: append / replace / patch
        
        Returns:
            Merged 데이터
        """
        if strategy == 'replace':
            # 완전 덮어쓰기
            return {**base, **overlay}
        
        elif strategy == 'append':
            # 누적 (list 값들을 append)
            merged = base.copy()
            
            for key, value in overlay.items():
                if key in merged:
                    # 기존 값이 list면 append
                    if isinstance(merged[key], list) and isinstance(value, list):
                        merged[key] = merged[key] + value
                    else:
                        # 그 외는 replace
                        merged[key] = value
                else:
                    merged[key] = value
            
            return merged
        
        elif strategy == 'patch':
            # 일부만 업데이트 (deep merge)
            merged = base.copy()
            
            for key, value in overlay.items():
                if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                    # Dict는 재귀 merge
                    merged[key] = self._apply_merge_strategy(merged[key], value, 'patch')
                else:
                    merged[key] = value
            
            return merged
        
        # 기본값은 replace
        return {**base, **overlay}
    
    def get_layer_info(self, layer_name: str) -> Optional[Dict[str, Any]]:
        """Layer 정보 조회"""
        return self.config.get('layers', {}).get(layer_name)
    
    def is_enabled(self) -> bool:
        """Overlay Layer 활성화 여부"""
        return self.enabled


# 예시 사용
if __name__ == "__main__":
    print("=" * 60)
    print("LayerManager 테스트")
    print("=" * 60)
    
    manager = LayerManager('layer_config.yaml')
    
    # 1. Layer 설정 확인
    print("\n[1] Layer 설정")
    print(f"Overlay 활성화: {manager.is_enabled()}")
    
    for layer_name in ['core', 'team', 'personal']:
        info = manager.get_layer_info(layer_name)
        if info:
            print(f"\n{layer_name.upper()} Layer:")
            print(f"  경로: {info['path']}")
            print(f"  우선순위: {info['priority']}")
            print(f"  접근: {info['write_access']}")
    
    # 2. Merge 전략
    print("\n[2] Merge 전략")
    
    test_cases = [
        ('patterns.yaml', 'append'),
        ('config.yaml', 'replace'),
        ('cases.yaml', 'append')
    ]
    
    for filename, expected in test_cases:
        strategy = manager._get_merge_strategy(filename)
        print(f"  {filename}: {strategy}")
    
    # 3. Merge 테스트
    print("\n[3] Merge 테스트 (append)")
    
    base = {'items': ['A', 'B'], 'version': '1.0'}
    overlay = {'items': ['C'], 'version': '1.1'}
    
    merged = manager._apply_merge_strategy(base, overlay, 'append')
    print(f"  Base: {base}")
    print(f"  Overlay: {overlay}")
    print(f"  Merged: {merged}")
    
    print("\n✅ LayerManager 작동 확인")

