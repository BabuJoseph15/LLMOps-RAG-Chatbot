FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (better Docker caching)
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy entire backend directory
COPY . .

# Verify chroma_db exists during build
RUN ls -R /app/chroma_db

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
