from uuid import uuid4 # генерация уникального ID запроса (Request-ID)

from app.database import SessionLocal
from app.crud import create_user, create_post, get_tag_by_name, create_tag, add_post_to_favorites
from app.models import UserRole

def main():
    db = SessionLocal()
    try:
        print("ИНТЕГРАЦИОННЫЙ ТЕСТ АРХИТЕКТУРЫ")

        # 1 - создание автора
        unique_id = uuid4().hex[:8]  # генерация случайного 8-значного числа для уникальности
        user = create_user(
            db=db,
            username=f"author_{unique_id}",
            email=f"test_{unique_id}@example.com",
            password_hash="hashed_pass",
            role=UserRole.admin
        )
        print(f"Пользователь создан: {user.username}")

        # 2 - обработка тега
        tag_name = "Мясо"
        tag = get_tag_by_name(db=db, name=tag_name)
        if not tag:
            tag = create_tag(db=db, name=tag_name)

        print(f"Тег готов к привязке: '{tag.name}'")

        # 3 - создание поста и привязка тега
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
        print(f"Тег '{tag.name}' успешно привязан к посту '{post.title}'.")

        # 4 - проверка защиты ролей
        reader_id = uuid4().hex[:8]

        reader = create_user(
            db=db,
            username=f"reader_{reader_id}",
            email=f"reader_{reader_id}@example.com",
            password_hash="pass",
            role=UserRole.user
        )
        print(f"\nСоздан читатель: {reader.username}")

        # попытка читателя создать пост
        try:
            illegal_post = create_post(
                db=db,
                title="Взлом системы",
                body="Этот пост не должен сохраниться",
                author_id=reader.id
            )
        except PermissionError as pe:
            print(f"Попытка создания поста заблокирована. Причина: {pe}")

        add_post_to_favorites(db, reader.id, post.id)
        print(f"Читатель '{reader.username}' смог добавить пост '{post.title}' в избранное. ID закладки: {fav.id}")

    except Exception as e:
        print(f"Ошибка выполнения: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()