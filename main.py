import os
import sys
import traceback
from dotenv import load_dotenv

# 로직 실행 전 최상단에서 로그 출력
print("[main] Starting application...", flush=True)

try:
    load_dotenv()
    from bot.discord_bot import bot
    from config.messages import M
    from core.stock_scheduler import start_stock_update_service
    
    def main():
        discord_token = os.getenv("DISCORD_TOKEN")
        if not discord_token:
            print("[main] FATAL: DISCORD_TOKEN not found!")
            sys.exit(1)
        
        print("[main] Starting stock update service...", flush=True)
        start_stock_update_service()
        
        print("[main] Starting bot...", flush=True)
        bot.run(discord_token)

    if __name__ == "__main__":
        main()

except Exception:
    print("[main] FATAL CRASH:")
    traceback.print_exc()
    sys.exit(1)
