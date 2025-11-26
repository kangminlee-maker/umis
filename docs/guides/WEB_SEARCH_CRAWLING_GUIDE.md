# Web Search 페이지 크롤링 가이드 (v7.11.1)

## 📋 개요

v7.11.1 4-Stage Fusion Architecture의 Stage 1 (Evidence Collection)에서 Google/DuckDuckGo 검색 결과의 실제 페이지를 크롤링하여 더 많은 정보를 획득할 수 있습니다.

### 성능 비교

| 모드 | 평균 텍스트량 | 숫자 추출 | 설명 |
|------|--------------|----------|------|
| **Snippet만** | ~111자/페이지 | 4개 | 검색 결과 요약만 사용 (기존) |
| **크롤링** | ~4,108자/페이지 | 41개 | 실제 페이지 내용 크롤링 (신규) |
| **개선율** | **3,614% 증가** | **10배 이상** | 훨씬 많은 정보 획득 |

## 🚀 사용법

### 1. 기본 설정 (.env)

```bash
# 페이지 크롤링 활성화 (기본값: true)
WEB_SEARCH_FETCH_FULL_PAGE=true

# 페이지당 최대 추출 문자 수 (기본값: 5000)
WEB_SEARCH_MAX_CHARS=5000

# 크롤링 타임아웃 (초, 기본값: 10)
WEB_SEARCH_TIMEOUT=10
```

### 2. 코드에서 사용

```python
from umis_rag.agents.estimator.sources.value import WebSearchSource
from umis_rag.agents.estimator.models import Context

# 초기화 (자동으로 .env 설정 읽기)
web_source = WebSearchSource()

# 검색 및 크롤링
estimates = web_source.collect(
    question="대한민국 인구는?",
    context=Context(region="South Korea")
)

# 결과 확인
for estimate in estimates:
    print(f"값: {estimate.value:,.0f}")
    print(f"신뢰도: {estimate.confidence:.2f}")
    print(f"출처: {estimate.source_detail}")
```

## ⚙️ 설정 옵션

### WEB_SEARCH_FETCH_FULL_PAGE

- **true** (권장): 검색 결과 URL을 방문하여 실제 페이지 내용 크롤링
  - 장점: 훨씬 많은 정보, 높은 정확도
  - 단점: 약간 느림 (페이지당 ~2초)

- **false**: Snippet만 사용 (기존 방식)
  - 장점: 빠름
  - 단점: 정보 제한적 (~160자)

### WEB_SEARCH_MAX_CHARS

페이지당 최대 추출 문자 수를 제한합니다.

```bash
# 기본값 (권장)
WEB_SEARCH_MAX_CHARS=5000

# 더 많은 정보 필요 시
WEB_SEARCH_MAX_CHARS=10000

# 빠른 응답 필요 시
WEB_SEARCH_MAX_CHARS=2000
```

**권장값**: 5,000자
- 대부분의 정보를 포함하면서도 빠른 응답
- 메모리 효율적

### WEB_SEARCH_TIMEOUT

각 페이지 크롤링 시 최대 대기 시간 (초)

```bash
# 기본값 (권장)
WEB_SEARCH_TIMEOUT=10

# 느린 네트워크 환경
WEB_SEARCH_TIMEOUT=15

# 빠른 응답 필요 시
WEB_SEARCH_TIMEOUT=5
```

**권장값**: 10초
- 대부분의 페이지를 안정적으로 로드
- 너무 느린 페이지는 자동으로 스킵 (snippet 사용)

## 🔍 작동 원리

### 1. 검색 엔진 호출

```
Google/DuckDuckGo → 5개 검색 결과 (URL + snippet)
```

### 2. 페이지 크롤링 (WEB_SEARCH_FETCH_FULL_PAGE=true인 경우)

```python
for result in search_results:
    # 실제 페이지 방문
    page_content = fetch_page_content(result['url'])

    if page_content:
        # 크롤링 성공: snippet 대체
        result['body'] = page_content  # ~5,000자
    else:
        # 크롤링 실패: snippet 유지
        result['body'] = result['snippet']  # ~160자
```

### 3. 텍스트 추출 및 정리

- **불필요한 요소 제거**: script, style, nav, header, footer, aside, iframe
- **텍스트 추출**: BeautifulSoup으로 실제 내용만 추출
- **공백 정리**: 연속 공백 제거, 줄바꿈 정리
- **길이 제한**: max_chars로 자르기

### 4. 숫자 추출 및 Consensus

```python
# 추출된 텍스트에서 숫자 패턴 매칭
numbers = extract_numbers_from_results(results)

# 여러 출처에서 일치하는 값 찾기
consensus = find_consensus(numbers)
# → 2개 이상 출처에서 ±30% 범위 내 값이면 신뢰
```

## 📊 성능 벤치마크

### 질문: "대한민국 인구는?"

| 메트릭 | Snippet 모드 | 크롤링 모드 | 개선율 |
|--------|-------------|------------|--------|
| 총 텍스트 | 553자 | 20,538자 | +3,614% |
| 평균/페이지 | 111자 | 4,108자 | +3,600% |
| 추출 숫자 | 4개 | 41개 | +925% |
| 응답 시간 | ~1초 | ~12초 | -1,100% |
| 정확도 | 중간 | 높음 | - |

### 질문: "서울 면적은?"

