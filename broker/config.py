import os

# адрес брокера сообщений
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")

# порт подключения к брокеру
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))

# название очереди сообщений
RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE", "notifications_queue")

# учетные данные из переменных окружения
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "guest")