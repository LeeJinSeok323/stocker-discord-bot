import sec.sec_fetch as fetch
import sec.sec_filter as filter
import sec.sec_save as save
from datetime import date, timedelta

NO_MEANING_ALERT_DATE_COUNT = 2
TARGET_TICKER = "BNAI"


submission = fetch.get_sec_submissions(TARGET_TICKER)
recent = submission["filings"]["recent"]
cutoff = (date.today() - timedelta(days=NO_MEANING_ALERT_DATE_COUNT)).strftime(
    "%Y-%m-%d"
)

cik = str(submission["cik"]).lstrip("0")
cik10 = fetch.get_cik10(TARGET_TICKER)

for accession_no, form_type, filing_date_str, primary_doc, accepted_at in zip(
    recent["accessionNumber"],
    recent["form"],
    recent["filingDate"],
    recent.get("primaryDocument", []),
    recent.get("acceptanceDateTime", []),
):
    if filing_date_str < cutoff:
        break

    status = filter.check_filing_status(accession_no, form_type)
    print(status)

    if not status["should_notify"]:
        continue

    acc_no_clean = accession_no.replace("-", "")
    base_dir = f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc_no_clean}"

    # MySQL DATETIME 형식에 맞게 단순 정제
    accepted_at_mysql = None
    if accepted_at:
        accepted_at_mysql = accepted_at.replace("T", " ").replace("Z", "")[:19]

    meta = {
        "cik10": cik10,
        "ticker": TARGET_TICKER,
        "accession_no": accession_no,
        "form_type": form_type,
        "filing_date": filing_date_str,
        "accepted_at": accepted_at_mysql,
        "primary_doc": primary_doc,
        "filing_html_url": f"{base_dir}/{primary_doc}" if primary_doc else None,
        "filing_txt_url": f"{base_dir}/{acc_no_clean}.txt",
    }

    filing_id = save.save_filing_meta(meta)
    print(f"saved filing_id={filing_id} for {accession_no}")
    break