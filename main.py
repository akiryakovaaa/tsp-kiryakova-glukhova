from fastapi import FastAPI
from routers import users

# инициализация приложения
app = FastAPI(title="Кулинарный новостной портал API")

# подключение маршрутов
app.include_router(users.router)