# 프로덕션 배포 시 보안 및 IP 보호

**작성일**: 2025-11-08  
**브랜치**: production-format-optimization  
**목적**: 프롬프트, 소스코드, 비즈니스 로직의 Encapsulation 전략

---

## 🎯 보호 대상 (UMIS IP Assets)

### 1. 프롬프트 엔지니어링
```yaml
가치: 매우 높음 🔴
위협: 쉽게 복제 가능
현재 상태: 평문 YAML (umis.yaml, umis_core.yaml)

보호 필요 자산:
  - Agent 시스템 프롬프트 (6개 Agent)
  - RAG 검색 프롬프트 템플릿
  - Estimator 3-Tier 추론 로직
  - Discovery Sprint 프로세스
  - 13차원 시장 정의 프레임워크
```

### 2. 비즈니스 로직 (패턴 라이브러리)
```yaml
가치: 핵심 자산 🔴
위협: 역공학 쉬움
현재 상태: 평문 YAML

자산:
  - 54개 비즈니스 모델 패턴
  - 23개 Disruption 패턴
  - 트리거 시그널 (수백 개)
  - 검증된 사례 및 메트릭
```

### 3. 알고리즘 및 방법론
```yaml
가치: 차별화 요소 🔴
위협: 구조 노출 시 모방 가능

자산:
  - SAM 4가지 계산 방법
  - Guestimation 템플릿 (150개+)
  - Estimator 학습 규칙 (2,000개 진화)
  - 벤치마크 데이터 (독자 수집)
```

### 4. Python 소스코드
```yaml
가치: 중간 🟡
위협: .pyc 역컴파일 가능

자산:
  - Agent 구현 로직
  - RAG 아키텍처
  - Guardian Meta-RAG
  - Excel 생성 엔진
```

---

## 🔒 위협 모델

### 시나리오 1: 평문 YAML 배포 (현재)

**공격 경로**:
```bash
# 1. Docker 이미지 다운로드
docker pull company/umis:latest

# 2. 컨테이너 추출
docker create --name temp company/umis:latest
docker cp temp:/app ./umis_extracted

# 3. YAML 파일 확인
cat umis_extracted/umis.yaml
cat umis_extracted/data/raw/umis_business_model_patterns.yaml

# ✅ 모든 프롬프트, 패턴, 로직 노출!
```

**소요 시간**: 5분  
**난이도**: ⭐ (누구나 가능)  
**결과**: 100% IP 노출

---

### 시나리오 2: .pyc만 배포 (Python Bytecode)

**공격 경로**:
```bash
# Python 소스 제거, .pyc만 배포
# 하지만...

# 1. 역컴파일 도구 사용
pip install uncompyle6

# 2. .pyc → .py 복원
uncompyle6 umis_rag/__init__.pyc > __init__.py

# ✅ 80-90% 소스코드 복원 가능
```

**소요 시간**: 10분  
**난이도**: ⭐⭐ (기술자)  
**결과**: 대부분 복원 가능

---

### 시나리오 3: YAML이지만 난독화

**공격 경로**:
```python
# Base64 인코딩 정도는...
import base64
encoded = base64.b64decode(obfuscated_yaml)

# ✅ 즉시 복원
```

**소요 시간**: 1분  
**난이도**: ⭐ (누구나)  
**결과**: 무의미한 보호

---

## 🛡️ 보호 전략 (난이도별)

### Level 1: 기본 보호 (쉬움, 1-2주)

#### 1.1 바이너리 포맷 + 압축

```yaml
적용:
  - YAML → MessagePack/Protobuf (바이너리)
  - 추가 압축: zstd
  
효과:
  - 가독성: 0 (바이너리)
  - 추출 난이도: ⭐⭐ (역직렬화 필요)
  - 역공학 시간: 1-2시간
  
한계:
  - 포맷 알면 복원 가능
  - 암호화는 아님
```

**구현**:
```python
import msgpack
import zstandard as zstd

# 압축 + 바이너리
data = yaml.safe_load(open('umis.yaml'))
packed = msgpack.packb(data)
compressed = zstd.compress(packed, level=22)  # 최대 압축

with open('umis.bin', 'wb') as f:
    f.write(compressed)

# 크기: 11.98KB → 3.2KB (73% 감소)
# 가독성: 완전 바이너리
```

**평가**:
- ✅ 빠른 구현
- ✅ 성능 개선도 얻음
- ⚠️ 결정적 보호는 아님
- **적합**: 일반 사용자 대상 SaaS

