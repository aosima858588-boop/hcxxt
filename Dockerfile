FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app ./app

# Expose port (will be set via PORT env var)
EXPOSE 8000

# Set default PORT if not provided
ENV PORT=8000

# Run the application
CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT
