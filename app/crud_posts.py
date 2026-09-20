from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models_posts import Tag, Post, PostType

# CRUD для Тегов
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
    """Возвращает тег по ID или None, если он не найден."""
    return db.query(Tag).filter(Tag.id == tag_id).first()

def get_tag_by_name(db: Session, name: str):
    """Возвращает тег по имени или None, если он не найден."""
    return db.query(Tag).filter(Tag.name == name).first()

def get_all_tags(db: Session):
    """Возвращает список всех тегов."""
    return db.query(Tag).all()

def delete_tag(db: Session, tag_id: int) -> bool:
    """Удаляет тег по ID. Возвращает True при успехе, False если тег не найден."""
    tag = get_tag_by_id(db, tag_id)
    if tag:
        db.delete(tag)
        db.commit()
        return True
    return False


# CRUD для Публикаций (Posts)
def create_post(db: Session, title: str, body: str, post_type: PostType, author_id: int, description: str = None, tag_ids: list[int] = None):
    """Создает новую публикацию и привязывает к ней теги, если они переданы."""
    new_post = Post(
        title=title,
        body=body,
        post_type=post_type,
        author_id=author_id,
        description=description
    )

    # Обработка связи М:М с тегами
    if tag_ids:
        # Находим все теги, чьи ID присутствуют в переданном списке
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
    """Возвращает публикацию по ID или None."""
    return db.query(Post).filter(Post.id == post_id).first()

def get_all_posts(db: Session):
    """Возвращает список всех публикаций."""
    return db.query(Post).all()

def update_post_status(db: Session, post_id: int, is_published: bool):
    """Обновляет статус публикации (is_published). Возвращает обновленный пост или None."""
    post = get_post_by_id(db, post_id)
    if post:
        post.is_published = is_published
        db.commit()
        db.refresh(post)
        return post
    return None

def delete_post(db: Session, post_id: int) -> bool:
    """Удаляет публикацию по ID. Возвращает True при успехе, False при отсутствии."""
    post = get_post_by_id(db, post_id)
    if post:
        db.delete(post)
        db.commit()
        return True
    return False