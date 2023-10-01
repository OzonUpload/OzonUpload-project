import datetime

time_zones = {
    'МСК':3,
    'ЕКБ':5
}

def get_data(city):
    """Получение даты и времени по городу"""
    
    offset = datetime.timedelta(hours=time_zones[city])
    tz = datetime.timezone(offset,city)
    date = datetime.datetime.now(tz)

    return date

