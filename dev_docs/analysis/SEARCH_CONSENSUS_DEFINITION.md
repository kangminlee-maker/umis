# Search Consensus (검색 엔진 공통 맥락) 정의

**출처**: `umis.yaml` line 5527-5533  
**Layer**: Guestimation Layer 3 (Source 3)  
**작성일**: 2025-11-05

---

## 📋 umis.yaml 원본 정의

```yaml
source_3_search_consensus:
  name: "검색 엔진 공통 맥락"
  description: "상위 검색 결과의 공통 패턴/범위"
  ai_method: "웹 서치 → 상위 5-10개 결과 분석 → 공통 값/범위 추출"
  trust: "High (복수 출처)"
  example: "'평균 식사 가격' → 상위 결과 공통: 8천~1.5만원"
  use_when: "최신 정보, 합의된 값 필요"
```

---

## 🎯 핵심 내용

### 정의
**상위 검색 결과에서 공통적으로 나타나는 값 또는 범위**

### 방법
1. 웹 서치 실행
2. 상위 5-10개 결과 분석
3. 공통 값/범위 추출

### 신뢰도
- **High (복수 출처)**
- 여러 출처가 동의하는 값이므로 신뢰도 높음

### 사용 시점
- 최신 정보 필요
- 합의된 값 필요
- 객관적 데이터 없을 때

---

## 💡 현재 구현과 비교

### umis.yaml 정의 (원본)
- 상위 **5-10개** 결과
- 공통 패턴/범위 추출
- 예시: "8천~1.5만원" (범위)

### 현재 Multi-Layer 구현 (v7.2.1)
- 상위 **20개** 결과 (확장됨!)
- 이상치 제거 (IQR)
- 유사도 0.7 클러스터링
- 최대 클러스터 중앙값

**개선사항**:
- ✅ 더 많은 결과 (5-10개 → 20개)
- ✅ 이상치 자동 제거
- ✅ 정밀한 공통값 추출

---

## 🔧 설정 매핑

### umis.yaml 개념 → config/multilayer_config.yaml

**umis.yaml**:
```yaml
source_3_search_consensus:
  ai_method: "웹 서치 → 상위 5-10개 → 공통값"
```

**multilayer_config.yaml** (구현):
```yaml
layer_3_web_search:
  mode: "native"  # Cursor web_search tool
  
  api:
    results_count: 20  # ← 5-10개에서 20개로 확장!
  
  consensus_extraction:
    # 공통값 추출 방법
    outlier_removal:
      enabled: true
      threshold: 1.5  # IQR * 1.5
    
    similarity_based:
      threshold: 0.7  # 유사도 0.7 이상
    
    clustering:
      min_cluster_size: 3
```

---

## 📊 구현 예시

### umis.yaml 예시
```
질문: "평균 식사 가격은?"
→ 웹 검색
→ 상위 5-10개: [8000, 12000, 10000, 9000, 15000]
→ 공통: 8천~1.5만원
```

### 현재 구현 (v7.2.1)
```python
질문: "평균 식사 가격은?"
→ SerpAPI 검색 (20개)
→ 추출: [8000, 12000, 10000, 50000, 9000, 15000, ...]
→ 이상치 제거: 50000 제거 (IQR)
→ 클러스터링: [8000, 9000, 10000, 12000, 15000]
→ 유사도 0.7 이상만
→ 중앙값: 10,000원
```

**차이점**:
- ✅ 이상치 자동 감지 및 제거
- ✅ 더 정확한 중앙값 (범위 아닌 값)
- ✅ 알고리즘 명확

---

## 🎯 설계 일치성 검증

### umis.yaml 요구사항 vs 구현

| 요구사항 | 구현 상태 |
|---------|----------|
| 웹 서치 | ✅ Native (Cursor) / API (SerpAPI) |
| 상위 5-10개 | ✅ 확장 (20개) |
| 공통 값/범위 추출 | ✅ 이상치 제거 + 클러스터링 |
| 신뢰도 High | ✅ 0.75-0.8 |
| 최신 정보 | ✅ SerpAPI 실시간 |

**결론**: ✅ **umis.yaml 정의를 완전히 구현하고 개선함**

---

## 💡 Interactive 모드와의 관계

### umis.yaml에는 Interactive 언급 없음

**Interactive는**:
- Guestimation 구현 시 추가된 기능
- umis.yaml 원본에는 없음
- Layer 2, 3에서 사용자 입력 옵션

**따라서**:
- ✅ `config/multilayer_config.yaml`에 위치 적절
- ❌ `.env` 전역 설정 아님 (맞음)

---

## 🎉 최종 결론

**Search Consensus = Layer 3 웹 검색 공통 맥락**

**umis.yaml 원본 정의**:
- 상위 5-10개 검색 결과의 공통 값

**현재 구현 (개선)**:
- 상위 20개
- 이상치 제거
- 유사도 0.7 클러스터링
- 정밀한 공통값 추출

**설정 위치**: ✅ `config/multilayer_config.yaml` (Guestimation 전용, 적절)

---

**작성**: 2025-11-05  
**검증**: ✅ umis.yaml 정의와 일치

