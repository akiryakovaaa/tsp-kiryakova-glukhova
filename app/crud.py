from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError # ошибка нарушения ограничений

from app.models import User, Post, Favorite, Tag, UserRole, PostType

# CRUD для users
def create_user(db: Session, username: str, email: str,
                password_hash: str, role: UserRole = UserRole.user):

    user = User(username = username, email = email, password_hash = password_hash, role = role)
    db.add(user)  # добавляем объект в сессию
    db.commit()  # сохраняем изменения в бд
    db.refresh(user)  # обновляем объект данными из базы (id)
    return user

def get_user_by_id(db: Session, user_id: int): # -> user | none
    return db.query(User).filter(User.id == user_id).first() # строки, где id совпадает с переданным

def get_all_users(db: Session): # -> list[user]
    return db.query(User).order_by(User.id).all() # список всех пользователей, отсортированных по ID

def update_user_email(db: Session, user_id: int, new_email: str): # -> user | none
    user = get_user_by_id(db, user_id)
    if user is None:
        return None

    user.email = new_email
    db.commit()
    db.refresh(user)
    return user

def delete_user(db: Session, user_id: int) -> bool:
    user = get_user_by_id(db, user_id)
    if user is None:
        return False

    db.delete(user)
    db.commit()
    return True

# CRUD для tags
def create_tag(db: Session, name: str): # -> tag
    new_tag = Tag(name = name)  # имя в поле таблицы

    try:
        db.add(new_tag)
        db.commit()
        db.refresh(new_tag)
        return new_tag
    except IntegrityError:
        db.rollback() # очищение сессии
        return None

def get_tag_by_id(db: Session, tag_id: int): # -> tag | none
    return db.query(Tag).filter(Tag.id == tag_id).first()

def get_tag_by_name(db: Session, name: str): # -> tag | none
    return db.query(Tag).filter(Tag.name == name).first()

def get_all_tags(db: Session): # -> list[Tag]
    return db.query(Tag).all()

def delete_tag(db: Session, tag_id: int) -> bool:
    tag = get_tag_by_id(db, tag_id)
    if tag:
        db.delete(tag)
        db.commit()
        return True
    return False

# CRUD для posts
def create_post(db: Session, title: str, body: str, author_id: int,
                post_type: PostType = PostType.recipe, description: str = None,
                is_published: bool = False, tag_ids: list[int] = None):

    # проверяем права пользователя
    user = get_user_by_id(db, author_id)
    if not user:
        raise ValueError("Ошибка: Пользователь с таким ID не найден")

    if user.role != UserRole.admin:
        raise PermissionError("Отказано в доступе: Только администраторы могут создавать публикации")

    # создаем новую публикацию и привязываем к ней теги
    new_post = Post(title = title, description = description, body = body, author_id = author_id,
                    post_type = post_type, is_published = is_published)

    # обработка связи М:М с тегами
    if tag_ids:
        tags = db.query(Tag).filter(Tag.id.in_(tag_ids)).all() # находим теги, чьи id есть в списке
        new_post.tags.extend(tags) # привязываем найденные теги к посту

    try:
        db.add(new_post)
        db.commit()
        db.refresh(new_post)
        return new_post

    except IntegrityError:
        db.rollback()
        return None

def get_post_by_id(db: Session, post_id: int): # -> post | none
    return db.query(Post).filter(Post.id == post_id).first()

def get_all_posts(db: Session): # -> list[post]
    return db.query(Post).order_by(Post.id).all()

def get_published_posts(db: Session): # -> list[post]
    return db.query(Post).filter(Post.is_published.is_(True)).order_by(Post.id).all()

def update_post_title(db: Session, post_id: int, new_title: str): # -> post | none
    post = get_post_by_id(db, post_id)
    if post is None:
        return None

    post.title = new_title
    db.commit()
    db.refresh(post)
    return post

def update_post_status(db: Session, post_id: int, is_published: bool): # -> post | none
    post = get_post_by_id(db, post_id)
    if post:
        post.is_published = is_published
        db.commit()
        db.refresh(post)
        return post
    return None

def delete_post(db: Session, post_id: int) -> bool:
    post = get_post_by_id(db, post_id)
    if post is None:
        return False

    db.delete(post)
    db.commit()
    return True

# CRUD для favorites
def add_post_to_favorites(db: Session, user_id: int, post_id: int):
    # добавлен ли уже этот пост в избранное у данного пользователя
    existing_favorite = db.query(Favorite).filter(Favorite.user_id == user_id,
                                                  Favorite.post_id == post_id).first()

    if existing_favorite is not None:
        return existing_favorite

    # создаем объект закладки, связывающий пользователя и пост
    favorite = Favorite(user_id = user_id, post_id = post_id)

    db.add(favorite)
    db.commit()
    db.refresh(favorite)
    return favorite

def get_favorite_by_id(db: Session, favorite_id: int): # -> favorite | none
    return db.query(Favorite).filter(Favorite.id == favorite_id).first()

def get_user_favorites(db: Session, user_id: int): # -> list[favorite]
    return db.query(Favorite).filter(Favorite.user_id == user_id).order_by(Favorite.id).all()

# все записи добавлений в избранное для конкретного поста по его post_id
def get_post_favorites(db: Session, post_id: int): # -> list[favorite]
    return db.query(Favorite).filter(Favorite.post_id == post_id).order_by(Favorite.id).all()

def remove_post_from_favorites(db: Session, user_id: int, post_id: int) -> bool:
    favorite = db.query(Favorite).filter(Favorite.user_id == user_id,
                                         Favorite.post_id == post_id).first()

    if favorite is None:
        return False

    db.delete(favorite)
    db.commit()
    return True