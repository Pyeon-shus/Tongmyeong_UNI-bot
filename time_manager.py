# password_manager.py
import datetime
import pytz

def time():
    KR_TZ = pytz.timezone('Asia/Seoul')
    timestamp = datetime.datetime.now(KR_TZ)
    return timestamp

def time_str():
    """현재 시간을 문자열로 반환"""
    return time().strftime("[%Y-%m-%d %H:%M:%S]")

def read():
    with open('config.py', 'r', encoding='utf-8') as file:
        for line in file:
            if line.startswith('END ='):
                return line.split('=')[1].strip().strip("'")
    return None

def write():
    with open('config.py', 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    with open('config.py', 'w', encoding='utf-8') as file:
        for line in lines:
            if line.startswith('END ='):
                file.write(f"END = '{time_str()}'")
            else:
                file.write(line)

def cal():
    """read()와 현재 시간의 차이를 계산"""
    end_time = get()
    cal = time() - end_time
    return cal

def get():
    """config.py에서 읽은 END 값을 offset-aware datetime 객체로 변환"""
    KR_TZ = pytz.timezone('Asia/Seoul')
    end_time_str = read()
    naive_datetime = datetime.datetime.strptime(end_time_str, "[%Y-%m-%d %H:%M:%S]")
    return KR_TZ.localize(naive_datetime)
