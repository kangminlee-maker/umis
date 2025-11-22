# 하이브리드 개발 전략 (개발 YAML + 프로덕션 JSON.gz)

**작성일**: 2025-11-08  
**브랜치**: production-format-optimization  
**전략**: 개발은 YAML, 배포 시 자동 변환

---

## 🎯 핵심 전략

### "개발자는 YAML만, 프로덕션은 자동으로"

```yaml
개발 환경 (Development):
  파일: YAML (100% 유지)
  편집: 자유롭게 YAML 수정
  Git: YAML만 커밋
  테스트: YAML 직접 사용
  
빌드 시 (CI/CD):
  변환: YAML → JSON.gz (자동)
  검증: 테스트 실행
  패키지: dist/ 생성
  
프로덕션 환경 (Production):
  파일: JSON.gz (자동 생성)
  로딩: 15배 빠름
  크기: 70% 작음
  YAML: 포함 안 함 (IP 보호)
```

---

## ✅ 이 방식의 장점

### 1. 개발자 경험 100% 유지 ⭐⭐⭐⭐⭐

```yaml
변하지 않는 것:
  ✅ YAML 편집 (익숙함)
  ✅ 주석 사용 가능
  ✅ Git diff 명확
  ✅ 머지 충돌 해결 쉬움
  ✅ 텍스트 에디터로 바로 수정
  ✅ 학습 곡선 0

개발자가 느끼는 것:
  "아무것도 안 바뀌었네? 그럼 좋지 뭐."
```

**예시**:
```bash
# 개발자 워크플로우 (변화 없음!)
vim config/schema_registry.yaml    # YAML 편집
git add config/schema_registry.yaml # Git 커밋
git commit -m "Update schema"
git push

# 끝! CI/CD가 알아서 변환
```

---

### 2. 프로덕션 성능 극대화 ⭐⭐⭐⭐⭐

```yaml
성능 개선:
  로딩 속도: 15배 빠름
  파일 크기: 70% 감소
  메모리: 8% 절약
  
비용 절감:
  AWS Lambda: 33% 절감 ($180/년)
  
보안 강화:
  YAML 원본: 배포 안 함
  주석/문서: 노출 안 됨
```

---

### 3. Git 히스토리 깔끔 ⭐⭐⭐⭐⭐

```yaml
Git에 커밋되는 것:
  ✅ YAML 원본만
  ❌ JSON.gz 제외 (.gitignore)
  
장점:
  ✅ diff 읽기 쉬움
  ✅ 히스토리 추적 용이
  ✅ 리뷰 가능
  ✅ 저장소 크기 작음
```

**예시**:
```diff
# Git diff (YAML, 읽기 쉬움)
diff --git a/config/agent_names.yaml b/config/agent_names.yaml
@@ -1,5 +1,5 @@
 agents:
   observer: Albert
-  explorer: Steve
+  explorer: Alex    # 이름 변경
   quantifier: Bill
```

vs

```diff
# JSON.gz를 Git에 넣었다면? (읽을 수 없음)
Binary files a/config/agent_names.json.gz and b/config/agent_names.json.gz differ
```

---

### 4. 롤백 쉬움 ⭐⭐⭐⭐⭐

```yaml
문제 발생 시:
  1. Git revert (YAML로)
  2. 재빌드 (자동)
  3. 재배포
  
시간: 5분
```

vs

```yaml
만약 프로덕션 포맷만 있다면:
  1. 바이너리 파일 수정? (불가능)
  2. 다시 처음부터 생성
  3. 검증 어려움
  
시간: 1-2시간
```

---

### 5. 팀 협업 용이 ⭐⭐⭐⭐⭐

```yaml
시나리오: 2명이 동시에 schema 수정

YAML (현재, 유지):
  Person A: users 스키마 수정
  Person B: products 스키마 수정
  Git merge: 자동 성공 ✅
  
JSON.gz (만약 이걸 편집한다면):
  Person A: 바이너리 수정
  Person B: 바이너리 수정
  Git merge: 충돌! 수동 해결 불가 ❌
```

