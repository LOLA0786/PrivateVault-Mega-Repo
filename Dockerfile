FROM python:3.10-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONPATH=/app/src

EXPOSE 8000

CMD ["uvicorn", "galani.api.app_v3:app", "--host", "0.0.0.0", "--port", "8000"]
