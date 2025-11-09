# GitHub 배포 전략 (Balanced 프로덕션)

**작성일**: 2025-11-08  
**브랜치**: production-format-optimization  
**전략**: 개발 YAML → 프로덕션 Balanced 자동 배포

---

## 🎯 핵심 원칙

```yaml
Git에 커밋하는 것:
  ✅ YAML 원본 (모든 설정/데이터)
  ✅ Python 소스코드
  ✅ 빌드 스크립트
  ❌ dist/ (빌드 산출물)
  ❌ *.json.gz, *.msgpack

빌드 시점:
  - CI/CD에서 자동 (푸시/PR 시)
  - 로컬에서도 가능 (테스트용)

배포 산출물:
  - Docker 이미지 (dist/만 포함)
  - YAML 원본 제외 (IP 보호)
```

---

## 📁 Git 구조

### .gitignore 설정

```gitignore
# .gitignore

# 빌드 산출물 (Git에서 제외)
dist/
*.json.gz
*.msgpack

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# 환경
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# 테스트
.pytest_cache/
.coverage
htmlcov/
.tox/

# 로그
*.log
logs/

# 주의: YAML 원본은 Git에 포함! (주석 처리 또는 제거)
# config/*.yaml  ← 이 줄 없어야 함
# data/raw/*.yaml ← 이 줄 없어야 함
```

---

### Git 커밋 내용

```bash
# Git에 포함되는 것
git ls-files

# 출력 예시:
.github/workflows/deploy.yml          # CI/CD
.gitignore                             # Git 설정
README.md                              # 문서
requirements.txt                       # 의존성
Dockerfile                             # Docker 설정

# YAML 원본 (소스 코드) ✅
umis.yaml
umis_core.yaml
config/schema_registry.yaml
config/agent_names.yaml
data/raw/umis_business_model_patterns.yaml
# ... (모든 YAML 파일)

# Python 코드 ✅
umis_rag/__init__.py
umis_rag/agents/explorer.py
# ... (모든 .py 파일)

# 빌드 스크립트 ✅
scripts/build_balanced.py
scripts/build_minimal.py

# dist/ 폴더는 없음 ❌ (빌드 시 생성)
```

---

## 🔄 브랜치 전략

### Git Flow 방식

```
main (프로덕션)
  ↑
  merge (자동 배포)
  ↑
develop (개발)
  ↑
  merge
  ↑
feature/* (기능 개발)
```

### 브랜치별 동작

```yaml
feature/* 브랜치:
  - 개발자가 YAML 편집
  - 로컬 테스트 (YAML 직접 사용)
  - PR 생성
  
  CI/CD:
    ✅ 린트 검사
    ✅ 단위 테스트 (YAML)
    ✅ 빌드 테스트 (Balanced)
    ❌ 배포 안 함

develop 브랜치:
  - feature 머지 후
  
  CI/CD:
    ✅ 모든 테스트
    ✅ Balanced 빌드
    ✅ 스테이징 배포
    ❌ 프로덕션 배포 안 함

main 브랜치:
  - develop 머지 후 (릴리즈)
  
  CI/CD:
    ✅ 모든 테스트
    ✅ Balanced 빌드
    ✅ 프로덕션 배포 ⭐
    ✅ Git 태그 생성
```

---

## 🚀 GitHub Actions 워크플로우

### 1. PR 검증 (feature → develop)

