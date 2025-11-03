# UMIS v7.0.0 설치

## 🚀 빠른 시작

### 방법 1: AI 자동 설치 (권장 ⭐)

```
Cursor Composer (Cmd+I):
"UMIS 설치해줘" 또는 "@setup"
```

AI가 자동으로 전체 설치를 진행합니다 (2-3분).

---

### 방법 2: 자동 스크립트

```bash
python setup/setup.py
```

또는 최소 설치 (Neo4j 제외):

```bash
python setup/setup.py --minimal
```

---

### 방법 3: 수동 설치

**최소 요구사항**:
- Python 3.9+
- OpenAI API 키

**단계**:

```bash
# 1. 패키지 설치
pip install -r requirements.txt

# 2. 환경 변수 설정
cp env.template .env
# .env 파일에서 OPENAI_API_KEY 입력

# 3. RAG 인덱스 빌드
python scripts/02_build_index.py --agent explorer

# 4. 완료! 사용 시작
```

---

## 📚 문서

**설치**:
- [`setup/SETUP.md`](setup/SETUP.md) - 상세 설치 가이드
- [`setup/AI_SETUP_GUIDE.md`](setup/AI_SETUP_GUIDE.md) - AI용 가이드
- [`setup/START_HERE.md`](setup/START_HERE.md) - 빠른 시작

**이해하기**:
- [`UMIS_ARCHITECTURE_BLUEPRINT.md`](UMIS_ARCHITECTURE_BLUEPRINT.md) - 전체 아키텍처 ⭐
- [`FOLDER_STRUCTURE.md`](FOLDER_STRUCTURE.md) - 폴더 구조
- [`CURRENT_STATUS.md`](CURRENT_STATUS.md) - 현재 상태

---

## ✅ 설치 확인

```bash
python setup/setup.py --check
```

---

## 🆘 문제 해결

### OpenAI API 키가 없어요
1. https://platform.openai.com/api-keys 방문
2. API 키 생성
3. `.env` 파일에 입력

### 패키지 설치 실패
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### RAG 인덱스 빌드 실패
1. `.env`에서 `OPENAI_API_KEY` 확인
2. 네트워크 연결 확인
3. 재시도: `python scripts/02_build_index.py --agent explorer`

---

## 💬 도움말

질문이나 문제가 있으면:
- GitHub Issues: https://github.com/kangminlee-maker/umis/issues
- 또는 AI에게 물어보세요: "UMIS 설치 오류 해결해줘"

