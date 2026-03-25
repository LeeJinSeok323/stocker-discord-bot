import schedule
import time
import threading
from core.stock_fetcher import batch_fetch_stocks

def run_scheduler():
    # 1시간마다 50개씩 수집하는 루프
    schedule.every(1).hours.do(batch_fetch_stocks)
    
    # 즉시 1회 실행
    batch_fetch_stocks()
    
    while True:
        schedule.run_pending()
        time.sleep(60)

def start_stock_update_service():
    print("[scheduler] Starting background stock update service...", flush=True)
    thread = threading.Thread(target=run_scheduler, daemon=True)
    thread.start()
