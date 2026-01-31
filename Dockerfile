FROM python:3.9-slim

WORKDIR /app

COPY . .

RUN chmod +x /app/main.py

CMD ["python", "/app/main.py"]
