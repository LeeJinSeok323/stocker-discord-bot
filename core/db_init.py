from config.db_config import get_db_connection

def initialize_db():
    """
    필요한 DB 테이블들을 생성합니다.
    (기존 sec_filing, sec_filing_content 테이블은 이미 존재하므로 건드리지 않습니다.)
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # 3. 유저 쓰레드별 경고 기록 테이블만 생성
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_thread_warning (
                id INT AUTO_INCREMENT PRIMARY KEY,
                thread_id BIGINT NOT NULL,
                user_id BIGINT NOT NULL,
                warning_count INT DEFAULT 0,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                UNIQUE KEY uk_thread_user (thread_id, user_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)
            
            conn.commit()
            print("[DB] Warning table initialized successfully.")
    except Exception as e:
        print(f"[DB] Error initializing database: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    initialize_db()
