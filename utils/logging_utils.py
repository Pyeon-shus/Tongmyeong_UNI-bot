#logging_utils.py
import datetime
import pytz

def mytime_1():
    KR_TZ = pytz.timezone('Asia/Seoul')
    timestamp = datetime.datetime.now(KR_TZ).strftime("[%Y-%m-%d %H:%M:%S]")
    return timestamp

def mytime_2():
    KR_TZ = pytz.timezone('Asia/Seoul')
    now_string = datetime.datetime.now(KR_TZ).strftime("%d일")
    return now_string

def mytime_3():
    KR_TZ = pytz.timezone('Asia/Seoul')
    weekday_name = datetime.datetime.now(KR_TZ).strftime("%A")  # 요일을 텍스트로 추출
    return weekday_name

"""mytime 예시 사용
if __name__ == "__main__":
    print(mytime_1())  # 현재 날짜와 시간 출력
    print(mytime_2())  # 현재 일 출력
    print(mytime_3())  # 현재 요일 출력
"""

def append_to_log(message, log_file):
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f'{mytime_1()} - {message}\n')

