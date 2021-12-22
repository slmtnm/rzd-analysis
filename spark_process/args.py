import argparse
from dataclasses import dataclass
from datetime import date
import utils


@dataclass
class Options:
    master_url: str
    data_dir: str
    departure_date: date
    type: str
    appname: str


def parse_args() -> Options:
    parser = argparse.ArgumentParser(
        description='Find chart with maximum tariff/seats ratio')
    parser.add_argument('master_url', help='spark master url')
    parser.add_argument('data_dir', help='path to data directory')
    parser.add_argument('departure_date', help='date when train leaves')
    parser.add_argument('type', help='characterisic to analyze',
                        choices=['tariff', 'seats'])
    parser.add_argument('--appname',
                        help='name of application to register in Hadoop',
                        default='rzd-analysis')
    args = parser.parse_args()
    return Options(args.master_url, args.data_dir,
                   utils.Date.from_str(args.departure_date),
                   args.type, args.appname)
