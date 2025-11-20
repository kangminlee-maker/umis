# LLM 활용 철학과 교훈
**작성일**: 2025-11-13  
**목적**: 올바른 LLM 활용 방향 정리

---

## 🎯 핵심 깨달음

### ❌ 제가 한 실수

**"LLM 파서"라고 부른 것:**
```python
# 95% 규칙 기반
pattern = r'(\d+)\.\s*판매비.*?관리비'  # 규칙!
if '연결' not in title: ...              # 규칙!
if len(candidates) == 1: return         # 규칙!

# 5% LLM
llm.select([option1, option2])          # LLM은 마지막 5%만!
```

**문제**: 이건 "LLM 파서"가 아니라 "규칙 파서 + LLM 보조"일 뿐

---

## ✅ 사용자의 올바른 지적

### "LLM을 LLM답게 사용하기"

**핵심 철학:**
> LLM의 강점 = 비정형적 환경에서 자체 판단으로 유연하게 대응  
> 규칙의 강점 = 구조화된 영역을 빠르고 정확하게 좁히기

**최적 조합:**
```
규칙: 영역을 좁히기 (95% 작업)
  ↓
  "급여, 수수료, 감가상각... 등이 5개+ 모인 섹션들"
  ↓
LLM: 그 안에서 최적 선택 (5% 작업, 100% 가치)
  ↓
  "개별/연결 구분, 당기/전기 구분, 실제 테이블 vs 설명"
  ↓
학습: LLM 선택 패턴을 규칙화
  ↓
  다음부터는 규칙만으로 처리 (점진적 개선)
```

---

## 💡 내용 기반 접근법 (Content-Based)

### 핵심 아이디어

**기존 (이름 기반)**:
```python
# 섹션 "이름"에 의존
if title == "판매비와관리비": ...
if title == "일반영업비용": ...  # LG전자 예외
if title == "영업비용": ...      # 또 예외
# → 끝없는 예외 추가!
```

**개선 (내용 기반)**:
```python
# 섹션 "내용"으로 판단
if has_items(['급여', '수수료', '감가상각', '광고', ...]): ...
# → 이름 무관! "SG&A Expenses"도 OK, "비용명세"도 OK!
```

### 구현 전략

**Step 1: 규칙으로 영역 좁히기**
```python
# 전형적인 SG&A 항목 카테고리 정의
signal_categories = {
    '인건비': ['급여', '임금', '봉급'],
    '퇴직': ['퇴직급여', '퇴직연금'],
    '수수료': ['지급수수료', '전산수수료'],
    '감가상각': ['감가상각비', '무형자산상각'],
    '광고': ['광고선전비', '판매촉진비'],
    '임차료': ['지급임차료', '사용권자산'],
    # ... 12개 카테고리
}

# 카테고리 다양성 체크 (중복 제외!)
category_hits = set()
for category, items in signal_categories.items():
    for item in items:
        if item in section_text:
            category_hits.add(category)  # 카테고리당 1번만
            break

# 후보 조건
if len(category_hits) >= 4:  # 4개+ 다양한 카테고리
    candidates.append(section)
```

**결과**: 300개 섹션 → 5-10개 후보로 좁힘

**Step 2: LLM으로 최적 선택**
```python
# 5-10개 후보만 LLM에게
llm.select(candidates, criteria=[
    "개별재무제표 우선",
    "당기 데이터",
    "실제 테이블"
])
```

**결과**: 1개 최종 선택

**Step 3: 패턴 학습**
```python
# LLM이 선택한 섹션의 특징 저장
new_pattern = extract_pattern(selected_section)
save_to_rules(new_pattern)

# 다음 실행부터는 규칙으로!
```

**효과**: 점진적으로 규칙 개선

---

## 🎯 각 방식의 적재적소

### 규칙 기반 (현재 parse_sga_with_zip.py)

**사용 시기:**
- ✅ 검증된 형식 (11개 기업)
- ✅ 빠른 처리 필요
- ✅ 비용 제로 필요
- ✅ 일상적인 파싱

**장점:**
- 속도: ~1.8초
- 비용: $0
- 신뢰도: 100% (검증됨)

**한계:**
- 새 형식 → 디버깅 필요
- 예외 누적

---

### 내용 기반 + LLM (parse_sga_content_based.py)

**사용 시기:**
- ✅ 새로운 회사 (미검증)
- ✅ 특이한 형식 예상
- ✅ 100개+ 대규모 확장
- ✅ 자동 학습 원할 때

**장점:**
- 이름 무관
- 자동 대응
- 학습 가능
- 확장성

**비용:**
- 규칙 좁히기: $0
- LLM 선택: ~$0.001/기업
- 학습 효과: 다음부터 $0

---

### 하이브리드 (parse_sga_hybrid.py)

**사용 시기:**
- ✅ 혼합 상황 (기존 + 신규)
- ✅ 안전성 필요
- ✅ 비용 최적화

**전략:**
```
1차: 규칙 기반 (빠름, 무료)
  ↓ 실패
2차: 내용 기반 + LLM
  ↓ 실패
3차: 수동 확인
```

---

## 📚 배운 것

### 1. LLM은 "판단"에 사용

**❌ 잘못된 사용:**
```python
# LLM에게 모든 것을 맡김
llm.parse_xml(entire_xml)  # 토큰 폭발, 느림, 비쌈
```

