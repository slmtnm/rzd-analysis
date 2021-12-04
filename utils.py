from datetime import date


def dmy_from_date(date: date):
    return f'{date.day}.{date.month}.{date.year}'
