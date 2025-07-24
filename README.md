# 🚀 AI 재무분석 & 감사 리스크 분석 플랫폼

> **OpenDart API**와 **Google Gemini AI**를 활용한 종합 재무분석 웹 애플리케이션

## 📋 프로젝트 개요

회계사 및 재무분석가를 위한 AI 기반 재무분석 도구로, 기업의 재무제표를 자동으로 분석하고 감사 리스크를 평가하는 웹 애플리케이션입니다.

### 🎯 주요 특징
- **실시간 재무데이터 조회**: 금융감독원 OpenDart API 연동
- **AI 감사 리스크 분석**: Google Gemini API 기반 자동 분석
- **시각적 데이터 표현**: 인터랙티브 차트 및 그래프
- **사용자 친화적 UI**: 반응형 웹 디자인

## 🛠 기술 스택

### Backend
- **Python 3.x**
- **Flask** - 웹 프레임워크
- **SQLite** - 기업 정보 데이터베이스
- **python-dotenv** - 환경변수 관리

### Data Analysis & Visualization
- **Pandas** - 데이터 처리 및 분석
- **NumPy** - 수치 연산
- **Matplotlib** - 데이터 시각화
- **Seaborn** - 통계적 시각화

### External APIs
- **OpenDart API** - 기업 재무정보 조회
- **Google Gemini AI** - AI 기반 감사 리스크 분석

### Frontend
- **HTML5/CSS3**
- **JavaScript (ES6+)**
- **반응형 웹 디자인**

## 🚀 주요 기능

### 1. 기업 검색 및 조회
- 기업명 기반 실시간 검색
- 기업코드, 주식코드 정보 제공
- 상장기업 데이터베이스 연동

### 2. 재무분석 대시보드
- **주요 재무비율 계산**
  - 유동비율, 부채비율, 자기자본비율
  - 영업이익률, 순이익률
  - ROA, ROE
- **전년 대비 변화율** 자동 계산
- **시각적 트렌드 분석**

### 3. 고급 시각화
- **재무상태표 구성 차트**
- **손익계산서 3개년 비교**
- **재무비율 추이 분석**
- **인터랙티브 그래프**

### 4. AI 감사 리스크 분석 🤖
- **자동 리스크 평가**: 높음/중간/낮음 등급 분류
- **다차원 분석**:
  - 재무적 리스크 (유동성, 수익성, 레버리지)
  - 감사 위험 요소 (고유위험, 통제위험, 발견위험)
  - 중요한 왜곡표시 위험
- **실무 중심 권고사항** 제공
- **한국 회계기준** 기반 분석

## 📱 화면 구성

### 메인 페이지
```
🚀 AI 재무분석 & 감사 리스크 분석 플랫폼
회사명을 검색하여 종합적인 재무분석과 AI 기반 감사 리스크 분석을 받아보세요

[📊 재무비율 분석] [📈 시각화 차트] [🤖 AI 감사 리스크 분석] [⚡ 실시간 분석]
```

### 재무분석 페이지
1. **주요 재무비율** - 7개 핵심 지표 카드형 표시
2. **재무비율 추이 분석** - 시계열 차트
3. **재무상태표 구성** - 파이차트/바차트
4. **손익계산서 분석** - 3개년 비교 차트
5. **AI 감사 리스크 분석** - 종합 리스크 보고서

## 🔧 설치 및 실행

### 1. 환경 설정
```bash
# 저장소 클론
git clone [repository-url]
cd ai-financial-analysis

# 가상환경 생성 (권장)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 의존성 설치
pip install -r requirements.txt
```

### 2. 환경변수 설정
`.env` 파일 생성:
```env
OPENDART_API_KEY=your_opendart_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
FLASK_DEBUG=True
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
```

### 3. 데이터베이스 초기화
```bash
python xml_to_db.py  # 기업정보 데이터베이스 생성
```

### 4. 애플리케이션 실행
```bash
python app.py
```

브라우저에서 `http://localhost:5000` 접속

## 📊 사용 예시

### 기업 분석 워크플로우
1. **기업 검색**: "삼성전자" 입력
2. **재무분석 시작**: 사업연도 및 보고서 선택
3. **자동 분석**: 재무비율 계산 및 차트 생성
4. **AI 분석**: Gemini AI가 감사 리스크 자동 평가
5. **결과 확인**: 종합 리스크 등급 및 권고사항 검토

## 🏗 아키텍처

```
Frontend (HTML/CSS/JS)
       ↓
Flask Web Framework
       ↓
┌─────────────┬─────────────┬─────────────┐
│ OpenDart API│   SQLite    │ Gemini AI  │
│   (재무데이터)  │  (기업정보)   │ (AI분석)    │
└─────────────┴─────────────┴─────────────┘
       ↓
Data Processing (Pandas/NumPy)
       ↓
Visualization (Matplotlib/Seaborn)
```

## 🎨 핵심 기술적 구현

### 1. 비동기 데이터 처리
```javascript
// 자동 AI 분석 트리거
async function analyzeFinancialData() {
    // 재무분석 완료 후 자동으로 AI 분석 시작
    await performAIAnalysis();
}
```

### 2. 동적 차트 생성
```python
def create_trend_analysis_chart(self, financial_data):
    # 다년도 재무비율 추이 분석
    # matplotlib 기반 인터랙티브 차트
```

### 3. AI 프롬프트 엔지니어링
```python
def _create_audit_risk_prompt(self, company_data, financial_metrics, full_financial_data):
    # 한국 회계기준 기반 감사 리스크 분석 프롬프트
    # 구조화된 JSON 응답 생성
```

## 📈 향후 개선 계획

- [ ] **실시간 주가 연동**
- [ ] **업종별 벤치마킹**
- [ ] **예측 모델링** (미래 재무성과 예측)
- [ ] **PDF 보고서 생성**
- [ ] **사용자 인증 시스템**
- [ ] **대시보드 커스터마이징**

## 🛡 보안 고려사항

- **환경변수**: API 키 보안 관리
- **입력 검증**: SQL 인젝션 방지
- **API 제한**: 요청 빈도 제한
- **오류 처리**: 민감정보 노출 방지

## 📞 연락처

**개발자**: [Your Name]
**이메일**: [your.email@example.com]
**GitHub**: [github.com/yourusername]
**LinkedIn**: [linkedin.com/in/yourprofile]

---

> 이 프로젝트는 실제 회계실무와 감사업무에 활용 가능한 수준의 기능을 구현하여, 
> AI 기술을 활용한 재무분석 도구의 가능성을 보여줍니다.

## 🏷 태그
`#Python` `#Flask` `#AI` `#FinTech` `#DataAnalysis` `#WebDevelopment` `#API` `#Visualization` 