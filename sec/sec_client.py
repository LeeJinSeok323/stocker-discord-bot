import traceback

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

print(f"[sec_client] TARGET_TICKER={TARGET_TICKER}, cutoff={cutoff}")

cik = str(submission["cik"]).lstrip("0")
cik10 = fetch.get_cik10(TARGET_TICKER)

saved_any = False

for accession_no, form_type, filing_date_str, primary_doc, accepted_at in zip(
    recent["accessionNumber"],
    recent["form"],
    recent["filingDate"],
    recent.get("primaryDocument", []),
    recent.get("acceptanceDateTime", []),
):
    print(
        f"[sec_client] check accession_no={accession_no}, form_type={form_type}, filing_date={filing_date_str}"
    )

    if filing_date_str < cutoff:
        print("[sec_client] filing_date < cutoff, loop break")
        break

    status = filter.check_filing_status(accession_no, form_type)
    print(f"[sec_client] status={status}")

    if not status["should_notify"]:
        print("[sec_client] already exists in DB, skip notify/save")
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

    print(f"[sec_client] try save meta={meta}")
    try:
        filing_id = save.save_filing_meta(meta)
        saved_any = True
        print(f"[sec_client] saved filing_id={filing_id} for {accession_no}")
    except Exception as e:
        print(f"[sec_client] ERROR while saving filing {accession_no}: {e!r}")
        traceback.print_exc()
    break

if not saved_any:
    print(
        "[sec_client] No filings were saved. Either there was no recent filing, or all were already in DB, or an error occurred during save."
    )