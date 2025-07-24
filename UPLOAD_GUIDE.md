# GitHub 업로드 가이드

## Git 설치 후 실행할 명령어들

### 1. Git 초기 설정
```bash
# Git 사용자 정보 설정 (GitHub 계정 정보로 설정)
git config --global user.name "Yeo-hy"
git config --global user.email "your-email@example.com"
```

### 2. 프로젝트 Git 저장소 초기화
```bash
# 현재 폴더에서 Git 저장소 초기화
git init

# 원격 저장소 연결
git remote add origin https://github.com/Yeo-hy/fsan.git
```

### 3. 파일 추가 및 커밋
```bash
# 모든 파일 추가 (.gitignore에 의해 .env 파일은 제외됨)
git add .

# 첫 번째 커밋
git commit -m "🚀 AI 재무분석 & 감사 리스크 분석 플랫폼 - 초기 배포"
```

### 4. GitHub에 업로드
```bash
# main 브랜치로 설정 (최신 GitHub 기본값)
git branch -M main

# GitHub에 푸시
git push -u origin main
```

## 주의사항
- .env 파일은 .gitignore에 의해 자동으로 제외됩니다 (보안상 중요)
- API 키는 나중에 Render에서 환경변수로 별도 설정
- 모든 명령어는 프로젝트 폴더에서 실행해야 함 