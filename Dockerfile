FROM python:3.11-slim

WORKDIR /app

RUN pip install -e . --no-cache-dir

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]