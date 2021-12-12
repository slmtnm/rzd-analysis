import sys
from pathlib import Path
sys.path.append(str((Path.cwd() / sys.argv[0]).parent.parent))

import utils
import pika
import pickle
import datetime
import argparse


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Add dates to AMQP')
    parser.add_argument('--amqp_url', required=True)
    subparsers = parser.add_subparsers()

    date_parser = subparsers.add_parser('date', help='Add one date')
    date_parser.add_argument('date',
                             help='date to add; format: yy.mm.dd')

    daterange_parser = subparsers.add_parser(
        'daterange',
        help='Add range of dates from first_date to second_date (inclusive)'
    )
    daterange_parser.add_argument(
        'first_date',
        help='first date of date range; format: yy.mm.dd'
    )
    daterange_parser.add_argument(
        'second_date',
        help='second date of date range; format: yy.mm.dd'
    )

    next_parser = subparsers.add_parser('next')
    next_parser.add_argument('next',
                             type=int,
                             help='number of dates from today')

    return parser.parse_args()


def main():
    args = parse_args()
    if hasattr(args, 'date'):
        dates = [utils.Date.from_str(args.date)]
    elif hasattr(args, 'first_date') and hasattr(args, 'second_date'):
        first_date = utils.Date.from_str(args.first_date)
        second_date = utils.Date.from_str(args.second_date)

        delta = second_date - first_date
        dates = []
        for i in range(delta.days + 1):
            dates.append(first_date + datetime.timedelta(days=i))
    elif hasattr(args, 'next'):
        dates = list(utils.Date.today().range(args.next))
    else:
        print('Wrong date/daterange format, see help', file=sys.stderr)
        exit(1)

    parameters = pika.URLParameters(args.amqp_url)
    with pika.BlockingConnection(parameters) as connection:
        channel = connection.channel()
        channel.queue_declare(queue='rzd-analysis')

        for date in dates:
            channel.basic_publish(exchange='',
                                  routing_key='rzd-analysis',
                                  body=pickle.dumps(date))
            print(f'Added date: {date}')


if __name__ == '__main__':
    main()
