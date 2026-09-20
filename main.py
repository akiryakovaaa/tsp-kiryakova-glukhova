from uuid import uuid4

from app.database import SessionLocal
from app.crud import (
    create_user,
    get_all_users,
    update_user_email,
    delete_user,
    create_post,
    get_all_posts,
    update_post_title,
    delete_post,
    add_post_to_favorites,
    get_user_favorites,
    remove_post_from_favorites
)


def main():
    db = SessionLocal()

    user = None
    post = None

    try:
        print("=== ВСЕ ПОЛЬЗОВАТЕЛИ ===")
        users = get_all_users(db)

        for item in users:
            print(item.id, item.username, item.email)

        unique_id = uuid4().hex[:8]
        original_email = f"test_{unique_id}@example.com"
        updated_email = f"updated_{unique_id}@example.com"

        print("\n=== CREATE: создание пользователя ===")
        user = create_user(
            db=db,
            username=f"test_user_{unique_id}",
            email=original_email,
            password_hash="temporary_password"
        )
        print(user.id, user.username, user.email)

        print("\n=== UPDATE: изменение email ===")
        user = update_user_email(
            db=db,
            user_id=user.id,
            new_email=updated_email
        )
        print(user.id, user.username, user.email)

        print("\n=== CREATE: создание поста ===")
        post = create_post(
            db=db,
            title="Тестовый рецепт",
            description="Тестовая запись для проверки CRUD",
            body="Ингредиенты и способ приготовления",
            author_id=user.id,
            is_published=True
        )
        print(post.id, post.title, post.author_id)

        print("\n=== READ: получение всех постов ===")
        posts = get_all_posts(db)

        for item in posts:
            print(item.id, item.title, item.author_id)

        print("\n=== UPDATE: изменение названия поста ===")
        post = update_post_title(
            db=db,
            post_id=post.id,
            new_title="Обновленный тестовый рецепт"
        )
        print(post.id, post.title)

        print("\n=== CREATE: добавление в избранное ===")
        favorite = add_post_to_favorites(
            db=db,
            user_id=user.id,
            post_id=post.id
        )
        print(favorite.id, favorite.user_id, favorite.post_id)

        print("\n=== READ: избранное пользователя ===")
        favorites = get_user_favorites(db, user.id)

        for item in favorites:
            print(item.id, item.user_id, item.post_id)

        print("\n=== DELETE: удаление из избранного ===")
        print(remove_post_from_favorites(db, user.id, post.id))

        print("\n=== DELETE: удаление поста ===")
        print(delete_post(db, post.id))
        post = None

        print("\n=== DELETE: удаление пользователя ===")
        print(delete_user(db, user.id))
        user = None

        print("\nCRUD-проверка завершена успешно")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()

