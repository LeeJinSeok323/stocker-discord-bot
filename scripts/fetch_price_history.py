import yfinance as yf
import time
import random
import pymysql
from config.db_config import get_db_connection

def fetch_and_save_full_history():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT ticker FROM stocks")
            tickers = [row['ticker'] for row in cursor.fetchall()]
    finally:
        conn.close()

    print(f"[batch] Found {len(tickers)} tickers to process for full history.")

    for ticker in tickers:
        try:
            print(f"[batch] Processing {ticker}...")
            # 상장 시점부터 현재까지 전체 데이터 수집 (start=None, end=None)
            stock = yf.Ticker(ticker)
            hist = stock.history(period="max")
            
            if hist.empty:
                continue

            # DB에 저장
            conn = get_db_connection()
            try:
                with conn.cursor() as cursor:
                    for date, row in hist.iterrows():
                        # yfinance의 DateIndex를 문자열로 변환 (time zone 제거)
                        date_str = date.strftime('%Y-%m-%d')
                        cursor.execute("""
                            INSERT INTO stock_price_history (ticker, date, open, high, low, close, volume)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                            ON DUPLICATE KEY UPDATE 
                                open = VALUES(open), high = VALUES(high), 
                                low = VALUES(low), close = VALUES(close), 
                                volume = VALUES(volume)
                        """, (ticker, date_str, row['Open'], row['High'], row['Low'], row['Close'], int(row['Volume'])))
                    conn.commit()
            finally:
                conn.close()

            # yfinance는 요청이 많으면 차단될 가능성이 높음.
            # 데이터가 많은 종목일수록 더 신중하게 속도 제한 적용 (2 ~ 5초)
            time.sleep(random.uniform(2, 5))
            
        except Exception as e:
            print(f"[batch] Error processing {ticker}: {e}")

if __name__ == "__main__":
    fetch_and_save_full_history()
