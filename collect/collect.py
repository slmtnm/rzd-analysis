import datetime
import json
import pathlib
from threading import Thread
from time import sleep
from concurrent.futures import ThreadPoolExecutor
from itertools import chain
from typing import Any, Optional
import httpx
from collections import deque


result: deque = deque()


with open('codes.txt') as f:
    codes = [line.split() for line in f]


with open('proxies.txt') as f:
    proxies: list[Optional[str]] = list(f.read().split('\n'))
    proxies.append(None)


def _fetch(date: str, from_code: str, where_code: str, proxy: str) -> Any:
    params: dict[str, int | str] = {
        'layer_id': 5827,
        'dir': 1,
        'tfl': 3,
        'checkSeats': 1,
        'code0': from_code,
        'code1': where_code,
        'dt0': date,
        'dt1': date,
    }

    addr = 'https://pass.rzd.ru/timetable/public/ru'
    with httpx.Client(proxies=proxy) as client:
        try:
            response = client.get(addr, params=params).json()
        except httpx.TimeoutException:
            return None

        if 'result' not in response or response['result'] != 'RID':
            return None
        params['rid'] = response['RID']

        sleep(2)

        try:
            response = client.get(addr, params=params).json()
        except httpx.TimeoutException:
            return None

        if 'tp' not in response:
            return None

        print(f'Collected {from_code}->{where_code}:{date}')
        return response['tp']


def _divide_codes(batch_size: int) -> list[list[list[str]]]:
    batches = []
    for i in range(0, len(codes), batch_size):
        batches.append(codes[i:min(i+batch_size, len(codes))])
    return batches


def _worker(batch, date, proxy):
    def target(pair):
        return _fetch(date, pair[0], pair[1], proxy)

    with ThreadPoolExecutor(max_workers=5) as executor:
        for r in executor.map(target, batch):
            if r is not None:
                result.append(r)


def collect(data_dir: str, dates: list[str]) -> None:
    today = datetime.datetime.today()
    today_str = f'{today.day}.{today.month}.{today.year}'

    batches = _divide_codes(len(codes) // len(proxies))

    all_processed = True
    for date in dates:
        filepath = pathlib.Path(data_dir) / str(today_str) / f'{date}.json'
        if filepath.exists():
            continue

        all_processed = False

        filepath.parent.mkdir(parents=True, exist_ok=True)

        threads = []
        for batch, proxy in zip(batches, proxies):
            threads.append(Thread(target=_worker, args=(batch, date, proxy)))

        print(f'Start collecting routes for {date}')
        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        with open(str(filepath), 'w') as f:
            json.dump([item for r in result for item in r], f)

        result.clear()

    if all_processed:
        print('All routes collected for today...')