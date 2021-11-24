import json
import datetime
from concurrent.futures import ThreadPoolExecutor
from itertools import combinations, chain
from typing import Any
from pathlib import Path

import yaml

from proxies import parse_proxies
from utils import Direction, train_routes


def _fetch(proxy: str, pairs: list, date: str, max_workers=30) -> list[dict[str, Any]]:
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        def target(pair):
            try:
                routes = train_routes(
                    from_code=str(pair[0]['code']),
                    where_code=str(pair[1]['code']),
                    date=date,
                    dir=Direction.ROUNDTRIP,
                    with_transfers=False,
                    proxies=proxy)
                print(f'Collected routes from {pair[0]["city"]} to {pair[1]["city"]}')
            except Exception as e:
                # print('Exception was occured: ', str(e))
                routes = None
            return routes

        result = filter(lambda route: route is not None,
                        executor.map(target, pairs))
        return list(result)


def collect(date: str, data_dir: str = 'data/'):
    '''Collects routes for specified date and stores them into data directory'''

    # create data directory if it is not exists
    # and abort if file already created
    data_dir_path = Path(data_dir)
    data_dir_path.mkdir(parents=True, exist_ok=True)
    file_path = data_dir_path/f'{date}.json'
    if file_path.exists():
        return

    proxies = parse_proxies()
    print('Configured proxies:')
    for proxy in proxies:
        print('- ', proxy)

    with open('codes.yaml') as f:
        cities: list[dict[str, Any]] = yaml.safe_load(f)
        print('Successfully read codes from codes.yaml')

    pairs = list(combinations(cities, 2))
    per_proxy = len(pairs) // len(proxies)
    chunks = []

    # split pairs into chunks of per_proxy length
    i = 0
    while i < len(pairs):
        chunks.append(pairs[i:min(len(pairs), i + per_proxy)])
        i += per_proxy

    with ThreadPoolExecutor(max_workers=len(proxies)) as executor:
        results = executor.map(lambda pair: _fetch(pair[0], pair[1], date=date), 
                               zip(proxies, chunks))

    result = [item for sublist in results for item in sublist]

    with open(str(file_path), 'w') as f:
        json.dump(result, f)


def main():
    current_date = datetime.datetime.today()
    dates = [current_date + datetime.timedelta(days=i) for i in chain(range(0, 16), range(25, 36), range(40, 51), range(55, 65), range(85, 91))]
    current_date_string = f'{current_date.day}.{current_date.month}.{current_date.year}'

    for date in dates:
        date_string = f'{date.day}.{date.month}.{date.year}'
        result = collect(date_string, data_dir=f'date/{current_date_string}/')


if __name__ == '__main__':
    main()
