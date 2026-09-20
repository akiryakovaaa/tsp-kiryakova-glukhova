from app.seed_posts import SessionLocal
from app import crud_posts as crud


def run_tests():
    """Выполняет сценарии тестирования CRUD-операций и выводит результаты в консоль."""
    db = SessionLocal()
    try:
        print("=== СЦЕНАРИЙ 1: Чтение данных (READ) ===")
        posts = crud.get_all_posts(db)

        if not posts:
            print("База данных пуста. Сначала запустите скрипт seed_posts.py!")
            return

        for post in posts:
            tag_names = [tag.name for tag in post.tags]
            tags_str = ", ".join(tag_names) if tag_names else "Нет тегов"
            print(f"Публикация: '{post.title}'")
            print(f" -> Тип: {post.post_type.name} | Опубликовано: {post.is_published}")
            print(f" -> Теги: {tags_str}\n")

        print("=== СЦЕНАРИЙ 2: Обновление данных (UPDATE) ===")
        first_post_id = posts[0].id
        updated_post = crud.update_post_status(db, post_id=first_post_id, is_published=True)

        if updated_post:
            print(f"Статус публикации '{updated_post.title}' успешно изменен.")
            print(f"Текущий статус 'Опубликовано': {updated_post.is_published}\n")

        print("=== СЦЕНАРИЙ 3: Удаление данных (DELETE) ===")
        tag_to_delete = crud.get_tag_by_name(db, "Учеба")

        if tag_to_delete:
            tag_id = tag_to_delete.id
            success = crud.delete_tag(db, tag_id)
            print(f"Попытка удаления тега 'Учеба': {'УСПЕШНО' if success else 'ОШИБКА'}\n")
        else:
            print("Тег 'Учеба' не найден в базе данных.\n")

        print("=== СЦЕНАРИЙ 4: Проверка каскадного обновления (READ) ===")
        updated_posts = crud.get_all_posts(db)
        for post in updated_posts:
            tag_names = [tag.name for tag in post.tags]
            tags_str = ", ".join(tag_names) if tag_names else "Нет тегов"
            print(f"Публикация: '{post.title}' | Оставшиеся теги: {tags_str}")

        print("-" * 50)
        print("УСПЕХ: Все сценарии тестирования успешно завершены!")

    except Exception as e:
        print(f"Произошла непредвиденная ошибка при тестировании: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    run_tests()