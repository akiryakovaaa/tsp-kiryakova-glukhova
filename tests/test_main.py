import subprocess  # запуск внешних процессов
from uuid import uuid4
from fastapi.testclient import TestClient  # клиент для отправки тестовых HTTP-запросов

from main import app
from app.database import SessionLocal
from app.crud import create_user
from app.models import UserRole

client = TestClient(app)

# тест сервера: проверка корневого маршрута FastAPI
def test_server_api():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "Проект успешно запущен в Docker!"}

# тест репозитория: проверка сохранения пользователя в бд
def test_repository_crud():
    db = SessionLocal()
    try:
        unique_id = uuid4().hex[:8] # генерируем уникальные данные, чтобы тест не падал при повторных запусках
        test_username = f"repo_test_{unique_id}"
        test_email = f"repo_{unique_id}@example.com"

        user = create_user(
            db=db,
            username=test_username,
            email=test_email,
            password_hash="test_pwd",
            role=UserRole.user
        )

        assert user.id is not None
        assert user.username == test_username
        assert user.email == test_email
    finally:
        db.close()

# тест демо-скрипта: проверка успешного выполнения файла main.py
def test_demo_script():
    # запускаем скрипт изолированно, имитируя ручной ввод команды в терминале
    result = subprocess.run(
        ["python", "main.py"],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0, f"Ошибка в демо-скрипте: {result.stderr}"