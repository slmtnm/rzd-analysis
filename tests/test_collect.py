import pytest
from collect.utils import station_code, train_routes, Direction


def test_station_code():
    assert station_code('Санкт-Петербург') == 2004000
    with pytest.raises(ValueError):
        station_code('Неверное название')


def test_train_routes():
    assert len(train_routes(
        from_code='2004000',
        where_code='2000000',
        date='01.01.2022',
        dir=Direction.ONEWAY,
        with_transfers=False
    )) > 0
