from uuid import uuid4
from app.database import SessionLocal
from app.crud import create_user, create_post, get_all_users
from app import crud_posts as crud_tags
from app.models import Tag

def main():
    db = SessionLocal()
    try:
        print("=== ИНТЕГРАЦИОННЫЙ ТЕСТ АРХИТЕКТУРЫ ===")

        # 1. Инфраструктура Юлии: Создание автора
        unique_id = uuid4().hex[:8]
        user = create_user(
            db=db,
            username=f"author_{unique_id}",
            email=f"test_{unique_id}@example.com",
            password_hash="hashed_pass"
        )
        print(f"Пользователь создан: {user.username}")

        # 2. Контентная часть Юлии: Создание поста
        post = create_post(
            db=db,
            title="Секреты идеального стейка",
            description="Кулинарная статья",
            body="Рецепт приготовления...",
            author_id=user.id,
            is_published=True
        )
        print(f"Пост создан: '{post.title}' (Автор ID: {post.author_id})")

        # 3. Контентная часть Анны: Добавление тегов к посту
        # Проверяем, существует ли тег, чтобы избежать ошибки уникальности
        tag = db.query(Tag).filter(Tag.name == "Мясо").first()
        if not tag:
            tag = Tag(name="Мясо")
            db.add(tag)
            db.commit()
            db.refresh(tag)

        post.tags.append(tag)
        db.commit()
        print(f"УСПЕХ: Тег '{tag.name}' успешно привязан к посту '{post.title}'.")
        print("Связь 'User -> Post -> Tag' работает корректно!")

    except Exception as e:
        print(f"Ошибка выполнения: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()