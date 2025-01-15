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

class Weather(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()

    @app_commands.command(name='날씨', description="지정된 위치의 날씨 정보를 보여줍니다.")
    @app_commands.describe(
        위치="미리 정의된 위치 중 선택",
        검색="직접 위치 입력 (위치를 선택하지 않았을 때 사용)"
    )
    @app_commands.choices(위치=[
        app_commands.Choice(name="대연동", value="대연동"),
        app_commands.Choice(name="용당동", value="용당동"),
        app_commands.Choice(name="용호동", value="용호동"),
        app_commands.Choice(name="광안리", value="광안리"),
    ])
    async def weather(self, interaction: discord.Interaction, 위치: app_commands.Choice[str] = None, 검색: str = None):
        await interaction.response.defer()
        
        if 위치 is None and 검색 is None:
            await interaction.followup.send("위치를 선택하거나 검색어를 입력해주세요.")
            return

        query = 위치.value if 위치 else 검색
        
        try:
            url = f'https://search.naver.com/search.naver?query={query}+날씨'
            async with self.session.get(url) as response:
                html = await response.text()
            
            res = requests.get(url)
            weather = BeautifulSoup(res.text, "html.parser")

            box = weather.find("div", {"class": "weather_info"})
            box_1 = weather.find("div", {"class": "day_data"})

            temperature = box.find("strong").text.replace("현재 온도", "")
            weather_status = box.find("span", {"class": "weather before_slash"}).text

            weather_time_status = box_1.find("div", {"class": "cell_weather"})

            morning_status = weather_time_status.find("strong", {"class": "time"}, string="오전")
            morning_rainfall = morning_status.find_next("span", {"class": "rainfall"}).text
            morning_icon = morning_status.find_next("i", {"class": "wt_icon"}).find_next("span", {"class": "blind"}).text

            afternoon_status = weather_time_status.find("strong", {"class": "time"}, string="오후")
            afternoon_rainfall = afternoon_status.find_next("span", {"class": "rainfall"}).text
            afternoon_icon = afternoon_status.find_next("i", {"class": "wt_icon"}).find_next("span", {"class": "blind"}).text

            temperature_change_element = box.find("span", {"class": "temperature down"})
            if temperature_change_element is None:
                temperature_change_element = box.find("span", {"class": "temperature up"})
            temperature_change_text = temperature_change_element.contents[0].strip()
            blind_element = temperature_change_element.find_next("span", {"class": "blind"})
            blind_text = blind_element.text.strip()

            summary_list = box.find("dl", {"class": "summary_list"})
            perceived_temperature = summary_list.find("dt", string="체감").find_next("dd").text
            humidity = summary_list.find("dt", string="습도").find_next("dd").text
            wind_direction = summary_list.find("dt", string=lambda text: text and "풍" in text).text
            wind_speed = summary_list.find("dt", string=lambda text: text and "풍" in text).find_next("dd").text

            chart_list = weather.find("ul", {"class": "today_chart_list"})

            fine_dust = chart_list.find("strong", string="미세먼지").find_next("span", {"class": "txt"}).text
            ultrafine_dust = chart_list.find("strong", string="초미세먼지").find_next("span", {"class": "txt"}).text
            uv_index = chart_list.find("strong", string="자외선").find_next("span", {"class": "txt"}).text

            sunrise_element = chart_list.find("strong", string=lambda text: text and ("일출" in text or "일몰" in text))
            if sunrise_element is not None:
                time_type = "일출" if "일출" in sunrise_element.text else "일몰"
                sunrise = sunrise_element.find_next("span", {"class": "txt"}).text

            embed = discord.Embed(title=f":white_sun_small_cloud:{query} 현재 날씨:white_sun_small_cloud:", description="",timestamp=datetime.datetime.now(pytz.timezone('UTC')), color=0x00b992)
            embed.set_thumbnail(url="https://cdn-1.webcatalog.io/catalog/naver-weather/naver-weather-icon-filled-256.webp?v=1675613733392")
            embed.add_field(name="\n", value=f"\n", inline=False)
            embed.add_field(name=f"현재 온도 {temperature}C", value=f"어제 보다 {temperature_change_text}C {blind_text}\n체감 온도는 {perceived_temperature}C 입니다.", inline=True)
            embed.add_field(name=f"{time_type}\n", value=f"{sunrise}\n", inline=True)
            embed.add_field(name="\n", value=f"\n", inline=False)
            embed.add_field(name="날씨\n", value=f"{weather_status}\n", inline=True)
            embed.add_field(name="습도\n", value=f"{humidity}\n", inline=True)
            embed.add_field(name=f"{wind_direction}\n", value=f"{wind_speed}\n", inline=True)

            embed.add_field(name="\n", value=f"\n", inline=False)
            embed.add_field(name="미세먼지\n", value=f"{fine_dust}\n", inline=True)
            embed.add_field(name="초미세먼지\n", value=f"{ultrafine_dust}\n", inline=True)
            embed.add_field(name="자외선 지수\n", value=f"{uv_index}\n", inline=True)

            embed.add_field(name="\n", value=f"\n", inline=False)
            embed.add_field(name="\n", value=f"\n", inline=False)
            embed.add_field(name="정보/시간\n", value=f"강수 확률\n날씨 정보", inline=True)
            embed.add_field(name="오전\n", value=f"{morning_rainfall}\n{morning_icon}\n", inline=True)
            embed.add_field(name="오후\n", value=f"{afternoon_rainfall}\n{afternoon_icon}\n", inline=True)

            embed.add_field(name="\n", value=f"\n", inline=False)
            embed.set_footer(text="Bot Made by. @k_shus, 자유롭게 이용해 주세요.😄")

            printf=f'({interaction.user.name}님의 입력)_{query} 날씨 정상 출력됨'
            print(printf)
            append_to_log(printf, LOG_FILE)
            await interaction.followup.send(embed=embed)
        except Exception as e:
            error_message = f"날씨 정보를 가져오는 중 오류가 발생했습니다:\n```\n{type(e).__name__}: {str(e)}\n```"
            printf=f'({interaction.user.name}님의 입력)_{query} 날씨 오류 출력\n{error_message}'
            print(printf)
            append_to_log(printf, LOG_FILE)
            await interaction.followup.send(error_message)

async def setup(bot):
    await bot.add_cog(Weather(bot))
