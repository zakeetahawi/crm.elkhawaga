#!/bin/bash

# Exit on error
set -e

# Print Python version for debugging
python --version

# Upgrade pip
python -m pip install --upgrade pip

# Install Python and dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install additional required packages
pip install pillow pandas numpy openpyxl xlrd gunicorn whitenoise

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

echo "Build completed successfully!"
