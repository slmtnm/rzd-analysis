import pika
from .args import parse_arguments
from .collect import collect
from .dates import generate_dates


def main():
    arguments = parse_arguments()

    if arguments.provider_url is None:
        collect(arguments.data_dir, generate_dates())
    else:
        parameters = pika.URLParameters(arguments.provider_url)
        with pika.BlockingConnection(parameters) as connection:
            channel = connection.channel()
            channel.queue_declare(queue='rzd-analysis')

            def callback(ch, method, properties, body):
                collect(arguments.data_dir, [body.decode()])

            channel.basic_consume(queue='rzd-analysis',
                                  on_message_callback=callback,
                                  auto_ack=True)
            channel.basic_consume
            channel.start_consuming()


if __name__ == '__main__':
    main()
