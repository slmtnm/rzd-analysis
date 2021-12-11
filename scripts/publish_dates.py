import pika
import pickle
import sys
import utils


def main():
    if len(sys.argv) < 2:
        print('Usage: python3 ./publish_dates.py <amqp_url>', file=sys.stderr)
        exit(1)

    parameters = pika.URLParameters(sys.argv[1])
    with pika.BlockingConnection(parameters) as connection:
        channel = connection.channel()
        channel.queue_declare(queue='rzd-analysis')

        for date in utils.Date.today().range(30):
            channel.basic_publish(exchange='',
                                  routing_key='rzd-analysis',
                                  body=pickle.dumps(date))


if __name__ == '__main__':
    main()