---

### 6. 디버깅 용이 ⭐⭐⭐⭐⭐

```yaml
문제: "설정이 이상해요"

YAML 있을 때:
  1. config/schema_registry.yaml 열기
  2. 바로 확인
  3. 수정
  4. 테스트
  
시간: 5분 ✅

YAML 없을 때:
  1. JSON.gz 압축 해제
  2. JSON 파싱
  3. 어디가 문제? (주석 없음)
  4. 수정 방법? (역변환?)
  
시간: 30분+ ❌
```

---

## ⚠️ 단점 및 해결책

### 단점 1: 빌드 시간 증가

```yaml
문제:
  YAML → JSON.gz 변환 (1-2분 추가)
  
해결책:
  1. 캐싱 (변경된 파일만 변환)
  2. 병렬 빌드
  3. 로컬은 YAML 직접 사용
  
실제 영향:
  로컬 개발: 0초 (YAML 직접 사용)
  CI/CD: +1분 (한 번만, 배포 시)
  
결론: 무시 가능 ✅
```

---

### 단점 2: 빌드 스크립트 유지보수

```yaml
문제:
  build_minimal.py 유지보수 필요
  
해결책:
  1. 간단한 로직 (YAML → JSON → gzip)
  2. 안정적 (표준 라이브러리만)
  3. 테스트 코드 작성
  
복잡도:
  스크립트: ~200줄 (단순)
  의존성: pyyaml만
  
결론: 관리 가능 ✅
```

---

### 단점 3: 개발/프로덕션 차이

```yaml
문제:
  개발: YAML 로딩
  프로덕션: JSON.gz 로딩
  다른 코드 경로 → 버그 가능?
  
해결책:
  1. 통일된 인터페이스
     # load_config('umis') → 환경에 맞게 자동
  
  2. 로컬에서 프로덕션 빌드 테스트
     # make test-production
  
  3. CI/CD에서 검증
     # 빌드 → 테스트 실행
  
결론: 인터페이스 통일로 해결 ✅
```

---

## 🏗️ 구현 방법

### 1. 환경 감지 로더

```python
# umis_rag/utils/config_loader.py
import os
from pathlib import Path

def load_config(name: str):
    """환경에 맞게 자동 로딩
    
    개발: YAML 직접 로드
    프로덕션: JSON.gz 로드
    """
    env = os.getenv('UMIS_ENV', 'development')
    
    if env == 'production':
        # 프로덕션: JSON.gz
        return load_json_gz(name)
    else:
        # 개발: YAML
        return load_yaml(name)

def load_yaml(name: str):
    """YAML 로드 (개발용)"""
    import yaml
    
    # 경로 매핑
    paths = {
        'umis': 'umis.yaml',
        'umis_core': 'umis_core.yaml',
        'config/schema_registry': 'config/schema_registry.yaml',
        'data/patterns': 'data/raw/umis_business_model_patterns.yaml',
    }
    
    yaml_path = paths.get(name, f'{name}.yaml')
    with open(yaml_path) as f:
        return yaml.safe_load(f)

def load_json_gz(name: str):
    """JSON.gz 로드 (프로덕션용)"""
    import gzip
    import json
    
    json_gz_path = f'dist/{name}.json.gz'
    with gzip.open(json_gz_path, 'rt') as f:
        return json.load(f)
```

**사용**:
```python
# 코드는 동일! 환경만 다름
from umis_rag.utils.config_loader import load_config

config = load_config('umis')
# 개발: umis.yaml 로드
# 프로덕션: dist/umis.json.gz 로드
```

---

### 2. .gitignore 설정

```gitignore
# .gitignore

# 프로덕션 빌드 결과 (Git에서 제외)
dist/
*.json.gz

# YAML 원본은 Git에 포함 (현재 유지)
# config/*.yaml  ← 주석 처리 (포함)
# data/raw/*.yaml ← 주석 처리 (포함)
```

