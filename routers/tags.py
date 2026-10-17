from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import crud
import schemas
from database import get_db

router = APIRouter(prefix="/tags", tags=["Tags"])


@router.post("/", response_model=schemas.TagResponse)
def create_tag(
    tag: schemas.TagCreate,
    author_id: int,
    db: Session = Depends(get_db),
):
    try:
        new_tag = crud.create_tag(
            db=db,
            name=tag.name,
            author_id=author_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))

    if new_tag is None:
        raise HTTPException(
            status_code=409,
            detail="Тег с таким названием уже существует",
        )

    return new_tag


@router.get("/", response_model=list[schemas.TagResponse])
def get_tags(db: Session = Depends(get_db)):
    return crud.get_all_tags(db)


@router.get("/{tag_id}", response_model=schemas.TagResponse)
def get_tag(tag_id: int, db: Session = Depends(get_db)):
    tag = crud.get_tag_by_id(db, tag_id)

    if tag is None:
        raise HTTPException(status_code=404, detail="Тег не найден")

    return tag


@router.delete("/{tag_id}")
def delete_tag(
    tag_id: int,
    author_id: int,
    db: Session = Depends(get_db),
):
    try:
        deleted = crud.delete_tag(
            db=db,
            tag_id=tag_id,
            author_id=author_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))

    if not deleted:
        raise HTTPException(status_code=404, detail="Тег не найден")

    return {"message": "Тег успешно удалён"}