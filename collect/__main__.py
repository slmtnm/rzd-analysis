from datetime import datetime, timedelta
from itertools import chain
import pika
from .args import parse_arguments
from .collect import collect


def date_to_string(date: datetime):
    return f'{date.day}.{date.month}.{date.year}'


if __name__ == '__main__':
    arguments = parse_arguments()

    if arguments.provider_url is None:
        today = datetime.today()
        dates = map(date_to_string, [
            today + timedelta(days=i)
            for i in chain(range(0, 15), range(25, 35), range(40, 50),
                           range(55, 65), range(85, 91))
        ])
        collect(arguments.data_dir, dates)
    else:
        parameters = pika.URLParameters(arguments.provider_url)
        with pika.BlockingConnection(parameters) as connection:
            channel = connection.channel()
            channel.queue_declare(queue='hello')

            def callback(ch, method, properties, body):
                collect(arguments.data_dir, [body.decode()])
                
            channel.basic_consume(queue='hello',
                                  on_message_callback=callback,
                                  auto_ack=True)
            channel.basic_consume
            channel.start_consuming()
