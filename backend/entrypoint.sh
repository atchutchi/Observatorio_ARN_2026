#!/bin/sh
set -e

is_true() {
    case "$(printf '%s' "${1:-}" | tr '[:upper:]' '[:lower:]')" in
        1|true|yes|on) return 0 ;;
        *) return 1 ;;
    esac
}

if is_true "${WAIT_FOR_POSTGRES:-true}"; then
    echo "Waiting for PostgreSQL..."
    python - <<'PY'
import os
import time

import psycopg2

database_url = os.environ.get('DATABASE_URL')
timeout = int(os.environ.get('POSTGRES_WAIT_TIMEOUT', '60'))
started_at = time.time()

while True:
    try:
        if database_url:
            conn = psycopg2.connect(database_url)
        else:
            conn = psycopg2.connect(
                dbname=os.environ.get('POSTGRES_DB'),
                user=os.environ.get('POSTGRES_USER'),
                password=os.environ.get('POSTGRES_PASSWORD'),
                host=os.environ.get('POSTGRES_HOST'),
                port=os.environ.get('POSTGRES_PORT'),
            )
        conn.close()
        break
    except psycopg2.Error as exc:
        if time.time() - started_at >= timeout:
            raise SystemExit(f'PostgreSQL not ready after {timeout}s: {exc}')
        time.sleep(1)
PY
    echo "PostgreSQL is ready."
else
    echo "Skipping PostgreSQL wait. Set WAIT_FOR_POSTGRES=true to enable it."
fi

if is_true "${RUN_MIGRATIONS_ON_STARTUP:-true}"; then
    echo "Running migrations..."
    python manage.py migrate --noinput
else
    echo "Skipping migrations. Set RUN_MIGRATIONS_ON_STARTUP=true to run them."
fi

if is_true "${RUN_COLLECTSTATIC_ON_STARTUP:-false}"; then
    echo "Collecting static files..."
    python manage.py collectstatic --noinput
else
    echo "Skipping collectstatic at startup. Static files should be collected at build time."
fi

echo "Ensuring superuser if configured..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
import os
username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
if not all([username, email, password]):
    print('DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL, and DJANGO_SUPERUSER_PASSWORD not set. Skipping superuser sync.')
else:
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            'email': email,
            'role': 'admin_arn',
            'is_staff': True,
            'is_superuser': True,
        },
    )
    user.email = email
    user.role = 'admin_arn'
    user.is_staff = True
    user.is_superuser = True
    user.set_password(password)
    user.save()
    if created:
        print(f'Superuser {username} created.')
    else:
        print(f'Superuser {username} updated.')
"

if is_true "$RUN_SEED_ON_STARTUP"; then
    echo "Seeding reference data..."
    python manage.py seed_data
else
    echo "Skipping seed_data. Set RUN_SEED_ON_STARTUP=true to run it."
fi

if is_true "$RUN_KPI_IMPORT_ON_STARTUP"; then
    KPI_IMPORT_YEARS="${KPI_IMPORT_YEARS:-2024 2021 2020 2019 2018}"
    echo "Importing KPI data for years: $KPI_IMPORT_YEARS"
    for year in $KPI_IMPORT_YEARS; do
        python manage.py import_kpi_json --data-dir "data/kpi_$year"
    done
else
    echo "Skipping KPI import. Set RUN_KPI_IMPORT_ON_STARTUP=true to run it."
fi

echo "Entrypoint complete."