```yaml
# .github/workflows/pr-check.yml
name: PR Check

on:
  pull_request:
    branches: [develop, main]

jobs:
  validate:
    runs-on: ubuntu-latest
    
    steps:
      # 1. 체크아웃
      - name: Checkout code
        uses: actions/checkout@v3
      
      # 2. Python 설정
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      # 3. 의존성 설치
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov pylint
      
      # 4. 린트 (YAML 검증)
      - name: Lint YAML files
        run: |
          pip install yamllint
          yamllint config/ data/raw/ *.yaml
      
      # 5. 린트 (Python)
      - name: Lint Python
        run: |
          pylint umis_rag/ --fail-under=8.0
      
      # 6. 단위 테스트 (YAML 직접 사용)
      - name: Unit tests
        run: |
          export UMIS_ENV=development
          pytest tests/unit/ -v --cov=umis_rag
      
      # 7. Balanced 빌드 테스트
      - name: Test Balanced build
        run: |
          pip install msgpack
          python scripts/build_balanced.py
      
      # 8. 통합 테스트 (Balanced 빌드로)
      - name: Integration tests with Balanced
        run: |
          export UMIS_ENV=production
          pytest tests/integration/ -v
      
      # 9. 빌드 산출물 검증
      - name: Validate build artifacts
        run: |
          python scripts/validate_build.py
      
      # 10. 성공 시 코멘트
      - name: Comment PR
        if: success()
        uses: actions/github-script@v6
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: '✅ All checks passed! Ready for review.'
            })
```

---

### 2. 스테이징 배포 (develop 브랜치)

```yaml
# .github/workflows/deploy-staging.yml
name: Deploy to Staging

on:
  push:
    branches: [develop]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    
    steps:
      # 1. 체크아웃
      - name: Checkout code
        uses: actions/checkout@v3
      
      # 2. Python 설정
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      # 3. 의존성 설치
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install msgpack
      
      # 4. Balanced 빌드 ⭐
      - name: Build Balanced
        run: |
          python scripts/build_balanced.py
      
      # 5. 빌드 검증
      - name: Validate build
        run: |
          python scripts/validate_build.py
          
          # 파일 크기 확인
          du -sh dist/
          
          # JSON.gz 테스트
          python -c "
          import gzip, json
          data = json.load(gzip.open('dist/umis.json.gz', 'rt'))
          print(f'✅ umis.json.gz: {len(data)} keys')
          "
          
          # MessagePack 테스트
          python -c "
          import msgpack
          data = msgpack.unpackb(open('dist/data/umis_business_model_patterns.msgpack', 'rb').read())
          print(f'✅ patterns.msgpack: {len(data)} items')
          "
      
      # 6. 테스트 (프로덕션 빌드로)
      - name: Test with production build
        run: |
          export UMIS_ENV=production
          pytest tests/ -v
      
      # 7. Docker 빌드
      - name: Build Docker image
        run: |
          docker build \
            -t umis:staging-${{ github.sha }} \
            -t umis:staging-latest \
            .
      
      # 8. Docker 이미지 검증
      - name: Validate Docker image
        run: |
          # 이미지 크기 확인
          docker images umis:staging-latest
          
          # dist/ 포함 확인
          docker run --rm umis:staging-latest ls -la dist/
          
          # YAML 제외 확인
          docker run --rm umis:staging-latest ls umis.yaml 2>&1 | grep -q "No such file" && echo "✅ YAML excluded" || exit 1
      
      # 9. ECR 푸시 (AWS)
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ap-northeast-2
      
      - name: Login to ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v1
      
      - name: Push to ECR
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          ECR_REPOSITORY: umis-staging
        run: |
          docker tag umis:staging-latest $ECR_REGISTRY/$ECR_REPOSITORY:latest
          docker tag umis:staging-latest $ECR_REGISTRY/$ECR_REPOSITORY:${{ github.sha }}
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:latest
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:${{ github.sha }}
      
      # 10. ECS 배포 (스테이징)
      - name: Deploy to ECS Staging
        run: |
          aws ecs update-service \
            --cluster umis-staging \
            --service umis-api \
            --force-new-deployment
      
      # 11. 배포 검증
      - name: Verify deployment
        run: |
          # Health check
          sleep 30
          curl -f https://staging.umis.ai/health || exit 1
          
          # 성능 테스트
          python scripts/performance_test.py --env staging
      
      # 12. Slack 알림
      - name: Notify Slack
        if: always()
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          text: |
            Staging deployment ${{ job.status }}
            Commit: ${{ github.sha }}
            Author: ${{ github.actor }}
          webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

---

### 3. 프로덕션 배포 (main 브랜치)

```yaml
# .github/workflows/deploy-production.yml
name: Deploy to Production

