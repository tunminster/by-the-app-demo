FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    unixodbc-dev \
    curl \
    gnupg \
    apt-transport-https \
    && apt-get update \
    # Clean up to reduce layer size
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

#CMD ["python", "run.py"]
CMD ["uvicorn", "app:create_app", "--host", "0.0.0.0", "--port", "8080", "--reload", "--ws", "websockets"]
