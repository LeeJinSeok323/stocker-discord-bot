import time
import random
from curl_cffi import requests
import yfinance as yf
from config.db_config import get_db_connection

def batch_fetch_stocks(limit=50):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT ticker FROM stocks 
                WHERE last_fetched_at IS NULL 
                ORDER BY ticker ASC LIMIT %s
            """, (limit,))
            tickers = [row['ticker'] for row in cursor.fetchall()]

        if not tickers:
            print("[batch] All stocks fetched. Nothing to do.", flush=True)
            return

        # curl_cffi를 사용하여 브라우저 지문을 모방한 세션 생성
        session = requests.Session(impersonate="chrome120")

        count = 0
        for ticker in tickers:
            try:
                print(f"[batch] Fetching {ticker}...", flush=True)

                data = yf.download(
                    tickers=ticker,
                    period="max",
                    interval="1d",
                    auto_adjust=False,
                    prepost=False,
                    threads=False,
                    session=session
                )

                if not data.empty:
                    data = data.dropna(subset=['Open', 'High', 'Low', 'Close', 'Volume'])
                    val_list = []
                    for date, row in data.iterrows():
                        val_list.append((
                            ticker,
                            date.strftime('%Y-%m-%d'),
                            float(row['Open']),
                            float(row['High']),
                            float(row['Low']),
                            float(row['Close']),
                            int(row['Volume'])
                        ))

                    with conn.cursor() as cursor:
                        sql = """
                            INSERT INTO stock_price_history (ticker, date, open, high, low, close, volume)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                            ON DUPLICATE KEY UPDATE 
                                open = VALUES(open), high = VALUES(high), 
                                low = VALUES(low), close = VALUES(close), 
                                volume = VALUES(volume)
                        """
                        cursor.executemany(sql, val_list)
                        cursor.execute("UPDATE stocks SET last_fetched_at = NOW() WHERE ticker = %s", (ticker,))
                        conn.commit()
                    print(f"[batch] {ticker} success. Inserted {len(val_list)} rows.", flush=True)
                else:
                    with conn.cursor() as cursor:
                        cursor.execute("UPDATE stocks SET last_fetched_at = NOW() WHERE ticker = %s", (ticker,))
                        conn.commit()
                    print(f"[batch] {ticker} has no data.", flush=True)

                count += 1
                if count % 50 == 0:
                    macro_sleep = random.uniform(120.0, 300.0)
                    print(f"[batch] Coffee break! Sleeping for {macro_sleep:.2f} seconds...", flush=True)
                    time.sleep(macro_sleep)
                else:
                    time.sleep(random.uniform(5.0, 15.0))

            except Exception as e:
                conn.rollback()
                error_msg = str(e).lower()
                if "429" in error_msg or "too many requests" in error_msg:
                    print(f"[batch] Rate limited on {ticker}. Sleeping for 15 minutes.", flush=True)
                    time.sleep(900)
                else:
                    print(f"[batch] Error on {ticker}: {e}", flush=True)
                    time.sleep(60)
    finally:
        conn.close()