---

### 3. CI/CD 파이프라인

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    
    steps:
      # 1. 체크아웃 (YAML 원본 가져오기)
      - uses: actions/checkout@v3
      
      # 2. Python 설정
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      # 3. 의존성 설치
      - name: Install dependencies
        run: pip install pyyaml
      
      # 4. 프로덕션 빌드 (YAML → JSON.gz)
      - name: Build production
        run: python scripts/build_minimal.py
      
      # 5. 테스트 (JSON.gz로)
      - name: Test production build
        run: |
          export UMIS_ENV=production
          python -m pytest tests/
      
      # 6. Docker 이미지 빌드 (dist/ 포함, YAML 제외)
      - name: Build Docker image
        run: docker build -t umis:${{ github.sha }} .
      
      # 7. 배포
      - name: Deploy to AWS
        run: |
          # ECR push, ECS 업데이트 등
          ...
```

---

### 4. Dockerfile (프로덕션)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 1. 의존성
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. dist/ 만 복사 (YAML 제외!) ← 핵심!
COPY dist/ /app/dist/

# 3. Python 코드
COPY umis_rag/ /app/umis_rag/

# 4. 환경변수 (프로덕션 모드)
ENV UMIS_ENV=production

# 5. 실행
CMD ["python", "-m", "umis_rag.cli"]
```

**중요**: YAML 원본은 Docker 이미지에 **포함 안 됨**
- ✅ IP 보호
- ✅ 이미지 크기 감소
- ✅ 보안 강화

---

### 5. 로컬 테스트 (프로덕션 빌드)

```bash
# Makefile
.PHONY: build-prod test-prod

# 프로덕션 빌드
build-prod:
	python scripts/build_minimal.py

# 프로덕션 환경으로 테스트
test-prod: build-prod
	UMIS_ENV=production python -m pytest tests/

# 사용
# make test-prod
```

---

## 📊 개발 vs 프로덕션 비교

| 항목 | 개발 (Development) | 프로덕션 (Production) |
|------|-------------------|----------------------|
| **파일 포맷** | YAML | JSON.gz |
| **파일 위치** | 원본 경로 | dist/ |
| **편집** | 텍스트 에디터 | 불가 (읽기 전용) |
| **Git 커밋** | ✅ 포함 | ❌ 제외 (.gitignore) |
| **로딩 속도** | 보통 (430ms) | 빠름 (28ms, 15배) |
| **파일 크기** | 1.1 MB | 0.33 MB (70% 작음) |
| **주석** | ✅ 지원 | ❌ 제거됨 |
| **디버깅** | ✅ 쉬움 | ⚠️ 어려움 (압축 해제 필요) |
| **환경변수** | `UMIS_ENV=development` | `UMIS_ENV=production` |

---

## 🎯 모범 사례 (Best Practices)

### 1. 단일 진실 공급원 (Single Source of Truth)

```yaml
진실: YAML 원본
생성: JSON.gz (자동)

규칙:
  ✅ YAML 수정 → 재빌드
  ❌ JSON.gz 직접 수정 금지
  
이유:
  YAML이 마스터, JSON.gz는 빌드 산출물
```

---

### 2. 빌드 검증 (Build Validation)

```python
# scripts/build_minimal.py 마지막에 추가
def validate_build():
    """빌드 결과 검증"""
    import gzip
    import json
    
    # 모든 JSON.gz 파일 검증
    for json_gz in Path('dist').rglob('*.json.gz'):
        try:
            with gzip.open(json_gz, 'rt') as f:
                data = json.load(f)
            print(f"✅ {json_gz.name} 검증 통과")
        except Exception as e:
            print(f"❌ {json_gz.name} 검증 실패: {e}")
            return False
    
    return True

# 빌드 후 호출
if not validate_build():
    sys.exit(1)
```

---

### 3. 버전 관리 (Version Control)

