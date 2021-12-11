import asyncio

import uvloop

from .args import parse_arguments
from .collector import Collector


async def main():
    arguments = parse_arguments()
    collector = Collector(arguments.provider_url, 'rzd-analysis',
                          'files/proxies.yaml', 'files/codes.yaml', None)
    await collector.run(workers=10)


if __name__ == '__main__':
    uvloop.install()
    asyncio.run(main())
