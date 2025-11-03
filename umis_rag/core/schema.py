"""
Schema Registry 로더 및 검증

config/schema_registry.yaml 기반으로 메타데이터 검증
"""

import yaml
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime


class SchemaRegistry:
    """Schema Registry 관리"""
    
    def __init__(self, registry_path: str = "config/schema_registry.yaml"):
        self.registry_path = Path(registry_path)
        self.schema = self._load_schema()
    
    def _load_schema(self) -> Dict[str, Any]:
        """config/schema_registry.yaml 로드"""
        with open(self.registry_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def get_id_pattern(self, namespace: str) -> str:
        """ID 패턴 가져오기"""
        return self.schema['id_namespaces'][namespace]['pattern']
    
    def get_id_prefix(self, namespace: str) -> str:
        """ID 접두사 가져오기"""
        return self.schema['id_namespaces'][namespace]['prefix']
    
    def validate_field(self, field_name: str, value: Any, layer: str = None) -> bool:
        """필드 검증"""
        # Core fields 확인
        if field_name in self.schema['core_fields']:
            field_spec = self.schema['core_fields'][field_name]
            return self._validate_type(value, field_spec)
        
        # Layer-specific 확인
        if layer:
            layer_key = f"layer_{layer}"
            if layer_key in self.schema:
                layer_fields = self.schema[layer_key].get('fields', {})
                if field_name in layer_fields:
                    return self._validate_type(value, layer_fields[field_name])
        
        return True
    
    def _validate_type(self, value: Any, spec: Dict) -> bool:
        """타입 검증"""
        field_type = spec.get('type')
        
        if field_type == 'string':
            return isinstance(value, str)
        elif field_type == 'int':
            return isinstance(value, int)
        elif field_type == 'float':
            return isinstance(value, float)
        elif field_type == 'bool':
            return isinstance(value, bool)
        elif field_type == 'datetime':
            return isinstance(value, str)  # ISO 8601 문자열
        elif field_type == 'enum':
            values = spec.get('values', [])
            return value in values
        elif field_type == 'object':
            return isinstance(value, dict)
        elif field_type == 'array':
            return isinstance(value, list)
        
        return True
    
    def get_required_fields(self, layer: str) -> List[str]:
        """필수 필드 목록"""
        required = []
        
        # Core fields
        for field, spec in self.schema['core_fields'].items():
            if isinstance(spec, dict) and spec.get('required'):
                required.append(field)
        
        return required


def generate_id(prefix: str, base: str) -> str:
    """
    고유 ID 생성
    
    Args:
        prefix: CAN/PRJ/GND/GED/MEM/RAE
        base: 기본 문자열
    
    Returns:
        {prefix}-{hash8}
    """
    import hashlib
    
    hash_input = f"{base}-{datetime.now().isoformat()}"
    hash_hex = hashlib.sha256(hash_input.encode()).hexdigest()[:8]
    
    return f"{prefix}-{hash_hex}"


def calculate_content_hash(content: str) -> str:
    """
    내용 SHA-256 해시
    
    Args:
        content: 텍스트 내용
    
    Returns:
        sha256:...
    """
    import hashlib
    
    hash_hex = hashlib.sha256(content.encode('utf-8')).hexdigest()
    return f"sha256:{hash_hex}"