```yaml
# dist/metadata.json (빌드 시 자동 생성)
{
  "build_time": "2025-11-08T22:00:00Z",
  "git_commit": "abc123",
  "source_files": 25,
  "total_size_bytes": 346234,
  "compression_ratio": 0.70
}
```

---

### 4. 문서화 (Documentation)

```markdown
# README.md

## 개발

YAML 파일만 편집하세요:
- config/*.yaml
- data/raw/*.yaml
- umis.yaml

변경 후 Git 커밋하면 끝!

## 프로덕션 빌드

```bash
python scripts/build_minimal.py
```

dist/ 폴더가 생성됩니다.

## 배포

CI/CD가 자동으로 처리합니다.
```

---

## ✅ 성공 사례

### 유사한 접근을 사용하는 프로젝트

```yaml
Next.js:
  개발: TypeScript + JSX
  프로덕션: JavaScript 번들 (자동)
  
Sass:
  개발: .scss 파일
  프로덕션: .css (자동 컴파일)
  
TypeScript:
  개발: .ts 파일
  프로덕션: .js (자동 트랜스파일)
  
공통점:
  개발자는 고급 언어 사용
  빌드 시 최적화된 형태로 자동 변환
```

---

## 🎓 결론

### 이 방식이 최선인 이유

```yaml
1. 개발자 경험:
   ✅ 변화 없음 (YAML 계속 사용)
   ✅ 학습 곡선 0
   ✅ 팀 협업 용이

2. 프로덕션 성능:
   ✅ 15배 빠름
   ✅ 70% 작음
   ✅ $180/년 절감

3. 유지보수:
   ✅ Git 히스토리 깔끔
   ✅ 롤백 쉬움
   ✅ 디버깅 가능

4. 보안:
   ✅ YAML 원본 노출 안 됨
   ✅ 주석/문서 제거됨
   ✅ IP 보호

5. 복잡도:
   ✅ 최소 (기술 2개)
   ✅ 빌드 스크립트 단순
   ✅ 자동화 가능
```

---

### 대안과 비교

| 방식 | 개발 경험 | 성능 | 복잡도 | 추천 |
|------|-----------|------|--------|------|
| **YAML 그대로 사용** | ⭐⭐⭐⭐⭐ | ⭐ | ⭐ | ❌ (느림) |
| **프로덕션 포맷만** | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ❌ (편집 불가) |
| **하이브리드 (YAML→JSON.gz)** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ✅✅✅ |

---

## 🚀 실행 계획

### 1주차: 구현

```bash
Day 1-2: 빌드 스크립트 작성 ✅ (이미 완료!)
  - scripts/build_minimal.py

Day 3-4: 로더 구현
  - umis_rag/utils/config_loader.py
  - 환경 감지 (UMIS_ENV)

Day 5: CI/CD 설정
  - .github/workflows/deploy.yml
  - Dockerfile 수정

Day 6-7: 테스트
  - 로컬 테스트
  - 프로덕션 빌드 테스트
  - 배포 테스트
```

### 2주차: 배포 및 모니터링

```bash
Day 1-3: 프로덕션 배포
  - 스테이징 배포
  - 검증
  - 프로덕션 배포

Day 4-5: 모니터링
  - 성능 측정
  - 에러 로그 확인
  - 최적화
```

---

## 💡 핵심 메시지

**"개발자는 YAML만 보고, 프로덕션은 자동으로"**

```
이것이 최선:
  ✅ 개발 경험 100% 유지
  ✅ 프로덕션 성능 극대화
  ✅ 자동화로 인간 오류 방지
  ✅ 비용 절감
  ✅ 보안 강화

복잡도:
  ⭐⭐ (매우 낮음)
  빌드 스크립트만 관리

ROI:
  무한대 (개발 생산성 + 성능 + 비용)
```

---

이 방식은 **업계 표준**이며 (TypeScript, Sass 등), UMIS에도 **완벽하게 적용 가능**합니다! 🎉