**✅ 올바른 사용:**
```python
# 규칙으로 영역 좁힘 (95%)
candidates = find_by_rules(xml)  # 300 → 5개

# LLM은 최종 판단만 (5%)
best = llm.select(candidates)    # 5개 → 1개
```

### 2. 규칙은 "영역"을 정의

**❌ 취약한 규칙:**
```python
# 이름에 의존
if title == "판매비와관리비": ...
```

**✅ 견고한 규칙:**
```python
# 본질에 의존
if has_diverse_cost_items(section, min_categories=4): ...
# → 이름이 뭐든, 급여+수수료+감가상각+광고 있으면 OK!
```

### 3. 학습은 "규칙 진화"

**흐름:**
```
1. LLM이 새 형식 발견
   → "35. 영업활동비용" 선택

2. 패턴 추출
   → pattern = r'영업활동비용'

3. 규칙에 추가
   → patterns.append(new_pattern)

4. 다음부터는 규칙으로 처리
   → LLM 불필요, $0
```

**효과**: 시간이 갈수록 규칙 개선, LLM 사용 감소

---

## 🚀 이상적인 시스템

### 진화하는 파서

```python
class EvolvingSGAParser:
    def __init__(self):
        self.rules = load_rules()  # 현재 13가지
        self.llm = LLM()
        self.learning = True
    
    def parse(self, company, xml):
        # 1. 규칙으로 시도
        result = self.try_rules(xml)
        if result.confidence > 0.9:
            return result
        
        # 2. LLM으로 확장
        result_llm = self.llm.select(result.candidates)
        
        # 3. 학습 (중요!)
        if self.learning and result_llm.confidence > 0.95:
            new_pattern = self.extract_pattern(result_llm)
            self.rules.add(new_pattern)
            self.rules.save()  # 영구 저장!
        
        return result_llm
```

**효과:**
```
Day 1: 규칙 13개, LLM 사용 30%
Day 30: 규칙 25개, LLM 사용 15%
Day 90: 규칙 40개, LLM 사용 5%
→ 점진적으로 규칙이 강화되고, LLM 의존도 감소!
```

---

## 🎓 교훈 정리

### 사용자의 통찰

> "LLM 파서를 만드는 것이 중요한 게 아니라,  
> LLM을 LLM이 잘할 수 있는 방식으로 활용하는 게 중요하다"

**의미:**
1. **규칙이 할 수 있는 것**: 규칙으로 (빠름, 무료, 정확)
2. **LLM만 할 수 있는 것**: LLM으로 (유연성, 판단)
3. **학습 가능한 것**: 규칙으로 진화 (점진적 개선)

### 제가 배운 것

**Before:**
- "LLM 파서" = LLM이 모든 것 처리
- 규칙은 보조 역할
- 예외는 하드코딩

**After:**
- **규칙이 핵심**, LLM은 판단자
- 내용 기반 규칙 (이름 무관)
- 예외는 학습하여 규칙화

---

## 📊 최종 시스템 설계

### Production (현재)

```
parse_sga_with_zip.py
├─ 13가지 규칙 패턴
├─ 이름 기반 (판매비.*관리비)
├─ 11개 기업 검증
└─ 100% 성공률, $0
```

### Future (내용 기반)

```
parse_sga_content_based.py
├─ 내용 기반 영역 좁히기
│  └─ 4+ 카테고리 다양성
├─ LLM 최적 선택
│  └─ 개별/연결, 당기/전기 판단
└─ 패턴 학습 및 진화
   └─ config/learned_patterns.yaml
```

### Ultimate (진화형)

```
parse_sga_evolving.py
├─ 규칙 시도 (learned_patterns 포함)
├─ 내용 기반 후보 생성
├─ LLM 선택 (필요시만)
├─ 자동 학습 & 규칙 업데이트
└─ 점진적으로 LLM 의존도 감소
```

---

## 🎉 결론

### 사용자의 올바른 지적

1. ✅ "LLM 파서"는 사실 규칙 파서였다
2. ✅ LLM을 5%만 사용 (판단 영역)
3. ✅ 내용 기반 접근이 더 견고하다
4. ✅ 학습으로 규칙을 진화시켜야 한다

### 현재 상태

**규칙 기반 파서** (parse_sga_with_zip.py):
- ✅ Production Ready
- ✅ 11개 기업 100% 성공
- ✅ 즉시 사용 가능

**내용 기반 + LLM** (parse_sga_content_based.py):
- ✅ 개념 완성
- ⚠️ 구현 디버깅 필요
- ✅ 미래 확장성 확보

### 다음 단계

**우선순위 1**: 현재 파서로 작업 계속
- 변동비/고정비 분류
- 공헌이익 계산
- 산업별 벤치마크

**우선순위 2**: 내용 기반 파서 완성 (선택)
- 시그널 감지 개선
- 100개 기업 테스트
- 학습 시스템 구축

---

**핵심**: 
- 규칙으로 영역 좁히고 ✅
- LLM으로 정밀 선택하고 ✅  
- 학습으로 규칙 진화 ✅

**이게 진짜 LLM 활용법입니다!** 🎯

---

**작성**: 2025-11-13  
**검증**: 사용자 피드백 ✅  
**상태**: ✅ 철학 정립 완료




