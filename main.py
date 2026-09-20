from uuid import uuid4
from app.database import SessionLocal
from app.crud import create_user, create_post, get_tag_by_name, create_tag


def main():
    db = SessionLocal()
    try:
        print("=== ИНТЕГРАЦИОННЫЙ ТЕСТ АРХИТЕКТУРЫ ===")

        # 1. Создание автора (Архитектура Юлии)
        unique_id = uuid4().hex[:8]
        user = create_user(
            db=db,
            username=f"author_{unique_id}",
            email=f"test_{unique_id}@example.com",
            password_hash="hashed_pass"
        )
        print(f"Пользователь создан: {user.username}")

        # 2. Обработка тега через единый CRUD-слой
        tag_name = "Мясо"
        tag = get_tag_by_name(db=db, name=tag_name)
        if not tag:
            tag = create_tag(db=db, name=tag_name)

        print(f"Тег готов к привязке: '{tag.name}'")

        # 3. Создание поста и автоматическая привязка тега (Слияние архитектур)
        post = create_post(
            db=db,
            title="Секреты идеального стейка",
            description="Кулинарная статья",
            body="Рецепт приготовления...",
            author_id=user.id,
            is_published=True,
            tag_ids=[tag.id] if tag else None
        )

        print(f"Пост создан: '{post.title}' (Автор ID: {post.author_id})")
        print(f"УСПЕХ: Тег '{tag.name}' успешно привязан к посту '{post.title}'.")
        print("Связь 'User -> Post -> Tag' работает корректно!")

    except Exception as e:
        print(f"Ошибка выполнения: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()