# 섹션 선택 로직 개선
**문제**: 섹션 번호는 회사마다 다름
**해결**: 내용 기반 검증

---

## ❌ 현재 로직 (문제)

```python
# 섹션 번호 큰 것 우선
if section_num >= 20:
    score += 50
```

**문제:**
- BGF리테일: 섹션 30 (주석)
- GS리테일: 섹션 28 (주석)
- 삼성전자: 섹션 22 (주석)
- LG전자: 섹션 28 (주석)

→ **회사마다 다름!**

---

## ✅ 개선 로직 (사용자 제안)

### 1. 내용 검증 (핵심!) ⭐

**체크 항목:**

**A. "상품매입" 체크 (매출원가 감지)**
```python
# 상품매입 있으면 잘못된 섹션!
if '상품매입' in section_text or '원재료' in section_text:
    score -= 100  # 큰 페널티!
```

**B. 항목 개수 체크**
```python
# SG&A 세부는 보통 15-30개
item_count = len(parsed_items)

if 15 <= item_count <= 35:
    score += 20  # 정상 범위
elif item_count > 50:
    score -= 50  # 너무 많음 (잘못된 섹션)
elif item_count < 10:
    score -= 30  # 너무 적음
```

**C. 표준 계정 매칭률**
```python
# 17개 표준 SG&A 계정 중 몇 개 매칭?
standard_matches = count_standard_matches(items)

if standard_matches >= 10:
    score += 30  # 많이 매칭 (올바른 섹션)
elif standard_matches >= 5:
    score += 10
```

**D. COGS 항목 페널티**
```python
# 매출원가 항목들
cogs_keywords = ['상품매입', '원재료', '제품변동', '재고변동']

cogs_count = sum(1 for item in items if any(k in item for k in cogs_keywords))

if cogs_count > 0:
    score -= cogs_count * 20  # 항목당 -20점
```

---

### 2. 최종 점수 시스템

```python
for m in matches:
    score = 0
    preview = xml[m.start():m.start()+8000]
    
    # 파싱 시도
    items = parse_section(preview)
    
    # 1. COGS 체크 (최우선!)
    if '상품매입' in preview or '원재료' in preview:
        score -= 100
    
    # 2. 항목 개수
    if 15 <= len(items) <= 35:
        score += 20
    elif len(items) > 50:
        score -= 50
    
    # 3. 표준 계정 매칭
    standard_matches = count_standard_matches(items)
    score += standard_matches * 3
    
    # 4. 개별재무제표
    if '연결' not in m.group():
        score += 10
    
    # 5. 당기 키워드
    if '당기' in preview:
        score += 5
    
    # 6. 섹션 번호 (참고만)
    section_num = int(re.search(r'(\d+)', m.group()).group(1))
    if section_num >= 20:
        score += 5  # 작은 보너스만
    
    if score > best_score:
        best_score = score
        best_match = m
```

---

### 3. 검증 예시

**GS리테일:**

**섹션 1 (잘못됨):**
```
COGS 체크: "상품매입" 있음 → -100점
항목 개수: 75개 → -50점 (너무 많음)
표준 매칭: 10개 → +30점
────────────────
총점: -120점 ❌
```

**섹션 28 (올바름):**
```
COGS 체크: 없음 → 0점
항목 개수: 25개 → +20점 (정상)
표준 매칭: 17개 → +51점
개별: +10점
당기: +5점
────────────────
총점: +86점 ✅
```

→ 섹션 28 선택!

---

## 🎯 핵심 원칙

**1. 내용이 정답을 말한다**
- 섹션 번호 X
- 파싱 결과 O

**2. COGS 체크가 최우선**
- "상품매입" 있으면 즉시 제외

**3. 항목 개수가 힌트**
- 15-30개: 정상
- >50개: 의심

**4. 표준 계정 매칭이 확증**
- 10개+ 매칭: 올바른 섹션

---

## 🚀 구현

**parse_sga_with_zip.py 개선:**

```python
def score_section(section_xml, section_match):
    """섹션 점수 평가"""
    
    score = 0
    preview = section_xml[section_match.start():section_match.start()+8000]
    
    # 파싱 시도
    items = quick_parse(preview)
    
    # 1. COGS 페널티 (최우선!)
    if has_cogs_items(preview):
        score -= 100
    
    # 2. 항목 개수
    score += evaluate_item_count(len(items))
    
    # 3. 표준 계정 매칭
    score += count_standard_matches(items) * 3
    
    # 4. 개별재무제표
    if '연결' not in section_match.group():
        score += 10
    
    # 5. 당기
    if '당기' in preview:
        score += 5
    
    return score, items
```

---

**이 방식이 섹션 번호보다 훨씬 견고합니다!** ✅




