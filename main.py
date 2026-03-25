import os
import sys
import traceback
from dotenv import load_dotenv

print("[main] Starting application...", flush=True)
load_dotenv()

try:
    from bot.discord_bot import bot
    from core.scheduler import start_stock_update_service
except Exception as e:
    print(f"[main] Import Error: {e}")
    traceback.print_exc()
    sys.exit(1)

def main():
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("[main] FATAL: DISCORD_TOKEN not found!")
        return

    # 스케줄러 시작 (백그라운드 스레드)
    start_stock_update_service()

    # 디스코드 봇 시작 (메인 스레드 점유)
    try:
        print("[main] Starting bot...", flush=True)
        bot.run(token)
    except Exception as e:
        print(f"[main] Bot Crash: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()