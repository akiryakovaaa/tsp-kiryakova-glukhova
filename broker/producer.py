import pickle  # python-словарь -> байты
import pika  # протокол AMQP и общение с RabbitMQ
from broker.config import RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_QUEUE


# отправляем сериализованное Python-событие в очередь RabbitMQ
def publish_event(event_type: str, payload: dict):
    message = {
        "event": event_type,
        **payload
    }

    try:
        # устанавливаем синхронное TCP-соединение
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT)  # передаём адрес и порт брокера
        )
        channel = connection.channel()  # открываем AMQP-канал

        # объявляем очередь
        channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)

        # публикуем сообщение
        channel.basic_publish(
            exchange="",  # обменник default exchange (тип Direct)
            routing_key=RABBITMQ_QUEUE,
            body=pickle.dumps(message),
            properties=pika.BasicProperties(  # метаданные
                content_type="application/python-pickle",
                delivery_mode=pika.DeliveryMode.Persistent,  # сохранять на диск
            ),
        )
        print(f"[RabbitMQ] Отправлено событие: {message}")
        connection.close()

    except Exception as exc:
        print(f"[RabbitMQ] Ошибка отправки сообщения: {exc}")