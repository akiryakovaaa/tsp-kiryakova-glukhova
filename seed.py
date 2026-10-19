from database import SessionLocal
from crud import create_user, create_post, create_tag, get_tag_by_name, add_post_to_favorites
from models import User, Post, PostType, UserRole

from sqlalchemy import select

def seed_data():
    db = SessionLocal()
    try:
        print("Начинаем заполнение базы данных")

        # 1 - создание пользователей
        user_anna = db.scalar(select(User).where(User.email == "anna@example.com"))
        if not user_anna:
            anna_schema = schemas.UserCreate(username="anna", email="anna@example.com", password="password123")
            user_anna = create_user(db=db, user=anna_schema, role=UserRole.admin)
            print("Создан admin: anna")

        user_julia = db.scalar(select(User).where(User.email == "julia@example.com"))
        if not user_julia:
            julia_schema = schemas.UserCreate(username="julia", email="julia@example.com", password="password123")
            user_julia = create_user(db=db, user=julia_schema, role=UserRole.admin)
            print("Создан admin: julia")

        # 2 - создание кулинарных тегов (-> tag + tag_id)
        tags_to_create = ["Супы", "Мясо", "Десерты", "Завтраки"]
        tag_objects = {}
        for t_name in tags_to_create:
            tag = get_tag_by_name(db, t_name)  # проверка на дубликат

            if not tag:
                tag_schema = schemas.TagCreate(name=t_name)  # валидация имени тега
                tag = create_tag(db=db, tag=tag_schema, author_id=user_anna.id)  # создание записи в БД

            tag_objects[t_name] = tag  # сохранение объекта в словарь для быстрой привязки к постам по ID {"Супы": <Tag id="1" name="Супы">}
        print("Кулинарные теги инициализированы")

        # 3 - создание публикаций
        post_recipe = db.scalar(select(Post).where(Post.title == "Домашний борщ"))
        if not post_recipe:
            recipe_schema = schemas.PostCreate(
                title="Домашний борщ",
                description="Классический рецепт",
                body="Свёкла, капуста, картофель, морковь, лук и мясо",
                post_type=PostType.recipe,
                is_published=True,
                tag_ids=[tag_objects["Супы"].id, tag_objects["Мясо"].id]
            )
            post_recipe = create_post(
                db=db,
                post=recipe_schema,
                author_id=user_julia.id
            )
            print("Создан пост: 'Домашний борщ'")

        post_steak = db.scalar(select(Post).where(Post.title == "Секреты идеального стейка"))
        if not post_steak:
            steak_schema = schemas.PostCreate(
                title="Секреты идеального стейка",
                description="Как выбрать мясо и степень прожарки",
                body="Для идеального стейка важно выбрать правильный отруб, например, рибай. Обжаривайте по 2 минуты с каждой стороны...",
                post_type=PostType.news,
                is_published=True,
                tag_ids=[tag_objects["Мясо"].id]
            )
            post_steak = create_post(
                db=db,
                post=steak_schema,
                author_id=user_anna.id
            )
            print("Создан пост: 'Секреты идеального стейка'")

        post_dessert = db.scalar(select(Post).where(Post.title == "Пышные сырники"))
        if not post_dessert:
            dessert_schema = schemas.PostCreate(
                title="Пышные сырники",
                description="Идеальный завтрак за 15 минут",
                body="Используйте сухой творог жирностью 5-9%, минимум муки и одно яйцо. Обжаривайте на слабом огне до золотистой корочки.",
                post_type=PostType.recipe,
                is_published=True,
                tag_ids=[tag_objects["Десерты"].id, tag_objects["Завтраки"].id]
            )
            post_dessert = create_post(
                db=db,
                post=dessert_schema,
                author_id=user_julia.id
            )
            print("Создан пост: 'Пышные сырники'")

        # 4 - добавление в избранное
        if user_anna and post_steak:
            add_post_to_favorites(db, user_anna.id, post_steak.id)
            print("Пост 'Секреты идеального стейка' добавлен в избранное пользователя anna")

        if user_anna and post_recipe:
            add_post_to_favorites(db, user_anna.id, post_recipe.id)
            print("Пост 'Домашний борщ' добавлен в избранное пользователя anna")

        if user_julia and post_dessert:
            add_post_to_favorites(db, user_julia.id, post_dessert.id)
            print("Пост 'Пышные сырники' добавлен в избранное пользователя julia")

        print("База данных кулинарного портала заполнена!")

    except Exception as e:
        print(f"Ошибка при заполнении БД: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()