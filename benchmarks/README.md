# UMIS Benchmarks

**Status**: ⚠️ **DEPRECATED** (v7.11.0)

---

## 📍 New Location

**All benchmarks have been migrated to the `tests/` folder:**

```
tests/
├── unit/                       # Unit Tests
│   ├── test_prior_estimator.py     # Stage 2 (Prior)
│   ├── test_fermi_estimator.py     # Stage 3 (Fermi)
│   └── ...
│
├── integration/                # Integration Tests
│   ├── test_stage_flow_v7_11_0.py  # Stage 1→2→3→4 flow
│   └── ...
│
├── e2e/                        # End-to-End Tests
│   ├── test_estimator_e2e_scenarios_v7_11_0.py  # 10 scenarios
│   └── ...
│
└── ab_testing/                 # AB Testing
    └── test_stage_ab_framework_v7_11_0.py  # Budget comparison
```

---

## 🚀 Running Benchmarks

### Unit Tests
```bash
# Stage 2 (Prior Estimator)
pytest tests/unit/test_prior_estimator.py -v

# Stage 3 (Fermi Estimator)
pytest tests/unit/test_fermi_estimator.py -v
```

### Integration Tests
```bash
# Stage 1→2→3→4 flow
pytest tests/integration/test_stage_flow_v7_11_0.py -v
```

### E2E Tests
```bash
# 10 Fermi problems
pytest tests/e2e/test_estimator_e2e_scenarios_v7_11_0.py -v
```

### AB Testing
```bash
# Standard vs Fast Budget
pytest tests/ab_testing/test_stage_ab_framework_v7_11_0.py -v
```

---

## 📚 Documentation

- **Architecture**: `/docs/architecture/UMIS_ARCHITECTURE_BLUEPRINT.md`
- **Migration Guide**: `/docs/MIGRATION_GUIDE_v7_11_0.md`
- **User Guide**: `/docs/guides/ESTIMATOR_USER_GUIDE_v7_11_0.md`
- **Budget Config**: `/docs/guides/BUDGET_CONFIGURATION_GUIDE.md`

---

## 🗂️ Legacy Benchmarks

**Phase-based benchmarks (v7.10.2 and below)** → **Archive**

- **Location**: `archive/benchmarks_all_legacy/`
- **Reason**: v7.11.0 migrated to 4-Stage Fusion Architecture
- **Contents**:
  - Phase 0-4 benchmarks (deprecated)
  - Recursive Fermi tests (deprecated)
  - Legacy model configurations

---

## 🎯 v7.11.0 Changes

### Architecture Shift
- **Phase 5 (0-4)** → **4-Stage Fusion (1-4)**
- Removed recursion (3-10x speed improvement)
- Budget-based exploration
- Unified test framework

### Test Organization
- Separated by test type (unit/integration/e2e/ab)
- Consistent naming conventions
- Standardized result formats

### Model Configuration
- Centralized in `config/model_configs.yaml`
- TaskType-specific overrides
- LLM Provider abstraction

---

**For legacy benchmarks, see**: `archive/benchmarks_all_legacy/`

**Last Updated**: 2025-11-26  
**Version**: Deprecated (use `tests/` instead)
