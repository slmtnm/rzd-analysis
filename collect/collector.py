import asyncio
import pickle
import time

import aio_pika
import httpx
import utils
from dataclasses import dataclass
from database.jsondatabase import JSONDatabase


@dataclass
class CollectorStat:
    total: int
    succeded: int = 0
    failed: int = 0
    started_at: float = time.perf_counter()

    def elapsed(self) -> float:
        return time.perf_counter() - self.started_at

    def __str__(self) -> str:
        progress = (self.succeded + self.failed) / self.total
        return (f'succeded: {self.succeded} '
                f'failed: {self.failed} '
                f'progress: {progress * 100:.2f}% '
                f'elapsed: {self.elapsed():.1f} secs')


class Collector:
    """
    Collector reads messages from AMQP, which are utils.Date
    pickle-serialized objects, and performs collection.
    """

    def __init__(self, amqp_url: str, amqp_queue: str, proxies_filename: str,
                 codes_filename: str, db: JSONDatabase) -> None:
        """
        Collector class constructor

        Args:
            amqp_url - url of message broker
            amqp_queue - name of queue in message broker to read messages from
            proxies_filename - file name to read proxies urls from
            codes_filename - file name to read station codes from
            db - database to store results
        """
        self._codes = utils.read_codes(codes_filename)
        self._proxies = utils.read_proxies(proxies_filename)
        self._amqp_url = amqp_url
        self._amqp_queue = amqp_queue
        self._db = db

        self.dates_queue: asyncio.Queue[utils.Date] = asyncio.Queue()

    async def run(self, workers=15):
        """
        Endlessly reading AMQP messages, which are utils.Date objects,
        and performs routes collection for each date
        between all pairs of station code

        Args:
            workers - number of workers per proxy
        """
        connection = await aio_pika.connect_robust(self._amqp_url)
        async with connection:
            channel = await connection.channel()
            queue = await channel.declare_queue(self._amqp_queue)

            async with queue.iterator() as qiter:
                async for message in qiter:
                    async with message.process():
                        date: utils.Date = pickle.loads(message.body)

                        for pair in self._codes:
                            self.dates_queue.put_nowait(pair)

                        tasks = []
                        for i in range(workers * len(self._proxies)):
                            proxy_index = i % len(self._proxies)
                            tasks.append(asyncio.create_task(
                                self._worker(self.dates_queue, date,
                                             self._proxies[proxy_index])))

                        print(f'\nCollecting routes for {date}:')
                        self._stat = CollectorStat(total=len(self._codes))
                        self._routes = []
                        await self.dates_queue.join()

                        for task in tasks:
                            task.cancel()

                        await asyncio.gather(*tasks, return_exceptions=True)

                        # store results in database
                        self._db.store(utils.Date.today(), date, self._routes)

    async def _worker(self, queue: asyncio.Queue, date: utils.Date,
                      proxy: str):
        while True:
            from_code, where_code = await queue.get()
            try:
                routes = await self._request_routes(from_code, where_code,
                                                    date, proxy)
                self._routes.extend(routes)
                self._stat.succeded += 1
            except Exception:
                self._stat.failed += 1

            print(self._stat, end='\r')
            queue.task_done()

    @utils.async_tries(5)
    async def _request_routes(self, from_code: int, where_code: int,
                              date: utils.Date, proxy: str):
        params: dict[str, int | str] = {
            "layer_id": 5827,
            "dir": 1,
            "tfl": 3,
            "checkSeats": 1,
            "code0": from_code,
            "code1": where_code,
            "dt0": str(date),
            "dt1": str(date),
        }

        addr = 'https://pass.rzd.ru/timetable/public/ru'
        async with httpx.AsyncClient(proxies=proxy) as client:
            response = await client.get(addr, params=params)
            response_json = response.json()

            if 'result' not in response_json:
                raise RuntimeError('Wrong response from server')

            if response_json['result'] == 'OK':
                # no tickets found
                return []

            params['rid'] = response_json['RID']

            await asyncio.sleep(5)

            response = await client.get(addr, params=params)
            response_json = response.json()

            if 'tp' not in response_json:
                raise ValueError(
                    f'Wrong response from server: {response_json}')

            return response_json["tp"]
