import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
import pytz
import aiohttp
from bs4 import BeautifulSoup
from utils.logging_utils import append_to_log
from config import LOG_FILE

class Shuttle_timetable(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.vacation_periods = None

    @app_commands.command(name='셔틀', description="셔틀 시간표를 확인합니다.")
    @app_commands.describe(시간표="'학기 중' 또는 '방학 중'을 입력하면 각각의 시간표를 보여줍니다.")
    #@app_commands.choices(시간표=[
    #    app_commands.Choice(name="학기 중", value=1),
    #    app_commands.Choice(name="방학 중", value=0),
    #])
    async def shuttle(self, interaction: discord.Interaction, 시간표: str = None):
        try:
            await interaction.response.defer()

            # 평일 확인
            weekday = datetime.now(pytz.timezone('Asia/Seoul')).strftime('%A')
            if weekday in ['Saturday', 'Sunday']:
                await interaction.followup.send("주말에는 셔틀 운행이 없습니다.")
                return

            # 학사 일정 크롤링
            if self.vacation_periods is None:
                self.vacation_periods = await self.crawl_academic_calendar()

            # 현재 날짜
            current_date = datetime.now(pytz.timezone('Asia/Seoul'))

            # 방학 기간 확인
            is_vacation = self.check_vacation_period(current_date)

            # 셔틀 시간표 (예시)
            shuttle_times = {
                'semester': [
                    '08:00', '08:10', '08:16', '08:23', '08:30', '08:37',
                    '08:43', '08:52', '08:59', '09:07', '09:12', '09:19',
                    '09:25', '09:31', '09:37', '09:45', '10:00', '10:15',
                    '10:30', '10:45', '11:00', '11:30', '12:00', '12:30',
                    '13:00', '13:10', '13:20', '13:30', '13:40', '13:50',
                    '14:00', '14:30', '15:00', '15:30', '16:00', '16:10',
                    '16:20', '16:30', '16:40', '17:00', '17:10', '17:20',
                    '17:30', '17:50', '18:00', '18:10', '18:20', '18:30',
                    '18:40', '18:50', '19:00', '19:10'
                ],
                'vacation': [
                    '09:00', '09:20', '09:40', '10:00','10:20', 
                    '10:40','11:00', '15:20', '15:40', '16:00', 
                    '16:20', '16:40', '17:00'
                ]
            }

            if 시간표 in ["학기 중", "방학 중"]:
                await self.send_timetable(interaction, 시간표, shuttle_times)
            else:
                await self.send_next_shuttle(interaction, is_vacation, shuttle_times, current_date)
        except Exception as e:
            printf = f"오류: {e}"
            print(printf)
            append_to_log(printf, LOG_FILE)
            await interaction.followup.send(f"셔틀 명령어 실행 중 오류가 발생했습니다: {str(e)}")

    async def crawl_academic_calendar(self):
        url = "https://www.tu.ac.kr/tuhome/scheduleTable.do"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                html = await response.text()
        
        soup = BeautifulSoup(html, 'html.parser')
        calendar_div = soup.find('div', class_='subConBox common')
        
        vacations = {
            'summer': None,
            'winter1': None,
            'winter2': None
        }

        for tr in calendar_div.find_all('tr', class_='notice'):
            month = tr.find('th', class_='name')
            if month:
                current_month = month.text.strip()
            
            subject = tr.find('td', class_='subject')
            if subject and '방학' in subject.text:
                date = tr.find('td', class_='name').text
                if '하계방학' in subject.text:
                    vacations['summer'] = f"{current_month} {date}"
                elif '동계방학' in subject.text:
                    if not vacations['winter1']:
                        vacations['winter1'] = f"{current_month} {date}"
                    else:
                        vacations['winter2'] = f"{current_month} {date}"

        return vacations

    def normalize_date(self, date_str, current_year):
        # 날짜 형식을 정규화하는 함수
        if '년' in date_str:
            # 2025년 2월 28일 형식 처리
            return f"{date_str.replace('년 ', '-').replace('월 ', '-').replace('일', '')}"
        elif '월' in date_str:
            # 8월 31일 형식 처리
            return f"{current_year}-{date_str.replace('월 ', '-').replace('일', '')}"
        elif len(date_str.split('.')) == 3:
            # 2025.2.28 형식 처리
            return date_str.replace('.', '-').replace(' ', '')
        else:
            # 다른 형식 처리
            if '.' in date_str:
                return f"{current_year}-{date_str.replace('.', '-').replace(' ', '')}"
            
    def check_vacation_period(self, current_date):
        current_year = current_date.year
        current_date = current_date.replace(tzinfo=pytz.timezone('Asia/Seoul'))  # Remove timezone info for comparison
        for vacation_period in self.vacation_periods.values():
            if vacation_period:
                start, end = vacation_period.split('~')
                # 요일 제거
                start = start.split('(')[0].strip()
                end = end.split('(')[0].strip()

                # 날짜 정규화
                start = self.normalize_date(start, current_year)
                end = self.normalize_date(end, current_year)

                # 날짜 변환
                try:
                    start_date = datetime.strptime(start, "%Y-%m-%d").replace(tzinfo=pytz.timezone('Asia/Seoul'))
                    end_date = datetime.strptime(end, "%Y-%m-%d").replace(tzinfo=pytz.timezone('Asia/Seoul'))
                except ValueError:
                    continue

                if start_date <= current_date <= end_date:
                    return True
        return False
    

    async def send_timetable(self, interaction, is_vacation, shuttle_times):
        timetable = shuttle_times['vacation'] if is_vacation else shuttle_times['semester']
        
        # 시간표 항목 처리
        formatted_times = ''
        for idx, time in enumerate(timetable):
            if idx % 6 == 0 and idx > 0:
                formatted_times += '\n'
            if idx % 2 == 0:
                formatted_times += f'`{time}`  '
            else:
                formatted_times += f'{time}  '
        
        # 임베드 생성
        embed = discord.Embed(title="셔틀 시간표", description=f"{'방학 중' if is_vacation else '학기 중'} 시간표:\n{formatted_times}", color=discord.Color.green())
        await interaction.followup.send(embed=embed)

    async def send_next_shuttle(self, interaction, is_vacation, shuttle_times, current_date):
        current_time = current_date.strftime("%H:%M")
        upcoming_shuttles = []
        
        # 선택된 셔틀 시간표에서 다음 셔틀 찾기
        times = shuttle_times['vacation'] if is_vacation else shuttle_times['semester']
        for time in times:
            if time > current_time:
                upcoming_shuttles.append(time)

        # 임베드 색상 계산
        current_hour = current_date.hour
        if current_hour < 12:
            embed_color = discord.Color.blue()  # 아침
        elif current_hour < 18:
            embed_color = discord.Color.orange()  # 오후
        elif current_hour < 19:
            embed_color = discord.Color.dark_red()  # 저녁
        else:
            embed_color = discord.Color.dark_blue()  # 밤

        # 임베드 생성
        embed = discord.Embed(title="다음 셔틀", color=embed_color)

        if not upcoming_shuttles:
            embed.description = "지금 현재 운행 중인 셔틀이 없습니다!"
        else:
            for time in upcoming_shuttles[:5]:  # 최대 5개까지 표시
                time_diff = datetime.strptime(time, "%H:%M") - datetime.strptime(current_time, "%H:%M")
                minutes_left = time_diff.total_seconds() / 60
                embed.add_field(name=f"**{time}**", value=f"`{int(minutes_left)}분 남았습니다`", inline=False)
        printf = f"정상출력"
        print(printf)
        append_to_log(printf, LOG_FILE)
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Shuttle_timetable(bot))
