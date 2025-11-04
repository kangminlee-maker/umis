#!/usr/bin/env python3
"""
모든 범위 하드코딩을 Named Range로 전환
남은 작업을 일괄 처리
"""

print("""
🎯 전부 Named Range 전환 작업

완료:
  ✅ Convergence: AVERAGE, STDEV, MAX/MIN
  ✅ Scenarios: Method별 Best/Base/Worst
  ✅ Method_2: 세그먼트별 SAM
  ✅ Method_4: 경쟁사별
  ✅ Revenue: 세그먼트 Year 0

남은 작업 (복잡도 높음):
  
  Revenue (Year 1-5): 
    - 세그먼트 4개 × Year 5개 = 20개 Named Range
    - 각 Year의 Total도 Named Range 필요
    
  Cost (OPEX): 
    - S&M, R&D, G&A × Year 6개 = 18개 Named Range
    
  예상 추가 Named Range: ~40개
  예상 코드: +100줄

복잡도 증가:
  Before: 코드 100줄, Named Range 44개
  After: 코드 200줄, Named Range 104개

개발 시간: +2시간
검증 시간: +30분

총 투자: 2.5시간

이득:
  - 완벽한 구조 독립성
  - 100% 자동 검증 가능
  - 세그먼트/Method 추가 시 코드 수정 불필요

계속 진행할까요? (y/n)
""")

