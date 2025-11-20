#!/usr/bin/env python3
"""
API Key 파싱 테스트

KOSIS API Key에 '=' 문자가 포함되어도
올바르게 로드되는지 확인

사용:
    python scripts/test_api_key_parsing.py
"""

import os
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

def test_api_key_parsing():
    """API Key 파싱 테스트"""
    
    print("="*60)
    print("API Key 파싱 테스트")
    print("="*60)
    
    # .env 로드
    load_dotenv()
    
    # DART API Key
    dart_key = os.getenv('DART_API_KEY')
    print(f"\nDART_API_KEY:")
    print(f"  존재: {'✓' if dart_key else '✗'}")
    if dart_key:
        print(f"  길이: {len(dart_key)}자")
        print(f"  값: {dart_key[:10]}...{dart_key[-10:] if len(dart_key) > 20 else ''}")
        print(f"  '=' 포함: {'✓' if '=' in dart_key else '✗'}")
    
    # KOSIS API Key
    kosis_key = os.getenv('KOSIS_API_KEY')
    print(f"\nKOSIS_API_KEY:")
    print(f"  존재: {'✓' if kosis_key else '✗'}")
    if kosis_key:
        print(f"  길이: {len(kosis_key)}자")
        print(f"  값: {kosis_key[:10]}...{kosis_key[-10:] if len(kosis_key) > 20 else ''}")
        print(f"  '=' 포함: {'✓ (따옴표 필수!)' if '=' in kosis_key else '✗ (따옴표 불필요)'}")
        
        if '=' in kosis_key and not (kosis_key == os.getenv('KOSIS_API_KEY')):
            print("  ⚠️ 파싱 오류 가능성!")
            print("  → .env에서 따옴표로 감싸세요:")
            print(f'     KOSIS_API_KEY="{kosis_key}"')
    
    # 결과
    print("\n" + "="*60)
    if dart_key and dart_key != 'your-dart-api-key-here':
        print("✅ DART API Key: 설정됨")
    else:
        print("⚠️ DART API Key: 미설정")
    
    if kosis_key and kosis_key != 'your-kosis-api-key-here':
        print("✅ KOSIS API Key: 설정됨")
        if '=' in kosis_key:
            print("   ℹ️ '=' 문자 포함 → 따옴표 사용 권장")
    else:
        print("⚠️ KOSIS API Key: 미설정")
    
    print("="*60)
    
    # Pydantic Settings 테스트
    print("\nPydantic Settings 로드 테스트:")
    try:
        from umis_rag.core.config import settings
        
        print(f"  DART Key: {'설정됨' if settings.dart_api_key else '미설정'}")
        print(f"  KOSIS Key: {'설정됨' if settings.kosis_api_key else '미설정'}")
        
        if settings.kosis_api_key and '=' in settings.kosis_api_key:
            print(f"  ✓ KOSIS Key '=' 문자 포함, 올바르게 로드됨!")
        
        print("\n✅ Pydantic Settings 정상 작동")
        
    except Exception as e:
        print(f"\n❌ Pydantic Settings 오류: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(test_api_key_parsing())





