# 프로덕션 포맷 벤치마크 가이드

**작성일**: 2025-11-08  
**브랜치**: production-format-optimization

---

## 빠른 시작

### 1. 기본 벤치마크 실행

```bash
python scripts/benchmark_formats.py
```

**결과 예시**:
```
============================================================
UMIS 포맷 벤치마크 시작
============================================================

[1/5] YAML 테스트...
  ✅ Write: 2.50ms | Read: 3.20ms | Size: 4.82KB
[2/5] JSON 테스트...
  ✅ Write: 0.80ms | Read: 0.95ms | Size: 4.95KB
[3/5] MessagePack 테스트...
  ✅ Write: 0.45ms | Read: 0.52ms | Size: 3.21KB
...

============================================================
벤치마크 결과 비교
============================================================

Format       Size (KB)    Write (ms)   Read (ms)    Total (ms)  
------------------------------------------------------------
YAML         4.82         2.50         3.20         5.70        
JSON         4.95         0.80         0.95         1.75        
MSGPACK      3.21         0.45         0.52         0.97        

============================================================
YAML 대비 성능 (낮을수록 좋음)
============================================================

Format       Size         Write        Read         Total       
------------------------------------------------------------
YAML         1.00         1.00         1.00         1.00        
JSON         1.03         0.32         0.30         0.31        
MSGPACK      0.67         0.18         0.16         0.17        

============================================================
권장사항
============================================================
📦 최소 크기: MSGPACK (3.21KB)
⚡ 최고 읽기 속도: MSGPACK (0.52ms)
🚀 최고 전체 속도: MSGPACK (0.97ms)
```

---

## 옵션

### 데이터 크기 변경

```bash
# 작은 데이터 (1개 패턴)
python scripts/benchmark_formats.py --size small

# 중간 데이터 (10개 패턴) - 기본값
python scripts/benchmark_formats.py --size medium

# 큰 데이터 (54개 패턴, 실제 UMIS 규모)
python scripts/benchmark_formats.py --size large
```

### 반복 실행 (평균 계산)

```bash
# 10회 반복 후 평균
python scripts/benchmark_formats.py --iterations 10

# 큰 데이터 + 10회 반복
python scripts/benchmark_formats.py --size large --iterations 10
```

---

## 필요 라이브러리

### 필수
```bash
pip install pyyaml
```

### 선택 (각 포맷 테스트용)
```bash
# MessagePack
pip install msgpack

# Parquet
pip install pandas pyarrow

# CBOR
pip install cbor2
```

**전체 설치**:
```bash
pip install pyyaml msgpack pandas pyarrow cbor2
```

---

## 실제 UMIS 파일 벤치마크

### 1. Explorer 패턴 (54개)

```bash
# 테스트 데이터 생성
python scripts/benchmark_formats.py --size large
```

### 2. 실제 설정 파일

```python
# scripts/benchmark_real_files.py (별도 작성 필요)
import yaml
from benchmark_formats import FormatBenchmark

# umis.yaml 테스트
with open('umis.yaml') as f:
    umis_config = yaml.safe_load(f)

benchmark = FormatBenchmark(umis_config)
results = benchmark.run_all()
```

---

## 결과 해석

### 파일 크기 (Size)
- **낮을수록 좋음**: 배포 이미지 크기 감소, 네트워크 전송 빠름
- **목표**: YAML 대비 30% 이상 감소

### 쓰기 속도 (Write)
- **빌드 시 중요**: 개발 중 자주 실행되는 경우
- **프로덕션**: 한 번만 빌드하므로 덜 중요

### 읽기 속도 (Read)
- **가장 중요**: 애플리케이션 시작 시마다 실행
- **목표**: YAML 대비 50% 이상 개선

### 전체 속도 (Total)
- **종합 성능 지표**
- **목표**: YAML 대비 50% 이상 개선

---

## 예상 결과 (경험적)

### Small (1개 패턴, ~5KB)

| Format | Size | Read Time | Total Time |
|--------|------|-----------|------------|
| YAML | 1.00x | 1.00x | 1.00x |
| JSON | 1.05x | 0.30x | 0.35x |
| MessagePack | **0.65x** | **0.15x** | **0.18x** |
| CBOR | 0.70x | 0.20x | 0.25x |

### Large (54개 패턴, ~200KB)

| Format | Size | Read Time | Total Time |
|--------|------|-----------|------------|
| YAML | 1.00x | 1.00x | 1.00x |
| JSON | 1.05x | 0.28x | 0.32x |
| MessagePack | **0.60x** | **0.12x** | **0.15x** |
| Parquet | **0.25x** | 0.10x | 0.12x |

**결론**:
- **MessagePack**: 범용적으로 2-6배 빠름, 30-40% 작음
- **Parquet**: 테이블 데이터의 경우 75% 작음 (압축 시)

---

## 다음 단계

### Phase 1: 검증 완료 후
1. ✅ 벤치마크 결과 확인
2. 📊 `docs/architecture/BENCHMARK_RESULTS.md` 작성
3. 🎯 시나리오 1 구현 결정

### Phase 2: 프로덕션 빌드 스크립트
```bash
# scripts/build_production.py
- YAML → JSON (config)
- YAML → MessagePack (patterns)
- YAML → Parquet (benchmarks)
```

### Phase 3: 환경별 로더
```python
# umis_rag/core/config_loader.py
if ENV == 'production':
    # MessagePack 로딩
else:
    # YAML 로딩 (개발)
```

---

## 참고

- 전체 분석: `docs/architecture/PRODUCTION_FORMAT_OPTIONS.md`
- 벤치마크 스크립트: `scripts/benchmark_formats.py`

