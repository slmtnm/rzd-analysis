from datetime import datetime, timedelta


def _date_to_string(date: datetime):
    return f'{date.day}.{date.month}.{date.year}'


def generate_dates() -> list[str]:
    today = datetime.today()
    dates = map(_date_to_string, [
        today + timedelta(days=i)
        for i in range(45)
    ])
    return list(dates)
