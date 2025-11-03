# UMIS Setup Files

이 폴더는 UMIS 설치와 관련된 모든 파일을 포함합니다.

## 📁 파일 구조

```
setup/
├── README.md                  # 이 파일
├── setup.py                   # 자동 설치 스크립트
├── AI_SETUP_GUIDE.md          # AI Assistant용 가이드
├── SETUP.md                   # 상세 설치 가이드 (사용자용)
└── START_HERE.md              # UMIS 시작 가이드
```

## 🚀 사용 방법

### AI 자동 설치

```
Cursor에서:
"UMIS 설치해줘" 또는 "@setup"
```

### 스크립트 실행

```bash
# 루트 디렉토리에서
python setup/setup.py              # 전체 설치
python setup/setup.py --minimal    # 최소 설치
python setup/setup.py --check      # 상태 확인
```

### 수동 설치

[`SETUP.md`](SETUP.md) 참조

## 📚 각 파일 설명

### setup.py
**대상**: 터미널 사용자 또는 AI  
**기능**: 전체 설치 프로세스 자동화
- 환경 확인
- 패키지 설치
- .env 설정
- RAG 인덱스 빌드
- Neo4j 설정 (선택)

### AI_SETUP_GUIDE.md
**대상**: AI Assistant (Cursor, Claude, GPT)  
**기능**: AI가 읽고 실행하는 단계별 가이드
- 사전 확인 체크리스트
- 실행 코드 예시
- 오류 처리 방법
- 진행 상황 리포트 템플릿

### SETUP.md
**대상**: 처음 사용하는 사용자  
**기능**: 상세한 수동 설치 가이드
- Repository Clone
- OpenAI API 키 설정
- Vector DB 생성
- 파일 설명

### START_HERE.md
**대상**: Cursor 사용자  
**기능**: UMIS 빠른 시작 가이드
- 30초 빠른 시작
- Agent 소개
- 프로젝트 구조
- 사용 흐름

## 🔗 관련 문서

- **루트**: [`../INSTALL.md`](../INSTALL.md) - 빠른 설치 안내
- **루트**: [`../README.md`](../README.md) - UMIS 소개
- **루트**: [`../UMIS_ARCHITECTURE_BLUEPRINT.md`](../UMIS_ARCHITECTURE_BLUEPRINT.md) - 전체 아키텍처

## 🎯 설치 순서

```
1. 루트의 INSTALL.md 또는 README.md 읽기
   ↓
2. 설치 방법 선택:
   - AI 자동 설치 (권장)
   - setup.py 실행
   - 수동 설치 (SETUP.md)
   ↓
3. START_HERE.md로 UMIS 시작
   ↓
4. UMIS_ARCHITECTURE_BLUEPRINT.md로 심화 학습
```

## ⚙️ 유지 관리

버전 업데이트 시:
- [ ] `setup.py` 버전 확인
- [ ] 모든 가이드의 버전 번호 업데이트
- [ ] 새로운 의존성 확인
- [ ] 설치 단계 변경 사항 반영

