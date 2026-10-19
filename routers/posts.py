from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

import crud
import schemas
from database import get_db

router = APIRouter(prefix="/posts", tags=["Posts"])

# создание публикации
@router.post("/", response_model=schemas.PostResponse, status_code=status.HTTP_201_CREATED)
def create_post(post: schemas.PostCreate, author_id: int, db: Session = Depends(get_db)):
    new_post = crud.create_post(
        db=db,
        post=post,
        author_id=author_id
    )
    if not new_post:
        raise HTTPException(status_code=400, detail="Не удалось создать пост") # 400 bad request
    return new_post

# получение списка публикаций
@router.get("/", response_model=list[schemas.PostResponse])
def get_posts(db: Session = Depends(get_db)):
    return crud.get_all_posts(db)

# получение публикации по ID
@router.get("/{post_id}", response_model=schemas.PostResponse)
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = crud.get_post_by_id(db, post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="Пост не найден") # 404 not found
    return post

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