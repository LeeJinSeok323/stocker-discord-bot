from config.db_config import get_db_connection

def get_warning_count(thread_id: int, user_id: int) -> int:
    """
    특정 쓰레드에서 유저의 경고 횟수를 가져옵니다.
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT warning_count FROM user_thread_warning WHERE thread_id=%s AND user_id=%s",
                (thread_id, user_id)
            )
            res = cursor.fetchone()
            return res['warning_count'] if res else 0
    finally:
        conn.close()

def add_warning(thread_id: int, user_id: int) -> int:
    """
    경고 횟수를 1 증가시키고 현재 횟수를 반환합니다.
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
            INSERT INTO user_thread_warning (thread_id, user_id, warning_count)
            VALUES (%s, %s, 1)
            ON DUPLICATE KEY UPDATE warning_count = warning_count + 1
            """
            cursor.execute(sql, (thread_id, user_id))
            conn.commit()
            
            cursor.execute(
                "SELECT warning_count FROM user_thread_warning WHERE thread_id=%s AND user_id=%s",
                (thread_id, user_id)
            )
            return cursor.fetchone()['warning_count']
    finally:
        conn.close()

def log_timeout(user_id: int, guild_id: int, reason: str, duration: int = 5):
    """
    유저의 타임아웃 제재 이력을 DB에 기록합니다.
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
            INSERT INTO user_timeout_log (user_id, guild_id, reason, duration_minutes)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql, (user_id, guild_id, reason, duration))
            conn.commit()
            print(f"[DB] Timeout logged for user {user_id} in guild {guild_id}")
    finally:
        conn.close()

def reset_warnings(thread_id: int, user_id: int):
    """
    경고 횟수를 초기화합니다.
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE user_thread_warning SET warning_count = 0 WHERE thread_id=%s AND user_id=%s",
                (thread_id, user_id)
            )
            conn.commit()
    finally:
        conn.close()

def get_user_warnings(user_id: int) -> list:
    """
    유저가 받은 현재 활성 상태인 경고 기록 목록을 가져옵니다. (warning_count > 0)
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT thread_id, warning_count, updated_at FROM user_thread_warning WHERE user_id=%s AND warning_count > 0 ORDER BY updated_at DESC",
                (user_id,)
            )
            return cursor.fetchall()
    finally:
        conn.close()

def get_user_timeout_logs(user_id: int, guild_id: int) -> list:
    """
    해당 길드에서 특정 유저가 받은 타임아웃 제재 이력을 최근 10개까지 가져옵니다.
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT reason, duration_minutes, created_at FROM user_timeout_log WHERE user_id=%s AND guild_id=%s ORDER BY created_at DESC LIMIT 10",
                (user_id, guild_id)
            )
            return cursor.fetchall()
    finally:
        conn.close()
