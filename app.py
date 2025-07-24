from flask import Flask, render_template, request, jsonify
import sqlite3
import os
from opendart_api import OpenDartAPI
from visualization import FinancialVisualizer
from ai_analysis import AuditRiskAnalyzer
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

app = Flask(__name__)

# 오픈다트 API 초기화
OPENDART_API_KEY = os.getenv('OPENDART_API_KEY')
if not OPENDART_API_KEY:
    raise ValueError("OPENDART_API_KEY 환경변수가 설정되지 않았습니다.")

opendart_api = OpenDartAPI(OPENDART_API_KEY)
visualizer = FinancialVisualizer()
ai_analyzer = AuditRiskAnalyzer()

def init_database():
    """데이터베이스를 초기화합니다."""
    try:
        from xml_to_db import create_database, parse_xml_and_insert
        print("데이터베이스를 초기화하는 중...")
        conn = create_database()
        parse_xml_and_insert(conn)
        conn.close()
        print("데이터베이스 초기화 완료!")
    except Exception as e:
        print(f"데이터베이스 초기화 중 오류 발생: {e}")

def get_db_connection():
    """데이터베이스 연결을 반환합니다."""
    if not os.path.exists('companies.db'):
        print("데이터베이스가 없습니다. 초기화를 시도합니다...")
        init_database()
        if not os.path.exists('companies.db'):
            return None
    conn = sqlite3.connect('companies.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    """메인 페이지를 렌더링합니다."""
    return render_template('index.html')

@app.route('/search')
def search():
    """회사명으로 검색하는 API 엔드포인트입니다."""
    query = request.args.get('q', '').strip()
    
    if not query:
        return jsonify({'results': [], 'message': '검색어를 입력해주세요.'})
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'results': [], 'message': '데이터베이스에 연결할 수 없습니다.'})
    
    try:
        # 회사명에서 부분 검색 수행
        cursor = conn.cursor()
        cursor.execute('''
            SELECT corp_code, corp_name, corp_eng_name, stock_code, modify_date
            FROM companies 
            WHERE corp_name LIKE ? OR corp_eng_name LIKE ?
            ORDER BY corp_name
            LIMIT 50
        ''', (f'%{query}%', f'%{query}%'))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'corp_code': row['corp_code'],
                'corp_name': row['corp_name'],
                'corp_eng_name': row['corp_eng_name'],
                'stock_code': row['stock_code'],
                'modify_date': row['modify_date']
            })
        
        conn.close()
        
        if results:
            return jsonify({'results': results, 'message': f'{len(results)}개의 회사를 찾았습니다.'})
        else:
            return jsonify({'results': [], 'message': '검색 결과가 없습니다.'})
            
    except Exception as e:
        conn.close()
        return jsonify({'results': [], 'message': f'검색 중 오류가 발생했습니다: {str(e)}'})

@app.route('/company/<corp_code>')
def company_detail(corp_code):
    """특정 회사의 상세 정보를 반환합니다."""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': '데이터베이스에 연결할 수 없습니다.'})
    
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT corp_code, corp_name, corp_eng_name, stock_code, modify_date
            FROM companies 
            WHERE corp_code = ?
        ''', (corp_code,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return jsonify({
                'corp_code': row['corp_code'],
                'corp_name': row['corp_name'],
                'corp_eng_name': row['corp_eng_name'],
                'stock_code': row['stock_code'],
                'modify_date': row['modify_date']
            })
        else:
            return jsonify({'error': '회사를 찾을 수 없습니다.'})
            
    except Exception as e:
        conn.close()
        return jsonify({'error': f'오류가 발생했습니다: {str(e)}'})

@app.route('/financial/<corp_code>')
def get_financial_info(corp_code):
    """회사의 재무정보를 조회합니다."""
    year = request.args.get('year', '2022')  # 기본값: 2022년
    report_type = request.args.get('report', '11011')  # 기본값: 사업보고서
    
    try:
        # 오픈다트 API로 재무데이터 조회
        raw_data = opendart_api.get_financial_data(corp_code, year, report_type)
        
        if not raw_data:
            return jsonify({'error': '재무데이터를 가져올 수 없습니다.'})
        
        # 데이터 파싱
        financial_data = opendart_api.parse_financial_data(raw_data)
        metrics = opendart_api.get_key_metrics(financial_data)
        
        # 시각화 차트 생성
        charts = {}
        try:
            charts['balance_sheet'] = visualizer.create_balance_sheet_chart(financial_data)
            charts['income_statement'] = visualizer.create_income_statement_chart(financial_data)
            charts['trend_analysis'] = visualizer.create_trend_analysis_chart(financial_data)
        except Exception as chart_error:
            print(f"차트 생성 오류: {chart_error}")
            charts = {}
        
        return jsonify({
            'basic_info': financial_data.get('basic_info', {}),
            'metrics': metrics,
            'charts': charts,
            'financial_data': financial_data
        })
        
    except Exception as e:
        return jsonify({'error': f'재무정보 조회 중 오류가 발생했습니다: {str(e)}'})

@app.route('/financial-page/<corp_code>')
def financial_page(corp_code):
    """재무정보 시각화 페이지를 렌더링합니다."""
    # 회사 기본 정보 조회
    conn = get_db_connection()
    if not conn:
        return "데이터베이스에 연결할 수 없습니다.", 500
    
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT corp_code, corp_name, corp_eng_name, stock_code
            FROM companies 
            WHERE corp_code = ?
        ''', (corp_code,))
        
        company = cursor.fetchone()
        conn.close()
        
        if not company:
            return "회사를 찾을 수 없습니다.", 404
        
        return render_template('financial.html', company=dict(company))
        
    except Exception as e:
        conn.close()
        return f"오류가 발생했습니다: {str(e)}", 500

