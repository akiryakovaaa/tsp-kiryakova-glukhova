from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

import crud
import schemas
from database import get_db
from grpc_client import get_similar_posts

router = APIRouter(prefix="/posts", tags=["Posts"])  # локальный роутер модуля

# создание публикации
@router.post("/", response_model=schemas.PostResponse, status_code=status.HTTP_201_CREATED)
def create_post(post: schemas.PostCreate, author_id: int, db: Session = Depends(get_db)):
    try:
        new_post = crud.create_post(
            db=db,
            post=post,
            author_id=author_id
        )
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))

    if not new_post:
        raise HTTPException(status_code=400, detail="Не удалось создать пост") # 400 bad request
    return new_post

# получение списка публикаций
@router.get("/", response_model=list[schemas.PostResponse])
def get_posts(db: Session = Depends(get_db)):
    return crud.get_all_posts(db)

# получение публикации по ID
@router.get("/{post_id}")
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = crud.get_post_by_id(db, post_id)

    if post is None:
        raise HTTPException(status_code=404, detail="Пост не найден")

    tags = [tag.name for tag in post.tags]

    try:
        similar_posts = get_similar_posts(post.id, tags)
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Сервис похожих публикаций недоступен: {exc}"
        )

    return {
        "post": schemas.PostResponse.model_validate(post),
        "similar_posts": similar_posts
    }

# удаление публикации
@router.delete("/{post_id}")
def delete_post(post_id: int, author_id: int, db: Session = Depends(get_db)):
    try:
        deleted = crud.delete_post(db=db, post_id=post_id, author_id=author_id)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) # 400 bad request

    if not deleted:
        raise HTTPException(status_code=404, detail="Пост не найден") # 404 not found
    return {"message": "Пост успешно удалён"}

# удаление публикации из избранного
@router.delete("/{post_id}/favorite")
def remove_post_from_favorites_endpoint(post_id: int, user_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_post_from_favorites(db=db, user_id=user_id, post_id=post_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Пост не найден в избранном у данного пользователя") # 404 not found
    return {"message": "Пост успешно удалён из избранного"}