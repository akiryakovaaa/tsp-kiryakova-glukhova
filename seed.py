from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from models import Base, PostType
import crud

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_app.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class DummyUser(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, default="test_author")

Base.metadata.create_all(bind=engine)

def seed_data():
    """Заполняет базу данных начальными тестовыми данными."""
    db = SessionLocal()
    try:
        print("Подключение к БД установлено. Начинаем заполнение...")

        fake_author = DummyUser(username="anna_tester")
        db.add(fake_author)
        db.commit()
        db.refresh(fake_author)
        print(f"1. Создан тестовый автор (ID: {fake_author.id})")

        tag1 = crud.create_tag(db, "Python")
        tag2 = crud.create_tag(db, "Учеба")
        tag3 = crud.create_tag(db, "Рексофт")
        print("2. Созданы тестовые теги")

        post1 = crud.create_post(
            db=db,
            title="Как работать с SQLAlchemy",
            body="Подробный разбор создания моделей и CRUD-операций.",
            post_type=PostType.ARTICLE,
            author_id=fake_author.id,
            description="Основы ORM",
            tag_ids=[tag1.id, tag2.id]
        )

        post2 = crud.create_post(
            db=db,
            title="Итоги стажировки",
            body="Разработка UI для киберспортивного портала завершена.",
            post_type=PostType.NEWS,
            author_id=fake_author.id,
            tag_ids=[tag3.id]
        )
        print(f"3. Созданы тестовые публикации (ID: {post1.id}, ID: {post2.id})")
        print("УСПЕХ: База данных успешно заполнена!")

    except Exception as e:
        print(f"Ошибка при заполнении БД: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()