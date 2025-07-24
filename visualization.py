import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import io
import base64
import os
import requests
from typing import Dict, List, Tuple

def setup_korean_font():
    """한글 폰트를 설정합니다."""
    try:
        # 간단한 방법: 폰트 캐시 재생성 및 설정
        plt.rcParams['font.family'] = ['DejaVu Sans', 'Liberation Sans', 'Arial Unicode MS', 'sans-serif']
        plt.rcParams['axes.unicode_minus'] = False
        
        # 폰트 캐시 재생성
        try:
            fm._get_fontconfig_fonts.cache_clear()
            fm.fontManager.__init__()
        except:
            pass
            
        # 시스템에서 사용 가능한 한글 폰트 찾기
        korean_fonts = ['Noto Sans CJK KR', 'Noto Sans KR', 'NanumGothic', 'Malgun Gothic', 'UnDotum']
        available_fonts = [f.name for f in fm.fontManager.ttflist]
        
        for font in korean_fonts:
            if font in available_fonts:
                plt.rcParams['font.family'] = [font] + plt.rcParams['font.family']
                print(f"한글 폰트 설정 완료: {font}")
                break
        else:
            print("한글 폰트를 찾을 수 없어 기본 폰트를 사용합니다.")
            # 유니코드 지원 폰트로 설정
            plt.rcParams['font.family'] = ['DejaVu Sans', 'Liberation Sans', 'sans-serif']
        
        print(f"현재 폰트 설정: {plt.rcParams['font.family']}")
        
    except Exception as e:
        print(f"폰트 설정 중 오류: {e}")
        # 안전한 기본 설정
        plt.rcParams['font.family'] = ['DejaVu Sans', 'sans-serif']
        plt.rcParams['axes.unicode_minus'] = False

# 한글 폰트 설정 실행
setup_korean_font()

def apply_korean_font(text_obj, fontsize=None):
    """텍스트 객체에 한글 폰트를 적용합니다."""
    try:
        if fontsize:
            text_obj.set_fontsize(fontsize)
        # 폰트 속성 직접 설정
        text_obj.set_fontfamily('DejaVu Sans')
    except:
        pass
    return text_obj

# 한글-영어 번역 사전 (차트 표시용)
CHART_LABELS = {
    '재무상태표 구성': 'Balance Sheet Composition',
    '자산': 'Assets',
    '부채와 자본': 'Liabilities & Equity', 
    '유동자산': 'Current Assets',
    '비유동자산': 'Non-current Assets',
    '유동부채': 'Current Liabilities',
    '비유동부채': 'Non-current Liabilities',
    '자본총계': 'Total Equity',
    '손익계산서 3개년 비교': 'Income Statement 3-Year Comparison',
    '매출액': 'Revenue',
    '영업이익': 'Operating Income',
    '당기순이익': 'Net Income',
    '재무비율 추이 분석': 'Financial Ratio Trend Analysis',
    '유동비율': 'Current Ratio',
    '부채비율': 'Debt Ratio',
    '자기자본비율': 'Equity Ratio',
    '영업이익률': 'Operating Margin',
    '순이익률': 'Net Margin',
    'ROA': 'ROA',
    'ROE': 'ROE',
    '년도': 'Year',
    '비율': 'Ratio',
    '금액 (조원)': 'Amount (Trillion KRW)',
    '백분율 (%)': 'Percentage (%)',
    '데이터가 없습니다': 'No Data Available'
}

def get_chart_label(korean_text):
    """한글 텍스트를 영어 차트 라벨로 변환합니다."""
    return CHART_LABELS.get(korean_text, korean_text)

