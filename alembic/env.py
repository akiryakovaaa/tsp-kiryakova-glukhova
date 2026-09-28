import os
from logging.config import fileConfig  # настройка логирования из конфигурационного файла
from sqlalchemy import engine_from_config, pool  # создание движка БД и управления пулом соединений
from alembic import context  # управление миграциями

from app.database import Base

config = context.config  # загружаем настройки из alembic.ini

db_url = os.getenv("DATABASE_URL")
if db_url:
    config.set_main_option("sqlalchemy.url", db_url) # подменяем стандартный адрес бд на тот, который пришел из окружения

if config.config_file_name is not None:
    fileConfig(config.config_file_name) # настраиваем логирование

target_metadata = Base.metadata

# генерация SQL-скрипта без подключения к БД
def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")

    # настраиваем диспетчер миграций Alembic
    context.configure(
        url=url,  # адрес базы данных
        target_metadata=target_metadata,  # модели для отслеживания структуры таблиц
        literal_binds=True, # подстановка значений прямо в текст SQL-запроса
        dialect_opts={"paramstyle": "named"},
        compare_type=True # автоматическое отслеживание изменений типов колонок
    )

    with context.begin_transaction(): # открываем транзакцию
        context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(  # объект-движок
        config.get_section(config.config_ini_section, {}),  # секция [alembic]
        prefix="sqlalchemy.",
        poolclass=pool.NullPool  # порт открывается на время миграции и сразу закрывается
    )

    with connectable.connect() as connection: # открываем соединение с бд
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True
        )

        with context.begin_transaction(): # открываем транзакцию
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()