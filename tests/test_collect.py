from collect import collect


def test_train_routes():
    collect(
        from_code='2004000',
        where_code='2000000',
        date='01.01.2022',
        proxy=None
    )
