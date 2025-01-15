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
        self.vacation_periods = None  # {'summer': "...", 'winter1': "...", 'winter2': "..."} 형식 예상

    @app_commands.command(name='셔틀', description="셔틀 시간표를 확인합니다.")
    @app_commands.describe(시간표="'학기 중' 또는 '방학 중'을 입력하면 각각의 시간표를 보여줍니다.")
    @app_commands.choices(시간표=[
        app_commands.Choice(name="학기 중", value=1),
        app_commands.Choice(name="방학 중", value=0),
    ])
    async def shuttle(self, interaction: discord.Interaction, 시간표: app_commands.Choice[int] = None):
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
                # 크롤링 결과 확인 (디버깅용)
                print("크롤링 결과 vacation_periods:", self.vacation_periods)

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

            if 시간표:
                # 직접 "학기 중" 또는 "방학 중"을 선택한 경우
                await self.send_timetable(interaction, 시간표, shuttle_times)
            else:
                # 기본 명령어 -> 현재 날짜 기준으로 방학 여부 판단
                await self.send_next_shuttle(interaction, is_vacation, shuttle_times, current_date)

        except Exception as e:
            printf = f"오류: {e}"
            print(printf)
            append_to_log(printf, LOG_FILE)
            await interaction.followup.send(f"셔틀 명령어 실행 중 오류가 발생했습니다: {str(e)}")

    async def crawl_academic_calendar(self):
        """
        학교 홈페이지에서 방학(하계/동계) 일정을 가져와 vacation_periods에 저장.
        동계방학은 보통 해가 바뀌므로 파싱 시 시작일 ~ 종료일 형태를 정확히 만들어주는 게 중요함.
        예: "12.20(수) ~ 1.10(수)"
        """
        # 연도별로 하계/동계가 어떻게 표기되는지 확인 후 필요시 로직 조정
        now = datetime.now()
        if now.month < 3:
            # 1~2월에는 직전 해 학사일정 조회
            url = f'https://www.tu.ac.kr/tuhome/scheduleTable.do?schType=U&siteId=tuhome&schYear={now.year-1}&schKeyword=방학'
        else:
            url = f'https://www.tu.ac.kr/tuhome/scheduleTable.do?schType=U&siteId=tuhome&schYear={now.year}&schKeyword=방학'

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                html = await response.text()

        soup = BeautifulSoup(html, 'html.parser')
        calendar_div = soup.find('div', class_='subConBox common')

        vacations = {
            'summer': None,
            'winter1': None,  # 동계방학 1차
            'winter2': None   # 동계방학 2차
        }

        # 아래는 예시 파싱 로직입니다. 실제 HTML 구조에 맞게 수정 필요
        for tr in calendar_div.find_all('tr', class_='notice'):
            month_th = tr.find('th', class_='name')  # ex) "8월", "12월" 등
            if month_th:
                current_month = month_th.text.strip()

            subject = tr.find('td', class_='subject')
            date_td = tr.find('td', class_='name')   # ex) "8.31(목) ~ 9.1(금)" 형태

            if subject and '방학' in subject.text and date_td:
                date_str = date_td.text.strip()  # ex) "8.31(목) ~ 9.1(금)"

                if '하계방학' in subject.text:
                    vacations['summer'] = date_str
                elif '동계방학' in subject.text:
                    if not vacations['winter1']:
                        vacations['winter1'] = date_str
                    else:
                        vacations['winter2'] = date_str

        return vacations

    def normalize_date(self, date_str, base_year):
        """
        주어진 date_str (예: "12.20(수)")를 YYYY-MM-DD 형태로 변환.
        단, '해가 바뀌는' 동계방학을 처리하기 위해선 별도 로직(종료일이 시작일보다 작다면 연도 +1) 등이 필요.
        """
        # 요일 제거: "12.20(수)" -> "12.20"
        date_str = date_str.split('(')[0].strip()

        # 여러 포맷 처리 예시
        # 1) "12.20" 형태
        if '.' in date_str:
            parts = date_str.split('.')
            month = int(parts[0])
            day = int(parts[1])
        # 2) "12월 20일" 형태 (필요시 추가)
        elif '월' in date_str and '일' in date_str:
            # "12월 20일"
            parts = date_str.split('월')
            month = int(parts[0])
            day = int(parts[1].replace('일', '').strip())
        else:
            # 기타 형식이 있으면 추가 처리
            # 일단은 기본값(1월 1일)로 처리하거나 로깅
            print("[normalize_date] 알 수 없는 형식:", date_str)
            month = 1
            day = 1

        return f"{base_year}-{month:02d}-{day:02d}"

    def check_vacation_period(self, current_date):
        """
        self.vacation_periods['summer'], ['winter1'], ['winter2'] 등이
        "12.20(수) ~ 1.10(수)" 형태로 들어왔다고 가정하고,
        각각을 파싱해서 방학 기간 중인지 확인한다.
        """
        current_year = current_date.year
        current_date = current_date.replace(tzinfo=pytz.timezone('Asia/Seoul'))  # 통일

        for key, vacation_period in self.vacation_periods.items():
            if vacation_period and '~' in vacation_period:
                # ex) "12.20(수) ~ 1.10(수)"
                start_str, end_str = vacation_period.split('~')
                start_str = start_str.strip()
                end_str = end_str.strip()

                # 날짜 정규화
                start_date_str = self.normalize_date(start_str, current_year)
                end_date_str   = self.normalize_date(end_str, current_year)

                try:
                    start_date = datetime.strptime(start_date_str, "%Y-%m-%d").replace(
                        tzinfo=pytz.timezone('Asia/Seoul')
                    )
                    end_date = datetime.strptime(end_date_str, "%Y-%m-%d").replace(
                        tzinfo=pytz.timezone('Asia/Seoul')
                    )
                except ValueError as e:
                    print(f"[check_vacation_period] 날짜 변환 실패: {e}")
                    continue

                # 만약 end_date가 start_date보다 과거라면 (동계방학 연도 교차 상황)
                if end_date < start_date:
                    # 동계방학이 해를 넘긴 경우로 보고, end_date 연도를 +1
                    end_date = end_date.replace(year=end_date.year + 1)

                # 현재 날짜가 방학 기간 사이인지 체크
                if start_date <= current_date <= end_date:
                    return True

        return False

    async def send_timetable(self, interaction, 시간표, shuttle_times):
        val = 시간표.value  # 1(학기 중), 0(방학 중)
        timetable = shuttle_times['semester'] if val == 1 else shuttle_times['vacation']

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
        embed = discord.Embed(
            title="셔틀 시간표",
            description=f"{'학기 중' if val else '방학 중'} 시간표:\n{formatted_times}",
            color=discord.Color.green()
        )

        printf = f'({interaction.user.name}님의 입력)_셔틀 {시간표.name} 시간표 출력'
        print(printf)
        append_to_log(printf, LOG_FILE)
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
            embed_color = discord.Color.blue()   # 아침
        elif current_hour < 18:
            embed_color = discord.Color.orange() # 오후
        elif current_hour < 19:
            embed_color = discord.Color.dark_red()  # 저녁
        else:
            embed_color = discord.Color.dark_blue() # 밤

        # 임베드 생성
        embed = discord.Embed(title="다음 셔틀", color=embed_color)

        if not upcoming_shuttles:
            embed.description = "지금 현재 운행 중인 셔틀이 없습니다!"
        else:
            for time in upcoming_shuttles[:5]:  # 최대 5개까지 표시
                time_diff = datetime.strptime(time, "%H:%M") - datetime.strptime(current_time, "%H:%M")
                minutes_left = time_diff.total_seconds() / 60
                embed.add_field(name=f"**{time}**", value=f"`{int(minutes_left)}분 남았습니다`", inline=False)

        printf = f'({interaction.user.name}님의 입력)_셔틀 is_vacation={is_vacation} 출력'
        print(printf)
        append_to_log(printf, LOG_FILE)
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Shuttle_timetable(bot))
