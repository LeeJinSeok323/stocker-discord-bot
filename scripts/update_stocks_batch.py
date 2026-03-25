import requests
import pymysql
from config.db_config import get_db_connection

def update_stocks():
    # SEC에서 최신 티커 목록 다운로드
    url = "https://www.sec.gov/files/company_tickers.json"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    res.raise_for_status()
    data = res.json()
    
    records = []
    for entry in data.values():
        records.append((entry['ticker'], str(entry['cik_str']), entry['title']))
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # 전체 삭제 후 재삽입 (최신화)
            cursor.execute("TRUNCATE TABLE stocks")
            cursor.executemany("""
                INSERT INTO stocks (ticker, cik, company_name)
                VALUES (%s, %s, %s)
            """, records)
            conn.commit()
            print(f"[batch] Updated {len(records)} stocks.")
    except Exception as e:
        print(f"[batch] Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    update_stocks()
