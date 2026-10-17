from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

import crud
import schemas
from database import get_db

router = APIRouter(prefix="/posts", tags=["Posts"])


@router.post("/", response_model=schemas.PostResponse)
def create_post(
    post: schemas.PostCreate,
    db: Session = Depends(get_db),
):
    try:
        new_post = crud.create_post(
            db=db,
            title=post.title,
            body=post.content,
            author_id=post.author_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))

    if new_post is None:
        raise HTTPException(
            status_code=400,
            detail="Не удалось создать пост",
        )

    return new_post

@router.get("/", response_model=list[schemas.PostResponse])
def get_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return (
        db.query(crud.Post)
        .order_by(crud.Post.id)
        .offset(skip)
        .limit(limit)
        .all()
    )

@router.get("/{post_id}", response_model=schemas.PostResponse)
def get_post(
    post_id: int,
    db: Session = Depends(get_db),
):
    post = crud.get_post_by_id(db, post_id)

    if post is None:
        raise HTTPException(
            status_code=404,
            detail="Пост не найден",
        )

    return post

@router.delete("/{post_id}")
def delete_post(
    post_id: int,
    author_id: int,
    db: Session = Depends(get_db),
):
    try:
        deleted = crud.delete_post(
            db=db,
            post_id=post_id,
            author_id=author_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Пост не найден",
        )

    return {"message": "Пост успешно удалён"}