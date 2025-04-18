#!/bin/bash
set -e

echo "Python version:"
python --version

echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Setting up directories..."
mkdir -p staticfiles media

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Applying migrations..."
python manage.py migrate --noinput

echo "Build completed!"
