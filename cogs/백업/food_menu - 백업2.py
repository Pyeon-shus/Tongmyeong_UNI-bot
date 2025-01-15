import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import aiohttp
import requests
from bs4 import BeautifulSoup
import datetime
import pytz
from utils.logging_utils import append_to_log
from config import LOG_FILE

class FoodMenu(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()

    @app_commands.command(name='학식', description="오늘의 학식 메뉴를 보여줍니다.")
    async def cafeteria_menu(self, interaction: discord.Interaction):
        await interaction.response.defer()
        try:
            url = 'https://www.tu.ac.kr/tuhome/diet.do?sch'
            async with self.session.get(url) as response:
                html = await response.text()
            
            soup = BeautifulSoup(html, 'html.parser')

            table = soup.find('div', class_='table-wrap')

            yangsik = []
            myeonryu = []
            bunsik = []
            teukjeongsik = []
            ddukbaegi = []
            ilpum = []
            won = []
            
            if table:
                for tr in table.find_all('tr'):
                    th = tr.find('th')
                    td = tr.find('td')
                    row = []
                    if th and td:
                        if th.text == '양식':
                            row.append(td.text)
                            yangsik.append(row)
                        elif th.text == '면류':
                            row.append(td.text)
                            myeonryu.append(row)
                        elif th.text == '분식':
                            row.append(td.text)
                            bunsik.append(row)
                        elif th.text == '특정식':
                            row.append(td.text)
                            teukjeongsik.append(row)
                        elif th.text == '뚝배기':
                            row.append(td.text)
                            ddukbaegi.append(row)
                        elif th.text == '일품':
                            row.append(td.text)
                            ilpum.append(row)
                        elif th.text == '천원의 아침밥':
                            row.append(td.text)
                            won.append(row)

                embed = discord.Embed(title=":fork_and_knife:오늘의 학식:fork_and_knife:", description="",timestamp=datetime.datetime.now(pytz.timezone('UTC')), color=0x00b992)
                embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/4474/4474873.png")
                embed.add_field(name="\n", value=f"\n", inline=False)
                
                for menu, title in [(yangsik, "🍳 #양식"), (myeonryu, "🍜 #면류"), (bunsik, "🍥 #분식"), 
                                    (teukjeongsik, " #🍚특정식"), (ddukbaegi, "🫕 #뚝배기"), (ilpum, "🍛 #일품"), (won, "💶 #천원의 아침밥")]:
                    if len(menu) > 0:
                        result = '\n'.join(['\n'.join(row) for row in menu])
                        embed.add_field(name=f"**{title}**", value=f"{result}\n\n", inline=False)

                embed.add_field(name=" ", value=f"식단 출처: {url}\n\n", inline=False)
                embed.set_footer(text="Bot Made by. @k_shus, 자유롭게 이용해 주세요.😄")
                
                printf=f'({interaction.user.name}님의 입력)_학식 정상 출력됨'
                print(printf)
                append_to_log(printf, LOG_FILE)
                await interaction.followup.send(embed=embed)
            else:
                embed = discord.Embed(title=":fork_and_knife:오늘의 학식:fork_and_knife:", description="",timestamp=datetime.datetime.now(pytz.timezone('UTC')), color=0x96C81E)
                embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/4474/4474873.png")
                embed.add_field(name="\n", value=f"\n", inline=False)
                embed.add_field(name="⚠️오늘 등록된 식단메뉴가 없습니다⚠️", value=f"", inline=False)
                embed.add_field(name="\n", value=f"\n", inline=False)
                embed.add_field(name=" ", value=f"식단 출처: {url}\n\n", inline=False)
                embed.set_footer(text="Bot Made by. @k_shus, 자유롭게 이용해 주세요.😄")
                
                printf=f'({interaction.user.name}님의 입력)_학식 정상 출력됨 (메뉴 없음)'
                print(printf)
                append_to_log(printf, LOG_FILE)
                await interaction.followup.send(embed=embed)
        except Exception as e:
            error_message = f"메뉴를 가져오는 중 오류가 발생했습니다:\n```\n{type(e).__name__}: {str(e)}\n```"
            printf=f'({interaction.user.name}님의 입력)_학식 오류 출력됨\n{error_message}'
            print(printf)
            append_to_log(printf, LOG_FILE)
            await interaction.followup.send(error_message)

    @app_commands.command(name='숙식', description="오늘의 기숙사 식단을 보여줍니다.")
    async def dormitory_menu(self, interaction: discord.Interaction):
        await interaction.response.defer()
        try:
            url = "https://www.tu.ac.kr/dormitory/sub06_06.do?mode=wList"
            res = requests.get(url)
            soup = BeautifulSoup(res.text, "html.parser")
            box_list = soup.find_all("div", {"class": "b-cal-content-box no-list"})
            
            today_s = datetime.datetime.now(pytz.timezone('UTC')).strftime("%Y.%m.%d")
            
            breakfast_menu_str = ""
            dinner_menu_str = ""

            for box in box_list:
                date_box = box.find("p", {"class": "b-cal-date"})
                date_value = ""
                if date_box:
                    date_text = date_box.find("span").text.strip()
                    date_value = date_text.split("(")[0]

                if date_value == today_s:
                    menu_list = box.find_all("ul", {"class": "b-cal-undergrad"})
                        
                    embed = discord.Embed(title=":fork_and_knife:오늘의 숙식:fork_and_knife:", description="",timestamp=datetime.datetime.now(pytz.timezone('UTC')), color=0x00b992)
                    embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/4916/4916579.png")
                    embed.add_field(name="\n", value=f"\n", inline=False)

                    for menu in menu_list:
                        menu_items = menu.find_all("li")
                        for item in menu_items:
                            menu_text = item.text.strip()
                            menu_split = menu_text.split(":")
                            if menu_split[0] == "조식 ":
                                breakfast_menu_str += menu_split[1] + "\n"
                            elif menu_split[0] in ["A코스 ", "B코스 "]:
                                breakfast_menu_str += menu_text + "\n"
                            elif menu_split[0] == "석식 ":
                                dinner_menu_str += menu_split[1] + "\n"
            
            embed.add_field(name=f"{today_s}숙식", value=f"\n", inline=False)
            embed.add_field(name="\n", value=f"\n", inline=False)                       
            
            embed.add_field(name="**☀️ #조식**", value=breakfast_menu_str if breakfast_menu_str else "오늘 조식 메뉴가 없습니다.", inline=False)
            embed.add_field(name="\n", value=f"\n", inline=False)
            
            embed.add_field(name="**🌙 #석식**", value=dinner_menu_str if dinner_menu_str else "오늘 석식 메뉴가 없습니다.", inline=False)
            embed.add_field(name="\n", value=f"\n", inline=False)
            
            embed.add_field(name=" ", value=f"식단 출처: {url}\n\n", inline=False)
            embed.set_footer(text="Bot Made by. @k_shus, 자유롭게 이용해 주세요.😄")
            
            printf=f'({interaction.user.name}님의 입력)_숙식 정상 출력됨'
            print(printf)
            append_to_log(printf, LOG_FILE)
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            error_message = f"메뉴를 가져오는 중 오류가 발생했습니다:\n```\n{type(e).__name__}: {str(e)}\n```"
            printf=f'({interaction.user.name}님의 입력)_숙식 오류 출력됨\n{error_message}'
            print(printf)
            append_to_log(printf, LOG_FILE)
            await interaction.followup.send(error_message)

async def setup(bot):
    await bot.add_cog(FoodMenu(bot))
