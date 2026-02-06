"""
SEC 공시 데이터를 가져옴
"""
import json
import requests
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import re

load_dotenv()
SEC_USER_AGENT = os.getenv("SEC_USER_AGENT")

with open("store/company_tickers.json", "r", encoding="utf-8") as f:
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

def get_filing_detail(submissions: dict, accession_no: str) -> str:
    """
    특정 공시의 상세 내용을 조회

    Args:
        submissions: get_sec_submissions() 결과
        accession_no: accession number

    Returns:
        공시 원문 텍스트(메인 문서 위주)
    """
    recent = submissions["filings"]["recent"]

    idx = recent["accessionNumber"].index(accession_no)
    primary_doc = recent["primaryDocument"][idx]
    form_type = recent.get("form", [""])[idx]

    cik = submissions["cik"]
    acc_no_clean = accession_no.replace("-", "")

    base_dir = f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc_no_clean}"
    index_url = f"{base_dir}/index.json"

    headers = {"User-Agent": SEC_USER_AGENT}

    # 1) index.json에서 complete submission(.txt) 찾기
    txt_url = None
    try:
        r = requests.get(index_url, headers=headers)
        r.raise_for_status()
        index_json = r.json()

        items = index_json.get("directory", {}).get("item", []) or []
        # 보통 {acc_no_clean}.txt가 "Complete submission text file"
        target_txt = f"{acc_no_clean}.txt"
        for it in items:
            name = it.get("name", "")
            if name == target_txt:
                txt_url = f"{base_dir}/{name}"
                break
        if txt_url is None:
            # 혹시 이름이 다르면 .txt 아무거나(가장 범용) 잡기
            for it in items:
                name = it.get("name", "")
                if name.lower().endswith(".txt"):
                    txt_url = f"{base_dir}/{name}"
                    break
    except Exception:
        txt_url = None

    # 2) complete submission이 있으면 그걸로 메인 문서 뽑기
    if txt_url:
        res = requests.get(txt_url, headers=headers)
        res.raise_for_status()
        raw = res.text

        # <DOCUMENT> 블록 분해
        docs = re.split(r"(?i)</DOCUMENT>\s*<DOCUMENT>", raw)
        parsed = []

        for i, chunk in enumerate(docs):
            # split 때문에 첫/끝 조각이 깨질 수 있어 보정
            if i != 0:
                chunk = "<DOCUMENT>" + chunk
            if i != len(docs) - 1:
                chunk = chunk + "</DOCUMENT>"

            def pick(tag: str) -> str:
                m = re.search(rf"(?is)<{tag}>\s*(.*?)\s*</{tag}>", chunk)
                return (m.group(1).strip() if m else "")

            doc_type = pick("TYPE")
            filename = pick("FILENAME")

            # 본문은 보통 <TEXT>...</TEXT> 안에 있음
            m_text = re.search(r"(?is)<TEXT>\s*(.*?)\s*</TEXT>", chunk)
            body = (m_text.group(1) if m_text else chunk)

            parsed.append({
                "type": doc_type,
                "filename": filename,
                "body": body
            })

        chosen = None

        # 1순위: TYPE이 form_type과 일치
        if form_type:
            for d in parsed:
                if d["type"].upper() == form_type.upper():
                    chosen = d
                    break

        # 2순위: filename이 primaryDocument와 일치
        if chosen is None and primary_doc:
            for d in parsed:
                if d["filename"] == primary_doc:
                    chosen = d
                    break

        # 3순위: 첫 문서
        if chosen is None and parsed:
            chosen = parsed[0]

        if chosen:
            body = chosen["body"]
            # HTML이면 텍스트로 정리
            if re.search(r"(?is)<html|<body|<div|<p|<table", body):
                soup = BeautifulSoup(body, "lxml")
                return soup.get_text(" ", strip=True)
            return body.strip()

        return raw

    # 3) complete submission을 못 찾으면 기존처럼 primary_doc 직접 반환(원래 로직 유지)
    url = f"{base_dir}/{primary_doc}"
    res = requests.get(url, headers=headers)
    res.raise_for_status()
    return res.text



