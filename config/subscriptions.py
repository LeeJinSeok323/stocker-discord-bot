import pymysql
import sec.sec_fetch as fetch
from config.db_config import get_db_connection

def subscribe(user_id: str, ticker: str):
    ticker = ticker.upper()
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # check if already exists
            cursor.execute("SELECT 1 FROM sec_watchlist WHERE discord_user_id = %s AND ticker = %s AND enabled = 'Y'", (user_id, ticker))
            if cursor.fetchone():
                return False

            cik_str = None
            conn_cik = get_db_connection()
            try:
                with conn_cik.cursor() as cursor_cik:
                    cursor_cik.execute("SELECT cik FROM stocks WHERE ticker = %s", (ticker,))
                    row = cursor_cik.fetchone()
                    if row:
                        cik_str = str(row['cik']).zfill(10)
            finally:
                conn_cik.close()
            
            # insert or update
            # Using REPLACE or ON DUPLICATE KEY UPDATE.
            # We already added unique index (ticker, discord_user_id)
            cursor.execute("""
                INSERT INTO sec_watchlist (ticker, cik, discord_user_id, enabled)
                VALUES (%s, %s, %s, 'Y')
                ON DUPLICATE KEY UPDATE enabled = 'Y', cik = VALUES(cik)
            """, (ticker, cik_str, user_id))
            conn.commit()
            return True
    except Exception as e:
        print(f"[subscriptions] ERROR in subscribe: {e}")
        return False
    finally:
        conn.close()

def unsubscribe(user_id: str, ticker: str):
    ticker = ticker.upper()
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE sec_watchlist SET enabled = 'N' WHERE discord_user_id = %s AND ticker = %s", (user_id, ticker))
            conn.commit()
            return cursor.rowcount > 0
    except Exception as e:
        print(f"[subscriptions] ERROR in unsubscribe: {e}")
        return False
    finally:
        conn.close()

def get_subscriptions(user_id: str):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT ticker FROM sec_watchlist WHERE discord_user_id = %s AND enabled = 'Y'", (user_id,))
            return [row['ticker'] for row in cursor.fetchall()]
    except Exception as e:
        print(f"[subscriptions] ERROR in get_subscriptions: {e}")
        return []
    finally:
        conn.close()

def get_all_subscriptions():
    """
    Returns {user_id_str: [ticker_list]}
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT discord_user_id, ticker FROM sec_watchlist WHERE enabled = 'Y'")
            rows = cursor.fetchall()
            result = {}
            for row in rows:
                uid = str(row['discord_user_id'])
                ticker = row['ticker']
                result.setdefault(uid, []).append(ticker)
            return result
    except Exception as e:
        print(f"[subscriptions] ERROR in get_all_subscriptions: {e}")
        return {}
    finally:
        conn.close()

def get_ticker_channel(ticker: str, guild_id: str):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT channel_id FROM sec_ticker_channel WHERE ticker = %s AND guild_id = %s", (ticker.upper(), str(guild_id)))
            row = cursor.fetchone()
            if row:
                return str(row['channel_id'])
            return None
    except Exception as e:
        print(f"[subscriptions] ERROR in get_ticker_channel: {e}")
        return None
    finally:
        conn.close()

def set_ticker_channel(ticker: str, guild_id: str, channel_id: str):
    ticker = ticker.upper()
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO sec_ticker_channel (ticker, guild_id, channel_id)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE channel_id = VALUES(channel_id)
            """, (ticker, str(guild_id), str(channel_id)))
            conn.commit()
    except Exception as e:
        print(f"[subscriptions] ERROR in set_ticker_channel: {e}")
    finally:
        conn.close()
