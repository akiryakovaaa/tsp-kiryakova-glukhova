import pika
from broker.config import RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_QUEUE
import pickle


def publish_event(event_type: str, payload: dict):
    """Отправляет сериализованное Python-событие в очередь RabbitMQ."""
    message = {
        "event": event_type,
        **payload
    }

    try:
        # открываем TCP-соединение и виртуальный канал (как в лекции)
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT)
        )
        channel = connection.channel()

        # объявляем устойчивую очередь (durable=True)
        channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)

        # публикуем сообщение через default exchange (exchange="")
        channel.basic_publish(
            exchange="",
            routing_key=RABBITMQ_QUEUE,
            body=pickle.dumps(message),
            properties=pika.BasicProperties(
                content_type="application/python-pickle",
                delivery_mode=pika.DeliveryMode.Persistent,  # сохранять на диск
            ),
        )
        print(f"[RabbitMQ] Отправлено событие: {message}")
        connection.close()

    except Exception as exc:
        # если брокер недоступен, FastAPI не должен падать
        print(f"[RabbitMQ] Ошибка отправки сообщения: {exc}")