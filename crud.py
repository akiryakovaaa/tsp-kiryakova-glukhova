import hashlib
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError # ошибка - нарушения ограничений бд
from sqlalchemy import select

from models import User, Post, Favorite, Tag, UserRole, PostType
import schemas

# CRUD для users
def create_user(db: Session, user: schemas.UserCreate, role: UserRole = UserRole.user):
    password_bytes = user.password.encode() # преобразуем str в байты (UTF-8)
    hash_object = hashlib.sha256(password_bytes) # объект хешера
    hashed_password = hash_object.hexdigest() # получаем 64-символьную шестнадцатеричную строку хеша

    db_user = User(
        username=user.username,
        email=user.email,
        password_hash=hashed_password,
        role=role
    )

    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    except IntegrityError:
        db.rollback()
        return None

# поиск по уник логину - при аутентификации (POST /users/login), чтобы найти аккаунт и сверить хеш пароля
def get_user_by_username(db: Session, username: str): # -> user | none
    return db.scalars(select(User).where(User.username == username)).first()

# быстрый поиск пользователя по первичному ключу
def get_user_by_id(db: Session, user_id: int): # -> user | none
    return db.get(User, user_id)# строки, где id совпадает с переданным

# получение полного списка пользователей
def get_all_users(db: Session): # -> list[user]
    return db.scalars(select(User).order_by(User.id)).all() # список всех пользователей, отсортированных по ID

def update_user_email(db: Session, user_id: int, new_email: str, author_id: int): # -> user | none
    # проверяем права пользователя
    current_user = get_user_by_id(db, author_id)
    if not current_user:
        raise ValueError("Ошибка: Пользователь с таким ID не найден")

    if current_user.role != UserRole.admin and current_user.id != user_id:
        raise PermissionError("Отказано в доступе: Можно изменять только свой аккаунт")

    user = get_user_by_id(db, user_id)
    if user is None:
        return None

    user.email = new_email
    db.commit()
    db.refresh(user)
    return user

def delete_user(db: Session, user_id: int, author_id: int) -> bool:
    # проверяем права пользователя
    current_user = get_user_by_id(db, author_id)
    if not current_user:
        raise ValueError("Ошибка: Пользователь с таким ID не найден")

    if current_user.role != UserRole.admin and current_user.id != user_id:
        raise PermissionError("Отказано в доступе: Можно удалять только свой аккаунт")

    user = get_user_by_id(db, user_id)
    if user is None:
        return False

    db.delete(user)
    db.commit()
    return True

# CRUD для tags
def create_tag(db: Session, tag: schemas.TagCreate, author_id: int): # -> tag
    # проверяем права пользователя
    user = get_user_by_id(db, author_id)
    if not user:
        raise ValueError("Ошибка: Пользователь с таким ID не найден")

    if user.role != UserRole.admin:
        raise PermissionError("Отказано в доступе: Только администраторы могут создавать теги")

    new_tag = Tag(
        name = tag.name.strip().lower()
    )

    try:
        db.add(new_tag)
        db.commit()
        db.refresh(new_tag)
        return new_tag
    except IntegrityError:
        db.rollback()
        return None

def get_tag_by_id(db: Session, tag_id: int): # -> tag | none
    return db.get(Tag, tag_id)

def get_tag_by_name(db: Session, name: str): # -> tag | none
    return db.scalar(select(Tag).where(Tag.name == name))

def get_all_tags(db: Session): # -> list[Tag]
    return db.scalars(select(Tag)).all()

def delete_tag(db: Session, tag_id: int, author_id: int) -> bool:
    # проверяем права пользователя
    user = get_user_by_id(db, author_id)
    if not user:
        raise ValueError("Ошибка: Пользователь с таким ID не найден")

    if user.role != UserRole.admin:
        raise PermissionError("Отказано в доступе: Только администраторы могут удалять теги")

    tag = get_tag_by_id(db, tag_id)
    if tag:
        db.delete(tag)
        db.commit()
        return True
    return False

