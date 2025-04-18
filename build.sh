#!/bin/bash
set -e

python -m pip install --upgrade pip
pip install -r requirements.txt

mkdir -p staticfiles media

python manage.py collectstatic --noinput
python manage.py migrate --noinput

echo "Build completed!"
