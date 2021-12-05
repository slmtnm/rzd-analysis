from datetime import date, datetime


def date_str(date: date) -> str:
    return f'{date.day}.{date.month}.{date.year}'


def str_date(date: str) -> date:
    return datetime.strptime(date, '%d.%m.%Y').date()
