import schedule
import time
import threading
from core.stock_fetcher import batch_fetch_stocks
from scripts.update_stocks_batch import update_stocks

def run_scheduler():
    print("[scheduler] Starting stock update jobs...", flush=True)
    schedule.every(7).days.do(update_stocks)
    print("[scheduler] Starting batch_fetch_stocks...", flush=True)
    schedule.every(1).hours.do(batch_fetch_stocks)

    print("[scheduler] Running initial jobs...", flush=True)
    update_stocks()
    batch_fetch_stocks()

    while True:
        schedule.run_pending()
        time.sleep(60)

def start_stock_update_service():
    print("[scheduler] Starting background stock update service...", flush=True)
    thread = threading.Thread(target=run_scheduler, daemon=True)
    thread.start()
