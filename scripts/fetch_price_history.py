import yfinance as yf
import time
import random
from config.db_config import get_db_connection
from datetime import datetime

def fetch_and_save_full_history():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT ticker FROM stocks WHERE status = 'ACTIVE'")
            tickers = [row['ticker'] for row in cursor.fetchall()]
    finally:
        conn.close()

    for ticker in tickers:
        try:
            print(f"[batch] Processing {ticker}...")
            stock = yf.Ticker(ticker)
            hist = stock.history(period="max")

            if hist.empty or ticker in yf.shared._errors:
                raise ValueError(f"Delisted or No Data: {yf.shared._errors.get(ticker)}")

            conn = get_db_connection()
            try:
                with conn.cursor() as cursor:
                    for date, row in hist.iterrows():
                        date_str = date.strftime('%Y-%m-%d')
                        cursor.execute("""
                            INSERT INTO stock_price_history (ticker, date, open, high, low, close, volume)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                            ON DUPLICATE KEY UPDATE 
                                open = VALUES(open), high = VALUES(high), 
                                low = VALUES(low), close = VALUES(close), volume = VALUES(volume)
                        """, (ticker, date_str, row['Open'], row['High'], row['Low'], row['Close'], int(row['Volume'])))
                    conn.commit()
            finally:
                conn.close()
            time.sleep(random.uniform(1, 3))

        except Exception as e:
            print(f"[batch] Delisting {ticker} due to: {e}")
            conn = get_db_connection()
            try:
                with conn.cursor() as cursor:
                    cursor.execute("UPDATE stocks SET status = 'DELISTED', delisted_at = NOW() WHERE ticker = %s", (ticker,))
                    conn.commit()
            finally:
                conn.close()

if __name__ == "__main__":
    fetch_and_save_full_history()