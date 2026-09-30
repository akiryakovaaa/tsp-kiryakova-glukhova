from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base # инструменты ORM: создание сессий и базовый класс для таблиц

SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://anna@localhost:5432/Culinary_news_portal"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False, # отключение автосохранения
    autoflush=False, # отключение автоматической отправки
    bind=engine # привязка к движку
)

Base = declarative_base()

# автоматическое создание всех таблиц в базе данных
def init_db():
    from app import models
    # импортируем модели, чтобы SQLAlchemy узнала об их структуре
    Base.metadata.create_all(bind=engine)