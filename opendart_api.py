import requests
import json
import os
from typing import Dict, List, Optional
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

class OpenDartAPI:
    """오픈다트 API 클래스"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://opendart.fss.or.kr/api"
    
    def get_financial_data(self, corp_code: str, bsns_year: str, reprt_code: str = "11011") -> Optional[Dict]:
        """
        단일회사 주요계정 정보를 가져옵니다.
        
        Args:
            corp_code: 고유번호 (8자리)
            bsns_year: 사업연도 (4자리)
            reprt_code: 보고서 코드 (기본값: 11011 - 사업보고서)
                       11013: 1분기보고서, 11012: 반기보고서, 11014: 3분기보고서, 11011: 사업보고서
        
        Returns:
            재무데이터 딕셔너리 또는 None (오류 시)
        """
        url = f"{self.base_url}/fnlttSinglAcnt.json"
        params = {
            'crtfc_key': self.api_key,
            'corp_code': corp_code,
            'bsns_year': bsns_year,
            'reprt_code': reprt_code
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') == '000':  # 정상
                return data
            else:
                print(f"API 오류: {data.get('status')} - {data.get('message')}")
                return None
                
        except requests.RequestException as e:
            print(f"네트워크 오류: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"JSON 파싱 오류: {e}")
            return None
    
    def parse_financial_data(self, raw_data: Dict) -> Dict:
        """
        API 응답 데이터를 구조화된 형태로 파싱합니다.
        
        Args:
            raw_data: API 응답 원본 데이터
            
        Returns:
            구조화된 재무데이터
        """
        if not raw_data or 'list' not in raw_data:
            return {}
        
        financial_data = {
            'consolidated': {  # 연결재무제표 (CFS)
                'balance_sheet': {},  # 재무상태표 (BS)
                'income_statement': {}  # 손익계산서 (IS)
            },
            'separate': {  # 재무제표 (OFS)
                'balance_sheet': {},  # 재무상태표 (BS)
                'income_statement': {}  # 손익계산서 (IS)
            },
            'basic_info': {}
        }
        
        for item in raw_data['list']:
            fs_div = item.get('fs_div')  # OFS(재무제표) or CFS(연결재무제표)
            sj_div = item.get('sj_div')  # BS(재무상태표) or IS(손익계산서)
            account_nm = item.get('account_nm')  # 계정명
            
            # 기본 정보 저장
            if not financial_data['basic_info']:
                financial_data['basic_info'] = {
                    'corp_code': item.get('corp_code'),
                    'stock_code': item.get('stock_code'),
                    'bsns_year': item.get('bsns_year'),
                    'reprt_code': item.get('reprt_code'),
                    'currency': item.get('currency', 'KRW')
                }
            
            # 금액 데이터 정리
            account_data = {
                'current_period': {
                    'name': item.get('thstrm_nm'),
                    'date': item.get('thstrm_dt'),
                    'amount': self._parse_amount(item.get('thstrm_amount'))
                },
                'previous_period': {
                    'name': item.get('frmtrm_nm'),
                    'date': item.get('frmtrm_dt'),
                    'amount': self._parse_amount(item.get('frmtrm_amount'))
                },
                'before_previous_period': {
                    'name': item.get('bfefrmtrm_nm'),
                    'date': item.get('bfefrmtrm_dt'),
                    'amount': self._parse_amount(item.get('bfefrmtrm_amount'))
                }
            }
            
            # 데이터 분류
            if fs_div == 'CFS':  # 연결재무제표
                if sj_div == 'BS':  # 재무상태표
                    financial_data['consolidated']['balance_sheet'][account_nm] = account_data
                elif sj_div == 'IS':  # 손익계산서
                    financial_data['consolidated']['income_statement'][account_nm] = account_data
            elif fs_div == 'OFS':  # 재무제표
                if sj_div == 'BS':  # 재무상태표
                    financial_data['separate']['balance_sheet'][account_nm] = account_data
                elif sj_div == 'IS':  # 손익계산서
                    financial_data['separate']['income_statement'][account_nm] = account_data
        
        return financial_data
    
    def _parse_amount(self, amount_str: str) -> int:
        """금액 문자열을 정수로 변환합니다."""
        if not amount_str:
            return 0
        
        try:
            # 쉼표 제거 후 정수 변환
            return int(amount_str.replace(',', ''))
        except ValueError:
            return 0
    
    def get_full_financial_statements(self, corp_code: str, bsns_year: str, reprt_code: str = "11011", fs_div: str = "CFS") -> Optional[Dict]:
        """
        단일회사 전체 재무제표 정보를 가져옵니다.
        
        Args:
            corp_code: 고유번호 (8자리)
            bsns_year: 사업연도 (4자리)
            reprt_code: 보고서 코드 (기본값: 11011 - 사업보고서)
            fs_div: 개별/연결구분 (OFS:재무제표, CFS:연결재무제표)
        
        Returns:
            전체 재무제표 데이터 딕셔너리 또는 None (오류 시)
        """
        url = f"{self.base_url}/fnlttSinglAcntAll.json"
        params = {
            'crtfc_key': self.api_key,
            'corp_code': corp_code,
            'bsns_year': bsns_year,
            'reprt_code': reprt_code,
            'fs_div': fs_div
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') == '000':  # 정상
                return data
            else:
                print(f"전체 재무제표 API 오류: {data.get('status')} - {data.get('message')}")
                return None
                
        except requests.RequestException as e:
            print(f"전체 재무제표 네트워크 오류: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"전체 재무제표 JSON 파싱 오류: {e}")
            return None

    def parse_full_financial_statements(self, raw_data: Dict) -> Dict:
        """
        전체 재무제표 API 응답 데이터를 구조화된 형태로 파싱합니다.
        
        Args:
            raw_data: API 응답 원본 데이터
            
        Returns:
            구조화된 전체 재무제표 데이터
        """
        if not raw_data or 'list' not in raw_data:
            return {}
        
        financial_statements = {
            'BS': {},   # 재무상태표
            'IS': {},   # 손익계산서  
            'CIS': {},  # 포괄손익계산서
            'CF': {},   # 현금흐름표
            'SCE': {},  # 자본변동표
            'basic_info': {}
        }
        
        for item in raw_data['list']:
            sj_div = item.get('sj_div')  # 재무제표구분
            account_nm = item.get('account_nm')  # 계정명
            
            # 기본 정보 저장 (첫 번째 항목에서만)
            if not financial_statements['basic_info']:
                financial_statements['basic_info'] = {
                    'corp_code': item.get('corp_code'),
                    'bsns_year': item.get('bsns_year'),
                    'reprt_code': item.get('reprt_code'),
                    'currency': item.get('currency', 'KRW')
                }
            
            # 계정 데이터 정리
            account_data = {
                'account_id': item.get('account_id'),
                'account_detail': item.get('account_detail'),
                'current_period': {
                    'name': item.get('thstrm_nm'),
                    'amount': self._parse_amount(item.get('thstrm_amount')),
                    'add_amount': self._parse_amount(item.get('thstrm_add_amount'))
                },
                'previous_period': {
                    'name': item.get('frmtrm_nm'),
                    'amount': self._parse_amount(item.get('frmtrm_amount')),
                    'q_name': item.get('frmtrm_q_nm'),
                    'q_amount': self._parse_amount(item.get('frmtrm_q_amount')),
                    'add_amount': self._parse_amount(item.get('frmtrm_add_amount'))
                },
                'before_previous_period': {
                    'name': item.get('bfefrmtrm_nm'),
                    'amount': self._parse_amount(item.get('bfefrmtrm_amount'))
                },
                'ord': item.get('ord'),  # 정렬순서
            }
            
            # 재무제표별로 분류
            if sj_div in financial_statements:
                financial_statements[sj_div][account_nm] = account_data
        
        return financial_statements

    def get_key_metrics(self, financial_data: Dict, use_consolidated: bool = True) -> Dict:
        """
        주요 재무지표를 계산합니다.
        
        Args:
            financial_data: 파싱된 재무데이터
            use_consolidated: 연결재무제표 사용 여부 (True: 연결, False: 개별)
            
        Returns:
            주요 재무지표 딕셔너리 (현재 + 전년도)
        """
        data_type = 'consolidated' if use_consolidated else 'separate'
        bs = financial_data.get(data_type, {}).get('balance_sheet', {})
        is_data = financial_data.get(data_type, {}).get('income_statement', {})
        
        # 현재 기간 데이터 추출
        current_assets = bs.get('유동자산', {}).get('current_period', {}).get('amount', 0)
        total_assets = bs.get('자산총계', {}).get('current_period', {}).get('amount', 0)
        current_liabilities = bs.get('유동부채', {}).get('current_period', {}).get('amount', 0)
        total_liabilities = bs.get('부채총계', {}).get('current_period', {}).get('amount', 0)
        total_equity = bs.get('자본총계', {}).get('current_period', {}).get('amount', 0)
        
        revenue = is_data.get('매출액', {}).get('current_period', {}).get('amount', 0)
        operating_profit = is_data.get('영업이익', {}).get('current_period', {}).get('amount', 0)
        net_income = is_data.get('당기순이익', {}).get('current_period', {}).get('amount', 0)
        
        # 전년 기간 데이터 추출
        prev_current_assets = bs.get('유동자산', {}).get('previous_period', {}).get('amount', 0)
        prev_total_assets = bs.get('자산총계', {}).get('previous_period', {}).get('amount', 0)
        prev_current_liabilities = bs.get('유동부채', {}).get('previous_period', {}).get('amount', 0)
        prev_total_liabilities = bs.get('부채총계', {}).get('previous_period', {}).get('amount', 0)
        prev_total_equity = bs.get('자본총계', {}).get('previous_period', {}).get('amount', 0)
        
        prev_revenue = is_data.get('매출액', {}).get('previous_period', {}).get('amount', 0)
        prev_operating_profit = is_data.get('영업이익', {}).get('previous_period', {}).get('amount', 0)
        prev_net_income = is_data.get('당기순이익', {}).get('previous_period', {}).get('amount', 0)
        
        # 현재 기간 주요 비율 계산
        current_ratio = round((current_assets / current_liabilities * 100), 2) if current_liabilities > 0 else 0
        debt_ratio = round((total_liabilities / total_assets * 100), 2) if total_assets > 0 else 0
        equity_ratio = round((total_equity / total_assets * 100), 2) if total_assets > 0 else 0
        operating_margin = round((operating_profit / revenue * 100), 2) if revenue > 0 else 0
        net_margin = round((net_income / revenue * 100), 2) if revenue > 0 else 0
        roa = round((net_income / total_assets * 100), 2) if total_assets > 0 else 0
        roe = round((net_income / total_equity * 100), 2) if total_equity > 0 else 0
        
        # 전년 기간 주요 비율 계산
        prev_current_ratio = round((prev_current_assets / prev_current_liabilities * 100), 2) if prev_current_liabilities > 0 else 0
        prev_debt_ratio = round((prev_total_liabilities / prev_total_assets * 100), 2) if prev_total_assets > 0 else 0
        prev_equity_ratio = round((prev_total_equity / prev_total_assets * 100), 2) if prev_total_assets > 0 else 0
        prev_operating_margin = round((prev_operating_profit / prev_revenue * 100), 2) if prev_revenue > 0 else 0
        prev_net_margin = round((prev_net_income / prev_revenue * 100), 2) if prev_revenue > 0 else 0
        prev_roa = round((prev_net_income / prev_total_assets * 100), 2) if prev_total_assets > 0 else 0
        prev_roe = round((prev_net_income / prev_total_equity * 100), 2) if prev_total_equity > 0 else 0
        
        metrics = {
            # 현재 기간 지표
            'current_ratio': current_ratio,
            'debt_ratio': debt_ratio,
            'equity_ratio': equity_ratio,
            'operating_margin': operating_margin,
            'net_margin': net_margin,
            'roa': roa,
            'roe': roe,
            # 전년 기간 지표 (추이 계산용)
            'current_ratio_previous': prev_current_ratio,
            'debt_ratio_previous': prev_debt_ratio,
            'equity_ratio_previous': prev_equity_ratio,
            'operating_margin_previous': prev_operating_margin,
            'net_margin_previous': prev_net_margin,
            'roa_previous': prev_roa,
            'roe_previous': prev_roe
        }
        
        return metrics

def test_api():
    """API 테스트 함수"""
    api = OpenDartAPI('353baf6666b17ba40389ce5967bd308e77bb579f')
    
    # 삼성전자 2018년 사업보고서 데이터 조회
    raw_data = api.get_financial_data('00126380', '2018', '11011')
    
    if raw_data:
        financial_data = api.parse_financial_data(raw_data)
        metrics = api.get_key_metrics(financial_data)
        
        print("=== 재무데이터 테스트 ===")
        print(f"회사 코드: {financial_data['basic_info']['corp_code']}")
        print(f"주식 코드: {financial_data['basic_info']['stock_code']}")
        print(f"사업연도: {financial_data['basic_info']['bsns_year']}")
        
        print("\n=== 주요 재무지표 ===")
        for key, value in metrics.items():
            print(f"{key}: {value}")
        
        return True
    else:
        print("API 테스트 실패")
        return False

if __name__ == "__main__":
    test_api() 