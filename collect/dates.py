from datetime import datetime, timedelta
from itertools import chain

def _date_to_string(date: datetime):
    return f'{date.day}.{date.month}.{date.year}'

def generate_dates() -> list[str]:
    today = datetime.today()
    dates = map(_date_to_string, [
        today + timedelta(days=i)
        for i in chain(range(0, 15), range(25, 35), range(40, 50),
                        range(55, 65), range(85, 91))
    ])
    return list(dates)