@app.route('/ai-audit-analysis/<corp_code>')
def ai_audit_analysis(corp_code):
    """AI 감사 리스크 분석 API 엔드포인트"""
    year = request.args.get('year', '2023')
    report = request.args.get('report', '11011')
    
    try:
        # 회사 정보 조회
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': '데이터베이스 연결 실패'})
        
        cursor = conn.cursor()
        cursor.execute('''
            SELECT corp_code, corp_name, corp_eng_name, stock_code
            FROM companies 
            WHERE corp_code = ?
        ''', (corp_code,))
        
        company = cursor.fetchone()
        conn.close()
        
        if not company:
            return jsonify({'error': '회사 정보를 찾을 수 없습니다.'})
        
        company_data = dict(company)
        
        # 재무 데이터 조회 (기본 주요 계정)
        raw_data = opendart_api.get_financial_data(corp_code, year, report)
        if not raw_data:
            return jsonify({'error': '재무 데이터를 가져올 수 없습니다.'})
        
        # 데이터 파싱
        financial_data = opendart_api.parse_financial_data(raw_data)
        
        # 재무비율 계산
        metrics = opendart_api.get_key_metrics(financial_data)
        
        # 전체 재무제표 데이터 조회 (AI 분석용)
        full_financial_raw_data = opendart_api.get_full_financial_statements(corp_code, year, report, 'CFS')
        full_financial_data = {}
        if full_financial_raw_data:
            full_financial_data = opendart_api.parse_full_financial_statements(full_financial_raw_data)
        
        # AI 감사 리스크 분석 수행 (전체 재무제표 데이터 포함)
        analysis_result = ai_analyzer.analyze_financial_risks(company_data, metrics, full_financial_data)
        
        if not analysis_result['success']:
            return jsonify({
                'error': 'AI 분석 중 오류가 발생했습니다.',
                'details': analysis_result.get('error', '알 수 없는 오류')
            })
        
        return jsonify({
            'success': True,
            'company': company_data,
            'metrics': metrics,
            'ai_analysis': analysis_result['analysis'],
            'year': year,
            'report': report
        })
        
    except Exception as e:
        return jsonify({
            'error': f'분석 중 오류가 발생했습니다: {str(e)}'
        })



if __name__ == '__main__':
    if not os.path.exists('companies.db'):
        print("데이터베이스가 없습니다. 먼저 xml_to_db.py를 실행해주세요.")
    else:
        # Flask 설정을 환경변수에서 가져오기
        flask_debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
        flask_host = os.getenv('FLASK_HOST', '0.0.0.0')
        # Render는 PORT 환경변수를 사용
        flask_port = int(os.getenv('PORT', os.getenv('FLASK_PORT', '5000')))
        
        print("웹 서버를 시작합니다...")
        print(f"브라우저에서 http://localhost:{flask_port} 을 열어주세요.")
        app.run(debug=flask_debug, host=flask_host, port=flask_port) 