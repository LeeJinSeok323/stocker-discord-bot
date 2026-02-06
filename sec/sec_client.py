import sec.sec_fetch as fetch
import sec.sec_filter as filter
import sec.sec_save as save
from datetime import date, timedelta

NO_MEANING_ALERT_DATE_COUNT = 2

ticker = input("티커를 입력하세요.")

submission = fetch.get_sec_submissions(ticker);
recent = submission["filings"]["recent"]
cutoff = cutoff_str = (date.today() - timedelta(days=NO_MEANING_ALERT_DATE_COUNT)).strftime("%Y-%m-%d")

for i in range(len(recent["accessionNumber"])):
    filing_date_str = recent["filingDate"][i]
    if filing_date_str < cutoff:
        break

    accession_no = recent["accessionNumber"][i]
    form_type = recent["form"][i]
    status = filter.check_filing_status(accession_no, form_type);
    print(status)