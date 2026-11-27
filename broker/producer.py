import pickle  # python-словарь -> байты
import pika  # протокол AMQP и общение с RabbitMQ
from broker.config import (
    RABBITMQ_HOST,
    RABBITMQ_PORT,
    RABBITMQ_QUEUE,
    RABBITMQ_USER,
    RABBITMQ_PASSWORD
)


# отправляем сериализованное Python-событие в очередь RabbitMQ
def publish_event(event_type: str, payload: dict):
    message = {
        "event": event_type,
        **payload
    }

    try:
        # учетные данные для подключения к брокеру из переменных окружения
        credentials = pika.PlainCredentials(
            RABBITMQ_USER,
            RABBITMQ_PASSWORD
        )

        # устанавливаем синхронное TCP-соединение с брокером сообщений
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=RABBITMQ_HOST,  # имя сервиса в сети Docker
                port=RABBITMQ_PORT,  # порт брокера сообщений
                credentials=credentials  # параметры авторизации
            )
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