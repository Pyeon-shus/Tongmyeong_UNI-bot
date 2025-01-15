import discord
from discord.ext import commands
from discord import app_commands
from utils.logging_utils import append_to_log
from config import LOG_FILE

class PingCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="핑", description="서버 컴퓨터에 핑을 보냅니다")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.defer()  # 응답 지연
        latency_time = round(self.bot.latency * 1000)  # ms 단위로 변환
        embed = discord.Embed(
            title="퐁!",
            description=f"응답 속도는 **{latency_time}ms**입니다!",
            color=0x00ff00  # 초록색
        )
        printf=f'({interaction.user.name}님의 입력)_핑 출력\n속도: {latency_time}ms'
        print(printf)
        append_to_log(printf, LOG_FILE)

        await interaction.followup.send(embed=embed)  # 응답 후속 조치

async def setup(bot):
    await bot.add_cog(PingCommand(bot))