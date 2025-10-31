# Deliverable Specifications

**목적**: UMIS v6.2 에이전트별 산출물의 AI 최적화 명세서  
**포맷**: 100% YAML (AI 파싱/생성 효율화)  
**버전**: 1.0  
**최종 업데이트**: 2024-10-31

---

## 📁 디렉토리 구조

```
deliverable_specs/
├── validator/          # Rachel (Validator)
│   └── source_registry_spec.yaml
├── quantifier/         # Bill (Quantifier)
│   └── market_sizing_workbook_spec.yaml
├── observer/           # Albert (Observer)
│   └── market_reality_report_spec.yaml
├── explorer/           # Steve (Explorer)
│   └── opportunity_hypothesis_spec.yaml
└── project/            # 프로젝트 공통
    ├── project_meta_spec.yaml
    └── deliverables_registry_spec.yaml
```

---

## 🎯 핵심 개념

### **Spec vs Output**

| Spec (명세서) | Output (산출물) | 사용자 |
|--------------|----------------|--------|
| `.yaml` (AI용) | `.yaml/.xlsx/.md` (사람용) | AI |
| 구조화된 스키마 | 실제 데이터/내용 | 사람 |
| `deliverable_specs/` | `projects/XXX/02_analysis/` | - |

**예시**:
```
Spec (AI가 읽음):
  deliverable_specs/explorer/opportunity_hypothesis_spec.yaml
  
Output (사람이 읽음):
  projects/20241031_piano/02_analysis/explorer/OPP_001.md
```

---

## 📋 Spec 파일 목록

### 1. Validator (Rachel) - 데이터 검증

**source_registry_spec.yaml** (162줄)
- **Output**: `source_registry.yaml` (Pure YAML)
- **Schema**: 17개 필수 필드
- **핵심**: `original_definition` vs `needed_definition` Gap 분석
- **검증**: 평균 신뢰도 ≥ 70%

---

### 2. Quantifier (Bill) - 정량 분석

**market_sizing_workbook_spec.yaml** (301줄)
- **Output**: `market_sizing_*.xlsx` (9개 시트 Excel)
- **핵심 시트**:
  - Sheet 1: Assumptions (직접데이터 vs 추정치 구분)
  - Sheet 2: **Estimation_Details** (7개 섹션 투명 문서화) ⭐
  - Sheet 3-6: 4가지 Method
  - Sheet 7: Convergence (±30% 수렴)
  - Sheet 8-9: Scenarios, Validation
- **검증**: Excel 함수 100%, PDF 백업

---

### 3. Observer (Albert) - 시장 구조

**market_reality_report_spec.yaml** (271줄)
- **Output**: `market_reality_report.md` (YAML Frontmatter + Markdown)
- **Frontmatter**: 시장 구조, 비효율성, 검증 상태
- **Markdown**: 7개 섹션 상세 분석
- **핵심**: 모든 주장에 SRC_ID 또는 quantifier 계산 참조
- **검증**: 3명 (quantifier, validator, guardian)

---

### 4. Explorer (Steve) - 기회 발굴

**opportunity_hypothesis_spec.yaml** (750줄) ⭐⭐⭐
- **Output**: `OPP_YYYYMMDD_NNN_{name}.md` (YAML Frontmatter + Markdown)
- **Frontmatter**: 
  - 검증 상태 (observer, quantifier, validator)
  - 5개 차원 점수 (우선순위 자동 계산)
  - 프레임워크 적용 (7 Powers, 사업모델, Counter-Positioning)
- **Markdown**: 7개 섹션
- **검증**: 3명 필수

**가장 중요한 이유**:
- ✅ 검증 상태 자동 추적
- ✅ 우선순위 자동 계산
- ✅ Portfolio 대시보드 자동 생성

---

### 5. Project 공통

**project_meta_spec.yaml** (261줄)
- **Output**: `.project_meta.yaml` (숨김 파일)
- **관리자**: Guardian (Stewart) 자동
- **추적**: 명확도, 에이전트 활동, 검증, 품질 메트릭
- **자동 업데이트**: 주요 이벤트마다

**deliverables_registry_spec.yaml** (194줄)
- **Output**: `deliverables_registry.yaml`
- **관리자**: Guardian (Stewart) 자동
- **기능**: 
  - 산출물 자동 등록
  - 검증 상태 추적
  - 대시보드 생성

---

## 🔑 Agent ID 기반 설계

### **ID 표준화**

| Agent ID | Role | Name (기본값) | 커스터마이징 가능 |
|----------|------|---------------|------------------|
| `validator` | Validator | Rachel | ✅ |
| `quantifier` | Quantifier | Bill | ✅ |
| `observer` | Observer | Albert | ✅ |
| `explorer` | Explorer | Steve | ✅ |
| `guardian` | Guardian | Stewart | ✅ |

### **폴더 구조**