# CRUD для posts
def create_post(db: Session, post: schemas.PostCreate, author_id: int):

    # проверяем права пользователя
    user = get_user_by_id(db, author_id)
    if not user:
        raise ValueError("Ошибка: Пользователь с таким ID не найден")

    if user.role != UserRole.admin:
        raise PermissionError("Отказано в доступе: Только администраторы могут создавать публикации")

    # создаем новую публикацию и привязываем к ней теги
    new_post = Post(
        title = post.title,
        description = post.description,
        body = post.body,
        author_id = author_id,
        post_type = post.post_type,
        is_published = post.is_published
    )

    # обработка связи М:М с тегами
    if post.tag_ids:
        tags = db.scalars(select(Tag).where(Tag.id.in_(post.tag_ids))).all() # ищем сразу все теги по переданному списку id
        new_post.tags.extend(tags) # добавляем загруженные объекты тегов в коллекцию поста

    try:
        db.add(new_post)
        db.commit()
        db.refresh(new_post)
        return new_post

    except IntegrityError:
        db.rollback()
        return None

def get_post_by_id(db: Session, post_id: int): # -> post | none
    return db.get(Post, post_id)

# список всех постов (включая черновики)
def get_all_posts(db: Session, skip: int = 0, limit: int = 100): # -> list[post]
    return db.scalars(select(Post).order_by(Post.id).offset(skip).limit(limit)).all()

# список только опубликованных постов
def get_published_posts(db: Session): # -> list[post]
    return db.scalars(select(Post).where(Post.is_published.is_(True)).order_by(Post.id)).all()

def update_post_title(db: Session, post_id: int, new_title: str, author_id: int): # -> post | none
    # проверяем права пользователя
    user = get_user_by_id(db, author_id)
    if not user:
        raise ValueError("Ошибка: Пользователь с таким ID не найден")

    if user.role != UserRole.admin:
        raise PermissionError("Отказано в доступе: Только администраторы могут изменять публикации")

    post = get_post_by_id(db, post_id)
    if post is None:
        return None

    post.title = new_title
    db.commit()
    db.refresh(post)
    return post

def update_post_status(db: Session, post_id: int, is_published: bool, author_id: int): # -> post | none
    # проверяем права пользователя
    user = get_user_by_id(db, author_id)
    if not user:
        raise ValueError("Ошибка: Пользователь с таким ID не найден")

    if user.role != UserRole.admin:
        raise PermissionError("Отказано в доступе: Только администраторы могут менять статус публикации")

    post = get_post_by_id(db, post_id)
    if post is None:
        return None

    post.is_published = is_published
    db.commit()
    db.refresh(post)
    return post

def delete_post(db: Session, post_id: int, author_id: int) -> bool:
    # проверяем права пользователя
    user = get_user_by_id(db, author_id)
    if not user:
        raise ValueError("Ошибка: Пользователь с таким ID не найден")

    if user.role != UserRole.admin:
        raise PermissionError("Отказано в доступе: Только администраторы могут удалять публикации")

    post = get_post_by_id(db, post_id)
    if post is None:
        return False

    db.delete(post)
    db.commit()
    return True

# CRUD для favorites
def add_post_to_favorites(db: Session, user_id: int, post_id: int):
    # добавлен ли уже этот пост в избранное у данного пользователя
    existing_favorite = db.scalar(
        select(Favorite).where(Favorite.user_id == user_id, Favorite.post_id == post_id)
    )

    if existing_favorite is not None:
        return existing_favorite

    # создаем объект закладки, связывающий пользователя и пост
    favorite = Favorite(user_id = user_id, post_id = post_id)

    db.add(favorite)
    db.commit()
    db.refresh(favorite)
    return favorite

def get_favorite_by_id(db: Session, favorite_id: int): # -> favorite | none
    return db.get(Favorite, favorite_id)

def get_user_favorites(db: Session, user_id: int): # -> list[favorite]
    return db.scalars(select(Favorite).where(Favorite.user_id == user_id).order_by(Favorite.id)).all()

# все записи добавлений в избранное для конкретного поста по его post_id
def get_post_favorites(db: Session, post_id: int): # -> list[favorite]
    return db.scalars(select(Favorite).where(Favorite.post_id == post_id).order_by(Favorite.id)).all()

def delete_post_from_favorites(db: Session, user_id: int, post_id: int) -> bool:
    favorite = db.scalar(select(Favorite).where(Favorite.user_id == user_id, Favorite.post_id == post_id))

    if favorite is None:
        return False

    db.delete(favorite)
    db.commit()
    return True