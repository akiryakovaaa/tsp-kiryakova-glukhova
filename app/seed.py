from app.database import SessionLocal
from app.crud import (
    create_user,
    create_post,
    add_post_to_favorites
)
from app.models import User, Post

def seed_data():
    db = SessionLocal()

    try:
        user = db.query(User).filter(
            User.email == "anna@example.com"
        ).first()

        if user is None:
            user = create_user(
                db=db,
                username="anna",
                email="anna@example.com",
                password_hash="test_password_hash"
            )
            print("Пользователь создан")
        else:
            print("Пользователь уже существует")

        post = db.query(Post).filter(
            Post.title == "Домашний борщ",
            Post.author_id == user.id
        ).first()

        if post is None:
            post = create_post(
                db=db,
                title="Домашний борщ",
                description="Классический рецепт домашнего борща",
                body="Свёкла, капуста, картофель, морковь, лук и мясо.",
                author_id=user.id,
                is_published=True
            )
            print("Пост создан")
        else:
            print("Пост уже существует")

        add_post_to_favorites(
            db=db,
            user_id=user.id,
            post_id=post.id
        )
        print("Пост добавлен в избранное")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()

if __name__ == "__main__":
    seed_data()