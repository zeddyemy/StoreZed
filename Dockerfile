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

# Use the shell form of CMD
CMD gunicorn --bind 0.0.0.0:$PORT --workers 4 --timeout 120 --worker-class gevent run:flask_app

# # Copy the server script and make it executable
# COPY server.sh .
# RUN chmod +x server.sh

# # Use ENTRYPOINT to run the script
# ENTRYPOINT ["./server.sh"]

# # Use production WSGI server instead of Flask dev server
# CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "--workers", "2", "--timeout", "120", "run:flask_app"]

# CMD ["flask", "run", "-h", "0.0.0.0"]