import pytest
from collect.utils import station_code, train_routes, Direction


@pytest.mark.asyncio
async def test_station_code():
    assert await station_code('Санкт-Петербург') == 2004000
    with pytest.raises(ValueError):
        await station_code('Неверное название')


@pytest.mark.asyncio
async def test_train_routes():
    assert len(await train_routes(
        from_code='2004000',
        where_code='2000000',
        date='01.01.2022',
        dir=Direction.ONEWAY,
        with_transfers=False
    )) > 0
