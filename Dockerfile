FROM python:3.12-slim

# Set environment variables (prevents Python from buffering outputs)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy requirements FIRST to leverage Docker layer caching
COPY requirements.txt requirements.txt

RUN pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Use production WSGI server instead of Flask dev server
CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "--workers", "2", "--timeout", "120", "run:flask_app"]

# CMD ["flask", "run", "-h", "0.0.0.0"]