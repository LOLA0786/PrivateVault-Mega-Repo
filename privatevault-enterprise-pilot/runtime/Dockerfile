FROM python:3.11-slim

WORKDIR /app

COPY runtime/requirements-integrated.txt ./

RUN pip install --no-cache-dir -r requirements-integrated.txt

COPY . .

ENV PYTHONUNBUFFERED=1

CMD ["python", "runtime/main_vault_integrated.py"]
