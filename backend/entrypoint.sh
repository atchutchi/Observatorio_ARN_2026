#!/bin/sh
set -e

echo "Waiting for PostgreSQL..."
while ! python -c "import psycopg2; psycopg2.connect(dbname='$POSTGRES_DB', user='$POSTGRES_USER', password='$POSTGRES_PASSWORD', host='$POSTGRES_HOST', port='$POSTGRES_PORT')" 2>/dev/null; do
    sleep 1
done
echo "PostgreSQL is ready."

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput 2>/dev/null || true

echo "Creating superuser if needed..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
import os
username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
if not all([username, email, password]):
    print('DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL, and DJANGO_SUPERUSER_PASSWORD must be set.')
elif not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password, role='admin_arn')
    print(f'Superuser {username} created.')
else:
    print(f'Superuser {username} already exists.')
" 2>/dev/null || true

echo "Seeding reference data..."
python manage.py seed_data 2>/dev/null || true

echo "Importing KPI data if available..."
python manage.py import_kpi_json --data-dir data/kpi_2024 2>/dev/null || true
python manage.py import_kpi_json --data-dir data/kpi_2020 2>/dev/null || true
python manage.py import_kpi_json --data-dir data/kpi_2019 2>/dev/null || true
python manage.py import_kpi_json --data-dir data/kpi_2018 2>/dev/null || true

echo "Entrypoint complete."