---

#### 1.2 .pyc 배포 + Strip

```python
# setup.py
from setuptools import setup

setup(
    # ...
    zip_safe=False,
    # .py 파일 제외
    include_package_data=False,
)

# 빌드 후
python -m compileall umis_rag/
find umis_rag -name "*.py" -delete  # 소스 삭제
find umis_rag -name "*.pyc" -exec strip {} \;  # 메타데이터 제거
```

**평가**:
- ✅ 소스코드 직접 노출 방지
- ⚠️ 역컴파일 가능
- **적합**: 오픈소스 기반 상업 제품

---

### Level 2: 중급 보호 (중간, 1개월)

#### 2.1 대칭키 암호화 (AES-256)

```python
from cryptography.fernet import Fernet
import msgpack

class EncryptedConfigLoader:
    def __init__(self, key: bytes):
        self.cipher = Fernet(key)
    
    def encrypt_config(self, yaml_path: str, output_path: str):
        """YAML → 암호화 바이너리"""
        data = yaml.safe_load(open(yaml_path))
        packed = msgpack.packb(data)
        encrypted = self.cipher.encrypt(packed)
        
        with open(output_path, 'wb') as f:
            f.write(encrypted)
    
    def load_config(self, encrypted_path: str):
        """복호화 → 사용"""
        with open(encrypted_path, 'rb') as f:
            encrypted = f.read()
        
        decrypted = self.cipher.decrypt(encrypted)
        return msgpack.unpackb(decrypted)

# 사용
key = Fernet.generate_key()  # 키 생성
loader = EncryptedConfigLoader(key)

# 빌드 시
loader.encrypt_config('umis.yaml', 'dist/umis.enc')

# 런타임
config = loader.load_config('umis.enc')
```

**키 관리 옵션**:

**A. 환경변수** (SaaS):
```python
import os
KEY = os.getenv('UMIS_ENCRYPTION_KEY')
if not KEY:
    raise RuntimeError("Missing encryption key")
```

**B. 하드코딩 + 난독화** (온프레미스):
```python
# 키를 코드에 숨김 (PyArmor와 함께 사용)
def _get_key():
    # 복잡한 계산으로 위장
    import hashlib
    seed = b"umis_v7.5.0_production_2025"
    return hashlib.pbkdf2_hmac('sha256', seed, b'salt', 100000)
```

**C. HSM/KMS** (엔터프라이즈):
```python
import boto3

kms = boto3.client('kms')
response = kms.decrypt(CiphertextBlob=encrypted_key)
KEY = response['Plaintext']
```

**평가**:
- ✅✅ 강력한 보호 (키 없이 복호화 불가)
- ⚠️ 키 관리 복잡도
- ⚠️ 런타임 복호화 오버헤드 (~1ms)
- **적합**: B2B SaaS, 엔터프라이즈

---

#### 2.2 코드 난독화 (PyArmor)

```bash
# PyArmor 설치
pip install pyarmor

# 난독화
pyarmor gen --pack dist umis_rag/

# 결과: 
# - C 확장으로 변환 (역컴파일 극도로 어려움)
# - 런타임 검증 (변조 감지)
# - 기간/기기 제한 가능
```

**고급 옵션**:
```bash
# 만료 날짜 설정
pyarmor gen --expired 2026-12-31 umis_rag/

# 특정 기기만 실행
pyarmor gen --bind-device umis_rag/

# 복수 보호
pyarmor gen \
  --pack dist \
  --expired 2026-12-31 \
  --obf-code 2 \
  --obf-module 1 \
  umis_rag/
```

**성능 영향**:
```
로딩 시간: +10-20%
실행 속도: +5-10%
메모리: +10-15%

Trade-off: 보안 vs 성능
```

**평가**:
- ✅✅ Python 소스 강력 보호
- ✅ 라이선스 관리 가능
- ⚠️ 성능 오버헤드
- ⚠️ 디버깅 어려움
- **비용**: $379/년 (Professional)
- **적합**: 온프레미스, IP 보호 중요

---

### Level 3: 고급 보호 (어려움, 3-6개월)

#### 3.1 서버 기반 아키텍처 (API 게이트웨이)

**개념**: 프롬프트/패턴을 클라이언트에 배포하지 않음

