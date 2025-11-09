# UMIS 보안 프로덕션 빌드 가이드

**작성일**: 2025-11-08  
**브랜치**: production-format-optimization  
**스크립트**: `scripts/build_secure_production.py`

---

## 🎯 목적

프로덕션 배포 시:
1. ⚡ **성능**: 15-87배 빠른 로딩
2. 📦 **크기**: 73% 감소
3. 🔒 **보안**: IP 보호 (프롬프트, 패턴, 알고리즘)

---

## 🔐 보안 레벨

### Level 1: 기본 보호 (무료, 권장)

```yaml
변환:
  - YAML → MessagePack + zstd 압축
  - Python → .pyc

보호 수준:
  - 평문 차단 ✅
  - 바이너리 난독화 ✅
  - 역공학 난이도: ⭐⭐

적합:
  - B2C SaaS
  - 오픈소스 기반 상업 제품
  - 일반적인 보호 필요
```

---

### Level 2: 고급 보호 (권장, B2B)

```yaml
변환:
  - YAML → MessagePack + zstd + AES-256
  - Python → .pyc (소스 제거)

보호 수준:
  - 강력한 암호화 ✅✅
  - 라이선스 키 필수 ✅
  - 역공학 난이도: ⭐⭐⭐⭐

적합:
  - B2B 온프레미스
  - 고객별 라이선스
  - IP 보호 중요
```

---

### Level 3: 최고 보호 (선택, 엔터프라이즈)

```yaml
변환:
  - YAML → MessagePack + zstd + AES-256
  - Python → PyArmor (C 확장)

보호 수준:
  - 완벽한 암호화 ✅✅✅
  - C 레벨 난독화 ✅✅
  - 역공학 난이도: ⭐⭐⭐⭐⭐

적합:
  - 금융/국방
  - 극비 알고리즘
  - 최고 수준 보호

비용:
  - PyArmor Pro: $379/년
```

---

## 📋 설치

### 필수 라이브러리

```bash
# Level 1 (기본)
pip install msgpack zstandard

# Level 2 (암호화)
pip install msgpack zstandard cryptography

# Level 3 (PyArmor)
pip install msgpack zstandard cryptography pyarmor
```

**또는 한번에**:
```bash
pip install msgpack zstandard cryptography
```

---

## 🚀 사용법

### Level 1: 기본 빌드

```bash
# 기본 빌드 (압축만)
python3 scripts/build_secure_production.py

# 또는
python3 scripts/build_secure_production.py --level 1
```

**결과**:
```
dist/
├── schema_registry.bin       # 압축된 설정
├── agent_names.bin
├── prompts.bin               # 압축된 프롬프트
├── umis_business_model_patterns.bin  # 압축된 패턴
└── config_loader.py          # 런타임 로더
```

**사용 (프로덕션)**:
```python
from dist.config_loader import load_config, load_prompts

# 설정 로드
config = load_config('schema_registry')
print(f"Loaded: {len(config)} schemas")

# 프롬프트 로드
prompts = load_prompts()
print(f"Loaded: {len(prompts)} prompts")
```

---

### Level 2: 암호화 빌드

```bash
# 라이선스 키와 함께 빌드
python3 scripts/build_secure_production.py \
  --level 2 \
  --license-key "your-secret-license-key-2025"

# 또는 환경변수 사용 (권장)
export UMIS_BUILD_LICENSE_KEY="your-secret-license-key-2025"
python3 scripts/build_secure_production.py --level 2
```

**결과**:
```
dist/
├── schema_registry.enc       # 암호화된 설정
├── agent_names.enc
├── prompts.enc               # 암호화된 프롬프트
├── umis_business_model_patterns.enc  # 암호화된 패턴
└── config_loader.py          # 런타임 로더 (복호화 포함)
```

**사용 (프로덕션)**:
```python
# 1. 라이선스 키 설정
import os
os.environ['UMIS_LICENSE_KEY'] = 'your-secret-license-key-2025'

# 2. 로드
from dist.config_loader import load_config

config = load_config('schema_registry')
# ✅ 올바른 키: 로드 성공
# ❌ 잘못된 키: ValueError 발생
```

**Docker 배포**:
```dockerfile
# Dockerfile
FROM python:3.11-slim

# dist/ 복사
COPY dist/ /app/dist/
COPY requirements.txt /app/

# 라이선스 키는 런타임에 주입
ENV UMIS_LICENSE_KEY=""

RUN pip install -r requirements.txt

# 애플리케이션 시작
CMD ["python", "main.py"]
```

```bash
# 실행 시 키 주입
docker run -e UMIS_LICENSE_KEY="customer-key-abc123" myapp
```

---

### Level 3: PyArmor 빌드

```bash
# PyArmor 설치 (최초 1회)
pip install pyarmor

# 빌드
export UMIS_BUILD_LICENSE_KEY="your-secret-license-key-2025"
python3 scripts/build_secure_production.py --level 3
```

