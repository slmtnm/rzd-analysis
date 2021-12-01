import pika
import sys
from collect.dates import generate_dates


def main():
    if len(sys.argv) < 2:
        print('Usage: python3 ./publish_dates.py <amqp_url>', file=sys.stderr)
        exit(1)

    parameters = pika.URLParameters(sys.argv[1])
    with pika.BlockingConnection(parameters) as connection:
        channel = connection.channel()
        channel.queue_declare(queue='rzd-analysis')

        for date in generate_dates():
            channel.basic_publish(exchange='',
                                routing_key='rzd-analysis',
                                body=date)
            print(f'published date: {date}')

if __name__ == '__main__':
    main()