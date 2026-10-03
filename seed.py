from app.database import SessionLocal
from app.crud import create_user, create_post, create_tag, get_tag_by_name, add_post_to_favorites
from app.models import User, Post, PostType, UserRole

def seed_data():
    db = SessionLocal()
    try:
        print("Начинаем заполнение базы данных")

        # 1 - создание пользователей
        user_anna = db.query(User).filter(User.email == "anna@example.com").first()
        if not user_anna:
            user_anna = create_user(db=db, username="anna", email="anna@example.com",
                                    password_hash="hash1", role=UserRole.admin)
            print("Создан admin: anna")

        user_julia = db.query(User).filter(User.email == "julia@example.com").first()
        if not user_julia:
            user_julia = create_user(db=db, username="julia", email="julia@example.com",
                                    password_hash="hash2", role=UserRole.admin)
            print("Создан admin: julia")

        # 2 - создание кулинарных тегов (-> tag + tag_id)
        tags_to_create = ["Супы", "Мясо", "Десерты", "Завтраки"]
        tag_objects = {}
        for t_name in tags_to_create:
            tag = get_tag_by_name(db, t_name)
            if not tag:
                tag = create_tag(db, t_name)
            tag_objects[t_name] = tag
        print("Кулинарные теги инициализированы")

        # 3 - создание публикаций
        post_recipe = db.query(Post).filter(Post.title == "Домашний борщ").first()
        if not post_recipe:
            post_recipe = create_post(
                db = db,
                title = "Домашний борщ",
                description = "Классический рецепт",
                body = "Свёкла, капуста, картофель, морковь, лук и мясо",
                author_id = user_julia.id,
                post_type = PostType.recipe,
                is_published = True,
                tag_ids = [tag_objects["Супы"].id, tag_objects["Мясо"].id]
            )
            print("Создан пост: 'Домашний борщ'")

        post_steak = db.query(Post).filter(Post.title == "Секреты идеального стейка").first()
        if not post_steak:
            post_steak = create_post(
                db = db,
                title = "Секреты идеального стейка",
                description = "Как выбрать мясо и степень прожарки",
                body = "Для идеального стейка важно выбрать правильный отруб, например, рибай. Обжаривайте по 2 минуты с каждой стороны...",
                author_id = user_anna.id,
                post_type = PostType.news,
                is_published = True,
                tag_ids = [tag_objects["Мясо"].id]
            )
            print("Создан пост: 'Секреты идеального стейка'")

        post_dessert = db.query(Post).filter(Post.title == "Пышные сырники").first()
        if not post_dessert:
            post_dessert = create_post(
                db = db,
                title = "Пышные сырники",
                description = "Идеальный завтрак за 15 минут",
                body = "Используйте сухой творог жирностью 5-9%, минимум муки и одно яйцо. Обжаривайте на слабом огне до золотистой корочки.",
                author_id = user_julia.id,
                post_type = PostType.recipe,
                is_published = True,
                tag_ids = [tag_objects["Десерты"].id, tag_objects["Завтраки"].id]
            )
            print("Создан пост: 'Пышные сырники'")

        # 4 - добавление в избранное
        add_post_to_favorites(db, user_anna.id, post_steak.id)
        print("Пост 'Секреты идеального стейка' добавлен в избранное пользователя anna")

        add_post_to_favorites(db, user_anna.id, post_recipe.id)
        print("Пост 'Домашний борщ' добавлен в избранное пользователя anna")

        add_post_to_favorites(db, user_julia.id, post_dessert.id)
        print("Пост 'Пышные сырники' добавлен в избранное пользователя julia")

        print(" База данных кулинарного портала заполнена!")

    except Exception as e:
        print(f"Ошибка при заполнении БД: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()