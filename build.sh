#!/bin/bash

# Exit on error
set -e

echo "Installing pip..."
python -m pip install --upgrade pip

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Creating directories..."
mkdir -p staticfiles
mkdir -p media

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Applying migrations..."
python manage.py migrate --noinput

echo "Build completed!"
