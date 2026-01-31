FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Make privatevault executable
RUN chmod +x /app/privatevault || true

# Debug: show permissions
RUN ls -l /app/privatevault || true

CMD ["/app/privatevault", "run", "demo"]