| 메트릭 | Snippet 모드 | 크롤링 모드 | 개선율 |
|--------|-------------|------------|--------|
| 총 텍스트 | ~600자 | ~19,000자 | +3,000% |
| 추출 숫자 | 3개 | 24개 | +700% |

## ⚠️ 주의사항

### 1. 응답 시간

크롤링 모드는 snippet 모드보다 느립니다:
- **Snippet 모드**: ~1-2초
- **크롤링 모드**: ~10-15초 (5개 페이지 × 2-3초)

### 2. 네트워크 트래픽

크롤링은 더 많은 데이터를 다운로드합니다:
- **Snippet**: ~5KB
- **크롤링**: ~50-100KB (페이지 크기에 따라)

### 3. 일부 사이트 차단

일부 사이트는 봇 크롤링을 차단할 수 있습니다:
- User-Agent 헤더로 일반 브라우저처럼 위장
- 차단되면 자동으로 snippet 사용 (fallback)

### 4. Consensus 실패 가능성

너무 많은 숫자가 추출되면 Consensus를 찾기 어려울 수 있습니다:
- 해결: 더 구체적인 검색 쿼리 사용
- 예: "대한민국 인구" → "대한민국 인구 2024"

## 🧪 테스트

### 단일 URL 크롤링 테스트

```bash
python scripts/test_web_search_crawling.py --mode url
```

**출력 예시:**
```
✅ 크롤링 성공!
  추출된 문자 수: 5,000자
  내용 샘플: South Korea - Wikipedia...
```

### 전체 검색 테스트

```bash
python scripts/test_web_search_crawling.py --mode full
```

### Snippet vs 크롤링 비교

```bash
python scripts/compare_snippet_vs_crawling.py
```

**출력 예시:**
```
📈 비교 결과:
  Snippet 모드: 553자
  크롤링 모드: 20,538자
  증가율: 3613.9% 증가

  ✅ 크롤링 모드에서 19,985자 더 많은 정보 획득!
```

## 🔧 트러블슈팅

### 문제: 크롤링이 작동하지 않음

**확인 사항:**
1. `.env`에 `WEB_SEARCH_FETCH_FULL_PAGE=true` 설정되어 있는지
2. `requests`, `beautifulsoup4` 패키지 설치되어 있는지

```bash
pip install requests beautifulsoup4
```

### 문제: 타임아웃 에러

**해결:**
```bash
# .env
WEB_SEARCH_TIMEOUT=15  # 기본 10 → 15로 증가
```

### 문제: 크롤링 성공했지만 결과 없음

**원인**: Consensus 알고리즘이 일치하는 값을 못 찾음
- 너무 많은 숫자가 추출되어 값이 분산됨

**해결:**
1. 더 구체적인 질문 사용
2. Context 추가 (region, domain 등)
3. 검색 쿼리 개선

## 📝 FAQ

### Q1: 크롤링 모드를 기본으로 사용해도 되나요?

**A**: 네, 권장합니다.
- 정확도가 훨씬 높습니다
- 응답 시간이 중요하지 않으면 항상 활성화

### Q2: 일부 페이지만 크롤링하고 싶어요

**A**: 현재는 전체 on/off만 가능합니다.
- 향후 업데이트에서 선택적 크롤링 지원 예정

### Q3: 크롤링 실패 시 어떻게 되나요?

**A**: 자동으로 snippet을 사용합니다 (fallback).
- 크롤링 실패해도 검색 자체는 계속됩니다

### Q4: 비용이 추가로 드나요?

**A**: 아니요.
- 크롤링은 무료입니다 (일반 HTTP 요청)
- Google Custom Search API 비용은 동일 ($5/1000 쿼리)

## 🎯 권장 설정

### 프로덕션 (정확도 중시)

```bash
WEB_SEARCH_FETCH_FULL_PAGE=true
WEB_SEARCH_MAX_CHARS=5000
WEB_SEARCH_TIMEOUT=10
```

### 개발 (빠른 테스트)

```bash
WEB_SEARCH_FETCH_FULL_PAGE=false
WEB_SEARCH_MAX_CHARS=2000
WEB_SEARCH_TIMEOUT=5
```

### 고성능 서버 (최대 정보)

```bash
WEB_SEARCH_FETCH_FULL_PAGE=true
WEB_SEARCH_MAX_CHARS=10000
WEB_SEARCH_TIMEOUT=15
```

## 📚 관련 문서

- [Web Search 설정 가이드](../setup/ENV_SETUP_GUIDE.md)
- [Estimator Stage 1 (Evidence Collection)](../../umis_core.yaml#L603-693)
- [Value Sources 아키텍처](../../umis_rag/agents/estimator/sources/value.py)

## 📅 변경 이력

### v7.11.1 (2025-11-26)
- 📝 4-Stage Fusion Architecture 반영
- 📝 Estimator Stage 1 (Evidence Collection) 참조 업데이트

### v7.7.0 (2025-11-12)
- ✨ 페이지 크롤링 기능 추가
- ✨ BeautifulSoup 기반 텍스트 추출
- ✨ 자동 fallback (크롤링 실패 시 snippet 사용)
- ✨ 설정 가능한 타임아웃 및 문자 수 제한
- 📊 테스트 스크립트 추가
- 📚 문서 업데이트

---

**작성자**: UMIS Team
**버전**: v7.11.1
**날짜**: 2025-11-26

