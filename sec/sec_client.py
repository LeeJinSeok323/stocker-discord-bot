import sec.sec_fetch as fetch
import sec.sec_filter as filter
from datetime import date, timedelta

NO_MEANING_ALERT_DATE_COUNT = 2
TARGET_TICKER = "BNAI"


submission = fetch.get_sec_submissions(TARGET_TICKER)
recent = submission["filings"]["recent"]
cutoff = (date.today() - timedelta(days=NO_MEANING_ALERT_DATE_COUNT)).strftime("%Y-%m-%d")

for accession_no, form_type, filing_date_str in zip(
    recent["accessionNumber"],
    recent["form"],
    recent["filingDate"],
):
    if filing_date_str < cutoff:
        break

    status = filter.check_filing_status(accession_no, form_type)
    print(status)