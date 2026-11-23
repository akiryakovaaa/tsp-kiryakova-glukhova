import asyncio
import websockets

# подключение к websocket-серверу
async def connect_to_server():
    uri = "ws://127.0.0.1:8001"

    print("[Client] Подключение к серверу...")

    try:
        # подключаемся к WebSocket-серверу (рукопожатие)
        async with websockets.connect(uri) as websocket:
            print("[Client] Успешное подключение")
            print("[Client] Ожидание уведомлений...\n")

            # получаем сообщения от сервера
            async for message in websocket:
                print(f"[УВЕДОМЛЕНИЕ] {message}")

    except Exception as exc:
        print(f"[Client] Ошибка подключения: {exc}")

if __name__ == "__main__":
    asyncio.run(connect_to_server())