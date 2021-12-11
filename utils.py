from datetime import date, timedelta
from functools import cache
from itertools import combinations
from operator import itemgetter

import yaml


def async_tries(times: int):
    """
    Parametrized function decorator that calls given function
    multiple times if exception is raised during its execution

    Args:
        times - number of times to retry
    """
    def deco(f):
        async def wrapper(*args, **kwargs):
            for _ in range(times):
                try:
                    return await f(*args, **kwargs)
                except Exception as e:
                    error = e
            raise error
        return wrapper
    return deco


@cache
def read_codes(filename: str) -> list[tuple[int, int]]:
    """
    Reads codes from file in YAML format:

    ---
    - city: МОСКВА
    code: 2000000
    - city: САНКТ-ПЕТЕРБУРГ
    code: 2004000
    ...

    And returns all 2-sized combinations between their codes
    """
    with open(filename) as f:
        return list(combinations(map(itemgetter('code'),
                                     yaml.safe_load(f)), 2))


@cache
def read_proxies(filename: str) -> list[str | None]:
    """
    Reads proxies from file in YAML format:

    ---
    # global settings
    login: x58bN5
    password: LvbxIBFUwU
    port: 1050
    proto: http

    proxies:
    # settings per proxy (can override global settings)
    - ip: <ip of first proxy>
    - ip: <ip of second proxy>
      port: 1060
    ...

    And returns list of URLs to these proxies in format:
    <proto>://<login>:<password>@<ip>:<port>
    """
    with open(filename) as f:
        root = yaml.safe_load(f)

    proxies: list[str | None] = []
    for proxy in root.get('proxies', []):
        ip = proxy.get('ip', root.get('ip', None))
        port = proxy.get('port', root.get('port', None))
        proto = proxy.get('proto', root.get('proto', None))
        login = proxy.get('login', root.get('login', None))
        password = proxy.get('password', root.get('password', None))

        if not all([ip, port, proto, login, password]):
            raise ValueError('Wrong proxies file format')
        proxies.append(f'{proto}://{login}:{password}@{ip}:{port}')

    return proxies


class Date(date):
    """
    Date is a wrapper around date from standard library
    that provides alternative constructor from string and
    overloads dates string representation. Also it provides function
    for getting range of dates

    Examples:
    >>> Date.from_str('1.1.2022')
    Date(2021, 1, 1)

    >>> str(Date(2021, 1, 1))
    '1.1.2021'

    >>> list(Date(2021, 1, 1).range(90))
    [Date(2021, 1, 1), Date(2021, 1, 2), Date(2021, 1, 3)]
    """

    @classmethod
    def from_str(cls, s: str):
        d, m, y = map(int, s.split("."))
        return cls.__new__(cls, y, m, d)

    def __str__(self) -> str:
        return f"{self.day}.{self.month}.{self.year}"

    def range(self, days: int):
        for offset in range(days):
            yield self + timedelta(offset)
