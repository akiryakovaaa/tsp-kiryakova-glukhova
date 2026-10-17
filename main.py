from fastapi import FastAPI
from routers import users, posts, tags

# инициализация приложения
app = FastAPI(title="Кулинарный новостной портал API")

# подключение маршрутов
app.include_router(users.router)
app.include_router(posts.router)
app.include_router(tags.router)