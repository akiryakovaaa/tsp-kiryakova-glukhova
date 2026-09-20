from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models import User, Post, Favorite, Tag, UserRole, PostType


# ==========================================
# CRUD ДЛЯ ПОЛЬЗОВАТЕЛЕЙ (USERS)
# ==========================================
def create_user(
        db: Session,
        username: str,
        email: str,
        password_hash: str,
        role: UserRole = UserRole.user
):
    user = User(
        username=username,
        email=email,
        password_hash=password_hash,
        role=role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def get_all_users(db: Session):
    return db.query(User).order_by(User.id).all()


def update_user_email(db: Session, user_id: int, new_email: str):
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


# ==========================================
# CRUD ДЛЯ ТЕГОВ (TAGS)
# ==========================================
def create_tag(db: Session, name: str):
    """Создает новый тег. Если тег уже существует, возвращает None."""
    new_tag = Tag(name=name)
    try:
        db.add(new_tag)
        db.commit()
        db.refresh(new_tag)
        return new_tag
    except IntegrityError:
        db.rollback()
        return None


def get_tag_by_id(db: Session, tag_id: int):
    return db.query(Tag).filter(Tag.id == tag_id).first()


def get_tag_by_name(db: Session, name: str):
    return db.query(Tag).filter(Tag.name == name).first()


def get_all_tags(db: Session):
    return db.query(Tag).all()


def delete_tag(db: Session, tag_id: int) -> bool:
    tag = get_tag_by_id(db, tag_id)
    if tag:
        db.delete(tag)
        db.commit()
        return True
    return False


# ==========================================
# CRUD ДЛЯ ПУБЛИКАЦИЙ (POSTS)
# ==========================================
def create_post(
        db: Session,
        title: str,
        body: str,
        author_id: int,
        post_type: PostType = PostType.recipe,
        description: str = None,
        is_published: bool = False,
        tag_ids: list[int] = None
):
    """Создает новую публикацию и привязывает к ней теги, если они переданы."""
    new_post = Post(
        title=title,
        description=description,
        body=body,
        author_id=author_id,
        post_type=post_type,
        is_published=is_published
    )

    # Обработка связи М:М с тегами
    if tag_ids:
        tags = db.query(Tag).filter(Tag.id.in_(tag_ids)).all()
        new_post.tags.extend(tags)

    try:
        db.add(new_post)
        db.commit()
        db.refresh(new_post)
        return new_post
    except IntegrityError:
        db.rollback()
        return None


def get_post_by_id(db: Session, post_id: int):
    return db.query(Post).filter(Post.id == post_id).first()


def get_all_posts(db: Session):
    return db.query(Post).order_by(Post.id).all()


def get_published_posts(db: Session):
    return db.query(Post).filter(Post.is_published.is_(True)).order_by(Post.id).all()


def update_post_title(db: Session, post_id: int, new_title: str):
    post = get_post_by_id(db, post_id)
    if post is None:
        return None

    post.title = new_title
    db.commit()
    db.refresh(post)
    return post


def update_post_status(db: Session, post_id: int, is_published: bool):
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


# ==========================================
# CRUD ДЛЯ ИЗБРАННОГО (FAVORITES)
# ==========================================
def add_post_to_favorites(db: Session, user_id: int, post_id: int):
    existing_favorite = db.query(Favorite).filter(
        Favorite.user_id == user_id,
        Favorite.post_id == post_id
    ).first()

    if existing_favorite is not None:
        return existing_favorite

    favorite = Favorite(
        user_id=user_id,
        post_id=post_id
    )

    db.add(favorite)
    db.commit()
    db.refresh(favorite)
    return favorite


def get_favorite_by_id(db: Session, favorite_id: int):
    return db.query(Favorite).filter(Favorite.id == favorite_id).first()


def get_user_favorites(db: Session, user_id: int):
    return db.query(Favorite).filter(Favorite.user_id == user_id).order_by(Favorite.id).all()


def get_post_favorites(db: Session, post_id: int):
    return db.query(Favorite).filter(Favorite.post_id == post_id).order_by(Favorite.id).all()


def remove_post_from_favorites(db: Session, user_id: int, post_id: int) -> bool:
    favorite = db.query(Favorite).filter(
        Favorite.user_id == user_id,
        Favorite.post_id == post_id
    ).first()

    if favorite is None:
        return False

    db.delete(favorite)
    db.commit()
    return True