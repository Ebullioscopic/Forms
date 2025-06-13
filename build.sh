#!/usr/bin/env bash
set -o errexit

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Navigate to Django project directory
cd collaborative_forms

# Create static directory if it doesn't exist
mkdir -p static

# Create migrations in correct order
python manage.py makemigrations accounts
python manage.py makemigrations forms
python manage.py makemigrations

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Go back to root for deployment
cd ..
