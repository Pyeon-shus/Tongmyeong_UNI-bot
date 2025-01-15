import signal
import sys
import asyncio
import discord
from discord.ext import commands
from config import TOKEN, ADMIN
from bot_setup import create_bot
from utils.bot_utils import load_extensions
from utils.logging_utils import append_to_log
from config import LOG_FILE
from time_manager import cal,write

def graceful_exit(signum, frame):
    print(f"신호 {signum} 감지. write() 실행 중...")
    write()
    sys.exit(0)

# 종료 신호 처리 등록
signal.signal(signal.SIGINT, graceful_exit)  # Ctrl+C
signal.signal(signal.SIGTERM, graceful_exit)  # Termination Signal

bot = create_bot()

@bot.event
async def on_ready():
    try:
        print("Syncing commands...")
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"동기화 중 오류 발생: {e}")
    printf=f'\n\n==================================\n{bot.user}봇이 온라인 입니다!\n공백기: [{cal()}]\n현재 {len(bot.guilds)}개의 서버에서 봇을 사용중!\n'
    print(printf)
    append_to_log(printf, LOG_FILE)
    #print(f'\n\n==================================\n{bot.user}봇이 온라인 입니다!')
    admin_user = await bot.fetch_user(ADMIN)
    await admin_user.send(f" # :battery:봇이 성공적으로 온라인이 되었습니다:battery:") 
    await admin_user.send(f" ## :white_check_mark:현재 {len(bot.guilds)}개의 서버에서 봇을 사용중!")
    for guild in bot.guilds:
        await admin_user.send(f' - {guild.name} (ID: {guild.id})')
    await admin_user.send(f'==================================')

    await bot.change_presence(activity=discord.Game(name='명령어 입력대기'))

async def main():
    async with bot:
        await load_extensions(bot)
        try:
            await bot.start(TOKEN)
        except Exception as e:
            print(f"봇 실행 중 오류 발생: {e}")

if __name__ == '__main__':
    asyncio.run(main())