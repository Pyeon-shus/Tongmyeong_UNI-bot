import discord
from discord.ext import commands
from discord import app_commands
import datetime
import pytz
from utils.logging_utils import append_to_log
from config import LOG_FILE

class Introduce(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='소개', description="동명봇의 자기 소개를 보여줍니다.")
    async def introduce(self, interaction: discord.Interaction):
        await interaction.response.defer()
        try:
            embed = discord.Embed(
                title=":fork_and_knife:동명봇 소개:fork_and_knife:", 
                description="",
                timestamp=datetime.datetime.now(pytz.timezone('UTC')), 
                color=0x00b992
            )
            embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/4712/4712123.png")
            embed.add_field(name="\n", value="\n", inline=False)
            embed.add_field(name="😲많은 이용부탁 드립니다!😲", value="", inline=False)
            embed.add_field(name="\n", value="\n", inline=False)
            
            commands_list = [command.name for command in self.bot.tree.get_commands()]
            embed.add_field(name="#현재 실행중인 명령어", value=f"/{', /'.join(commands_list)}", inline=False)
            
            embed.add_field(name="\n", value="\n", inline=False)
            embed.set_footer(text="Bot Made by. @k_shus, 자유롭게 이용해 주세요.😄")
            
            printf = f'({interaction.user.name}님의 입력)_소개 정상 출력됨'
            print(printf)
            append_to_log(printf, LOG_FILE)
            
            await interaction.followup.send(embed=embed)
        
        except Exception as e:
            error_message = f"메시지를 가져오는 중 오류가 발생했습니다:\n```\n{type(e).__name__}: {str(e)}\n```"
            printf = f'({interaction.user.name}님의 입력)_소개 오류 출력됨\n{error_message}'
            print(printf)
            append_to_log(printf, LOG_FILE)
            await interaction.followup.send(error_message)

async def setup(bot):
    await bot.add_cog(Introduce(bot))
