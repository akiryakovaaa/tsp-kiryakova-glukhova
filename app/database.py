from sqlalchemy import create_engine # создание подключения к бд
from sqlalchemy.orm import sessionmaker, declarative_base # инструменты ORM: фабрику сессий и базовый класс для моделей

DATABASE_URL = "postgresql+psycopg2://anna@localhost:5432/Culinary_news_portal" # строка подключения

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False, # отключение автосохранения
    autoflush=False, # отключение автоматической отправки
    bind=engine # привязка к движку
)

Base = declarative_base() # базовый класс для всех моделей (таблиц) базы данных