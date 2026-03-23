import os
import discord
from discord.ext import commands, tasks

from config.subscriptions import (
    subscribe, unsubscribe, get_subscriptions, 
    get_all_subscriptions, get_ticker_channel, set_ticker_channel
)
from core.sec_checker import check_new_filings
from config.messages import M

class SECBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True # 메시지 내용을 읽기 위해 필요
        super().__init__(command_prefix="!", intents=intents)
    
    async def setup_hook(self):
        # 봇이 켜질 때 슬래시 명령어 동기화
        await self.tree.sync()
        # SEC 확인 스케줄러 시작
        self.check_sec_loop.start()

    async def on_ready(self):
        print(M["LOG_BOT_READY"].format(user=self.user, user_id=self.user.id))
        print("------")

    @tasks.loop(seconds=20.0)
    async def check_sec_loop(self):
        print(M["LOG_TASK_START"])
        all_subs = get_all_subscriptions()
        
        # 중복 조회를 방지하기 위해 ticker 단위로 유저 매핑
        ticker_to_users = {}
        for user_id_str, tickers in all_subs.items():
            for t in tickers:
                ticker_to_users.setdefault(t, []).append(user_id_str)
        
        active_tickers = [t for t, users in ticker_to_users.items() if users]
        if not active_tickers:
            return

        import asyncio
        # 병렬 처리를 위해 각 티커별 작업을 생성
        async def process_ticker(ticker):
            try:
                # check_new_filings는 동기 함수이므로 루프를 막지 않게 run_in_executor 사용 권장되나
                # 여기서는 단순화를 위해 직접 호출하거나 비동기 래핑 고려
                # 우선은 속도를 위해 병렬 실행 구조로 변경
                loop = asyncio.get_event_loop()
                new_filings = await loop.run_in_executor(None, check_new_filings, ticker)
                
                for filing in new_filings:
                    embed = discord.Embed(
                        title=M["EMBED_NEW_FILING_TITLE"].format(ticker=ticker, form_type=filing['form_type']),
                        url=filing.get("filing_html_url") or filing.get("filing_txt_url") or "https://www.sec.gov",
                        description=M["EMBED_NEW_FILING_DESC"].format(ticker=ticker, form_type=filing['form_type']),
                        color=discord.Color.blue()
                    )
                    embed.add_field(name=M["EMBED_FIELD_DATE"], value=filing.get("filing_date", M["EMBED_VALUE_NA"]), inline=True)
                    embed.add_field(name=M["EMBED_FIELD_ACC_NO"], value=filing.get("accession_no", M["EMBED_VALUE_NA"]), inline=True)
                    if filing.get("accepted_at"):
                        embed.add_field(name=M["EMBED_FIELD_ACCEPTED"], value=filing.get("accepted_at", M["EMBED_VALUE_NA"]), inline=False)
                    
                    channel_id = get_ticker_channel(ticker)
                    if channel_id:
                        channel = self.get_channel(int(channel_id))
                        if channel:
                            await channel.send(content=M["MENTION_NEW_FILING"], embed=embed)
            except Exception as e:
                print(M["LOG_TASK_ERR_CHECK"].format(ticker=ticker, err=e))

        # 모든 티커를 동시에 처리
        await asyncio.gather(*(process_ticker(t) for t in active_tickers))

    @check_sec_loop.before_loop
    async def before_check_sec_loop(self):
        await self.wait_until_ready()

bot = SECBot()

@bot.event
async def on_message(message: discord.Message):
    # 봇 자신이 보낸 메시지면 무시
    if message.author.bot:
        return

    # 관리자 채팅은 지우지 않음
    if message.author.guild_permissions.administrator:
        await bot.process_commands(message)
        return

    # 채널의 카테고리가 "알림"인지 확인 (티커 방들)
    if message.channel.category and message.channel.category.name == M["CATEGORY_NAME"]:
        try:
            # 유저의 채팅 메시지 삭제
            await message.delete()
            # 경고 메시지를 잠시 띄웠다가 5초 뒤에 자동 삭제
            await message.channel.send(M["CMD_WARN_CHAT_DISABLED"].format(mention=message.author.mention), delete_after=5.0)
        except discord.Forbidden:
            pass # 봇에게 메시지 삭제/전송 권한이 없는 경우 무시
        except discord.NotFound:
            pass # 이미 삭제된 메시지인 경우 무시
    
    # 봇의 기본 명령어 처리 로직 유지
    await bot.process_commands(message)

async def get_or_create_ticker_channel(guild: discord.Guild, ticker: str):
    ticker = ticker.upper()
    channel_id = get_ticker_channel(ticker)
    
    if channel_id:
        channel = guild.get_channel(int(channel_id))
        if channel:
            return channel
            
    # 카테고리 생성 또는 가져오기 ("알림"으로 변경)
    category_name = M["CATEGORY_NAME"]
    category = discord.utils.get(guild.categories, name=category_name)
    if not category:
        category = await guild.create_category(category_name)
        
    # 권한 설정: 기본적으로 아무도 못 봄, 봇은 볼 수 있고 메시지도 쓸 수 있음
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(
            read_messages=False,
            send_messages=False,
            create_public_threads=False,
            create_private_threads=False,
            send_messages_in_threads=False
        ),
        guild.me: discord.PermissionOverwrite(
            read_messages=True, 
            send_messages=True, 
            manage_messages=True, 
            embed_links=True
        )
    }
    
    # 디스코드 텍스트 채널은 시스템상 무조건 "소문자"만 지원하므로 소문자로 생성됩니다.
    # 대문자 입력 시 에러가 발생하므로 lower()를 유지해야 합니다.
    channel_name = ticker.lower()
    channel = await guild.create_text_channel(channel_name, category=category, overwrites=overwrites)
    
    set_ticker_channel(ticker, str(channel.id))
    return channel

