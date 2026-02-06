"""
SEC 공시 데이터를 저장함
"""

# sec_save.py
from config.db_config import get_db_connection

def save_filing_meta(meta: dict) -> int:
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
            INSERT INTO sec_filing
              (cik10, ticker, accession_no, form_type, filing_date,
               accepted_at, primary_doc, filing_html_url, filing_txt_url, created_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s, NOW())
            """
            cursor.execute(sql, (
                meta["cik10"],
                meta.get("ticker"),
                meta["accession_no"],
                meta["form_type"],
                meta["filing_date"],
                meta.get("accepted_at"),
                meta.get("primary_doc"),
                meta.get("filing_html_url"),
                meta.get("filing_txt_url"),
            ))
            conn.commit()

            # 방금 insert된 id 반환 (SELECT 재조회 불필요)
            return cursor.lastrowid
    finally:
        conn.close()



def save_filing_content(filing_id: int, content_type: str, content: str) -> int:
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
            INSERT INTO sec_filing_content (filing_id, content_type, content)
            VALUES (%s,%s,%s)
            ON DUPLICATE KEY UPDATE content=VALUES(content)
            """
            cursor.execute(sql, (filing_id, content_type, content))
            conn.commit()

            cursor.execute(
                "SELECT id FROM sec_filing_content WHERE filing_id=%s AND content_type=%s",
                (filing_id, content_type)
            )
            return cursor.fetchone()["id"]
    finally:
        conn.close()
