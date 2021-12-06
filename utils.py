from datetime import date, datetime
from functools import cache


def date_str(date: date) -> str:
    return f'{date.day}.{date.month}.{date.year}'


def str_date(date: str) -> date:
    return datetime.strptime(date, '%d.%m.%Y').date()


@cache
def read_codes(filename: str) -> list[tuple[int, int]]:
    codes = []
    with open(filename) as f:
        for line in f:
            code0, code1 = line.split()
            codes.append((int(code0), int(code1)))
    return codes
