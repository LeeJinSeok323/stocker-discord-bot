import time
import random
import yfinance as yf
from config.db_config import get_db_connection

def batch_fetch_stocks(limit=50):
    conn = get_db_connection()
    try:
        # 수집 안 된 종목 50개만 조회
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT ticker FROM stocks 
                WHERE last_fetched_at IS NULL 
                ORDER BY ticker ASC LIMIT %s
            """, (limit,))
            tickers = [row['ticker'] for row in cursor.fetchall()]
        
        if not tickers:
            print("[batch] All stocks fetched. Nothing to do.")
            return

        for ticker in tickers:
            try:
                print(f"[batch] Fetching {ticker}...")
                stock = yf.Ticker(ticker)
                hist = stock.history(period="max")
                
                if not hist.empty:
                    with conn.cursor() as cursor:
                        for date, row in hist.iterrows():
                            cursor.execute("""
                                INSERT INTO stock_price_history (ticker, date, open, high, low, close, volume)
                                VALUES (%s, %s, %s, %s, %s, %s, %s)
                                ON DUPLICATE KEY UPDATE 
                                    open = VALUES(open), high = VALUES(high), 
                                    low = VALUES(low), close = VALUES(close), 
                                    volume = VALUES(volume)
                            """, (ticker, date.strftime('%Y-%m-%d'), row['Open'], row['High'], row['Low'], row['Close'], int(row['Volume'])))
                        
                        cursor.execute("UPDATE stocks SET last_fetched_at = NOW() WHERE ticker = %s", (ticker,))
                        conn.commit()
                        print(f"[batch] {ticker} success.")
                else:
                    # 데이터가 없는 경우도 완료 처리
                    with conn.cursor() as cursor:
                        cursor.execute("UPDATE stocks SET last_fetched_at = NOW() WHERE ticker = %s", (ticker,))
                        conn.commit()
                
                time.sleep(random.uniform(5, 10))
            except Exception as e:
                print(f"[batch] Error on {ticker}: {e}")
                time.sleep(60) 
    finally:
        conn.close()
