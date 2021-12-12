import asyncio
from pathlib import Path
import aiormq

import uvloop

from .args import parse_arguments
from database.jsondatabase import JSONDatabase
from .collector import Collector


async def main():
    arguments = parse_arguments()
    collector = Collector(arguments.amqp_url, 'rzd-analysis',
                          'files/proxies.yaml', 'files/codes.yaml',
                          JSONDatabase(arguments.data_dir))
    while True:
        try:
            await collector.run(workers=10)
        except aiormq.exceptions.ChannelInvalidStateError:
            continue


if __name__ == '__main__':
    uvloop.install()
    asyncio.run(main())