on:
  push:
    branches: [main]
  
  # 수동 트리거 (선택)
  workflow_dispatch:
    inputs:
      version:
        description: 'Version tag (e.g., v7.5.1)'
        required: true

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    
    steps:
      # ... (스테이징과 동일한 빌드 과정)
      
      # 추가: Git 태그 생성
      - name: Create Git tag
        if: github.event_name == 'workflow_dispatch'
        run: |
          git config user.name github-actions
          git config user.email github-actions@github.com
          git tag ${{ github.event.inputs.version }}
          git push origin ${{ github.event.inputs.version }}
      
      # ECR 푸시 (프로덕션)
      - name: Push to ECR Production
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          ECR_REPOSITORY: umis-production
        run: |
          docker tag umis:latest $ECR_REGISTRY/$ECR_REPOSITORY:latest
          docker tag umis:latest $ECR_REGISTRY/$ECR_REPOSITORY:${{ github.sha }}
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:latest
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:${{ github.sha }}
      
      # Blue-Green 배포 (선택)
      - name: Blue-Green deployment
        run: |
          # Green 환경에 배포
          aws ecs update-service \
            --cluster umis-production \
            --service umis-api-green \
            --force-new-deployment
          
          # Health check
          sleep 60
          curl -f https://green.umis.ai/health
          
          # Traffic 전환
          aws elbv2 modify-listener \
            --listener-arn ${{ secrets.ALB_LISTENER_ARN }} \
            --default-actions Type=forward,TargetGroupArn=${{ secrets.GREEN_TG_ARN }}
          
          # 모니터링 (10분)
          python scripts/monitor_deployment.py --duration 600
          
          # 문제 없으면 Blue 종료
          aws ecs update-service \
            --cluster umis-production \
            --service umis-api-blue \
            --desired-count 0
      
      # 배포 검증
      - name: Production smoke tests
        run: |
          python scripts/smoke_test.py --env production
      
      # Rollback 준비
      - name: Store rollback info
        run: |
          echo "${{ github.sha }}" > .last-successful-deploy
          aws s3 cp .last-successful-deploy s3://umis-deployments/
```

---

## 📦 Dockerfile (Balanced 전용)

```dockerfile
# Dockerfile
FROM python:3.11-slim AS builder

WORKDIR /build

# 1. 의존성 복사
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt msgpack

# 2. YAML 원본 복사 (빌드용)
COPY umis.yaml umis_core.yaml ./
COPY config/ config/
COPY data/ data/

# 3. 빌드 스크립트 복사
COPY scripts/ scripts/

# 4. Balanced 빌드 실행 ⭐
RUN python scripts/build_balanced.py

# 5. 빌드 검증
RUN python scripts/validate_build.py

# ============================================
# 프로덕션 이미지 (작고 안전)
# ============================================
FROM python:3.11-slim

WORKDIR /app

# 1. 런타임 의존성만
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt msgpack

# 2. dist/ 만 복사 (YAML 제외!) ⭐
COPY --from=builder /build/dist/ /app/dist/

# 3. Python 코드
COPY umis_rag/ /app/umis_rag/

# 4. 환경변수 (프로덕션 모드)
ENV UMIS_ENV=production
ENV PYTHONUNBUFFERED=1

# 5. 헬스체크
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health').raise_for_status()"

# 6. 실행
CMD ["python", "-m", "umis_rag.cli"]
```

**중요**:
- ✅ YAML 원본은 builder stage에서만 (빌드용)
- ✅ 프로덕션 이미지는 dist/만 포함
- ✅ IP 보호 (YAML 노출 안 됨)
- ✅ 이미지 크기 감소

---

## 🔐 환경별 설정 관리

### GitHub Secrets

```yaml
# GitHub Repository Settings → Secrets

