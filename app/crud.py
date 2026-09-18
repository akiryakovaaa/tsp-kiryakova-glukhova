from app.models import User, Post, Favorite, UserRole, PostType


def create_user(
    db,
    username,
    email,
    password_hash,
    role=UserRole.user
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


def get_user_by_id(db, user_id):
    return db.query(User).filter(
        User.id == user_id
    ).first()


def get_all_users(db):
    return db.query(User).order_by(
        User.id
    ).all()


def update_user_email(db, user_id, new_email):
    user = get_user_by_id(db, user_id)

    if user is None:
        return None

    user.email = new_email

    db.commit()
    db.refresh(user)

    return user


def delete_user(db, user_id):
    user = get_user_by_id(db, user_id)

    if user is None:
        return False

    db.delete(user)
    db.commit()

    return True


def create_post(
    db,
    title,
    description,
    body,
    author_id,
    post_type=PostType.recipe,
    is_published=False
):
    post = Post(
        title=title,
        description=description,
        body=body,
        author_id=author_id,
        post_type=post_type,
        is_published=is_published
    )

    db.add(post)
    db.commit()
    db.refresh(post)

    return post


def get_post_by_id(db, post_id):
    return db.query(Post).filter(
        Post.id == post_id
    ).first()


def get_all_posts(db):
    return db.query(Post).order_by(
        Post.id
    ).all()


def get_published_posts(db):
    return db.query(Post).filter(
        Post.is_published.is_(True)
    ).order_by(
        Post.id
    ).all()


def update_post_title(db, post_id, new_title):
    post = get_post_by_id(db, post_id)

    if post is None:
        return None

    post.title = new_title

    db.commit()
    db.refresh(post)

    return post


def delete_post(db, post_id):
    post = get_post_by_id(db, post_id)

    if post is None:
        return False

    db.delete(post)
    db.commit()

    return True


def add_post_to_favorites(db, user_id, post_id):
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


def get_favorite_by_id(db, favorite_id):
    return db.query(Favorite).filter(
        Favorite.id == favorite_id
    ).first()


def get_user_favorites(db, user_id):
    return db.query(Favorite).filter(
        Favorite.user_id == user_id
    ).order_by(
        Favorite.id
    ).all()


def get_post_favorites(db, post_id):
    return db.query(Favorite).filter(
        Favorite.post_id == post_id
    ).order_by(
        Favorite.id
    ).all()


def remove_post_from_favorites(db, user_id, post_id):
    favorite = db.query(Favorite).filter(
        Favorite.user_id == user_id,
        Favorite.post_id == post_id
    ).first()

    if favorite is None:
        return False

    db.delete(favorite)
    db.commit()

    return True


