# Routing YAML 전문가 피드백

**날짜:** 2025-11-02  
**출처:** 동료 전문가

---

## 📊 피드백: P0-7

### 확장

```yaml
v2.0:
  config/routing_policy.yaml
  → workflow 정의

v3.0 추가:
  retrieval_policy
  → intent 기반 라우팅

추가 내용:
  - if: intent=="opportunity_discovery"
    then:
      profile: "steve.explorer_v1"
      layers: ["projected", "graph_expand"]
      projection: {method: "rule", view: "explorer"}
```

---

## ✅ v3.0 반영

```yaml
config/routing_policy.yaml 확장:
  
  workflows: (기존)
    explorer_workflow:
      steps: [...]
  
  retrieval: (신규!)
    opportunity_discovery:
      profile: "explorer_v1"
      layers: ["projected", "graph"]
      projection: "rule"

효과:
  더 세밀한 제어
  intent 기반
```

---

**전문가 평가:**
"Intent→Agent/Layer 라우팅 표준화 (YAML-first 유지)"

