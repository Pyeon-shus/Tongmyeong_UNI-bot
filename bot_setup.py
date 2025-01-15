import discord
from discord.ext import commands
from config import PREFIX

def create_bot():
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    intents.guilds = True  # 서버 관련 이벤트를 수신하기 위해 intents.guilds를 True로 설정합니다.
    return commands.Bot(command_prefix=PREFIX, intents=intents)