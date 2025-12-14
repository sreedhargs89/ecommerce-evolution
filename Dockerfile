FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy everything (but .dockerignore will filter)
COPY . .

# Default command (overridden by docker-compose)
CMD ["uvicorn", "services.users.main:app", "--host", "0.0.0.0", "--port", "8000"]
