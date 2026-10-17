from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker # инструменты ORM: создание сессий
from models import Base

SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://anna@localhost:5432/Culinary_news_portal"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

# создаем фабрику сессий
SessionLocal = sessionmaker(
    autocommit=False,  # автофиксация: транзакция сохраняется в БД только вручную через db.commit()
    autoflush=False,   # автоотправка: SQL-запросы не летят в БД автоматически перед каждым поиском/чтением
    bind=engine # привязка к движку
)

# автоматическое создание всех таблиц в базе данных
def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()