class FinancialVisualizer:
    """재무데이터 시각화 클래스"""
    
    def __init__(self):
        self.colors = {
            'primary': '#667eea',
            'secondary': '#764ba2',
            'success': '#28a745',
            'danger': '#dc3545',
            'warning': '#ffc107',
            'info': '#17a2b8',
            'light': '#f8f9fa',
            'dark': '#343a40'
        }
    
    def create_balance_sheet_chart(self, financial_data: Dict, use_consolidated: bool = True) -> str:
        """
        재무상태표 차트를 생성합니다.
        
        Args:
            financial_data: 파싱된 재무데이터
            use_consolidated: 연결재무제표 사용 여부
            
        Returns:
            base64 인코딩된 이미지 문자열
        """
        data_type = 'consolidated' if use_consolidated else 'separate'
        bs = financial_data.get(data_type, {}).get('balance_sheet', {})
        
        if not bs:
            return self._create_no_data_chart("재무상태표 데이터가 없습니다.")
        
        # 주요 항목 추출 (조원 단위)
        assets_data = {
            '유동자산': bs.get('유동자산', {}).get('current_period', {}).get('amount', 0) / 1000000000000,
            '비유동자산': bs.get('비유동자산', {}).get('current_period', {}).get('amount', 0) / 1000000000000
        }
        
        liabilities_data = {
            '유동부채': bs.get('유동부채', {}).get('current_period', {}).get('amount', 0) / 1000000000000,
            '비유동부채': bs.get('비유동부채', {}).get('current_period', {}).get('amount', 0) / 1000000000000,
            '자본총계': bs.get('자본총계', {}).get('current_period', {}).get('amount', 0) / 1000000000000
        }
        
        # 차트 생성 - 박스형 적층 막대 차트
        fig, ax = plt.subplots(1, 1, figsize=(12, 8))
        fig.suptitle(get_chart_label('재무상태표 구성'), fontsize=16, fontweight='bold')
        
        # 데이터 준비
        categories = [get_chart_label('자산'), get_chart_label('부채와 자본')]
        
        # 자산 쌓기
        assets_current = assets_data['유동자산']
        assets_non_current = assets_data['비유동자산']
        
        # 부채와 자본 쌓기
        liabilities_current = liabilities_data['유동부채']
        liabilities_non_current = liabilities_data['비유동부채']
        equity = liabilities_data['자본총계']
        
        # 막대 위치 - 박스들을 붙여서 배치
        bar_width = 0.4
        x_pos = [0.2, 0.6]  # 박스들을 가깝게 배치
        
        # 총 금액 계산 (퍼센트 계산용)
        total_assets = assets_current + assets_non_current
        total_liab_equity = liabilities_current + liabilities_non_current + equity
        
        # 자산 측 (왼쪽) - 비유동자산을 먼저, 유동자산을 위에
        if assets_non_current > 0:
            bar1 = ax.bar(x_pos[0], assets_non_current, bar_width, 
                         color=self.colors['secondary'], alpha=0.8)
        if assets_current > 0:
            bar2 = ax.bar(x_pos[0], assets_current, bar_width, 
                         bottom=assets_non_current, 
                         color=self.colors['primary'], alpha=0.8)
        
        # 부채와 자본 측 (오른쪽) - 자본을 먼저, 비유동부채, 유동부채 순으로 위에
        if equity > 0:
            bar3 = ax.bar(x_pos[1], equity, bar_width, 
                         color=self.colors['success'], alpha=0.8)
        if liabilities_non_current > 0:
            bar4 = ax.bar(x_pos[1], liabilities_non_current, bar_width, 
                         bottom=equity, 
                         color=self.colors['warning'], alpha=0.8)
        if liabilities_current > 0:
            bar5 = ax.bar(x_pos[1], liabilities_current, bar_width, 
                         bottom=equity + liabilities_non_current, 
                         color=self.colors['danger'], alpha=0.8)
        
        # 축 설정
        ax.set_xticks(x_pos)
        ax.set_xticklabels(categories, fontsize=14, fontweight='bold')
        ax.set_ylabel('금액 (조원)', fontsize=12, fontweight='bold')
        ax.grid(axis='y', alpha=0.3)
        
        # 각 구간별 값 표시 (계정명 + 금액 + 퍼센트)
        def add_value_labels(bar_container, values, bottom_values, total_value, account_names):
            for bar, value, bottom, account_name in zip(bar_container, values, bottom_values, account_names):
                if value > 0:
                    height = value / 2 + bottom
                    percentage = (value / total_value) * 100 if total_value > 0 else 0
                    ax.annotate(f'{account_name}\n{value:.1f}조원\n({percentage:.1f}%)',
                               xy=(bar.get_x() + bar.get_width() / 2, height),
                               ha='center', va='center',
                               fontsize=9, fontweight='bold',
                               color='white' if value > 10 else 'black')
        
        # 값 표시
        # 비유동자산을 먼저 표시 (아래)
        if assets_non_current > 0:
            add_value_labels([ax.patches[0]], [assets_non_current], [0], total_assets, ['비유동자산'])
        # 유동자산 표시 (위)
        if assets_current > 0:
            add_value_labels([ax.patches[1]], [assets_current], [assets_non_current], total_assets, ['유동자산'])
        
        patch_idx = 2 if assets_non_current > 0 else 1 if assets_current > 0 else 0
        
        # 자본을 먼저 표시 (아래)
        if equity > 0:
            add_value_labels([ax.patches[patch_idx]], [equity], [0], total_liab_equity, ['자본총계'])
            patch_idx += 1
        # 비유동부채 표시 (중간)
        if liabilities_non_current > 0:
            add_value_labels([ax.patches[patch_idx]], [liabilities_non_current], [equity], total_liab_equity, ['비유동부채'])
            patch_idx += 1
        # 유동부채 표시 (위)
        if liabilities_current > 0:
            add_value_labels([ax.patches[patch_idx]], [liabilities_current], [equity + liabilities_non_current], total_liab_equity, ['유동부채'])
        
        # 총계 표시 (이미 위에서 계산됨)
        
        # 상단에 총계 표시
        if total_assets > 0:
            ax.text(x_pos[0], total_assets + max(total_assets, total_liab_equity) * 0.02, 
                   f'총 {total_assets:.1f}조원', ha='center', va='bottom', 
                   fontsize=12, fontweight='bold', color=self.colors['dark'])
        
        if total_liab_equity > 0:
            ax.text(x_pos[1], total_liab_equity + max(total_assets, total_liab_equity) * 0.02, 
                   f'총 {total_liab_equity:.1f}조원', ha='center', va='bottom', 
                   fontsize=12, fontweight='bold', color=self.colors['dark'])
        
        # y축 상한 설정
        max_value = max(total_assets, total_liab_equity)
        ax.set_ylim(0, max_value * 1.15)
        
        plt.tight_layout()
        return self._save_chart_as_base64(fig)
    
    def create_income_statement_chart(self, financial_data: Dict, use_consolidated: bool = True) -> str:
        """
        손익계산서 차트를 생성합니다.
        
        Args:
            financial_data: 파싱된 재무데이터
            use_consolidated: 연결재무제표 사용 여부
            
        Returns:
            base64 인코딩된 이미지 문자열
        """
        data_type = 'consolidated' if use_consolidated else 'separate'
        is_data = financial_data.get(data_type, {}).get('income_statement', {})
        
        if not is_data:
            return self._create_no_data_chart("손익계산서 데이터가 없습니다.")
        
        # 3개년 데이터 추출
        categories = ['매출액', '영업이익', '당기순이익']
        current_values = []
        previous_values = []
        before_previous_values = []
        
        for category in categories:
            current_values.append(is_data.get(category, {}).get('current_period', {}).get('amount', 0) / 1000000000000)  # 조원 단위
            previous_values.append(is_data.get(category, {}).get('previous_period', {}).get('amount', 0) / 1000000000000)
            before_previous_values.append(is_data.get(category, {}).get('before_previous_period', {}).get('amount', 0) / 1000000000000)
        
        # 연도 정보 추출 및 실제 연도로 변환
        current_year_name = is_data.get('매출액', {}).get('current_period', {}).get('name', '당기')
        previous_year_name = is_data.get('매출액', {}).get('previous_period', {}).get('name', '전기')
        before_previous_year_name = is_data.get('매출액', {}).get('before_previous_period', {}).get('name', '전전기')
        
        # 기본 정보에서 사업연도 추출
        base_year = int(financial_data.get('basic_info', {}).get('bsns_year', '2022'))
        current_year = f'{base_year}년'
        previous_year = f'{base_year-1}년'
        before_previous_year = f'{base_year-2}년'
        
        # 연도별로 데이터 재구성
        years = [before_previous_year, previous_year, current_year]
        year_data = {
            before_previous_year: before_previous_values,
            previous_year: previous_values,
            current_year: current_values
        }
        
        # 이익률 계산 (매출액이 0이 아닌 경우만)
        operating_margin_values = []
        net_margin_values = []
        
        for year in years:
            revenue = year_data[year][0]  # 매출액
            operating_profit = year_data[year][1]  # 영업이익
            net_profit = year_data[year][2]  # 당기순이익
            
            if revenue > 0:
                operating_margin = (operating_profit / revenue) * 100
                net_margin = (net_profit / revenue) * 100
            else:
                operating_margin = 0
                net_margin = 0
                
            operating_margin_values.append(operating_margin)
            net_margin_values.append(net_margin)
        
        # 복합 차트 생성 - 막대차트 + 꺾은선차트
        fig, ax1 = plt.subplots(figsize=(14, 8))
        
        x = np.arange(len(years))
        width = 0.25
        
        # 막대 차트 (왼쪽 y축)
        bars1 = ax1.bar(x - width, [year_data[year][0] for year in years], width, 
                       label=categories[0], color=self.colors['primary'], alpha=0.8)
        bars2 = ax1.bar(x, [year_data[year][1] for year in years], width, 
                       label=categories[1], color=self.colors['warning'], alpha=0.8)
        bars3 = ax1.bar(x + width, [year_data[year][2] for year in years], width, 
                       label=categories[2], color=self.colors['success'], alpha=0.8)
        
        ax1.set_xlabel('연도', fontsize=12, fontweight='bold')
        ax1.set_ylabel('금액 (조원)', fontsize=12, fontweight='bold')
        ax1.set_title('손익계산서 주요 항목 및 이익률 (3개년 비교)', fontsize=16, fontweight='bold')
        ax1.set_xticks(x)
        ax1.set_xticklabels(years)
        ax1.grid(axis='y', alpha=0.3)
        
        # 두 번째 y축 생성 (오른쪽)
        ax2 = ax1.twinx()
        
        # 꺾은선 차트 (오른쪽 y축) - 이익률 (막대차트와 동일한 색상 사용)
        line1 = ax2.plot(x, operating_margin_values, marker='o', linewidth=3, markersize=8,
                        color=self.colors['warning'], label='영업이익률', linestyle='-')
        line2 = ax2.plot(x, net_margin_values, marker='s', linewidth=3, markersize=8,
                        color=self.colors['success'], label='당기순이익률', linestyle='-')
        
        ax2.set_ylabel('이익률 (%)', fontsize=12, fontweight='bold')
        ax2.set_ylim(0, max(max(operating_margin_values), max(net_margin_values)) * 1.2 if max(operating_margin_values) > 0 else 10)
        
        # 범례 통합
        bars_legend = ax1.legend(loc='upper left', bbox_to_anchor=(0, 1))
        lines_legend = ax2.legend(loc='upper right', bbox_to_anchor=(1, 1))
        
        # 막대 차트 값 표시
        for bars in [bars1, bars2, bars3]:
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    ax1.annotate(f'{height:.1f}',
                               xy=(bar.get_x() + bar.get_width() / 2, height),
                               xytext=(0, 3),
                               textcoords="offset points",
                               ha='center', va='bottom',
                               fontsize=9)
        
        # 꺾은선 차트 값 표시
        for i, (op_margin, net_margin) in enumerate(zip(operating_margin_values, net_margin_values)):
            if op_margin > 0:
                ax2.annotate(f'{op_margin:.1f}%',
                           xy=(i, op_margin),
                           xytext=(5, 5),
                           textcoords="offset points",
                           ha='left', va='bottom',
                           fontsize=9, color=self.colors['warning'])
            if net_margin > 0:
                ax2.annotate(f'{net_margin:.1f}%',
                           xy=(i, net_margin),
                           xytext=(5, -15),
                           textcoords="offset points",
                           ha='left', va='top',
                           fontsize=9, color=self.colors['success'])
        
        plt.tight_layout()
        return self._save_chart_as_base64(fig)
    
    def create_financial_ratios_chart(self, metrics: Dict) -> str:
        """
        재무비율 차트를 생성합니다.
        
        Args:
            metrics: 계산된 재무지표
            
        Returns:
            base64 인코딩된 이미지 문자열
        """
        if not metrics:
            return self._create_no_data_chart("재무비율 데이터가 없습니다.")
        
        # 비율 데이터 정리
        ratio_data = {
            '유동비율': metrics.get('current_ratio', 0),
            '부채비율': metrics.get('debt_ratio', 0),
            '자기자본비율': metrics.get('equity_ratio', 0),
            '영업이익률': metrics.get('operating_margin', 0),
            '순이익률': metrics.get('net_margin', 0),
            'ROA': metrics.get('roa', 0),
            'ROE': metrics.get('roe', 0)
        }
        
        # 레이더 차트 생성
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
        
        categories = list(ratio_data.keys())
        values = list(ratio_data.values())
        
        # 각도 계산
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        values += values[:1]  # 첫 번째 값을 마지막에 추가하여 원형 완성
        angles += angles[:1]
        
        # 차트 그리기
        ax.plot(angles, values, 'o-', linewidth=2, color=self.colors['primary'])
        ax.fill(angles, values, alpha=0.25, color=self.colors['primary'])
        
        # 카테고리 라벨 설정
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories)
        ax.set_ylim(0, max(max(values), 100))
        
        # 값 표시
        for angle, value, category in zip(angles[:-1], values[:-1], categories):
            ax.annotate(f'{value:.1f}%', 
                       xy=(angle, value), 
                       xytext=(5, 5), 
                       textcoords='offset points',
                       fontsize=10, 
                       fontweight='bold')
        
        ax.set_title('주요 재무비율', fontsize=16, fontweight='bold', pad=20)
        ax.grid(True)
        
        plt.tight_layout()
        return self._save_chart_as_base64(fig)
    
    def create_trend_analysis_chart(self, financial_data: Dict, use_consolidated: bool = True) -> str:
        """
        주요 재무비율 트렌드 분석 차트를 생성합니다.
        
        Args:
            financial_data: 파싱된 재무데이터
            use_consolidated: 연결재무제표 사용 여부
            
        Returns:
            base64 인코딩된 이미지 문자열
        """
        data_type = 'consolidated' if use_consolidated else 'separate'
        bs = financial_data.get(data_type, {}).get('balance_sheet', {})
        is_data = financial_data.get(data_type, {}).get('income_statement', {})
        
        if not bs or not is_data:
            return self._create_no_data_chart("재무비율 트렌드 분석을 위한 데이터가 부족합니다.")
        
        # 기본 정보에서 사업연도 추출하여 실제 연도로 변환
        base_year = int(financial_data.get('basic_info', {}).get('bsns_year', '2022'))
        years = [f'{base_year-2}년', f'{base_year-1}년', f'{base_year}년']
        
        # 3개년 재무비율 계산
        roe_values = []
        roa_values = []
        debt_ratio_values = []
        
        periods = ['before_previous_period', 'previous_period', 'current_period']
        
        for period in periods:
            # 각 기간별 데이터 추출
            total_assets = bs.get('자산총계', {}).get(period, {}).get('amount', 0)
            total_equity = bs.get('자본총계', {}).get(period, {}).get('amount', 0)
            total_liabilities = bs.get('부채총계', {}).get(period, {}).get('amount', 0)
            net_income = is_data.get('당기순이익', {}).get(period, {}).get('amount', 0)
            
            # ROE 계산 (당기순이익 / 자기자본 * 100)
            if total_equity > 0:
                roe = (net_income / total_equity) * 100
            else:
                roe = 0
            roe_values.append(roe)
            
            # ROA 계산 (당기순이익 / 총자산 * 100)
            if total_assets > 0:
                roa = (net_income / total_assets) * 100
            else:
                roa = 0
            roa_values.append(roa)
            
            # 부채비율 계산 (부채총계 / 자기자본 * 100)
            if total_equity > 0:
                debt_ratio = (total_liabilities / total_equity) * 100
            else:
                debt_ratio = 0
            debt_ratio_values.append(debt_ratio)
        
        # 복합 차트 생성 (ROE, ROA는 왼쪽 축, 부채비율은 오른쪽 축)
        fig, ax1 = plt.subplots(figsize=(12, 8))
        
        x = np.arange(len(years))
        
        # 왼쪽 y축 - ROE, ROA
        line1 = ax1.plot(x, roe_values, marker='o', linewidth=3, markersize=8,
                        color=self.colors['success'], label='ROE', linestyle='-')
        line2 = ax1.plot(x, roa_values, marker='s', linewidth=3, markersize=8,
                        color=self.colors['primary'], label='ROA', linestyle='-')
        
        ax1.set_xlabel('연도', fontsize=12, fontweight='bold')
        ax1.set_ylabel('수익성 비율 (%)', fontsize=12, fontweight='bold')
        ax1.set_title('주요 재무비율 추이 분석', fontsize=16, fontweight='bold')
        ax1.set_xticks(x)
        ax1.set_xticklabels(years)
        ax1.grid(True, alpha=0.3)
        
        # 오른쪽 y축 - 부채비율
        ax2 = ax1.twinx()
        line3 = ax2.plot(x, debt_ratio_values, marker='^', linewidth=3, markersize=8,
                        color=self.colors['danger'], label='부채비율', linestyle='-')
        
        ax2.set_ylabel('부채비율 (%)', fontsize=12, fontweight='bold')
        
        # 범례 통합
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', bbox_to_anchor=(0, 1))
        
        # 값 표시
        for i, (roe, roa, debt) in enumerate(zip(roe_values, roa_values, debt_ratio_values)):
            if roe != 0:
                ax1.annotate(f'{roe:.1f}%',
                           xy=(i, roe),
                           xytext=(5, 10),
                           textcoords="offset points",
                           ha='left', va='bottom',
                           fontsize=9, color=self.colors['success'])
            
            if roa != 0:
                ax1.annotate(f'{roa:.1f}%',
                           xy=(i, roa),
                           xytext=(5, -15),
                           textcoords="offset points",
                           ha='left', va='top',
                           fontsize=9, color=self.colors['primary'])
            
            if debt != 0:
                ax2.annotate(f'{debt:.1f}%',
                           xy=(i, debt),
                           xytext=(-10, 5),
                           textcoords="offset points",
                           ha='right', va='bottom',
                           fontsize=9, color=self.colors['danger'])
        
        plt.tight_layout()
        return self._save_chart_as_base64(fig)
    
    def _save_chart_as_base64(self, fig) -> str:
        """차트를 base64 문자열로 변환합니다."""
        buffer = io.BytesIO()
        fig.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close(fig)
        return image_base64
    
    def _create_no_data_chart(self, message: str) -> str:
        """데이터가 없을 때 표시할 차트를 생성합니다."""
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, message, transform=ax.transAxes, 
               ha='center', va='center', fontsize=16, 
               bbox=dict(boxstyle="round,pad=0.3", facecolor=self.colors['light']))
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        return self._save_chart_as_base64(fig) 