
import asyncio
import json
import aio_pika

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn

from broker.config import (
    RABBITMQ_HOST,
    RABBITMQ_PORT,
    RABBITMQ_QUEUE
)

app = FastAPI()

# храним активные подключения клиентов
active_connections = set()


# подключение клиента к websocket
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.add(websocket)

    print("[WebSocket] Клиент подключился")

    try:
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        active_connections.remove(websocket)
        print("[WebSocket] Клиент отключился")


# отправка уведомления всем подключённым клиентам
async def broadcast_notification(message: str):
    disconnected = set()

    for websocket in active_connections:
        try:
            await websocket.send_text(message)
        except Exception:
            disconnected.add(websocket)

    active_connections.difference_update(disconnected)


# обработка сообщений из RabbitMQ
async def process_message(message: aio_pika.IncomingMessage):
    async with message.process():
        event = json.loads(message.body.decode("utf-8"))

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
    connection = await aio_pika.connect_robust(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT
    )

    channel = await connection.channel()

    queue = await channel.declare_queue(
        RABBITMQ_QUEUE,
        durable=True
    )

    print(f"[RabbitMQ] Подписка на очередь {RABBITMQ_QUEUE}")

    await queue.consume(process_message)

    print("[RabbitMQ] Ожидание сообщений...")

    await asyncio.Future()


# запуск notification service
async def start_service():
    # запускаем websocket-сервер
    config = uvicorn.Config(
        app,
        host="127.0.0.1",
        port=8001,
        log_level="info"
    )

    server = uvicorn.Server(config)

    # запускаем websocket и rabbitmq одновременно
    websocket_task = asyncio.create_task(server.serve())
    rabbitmq_task = asyncio.create_task(consume_messages())

    print("[Notification Service] Сервис запущен")
    print("[WebSocket] Сервер доступен по адресу ws://localhost:8001/ws")

    try:
        await asyncio.gather(websocket_task, rabbitmq_task)
    except asyncio.CancelledError:
        print("[Notification Service] Завершение работы")


if __name__ == "__main__":
    asyncio.run(start_service())

