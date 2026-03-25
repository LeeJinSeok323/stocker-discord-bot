import os
import requests
from config.db_config import get_db_connection
from dotenv import load_dotenv

load_dotenv()

def update_stocks():
    url = "https://www.sec.gov/files/company_tickers_exchange.json"
    headers = {"User-Agent": os.getenv("SEC_USER_AGENT", "MyBot/1.0 (contact@example.com)")}

    try:
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        data = res.json()

        rows = data['data']
        new_tickers = []
        records = []

        for row in rows:
            ticker = row[2]
            if any(ticker.endswith(s) for s in [".OB", ".PK", "-WT", "-UN", "-PR"]): continue
            if any(c in ticker for c in ["^", "/", "$"]): continue

            exchange = (row[3] or "UNKNOWN").upper()
            new_tickers.append(ticker)
            records.append((ticker, str(row[0]), row[1], exchange))

        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                if records:
                    sql_upsert = """
                        INSERT INTO stocks (ticker, cik, company_name, exchange, status, delisted_at)
                        VALUES (%s, %s, %s, %s, 'ACTIVE', NULL)
                        ON DUPLICATE KEY UPDATE 
                            cik = VALUES(cik), company_name = VALUES(company_name),
                            exchange = VALUES(exchange), status = 'ACTIVE', delisted_at = NULL
                    """
                    cursor.executemany(sql_upsert, records)

                    format_strings = ','.join(['%s'] * len(new_tickers))
                    sql_delist = f"UPDATE stocks SET status = 'DELISTED', delisted_at = NOW() WHERE status = 'ACTIVE' AND ticker NOT IN ({format_strings})"
                    cursor.execute(sql_delist, tuple(new_tickers))
                    conn.commit()
                    print(f"[batch] Updated {len(records)} stocks.", flush=True)
        except Exception as e:
            conn.rollback()
            print(f"[batch] DB Error: {e}", flush=True)
        finally:
            conn.close()
    except Exception as e:
        print(f"[batch] Fetching Error: {e}", flush=True)

if __name__ == "__main__":
    update_stocks()