```
Before (현재):
┌─────────────────┐
│  Docker Image   │
│  - Python 코드  │
│  - YAML 설정    │ ← 모든 IP 포함!
│  - 패턴 54개    │
│  - 프롬프트     │
└─────────────────┘

After (서버 기반):
┌─────────────────┐         ┌──────────────────┐
│  Client         │         │  UMIS API Server │
│  - UI만         │  HTTPS  │  - 프롬프트      │
│  - API 호출     │ ──────→ │  - 패턴         │
│  - 결과 렌더링   │         │  - 알고리즘      │
└─────────────────┘         │  (내부 네트워크)  │
                            └──────────────────┘
```

**구현 예시**:
```python
# 클라이언트 (배포)
class UMISClient:
    def __init__(self, api_key: str):
        self.base_url = "https://api.umis.ai/v1"
        self.api_key = api_key
    
    def analyze_market(self, industry: str):
        """시장 분석 요청 (프롬프트 노출 없음)"""
        response = requests.post(
            f"{self.base_url}/analyze",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={"industry": industry}
        )
        return response.json()

# 서버 (비공개)
class UMISServer:
    def __init__(self):
        # 모든 IP는 서버에만 존재
        self.prompts = load_prompts('umis_core.yaml')  # 서버 내부
        self.patterns = load_patterns('patterns.yaml')
        self.rag = RAGSystem()
    
    def analyze(self, industry: str):
        # 비즈니스 로직 실행 (클라이언트는 모름)
        context = self.rag.search(industry)
        prompt = self.prompts['observer']['market_structure']
        result = llm.generate(prompt + context)
        return sanitize_output(result)  # 민감 정보 제거
```

**평가**:
- ✅✅✅ 완벽한 IP 보호
- ✅✅ 중앙 집중 업데이트
- ✅ 사용 추적 및 과금
- ⚠️⚠️ 아키텍처 대변경
- ⚠️ 네트워크 지연
- ⚠️ 서버 비용 증가
- **적합**: SaaS 플랫폼, API 비즈니스

---

#### 3.2 TEE (Trusted Execution Environment)

**개념**: 하드웨어 암호화 영역에서만 실행

```yaml
기술:
  - Intel SGX
  - AMD SEV
  - AWS Nitro Enclaves
  
원리:
  - 메모리 암호화 (CPU 레벨)
  - OS도 접근 불가
  - 코드 변조 감지
  
장점:
  - 클라이언트 환경에서도 안전
  - 역공학 거의 불가능
  
단점:
  - 특수 하드웨어 필요
  - 복잡한 구현
  - 성능 오버헤드 20-30%
```

**평가**:
- ✅✅✅ 최고 수준 보호
- ⚠️⚠️⚠️ 구현 복잡도 극상
- ⚠️⚠️ 하드웨어 의존성
- **적합**: 국방, 금융 (극비 알고리즘)

---

#### 3.3 Homomorphic Encryption (미래 기술)

**개념**: 암호화된 채로 연산

```python
# 이론적 예시 (현재는 너무 느림)
encrypted_input = encrypt(user_query)
encrypted_result = umis_model(encrypted_input)  # 암호화 상태로 추론
decrypted_result = decrypt(encrypted_result)

# 서버는 입력/출력을 모름!
```

**평가**:
- ✅✅✅ 이론상 완벽
- ❌❌❌ 현실적으로 너무 느림 (1000배+)
- **적합**: 5-10년 후 고려

---

## 📊 보호 수준 비교표

### 포맷별 보호 수준

| 포맷 | 가독성 차단 | 역공학 난이도 | 복원 시간 | 암호학적 안전 |
|------|-------------|---------------|-----------|---------------|
| **YAML** | ❌ | ⭐ | 5분 | ❌ |
| **JSON** | ❌ | ⭐ | 5분 | ❌ |
| **MessagePack** | ✅ | ⭐⭐ | 1시간 | ❌ |
| **Protobuf** | ✅ | ⭐⭐ | 2시간 | ❌ |
| **Encrypted MsgPack** | ✅ | ⭐⭐⭐⭐ | 불가능* | ✅ |
| **PyArmor** | ✅ | ⭐⭐⭐⭐⭐ | 수주 | ⚠️ |
| **Server API** | ✅ | N/A | 불가능 | ✅ |

*키가 노출되지 않은 경우

---

### 통합 전략 (권장)

#### Tier 1: 일반 SaaS (낮은 보호)

