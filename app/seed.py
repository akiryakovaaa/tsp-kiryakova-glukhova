from app.database import SessionLocal
from app.crud import (
    create_user,
    create_post,
    create_tag,
    get_tag_by_name,
    add_post_to_favorites
)
from app.models import User, Post, PostType


def seed_data():
    db = SessionLocal()
    try:
        print("=== Начинаем заполнение базы данных ===")

        # 1. Создание пользователей
        user_main = db.query(User).filter(User.email == "anna@example.com").first()
        if not user_main:
            user_main = create_user(
                db=db, username="anna", email="anna@example.com", password_hash="hash1"
            )
            print("Создан автор: anna")

        user_chef = db.query(User).filter(User.email == "chef@example.com").first()
        if not user_chef:
            user_chef = create_user(
                db=db, username="chef_julia", email="chef@example.com", password_hash="hash2"
            )
            print("Создан автор: chef_julia")

        # 2. Создание кулинарных тегов
        tags_to_create = ["Супы", "Мясо", "Десерты", "Завтраки"]
        tag_objects = {}
        for t_name in tags_to_create:
            tag = get_tag_by_name(db, t_name)
            if not tag:
                tag = create_tag(db, t_name)
            tag_objects[t_name] = tag
        print("Кулинарные теги инициализированы.")

        # 3. Создание публикаций
        post_recipe = db.query(Post).filter(Post.title == "Домашний борщ").first()
        if not post_recipe:
            post_recipe = create_post(
                db=db,
                title="Домашний борщ",
                description="Классический рецепт",
                body="Свёкла, капуста, картофель, морковь, лук и мясо.",
                author_id=user_main.id,
                post_type=PostType.recipe,
                is_published=True,
                tag_ids=[tag_objects["Супы"].id, tag_objects["Мясо"].id]
            )
            print("Создан пост: 'Домашний борщ'")

        post_steak = db.query(Post).filter(Post.title == "Секреты идеального стейка").first()
        if not post_steak:
            post_steak = create_post(
                db=db,
                title="Секреты идеального стейка",
                description="Как выбрать мясо и степень прожарки",
                body="Для идеального стейка важно выбрать правильный отруб, например, рибай. Обжаривайте по 2 минуты с каждой стороны...",
                author_id=user_chef.id,
                post_type=PostType.article,
                is_published=True,
                tag_ids=[tag_objects["Мясо"].id]
            )
            print("Создан пост: 'Секреты идеального стейка'")

        post_dessert = db.query(Post).filter(Post.title == "Пышные сырники").first()
        if not post_dessert:
            post_dessert = create_post(
                db=db,
                title="Пышные сырники",
                description="Идеальный завтрак за 15 минут",
                body="Используйте сухой творог жирностью 5-9%, минимум муки и одно яйцо. Обжаривайте на слабом огне до золотистой корочки.",
                author_id=user_chef.id,
                post_type=PostType.recipe,
                is_published=True,
                tag_ids=[tag_objects["Десерты"].id, tag_objects["Завтраки"].id]
            )
            print("Создан пост: 'Пышные сырники'")

        # 4. Добавление в избранное
        add_post_to_favorites(db, user_main.id, post_steak.id)
        print("Пост 'Секреты идеального стейка' добавлен в избранное пользователя anna")

        print("=== УСПЕХ: База данных кулинарного портала заполнена! ===")

    except Exception as e:
        print(f"Ошибка при заполнении БД: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()