Development/Staging:
  STAGING_AWS_ACCESS_KEY_ID
  STAGING_AWS_SECRET_ACCESS_KEY
  STAGING_ECR_REPOSITORY
  STAGING_ECS_CLUSTER

Production:
  PROD_AWS_ACCESS_KEY_ID
  PROD_AWS_SECRET_ACCESS_KEY
  PROD_ECR_REPOSITORY
  PROD_ECS_CLUSTER
  PROD_ALB_LISTENER_ARN

Notifications:
  SLACK_WEBHOOK
  PAGERDUTY_KEY

API Keys (런타임):
  OPENAI_API_KEY (ECS 환경변수로 주입)
  ANTHROPIC_API_KEY
```

---

### 환경변수 주입 (ECS)

```yaml
# ecs-task-definition.json
{
  "family": "umis-production",
  "containerDefinitions": [
    {
      "name": "umis-api",
      "image": "${ECR_IMAGE}",
      "environment": [
        {
          "name": "UMIS_ENV",
          "value": "production"
        }
      ],
      "secrets": [
        {
          "name": "OPENAI_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:..."
        }
      ]
    }
  ]
}
```

---

## 🧪 테스트 전략

### 테스트 단계별

```yaml
1. 로컬 테스트 (개발자):
   환경: UMIS_ENV=development
   데이터: YAML 직접 사용
   속도: 빠름 (즉시 피드백)

2. PR 검증 (CI):
   환경: UMIS_ENV=development (단위)
         UMIS_ENV=production (통합)
   데이터: YAML → Balanced 빌드
   검증: 빌드 성공, 테스트 통과

3. 스테이징 배포:
   환경: UMIS_ENV=production
   데이터: Balanced 빌드
   검증: E2E 테스트, 성능 테스트

4. 프로덕션 배포:
   환경: UMIS_ENV=production
   데이터: Balanced 빌드
   검증: Smoke test, 모니터링
```

---

### 테스트 파일 구조

```
tests/
├── unit/
│   ├── test_config_loader.py       # 로더 테스트
│   ├── test_agents.py               # Agent 로직
│   └── conftest.py                  # Fixture (YAML)
│
├── integration/
│   ├── test_workflow.py             # 전체 워크플로우
│   ├── test_balanced_build.py       # Balanced 빌드
│   └── conftest.py                  # Fixture (Balanced)
│
├── e2e/
│   ├── test_api.py                  # API 엔드포인트
│   └── test_scenarios.py            # 실제 시나리오
│
└── performance/
    ├── test_loading_speed.py        # 로딩 속도
    └── benchmark.py                 # 벤치마크
```

---

## 📊 모니터링

### 배포 후 모니터링

```yaml
# scripts/monitor_deployment.py
import requests
import time

def monitor(duration=600):
    """배포 후 모니터링 (10분)"""
    
    start = time.time()
    errors = []
    
    while time.time() - start < duration:
        try:
            # Health check
            r = requests.get('https://api.umis.ai/health')
            r.raise_for_status()
            
            # 성능 체크
            latency = r.elapsed.total_seconds()
            if latency > 1.0:
                errors.append(f"High latency: {latency}s")
            
            # 메모리 체크
            metrics = requests.get('https://api.umis.ai/metrics').json()
            if metrics['memory_usage'] > 0.8:
                errors.append(f"High memory: {metrics['memory_usage']}")
            
        except Exception as e:
            errors.append(str(e))
        
        time.sleep(10)
    
    if errors:
        print(f"❌ {len(errors)} issues detected")
        for e in errors[:10]:
            print(f"  - {e}")
        return False
    
    print("✅ Deployment healthy")
    return True
```

---

## 🔄 Rollback 전략

### 자동 Rollback

```yaml
# .github/workflows/deploy-production.yml (추가)

# 배포 후 모니터링
- name: Monitor deployment
  id: monitor
  run: |
    python scripts/monitor_deployment.py --duration 600
  continue-on-error: true