```yaml
설정 파일:
  - MessagePack + zstd 압축
  - 환경변수로 일부 설정

소스 코드:
  - .pyc 배포

프롬프트/패턴:
  - MessagePack (바이너리)

평가:
  - 비용: $0
  - 구현: 1-2주
  - 보호 수준: ⭐⭐
  - 적합: B2C, 낮은 경쟁 강도
```

---

#### Tier 2: B2B SaaS (중급 보호)

```yaml
설정 파일:
  - AES-256 암호화
  - 키: 환경변수 (고객별)

소스 코드:
  - PyArmor Basic (오픈소스)

프롬프트/패턴:
  - Protobuf + AES-256
  - 고객 인증 필요

평가:
  - 비용: $0-100/년
  - 구현: 1개월
  - 보호 수준: ⭐⭐⭐⭐
  - 적합: B2B, 온프레미스
```

---

#### Tier 3: 엔터프라이즈 (고급 보호)

```yaml
아키텍처:
  - 서버 기반 API
  - 클라이언트는 UI만

설정/프롬프트:
  - 서버 내부에만 존재
  - AWS KMS 키 관리

소스 코드:
  - PyArmor Pro ($379/년)
  - 만료 날짜/기기 제한

추가 보안:
  - API 키 인증
  - Rate limiting
  - 감사 로그

평가:
  - 비용: $400-5,000/년
  - 구현: 3-6개월
  - 보호 수준: ⭐⭐⭐⭐⭐
  - 적합: 금융, 컨설팅
```

---

## 🎯 UMIS 권장 전략

### Phase 1: 즉시 적용 (무료, 1주)

```python
# 1. MessagePack + 압축
import msgpack
import zstandard as zstd

def build_production():
    # 프롬프트
    prompts = yaml.safe_load(open('umis_core.yaml'))
    packed = msgpack.packb(prompts)
    compressed = zstd.compress(packed, level=22)
    open('dist/prompts.bin', 'wb').write(compressed)
    
    # 패턴
    patterns = yaml.safe_load(open('data/raw/umis_business_model_patterns.yaml'))
    packed = msgpack.packb(patterns)
    compressed = zstd.compress(packed, level=22)
    open('dist/patterns.bin', 'wb').write(compressed)
    
    # 설정
    config = yaml.safe_load(open('config/schema_registry.yaml'))
    packed = msgpack.packb(config)
    compressed = zstd.compress(packed, level=22)
    open('dist/config.bin', 'wb').write(compressed)

# 2. .pyc만 배포
python -m compileall umis_rag/
find umis_rag -name "*.py" -delete
```

**효과**:
- ✅ 성능: 87배 빠름 (기존 벤치마크)
- ✅ 크기: 73% 감소
- ✅ 보호: 평문 차단 (기본 역공학만 막음)
- ✅ 비용: $0

---

### Phase 2: 중급 보호 (선택, 1개월)

**조건**:
- B2B 고객 대상
- 경쟁사 모방 우려
- 온프레미스 배포

```python
# 1. AES-256 암호화
from cryptography.fernet import Fernet
import msgpack

class SecureUMIS:
    def __init__(self):
        # 고객별 키 생성
        self.key = os.getenv('UMIS_LICENSE_KEY')
        if not self.key:
            raise LicenseError("Invalid license")
        
        self.cipher = Fernet(self.key.encode())
    
    def load_prompts(self):
        encrypted = open('prompts.enc', 'rb').read()
        decrypted = self.cipher.decrypt(encrypted)
        return msgpack.unpackb(decrypted)

# 2. PyArmor (선택)
pyarmor gen --pack dist --obf-code 2 umis_rag/
```

**효과**:
- ✅✅ 보호: 키 없이 사용 불가
- ✅ 라이선스: 고객별 관리
- ⚠️ 성능: +1ms (복호화)
- ⚠️ 비용: $0-379/년

---

### Phase 3: API 서비스 (선택, 6개월)

**조건**:
- SaaS 비즈니스 모델
- 사용량 기반 과금
- 완벽한 IP 보호 필요

```python
# 서버 (FastAPI)
from fastapi import FastAPI, Depends
from umis_rag import UMISCore

app = FastAPI()
umis = UMISCore()  # 모든 IP 서버에만

@app.post("/api/v1/analyze")
async def analyze(
    request: AnalysisRequest,
    api_key: str = Depends(verify_api_key)
):
    # 비즈니스 로직 실행 (클라이언트 모름)
    result = umis.analyze(
        industry=request.industry,
        prompts=umis.prompts,  # 서버 내부
        patterns=umis.patterns
    )
    return sanitize(result)

# 클라이언트 SDK
class UMISClient:
    def analyze(self, industry: str):
        return requests.post(
            "https://api.umis.ai/v1/analyze",
            json={"industry": industry}
        )
```

