import os
import sys
from .base import *  # noqa: F401,F403

DEBUG = True

CORS_ALLOW_ALL_ORIGINS = True
REPORTS_GENERATE_SYNC = os.environ.get('REPORTS_GENERATE_SYNC', 'true').lower() == 'true'
DATA_UPLOAD_PROCESS_SYNC = os.environ.get('DATA_UPLOAD_PROCESS_SYNC', 'true').lower() == 'true'

if os.environ.get('USE_SQLITE', 'false').lower() == 'true':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

if 'test' in sys.argv:
    CELERY_BROKER_URL = 'memory://'
    CELERY_RESULT_BACKEND = 'cache+memory://'
    REPORTS_GENERATE_SYNC = os.environ.get('REPORTS_GENERATE_SYNC', 'false').lower() == 'true'
    DATA_UPLOAD_PROCESS_SYNC = os.environ.get('DATA_UPLOAD_PROCESS_SYNC', 'false').lower() == 'true'
