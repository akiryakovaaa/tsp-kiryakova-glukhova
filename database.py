from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase # инструменты ORM: создание сессий и базовый класс для таблиц
from models import Base

SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://anna@localhost:5432/Culinary_news_portal"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False, # отключение автосохранения
    autoflush=False, # отключение автоматической отправки
    bind=engine # привязка к движку
)

# автоматическое создание всех таблиц в базе данных
def init_db():
    Base.metadata.create_all(bind=engine)