#!/usr/bin/env python3
"""UMIS_ARCHITECTURE_BLUEPRINT.md 정리 스크립트"""

import re

def clean_architecture_file():
    file_path = "docs/architecture/UMIS_ARCHITECTURE_BLUEPRINT.md"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Version History 섹션 완전 삭제 (line 862-1016 근처)
    # ## 📚 Version History부터 다음 ## 섹션 전까지 삭제
    content = re.sub(
        r'## 📚 Version History\n\n.*?(?=\n## 🔧 Configuration Quick Reference)',
        '',
        content,
        flags=re.DOTALL
    )
    
    # 2. 버전 주석 제거 패턴들
    patterns_to_remove = [
        (r' ⭐⭐⭐ NEW!', ''),
        (r' ⭐⭐⭐', ''),
        (r' ⭐⭐', ''),
        (r' ⭐', ''),
        (r' \(v\d+\.\d+\.\d+\+?\)', ''),  # (v7.3.1+) 형태
        (r' \(v\d+\.\d+\.\d+\)', ''),     # (v7.3.1) 형태
        (r' v\d+\.\d+\.\d+:', ':'),       # v7.7.0: → :
        (r' - v\d+\.\d+\.\d+', ''),       # - v7.8.0
    ]
    
    for pattern, replacement in patterns_to_remove:
        content = re.sub(pattern, replacement, content)
    
    # 3. 특정 라인 정리
    # "cursor-native Integration" 같은 부제목 제거
    content = content.replace(' "cursor-native Integration"', '')
    
    # 4. Last Reviewed 라인 업데이트
    content = re.sub(
        r'\*\*Last Reviewed\*\*: .*\n',
        '**Last Reviewed**: 2025-11-24\n',
        content
    )
    
    # 5. Document Owner 섹션 업데이트
    content = re.sub(
        r'\*\*Document Owner\*\*: AI Team\n\*\*Last Reviewed\*\*: .*\n\*\*Next Review\*\*: .*\n',
        '**Document Owner**: AI Team\n**Last Reviewed**: 2025-11-24\n**Next Review**: 버전 업데이트 시\n',
        content
    )
    
    # 6. 마지막 문단에 CHANGELOG 링크 추가
    content = re.sub(
        r'\*이 문서는 UMIS의 "살아있는 설계도"입니다\. 모든 버전 업데이트 시 함께 업데이트되어야 합니다\.\*\n',
        '*이 문서는 UMIS의 "살아있는 설계도"입니다. 모든 버전 업데이트 시 함께 업데이트되어야 합니다.*\n\n**변경 이력**: [CHANGELOG.md](../../CHANGELOG.md)\n',
        content
    )
    
    # 7. 연속된 빈 줄 정리 (3개 이상 → 2개)
    content = re.sub(r'\n\n\n+', '\n\n', content)
    
    # 8. 파일 저장
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ UMIS_ARCHITECTURE_BLUEPRINT.md 정리 완료!")
    print("   - Version History 섹션 삭제")
    print("   - 버전 주석 제거 (⭐, v7.x.x)")
    print("   - CHANGELOG.md 링크 추가")

if __name__ == "__main__":
    clean_architecture_file()
