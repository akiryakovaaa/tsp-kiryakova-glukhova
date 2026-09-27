# исходный образ Python
FROM python:3.11-slim

# установка системных библиотек, для драйвера psycopg2
RUN apt-get update && apt-get install -y libpq-dev gcc

# установка рабочей директории внутри контейнера
WORKDIR /app

# копирование файла с зависимостями
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# копирование всех файлов проекта в контейнер
COPY . .

# команда для запуска сервера
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]