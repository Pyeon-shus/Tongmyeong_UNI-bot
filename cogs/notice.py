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

class Notice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='학교공지', description="최근 공지 5개를 보여주거나 검색을 할 수 있습니다")
    @app_commands.describe(검색="검색하고 키워드를 입력하세요(기본값은 최근 공지 5개 입니다)")
    async def notification(self, interaction: discord.Interaction, 검색: str = None):
        await interaction.response.defer()
        query = f"?mode=list&srSearchKey=&srSearchVal={검색}" if 검색 else ""
        
        try:
            url_O = 'https://www.tu.ac.kr/tuhome/sub07_01_01.do'
            url_P = f'{url_O}{query}'
            res = requests.get(url_P)

            # BeautifulSoup를 사용하여 HTML 파싱
            soup = BeautifulSoup(res.text, 'html.parser')

            # 공지사항 테이블의 행을 찾는 부분
            rows = soup.select('table.listTypeA tbody tr')

            # 공지사항 데이터를 저장할 배열
            notices = []

            # 최대 5개의 공지사항을 추출
            for row in rows[:5]:
                num = row.select_one('td.num').text.strip()
                title = row.select_one('td.subject a').text.strip()
                link = row.select_one('td.subject a')['href']
                author = row.select_one('td.name').text.strip()
                date = row.select_one('td.data').text.strip()
                hits = row.select_one('td.hit').text.strip()
                attachment = "첨부파일 있음" if row.select_one('td.file img') else "첨부파일 없음"
                
                notices.append({
                    '번호': num,
                    '제목': title,
                    '링크': link,
                    '작성자': author,
                    '작성일': date,
                    '조회수': hits,
                    '첨부파일': attachment
                })

            embed = discord.Embed(title=f":mag:{검색}의 검색결과:mag:" if 검색 else ":mag:최근 공지 5개:mag:", description="", timestamp=datetime.datetime.now(pytz.timezone('UTC')), color=0x00b992)
            embed.add_field(name=" ", value=f"출처: {url_P}\n\n", inline=False)
            
            # embed에 공지사항 추가
            for notice in notices:
                attachment_emoji = ":ballot_box_with_check:" if notice['첨부파일'] == "첨부파일 있음" else ":no_entry_sign:"
                embed.add_field(name=notice['제목'], value=f"작성일: {notice['작성일']} / 조회수: {notice['조회수']} / 작성자: {notice['작성자']}\n첨부파일: {attachment_emoji} / [자세히 보기]({url_O}{notice['링크']})", inline=False)
            
            printf=f'({interaction.user.name}님의 입력)_최근 공지 5개 및 {검색}의 검색결과 정상 출력'
            print(printf)
            append_to_log(printf, LOG_FILE)

            embed.set_footer(text="Bot Made by. @k_shus, 자유롭게 이용해 주세요.😄")
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            error_message = f"공지사항 정보를 가져오는 중 오류가 발생했습니다:\n```\n{type(e).__name__}: {str(e)}\n```"
            printf=f'({interaction.user.name}님의 입력)_최근 공지 5개 및 {검색}의 검색결과 오류 출력\n{error_message}'
            print(printf)
            append_to_log(printf, LOG_FILE)
            await interaction.followup.send(error_message)

async def setup(bot):
    await bot.add_cog(Notice(bot))
