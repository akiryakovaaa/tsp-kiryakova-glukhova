from fastapi import FastAPI
from routers import users, posts, tags
from database import init_db

# инициализация приложения
app = FastAPI(title="Кулинарный новостной портал API")

# автоматическое создание таблиц в PostgreSQL при старте
init_db()

# подключение маршрутов
app.include_router(users.router)
app.include_router(posts.router)
app.include_router(tags.router)