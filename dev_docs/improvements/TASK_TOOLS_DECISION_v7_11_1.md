# Task 도구 제거 결정 (v7.11.1)

## 결정 사항

**Complete 도구만 사용 (15개)**

- System 도구: 9개
- Complete 도구: 6개
- Task 도구: 제거 (0개)

## 근거

### 1. 유지보수 복잡도
- Complete: 15개 관리
- Task 포함: 44개 관리 (2.9배 ↑)
- umis.yaml 업데이트마다 44개 재생성 필요

### 2. 실제 동작
- Task 쿼리 → Complete로 Vector Fallback
- Task 없어도 시스템 정상 작동
- 현재 tool_registry.yaml (365KB) > 백업 (113KB)
  → 의도적 Task 제거로 추정

### 3. ROI 분석
| 사용 규모 | API 절감 | 개발+유지 | ROI |
|----------|---------|----------|-----|
| 개인 (100회/월) | $42.6/년 | 59시간 | ❌ |
| 스타트업 (500회/월) | $213/년 | 59시간 | ⚠️ |
| 기업 (2000회/월) | $852/년 | 59시간 | ✅ |

### 4. 사용 패턴
- **모호한 요청**: Complete 필수
- **복잡한 협업**: Complete가 효율적
- **작업 범위 확장**: Task는 여러 번 RAG 호출

### 5. 컨텍스트
- 200K 모델: Discovery Sprint 51% (안정적)
- 400K 모델: Discovery Sprint 26% (여유)
- Complete로 충분

## 대안 옵션 (재고려 가능)

### Option 2: Hybrid
**조건**: 128K 모델 + Discovery Sprint  
**구현**: 특정 시나리오만 Task 선택  
**적합**: 컨텍스트 제약 실제 문제

### Option 3: Task 재생성
**조건**: 엔터프라이즈 (2000+회/월)  
**구현**: 백업 복원 또는 자동 생성  
**적합**: API 비용 최우선

## 구현

- [x] `umis_core.yaml`: 44개 → 15개
- [x] Task 제거 근거 주석
- [x] 대안 옵션 문서화
- [x] Discovery Sprint 패턴 추가

## 권장 전략

```yaml
일반 작업:
  모델: claude-sonnet-3.5 (200K)
  도구: Complete

Discovery Sprint:
  모델: gemini-1.5-pro (272K)
  도구: Complete

예산 최우선:
  모델: gpt-4o-mini (128K)
  전략: 작업 분할
```

---

**날짜**: 2025-11-26  
**버전**: v7.11.1  
**상세**: `CONTEXT_WINDOW_STRATEGY.md` 참조
