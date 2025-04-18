#!/bin/bash

# Exit on error
set -e

# Print Python version for debugging
python --version

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p staticfiles
mkdir -p media

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate --noinput

# Create initial superuser if needed (commented out for security)
# if [[ -n "${DJANGO_SUPERUSER_USERNAME}" ]]; then
#     python manage.py createsuperuser --noinput || true
# fi

echo "Build completed successfully!"
