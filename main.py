import os
from dotenv import load_dotenv
from bot.discord_bot import bot
from config.messages import M
from core.db_init import initialize_db

def main():
    load_dotenv()
    initialize_db()
    discord_token = os.getenv("DISCORD_TOKEN")
    
    if not discord_token:
        print(M["LOG_MAIN_NO_TOKEN"])
        return
    
    print(M["LOG_MAIN_START"])
    bot.run(discord_token)

if __name__ == "__main__":
    main()
