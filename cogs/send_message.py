import discord
from discord.ext import commands
from discord import app_commands
import datetime
import pytz
from utils.logging_utils import append_to_log
from config import LOG_FILE

class SendMessage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='관리자메시지', description="동명봇이 사용자의 메시지를 관리자에게 DM을 보냅니다.")
    @app_commands.describe(메시지="보낼 메시지를 입력하세요")
    async def cafeteria_menu(self, interaction: discord.Interaction, 메시지: str = None):
        await interaction.response.defer()
        try:
            admin_id = '424425205343977475'  # 여기에 관리자 디스코드 ID를 입력하세요.
            admin_user = await self.bot.fetch_user(admin_id)
            
            embed = discord.Embed(title=f":mailbox_with_no_mail:DM to 관리자:mailbox_with_mail: ", description="", timestamp=datetime.datetime.now(pytz.timezone('UTC')), color=0x00b992)
            embed.add_field(name=f"{interaction.user.name}님이 보내는 메시지...", value=f"내용: {메시지}\n\n", inline=False)
            embed.add_field(name=" ", value=f"관리자에게 DM을 성공적으로 보냈습니다.\n\n", inline=False)
            
                       
            printf=f'({interaction.user.name}님의 입력)_관리자에게 DM을 성공적으로 보냈습니다.\n내용: {메시지}'
            print(printf)
            append_to_log(printf, LOG_FILE)

            embed.set_footer(text="Bot Made by. @k_shus, 자유롭게 이용해 주세요.😄")
            await interaction.followup.send(embed=embed)
            await admin_user.send(embed=embed)
            
        except Exception as e:
            error_message = f"관리자에게 DM을 보내는 중 오류가 발생했습니다:\n```\n{type(e).__name__}: {str(e)}\n```"
            printf=f'({interaction.user.name}님의 입력)_DM 오류 출력\n내용: {메시지}\n\n{error_message}'
            print(printf)
            append_to_log(printf, LOG_FILE)
            await interaction.followup.send(error_message)

async def setup(bot):
    await bot.add_cog(SendMessage(bot))
