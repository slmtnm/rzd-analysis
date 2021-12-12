import argparse
from dataclasses import dataclass


@dataclass
class Arguments:
    data_dir: str
    amqp_url: str


def parse_arguments() -> Arguments:
    parser = argparse.ArgumentParser(description='Collect routes from RZD',
                                     prog='collect')
    parser.add_argument(
        '--data_dir',
        default='data',
        help='directory to strore resulting json files')
    parser.add_argument(
        '--amqp_url',
        help='collection dates provider amqp URL (if no provided \
            dates will be determined by subfolders in data dir)',
    )
    args = parser.parse_args()
    return Arguments(data_dir=args.data_dir, amqp_url=args.amqp_url)