```
projects/YYYYMMDD_project_name/
└── 02_analysis/
    ├── validator/      # Rachel
    ├── quantifier/     # Bill
    ├── observer/       # Albert
    └── explorer/       # Steve
```

### **Call Sign 형식**

```
[DELIVERABLE_COMPLETE] {agent_id} {filename}
[VALIDATION_REQUEST] {agent_id} {deliverable}

예시:
[DELIVERABLE_COMPLETE] validator source_registry.yaml
[VALIDATION_REQUEST] observer market_reality_report.md
```

---

## 🎯 AI 사용 방식

### **1. 산출물 생성**

```python
# 1. Spec 로드
spec = load_yaml("deliverable_specs/explorer/opportunity_hypothesis_spec.yaml")

# 2. 데이터 준비
data = {
  "hypothesis": {"title": "피아노 구독 서비스", ...},
  "scores": {"market_size": 8, ...}
}

# 3. Frontmatter 생성
frontmatter = generate_frontmatter(spec.frontmatter_schema, data)

# 4. Markdown Body 생성
body = generate_markdown(spec.markdown_sections, data)

# 5. 산출물 저장
output = f"---\n{frontmatter}\n---\n\n{body}"
save("projects/XXX/02_analysis/explorer/OPP_001.md", output)

# 6. Registry 등록
emit("[DELIVERABLE_COMPLETE] explorer OPP_001.md")
```

### **2. 검증 상태 업데이트**

```python
# 1. Observer가 검증 완료
validation_feedback = {
  "status": "passed",
  "score": 8,
  "comment": "구조적으로 실현 가능"
}

# 2. OPP_001.md 파일 읽기
content = load("OPP_001.md")
frontmatter, body = parse_yaml_frontmatter(content)

# 3. Frontmatter 업데이트
frontmatter["validation"]["observer"] = validation_feedback

# 4. Overall 상태 재계산
if all_validators_passed(frontmatter["validation"]):
    frontmatter["validation"]["overall"]["status"] = "passed"

# 5. 파일 저장
save(frontmatter, body)
```

### **3. 대시보드 생성**

```python
# 모든 OPP_*.md의 frontmatter만 파싱
all_opportunities = []
for file in glob("projects/*/02_analysis/explorer/OPP_*.md"):
    fm = parse_frontmatter_only(file)  # Body 읽지 않음 (효율)
    all_opportunities.append(fm)

# 우선순위 정렬 (scores.total 기준)
sorted_opps = sorted(all_opportunities, key=lambda x: x["scores"]["total"], reverse=True)

# Prioritization Matrix 자동 생성
generate_portfolio_dashboard(sorted_opps)
```

---

## 💡 장점

### **AI 관점**

- ✅ **100% 구조화**: YAML 파싱 완벽
- ✅ **자동 검증**: 스키마 기반 필수 필드 체크
- ✅ **효율적 쿼리**: Frontmatter만 읽기 (대시보드)
- ✅ **자동 업데이트**: 검증 상태 자동 반영

### **사람 관점**

- ✅ **가독성**: 산출물은 Markdown/Excel (읽기 편함)
- ✅ **편집 용이**: Frontmatter 무시하고 본문만 편집 가능
- ✅ **재검증**: 모든 근거 추적 가능

### **시스템 관점**

- ✅ **단일 소스**: `deliverable_specs/`만 관리
- ✅ **일관성**: 스키마 기반 강제
- ✅ **확장성**: 새 필드 추가 쉬움
- ✅ **커스터마이징**: ID 기반 → Name 변경 가능

---

## 📊 통계

| Spec 파일 | 줄 수 | 용도 |
|-----------|------|------|
| opportunity_hypothesis_spec.yaml | 750줄 | Explorer 기회 가설 (가장 복잡) |
| market_sizing_workbook_spec.yaml | 301줄 | Quantifier Excel (9개 시트) |
| market_reality_report_spec.yaml | 271줄 | Observer 시장 구조 |
| project_meta_spec.yaml | 261줄 | 프로젝트 메타데이터 |
| deliverables_registry_spec.yaml | 194줄 | 산출물 레지스트리 |
| source_registry_spec.yaml | 162줄 | Validator 데이터 출처 |
| **Total** | **1,939줄** | **6개 Spec** |

---

## 🚀 사용 가이드

### **AI 개발자용**

1. Spec YAML 로드
2. 스키마대로 데이터 준비
3. 렌더링 함수로 산출물 생성
4. 검증 규칙 자동 체크
5. Registry 자동 등록

### **UMIS 사용자용**

- **몰라도 됩니다!**
- AI가 자동으로 처리
- 산출물(MD/XLSX)만 보면 됨

---

## 📖 참조

- **Parent**: `umis_deliverable_standards_v6.2.yaml`
- **Guidelines**: `umis_guidelines_v6.2.yaml` SECTION 5
- **Examples**: `umis_examples_v6.2.yaml`

---

**Spec Version**: 1.0  
**UMIS Version**: 6.2  
**Release**: 2024-10-31


