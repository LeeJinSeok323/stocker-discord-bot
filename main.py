import os
from dotenv import load_dotenv
from bot.discord_bot import bot
from config.messages import M
from core.stock_scheduler import start_stock_update_service

def main():
    load_dotenv()
    discord_token = os.getenv("DISCORD_TOKEN")
    
    if not discord_token:
        print(M["LOG_MAIN_NO_TOKEN"])
        return
    
    # 백그라운드 데이터 수집 서비스 시작
    start_stock_update_service()
    
    print(M["LOG_MAIN_START"])
    bot.run(discord_token)

if __name__ == "__main__":
    main()
