import xml.etree.ElementTree as ET
import sqlite3
import os

def create_database():
    """SQLite 데이터베이스와 테이블을 생성합니다."""
    conn = sqlite3.connect('companies.db')
    cursor = conn.cursor()
    
    # 기존 테이블이 있다면 삭제
    cursor.execute('DROP TABLE IF EXISTS companies')
    
    # 회사 정보 테이블 생성
    cursor.execute('''
        CREATE TABLE companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            corp_code TEXT NOT NULL,
            corp_name TEXT NOT NULL,
            corp_eng_name TEXT,
            stock_code TEXT,
            modify_date TEXT
        )
    ''')
    
    # 검색 성능을 위한 인덱스 생성
    cursor.execute('CREATE INDEX idx_corp_name ON companies(corp_name)')
    cursor.execute('CREATE INDEX idx_corp_code ON companies(corp_code)')
    
    conn.commit()
    return conn

def parse_xml_and_insert(conn):
    """XML 파일을 파싱하여 데이터베이스에 삽입합니다."""
    if not os.path.exists('corp.xml'):
        print("corp.xml 파일을 찾을 수 없습니다.")
        return
    
    cursor = conn.cursor()
    
    # XML 파일 파싱
    tree = ET.parse('corp.xml')
    root = tree.getroot()
    
    companies_data = []
    
    # 각 list 요소를 순회하며 회사 정보 추출
    for list_item in root.findall('list'):
        corp_code = list_item.find('corp_code').text if list_item.find('corp_code') is not None else ''
        corp_name = list_item.find('corp_name').text if list_item.find('corp_name') is not None else ''
        corp_eng_name = list_item.find('corp_eng_name').text if list_item.find('corp_eng_name') is not None else ''
        stock_code = list_item.find('stock_code').text if list_item.find('stock_code') is not None else ''
        modify_date = list_item.find('modify_date').text if list_item.find('modify_date') is not None else ''
        
        companies_data.append((corp_code, corp_name, corp_eng_name, stock_code, modify_date))
    
    # 배치로 데이터 삽입
    cursor.executemany('''
        INSERT INTO companies (corp_code, corp_name, corp_eng_name, stock_code, modify_date)
        VALUES (?, ?, ?, ?, ?)
    ''', companies_data)
    
    conn.commit()
    print(f"{len(companies_data)}개의 회사 정보가 데이터베이스에 저장되었습니다.")

def main():
    """메인 함수"""
    print("XML 파일을 데이터베이스로 변환하는 중...")
    
    # 데이터베이스 생성 및 연결
    conn = create_database()
    
    # XML 파싱 및 데이터 삽입
    parse_xml_and_insert(conn)
    
    # 연결 종료
    conn.close()
    
    print("데이터베이스 변환이 완료되었습니다!")

if __name__ == "__main__":
    main() 