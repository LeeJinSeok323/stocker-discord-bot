import json
import os

CONFIG_FILE = "config.json"

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {"users": {}, "ticker_channels": {}}
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            if "users" not in data:
                data["users"] = {}
            if "ticker_channels" not in data:
                data["ticker_channels"] = {}
            return data
        except json.JSONDecodeError:
            return {"users": {}, "ticker_channels": {}}

def save_config(data):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def subscribe(user_id: str, ticker: str):
    data = load_config()
    users = data.setdefault("users", {})
    tickers = users.setdefault(str(user_id), [])
    ticker = ticker.upper()
    if ticker not in tickers:
        tickers.append(ticker)
        save_config(data)
        return True
    return False

def unsubscribe(user_id: str, ticker: str):
    data = load_config()
    users = data.setdefault("users", {})
    tickers = users.setdefault(str(user_id), [])
    ticker = ticker.upper()
    if ticker in tickers:
        tickers.remove(ticker)
        save_config(data)
        return True
    return False

def get_subscriptions(user_id: str):
    data = load_config()
    return data.get("users", {}).get(str(user_id), [])

def get_all_subscriptions():
    data = load_config()
    return data.get("users", {})

def get_ticker_channel(ticker: str):
    data = load_config()
    return data.get("ticker_channels", {}).get(ticker.upper())

def set_ticker_channel(ticker: str, channel_id: str):
    data = load_config()
    channels = data.setdefault("ticker_channels", {})
    channels[ticker.upper()] = str(channel_id)
    save_config(data)