**주의**:
- PyArmor는 C 확장으로 변환하므로 플랫폼별 빌드 필요
- 디버깅 어려움 (프로덕션 전용)

---

## 🔍 빌드 전/후 비교

### 파일 크기

```
Before (YAML):
  umis_core.yaml:                    240 KB
  umis_business_model_patterns.yaml:  12 KB
  config/*.yaml:                      15 KB
  Total:                             267 KB

After (Level 1 - 압축):
  prompts.bin:                        65 KB (-73%)
  patterns.bin:                        3 KB (-75%)
  config/*.bin:                        4 KB (-73%)
  Total:                              72 KB (-73% 🎉)

After (Level 2 - 암호화):
  prompts.enc:                        66 KB
  patterns.enc:                        3 KB
  config/*.enc:                        4 KB
  Total:                              73 KB (-73% + 암호화 ✅)
```

---

### 로딩 속도

```
Before (YAML):
  Load umis_core.yaml:     150 ms
  Load patterns.yaml:       10 ms
  Total:                   160 ms

After (Level 1):
  Load prompts.bin:         10 ms  (-93%)
  Load patterns.bin:         1 ms  (-90%)
  Total:                    11 ms  (-93% 🚀)

After (Level 2):
  Load prompts.enc:         12 ms  (복호화 +2ms)
  Load patterns.enc:         2 ms
  Total:                    14 ms  (-91% + 보안 ✅)
```

---

### 보안 수준

```
Before (YAML):
  역공학 시간:     5분
  도구:           텍스트 에디터
  보호 수준:      ❌ 없음

After (Level 1 - 압축):
  역공학 시간:     1-2시간
  도구:           Python + msgpack
  보호 수준:      ⭐⭐ 기본

After (Level 2 - 암호화):
  역공학 시간:     불가능 (키 없이)
  도구:           암호 분석 필요
  보호 수준:      ⭐⭐⭐⭐ 강력

After (Level 3 - PyArmor):
  역공학 시간:     수주 (C 디컴파일)
  도구:           IDA Pro + 전문 지식
  보호 수준:      ⭐⭐⭐⭐⭐ 최고
```

---

## 💡 고급 사용법

### 고객별 라이선스 키 생성

```python
import secrets

def generate_license_key(customer_id: str) -> str:
    """고객별 유니크 키 생성"""
    random_part = secrets.token_urlsafe(32)
    return f"UMIS-{customer_id}-{random_part}"

# 사용
key_acme = generate_license_key("ACME-CORP")
key_globex = generate_license_key("GLOBEX-INC")

print(f"ACME Corp:   {key_acme}")
print(f"Globex Inc:  {key_globex}")

# 각 고객별로 개별 빌드
# python3 scripts/build_secure_production.py --level 2 --license-key "$key_acme"
```

---

### 만료 날짜 추가 (선택)

```python
# dist/config_loader.py 수정
import datetime

class SecureConfigLoader:
    def __init__(self, license_key: str = None):
        # ... 기존 코드 ...
        
        # 만료 날짜 체크
        expiry_date = datetime.date(2026, 12, 31)
        if datetime.date.today() > expiry_date:
            raise RuntimeError("License expired. Contact sales@umis.ai")
```

---

### 기기 제한 (PyArmor)

```bash
# 특정 MAC 주소에서만 실행
pyarmor gen \
  --bind-device \
  --pack dist \
  umis_rag/

# 또는 빌드 스크립트에 추가
```

---

## 🐳 Docker 배포 예시

### Dockerfile

```dockerfile
FROM python:3.11-slim AS builder

# 빌드 환경
WORKDIR /build
COPY . .

# Level 2 빌드
ARG LICENSE_KEY
ENV UMIS_BUILD_LICENSE_KEY=${LICENSE_KEY}
RUN pip install msgpack zstandard cryptography && \
    python3 scripts/build_secure_production.py --level 2

# 프로덕션 이미지
FROM python:3.11-slim

WORKDIR /app

# dist/ 만 복사 (소스 코드 제외!)
COPY --from=builder /build/dist /app/dist
COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

# 라이선스 키는 런타임에 주입
ENV UMIS_LICENSE_KEY=""

CMD ["python", "-m", "umis_rag.cli"]
```

### 빌드 및 실행

```bash
# 1. 빌드 (라이선스 키 주입)
docker build \
  --build-arg LICENSE_KEY="build-time-key-2025" \
  -t umis:v7.5.0-secure \
  .

# 2. 실행 (고객별 키)
docker run \
  -e UMIS_LICENSE_KEY="customer-runtime-key-abc123" \
  umis:v7.5.0-secure

# 이미지 크기 확인
docker images umis:v7.5.0-secure
# REPOSITORY   TAG              SIZE
# umis         v7.5.0-secure    150 MB  (vs 500 MB 기존)
```