@bot.tree.command(name="구독", description="특정 종목의 SEC 공시 알림을 구독합니다.")
async def subscribe_cmd(interaction: discord.Interaction, ticker: str):
    ticker = ticker.upper().strip()
    
    # 티커 유효성 검사 (sec_fetch에 로드된 목록에 있는지 확인)
    import sec.sec_fetch as fetch
    if ticker not in fetch.ticker_to_cik:
        await interaction.response.send_message(M["CMD_ERR_INVALID_TICKER"].format(ticker=ticker), ephemeral=True)
        return

    success = subscribe(str(interaction.user.id), ticker)
    
    if success:
        # 티커 채널 생성 혹은 가져오기
        channel = await get_or_create_ticker_channel(interaction.guild, ticker)
        
        # 해당 유저에게 채널 읽기 권한 부여, 쓰기 권한은 없음
        await channel.set_permissions(
            interaction.user, 
            read_messages=True, 
            send_messages=False,
            create_public_threads=False,
            create_private_threads=False,
            send_messages_in_threads=False
        )
        
        await interaction.response.send_message(M["CMD_SUB_SUCCESS"].format(ticker=ticker, channel_mention=channel.mention), ephemeral=True)
    else:
        # 이미 구독 중이어도 채널 권한 혹시 모르니 다시 세팅
        channel = await get_or_create_ticker_channel(interaction.guild, ticker)
        await channel.set_permissions(interaction.user, read_messages=True, send_messages=False)
        
        await interaction.response.send_message(M["CMD_SUB_ALREADY"].format(ticker=ticker, channel_mention=channel.mention), ephemeral=True)

@bot.tree.command(name="구독취소", description="특정 종목의 SEC 공시 알림 구독을 취소합니다.")
async def unsubscribe_cmd(interaction: discord.Interaction, ticker: str):
    ticker = ticker.upper()
    success = unsubscribe(str(interaction.user.id), ticker)
    
    if success:
        channel_id = get_ticker_channel(ticker)
        if channel_id:
            channel = interaction.guild.get_channel(int(channel_id))
            if channel:
                # 유저의 해당 채널 권한 덮어쓰기 삭제 (채널에서 안 보이게 됨)
                await channel.set_permissions(interaction.user, overwrite=None)
                
        await interaction.response.send_message(M["CMD_UNSUB_SUCCESS"].format(ticker=ticker), ephemeral=True)
    else:
        await interaction.response.send_message(M["CMD_UNSUB_NOT_SUBBED"].format(ticker=ticker), ephemeral=True)

@bot.tree.command(name="목록", description="현재 구독 중인 종목 목록을 확인합니다.")
async def list_cmd(interaction: discord.Interaction):
    tickers = get_subscriptions(str(interaction.user.id))
    if tickers:
        ticker_mentions = []
        for t in tickers:
            ch_id = get_ticker_channel(t)
            if ch_id:
                ticker_mentions.append(f"<#{ch_id}>")
            else:
                ticker_mentions.append(t)
        
        ticker_list = ", ".join(ticker_mentions)
        await interaction.response.send_message(M["CMD_LIST_RESULT"].format(ticker_list=ticker_list), ephemeral=True)
    else:
        await interaction.response.send_message(M["CMD_LIST_EMPTY"], ephemeral=True)

@bot.tree.command(name="테스트공시", description="(관리자 전용) 특정 종목의 가짜 공시 알림을 테스트로 전송합니다.")
@discord.app_commands.default_permissions(administrator=True)
async def test_filing_cmd(interaction: discord.Interaction, ticker: str):
    ticker = ticker.upper()
    channel_id = get_ticker_channel(ticker)
    
    if not channel_id:
        await interaction.response.send_message(M["CMD_TEST_NO_ROOM"].format(ticker=ticker), ephemeral=True)
        return
        
    channel = interaction.guild.get_channel(int(channel_id))
    if not channel:
        await interaction.response.send_message(M["CMD_TEST_NO_CHANNEL"].format(ticker=ticker), ephemeral=True)
        return

    embed = discord.Embed(
        title=M["CMD_TEST_EMBED_TITLE"].format(ticker=ticker),
        url="https://www.sec.gov",
        description=M["CMD_TEST_EMBED_DESC"].format(ticker=ticker),
        color=discord.Color.red()
    )
    embed.add_field(name=M["EMBED_FIELD_DATE"], value="2026-03-23", inline=True)
    embed.add_field(name=M["EMBED_FIELD_ACC_NO"], value="0001234567-89-012345", inline=True)
    
    await channel.send(content=M["CMD_TEST_MENTION"], embed=embed)
    await interaction.response.send_message(M["CMD_TEST_SUCCESS"].format(ticker=ticker), ephemeral=True)
