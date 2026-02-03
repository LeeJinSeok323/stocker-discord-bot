import json
import requests

with open("D:/CUMILIA/STOCKER_A/store/company_tickers.json", "r", encoding="utf-8") as f:
    data = json.load(f)


ticker_to_cik = {
    item["ticker"]: int(item["cik_str"])
    for item in data.values()
}

def get_cik10(ticker: str) -> str:
    cik = ticker_to_cik[ticker.upper().strip()]  # 없으면 KeyError
    return str(cik).zfill(10)


def get_sec_submissions(cik10: str) -> dict:
    url = f"https://data.sec.gov/submissions/CIK{cik10}.json"
    headers = {
        "User-Agent": "stocker-discord-bot jinseoki10@gmail.com"
    }
    res = requests.get(url, headers=headers)
    res.raise_for_status()
    return res.json()


data = get_sec_submissions("0001838163")
print(data)

