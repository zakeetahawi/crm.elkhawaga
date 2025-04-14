# Use Python 3.11 slim image as specified in netlify.toml
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE=crm.settings
ENV PYTHONPATH=.
ENV DEBUG=0

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    curl \
    libjpeg-dev \
    libpng-dev \
    libpq-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements-dev.txt \
    && pip install pandas numpy openpyxl xlrd Pillow

# Copy project
COPY . .

# Create necessary directories
RUN mkdir -p staticfiles media

# Collect static files and run migrations
RUN python manage.py collectstatic --noinput
RUN python manage.py migrate --noinput

# Run gunicorn
CMD ["gunicorn", "crm.wsgi:application", "--bind", "0.0.0.0:8000"]