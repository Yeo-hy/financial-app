import google.generativeai as genai
import json
import os
from typing import Dict, List, Any
import traceback
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# Gemini API 설정
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY 환경변수가 설정되지 않았습니다.")
genai.configure(api_key=GEMINI_API_KEY)

class AuditRiskAnalyzer:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def analyze_financial_risks(self, company_data: Dict, financial_metrics: Dict, full_financial_data: Dict = None) -> Dict:
        """
        재무제표 감사업무용 리스크 분석 수행
        """
        try:
            # 분석용 프롬프트 생성
            prompt = self._create_audit_risk_prompt(company_data, financial_metrics, full_financial_data)
            
            # Gemini API 호출
            response = self.model.generate_content(prompt)
            
            # 응답 파싱 및 구조화
            analysis_result = self._parse_gemini_response(response.text)
            
            return {
                'success': True,
                'analysis': analysis_result,
                'raw_response': response.text
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc()
            }
    
    def _create_audit_risk_prompt(self, company_data: Dict, financial_metrics: Dict, full_financial_data: Dict = None) -> str:
        """
        감사업무용 리스크 분석 프롬프트 생성
        """
        prompt = f"""
        당신은 경험이 풍부한 공인회계사이며, 재무제표 감사업무의 전문가입니다.
        다음 기업에 대한 감사업무 수임 후, 감사업무 개시 전 리스크 분석을 수행해야 합니다.

        **기업 정보:**
        - 회사명: {company_data.get('corp_name', 'N/A')}
        - 기업코드: {company_data.get('corp_code', 'N/A')}
        - 주식코드: {company_data.get('stock_code', 'N/A')}

        **재무비율 분석 결과:**
        - 유동비율: {financial_metrics.get('current_ratio', 0)}%
        - 부채비율: {financial_metrics.get('debt_ratio', 0)}%
        - 자기자본비율: {financial_metrics.get('equity_ratio', 0)}%
        - 영업이익률: {financial_metrics.get('operating_margin', 0)}%
        - 순이익률: {financial_metrics.get('net_margin', 0)}%
        - ROA: {financial_metrics.get('roa', 0)}%
        - ROE: {financial_metrics.get('roe', 0)}%

        {self._format_full_financial_data(full_financial_data)}

        다음 관점에서 종합적인 감사 리스크 분석을 수행하고, JSON 형태로 구조화된 보고서를 제공해주세요:

        1. **재무적 리스크 (Financial Risks)**
           - 유동성 위험
           - 수익성 위험
           - 레버리지 위험
           - 자본 구조 위험

        2. **감사 위험 요소 (Audit Risk Factors)**
           - 고유위험 (Inherent Risk)
           - 통제위험 (Control Risk)
           - 발견위험 (Detection Risk)

        3. **중요한 왜곡표시 위험 (Risk of Material Misstatement)**
           - 수익 인식 관련 위험
           - 자산 평가 위험
           - 부채 누락 위험
           - 공정가치 측정 위험

        4. **권고사항 (Recommendations)**
           - 추가 감사절차 필요 영역
           - 집중 검토 대상 계정과목
           - 리스크 완화 방안

        5. **전체 리스크 등급**
           - 높음/중간/낮음으로 분류
           - 근거와 함께 제시

        응답은 반드시 다음 JSON 구조를 따라주세요:

        {{
            "overall_risk_level": "높음/중간/낮음",
            "overall_assessment": "전체적인 리스크 평가 요약",
            "financial_risks": {{
                "liquidity_risk": {{"level": "높음/중간/낮음", "description": "설명", "indicators": ["지표1", "지표2"]}},
                "profitability_risk": {{"level": "높음/중간/낮음", "description": "설명", "indicators": ["지표1", "지표2"]}},
                "leverage_risk": {{"level": "높음/중간/낮음", "description": "설명", "indicators": ["지표1", "지표2"]}},
                "capital_structure_risk": {{"level": "높음/중간/낮음", "description": "설명", "indicators": ["지표1", "지표2"]}}
            }},
            "audit_risk_factors": {{
                "inherent_risk": {{"level": "높음/중간/낮음", "description": "설명", "factors": ["요인1", "요인2"]}},
                "control_risk": {{"level": "높음/중간/낮음", "description": "설명", "factors": ["요인1", "요인2"]}},
                "detection_risk": {{"level": "높음/중간/낮음", "description": "설명", "factors": ["요인1", "요인2"]}}
            }},
            "material_misstatement_risks": [
                {{"area": "수익인식", "risk_level": "높음/중간/낮음", "description": "설명", "audit_procedures": ["절차1", "절차2"]}},
                {{"area": "자산평가", "risk_level": "높음/중간/낮음", "description": "설명", "audit_procedures": ["절차1", "절차2"]}},
                {{"area": "부채", "risk_level": "높음/중간/낮음", "description": "설명", "audit_procedures": ["절차1", "절차2"]}}
            ],
            "recommendations": {{
                "priority_areas": ["우선순위 영역1", "우선순위 영역2"],
                "additional_procedures": ["추가 절차1", "추가 절차2"],
                "focus_accounts": ["계정과목1", "계정과목2"],
                "risk_mitigation": ["완화방안1", "완화방안2"]
            }},
            "key_insights": [
                "핵심 인사이트 1",
                "핵심 인사이트 2",
                "핵심 인사이트 3"
            ]
        }}

        한국 회계기준과 감사기준을 기반으로 전문적이고 실무적인 분석을 제공해주세요.
        """
        
        return prompt
    
    def _format_full_financial_data(self, full_financial_data: Dict) -> str:
        """
        전체 재무제표 데이터를 프롬프트용으로 포맷팅
        """
        if not full_financial_data:
            return "**전체 재무제표 데이터:** 데이터가 제공되지 않았습니다."
        
        formatted_text = "**상세 재무제표 정보:**\n"
        
        # 재무상태표 (BS) 주요 항목
        bs_data = full_financial_data.get('BS', {})
        if bs_data:
            formatted_text += "\n📊 **재무상태표 주요 항목:**\n"
            key_bs_accounts = ['자산총계', '유동자산', '비유동자산', '부채총계', '유동부채', '비유동부채', '자본총계', '자기자본']
            for account in key_bs_accounts:
                if account in bs_data:
                    current_amount = bs_data[account].get('current_period', {}).get('amount', 0)
                    previous_amount = bs_data[account].get('previous_period', {}).get('amount', 0)
                    formatted_text += f"  - {account}: 당기 {current_amount:,}원, 전기 {previous_amount:,}원\n"
        
        # 손익계산서 (IS) 주요 항목  
        is_data = full_financial_data.get('IS', {})
        if is_data:
            formatted_text += "\n📈 **손익계산서 주요 항목:**\n"
            key_is_accounts = ['수익(매출액)', '매출액', '매출총이익', '영업이익', '법인세비용차감전순이익', '당기순이익']
            for account in key_is_accounts:
                if account in is_data:
                    current_amount = is_data[account].get('current_period', {}).get('amount', 0)
                    previous_amount = is_data[account].get('previous_period', {}).get('amount', 0)
                    formatted_text += f"  - {account}: 당기 {current_amount:,}원, 전기 {previous_amount:,}원\n"
        
        # 현금흐름표 (CF) 주요 항목
        cf_data = full_financial_data.get('CF', {})
        if cf_data:
            formatted_text += "\n💰 **현금흐름표 주요 항목:**\n"
            key_cf_accounts = ['영업활동현금흐름', '투자활동현금흐름', '재무활동현금흐름', '현금및현금성자산의증가']
            for account in key_cf_accounts:
                if account in cf_data:
                    current_amount = cf_data[account].get('current_period', {}).get('amount', 0)
                    previous_amount = cf_data[account].get('previous_period', {}).get('amount', 0)
                    formatted_text += f"  - {account}: 당기 {current_amount:,}원, 전기 {previous_amount:,}원\n"
        
        # 계정과목 수 정보
        total_accounts = len(bs_data) + len(is_data) + len(cf_data) + len(full_financial_data.get('CIS', {})) + len(full_financial_data.get('SCE', {}))
        formatted_text += f"\n📋 **전체 계정과목 수:** {total_accounts}개\n"
        
        return formatted_text
    
    def _parse_gemini_response(self, response_text: str) -> Dict:
        """
        Gemini 응답을 파싱하여 구조화된 데이터로 변환
        """
        try:
            # JSON 블록 추출
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = response_text[start_idx:end_idx]
                return json.loads(json_str)
            else:
                # JSON 형태가 아닌 경우 기본 구조로 파싱
                return self._create_fallback_structure(response_text)
                
        except json.JSONDecodeError:
            return self._create_fallback_structure(response_text)
    
    def _create_fallback_structure(self, response_text: str) -> Dict:
        """
        JSON 파싱 실패 시 대체 구조 생성
        """
        return {
            "overall_risk_level": "분석 필요",
            "overall_assessment": response_text[:500] + "..." if len(response_text) > 500 else response_text,
            "financial_risks": {
                "liquidity_risk": {"level": "분석 필요", "description": "상세 분석이 필요합니다.", "indicators": []},
                "profitability_risk": {"level": "분석 필요", "description": "상세 분석이 필요합니다.", "indicators": []},
                "leverage_risk": {"level": "분석 필요", "description": "상세 분석이 필요합니다.", "indicators": []},
                "capital_structure_risk": {"level": "분석 필요", "description": "상세 분석이 필요합니다.", "indicators": []}
            },
            "audit_risk_factors": {
                "inherent_risk": {"level": "분석 필요", "description": "상세 분석이 필요합니다.", "factors": []},
                "control_risk": {"level": "분석 필요", "description": "상세 분석이 필요합니다.", "factors": []},
                "detection_risk": {"level": "분석 필요", "description": "상세 분석이 필요합니다.", "factors": []}
            },
            "material_misstatement_risks": [
                {"area": "수익인식", "risk_level": "분석 필요", "description": "상세 분석이 필요합니다.", "audit_procedures": []},
                {"area": "자산평가", "risk_level": "분석 필요", "description": "상세 분석이 필요합니다.", "audit_procedures": []},
                {"area": "부채", "risk_level": "분석 필요", "description": "상세 분석이 필요합니다.", "audit_procedures": []}
            ],
            "recommendations": {
                "priority_areas": [],
                "additional_procedures": [],
                "focus_accounts": [],
                "risk_mitigation": []
            },
            "key_insights": ["AI 분석 결과를 확인해주세요."],
            "raw_response": response_text
        }

def get_risk_level_color(level: str) -> str:
    """리스크 수준에 따른 색상 반환"""
    color_map = {
        '높음': '#dc3545',
        '중간': '#ffc107', 
        '낮음': '#28a745',
        '분석 필요': '#6c757d'
    }
    return color_map.get(level, '#6c757d')

def get_risk_level_icon(level: str) -> str:
    """리스크 수준에 따른 아이콘 반환"""
    icon_map = {
        '높음': '🔴',
        '중간': '🟡',
        '낮음': '🟢',
        '분석 필요': '⚪'
    }
    return icon_map.get(level, '⚪') 