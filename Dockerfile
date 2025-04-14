FROM python:3.9-slim

WORKDIR /app

# Install dependencies including curl for healthcheck
RUN apt-get update && apt-get install -y curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Set file permissions and line endings
COPY . .
RUN find /app -type f -name "*.py" -exec chmod +x {} \; && \
    find /app -type f -name "*.sh" -exec chmod +x {} \;

# Create config file
RUN echo "[HOST]\nhost = 0.0.0.0\nport = 5000\n\n[DEBUG]\ndebug = true" > config.ini

# Expose port
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=app.py
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Run the integrated application with Windows-compatible syntax
CMD ["python", "-u", "app.py"] 