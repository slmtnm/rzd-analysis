import pika
import sys


def main():
    if len(sys.argv) < 3:
        print('Usage: python3 ./publish_dates.py <amqp_url>', file=sys.stderr)
        exit(1)

    parameters = pika.URLParameters(sys.argv[1])
    with pika.BlockingConnection(parameters) as connection:
        channel = connection.channel()
        channel.queue_declare(queue='hello')
        channel.basic_publish(exchange='',
                              routing_key='hello',
                              body=sys.argv[2])

if __name__ == '__main__':
    main()