---

## 📊 비용 효과 분석

### Level 1 (무료)

```yaml
비용:           $0
구현 시간:      1주
성능 개선:      93%
보호 수준:      기본

ROI:           무한대 (무료 + 성능 향상)
```

---

### Level 2 (권장, B2B)

```yaml
비용:           $0 (라이브러리 무료)
구현 시간:      2주
성능 개선:      91%
보호 수준:      강력

시나리오 (100 고객, $10K/년):
  - IP 유출 방지로 고객 이탈 -25%
  - 매출 보호: $250K/년
  - ROI: 무한대
```

---

### Level 3 (엔터프라이즈)

```yaml
비용:           $379/년 (PyArmor Pro)
구현 시간:      1개월
성능 개선:      85% (난독화 오버헤드)
보호 수준:      최고

시나리오 (10개 엔터프라이즈, $100K/년):
  - IP 보호로 경쟁 진입 방지
  - 매출 보호: $1M/년
  - ROI: 264,000%
```

---

## ⚠️ 주의사항

### 1. 라이선스 키 관리

**❌ 하지 말 것**:
```python
# 코드에 하드코딩
LICENSE_KEY = "my-secret-key-12345"  # ❌ Git에 커밋됨!
```

**✅ 권장**:
```python
# 환경변수
LICENSE_KEY = os.getenv('UMIS_LICENSE_KEY')

# AWS Secrets Manager
import boto3
secrets = boto3.client('secretsmanager')
LICENSE_KEY = secrets.get_secret_value(SecretId='umis-license')['SecretString']

# .env 파일 (로컬만, .gitignore에 추가)
from dotenv import load_dotenv
load_dotenv()
LICENSE_KEY = os.getenv('UMIS_LICENSE_KEY')
```

---

### 2. 키 분실 시

```yaml
문제:
  - 암호화된 파일 복호화 불가능
  - 데이터 영구 손실

해결책:
  1. 키 백업 (안전한 곳에)
  2. 원본 YAML 보관 (Git)
  3. 재빌드 가능
```

---

### 3. 성능 트레이드오프

```yaml
Level 1:
  - 오버헤드: 거의 없음 (<1%)
  
Level 2:
  - 복호화: +1-2ms
  - 메모리: +10%
  
Level 3 (PyArmor):
  - 로딩: +10-20%
  - 실행: +5-10%
  - 메모리: +10-15%
```

---

## 🔍 디버깅

### 빌드 실패 시

```bash
# 자세한 로그
python3 scripts/build_secure_production.py --level 2 -v

# 의존성 확인
pip list | grep -E "(msgpack|zstandard|cryptography)"

# 개별 테스트
python3 -c "import msgpack; print('✅ msgpack OK')"
python3 -c "import zstandard; print('✅ zstd OK')"
python3 -c "from cryptography.fernet import Fernet; print('✅ crypto OK')"
```

---

### 런타임 로드 실패 시

```python
# 수동 디버그
import zstandard as zstd
import msgpack

# 1. 파일 읽기
with open('dist/prompts.bin', 'rb') as f:
    compressed = f.read()
    print(f"Compressed size: {len(compressed)} bytes")

# 2. 압축 해제
try:
    decompressed = zstd.decompress(compressed)
    print(f"Decompressed size: {len(decompressed)} bytes")
except Exception as e:
    print(f"❌ Decompress failed: {e}")

# 3. MessagePack 디코딩
try:
    data = msgpack.unpackb(decompressed, raw=False)
    print(f"✅ Data loaded: {len(data)} keys")
except Exception as e:
    print(f"❌ Unpack failed: {e}")
```

---

## 📖 참고 자료

- **보안 전략**: `docs/architecture/SECURITY_AND_IP_PROTECTION.md`
- **성능 벤치마크**: `docs/architecture/BENCHMARK_RESULTS.md`
- **전체 포맷 분석**: `docs/architecture/PRODUCTION_FORMAT_OPTIONS.md`
- **빌드 스크립트**: `scripts/build_secure_production.py`

---

## ✅ 체크리스트

### 빌드 전
- [ ] 의존성 설치 확인
- [ ] 원본 YAML 백업 (Git 커밋)
- [ ] 라이선스 키 생성 (Level 2+)
- [ ] 환경 설정 확인

### 빌드
- [ ] Level 선택 (1, 2, 3)
- [ ] 빌드 실행
- [ ] dist/ 파일 확인
- [ ] 크기/속도 측정

### 배포 전
- [ ] 로더 테스트
- [ ] 라이선스 키 환경변수 설정
- [ ] Docker 이미지 빌드 (선택)
- [ ] 프로덕션 환경 테스트

### 배포 후
- [ ] 로딩 성능 모니터링
- [ ] 에러 로그 확인
- [ ] 라이선스 키 관리
- [ ] 백업 확인

