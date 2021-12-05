from pathlib import Path
from datetime import date
from db.jsondatabase import JSONDatabase


def test_filename():
    db = JSONDatabase('data')
    got_str = str(db.get_file_name(date(2021, 11, 19), date(2021, 11, 26)))
    ref_str = str(Path.cwd()) + '/data/19.11.2021/26.11.2021.json'
    assert got_str == ref_str


def test_open_json():
    db = JSONDatabase('data')
    data = db.open_json_file(date(2021, 11, 19), date(2021, 11, 26))
    data[1]
