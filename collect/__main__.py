import json
from concurrent.futures import ThreadPoolExecutor
from itertools import combinations
from typing import Any

import yaml

from .proxies import parse_proxies
from .utils import Direction, train_routes


def fetch(proxy: str, pairs: list, max_workers=2) -> list[dict[str, Any]]:
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        def target(pair):
            try:
                routes = train_routes(
                    from_code=str(pair[0]['code']),
                    where_code=str(pair[1]['code']),
                    date='01.01.2022',
                    dir=Direction.ROUNDTRIP,
                    with_transfers=False,
                    proxies=proxy)
            except Exception as e:
                print('Exception was occured: ', str(e))
                routes = None
            return routes

        result = filter(lambda route: route is not None,
                        executor.map(target, pairs))
        return list(result)


def main():
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

    result = []
    for proxy, chunk in zip(proxies, chunks):
        result += fetch(proxy, chunk)

    with open('result.json', 'w') as f:
        json.dump(result, f)


if __name__ == '__main__':
    main()
