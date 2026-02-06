from config.db_config import get_db_connection

FILING_TABLE = "sec_filing"

# GPT 요약이 필요한 주가 영향 공시 (현재 정책)
GPT_FORMS = {
    "8-K",

    # 지분 / 수급
    "SC 13D",
    "SC 13D/A",
    "SC 13G",
    "SC 13G/A",

    # 오퍼링 요약본
    "424B3",
    "424B5",

    # 경영 / 의결
    "DEF 14A",

    # 내부자 거래
    "4",
    "4/A",
}


def _exists_in_sec_filing(accession_no: str) -> bool:
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                f"SELECT 1 FROM {FILING_TABLE} WHERE accession_no = %s LIMIT 1",
                (accession_no,)
            )
            return cursor.fetchone() is not None
    finally:
        conn.close()


def check_filing_status(accession_no: str, form_type: str) -> dict:
    """
    SEC 공시 상태 판정 (판단만, 처리 X)
    """
    accession_no = (accession_no or "").strip()
    form_type = (form_type or "").strip().upper()

    meta_exists = _exists_in_sec_filing(accession_no)

    should_notify = not meta_exists
    should_gpt = should_notify and (form_type in GPT_FORMS)

    return {
        "should_notify": should_notify,
        "should_gpt": should_gpt,
    }
