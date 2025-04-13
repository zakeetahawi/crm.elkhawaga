#!/bin/bash

# Exit on error
set -e

# Install Python and dependencies
echo "Installing dependencies..."
python -m pip install --upgrade pip
pip install -r requirements-dev.txt

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate --noinput

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p staticfiles
mkdir -p media

# Print Python and pip versions for debugging
echo "Python version:"
python --version
echo "Pip version:"
pip --version

echo "Build completed successfully!"
