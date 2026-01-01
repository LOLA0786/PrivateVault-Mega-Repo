FROM python:3.9-slim

WORKDIR /app

# Install system dependencies for math
RUN apt-get update && apt-get install -y libgomp1 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Launch with 4 Workers (MAANG Standard for high concurrency)
CMD ["uvicorn", "sovereign_api.py:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
