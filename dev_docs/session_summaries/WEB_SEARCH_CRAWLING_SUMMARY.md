# Web Search 페이지 크롤링 기능 - 빠른 시작 가이드

## ✨ 무엇이 개선되었나요?

Google 검색 API가 반환하는 snippet(요약)은 **약 160자**로 제한되어 있어 충분한 정보를 얻기 어려웠습니다.

이제 **v7.7.0**부터 검색 결과의 **실제 페이지를 크롤링**하여 훨씬 많은 정보를 얻을 수 있습니다!

## 📊 성능 비교

| 모드 | 텍스트량/페이지 | 총 텍스트 | 추출 숫자 |
|------|----------------|----------|----------|
| **기존 (Snippet)** | ~111자 | 553자 | 4개 |
| **신규 (크롤링)** | ~4,108자 | 20,538자 | 41개 |
| **개선율** | **37배** | **37배** | **10배** |

## 🚀 사용법 (1분 설정)

### 1. 패키지 설치

```bash
pip install requests beautifulsoup4
```

### 2. .env 설정

`.env` 파일에 다음 추가:

```bash
# 페이지 크롤링 활성화 (기본값: true)
WEB_SEARCH_FETCH_FULL_PAGE=true

# 페이지당 최대 추출 문자 수 (기본값: 5000)
WEB_SEARCH_MAX_CHARS=5000

# 크롤링 타임아웃 (초, 기본값: 10)
WEB_SEARCH_TIMEOUT=10
```

### 3. 완료! 🎉

이제 자동으로 페이지 크롤링이 활성화됩니다.

## 🧪 테스트

### 빠른 테스트 (단일 URL)

```bash
python scripts/test_web_search_crawling.py --mode url
```

**예상 출력:**
```
✅ 크롤링 성공!
  추출된 문자 수: 5,000자
```

### 성능 비교 테스트

```bash
python scripts/compare_snippet_vs_crawling.py
```

**예상 출력:**
```
📈 비교 결과:
  Snippet 모드: 553자
  크롤링 모드: 20,538자
  증가율: 3613.9% 증가

  ✅ 크롤링 모드에서 19,985자 더 많은 정보 획득!
```

## ⚙️ 설정 옵션

### 크롤링 비활성화 (snippet만 사용)

속도가 중요한 경우:

```bash
WEB_SEARCH_FETCH_FULL_PAGE=false
```

### 더 많은 정보 필요

```bash
WEB_SEARCH_MAX_CHARS=10000  # 5000 → 10000
```

### 느린 네트워크 환경

```bash
WEB_SEARCH_TIMEOUT=15  # 10 → 15
```

## 🔧 작동 원리

```
1. Google/DuckDuckGo 검색 → 5개 결과 (URL + snippet)
   ↓
2. 각 URL 방문 → 실제 페이지 크롤링 (최대 5,000자)
   ↓
3. 크롤링 실패 시 → 자동으로 snippet 사용 (fallback)
   ↓
4. 텍스트에서 숫자 추출 → Consensus 알고리즘
   ↓
5. 신뢰도 높은 값 반환
```

## ⚠️ 주의사항

### 응답 시간

- **Snippet 모드**: ~1-2초
- **크롤링 모드**: ~10-15초 (5개 페이지 크롤링)

정확도가 중요하면 크롤링 모드를, 속도가 중요하면 snippet 모드를 사용하세요.

### 일부 사이트 차단

일부 사이트는 봇 크롤링을 차단할 수 있습니다.
→ 자동으로 snippet을 사용합니다 (걱정 안 해도 됩니다!)

## 📚 상세 문서

더 자세한 정보는 다음 문서를 참고하세요:

- [Web Search 크롤링 가이드](docs/guides/WEB_SEARCH_CRAWLING_GUIDE.md) - 전체 가이드
- [ENV 설정 가이드](setup/ENV_SETUP_GUIDE.md) - 환경 변수 설정
- [CHANGELOG](CHANGELOG.md) - v7.7.0 변경사항

## 🎯 권장 설정

대부분의 경우 **기본 설정**을 그대로 사용하면 됩니다:

```bash
WEB_SEARCH_FETCH_FULL_PAGE=true  # 크롤링 활성화
WEB_SEARCH_MAX_CHARS=5000        # 5,000자 제한
WEB_SEARCH_TIMEOUT=10            # 10초 타임아웃
```

이 설정으로 **정확도와 속도의 최적 균형**을 얻을 수 있습니다! ⚡

---

**버전**: v7.7.0
**날짜**: 2025-11-12
**문제 해결**: 구글 검색 API 500자 제한 → 20,000자 이상 획득 (40배 개선)

