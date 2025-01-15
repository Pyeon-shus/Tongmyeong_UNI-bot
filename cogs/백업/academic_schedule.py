import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import requests
from bs4 import BeautifulSoup
import datetime
import pytz
from utils.logging_utils import append_to_log
from config import LOG_FILE

class AcademicSchedule(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='학사일정', description="선택한 월의 학사 일정을 보여줍니다.(3~12월=>올해, 1~2월=>다음 해)")
    @app_commands.describe(달월="검색하고 싶은 월을 선택하세요(기본값은 현재 월입니다)")
    @app_commands.choices(달월=[
        app_commands.Choice(name="1월", value=1),
        app_commands.Choice(name="2월", value=2),
        app_commands.Choice(name="3월", value=3),
        app_commands.Choice(name="4월", value=4),
        app_commands.Choice(name="5월", value=5),
        app_commands.Choice(name="6월", value=6),
        app_commands.Choice(name="7월", value=7),
        app_commands.Choice(name="8월", value=8),
        app_commands.Choice(name="9월", value=9),
        app_commands.Choice(name="10월", value=10),
        app_commands.Choice(name="11월", value=11),
        app_commands.Choice(name="12월", value=12)
    ])
    async def academic_schedule(self, interaction: discord.Interaction, 달월: app_commands.Choice[int] = None):
        await interaction.response.defer()

        selected_month = 달월.value if 달월 else datetime.datetime.now().month
        
        try:
            url = 'https://www.tu.ac.kr/tuhome/scheduleTable.do'
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')

            schedule = []
            month_found = False

            for tr in soup.find_all('tr', class_='notice'):
                month_header = tr.find('th', class_='name')
                
                if month_header:
                    month = int(month_header.text.strip().rstrip('월'))
                    if month == selected_month:
                        month_found = True
                    elif month_found:
                        break
                
                if month_found:
                    date_td = tr.find('td', class_='name')
                    event_td = tr.find('td', class_='subject')
                    
                    if date_td and event_td:
                        date = date_td.text.strip()
                        event = event_td.text.strip()
                        
                        # 날짜와 요일 구분
                        date_parts = date.split('~')
                        start_date = date_parts[0].strip()
                        end_date = date_parts[1].strip() if len(date_parts) > 1 else ""
                        
                        start_day = start_date.split('(')[1].rstrip(')') if '(' in start_date else ""
                        start_date = start_date.split('(')[0].strip() if '(' in start_date else start_date
                        
                        end_day = end_date.split('(')[1].rstrip(')') if '(' in end_date else ""
                        end_date = end_date.split('(')[0].strip() if '(' in end_date else end_date
                        
                        start_date = start_date.replace('.0','월 ')
                        start_date = start_date.replace('.','월 ')
                        
                        if end_date:
                            end_date = end_date.replace('.0','월 ')
                            end_date = end_date.replace('.','월 ')
                            date_range = f"{start_date}일_({start_day}요일) ~ {end_date}일_({end_day}요일)"
                        else:
                            date_range = f"{start_date}일_({start_day}요일)"
                        
                        schedule.append({
                            'date': date_range,
                            'event': event
                        })
            if(selected_month>2):
                embed = discord.Embed(title=f":calendar_spiral: {datetime.datetime.now().year}년 {selected_month}월 학사 일정 :calendar_spiral:", description="", timestamp=datetime.datetime.now(pytz.timezone('UTC')), color=0x00b992)
            else:
                embed = discord.Embed(title=f":calendar_spiral: {datetime.datetime.now().year+1}년 {selected_month}월 학사 일정 :calendar_spiral:", description="", timestamp=datetime.datetime.now(pytz.timezone('UTC')), color=0x00b992)
                
            for item in schedule:
                embed.add_field(name=item['date'], value=item['event'], inline=False)
            embed.add_field(name=" ", value=f"출처: {url}\n\n", inline=False)
            embed.set_footer(text="Bot Made by. @k_shus, 자유롭게 이용해 주세요.😄")
            if(selected_month>2):
                printf=f'({interaction.user.name}님의 입력)_{datetime.datetime.now().year}년 {selected_month}월 학사일정 정상 출력됨'
            else:
                printf=f'({interaction.user.name}님의 입력)_{datetime.datetime.now().year+1}년 {selected_month}월 학사일정 정상 출력됨'
            print(printf)
            append_to_log(printf, LOG_FILE)
            await interaction.followup.send(embed=embed)
        except Exception as e:
            error_message = f"날씨 정보를 가져오는 중 오류가 발생했습니다:\n```\n{type(e).__name__}: {str(e)}\n```"
            if(selected_month>2):
                printf=f'({interaction.user.name}님의 입력)_{datetime.datetime.now().year}년 {selected_month}월 오류 출력\n{error_message}'
            else:
                printf=f'({interaction.user.name}님의 입력)_{datetime.datetime.now().year+1}년 {selected_month}월 오류 출력\n{error_message}'
            print(printf)
            append_to_log(printf, LOG_FILE)
            await interaction.followup.send(error_message)


async def setup(bot):
    await bot.add_cog(AcademicSchedule(bot))
