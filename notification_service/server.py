import asyncio  # запуск WebSocket и RabbitMQ
import pickle  # байты -> python-словарь
import aio_pika  # подключение к RabbitMQ по протоколу AMQP
import websockets
from broker.config import RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_QUEUE

# храним активные подключения клиентов
active_connections = set()

# подключение клиента к websocket
async def websocket_handler(websocket):
    active_connections.add(websocket)
    print("[WebSocket] Клиент подключился")

    try:
        await websocket.wait_closed()  # удерживаем соединение

    finally:
        active_connections.discard(websocket)  # безопасно удаляем отключившегося клиента
        print("[WebSocket] Клиент отключился")

# рассылка уведомления всем подключённым клиентам
async def broadcast_notification(message: str):
    disconnected = set()

    for websocket in active_connections.copy():
        try:
            await websocket.send(message)
        except Exception:
            disconnected.add(websocket)

    active_connections.difference_update(disconnected)

# обработка сообщений из RabbitMQ
async def process_message(message: aio_pika.IncomingMessage):
    async with message.process():
        event = pickle.loads(message.body)

        print(f"[RabbitMQ] Получено событие: {event}")

        if event.get("event") == "new_post":
            notification = (
                f"Новая публикация: {event.get('title')}, "
                f"ID: {event.get('post_id')}"
            )
        else:
            notification = f"Новое событие: {event}"

        await broadcast_notification(notification)

# подключение к RabbitMQ и получение сообщений
async def consume_messages():
    # открываем асинхронное TCP-соединение с RabbitMQ
    connection = await aio_pika.connect_robust(host=RABBITMQ_HOST, port=RABBITMQ_PORT)

    channel = await connection.channel()
    queue = await channel.declare_queue(RABBITMQ_QUEUE, durable=True)

    print(f"[RabbitMQ] Подписка на очередь {RABBITMQ_QUEUE}")
    await queue.consume(process_message)  # при новом сообщении RabbitMQ вызываем process_message

    print("[RabbitMQ] Ожидание сообщений...")
    await asyncio.Future()  # не завершаем функцию и не закрываем соединение


# запуск notification service
async def start_service():
    # открываем слушающий сокет
    async with websockets.serve(websocket_handler, "127.0.0.1", 8001):
        print("[Notification Service] Сервис запущен")
        print("[WebSocket] Сервер доступен по адресу ws://127.0.0.1:8001")

        await consume_messages()


if __name__ == "__main__":
    asyncio.run(start_service())