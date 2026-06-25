from datetime import datetime
import pytz


def get_now(lang: str) -> datetime:
    if lang == 'ru':
        return datetime.now(pytz.timezone('Europe/Moscow'))
    else:
        return datetime.now(pytz.timezone('Etc/GMT+3'))