# 실패 시 자동 Rollback
- name: Rollback on failure
  if: steps.monitor.outcome == 'failure'
  run: |
    echo "❌ Deployment failed, rolling back..."
    
    # 이전 성공 버전 가져오기
    LAST_GOOD=$(aws s3 cp s3://umis-deployments/.last-successful-deploy -)
    
    # 이전 버전으로 되돌리기
    aws ecs update-service \
      --cluster umis-production \
      --service umis-api \
      --task-definition umis-production:$LAST_GOOD \
      --force-new-deployment
    
    # Slack 알림
    curl -X POST ${{ secrets.SLACK_WEBHOOK }} \
      -d '{"text": "⚠️ Production rollback executed!"}'
    
    exit 1
```

---

## 📝 배포 체크리스트

### PR 머지 전

- [ ] YAML 파일 검증 (yamllint)
- [ ] Python 린트 통과 (pylint)
- [ ] 단위 테스트 통과 (YAML)
- [ ] Balanced 빌드 성공
- [ ] 통합 테스트 통과 (Balanced)
- [ ] 코드 리뷰 완료

### 스테이징 배포 전

- [ ] develop 브랜치 안정
- [ ] 모든 테스트 통과
- [ ] Balanced 빌드 검증
- [ ] Docker 이미지 검증

### 프로덕션 배포 전

- [ ] 스테이징 검증 완료
- [ ] 릴리즈 노트 작성
- [ ] Git 태그 생성
- [ ] 배포 시간 확인 (트래픽 적은 시간)
- [ ] Rollback 준비

### 배포 후

- [ ] Health check 통과
- [ ] Smoke test 통과
- [ ] 성능 모니터링 (10분)
- [ ] 에러 로그 확인
- [ ] 메모리/CPU 사용률 확인

---

## 🎯 최종 워크플로우 요약

### 개발자 관점

```bash
# 1. Feature 개발
git checkout -b feature/new-pattern
vim data/raw/umis_business_model_patterns.yaml  # YAML 편집
pytest tests/unit/  # 로컬 테스트 (YAML)
git commit -am "Add new pattern"
git push origin feature/new-pattern

# 2. PR 생성
# → GitHub Actions 자동 실행:
#    - YAML 검증
#    - Balanced 빌드 테스트
#    - 통합 테스트

# 3. 리뷰 후 머지
# → develop 브랜치로 머지
# → 스테이징 자동 배포

# 4. develop → main 머지 (릴리즈)
# → 프로덕션 자동 배포
```

---

### CI/CD 관점

```yaml
Push to feature/*:
  ✅ 린트
  ✅ 테스트
  ✅ Balanced 빌드
  ❌ 배포 안 함

Push to develop:
  ✅ 모든 검증
  ✅ Balanced 빌드
  ✅ Docker 빌드
  ✅ 스테이징 배포 ⭐

Push to main:
  ✅ 모든 검증
  ✅ Balanced 빌드
  ✅ Docker 빌드
  ✅ 프로덕션 배포 ⭐⭐
  ✅ Git 태그
  ✅ 모니터링
  ✅ Rollback (실패 시)
```

---

## 💡 핵심 포인트

```yaml
1. Git에는 YAML만:
   ✅ 소스 코드로서의 YAML
   ✅ 버전 관리 용이
   ✅ 코드 리뷰 가능

2. 빌드는 CI/CD에서:
   ✅ YAML → Balanced 자동 변환
   ✅ 개발자는 신경 안 씀
   ✅ 일관성 보장

3. 배포는 dist/만:
   ✅ YAML 원본 제외
   ✅ IP 보호
   ✅ 이미지 크기 감소

4. 환경은 자동 감지:
   ✅ UMIS_ENV=development (로컬)
   ✅ UMIS_ENV=production (배포)
   ✅ 같은 코드, 다른 데이터 소스
```

---

이것이 Balanced 전략의 **완벽한 GitHub 배포 워크플로우**입니다! 🚀

