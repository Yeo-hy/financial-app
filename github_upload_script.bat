@echo off
echo 🚀 AI 재무분석 플랫폼 GitHub 업로드 스크립트
echo.

REM GitHub CLI 설치 확인
gh --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ GitHub CLI가 설치되지 않았습니다.
    echo 📥 설치 방법: https://cli.github.com/
    echo    또는 winget install --id GitHub.cli
    pause
    exit /b 1
)

echo ✅ GitHub CLI 확인됨

REM GitHub 로그인 확인
gh auth status >nul 2>&1
if %errorlevel% neq 0 (
    echo 🔐 GitHub에 로그인해주세요...
    gh auth login
)

echo ✅ GitHub 인증 확인됨

REM 저장소 복제 또는 초기화
if not exist ".git" (
    echo 📂 GitHub 저장소 초기화 중...
    git init
    git remote add origin https://github.com/Yeo-hy/fsan.git
)

echo 📤 파일 업로드 시작...

REM 모든 파일 추가
git add .

REM 커밋
git commit -m "🚀 AI 재무분석 & 감사 리스크 분석 플랫폼 - 초기 배포

✨ 주요 기능:
- 📊 재무비율 분석 및 시각화  
- 🤖 AI 기반 감사 리스크 분석 (Gemini API)
- 📈 실시간 재무데이터 조회 (OpenDart API)
- ⚡ Flask 웹 애플리케이션

🛠️ 기술 스택: Python, Flask, AI, Data Analysis"

REM GitHub에 푸시
git branch -M main
git push -u origin main

echo.
echo ✅ GitHub 업로드 완료!
echo 🌐 저장소 주소: https://github.com/Yeo-hy/fsan
echo.
pause 