import json
import requests
import os
from dotenv import load_dotenv

load_dotenv()
SEC_USER_AGENT = os.getenv("SEC_USER_AGENT")

with open("../store/company_tickers.json", "r", encoding="utf-8") as f:
    data = json.load(f)


ticker_to_cik = {
    item["ticker"]: int(item["cik_str"])
    for item in data.values()
}

def get_cik10(ticker: str) -> str:
    cik = ticker_to_cik[ticker.upper().strip()]  # 없으면 KeyError
    return str(cik).zfill(10)


def get_sec_submissions(ticker: str) -> dict:
    cik10 = get_cik10(ticker)
    url = f"https://data.sec.gov/submissions/CIK{cik10}.json"
    headers = {
        "User-Agent": SEC_USER_AGENT
    }
    res = requests.get(url, headers=headers)
    res.raise_for_status()
    return res.json()

