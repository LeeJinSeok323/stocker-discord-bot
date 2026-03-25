import os
import schedule
import time
import threading
from scripts.update_stocks_batch import update_stocks

def run_scheduler(interval_days=7):
    # 즉시 1회 실행
    print("[scheduler] Running initial stock update...")
    update_stocks()
    
    # 주기 설정
    schedule.every(interval_days).days.do(update_stocks)
    
    while True:
        schedule.run_pending()
        time.sleep(3600) # 1시간마다 체크

def start_stock_update_service(interval_days=7):
    thread = threading.Thread(target=run_scheduler, args=(interval_days,), daemon=True)
    thread.start()
