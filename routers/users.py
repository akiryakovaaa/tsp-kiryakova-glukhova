from fastapi import APIRouter, Depends, HTTPException, status  # инструменты FastAPI: маршрутизация, DI, ошибки и HTTP-статусы
from sqlalchemy.orm import Session
import hashlib  # хеширование паролей

import crud
import schemas
from database import get_db

router = APIRouter(prefix="/users", tags=["Users"])  # локальный роутер модуля

# регистрация пользователя
@router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    new_user = crud.create_user(db=db, user=user)
    if not new_user:
        raise HTTPException(status_code=400, detail="Пользователь с такими данными уже существует") # 400 bad request
    return new_user

# аутентификация пользователя (вход в систему по логину и паролю)
@router.post("/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if not db_user or db_user.password_hash != hashlib.sha256(user.password.encode()).hexdigest():
        raise HTTPException(status_code=401, detail="Неверное имя пользователя или пароль") # 401 unauthorized
    return {"message": "Успешная авторизация", "user_id": db_user.id}

# получение списка всех пользователей
@router.get("/", response_model=list[schemas.UserResponse])
def get_users(db: Session = Depends(get_db)):
    return crud.get_all_users(db)

# добавление публикации в избранное
@router.post("/{user_id}/favorites/{post_id}", status_code=status.HTTP_201_CREATED)
def add_favorite(user_id: int, post_id: int, db: Session = Depends(get_db)):
    return crud.add_post_to_favorites(db, user_id=user_id, post_id=post_id)