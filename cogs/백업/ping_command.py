import discord
from discord.ext import commands
from discord import app_commands

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
        await interaction.followup.send(embed=embed)  # 응답 후속 조치

async def setup(bot):
    await bot.add_cog(PingCommand(bot))