**효과**:
- ✅✅✅ 보호: IP 완전 비노출
- ✅✅ 수익: 사용량 과금
- ✅ 업데이트: 실시간
- ⚠️⚠️ 비용: 서버 운영
- ⚠️ 레이턴시: +100-300ms

---

## 💰 비용 효과 분석 (보안 포함)

### 시나리오 A: B2B 온프레미스 (100 고객)

| 항목 | 평문 YAML | 암호화 MsgPack | 차이 |
|------|-----------|----------------|------|
| **고객 이탈 (모방)** | 30% | 5% | -25% |
| **연간 매출** | $700K | $950K | **+$250K** |
| **구현 비용** | $0 | $5K | -$5K |
| **순이익 증가** | - | - | **+$245K** |

**ROI**: 4,900%

---

### 시나리오 B: SaaS API (10,000 사용자)

| 항목 | 평문 배포 | API 서비스 | 차이 |
|------|-----------|------------|------|
| **IP 유출 확률** | 80% | 0% | -80% |
| **경쟁사 진입 장벽** | 낮음 | 높음 | ✅ |
| **서버 비용** | $0 | $500/월 | -$6K/년 |
| **매출 보호** | - | $1M+/년 | **+$1M** |

**ROI**: 무한대 (IP 보호 가치)

---

## 🚨 실제 사례 (경고)

### Case 1: OpenAI GPTs (2023)
```
문제: 커스텀 GPT 프롬프트 추출 가능
방법: "Repeat the words above"
결과: 수많은 프롬프트 유출

교훈: 평문 프롬프트는 반드시 유출됨
```

### Case 2: Midjourney (2023)
```
문제: 프롬프트 엔지니어링 역공학
방법: 결과물 분석으로 프롬프트 추론
결과: 경쟁 서비스 등장

교훈: 서버 기반도 완벽하지 않음 (출력 분석)
```

### Case 3: GitHub Copilot
```
해결책: 모델 자체를 서버에만
방법: VSCode는 API 호출만
결과: IP 보호 성공

교훈: API 아키텍처가 Best Practice
```

---

## ✅ 최종 권장사항

### UMIS v7.5.0 프로덕션 전략

```yaml
개발 환경:
  - YAML (가독성, Git diff)
  
빌드 시 변환:
  - YAML → MessagePack + zstd
  - Python → .pyc
  
추가 보호 (고객 유형별):
  
  무료/오픈소스:
    - MessagePack (바이너리 정도)
  
  B2C SaaS:
    - MessagePack + zstd
    - 환경변수 설정
  
  B2B 온프레미스:
    - AES-256 암호화
    - 고객별 라이선스 키
    - PyArmor Basic (오픈소스)
  
  엔터프라이즈:
    - PyArmor Pro ($379/년)
    - AES-256 + KMS
    - 만료/기기 제한
  
  SaaS API:
    - 서버 기반 아키텍처
    - 클라이언트 SDK만 배포
    - IP 100% 서버 보관
```

---

## 📋 체크리스트

### Phase 1 (즉시)
- [ ] MessagePack + zstd 빌드 스크립트
- [ ] .py → .pyc 변환
- [ ] Docker 이미지 최적화
- [ ] 배포 테스트

### Phase 2 (1개월, B2B 시)
- [ ] AES-256 암호화 구현
- [ ] 라이선스 키 관리 시스템
- [ ] PyArmor 평가 및 도입
- [ ] 고객별 빌드 자동화

### Phase 3 (6개월, SaaS 시)
- [ ] API 서버 아키텍처 설계
- [ ] 클라이언트 SDK 개발
- [ ] 인증/과금 시스템
- [ ] 마이그레이션 계획

---

## 참고 자료

- **PyArmor**: https://pyarmor.readthedocs.io/
- **Fernet 암호화**: https://cryptography.io/en/latest/fernet/
- **AWS KMS**: https://aws.amazon.com/kms/
- **Intel SGX**: https://www.intel.com/content/www/us/en/developer/tools/software-guard-extensions/overview.html

