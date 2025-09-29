# Dockerfile (simples para avaliação local)
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PORT=8000
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
# Migra e sobe o servidor em 0.0.0.0:8000
CMD sh -c "python manage.py migrate --noinput && python manage.py runserver 0.0.0.0:${PORT}"
