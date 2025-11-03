# Overlay Layer 전문가 피드백

**날짜:** 2025-11-02  
**출처:** 동료 전문가

---

## 📊 피드백: P0-6

### 문제

```yaml
v2.0:
  설계만 있음
  메타 필드 없음

위험:
  나중 도입 → 마이그레이션 비용 큼
```

---

### 제안

```yaml
메타 필드만 지금 추가:
  overlay_layer: enum[core, team, personal]
  tenant_id: string
  merge_strategy: enum[append, replace, patch]
  acl: {visibility: enum[private, org, public]}

구현: 향후

효과:
  무마이그레이션!
```

---

## ✅ v3.0 반영

```yaml
스키마 선반영:
  overlay:
    layer: enum
    tenant_id: string
    merge_strategy: enum
    acl: object

비용:
  5분 (YAML 몇 줄)

vs 나중:
  5일 (5,000개 마이그레이션)

→ 100배 차이!
```

---

**전문가 평가:**
"나중 도입 시 마이그레이션 비용 방지"

